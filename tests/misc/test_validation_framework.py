"""
Unit Tests for Validation Framework

Tests all validators from Phase 2: Validation Framework.

Version: 1.0.0
Author: Asif Hussain
"""

import pytest
from src.orchestrators.validation_framework import (
    ValidationResult,
    PlanMetadataValidator,
    PlanPhaseValidator,
    PlanDoRDoDValidator,
    CompositePlanValidator,
    TaskImplementationValidator,
    TDDPhaseValidator,
    TDDTestValidator,
    ConfigurationValidator,
    TransactionValidator,
    validate_plan,
    validate_task,
    validate_tdd_transition,
    validate_code_quality
)


# ============================================================================
# ValidationResult Tests
# ============================================================================

def test_validation_result_defaults():
    """Test ValidationResult initialization."""
    result = ValidationResult(valid=True)
    assert result.valid is True
    assert result.errors == []
    assert result.warnings == []
    assert result.checks_performed == 0


def test_validation_result_add_error():
    """Test adding errors invalidates result."""
    result = ValidationResult(valid=True)
    result.add_error("Test error")
    
    assert result.valid is False
    assert "Test error" in result.errors


def test_validation_result_merge():
    """Test merging validation results."""
    result1 = ValidationResult(valid=True, checks_performed=2)
    result1.add_warning("Warning 1")
    
    result2 = ValidationResult(valid=False, checks_performed=3)
    result2.add_error("Error 1")
    
    result1.merge(result2)
    
    assert result1.valid is False
    assert result1.checks_performed == 5
    assert "Warning 1" in result1.warnings
    assert "Error 1" in result1.errors


# ============================================================================
# Plan Validator Tests
# ============================================================================

def test_plan_metadata_validator_valid():
    """Test valid plan metadata."""
    plan_data = {
        "metadata": {
            "title": "Test Feature",
            "description": "This is a test description with enough characters",
            "author": "Test Author",
            "priority": "high"
        }
    }
    
    validator = PlanMetadataValidator()
    result = validator.validate(plan_data)
    
    assert result.valid is True
    assert len(result.errors) == 0


def test_plan_metadata_validator_missing_title():
    """Test missing title error."""
    plan_data = {
        "metadata": {
            "description": "Test"
        }
    }
    
    validator = PlanMetadataValidator()
    result = validator.validate(plan_data)
    
    assert result.valid is False
    assert any("title" in err.lower() for err in result.errors)


def test_plan_phase_validator_valid():
    """Test valid plan phases."""
    plan_data = {
        "phases": [
            {
                "name": "Phase 1",
                "tasks": [
                    {"description": "Task 1", "type": "implementation"}
                ]
            }
        ]
    }
    
    validator = PlanPhaseValidator()
    result = validator.validate(plan_data)
    
    assert result.valid is True


def test_plan_phase_validator_empty_tasks():
    """Test empty tasks error."""
    plan_data = {
        "phases": [
            {
                "name": "Phase 1",
                "tasks": []
            }
        ]
    }
    
    validator = PlanPhaseValidator()
    result = validator.validate(plan_data)
    
    assert result.valid is False


def test_composite_plan_validator():
    """Test composite plan validation."""
    plan_data = {
        "metadata": {
            "title": "Test Plan",
            "description": "A comprehensive test plan"
        },
        "phases": [
            {
                "name": "Implementation",
                "tasks": [{"description": "Implement feature"}]
            }
        ],
        "definition_of_ready": ["Req 1", "Req 2"],
        "definition_of_done": ["Done 1", "Done 2"]
    }
    
    result = validate_plan(plan_data)
    
    assert result.valid is True
    assert result.checks_performed > 0


# ============================================================================
# Task Validator Tests
# ============================================================================

def test_task_validator_data_operations():
    """Test data operations warning."""
    task = {
        "description": "Insert data into database and update records",
        "type": "implementation"
    }
    
    result = validate_task(task)
    
    # Should warn about missing transaction
    assert any("transaction" in warn.lower() for warn in result.warnings)


def test_task_validator_security():
    """Test security requirements."""
    task = {
        "description": "Implement authentication with password validation",
        "type": "implementation"
    }
    
    result = validate_task(task)
    
    assert result.metadata.get("requires_security_review") is True


def test_task_validator_anemic_model():
    """Test anemic model detection."""
    task = {
        "description": "Create getters and setters for User properties",
        "type": "implementation"
    }
    
    result = validate_task(task)
    
    # Should warn about anemic models
    assert any("anemic" in warn.lower() for warn in result.warnings)


# ============================================================================
# TDD Validator Tests
# ============================================================================

def test_tdd_phase_validator_valid_transition():
    """Test valid TDD phase transition."""
    result = validate_tdd_transition("red", "green")
    
    assert result.valid is True


def test_tdd_phase_validator_invalid_transition():
    """Test invalid TDD phase transition."""
    result = validate_tdd_transition("red", "refactor")
    
    assert result.valid is False
    assert any("invalid transition" in err.lower() for err in result.errors)


def test_tdd_test_validator():
    """Test TDD test file validation."""
    validator = TDDTestValidator()
    
    test_files = ["test_feature.py", "test_utils.py"]
    impl_files = ["feature.py", "utils.py"]
    
    result = validator.validate(test_files, impl_files)
    
    assert result.valid is True
    assert result.metadata["test_files"] == 2
    assert result.metadata["implementation_files"] == 2


def test_tdd_test_validator_naming():
    """Test test file naming warnings."""
    validator = TDDTestValidator()
    
    test_files = ["feature_test.py"]  # Wrong naming
    impl_files = ["feature.py"]
    
    result = validator.validate(test_files, impl_files)
    
    # Should warn about naming
    assert any("test_" in warn for warn in result.warnings)


# ============================================================================
# Code Quality Validator Tests
# ============================================================================

def test_configuration_validator_hard_coded_url():
    """Test hard-coded URL detection."""
    code = '''
    def connect():
        url = "https://api.example.com/endpoint"
        return requests.get(url)
    '''
    
    result = validate_code_quality(code)
    
    assert any("url" in warn.lower() for warn in result.warnings)


def test_configuration_validator_hard_coded_password():
    """Test hard-coded password detection."""
    code = '''
    password = "MySecretPassword123"
    '''
    
    result = validate_code_quality(code)
    
    assert any("password" in warn.lower() for warn in result.warnings)


def test_transaction_validator_multiple_operations():
    """Test transaction validator detects multiple DB ops."""
    code = '''
    def update_user(user_id, data):
        cursor.execute("UPDATE users SET ...")
        cursor.execute("INSERT INTO audit_log ...")
        cursor.execute("DELETE FROM cache ...")
    '''
    
    result = validate_code_quality(code)
    
    assert any("transaction" in warn.lower() for warn in result.warnings)


def test_transaction_validator_with_transaction():
    """Test transaction validator passes with explicit transaction."""
    code = '''
    def update_user(user_id, data):
        with transaction.BeginTransaction():
            cursor.execute("UPDATE users SET ...")
            cursor.execute("INSERT INTO audit_log ...")
            transaction.commit()
    '''
    
    result = validate_code_quality(code)
    
    # Should not warn about transactions
    assert not any("transaction" in warn.lower() and "without" in warn.lower() 
                  for warn in result.warnings)


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_plan_validation():
    """Test complete plan validation workflow."""
    plan_data = {
        "metadata": {
            "title": "User Authentication Feature",
            "description": "Implement secure user authentication with JWT tokens",
            "author": "Dev Team",
            "priority": "high"
        },
        "phases": [
            {
                "name": "Implementation",
                "tasks": [
                    {
                        "description": "Implement password hashing and validation",
                        "type": "implementation"
                    },
                    {
                        "description": "Create JWT token generation",
                        "type": "implementation"
                    }
                ]
            },
            {
                "name": "Testing",
                "tasks": [
                    {
                        "description": "Unit tests for authentication",
                        "type": "testing"
                    }
                ]
            }
        ],
        "definition_of_ready": [
            "Requirements documented",
            "Security requirements reviewed"
        ],
        "definition_of_done": [
            "All tests passing",
            "Code reviewed",
            "Security audit completed"
        ]
    }
    
    result = validate_plan(plan_data)
    
    assert result.valid is True
    assert result.metadata["dor_items"] == 2
    assert result.metadata["dod_items"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
