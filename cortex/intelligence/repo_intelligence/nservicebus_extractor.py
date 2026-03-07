"""NServiceBusExtractor — discovers NServiceBus message handlers and sagas.

Scans C# source files for ``IHandleMessages<T>``, ``Saga<T>``, and
``IAmStartedByMessages<T>`` patterns.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor

_HANDLER_PATTERNS = [
    re.compile(r"IHandleMessages\s*<", re.IGNORECASE),
    re.compile(r"IAmStartedByMessages\s*<", re.IGNORECASE),
]
_SAGA_RE = re.compile(r":\s*Saga\s*<", re.IGNORECASE)


class NServiceBusExtractor(BaseExtractor):
    """Detect NServiceBus message handlers and sagas in C# source files.

    Returns:
        Dict with keys:
            - ``handlers`` (list[str]): files containing IHandleMessages<T>.
            - ``sagas`` (list[str]): files containing Saga<T>.
            - ``handlers_found`` (int): count of handler files.
            - ``sagas_found`` (int): count of saga files.
    """

    name: str = "nservicebus"

    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """Run extraction against *repo_path*.

        Args:
            repo_path: Repository root path.

        Returns:
            Extraction result dictionary.
        """
        handlers: List[str] = []
        sagas: List[str] = []

        for cs_file in repo_path.rglob("*.cs"):
            try:
                content = cs_file.read_text(encoding="utf-8", errors="replace")
                if any(pat.search(content) for pat in _HANDLER_PATTERNS):
                    handlers.append(str(cs_file.relative_to(repo_path)))
                if _SAGA_RE.search(content):
                    sagas.append(str(cs_file.relative_to(repo_path)))
            except OSError:
                continue

        return {
            "handlers": handlers,
            "sagas": sagas,
            "handlers_found": len(handlers),
            "sagas_found": len(sagas),
        }
