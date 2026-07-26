"""No-key smoke tests for the durable core."""
from backend.graph_engine import blast_radius, build_dependencies
from backend.models import Scene, Story, StoryBible
from backend.seed_data import RAW_STORIES


def test_seed_corpus() -> None:
    assert len(RAW_STORIES) == 10
    assert all(len(item[-1]) >= 10 for item in RAW_STORIES)


def test_unrelated_scene_is_outside_blast_radius() -> None:
    story = Story(story_id="test", title="Test", genre="Test", logline="Test", cover_gradient="x", scenes=[
        Scene(scene_id="s01", title="Setup", text="A", order=1, bible=StoryBible(
            established_facts=["letter"], causal_setup=["reveal"], writes=[{"state_var_id": "has_letter", "new_value": "true"}],
        )),
        Scene(scene_id="s02", title="Payoff", text="B", order=2, bible=StoryBible(
            objects_facts=["letter"], causal_payoff_of=["reveal"], reads=["has_letter"],
        )),
        Scene(scene_id="s03", title="Unrelated", text="C", order=3, bible=StoryBible(characters_present=["Other"])),
    ])
    story.dependencies = build_dependencies(story)
    assert [candidate.scene_id for candidate in blast_radius(story, "s01")] == ["s02"]
