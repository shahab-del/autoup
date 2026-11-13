# Cloud-only YouTube production: setup

## First: privacy
The repository is currently PUBLIC. Change visibility via GitHub Settings > General > Danger Zone > Change visibility if you want it private. Never commit secrets, tokens or client_secret.json.

## OpenAI
Create an API key at https://platform.openai.com/ and set a project budget.
In GitHub Settings > Secrets and variables > Actions, add secret OPENAI_API_KEY.
OpenAI API usage is separate from ChatGPT subscription billing.

## Generate the first video
This starter is manual-run only; it does not schedule publishing.
Open Actions > Build YouTube draft > Run workflow > topic_index=0.
The completed job produces an artifact ZIP with video.mp4, script.json, thumbnail.png, and individual audio/scenes.
Download and check content for correctness, originality, narration timing and quality before publishing.

## YouTube connection
Create a Google Cloud project, enable YouTube Data API v3, configure OAuth consent and a Desktop OAuth client. Download credentials to client_secret.json *on your own computer* (not in Git).
Clone the repository locally, install requirements and run python -m src.auth_local.
Authenticate the intended YouTube channel. Save the token as a secret, never a tracked file.
For a reviewed local output directory, run python -m src.upload with YOUTUBE_TOKEN_JSON set securely.
The uploader always uses privacyStatus=private; make content public manually in YouTube Studio after review.
Some unverified YouTube API projects may be restricted to private uploads.

## Notes
There is no automated research from live sources or factual verification yet.
The AI creates narrated slide videos, not live app demonstrations or photorealistic footage.
Avoid misleading claims that tools have been tested. YouTube can reject repetitive/mass-produced low-value content.
Next steps: citation-backed research, motion graphics, captions, duplicate detection, quality gate and cost tracking.
