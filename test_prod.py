import os
import time
from slide_generation import generate_slides
from tts_generation import generate_tts
from video_generation import render_video
from schemas import Slide

print("Starting PROD test without mocks...")
topic = "Prod Deployment Verification"

print(f"\n1. Generating slides for: {topic}")
slides = generate_slides(topic, count=2, style="Modern")
print(f"Generated {len(slides)} slides successfully.")
for i, s in enumerate(slides):
    print(f" Slide {i+1}: {s.title} - {len(s.speakerNotes)} chars of notes")

print("\n2. Generating Audio (TTS) for the first slide...")
notes = slides[0].speakerNotes or "Welcome to the test."
script = [{"speaker": "Presenter", "line": notes}]
audio_b64 = generate_tts(script, language="en-US")
print(f"Generated TTS audio base64, length: {len(audio_b64)}")

# Inject audio back to slide for video render
slides[0].audioUrl = f"data:audio/mp3;base64,{audio_b64}"

print("\n3. Rendering Video...")
output_dir = os.path.join(os.getcwd(), "outputs")
video_path, filename = render_video(
    topic=topic,
    slides=slides,
    output_dir=output_dir,
    format="16:9",
    fps=30,
    output_format="mp4",
    generate_audio=False # we already did it manually for slide 1 or it will do it automatically
)

print(f"\n✅ PROD test complete! Video successfully rendered at: {video_path}")
print(f"Filename: {filename}")
