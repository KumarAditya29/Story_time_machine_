from .seed_data import RAW_STORIES


def test_seed_library_has_ten_complete_stories() -> None:
    assert len(RAW_STORIES) == 10
    assert all(len(story[-1]) >= 10 for story in RAW_STORIES)
    assert len({story[0] for story in RAW_STORIES}) == len(RAW_STORIES)
