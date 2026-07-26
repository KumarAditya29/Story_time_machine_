"""Durable Pydantic contracts shared by storage, graph, and API modules."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class StoryBible(BaseModel):
    characters_present: list[str] = Field(default_factory=list)
    character_states: dict[str, str] = Field(default_factory=dict)
    location: str = ""
    objects_facts: list[str] = Field(default_factory=list)
    established_facts: list[str] = Field(default_factory=list)
    emotional_tone: str = ""
    timeline_position: int = 0
    causal_setup: list[str] = Field(default_factory=list)
    causal_payoff_of: list[str] = Field(default_factory=list)
    reads: list[str] = Field(default_factory=list)
    writes: list[dict[str, str]] = Field(default_factory=list)


class Scene(BaseModel):
    scene_id: str
    title: str
    text: str
    order: int
    bible: StoryBible | None = None


class Dependency(BaseModel):
    source_scene_id: str
    target_scene_id: str
    kind: Literal["fact", "character", "causal", "foreshadow"]
    reason: str
    confidence: float = Field(ge=0, le=1)


class AuditEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scene_id: str
    action: Literal["edited", "checked", "regenerated", "skipped"]
    reason: str
    hop: int = 0
    before_text: str | None = None
    after_text: str | None = None
    confidence: float | None = None


class StoryVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    label: str
    parent_version_id: str | None = None
    changed_scene_ids: list[str] = Field(default_factory=list)
    audit: list[AuditEntry] = Field(default_factory=list)
    scenes_snapshot: list[Scene] = Field(default_factory=list)
    dependencies_snapshot: list[Dependency] = Field(default_factory=list)


class Story(BaseModel):
    story_id: str
    title: str
    genre: str
    logline: str
    cover_gradient: str
    scenes: list[Scene]
    dependencies: list[Dependency] = Field(default_factory=list)
    versions: list[StoryVersion] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StorySummary(BaseModel):
    story_id: str
    title: str
    genre: str
    logline: str
    cover_gradient: str
    scene_count: int
    updated_at: datetime


def summary(story: Story) -> StorySummary:
    return StorySummary(
        story_id=story.story_id,
        title=story.title,
        genre=story.genre,
        logline=story.logline,
        cover_gradient=story.cover_gradient,
        scene_count=len(story.scenes),
        updated_at=story.updated_at,
    )
