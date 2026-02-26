"""registry_backed_orchestrator_registry.py — Registry-Backed Orchestrator Registry.

Auto-loads orchestrator entries from wiring YAML specs (Phase 84-c, GAP-84-11).
Imported by cortex/tools/orchestrator_scaffolder.py.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

_SPECS_DIR = (
    Path(__file__).resolve().parents[3] / "cortex-registry" / "core" / "specifications"
)


class RegistryBackedOrchestratorRegistry:
    """
    Orchestrator registry backed by wiring YAML specifications.

    On initialisation, auto-loads entries from all wiring YAML files in
    cortex-registry/core/specifications/. Replaces the empty dict-only stub
    (GAP-84-11).
    """

    def __init__(self) -> None:
        """Initialise and auto-load from wiring YAML specs."""
        self._entries: Dict[str, Any] = {}
        self._load_from_specs()

    # ── Public API ───────────────────────────────────────────────────────────

    def register(self, name: str, cls: Any) -> None:
        """
        Register an orchestrator class by name.

        Args:
            name: Orchestrator name key.
            cls: Orchestrator class or any associated value.
        """
        self._entries[name] = cls

    def get(self, name: str) -> Optional[Any]:
        """
        Retrieve an orchestrator entry by name.

        Args:
            name: Orchestrator name.

        Returns:
            Registered value or None.
        """
        return self._entries.get(name)

    def list_all(self) -> List[str]:
        """
        Return all registered orchestrator names.

        Returns:
            List of registered orchestrator name strings.
        """
        return list(self._entries.keys())

    # ── Private helpers ───────────────────────────────────────────────────────

    def _load_from_specs(self) -> None:
        """Load orchestrator names from all wiring YAML files in the specs dir."""
        if not _SPECS_DIR.exists():
            logger.debug("RegistryBackedOrchestratorRegistry: specs dir not found %s", _SPECS_DIR)
            return

        for spec_file in _SPECS_DIR.glob("*-wiring.yaml"):
            try:
                data = yaml.safe_load(spec_file.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
                self._extract_entries(data, source=spec_file.name)
            except Exception as exc:
                logger.warning("RegistryBackedOrchestratorRegistry: failed to load %s — %s", spec_file, exc)

    def _extract_entries(self, data: Dict[str, Any], source: str) -> None:
        """
        Extract and register orchestrator names from a parsed wiring YAML.

        Args:
            data: Parsed wiring YAML dict.
            source: Source filename (used as a tag).
        """
        for key in ("orchestrators", "wired_orchestrators", "provides", "initialization_order"):
            entries = data.get(key, [])
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict):
                        name = entry.get("name") or entry.get("class") or entry.get("module_name")
                        if name:
                            self._entries[str(name)] = {"source": source, "meta": entry}
                    elif isinstance(entry, str):
                        self._entries[entry] = {"source": source}

        # Fallback: module_name as a single entry
        if "module_name" in data and data["module_name"] not in self._entries:
            self._entries[str(data["module_name"])] = {"source": source}