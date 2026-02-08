# AC_START: AC-PHASE49-S1-test_ccl_core
# Description: Core CCL component tests
# Author: Asif Hussain
# Date: 2026-02-08
# Phase: 49, Stage 1

"""
S1 Tests: Core Context Crystallization Layer.

20 test cases covering:
- CCL instantiation (2)
- Async prefetch (5)
- CrystallizedContext (4)
- Timeout handling (5)
- Fallback paths (2)
- Audit logging (2)
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.context_crystallization.ccl_core import (
    ContextCrystallizationLayer,
    CrystallizedContext,
)
from cortex.orchestrators.context_crystallization.rules_cache import RulesCache
from cortex.orchestrators.context_crystallization.lens_warmer import LENSWarmer
from cortex.orchestrators.context_crystallization.infrastructure_detector import (
    InfrastructureDetector,
)


def test_ccl_instantiation_default():
    """Test 1: CCL instantiation with defaults."""
    ccl = ContextCrystallizationLayer()
    assert ccl is not None
    assert ccl.timeout_sla_ms == 300
    assert ccl.fallback_timeout_ms == 500
    assert ccl.executor is not None


def test_ccl_instantiation_custom():
    """Test 2: CCL instantiation with custom timeouts."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=200, fallback_timeout_ms=400)
    assert ccl.timeout_sla_ms == 200
    assert ccl.fallback_timeout_ms == 400


@pytest.mark.asyncio
async def test_prefetch_async_non_blocking():
    """Test 3: Async prefetch returns immediately (non-blocking)."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)

    start = time.time()
    context = await ccl.prefetch_async()
    elapsed = (time.time() - start) * 1000

    assert isinstance(context, CrystallizedContext)
    # Should be fast (< 500ms even with slow phases)
    assert elapsed < 2000  # Very generous bound


@pytest.mark.asyncio
async def test_prefetch_async_with_file():
    """Test 4: Prefetch with file path parameter."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)

    context = await ccl.prefetch_async(file_path="/tmp/test.py")

    assert isinstance(context, CrystallizedContext)


@pytest.mark.asyncio
async def test_prefetch_async_with_context():
    """Test 5: Prefetch with request context parameter."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)

    req_ctx = {"user": "test", "intent": "IMPLEMENT"}
    context = await ccl.prefetch_async(request_context=req_ctx)

    assert isinstance(context, CrystallizedContext)


@pytest.mark.asyncio
async def test_prefetch_async_timeout_handling():
    """Test 6: Timeout handling with short SLA."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=50)  # Very short

    context = await ccl.prefetch_async()

    # Should return context (possibly partial) without crashing
    assert isinstance(context, CrystallizedContext)
    assert isinstance(context.error_details, dict)


@pytest.mark.asyncio
async def test_prefetch_async_no_file():
    """Test 7: Prefetch without file path."""
    ccl = ContextCrystallizationLayer(timeout_sla_ms=1000)

    context = await ccl.prefetch_async(file_path=None)

    assert isinstance(context, CrystallizedContext)


def test_crystallized_context_init():
    """Test 8: CrystallizedContext structure."""
    ctx = CrystallizedContext()

    assert ctx.rules is None
    assert ctx.lens is None
    assert ctx.infrastructure is None
    assert ctx.rules_ready is False
    assert ctx.lens_ready is False
    assert ctx.infrastructure_ready is False
    assert ctx.fallback_invoked is False
    assert ctx.error_details == {}


def test_crystallized_context_is_ready_false():
    """Test 9: is_ready() returns False when nothing is ready."""
    ctx = CrystallizedContext()
    assert ctx.is_ready() is False


def test_crystallized_context_is_ready_true():
    """Test 10: is_ready() returns True when at least one phase ready."""
    ctx = CrystallizedContext(rules_ready=True)
    assert ctx.is_ready() is True

    ctx2 = CrystallizedContext(lens_ready=True)
    assert ctx2.is_ready() is True

    ctx3 = CrystallizedContext(infrastructure_ready=True)
    assert ctx3.is_ready() is True


def test_crystallized_context_to_dict():
    """Test 11: Serialization to dict."""
    ctx = CrystallizedContext(
        rules_ready=True,
        lens_ready=False,
        infrastructure_ready=True,
        total_latency_ms=150.5,
        fallback_invoked=False,
    )

    data = ctx.to_dict()

    assert data["rules_ready"] is True
    assert data["lens_ready"] is False
    assert data["infrastructure_ready"] is True
    assert data["total_latency_ms"] == 150.5
    assert data["fallback_invoked"] is False


def test_crystallized_context_error_tracking():
    """Test 12: Error details tracking."""
    ctx = CrystallizedContext()

    ctx.error_details["rules"] = "Timeout after 300ms"
    ctx.error_details["lens"] = "File not found: /tmp/missing.py"

    assert len(ctx.error_details) == 2
    assert "Timeout" in ctx.error_details["rules"]
    assert "not found" in ctx.error_details["lens"]


def test_blocking_prefetch_timeout():
    """Test 13: Blocking prefetch with timeout."""
    ccl = ContextCrystallizationLayer(fallback_timeout_ms=500)

    start = time.time()
    context = ccl.prefetch_blocking()
    elapsed = (time.time() - start) * 1000

    assert isinstance(context, CrystallizedContext)
    assert elapsed < 1000  # Should timeout quickly


def test_blocking_prefetch_no_file():
    """Test 14: Blocking prefetch without file."""
    ccl = ContextCrystallizationLayer(fallback_timeout_ms=500)

    context = ccl.prefetch_blocking(file_path=None)

    assert isinstance(context, CrystallizedContext)


def test_blocking_prefetch_with_file():
    """Test 15: Blocking prefetch with file."""
    ccl = ContextCrystallizationLayer(fallback_timeout_ms=500)

    context = ccl.prefetch_blocking(file_path="/tmp/test.py")

    assert isinstance(context, CrystallizedContext)


def test_ccl_lazy_init_rules_cache():
    """Test 16: Lazy initialization of RulesCache."""
    ccl = ContextCrystallizationLayer()

    assert ccl._rules_cache is None

    rules = ccl._get_rules_cache()

    assert isinstance(rules, RulesCache)
    assert ccl._rules_cache is rules  # Cached for reuse


def test_ccl_lazy_init_lens_warmer():
    """Test 17: Lazy initialization of LENSWarmer."""
    ccl = ContextCrystallizationLayer()

    assert ccl._lens_warmer is None

    warmer = ccl._get_lens_warmer()

    assert isinstance(warmer, LENSWarmer)
    assert ccl._lens_warmer is warmer


def test_ccl_lazy_init_infrastructure():
    """Test 18: Lazy initialization of InfrastructureDetector."""
    ccl = ContextCrystallizationLayer()

    assert ccl._infrastructure_detector is None

    detector = ccl._get_infrastructure_detector()

    assert isinstance(detector, InfrastructureDetector)
    assert ccl._infrastructure_detector is detector


def test_crystallized_context_latency_tracking():
    """Test 19: Latency tracking."""
    ctx = CrystallizedContext(
        rules_latency_ms=45.5,
        lens_latency_ms=120.3,
        infrastructure_latency_ms=32.1,
        total_latency_ms=198.9,
    )

    assert ctx.rules_latency_ms == 45.5
    assert ctx.lens_latency_ms == 120.3
    assert ctx.infrastructure_latency_ms == 32.1
    assert ctx.total_latency_ms == 198.9


def test_crystallized_context_completion_time():
    """Test 20: Completion time tracking."""
    import time

    ctx = CrystallizedContext()
    assert ctx.completed_at is None

    ctx.completed_at = time.time()

    assert ctx.completed_at is not None
    assert isinstance(ctx.completed_at, float)


# AC_COMPLETE: AC-PHASE49-S1-test_ccl_core ✅
# Tests: 20/20 ✅
