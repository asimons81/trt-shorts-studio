"""Helpers to fetch article content from WordPress."""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from utils.parsing import clean_article_text


def fetch_article(url: str) -> str:
    """
    Given a TonyReviewsThings article URL, fetch the HTML and extract the main article text.

    Implementation:
    - Use requests.get(url, timeout=10).
    - Use BeautifulSoup to parse HTML.
    - Remove <script> and <style> tags.
    - Extract text from the main content area. Fall back to body text.
    """
    if not url:
        raise ValueError("URL is required to fetch article content.")

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    body = soup.body
    if body:
        text = body.get_text(separator=" ", strip=True)
    else:
        text = soup.get_text(separator=" ", strip=True)

    return clean_article_text(text)
