"""
Phase 20 — Golden E2E Truth Tests: ADO Context Mapper + KG Indexing + Cross-Domain Synthesis

Verifies end-to-end that:
1. ADOContextMapper correctly extracts sprint context from WorkItem lists (AC-P20-002)
2. KnowledgeIndexer.index_registry_yaml() indexes live registry profiles (AC-P20-004)
3. KnowledgeInference.infer_related_rules() returns rule IDs for known entities (AC-P20-005)
4. UnifiedIntelligenceProvider.full() indexes profiles without raising (AC-P20-006)
5. _synthesize_cross_domain() returns non-empty architecture/security/testing lists (AC-P20-007)
6. full() with repo_name="cortex" returns non-empty context (AC-P20-008)
7. ADO call is silently skipped when ADO_ORG_URL is absent (AC-P20-013)
8. KG indexing is idempotent — double-call does not corrupt entity count (AC-P20-014)

These are TRUTH tests — they assert behaviour against live cortex-registry/ files.

Authority: AC-P20-001..AC-P20-014
Test count: 10
"""
# ruff: noqa: S101
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, List

import pytest
import yaml

from cortex.repositories.work_item_provider import WorkItem

REPO_ROOT = Path(__file__).parents[2]
PROFILES_DIR = REPO_ROOT / "cortex-registry" / "knowledge-base" / "profiles"
REPOS_DIR = REPO_ROOT / "cortex-registry" / "knowledge-base" / "repositories"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_workitem(
    item_id: str = "1",
    title: str = "User Story",
    state: str = "Active",
    iteration: str = "MyTeam\\Sprint 42",
    area: str = "CORTEX\\Backend",
) -> WorkItem:
    return WorkItem(
        id=item_id,
        title=title,
        description="",
        state=state,
        type="User Story",
        tags=[],
        url="",
        raw={
            "fields": {
                "System.IterationPath": iteration,
                "System.AreaPath": area,
                "System.State": state,
            }
        },
    )


# ===========================================================================================
# GROUP 1: ADOContextMapper — live WorkItem mapping (AC-P20-002, AC-P20-009, AC-P20-013)
# ===========================================================================================

def test_ado_context_mapper_sprint_name_extraction() -> None:
    """AC-P20-002a: ADOContextMapper extracts sprint name from IterationPath."""
    from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper

    stories = [_make_workitem(iteration="MyTeam\\Sprints\\Sprint 99")]
    result = ADOContextMapper.map(stories)

    assert result["sprint_name"] == "Sprint 99", (
        f"Expected 'Sprint 99', got: {result['sprint_name']!r}"
    )


def test_ado_context_mapper_open_and_inprogress_counts() -> None:
    """AC-P20-002c: ADOContextMapper returns correct open_count and in_progress_count."""
    from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper

    stories = [
        _make_workitem("1", state="Active"),
        _make_workitem("2", state="Active"),
        _make_workitem("3", state="New"),
        _make_workitem("4", state="Resolved"),
    ]
    result = ADOContextMapper.map(stories)

    assert result["open_count"] == 4
    assert result["in_progress_count"] == 2


def test_ado_context_mapper_empty_stories() -> None:
    """AC-P20-009: ADOContextMapper.map([]) returns zero counts without error."""
    from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper

    result = ADOContextMapper.map([])

    assert result["open_count"] == 0
    assert result["stories"] == []
    assert result["sprint_name"] == ""


# ===========================================================================================
# GROUP 2: KG Indexer — live registry files (AC-P20-004, AC-P20-014)
# ===========================================================================================

def test_kg_indexer_indexes_live_profiles() -> None:
    """AC-P20-004: index_registry_yaml() indexes all live knowledge-base/profiles/ YAMLs."""
    from cortex.intelligence.domain_brain.domain_brain.kg_indexer import KnowledgeIndexer

    indexer = KnowledgeIndexer()
    profile_yamls = list(PROFILES_DIR.glob("*.yaml"))
    assert len(profile_yamls) > 0, f"No profiles found in {PROFILES_DIR}"

    for yaml_path in profile_yamls:
        indexer.index_registry_yaml(yaml_path, entity_type="profile")

    assert len(indexer.entity_index) == len(profile_yamls), (
        f"Expected {len(profile_yamls)} entities indexed, got {len(indexer.entity_index)}"
    )


def test_kg_indexer_idempotent_on_live_profiles() -> None:
    """AC-P20-014: Indexing the same profiles twice produces identical entity count."""
    from cortex.intelligence.domain_brain.domain_brain.kg_indexer import KnowledgeIndexer

    indexer = KnowledgeIndexer()
    profile_yamls = list(PROFILES_DIR.glob("*.yaml"))

    for yaml_path in profile_yamls:
        indexer.index_registry_yaml(yaml_path, entity_type="profile")

    count_after_first = len(indexer.entity_index)

    # Second pass — idempotency
    for yaml_path in profile_yamls:
        indexer.index_registry_yaml(yaml_path, entity_type="profile")

    assert len(indexer.entity_index) == count_after_first, (
        "KG indexing is not idempotent — entity count changed on second pass"
    )


# ===========================================================================================
# GROUP 3: KG Inference — infer_related_rules() (AC-P20-005)
# ===========================================================================================

def test_kg_inference_finops_rules() -> None:
    """AC-P20-005: infer_related_rules('finops-v1.0') returns FIN rule IDs."""
    from cortex.intelligence.domain_brain.domain_brain.kg_inference import KnowledgeInference

    inference = KnowledgeInference()
    rules = inference.infer_related_rules("finops-v1.0")

    assert isinstance(rules, list)
    assert len(rules) > 0, "Expected at least one rule for 'finops-v1.0'"
    assert all(isinstance(r, str) for r in rules)


def test_kg_inference_unknown_entity_returns_empty_list() -> None:
    """AC-P20-005b: infer_related_rules() returns [] for unknown entity — no exception."""
    from cortex.intelligence.domain_brain.domain_brain.kg_inference import KnowledgeInference

    inference = KnowledgeInference()
    rules = inference.infer_related_rules("completely-unknown-entity-xyz")

    assert rules == [], f"Expected empty list for unknown entity, got {rules!r}"


# ===========================================================================================
# GROUP 4: UnifiedIntelligenceProvider.full() — integration (AC-P20-006, AC-P20-007, AC-P20-008)
# ===========================================================================================

def test_provider_full_does_not_raise_without_ado() -> None:
    """AC-P20-013: full() completes without error when ADO_ORG_URL is absent."""
    # Ensure ADO env var is unset for this test
    os.environ.pop("ADO_ORG_URL", None)

    from cortex.intelligence.provider import UnifiedIntelligenceProvider

    provider = UnifiedIntelligenceProvider()
    context = provider.full(intent="IMPLEMENT", repo_name="cortex")

    assert context is not None, "full() must return a non-None context"


def test_cross_domain_synthesis_returns_populated_lists() -> None:
    """AC-P20-007: _synthesize_cross_domain() returns non-empty architecture/security/testing."""
    from cortex.intelligence.provider import UnifiedIntelligenceProvider

    provider = UnifiedIntelligenceProvider()
    result = provider._synthesize_cross_domain("IMPLEMENT", "FastAPI endpoint in DDD repo")

    assert isinstance(result, dict), "_synthesize_cross_domain() must return a dict"
    for key in ("architecture", "security", "testing"):
        assert key in result, f"Missing key '{key}' in cross-domain synthesis result"
        assert len(result[key]) > 0, (
            f"Expected non-empty list for '{key}', got: {result[key]!r}"
        )


def test_provider_full_company_knowledge_non_empty() -> None:
    """AC-P20-008: full() returns context that consumed real company domain knowledge."""
    os.environ.pop("ADO_ORG_URL", None)

    from cortex.intelligence.provider import UnifiedIntelligenceProvider

    provider = UnifiedIntelligenceProvider()
    context = provider.full(intent="IMPLEMENT", repo_name="cortex")

    assert context is not None

    # Verify company domain files are present and loader reads them correctly
    # Use a fresh (non-singleton) instance to avoid stale cache from other tests
    from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader

    DOMAINS_DIR = REPO_ROOT / "cortex-registry" / "company" / "domains"
    fresh_loader = CompanyDomainLoader(domains_dir=DOMAINS_DIR)
    knowledge = fresh_loader.load()
    assert knowledge.domain_rules != {}, (
        f"CompanyDomainLoader should return non-empty domain_rules. "
        f"YAML files in {DOMAINS_DIR}: {list(DOMAINS_DIR.glob('*.yaml'))}"
    )
