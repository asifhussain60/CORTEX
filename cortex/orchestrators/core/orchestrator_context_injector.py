"""
Orchestrator Context Injector

Injects orchestrator metadata (from wiring YAMLs) into decorated function results.
Reads ``cortex-registry/core/specifications/*.yaml`` to extract per-orchestrator
category, description, entry_point, and features at runtime.

Authority: GAP-117-03c — Phase 117-b (injector real implementation replacing placeholder)
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

import logging
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List

import yaml

logger = logging.getLogger(__name__)

# ── Wiring YAML paths (relative to project root) ─────────────────────────────
_WIRING_SPECS_DIR: Path = (
    Path(__file__).parents[3] / "cortex-registry" / "core" / "specifications"
)
_WIRING_YAML_FILES: List[str] = [
    "core-orchestrator-wiring.yaml",
    "orchestration-master-wiring.yaml",
    "domain-orchestrator-wiring.yaml",
    "support-orchestrator-wiring.yaml",
    "git-orchestrator-wiring.yaml",
]


class OrchestratorMetadataRegistry:
    """In-process cache of orchestrator metadata entries."""

    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, orchestrator_id: str, metadata: Dict[str, Any]) -> None:
        """Register (or overwrite) metadata for *orchestrator_id*."""
        cls._registry[orchestrator_id] = metadata

    @classmethod
    def get(cls, orchestrator_id: str) -> Dict[str, Any]:
        """Return registered metadata or ``{}`` when not found."""
        return cls._registry.get(orchestrator_id, {})


# ── YAML loading helper (patchable in tests) ─────────────────────────────────


def _load_wiring_yaml(yaml_path: Path) -> Dict[str, Any]:
    """Load and parse a single wiring YAML file.

    Args:
        yaml_path: Absolute path to the YAML file.

    Returns:
        Parsed dict, or ``{}`` on any read/parse error.
    """
    try:
        with yaml_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            return data if isinstance(data, dict) else {}
    except Exception as exc:  # pragma: no cover — I/O errors
        logger.debug("_load_wiring_yaml: could not load %s — %s", yaml_path, exc)
        return {}


def extract_orchestrator_metadata_from_wiring(orchestrator_name: str) -> Dict[str, Any]:
    """Extract orchestrator metadata by searching all wiring YAML files.

    Each wiring YAML has a top-level ``provides`` key whose value is a list of
    dicts with at minimum a ``name`` field.  This function searches all files in
    ``_WIRING_YAML_FILES`` for an entry whose ``name`` matches *orchestrator_name*
    (case-insensitive substring match).

    Args:
        orchestrator_name: Display name or class name of the orchestrator.

    Returns:
        Dict with keys ``name``, ``category``, ``description``, ``entry_point``,
        ``features``, ``source_yaml``, ``version`` — or ``{}`` when not found.
    """
    name_lower = orchestrator_name.lower()
    for yaml_filename in _WIRING_YAML_FILES:
        yaml_path = _WIRING_SPECS_DIR / yaml_filename
        if not yaml_path.exists():
            continue
        try:
            data = _load_wiring_yaml(yaml_path)
        except Exception as exc:
            logger.debug(
                "extract_orchestrator_metadata_from_wiring: error loading %s — %s",
                yaml_filename,
                exc,
            )
            continue
        # Top-level `provides` is a list of orchestrator entry dicts
        provides: Any = data.get("provides", [])
        if not isinstance(provides, list):
            continue
        for entry in provides:
            if not isinstance(entry, dict):
                continue
            entry_name = str(entry.get("name", ""))
            if name_lower in entry_name.lower():
                return {
                    "name": entry.get("name", orchestrator_name),
                    "category": entry.get("category", ""),
                    "description": entry.get("description", ""),
                    "entry_point": entry.get("entry_point", ""),
                    "features": entry.get("features", []),
                    "source_yaml": yaml_filename,
                    "version": entry.get("version", ""),
                }
    logger.debug(
        "extract_orchestrator_metadata_from_wiring: '%s' not found in wiring specs",
        orchestrator_name,
    )
    return {}


def inject_orchestrator_context(func: Callable) -> Callable:
    """Decorator: inject ``_orchestrator_meta`` into dict-typed function results.

    When the decorated function returns a ``dict``, the decorator enriches it
    with an ``_orchestrator_meta`` key containing metadata extracted from the
    wiring YAMLs.  Non-dict results are passed through unchanged.

    Args:
        func: The orchestrator method or function to decorate.

    Returns:
        Wrapped callable with context injection.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Invoke *func* and enrich dict results with orchestrator metadata."""
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            # Derive a plausible orchestrator name from the owning class (if any)
            orchestrator_name: str = ""
            if args:
                cls = type(args[0])
                orchestrator_name = cls.__name__
            meta = extract_orchestrator_metadata_from_wiring(orchestrator_name)
            result.setdefault("_orchestrator_meta", meta)
        return result

    return wrapper
