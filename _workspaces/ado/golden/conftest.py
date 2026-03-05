"""
ADO Golden Tests — Shared Fixtures & Configuration.

Authority: CORE-008 (TDD) · CORE-049 (silent exec)
"""

from __future__ import annotations

import os
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

# Ensure ADO env vars are set to safe test values before any imports
# that might trigger provider instantiation.
os.environ.setdefault("ADO_ORG_URL", "https://dev.azure.com/HQY01")
os.environ.setdefault("ADO_PAT", "test-pat-golden-suite")
os.environ.setdefault("ADO_PROJECT", "V5")
os.environ.setdefault("ADO_SKIP_HEALTH_CHECK", "true")


# ──────────────────────────────────────────────────────────────────────────────
# Raw ADO response fixture (reused across all 4 test modules)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def raw_story_692945() -> Dict[str, Any]:
    """Realistic ADO REST API response for story #692945 with $expand=all."""
    from _workspaces.ado.fixtures.ado_fixtures import ADO_STORY_692945_RAW
    return ADO_STORY_692945_RAW


@pytest.fixture(scope="session")
def raw_task_692946() -> Dict[str, Any]:
    """Realistic ADO REST API response for child task #692946."""
    from _workspaces.ado.fixtures.ado_fixtures import ADO_TASK_692946_RAW
    return ADO_TASK_692946_RAW


@pytest.fixture(scope="session")
def raw_wiql_response() -> Dict[str, Any]:
    """Realistic ADO WIQL query response with 3 work item IDs."""
    from _workspaces.ado.fixtures.ado_fixtures import ADO_WIQL_RESPONSE
    return ADO_WIQL_RESPONSE


@pytest.fixture(scope="session")
def raw_batch_response() -> Dict[str, Any]:
    """Realistic ADO workitemsbatch response with 3 stories."""
    from _workspaces.ado.fixtures.ado_fixtures import ADO_BATCH_RESPONSE
    return ADO_BATCH_RESPONSE


@pytest.fixture(scope="session")
def expected_692945() -> Dict[str, Any]:
    """Expected mapped values for story #692945."""
    from _workspaces.ado.fixtures.ado_fixtures import EXPECTED_STORY_692945
    return EXPECTED_STORY_692945


# ──────────────────────────────────────────────────────────────────────────────
# Pre-built provider fixture (no real HTTP calls)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def ado_provider():
    """ADOWorkItemProvider with test credentials (no HTTP calls by default)."""
    from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
    return ADOWorkItemProvider(
        org_url="https://dev.azure.com/HQY01",
        pat="test-pat-golden-suite",
        project="V5",
    )


@pytest.fixture
def ado_provider_with_mock_http(raw_story_692945):
    """ADOWorkItemProvider with _get_work_item_expand_all mocked to return fixture 692945."""
    from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
    provider = ADOWorkItemProvider(
        org_url="https://dev.azure.com/HQY01",
        pat="test-pat-golden-suite",
        project="V5",
    )
    provider._get_work_item_expand_all = MagicMock(return_value=raw_story_692945)
    return provider


@pytest.fixture
def user_story_context_692945(ado_provider_with_mock_http):
    """Fully mapped UserStoryContext for story #692945 (no HTTP)."""
    return ado_provider_with_mock_http.fetch_story_context("692945")


# ──────────────────────────────────────────────────────────────────────────────
# Orchestrator fixture
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def ado_orchestrator_fetch_story():
    """ADOOrchestrator in fetch_story mode for story 692945."""
    from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
    return ADOOrchestrator(story_id=692945, mode="fetch_story")


@pytest.fixture
def ado_orchestrator_bulk(raw_batch_response):
    """ADOOrchestrator in fetch_bulk mode with mocked provider."""
    from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator
    from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
    provider = ADOWorkItemProvider(
        org_url="https://dev.azure.com/HQY01",
        pat="test-pat-golden-suite",
        project="V5",
    )
    orch = ADOOrchestrator(mode="fetch_bulk", project="V5")
    orch._provider = provider
    return orch


# ──────────────────────────────────────────────────────────────────────────────
# Enricher fixture
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def ado_enricher(ado_provider_with_mock_http):
    """ADOContextEnricher with mocked provider (no HTTP calls)."""
    from cortex.orchestrators.core.ado_context_enricher import ADOContextEnricher
    enricher = ADOContextEnricher(provider=ado_provider_with_mock_http)
    return enricher


@pytest.fixture
def empty_intel_context():
    """Minimal UnifiedIntelligenceContext for enricher injection tests."""
    from cortex.intelligence.knowledge.unified_intelligence_context import (
        UnifiedIntelligenceContext, LENSIntelligence, CompanyKnowledge,
        CORTEXKnowledge, SynthesisResult,
    )
    import time
    return UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence(
            git_analysis={}, ast_analysis={}, comment_analysis={}
        ),
        company_knowledge=CompanyKnowledge(
            domain_rules={}, compliance_standards=[], precedence="OVERRIDE"
        ),
        cortex_knowledge=CORTEXKnowledge(
            best_practices={}, applicable_patterns=[], anti_patterns=[],
            synthesis_metadata={}
        ),
        synthesis_result=SynthesisResult(
            merged_rules={}, citations=[], violations=[], guidance=[]
        ),
        intent_type="IMPLEMENT",
        file_path="",
        timestamp=time.time(),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Request string fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def request_full_url() -> str:
    from _workspaces.ado.fixtures.ado_fixtures import REQUEST_FULL_URL
    return REQUEST_FULL_URL


@pytest.fixture(scope="session")
def request_hash_id() -> str:
    from _workspaces.ado.fixtures.ado_fixtures import REQUEST_HASH_ID
    return REQUEST_HASH_ID


@pytest.fixture(scope="session")
def request_bare_id_with_hint() -> str:
    from _workspaces.ado.fixtures.ado_fixtures import REQUEST_BARE_ID_WITH_HINT
    return REQUEST_BARE_ID_WITH_HINT


@pytest.fixture(scope="session")
def request_multiple_ids() -> str:
    from _workspaces.ado.fixtures.ado_fixtures import REQUEST_MULTIPLE_IDS
    return REQUEST_MULTIPLE_IDS


@pytest.fixture(scope="session")
def request_no_ado() -> str:
    from _workspaces.ado.fixtures.ado_fixtures import REQUEST_NO_ADO_ID
    return REQUEST_NO_ADO_ID
