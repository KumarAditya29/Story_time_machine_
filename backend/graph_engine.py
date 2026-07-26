"""Narrative dependency graph construction and tightly-scoped impact traversal."""
from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass

import networkx as nx

from .models import Dependency, Scene, Story


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _overlap(left: list[str], right: list[str]) -> set[str]:
    left_keys = {_key(item) for item in left if _key(item)}
    right_keys = {_key(item) for item in right if _key(item)}
    return {a for a in left_keys for b in right_keys if a == b or (len(a) > 4 and (a in b or b in a))}


def _facts(scene: Scene) -> list[str]:
    if not scene.bible:
        return []
    return scene.bible.objects_facts + scene.bible.established_facts + [item["state_var_id"] for item in scene.bible.writes]


def _reads(scene: Scene) -> list[str]:
    if not scene.bible:
        return []
    return scene.bible.reads + scene.bible.objects_facts + scene.bible.established_facts


def build_dependencies(story: Story) -> list[Dependency]:
    """Derive explainable links. A pair may have several reasons, but only its strongest link is retained."""
    dependencies: list[Dependency] = []
    ordered = sorted(story.scenes, key=lambda scene: scene.order)
    for index, source in enumerate(ordered):
        if not source.bible:
            continue
        for target in ordered[index + 1:]:
            if not target.bible:
                continue
            candidates: list[tuple[str, str, float]] = []
            fact_matches = _overlap(_facts(source), _reads(target))
            if fact_matches:
                candidates.append(("fact", f"References established state: {', '.join(sorted(fact_matches)[:2])}", 0.9))
            characters = set(source.bible.characters_present) & set(target.bible.characters_present)
            stateful = set(source.bible.character_states) & set(target.bible.character_states)
            if characters:
                continuity = sorted(stateful or characters)
                confidence = 0.72 if stateful else 0.5
                candidates.append(("character", f"Character continuity: {', '.join(continuity[:2])}", confidence))
            causal_matches = _overlap(source.bible.causal_setup, target.bible.causal_payoff_of)
            if causal_matches:
                candidates.append(("causal", f"Causal setup/payoff: {', '.join(sorted(causal_matches)[:2])}", 0.96))
            foreshadow_matches = _overlap(source.bible.causal_setup, target.bible.causal_setup)
            if foreshadow_matches:
                candidates.append(("foreshadow", f"Shared narrative thread: {', '.join(sorted(foreshadow_matches)[:2])}", 0.62))
            if candidates:
                kind, reason, confidence = max(candidates, key=lambda item: item[2])
                dependencies.append(Dependency(source_scene_id=source.scene_id, target_scene_id=target.scene_id,
                                               kind=kind, reason=reason, confidence=confidence))
    return dependencies


def build_graph(story: Story) -> nx.DiGraph:
    graph = nx.DiGraph()
    for scene in story.scenes:
        graph.add_node(scene.scene_id, order=scene.order)
    for dependency in story.dependencies:
        graph.add_edge(dependency.source_scene_id, dependency.target_scene_id,
                       kind=dependency.kind, reason=dependency.reason, confidence=dependency.confidence)
    return graph


@dataclass(frozen=True)
class ImpactCandidate:
    scene_id: str
    hop: int
    direction: str
    dependency_reason: str
    confidence: float


def blast_radius(story: Story, changed_scene_id: str, changed_fields: set[str] | None = None,
                 include_backward: bool = True, max_hops: int = 4) -> list[ImpactCandidate]:
    """BFS through only meaningful dependency edges, including foreshadowing predecessors."""
    graph = build_graph(story)
    if changed_scene_id not in graph:
        raise ValueError(f"Unknown scene: {changed_scene_id}")
    result: list[ImpactCandidate] = []
    visited = {changed_scene_id}
    queue = deque([(changed_scene_id, 0, "forward"), (changed_scene_id, 0, "backward")])
    while queue:
        node, hop, direction = queue.popleft()
        if hop >= max_hops:
            continue
        edges = graph.out_edges(node, data=True) if direction == "forward" else graph.in_edges(node, data=True)
        for left, right, data in edges:
            neighbor = right if direction == "forward" else left
            if neighbor in visited:
                continue
            # Backward traversal is solely for foreshadow/payoff consistency.
            if direction == "backward" and data["kind"] not in {"foreshadow", "causal"}:
                continue
            if changed_fields and data["kind"] == "fact":
                reason = _key(data["reason"])
                if not any(_key(field) in reason or reason in _key(field) for field in changed_fields):
                    continue
            visited.add(neighbor)
            result.append(ImpactCandidate(scene_id=neighbor, hop=hop + 1, direction=direction,
                                          dependency_reason=data["reason"], confidence=float(data["confidence"])))
            queue.append((neighbor, hop + 1, direction))
    return sorted(result, key=lambda candidate: (candidate.hop, candidate.scene_id))
