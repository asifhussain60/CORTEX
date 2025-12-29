"""
Tests for ValidationFrameworkAdapter

Validates multi-layer validation framework including schema, business rules,
cross-field validation, and async validation.
"""

import pytest
import asyncio
from pathlib import Path
from src.orchestrators.planning.intelligence.validation_framework_adapter import (
    ValidationFrameworkAdapter,
    ValidationLevel,
    ValidationType,
    ValidationResult,
    ValidationReport
)


class TestValidationFrameworkAdapterInit:
    """Test ValidationFrameworkAdapter initialization."""
    
    def test_adapter_init_default(self):
        """Test default initialization."""
        adapter = ValidationFrameworkAdapter()
        assert adapter.strict_mode is True
        assert adapter.logger is not None
    
    def test_adapter_init_non_strict(self):
        """Test non-strict mode initialization."""
        adapter = ValidationFrameworkAdapter(strict_mode=False)
        assert adapter.strict_mode is False


class TestSchemaValidation:
    """Test schema validation functionality."""
    
    @pytest.mark.asyncio
    async def test_valid_schema(self):
        """Test validation of valid schema."""
        adapter = ValidationFrameworkAdapter()
        plan_data = {
            "metadata": {
                "plan_name": "Test Plan",
                "complexity": "medium",
                "estimated_hours": 10
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "tasks": [
                        {
                            "task_id": "T1",
                            "task_name": "Task 1",
                            "estimated_hours": 5
                        }
                    ]
                }
            ]
        }
        
        report = await adapter.validate_plan(plan_data, validation_levels=["schema"])
        assert report.is_valid is True
        assert report.errors == 0
    
    @pytest.mark.asyncio
    async def test_missing_metadata(self):
        """Test detection of missing metadata."""
        adapter = ValidationFrameworkAdapter()
        plan_data = {
            "phases": []
        }
        
        report = await adapter.validate_plan(plan_data, validation_levels=["schema"])
        assert report.is_valid is False
        assert report.errors > 0
        assert any("metadata" in r.field_path for r in report.results)
    
    @pytest.mark.asyncio
    async def test_invalid_complexity(self):
        """Test detection of invalid complexity value."""
        adapter = ValidationFrameworkAdapter()
        plan_data = {
            "metadata": {
                "complexity": "invalid_value"
            },
            "phases": []
        }
        
        report = await adapter.validate_plan(plan_data, validation_levels=["schema"])
        assert report.is_valid is False
        errors = [r for r in report.results if r.level == ValidationLevel.ERROR]
        assert any("complexity" in r.field_path for r in errors)


class TestBusinessRuleValidation:
    """Test business rule validation functionality."""
    
    @pytest.mark.asyncio
    async def test_sequential_phase_numbers(self):
        """Test validation of sequential phase numbers."""
        adapter = ValidationFrameworkAdapter()
        plan_data = {
            "metadata": {
                "plan_name": "Test",
                "complexity": "low",
                "estimated_hours": 10
            },
            "phases": [
                {"phase_number": 1, "phase_name": "P1", "tasks": []},
                {"phase_number": 3, "phase_name": "P2", "tasks": []},  # Skip 2
            ]
        }
        
        report = await adapter.validate_plan(plan_data, validation_levels=["business_rule"])
        assert report.is_valid is False
        assert any("Phase numbers not sequential" in r.message for r in report.results)
    
    @pytest.mark.asyncio
    async def test_high_time_estimate_warning(self):
        """Test warning for very high time estimates."""
        adapter = ValidationFrameworkAdapter()
        plan_data = {
            "metadata": {
                "estimated_hours": 2000  # Very high
            },
            "phases": [
                {
                    "phase_number": 1,
                    "tasks": [
                        {"task_id": "T1", "estimated_hours": 2000}
                    ]
                }
            ]
        }
        
        report = await adapter.validate_plan(plan_data, validation_levels=["business_rule"])
        warnings = [r for r in report.results if r.level == ValidationLevel.WARNING]
        assert any("high time estimate" in r.message.lower() for r in warnings)


class TestCrossFieldValidation:
    """Test cross-field validation functionality."""
    
    @pytest.mark.asyncio
    async def test_metadata_hours_mismatch(self):
        """Test detection of metadata/calculated hours mismatch."""
        adapter = ValidationFrameworkAdapter()
        plan_data = {
            "metadata": {
                "estimated_hours": 100  # Doesn't match sum
            },
            "phases": [
                {
                    "phase_number": 1,
                    "tasks": [
                        {"task_id": "T1", "estimated_hours": 5},
                        {"task_id": "T2", "estimated_hours": 10}
                    ]
                }
            ]
        }
        
        report = await adapter.validate_plan(plan_data, validation_levels=["cross_field"])
        warnings = [r for r in report.results if r.level == ValidationLevel.WARNING]
        assert any("estimated_hours" in r.field_path for r in warnings)
    
    @pytest.mark.asyncio
    async def test_invalid_task_dependency(self):
        """Test detection of invalid task dependencies."""
        adapter = ValidationFrameworkAdapter()
        plan_data = {
            "metadata": {},
            "phases": [
                {
                    "phase_number": 1,
                    "tasks": [
                        {
                            "task_id": "T1",
                            "dependencies": ["T_NONEXISTENT"]  # Invalid
                        }
                    ]
                }
            ]
        }
        
        report = await adapter.validate_plan(plan_data, validation_levels=["cross_field"])
        errors = [r for r in report.results if r.level == ValidationLevel.ERROR]
        assert any("Invalid dependency" in r.message for r in errors)


class TestPhaseTransitionValidation:
    """Test phase transition validation."""
    
    def test_valid_phase_transition(self):
        """Test valid phase transition."""
        adapter = ValidationFrameworkAdapter()
        phase_data = {"status": "complete"}
        
        report = adapter.validate_phase_transition(
            current_phase=1,
            target_phase=2,
            phase_data=phase_data
        )
        
        assert report.is_valid is True
        assert report.errors == 0
    
    def test_phase_skip_not_allowed(self):
        """Test that skipping phases is not allowed."""
        adapter = ValidationFrameworkAdapter()
        phase_data = {"status": "complete"}
        
        report = adapter.validate_phase_transition(
            current_phase=1,
            target_phase=3,  # Skip phase 2
            phase_data=phase_data
        )
        
        assert report.is_valid is False
        assert any("Cannot skip phases" in r.message for r in report.results)
    
    def test_incomplete_phase_blocks_transition(self):
        """Test that incomplete phase blocks transition."""
        adapter = ValidationFrameworkAdapter()
        phase_data = {"status": "in_progress"}  # Not complete
        
        report = adapter.validate_phase_transition(
            current_phase=1,
            target_phase=2,
            phase_data=phase_data
        )
        
        assert report.is_valid is False
        assert any("not complete" in r.message.lower() for r in report.results)


class TestValidationReport:
    """Test ValidationReport functionality."""
    
    def test_report_add_result(self):
        """Test adding results to report."""
        report = ValidationReport(is_valid=True)
        
        result = ValidationResult(
            validation_type=ValidationType.SCHEMA,
            level=ValidationLevel.ERROR,
            field_path="test.field",
            message="Test error"
        )
        
        report.add_result(result)
        assert report.errors == 1
        assert report.is_valid is False
    
    def test_report_blocking_errors(self):
        """Test getting blocking errors."""
        report = ValidationReport(is_valid=True)
        
        error = ValidationResult(
            validation_type=ValidationType.SCHEMA,
            level=ValidationLevel.ERROR,
            field_path="test",
            message="Error"
        )
        warning = ValidationResult(
            validation_type=ValidationType.SCHEMA,
            level=ValidationLevel.WARNING,
            field_path="test",
            message="Warning"
        )
        
        report.add_result(error)
        report.add_result(warning)
        
        blocking = report.get_blocking_errors()
        assert len(blocking) == 1
        assert blocking[0].level == ValidationLevel.ERROR
    
    def test_report_summary(self):
        """Test report summary generation."""
        report = ValidationReport(is_valid=True)
        summary = report.get_summary()
        assert "✅" in summary
        assert "passed" in summary.lower()
