"""
discovery_pipeline.py — Documentation Discovery Pipeline

Restored for import compatibility. Scans workspace for
documentation artefacts.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class DiscoveryPipeline:
    """Discovers documentation files across the workspace."""

    def __init__(self, root: str | Path = ".") -> None:
        """Initialise pipeline with a workspace root.

        Args:
            root: Root directory to scan.
        """
        self.root = Path(root)

    def discover(self) -> list[dict[str, Any]]:
        """Run discovery and return list of found doc artefacts.

        Returns:
            List of artefact dicts with 'path' and 'type' keys.
        """
        results: list[dict[str, Any]] = []
        for ext in ("*.md", "*.rst", "*.html"):
            for p in self.root.rglob(ext):
                results.append({"path": str(p), "type": ext.lstrip("*.")})
        return results
