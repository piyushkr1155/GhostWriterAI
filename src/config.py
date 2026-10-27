"""Configuration module for GhostWriter."""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Try to load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class StoryOption:
    id: str
    label: str
    description: str = ""

@dataclass
class AppConfig:
    app_name: str = "GhostWriter"
    tagline: str = "Every shadow has a story. Every story has a ghost."
    version: str = "1.0.0"

    # Ollama settings
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    )
    default_model: str = field(
        default_factory=lambda: os.getenv("GHOSTWRITER_MODEL", "qwen2.5:3b")
    )
    timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("OLLAMA_TIMEOUT", "90"))
    )
    default_temperature: float = field(
        default_factory=lambda: float(os.getenv("DEFAULT_TEMPERATURE", "0.75"))
    )

    # Storage settings
    data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data")
    db_path: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "ghostwriter.db")

    # Story parameters & curated options
    settings: List[str] = field(default_factory=lambda: [
        "Abandoned Mansion",
        "Haunted Forest",
        "Old Hospital",
        "Deserted Railway Station",
        "Submerged Victorian Asylum",
        "Fog-Drenched Lighthouse",
        "Ancestral Crypt",
        "Custom Setting..."
    ])

    characters: List[str] = field(default_factory=lambda: [
        "Night Guard",
        "Detective",
        "Student",
        "Traveller",
        "Antique Appraiser",
        "Radio Host",
        "Skeptical Priest",
        "Custom Character..."
    ])

    styles: Dict[str, str] = field(default_factory=lambda: {
        "Psychological Horror": "Focus on escalating paranoia, memory distortion, claustrophobia, and the slow unraveling of reality.",
        "Supernatural Ghost Story": "Spectral apparitions, cold spots, cursed artifacts, vengeful spirits, and whispers through the walls.",
        "Gothic Horror": "Decaying architecture, family curses, heavy melancholia, brooding stormy atmosphere, and ancient secrets.",
        "Mystery and Suspense": "A ticking clock, an investigation into a macabre secret, hidden motives, and a shocking psychological twist.",
        "Funny Horror": "Spooky situations colliding with dark, witty, sarcastic comedy and absurd supernatural misunderstandings."
    })

    lengths: Dict[str, Tuple[int, int, str]] = field(default_factory=lambda: {
        "Short": (250, 400, "Brief chilling vignette, ideal for a quick scare (~300 words)."),
        "Medium": (500, 750, "Full-bodied eerie narrative with rising dread and climax (~600 words)."),
        "Long": (850, 1200, "Deeply atmospheric horror novelette with rich lore and twists (~1000 words).")
    })

    # Recommended lightweight open models
    recommended_models: List[Dict[str, str]] = field(default_factory=lambda: [
        {"name": "qwen2.5:3b", "size": "1.9 GB", "desc": "Top choice: Fast, atmospheric, high coherence. Ideal for 4GB VRAM."},
        {"name": "llama3.2:latest", "size": "2.0 GB", "desc": "Llama 3.2 3B: Excellent dialogue and pacing. Low memory footprint."},
        {"name": "qwen2.5:1.5b", "size": "986 MB", "desc": "Ultra-lightweight: Blazing fast even on CPU or older laptops."},
        {"name": "gemma2:2b", "size": "1.6 GB", "desc": "Google Gemma 2: High literary quality and descriptive prose."}
    ])

    def ensure_directories(self) -> None:
        """Create data and assets directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

config = AppConfig()
config.ensure_directories()
