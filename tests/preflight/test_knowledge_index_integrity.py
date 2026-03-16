"""Preflight: knowledge index integrity guardrail.

Validates that all `path` entries in `cortex-registry/knowledge/INDEX.yaml`
resolve to existing files so knowledge retrieval remains deterministic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List

import pytest
import yaml

CORTEX_ROOT = Path(__file__).parents[2]
KNOWLEDGE_INDEX = CORTEX_ROOT / "cortex-registry" / "knowledge" / "INDEX.yaml"


def _collect_paths(obj: Any) -> List[str]:
    """Collect all `path` values from nested YAML structures."""
    paths: List[str] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "path" and isinstance(value, str):
                paths.append(value)
            else:
                paths.extend(_collect_paths(value))
    elif isinstance(obj, list):
        for item in obj:
            paths.extend(_collect_paths(item))

    return paths


def _resolve_knowledge_path(path_value: str) -> Path:
    """Resolve a knowledge INDEX path to an absolute file path.

    Resolution rules:
    - `../knowledge-base/...` → `cortex-registry/knowledge-base/...`
    - `docs/...` → repository-root `docs/...`
    - everything else → `cortex-registry/knowledge/...`
    """
    if path_value.startswith("../knowledge-base/"):
        suffix = path_value[len("../knowledge-base/") :]
        return CORTEX_ROOT / "cortex-registry" / "knowledge-base" / suffix

    if path_value.startswith("docs/"):
        return CORTEX_ROOT / path_value

    return CORTEX_ROOT / "cortex-registry" / "knowledge" / path_value


class TestKnowledgeIndexIntegrity:
    """Knowledge INDEX must only reference files that exist."""

    def test_knowledge_index_exists(self) -> None:
        """INDEX file must be present."""
        assert KNOWLEDGE_INDEX.exists(), (
            "Missing knowledge INDEX: cortex-registry/knowledge/INDEX.yaml"
        )

    def test_all_index_paths_resolve_to_existing_files(self) -> None:
        """Every `path` in INDEX must resolve to an existing file."""
        if not KNOWLEDGE_INDEX.exists():
            pytest.skip("Knowledge INDEX not found")

        data = yaml.safe_load(KNOWLEDGE_INDEX.read_text(encoding="utf-8")) or {}
        path_entries = _collect_paths(data)

        missing: List[str] = []
        for entry in path_entries:
            resolved = _resolve_knowledge_path(entry)
            if not resolved.exists():
                missing.append(f"{entry} -> {resolved.relative_to(CORTEX_ROOT)}")

        assert not missing, (
            "Knowledge INDEX contains missing path references:\n"
            + "\n".join(f"  - {item}" for item in missing)
        )

    def test_index_paths_are_unique(self) -> None:
        """Duplicate path entries in INDEX are disallowed to prevent drift."""
        if not KNOWLEDGE_INDEX.exists():
            pytest.skip("Knowledge INDEX not found")

        data = yaml.safe_load(KNOWLEDGE_INDEX.read_text(encoding="utf-8")) or {}
        path_entries = _collect_paths(data)

        duplicates = sorted({p for p in path_entries if path_entries.count(p) > 1})
        assert not duplicates, (
            "Knowledge INDEX contains duplicate path entries:\n"
            + "\n".join(f"  - {item}" for item in duplicates)
        )
