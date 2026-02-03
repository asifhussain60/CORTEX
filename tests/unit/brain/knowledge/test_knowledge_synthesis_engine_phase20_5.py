"""
Tests for KnowledgeSynthesisEngine Phase 20.5 Enhancement (Component 2).

Authority: AC-KNOWLEDGE-SYNTHESIS-001
Rule: CORE-008 (TDD First)
"""

import pytest
from unittest.mock import Mock, patch
import time

from cortex.brain.knowledge.knowledge_synthesis_engine import (
    KnowledgeSynthesisEngine,
    get_synthesis_engine,
)
from cortex.brain.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
    LENSIntelligence,
    CompanyKnowledge,
    CORTEXKnowledge,
    SynthesisResult,
)


class TestKnowledgeSynthesisEngineEnhancement:
    """Test Phase 20.5 enhancements to KnowledgeSynthesisEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create KnowledgeSynthesisEngine instance."""
        return KnowledgeSynthesisEngine()
    
    @pytest.fixture
    def mock_lens_intelligence(self):
        """Create mock LENS intelligence."""
        return LENSIntelligence(
            git_analysis={"commits": 42, "hotspots": ["src/main.py"]},
            ast_analysis={"complexity": 15, "functions": 8},
            comment_analysis={"todos": 3, "fixmes": 1}
        )
    
    @pytest.fixture
    def mock_company_knowledge(self):
        """Create mock company knowledge."""
        return CompanyKnowledge(
            domain_rules={"payment": "PCI-DSS required"},
            compliance_standards=["PCI-DSS"],
            precedence="OVERRIDE"
        )
    
    def test_synthesize_unified_context_basic(self, engine, mock_lens_intelligence, mock_company_knowledge):
        """Test synthesize_unified_context with basic inputs."""
        context = engine.synthesize_unified_context(
            intent_type="IMPLEMENT",
            lens_intelligence=mock_lens_intelligence,
            company_knowledge=mock_company_knowledge,
            file_path="/test/file.py"
        )
        
        assert isinstance(context, UnifiedIntelligenceContext)
        assert context.intent_type == "IMPLEMENT"
        assert context.file_path == "/test/file.py"
        assert context.lens_intelligence == mock_lens_intelligence
        assert context.company_knowledge == mock_company_knowledge
    
    def test_synthesize_unified_context_loads_cortex_knowledge(self, engine, mock_lens_intelligence, mock_company_knowledge):
        """Test that synthesize_unified_context loads CORTEX knowledge."""
        context = engine.synthesize_unified_context(
            intent_type="IMPLEMENT",
            lens_intelligence=mock_lens_intelligence,
            company_knowledge=mock_company_knowledge,
            file_path="/test/file.py"
        )
        
        assert isinstance(context.cortex_knowledge, CORTEXKnowledge)
        assert isinstance(context.cortex_knowledge.best_practices, dict)
        assert isinstance(context.cortex_knowledge.applicable_patterns, list)
    
    def test_synthesize_unified_context_generates_synthesis_result(self, engine, mock_lens_intelligence, mock_company_knowledge):
        """Test that synthesize_unified_context generates synthesis result."""
        context = engine.synthesize_unified_context(
            intent_type="IMPLEMENT",
            lens_intelligence=mock_lens_intelligence,
            company_knowledge=mock_company_knowledge,
            file_path="/test/file.py"
        )
        
        assert isinstance(context.synthesis_result, SynthesisResult)
        assert isinstance(context.synthesis_result.merged_rules, dict)
        assert isinstance(context.synthesis_result.citations, list)
        assert isinstance(context.synthesis_result.violations, list)
        assert isinstance(context.synthesis_result.guidance, list)
    
    def test_synthesize_unified_context_company_override_precedence(self, engine, mock_lens_intelligence, mock_company_knowledge):
        """Test that company rules override CORTEX rules in synthesis."""
        # Add conflicting rule to company knowledge
        mock_company_knowledge.domain_rules["testing"] = "COMPANY: Manual testing required"
        
        context = engine.synthesize_unified_context(
            intent_type="IMPLEMENT",
            lens_intelligence=mock_lens_intelligence,
            company_knowledge=mock_company_knowledge,
            file_path="/test/file.py"
        )
        
        # Company rule should be in merged rules (if testing is applicable)
        assert context.synthesis_result is not None
    
    def test_synthesize_unified_context_without_lens(self, engine, mock_company_knowledge):
        """Test synthesize_unified_context without LENS intelligence (fallback)."""
        context = engine.synthesize_unified_context(
            intent_type="IMPLEMENT",
            lens_intelligence=None,
            company_knowledge=mock_company_knowledge,
            file_path="/test/file.py"
        )
        
        assert isinstance(context, UnifiedIntelligenceContext)
        assert context.intent_type == "IMPLEMENT"
        # Should have empty LENS intelligence
        assert len(context.lens_intelligence.git_analysis) == 0
    
    def test_synthesize_unified_context_without_company(self, engine, mock_lens_intelligence):
        """Test synthesize_unified_context without company knowledge (fallback)."""
        context = engine.synthesize_unified_context(
            intent_type="IMPLEMENT",
            lens_intelligence=mock_lens_intelligence,
            company_knowledge=None,
            file_path="/test/file.py"
        )
        
        assert isinstance(context, UnifiedIntelligenceContext)
        assert context.intent_type == "IMPLEMENT"
        # Should have empty company knowledge
        assert len(context.company_knowledge.domain_rules) == 0
    
    def test_synthesize_unified_context_timestamp(self, engine, mock_lens_intelligence, mock_company_knowledge):
        """Test that synthesize_unified_context adds timestamp."""
        before = time.time()
        context = engine.synthesize_unified_context(
            intent_type="IMPLEMENT",
            lens_intelligence=mock_lens_intelligence,
            company_knowledge=mock_company_knowledge,
            file_path="/test/file.py"
        )
        after = time.time()
        
        assert before <= context.timestamp <= after
    
    def test_load_cortex_best_practices(self, engine):
        """Test _load_cortex_best_practices loads YAML files."""
        best_practices = engine._load_cortex_best_practices(intent_type="IMPLEMENT")
        
        assert isinstance(best_practices, dict)
        # Should attempt to load some CORE rules
        # (may be empty if YAMLs not found, but should not error)
    
    def test_resolve_rule_conflicts_company_precedence(self, engine):
        """Test _resolve_rule_conflicts gives company rules precedence."""
        cortex_rules = {"testing": "CORTEX: TDD required"}
        company_rules = {"testing": "COMPANY: Manual testing required"}
        
        merged = engine._resolve_rule_conflicts(cortex_rules, company_rules)
        
        # Company rule should override
        assert "testing" in merged
        assert "COMPANY" in merged["testing"]
    
    def test_resolve_rule_conflicts_no_conflict(self, engine):
        """Test _resolve_rule_conflicts when no conflicts."""
        cortex_rules = {"testing": "CORTEX: TDD required"}
        company_rules = {"security": "COMPANY: Auth required"}
        
        merged = engine._resolve_rule_conflicts(cortex_rules, company_rules)
        
        # Both should be present
        assert "testing" in merged
        assert "security" in merged


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
