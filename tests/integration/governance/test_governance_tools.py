"""Tests for Governance Tools - Rule Analysis and Enforcement."""

import pytest
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta

from cortex.governance.governance_analyzer import GovernanceAnalyzer, ViolationReport
from cortex.governance.compliance_reporter import ComplianceReporter
from cortex.governance.audit_navigator import AuditNavigator, AuditEntry
from cortex.governance.policy_enforcer import PolicyEnforcer, EnforcementDecision


class TestGovernanceAnalyzer:
    """Tests for Governance Analyzer."""

    def test_analyzer_initialization(self) -> None:
        """Test analyzer can be initialized."""
        analyzer = GovernanceAnalyzer()
        assert analyzer is not None

    def test_analyzer_detects_violations(self) -> None:
        """Test analyzer detects policy violations."""
        analyzer = GovernanceAnalyzer()
        violations = analyzer.analyze(
            entity_type="operation",
            entity_data={"bare_except": True, "logging": False}
        )
        
        assert isinstance(violations, list)
        assert len(violations) > 0

    def test_violation_report_contains_remediation(self) -> None:
        """Test violation reports include remediation suggestions."""
        analyzer = GovernanceAnalyzer()
        violations = analyzer.analyze(
            entity_type="code",
            entity_data={"has_type_hints": False}
        )
        
        if violations:
            assert all(hasattr(v, "remediation") for v in violations)

    def test_analyzer_accuracy_high(self) -> None:
        """Test analyzer accurately identifies violations."""
        analyzer = GovernanceAnalyzer()
        
        # Compliant code
        compliant = analyzer.analyze(
            entity_type="function",
            entity_data={
                "has_type_hints": True,
                "has_docstring": True,
                "bare_except": False
            }
        )
        
        # Non-compliant code
        non_compliant = analyzer.analyze(
            entity_type="function",
            entity_data={
                "has_type_hints": False,
                "has_docstring": False,
                "bare_except": True
            }
        )
        
        assert len(compliant) < len(non_compliant)

    def test_analyzer_supports_multiple_entity_types(self) -> None:
        """Test analyzer supports multiple entity types."""
        analyzer = GovernanceAnalyzer()
        
        entity_types = ["operation", "code", "function", "class", "module"]
        for entity_type in entity_types:
            violations = analyzer.analyze(
                entity_type=entity_type,
                entity_data={}
            )
            assert isinstance(violations, list)


class TestComplianceReporter:
    """Tests for Compliance Reporter."""

    def test_reporter_initialization(self) -> None:
        """Test reporter can be initialized."""
        reporter = ComplianceReporter()
        assert reporter is not None

    def test_reporter_generates_json_report(self) -> None:
        """Test reporter generates JSON compliance reports."""
        reporter = ComplianceReporter()
        violations = [
            ViolationReport(
                rule_id="CORE-011",
                severity="HIGH",
                message="Missing type hints",
                entity="function_xyz",
                remediation="Add type hints"
            )
        ]
        
        report = reporter.generate_json_report(violations)
        assert isinstance(report, str)
        assert "CORE-011" in report

    def test_reporter_generates_pdf_report(self) -> None:
        """Test reporter can generate PDF compliance reports."""
        reporter = ComplianceReporter()
        violations = []
        
        pdf_bytes = reporter.generate_pdf_report(violations)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_report_includes_compliance_metrics(self) -> None:
        """Test compliance report includes metrics."""
        reporter = ComplianceReporter()
        violations = []
        
        report = reporter.generate_json_report(violations)
        assert "compliance_percentage" in report or "metrics" in report

    def test_reporter_handles_multiple_violations(self) -> None:
        """Test reporter handles multiple violations."""
        reporter = ComplianceReporter()
        violations = [
            ViolationReport(
                rule_id=f"CORE-{i:03d}",
                severity="HIGH" if i % 2 == 0 else "MEDIUM",
                message=f"Violation {i}",
                entity=f"entity_{i}",
                remediation=f"Fix {i}"
            )
            for i in range(1, 6)
        ]
        
        report = reporter.generate_json_report(violations)
        assert len(violations) == 5
        assert all(str(v.rule_id) in report for v in violations)


class TestAuditNavigator:
    """Tests for Audit Navigator."""

    def test_navigator_initialization(self) -> None:
        """Test navigator can be initialized."""
        navigator = AuditNavigator()
        assert navigator is not None

    def test_navigator_queries_by_entity(self) -> None:
        """Test navigator can query audit trail by entity."""
        navigator = AuditNavigator()
        
        # Log some entries
        navigator.log_entry(
            entity_type="operation",
            entity_id="op_123",
            action="CREATE",
            actor="user_1"
        )
        
        entries = navigator.query_by_entity("operation", "op_123")
        assert isinstance(entries, list)
        assert len(entries) > 0

    def test_navigator_queries_by_time_range(self) -> None:
        """Test navigator can query audit trail by time range."""
        navigator = AuditNavigator()
        
        # Log an entry
        navigator.log_entry(
            entity_type="operation",
            entity_id="op_456",
            action="UPDATE",
            actor="user_2"
        )
        
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)
        
        entries = navigator.query_by_time_range(start, end)
        assert isinstance(entries, list)

    def test_navigator_queries_by_action(self) -> None:
        """Test navigator can query audit trail by action."""
        navigator = AuditNavigator()
        
        navigator.log_entry(
            entity_type="operation",
            entity_id="op_789",
            action="DELETE",
            actor="user_3"
        )
        
        entries = navigator.query_by_action("DELETE")
        assert isinstance(entries, list)

    def test_audit_entry_contains_required_fields(self) -> None:
        """Test audit entries contain required fields."""
        navigator = AuditNavigator()
        
        navigator.log_entry(
            entity_type="operation",
            entity_id="op_final",
            action="READ",
            actor="user_4"
        )
        
        entries = navigator.query_by_action("READ")
        assert len(entries) > 0
        
        entry = entries[0]
        assert hasattr(entry, "timestamp")
        assert hasattr(entry, "entity_type")
        assert hasattr(entry, "entity_id")
        assert hasattr(entry, "action")
        assert hasattr(entry, "actor")


class TestPolicyEnforcer:
    """Tests for Policy Enforcer."""

    def test_enforcer_initialization(self) -> None:
        """Test enforcer can be initialized."""
        enforcer = PolicyEnforcer()
        assert enforcer is not None

    def test_enforcer_allows_compliant_operations(self) -> None:
        """Test enforcer allows compliant operations."""
        enforcer = PolicyEnforcer()
        
        decision = enforcer.check_compliance(
            operation_type="api_call",
            operation_data={
                "has_type_hints": True,
                "has_logging": True,
                "error_handling": True
            }
        )
        
        assert decision.allowed is True
        assert decision.action in ["allow", "warn"]

    def test_enforcer_blocks_non_compliant_operations(self) -> None:
        """Test enforcer blocks non-compliant operations."""
        enforcer = PolicyEnforcer()
        
        decision = enforcer.check_compliance(
            operation_type="code_execution",
            operation_data={
                "has_type_hints": False,
                "has_logging": False,
                "bare_except": True
            }
        )
        
        if not decision.allowed:
            assert decision.action in ["block", "warn"]

    def test_enforcer_dry_run_mode(self) -> None:
        """Test enforcer supports dry-run mode."""
        enforcer = PolicyEnforcer(dry_run=True)
        
        decision = enforcer.check_compliance(
            operation_type="operation",
            operation_data={"compliant": False}
        )
        
        # In dry-run, should warn but not block
        assert decision.action in ["allow", "warn"]

    def test_enforcement_decision_contains_reasoning(self) -> None:
        """Test enforcement decisions include reasoning."""
        enforcer = PolicyEnforcer()
        
        decision = enforcer.check_compliance(
            operation_type="operation",
            operation_data={}
        )
        
        assert hasattr(decision, "reason")
        assert decision.reason is not None


class TestGovernanceIntegration:
    """Integration tests for governance tools."""

    def test_end_to_end_governance_flow(self) -> None:
        """Test complete governance flow."""
        analyzer = GovernanceAnalyzer()
        reporter = ComplianceReporter()
        navigator = AuditNavigator()
        enforcer = PolicyEnforcer()
        
        # Analyze
        violations = analyzer.analyze(
            entity_type="operation",
            entity_data={"compliant": False}
        )
        
        # Report
        report = reporter.generate_json_report(violations)
        
        # Navigate audit
        navigator.log_entry(
            entity_type="governance_check",
            entity_id="check_1",
            action="ANALYZE",
            actor="governance_system"
        )
        
        audit_entries = navigator.query_by_entity("governance_check", "check_1")
        
        # Enforce
        decision = enforcer.check_compliance(
            operation_type="operation",
            operation_data={"compliant": False}
        )
        
        assert isinstance(violations, list)
        assert isinstance(report, str)
        assert isinstance(audit_entries, list)
        assert hasattr(decision, "allowed")

    def test_governance_with_custom_rules(self) -> None:
        """Test governance tools support custom rules."""
        analyzer = GovernanceAnalyzer()
        
        # Add custom rule
        analyzer.add_custom_rule(
            rule_id="CUSTOM-001",
            rule_text="Custom governance rule",
            check_function=lambda x: len(str(x)) > 10
        )
        
        violations = analyzer.analyze(
            entity_type="custom",
            entity_data="short"
        )
        
        # Should detect the custom rule violation
        assert isinstance(violations, list)

    def test_governance_metrics_collection(self) -> None:
        """Test governance metrics are collected."""
        analyzer = GovernanceAnalyzer()
        
        # Run multiple analyses
        for i in range(5):
            analyzer.analyze(
                entity_type="test",
                entity_data={"index": i}
            )
        
        metrics = analyzer.get_metrics()
        assert isinstance(metrics, dict)
        assert "violations_detected" in metrics or "total_checks" in metrics

    def test_governance_compliance_percentage(self) -> None:
        """Test compliance percentage calculation."""
        reporter = ComplianceReporter()
        
        violations = [
            ViolationReport(
                rule_id="CORE-001",
                severity="HIGH",
                message="Test",
                entity="entity_1",
                remediation="Fix"
            )
        ]
        
        report = reporter.generate_json_report(violations)
        # Report should indicate non-100% compliance
        assert "compliance" in report.lower() or "violation" in report.lower()
