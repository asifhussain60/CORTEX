"""
TDD tests for coherence models - Phase 0 Foundation.

Tests for: CoherenceReport, ContractValidation, CoherenceIssue
Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 0
Compliance: CORE-008 (TDD - tests BEFORE code), CORE-011 (type hints), CORE-012 (docstrings)
"""

import unittest
from datetime import datetime
from enum import Enum


class TestCoherenceIssueModel(unittest.TestCase):
    """Tests for CoherenceIssue data model."""
    
    def test_coherence_issue_creation(self) -> None:
        """Verify CoherenceIssue can be created with all fields."""
        from cortex.models.coherence_models import CoherenceIssue, IssueType
        
        issue = CoherenceIssue(
            issue_type=IssueType.ENUM_MISMATCH,
            python_value="SeverityLevel.HIGH",
            javascript_value="Severity.high",
            recommendation="Add mapping: SeverityLevel.HIGH → 'high'",
            severity="HIGH"
        )
        
        self.assertEqual(issue.issue_type, IssueType.ENUM_MISMATCH)
        self.assertEqual(issue.python_value, "SeverityLevel.HIGH")
        self.assertEqual(issue.javascript_value, "Severity.high")
        self.assertEqual(issue.severity, "HIGH")
    
    def test_issue_type_enum_values(self) -> None:
        """Verify IssueType enum has expected values."""
        from cortex.models.coherence_models import IssueType
        
        expected = {"ENUM_MISMATCH", "FIELD_NAME_MISMATCH", "TYPE_INCOMPATIBILITY", "MISSING_MAPPING"}
        actual = {t.name for t in IssueType}
        self.assertEqual(actual, expected)


class TestCoherenceReportModel(unittest.TestCase):
    """Tests for CoherenceReport data model."""
    
    def test_coherence_report_pass(self) -> None:
        """Verify CoherenceReport can represent a passing validation."""
        from cortex.models.coherence_models import CoherenceReport, CoherenceStatus
        
        report = CoherenceReport(
            status=CoherenceStatus.PASS,
            issues=[],
            contracts_validated=5,
            validation_timestamp=datetime.now()
        )
        
        self.assertEqual(report.status, CoherenceStatus.PASS)
        self.assertEqual(len(report.issues), 0)
        self.assertEqual(report.contracts_validated, 5)
    
    def test_coherence_report_fail_with_issues(self) -> None:
        """Verify CoherenceReport can include failure issues."""
        from cortex.models.coherence_models import (
            CoherenceReport, CoherenceStatus, CoherenceIssue, IssueType
        )
        
        report = CoherenceReport(
            status=CoherenceStatus.FAIL,
            issues=[
                CoherenceIssue(
                    issue_type=IssueType.ENUM_MISMATCH,
                    python_value="type",
                    javascript_value="category",
                    recommendation="Rename JS field to 'type'",
                    severity="MEDIUM"
                )
            ],
            contracts_validated=3,
            validation_timestamp=datetime.now()
        )
        
        self.assertEqual(report.status, CoherenceStatus.FAIL)
        self.assertEqual(len(report.issues), 1)
    
    def test_coherence_status_enum_values(self) -> None:
        """Verify CoherenceStatus enum has expected values."""
        from cortex.models.coherence_models import CoherenceStatus
        
        expected = {"PASS", "FAIL", "WARNING"}
        actual = {s.name for s in CoherenceStatus}
        self.assertEqual(actual, expected)


class TestContractValidationModel(unittest.TestCase):
    """Tests for ContractValidation data model."""
    
    def test_contract_validation_creation(self) -> None:
        """Verify ContractValidation can be created with results."""
        from cortex.models.coherence_models import ContractValidation
        
        validation = ContractValidation(
            contract_id="severity_enum_alignment",
            is_valid=True,
            tests_run=3,
            tests_passed=3,
            error_message=None
        )
        
        self.assertEqual(validation.contract_id, "severity_enum_alignment")
        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.tests_run, 3)
        self.assertEqual(validation.tests_passed, 3)
    
    def test_contract_validation_failure(self) -> None:
        """Verify ContractValidation can represent a failure."""
        from cortex.models.coherence_models import ContractValidation
        
        validation = ContractValidation(
            contract_id="field_mapping",
            is_valid=False,
            tests_run=5,
            tests_passed=3,
            error_message="2 field mappings failed validation"
        )
        
        self.assertFalse(validation.is_valid)
        self.assertEqual(validation.tests_passed, 3)
        self.assertIsNotNone(validation.error_message)


class TestIntegrationValidationModel(unittest.TestCase):
    """Tests for IntegrationValidation data model."""
    
    def test_integration_validation_creation(self) -> None:
        """Verify IntegrationValidation can aggregate contract validations."""
        from cortex.models.coherence_models import IntegrationValidation, ContractValidation
        
        validation = IntegrationValidation(
            overall_valid=True,
            contract_validations=[
                ContractValidation("contract_1", True, 3, 3, None),
                ContractValidation("contract_2", True, 5, 5, None)
            ],
            total_tests=8,
            total_passed=8
        )
        
        self.assertTrue(validation.overall_valid)
        self.assertEqual(len(validation.contract_validations), 2)
        self.assertEqual(validation.total_tests, 8)


if __name__ == "__main__":
    unittest.main()
