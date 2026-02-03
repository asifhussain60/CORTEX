"""
Tests for UnifiedIntelligenceContext (Phase 20.5 Component #1).

Authority: AC-KNOWLEDGE-SYNTHESIS-001
Rule: CORE-008 (TDD First)
"""

import pytest
import time
from typing import Dict, Any, Optional

from cortex.brain.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
    LENSIntelligence,
    CompanyKnowledge,
    CORTEXKnowledge,
    SynthesisResult,
)


class TestLENSIntelligence:
    """Test LENSIntelligence dataclass."""
    
    def test_lens_intelligence_creation(self):
        """Test LENSIntelligence can be created."""
        lens = LENSIntelligence(
            git_analysis={"commits": 42, "hotspots": ["src/main.py"]},
            ast_analysis={"complexity": 15, "functions": 8},
            comment_analysis={"todos": 3, "fixmes": 1}
        )
        
        assert lens.git_analysis["commits"] == 42
        assert lens.ast_analysis["complexity"] == 15
        assert lens.comment_analysis["todos"] == 3
    
    def test_lens_intelligence_empty(self):
        """Test LENSIntelligence with empty dicts."""
        lens = LENSIntelligence(
            git_analysis={},
            ast_analysis={},
            comment_analysis={}
        )
        
        assert lens.git_analysis == {}
        assert lens.ast_analysis == {}
        assert lens.comment_analysis == {}


class TestCompanyKnowledge:
    """Test CompanyKnowledge dataclass."""
    
    def test_company_knowledge_creation(self):
        """Test CompanyKnowledge can be created."""
        company = CompanyKnowledge(
            domain_rules={"payment": "PCI-DSS required"},
            compliance_standards=["PCI-DSS", "HIPAA"],
            precedence="OVERRIDE"
        )
        
        assert company.domain_rules["payment"] == "PCI-DSS required"
        assert "PCI-DSS" in company.compliance_standards
        assert company.precedence == "OVERRIDE"
    
    def test_company_knowledge_no_compliance(self):
        """Test CompanyKnowledge without compliance standards."""
        company = CompanyKnowledge(
            domain_rules={"auth": "OAuth2 required"},
            compliance_standards=[],
            precedence="OVERRIDE"
        )
        
        assert len(company.compliance_standards) == 0


class TestCORTEXKnowledge:
    """Test CORTEXKnowledge dataclass."""
    
    def test_cortex_knowledge_creation(self):
        """Test CORTEXKnowledge can be created."""
        cortex = CORTEXKnowledge(
            best_practices={"CORE-008": "TDD first", "CORE-011": "Type hints"},
            applicable_patterns=["Repository Pattern", "Factory Pattern"],
            anti_patterns=["God Object", "Spaghetti Code"],
            synthesis_metadata={"rules_loaded": 45, "rules_applied": 12}
        )
        
        assert cortex.best_practices["CORE-008"] == "TDD first"
        assert len(cortex.applicable_patterns) == 2
        assert len(cortex.anti_patterns) == 2
        assert cortex.synthesis_metadata["rules_loaded"] == 45
    
    def test_cortex_knowledge_minimal(self):
        """Test CORTEXKnowledge with minimal data."""
        cortex = CORTEXKnowledge(
            best_practices={},
            applicable_patterns=[],
            anti_patterns=[],
            synthesis_metadata={}
        )
        
        assert len(cortex.best_practices) == 0
        assert len(cortex.applicable_patterns) == 0


class TestSynthesisResult:
    """Test SynthesisResult dataclass."""
    
    def test_synthesis_result_creation(self):
        """Test SynthesisResult can be created."""
        result = SynthesisResult(
            merged_rules={"CORE-008": "TDD first", "COMPANY-001": "Auth required"},
            citations=["CORE-008", "CORE-011", "COMPANY-001"],
            violations=["CORE-013: Bare except found"],
            guidance=["Use pytest for TDD", "Add type hints to functions"]
        )
        
        assert len(result.merged_rules) == 2
        assert len(result.citations) == 3
        assert len(result.violations) == 1
        assert len(result.guidance) == 2
    
    def test_synthesis_result_no_violations(self):
        """Test SynthesisResult without violations."""
        result = SynthesisResult(
            merged_rules={"CORE-008": "TDD first"},
            citations=["CORE-008"],
            violations=[],
            guidance=["Continue with TDD approach"]
        )
        
        assert len(result.violations) == 0
        assert len(result.guidance) == 1


class TestUnifiedIntelligenceContext:
    """Test UnifiedIntelligenceContext main class."""
    
    def test_unified_context_creation(self):
        """Test UnifiedIntelligenceContext can be created."""
        lens = LENSIntelligence(
            git_analysis={"commits": 42},
            ast_analysis={"complexity": 15},
            comment_analysis={"todos": 3}
        )
        
        company = CompanyKnowledge(
            domain_rules={"payment": "PCI-DSS required"},
            compliance_standards=["PCI-DSS"],
            precedence="OVERRIDE"
        )
        
        cortex = CORTEXKnowledge(
            best_practices={"CORE-008": "TDD first"},
            applicable_patterns=["Repository Pattern"],
            anti_patterns=["God Object"],
            synthesis_metadata={"rules_loaded": 45}
        )
        
        synthesis = SynthesisResult(
            merged_rules={"CORE-008": "TDD first"},
            citations=["CORE-008"],
            violations=[],
            guidance=["Use pytest"]
        )
        
        context = UnifiedIntelligenceContext(
            lens_intelligence=lens,
            company_knowledge=company,
            cortex_knowledge=cortex,
            synthesis_result=synthesis,
            intent_type="IMPLEMENT",
            file_path="/test/file.py",
            timestamp=time.time()
        )
        
        assert context.intent_type == "IMPLEMENT"
        assert context.file_path == "/test/file.py"
        assert context.lens_intelligence.git_analysis["commits"] == 42
        assert context.company_knowledge.precedence == "OVERRIDE"
        assert context.cortex_knowledge.best_practices["CORE-008"] == "TDD first"
        assert len(context.synthesis_result.citations) == 1
    
    def test_unified_context_optional_file_path(self):
        """Test UnifiedIntelligenceContext with optional file_path."""
        lens = LENSIntelligence({}, {}, {})
        company = CompanyKnowledge({}, [], "OVERRIDE")
        cortex = CORTEXKnowledge({}, [], [], {})
        synthesis = SynthesisResult({}, [], [], [])
        
        context = UnifiedIntelligenceContext(
            lens_intelligence=lens,
            company_knowledge=company,
            cortex_knowledge=cortex,
            synthesis_result=synthesis,
            intent_type="ANALYZE",
            file_path=None,
            timestamp=time.time()
        )
        
        assert context.file_path is None
        assert context.intent_type == "ANALYZE"
    
    def test_unified_context_to_dict(self):
        """Test UnifiedIntelligenceContext.to_dict() method."""
        lens = LENSIntelligence(
            git_analysis={"commits": 42},
            ast_analysis={"complexity": 15},
            comment_analysis={"todos": 3}
        )
        
        company = CompanyKnowledge(
            domain_rules={"payment": "PCI-DSS required"},
            compliance_standards=["PCI-DSS"],
            precedence="OVERRIDE"
        )
        
        cortex = CORTEXKnowledge(
            best_practices={"CORE-008": "TDD first"},
            applicable_patterns=["Repository Pattern"],
            anti_patterns=["God Object"],
            synthesis_metadata={"rules_loaded": 45}
        )
        
        synthesis = SynthesisResult(
            merged_rules={"CORE-008": "TDD first"},
            citations=["CORE-008"],
            violations=[],
            guidance=["Use pytest"]
        )
        
        context = UnifiedIntelligenceContext(
            lens_intelligence=lens,
            company_knowledge=company,
            cortex_knowledge=cortex,
            synthesis_result=synthesis,
            intent_type="IMPLEMENT",
            file_path="/test/file.py",
            timestamp=time.time()
        )
        
        result = context.to_dict()
        
        assert result["intent_type"] == "IMPLEMENT"
        assert result["file_path"] == "/test/file.py"
        assert result["lens_intelligence"]["git_analysis"]["commits"] == 42
        assert result["company_knowledge"]["precedence"] == "OVERRIDE"
        assert result["cortex_knowledge"]["best_practices"]["CORE-008"] == "TDD first"
        assert len(result["synthesis_result"]["citations"]) == 1
    
    def test_unified_context_has_violations(self):
        """Test UnifiedIntelligenceContext.has_violations() method."""
        lens = LENSIntelligence({}, {}, {})
        company = CompanyKnowledge({}, [], "OVERRIDE")
        cortex = CORTEXKnowledge({}, [], [], {})
        
        # With violations
        synthesis_with_violations = SynthesisResult(
            merged_rules={},
            citations=[],
            violations=["CORE-013: Bare except found"],
            guidance=[]
        )
        
        context_with_violations = UnifiedIntelligenceContext(
            lens_intelligence=lens,
            company_knowledge=company,
            cortex_knowledge=cortex,
            synthesis_result=synthesis_with_violations,
            intent_type="IMPLEMENT",
            file_path=None,
            timestamp=time.time()
        )
        
        assert context_with_violations.has_violations() is True
        
        # Without violations
        synthesis_no_violations = SynthesisResult(
            merged_rules={},
            citations=[],
            violations=[],
            guidance=[]
        )
        
        context_no_violations = UnifiedIntelligenceContext(
            lens_intelligence=lens,
            company_knowledge=company,
            cortex_knowledge=cortex,
            synthesis_result=synthesis_no_violations,
            intent_type="IMPLEMENT",
            file_path=None,
            timestamp=time.time()
        )
        
        assert context_no_violations.has_violations() is False
    
    def test_unified_context_get_cited_rules(self):
        """Test UnifiedIntelligenceContext.get_cited_rules() method."""
        lens = LENSIntelligence({}, {}, {})
        company = CompanyKnowledge({}, [], "OVERRIDE")
        cortex = CORTEXKnowledge({}, [], [], {})
        synthesis = SynthesisResult(
            merged_rules={},
            citations=["CORE-008", "CORE-011", "COMPANY-001"],
            violations=[],
            guidance=[]
        )
        
        context = UnifiedIntelligenceContext(
            lens_intelligence=lens,
            company_knowledge=company,
            cortex_knowledge=cortex,
            synthesis_result=synthesis,
            intent_type="IMPLEMENT",
            file_path=None,
            timestamp=time.time()
        )
        
        cited_rules = context.get_cited_rules()
        
        assert len(cited_rules) == 3
        assert "CORE-008" in cited_rules
        assert "CORE-011" in cited_rules
        assert "COMPANY-001" in cited_rules


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
