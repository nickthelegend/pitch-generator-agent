from __future__ import annotations

from typing import List
from schemas import Slide
from podio_client import generate_slides as podio_generate_slides, update_slide as podio_update_slide


def generate_slides(topic: str, count: int = 5, style: str = "Modern") -> List[Slide]:
    payload = podio_generate_slides(topic=topic, count=count, style=style)
    slides = [Slide(**s) for s in payload.get("slides", [])]
    return slides


def update_slide(topic: str, instruction: str, current_slide: Slide, style: str = "Modern") -> Slide:
    payload = podio_update_slide(topic=topic, instruction=instruction, current_slide=current_slide.model_dump(), style=style)
    slide_data = payload.get("slide") or payload
    return Slide(**slide_data)
