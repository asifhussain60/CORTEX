#!/usr/bin/env python3
"""
Phase 20.5 Component 3 Validation Script

Validates MasterOrchestrator Stage 2 knowledge synthesis integration.
Direct Python execution bypassing pytest.

Authority: AC-KNOWLEDGE-SYNTHESIS-001
"""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from unittest.mock import MagicMock, patch
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.brain.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
    LENSIntelligence,
    CompanyKnowledge,
    CORTEXKnowledge,
    SynthesisResult,
)


def test_synthesis_invocation():
    """Test that _stage_2_routing() invokes synthesis engine."""
    print("Testing synthesis invocation...")
    
    master = MasterOrchestrator()
    
    # Mock dependencies
    mock_engine = MagicMock()
    mock_router = MagicMock()
    
    # Sample data
    request = {
        "operation": "IMPLEMENT",
        "description": "Add auth",
        "file_path": "/app/auth.py",
        "company_name": "AcmeCorp"
    }
    
    routing_result = {
        "intent": "IMPLEMENT",
        "target_orchestrator": "TDDOrchestrator",
        "confidence_score": 0.9,
        "reasoning": "Implementation detected",
        "context": {
            "lens_insights": {
                "git_analysis": {"commits": 42},
                "ast_analysis": {"complexity": 5},
                "comment_analysis": {"coverage": 0.8},
                "company_knowledge": {
                    "domain_rules": {},
                    "compliance_standards": []
                }
            }
        }
    }
    
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence(
            git_analysis={"commits": 42},
            ast_analysis={"complexity": 5},
            comment_analysis={"coverage": 0.8}
        ),
        company_knowledge=CompanyKnowledge(
            domain_rules={},
            compliance_standards=[],
            precedence="OVERRIDE"
        ),
        cortex_knowledge=CORTEXKnowledge(
            best_practices={"CORE-008": {"title": "TDD"}},
            applicable_patterns=[],
            anti_patterns=[],
            synthesis_metadata={}
        ),
        synthesis_result=SynthesisResult(
            merged_rules={"CORE-008": {"title": "TDD"}},
            citations=["CORE-008"],
            violations=[],
            guidance=["Write tests first"]
        ),
        intent_type="IMPLEMENT",
        file_path="/app/auth.py",
        timestamp=time.time()
    )
    
    mock_router.route_with_lens_auto_fetch.return_value = routing_result
    mock_engine.synthesize_unified_context.return_value = unified_context
    
    master.intent_router = mock_router
    master._synthesis_engine = mock_engine
    
    # Execute
    result = master._stage_2_routing(request)
    
    # Verify
    assert mock_engine.synthesize_unified_context.called, "Synthesis not invoked"
    assert "unified_intelligence" in result, "Unified intelligence missing"
    assert "cited_rules" in result, "Cited rules missing"
    print("✅ Synthesis invocation working")


def test_unified_intelligence_attachment():
    """Test that unified intelligence is attached to result."""
    print("Testing unified intelligence attachment...")
    
    master = MasterOrchestrator()
    
    mock_engine = MagicMock()
    mock_router = MagicMock()
    
    request = {"operation": "IMPLEMENT", "description": "Add feature"}
    
    routing_result = {
        "intent": "IMPLEMENT",
        "target_orchestrator": "TDDOrchestrator",
        "confidence_score": 0.9,
        "reasoning": "Implementation",
        "context": {"lens_insights": {
            "git_analysis": {},
            "ast_analysis": {},
            "comment_analysis": {},
            "company_knowledge": {"domain_rules": {}, "compliance_standards": []}
        }}
    }
    
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({"CORE-008": {}}, [], [], {}),
        synthesis_result=SynthesisResult(
            merged_rules={},
            citations=["CORE-008", "CORE-011"],
            violations=[],
            guidance=["Test first"]
        ),
        intent_type="IMPLEMENT",
        file_path=None,
        timestamp=time.time()
    )
    
    mock_router.route_with_lens_auto_fetch.return_value = routing_result
    mock_engine.synthesize_unified_context.return_value = unified_context
    
    master.intent_router = mock_router
    master._synthesis_engine = mock_engine
    
    result = master._stage_2_routing(request)
    
    assert "unified_intelligence" in result
    assert result["cited_rules"] == ["CORE-008", "CORE-011"]
    assert result["violations"] == []
    assert result["guidance"] == ["Test first"]
    print("✅ Unified intelligence attachment working")


def test_synthesis_failure_graceful_degradation():
    """Test graceful degradation if synthesis fails."""
    print("Testing synthesis failure handling...")
    
    master = MasterOrchestrator()
    
    mock_engine = MagicMock()
    mock_router = MagicMock()
    
    request = {"operation": "IMPLEMENT", "description": "Add feature"}
    
    routing_result = {
        "intent": "IMPLEMENT",
        "target_orchestrator": "TDDOrchestrator",
        "confidence_score": 0.9,
        "reasoning": "Implementation",
        "context": {}
    }
    
    mock_router.route_with_lens_auto_fetch.return_value = routing_result
    mock_engine.synthesize_unified_context.side_effect = Exception("Synthesis error")
    
    master.intent_router = mock_router
    master._synthesis_engine = mock_engine
    
    # Should not raise
    result = master._stage_2_routing(request)
    
    assert result["intent"] == "IMPLEMENT"
    assert result["target_orchestrator"] == "TDDOrchestrator"
    print("✅ Graceful degradation working")


def test_no_lens_insights():
    """Test synthesis with no LENS insights."""
    print("Testing no LENS insights handling...")
    
    master = MasterOrchestrator()
    
    mock_engine = MagicMock()
    mock_router = MagicMock()
    
    request = {"operation": "IMPLEMENT", "description": "Add feature"}
    
    # No lens_insights in context
    routing_result = {
        "intent": "IMPLEMENT",
        "target_orchestrator": "TDDOrchestrator",
        "confidence_score": 0.9,
        "reasoning": "Implementation",
        "context": {}
    }
    
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({}, [], [], {}),
        synthesis_result=SynthesisResult({}, [], [], []),
        intent_type="IMPLEMENT",
        file_path=None,
        timestamp=time.time()
    )
    
    mock_router.route_with_lens_auto_fetch.return_value = routing_result
    mock_engine.synthesize_unified_context.return_value = unified_context
    
    master.intent_router = mock_router
    master._synthesis_engine = mock_engine
    
    result = master._stage_2_routing(request)
    
    # Should still call synthesis (with empty LENS)
    assert mock_engine.synthesize_unified_context.called
    print("✅ No LENS insights handling working")


def test_intent_router_result_preservation():
    """Test that IntentRouter result is preserved."""
    print("Testing IntentRouter result preservation...")
    
    master = MasterOrchestrator()
    
    mock_engine = MagicMock()
    mock_router = MagicMock()
    
    request = {"operation": "IMPLEMENT", "description": "Add feature"}
    
    routing_result = {
        "intent": "IMPLEMENT",
        "target_orchestrator": "TDDOrchestrator",
        "confidence_score": 0.9,
        "reasoning": "Implementation detected",
        "context": {"lens_insights": {
            "git_analysis": {},
            "ast_analysis": {},
            "comment_analysis": {},
            "company_knowledge": {"domain_rules": {}, "compliance_standards": []}
        }}
    }
    
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({}, [], [], {}),
        synthesis_result=SynthesisResult({}, [], [], []),
        intent_type="IMPLEMENT",
        file_path=None,
        timestamp=time.time()
    )
    
    mock_router.route_with_lens_auto_fetch.return_value = routing_result
    mock_engine.synthesize_unified_context.return_value = unified_context
    
    master.intent_router = mock_router
    master._synthesis_engine = mock_engine
    
    result = master._stage_2_routing(request)
    
    # Original fields preserved
    assert result["intent"] == "IMPLEMENT"
    assert result["target_orchestrator"] == "TDDOrchestrator"
    assert result["confidence_score"] == 0.9
    assert result["reasoning"] == "Implementation detected"
    # Enhanced with synthesis
    assert "unified_intelligence" in result
    print("✅ IntentRouter result preservation working")


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Phase 20.5 Component 3 Validation")
    print("MasterOrchestrator Stage 2 Knowledge Synthesis Integration")
    print("=" * 60)
    print()
    
    tests = [
        test_synthesis_invocation,
        test_unified_intelligence_attachment,
        test_synthesis_failure_graceful_degradation,
        test_no_lens_insights,
        test_intent_router_result_preservation,
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
