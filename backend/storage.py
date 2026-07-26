"""Small JSON repository: one portable file per story."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

from .models import Story, StorySummary, summary

DATA_DIR = Path(__file__).parent / "data" / "stories"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def story_path(story_id: str) -> Path:
    if not story_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Invalid story id")
    return DATA_DIR / f"{story_id}.json"


def save_story(story: Story) -> Story:
    ensure_data_dir()
    story.updated_at = datetime.now(timezone.utc)
    story_path(story.story_id).write_text(story.model_dump_json(indent=2), encoding="utf-8")
    return story


def get_story(story_id: str) -> Story:
    path = story_path(story_id)
    if not path.exists():
        raise FileNotFoundError(story_id)
    return Story.model_validate(json.loads(path.read_text(encoding="utf-8")))


def list_stories() -> list[StorySummary]:
    ensure_data_dir()
    return sorted((summary(get_story(path.stem)) for path in DATA_DIR.glob("*.json")), key=lambda item: item.title)


def story_exists(story_id: str) -> bool:
    return story_path(story_id).exists()
