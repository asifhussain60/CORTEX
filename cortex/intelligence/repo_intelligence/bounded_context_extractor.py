"""BoundedContextExtractor — infers domain boundary structure from folder layout.

Detects bounded contexts by looking for top-level folders that contain a
``Domain`` sub-folder — a common DDD convention in .NET enterprise projects.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor

# Sub-folder names that signal a bounded context / domain namespace
_DOMAIN_MARKERS = {"Domain", "domain", "Core", "Application", "Infrastructure"}


class BoundedContextExtractor(BaseExtractor):
    """Infer bounded contexts from DDD-style folder structures.

    Looks for top-level directories containing at least one recognised
    domain-marker sub-folder (``Domain``, ``Core``, ``Application``,
    ``Infrastructure``).

    Returns:
        Dict with keys:
            - ``contexts`` (list[str]): names of identified bounded context folders.
            - ``contexts_found`` (int): count.
    """

    name: str = "bounded_contexts"

    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """Run extraction against *repo_path*.

        Args:
            repo_path: Repository root path.

        Returns:
            Extraction result dictionary.
        """
        contexts: List[str] = []

        for candidate in sorted(repo_path.iterdir()):
            if not candidate.is_dir():
                continue
            if candidate.name.startswith("."):
                continue
            # Check for at least one domain-marker sub-folder
            sub_names = {child.name for child in candidate.iterdir() if child.is_dir()}
            if sub_names & _DOMAIN_MARKERS:
                contexts.append(candidate.name)

        return {
            "contexts": contexts,
            "contexts_found": len(contexts),
        }
