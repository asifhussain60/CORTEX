"""AICurator — AI-assisted knowledge curation (KN-002-01)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class CurationResult:
    entry_id: str
    quality_score: float
    is_duplicate: bool
    suggested_categories: List[str]
    recommendations: List[str]


class AICurator:
    """Curates knowledge entries using AI-assisted quality scoring."""

    _CONFIG_PATH = (
        Path(__file__).parent.parent.parent.parent.parent.parent
        / "cortex.intelligence" / "tier3" / "knowledge" / "curation-config.yaml"
    )

    def __init__(self) -> None:
        """Initialize instance."""
        self._config: Optional[Dict[str, Any]] = None

    def _load_config(self) -> Dict[str, Any]:
        """Load config."""
        if self._config is None:
            if self._CONFIG_PATH.exists():
                self._config = yaml.safe_load(self._CONFIG_PATH.read_text()) or {}
            else:
                self._config = {}
        return self._config

    def score_quality(self, entry: Dict[str, Any]) -> float:
        """Score entry quality 0.0–1.0."""
        score = 0.5
        if entry.get("title"):
            score += 0.1
        if entry.get("description") and len(str(entry["description"])) > 50:
            score += 0.2
        if entry.get("tags"):
            score += 0.1
        if entry.get("examples"):
            score += 0.1
        return min(1.0, score)

    def detect_duplicate(self, entry: Dict[str, Any], corpus: List[Dict[str, Any]]) -> bool:
        """Return True if entry is a likely duplicate."""
        title = str(entry.get("title", "")).lower()
        for existing in corpus:
            existing_title = str(existing.get("title", "")).lower()
            if title == existing_title:
                return True
        return False

    def suggest_categories(self, entry: Dict[str, Any]) -> List[str]:
        """Suggest categories based on entry content."""
        config = self._load_config()
        categories = config.get("categories", [])
        text = f"{entry.get('title','')} {entry.get('description','')}".lower()
        return [c for c in categories if c.lower() in text] or ["general"]

    def curate(self, entry: Dict[str, Any], corpus: Optional[List[Dict[str, Any]]] = None) -> CurationResult:
        """Run full curation pipeline on an entry."""
        entry_id = str(entry.get("id", "unknown"))
        quality = self.score_quality(entry)
        is_dup = self.detect_duplicate(entry, corpus or [])
        categories = self.suggest_categories(entry)
        recs: List[str] = []
        if quality < 0.7:
            recs.append("Improve description length and detail")
        if not entry.get("examples"):
            recs.append("Add usage examples")
        if is_dup:
            recs.append("Review for duplication with existing entries")
        return CurationResult(
            entry_id=entry_id,
            quality_score=quality,
            is_duplicate=is_dup,
            suggested_categories=categories,
            recommendations=recs,
        )