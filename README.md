# Strategic PM Tool

**Turn any competitor's landing page into a product strategy brief — in under 10 seconds.**

### [Open the live app →](https://strategic-pm-tool-ub3gamwfuyfcf9usjygvpe.streamlit.app/)

![App screenshot](docs/screenshot.png)

---

## The Problem

Competitive research is the PM tax no one talks about.

Every kickoff, every roadmap review, every pricing conversation starts with the same grind: open 10 tabs, skim marketing pages, try to decode positioning, translate features into user value, build a slide deck no one reads. The output is inconsistent across teammates, out-of-date the moment it's filed, and — worst of all — **it rarely surfaces the one thing PMs actually need: the strategic gap between what competitors ship and what users still don't have**.

PMs don't need more data. They need faster, sharper signal on where to place the next bet.

## The Solution

Strategic PM Tool collapses the research loop from **two hours to ten seconds**.

Paste a competitor's URL → the tool scrapes their landing page, runs it through a structured AI analysis, and returns a battle-card-ready brief: value proposition, core features, target audience, SWOT, and — the piece that changes the conversation — **one concrete feature gap worth building against**, grounded in evidence from the page itself.

The value isn't that it reads landing pages faster than a human. It's that it forces a **consistent analytical frame** across every competitor, every time, so you can compare, stack-rank, and decide instead of interpret.

**The point is to stop doing market research and start doing market strategy.**

## Who It's For

- **Product Managers** preparing roadmap reviews, competitive decks, or "why are we losing deals?" analyses
- **Founders & early-stage operators** sizing up a space before committing engineering cycles
- **Growth & product marketers** building positioning documents and sales battle cards
- **Strategy / BizOps teams** running quarterly competitive sweeps at scale

## Product Features

### ◆ Automated Competitive Analysis
One URL, full brief. Value proposition, core features, and target audience inferred from the page — not assumed, not guessed.

### ◆ Structured SWOT at a Glance
A color-coded 2×2 grid (Strengths, Weaknesses, Opportunities, Threats) with 2-3 sharp, evidence-backed points per quadrant. Built for scanning in a meeting, not reading in a doc.

### ◆ Feature Gap Discovery — the PM Edge
The most valuable output. One specific, buildable feature the competitor is missing — paired with the rationale (what signals on the page point to it) and the user value (who benefits if someone builds it). This is what turns research into a roadmap input.

### ◆ Stakeholder-Ready Battle Card PDF
One click → a branded, print-ready PDF. Drop it in a Slack thread, attach it to a PRD, hand it to sales. The output is designed to be shared, not just consumed by the analyst.

### ◆ Persistent Results
Session state keeps your analysis on screen across downloads and toggles — no losing your work to a re-run.

## What's Next (Roadmap)

### Near-term
- **Side-by-side comparison** — analyze 2–4 competitors at once, rendered in a single diff view so gaps between players pop out instantly
- **Positioning map** — auto-generated 2×2 matrix (e.g. Price vs. Complexity) plotting the analyzed competitor within its category
- **Analysis history** — keep a rolling log of competitors analyzed over time, with diff alerts when a landing page materially changes

### Mid-term
- **Pricing history tracking** — monitor competitor pricing pages weekly and surface changes (anchor price shifts, new tiers, removed discounts)
- **Chrome extension** — one-click analysis from any page you're already reading, bypassing the paste-URL flow
- **Team workspaces** — shared analyses, comments, tags, export-to-Notion/Linear

### Longer-term vision
- **Source expansion beyond landing pages** — pricing pages, changelogs, job postings (hiring signals often leak roadmap), G2/Capterra review deltas
- **Proactive alerts** — "your competitor just shipped X, here's what it threatens in your roadmap"
- **API** — feed the structured output into existing PM tools (Productboard, Jira, Notion) so competitive signal becomes a real input to prioritization

## Why I Built This

I built this as a portfolio piece while applying for a PM role at [Wix](https://www.wix.com). The goal wasn't to ship a polished SaaS — it was to demonstrate three things product thinking cares about:

1. **Framing a real problem** (PMs waste hours on research that rarely drives decisions) and solving for the *job* (get to a decision faster), not the *symptom* (make the research itself prettier).
2. **Making the strategic insight the hero of the output** — the "Feature Gap" recommendation is what separates this from yet another AI summarizer.
3. **Shipping the whole loop end-to-end** — from scrape to rendered report to exportable artifact — because PMs who have built products tend to make better product decisions.

---

## Technical Setup

<details>
<summary>Architecture, stack, and run instructions</summary>

### Stack
Python · Streamlit · Google Gemini (`google-genai`) · BeautifulSoup · Pydantic · fpdf2

### Architecture

| Module         | Responsibility                                              |
| -------------- | ----------------------------------------------------------- |
| `scraper.py`   | URL → raw HTML + title/meta                                 |
| `parser.py`    | HTML → clean text + headings + CTAs                         |
| `analyzer.py`  | Parsed page → Gemini (structured JSON) → `AnalysisResult`   |
| `models.py`    | Pydantic schemas — the LLM contract                         |
| `pdf_export.py`| `AnalysisResult` → PDF battle card                          |
| `app.py`       | Streamlit UI — thin orchestrator                            |
| `config.py`    | Layered secrets: `st.secrets` (cloud) → `.env` (local)      |

Data flow: `URL → scrape → parse → analyze → render + export`

### Design decisions worth calling out
- **Structured LLM output via Pydantic schema** — Gemini returns a validated object, not a string we parse. Changing the analysis shape means changing one file (`models.py`).
- **Layered secret resolution** — same `config.py` reads from Streamlit Cloud secrets in production and `.env` locally. No environment-specific branches.
- **XSS-safe HTML rendering** — all LLM-generated text is `html.escape()`'d before being injected into the custom CSS layout.
- **Thin UI layer** — `app.py` only orchestrates; swapping Streamlit for a React+FastAPI stack is a weekend of work, not a rewrite.

### Run locally

```bash
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # paste your Gemini key from https://aistudio.google.com/app/apikey
streamlit run app.py
```

</details>
