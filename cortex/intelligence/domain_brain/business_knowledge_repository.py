"""Business Knowledge Repository — YAML-backed implementation.

Provides YAML file-based persistence for business knowledge entries
in the Domain Brain (Phase 84-b/c, GAP-84-03).

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


_DEFAULT_RULES_PATH = (
    Path(__file__).resolve().parents[4]
    / "cortex-registry" / "company" / "domains" / "shared" / "business-rules.yaml"
)


@dataclass
class BusinessKnowledgeEntry:
    """A single business knowledge entry stored in the repository."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BusinessKnowledgeRepository:
    """YAML-backed repository for business knowledge entries.

    Replaces the in-memory implementation with file-based
    persistence. Rules are loaded from and saved to a YAML file under
    cortex-registry/company/domains/shared/.
    """

    def __init__(self, rules_path: Optional[Path] = None) -> None:
        """Initialise the repository.

        Args:
            rules_path: Path to the YAML rules file. Defaults to the
                        shared business-rules.yaml in cortex-registry.
        """
        self._path: Path = Path(rules_path) if rules_path else _DEFAULT_RULES_PATH
        self._entries: Dict[str, BusinessKnowledgeEntry] = {}
        self._load()

    def add(self, entry: BusinessKnowledgeEntry) -> None:
        """Add a business knowledge entry.

        Args:
            entry: The entry to add.
        """
        self._entries[entry.id] = entry
        self._save()

    def get(self, entry_id: str) -> Optional[BusinessKnowledgeEntry]:
        """Retrieve a business knowledge entry by ID.

        Args:
            entry_id: Unique identifier string.

        Returns:
            BusinessKnowledgeEntry if found, else None.
        """
        return self._entries.get(entry_id)

    def list_all(self) -> List[BusinessKnowledgeEntry]:
        """Return all knowledge entries."""
        return list(self._entries.values())

    def get_rules(self) -> List[Dict[str, Any]]:
        """Return all rules as raw dicts (compatible with rule-based usage)."""
        rules_data: List[Dict[str, Any]] = []
        if self._path.exists():
            try:
                data = yaml.safe_load(self._path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    rules_data = data.get("rules", [])
            except Exception:
                pass
        return rules_data

    def reload(self) -> None:
        """Reload entries from the YAML file."""
        self._load()

    def _load(self) -> None:
        """Load entries from the YAML file if it exists."""
        if not self._path.exists():
            return
        try:
            data = yaml.safe_load(self._path.read_text(encoding="utf-8")) or {}
            for rule in data.get("rules", []):
                if isinstance(rule, dict) and "id" in rule:
                    entry = BusinessKnowledgeEntry(
                        id=str(rule["id"]),
                        content=str(rule.get("description", "")),
                        metadata=rule,
                    )
                    self._entries[entry.id] = entry
        except Exception:
            pass

    def _save(self) -> None:
        """Persist entries to the YAML file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        rules = [
            {"id": e.id, "description": e.content, **{k: v for k, v in e.metadata.items() if k not in ("id", "description")}}
            for e in self._entries.values()
        ]
        with open(self._path, "w", encoding="utf-8") as f:
            yaml.dump({"rules": rules, "version": "1.0"}, f, default_flow_style=False)
