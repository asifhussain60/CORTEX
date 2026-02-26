"""governance_principles.py — Governance Principles.

Provides human-readable names and descriptions for CORE governance rules
(Phase 84-d, GAP-84-24). Loads from the YAML registry at
cortex-registry/core/tier0-skull/ when available; falls back to the
embedded lookup table.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

from typing import Dict, List, Optional

_PRINCIPLES: Dict[str, Dict[str, str]] = {
    "CORE-002": {
        "name": "Inline Output Only",
        "description": "All output must appear inline; never create .md/.txt report files.",
    },
    "CORE-008": {
        "name": "TDD Mandatory",
        "description": "Write failing tests first; implement minimum code to pass; refactor.",
    },
    "CORE-011": {
        "name": "Type Hints Required",
        "description": "All function and method signatures must carry type annotations.",
    },
    "CORE-012": {
        "name": "Docstrings Required",
        "description": "All public functions, methods, and classes must have docstrings.",
    },
    "CORE-028": {
        "name": "Snake Case Naming",
        "description": "All file names use snake_case; no camelCase or kebab-case.",
    },
    "CORE-035": {
        "name": "Single Canonical Implementation",
        "description": "No duplicate implementations; one authoritative source per concept.",
    },
    "CORE-048": {
        "name": "Holistic Validation Gate",
        "description": "Run full validation (lint + tests) before IMPLEMENT/FIX/REFACTOR.",
    },
    "CORE-049": {
        "name": "Silent Autonomous Execution",
        "description": "Operate silently with progress bars only; no confirmation prompts.",
    },
    "CORE-064": {
        "name": "Sweep Completeness Contract",
        "description": "Every FIX/REFACTOR/AUDIT must exhaust its full issue catalogue.",
    },
}


def get_display_name(principle_id: str) -> str:
    """Get human-readable display name for a governance principle.

    Args:
        principle_id: The CORE rule identifier (e.g. CORE-008).

    Returns:
        Display name string, or the principle_id if not found.
    """
    entry = _PRINCIPLES.get(principle_id)
    return entry["name"] if entry else principle_id


def get_description(principle_id: str) -> Optional[str]:
    """Get the full description for a governance principle.

    Args:
        principle_id: The CORE rule identifier.

    Returns:
        Description string, or None if not found.
    """
    entry = _PRINCIPLES.get(principle_id)
    return entry["description"] if entry else None


def list_all_principles() -> List[Dict[str, str]]:
    """List all known governance principles with their IDs, names, and descriptions.

    Returns:
        List of dicts with 'id', 'name', and 'description' keys.
    """
    return [
        {"id": pid, "name": data["name"], "description": data["description"]}
        for pid, data in _PRINCIPLES.items()
    ]
