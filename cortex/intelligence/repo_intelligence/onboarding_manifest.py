"""OnboardingManifest — structured output for Universal Repo Intelligence Engine.

Holds per-extractor results and a high-level summary, serialisable to
dict / JSON for storage in the CORTEX intelligence registry.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class OnboardingManifest:
    """Structured manifest produced by the 8-extractor repo intelligence pipeline.

    Attributes:
        repo_path: Absolute path to the repository that was analysed.
        extractor_results: Mapping of extractor name → result dict.
        summary: High-level narrative / key stats (populated by facade).
    """

    def __init__(
        self,
        repo_path: Path,
        extractor_results: Optional[Dict[str, Dict[str, Any]]] = None,
        summary: Optional[str] = None,
    ) -> None:
        """Initialise manifest.

        Args:
            repo_path: Repository root path.
            extractor_results: Optional pre-populated extractor results.
            summary: Optional high-level summary string.
        """
        self.repo_path: Path = repo_path
        self.extractor_results: Dict[str, Dict[str, Any]] = extractor_results or {}
        self.summary: str = summary or ""

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise manifest to a plain dictionary.

        Returns:
            Dict with ``repo_path`` (str), ``extractor_results``, ``summary``.
        """
        return {
            "repo_path": str(self.repo_path),
            "extractor_results": self.extractor_results,
            "summary": self.summary,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialise manifest to a JSON string.

        Args:
            indent: Pretty-print indentation level.

        Returns:
            JSON-encoded string representation.
        """
        return json.dumps(self.to_dict(), indent=indent, default=str)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        n = len(self.extractor_results)
        return f"OnboardingManifest(repo={self.repo_path.name!r}, extractors={n})"
