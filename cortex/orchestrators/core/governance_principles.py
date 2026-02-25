"""governance_principles.py — Governance Principles stub."""
from __future__ import annotations


def get_display_name(principle_id: str) -> str:
    """Get human-readable display name for a governance principle.

    Args:
        principle_id: The CORE rule identifier (e.g. CORE-008).

    Returns:
        Display name string.
    """
    names = {
        "CORE-002": "Inline Output Only",
        "CORE-008": "TDD Mandatory",
        "CORE-011": "Type Hints Required",
        "CORE-012": "Docstrings Required",
        "CORE-028": "Snake Case Naming",
        "CORE-035": "Single Canonical Implementation",
        "CORE-048": "Holistic Validation Gate",
        "CORE-049": "Silent Autonomous Execution",
        "CORE-064": "Sweep Completeness Contract",
    }
    return names.get(principle_id, principle_id)
