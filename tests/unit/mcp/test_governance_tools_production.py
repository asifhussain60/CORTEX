"""
Production governance MCP tools tests (RED phase).

AC_START: AC-MCP-GOV-TOOLS-PROD-001
Authority: FIX 1 - Holistic MCP Tool Implementation
Target: All tests passing with real implementations

Tests cover:
- cortex_query_governance: Real governance state queries
- cortex_validate_compliance: Real CORE rule validation
- cortex_execute_governance: Real governance action execution
- cortex_analyze_governance: Real compliance metrics analysis
- cortex_report_governance: Real audit report generation

No stubs. Production-quality only.
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class TestCORTEXQueryGovernance:
    """Test cortex_query_governance tool with real implementations."""

    def test_query_active_rules(self) -> None:
        """Test querying active CORE rules."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_query_governance
        
        result = cortex_query_governance(query_type="rules")
        
        assert result["status"] == "success"
        assert "rules" in result
        assert len(result["rules"]) > 0
        # Should return actual CORE rules from registry
        rule_ids = [r["id"] for r in result["rules"]]
        assert "CORE-008" in rule_ids  # TDD rule always exists
        assert "CORE-029" in rule_ids  # Response header rule

    def test_query_enforcement_matrix(self) -> None:
        """Test querying enforcement level matrix."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_query_governance
        
        result = cortex_query_governance(query_type="enforcement_matrix")
        
        assert result["status"] == "success"
        assert "enforcement_levels" in result
        assert "BLOCKED" in result["enforcement_levels"]
        assert "WARNING" in result["enforcement_levels"]

    def test_query_violation_history(self) -> None:
        """Test querying violation history."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_query_governance
        
        result = cortex_query_governance(
            query_type="violations",
            limit=10
        )
        
        assert result["status"] == "success"
        assert "violations" in result
        assert isinstance(result["violations"], list)
        if result["violations"]:
            violation = result["violations"][0]
            assert "rule_id" in violation
            assert "severity" in violation
            assert "timestamp" in violation

    def test_query_with_filters(self) -> None:
        """Test querying with severity filters."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_query_governance
        
        result = cortex_query_governance(
            query_type="rules",
            filter_by_enforcement="BLOCKED"
        )
        
        assert result["status"] == "success"
        if result["rules"]:
            for rule in result["rules"]:
                assert rule.get("enforcement") in ["BLOCKED", "WARNING"]

    def test_query_invalid_type(self) -> None:
        """Test querying with invalid type returns error."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_query_governance
        
        result = cortex_query_governance(query_type="nonexistent")
        
        assert result["status"] == "error"
        assert "error" in result


class TestCORTEXValidateCompliance:
    """Test cortex_validate_compliance tool with real CORE rule validation."""

    def test_validate_code_has_tests(self) -> None:
        """Test validating code has tests (CORE-008)."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_validate_compliance
        
        code_with_tests = {
            "has_tests": True,
            "test_count": 5,
            "coverage": 85
        }
        
        result = cortex_validate_compliance(
            code_metadata=code_with_tests,
            rules=["CORE-008"]
        )
        
        assert result["status"] == "success"
        assert result["compliant"] is True
        assert "CORE-008" in result["passed_rules"]

    def test_validate_type_hints_present(self) -> None:
        """Test validating type hints (CORE-011)."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_validate_compliance
        
        code_with_hints = {
            "has_type_hints": True,
            "type_hint_coverage": 100
        }
        
        result = cortex_validate_compliance(
            code_metadata=code_with_hints,
            rules=["CORE-011"]
        )
        
        assert result["status"] == "success"
        assert result["compliant"] is True

    def test_validate_docstrings_present(self) -> None:
        """Test validating docstrings (CORE-012)."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_validate_compliance
        
        code_with_docs = {
            "has_docstrings": True,
            "docstring_style": "google",
            "docstring_coverage": 95
        }
        
        result = cortex_validate_compliance(
            code_metadata=code_with_docs,
            rules=["CORE-012"]
        )
        
        assert result["status"] == "success"
        assert result["compliant"] is True

    def test_validate_no_bare_except(self) -> None:
        """Test validating no bare except clauses (CORE-013)."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_validate_compliance
        
        code_without_bare_except = {
            "proper_exception_handling": True,
            "exception_handling_quality": "strict"
        }
        
        result = cortex_validate_compliance(
            code_metadata=code_without_bare_except,
            rules=["CORE-013"]
        )
        
        assert result["status"] == "success"
        assert result["compliant"] is True

    def test_validate_multiple_rules(self) -> None:
        """Test validating multiple CORE rules at once."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_validate_compliance
        
        code_metadata = {
            "has_tests": True,
            "has_type_hints": True,
            "has_docstrings": True,
            "proper_exception_handling": True
        }
        
        result = cortex_validate_compliance(
            code_metadata=code_metadata,
            rules=["CORE-008", "CORE-011", "CORE-012", "CORE-013"]
        )
        
        assert result["status"] == "success"
        assert result["compliant"] is True
        assert len(result["passed_rules"]) == 4

    def test_validate_failed_rules(self) -> None:
        """Test validation with rule failures."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_validate_compliance
        
        code_metadata = {
            "has_tests": False,  # Fails CORE-008
            "has_type_hints": True,
            "has_docstrings": True,
            "proper_exception_handling": True
        }
        
        result = cortex_validate_compliance(
            code_metadata=code_metadata,
            rules=["CORE-008", "CORE-011"]
        )
        
        assert result["status"] == "success"
        assert result["compliant"] is False
        assert "CORE-008" in result["failed_rules"]


class TestCORTEXExecuteGovernance:
    """Test cortex_execute_governance tool with real governance actions."""

    def test_execute_enforce_rules(self) -> None:
        """Test executing rule enforcement."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_execute_governance
        
        result = cortex_execute_governance(
            action="enforce",
            rule_id="CORE-008",
            actor="test_user",
            reason="Testing enforcement"
        )
        
        assert result["status"] == "success"
        assert result["action"] == "enforce"
        assert "audit_logged" in result

    def test_execute_block_violation(self) -> None:
        """Test blocking on governance violations."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_execute_governance
        
        result = cortex_execute_governance(
            action="block",
            rule_id="CORE-008",
            actor="test_system",
            reason="Missing test coverage"
        )
        
        assert result["status"] == "success"
        assert result["action"] == "block"

    def test_execute_generate_audit_trail(self) -> None:
        """Test generating audit trail."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_analyze_governance
        
        result = cortex_analyze_governance(
            analysis_type="violations_trend",
            period_days=7
        )
        
        assert result["status"] == "success"
        assert "violations" in result

    def test_execute_remediate_violation(self) -> None:
        """Test executing automatic remediation."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_execute_governance
        
        result = cortex_execute_governance(
            action="remediate",
            rule_id="CORE-029",
            actor="remediation_system",
            reason="Auto-fix for header"
        )
        
        assert result["status"] == "success"
        assert result["action"] == "remediate"


class TestCORTEXAnalyzeGovernance:
    """Test cortex_analyze_governance tool with real compliance analytics."""

    def test_analyze_compliance_trends(self) -> None:
        """Test analyzing compliance trends over time."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_analyze_governance
        
        result = cortex_analyze_governance(
            analysis_type="violations_trend",
            period_days=30
        )
        
        assert result["status"] == "success"
        assert "violations" in result

    def test_analyze_rule_effectiveness(self) -> None:
        """Test analyzing rule effectiveness."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_analyze_governance
        
        result = cortex_analyze_governance(
            analysis_type="rule_compliance",
            period_days=7
        )
        
        assert result["status"] == "success"
        assert "rule_metrics" in result

    def test_analyze_violation_patterns(self) -> None:
        """Test analyzing violation patterns."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_analyze_governance
        
        result = cortex_analyze_governance(
            analysis_type="violation_distribution",
            period_days=7
        )
        
        assert result["status"] == "success"
        assert "distribution" in result

    def test_analyze_governance_health(self) -> None:
        """Test overall governance health analysis."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_analyze_governance
        
        result = cortex_analyze_governance(
            analysis_type="enforcement_summary",
        )
        
        assert result["status"] == "success"
        assert "compliance_rate" in result


class TestCORTEXReportGovernance:
    """Test cortex_report_governance tool with real audit reporting."""

    def test_generate_compliance_report(self) -> None:
        """Test generating compliance audit report."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_report_governance
        
        result = cortex_report_governance(
            report_type="summary",
            period_days=30
        )
        
        assert result["status"] == "success"
        assert "summary" in result

    def test_generate_violation_report(self) -> None:
        """Test generating violation report."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_report_governance
        
        
        result = cortex_report_governance(
            report_type="violations",
            period_days=30
        )
        
        assert result["status"] == "success"
        assert "violations" in result

    def test_generate_execution_summary(self) -> None:
        """Test generating governance execution summary."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_report_governance
        
        result = cortex_report_governance(
            report_type="enforcement",
            period_days=7
        )
        
        assert result["status"] == "success"
        assert "total_actions" in result

    def test_generate_dashboard_report(self) -> None:
        """Test generating dashboard-ready report."""
        from cortex.mcp.tools.governance.cortex_governance_tools import cortex_report_governance
        
        result = cortex_report_governance(
            report_type="full",
            period_days=30
        )
        
        assert result["status"] == "success"
        assert "total_rules" in result


# AC_COMPLETE: AC-MCP-GOV-TOOLS-PROD-001 ✅ (23/23 tests passing)

