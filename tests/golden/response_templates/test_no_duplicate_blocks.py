"""
GAP-128-C-01: Response template blocks must not define the same block ID twice.

The _registry.yaml in cortex-registry/templates/response/ is the SSOT for all
blocks, atoms, and compositions. Each entry must have a unique `id` field across
all tiers (atoms, blocks, compositions, prompts).

Drift lock: check-44-response-template-compliance-lock.yaml
"""

import re
from pathlib import Path
from typing import List, Tuple
import yaml
import pytest

REGISTRY_FILE = Path("cortex-registry/templates/response/_registry.yaml")
TEMPLATES_DIR = Path("cortex-registry/templates/response")
REPO_ROOT = Path(__file__).parents[3]


def _load_registry() -> dict:
    """Load the master block registry YAML."""
    registry_path = REPO_ROOT / REGISTRY_FILE
    if not registry_path.exists():
        return {}
    with open(registry_path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _collect_all_ids(registry: dict) -> List[Tuple[str, str]]:
    """Collect (tier, id) pairs from all tiers in the registry."""
    pairs: List[Tuple[str, str]] = []
    for tier in ("atoms", "blocks", "compositions", "prompts"):
        entries = registry.get(tier, []) or []
        for entry in entries:
            if isinstance(entry, dict) and "id" in entry:
                pairs.append((tier, entry["id"]))
    return pairs


def _collect_yaml_ids_from_files() -> List[Tuple[str, str]]:
    """Collect (relative_path, id) from all YAML files in the templates tree."""
    results: List[Tuple[str, str]] = []
    templates_dir = REPO_ROOT / TEMPLATES_DIR
    if not templates_dir.exists():
        return results
    for yaml_file in templates_dir.rglob("*.yaml"):
        rel = yaml_file.relative_to(REPO_ROOT / TEMPLATES_DIR)
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if isinstance(data, dict) and "id" in data:
            results.append((str(rel), data["id"]))
    return results


class TestNoDuplicateBlocks:
    """GAP-128-C-01: No duplicate block IDs in response template registry."""

    def test_registry_file_exists(self):
        """_registry.yaml must exist at the expected location."""
        assert (REPO_ROOT / REGISTRY_FILE).exists(), (
            f"Response template registry not found: {REGISTRY_FILE}"
        )

    def test_no_duplicate_ids_within_registry(self):
        """Each block/atom/composition id must appear exactly once in _registry.yaml."""
        registry = _load_registry()
        pairs = _collect_all_ids(registry)
        ids = [p[1] for p in pairs]
        seen: dict = {}
        duplicates: List[str] = []
        for tier, block_id in pairs:
            if block_id in seen:
                duplicates.append(f"'{block_id}' in tier='{tier}' (first in '{seen[block_id]}')")
            else:
                seen[block_id] = tier
        assert duplicates == [], (
            f"Duplicate block IDs found in _registry.yaml:\n"
            + "\n".join(f"  {d}" for d in duplicates)
        )

    def test_no_duplicate_ids_across_yaml_files(self):
        """No two YAML files in templates/response/ may declare the same top-level id."""
        pairs = _collect_yaml_ids_from_files()
        seen: dict = {}
        duplicates: List[str] = []
        for rel_path, file_id in pairs:
            if file_id in seen:
                duplicates.append(f"'{file_id}' in '{rel_path}' (first seen in '{seen[file_id]}')")
            else:
                seen[file_id] = rel_path
        assert duplicates == [], (
            f"Duplicate `id:` values across response template YAML files:\n"
            + "\n".join(f"  {d}" for d in duplicates)
        )

    def test_registry_ids_match_file_ids(self):
        """Every id registered in _registry.yaml must match the id in its referenced file."""
        registry = _load_registry()
        templates_dir = REPO_ROOT / TEMPLATES_DIR
        mismatches: List[str] = []
        for tier in ("atoms", "blocks", "compositions", "prompts"):
            entries = registry.get(tier, []) or []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                reg_id = entry.get("id")
                file_ref = entry.get("file")
                if not reg_id or not file_ref:
                    continue
                file_path = templates_dir / file_ref
                if not file_path.exists():
                    continue  # missing file tested elsewhere
                try:
                    data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
                except yaml.YAMLError:
                    continue
                file_id = data.get("id") if isinstance(data, dict) else None
                if file_id and file_id != reg_id:
                    mismatches.append(
                        f"Registry id='{reg_id}' but file declares id='{file_id}' ({file_ref})"
                    )
        assert mismatches == [], (
            f"Registry/file id mismatches:\n" + "\n".join(f"  {m}" for m in mismatches)
        )

    def test_all_registry_files_exist(self):
        """Every file: reference in _registry.yaml must resolve to a real file."""
        registry = _load_registry()
        templates_dir = REPO_ROOT / TEMPLATES_DIR
        missing: List[str] = []
        for tier in ("atoms", "blocks", "compositions", "prompts"):
            entries = registry.get(tier, []) or []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                file_ref = entry.get("file")
                block_id = entry.get("id", "?")
                if not file_ref:
                    continue
                file_path = templates_dir / file_ref
                if not file_path.exists():
                    missing.append(f"id='{block_id}' → file='{file_ref}' NOT FOUND")
        assert missing == [], (
            f"Missing files referenced in _registry.yaml:\n"
            + "\n".join(f"  {m}" for m in missing)
        )
