"""OpenAI-backed story-bible extraction. Regeneration functions arrive in Milestone 3."""
from __future__ import annotations

import os
from typing import Iterable

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from .models import Scene, Story, StoryBible
from .graph_engine import build_dependencies

load_dotenv()


class StateWrite(BaseModel):
    state_var_id: str = Field(description="stable snake_case fact or character-state id")
    new_value: str


class CharacterState(BaseModel):
    character: str
    state: str


class ExtractedBible(BaseModel):
    characters_present: list[str]
    # JSON-schema structured outputs require closed objects, so a list is used
    # at the API boundary and converted back to the durable dict contract below.
    character_states: list[CharacterState]
    location: str
    objects_facts: list[str]
    established_facts: list[str]
    emotional_tone: str
    causal_setup: list[str]
    causal_payoff_of: list[str]
    reads: list[str]
    writes: list[StateWrite]


class VerificationDecision(BaseModel):
    needs_change: bool
    reason: str
    required_change: str


class MinimalRewrite(BaseModel):
    rewritten_text: str


SYSTEM_PROMPT = """You are a meticulous narrative continuity editor. Extract only facts established or required by this atomic scene. Use stable, reusable snake_case IDs for reads/writes (for example bob_has_letter, alice_trusts_bob). Do not invent plot facts. causal_setup is what this scene plants for later; causal_payoff_of is an earlier thread resolved here."""


def _client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to .env before running story analysis.")
    # Never leave the writer interface spinning forever if an upstream request stalls.
    return OpenAI(timeout=35.0, max_retries=1)


def extract_state(scene_text: str, timeline_position: int, neighbor_context: Iterable[str] = ()) -> StoryBible:
    context = "\n".join(f"- {item}" for item in neighbor_context)
    prompt = f"""Scene position: {timeline_position}\nScene text:\n{scene_text}\n\nAdjacent scene context (do not extract their facts):\n{context or '(none)'}"""
    completion = _client().beta.chat.completions.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        response_format=ExtractedBible,
        temperature=0,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError("OpenAI returned no structured story-bible data")
    return StoryBible(
        **parsed.model_dump(exclude={"writes", "character_states"}),
        character_states={item.character: item.state for item in parsed.character_states},
        timeline_position=timeline_position,
        writes=[item.model_dump() for item in parsed.writes],
    )


def extract_scene(scene: Scene, neighbors: Iterable[Scene] = ()) -> Scene:
    scene.bible = extract_state(scene.text, scene.order, [neighbor.text for neighbor in neighbors])
    return scene


def analyze_story(story: Story) -> Story:
    """Populate the story bible once per scene, then derive the persisted graph."""
    ordered = sorted(story.scenes, key=lambda item: item.order)
    for index, scene in enumerate(ordered):
        neighbors = [candidate for candidate in (ordered[index - 1:index] + ordered[index + 1:index + 2])]
        extract_scene(scene, neighbors)
    story.dependencies = build_dependencies(story)
    return story


def verify_scene(original_edited_text: str, new_edited_text: str, delta: list[str], candidate: Scene,
                 dependency_reason: str, hop: int) -> VerificationDecision:
    prompt = f"""An upstream scene was edited. Decide if the candidate scene truly requires revision for continuity.

Original upstream scene:\n{original_edited_text}

Edited upstream scene:\n{new_edited_text}

Specific metadata delta:\n{chr(10).join('- ' + item for item in delta)}

Candidate scene (do not rewrite it yet):\n{candidate.text}

Graph connection: {dependency_reason}; propagation hop: {hop}.

Say needs_change=false unless a concrete inconsistency exists. If true, name only the minimum required change."""
    completion = _client().beta.chat.completions.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "system", "content": "You are a strict narrative continuity verifier. Avoid unnecessary rewrites."},
                  {"role": "user", "content": prompt}], response_format=VerificationDecision, temperature=0,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError("OpenAI returned no verification decision")
    return parsed


def regenerate_scene(original_text: str, delta: list[str], neighbor_context: Iterable[str]) -> str:
    prompt = f"""Rewrite the following story scene only where necessary to accommodate the specific upstream delta.
Preserve voice, pacing, facts not affected by the delta, and as much exact wording as possible. Do not add explanation.

Upstream delta:\n{chr(10).join('- ' + item for item in delta)}

Neighboring untouched scenes for voice only:\n{chr(10).join('- ' + item for item in neighbor_context)}

Original scene:\n{original_text}"""
    completion = _client().beta.chat.completions.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "system", "content": "You are a minimal-change fiction editor. Make the smallest consistency repair possible."},
                  {"role": "user", "content": prompt}], response_format=MinimalRewrite, temperature=0.2,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError("OpenAI returned no rewritten scene")
    return parsed.rewritten_text
