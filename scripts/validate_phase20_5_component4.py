#!/usr/bin/env python3
"""
Phase 20.5 Component 4 Validation Script

Validates IntentRouter smart citations enhancement.
Direct Python execution bypassing pytest.

Authority: AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5 Component #4)
"""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from unittest.mock import MagicMock, patch
from cortex.orchestrators.core.intent_router import IntentRouter
from cortex.brain.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
    LENSIntelligence,
    CompanyKnowledge,
    CORTEXKnowledge,
    SynthesisResult,
)


def test_route_without_unified_intelligence():
    """Test backward compatibility - routing without unified intelligence."""
    print("Testing backward compatibility (no unified intelligence)...")
    
    router = IntentRouter()
    
    request = {
        "intent": "IMPLEMENT",
        "description": "Add authentication feature",
        "file_path": "/app/auth.py"
    }
    
    # Mock route() to avoid actual routing logic
    with patch.object(router, 'route') as mock_route:
        mock_decision = MagicMock()
        mock_decision.intent_type.value = "IMPLEMENT"
        mock_decision.target_handler = "TDDOrchestrator"
        mock_decision.confidence_score = 0.9
        mock_decision.reasoning = "Implementation request detected"
        mock_route.return_value = mock_decision
        
        result = router.route_with_lens_auto_fetch(request)
        
        assert result["intent"] == "IMPLEMENT"
        assert result["target_orchestrator"] == "TDDOrchestrator"
        assert result["reasoning"] == "Implementation request detected"
        assert "cited_rules" not in result  # No citations without unified intelligence
        print("✅ Backward compatibility working")


def test_route_with_unified_intelligence_citations():
    """Test smart citations when unified intelligence provided."""
    print("Testing smart citations with unified intelligence...")
    
    router = IntentRouter()
    
    request = {
        "intent": "IMPLEMENT",
        "description": "Add authentication",
        "file_path": "/app/auth.py"
    }
    
    # Create unified intelligence with citations
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({}, [], [], {}),
        synthesis_result=SynthesisResult(
            merged_rules={
                "CORE-008": {"title": "TDD Required"},
                "CORE-011": {"title": "Type Hints"}
            },
            citations=["CORE-008", "CORE-011", "CORE-012"],
            violations=[],
            guidance=["Write tests first"]
        ),
        intent_type="IMPLEMENT",
        file_path="/app/auth.py",
        timestamp=time.time()
    )
    
    with patch.object(router, 'route') as mock_route:
        mock_decision = MagicMock()
        mock_decision.intent_type.value = "IMPLEMENT"
        mock_decision.target_handler = "TDDOrchestrator"
        mock_decision.confidence_score = 0.9
        mock_decision.reasoning = "Implementation request"
        mock_route.return_value = mock_decision
        
        result = router.route_with_lens_auto_fetch(request, unified_context)
        
        assert result["intent"] == "IMPLEMENT"
        assert "Cited:" in result["reasoning"]  # Citations added
        assert "cited_rules" in result
        assert len(result["cited_rules"]) > 0
        print("✅ Smart citations working")


def test_route_with_violations_warning():
    """Test violation warnings in reasoning."""
    print("Testing violation warnings...")
    
    router = IntentRouter()
    
    request = {"intent": "IMPLEMENT", "description": "Add feature"}
    
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({}, [], [], {}),
        synthesis_result=SynthesisResult(
            merged_rules={},
            citations=["CORE-008"],
            violations=["Missing tests", "No type hints"],
            guidance=[]
        ),
        intent_type="IMPLEMENT",
        file_path=None,
        timestamp=time.time()
    )
    
    with patch.object(router, 'route') as mock_route:
        mock_decision = MagicMock()
        mock_decision.intent_type.value = "IMPLEMENT"
        mock_decision.target_handler = "TDDOrchestrator"
        mock_decision.confidence_score = 0.9
        mock_decision.reasoning = "Implementation"
        mock_route.return_value = mock_decision
        
        result = router.route_with_lens_auto_fetch(request, unified_context)
        
        assert "⚠️" in result["reasoning"]  # Violation warning
        assert "2 violation(s)" in result["reasoning"]
        print("✅ Violation warnings working")


def test_intent_applicable_rules_filtering():
    """Test filtering rules by intent type."""
    print("Testing intent-specific rule filtering...")
    
    router = IntentRouter()
    
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({}, [], [], {}),
        synthesis_result=SynthesisResult(
            merged_rules={
                "CORE-008": {"title": "TDD Required"},
                "CORE-011": {"title": "Type Hints"},
                "CORE-013": {"title": "Exception Handling"}
            },
            citations=["CORE-008", "CORE-011", "CORE-013"],
            violations=[],
            guidance=[]
        ),
        intent_type="IMPLEMENT",
        file_path=None,
        timestamp=time.time()
    )
    
    # Test IMPLEMENT intent (should prioritize CORE-008, CORE-011)
    applicable = router._get_intent_applicable_rules(
        "IMPLEMENT",
        ["CORE-008", "CORE-011", "CORE-013"],
        unified_context
    )
    
    assert len(applicable) >= 2
    assert any("CORE-008" in rule for rule in applicable)
    assert any("CORE-011" in rule for rule in applicable)
    print("✅ Intent-specific rule filtering working")


def test_citation_failure_graceful_degradation():
    """Test graceful degradation if citation processing fails."""
    print("Testing citation failure handling...")
    
    router = IntentRouter()
    
    request = {"intent": "IMPLEMENT", "description": "Add feature"}
    
    # Create malformed unified intelligence that will cause AttributeError
    unified_context = MagicMock()
    unified_context.synthesis_result.citations.side_effect = AttributeError("Test error")
    
    with patch.object(router, 'route') as mock_route:
        mock_decision = MagicMock()
        mock_decision.intent_type.value = "IMPLEMENT"
        mock_decision.target_handler = "TDDOrchestrator"
        mock_decision.confidence_score = 0.9
        mock_decision.reasoning = "Implementation"
        mock_route.return_value = mock_decision
        
        # Should not raise exception
        result = router.route_with_lens_auto_fetch(request, unified_context)
        
        assert result["intent"] == "IMPLEMENT"
        assert result["target_orchestrator"] == "TDDOrchestrator"
        # Should have reasoning (even if citations failed)
        assert "reasoning" in result
        print("✅ Citation failure handling working")


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Phase 20.5 Component 4 Validation")
    print("IntentRouter Smart Citations")
    print("=" * 60)
    print()
    
    tests = [
        test_route_without_unified_intelligence,
        test_route_with_unified_intelligence_citations,
        test_route_with_violations_warning,
        test_intent_applicable_rules_filtering,
        test_citation_failure_graceful_degradation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"❌ {failed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
