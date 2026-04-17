"""Fetch a URL and return the raw HTML + headline metadata."""
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, USER_AGENT


class ScrapeError(Exception):
    """Raised when a page cannot be fetched or looks unusable."""


@dataclass
class ScrapedPage:
    url: str
    title: str
    description: str
    html: str


def scrape(url: str) -> ScrapedPage:
    """Fetch `url` and return headline metadata + raw HTML.

    Raises ScrapeError on network failure, non-2xx response, or empty body.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise ScrapeError(f"Could not fetch {url}: {e}") from e

    if not response.text.strip():
        raise ScrapeError(f"{url} returned an empty page")

    soup = BeautifulSoup(response.text, "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else "")

    desc_tag = (
        soup.find("meta", attrs={"name": "description"})
        or soup.find("meta", attrs={"property": "og:description"})
    )
    description = (desc_tag.get("content", "").strip() if desc_tag else "")

    return ScrapedPage(
        url=url,
        title=title,
        description=description,
        html=response.text,
    )
