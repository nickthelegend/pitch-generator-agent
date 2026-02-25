from __future__ import annotations

import os
from typing import Any, Dict
import httpx


class PodioAIError(RuntimeError):
    pass


def _base_url() -> str:
    return os.getenv("PODIO_AI_BASE_URL", "http://localhost:3002").rstrip("/")


def _post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{_base_url()}{path}"
    try:
        with httpx.Client(timeout=90) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        raise PodioAIError(f"Podio AI request failed: {exc}") from exc


def generate_slides(topic: str, count: int = 5, style: str = "Modern") -> Dict[str, Any]:
    return _post("/api/slides/generate", {
        "topic": topic,
        "count": count,
        "style": style,
    })


def update_slide(topic: str, instruction: str, current_slide: Dict[str, Any], style: str = "Modern") -> Dict[str, Any]:
    return _post("/api/slides/update", {
        "topic": topic,
        "instruction": instruction,
        "currentSlide": current_slide,
        "style": style,
    })


def generate_tts(script: list[dict], language: str = "en-US") -> Dict[str, Any]:
    return _post("/api/podcast/tts", {
        "script": script,
        "language": language,
    })
def save_project(project_id: str, topic: str, slides: list[dict], has_video: bool = True) -> Dict[str, Any]:
    content = {
        "projectId": project_id,
        "topic": topic,
        "style": "Modern",
        "format": "16:9",
        "slides": slides,
        "hasVideo": has_video,
    }
    return _post("/api/project/save", {
        "projectId": project_id,
        "title": topic,
        "content": content
    })
