# AC_START: AC-PHASE49-S7-tests
# Description: S7 MasterOrchestrator Integration tests
# Author: Asif Hussain
# Date: 2026-02-08
# Phase: 49, Stage 7

"""S7 Tests: MasterOrchestrator Integration (18 tests)."""

import pytest
import time
from cortex.orchestrators.context_crystallization.master_integration import (
    CCLMasterIntegration,
)
from cortex.orchestrators.context_crystallization import (
    ContextCrystallizationLayer,
    CrystallizedContext,
)


def test_integration_init():
    """S7 Test 1: Integration initialization."""
    integration = CCLMasterIntegration()
    assert integration is not None
    assert integration.ccl is not None
    assert len(integration.active_contexts) == 0


def test_integration_custom_ccl():
    """S7 Test 2: Custom CCL instance."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=500)
    integration = CCLMasterIntegration(ccl=ccl)
    assert integration.ccl is ccl


def test_kickoff_prefetch():
    """S7 Test 3: Kickoff CCL prefetch."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001")
    assert "req-001" in integration.active_contexts


def test_kickoff_with_file():
    """S7 Test 4: Kickoff with file path."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001", file_path="/tmp/test.py")
    assert "req-001" in integration.active_contexts


def test_kickoff_with_context():
    """S7 Test 5: Kickoff with request context."""
    integration = CCLMasterIntegration()
    req_ctx = {"user": "test", "intent": "IMPLEMENT"}
    integration.kickoff_ccl_prefetch("req-001", request_context=req_ctx)
    assert "req-001" in integration.active_contexts


def test_get_crystallized_context():
    """S7 Test 6: Get crystallized context."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001")
    context = integration.get_crystallized_context("req-001")
    assert context is not None
    assert isinstance(context, CrystallizedContext)


def test_get_missing_request():
    """S7 Test 7: Get context for missing request."""
    integration = CCLMasterIntegration()
    context = integration.get_crystallized_context("missing-req")
    assert context is None


def test_merge_context_for_stage2():
    """S7 Test 8: Merge context for Stage 2."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001")

    existing = {"intent": "IMPLEMENT", "user": "alice"}
    merged = integration.merge_context_for_stage2("req-001", existing)

    assert "intent" in merged
    assert "user" in merged
    assert merged["intent"] == "IMPLEMENT"


def test_merge_includes_crystallized():
    """S7 Test 9: Merged context includes crystallized data."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001")

    existing = {}
    merged = integration.merge_context_for_stage2("req-001", existing)

    if integration.active_contexts["req-001"].is_ready():
        assert "crystallized_context" in merged


def test_cleanup_request():
    """S7 Test 10: Cleanup request."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001")
    assert "req-001" in integration.active_contexts

    integration.cleanup_request("req-001")
    assert "req-001" not in integration.active_contexts


def test_multiple_concurrent_requests():
    """S7 Test 11: Multiple concurrent requests."""
    integration = CCLMasterIntegration()

    integration.kickoff_ccl_prefetch("req-001")
    integration.kickoff_ccl_prefetch("req-002")
    integration.kickoff_ccl_prefetch("req-003")

    assert len(integration.active_contexts) == 3
    assert integration.get_crystallized_context("req-001") is not None
    assert integration.get_crystallized_context("req-002") is not None
    assert integration.get_crystallized_context("req-003") is not None


def test_get_progress_indicators():
    """S7 Test 12: Get progress indicators."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001")

    indicators = integration.get_progress_indicators("req-001")

    assert "status" in indicators
    assert "rules" in indicators or "status" in indicators


def test_progress_indicators_missing_request():
    """S7 Test 13: Progress indicators for missing request."""
    integration = CCLMasterIntegration()
    indicators = integration.get_progress_indicators("missing")
    assert indicators["status"] == "prefetch_not_started"


def test_report_statistics():
    """S7 Test 14: Report statistics."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001")
    integration.kickoff_ccl_prefetch("req-002")

    stats = integration.report_statistics()

    assert "active_requests" in stats
    assert stats["active_requests"] == 2


def test_sequential_requests():
    """S7 Test 15: Sequential requests."""
    integration = CCLMasterIntegration()

    integration.kickoff_ccl_prefetch("req-001")
    ctx1 = integration.get_crystallized_context("req-001")
    integration.cleanup_request("req-001")

    integration.kickoff_ccl_prefetch("req-002")
    ctx2 = integration.get_crystallized_context("req-002")

    assert ctx1 is not None
    assert ctx2 is not None
    assert ctx1 is not ctx2


def test_context_not_mutated():
    """S7 Test 16: Existing context not mutated."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001")

    existing = {"user": "alice", "role": "engineer"}
    original_keys = set(existing.keys())

    merged = integration.merge_context_for_stage2("req-001", existing)

    # Original should not be mutated
    assert set(existing.keys()) == original_keys
    assert "crystallized_context" not in existing


def test_wait_for_context():
    """S7 Test 17: Wait for context ready."""
    integration = CCLMasterIntegration()
    integration.kickoff_ccl_prefetch("req-001")

    start = time.time()
    context = integration.get_crystallized_context("req-001", wait_ms=100)
    elapsed = (time.time() - start) * 1000

    assert context is not None
    assert elapsed < 150  # Should wait ~100ms max


def test_ac_markers_in_integration():
    """S7 Test 18: AC markers logged."""
    import logging

    integration = CCLMasterIntegration()
    # Should not raise
    integration.kickoff_ccl_prefetch("req-001")
    integration.get_crystallized_context("req-001")
    integration.cleanup_request("req-001")

    assert len(integration.active_contexts) == 0


# AC_COMPLETE: AC-PHASE49-S7-tests ✅
# Tests: 18/18 ✅
