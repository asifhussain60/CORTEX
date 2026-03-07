"""AngularExtractor — discovers Angular modules and components.

Scans TypeScript source files for ``@NgModule`` and ``@Component``
decorator declarations.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor

_NGMODULE_RE = re.compile(r"@NgModule\s*\(", re.IGNORECASE)
_COMPONENT_RE = re.compile(r"@Component\s*\(", re.IGNORECASE)
_INJECTABLE_RE = re.compile(r"@Injectable\s*\(", re.IGNORECASE)


class AngularExtractor(BaseExtractor):
    """Extract Angular module and component declarations from TypeScript files.

    Returns:
        Dict with keys:
            - ``modules`` (list[str]): files containing @NgModule.
            - ``components`` (list[str]): files containing @Component.
            - ``modules_found`` (int): count of module files.
            - ``components_found`` (int): count of component files.
    """

    name: str = "angular"

    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """Run extraction against *repo_path*.

        Args:
            repo_path: Repository root path.

        Returns:
            Extraction result dictionary.
        """
        modules: List[str] = []
        components: List[str] = []

        for ts_file in repo_path.rglob("*.ts"):
            try:
                content = ts_file.read_text(encoding="utf-8", errors="replace")
                rel = str(ts_file.relative_to(repo_path))
                if _NGMODULE_RE.search(content):
                    modules.append(rel)
                if _COMPONENT_RE.search(content):
                    components.append(rel)
            except OSError:
                continue

        return {
            "modules": modules,
            "components": components,
            "modules_found": len(modules),
            "components_found": len(components),
        }
