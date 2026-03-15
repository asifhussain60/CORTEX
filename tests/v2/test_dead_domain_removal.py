import importlib
from pathlib import Path

import pytest


DEAD_MODULES = [
    "cortex.orchestrators.persona",
    "cortex.orchestrators.strategies",
    "cortex.orchestrators.synthesis",
    "cortex.orchestrators.tools",
    "cortex.orchestrators.response",
]
_ROOT = "cortex.orchestrators"
_DEAD_SEGMENTS = ["persona", "strategies", "synthesis", "tools", "response"]
DEAD_IMPORT_PATTERNS = []
for _segment in _DEAD_SEGMENTS:
    _target = f"{_ROOT}.{_segment}"
    DEAD_IMPORT_PATTERNS.append(f"from {_target}")
    DEAD_IMPORT_PATTERNS.append(f"import {_target}")


@pytest.mark.parametrize("module_name", DEAD_MODULES)
def test_dead_domain_modules_not_importable(module_name: str):
    with pytest.raises((ModuleNotFoundError, ImportError)):
        importlib.import_module(module_name)


def test_no_dead_domain_import_references_in_cortex_or_tests():
    project_root = Path(__file__).resolve().parents[2]
    search_roots = [project_root / "cortex", project_root / "tests"]
    offenders = []

    for root in search_roots:
        for file_path in root.rglob("*.py"):
            if file_path.name == "test_dead_domain_removal.py":
                continue
            text = file_path.read_text(encoding="utf-8")
            for pattern in DEAD_IMPORT_PATTERNS:
                if pattern in text:
                    offenders.append(f"{file_path.relative_to(project_root)}::{pattern}")

    assert offenders == [], "Found dead domain import references:\n" + "\n".join(offenders)
