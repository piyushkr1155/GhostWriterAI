"""Local SQLite storage repository for GhostWriter stories."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from contextlib import contextmanager

from src.config import config

@dataclass
class StoryRecord:
    id: Optional[int]
    title: str
    story_text: str
    setting: str
    character: str
    horror_style: str
    length_category: str
    custom_prompt: str
    model_used: str
    word_count: int
    created_at: str
    is_favorite: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_export_text(self) -> str:
        """Format the story for download as a clean .txt file."""
        divider = "=" * 60
        header = f"""{self.title.upper()}
{divider}
Atmosphere: {self.horror_style}
Setting:    {self.setting}
Character:  {self.character}
Length:     {self.length_category} ({self.word_count} words)
Model:      {self.model_used}
Created:    {self.created_at}
{divider}
"""
        return header + "\n" + self.story_text.strip() + "\n\n" + divider + "\nSummoned with GhostWriter 👻 (Offline AI)\n"


class GhostStorage:
    """Manages local persistent story storage via SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Context manager that guarantees connection is closed on exit."""
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database schema with proper indexes."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    story_text TEXT NOT NULL,
                    setting TEXT NOT NULL,
                    character TEXT NOT NULL,
                    horror_style TEXT NOT NULL,
                    length_category TEXT NOT NULL,
                    custom_prompt TEXT DEFAULT '',
                    model_used TEXT NOT NULL,
                    word_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    is_favorite INTEGER DEFAULT 0
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stories_created ON stories(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stories_style ON stories(horror_style)")
            conn.commit()

    def save_story(
        self,
        title: str,
        story_text: str,
        setting: str,
        character: str,
        horror_style: str,
        length_category: str,
        model_used: str,
        custom_prompt: str = "",
        is_favorite: bool = False,
        created_at: Optional[str] = None
    ) -> StoryRecord:
        """Save a generated story to local database."""
        clean_title = title.strip() or "Untitled Nightmare"
        clean_text = story_text.strip()
        word_count = len(clean_text.split())
        timestamp = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stories (
                    title, story_text, setting, character, horror_style,
                    length_category, custom_prompt, model_used, word_count,
                    created_at, is_favorite
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                clean_title, clean_text, setting, character, horror_style,
                length_category, custom_prompt, model_used, word_count,
                timestamp, 1 if is_favorite else 0
            ))
            conn.commit()
            story_id = cursor.lastrowid

        return StoryRecord(
            id=story_id,
            title=clean_title,
            story_text=clean_text,
            setting=setting,
            character=character,
            horror_style=horror_style,
            length_category=length_category,
            custom_prompt=custom_prompt,
            model_used=model_used,
            word_count=word_count,
            created_at=timestamp,
            is_favorite=is_favorite
        )

    def get_all_stories(
        self,
        filter_style: Optional[str] = None,
        search_query: Optional[str] = None,
        only_favorites: bool = False
    ) -> List[StoryRecord]:
        """Fetch stories with optional filtering and text search."""
        query = "SELECT * FROM stories WHERE 1=1"
        params: List[Any] = []

        if filter_style and filter_style != "All Styles":
            query += " AND horror_style = ?"
            params.append(filter_style)

        if only_favorites:
            query += " AND is_favorite = 1"

        if search_query and search_query.strip():
            like_term = f"%{search_query.strip()}%"
            query += " AND (title LIKE ? OR story_text LIKE ? OR setting LIKE ? OR character LIKE ?)"
            params.extend([like_term, like_term, like_term, like_term])

        query += " ORDER BY created_at DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                StoryRecord(
                    id=row["id"],
                    title=row["title"],
                    story_text=row["story_text"],
                    setting=row["setting"],
                    character=row["character"],
                    horror_style=row["horror_style"],
                    length_category=row["length_category"],
                    custom_prompt=row["custom_prompt"] or "",
                    model_used=row["model_used"],
                    word_count=row["word_count"],
                    created_at=row["created_at"],
                    is_favorite=bool(row["is_favorite"])
                )
                for row in rows
            ]

    def get_story_by_id(self, story_id: int) -> Optional[StoryRecord]:
        """Fetch a single story by ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
            if not row:
                return None
            return StoryRecord(
                id=row["id"],
                title=row["title"],
                story_text=row["story_text"],
                setting=row["setting"],
                character=row["character"],
                horror_style=row["horror_style"],
                length_category=row["length_category"],
                custom_prompt=row["custom_prompt"] or "",
                model_used=row["model_used"],
                word_count=row["word_count"],
                created_at=row["created_at"],
                is_favorite=bool(row["is_favorite"])
            )

    def delete_story(self, story_id: int) -> bool:
        """Delete a saved story. Returns True if row was deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stories WHERE id = ?", (story_id,))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_favorite(self, story_id: int) -> bool:
        """Toggle favorite bookmark state of a story. Returns new state."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE stories SET is_favorite = 1 - is_favorite WHERE id = ?", (story_id,))
            conn.commit()
            row = conn.execute("SELECT is_favorite FROM stories WHERE id = ?", (story_id,)).fetchone()
            return bool(row["is_favorite"]) if row else False

    def get_stats(self) -> Dict[str, Any]:
        """Return aggregate statistics about stored stories."""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
            favs = conn.execute("SELECT COUNT(*) FROM stories WHERE is_favorite = 1").fetchone()[0]
            words = conn.execute("SELECT COALESCE(SUM(word_count), 0) FROM stories").fetchone()[0]
            by_style = conn.execute(
                "SELECT horror_style, COUNT(*) as cnt FROM stories GROUP BY horror_style"
            ).fetchall()
            return {
                "total_stories": total,
                "favorite_stories": favs,
                "total_words_written": words,
                "by_style": {r["horror_style"]: r["cnt"] for r in by_style}
            }
