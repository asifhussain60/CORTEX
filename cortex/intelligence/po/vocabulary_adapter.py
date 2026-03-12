"""Vocabulary Adapter — translates developer terms to SAFe/Scrum language (GAP-129-06)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

_VOCAB_FILE = (
    Path(__file__).parent.parent.parent.parent
    / "cortex-registry"
    / "knowledge"
    / "po"
    / "safe-scrum-vocabulary.yaml"
)


class VocabularyAdapter:
    """Translates CORTEX/developer terminology into SAFe/Scrum language.

    Loads translations from safe-scrum-vocabulary.yaml (SSOT).
    Falls back to built-in minimal vocabulary if file unavailable.
    """

    def __init__(self, vocab_file: Optional[Path] = None) -> None:
        self._vocab_file = Path(vocab_file) if vocab_file else _VOCAB_FILE
        data = self._load_vocab()
        self._translations: Dict[str, str] = data.get("translations", {})
        self._ceremonies: Dict[str, Any] = data.get("ceremonies", {})

    def translate(self, developer_term: str) -> str:
        """Translate a single developer term to SAFe/Scrum equivalent.

        Returns the original term if no translation is found.
        """
        exact = self._translations.get(developer_term)
        if exact:
            return exact
        lower = developer_term.lower()
        for key, value in self._translations.items():
            if key.lower() == lower:
                return value
        return developer_term

    def translate_text(self, text: str) -> str:
        """Replace all known developer terms in a block of text with SAFe equivalents."""
        result = text
        # Longest-first to avoid partial replacements
        for term, translation in sorted(
            self._translations.items(), key=lambda x: len(x[0]), reverse=True
        ):
            result = result.replace(term, translation)
        return result

    def available_terms(self) -> List[str]:
        """Return list of developer terms with translations."""
        return list(self._translations.keys())

    def ceremony_guidance(self, ceremony_name: str) -> Dict[str, Any]:
        """Return ceremony guidance for a given SAFe ceremony name (case-insensitive)."""
        lower = ceremony_name.lower().replace(" ", "_")
        for key, value in self._ceremonies.items():
            if key.lower() == lower or value.get("name", "").lower() == ceremony_name.lower():
                return value
        return {}

    def _load_vocab(self) -> Dict[str, Any]:
        if self._vocab_file.exists() and yaml is not None:
            try:
                return yaml.safe_load(self._vocab_file.read_text()) or {}
            except Exception:
                pass
        return {
            "translations": {
                "orchestrator": "workflow automation engine",
                "LENS analysis": "codebase intelligence scan",
                "CORTEX": "AI engineering assistant",
                "TDD": "Test-Driven Development",
                "RCA": "Root Cause Analysis",
                "WSJF": "Weighted Shortest Job First",
            },
            "ceremonies": {},
        }
