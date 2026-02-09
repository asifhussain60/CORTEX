"""
Unit tests for Phase D - Intelligence Warming (Phase 54 S5 integration).

Tests for:
- Async intelligence context pre-warming
- Multi-intent caching (IMPLEMENT, FIX, ANALYZE, GENERIC)
- Cache retrieval and latency
- Graceful degradation on synthesis failure

CORE Rules:
- CORE-008: TDD (tests before code) ✅
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from cortex.orchestrators.phase_49.context_crystallization_layer import (
    ContextCrystallizationLayer,
)


class TestPhaseD_IntelligenceWarming:
    """Test Phase D intelligence warming (Phase 54 S5 integration)."""

    @pytest.fixture
    def ccl(self):
        """Create CCL with all phases enabled."""
        return ContextCrystallizationLayer(
            timeout_ms=500,
            enable_rules_cache=True,
            enable_lens_warmer=True,
            enable_infra_detection=True,
        )

    def test_intelligence_cache_initialized(self, ccl):
        """Intelligence cache should initialize as empty dict."""
        cache = ccl.get_intelligence_cache()
        assert isinstance(cache, dict)
        assert len(cache) == 0

    @pytest.mark.asyncio
    async def test_phase_d_intelligence_warming(self, ccl):
        """Phase D should pre-warm intelligence contexts."""
        with patch("cortex.orchestrators.phase_49.context_crystallization_layer.get_synthesis_engine") as mock_engine:
            with patch("cortex.orchestrators.phase_49.context_crystallization_layer.IntelligenceGate") as mock_gate:
                # Mock context
                mock_context = Mock()
                mock_context.rules = []
                mock_engine.return_value.synthesize_unified_context.return_value = mock_context
                mock_gate.return_value = Mock()

                # Run phase D directly
                result = await ccl._phase_d_intelligence_warming()

                # Should return dict with cache
                assert isinstance(result, dict)
                assert "intelligence_cache" in result
                assert "warmup_latency_ms" in result
                assert result["warmup_latency_ms"] >= 0

    @pytest.mark.asyncio
    async def test_phase_d_caches_multiple_intents(self, ccl):
        """Phase D should cache contexts for multiple intents."""
        with patch("cortex.orchestrators.phase_49.context_crystallization_layer.get_synthesis_engine") as mock_engine:
            with patch("cortex.orchestrators.phase_49.context_crystallization_layer.IntelligenceGate"):
                mock_context = Mock()
                mock_engine.return_value.synthesize_unified_context.return_value = mock_context

                # Run phase D
                result = await ccl._phase_d_intelligence_warming()

                # Should have called synthesis for each intent
                calls = mock_engine.return_value.synthesize_unified_context.call_args_list
                intent_calls = [call[1]["intent_type"] for call in calls]
                
                assert "IMPLEMENT" in intent_calls
                assert "FIX" in intent_calls
                assert "ANALYZE" in intent_calls
                assert "GENERIC" in intent_calls

    @pytest.mark.asyncio
    async def test_phase_d_handles_synthesis_failure(self, ccl):
        """Phase D should handle synthesis failures gracefully."""
        with patch("cortex.orchestrators.phase_49.context_crystallization_layer.get_synthesis_engine") as mock_engine:
            with patch("cortex.orchestrators.phase_49.context_crystallization_layer.IntelligenceGate"):
                mock_engine.return_value.synthesize_unified_context.side_effect = Exception("Synthesis failed")

                result = await ccl._phase_d_intelligence_warming()

                # Should return error dict
                assert isinstance(result, dict)
                assert result["intelligence_cache"] == {}
                assert "error" in result

    @pytest.mark.asyncio
    async def test_phase_d_respects_file_path(self, ccl):
        """Phase D should pass file_path to synthesis engine."""
        ccl._pending_file_path = "/src/main.py"

        with patch("cortex.orchestrators.phase_49.context_crystallization_layer.get_synthesis_engine") as mock_engine:
            with patch("cortex.orchestrators.phase_49.context_crystallization_layer.IntelligenceGate"):
                mock_context = Mock()
                mock_engine.return_value.synthesize_unified_context.return_value = mock_context

                await ccl._phase_d_intelligence_warming()

                # Should have called with file_path
                calls = mock_engine.return_value.synthesize_unified_context.call_args_list
                for call in calls:
                    assert call[1]["file_path"] == "/src/main.py"

    @pytest.mark.asyncio
    async def test_ccl_run_prefetch_phases_includes_d(self, ccl):
        """CCL prefetch should include Phase D in parallel."""
        with patch.object(ccl, "_phase_a_rules_cache", new_callable=AsyncMock) as mock_a:
            with patch.object(ccl, "_phase_b_lens_warmer", new_callable=AsyncMock) as mock_b:
                with patch.object(ccl, "_phase_c_infra_detection", new_callable=AsyncMock) as mock_c:
                    with patch.object(ccl, "_phase_d_intelligence_warming", new_callable=AsyncMock) as mock_d:
                        mock_a.return_value = {}
                        mock_b.return_value = Mock(ast_ready=False, git_history_cached=False)
                        mock_c.return_value = Mock(environment="dev", capabilities=[])
                        mock_d.return_value = {"intelligence_cache": {}, "warmup_latency_ms": 10}

                        ctx = await ccl._run_prefetch_phases()

                        # Phase D should have been called
                        mock_d.assert_called_once()
                        assert ctx.rules_cache is not None

    def test_intelligence_cache_exposed_via_getter(self, ccl):
        """Intelligence cache should be accessible via getter."""
        test_context = {"test": "context"}
        ccl._intelligence_cache = test_context

        cache = ccl.get_intelligence_cache()
        assert cache == test_context

    @pytest.mark.asyncio
    async def test_phase_d_latency_reported(self, ccl):
        """Phase D should report warmup latency."""
        with patch("cortex.orchestrators.phase_49.context_crystallization_layer.get_synthesis_engine") as mock_engine:
            with patch("cortex.orchestrators.phase_49.context_crystallization_layer.IntelligenceGate"):
                mock_context = Mock()
                mock_engine.return_value.synthesize_unified_context.return_value = mock_context

                result = await ccl._phase_d_intelligence_warming()

                latency = result.get("warmup_latency_ms")
                assert latency is not None
                assert latency >= 0

    @pytest.mark.asyncio
    async def test_ccl_stores_intelligence_cache(self, ccl):
        """CCL should store Phase D intelligence cache internally."""
        with patch.object(ccl, "_phase_a_rules_cache", new_callable=AsyncMock) as mock_a:
            with patch.object(ccl, "_phase_b_lens_warmer", new_callable=AsyncMock) as mock_b:
                with patch.object(ccl, "_phase_c_infra_detection", new_callable=AsyncMock) as mock_c:
                    with patch.object(ccl, "_phase_d_intelligence_warming", new_callable=AsyncMock) as mock_d:
                        mock_intent_context = Mock(rules=["rule1"])
                        mock_cache = {"IMPLEMENT": mock_intent_context}
                        
                        mock_a.return_value = {}
                        mock_b.return_value = Mock(ast_ready=False, git_history_cached=False)
                        mock_c.return_value = Mock(environment="dev", capabilities=[])
                        mock_d.return_value = {"intelligence_cache": mock_cache, "warmup_latency_ms": 20}

                        await ccl._run_prefetch_phases()

                        # Should store in _intelligence_cache
                        assert ccl._intelligence_cache == mock_cache

    def test_phase_d_marked_with_ac_marker(self, ccl):
        """Phase D should include AC markers for audit."""
        # Check that _phase_d_intelligence_warming is defined
        assert hasattr(ccl, "_phase_d_intelligence_warming")
        assert callable(getattr(ccl, "_phase_d_intelligence_warming"))
        
        # Get the method docstring
        method = getattr(ccl, "_phase_d_intelligence_warming")
        assert "Phase 54 S5" in method.__doc__
        assert "AC_PHASE54-S5-001" in method.__code__.co_consts or "AC_PHASE54-S5" in method.__doc__
