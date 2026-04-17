# Strategic PM Tool — Competitor Intelligence

A Streamlit app that takes a competitor's URL and returns a PM-grade analysis: value proposition, core features, target audience, SWOT, and a concrete **feature-gap recommendation** — one specific thing the competitor is missing that you should build.

Ships with a one-click **Battle Card PDF export** so PMs can hand the result to sales or leadership.

Built with Python, Streamlit, BeautifulSoup, Pydantic, and Google Gemini (`google-genai` SDK).

## Local setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

## Configure locally

1. Get a free Gemini API key: https://aistudio.google.com/app/apikey
2. Copy `.env.example` to `.env` and paste your key:
   ```
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-2.5-flash-lite
   ```

`.env` is gitignored — it never leaves your machine.

## Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. Paste a competitor URL, hit **Analyze**, and download the PDF battle card.

## Architecture

| Module         | Responsibility                                                  |
| -------------- | --------------------------------------------------------------- |
| `scraper.py`   | Fetch URL → raw HTML + title/meta                               |
| `parser.py`    | HTML → clean body text + headings + CTAs                        |
| `analyzer.py`  | Parsed page → Gemini (structured JSON) → `AnalysisResult`       |
| `models.py`    | Pydantic schemas — single source of truth for the LLM contract  |
| `prompts.py`   | Prompt templates                                                |
| `pdf_export.py`| `AnalysisResult` → PDF battle card                              |
| `app.py`       | Streamlit UI — thin orchestrator                                |
| `config.py`    | Layered secret resolution (Streamlit Secrets → `.env`)          |

Data flow: `URL → scrape → parse → analyze → render + export`.

## Deployment (Streamlit Community Cloud)

The app uses **layered secret resolution**: on Streamlit Cloud it reads from `st.secrets`; locally it falls back to `.env`. Same code path — no environment-specific branches.

### Deployment steps

1. Push this repo to GitHub (see commands below). **Never commit `.env` or `.streamlit/secrets.toml`** — both are gitignored.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app**, select this repo, branch `main`, main file `app.py`.
4. Before clicking **Deploy**, open **Advanced settings → Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "your_real_key_here"
   GEMINI_MODEL = "gemini-2.5-flash-lite"
   ```
   The [.streamlit/secrets.toml.example](.streamlit/secrets.toml.example) file in this repo is the template.
5. Click **Deploy**. Streamlit installs from `requirements.txt` and serves the app at `your-app.streamlit.app`.

### How secrets work in this codebase

[config.py](config.py) resolves the API key in this order:

1. **`st.secrets["GEMINI_API_KEY"]`** (or `GOOGLE_API_KEY` alias) — injected by Streamlit Cloud
2. **OS env var** — set by `load_dotenv()` from the local `.env` file

Both paths land on the same `GEMINI_API_KEY` module attribute, so the rest of the app doesn't care where the key came from. `st.secrets` access is wrapped in a try/except because it raises when there's no `secrets.toml` (the local dev case) — that's fine, we just fall through to env vars.

## Security checklist (done)

- [x] `.gitignore` excludes `.env`, `venv/`, `.venv/`, `.streamlit/secrets.toml`
- [x] API key never logged or printed
- [x] All LLM-generated content HTML-escaped before rendering (XSS-safe)
- [x] Streamlit Secrets used for deployed environments, `.env` for local only
- [x] Committable templates (`.env.example`, `.streamlit/secrets.toml.example`) show structure without leaking values

## Extending

- Swap models by setting `GEMINI_MODEL` in `.env` or Streamlit Secrets. Run `client.models.list()` to see what your key has access to.
- For JS-rendered pages, replace `scraper.py` with a Crawl4AI/Playwright implementation; the rest of the pipeline stays the same.
- Add side-by-side competitor comparison by calling `analyze()` twice and rendering the two `AnalysisResult` objects in parallel columns.
