"""Preflight: critical duplicate class blocker.

Blocks known high-risk duplicate class names that can cause ambiguous imports,
drift in governance checks, and non-deterministic type resolution.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List

CORTEX_ROOT = Path(__file__).parents[2]
SOURCE_ROOT = CORTEX_ROOT / "cortex"

CRITICAL_CLASS_NAMES = {
    "GateVerdict",
    "PatternRegistry",
}


def _collect_class_locations() -> Dict[str, List[str]]:
    """Collect class-definition locations for critical class names."""
    class_locations: Dict[str, List[str]] = {name: [] for name in CRITICAL_CLASS_NAMES}

    for py_file in SOURCE_ROOT.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue

        rel = str(py_file.relative_to(CORTEX_ROOT))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in class_locations:
                class_locations[node.name].append(f"{rel}:{node.lineno}")

    return class_locations


class TestCriticalDuplicateClassBlockers:
    """Prevent recurrence of known critical duplicate class names."""

    def test_critical_class_names_are_unique(self) -> None:
        """Each critical class name must have exactly one canonical definition."""
        locations = _collect_class_locations()

        violations: List[str] = []
        for class_name, refs in locations.items():
            if len(refs) > 1:
                details = "\n    ".join(refs)
                violations.append(
                    f"{class_name} has {len(refs)} definitions:\n    {details}"
                )

        assert not violations, (
            "Critical duplicate class definitions detected (production blocker):\n"
            + "\n\n".join(violations)
            + "\n\nFix: keep one canonical class definition per critical type name."
        )
