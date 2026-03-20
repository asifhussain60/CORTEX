"""RegistryIndexManager utilities for thin-index phase access."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


class RegistryIndexManager:
    """Read-only helper over the master index YAML."""

    def __init__(self, master_index_path: Path) -> None:
        """Initialize manager.

        Args:
            master_index_path: Path to master YAML index file.
        """
        self._master_index_path = master_index_path

    def _load(self) -> Dict[str, Any]:
        """Load master index document.

        Returns:
            Parsed YAML mapping.
        """
        with self._master_index_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        return data if isinstance(data, dict) else {}

    def list_phase_ids(self) -> List[str]:
        """Return phase ids from the master index.

        Returns:
            Ordered list of phase ids.
        """
        data = self._load()
        phases = data.get("phases", [])
        phase_ids: List[str] = []
        for phase in phases:
            if isinstance(phase, dict):
                phase_id = phase.get("id")
                if isinstance(phase_id, str):
                    phase_ids.append(phase_id)
        return phase_ids
