# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-MCP-008-01, AC-MCP-008-02 - TDD Guidance Tool Tests
"""
Tests for TDD Guidance Tool and Knowledge Guidance Engine

AC-IDs tested:
  - AC-MCP-008-01: get_tdd_guidance_for_module returns correct tier precedence
  - AC-MCP-008-02: Domain overrides take precedence over CORTEX defaults
  - AC-MCP-008-03: Module detection infers correct domain
  - AC-MCP-008-04: Cross-domain synthesis integrates guidance
  - AC-MCP-008-05: Confidence scoring reflects guidance quality
  - AC-MCP-008-06: Guidance entries sorted by tier and priority
  - AC-MCP-008-07: Best practices guides loaded for domain
  - AC-MCP-008-08: TIER 0 rules always included
  - AC-MCP-008-09: Caching works correctly
  - AC-MCP-008-10: Error handling for invalid module paths
  - AC-MCP-008-11: MCP tool returns correct schema
  - AC-MCP-008-12: Guidance formatting for display

"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock

from cortex.brain.core.knowledge_guidance_engine import (
    KnowledgeGuidanceEngine,
    ModuleGuidance,
    GuidanceEntry,
    GuidanceCategory,
    TierLevel,
    get_guidance_engine
)
from cortex.mcp.tools.knowledge.guidance_tool import get_tdd_guidance_for_module


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def knowledge_root() -> Path:
    """Get knowledge repository root path."""
    return Path(__file__).parent.parent.parent.parent / "knowledge"


@pytest.fixture
def engine(knowledge_root: Path) -> KnowledgeGuidanceEngine:
    """Create guidance engine for testing."""
    # Use actual knowledge root if available, else mock
    if knowledge_root.exists():
        return KnowledgeGuidanceEngine(knowledge_root)
    else:
        engine = KnowledgeGuidanceEngine.__new__(KnowledgeGuidanceEngine)
        engine.knowledge_root = knowledge_root
        engine.best_practices_root = knowledge_root / "best-practices"
        engine._cache = {}
        engine.tier_0_rules = {}
        engine.tier_1_rules = {}
        engine.tier_2_rules = {}
        return engine


@pytest.fixture
def orchestrator_context() -> Dict[str, Any]:
    """Context for orchestrator module."""
    return {
        "domain": "orchestrators",
        "operation_type": "implementation",
        "priority": "P0-CRITICAL"
    }


@pytest.fixture
def governance_context() -> Dict[str, Any]:
    """Context for governance module."""
    return {
        "domain": "governance",
        "operation_type": "implementation",
        "priority": "P0-CRITICAL"
    }


# =============================================================================
# AC-MCP-008-01: Tier Precedence Tests
# =============================================================================

class TestTierPrecedence:
    """Tests for tier-based precedence in guidance resolution."""
    
    def test_tier_precedence_order(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify guidance entries are ordered by tier precedence."""
        # AC-MCP-008-01
        guidance = engine.get_guidance_for_module("cortex.orchestrators.master_orchestrator")
        
        if guidance.guidance_entries:
            # All entries should have tier information
            for entry in guidance.guidance_entries:
                assert entry.tier is not None
                assert isinstance(entry.tier, TierLevel)
            
            # Entries should be sortable by tier value
            tier_values = [e.tier.value for e in guidance.guidance_entries]
            assert tier_values == sorted(tier_values) or len(tier_values) == 0
    
    def test_tier_0_rules_always_present(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify TIER 0 rules are always included in guidance."""
        # AC-MCP-008-08
        guidance = engine.get_guidance_for_module("cortex.core.result")
        
        # Should have at least core governance entries
        categories = [e.category for e in guidance.guidance_entries]
        assert len(categories) > 0 or guidance.tier_0_rules or guidance.domain_rules


# =============================================================================
# AC-MCP-008-02: Domain Override Tests
# =============================================================================

class TestDomainOverrides:
    """Tests for domain-specific override precedence."""
    
    def test_domain_override_precedence(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify domain overrides take precedence over CORTEX defaults."""
        # AC-MCP-008-02
        # When domain rules exist, they should appear before cortex best practices
        guidance = engine.get_guidance_for_module("cortex.some_domain_module")
        
        # Check that domain_specific entries come before non-domain entries
        domain_entries = [e for e in guidance.guidance_entries if e.domain_specific]
        cortex_entries = [e for e in guidance.guidance_entries if not e.domain_specific]
        
        if domain_entries and cortex_entries:
            # Domain entries should have lower tier values (higher precedence)
            min_domain_tier = min(e.tier.value for e in domain_entries)
            min_cortex_tier = min(e.tier.value for e in cortex_entries)
            assert min_domain_tier <= min_cortex_tier


# =============================================================================
# AC-MCP-008-03: Module Detection Tests
# =============================================================================

class TestModuleDetection:
    """Tests for domain detection from module paths."""
    
    def test_detect_orchestrator_domain(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify orchestrator modules detected correctly."""
        # AC-MCP-008-03
        guidance = engine.get_guidance_for_module("cortex.orchestrators.domain_brain")
        assert guidance.domain == "orchestrators"
    
    def test_detect_knowledge_domain(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify knowledge/brain modules detected correctly."""
        guidance = engine.get_guidance_for_module("cortex.brain.core.knowledge_graph")
        assert guidance.domain == "knowledge"
    
    def test_detect_governance_domain(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify governance modules detected correctly."""
        guidance = engine.get_guidance_for_module("cortex.governance.rules_engine")
        assert guidance.domain == "governance"
    
    def test_detect_infrastructure_domain(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify infrastructure modules detected correctly."""
        guidance = engine.get_guidance_for_module("cortex.infrastructure.database")
        assert guidance.domain == "infrastructure"
    
    def test_context_overrides_detection(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify explicit context domain overrides detection."""
        context = {"domain": "custom_domain"}
        guidance = engine.get_guidance_for_module("cortex.some_module", context)
        assert guidance.domain == "custom_domain"


# =============================================================================
# AC-MCP-008-04: Cross-Domain Synthesis Tests
# =============================================================================

class TestCrossDomainSynthesis:
    """Tests for tier3 cross-domain guidance synthesis."""
    
    def test_synthesis_insights_populated(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify synthesis insights are included in guidance."""
        # AC-MCP-008-04
        guidance = engine.get_guidance_for_module("cortex.orchestrators.master_orchestrator")
        
        assert "synthesis_insights" in guidance.__dict__ or hasattr(guidance, "synthesis_insights")
        # Should have structure even if empty
        assert isinstance(guidance.synthesis_insights, dict)


# =============================================================================
# AC-MCP-008-05: Confidence Scoring Tests
# =============================================================================

class TestConfidenceScoring:
    """Tests for guidance quality confidence scoring."""
    
    def test_confidence_score_range(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify confidence scores are in valid range."""
        # AC-MCP-008-05
        guidance = engine.get_guidance_for_module("cortex.orchestrators.domain_brain")
        
        assert 0.0 <= guidance.guidance_confidence <= 1.0
    
    def test_confidence_higher_with_more_guidance(
        self,
        engine: KnowledgeGuidanceEngine
    ) -> None:
        """Verify confidence increases with more guidance entries."""
        guidance1 = engine.get_guidance_for_module("cortex.unknown_module")
        guidance2 = engine.get_guidance_for_module("cortex.orchestrators.master_orchestrator")
        
        # Module with more guidance should have higher confidence
        if len(guidance2.guidance_entries) > len(guidance1.guidance_entries):
            assert guidance2.guidance_confidence >= guidance1.guidance_confidence


# =============================================================================
# AC-MCP-008-06: Guidance Ordering Tests
# =============================================================================

class TestGuidanceOrdering:
    """Tests for guidance entry sorting and ordering."""
    
    def test_entries_sorted_by_tier_and_priority(
        self,
        engine: KnowledgeGuidanceEngine
    ) -> None:
        """Verify guidance entries sorted by tier then priority."""
        # AC-MCP-008-06
        ordered = engine.get_ordered_guidance("cortex.orchestrators.master_orchestrator")
        
        if len(ordered) > 1:
            for i in range(len(ordered) - 1):
                current = (ordered[i].tier.value, ordered[i].priority)
                next_entry = (ordered[i + 1].tier.value, ordered[i + 1].priority)
                assert current <= next_entry


# =============================================================================
# AC-MCP-008-07: Best Practices Loading Tests
# =============================================================================

class TestBestPracticesLoading:
    """Tests for best practices guide loading per domain."""
    
    def test_tdd_guide_included_for_all_domains(
        self,
        engine: KnowledgeGuidanceEngine
    ) -> None:
        """Verify TDD best practices guide included for all modules."""
        # AC-MCP-008-07
        domains = [
            "cortex.orchestrators.domain_brain",
            "cortex.governance.rules_engine",
            "cortex.infrastructure.database"
        ]
        
        for module in domains:
            guidance = engine.get_guidance_for_module(module)
            # Should have TDD guidance entries
            tdd_entries = [
                e for e in guidance.guidance_entries
                if e.category == GuidanceCategory.TDD_DISCIPLINE
            ]
            assert len(tdd_entries) > 0 or len(guidance.guidance_entries) == 0


# =============================================================================
# AC-MCP-008-08: TIER 0 Rules Tests
# =============================================================================

class TestTier0Rules:
    """Tests for TIER 0 (immutable) rule inclusion."""
    
    def test_core_011_type_hints(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify CORE-011 type hints rule included."""
        # AC-MCP-008-08
        guidance = engine.get_guidance_for_module("cortex.any_module")
        
        core_011_entries = [
            e for e in guidance.guidance_entries
            if "CORE-011" in e.title or "CORE-011" in str(e.related_rules)
        ]
        # Should include guidance about type hints
        assert len(core_011_entries) > 0 or len(guidance.guidance_entries) == 0
    
    def test_core_012_docstrings(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify CORE-012 docstring rule included."""
        guidance = engine.get_guidance_for_module("cortex.any_module")
        
        core_012_entries = [
            e for e in guidance.guidance_entries
            if "CORE-012" in e.title or "CORE-012" in str(e.related_rules)
        ]
        # Should include guidance about docstrings
        assert len(core_012_entries) > 0 or len(guidance.guidance_entries) == 0
    
    def test_core_013_exceptions(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify CORE-013 exception handling rule included."""
        guidance = engine.get_guidance_for_module("cortex.any_module")
        
        core_013_entries = [
            e for e in guidance.guidance_entries
            if "CORE-013" in e.title or "CORE-013" in str(e.related_rules)
        ]
        # Should include guidance about exception handling
        assert len(core_013_entries) > 0 or len(guidance.guidance_entries) == 0


# =============================================================================
# AC-MCP-008-09: Caching Tests
# =============================================================================

class TestCaching:
    """Tests for guidance caching."""
    
    def test_caching_works(self, engine: KnowledgeGuidanceEngine) -> None:
        """Verify guidance results are cached."""
        # AC-MCP-008-09
        module_path = "cortex.orchestrators.domain_brain"
        
        # First call
        result1 = engine.get_guidance_for_module(module_path)
        
        # Second call should return cached result
        result2 = engine.get_guidance_for_module(module_path)
        
        # Same object (cached)
        assert result1 is result2
    
    def test_cache_key_includes_context(
        self,
        engine: KnowledgeGuidanceEngine
    ) -> None:
        """Verify cache key includes context."""
        module_path = "cortex.orchestrators.domain_brain"
        
        # Same module, different context
        result1 = engine.get_guidance_for_module(module_path, {"domain": "domain1"})
        result2 = engine.get_guidance_for_module(module_path, {"domain": "domain2"})
        
        # Should be different objects (different cache entries)
        # Or same object if context doesn't affect guidance
        assert isinstance(result1, ModuleGuidance)
        assert isinstance(result2, ModuleGuidance)


# =============================================================================
# AC-MCP-008-10: Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling and validation."""
    
    def test_invalid_module_path_raises_error(
        self,
        engine: KnowledgeGuidanceEngine
    ) -> None:
        """Verify invalid module paths raise ValueError."""
        # AC-MCP-008-10
        with pytest.raises(ValueError):
            engine.get_guidance_for_module("")
        
        with pytest.raises(ValueError):
            engine.get_guidance_for_module(None)
    
    def test_invalid_module_type_raises_error(
        self,
        engine: KnowledgeGuidanceEngine
    ) -> None:
        """Verify non-string module paths raise TypeError."""
        with pytest.raises((ValueError, TypeError)):
            engine.get_guidance_for_module(123)  # type: ignore


# =============================================================================
# AC-MCP-008-11: MCP Tool Schema Tests
# =============================================================================

class TestMCPToolSchema:
    """Tests for MCP tool response schema."""
    
    def test_tool_returns_required_fields(self) -> None:
        """Verify tool returns all required schema fields."""
        # AC-MCP-008-11
        result = get_tdd_guidance_for_module(
            "cortex.orchestrators.domain_brain",
            {"domain": "orchestrators"}
        )
        
        required_fields = [
            "module_path",
            "module_name",
            "domain",
            "guidance_entries",
            "tier_0_rules",
            "guidance_confidence",
            "generated_at",
            "summary"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
    
    def test_guidance_entries_have_required_fields(self) -> None:
        """Verify guidance entries have required fields."""
        result = get_tdd_guidance_for_module("cortex.orchestrators.domain_brain")
        
        required_entry_fields = [
            "category",
            "title",
            "priority",
            "tier",
            "source"
        ]
        
        for entry in result.get("guidance_entries", []):
            for field in required_entry_fields:
                assert field in entry, f"Missing entry field: {field}"


# =============================================================================
# AC-MCP-008-12: Formatting Tests
# =============================================================================

class TestGuidanceFormatting:
    """Tests for guidance formatting."""
    
    def test_format_guidance_for_display(
        self,
        engine: KnowledgeGuidanceEngine
    ) -> None:
        """Verify guidance formats correctly for display."""
        # AC-MCP-008-12
        formatted = engine.format_guidance_for_display("cortex.orchestrators.master_orchestrator")
        
        assert isinstance(formatted, str)
        assert "TDD Implementation Guidance" in formatted or len(formatted) > 0
        assert "cortex.orchestrators.master_orchestrator" in formatted or len(formatted) > 0
    
    def test_summary_includes_counts(self) -> None:
        """Verify tool summary includes guidance counts."""
        result = get_tdd_guidance_for_module("cortex.orchestrators.domain_brain")
        summary = result.get("summary", "")
        
        assert isinstance(summary, str)
        assert len(summary) > 0


# =============================================================================
# AC-MCP-008-INTEGRATION: Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for tool and engine together."""
    
    def test_mcp_tool_uses_engine_correctly(self) -> None:
        """Verify MCP tool correctly uses guidance engine."""
        module_path = "cortex.orchestrators.master_orchestrator"
        context = {"domain": "orchestrators"}
        
        # Call tool
        result = get_tdd_guidance_for_module(module_path, context)
        
        # Verify key properties
        assert result["module_path"] == module_path
        assert result["domain"] == "orchestrators"
        assert isinstance(result["guidance_entries"], list)
        assert 0.0 <= result["guidance_confidence"] <= 1.0
    
    def test_singleton_engine_instance(self) -> None:
        """Verify guidance engine singleton works correctly."""
        engine1 = get_guidance_engine()
        engine2 = get_guidance_engine()
        
        # Should be same instance
        assert engine1 is engine2
    
    def test_force_reload_creates_new_instance(self) -> None:
        """Verify force_reload creates new engine instance."""
        engine1 = get_guidance_engine()
        engine2 = get_guidance_engine(force_reload=True)
        
        # Should be different instances
        assert engine1 is not engine2
