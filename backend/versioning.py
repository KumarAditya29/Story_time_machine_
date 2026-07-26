"""Safe versioned story edits with LLM verification before every rewrite."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from .generation import analyze_story, extract_scene, regenerate_scene, verify_scene
from .graph_engine import blast_radius, build_dependencies
from .models import AuditEntry, Scene, Story, StoryVersion
from .storage import get_story, save_story


def _items(value: object) -> set[str]:
    if isinstance(value, dict):
        return {f"{key}={item}" for key, item in value.items()}
    if isinstance(value, list):
        return {str(item) for item in value}
    return {str(value)} if value else set()


def metadata_delta(before: Scene, after: Scene) -> list[str]:
    if not before.bible or not after.bible:
        return ["scene text changed; metadata must be reconciled"]
    changes: list[str] = []
    before_data, after_data = before.bible.model_dump(), after.bible.model_dump()
    for field in before_data:
        removed = _items(before_data[field]) - _items(after_data[field])
        added = _items(after_data[field]) - _items(before_data[field])
        changes.extend(f"{field}: removed {item}" for item in sorted(removed))
        changes.extend(f"{field}: added {item}" for item in sorted(added))
    return changes or ["text wording changed with no extracted continuity-state delta"]


def _scene(story: Story, scene_id: str) -> Scene:
    return next((scene for scene in story.scenes if scene.scene_id == scene_id), None) or (_ for _ in ()).throw(ValueError(f"Unknown scene: {scene_id}"))


def _neighbors(story: Story, scene: Scene) -> list[str]:
    ordered = sorted(story.scenes, key=lambda item: item.order)
    index = ordered.index(scene)
    return [item.text for item in (ordered[max(0, index - 1):index] + ordered[index + 1:index + 2])]


def edit_scene(story_id: str, scene_id: str, new_text: str, label: str | None = None) -> Story:
    story = get_story(story_id)
    # An edit must always start from a complete pre-edit story bible/graph.
    # Otherwise the first edit of an unmapped story has no causal history to traverse.
    if any(scene.bible is None for scene in story.scenes):
        analyze_story(story)
    original_story = deepcopy(story)
    target = _scene(story, scene_id)
    original_target = deepcopy(target)
    target.text = new_text.strip()
    extract_scene(target, [scene for scene in story.scenes if abs(scene.order - target.order) == 1])
    delta = metadata_delta(original_target, target)
    audit = [AuditEntry(scene_id=scene_id, action="edited", reason="; ".join(delta), before_text=original_target.text, after_text=target.text)]

    # Candidate selection uses the UNION of the pre- and post-edit graph. The old
    # links are crucial when an edit removes a fact/setup: rebuilding first would
    # disconnect precisely the scenes whose continuity must be checked.
    updated_dependencies = build_dependencies(story)
    previous_dependencies = original_story.dependencies
    union = {(edge.source_scene_id, edge.target_scene_id, edge.kind): edge for edge in previous_dependencies}
    union.update({(edge.source_scene_id, edge.target_scene_id, edge.kind): edge for edge in updated_dependencies})
    candidate_story = deepcopy(story)
    candidate_story.dependencies = list(union.values())
    candidates = blast_radius(candidate_story, scene_id, max_hops=3)
    thresholds = {1: 0.35, 2: 0.62, 3: 0.82}
    changed_ids = [scene_id]
    for candidate in candidates:
        current = _scene(story, candidate.scene_id)
        required_confidence = thresholds.get(candidate.hop, 0.95)
        if candidate.confidence < required_confidence:
            audit.append(AuditEntry(scene_id=current.scene_id, action="skipped", hop=candidate.hop,
                                    confidence=candidate.confidence, reason=f"Below hop-{candidate.hop} confidence threshold"))
            continue
        decision = verify_scene(original_target.text, target.text, delta, current, candidate.dependency_reason, candidate.hop)
        audit.append(AuditEntry(scene_id=current.scene_id, action="checked", hop=candidate.hop,
                                confidence=candidate.confidence, reason=decision.reason))
        if not decision.needs_change:
            audit.append(AuditEntry(scene_id=current.scene_id, action="skipped", hop=candidate.hop,
                                    confidence=candidate.confidence, reason="Verifier: no continuity change required"))
            continue
        before_text = current.text
        current.text = regenerate_scene(before_text, delta + [decision.required_change], _neighbors(story, current))
        extract_scene(current, [scene for scene in story.scenes if abs(scene.order - current.order) == 1])
        changed_ids.append(current.scene_id)
        audit.append(AuditEntry(scene_id=current.scene_id, action="regenerated", hop=candidate.hop,
                                confidence=candidate.confidence, reason=decision.required_change,
                                before_text=before_text, after_text=current.text))

    story.dependencies = build_dependencies(story)
    story.versions.append(StoryVersion(label=label or f"Edit {datetime.now(timezone.utc).strftime('%H:%M:%S')}",
                                       parent_version_id=original_story.versions[-1].version_id if original_story.versions else None,
                                       changed_scene_ids=changed_ids, audit=audit,
                                       scenes_snapshot=deepcopy(story.scenes), dependencies_snapshot=deepcopy(story.dependencies)))
    return save_story(story)
