# The Workflow Lab — cloud video automation

Cloud-only YouTube video pipeline. Initial state: private-ready, manual runs only; does not publish automatically.

## Flow

1. AI creates a script and factual verification checklist from a curated topic.
2. Narration via OpenAI TTS.
3. Pillow creates branded scenes and thumbnails.
4. FFmpeg renders an MP4.
5. GitHub Actions retains files as downloadable artifacts.
6. Optional YouTube API upload (private only) after OAuth setup.

See `docs/SETUP.md`. Do not commit API keys, OAuth refresh tokens, or generated private data. AI-generated content must be checked for factual errors and repetitive/low-value output before publication.
