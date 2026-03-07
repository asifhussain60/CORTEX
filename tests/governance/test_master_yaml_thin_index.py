"""
Phase 112 — THIN INDEX CONTRACT governance tests.
CORE-064: These tests enforce the cortex-master.yaml line count limit and
prohibited key constraints. They must FAIL at RED (543L) and PASS after
Phase 112-a GREEN trims the file to ≤850 lines.
"""
from __future__ import annotations

import pathlib
import re

import pytest
import yaml

MASTER_YAML = pathlib.Path("cortex-registry/cortex-master.yaml")

# Maximum allowed line count per cortex-architect.prompt.md Check #25
MAX_LINES = 850

# Keys that must never appear inline in cortex-master.yaml (THIN INDEX CONTRACT)
PROHIBITED_KEYS = [
    "gap_catalogue",
    "tdd_sequence",
    "new_files",
    "files_to_edit",
    "implementation",
    "code_snippets",
]


def test_master_yaml_is_valid_yaml() -> None:
    """cortex-master.yaml must be syntactically valid YAML at all times."""
    assert MASTER_YAML.exists(), f"cortex-master.yaml not found at {MASTER_YAML}"
    try:
        yaml.safe_load(MASTER_YAML.read_text())
    except yaml.YAMLError as exc:
        pytest.fail(f"cortex-master.yaml is not valid YAML: {exc}")


def test_master_yaml_line_count() -> None:
    """cortex-master.yaml must be ≤850 lines (THIN INDEX CONTRACT, Check #25)."""
    assert MASTER_YAML.exists(), f"cortex-master.yaml not found at {MASTER_YAML}"
    lines = MASTER_YAML.read_text().splitlines()
    count = len(lines)
    assert count <= MAX_LINES, (
        f"cortex-master.yaml is {count} lines — {count - MAX_LINES} lines over the "
        f"≤{MAX_LINES} THIN INDEX CONTRACT limit (cortex-architect.prompt.md Check #25). "
        f"Extract inline phase detail to cortex-registry/planning/phases/planned/<phase>.yaml "
        f"and replace with a thin file: pointer entry."
    )


def test_master_yaml_no_prohibited_keys() -> None:
    """cortex-master.yaml must not contain prohibited inline keys (THIN INDEX CONTRACT)."""
    assert MASTER_YAML.exists(), f"cortex-master.yaml not found at {MASTER_YAML}"
    content = MASTER_YAML.read_text()
    violations: list[tuple[str, int]] = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        for key in PROHIBITED_KEYS:
            if re.search(rf"^\s*{re.escape(key)}\s*:", line):
                violations.append((key, lineno))
    assert not violations, (
        f"cortex-master.yaml contains prohibited inline keys (THIN INDEX CONTRACT):\n"
        + "\n".join(f"  Line {ln}: '{key}:'" for key, ln in violations)
        + "\nMove this detail to the dedicated phase YAML file and replace with a thin file: pointer."
    )


def test_master_yaml_file_pointers_resolve() -> None:
    """Every file: pointer in cortex-master.yaml must resolve to an existing file."""
    assert MASTER_YAML.exists(), f"cortex-master.yaml not found at {MASTER_YAML}"
    doc = yaml.safe_load(MASTER_YAML.read_text()) or {}
    root = MASTER_YAML.parent.parent  # workspace root

    missing: list[str] = []
    # Check both phase_detail_files and phases lists
    for section_key in ("phase_detail_files", "phases"):
        entries = doc.get(section_key, []) or []
        for entry in entries:
            if isinstance(entry, dict) and "file" in entry:
                file_path = pathlib.Path(root / entry["file"])
                if not file_path.exists():
                    missing.append(f"  {entry.get('id', '?')} → {entry['file']}")

    assert not missing, (
        f"cortex-master.yaml has {len(missing)} broken file: pointer(s):\n"
        + "\n".join(missing)
        + "\nUpdate or remove these entries."
    )
