"""NHibernateExtractor — discovers NHibernate ORM mapping files.

Looks for ``.hbm.xml`` mapping files and C# classes decorated with
FluentNHibernate ``ClassMap<T>`` patterns.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor

_CLASSMAP_RE = re.compile(r"ClassMap\s*<\s*\w+\s*>", re.IGNORECASE)


class NHibernateExtractor(BaseExtractor):
    """Detect NHibernate ORM mappings — both .hbm.xml and FluentNHibernate ClassMap<T>.

    Returns:
        Dict with keys:
            - ``mappings`` (list[str]): paths to .hbm.xml files found.
            - ``fluent_mappings`` (list[str]): C# files with ClassMap<T>.
            - ``mappings_found`` (int): total mapping artefact count.
    """

    name: str = "nhibernate"

    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """Run extraction against *repo_path*.

        Args:
            repo_path: Repository root path.

        Returns:
            Extraction result dictionary.
        """
        mappings: List[str] = []
        fluent_mappings: List[str] = []

        # Classic XML mappings
        for hbm in repo_path.rglob("*.hbm.xml"):
            mappings.append(str(hbm.relative_to(repo_path)))

        # FluentNHibernate ClassMap<T>
        for cs_file in repo_path.rglob("*.cs"):
            try:
                content = cs_file.read_text(encoding="utf-8", errors="replace")
                if _CLASSMAP_RE.search(content):
                    fluent_mappings.append(str(cs_file.relative_to(repo_path)))
            except OSError:
                continue

        total = len(mappings) + len(fluent_mappings)
        return {
            "mappings": mappings,
            "fluent_mappings": fluent_mappings,
            "mappings_found": total,
        }
