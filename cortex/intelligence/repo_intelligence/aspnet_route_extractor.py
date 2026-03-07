"""AspNetRouteExtractor — maps the HTTP API surface of an ASP.NET Core application.

Scans C# controller files for ``[HttpGet]``, ``[HttpPost]``, ``[HttpPut]``,
``[HttpDelete]``, ``[HttpPatch]``, and ``[Route]`` attribute annotations.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor

_ROUTE_RE = re.compile(
    r'\[(HttpGet|HttpPost|HttpPut|HttpDelete|HttpPatch|Route)\s*(?:\("([^"]*)"\))?\]',
    re.IGNORECASE,
)


class AspNetRouteExtractor(BaseExtractor):
    """Extract ASP.NET Core HTTP route declarations from C# controller files.

    Returns:
        Dict with keys:
            - ``routes`` (list[dict]): each entry has ``method``, ``path``, ``file``.
            - ``routes_found`` (int): total route count.
    """

    name: str = "aspnet_routes"

    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """Run extraction against *repo_path*.

        Args:
            repo_path: Repository root path.

        Returns:
            Extraction result dictionary.
        """
        routes: List[Dict[str, str]] = []

        for cs_file in repo_path.rglob("*.cs"):
            try:
                content = cs_file.read_text(encoding="utf-8", errors="replace")
                rel = str(cs_file.relative_to(repo_path))
                for match in _ROUTE_RE.finditer(content):
                    method = match.group(1).upper()
                    path = match.group(2) or ""
                    routes.append({"method": method, "path": path, "file": rel})
            except OSError:
                continue

        return {
            "routes": routes,
            "routes_found": len(routes),
        }
