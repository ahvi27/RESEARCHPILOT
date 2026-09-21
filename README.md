<div align="center">

# 🔎 ResearchPilot

**A local research agent that turns web sources into structured, citation-backed reports.**

![Python](https://img.shields.io/badge/Python-020617?style=for-the-badge&logo=python&logoColor=F7DF1E)
![FastAPI](https://img.shields.io/badge/FastAPI-020617?style=for-the-badge&logo=fastapi&logoColor=009688)
![SQLite](https://img.shields.io/badge/SQLite-020617?style=for-the-badge&logo=sqlite&logoColor=22D3EE)
![OpenAI](https://img.shields.io/badge/OpenAI_Optional-020617?style=for-the-badge&logo=openai&logoColor=FFFFFF)

</div>

## Overview

ResearchPilot searches the web, extracts evidence, generates structured reports with citations, stores research history locally, and exports results as Markdown. It remains useful without an API key through an evidence-map fallback.

<!-- Upload a real screenshot as docs/researchpilot-home.png, then uncomment:
![ResearchPilot interface](docs/researchpilot-home.png)
-->

## Features

- Quick, standard, and deep research modes
- Balanced, academic, news, and market search strategies
- Source extraction and citation-backed output
- Optional AI synthesis with OpenAI
- Evidence-map fallback without an AI key
- Local SQLite research history
- Markdown report export
- Responsive browser interface
- Linux, macOS, and Windows launch scripts

## Technology

`Python` · `FastAPI` · `Uvicorn` · `HTTPX` · `Beautiful Soup` · `DDGS` · `SQLite` · `OpenAI API`

## Run locally

```bash
git clone https://github.com/ahvi27/RESEARCHPILOT.git
cd RESEARCHPILOT
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn server:app --reload
```

Open `http://127.0.0.1:8000`. The OpenAI key is optional. Never commit your `.env` file.

## Privacy

Research history stays in the local `research_history.db` database. Search queries go to the selected provider. If OpenAI synthesis is enabled, collected source text is sent to the configured OpenAI model.

## Author

Built by [Gelila Mulugeta](https://github.com/ahvi27).
# ResearchPilot

ResearchPilot is a local research agent that searches the web, reads sources, produces a structured report with citations, saves research history, and exports reports as Markdown.

## Features

- Quick, standard, and deep research modes
- Balanced, academic, news, and market-focused searches
- Source extraction and citation-backed reports
- AI synthesis with an optional OpenAI API key
- Useful evidence-map fallback without an AI key
- Local SQLite research history
- Markdown report export
- Responsive web interface

## Run on Linux, macOS, or Windows

1. Open a terminal in this folder.
2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

3. Activate it:

   Linux/macOS:
   ```bash
   source .venv/bin/activate
   ```

   Windows PowerShell:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Optional: copy `.env.example` to `.env` and add your OpenAI API key.
6. Start the app:

   ```bash
   uvicorn server:app --reload
   ```

7. Open `http://127.0.0.1:8000` in your browser.

## Privacy

Reports are stored only in `research_history.db` on your computer. Search queries are sent to the search provider; when an OpenAI key is configured, collected source text is also sent to OpenAI for synthesis.

