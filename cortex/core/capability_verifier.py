"""CapabilityVerifier — Import-time architecture drift detection.

Reads cortex-registry/config/capabilities-manifest.yaml and attempts
importlib.import_module() for every declared orchestrator. Returns a
drift list of unimportable modules, enabling init-time architecture
drift detection.

Authority: CORE-011 (type hints), CORE-012 (docstrings), CORE-035, CORE-064
Phase: 137 (GAP-137-02)
"""
from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)

__all__ = ["verify_capabilities_manifest"]


def verify_capabilities_manifest(manifest_path: str) -> List[Dict[str, Any]]:
    """Verify all declared orchestrators in the capabilities manifest are importable.

    Reads the manifest YAML at ``manifest_path`` and attempts to import each
    declared orchestrator module. Returns a list of drift entries for any
    modules that cannot be imported. An empty return list means no drift.

    Args:
        manifest_path: Absolute path to the capabilities-manifest.yaml file.

    Returns:
        List of drift entry dicts — each with keys:
          - ``orchestrator`` — orchestrator id string
          - ``module`` — declared module path
          - ``tier`` — declared tier (e.g. ``"core"``)
          - ``error`` — import error message

        Empty list when all declared modules are importable.

    Raises:
        FileNotFoundError: When ``manifest_path`` does not exist.
    """
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        raise FileNotFoundError(f"Capabilities manifest not found: {manifest_path}")

    try:
        data = yaml.safe_load(manifest_file.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        logger.error("verify_capabilities_manifest: failed to parse %s — %s", manifest_path, exc)
        return []

    drift: List[Dict[str, Any]] = []

    orchestrators_section = data.get("orchestrators", {})
    tiers = orchestrators_section.get("tiers", {})

    for tier_name, tier_data in tiers.items():
        if not isinstance(tier_data, dict):
            continue
        members = tier_data.get("members", [])
        if not isinstance(members, list):
            continue

        for member in members:
            if not isinstance(member, dict):
                continue
            orch_id = member.get("id", "<unknown>")
            module_path = member.get("module", "")
            tier = member.get("tier", tier_name)

            if not module_path:
                continue

            try:
                importlib.import_module(module_path)
            except (ImportError, ModuleNotFoundError) as exc:
                drift.append({
                    "orchestrator": orch_id,
                    "module": module_path,
                    "tier": tier,
                    "error": str(exc),
                })
                logger.warning(
                    "verify_capabilities_manifest: drift detected — %s (%s): %s",
                    orch_id,
                    module_path,
                    exc,
                )

    if drift:
        logger.warning(
            "verify_capabilities_manifest: %d unimportable module(s) detected",
            len(drift),
        )
    else:
        logger.debug("verify_capabilities_manifest: no drift detected — all modules importable")

    return drift
