"""
Tests for ManifestComplianceValidator

Validates manifest compliance checking including DoR/DoD requirements,
phase structure, and TDD requirements.
"""

import pytest
from pathlib import Path
from src.orchestrators.planning.intelligence.manifest_compliance_validator import (
    ManifestComplianceValidator,
    ComplianceLevel,
    ManifestSection,
    ComplianceViolation,
    ComplianceReport
)


class TestManifestComplianceValidatorInit:
    """Test ManifestComplianceValidator initialization."""
    
    def test_validator_init(self):
        """Test validator initialization."""
        validator = ManifestComplianceValidator()
        assert validator.manifest is not None
        assert validator.dor_requirements is not None
        assert validator.dod_requirements is not None
    
    def test_validator_uses_default_manifest(self):
        """Test validator uses default manifest if file not found."""
        validator = ManifestComplianceValidator(manifest_path=Path("/nonexistent/path"))
        assert validator.manifest is not None
        assert "definition_of_ready" in validator.manifest


class TestDoRValidation:
    """Test Definition of Ready validation."""
    
    def test_missing_dor_section(self):
        """Test detection of missing DoR section."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {"plan_name": "Test"},
            "phases": []
        }
        
        report = validator.validate_plan_compliance(plan_data)
        critical = report.get_critical_violations()
        assert any("definition_of_ready" in v.message.lower() for v in critical)
        assert report.compliance_level == ComplianceLevel.NON_COMPLIANT
    
    def test_empty_dor_requirement(self):
        """Test detection of empty DoR requirement."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {"plan_name": "Test"},
            "definition_of_ready": {
                "requirements_clear": "",  # Empty
                "acceptance_criteria_defined": "Yes"
            },
            "definition_of_done": {
                "code_complete": "Yes"
            },
            "phases": []
        }
        
        report = validator.validate_plan_compliance(plan_data)
        assert report.dor_compliance < 100.0
        assert any("Empty DoR requirement" in v.message for v in report.violations)
    
    def test_complete_dor(self):
        """Test fully compliant DoR."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {"plan_name": "Test", "version": "1.0", "complexity": "low", "estimated_hours": 10, "created_at": "2025-12-24"},
            "definition_of_ready": {
                "requirements_clear": "Yes, all requirements defined",
                "acceptance_criteria_defined": "Yes, all criteria listed",
                "dependencies_identified": "No external dependencies"
            },
            "definition_of_done": {
                "code_complete": "Yes",
                "tests_passing": "Yes",
                "documentation_updated": "Yes"
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "tasks": [
                        {
                            "task_id": "T1",
                            "task_name": "Task 1",
                            "estimated_hours": 10,
                            "acceptance_criteria": ["AC1"]
                        }
                    ],
                    "dor": "Complete",
                    "dod": "Complete"
                }
            ]
        }
        
        report = validator.validate_plan_compliance(plan_data)
        assert report.dor_compliance == 100.0


class TestDoDValidation:
    """Test Definition of Done validation."""
    
    def test_missing_dod_section(self):
        """Test detection of missing DoD section."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {"plan_name": "Test"},
            "definition_of_ready": {
                "requirements_clear": "Yes"
            },
            "phases": []
        }
        
        report = validator.validate_plan_compliance(plan_data)
        critical = report.get_critical_violations()
        assert any("definition_of_done" in v.message.lower() for v in critical)
    
    def test_dod_score_calculation(self):
        """Test DoD score calculation."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {"plan_name": "Test"},
            "definition_of_ready": {
                "requirements_clear": "Yes",
                "acceptance_criteria_defined": "Yes",
                "dependencies_identified": "Yes"
            },
            "definition_of_done": {
                "code_complete": "Yes",
                "tests_passing": "Yes"
                # Missing "documentation_updated"
            },
            "phases": []
        }
        
        report = validator.validate_plan_compliance(plan_data)
        # Should be 66.67% (2 out of 3)
        assert 60 < report.dod_compliance < 70


class TestPhaseStructureValidation:
    """Test phase structure validation."""
    
    def test_missing_phase_fields(self):
        """Test detection of missing phase fields."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {"plan_name": "Test"},
            "definition_of_ready": {"requirements_clear": "Yes"},
            "definition_of_done": {"code_complete": "Yes"},
            "phases": [
                {
                    "phase_number": 1
                    # Missing phase_name, tasks, dor, dod
                }
            ]
        }
        
        report = validator.validate_plan_compliance(plan_data)
        major_violations = [v for v in report.violations if v.severity == "major"]
        assert len(major_violations) > 0
        assert any("phase_name" in v.message.lower() for v in major_violations)
    
    def test_missing_task_fields(self):
        """Test detection of missing task fields."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {"plan_name": "Test"},
            "definition_of_ready": {"requirements_clear": "Yes"},
            "definition_of_done": {"code_complete": "Yes"},
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "tasks": [
                        {
                            "task_id": "T1"
                            # Missing task_name, estimated_hours, acceptance_criteria
                        }
                    ],
                    "dor": "Complete",
                    "dod": "Complete"
                }
            ]
        }
        
        report = validator.validate_plan_compliance(plan_data)
        major_violations = [v for v in report.violations if v.severity == "major"]
        assert any("task_name" in v.message.lower() for v in major_violations)
        assert any("estimated_hours" in v.message.lower() for v in major_violations)


class TestTDDRequirements:
    """Test TDD requirements validation."""
    
    def test_tdd_required_for_medium_complexity(self):
        """Test TDD requirement for medium complexity."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {
                "plan_name": "Test",
                "complexity": "medium"
            },
            "definition_of_ready": {"requirements_clear": "Yes"},
            "definition_of_done": {"code_complete": "Yes"},
            "phases": []
            # Missing tdd_workflow
        }
        
        report = validator.validate_plan_compliance(plan_data)
        critical = report.get_critical_violations()
        assert any("TDD workflow" in v.message for v in critical)
    
    def test_tdd_not_required_for_low_complexity(self):
        """Test TDD not required for low complexity."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {
                "plan_name": "Test",
                "complexity": "low",
                "version": "1.0",
                "estimated_hours": 5,
                "created_at": "2025-12-24"
            },
            "definition_of_ready": {
                "requirements_clear": "Yes",
                "acceptance_criteria_defined": "Yes",
                "dependencies_identified": "Yes"
            },
            "definition_of_done": {
                "code_complete": "Yes",
                "tests_passing": "Yes",
                "documentation_updated": "Yes"
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "tasks": [
                        {
                            "task_id": "T1",
                            "task_name": "Task 1",
                            "estimated_hours": 5,
                            "acceptance_criteria": ["AC1"]
                        }
                    ],
                    "dor": "Complete",
                    "dod": "Complete"
                }
            ]
            # No tdd_workflow, but that's OK for low complexity
        }
        
        report = validator.validate_plan_compliance(plan_data)
        critical = report.get_critical_violations()
        # No critical TDD violations for low complexity
        tdd_critical = [v for v in critical if v.section == ManifestSection.TDD_REQUIREMENTS]
        assert len(tdd_critical) == 0
    
    def test_tdd_workflow_missing_phases(self):
        """Test detection of incomplete TDD workflow."""
        validator = ManifestComplianceValidator()
        plan_data = {
            "metadata": {
                "plan_name": "Test",
                "complexity": "high"
            },
            "definition_of_ready": {"requirements_clear": "Yes"},
            "definition_of_done": {"code_complete": "Yes"},
            "tdd_workflow": {
                "red_phase": "Write failing tests"
                # Missing green_phase, refactor_phase
            },
            "phases": []
        }
        
        report = validator.validate_plan_compliance(plan_data)
        major_violations = [v for v in report.violations if v.severity == "major"]
        assert any("green_phase" in v.message.lower() for v in major_violations)
        assert any("refactor_phase" in v.message.lower() for v in major_violations)


class TestComplianceReport:
    """Test ComplianceReport functionality."""
    
    def test_report_add_violation(self):
        """Test adding violations to report."""
        report = ComplianceReport(compliance_level=ComplianceLevel.FULL)
        
        violation = ComplianceViolation(
            section=ManifestSection.METADATA,
            requirement="Test",
            severity="critical",
            message="Test violation"
        )
        
        report.add_violation(violation)
        assert report.critical_violations == 1
        assert report.compliance_level == ComplianceLevel.NON_COMPLIANT
    
    def test_report_summary_full_compliance(self):
        """Test summary for full compliance."""
        report = ComplianceReport(compliance_level=ComplianceLevel.FULL)
        report.overall_score = 100.0
        
        summary = report.get_summary()
        assert "✅" in summary
        assert "Fully compliant" in summary
    
    def test_report_summary_non_compliant(self):
        """Test summary for non-compliance."""
        report = ComplianceReport(compliance_level=ComplianceLevel.NON_COMPLIANT)
        report.critical_violations = 3
        report.overall_score = 40.0
        
        summary = report.get_summary()
        assert "❌" in summary
        assert "Non-compliant" in summary
        assert "3 critical" in summary
