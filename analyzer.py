"""Call Gemini with the parsed page and return a structured AnalysisResult."""
from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL
from models import AnalysisResult
from parser import ParsedPage
from prompts import ANALYSIS_PROMPT


class AnalyzerError(Exception):
    """Raised when the LLM call fails or returns invalid JSON."""


def _build_content_block(page: ParsedPage) -> str:
    """Bundle the signals we extracted into a compact LLM-ready block."""
    parts = []
    if page.headings:
        parts.append("KEY HEADINGS:\n" + "\n".join(f"- {h}" for h in page.headings))
    if page.ctas:
        parts.append("CALLS-TO-ACTION:\n" + "\n".join(f"- {c}" for c in page.ctas))
    parts.append("PAGE BODY:\n" + page.body_text)
    return "\n\n".join(parts)


def analyze(page: ParsedPage) -> AnalysisResult:
    """Run the competitor analysis. Raises AnalyzerError on any failure."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise AnalyzerError(
            "GEMINI_API_KEY is missing. Add it to the .env file "
            "(get a free key at https://aistudio.google.com/app/apikey)."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = ANALYSIS_PROMPT.format(
        url=page.url,
        title=page.title or "(none)",
        description=page.description or "(none)",
        content=_build_content_block(page),
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalysisResult,
                temperature=0.4,
            ),
        )
    except Exception as e:
        raise AnalyzerError(f"Gemini API call failed: {e}") from e

    # google-genai returns the validated Pydantic object on `.parsed` when
    # a response_schema is provided. Fall back to JSON parsing if needed.
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, AnalysisResult):
        return parsed

    raw = (response.text or "").strip()
    if not raw:
        raise AnalyzerError("Gemini returned an empty response.")

    try:
        return AnalysisResult.model_validate_json(raw)
    except Exception as e:
        raise AnalyzerError(f"Could not parse LLM response as JSON: {e}") from e
