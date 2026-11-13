"""Manual private-only upload of an already-reviewed video."""
import json
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    if not os.getenv("YOUTUBE_TOKEN_JSON"):
        raise RuntimeError("YOUTUBE_TOKEN_JSON must be supplied securely")
    if not (OUT / "video.mp4").exists():
        raise FileNotFoundError("Review and provide output/video.mp4 before upload")
    credentials = Credentials.from_authorized_user_info(
        json.loads(os.environ["YOUTUBE_TOKEN_JSON"]), SCOPES)
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise RuntimeError("Invalid OAuth credentials")
    youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    script = json.loads((OUT / "script.json").read_text())
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": script["title"][:100],
                        "description": script["description"][:4900],
                        "categoryId": "28"},
            "status": {"privacyStatus": "private",
                       "selfDeclaredMadeForKids": False},
        },
        media_body=MediaFileUpload(str(OUT / "video.mp4"),
                                   mimetype="video/mp4", resumable=True))
    result = None
    while result is None:
        _, result = request.next_chunk()
    print("Uploaded privately. Video ID:", result["id"])
    thumb = OUT / "thumbnail.png"
    if thumb.exists():
        youtube.thumbnails().set(
            videoId=result["id"],
            media_body=MediaFileUpload(str(thumb), mimetype="image/png")).execute()

if __name__ == "__main__":
    main()
