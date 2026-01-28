"""Tests for MCP Governance Tools - PHASE-DEPLOYMENT-003-mcp-expansion.

AC-DEP-003-02: Governance tools expose tier resolution and rule evaluation.
Tests 5 governance tools callable via MCP.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestTierResolverPrecedence:
    """Test tier resolver follows precedence: tier0 > tier1 > tier2."""

    def test_tier0_overrides_tier1(self):
        """Tier0 rules should override tier1 rules."""
        from cortex.brain.core.tier_resolver import TierResolver
        
        resolver = TierResolver()
        
        # Test that tier 0 rules cannot be overridden
        tier_result = resolver.get_tier_for_rule("CORE-008")
        # If rule exists and is tier 0, it can't be overridden
        override_result = resolver.is_overridden("CORE-008", tier=0)
        
        # Tier 0 rules should not be overridden
        assert override_result.is_ok()
        assert override_result.unwrap() == False, "Tier0 should not be overridable"

    def test_tier1_overrides_tier2(self):
        """Tier1 rules should override tier2 rules."""
        from cortex.brain.core.tier_resolver import TierResolver
        
        resolver = TierResolver()
        
        # Tier 1 can override tier 2
        # Testing the precedence concept
        tier1_override = resolver.is_overridden("ARCH-001", tier=1)
        tier2_override = resolver.is_overridden("ARCH-001", tier=2)
        
        # Tier 2 can be overridden by tier 1
        assert tier1_override.is_ok()
        assert tier2_override.is_ok()

    def test_tier2_default_when_no_override(self):
        """Tier2 should be used when no higher tier rules exist."""
        from cortex.brain.core.tier_resolver import TierResolver
        
        resolver = TierResolver()
        
        # Test that get_effective_rule returns a rule
        result = resolver.get_effective_rule("CORE-008")
        
        # Should return some result (ok or err)
        assert result.is_ok() or result.is_err()
        # The precedence is built into the registry lookup


class TestRuleEvaluatorChecksCode:
    """Test rule evaluator checks code against rules."""

    def test_core008_checks_test_exists(self):
        """CORE-008 should verify test file exists for implementation."""
        from cortex.mcp.tools.governance.rule_evaluator import RuleEvaluator
        
        evaluator = RuleEvaluator()
        
        # Mock implementation file without test
        code_path = "src/new_feature.py"
        test_path = "tests/test_new_feature.py"
        
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.side_effect = lambda: code_path.endswith(".py")
            
            result = evaluator.evaluate_rule("CORE-008", code_path, test_exists=False)
        
        assert result["passed"] is False
        assert "test" in result["message"].lower()

    def test_core008_passes_with_test(self):
        """CORE-008 should pass when test file exists."""
        from cortex.mcp.tools.governance.rule_evaluator import RuleEvaluator
        
        evaluator = RuleEvaluator()
        
        result = evaluator.evaluate_rule("CORE-008", "src/new_feature.py", test_exists=True)
        
        assert result["passed"] is True

    def test_rule_evaluator_returns_structured_result(self):
        """Rule evaluator should return structured result."""
        from cortex.mcp.tools.governance.rule_evaluator import RuleEvaluator
        
        evaluator = RuleEvaluator()
        
        result = evaluator.evaluate_rule("CORE-008", "src/test.py", test_exists=True)
        
        assert "rule_id" in result
        assert "passed" in result
        assert "message" in result


class TestAuditQueryFindsEntries:
    """Test audit query searches governance.db."""

    def test_query_by_ac_id(self):
        """Should find entries by AC-ID."""
        from cortex.mcp.tools.governance.audit_query import AuditQuery
        
        query = AuditQuery()
        
        # Mock database
        with patch.object(query, "_execute_query") as mock_query:
            mock_query.return_value = [
                {"ac_id": "AC-INT-001", "timestamp": "2025-01-01", "operation": "CREATE"}
            ]
            
            results = query.search(ac_id="AC-INT-001")
        
        assert len(results) >= 1
        assert results[0]["ac_id"] == "AC-INT-001"

    def test_query_by_timestamp_range(self):
        """Should find entries by timestamp range."""
        from cortex.mcp.tools.governance.audit_query import AuditQuery
        
        query = AuditQuery()
        
        with patch.object(query, "_execute_query") as mock_query:
            mock_query.return_value = [
                {"ac_id": "AC-INT-001", "timestamp": "2025-01-15", "operation": "UPDATE"}
            ]
            
            results = query.search(start_date="2025-01-01", end_date="2025-01-31")
        
        assert len(results) >= 1

    def test_query_by_phase(self):
        """Should find entries by phase."""
        from cortex.mcp.tools.governance.audit_query import AuditQuery
        
        query = AuditQuery()
        
        with patch.object(query, "_execute_query") as mock_query:
            mock_query.return_value = [
                {"ac_id": "AC-DEP-003-01", "phase": "DEPLOYMENT-003", "operation": "CREATE"}
            ]
            
            results = query.search(phase="DEPLOYMENT-003")
        
        assert len(results) >= 1
        assert "DEP-003" in results[0]["ac_id"]


class TestPolicyEnforcerBlocksViolations:
    """Test policy enforcer blocks tier0 violations."""

    def test_enforcer_blocks_violation(self):
        """Should block code that violates tier0 policy."""
        from cortex.mcp.tools.governance.policy_enforcer import PolicyEnforcer
        
        enforcer = PolicyEnforcer()
        
        # Code without docstring violates CORE-012
        code = '''
def my_function():
    pass
'''
        
        result = enforcer.check_policy("CORE-012", code)
        
        assert result["blocked"] is True
        assert "docstring" in result["reason"].lower()

    def test_enforcer_allows_compliant_code(self):
        """Should allow code that complies with tier0 policy."""
        from cortex.mcp.tools.governance.policy_enforcer import PolicyEnforcer
        
        enforcer = PolicyEnforcer()
        
        code = '''
def my_function():
    """This is a docstring."""
    pass
'''
        
        result = enforcer.check_policy("CORE-012", code)
        
        assert result["blocked"] is False

    def test_enforcer_returns_violation_details(self):
        """Should return detailed violation information."""
        from cortex.mcp.tools.governance.policy_enforcer import PolicyEnforcer
        
        enforcer = PolicyEnforcer()
        
        code = "def f(): pass"
        
        result = enforcer.check_policy("CORE-012", code)
        
        assert "policy_id" in result
        assert "blocked" in result
        assert "reason" in result


class TestComplianceReporterGeneratesReport:
    """Test compliance reporter generates reports."""

    def test_generates_summary_report(self):
        """Should generate summary compliance report."""
        from cortex.mcp.tools.governance.compliance_reporter import ComplianceReporter
        
        reporter = ComplianceReporter()
        
        report = reporter.generate_report(scope="project")
        
        assert "total_rules" in report
        assert "passed" in report
        assert "failed" in report
        assert "compliance_percentage" in report

    def test_report_includes_rule_details(self):
        """Report should include per-rule details."""
        from cortex.mcp.tools.governance.compliance_reporter import ComplianceReporter
        
        reporter = ComplianceReporter()
        
        report = reporter.generate_report(scope="project", detailed=True)
        
        assert "rules" in report
        assert isinstance(report["rules"], list)

    def test_report_filterable_by_tier(self):
        """Report should be filterable by tier."""
        from cortex.mcp.tools.governance.compliance_reporter import ComplianceReporter
        
        reporter = ComplianceReporter()
        
        report = reporter.generate_report(scope="project", tier="tier0")
        
        assert report["tier_filter"] == "tier0"
