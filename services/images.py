"""Preview image generation (placeholder by default)."""
from __future__ import annotations

from typing import List

from PIL import Image, ImageDraw, ImageFont


CANVAS_SIZE = (1080, 1920)
BACKGROUND = (24, 24, 24)
TEXT_COLOR = (240, 240, 240)


def _draw_centered_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, canvas_size):
    width, height = canvas_size
    text = "\n".join(_wrap_text(text, 28))
    text_bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.multiline_text(position, text, font=font, fill=TEXT_COLOR, align="center", spacing=6)


def _wrap_text(text: str, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current: List[str] = []
    for word in words:
        if len(" ".join(current + [word])) <= max_width:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines or [text]


def generate_preview_images(prompts: List[str]) -> List[Image.Image]:
    """
    Generate placeholder images for the supplied prompts.
    """
    images: List[Image.Image] = []
    if not prompts:
        return images

    try:
        font = ImageFont.load_default()
    except Exception:  # pragma: no cover - fallback
        font = ImageFont.load_default()

    for prompt in prompts:
        img = Image.new("RGB", CANVAS_SIZE, BACKGROUND)
        draw = ImageDraw.Draw(img)
        _draw_centered_text(draw, prompt, font, CANVAS_SIZE)
        images.append(img)

    return images
