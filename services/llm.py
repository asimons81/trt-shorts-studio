"""Gemini 2.5 Flash integration for short package generation."""
from __future__ import annotations

import json
import os
from typing import Dict, Any

import google.generativeai as genai

try:  # Streamlit is optional for non-UI contexts
    import streamlit as st
except ImportError:  # pragma: no cover - fallback when Streamlit isn't available
    st = None  # type: ignore


MODEL_NAME = "gemini-2.0-flash"


def _get_api_key() -> str:
    if st is not None:
        api_key = st.secrets.get("GEMINI_API_KEY", "")  # type: ignore[attr-defined]
        if api_key:
            return api_key
    return os.environ.get("GEMINI_API_KEY", "")


def _ensure_keys(pkg: Dict[str, Any]) -> Dict[str, Any]:
    defaults = {
        "summary": "",
        "concepts": [],
        "script": "",
        "onscreen_text": [],
        "visual_ideas": [],
        "title": "",
        "description": "",
        "tags": [],
    }
    for key, default in defaults.items():
        pkg.setdefault(key, default)
    # Normalize list fields
    for list_key in ["concepts", "onscreen_text", "visual_ideas", "tags"]:
        value = pkg.get(list_key)
        if isinstance(value, str):
            pkg[list_key] = [v.strip() for v in value.split("\n") if v.strip()]
        elif not isinstance(value, list):
            pkg[list_key] = []
    return pkg


def generate_short_package(article_text: str, topic_hint: str = "") -> Dict[str, Any]:
    """
    Generate a Short package from article text using Gemini 2.5 Flash.
    """
    if not article_text:
        raise ValueError("Article text is required to generate a short package.")

    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=MODEL_NAME)

    prompt = {
        "role": "user",
        "parts": [
            "You are a YouTube Shorts writer for the channel 'Tony Reviews Things'.",
            "Create a JSON object with keys: summary, concepts, script, onscreen_text, visual_ideas, title, description, tags.",
            "Rules:",
            "- summary: 1-2 sentences summarizing the source article.",
            "- concepts: 2-3 possible short angles/hooks.",
            "- script: 30-45 second voiceover, concise, no greetings like 'Hey guys'.",
            "- onscreen_text: 3-8 short phrases, a few words each.",
            "- visual_ideas: 4-8 prompts for B-roll or AI clips (Sora/Runway/Imagen style).",
            "- title: compelling YouTube title.",
            "- description: concise video description.",
            "- tags: list of keywords.",
            "If topic_hint is provided, align the angle accordingly.",
            f"topic_hint: {topic_hint or 'None provided'}",
            "Article text:",
            article_text,
            "Return only valid JSON with no explanations.",
        ],
    }

    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    except Exception as exc:  # pragma: no cover - depends on external service
        raise RuntimeError(f"Failed to generate content with Gemini: {exc}") from exc

    raw_text = getattr(response, "text", None) or str(response)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini response was not valid JSON.") from exc

    pkg = _ensure_keys(data)
    return pkg
