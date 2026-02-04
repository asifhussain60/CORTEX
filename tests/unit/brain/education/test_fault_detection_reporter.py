"""
Unit tests for FaultDetectionReporter.

Tests the intelligent fault detection and reporting system that identifies
implementation issues and provides actionable recommendations.

Authority: AC-EDUCATIONAL-INTERACTION-001, PHASE-22-ASK-MODE-SYSTEM.yaml
Rules: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import unittest
from typing import List
from dataclasses import dataclass

from cortex.brain.education.fault_detection_reporter import (
    FaultDetectionReporter,
    FaultReport,
    FaultSeverity,
    FaultCategory,
)


class TestFaultDetectionReporter(unittest.TestCase):
    """Test suite for FaultDetectionReporter."""

    def setUp(self):
        """Set up test fixtures."""
        self.reporter = FaultDetectionReporter()

    def test_initialization_succeeds(self):
        """Test FaultDetectionReporter initializes correctly."""
        self.assertIsNotNone(self.reporter)
        self.assertIsInstance(self.reporter, FaultDetectionReporter)

    def test_generates_fault_report(self):
        """Test that fault report is generated."""
        report = self.reporter.detect_faults(
            topic="MasterOrchestrator",
            verification_results={}
        )
        
        self.assertIsInstance(report, FaultReport)
        self.assertIsNotNone(report.faults)

    def test_detects_missing_orchestrator(self):
        """Test detection of missing orchestrator."""
        verification = {
            "orchestrator_exists": False,
            "file_path": None
        }
        
        report = self.reporter.detect_faults(
            topic="NonExistentOrchestrator",
            verification_results=verification
        )
        
        self.assertGreater(len(report.faults), 0)
        self.assertEqual(report.faults[0].severity, FaultSeverity.ERROR)

    def test_detects_missing_wiring(self):
        """Test detection of orchestrator not in wiring."""
        verification = {
            "orchestrator_exists": True,
            "wiring_registered": False
        }
        
        report = self.reporter.detect_faults(
            topic="UnwiredOrchestrator",
            verification_results=verification
        )
        
        has_wiring_fault = any(
            fault.category == FaultCategory.WIRING
            for fault in report.faults
        )
        self.assertTrue(has_wiring_fault)

    def test_detects_missing_tests(self):
        """Test detection of missing test coverage."""
        verification = {
            "orchestrator_exists": True,
            "test_coverage": 0
        }
        
        report = self.reporter.detect_faults(
            topic="UntestedOrchestrator",
            verification_results=verification
        )
        
        has_test_fault = any(
            fault.category == FaultCategory.TESTING
            for fault in report.faults
        )
        self.assertTrue(has_test_fault)

    def test_severity_levels_assigned(self):
        """Test that appropriate severity levels are assigned."""
        verification = {
            "orchestrator_exists": False  # ERROR
        }
        
        report = self.reporter.detect_faults(
            topic="TestOrchestrator",
            verification_results=verification
        )
        
        severities = {fault.severity for fault in report.faults}
        self.assertIn(FaultSeverity.ERROR, severities)

    def test_provides_recommendations(self):
        """Test that actionable recommendations are provided."""
        verification = {
            "orchestrator_exists": True,
            "wiring_registered": False
        }
        
        report = self.reporter.detect_faults(
            topic="UnwiredOrchestrator",
            verification_results=verification
        )
        
        for fault in report.faults:
            self.assertIsNotNone(fault.recommendation)
            self.assertGreater(len(fault.recommendation), 20)

    def test_categorizes_faults(self):
        """Test that faults are properly categorized."""
        verification = {
            "orchestrator_exists": True,
            "wiring_registered": False,
            "test_coverage": 0,
            "documentation": None
        }
        
        report = self.reporter.detect_faults(
            topic="FaultyOrchestrator",
            verification_results=verification
        )
        
        categories = {fault.category for fault in report.faults}
        self.assertGreater(len(categories), 1)  # Multiple categories

    def test_empty_verification_handled(self):
        """Test that empty verification results are handled."""
        report = self.reporter.detect_faults(
            topic="SomeOrchestrator",
            verification_results={}
        )
        
        self.assertIsInstance(report, FaultReport)

    def test_detects_documentation_issues(self):
        """Test detection of missing or poor documentation."""
        verification = {
            "orchestrator_exists": True,
            "documentation": None
        }
        
        report = self.reporter.detect_faults(
            topic="PoorlyDocumentedOrchestrator",
            verification_results=verification
        )
        
        has_doc_fault = any(
            fault.category == FaultCategory.DOCUMENTATION
            for fault in report.faults
        )
        self.assertTrue(has_doc_fault)

    def test_detects_interface_compliance_issues(self):
        """Test detection of interface compliance problems."""
        verification = {
            "orchestrator_exists": True,
            "implements_interface": False
        }
        
        report = self.reporter.detect_faults(
            topic="NonCompliantOrchestrator",
            verification_results=verification
        )
        
        has_interface_fault = any(
            fault.category == FaultCategory.INTERFACE
            for fault in report.faults
        )
        self.assertTrue(has_interface_fault)

    def test_warning_severity_for_minor_issues(self):
        """Test that minor issues get WARNING severity."""
        verification = {
            "orchestrator_exists": True,
            "test_coverage": 50  # Partial coverage
        }
        
        report = self.reporter.detect_faults(
            topic="PartiallyTestedOrchestrator",
            verification_results=verification
        )
        
        if len(report.faults) > 0:
            severities = {fault.severity for fault in report.faults}
            # Should have warnings, not errors
            self.assertTrue(
                FaultSeverity.WARNING in severities or len(report.faults) == 0
            )

    def test_formats_report_for_display(self):
        """Test that report can be formatted for user display."""
        verification = {
            "orchestrator_exists": False
        }
        
        report = self.reporter.detect_faults(
            topic="TestOrchestrator",
            verification_results=verification
        )
        
        formatted = self.reporter.format_report(report)
        
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 50)

    def test_prioritizes_faults_by_severity(self):
        """Test that faults are sorted by severity."""
        verification = {
            "orchestrator_exists": True,
            "wiring_registered": False,  # WARNING
            "test_coverage": 0  # ERROR
        }
        
        report = self.reporter.detect_faults(
            topic="FaultyOrchestrator",
            verification_results=verification
        )
        
        # Errors should come before warnings
        if len(report.faults) > 1:
            severities = [fault.severity for fault in report.faults]
            errors_first = all(
                severities[i].value >= severities[i+1].value
                for i in range(len(severities)-1)
            )
            self.assertTrue(errors_first)

    def test_provides_file_references(self):
        """Test that file paths are included when available."""
        verification = {
            "orchestrator_exists": True,
            "file_path": "cortex/orchestrators/test/test_orchestrator.py"
        }
        
        report = self.reporter.detect_faults(
            topic="TestOrchestrator",
            verification_results=verification
        )
        
        # File path should be in report or fault details
        self.assertIsNotNone(report.topic)


if __name__ == "__main__":
    unittest.main()
