"""KnowledgeIndexer - auto-indexing system for tier3 knowledge (KN-001-02)."""
# CORE-035 - domain-scoped; class name appropriate for this module
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


_REPO_ROOT = Path(__file__).resolve().parents[4]
_KNOWLEDGE_DIR = _REPO_ROOT / "cortex.intelligence" / "tier3" / "knowledge"
_KNOWLEDGE_INDEX_PATH = _KNOWLEDGE_DIR / ".knowledge-index.json"
_REGISTRY_INDEX_PATH = _REPO_ROOT / "cortex-registry" / "knowledge" / "INDEX.yaml"
_AC_ID_PATTERN = re.compile(r"\b(?:AC|KN)-[A-Z0-9-]+\b")

_CANONICAL_DOMAINS = [
    "GOVERNANCE",
    "INTENT-ROUTING",
    "HALLUCINATION-PREVENTION",
    "EXECUTION-ORCHESTRATION",
    "DATA-MANAGEMENT",
    "OBSERVABILITY",
    "SECURITY",
    "API-DESIGN",
    "ML-MODELS",
    "KNOWLEDGE-CURATION",
    "TESTING-VALIDATION",
    "DEPLOYMENT",
    "DOCUMENTATION",
    "PERFORMANCE",
    "ARCHITECTURE",
    "ERROR-HANDLING",
]

_DOMAIN_ALIASES = {
    "ai-context": "KNOWLEDGE-CURATION",
    "architecture": "ARCHITECTURE",
    "backend-python": "ARCHITECTURE",
    "business-rules": "DATA-MANAGEMENT",
    "devops-infrastructure": "DEPLOYMENT",
    "documentation": "DOCUMENTATION",
    "governance": "GOVERNANCE",
    "migration": "ARCHITECTURE",
    "operational-patterns": "ERROR-HANDLING",
    "performance-optimization": "PERFORMANCE",
    "profiles": "INTENT-ROUTING",
    "repositories": "EXECUTION-ORCHESTRATION",
    "sdlc": "TESTING-VALIDATION",
    "security": "SECURITY",
    "testing-validation": "TESTING-VALIDATION",
}


@dataclass
class IndexEntry:
    """Indexed knowledge entry with domain classification and quality score.

    Args:
        entry_id: Stable entry identifier.
        domain: Canonical knowledge domain.
        title: Human-readable title.
        ac_ids: Acceptance-criteria identifiers referenced by the entry.
        created_at: Entry creation timestamp.
        quality_score: Optional quality score.
        file_path: Optional source file path.
    """

    entry_id: str
    domain: str
    title: str
    ac_ids: List[str]
    created_at: datetime
    quality_score: Optional[float] = None
    file_path: Optional[str] = None


class KnowledgeIndexer:  # CORE-035-scoped - domain-specific variant
    """Maintain SQLite and JSON indexes for tier3 knowledge entries."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialise the knowledge indexer.

        Args:
            db_path: Optional explicit SQLite database path.
        """
        if db_path:
            self._db_path = Path(db_path)
            self._json_index_path = self._db_path.with_name(".knowledge-index.json")
        else:
            _KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
            self._db_path = _KNOWLEDGE_DIR / "knowledge-index.db"
            self._json_index_path = _KNOWLEDGE_INDEX_PATH

        self._init_db()
        self._ensure_sidecar_index()

    def _init_db(self) -> None:
        """Initialise the SQLite backing store."""
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    entry_id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    title TEXT NOT NULL,
                    ac_ids TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    quality_score REAL,
                    file_path TEXT
                )
                """
            )
            conn.commit()

    def _ensure_sidecar_index(self) -> None:
        """Ensure the JSON sidecar index exists on disk."""
        self.rebuild_index()

    def _fetch_db_entries(self) -> List[IndexEntry]:
        """Load all entries currently stored in SQLite.

        Returns:
            List of entries persisted in the database.
        """
        with sqlite3.connect(str(self._db_path)) as conn:
            rows = conn.execute("SELECT * FROM entries ORDER BY entry_id").fetchall()

        return [
            IndexEntry(
                entry_id=row[0],
                domain=row[1],
                title=row[2],
                ac_ids=json.loads(row[3]),
                created_at=datetime.fromisoformat(row[4]),
                quality_score=row[5],
                file_path=row[6],
            )
            for row in rows
        ]

    def _load_json_index(self) -> Dict[str, Any]:
        """Load the JSON sidecar index, rebuilding it when missing.

        Returns:
            Parsed JSON payload.
        """
        if not self._json_index_path.exists():
            self.rebuild_index()

        with self._json_index_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _canonical_domain(self, raw_domain: str) -> str:
        """Map registry domains into the KN-001-02 canonical domain set.

        Args:
            raw_domain: Domain label from the registry index.

        Returns:
            Canonical domain label.
        """
        return _DOMAIN_ALIASES.get(raw_domain, "KNOWLEDGE-CURATION")

    def _extract_ac_ids(self, file_path: Path) -> List[str]:
        """Extract AC and KN identifiers from a knowledge source file.

        Args:
            file_path: Source file to inspect.

        Returns:
            Sorted unique list of identifiers found in the file.
        """
        if not file_path.exists():
            return []

        matches = _AC_ID_PATTERN.findall(file_path.read_text(encoding="utf-8"))
        return sorted(set(matches))

    def _resolve_registry_path(self, relative_path: str) -> Path:
        """Resolve a knowledge INDEX path to an absolute file path.

        Args:
            relative_path: Path string from the registry index.

        Returns:
            Absolute path to the referenced knowledge source.
        """
        if relative_path.startswith("../knowledge-base/"):
            suffix = relative_path[len("../knowledge-base/") :]
            return _REPO_ROOT / "cortex-registry" / "knowledge-base" / suffix
        if relative_path.startswith("docs/"):
            return _REPO_ROOT / relative_path
        return _REPO_ROOT / "cortex-registry" / "knowledge" / relative_path

    def _build_registry_entries(self) -> List[IndexEntry]:
        """Build deterministic index entries from the knowledge registry.

        Returns:
            Registry-derived entries.
        """
        if not _REGISTRY_INDEX_PATH.exists():
            return []

        payload = yaml.safe_load(_REGISTRY_INDEX_PATH.read_text(encoding="utf-8")) or {}
        created_at = datetime.fromisoformat(str(payload.get("created", "2026-02-09")))
        entries: List[IndexEntry] = []
        counter = 1

        for section_name, section_data in payload.items():
            if not isinstance(section_data, dict):
                continue

            guides = section_data.get("guides", [])
            if not isinstance(guides, list):
                continue

            for guide in guides:
                if not isinstance(guide, dict):
                    continue

                relative_path = str(guide.get("path", "")).strip()
                if not relative_path:
                    continue

                absolute_path = self._resolve_registry_path(relative_path)
                title = str(guide.get("title", absolute_path.stem)).strip()

                entries.append(
                    IndexEntry(
                        entry_id=f"KE-{counter:04d}",
                        domain=self._canonical_domain(section_name),
                        title=title,
                        ac_ids=self._extract_ac_ids(absolute_path),
                        created_at=created_at,
                        file_path=str(absolute_path),
                    )
                )
                counter += 1

        return entries

    def _serialize_entry(self, entry: IndexEntry) -> Dict[str, Any]:
        """Serialize an index entry for JSON persistence.

        Args:
            entry: Entry to serialize.

        Returns:
            JSON-safe dictionary.
        """
        return {
            "entry_id": entry.entry_id,
            "domain": entry.domain,
            "title": entry.title,
            "ac_ids": list(entry.ac_ids),
            "created_at": entry.created_at.isoformat(),
            "quality_score": entry.quality_score,
            "file_path": entry.file_path,
        }

    def _entry_from_payload(self, payload: Dict[str, Any]) -> IndexEntry:
        """Hydrate an IndexEntry from JSON payload data.

        Args:
            payload: Serialized entry dictionary.

        Returns:
            Hydrated index entry.
        """
        created_at_raw = str(payload.get("created_at", "2026-02-09T00:00:00"))
        return IndexEntry(
            entry_id=str(payload.get("entry_id", "")),
            domain=str(payload.get("domain", "KNOWLEDGE-CURATION")),
            title=str(payload.get("title", "")),
            ac_ids=list(payload.get("ac_ids", [])),
            created_at=datetime.fromisoformat(created_at_raw),
            quality_score=payload.get("quality_score"),
            file_path=payload.get("file_path"),
        )

    def _write_json_index(self, entries: List[IndexEntry]) -> Dict[str, Any]:
        """Persist the JSON sidecar index.

        Args:
            entries: Entries to persist.

        Returns:
            JSON payload written to disk.
        """
        ordered_entries = sorted(entries, key=lambda item: item.entry_id)
        by_domain: Dict[str, List[str]] = {domain: [] for domain in _CANONICAL_DOMAINS}
        ac_id_mapping: Dict[str, Dict[str, str]] = {}

        for entry in ordered_entries:
            by_domain.setdefault(entry.domain, []).append(entry.entry_id)
            for ac_id in entry.ac_ids:
                if ac_id not in ac_id_mapping:
                    ac_id_mapping[ac_id] = {
                        "entry_id": entry.entry_id,
                        "domain": entry.domain,
                    }

        timestamp = datetime.utcnow().isoformat()
        payload: Dict[str, Any] = {
            "metadata": {
                "version": "1.0",
                "ac_id": "KN-001-02",
                "created_at": timestamp,
                "updated_at": timestamp,
                "entry_count": len(ordered_entries),
            },
            "entries": [self._serialize_entry(entry) for entry in ordered_entries],
            "ac_id_mapping": ac_id_mapping,
            "by_domain": by_domain,
        }

        self._json_index_path.parent.mkdir(parents=True, exist_ok=True)
        self._json_index_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return payload

    def index_entry(self, entry: IndexEntry) -> bool:
        """Index a knowledge entry in SQLite and refresh the JSON sidecar.

        Args:
            entry: Entry to persist.

        Returns:
            True when persistence succeeds.
        """
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO entries
                (entry_id, domain, title, ac_ids, created_at, quality_score, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.entry_id,
                    entry.domain,
                    entry.title,
                    json.dumps(entry.ac_ids),
                    entry.created_at.isoformat(),
                    entry.quality_score,
                    entry.file_path,
                ),
            )
            conn.commit()

        self._write_json_index(self._fetch_db_entries())
        return True

    def search(self, query: str, domain: Optional[str] = None) -> List[IndexEntry]:
        """Search indexed entries by query string and optional domain.

        Args:
            query: Text to search in title or entry ID.
            domain: Optional domain filter.

        Returns:
            Matching index entries.
        """
        entries = [
            self._entry_from_payload(item)
            for item in self._load_json_index().get("entries", [])
        ]
        query_text = query.lower()
        matches: List[IndexEntry] = []

        for entry in entries:
            if domain and entry.domain != domain:
                continue
            if not query_text:
                matches.append(entry)
                continue
            if query_text in entry.title.lower() or query_text in entry.entry_id.lower():
                matches.append(entry)

        return matches

    def get_by_ac_id(self, ac_id: str) -> List[IndexEntry]:
        """Retrieve entries matching an AC identifier.

        Args:
            ac_id: Acceptance-criteria identifier.

        Returns:
            Entries containing the AC identifier.
        """
        return self.find_entries_by_ac_id(ac_id)

    def get_by_domain(self, domain: str) -> List[IndexEntry]:
        """Retrieve all entries for a domain.

        Args:
            domain: Canonical domain name.

        Returns:
            Entries assigned to that domain.
        """
        return self.find_entries_by_domain(domain)

    def find_entries_by_domain(self, domain: str) -> List[IndexEntry]:
        """Find entries for a canonical domain.

        Args:
            domain: Canonical domain name.

        Returns:
            Matching entries.
        """
        return self.search("", domain=domain)

    def find_entries_by_ac_id(self, ac_id: str) -> List[IndexEntry]:
        """Find entries containing an AC identifier.

        Args:
            ac_id: Acceptance-criteria identifier.

        Returns:
            Entries referencing the identifier.
        """
        entries = [
            self._entry_from_payload(item)
            for item in self._load_json_index().get("entries", [])
        ]
        return [entry for entry in entries if ac_id in entry.ac_ids]

    def find_domain_for_ac_id(self, ac_id: str) -> Optional[str]:
        """Find the canonical domain associated with an AC identifier.

        Args:
            ac_id: Acceptance-criteria identifier.

        Returns:
            Canonical domain when found, otherwise None.
        """
        mapping = self._load_json_index().get("ac_id_mapping", {})
        match = mapping.get(ac_id)
        if not isinstance(match, dict):
            return None
        domain = match.get("domain")
        return str(domain) if domain else None

    def search_by_title(self, query: str) -> List[IndexEntry]:
        """Search entries by title.

        Args:
            query: Case-insensitive title fragment.

        Returns:
            Entries with matching titles.
        """
        return self.search(query)

    def get_index_stats(self) -> Dict[str, Any]:
        """Return summary statistics for the current index.

        Returns:
            Dictionary with metadata, domain counts, and AC-ID totals.
        """
        payload = self._load_json_index()
        by_domain = payload.get("by_domain", {})
        return {
            "metadata": payload.get("metadata", {}),
            "domain_counts": {
                domain: len(entries)
                for domain, entries in by_domain.items()
                if isinstance(entries, list)
            },
            "ac_id_count": len(payload.get("ac_id_mapping", {})),
        }

    def rebuild_index(self) -> bool:
        """Rebuild the JSON index from registry and SQLite sources.

        Returns:
            True when the rebuild completes successfully.
        """
        registry_entries = self._build_registry_entries()
        db_entries = self._fetch_db_entries()
        merged: Dict[str, IndexEntry] = {entry.entry_id: entry for entry in registry_entries}
        merged.update({entry.entry_id: entry for entry in db_entries})
        self._write_json_index(list(merged.values()))
        return True

    def update_entry(self, entry: IndexEntry) -> bool:
        """Update a single knowledge entry.

        Args:
            entry: Entry to upsert.

        Returns:
            True when the update succeeds.
        """
        return self.index_entry(entry)

    def get_index_file(self) -> Path:
        """Return the path to the SQLite index file.

        Returns:
            SQLite index path.
        """
        return self._db_path

    def inventory(self) -> List[str]:
        """Return all indexed entry IDs as a list of strings.

        Returns:
            Entry identifiers currently present in the JSON index.
        """
        payload = self._load_json_index()
        return [
            str(entry.get("entry_id", ""))
            for entry in payload.get("entries", [])
            if entry.get("entry_id")
        ]
