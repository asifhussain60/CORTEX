"""InquiryCache - Repo-scoped SQLite cache for inquiry responses.

AC-ID: INQUIRY-002-NEW
Purpose: Provide fast caching with isolation between CORTEX and user repos
Author: Asif Hussain
Date: 2026-01-27

Cache Design:
- SQLite database at .cortex/inquiry_cache.db
- Repo-scoped keys: {repo_name}:{question_hash}
- Automatic isolation between CORTEX and user repositories
- Thread-safe operations

Schema:
    CREATE TABLE inquiry_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_name TEXT NOT NULL,
        question_hash TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(repo_name, question_hash)
    )
"""

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.models.inquiry_models import RepoContext


class InquiryCache:
    """SQLite-backed cache with repo-scoped isolation.

    Provides fast caching for inquiry responses with automatic isolation
    between CORTEX and user repositories. Thread-safe operations.

    Attributes:
        db_path: Path to SQLite database
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize cache with SQLite database.

        Args:
            db_path: Optional path to SQLite database
                    (defaults to .cortex/inquiry_cache.db)
        """
        if db_path is None:
            db_path = Path.cwd() / ".cortex" / "inquiry_cache.db"

        self.db_path = db_path
        self._ensure_database()

    def _ensure_database(self) -> None:
        """Ensure database and schema exist."""
        # Create directory if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create schema
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inquiry_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL,
                question_hash TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(repo_name, question_hash)
            )
        """)

        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_repo_question
            ON inquiry_cache(repo_name, question_hash)
        """)

        conn.commit()
        conn.close()

    def generate_cache_key(
        self,
        question: str,
        repo_context: RepoContext,
    ) -> str:
        """Generate repo-scoped cache key.

        Args:
            question: Question text
            repo_context: Repository context

        Returns:
            Cache key in format: {repo_name}:{8char_hash}
        """
        # Generate hash from question
        question_hash = hashlib.sha256(question.encode()).hexdigest()[:8]

        # Combine with repo name for scoping
        return f"{repo_context.repo_name}:{question_hash}"

    def set(
        self,
        question: str,
        repo_context: RepoContext,
        response: Dict[str, Any],
    ) -> None:
        """Set cached response for question.

        Args:
            question: Question text
            repo_context: Repository context
            response: Response dictionary to cache
        """
        cache_key = self.generate_cache_key(question, repo_context)
        repo_name, question_hash = cache_key.split(":", 1)

        # Serialize response
        response_json = json.dumps(response)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Insert or replace
        cursor.execute("""
            INSERT OR REPLACE INTO inquiry_cache
            (repo_name, question_hash, response)
            VALUES (?, ?, ?)
        """, (repo_name, question_hash, response_json))

        conn.commit()
        conn.close()

    def get(
        self,
        question: str,
        repo_context: RepoContext,
    ) -> Optional[Dict[str, Any]]:
        """Get cached response for question.

        Args:
            question: Question text
            repo_context: Repository context

        Returns:
            Cached response dictionary or None if not found
        """
        cache_key = self.generate_cache_key(question, repo_context)
        repo_name, question_hash = cache_key.split(":", 1)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT response FROM inquiry_cache
            WHERE repo_name = ? AND question_hash = ?
        """, (repo_name, question_hash))

        result = cursor.fetchone()
        conn.close()

        if result is None:
            return None

        # Deserialize response
        return json.loads(result[0])

    def clear_repo(self, repo_context: RepoContext) -> None:
        """Clear cache for specific repository.

        Args:
            repo_context: Repository context to clear
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM inquiry_cache
            WHERE repo_name = ?
        """, (repo_context.repo_name,))

        conn.commit()
        conn.close()

    def clear_all(self) -> None:
        """Clear entire cache (all repositories)."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("DELETE FROM inquiry_cache")

        conn.commit()
        conn.close()
