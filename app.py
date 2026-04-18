"""Streamlit UI for the Competitor Intelligence & Product Strategy tool."""
from html import escape
from typing import Iterable
from urllib.parse import urlparse

import streamlit as st

from analyzer import AnalyzerError, analyze
from config import GEMINI_API_KEY, GEMINI_MODEL
from parser import parse
from pdf_export import build_battle_card
from scraper import ScrapeError, scrape


# ---------------------------------------------------------------------------
# Page config + design system
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Strategic PM Tool",
    page_icon="\u25c6",  # ◆
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Design tokens — kept in one place so it's easy to retune the whole look.
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #f7f8fc;
    --surface: #ffffff;
    --border: #e5e7eb;
    --text: #0f172a;
    --muted: #64748b;
    --brand: #4f46e5;
    --brand-soft: #eef2ff;
    --accent: #f59e0b;
    --accent-soft: #fef3c7;
    --accent-ink: #78350f;
    --radius-lg: 16px;
    --radius-md: 12px;
    --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04), 0 1px 1px rgba(15, 23, 42, 0.02);
    --shadow-md: 0 4px 16px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.04);
}

/* Base */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text);
}

/* -------- Animated mesh gradient background (Stripe/Linear-style) --------
   Painted directly on .stApp so there's no pseudo-element stacking context
   to fight. Each blob is a discrete sized radial gradient, drawn on its own
   background layer with no-repeat; we animate `background-position` to drift
   the blobs. Sized blobs (not full-tile percentage gradients) keep the
   "mesh" look distinct instead of blurring into one wash. */
.stApp {
    background-color: #f7f8fc;
    background-image:
        radial-gradient(circle, rgba(129, 140, 248, 0.60) 0%, transparent 70%),
        radial-gradient(circle, rgba(147, 197, 253, 0.55) 0%, transparent 70%),
        radial-gradient(circle, rgba(196, 181, 253, 0.55) 0%, transparent 70%),
        radial-gradient(circle, rgba(165, 243, 252, 0.50) 0%, transparent 70%),
        radial-gradient(circle, rgba(224, 231, 255, 0.50) 0%, transparent 75%);
    background-size:
        900px 800px,
        800px 750px,
        950px 850px,
        850px 780px,
        1100px 1000px;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: 15% 20%, 85% 15%, 80% 85%, 20% 80%, 50% 50%;
    animation: meshDrift 26s ease-in-out infinite alternate;
}
@keyframes meshDrift {
    0% {
        background-position: 15% 20%, 85% 15%, 80% 85%, 20% 80%, 50% 50%;
    }
    50% {
        background-position: 22% 14%, 78% 24%, 86% 76%, 14% 88%, 56% 46%;
    }
    100% {
        background-position: 25% 18%, 75% 28%, 88% 72%, 12% 86%, 44% 54%;
    }
}
@media (prefers-reduced-motion: reduce) {
    .stApp { animation: none; }
}

/* Kill Streamlit chrome we don't need */
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2.5rem; padding-bottom: 4rem; max-width: 1100px; }

/* Hero */
.hero { text-align: center; padding: 2.5rem 0 1rem; }
.hero-eyebrow {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--brand);
    background: var(--brand-soft);
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2.75rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin: 0 0 0.75rem;
    padding: 0 0.75rem 0.15rem;  /* guard against gradient-text descender clipping */
    overflow: visible;
}
.hero-title .accent {
    background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding-right: 0.1em;  /* reserve space for the ascender on the last glyph */
    display: inline-block;
}
.hero-sub {
    font-size: 1.05rem;
    color: var(--muted);
    max-width: 620px;
    margin-left: auto !important;
    margin-right: auto !important;
    margin-bottom: 1.5rem;
    line-height: 1.55;
    text-align: center !important;
    display: block;
}

/* Input + button */
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    padding: 0.85rem 1rem !important;
    font-size: 1rem !important;
    background: var(--surface) !important;
    color: #31333F !important;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
}
.stTextInput label { font-weight: 500; color: var(--text); }

.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
    background: var(--brand) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: transform 0.08s, box-shadow 0.15s, background 0.15s !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
    background: #4338ca !important;
    transform: translateY(-1px);
    box-shadow: var(--shadow-md) !important;
}

/* Status box */
[data-testid="stStatusWidget"], div[data-testid="stStatus"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
}

/* Report layout */
.report-header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 2rem 2.25rem;
    margin-top: 2rem;
    box-shadow: var(--shadow-sm);
}
.report-header .company {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0 0 0.25rem;
}
.report-header .url {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 1.25rem;
    word-break: break-all;
}
.report-header .valueprop {
    font-size: 1.25rem;
    font-weight: 500;
    line-height: 1.45;
    color: var(--text);
    padding-left: 1rem;
    border-left: 3px solid var(--brand);
    margin: 0;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.75rem;
    box-shadow: var(--shadow-sm);
    height: 100%;
}
.card h3 {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 0.85rem;
}
.card p, .card li { font-size: 0.95rem; line-height: 1.55; color: var(--text); margin: 0; }
.card ul { margin: 0; padding-left: 1.15rem; }
.card ul li { margin-bottom: 0.4rem; }

.section-title {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 2.25rem 0 0.85rem;
}

/* SWOT grid */
.swot-card {
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.4rem;
    border: 1px solid transparent;
    height: 100%;
}
.swot-card .label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 0 0 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.swot-card .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.swot-card ul { margin: 0; padding-left: 1.1rem; }
.swot-card li { font-size: 0.92rem; line-height: 1.5; margin-bottom: 0.35rem; }

/* Spacer between the two SWOT rows (st.columns has no row gap) */
.swot-gap { height: 1rem; }

.swot-strengths     { background: #ecfdf5; border-color: #a7f3d0; color: #064e3b; }
.swot-strengths .dot{ background: #10b981; }
.swot-weaknesses    { background: #fffbeb; border-color: #fde68a; color: #78350f; }
.swot-weaknesses .dot{ background: #f59e0b; }
.swot-opportunities { background: #eff6ff; border-color: #bfdbfe; color: #1e3a8a; }
.swot-opportunities .dot{ background: #3b82f6; }
.swot-threats       { background: #fef2f2; border-color: #fecaca; color: #7f1d1d; }
.swot-threats .dot  { background: #ef4444; }

/* Feature gap callout */
.gap {
    position: relative;
    background: linear-gradient(180deg, var(--accent-soft) 0%, #fef9e7 100%);
    border: 1px solid #fde68a;
    border-left: 4px solid var(--accent);
    border-radius: var(--radius-lg);
    padding: 1.75rem 2rem;
    margin-top: 0.5rem;
}
.gap .eyebrow {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent-ink);
    margin-bottom: 0.5rem;
}
.gap .headline {
    font-size: 1.35rem;
    font-weight: 700;
    line-height: 1.35;
    color: #451a03;
    margin: 0 0 1rem;
    letter-spacing: -0.01em;
}
.gap .meta { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.gap .meta .k {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent-ink);
    margin-bottom: 0.3rem;
}
.gap .meta .v { font-size: 0.95rem; line-height: 1.55; color: #1c1917; }
@media (max-width: 640px) { .gap .meta { grid-template-columns: 1fr; } }

/* Divider replacement */
.spacer { height: 1.5rem; }

/* Expander */
.streamlit-expanderHeader { font-weight: 500 !important; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Render helpers (HTML-escape everything from the LLM before injecting)
# ---------------------------------------------------------------------------

def _bullets_html(items: Iterable[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <span class="hero-eyebrow">Competitor Intelligence</span>
            <h1 class="hero-title">Turn any landing page into a <span class="accent">product strategy brief</span></h1>
            <p class="hero-sub">
                Drop a competitor URL. Get a PM-grade analysis — value prop, core features, target audience,
                SWOT, and one concrete feature gap to build against — in seconds.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_report_header(result, url: str) -> None:
    st.markdown(
        f"""
        <div class="report-header">
            <div class="company">{escape(result.company_name)}</div>
            <div class="url">{escape(url)}</div>
            <p class="valueprop">{escape(result.value_proposition)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_cards(result) -> None:
    features_html = _bullets_html(result.core_features)
    st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        st.markdown(
            f"""
            <div class="card">
                <h3>Target Audience</h3>
                <p>{escape(result.target_audience)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f"""
            <div class="card">
                <h3>Core Features</h3>
                <ul>{features_html}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _swot_card(variant: str, label: str, items: Iterable[str]) -> str:
    return (
        f'<div class="swot-card swot-{variant}">'
        f'  <div class="label"><span class="dot"></span>{escape(label)}</div>'
        f'  <ul>{_bullets_html(items)}</ul>'
        f'</div>'
    )


def render_swot(result) -> None:
    st.markdown('<div class="section-title">SWOT Analysis</div>', unsafe_allow_html=True)
    row1_a, row1_b = st.columns(2, gap="medium")
    with row1_a:
        st.markdown(_swot_card("strengths", "Strengths", result.swot.strengths), unsafe_allow_html=True)
    with row1_b:
        st.markdown(_swot_card("weaknesses", "Weaknesses", result.swot.weaknesses), unsafe_allow_html=True)
    # Vertical gap between the two rows — st.columns doesn't give us one.
    st.markdown('<div class="swot-gap"></div>', unsafe_allow_html=True)
    row2_a, row2_b = st.columns(2, gap="medium")
    with row2_a:
        st.markdown(_swot_card("opportunities", "Opportunities", result.swot.opportunities), unsafe_allow_html=True)
    with row2_b:
        st.markdown(_swot_card("threats", "Threats", result.swot.threats), unsafe_allow_html=True)


def render_feature_gap(result) -> None:
    st.markdown('<div class="section-title">The PM Edge — Feature Gap</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="gap">
            <div class="eyebrow">What to build</div>
            <div class="headline">{escape(result.feature_gap.gap)}</div>
            <div class="meta">
                <div>
                    <div class="k">Why this gap exists</div>
                    <div class="v">{escape(result.feature_gap.rationale)}</div>
                </div>
                <div>
                    <div class="k">User value</div>
                    <div class="v">{escape(result.feature_gap.user_value)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Flow
# ---------------------------------------------------------------------------

render_hero()

# Guardrail: refuse to run without a key so the user gets a clear message.
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    st.error(
        "GEMINI_API_KEY is missing. Open the `.env` file in this folder and paste "
        "your key (free at https://aistudio.google.com/app/apikey), then restart the app."
    )
    st.stop()

# Centered input form
_, mid, _ = st.columns([1, 3, 1])
with mid:
    with st.form("analyze_form", clear_on_submit=False):
        url = st.text_input(
            "Competitor URL",
            placeholder="https://www.notion.so",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Analyze competitor", type="primary", use_container_width=True)

# Run analysis on new submission and stash everything in session_state so it
# survives reruns (e.g. clicking the download button). Clearing is implicit:
# submitting a new URL overwrites the stored result.
if submitted:
    if not url.strip():
        st.warning("Please enter a URL to analyze.")
        st.stop()

    _raw = url.strip()
    _normalized = _raw if _raw.startswith(("http://", "https://")) else f"https://{_raw}"
    _parsed = urlparse(_normalized)
    if not _parsed.hostname or "." not in _parsed.hostname:
        st.warning(
            "Oops! That doesn't look like a valid URL. Please make sure to paste "
            "a complete link (e.g., https://www.notion.so) and try again."
        )
        st.stop()

    _FRIENDLY_ERROR = (
        "Oops! That doesn't look like a valid URL. Please make sure to paste "
        "a complete link (e.g., https://www.notion.so) and try again."
    )

    try:
        with st.status("Analyzing competitor...", expanded=True) as status:
            st.write("Fetching page...")
            page = scrape(url.strip())
            st.write("Parsing content...")
            parsed = parse(page)
            st.write(f"Running AI analysis with `{GEMINI_MODEL}`...")
            result = analyze(parsed)
            status.update(label="Analysis complete", state="complete", expanded=False)
    except ScrapeError:
        st.warning(_FRIENDLY_ERROR)
        st.stop()
    except AnalyzerError:
        st.warning(_FRIENDLY_ERROR)
        st.stop()

    # Generate the PDF once (not on every rerun) and cache alongside the result.
    st.session_state["result"] = result
    st.session_state["page_url"] = page.url
    st.session_state["pdf_bytes"] = build_battle_card(result, page.url)

# Render from session_state so the analysis stays on screen across reruns
# (download clicks, JSON expander toggles, etc.).
if "result" in st.session_state:
    result = st.session_state["result"]
    page_url = st.session_state["page_url"]
    pdf_bytes = st.session_state["pdf_bytes"]

    render_report_header(result, page_url)
    render_summary_cards(result)
    render_swot(result)
    render_feature_gap(result)

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

    safe_name = "".join(c if c.isalnum() else "_" for c in result.company_name).strip("_").lower()
    col_dl, col_json = st.columns([1, 1])
    with col_dl:
        st.download_button(
            label="Download Battle Card (PDF)",
            data=pdf_bytes,
            file_name=f"battle_card_{safe_name or 'competitor'}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col_json:
        with st.expander("View raw analysis (JSON)"):
            st.json(result.model_dump())
