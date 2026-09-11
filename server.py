from __future__ import annotations

import asyncio
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "research_history.db"
load_dotenv(ROOT / ".env")

app = FastAPI(title="ResearchPilot", version="1.0.0")


class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    depth: Literal["quick", "standard", "deep"] = "standard"
    focus: Literal["balanced", "academic", "news", "market"] = "balanced"


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                created_at TEXT NOT NULL,
                report TEXT NOT NULL,
                sources TEXT NOT NULL,
                depth TEXT NOT NULL,
                focus TEXT NOT NULL
            )"""
        )


init_db()


def safe_domain(url: str) -> str:
    return urlparse(url).netloc.removeprefix("www.")


def search_web(query: str, count: int, focus: str) -> list[dict]:
    suffix = {
        "academic": "research paper study",
        "news": "latest news",
        "market": "market analysis industry report",
        "balanced": "",
    }[focus]
    with DDGS(timeout=12) as client:
        rows = list(client.text(f"{query} {suffix}".strip(), max_results=count))
    results = []
    seen = set()
    for row in rows:
        url = row.get("href") or row.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        results.append({
            "title": row.get("title", "Untitled source"),
            "url": url,
            "snippet": row.get("body", ""),
            "domain": safe_domain(url),
        })
    return results


async def enrich_source(client: httpx.AsyncClient, source: dict) -> dict:
    try:
        response = await client.get(source["url"], follow_redirects=True)
        response.raise_for_status()
        if "text/html" not in response.headers.get("content-type", ""):
            return source
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "form", "aside"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()
        source["content"] = text[:6500]
    except Exception:
        source["content"] = source["snippet"]
    return source


async def enrich_sources(sources: list[dict]) -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0 ResearchPilot/1.0"}
    async with httpx.AsyncClient(timeout=10, headers=headers) as client:
        return await asyncio.gather(*(enrich_source(client, item) for item in sources))


def fallback_report(query: str, sources: list[dict]) -> str:
    lines = [
        f"# Research brief: {query}", "",
        "## Executive summary", "",
        "The following evidence map organizes the strongest available web results. "
        "Add an OpenAI API key to generate a fully synthesized narrative.", "",
        "## Key findings", "",
    ]
    for index, source in enumerate(sources, 1):
        snippet = source.get("snippet") or source.get("content", "")[:420]
        lines.append(f"### {index}. {source['title']}")
        lines.append(f"{snippet.strip()} [{index}]")
        lines.append("")
    lines += ["## Sources", ""]
    lines += [f"[{i}] {s['title']} — {s['url']}" for i, s in enumerate(sources, 1)]
    return "\n".join(lines)


async def ai_report(query: str, sources: list[dict], depth: str, focus: str) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return fallback_report(query, sources)
    from openai import AsyncOpenAI

    evidence = "\n\n".join(
        f"SOURCE [{i}]\nTitle: {s['title']}\nURL: {s['url']}\nEvidence: {s.get('content') or s['snippet']}"
        for i, s in enumerate(sources, 1)
    )
    prompt = f"""You are a rigorous research analyst. Answer the research question using only the supplied evidence.
Research question: {query}
Depth: {depth}. Focus: {focus}.

Write a clear Markdown report with: Executive summary, Key findings, Detailed analysis, Gaps and uncertainties, and Sources.
Every factual claim must have an inline citation like [1]. Distinguish facts from inference. Do not invent evidence.

{evidence}"""
    client = AsyncOpenAI(api_key=key)
    response = await client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=prompt,
    )
    return response.output_text


@app.post("/api/research")
async def research(request: ResearchRequest):
    count = {"quick": 5, "standard": 8, "deep": 12}[request.depth]
    try:
        sources = await asyncio.to_thread(search_web, request.query, count, request.focus)
        if not sources:
            raise RuntimeError("No search results were returned")
        sources = await enrich_sources(sources)
        report = await ai_report(request.query, sources, request.depth, request.focus)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Research failed: {exc}") from exc

    created_at = datetime.now(timezone.utc).isoformat()
    public_sources = [{k: s[k] for k in ("title", "url", "snippet", "domain")} for s in sources]
    with db() as conn:
        cursor = conn.execute(
            "INSERT INTO reports(query, created_at, report, sources, depth, focus) VALUES (?, ?, ?, ?, ?, ?)",
            (request.query, created_at, report, json.dumps(public_sources), request.depth, request.focus),
        )
        report_id = cursor.lastrowid
    return {"id": report_id, "query": request.query, "created_at": created_at, "report": report, "sources": public_sources}


@app.get("/api/history")
def history():
    with db() as conn:
        rows = conn.execute("SELECT id, query, created_at, depth, focus FROM reports ORDER BY id DESC LIMIT 30").fetchall()
    return [dict(row) for row in rows]


@app.get("/api/reports/{report_id}")
def get_report(report_id: int):
    with db() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Report not found")
    result = dict(row)
    result["sources"] = json.loads(result["sources"])
    return result


@app.get("/api/reports/{report_id}/export")
def export_report(report_id: int):
    record = get_report(report_id)
    filename = re.sub(r"[^a-zA-Z0-9]+", "-", record["query"]).strip("-")[:60] or "research-report"
    return StreamingResponse(
        iter([record["report"]]),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}.md"'},
    )


@app.get("/health")
def health():
    return {"status": "ok", "ai_enabled": bool(os.getenv("OPENAI_API_KEY"))}


app.mount("/assets", StaticFiles(directory=ROOT / "static"), name="assets")


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")

