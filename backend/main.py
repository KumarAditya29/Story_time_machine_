from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .generation import analyze_story
from .graph_engine import build_graph
from .models import Scene, Story, StoryVersion, summary
from .seed_data import seed_stories
from .storage import get_story, list_stories, save_story, story_exists
from .versioning import edit_scene


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_stories()
    yield


app = FastAPI(title="Story Time Machine", version="1.0.0", lifespan=lifespan)
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


class CreateScene(BaseModel):
    title: str = Field(min_length=1)
    text: str = Field(min_length=1)


class CreateStoryRequest(BaseModel):
    title: str = Field(min_length=1)
    genre: str = Field(min_length=1)
    logline: str = Field(min_length=1)
    scenes: list[CreateScene] = Field(min_length=2)


class EditRequest(BaseModel):
    text: str = Field(min_length=1)
    label: str | None = None


def fetch(story_id: str) -> Story:
    try:
        return get_story(story_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Story not found") from error


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/stories")
def stories():
    return list_stories()


@app.post("/api/stories", status_code=201)
def create_story(request: CreateStoryRequest) -> Story:
    story_id = "-".join("".join(char.lower() if char.isalnum() else " " for char in request.title).split())
    story_id = f"{story_id}-{uuid4().hex[:5]}"
    story = Story(story_id=story_id, title=request.title, genre=request.genre, logline=request.logline,
                  cover_gradient="linear-gradient(135deg,#2563eb,#a855f7)",
                  scenes=[Scene(scene_id=f"s{index:02d}", title=scene.title, text=scene.text, order=index)
                          for index, scene in enumerate(request.scenes, 1)])
    story.versions = [StoryVersion(label="Original draft", scenes_snapshot=story.scenes)]
    return save_story(story)


@app.get("/api/stories/{story_id}")
def story(story_id: str) -> Story:
    return fetch(story_id)


@app.post("/api/stories/{story_id}/analyze")
def analyze(story_id: str) -> Story:
    try:
        return save_story(analyze_story(fetch(story_id)))
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.post("/api/stories/{story_id}/scenes/{scene_id}/edit")
def edit(story_id: str, scene_id: str, request: EditRequest) -> Story:
    try:
        return edit_scene(story_id, scene_id, request.text, request.label)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.get("/api/stories/{story_id}/graph")
def graph(story_id: str):
    item = fetch(story_id)
    graph_data = build_graph(item)
    return {
        "nodes": [{"id": scene.scene_id, "title": scene.title, "order": scene.order,
                   "analyzed": scene.bible is not None} for scene in item.scenes],
        "edges": [{"id": f"{left}-{right}", "source": left, "target": right, **data}
                  for left, right, data in graph_data.edges(data=True)],
    }


# Databricks Apps serves this FastAPI process as the single public application.
# The frontend build is copied to backend/static during the Databricks build step.
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
