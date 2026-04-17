"""Configuration with layered secret resolution.

Resolution order for the Gemini API key:
1. Streamlit Secrets (`st.secrets["GEMINI_API_KEY"]` or `GOOGLE_API_KEY`) — how
   Streamlit Cloud injects secrets on deployment.
2. OS env var / `.env` file — for local development.

Both paths land on the same `GEMINI_API_KEY` module attribute so the rest of
the app doesn't care where the key came from.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Always load the .env sitting next to this file (regardless of cwd). `override=True`
# lets the file win over stale shell env vars that may not match what the user
# just edited.
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)


def _from_streamlit_secrets() -> tuple[str, str]:
    """Return (api_key, model) from Streamlit secrets, or ("", "") if unavailable.

    Importing `streamlit` is deferred so this module stays usable outside a
    Streamlit process (tests, scripts). Accessing `st.secrets` when no
    secrets.toml exists raises; we treat that as "not configured" and fall
    through to env vars.
    """
    try:
        import streamlit as st  # noqa: WPS433 — local import is intentional
    except ImportError:
        return "", ""

    try:
        # Accept both GEMINI_API_KEY (preferred) and GOOGLE_API_KEY (Google's
        # common convention) so recruiters can use either name.
        key = str(
            st.secrets.get("GEMINI_API_KEY")
            or st.secrets.get("GOOGLE_API_KEY")
            or ""
        ).strip()
        model = str(st.secrets.get("GEMINI_MODEL", "")).strip()
        return key, model
    except Exception:
        # st.secrets raises on missing secrets.toml; treat as "not configured".
        return "", ""


_secret_key, _secret_model = _from_streamlit_secrets()

GEMINI_API_KEY = _secret_key or os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = (
    _secret_model
    or os.getenv("GEMINI_MODEL", "").strip()
    or "gemini-2.5-flash-lite"
)

# Scraper settings
REQUEST_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# Content budget for the LLM (roughly the chars we send as the body)
MAX_CONTENT_CHARS = 8000
