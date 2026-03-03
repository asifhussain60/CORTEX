"""KnowledgeIndexer — auto-indexing system for tier3 knowledge (KN-001-02)."""
# noqa: CORE-035 — domain-scoped; class name appropriate for this module
from __future__ import annotations

import sqlite3
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


_KNOWLEDGE_DIR = (
    Path(__file__).parent.parent.parent.parent.parent.parent
    / "cortex.intelligence" / "tier3" / "knowledge"
)


@dataclass
class IndexEntry:
    """Indexed knowledge entry with domain classification and quality score."""

    entry_id: str
    domain: str
    title: str
    ac_ids: List[str]
    created_at: datetime
    quality_score: Optional[float] = None
    file_path: Optional[str] = None


class KnowledgeIndexer:
    """Maintains a SQLite index of knowledge entries."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialise knowledge indexer with SQLite backend."""
        if db_path:
            self._db_path = Path(db_path)
        else:
            _KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
            self._db_path = _KNOWLEDGE_DIR / "knowledge-index.db"
        self._init_db()

    def _init_db(self) -> None:
        """Init db."""
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    entry_id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    title TEXT NOT NULL,
                    ac_ids TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    quality_score REAL,
                    file_path TEXT
                )
            """)
            conn.commit()

    def index_entry(self, entry: IndexEntry) -> bool:
        """Index a knowledge entry in the database."""
        with sqlite3.connect(str(self._db_path)) as conn:
            import json
            conn.execute("""
                INSERT OR REPLACE INTO entries
                (entry_id, domain, title, ac_ids, created_at, quality_score, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.entry_id, entry.domain, entry.title,
                json.dumps(entry.ac_ids), entry.created_at.isoformat(),
                entry.quality_score, entry.file_path,
            ))
            conn.commit()
        return True

    def search(self, query: str, domain: Optional[str] = None) -> List[IndexEntry]:
        """Search indexed entries by query string and optional domain."""
        with sqlite3.connect(str(self._db_path)) as conn:
            import json
            if domain:
                rows = conn.execute(
                    "SELECT * FROM entries WHERE domain=? AND (title LIKE ? OR entry_id LIKE ?)",
                    (domain, f"%{query}%", f"%{query}%")
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM entries WHERE title LIKE ? OR entry_id LIKE ?",
                    (f"%{query}%", f"%{query}%")
                ).fetchall()
            return [
                IndexEntry(
                    entry_id=r[0], domain=r[1], title=r[2],
                    ac_ids=json.loads(r[3]), created_at=datetime.fromisoformat(r[4]),
                    quality_score=r[5], file_path=r[6],
                )
                for r in rows
            ]

    def get_by_ac_id(self, ac_id: str) -> List[IndexEntry]:
        """Retrieve entries matching an AC identifier."""
        return self.search(ac_id)

    def get_by_domain(self, domain: str) -> List[IndexEntry]:
        """Retrieve all entries for a domain."""
        return self.search("", domain=domain)

    def get_index_file(self) -> Path:
        """Return the path to the SQLite index file."""
        return self._db_path

    def inventory(self) -> List[str]:
        """Return all indexed entry IDs as a list of strings.

        Provides a quick summary of every entry currently held in the
        knowledge index, suitable for docgen sync and bridge operations
        (GAP-66-005 — Phase 66-A).

        Returns:
            List of ``entry_id`` strings for every indexed knowledge entry.
        """
        with sqlite3.connect(str(self._db_path)) as conn:
            rows = conn.execute("SELECT entry_id FROM entries").fetchall()
        return [r[0] for r in rows]