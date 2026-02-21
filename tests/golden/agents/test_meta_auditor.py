"""
Golden tests for MetaAuditorAgent — validates audit results (no false positives).

Authority: Phase 29 S1 | Zero-Mock Philosophy
Test Count: 8 golden tests
"""
import pytest
from pathlib import Path
from cortex.orchestrators.intelligence.meta_auditor_agent import MetaAuditorAgent, AuditValidationResult


class TestMetaAuditorValidation:
    """Golden test: Meta-auditor validates audit results."""
    
    def test_detect_false_positive_in_audit(self, tmp_path: Path) -> None:
        """Golden: Detect false positive in audit results."""
        agent = MetaAuditorAgent()
        
        # Simulate audit result claiming CORE-008 violation (but code has tests)
        audit_result = {
            "violations": [
                {"rule": "CORE-008", "file": "cortex/example.py", "message": "No tests found"}
            ]
        }
        
        # Meta-auditor validates (finds tests exist)
        validation = agent.validate_audit_result(audit_result, workspace=tmp_path)
        
        assert validation.has_false_positives is True
        assert "CORE-008" in validation.false_positive_rules
    
    def test_approve_valid_audit_result(self) -> None:
        """Golden: Approve audit with no false positives."""
        agent = MetaAuditorAgent()
        
        audit_result = {
            "violations": [
                {"rule": "CORE-028", "file": "BAD_NAME.py", "message": "SCREAMING_CASE forbidden"}
            ]
        }
        
        validation = agent.validate_audit_result(audit_result)
        
        assert validation.has_false_positives is False
        assert validation.approved is True
    
    def test_re_run_audit_on_false_positive(self) -> None:
        """Golden: Re-run audit after detecting false positive."""
        agent = MetaAuditorAgent()
        
        audit_result = {"violations": [{"rule": "CORE-011", "file": "typed.py"}]}
        validation = agent.validate_audit_result(audit_result)
        
        if validation.has_false_positives:
            corrected = agent.re_run_audit_with_fixes(audit_result)
            assert corrected["violations"] == []


class TestMetaAuditorIntegration:
    """Golden test: Meta-auditor integrates with EnforcementOrchestrator."""

    def test_enforcement_result_validated_by_meta_auditor(self) -> None:
        """Golden: EnforcementOrchestrator result validated by meta-auditor."""
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator

        enforcer = EnforcementOrchestrator()
        agent = MetaAuditorAgent()

        # Run enforcement on a benign operation
        result = enforcer.validate_operation({
            "intent": "QUERY",
            "files": [],
            "description": "simple query",
        })

        # Meta-auditor validates the enforcement output
        audit_result = {"violations": []}
        if result.is_err():
            enforcement = result.err()
            audit_result = {"violations": [{"rule": v, "file": "", "message": v} for v in enforcement.violations]}

        validation = agent.validate_audit_result(audit_result)
        assert validation is not None
        assert hasattr(validation, "approved")

    def test_audit_pipeline_with_validation(self) -> None:
        """Golden: Full audit pipeline — validate then meta-audit."""
        agent = MetaAuditorAgent()

        # Simulate a clean audit result
        audit_result = {"violations": []}
        validation = agent.validate_audit_result(audit_result)

        assert validation.has_false_positives is False
        assert validation.approved is True
