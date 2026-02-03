#!/usr/bin/env python3
"""
Phase 20.5 Component 5 Validation Script

Validates Early Violation Prevention at Stage 2.
Direct Python execution bypassing pytest.

Authority: AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5 Component #5)
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


def test_no_violations_continues_execution():
    """Test that execution continues when no violations detected."""
    print("Testing execution with no violations...")
    
    master = MasterOrchestrator()
    
    mock_engine = MagicMock()
    mock_router = MagicMock()
    
    request = {
        "operation": "IMPLEMENT",
        "description": "Add feature",
        "file_path": "/app/feature.py"
    }
    
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
    
    # No violations
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({}, [], [], {}),
        synthesis_result=SynthesisResult(
            merged_rules={},
            citations=["CORE-008"],
            violations=[],  # No violations
            guidance=["Write tests first"]
        ),
        intent_type="IMPLEMENT",
        file_path="/app/feature.py",
        timestamp=time.time()
    )
    
    mock_router.route_with_lens_auto_fetch.return_value = routing_result
    mock_engine.synthesize_unified_context.return_value = unified_context
    
    master.intent_router = mock_router
    master._synthesis_engine = mock_engine
    
    result = master._stage_2_routing(request)
    
    # Should NOT be blocked
    assert result["target_orchestrator"] == "TDDOrchestrator"
    assert result.get("status") != "BLOCKED"
    print("✅ Execution continues with no violations")


def test_non_critical_violations_continues_with_warning():
    """Test that non-critical violations generate warnings but continue."""
    print("Testing non-critical violations...")
    
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
    
    # Non-critical violations
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({}, [], [], {}),
        synthesis_result=SynthesisResult(
            merged_rules={},
            citations=[],
            violations=["Missing docstring", "Code formatting issue"],  # Non-critical
            guidance=[]
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
    
    # Should continue (not blocked)
    assert result["target_orchestrator"] == "TDDOrchestrator"
    assert result.get("status") != "BLOCKED"
    print("✅ Non-critical violations generate warnings only")


def test_critical_violations_blocks_execution():
    """Test that critical violations block execution."""
    print("Testing critical violation blocking...")
    
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
    
    # Critical violations
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({}, [], [], {}),
        synthesis_result=SynthesisResult(
            merged_rules={},
            citations=["CORE-008", "CORE-013"],
            violations=[
                "CORE-008 violation: No tests present",
                "CORE-013 violation: Bare except clause detected",
                "Security issue: SQL injection vulnerability"
            ],
            guidance=["Add tests before implementation", "Use specific exception handling"]
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
    
    # Should be BLOCKED
    assert result["target_orchestrator"] == "BLOCKED"
    assert result["status"] == "BLOCKED"
    assert "violations" in result
    assert "critical_violations" in result
    assert len(result["critical_violations"]) == 3  # All 3 are critical
    assert "error" in result
    print("✅ Critical violations block execution")


def test_violation_summary_formatting():
    """Test violation summary formatting."""
    print("Testing violation summary formatting...")
    
    master = MasterOrchestrator()
    
    critical_violations = [
        "CORE-008 violation: No tests",
        "Security issue: SQL injection"
    ]
    
    unified_context = UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence({}, {}, {}),
        company_knowledge=CompanyKnowledge({}, [], "OVERRIDE"),
        cortex_knowledge=CORTEXKnowledge({}, [], [], {}),
        synthesis_result=SynthesisResult(
            merged_rules={},
            citations=["CORE-008", "CORE-011"],
            violations=critical_violations,
            guidance=["Add tests", "Sanitize inputs"]
        ),
        intent_type="IMPLEMENT",
        file_path=None,
        timestamp=time.time()
    )
    
    summary = master._format_violation_summary(critical_violations, unified_context)
    
    assert "BLOCKED" in summary
    assert "CORE-008" in summary
    assert "SQL injection" in summary
    assert "Remediation Guidance" in summary
    assert "Add tests" in summary
    print("✅ Violation summary formatting working")


def test_critical_violation_filtering():
    """Test filtering of critical vs non-critical violations."""
    print("Testing critical violation filtering...")
    
    master = MasterOrchestrator()
    
    all_violations = [
        "CORE-008 violation: No tests",  # Critical
        "Missing docstring",  # Non-critical
        "Security issue detected",  # Critical
        "Code formatting issue",  # Non-critical
        "CORE-013 violation: Bare except",  # Critical
    ]
    
    critical = master._filter_critical_violations(all_violations)
    
    assert len(critical) == 3
    assert any("CORE-008" in v for v in critical)
    assert any("Security" in v for v in critical)
    assert any("CORE-013" in v for v in critical)
    assert not any("docstring" in v for v in critical)
    assert not any("formatting" in v for v in critical)
    print("✅ Critical violation filtering working")


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Phase 20.5 Component 5 Validation")
    print("Early Violation Prevention")
    print("=" * 60)
    print()
    
    tests = [
        test_no_violations_continues_execution,
        test_non_critical_violations_continues_with_warning,
        test_critical_violations_blocks_execution,
        test_violation_summary_formatting,
        test_critical_violation_filtering,
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
