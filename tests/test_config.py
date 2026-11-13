import json
from pathlib import Path

def test_topics():
    topics = json.loads((Path(__file__).parents[1] / "config/topics.json").read_text())
    assert topics and all(t.get("title") and t.get("points") for t in topics)
