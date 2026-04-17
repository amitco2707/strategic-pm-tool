"""Render an AnalysisResult as a one-page PDF 'battle card' for PMs to share."""
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from models import AnalysisResult


def _safe(text: str) -> str:
    """fpdf2's core fonts are latin-1; replace anything outside that range."""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _content_width(pdf: FPDF) -> float:
    """Full writable width of the current page."""
    return pdf.w - pdf.l_margin - pdf.r_margin


def _reset_x(pdf: FPDF) -> None:
    """Snap the cursor back to the left margin.

    Needed because fpdf2's deprecated `ln=True` and `multi_cell(w=0, ...)` can
    leave the cursor drifted to the right edge. If a subsequent draw then
    computes its width from current x, we get 0 width and fpdf2 raises
    `Not enough horizontal space to render a single character`.
    """
    pdf.set_x(pdf.l_margin)


def _cell_line(pdf: FPDF, text: str, height: float) -> None:
    """Single-line cell that always starts at the left margin and advances."""
    _reset_x(pdf)
    pdf.cell(
        _content_width(pdf),
        height,
        _safe(text),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )


def _paragraph(pdf: FPDF, text: str, height: float = 5) -> None:
    """Wrapped paragraph that always starts at the left margin and advances."""
    _reset_x(pdf)
    pdf.multi_cell(
        _content_width(pdf),
        height,
        _safe(text),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )


def _section_header(pdf: FPDF, title: str) -> None:
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    _cell_line(pdf, title, height=8)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)


def _bullets(pdf: FPDF, items) -> None:
    for it in items:
        _paragraph(pdf, f"- {it}")


def build_battle_card(result: AnalysisResult, url: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title block
    pdf.set_font("Helvetica", "B", 20)
    _cell_line(pdf, "Competitor Battle Card", height=10)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(110, 110, 110)
    _cell_line(pdf, result.company_name, height=6)
    # URLs can be long and unbreakable; use a wrapping paragraph, not a single-
    # line cell, so an overflowing URL never pushes the cursor off-page.
    _paragraph(pdf, url)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    _section_header(pdf, "Value Proposition")
    _paragraph(pdf, result.value_proposition)
    pdf.ln(3)

    _section_header(pdf, "Target Audience")
    _paragraph(pdf, result.target_audience)
    pdf.ln(3)

    _section_header(pdf, "Core Features")
    _bullets(pdf, result.core_features)
    pdf.ln(3)

    _section_header(pdf, "SWOT Analysis")
    for label, items in [
        ("Strengths", result.swot.strengths),
        ("Weaknesses", result.swot.weaknesses),
        ("Opportunities", result.swot.opportunities),
        ("Threats", result.swot.threats),
    ]:
        pdf.set_font("Helvetica", "B", 10)
        _cell_line(pdf, label, height=6)
        pdf.set_font("Helvetica", "", 10)
        _bullets(pdf, items)
    pdf.ln(2)

    _section_header(pdf, "Feature Gap Opportunity")
    pdf.set_font("Helvetica", "B", 10)
    _paragraph(pdf, result.feature_gap.gap)
    pdf.set_font("Helvetica", "", 10)
    _paragraph(pdf, f"Rationale: {result.feature_gap.rationale}")
    _paragraph(pdf, f"User Value: {result.feature_gap.user_value}")

    out = pdf.output(dest="S")
    # fpdf2 returns bytearray; normalize to bytes for Streamlit's download_button.
    return bytes(out)
