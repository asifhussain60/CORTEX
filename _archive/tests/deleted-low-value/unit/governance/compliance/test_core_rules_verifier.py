"""
Unit tests for CoreRulesVerifier (ENH-086 Stage 1).

Tests behavioral contracts for CORE rules compliance verification.
Covers 30 CORE rules (CORE-001 to CORE-051).

Authority: WAVE-K/ENH-086 - Architecture Alignment Verification
TDD Cycle: RED Phase
"""

import pytest
from pathlib import Path
from typing import List, Dict
from unittest.mock import Mock, patch, MagicMock

# AC_START: AC-WAVEK-001
# Description: ENH-086 Stage 1 - CORE Rules Verifier behavioral contracts
# Authority: cortex-registry/_cortex-master/index.yaml (WAVE-K)


class TestCoreRulesVerifier:
    """Test suite for CoreRulesVerifier (30 CORE rules)."""
    
    def test_verify_all_rules_returns_compliance_report(self):
        """CORE rules verifier returns structured compliance report."""
        # Behavioral contract: verify_all_rules() → ComplianceReport
        # Expected: {rule_id: bool, violations: List[str], score: float}
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        
        verifier = CoreRulesVerifier()
        report = verifier.verify_all_rules(target_path=Path("cortex/"))
        
        assert isinstance(report, dict)
        assert "rules_checked" in report
        assert "total_violations" in report
        assert "compliance_score" in report
        assert report["rules_checked"] == 15  # 15 rules implemented
    
    def test_verify_core_002_no_markdown_generation(self):
        """CORE-002: No markdown file generation in code."""
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        
        verifier = CoreRulesVerifier()
        violations = verifier.check_rule_002(target_path=Path("cortex/"))
        
        # Should detect: create_file("*.md"), cat > *.md, etc.
        assert isinstance(violations, list)
        # Empty list = compliant, non-empty = violations found
    
    def test_verify_core_008_tdd_mandatory(self):
        """CORE-008: Tests BEFORE code (TDD enforcement)."""
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        
        verifier = CoreRulesVerifier()
        violations = verifier.check_rule_008(target_path=Path("cortex/"))
        
        # Should detect: functions without test coverage, --ignore flags, _skip_ renames
        assert isinstance(violations, list)
    
    def test_verify_core_011_type_hints_mandatory(self):
        """CORE-011: Type hints required for all functions."""
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        
        verifier = CoreRulesVerifier()
        violations = verifier.check_rule_011(target_path=Path("cortex/"))
        
        # Should detect: def foo(a, b): without type hints
        assert isinstance(violations, list)
    
    def test_verify_core_029_response_header_mandatory(self):
        """CORE-029: Response header required in MCP tools."""
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        
        verifier = CoreRulesVerifier()
        violations = verifier.check_rule_029(target_path=Path("cortex/mcp/"))
        
        # Should detect: missing "## 🧠 CORTEX {operation}" headers
        assert isinstance(violations, list)
    
    def test_verify_core_035_single_canonical_implementation(self):
        """CORE-035: Single canonical implementation (no duplicates)."""
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        
        verifier = CoreRulesVerifier()
        violations = verifier.check_rule_035(target_path=Path("cortex/"))
        
        # Should detect: duplicate code blocks, copy-paste violations
        assert isinstance(violations, list)
    
    def test_verify_core_049_mcp_first_enforcement(self):
        """CORE-049: MCP-FIRST architecture (no direct file ops)."""
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        
        verifier = CoreRulesVerifier()
        violations = verifier.check_rule_049(target_path=Path("cortex/"))
        
        # Should detect: open(), write(), direct file creation bypassing MCP
        assert isinstance(violations, list)
    
    def test_batch_rule_verification_performance(self):
        """Batch verification completes in <5 seconds for 15 rules."""
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        import time
        
        verifier = CoreRulesVerifier()
        start = time.time()
        report = verifier.verify_all_rules(target_path=Path("cortex/orchestrators/"))
        elapsed = time.time() - start
        
        assert elapsed < 5.0  # Performance requirement
        assert report["rules_checked"] == 15
    
    def test_rule_severity_classification(self):
        """Rules classified by severity: P0-CRITICAL, P1-HIGH, P2-MEDIUM."""
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        
        verifier = CoreRulesVerifier()
        severity_map = verifier.get_rule_severity_map()
        
        assert severity_map["CORE-002"] == "P0-CRITICAL"
        assert severity_map["CORE-008"] == "P0-CRITICAL"
        assert severity_map["CORE-049"] == "P0-CRITICAL"
        assert len(severity_map) == 15  # 15 rules classified
    
    def test_compliance_score_calculation(self):
        """Compliance score = (rules_passed / total_rules) * 100."""
        from cortex.governance.core_rules_verifier import CoreRulesVerifier
        
        verifier = CoreRulesVerifier()
        report = verifier.verify_all_rules(target_path=Path("cortex/"))
        
        assert 0 <= report["compliance_score"] <= 100
        assert isinstance(report["compliance_score"], float)


# AC_COMPLETE: AC-WAVEK-001 ✅ 10/10 behavioral tests (RED phase)
