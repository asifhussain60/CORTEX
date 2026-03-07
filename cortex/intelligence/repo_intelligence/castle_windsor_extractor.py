"""CastleWindsorExtractor — detects Castle Windsor IoC container registrations.

Scans C# source files for ``container.Register`` / ``Component.For`` / ``Castle.Windsor``
call patterns.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor

_REGISTRATION_PATTERNS = [
    re.compile(r"container\.Register\s*\(", re.IGNORECASE),
    re.compile(r"Component\.For\s*<", re.IGNORECASE),
    re.compile(r"Castle\.Windsor", re.IGNORECASE),
    re.compile(r"IWindsorContainer", re.IGNORECASE),
]


class CastleWindsorExtractor(BaseExtractor):
    """Detect Castle Windsor IoC registrations in C# source files.

    Returns:
        Dict with keys:
            - ``registrations`` (list[str]): files containing Castle Windsor usage.
            - ``registrations_found`` (int): count of matched files.
    """

    name: str = "castle_windsor"

    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """Run extraction against *repo_path*.

        Args:
            repo_path: Repository root path.

        Returns:
            Extraction result dictionary.
        """
        registrations: List[str] = []

        for cs_file in repo_path.rglob("*.cs"):
            try:
                content = cs_file.read_text(encoding="utf-8", errors="replace")
                if any(pat.search(content) for pat in _REGISTRATION_PATTERNS):
                    registrations.append(str(cs_file.relative_to(repo_path)))
            except OSError:
                continue

        return {
            "registrations": registrations,
            "registrations_found": len(registrations),
        }
