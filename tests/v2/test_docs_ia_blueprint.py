"""Phase M12 tests for docs IA blueprint and migration map."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(path: str) -> dict:
    data = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_m12_docs_ia_blueprint_has_required_sections() -> None:
    """Blueprint defines platform/domain/operations/governance sections."""
    blueprint = _load(
        "cortex-registry/planning/phases/v2/artifacts/phase-m12/docs-ia-blueprint.yaml"
    )
    section_ids = {entry["id"] for entry in blueprint["sections"]}
    assert {"platform", "domains", "operations", "governance"}.issubset(section_ids)


def test_m12_docs_migration_map_is_complete() -> None:
    """Migration map marks stale/missing analysis and complete mapping."""
    mapping = _load(
        "cortex-registry/planning/phases/v2/artifacts/phase-m12/docs-migration-map.yaml"
    )
    assert mapping["coverage"]["stale_areas_identified"] is True
    assert mapping["coverage"]["missing_areas_identified"] is True
    assert mapping["coverage"]["mapping_complete"] is True
