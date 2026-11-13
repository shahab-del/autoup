"""Create an illustrated, narrated YouTube video from a curated topic."""
import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
W, H = 1280, 720

def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def graphic(title, subtitle, path, thumbnail=False):
    image = Image.new("RGB", (W, H), "#101927")
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((45, 45, 1235, 675), radius=26, outline="#285263", width=3)
    d.rectangle((75, 80, 94, 145), fill="#3DE0BC")
    d.text((116, 84), "THE WORKFLOW LAB", font=font(32), fill="#3DE0BC")
    size = 68 if thumbnail else 56
    lines = textwrap.wrap(title, width=27 if thumbnail else 32)[:5]
    for n, line in enumerate(lines):
        d.text((75, 180 + n * (size + 12)), line, font=font(size), fill="#F4F7FA")
    d.text((78, 619), subtitle[:85], font=font(23), fill="#A8C5CC")
    image.save(path)

def generate_script(client, topic):
    instructions = (
        "Write an original, useful YouTube explainer based ONLY on the provided topic. "
        "Respond with valid JSON, no markdown, with title (string), description (string), "
        "scenes (array of 5-7 objects with heading, narration, takeaway strings). "
        "Write about 90-140 spoken words per scene. Each heading max 55 characters, "
        "each takeaway max 85 characters. Avoid unverifiable news, made-up statistics, "
        "claims to have tested products, fictional first-hand experiences, or income promises. "
        "Explain uncertainty where necessary. Description must note AI-assisted narration."
    )
    response = client.responses.create(
        model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini"),
        input=[{"role": "system", "content": instructions},
               {"role": "user", "content": json.dumps(topic)}],
        max_output_tokens=3800,
    )
    raw = response.output_text.strip()
    if raw.startswith(""+chr(96)*3):
        raw = raw.split("\n", 1)[1].rsplit(chr(96)*3, 1)[0]
    result = json.loads(raw)
    if not (5 <= len(result.get("scenes", [])) <= 7):
        raise ValueError("Invalid scene count")
    for scene in result["scenes"]:
        if not all(isinstance(scene.get(k), str) and scene[k].strip()
                   for k in ("heading", "narration", "takeaway")):
            raise ValueError("Incomplete scene")
    return result

def audio_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True)
    return max(1, float(result.stdout.strip()))

def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe required")
    topic_index = int(os.getenv("TOPIC_INDEX", "0"))
    topics = json.loads((ROOT / "config/topics.json").read_text())
    if not 0 <= topic_index < len(topics):
        raise ValueError("Invalid TOPIC_INDEX")
    OUT.mkdir(exist_ok=True)
    client = OpenAI()
    script = generate_script(client, topics[topic_index])
    (OUT / "script.json").write_text(json.dumps(script, indent=2), encoding="utf-8")
    graphic(script["title"], "AI + PRODUCTIVITY", OUT / "thumbnail.png", True)
    clips = []
    for i, scene in enumerate(script["scenes"]):
        image = OUT / f"scene_{i:02}.png"
        audio = OUT / f"voice_{i:02}.mp3"
        clip = OUT / f"clip_{i:02}.mp4"
        graphic(scene["heading"], scene["takeaway"], image)
        with client.audio.speech.with_streaming_response.create(
            model=os.getenv("OPENAI_TTS_MODEL", "tts-1"),
            voice=os.getenv("OPENAI_VOICE", "alloy"),
            input=scene["narration"],
            response_format="mp3"
        ) as response:
            response.stream_to_file(audio)
        duration = audio_duration(audio)
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-loop", "1", "-framerate", "24", "-i", str(image),
             "-i", str(audio), "-t", str(duration), "-c:v", "libx264",
             "-preset", "veryfast", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", "-shortest", str(clip)],
            check=True,
        )
        clips.append(clip)
    (OUT / "concat.txt").write_text(
        "".join("file '" + p.name + "'\n" for p in clips), encoding="utf-8")
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "concat", "-safe", "0", "-i", str(OUT / "concat.txt"),
         "-c", "copy", str(OUT / "video.mp4")],
        check=True,
    )
    print("Draft video created in output/video.mp4")

if __name__ == "__main__":
    main()
