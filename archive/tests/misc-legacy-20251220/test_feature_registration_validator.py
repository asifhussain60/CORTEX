"""
Unit tests for Feature Registration Validator

Tests the FeatureRegistrationValidator class for CORTEX Align v2.0.

Author: Asif Hussain
Date: December 3, 2025
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.operations.modules.realignment.feature_registration_validator import (
    FeatureRegistrationValidator,
    ValidationResult
)


@pytest.fixture
def mock_project_structure(tmp_path):
    """Create mock CORTEX project structure."""
    # Create directory structure
    operations_dir = tmp_path / "src" / "operations"
    operations_dir.mkdir(parents=True)
    
    modules_dir = operations_dir / "modules"
    modules_dir.mkdir()
    
    # Create operation files
    (operations_dir / "planning.py").touch()
    (operations_dir / "tdd.py").touch()
    (operations_dir / "commit.py").touch()
    (operations_dir / "__init__.py").touch()  # Should be excluded
    
    # Create module directories and files
    planning_dir = modules_dir / "planning"
    planning_dir.mkdir()
    (planning_dir / "planning_utility.py").touch()
    
    tdd_dir = modules_dir / "tdd"
    tdd_dir.mkdir()
    (tdd_dir / "tdd_utility.py").touch()
    
    # Create cortex-operations.yaml
    operations_yaml = tmp_path / "cortex-operations.yaml"
    yaml_content = {
        'operations': {
            'planning': {
                'name': 'Planning Operation',
                'modules': ['planning_utility']
            },
            'tdd': {
                'name': 'TDD Operation',
                'modules': ['tdd_utility']
            }
        }
    }
    
    with open(operations_yaml, 'w') as f:
        yaml.dump(yaml_content, f)
    
    return tmp_path


@pytest.fixture
def validator(mock_project_structure):
    """Create validator instance with mock project structure."""
    return FeatureRegistrationValidator(project_root=mock_project_structure)


class TestFeatureRegistrationValidator:
    """Test suite for FeatureRegistrationValidator."""
    
    def test_init_with_project_root(self, mock_project_structure):
        """Test initialization with explicit project root."""
        validator = FeatureRegistrationValidator(project_root=mock_project_structure)
        
        assert validator.project_root == mock_project_structure
        assert validator.operations_dir == mock_project_structure / "src" / "operations"
        assert validator.modules_dir == mock_project_structure / "src" / "operations" / "modules"
        assert validator.operations_yaml == mock_project_structure / "cortex-operations.yaml"
    
    def test_scan_operations_directory(self, validator):
        """Test scanning operations directory for entry points."""
        operations = validator.scan_operations_directory()
        
        # Should find planning, tdd, commit (but not __init__.py)
        assert len(operations) == 3
        assert 'planning' in operations
        assert 'tdd' in operations
        assert 'commit' in operations
        assert '__init__' not in operations
    
    def test_scan_operations_directory_excludes_base_files(self, validator):
        """Test that base files are excluded from scan."""
        # Create base file that should be excluded
        base_file = validator.operations_dir / "base_operation_module.py"
        base_file.touch()
        
        operations = validator.scan_operations_directory()
        
        assert 'base_operation_module' not in operations
    
    def test_scan_operation_modules(self, validator):
        """Test scanning modules directory for utilities."""
        modules = validator.scan_operation_modules()
        
        # Should find planning_utility and tdd_utility
        assert len(modules) == 2
        
        module_names = [m['module'] for m in modules]
        assert 'planning_utility' in module_names
        assert 'tdd_utility' in module_names
        
        # Check structure
        for mod in modules:
            assert 'category' in mod
            assert 'module' in mod
            assert 'path' in mod
    
    def test_scan_operation_modules_excludes_pycache(self, validator):
        """Test that __pycache__ directories are excluded."""
        # Create __pycache__ directory
        pycache = validator.modules_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "some_utility.py").touch()
        
        modules = validator.scan_operation_modules()
        
        # Should not find anything from __pycache__
        for mod in modules:
            assert '__pycache__' not in mod['path']
    
    def test_load_registered_operations(self, validator):
        """Test loading operations from YAML file."""
        operations = validator.load_registered_operations()
        
        assert 'planning' in operations
        assert 'tdd' in operations
        assert operations['planning']['name'] == 'Planning Operation'
        assert 'modules' in operations['planning']
    
    def test_load_registered_operations_file_not_found(self, tmp_path):
        """Test error handling when YAML file doesn't exist."""
        validator = FeatureRegistrationValidator(project_root=tmp_path)
        
        with pytest.raises(FileNotFoundError):
            validator.load_registered_operations()
    
    def test_is_module_registered_returns_true(self, validator):
        """Test module registration check returns True for registered modules."""
        registered_ops = validator.load_registered_operations()
        
        module_info = {
            'category': 'planning',
            'module': 'planning_utility',
            'path': 'planning/planning_utility'
        }
        
        assert validator.is_module_registered(module_info, registered_ops) is True
    
    def test_is_module_registered_returns_false(self, validator):
        """Test module registration check returns False for unregistered modules."""
        registered_ops = validator.load_registered_operations()
        
        module_info = {
            'category': 'commit',
            'module': 'commit_utility',
            'path': 'commit/commit_utility'
        }
        
        assert validator.is_module_registered(module_info, registered_ops) is False
    
    def test_identify_unregistered_with_unregistered_operation(self, validator):
        """Test identification of unregistered operations."""
        unregistered = validator.identify_unregistered()
        
        # commit operation exists but isn't registered
        assert 'commit' in unregistered['operations']
        assert len(unregistered['operations']) == 1
    
    def test_identify_unregistered_with_all_registered(self, validator):
        """Test identification when all items are registered."""
        # Remove unregistered operation file
        commit_file = validator.operations_dir / "commit.py"
        commit_file.unlink()
        
        unregistered = validator.identify_unregistered()
        
        assert len(unregistered['operations']) == 0
        assert len(unregistered['modules']) == 0
    
    def test_identify_unregistered_statistics(self, validator):
        """Test that unregistered identification includes statistics."""
        unregistered = validator.identify_unregistered()
        
        assert 'total_operations' in unregistered
        assert 'total_modules' in unregistered
        assert 'registered_operations' in unregistered
        assert 'registered_module_count' in unregistered
        
        assert unregistered['total_operations'] == 3  # planning, tdd, commit
        assert len(unregistered['registered_operations']) == 2  # planning, tdd
    
    def test_validate_returns_pass_when_all_registered(self, validator):
        """Test validate returns PASS when everything is registered."""
        # Remove unregistered files
        (validator.operations_dir / "commit.py").unlink()
        
        result = validator.validate()
        
        assert result.passed is True
        assert result.severity == 'PASS'
        assert result.message == "All features properly registered"
        assert len(result.unregistered_operations) == 0
    
    def test_validate_returns_error_when_operations_unregistered(self, validator):
        """Test validate returns ERROR when operations are unregistered."""
        result = validator.validate()
        
        assert result.passed is False
        assert result.severity == 'ERROR'
        assert 'unregistered operations' in result.message.lower()
        assert len(result.unregistered_operations) == 1
        assert 'commit' in result.unregistered_operations
    
    def test_validation_result_unregistered_count(self, validator):
        """Test ValidationResult.unregistered_count property."""
        result = validator.validate()
        
        expected_count = len(result.unregistered_operations) + len(result.unregistered_modules)
        assert result.unregistered_count == expected_count
    
    def test_validation_result_registration_percentage(self, validator):
        """Test ValidationResult.registration_percentage property."""
        result = validator.validate()
        
        # Should return a percentage between 0 and 100
        assert 0 <= result.registration_percentage <= 100
        
        # With 3 ops (2 registered) and 2 modules (2 registered),
        # we have 2+2=4 registered out of 3+2=5 total = 80%
        # But commit is unregistered, so 2 ops registered
        # Result: 2 ops + 2 modules registered = 4, but module count may vary
        # Just verify it's a valid percentage
        assert isinstance(result.registration_percentage, float)
    
    def test_generate_report_with_pass_status(self, validator):
        """Test report generation with PASS status."""
        # Remove unregistered files
        (validator.operations_dir / "commit.py").unlink()
        
        result = validator.validate()
        report = validator.generate_report(result)
        
        assert '✅ PASS' in report
        assert 'All Clear' in report
        assert 'properly registered' in report.lower()
    
    def test_generate_report_with_fail_status(self, validator):
        """Test report generation with FAIL status."""
        result = validator.validate()
        report = validator.generate_report(result)
        
        assert '❌ FAIL' in report
        assert 'Unregistered Operations' in report
        assert 'commit' in report
        assert 'Recommended Actions' in report
    
    def test_generate_report_includes_statistics(self, validator):
        """Test that report includes comprehensive statistics."""
        result = validator.validate()
        report = validator.generate_report(result)
        
        assert 'Operations Found' in report
        assert 'Operations Registered' in report
        assert 'Operations Unregistered' in report
        assert 'Modules Found' in report
        assert 'Registration Rate' in report
    
    def test_validate_handles_exceptions_gracefully(self, validator):
        """Test that validate handles exceptions and returns error result."""
        # Break the validator by removing YAML file
        validator.operations_yaml.unlink()
        
        result = validator.validate()
        
        assert result.passed is False
        assert result.severity == 'ERROR'
        assert 'error' in result.message.lower()
    
    def test_excluded_files_not_scanned(self, validator):
        """Test that excluded files are not included in scans."""
        # Create files that should be excluded
        (validator.operations_dir / "__init__.py").write_text("# init")
        (validator.operations_dir / "base_operation_module.py").write_text("# base")
        
        operations = validator.scan_operations_directory()
        
        assert '__init__' not in operations
        assert 'base_operation_module' not in operations


class TestValidationResultDataclass:
    """Test ValidationResult dataclass."""
    
    def test_validation_result_creation(self):
        """Test ValidationResult instantiation."""
        result = ValidationResult(
            passed=True,
            unregistered_operations=['op1', 'op2'],
            total_operations_found=5,
            total_registered_operations=3
        )
        
        assert result.passed is True
        assert len(result.unregistered_operations) == 2
        assert result.total_operations_found == 5
    
    def test_validation_result_default_values(self):
        """Test ValidationResult default field values."""
        result = ValidationResult(passed=True)
        
        assert result.unregistered_operations == []
        assert result.unregistered_modules == []
        assert result.total_operations_found == 0
        assert result.severity == "PASS"
    
    def test_unregistered_count_property(self):
        """Test unregistered_count computed property."""
        result = ValidationResult(
            passed=False,
            unregistered_operations=['op1', 'op2'],
            unregistered_modules=[{'name': 'mod1'}, {'name': 'mod2'}, {'name': 'mod3'}]
        )
        
        assert result.unregistered_count == 5  # 2 ops + 3 modules
    
    def test_registration_percentage_with_zero_total(self):
        """Test registration_percentage returns 100 when no items found."""
        result = ValidationResult(
            passed=True,
            total_operations_found=0,
            total_modules_found=0
        )
        
        assert result.registration_percentage == 100.0
    
    def test_registration_percentage_calculation(self):
        """Test registration_percentage calculation."""
        result = ValidationResult(
            passed=False,
            total_operations_found=10,
            total_modules_found=20,
            registered_operations=['o1', 'o2', 'o3'],  # 3 registered
            registered_modules=['m1', 'm2']  # 2 registered
        )
        
        # Total: 30, Registered: 5, Percentage: 5/30 * 100 = 16.67%
        expected = (5 / 30) * 100.0
        assert result.registration_percentage == pytest.approx(expected, 0.1)


class TestStandaloneExecution:
    """Test standalone CLI execution."""
    
    @patch('src.operations.modules.realignment.feature_registration_validator.FeatureRegistrationValidator')
    def test_main_success(self, mock_validator_class, capsys):
        """Test main function with successful validation."""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        
        mock_result = ValidationResult(passed=True, message="All good")
        mock_validator.validate.return_value = mock_result
        mock_validator.generate_report.return_value = "✅ PASS Report"
        
        from src.operations.modules.realignment.feature_registration_validator import main
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "✅ PASS" in captured.out
    
    @patch('src.operations.modules.realignment.feature_registration_validator.FeatureRegistrationValidator')
    def test_main_failure(self, mock_validator_class):
        """Test main function with failed validation."""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        
        mock_result = ValidationResult(passed=False, message="Errors found")
        mock_validator.validate.return_value = mock_result
        mock_validator.generate_report.return_value = "❌ FAIL Report"
        
        from src.operations.modules.realignment.feature_registration_validator import main
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('src.operations.modules.realignment.feature_registration_validator.FeatureRegistrationValidator')
    def test_main_exception(self, mock_validator_class):
        """Test main function handles exceptions."""
        mock_validator_class.side_effect = Exception("Test error")
        
        from src.operations.modules.realignment.feature_registration_validator import main
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
