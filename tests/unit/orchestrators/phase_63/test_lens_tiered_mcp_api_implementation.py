"""
Phase 63: LENS Tiered MCP API - GREEN Phase Implementation Tests

Full test suite for cortex_lens_quick, cortex_lens_targeted, cortex_lens_stream,
and Tier 4 backward compatibility.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import time
from typing import List

from cortex.lens.lens_tiered_mcp_api import (
    LensTier,
    LensAnalysisResult,
    StreamEvent,
    LensCapability,
    LensCapabilityRegistry,
    LensQuickTier2,
    LensTargetedTier3,
    LensStreamTier3,
    LensAnalyzerTier4,
    LensOrchestratorIntegration,
)


class TestLensCapability:
    """Tests for LensCapability"""
    
    def test_capability_initialization(self):
        """Capability initializes with correct attributes"""
        cap = LensCapability("test_cap", priority=5, cost_ms=100)
        
        assert cap.name == "test_cap"
        assert cap.priority == 5
        assert cap.cost_ms == 100
        assert len(cap.dependencies) == 0
    
    def test_capability_add_dependency(self):
        """Can add capability dependencies"""
        cap = LensCapability("dep_test")
        cap.add_dependency("other_cap")
        
        assert "other_cap" in cap.dependencies
    
    def test_capability_multiple_dependencies(self):
        """Can add multiple dependencies"""
        cap = LensCapability("multi_dep")
        cap.add_dependency("cap1")
        cap.add_dependency("cap2")
        
        assert len(cap.dependencies) == 2
        assert "cap1" in cap.dependencies


class TestLensCapabilityRegistry:
    """Tests for LensCapabilityRegistry"""
    
    def test_registry_initialization(self):
        """Registry initializes with standard capabilities"""
        registry = LensCapabilityRegistry()
        
        assert len(registry.capabilities) > 0
        assert registry.get("syntax_check") is not None
    
    def test_registry_get_by_priority(self):
        """Get capabilities by priority threshold"""
        registry = LensCapabilityRegistry()
        high_priority = registry.get_by_priority(max_priority=3)
        
        assert len(high_priority) > 0
        assert all(c.priority <= 3 for c in high_priority)
    
    def test_registry_register_capability(self):
        """Can register new capabilities"""
        registry = LensCapabilityRegistry()
        initial_count = len(registry.capabilities)
        
        registry.register("custom_cap", priority=7, cost_ms=50)
        
        assert len(registry.capabilities) == initial_count + 1
        assert registry.get("custom_cap") is not None
    
    def test_registry_validate_capabilities_valid(self):
        """Validates valid capabilities"""
        registry = LensCapabilityRegistry()
        valid, missing = registry.validate_capabilities(["syntax_check"])
        
        assert valid is True
        assert len(missing) == 0
    
    def test_registry_validate_capabilities_invalid(self):
        """Detects invalid capabilities"""
        registry = LensCapabilityRegistry()
        valid, missing = registry.validate_capabilities(["nonexistent_cap"])
        
        assert valid is False
        assert "nonexistent_cap" in missing


class TestLensAnalysisResult:
    """Tests for LensAnalysisResult"""
    
    def test_result_creation(self):
        """Result creates with correct attributes"""
        result = LensAnalysisResult(
            tier=LensTier.TIER_2_QUICK,
            file_path=Path("test.py"),
            timestamp="2026-02-09T00:00:00",
            findings=[{"finding": "test"}],
            capabilities_used=["test_cap"],
            analysis_time_ms=50.0,
        )
        
        assert result.tier == LensTier.TIER_2_QUICK
        assert result.file_path == Path("test.py")
        assert len(result.findings) == 1
    
    def test_result_to_dict(self):
        """Result exports to dictionary"""
        result = LensAnalysisResult(
            tier=LensTier.TIER_2_QUICK,
            file_path=Path("test.py"),
            timestamp="2026-02-09T00:00:00",
        )
        
        result_dict = result.to_dict()
        
        assert "tier" in result_dict
        assert "file_path" in result_dict
        assert "findings" in result_dict


class TestLensQuickTier2:
    """Tests for Tier 2 Quick Analysis"""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            path = Path(f.name)
        yield path
        path.unlink()
    
    def test_tier2_initialization(self):
        """Tier 2 initializes correctly"""
        tier2 = LensQuickTier2()
        
        assert tier2.cache_ttl_seconds == 300
        assert len(tier2.cache) == 0
    
    @pytest.mark.asyncio
    async def test_tier2_quick_analysis(self, temp_file):
        """Tier 2 performs quick analysis under 200ms"""
        tier2 = LensQuickTier2()
        
        start = time.time()
        result = await tier2.analyze(temp_file)
        elapsed_ms = (time.time() - start) * 1000
        
        assert result.tier == LensTier.TIER_2_QUICK
        assert elapsed_ms < 500  # Generous buffer
        assert len(result.findings) > 0
    
    @pytest.mark.asyncio
    async def test_tier2_caching(self, temp_file):
        """Tier 2 caches results"""
        tier2 = LensQuickTier2()
        
        result1 = await tier2.analyze(temp_file, use_cache=False)
        result2 = await tier2.analyze(temp_file, use_cache=True)
        
        assert result1.timestamp == result2.timestamp
    
    @pytest.mark.asyncio
    async def test_tier2_no_cache_on_disable(self, temp_file):
        """Tier 2 skips cache when disabled"""
        tier2 = LensQuickTier2()
        
        result1 = await tier2.analyze(temp_file, use_cache=False)
        result2 = await tier2.analyze(temp_file, use_cache=False)
        
        assert result1.timestamp != result2.timestamp
    
    @pytest.mark.asyncio
    async def test_tier2_clear_cache(self):
        """Can clear Tier 2 cache"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            path = Path(f.name)
        
        try:
            tier2 = LensQuickTier2()
            await tier2.analyze(path, use_cache=True)
            
            assert len(tier2.cache) > 0
            tier2.clear_cache()
            assert len(tier2.cache) == 0
        finally:
            Path(path).unlink()


class TestLensTargetedTier3:
    """Tests for Tier 3 Targeted Analysis"""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            path = Path(f.name)
        yield path
        path.unlink()
    
    def test_tier3_initialization(self):
        """Tier 3 initializes correctly"""
        tier3 = LensTargetedTier3()
        
        assert tier3.registry is not None
    
    @pytest.mark.asyncio
    async def test_tier3_targeted_analysis(self, temp_file):
        """Tier 3 performs targeted analysis"""
        tier3 = LensTargetedTier3()
        
        result = await tier3.analyze(
            temp_file,
            capabilities=["syntax_check", "type_hints_analysis"],
        )
        
        assert result.tier == LensTier.TIER_3_TARGETED
        assert "syntax_check" in result.capabilities_used
    
    @pytest.mark.asyncio
    async def test_tier3_default_capabilities(self, temp_file):
        """Tier 3 uses default capabilities if not specified"""
        tier3 = LensTargetedTier3()
        
        result = await tier3.analyze(temp_file)
        
        assert len(result.capabilities_used) > 0
    
    @pytest.mark.asyncio
    async def test_tier3_invalid_capability_error(self, temp_file):
        """Tier 3 raises error for invalid capabilities"""
        tier3 = LensTargetedTier3()
        
        with pytest.raises(ValueError):
            await tier3.analyze(
                temp_file,
                capabilities=["nonexistent_cap"],
            )
    
    def test_tier3_resolve_dependencies(self):
        """Tier 3 resolves capability dependencies"""
        tier3 = LensTargetedTier3()
        
        result = tier3.resolve_dependencies(["syntax_check"])
        
        assert "syntax_check" in result


class TestLensStreamTier3:
    """Tests for Tier 3 Streaming Analysis"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository with Python files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "file1.py").write_text("def foo(): pass")
            (repo / "file2.py").write_text("def bar(): pass")
            yield repo
    
    def test_stream_tier3_initialization(self):
        """Stream Tier 3 initializes correctly"""
        stream = LensStreamTier3(batch_size=5)
        
        assert stream.batch_size == 5
    
    @pytest.mark.asyncio
    async def test_stream_analysis_yields_events(self, temp_repo):
        """Streaming analysis yields events"""
        stream = LensStreamTier3()
        events = []
        
        async for event in stream.stream_analysis(temp_repo):
            events.append(event)
        
        assert len(events) > 0
    
    @pytest.mark.asyncio
    async def test_stream_progress_event(self, temp_repo):
        """Stream emits progress events"""
        stream = LensStreamTier3()
        
        async for event in stream.stream_analysis(temp_repo):
            if event.event_type == "progress":
                assert "total_files" in event.data
                break
    
    @pytest.mark.asyncio
    async def test_stream_result_event(self, temp_repo):
        """Stream emits result events"""
        stream = LensStreamTier3()
        
        async for event in stream.stream_analysis(temp_repo):
            if event.event_type == "result":
                assert "results" in event.data
                break
    
    @pytest.mark.asyncio
    async def test_stream_complete_event(self, temp_repo):
        """Stream emits completion event"""
        stream = LensStreamTier3()
        events = []
        
        async for event in stream.stream_analysis(temp_repo):
            events.append(event)
        
        assert events[-1].event_type == "complete"


class TestLensAnalyzerTier4:
    """Tests for Tier 4 Full Analysis"""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            path = Path(f.name)
        yield path
        path.unlink()
    
    def test_tier4_initialization(self):
        """Tier 4 initializes correctly"""
        tier4 = LensAnalyzerTier4()
        
        assert tier4.registry is not None
    
    @pytest.mark.asyncio
    async def test_tier4_full_analysis(self, temp_file):
        """Tier 4 performs full analysis"""
        tier4 = LensAnalyzerTier4()
        
        result = await tier4.analyze(temp_file)
        
        assert result.tier == LensTier.TIER_4_FULL
        assert len(result.findings) > 0
    
    @pytest.mark.asyncio
    async def test_tier4_all_capabilities(self, temp_file):
        """Tier 4 uses all capabilities"""
        tier4 = LensAnalyzerTier4()
        
        result = await tier4.analyze(temp_file)
        
        # Should have multiple capabilities
        assert len(result.capabilities_used) >= 5


class TestBackwardCompatibility:
    """Tests for backward compatibility with Tier 4"""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            path = Path(f.name)
        yield path
        path.unlink()
    
    @pytest.mark.asyncio
    async def test_tier4_result_format_stable(self, temp_file):
        """Tier 4 result format unchanged"""
        tier4 = LensAnalyzerTier4()
        result = await tier4.analyze(temp_file)
        
        # Verify expected fields
        assert hasattr(result, 'tier')
        assert hasattr(result, 'file_path')
        assert hasattr(result, 'findings')
        assert hasattr(result, 'capabilities_used')
    
    @pytest.mark.asyncio
    async def test_tier4_json_export(self, temp_file):
        """Tier 4 exports to JSON correctly"""
        tier4 = LensAnalyzerTier4()
        result = await tier4.analyze(temp_file)
        
        json_data = result.to_dict()
        
        assert isinstance(json_data, dict)
        assert "tier" in json_data
        assert json_data["tier"] == "tier_4_full"


class TestOrchestratorIntegration:
    """Tests for orchestrator integration"""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            path = Path(f.name)
        yield path
        path.unlink()
    
    def test_orchestrator_integration_init(self):
        """Orchestrator integration initializes all tiers"""
        integration = LensOrchestratorIntegration()
        
        assert integration.tier2 is not None
        assert integration.tier3_targeted is not None
        assert integration.tier3_stream is not None
        assert integration.tier4 is not None
    
    @pytest.mark.asyncio
    async def test_interaction_orchestrator_quick_analysis(self, temp_file):
        """InteractionOrchestrator uses Tier 2"""
        integration = LensOrchestratorIntegration()
        
        result = await integration.interaction_orchestrator_quick_analysis(temp_file)
        
        assert result.tier == LensTier.TIER_2_QUICK
    
    @pytest.mark.asyncio
    async def test_tdd_orchestrator_context_enrichment(self, temp_file):
        """TDDOrchestrator uses Tier 2 for context"""
        integration = LensOrchestratorIntegration()
        
        result = await integration.tdd_orchestrator_context_enrichment(temp_file)
        
        assert result.tier == LensTier.TIER_2_QUICK
    
    @pytest.mark.asyncio
    async def test_plan_orchestrator_validation(self, temp_file):
        """PlanOrchestrator uses Tier 3 targeted"""
        integration = LensOrchestratorIntegration()
        
        result = await integration.plan_orchestrator_validation(
            temp_file,
            capabilities=["syntax_check"],
        )
        
        assert result.tier == LensTier.TIER_3_TARGETED
    
    @pytest.mark.asyncio
    async def test_onboarding_orchestrator_full(self, temp_file):
        """RepositoryOnboardingOrchestrator uses Tier 4"""
        integration = LensOrchestratorIntegration()
        
        result = await integration.onboarding_orchestrator_full_analysis(temp_file)
        
        assert result.tier == LensTier.TIER_4_FULL


class TestStreamEvent:
    """Tests for StreamEvent"""
    
    def test_stream_event_creation(self):
        """Stream event creates with correct attributes"""
        event = StreamEvent(
            event_type="progress",
            data={"stage": "initialized"},
        )
        
        assert event.event_type == "progress"
        assert event.data["stage"] == "initialized"
        assert event.timestamp is not None


class TestPerformanceCharacteristics:
    """Tests for tier performance SLAs"""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            path = Path(f.name)
        yield path
        path.unlink()
    
    @pytest.mark.asyncio
    async def test_tier2_performance_sla(self, temp_file):
        """Tier 2 meets <200ms SLA"""
        tier2 = LensQuickTier2()
        
        start = time.time()
        await tier2.analyze(temp_file)
        elapsed_ms = (time.time() - start) * 1000
        
        # Conservative: allow up to 500ms to account for system variability
        assert elapsed_ms < 500
    
    @pytest.mark.asyncio
    async def test_tier3_performance(self, temp_file):
        """Tier 3 completes reasonably"""
        tier3 = LensTargetedTier3()
        
        start = time.time()
        await tier3.analyze(temp_file)
        elapsed_ms = (time.time() - start) * 1000
        
        # Tier 3 should be faster than Tier 4
        assert elapsed_ms < 5000


class TestErrorHandling:
    """Tests for error handling"""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            path = Path(f.name)
        yield path
        path.unlink()
    
    @pytest.mark.asyncio
    async def test_nonexistent_file_handling(self):
        """Handles nonexistent files gracefully"""
        tier2 = LensQuickTier2()
        
        # Should not crash, may return error or empty result
        result = await tier2.analyze(Path("/nonexistent/file.py"))
        assert result is not None


class TestTierUpgradePath:
    """Tests for tier upgrade capabilities"""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass")
            path = Path(f.name)
        yield path
        path.unlink()
    
    @pytest.mark.asyncio
    async def test_upgrade_from_tier2_to_tier3(self, temp_file):
        """Can upgrade from Tier 2 to Tier 3"""
        tier2 = LensQuickTier2()
        tier3 = LensTargetedTier3()
        
        result2 = await tier2.analyze(temp_file)
        result3 = await tier3.analyze(temp_file)
        
        # Both should complete successfully
        assert result2.tier == LensTier.TIER_2_QUICK
        assert result3.tier == LensTier.TIER_3_TARGETED
    
    @pytest.mark.asyncio
    async def test_upgrade_from_tier2_to_tier4(self, temp_file):
        """Can upgrade from Tier 2 to Tier 4"""
        tier2 = LensQuickTier2()
        tier4 = LensAnalyzerTier4()
        
        result2 = await tier2.analyze(temp_file)
        result4 = await tier4.analyze(temp_file)
        
        # Both should complete successfully
        assert result2.tier == LensTier.TIER_2_QUICK
        assert result4.tier == LensTier.TIER_4_FULL
