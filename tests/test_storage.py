"""Tests for GhostWriter local SQLite storage repository."""
import os
import tempfile
from pathlib import Path
import pytest

from src.storage import GhostStorage, StoryRecord

@pytest.fixture
def temp_storage():
    """Create a temporary SQLite storage instance for isolated testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_stories.db"
        storage = GhostStorage(db_path=db_path)
        yield storage


def test_init_and_empty_storage(temp_storage):
    """Test initial state of an empty storage database."""
    stories = temp_storage.get_all_stories()
    assert len(stories) == 0
    stats = temp_storage.get_stats()
    assert stats["total_stories"] == 0
    assert stats["favorite_stories"] == 0


def test_save_and_retrieve_story(temp_storage):
    """Test saving a story and fetching it by ID and list."""
    saved = temp_storage.save_story(
        title="The Whispering Shadows",
        story_text="The cold seeped through the floorboards as the clock struck midnight...",
        setting="Abandoned Mansion",
        character="Night Guard",
        horror_style="Supernatural Ghost Story",
        length_category="Short",
        model_used="qwen2.5:3b",
        custom_prompt="A clock that ticks backward"
    )

    assert saved.id is not None
    assert saved.title == "The Whispering Shadows"
    assert saved.word_count > 5
    assert saved.is_favorite is False

    # Fetch by ID
    fetched = temp_storage.get_story_by_id(saved.id)
    assert fetched is not None
    assert fetched.title == saved.title
    assert fetched.setting == "Abandoned Mansion"
    assert fetched.custom_prompt == "A clock that ticks backward"

    # Fetch all
    all_stories = temp_storage.get_all_stories()
    assert len(all_stories) == 1
    assert all_stories[0].id == saved.id


def test_filter_by_style_and_search(temp_storage):
    """Test filtering stories by horror style and text searching."""
    temp_storage.save_story(
        title="Midnight Patient",
        story_text="Room 402 was supposed to be empty...",
        setting="Old Hospital",
        character="Doctor",
        horror_style="Psychological Horror",
        length_category="Short",
        model_used="qwen2.5:3b"
    )
    temp_storage.save_story(
        title="The Railway Specter",
        story_text="A whistle echoed down the abandoned tracks...",
        setting="Deserted Railway Station",
        character="Traveller",
        horror_style="Supernatural Ghost Story",
        length_category="Medium",
        model_used="llama3.2:latest"
    )

    # Filter by style
    psych_stories = temp_storage.get_all_stories(filter_style="Psychological Horror")
    assert len(psych_stories) == 1
    assert psych_stories[0].title == "Midnight Patient"

    ghost_stories = temp_storage.get_all_stories(filter_style="Supernatural Ghost Story")
    assert len(ghost_stories) == 1
    assert ghost_stories[0].title == "The Railway Specter"

    # Search query
    search_results = temp_storage.get_all_stories(search_query="whistle")
    assert len(search_results) == 1
    assert search_results[0].title == "The Railway Specter"

    # Non-matching search
    empty_results = temp_storage.get_all_stories(search_query="nonexistent term")
    assert len(empty_results) == 0


def test_toggle_favorite_and_delete(temp_storage):
    """Test toggling favorite flag and deleting stories."""
    story = temp_storage.save_story(
        title="Crypt of the Damned",
        story_text="Stone tombs groaned open under the pale moonlight...",
        setting="Ancestral Crypt",
        character="Antique Appraiser",
        horror_style="Gothic Horror",
        length_category="Short",
        model_used="qwen2.5:3b"
    )

    # Toggle favorite
    new_fav = temp_storage.toggle_favorite(story.id)
    assert new_fav is True
    fav_stories = temp_storage.get_all_stories(only_favorites=True)
    assert len(fav_stories) == 1

    # Toggle off
    new_fav_off = temp_storage.toggle_favorite(story.id)
    assert new_fav_off is False
    assert len(temp_storage.get_all_stories(only_favorites=True)) == 0

    # Delete story
    deleted = temp_storage.delete_story(story.id)
    assert deleted is True
    assert temp_storage.get_story_by_id(story.id) is None
    assert len(temp_storage.get_all_stories()) == 0

    # Delete nonexistent story
    assert temp_storage.delete_story(99999) is False


def test_export_story_format(temp_storage):
    """Test formatting story for .txt file export."""
    story = temp_storage.save_story(
        title="Curse of Blackwood",
        story_text="The fog crept between the ancient gnarled oaks.",
        setting="Haunted Forest",
        character="Student",
        horror_style="Mystery and Suspense",
        length_category="Short",
        model_used="qwen2.5:3b"
    )

    export_txt = story.to_export_text()
    assert "CURSE OF BLACKWOOD" in export_txt
    assert "Atmosphere: Mystery and Suspense" in export_txt
    assert "Setting:    Haunted Forest" in export_txt
    assert "The fog crept between the ancient gnarled oaks." in export_txt
    assert "Summoned with GhostWriter 👻" in export_txt
