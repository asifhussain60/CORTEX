"""SolutionTopologyExtractor — parses .sln files to build a project dependency graph.

Scans the repository root for Visual Studio Solution files and extracts
the list of included project names.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor

# Regex that matches the Project(...) = "Name", "Path", "{GUID}" lines in .sln
_SLN_PROJECT_RE = re.compile(
    r'Project\("\{[^}]+\}"\)\s*=\s*"([^"]+)"\s*,\s*"([^"]+)"',
    re.IGNORECASE,
)


class SolutionTopologyExtractor(BaseExtractor):
    """Extract project graph from Visual Studio .sln files.

    Returns:
        Dict with keys:
            - ``projects`` (list[str]): project names found in .sln files.
            - ``projects_found`` (int): count of discovered projects.
            - ``solution_files`` (list[str]): .sln file paths (relative).
    """

    name: str = "solution_topology"

    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """Run extraction against *repo_path*.

        Args:
            repo_path: Absolute path to the repository root.

        Returns:
            Extraction result dictionary.
        """
        projects: List[str] = []
        solution_files: List[str] = []

        for sln_file in repo_path.rglob("*.sln"):
            solution_files.append(str(sln_file.relative_to(repo_path)))
            try:
                content = sln_file.read_text(encoding="utf-8", errors="replace")
                for match in _SLN_PROJECT_RE.finditer(content):
                    proj_name = match.group(1)
                    proj_path = match.group(2)
                    # Skip Solution Folders (their "path" == their name with no extension)
                    if not proj_path.endswith((".csproj", ".vbproj", ".fsproj", ".sqlproj")):
                        # Accept if it looks like a project (has a folder separator)
                        if "\\" not in proj_path and "/" not in proj_path:
                            continue
                    projects.append(proj_name)
            except OSError:
                continue

        return {
            "projects": projects,
            "projects_found": len(projects),
            "solution_files": solution_files,
        }
