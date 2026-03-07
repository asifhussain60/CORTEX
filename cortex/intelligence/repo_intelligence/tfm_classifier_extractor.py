"""TfmClassifierExtractor — detects .NET target framework monikers (TFMs).

Reads ``<TargetFramework>`` and ``<TargetFrameworks>`` elements from
``.csproj``, ``.vbproj``, and ``.fsproj`` project files.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor

_TFM_RE = re.compile(
    r"<TargetFrameworks?\s*>(.*?)</TargetFrameworks?>",
    re.IGNORECASE | re.DOTALL,
)
_PROJECT_GLOBS = ("*.csproj", "*.vbproj", "*.fsproj")


class TfmClassifierExtractor(BaseExtractor):
    """Extract .NET target framework monikers from project files.

    Returns:
        Dict with keys:
            - ``frameworks`` (list[str]): unique TFMs found (e.g. ``net8.0``).
            - ``frameworks_found`` (int): unique TFM count.
            - ``project_files`` (list[str]): project file paths scanned.
    """

    name: str = "tfm_classifier"

    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """Run extraction against *repo_path*.

        Args:
            repo_path: Repository root path.

        Returns:
            Extraction result dictionary.
        """
        frameworks: Set[str] = set()
        project_files: List[str] = []

        for glob in _PROJECT_GLOBS:
            for proj_file in repo_path.rglob(glob):
                rel = str(proj_file.relative_to(repo_path))
                project_files.append(rel)
                try:
                    content = proj_file.read_text(encoding="utf-8", errors="replace")
                    for match in _TFM_RE.finditer(content):
                        raw = match.group(1).strip()
                        # TargetFrameworks may be semicolon-separated
                        for tfm in raw.split(";"):
                            tfm = tfm.strip()
                            if tfm:
                                frameworks.add(tfm)
                except OSError:
                    continue

        sorted_frameworks = sorted(frameworks)
        return {
            "frameworks": sorted_frameworks,
            "frameworks_found": len(sorted_frameworks),
            "project_files": project_files,
        }
