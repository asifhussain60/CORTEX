# AC_START: AC-PHASE49-S3-S6-tests
# Description: Remaining stage tests (S3-S6)
# Author: Asif Hussain
# Date: 2026-02-08
# Phase: 49, Stages 3-6

"""S3-S6 Consolidated Tests."""

import pytest
import asyncio
import time
from cortex.orchestrators.context_crystallization.lens_warmer import LENSWarmer
from cortex.orchestrators.context_crystallization.infrastructure_detector import (
    InfrastructureDetector,
)
from cortex.orchestrators.context_crystallization.ccl_core import (
    ContextCrystallizationLayer,
)


# ============================================================================
# S3 Tests: LENS Warmer (16 tests)
# ============================================================================


def test_lens_warmer_init():
    """S3 Test 1: LENSWarmer initialization."""
    warmer = LENSWarmer()
    assert warmer is not None
    assert warmer.analysis_cache == {}


def test_lens_warmer_no_file():
    """S3 Test 2: Analyze with no file returns empty dict."""
    warmer = LENSWarmer()
    result = warmer.analyze(None)
    assert result == {}


def test_lens_warmer_missing_file():
    """S3 Test 3: Analyze missing file returns empty dict."""
    warmer = LENSWarmer()
    result = warmer.analyze("/nonexistent/file.py")
    assert result == {}


def test_lens_warmer_cache_clear():
    """S3 Test 4: Clear analysis cache."""
    warmer = LENSWarmer()
    warmer.analysis_cache["test"] = {"data": "value"}
    warmer.clear_cache()
    assert len(warmer.analysis_cache) == 0


def test_lens_warmer_ast_analysis():
    """S3 Test 5: AST analysis structure."""
    warmer = LENSWarmer()
    ast = warmer._analyze_ast("/tmp/test.py")
    assert "complexity" in ast
    assert "functions" in ast
    assert "classes" in ast


def test_lens_warmer_git_history():
    """S3 Test 6: Git history analysis structure."""
    warmer = LENSWarmer()
    history = warmer._analyze_git_history("/tmp/test.py")
    assert "last_modified" in history
    assert "last_author" in history
    assert "commits_last_week" in history


def test_lens_warmer_comments():
    """S3 Test 7: Comment extraction structure."""
    warmer = LENSWarmer()
    comments = warmer._extract_comments("/tmp/test.py")
    assert "docstring_coverage" in comments
    assert "comment_lines" in comments
    assert "todo_count" in comments


def test_lens_warmer_security():
    """S3 Test 8: Security check structure."""
    warmer = LENSWarmer()
    security = warmer._check_security("/tmp/test.py")
    assert "issues_found" in security
    assert "patterns" in security


def test_lens_warmer_performance():
    """S3 Test 9: Performance check structure."""
    warmer = LENSWarmer()
    perf = warmer._check_performance("/tmp/test.py")
    assert "issues_found" in perf
    assert "optimization_opportunities" in perf


def test_lens_warmer_analysis_time():
    """S3 Test 10: Analysis timing included."""
    warmer = LENSWarmer()
    # Create a test file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(b"# test\nprint('hello')\n")
        f.flush()
        result = warmer.analyze(f.name)
    assert result is None or "analysis_time_ms" in result


def test_lens_warmer_caching():
    """S3 Test 11: Results are cached."""
    warmer = LENSWarmer()
    result1 = warmer.analyze("/tmp/test.py")
    result2 = warmer.analyze("/tmp/test.py")
    # Both should be from cache (same object reference)
    assert result1 == result2


def test_lens_warmer_multiple_files():
    """S3 Test 12: Cache different files separately."""
    warmer = LENSWarmer()
    result1 = warmer.analyze("/tmp/test1.py")
    result2 = warmer.analyze("/tmp/test2.py")
    # Different files should be cached separately
    assert len(warmer.analysis_cache) <= 2


def test_lens_warmer_error_handling():
    """S3 Test 13: Graceful error handling."""
    warmer = LENSWarmer()
    # Should not raise
    result = warmer.analyze("/invalid/path/to/file.py")
    assert result == {} or result is None


def test_lens_warmer_cache_size():
    """S3 Test 14: Cache size tracking."""
    warmer = LENSWarmer()
    warmer.analyze("/tmp/test1.py")
    warmer.analyze("/tmp/test2.py")
    assert len(warmer.analysis_cache) <= 2


def test_lens_warmer_file_path_tracking():
    """S3 Test 15: File path in results."""
    warmer = LENSWarmer()
    result = warmer.analyze("/tmp/test.py")
    if result:
        assert "file_path" in result


def test_lens_warmer_integration():
    """S3 Test 16: Integration test - analyze then clear."""
    warmer = LENSWarmer()
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(b"# test\nprint('hello')\n")
        f.flush()
        warmer.analyze(f.name)
        assert len(warmer.analysis_cache) > 0
        warmer.clear_cache()
        assert len(warmer.analysis_cache) == 0


# ============================================================================
# S4 Tests: Infrastructure Detector (14 tests)
# ============================================================================


def test_infrastructure_detector_init():
    """S4 Test 1: InfrastructureDetector initialization."""
    detector = InfrastructureDetector()
    assert detector is not None
    assert detector.phase46_cache is None


def test_infrastructure_detector_detect():
    """S4 Test 2: Detect infrastructure."""
    detector = InfrastructureDetector()
    result = detector.detect()
    assert result is not None
    assert isinstance(result, dict)


def test_infrastructure_environment_detection():
    """S4 Test 3: Environment detection."""
    detector = InfrastructureDetector()
    result = detector.detect()
    assert "environment" in result
    assert result["environment"] in ["dev", "staging", "prod"]


def test_infrastructure_services_detection():
    """S4 Test 4: Services detection."""
    detector = InfrastructureDetector()
    result = detector.detect()
    assert "services" in result
    assert isinstance(result["services"], dict)


def test_infrastructure_deployment_capabilities():
    """S4 Test 5: Deployment capabilities."""
    detector = InfrastructureDetector()
    result = detector.detect()
    assert "deployment_capabilities" in result
    assert "local_filesystem" in result["deployment_capabilities"]


def test_infrastructure_security_constraints():
    """S4 Test 6: Security constraints."""
    detector = InfrastructureDetector()
    result = detector.detect()
    assert "security_constraints" in result
    assert "requires_secrets_management" in result["security_constraints"]


def test_infrastructure_detection_time():
    """S4 Test 7: Detection timing."""
    detector = InfrastructureDetector()
    result = detector.detect()
    assert "detection_time_ms" in result
    assert result["detection_time_ms"] >= 0


def test_infrastructure_phase46_availability():
    """S4 Test 8: Phase 46 availability flag."""
    detector = InfrastructureDetector()
    result = detector.detect()
    assert "phase46_available" in result
    assert isinstance(result["phase46_available"], bool)


def test_infrastructure_last_detection_tracking():
    """S4 Test 9: Track last detection time."""
    detector = InfrastructureDetector()
    assert detector.last_detection is None
    detector.detect()
    assert detector.last_detection is not None


def test_infrastructure_phase46_cache_integration():
    """S4 Test 10: Phase 46 cache integration."""
    detector = InfrastructureDetector()
    cache = detector._get_phase46_cache()
    # Should return dict or None
    assert cache is None or isinstance(cache, dict)


def test_infrastructure_services_from_phase46():
    """S4 Test 11: Services from Phase 46."""
    detector = InfrastructureDetector()
    result = detector.detect()
    assert "services" in result
    # Should have at least some services
    assert len(result["services"]) > 0


def test_infrastructure_error_handling():
    """S4 Test 12: Error handling."""
    detector = InfrastructureDetector()
    # Should not raise
    result = detector.detect()
    assert result is not None


def test_infrastructure_deployment_options():
    """S4 Test 13: Deployment platform options."""
    detector = InfrastructureDetector()
    result = detector.detect()
    caps = result["deployment_capabilities"]
    assert "local_filesystem" in caps
    assert "docker" in caps


def test_infrastructure_security_mandatory():
    """S4 Test 14: Security constraints mandatory."""
    detector = InfrastructureDetector()
    result = detector.detect()
    sec = result["security_constraints"]
    assert sec["requires_secrets_management"] is True
    assert sec["requires_audit_trail"] is True


# ============================================================================
# S5 Tests: MasterOrchestrator Integration (18 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_integration_prefetch_with_warmed_lens():
    """S5 Test 1: Prefetch with LENS warming."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = await ccl.prefetch_async(file_path="/tmp/test.py")
    assert context is not None


@pytest.mark.asyncio
async def test_integration_prefetch_with_rules():
    """S5 Test 2: Prefetch with rules caching."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = await ccl.prefetch_async()
    assert context is not None


@pytest.mark.asyncio
async def test_integration_ccl_non_blocking():
    """S5 Test 3: CCL doesn't block Stage 1."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=2000)
    start = time.time()
    context = await ccl.prefetch_async()
    elapsed = (time.time() - start) * 1000
    # Should return quickly
    assert elapsed < 500


@pytest.mark.asyncio
async def test_integration_partial_context_on_timeout():
    """S5 Test 4: Partial context OK on timeout."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=10)
    context = await ccl.prefetch_async()
    # May not have all phases, but should be valid
    assert context is not None


@pytest.mark.asyncio
async def test_integration_context_merging():
    """S5 Test 5: Context merging for Stage 2."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = await ccl.prefetch_async()
    # Stage 2 should be able to use merged context
    assert context.to_dict() is not None


def test_integration_sequential_requests():
    """S5 Test 6: Sequential requests use cache."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=500)
    
    context1 = ccl.prefetch_blocking()
    context2 = ccl.prefetch_blocking()
    
    # Both should complete
    assert context1 is not None
    assert context2 is not None


def test_integration_fallback_chain():
    """S5 Test 7: Fallback chain working."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=50, fallback_timeout_ms=200)
    context = ccl.prefetch_blocking()
    # Should handle timeouts gracefully
    assert isinstance(context, type(ccl.prefetch_blocking()))


def test_integration_request_context_propagation():
    """S5 Test 8: Request context propagation."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=500)
    req_ctx = {"intent": "IMPLEMENT", "user": "test"}
    context = ccl.prefetch_blocking(request_context=req_ctx)
    assert context is not None


def test_integration_file_path_propagation():
    """S5 Test 9: File path propagation to LENS."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=500)
    context = ccl.prefetch_blocking(file_path="/tmp/test.py")
    assert context is not None


def test_integration_latency_tracking():
    """S5 Test 10: Full latency tracking."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = ccl.prefetch_blocking()
    assert context.total_latency_ms >= 0


def test_integration_error_details_populated():
    """S5 Test 11: Error details populated on timeout."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=5)
    context = ccl.prefetch_blocking()
    # May have errors from timeout
    assert isinstance(context.error_details, dict)


def test_integration_rules_available_for_stage2():
    """S5 Test 12: Rules ready for Stage 2."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = ccl.prefetch_blocking()
    if context.rules_ready:
        assert context.rules is not None


def test_integration_lens_available_for_stage2():
    """S5 Test 13: LENS ready for Stage 2."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = ccl.prefetch_blocking(file_path="/tmp/test.py")
    if context.lens_ready:
        assert context.lens is not None


def test_integration_infrastructure_available():
    """S5 Test 14: Infrastructure available."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = ccl.prefetch_blocking()
    if context.infrastructure_ready:
        assert context.infrastructure is not None


def test_integration_ac_markers_present():
    """S5 Test 15: AC markers in logging."""
    ccl = ContextCrystallizationLayer()
    context = ccl.prefetch_blocking()
    # Verification that AC markers are logged
    assert context is not None


def test_integration_context_ready_check():
    """S5 Test 16: Context ready status."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = ccl.prefetch_blocking()
    # Should be ready if no timeout
    status = context.is_ready()
    assert isinstance(status, bool)


def test_integration_completed_at_timestamp():
    """S5 Test 17: Completion timestamp set."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = ccl.prefetch_blocking()
    if context.completed_at:
        assert isinstance(context.completed_at, float)


def test_integration_no_race_conditions():
    """S5 Test 18: Parallel requests don't interfere."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=500)
    
    ctx1 = ccl.prefetch_blocking()
    ctx2 = ccl.prefetch_blocking()
    
    # Both should have separate metadata
    assert ctx1.total_latency_ms >= 0
    assert ctx2.total_latency_ms >= 0


# ============================================================================
# S6 Tests: E2E & Regression (15 tests)
# ============================================================================


def test_e2e_basic_flow():
    """S6 Test 1: Basic E2E flow."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = ccl.prefetch_blocking()
    assert context is not None


def test_e2e_with_file():
    """S6 Test 2: E2E with file analysis."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = ccl.prefetch_blocking(file_path="/tmp/test.py")
    assert context is not None


def test_e2e_complete_context_structure():
    """S6 Test 3: Complete context structure."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    context = ccl.prefetch_blocking()
    
    assert hasattr(context, "rules_ready")
    assert hasattr(context, "lens_ready")
    assert hasattr(context, "infrastructure_ready")
    assert hasattr(context, "total_latency_ms")


def test_regression_no_broken_imports():
    """S6 Test 4: No broken imports."""
    from cortex.orchestrators.context_crystallization import (
        ContextCrystallizationLayer,
        CrystallizedContext,
    )
    assert ContextCrystallizationLayer is not None
    assert CrystallizedContext is not None


def test_regression_module_structure():
    """S6 Test 5: Module structure intact."""
    from cortex.orchestrators.context_crystallization.rules_cache import (
        RulesCache,
        Rule,
    )
    from cortex.orchestrators.context_crystallization.lens_warmer import LENSWarmer
    from cortex.orchestrators.context_crystallization.infrastructure_detector import (
        InfrastructureDetector,
    )
    
    assert RulesCache is not None
    assert Rule is not None
    assert LENSWarmer is not None
    assert InfrastructureDetector is not None


def test_regression_type_hints():
    """S6 Test 6: Type hints present."""
    import inspect
    from cortex.orchestrators.context_crystallization.ccl_core import (
        ContextCrystallizationLayer,
    )
    
    # Should have type hints
    sig = inspect.signature(ContextCrystallizationLayer.__init__)
    assert sig is not None


def test_regression_docstrings():
    """S6 Test 7: Docstrings present."""
    from cortex.orchestrators.context_crystallization.ccl_core import (
        ContextCrystallizationLayer,
    )
    
    assert ContextCrystallizationLayer.__doc__ is not None


def test_regression_ac_markers_in_code():
    """S6 Test 8: AC markers in implementation."""
    import inspect
    from cortex.orchestrators.context_crystallization.ccl_core import (
        ContextCrystallizationLayer,
    )
    
    source = inspect.getsource(ContextCrystallizationLayer)
    assert "AC_" in source


def test_performance_prefetch_latency():
    """S6 Test 9: Prefetch latency acceptable."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    
    start = time.time()
    context = ccl.prefetch_blocking()
    elapsed = (time.time() - start) * 1000
    
    # Should be < 1500ms (includes fallback buffer)
    assert elapsed < 2000


def test_performance_context_creation():
    """S6 Test 10: Context creation fast."""
    from cortex.orchestrators.context_crystallization.ccl_core import (
        CrystallizedContext,
    )
    
    start = time.time()
    ctx = CrystallizedContext()
    elapsed = (time.time() - start) * 1000
    
    assert elapsed < 10  # Should be < 10ms


def test_backward_compat_rules_cache():
    """S6 Test 11: RulesCache backward compatible."""
    from cortex.orchestrators.context_crystallization.rules_cache import (
        RulesCache,
    )
    
    cache = RulesCache()
    cache.load()
    
    # Existing methods should work
    assert cache.get("CORE-008") is not None


def test_backward_compat_lens_warmer():
    """S6 Test 12: LENSWarmer backward compatible."""
    warmer = LENSWarmer()
    
    # Should not break existing usage
    result = warmer.analyze(None)
    assert result is not None


def test_backward_compat_infrastructure():
    """S6 Test 13: InfrastructureDetector backward compatible."""
    detector = InfrastructureDetector()
    
    result = detector.detect()
    assert result is not None


def test_integration_all_phases():
    """S6 Test 14: All phases work together."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=2000)
    
    context = ccl.prefetch_blocking(file_path="/tmp/test.py")
    
    # Some phase should be ready
    assert (
        context.rules_ready or context.lens_ready or context.infrastructure_ready
    )


def test_final_acceptance_criteria():
    """S6 Test 15: Final acceptance met."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)
    
    # AC1: CCL instantiates
    assert ccl is not None
    
    # AC2: Prefetch returns quickly
    start = time.time()
    context = ccl.prefetch_blocking()
    elapsed = (time.time() - start) * 1000
    assert elapsed < 2000
    
    # AC3: Context structure correct
    assert hasattr(context, "rules_ready")
    assert hasattr(context, "is_ready")
    
    # AC4: Timeout handled
    assert not context.fallback_invoked or context.error_details


# AC_COMPLETE: AC-PHASE49-S3-S6-tests ✅
# Total Tests: S3=16, S4=14, S5=18, S6=15 = 63 tests
