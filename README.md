# Strategic PM Tool — Competitor Intelligence

Drop a competitor's URL. Get a PM-grade strategy brief — value prop, core features, target audience, SWOT, and one concrete feature gap to build against. Export as a branded Battle Card PDF.

**Live demo:** https://strategic-pm-tool-ub3gamwfuyfcf9usjygvpe.streamlit.app/

![App screenshot](docs/screenshot.png)

## What it does

- Scrapes the landing page (BeautifulSoup) — headings, CTAs, body copy
- Runs a structured Gemini call — returns a validated Pydantic `AnalysisResult`
- Renders the result as a designed report: executive summary cards, color-coded SWOT grid, feature-gap callout
- Exports a one-page PDF battle card for sharing with sales or leadership

Stack: Python · Streamlit · google-genai · BeautifulSoup · Pydantic · fpdf2

## Run locally

```bash
python -m venv venv
venv\Scripts\activate               # Windows  (use `source venv/bin/activate` on macOS/Linux)
pip install -r requirements.txt

cp .env.example .env                # then paste your key from https://aistudio.google.com/app/apikey
streamlit run app.py
```

## Architecture

| Module          | Responsibility                                              |
| --------------- | ----------------------------------------------------------- |
| `scraper.py`    | URL → raw HTML + title/meta                                 |
| `parser.py`    | HTML → clean text + headings + CTAs                         |
| `analyzer.py`  | Parsed page → Gemini (structured JSON) → `AnalysisResult`   |
| `models.py`    | Pydantic schemas — the LLM contract                         |
| `pdf_export.py`| `AnalysisResult` → PDF battle card                          |
| `app.py`       | Streamlit UI — thin orchestrator                            |
| `config.py`    | Layered secrets: `st.secrets` (cloud) → `.env` (local)      |

Data flow: `URL → scrape → parse → analyze → render + export`

## Deploy to Streamlit Cloud

1. Fork/clone this repo on GitHub
2. At https://share.streamlit.io → **New app** → select repo, branch `main`, file `app.py`
3. **Advanced settings → Secrets**:
   ```toml
   GEMINI_API_KEY = "your_key"
   GEMINI_MODEL   = "gemini-2.5-flash-lite"
   ```
4. Deploy

The same `config.py` reads secrets in both environments — no environment-specific code.
