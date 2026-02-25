# 🎙️ Pitch Generator Agent

A fully autonomous Masumi-compatible Agent that generates breathtaking, visually stunning slide decks and synchronized voiceover presentations based on a simple text prompt. 

## ⚡ Overview

The **Pitch Generator Agent** orchestrates an end-to-end multimedia creation pipeline. Rather than struggling with primitive Python rendering libraries, this agent natively hooks directly into the **Podio AI Next.js frontend** and its incredibly powerful React `<Remotion>` framework. This ensures that every presentation benefits from beautiful HTML/CSS components (e.g., glassmorphism, glowing custom gradients) crafted dynamically via Gemini 2.0 Flash instead of boring static images.

### Pipeline Flow:
1. **Topic Generation**: Accepts a user prompt (e.g., "The impact of AI on the job market").
2. **Slide Architecting**: Pings the `podio-ai` API backend (powered by Gemini Flash) to build complex HTML/CSS visual slides and associated speaker notes.
3. **Text-to-Speech (TTS) Synthesis**: Processes the speaker notes using Google Cloud TTS to generate synchronized MP3 voiceovers, mathematically adjusting the duration of each slide to match the audio playback perfectly.
4. **Decentralized Storage**: Backs up the raw generated layout schemas natively into the `podio-ai` PostgreSQL database (via Supabase).
5. **Remotion Compilation**: Programmatically triggers an invisible headless Chromium process (`npx remotion render`) locally within your Next.js directory to stitch together a perfect `16:9` MP4 export complete with audio, animations, and transitions.
6. **Web3 IPFS Publishing**: Safely uploads the finished `.mp4` into decentralized storage via **Pinata**, returning the final IPFS hash alongside a local deep link for playback!

---

## 🛠️ Requirements & Setup

1. **Environment Setup**: Ensure your Python `3.12+` virtual environment is ready:
   ```bash
   python -m venv .venv312
   source .venv312/bin/activate
   pip install -r requirements.txt
   ```

2. **Podio-AI Frontend**: Your Next.js web application **must** be actively running in the background for this agent to successfully process API calls:
   ```bash
   cd ../podio-ai
   npm install zod@3.22.3  # Required for Remotion compatibility
   npm run dev
   ```

3. **Configure Environment Variables**:
   Copy the example environment file and add your credentials:
   ```bash
   cp .env.example .env
   ```
   **Important Keys:**
   - `PODIO_AI_BASE_URL`: Must point to your running frontend (e.g., `http://localhost:3002`)
   - `PINATA_JWT`: Your Pinata JWT string for IPFS deployment.
   - `PAYMENT_SERVICE_URL` & `PAYMENT_API_KEY`: Needed if enabling live ADA deposits via Masumi integration.

---

## 🚀 Running the Agent

### Start the API Server
To expose the `FastAPI` instance and `/start_job` endpoints (standard Masumi Protocol):
```bash
python main.py api
```

### Standalone Local Execution (Testing)
Run a hardcoded agent pipeline prompt locally to quickly test the pipeline:
```bash
masumi run
# OR
python main.py
```

### Expected Output
When execution successfully completes, the agent will spit out the following payload:
```
======================================================================
✅ Crew Output:
======================================================================

Presentation Generated Successfully!
View and Export your Remotion Video here: http://localhost:3002/project/e9748142-1fca-4a08-bcb2-038459b6e10f/export
IPFS Backup URL (Pinata): ipfs://QmewE8FjNssfn5gpFHXou2dzNdZzBmztXpb8mqsBPq9gxU

======================================================================
```
