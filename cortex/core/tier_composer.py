"""tier_composer.py — Tier Composer.

Reads wiring YAML specs to build the orchestrator tier map (Phase 84-c, GAP-84-09).
Imported by cortex/testing/auto_initialization_suite.py.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)

_SPECS_DIR = Path(__file__).resolve().parents[2] / "cortex-registry" / "core" / "specifications"
_TIER_WIRING_FILES = {
    "core": "core-orchestrator-wiring.yaml",
    "domain": "domain-orchestrator-wiring.yaml",
    "support": "support-orchestrator-wiring.yaml",
    "git": "git-orchestrator-wiring.yaml",
}


class TierComposer:
    """
    Composes orchestrator tiers by reading wiring YAML specifications.

    Replaces the hollow stub that returned empty tier lists (GAP-84-09).
    Reads cortex-registry/core/specifications/*.yaml to build a tier map
    of orchestrator names per tier.
    """

    def compose_tiers(self) -> Dict[str, List[str]]:
        """
        Read wiring YAML specs and return the orchestrator tier map.

        Parses core-orchestrator-wiring.yaml, domain-orchestrator-wiring.yaml,
        support-orchestrator-wiring.yaml, and git-orchestrator-wiring.yaml.

        Returns:
            Dict mapping tier names ('core', 'domain', 'support', 'git') to
            lists of orchestrator class names found in each spec.
        """
        tier_map: Dict[str, List[str]] = {tier: [] for tier in _TIER_WIRING_FILES}

        for tier, filename in _TIER_WIRING_FILES.items():
            spec_path = _SPECS_DIR / filename
            if not spec_path.exists():
                logger.debug("TierComposer: spec not found %s", spec_path)
                continue
            try:
                data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
                # Extract orchestrator names from the wiring spec
                names = self._extract_names(data)
                tier_map[tier] = names
            except Exception as exc:
                logger.warning("TierComposer: failed to read %s — %s", spec_path, exc)

        return tier_map

    # ── Private helpers ──────────────────────────────────────────────────────

    def _extract_names(self, data: Dict[str, Any]) -> List[str]:
        """
        Extract orchestrator names from a wiring YAML dict.

        Looks for 'orchestrators', 'wired_orchestrators', 'provides', or
        'module_name' keys to build the list.

        Args:
            data: Parsed wiring YAML dict.

        Returns:
            List of orchestrator names found in the spec.
        """
        names: List[str] = []

        # Common patterns in wiring YAML files (covers all known key variants)
        for key in ("orchestrators", "wired_orchestrators", "provides", "initialization_order"):
            entries = data.get(key, [])
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict):
                        name = entry.get("name") or entry.get("class") or entry.get("module_name")
                        if name:
                            names.append(str(name))
                    elif isinstance(entry, str):
                        names.append(entry)

        # Fallback: use module_name if no orchestrators list found
        if not names and "module_name" in data:
            names.append(str(data["module_name"]))

        return names
