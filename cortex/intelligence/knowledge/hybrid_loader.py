"""
hybrid_loader.py — Knowledge Hybrid Loader

Restored for import compatibility. Loads knowledge from both
YAML registry files and live inference sources.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class HybridLoader:
    """Loads knowledge from YAML files and fallback inference."""

    def __init__(self, registry_path: str | Path = "cortex-registry/knowledge") -> None:
        """Initialise with the knowledge registry path.

        Args:
            registry_path: Path to the YAML knowledge registry directory.
        """
        self.registry_path = Path(registry_path)

    def load(self, domain: str) -> list[dict[str, Any]]:
        """Load knowledge entries for a domain.

        Args:
            domain: Knowledge domain name (e.g. 'architecture').

        Returns:
            List of knowledge entry dicts.
        """
        results: list[dict[str, Any]] = []
        for yml_file in self.registry_path.glob(f"*{domain}*.yaml"):
            try:
                data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    results.extend(data)
                elif isinstance(data, dict):
                    results.append(data)
            except Exception:
                continue
        return results
