from __future__ import annotations

import os
import re
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from schemas import Slide, BrandKit


DIMENSIONS = {
    "16:9": (1280, 720),
    "4:5": (1080, 1350),
    "9:16": (720, 1280),
}


def render_slide(slide: Slide, output_path: str, format: str = "16:9", brand: Optional[BrandKit] = None) -> str:
    width, height = DIMENSIONS.get(format, DIMENSIONS["16:9"])
    image = Image.new("RGB", (width, height), slide.backgroundColor or "#0a0a0f")

    if slide.gradient:
        colors = _extract_gradient_colors(slide.gradient)
        if colors:
            image = _draw_vertical_gradient(width, height, colors[0], colors[-1])

    draw = ImageDraw.Draw(image)

    accent = (brand.primaryColor if brand and brand.primaryColor else slide.accentColor) or "#ec4899"
    text_color = slide.textColor or "#ffffff"

    title_font = _load_font(54, bold=True)
    body_font = _load_font(28, bold=False)
    small_font = _load_font(20, bold=False)

    padding_x = 80
    padding_y = 60

    if slide.layoutType == "title":
        _draw_centered_text(draw, slide.title, title_font, text_color, width, height * 0.4)
        subtitle = slide.subtitle or slide.description or (slide.bullets[0] if slide.bullets else "")
        if subtitle:
            _draw_centered_text(draw, subtitle, body_font, _fade_color(text_color, 0.7), width, height * 0.55)
    elif slide.layoutType == "statistics":
        draw.text((padding_x, padding_y), slide.title, font=title_font, fill=text_color)
        stats = slide.bullets[:4]
        grid_top = padding_y + 120
        col_width = (width - 2 * padding_x) // 2
        row_height = 160
        for idx, stat in enumerate(stats):
            col = idx % 2
            row = idx // 2
            x = padding_x + col * col_width
            y = grid_top + row * row_height
            value, label = _split_stat(stat)
            draw.text((x, y), value, font=title_font, fill=accent)
            if label:
                draw.text((x, y + 70), label, font=small_font, fill=_fade_color(text_color, 0.75))
    elif slide.layoutType == "conclusion":
        _draw_centered_text(draw, slide.title, title_font, text_color, width, height * 0.35)
        tags = slide.bullets
        if tags:
            _draw_tag_cloud(draw, tags, width, height * 0.55, accent, text_color)
    else:
        draw.text((padding_x, padding_y), slide.title, font=title_font, fill=text_color)
        content_top = padding_y + 120
        bullets = slide.bullets or []
        for idx, bullet in enumerate(bullets):
            bullet_lines = _wrap_text(bullet, body_font, width - padding_x * 2 - 40)
            y = content_top + idx * 80
            draw.rectangle([padding_x, y + 8, padding_x + 8, y + 24], fill=accent)
            draw.text((padding_x + 24, y), bullet_lines[0], font=body_font, fill=text_color)
            if len(bullet_lines) > 1:
                for i, line in enumerate(bullet_lines[1:], start=1):
                    draw.text((padding_x + 24, y + i * 32), line, font=body_font, fill=text_color)

    if brand and brand.name:
        draw.text((padding_x, height - 40), brand.name.upper(), font=small_font, fill=accent)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)
    return output_path


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = []
    for word in words:
        current.append(word)
        line = " ".join(current)
        if font.getlength(line) > max_width:
            current.pop()
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _draw_centered_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, fill: str, width: int, y: float) -> None:
    lines = _wrap_text(text, font, int(width * 0.8))
    total_height = len(lines) * (font.size + 8)
    start_y = y - total_height / 2
    for idx, line in enumerate(lines):
        line_width = font.getlength(line)
        draw.text(((width - line_width) / 2, start_y + idx * (font.size + 8)), line, font=font, fill=fill)


def _extract_gradient_colors(gradient: str) -> List[str]:
    return re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}", gradient)


def _draw_vertical_gradient(width: int, height: int, start_color: str, end_color: str) -> Image.Image:
    base = Image.new("RGB", (width, height), start_color)
    top = Image.new("RGB", (width, height), end_color)
    mask = Image.new("L", (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base


def _split_stat(text: str) -> Tuple[str, str]:
    if ":" in text:
        parts = text.split(":", 1)
        return parts[0].strip(), parts[1].strip()
    return text.strip(), ""


def _draw_tag_cloud(draw: ImageDraw.ImageDraw, tags: List[str], width: int, start_y: float, accent: str, text_color: str) -> None:
    x = 80
    y = start_y
    font = _load_font(24)
    for tag in tags:
        w = font.getlength(tag) + 32
        h = font.size + 16
        if x + w > width - 80:
            x = 80
            y += h + 12
        draw.rounded_rectangle([x, y, x + w, y + h], radius=20, outline=accent, width=2)
        draw.text((x + 16, y + 8), tag, font=font, fill=text_color)
        x += w + 12


def _fade_color(color: str, factor: float) -> str:
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join([c * 2 for c in color])
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"
