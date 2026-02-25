from __future__ import annotations

import base64
import os
import shutil
import subprocess
import tempfile
from typing import List, Optional, Tuple

from schemas import Slide, BrandKit
from slide_rendering import render_slide, DIMENSIONS
from tts_generation import generate_tts


class VideoGenerationError(RuntimeError):
    pass


def _ffmpeg_path() -> str:
    return os.getenv("FFMPEG_PATH") or shutil.which("ffmpeg") or "ffmpeg"


def _ffprobe_path() -> str:
    return os.getenv("FFPROBE_PATH") or shutil.which("ffprobe") or "ffprobe"


def _probe_duration(path: str) -> float:
    cmd = [
        _ffprobe_path(),
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 0.0
    try:
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def _write_audio_from_base64(audio_base64: str, output_path: str) -> str:
    audio_bytes = base64.b64decode(audio_base64)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    return output_path


def _estimate_duration(slide: Slide) -> float:
    if slide.duration:
        return float(slide.duration)
    word_count = len(slide.speakerNotes.split()) if slide.speakerNotes else 0
    if word_count == 0:
        return 5.0
    base = word_count / 2.2
    return max(5.0, base + 1.5)


def render_video(
    topic: str,
    slides: List[Slide],
    output_dir: str,
    format: str = "16:9",
    brand: Optional[BrandKit] = None,
    fps: int = 30,
    output_format: str = "mp4",
    generate_audio: bool = True,
    tts_language: str = "en-US",
    tts_provider: Optional[str] = None,
    tts_voice: Optional[str] = None,
) -> Tuple[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    width, height = DIMENSIONS.get(format, DIMENSIONS["16:9"])

    with tempfile.TemporaryDirectory() as temp_dir:
        segment_paths: List[str] = []

        for idx, slide in enumerate(slides):
            image_path = os.path.join(temp_dir, f"slide_{idx + 1}.png")
            render_slide(slide, image_path, format=format, brand=brand)

            audio_path = None
            if slide.audioUrl:
                audio_path = os.path.join(temp_dir, f"audio_{idx + 1}.mp3")
                _write_audio_from_base64(_strip_data_prefix(slide.audioUrl), audio_path)
            elif generate_audio and slide.speakerNotes:
                audio_base64 = generate_tts(
                    [{"speaker": "Presenter", "line": slide.speakerNotes}],
                    language=tts_language,
                )
                audio_path = os.path.join(temp_dir, f"audio_{idx + 1}.mp3")
                _write_audio_from_base64(audio_base64, audio_path)

            duration = _estimate_duration(slide)
            if audio_path:
                duration = max(duration, _probe_duration(audio_path) or duration)

            segment_path = os.path.join(temp_dir, f"segment_{idx + 1}.{output_format}")
            _render_segment(image_path, audio_path, duration, segment_path, fps, width, height, output_format)
            segment_paths.append(segment_path)

        concat_list_path = os.path.join(temp_dir, "concat.txt")
        with open(concat_list_path, "w") as f:
            for path in segment_paths:
                f.write(f"file '{path}'\n")

        filename = _safe_filename(topic) + f".{output_format}"
        output_path = os.path.join(output_dir, filename)

        cmd = [
            _ffmpeg_path(),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_list_path,
            "-c",
            "copy",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise VideoGenerationError(result.stderr or "Failed to concatenate video segments")

    return output_path, filename


def _render_segment(image_path: str, audio_path: Optional[str], duration: float, output_path: str, fps: int, width: int, height: int, output_format: str) -> None:
    cmd = [
        _ffmpeg_path(),
        "-y",
        "-loop",
        "1",
        "-i",
        image_path,
    ]

    if audio_path:
        cmd += ["-i", audio_path]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]

    cmd += [
        "-t",
        f"{duration}",
        "-r",
        f"{fps}",
        "-s",
        f"{width}x{height}",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise VideoGenerationError(result.stderr or "Failed to render video segment")


def _safe_filename(text: str) -> str:
    keep = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text.strip())
    return keep.strip("_") or "presentation"


def _strip_data_prefix(audio_data: str) -> str:
    if audio_data.startswith("data:"):
        return audio_data.split(",", 1)[1]
    return audio_data
