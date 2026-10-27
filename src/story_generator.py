"""Horror story generator and prompt engineering orchestrator."""
import re
import logging
from typing import Tuple, Dict, Any, Optional, Generator

from src.config import config
from src.ollama_client import OllamaClient, OllamaClientError

logger = logging.getLogger(__name__)

class StoryValidationError(Exception):
    """Raised when story generation inputs fail validation."""
    pass


class StoryGenerator:
    """Orchestrates horror story generation with local models."""

    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()

    def validate_inputs(
        self,
        setting: str,
        character: str,
        horror_style: str,
        length_category: str,
        custom_prompt: str = ""
    ) -> Dict[str, str]:
        """Validate and sanitize user inputs before inference.

        Raises:
            StoryValidationError: If required fields are empty or invalid.
        """
        clean_setting = (setting or "").strip()
        clean_character = (character or "").strip()
        clean_style = (horror_style or "").strip()
        clean_length = (length_category or "").strip()
        clean_custom = (custom_prompt or "").strip()

        if not clean_setting or clean_setting == "Custom Setting...":
            raise StoryValidationError("Please specify a story setting (e.g., Abandoned Asylum, Blackwood Forest).")

        if not clean_character or clean_character == "Custom Character...":
            raise StoryValidationError("Please specify a protagonist character (e.g., Night Guard, Skeptical Detective).")

        if clean_style not in config.styles:
            valid_styles = ", ".join(config.styles.keys())
            raise StoryValidationError(f"Invalid horror style '{clean_style}'. Choose from: {valid_styles}")

        if clean_length not in config.lengths:
            valid_lengths = ", ".join(config.lengths.keys())
            raise StoryValidationError(f"Invalid story length '{clean_length}'. Choose from: {valid_lengths}")

        if len(clean_custom) > 600:
            raise StoryValidationError("Custom idea is too long. Please keep it under 600 characters.")

        return {
            "setting": clean_setting,
            "character": clean_character,
            "horror_style": clean_style,
            "length_category": clean_length,
            "custom_prompt": clean_custom
        }

    def build_system_prompt(self, horror_style: str) -> str:
        """Construct specialized system instructions based on horror subgenre."""
        style_guidance = config.styles.get(horror_style, "Create an atmospheric horror narrative.")

        return f"""You are GhostWriter, an elite horror and dark fiction novelist known for literary dread, claustrophobic atmosphere, and unexpected psychological chills.

Style Guidance for {horror_style}:
{style_guidance}

Storytelling Rules:
1. Ground the scene in sensory detail: smell of copper and rot, damp cold seeping through floorboards, silence so thick it rings.
2. Build suspense gradually. Start with an unsettling subtle anomaly, escalate the paranoia, and culminate in a haunting, memorable climax.
3. NEVER start with clichés like "It was a dark and stormy night" or "Little did they know".
4. The protagonist must feel authentic, vulnerable, and flawed.
5. Provide a captivating, original title on the very first line prefixed exactly with "TITLE: ".
6. Follow the target length strictly. Maintain immersive prose with clean paragraph breaks."""

    def build_user_prompt(
        self,
        setting: str,
        character: str,
        horror_style: str,
        length_category: str,
        custom_prompt: str = ""
    ) -> str:
        """Construct the user prompt incorporating all narrative parameters."""
        min_words, max_words, length_desc = config.lengths.get(length_category, (400, 700, "Medium story"))

        prompt_parts = [
            f"Write an original horror story adhering to these specifications:",
            f"- Setting: {setting}",
            f"- Protagonist: {character}",
            f"- Subgenre / Style: {horror_style}",
            f"- Target Length: Between {min_words} and {max_words} words ({length_desc})",
        ]

        if custom_prompt:
            prompt_parts.append(f"- Specific Premise / User Twist: {custom_prompt}")

        prompt_parts.extend([
            "",
            "Format Requirement:",
            "TITLE: <Invent an evocative, creepy title here>",
            "<Begin the story prose directly on the next line>",
            "",
            "Deliver the complete horror story now:"
        ])

        return "\n".join(prompt_parts)

    def extract_title_and_text(self, raw_output: str) -> Tuple[str, str]:
        """Extract title and narrative body from the model's raw response."""
        lines = raw_output.strip().split("\n")
        title = "The Untitled Haunting"
        story_lines = []
        found_title = False

        for i, line in enumerate(lines):
            clean_line = line.strip()
            # Match variations of TITLE: ...
            if not found_title and (
                clean_line.upper().startswith("TITLE:") or
                clean_line.upper().startswith("# TITLE:") or
                clean_line.startswith("**Title:**") or
                clean_line.startswith("## ")
            ):
                extracted = re.sub(r"^(#+\s*|TITLE:\s*|\*\*Title:\*\*\s*)", "", clean_line, flags=re.IGNORECASE)
                extracted = extracted.strip(' "*#')
                if extracted:
                    title = extracted
                    found_title = True
                    continue

            # If no explicit TITLE tag was found on the first non-empty line
            if not found_title and clean_line and i == 0:
                if len(clean_line) < 70 and not clean_line.endswith("."):
                    title = clean_line.strip(' "*#')
                    found_title = True
                    continue

            story_lines.append(line)

        story_text = "\n".join(story_lines).strip()
        # Clean any leading markdown formatting or leftover labels
        story_text = re.sub(r"^(Here is the story:?\s*|Story:?\s*)", "", story_text, flags=re.IGNORECASE).strip()

        if not story_text:
            story_text = raw_output.strip()

        return title, story_text

    def generate_story(
        self,
        setting: str,
        character: str,
        horror_style: str,
        length_category: str,
        custom_prompt: str = "",
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, str, int]:
        """Generate a complete horror story synchronously.

        Returns:
            Tuple of (title, story_text, word_count)
        """
        validated = self.validate_inputs(setting, character, horror_style, length_category, custom_prompt)
        system_prompt = self.build_system_prompt(validated["horror_style"])
        user_prompt = self.build_user_prompt(
            setting=validated["setting"],
            character=validated["character"],
            horror_style=validated["horror_style"],
            length_category=validated["length_category"],
            custom_prompt=validated["custom_prompt"]
        )

        # Max tokens estimate: ~1.5 tokens per word
        _, max_words, _ = config.lengths.get(validated["length_category"], (400, 700, ""))
        max_tokens = int(max_words * 1.8) + 200

        raw_output = self.client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=model,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens
        )

        title, story_text = self.extract_title_and_text(raw_output)
        word_count = len(story_text.split())

        return title, story_text, word_count

    def generate_story_stream(
        self,
        setting: str,
        character: str,
        horror_style: str,
        length_category: str,
        custom_prompt: str = "",
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Generator[str, None, None]:
        """Stream story tokens from local model in real time."""
        validated = self.validate_inputs(setting, character, horror_style, length_category, custom_prompt)
        system_prompt = self.build_system_prompt(validated["horror_style"])
        user_prompt = self.build_user_prompt(
            setting=validated["setting"],
            character=validated["character"],
            horror_style=validated["horror_style"],
            length_category=validated["length_category"],
            custom_prompt=validated["custom_prompt"]
        )

        _, max_words, _ = config.lengths.get(validated["length_category"], (400, 700, ""))
        max_tokens = int(max_words * 1.8) + 200

        return self.client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=model,
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens
        )

