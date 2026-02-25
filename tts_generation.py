from __future__ import annotations

import base64
from typing import List
from podio_client import generate_tts as podio_generate_tts


class TTSGenerationError(RuntimeError):
    pass


def generate_tts(lines: List[dict], language: str = "en-US") -> str:
    payload = podio_generate_tts(script=lines, language=language)
    audio = payload.get("audio")
    if not audio:
        raise TTSGenerationError("No audio generated from podio-ai TTS")
    # validate base64
    try:
        base64.b64decode(audio)
    except Exception as exc:
        raise TTSGenerationError(f"Invalid audio base64: {exc}") from exc
    return audio
