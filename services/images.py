import io
from typing import List
from PIL import Image, ImageDraw


def generate_preview_images(prompts: List[str]) -> List[bytes]:
    """
    Given a small list of visual prompts, generate simple placeholder images
    that display the prompt text. This avoids needing any external image API
    and lets the Streamlit app show something in the Visuals tab.

    Each image is 1080x1920 with a dark background and white text.
    """
    images: List[bytes] = []

    for prompt in prompts:
        # Create a blank dark image
        img = Image.new("RGB", (1080, 1920), color=(20, 24, 28))
        draw = ImageDraw.Draw(img)

        # Truncate text so it fits reasonably
        text = prompt.strip()
        if len(text) > 160:
            text = text[:157] + "..."

        # Compute simple centered position
        try:
            # Pillow >= 8.0 has multiline_textbbox
            bbox = draw.multiline_textbbox((0, 0), text, align="center")
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Fallback: approximate sizing by splitting lines
            lines = text.split("\n")
            # Rough approximation: 20px per character wide, 30px per line high
            max_len = max(len(line) for line in lines) if lines else 0
            text_width = max_len * 20
            text_height = len(lines) * 30

        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2

        # Draw the prompt text in white
        draw.multiline_text((x, y), text, fill=(255, 255, 255), align="center")

        # Convert to a PNG byte payload so Streamlit can reliably render
        # and store the previews in session state without serialization
        # issues.
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        images.append(buffer.getvalue())

    return images
