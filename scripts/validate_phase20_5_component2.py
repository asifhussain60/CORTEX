"""
Phase 20.5 Component 2 Validation Script

Validates KnowledgeSynthesisEngine enhancement for UnifiedIntelligenceContext.

Authority: AC-KNOWLEDGE-SYNTHESIS-001
"""

import os
import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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


def test_synthesize_unified_context_basic():
    """Test basic synthesize_unified_context functionality."""
    print("Testing synthesize_unified_context basic...")
    
    engine = KnowledgeSynthesisEngine()
    
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
    
    context = engine.synthesize_unified_context(
        intent_type="IMPLEMENT",
        lens_intelligence=lens,
        company_knowledge=company,
        file_path="/test/file.py"
    )
    
    assert isinstance(context, UnifiedIntelligenceContext)
    assert context.intent_type == "IMPLEMENT"
    assert context.file_path == "/test/file.py"
    assert context.lens_intelligence == lens
    assert context.company_knowledge == company
    print("✅ Basic synthesis working")


def test_loads_cortex_knowledge():
    """Test that CORTEX knowledge is loaded."""
    print("\nTesting CORTEX knowledge loading...")
    
    engine = KnowledgeSynthesisEngine()
    
    lens = LENSIntelligence({}, {}, {})
    company = CompanyKnowledge({}, [], "OVERRIDE")
    
    context = engine.synthesize_unified_context(
        intent_type="IMPLEMENT",
        lens_intelligence=lens,
        company_knowledge=company,
        file_path="/test/file.py"
    )
    
    assert isinstance(context.cortex_knowledge, CORTEXKnowledge)
    assert len(context.cortex_knowledge.best_practices) > 0
    assert "CORE-008" in context.cortex_knowledge.best_practices
    assert "CORE-011" in context.cortex_knowledge.best_practices
    assert len(context.cortex_knowledge.applicable_patterns) > 0
    print("✅ CORTEX knowledge loaded successfully")


def test_synthesis_result_generation():
    """Test that synthesis result is generated."""
    print("\nTesting synthesis result generation...")
    
    engine = KnowledgeSynthesisEngine()
    
    lens = LENSIntelligence(
        git_analysis={},
        ast_analysis={"complexity": 25},  # High complexity
        comment_analysis={"fixmes": 7}  # Many FIXMEs
    )
    
    company = CompanyKnowledge({}, [], "OVERRIDE")
    
    context = engine.synthesize_unified_context(
        intent_type="IMPLEMENT",
        lens_intelligence=lens,
        company_knowledge=company,
        file_path="/test/file.py"
    )
    
    assert isinstance(context.synthesis_result, SynthesisResult)
    assert isinstance(context.synthesis_result.merged_rules, dict)
    assert isinstance(context.synthesis_result.citations, list)
    assert isinstance(context.synthesis_result.violations, list)
    assert isinstance(context.synthesis_result.guidance, list)
    
    # Should have citations
    assert len(context.synthesis_result.citations) > 0
    
    # Should detect violations (high complexity, many FIXMEs)
    assert len(context.synthesis_result.violations) > 0
    
    # Should have guidance
    assert len(context.synthesis_result.guidance) > 0
    
    print("✅ Synthesis result generation working")


def test_company_override_precedence():
    """Test that company rules override CORTEX rules."""
    print("\nTesting company override precedence...")
    
    engine = KnowledgeSynthesisEngine()
    
    lens = LENSIntelligence({}, {}, {})
    company = CompanyKnowledge(
        domain_rules={"testing": "COMPANY: Manual testing required"},
        compliance_standards=[],
        precedence="OVERRIDE"
    )
    
    context = engine.synthesize_unified_context(
        intent_type="IMPLEMENT",
        lens_intelligence=lens,
        company_knowledge=company,
        file_path="/test/file.py"
    )
    
    # Company rule should be in merged rules
    merged_rules = context.synthesis_result.merged_rules
    assert "testing" in merged_rules
    assert "COMPANY" in merged_rules["testing"]
    
    print("✅ Company override precedence working")


def test_graceful_degradation_no_lens():
    """Test graceful degradation without LENS intelligence."""
    print("\nTesting graceful degradation (no LENS)...")
    
    engine = KnowledgeSynthesisEngine()
    
    company = CompanyKnowledge({}, [], "OVERRIDE")
    
    context = engine.synthesize_unified_context(
        intent_type="IMPLEMENT",
        lens_intelligence=None,  # No LENS
        company_knowledge=company,
        file_path="/test/file.py"
    )
    
    assert isinstance(context, UnifiedIntelligenceContext)
    assert len(context.lens_intelligence.git_analysis) == 0
    assert len(context.cortex_knowledge.best_practices) > 0
    
    print("✅ Graceful degradation (no LENS) working")


def test_graceful_degradation_no_company():
    """Test graceful degradation without company knowledge."""
    print("\nTesting graceful degradation (no company)...")
    
    engine = KnowledgeSynthesisEngine()
    
    lens = LENSIntelligence({}, {}, {})
    
    context = engine.synthesize_unified_context(
        intent_type="IMPLEMENT",
        lens_intelligence=lens,
        company_knowledge=None,  # No company
        file_path="/test/file.py"
    )
    
    assert isinstance(context, UnifiedIntelligenceContext)
    assert len(context.company_knowledge.domain_rules) == 0
    assert len(context.cortex_knowledge.best_practices) > 0
    
    print("✅ Graceful degradation (no company) working")


def test_intent_specific_patterns():
    """Test that intent-specific patterns are loaded."""
    print("\nTesting intent-specific patterns...")
    
    engine = KnowledgeSynthesisEngine()
    
    lens = LENSIntelligence({}, {}, {})
    company = CompanyKnowledge({}, [], "OVERRIDE")
    
    # Test IMPLEMENT intent
    context_implement = engine.synthesize_unified_context(
        intent_type="IMPLEMENT",
        lens_intelligence=lens,
        company_knowledge=company,
        file_path="/test/file.py"
    )
    
    patterns_implement = context_implement.cortex_knowledge.applicable_patterns
    assert "TDD Pattern" in patterns_implement
    
    # Test REFACTOR intent
    context_refactor = engine.synthesize_unified_context(
        intent_type="REFACTOR",
        lens_intelligence=lens,
        company_knowledge=company,
        file_path="/test/file.py"
    )
    
    patterns_refactor = context_refactor.cortex_knowledge.applicable_patterns
    assert "Extract Method" in patterns_refactor
    
    print("✅ Intent-specific patterns working")


def test_singleton_accessor():
    """Test get_synthesis_engine singleton accessor."""
    print("\nTesting singleton accessor...")
    
    engine1 = get_synthesis_engine()
    engine2 = get_synthesis_engine()
    
    assert engine1 is engine2
    assert isinstance(engine1, KnowledgeSynthesisEngine)
    
    print("✅ Singleton accessor working")


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Phase 20.5 Component 2 Validation")
    print("KnowledgeSynthesisEngine Enhancement")
    print("=" * 60)
    
    try:
        test_synthesize_unified_context_basic()
        test_loads_cortex_knowledge()
        test_synthesis_result_generation()
        test_company_override_precedence()
        test_graceful_degradation_no_lens()
        test_graceful_degradation_no_company()
        test_intent_specific_patterns()
        test_singleton_accessor()
        
        print("\n" + "=" * 60)
        print("✅ ALL PHASE 20.5 COMPONENT 2 TESTS PASSED")
        print("=" * 60)
        print("\nComponent 2 Status: ✅ COMPLETE")
        print("- synthesize_unified_context() method")
        print("- CORTEX best practices loading (10+ CORE rules)")
        print("- Company override precedence")
        print("- Violation detection")
        print("- Proactive guidance generation")
        print("- Intent-specific patterns")
        print("- Graceful degradation (fallback support)")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
