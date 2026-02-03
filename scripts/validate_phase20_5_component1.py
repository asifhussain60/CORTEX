"""
Phase 20.5 Component 1 Validation Script

Validates UnifiedIntelligenceContext implementation without pytest-asyncio.

Authority: AC-KNOWLEDGE-SYNTHESIS-001
"""

import os
import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cortex.brain.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
    LENSIntelligence,
    CompanyKnowledge,
    CORTEXKnowledge,
    SynthesisResult,
)


def test_lens_intelligence():
    """Test LENSIntelligence dataclass."""
    print("Testing LENSIntelligence...")
    
    lens = LENSIntelligence(
        git_analysis={"commits": 42, "hotspots": ["src/main.py"]},
        ast_analysis={"complexity": 15, "functions": 8},
        comment_analysis={"todos": 3, "fixmes": 1}
    )
    
    assert lens.git_analysis["commits"] == 42
    assert lens.ast_analysis["complexity"] == 15
    assert lens.comment_analysis["todos"] == 3
    print("✅ LENSIntelligence working")


def test_company_knowledge():
    """Test CompanyKnowledge dataclass."""
    print("\nTesting CompanyKnowledge...")
    
    company = CompanyKnowledge(
        domain_rules={"payment": "PCI-DSS required"},
        compliance_standards=["PCI-DSS", "HIPAA"],
        precedence="OVERRIDE"
    )
    
    assert company.domain_rules["payment"] == "PCI-DSS required"
    assert "PCI-DSS" in company.compliance_standards
    assert company.precedence == "OVERRIDE"
    print("✅ CompanyKnowledge working")


def test_cortex_knowledge():
    """Test CORTEXKnowledge dataclass."""
    print("\nTesting CORTEXKnowledge...")
    
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
    print("✅ CORTEXKnowledge working")


def test_synthesis_result():
    """Test SynthesisResult dataclass."""
    print("\nTesting SynthesisResult...")
    
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
    print("✅ SynthesisResult working")


def test_unified_context_creation():
    """Test UnifiedIntelligenceContext creation."""
    print("\nTesting UnifiedIntelligenceContext creation...")
    
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
    print("✅ UnifiedIntelligenceContext creation working")


def test_unified_context_to_dict():
    """Test UnifiedIntelligenceContext.to_dict() method."""
    print("\nTesting UnifiedIntelligenceContext.to_dict()...")
    
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
    print("✅ to_dict() working")


def test_unified_context_has_violations():
    """Test UnifiedIntelligenceContext.has_violations() method."""
    print("\nTesting UnifiedIntelligenceContext.has_violations()...")
    
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
    print("✅ has_violations() working")


def test_unified_context_get_cited_rules():
    """Test UnifiedIntelligenceContext.get_cited_rules() method."""
    print("\nTesting UnifiedIntelligenceContext.get_cited_rules()...")
    
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
    print("✅ get_cited_rules() working")


def test_unified_context_create_empty():
    """Test UnifiedIntelligenceContext.create_empty() factory method."""
    print("\nTesting UnifiedIntelligenceContext.create_empty()...")
    
    context = UnifiedIntelligenceContext.create_empty(
        intent_type="ANALYZE",
        file_path="/test/file.py"
    )
    
    assert context.intent_type == "ANALYZE"
    assert context.file_path == "/test/file.py"
    assert len(context.lens_intelligence.git_analysis) == 0
    assert len(context.company_knowledge.domain_rules) == 0
    assert len(context.cortex_knowledge.best_practices) == 0
    assert len(context.synthesis_result.merged_rules) == 0
    assert context.has_violations() is False
    print("✅ create_empty() working")


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Phase 20.5 Component 1 Validation")
    print("UnifiedIntelligenceContext Implementation")
    print("=" * 60)
    
    try:
        test_lens_intelligence()
        test_company_knowledge()
        test_cortex_knowledge()
        test_synthesis_result()
        test_unified_context_creation()
        test_unified_context_to_dict()
        test_unified_context_has_violations()
        test_unified_context_get_cited_rules()
        test_unified_context_create_empty()
        
        print("\n" + "=" * 60)
        print("✅ ALL PHASE 20.5 COMPONENT 1 TESTS PASSED")
        print("=" * 60)
        print("\nComponent 1 Status: ✅ COMPLETE")
        print("- UnifiedIntelligenceContext dataclass")
        print("- LENSIntelligence dataclass")
        print("- CompanyKnowledge dataclass")
        print("- CORTEXKnowledge dataclass")
        print("- SynthesisResult dataclass")
        print("- Helper methods (to_dict, has_violations, etc.)")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
