"""
Phase 20 Sub-Phase B — TDD RED Tests: KGIndexer.index_registry_yaml()

Authority: AC-P20-004, AC-P20-005, AC-P20-006, AC-P20-014
Rule: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_yaml(tmp: Path, filename: str, data: dict) -> Path:
    """Write a YAML file to a temp directory."""
    path = tmp / filename
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# AC-P20-004 — KGIndexer has index_registry_yaml()
# ---------------------------------------------------------------------------

def test_kg_indexer_has_index_registry_yaml() -> None:
    """AC-P20-004: KGIndexer (KnowledgeIndexer) has index_registry_yaml() method."""
    from cortex.intelligence.domain_brain.domain_brain.kg_indexer import KnowledgeIndexer

    indexer = KnowledgeIndexer()
    assert hasattr(indexer, "index_registry_yaml"), (
        "KnowledgeIndexer must expose index_registry_yaml(yaml_path, entity_type)"
    )


def test_kg_indexer_indexes_entities_from_yaml() -> None:
    """AC-P20-004b: index_registry_yaml() reads YAML and indexes entities."""
    from cortex.intelligence.domain_brain.domain_brain.kg_indexer import KnowledgeIndexer

    indexer = KnowledgeIndexer()
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        yaml_path = _write_yaml(tmp, "finops.yaml", {
            "profile": {
                "id": "finops-v1.0",
                "name": "FinOps Domain Profile",
                "tags": ["billing", "cost-management"],
            }
        })

        indexer.index_registry_yaml(yaml_path, entity_type="profile")

        # Entity should be retrievable by id
        entity = indexer.get_entity("finops-v1.0")
        assert entity is not None, "Entity 'finops-v1.0' should be indexed after index_registry_yaml()"
        assert entity.get("type") == "profile"


def test_kg_indexer_handles_missing_file_gracefully() -> None:
    """AC-P20-004c: index_registry_yaml() does not raise when file is missing."""
    from cortex.intelligence.domain_brain.domain_brain.kg_indexer import KnowledgeIndexer

    indexer = KnowledgeIndexer()
    missing = Path("/tmp/nonexistent_registry_yaml_12345.yaml")
    # Must not raise — graceful degradation
    indexer.index_registry_yaml(missing, entity_type="repo")


# ---------------------------------------------------------------------------
# AC-P20-014 — idempotency: indexing twice does not duplicate entities
# ---------------------------------------------------------------------------

def test_kg_indexer_idempotent() -> None:
    """AC-P20-014: index_registry_yaml() is idempotent — double call does not duplicate entities."""
    from cortex.intelligence.domain_brain.domain_brain.kg_indexer import KnowledgeIndexer

    indexer = KnowledgeIndexer()
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        yaml_path = _write_yaml(tmp, "auth.yaml", {
            "profile": {"id": "auth-v1.0", "name": "Auth Profile", "tags": ["auth", "oauth2"]}
        })

        indexer.index_registry_yaml(yaml_path, entity_type="profile")
        indexer.index_registry_yaml(yaml_path, entity_type="profile")

        # Count entities — must be exactly 1, not 2
        count = len(indexer.entity_index)
        assert count == 1, f"Idempotency violation: expected 1 entity, got {count}"


# ---------------------------------------------------------------------------
# AC-P20-005 — KGInference.infer_related_rules() (future hook; guards contract)
# ---------------------------------------------------------------------------

def test_kg_inference_has_infer_related_rules() -> None:
    """AC-P20-005: KnowledgeInference exposes infer_related_rules() method."""
    from cortex.intelligence.domain_brain.domain_brain.kg_inference import KnowledgeInference

    inference = KnowledgeInference()
    assert hasattr(inference, "infer_related_rules"), (
        "KnowledgeInference must have infer_related_rules(entity_id) for Phase-20 KG contract"
    )


def test_kg_inference_infer_related_rules_returns_list() -> None:
    """AC-P20-005b: infer_related_rules() returns a list (possibly empty) for any entity_id."""
    from cortex.intelligence.domain_brain.domain_brain.kg_inference import KnowledgeInference

    inference = KnowledgeInference()
    result = inference.infer_related_rules("finops-v1.0")
    assert isinstance(result, list), (
        f"infer_related_rules() must return list, got {type(result)}"
    )
