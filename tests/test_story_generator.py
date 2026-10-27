"""Tests for StoryGenerator prompt construction and validation."""
from unittest.mock import MagicMock
import pytest

from src.story_generator import StoryGenerator, StoryValidationError
from src.ollama_client import OllamaClient

@pytest.fixture
def mock_generator():
    """Create a StoryGenerator with a mocked OllamaClient."""
    mock_client = MagicMock(spec=OllamaClient)
    return StoryGenerator(client=mock_client)


def test_input_validation_success(mock_generator):
    """Test successful validation of valid inputs."""
    validated = mock_generator.validate_inputs(
        setting="Abandoned Mansion",
        character="Night Guard",
        horror_style="Supernatural Ghost Story",
        length_category="Short",
        custom_prompt="Include an old radio playing static"
    )
    assert validated["setting"] == "Abandoned Mansion"
    assert validated["character"] == "Night Guard"
    assert validated["horror_style"] == "Supernatural Ghost Story"
    assert validated["length_category"] == "Short"
    assert validated["custom_prompt"] == "Include an old radio playing static"


def test_input_validation_empty_setting(mock_generator):
    """Test that missing or placeholder setting raises validation error."""
    with pytest.raises(StoryValidationError, match="specify a story setting"):
        mock_generator.validate_inputs(
            setting="",
            character="Night Guard",
            horror_style="Psychological Horror",
            length_category="Short"
        )

    with pytest.raises(StoryValidationError, match="specify a story setting"):
        mock_generator.validate_inputs(
            setting="Custom Setting...",
            character="Night Guard",
            horror_style="Psychological Horror",
            length_category="Short"
        )


def test_input_validation_empty_character(mock_generator):
    """Test that missing or placeholder character raises validation error."""
    with pytest.raises(StoryValidationError, match="specify a protagonist character"):
        mock_generator.validate_inputs(
            setting="Haunted Forest",
            character="  ",
            horror_style="Gothic Horror",
            length_category="Medium"
        )


def test_input_validation_invalid_style(mock_generator):
    """Test that unrecognized horror style raises validation error."""
    with pytest.raises(StoryValidationError, match="Invalid horror style"):
        mock_generator.validate_inputs(
            setting="Haunted Forest",
            character="Student",
            horror_style="Romantic Comedy",
            length_category="Short"
        )


def test_input_validation_invalid_length(mock_generator):
    """Test that unrecognized length raises validation error."""
    with pytest.raises(StoryValidationError, match="Invalid story length"):
        mock_generator.validate_inputs(
            setting="Haunted Forest",
            character="Student",
            horror_style="Gothic Horror",
            length_category="SuperExtraLong"
        )


def test_input_validation_custom_prompt_too_long(mock_generator):
    """Test that custom prompt exceeding character limits is rejected."""
    long_prompt = "A" * 700
    with pytest.raises(StoryValidationError, match="Custom idea is too long"):
        mock_generator.validate_inputs(
            setting="Haunted Forest",
            character="Student",
            horror_style="Gothic Horror",
            length_category="Short",
            custom_prompt=long_prompt
        )


def test_system_prompt_construction(mock_generator):
    """Test that system prompt incorporates style guidance and rules."""
    sys_prompt = mock_generator.build_system_prompt("Psychological Horror")
    assert "GhostWriter" in sys_prompt
    assert "Psychological Horror" in sys_prompt
    assert "paranoia" in sys_prompt.lower()
    assert "TITLE: " in sys_prompt


def test_user_prompt_construction(mock_generator):
    """Test user prompt structure and parameter inclusion."""
    user_prompt = mock_generator.build_user_prompt(
        setting="Old Hospital",
        character="Skeptical Doctor",
        horror_style="Mystery and Suspense",
        length_category="Medium",
        custom_prompt="An autopsy file dated for tomorrow"
    )
    assert "- Setting: Old Hospital" in user_prompt
    assert "- Protagonist: Skeptical Doctor" in user_prompt
    assert "- Subgenre / Style: Mystery and Suspense" in user_prompt
    assert "An autopsy file dated for tomorrow" in user_prompt
    assert "TITLE: " in user_prompt


def test_extract_title_and_text(mock_generator):
    """Test parsing raw model output into clean title and narrative body."""
    raw = """TITLE: Whispers Beneath the Ashen Silt
The cold water crept past the shattered seal of the lower airlock.
Dr. Aris reached for the valve with shaking fingers.
He was not alone in the dark."""

    title, story_text = mock_generator.extract_title_and_text(raw)
    assert title == "Whispers Beneath the Ashen Silt"
    assert "The cold water crept past" in story_text
    assert "TITLE:" not in story_text


def test_extract_title_fallback(mock_generator):
    """Test title extraction when model does not prefix with TITLE:."""
    raw = """Echoes in Room 402
The hospital hallway stretched endlessly into violet shadow.
Nurse Clara checked the empty charts."""

    title, story_text = mock_generator.extract_title_and_text(raw)
    assert title == "Echoes in Room 402"
    assert "The hospital hallway stretched endlessly" in story_text


def test_generate_story_execution(mock_generator):
    """Test full synchronous story generation flow with mocked client."""
    mock_generator.client.generate.return_value = """TITLE: The Night Watchman's Toll
The gate swung open on rusted hinges.
Gareth raised his flashlight into the fog."""

    title, story_text, word_count = mock_generator.generate_story(
        setting="Deserted Railway Station",
        character="Night Guard",
        horror_style="Gothic Horror",
        length_category="Short"
    )

    assert title == "The Night Watchman's Toll"
    assert "The gate swung open" in story_text
    assert word_count > 5
    mock_generator.client.generate.assert_called_once()

