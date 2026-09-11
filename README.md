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

