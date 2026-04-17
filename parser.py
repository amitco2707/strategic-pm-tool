"""Clean and extract structured signals from a scraped page."""
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup

from config import MAX_CONTENT_CHARS
from scraper import ScrapedPage


@dataclass
class ParsedPage:
    url: str
    title: str
    description: str
    headings: List[str]
    ctas: List[str]
    body_text: str


# HTML tags that are almost always noise for competitive analysis
_NOISE_TAGS = ("script", "style", "noscript", "iframe", "svg")


def parse(page: ScrapedPage) -> ParsedPage:
    """Extract headings, CTAs, and clean body text from the scraped HTML."""
    soup = BeautifulSoup(page.html, "html.parser")

    for tag in soup(_NOISE_TAGS):
        tag.decompose()

    headings = [
        h.get_text(strip=True)
        for h in soup.find_all(["h1", "h2", "h3"])
        if h.get_text(strip=True)
    ][:30]

    # Buttons and short anchor tags — likely CTAs
    ctas: List[str] = []
    for el in soup.find_all(["button", "a"]):
        text = el.get_text(strip=True)
        if text and 3 <= len(text) <= 40:
            ctas.append(text)
    # Preserve order, dedupe, cap
    ctas = list(dict.fromkeys(ctas))[:20]

    # Collapse whitespace and trim to budget
    body_text = " ".join(soup.get_text(separator=" ").split())[:MAX_CONTENT_CHARS]

    return ParsedPage(
        url=page.url,
        title=page.title,
        description=page.description,
        headings=headings,
        ctas=ctas,
        body_text=body_text,
    )
