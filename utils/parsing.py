"""Parsing helpers for article text."""
from __future__ import annotations

import re


def clean_article_text(raw_text: str) -> str:
    """
    Normalize whitespace in the article text and trim it.
    """
    if not raw_text:
        return ""
    cleaned = re.sub(r"\s+", " ", raw_text)
    return cleaned.strip()
