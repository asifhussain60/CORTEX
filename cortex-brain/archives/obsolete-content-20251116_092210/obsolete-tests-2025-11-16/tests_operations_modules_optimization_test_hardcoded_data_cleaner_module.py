"""
Tests for Hardcoded Data Cleaner Module

Validates aggressive detection of:
- Hardcoded paths
- Mock data in production
- Fallback mechanisms
- Placeholder values

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.operations.modules.optimization.hardcoded_data_cleaner_module import (
    HardcodedDataCleanerModule,
    HardcodedViolation,
    HardcodedDataMetrics
)
from src.operations.base_operation_module import OperationStatus


class TestHardcodedDataCleanerModule:
    """Test suite for hardcoded data detection."""
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create temporary project structure."""
        # Create directory structure
        src_dir = tmp_path / 'src'
        tests_dir = tmp_path / 'tests'
        src_dir.mkdir()
        tests_dir.mkdir()
        
        return tmp_path
    
    @pytest.fixture
    def cleaner(self, temp_project):
        """Create cleaner module instance."""
        return HardcodedDataCleanerModule()
    
    def test_module_metadata(self, cleaner):
        """Test module metadata is correct."""
        metadata = cleaner.get_metadata()
        
        assert metadata.module_id == "hardcoded_data_cleaner"
        assert "hardcoded" in metadata.name.lower()
        assert metadata.version == "1.0.0"
        assert "hardcoded-data" in metadata.tags
    
    def test_detect_hardcoded_windows_path(self, temp_project, cleaner):
        """Test detection of hardcoded Windows absolute paths."""
        test_file = temp_project / 'src' / 'example.py'
        test_file.write_text("""
def load_config():
    path = "C:\\\\Users\\\\asif\\\\config.json"
    return load(path)
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        assert result.success is True  # Success with violations
        metrics = result.data['metrics']
        assert metrics['violations_found'] >= 1
        assert metrics['critical_violations'] >= 1
        
        # Check violation details
        violations = result.data['violations']
        path_violations = [v for v in violations if v['type'] == 'hardcoded_path']
        assert len(path_violations) >= 1
        # The code snippet contains escaped backslashes (\\\\)
        assert 'C:\\\\' in path_violations[0]['code'] or 'C:\\Users' in path_violations[0]['code']
    
    def test_detect_hardcoded_unix_path(self, temp_project, cleaner):
        """Test detection of hardcoded Unix absolute paths."""
        test_file = temp_project / 'src' / 'example.py'
        test_file.write_text("""
def load_data():
    data_path = "/home/user/data/file.json"
    return read(data_path)
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        metrics = result.data['metrics']
        assert metrics['violations_found'] >= 1
        assert metrics['critical_violations'] >= 1
        
        violations = result.data['violations']
        assert any('/home/user' in v['code'] for v in violations)
    
    def test_detect_mock_in_production_code(self, temp_project, cleaner):
        """Test detection of mock data in non-test files."""
        test_file = temp_project / 'src' / 'service.py'
        test_file.write_text("""
from unittest.mock import Mock, patch

class UserService:
    def get_user(self, user_id):
        mock_user = Mock()
        mock_user.name = "Test User"
        return mock_user
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        metrics = result.data['metrics']
        assert metrics['violations_found'] >= 1
        assert metrics['critical_violations'] >= 1
        
        violations = result.data['violations']
        mock_violations = [v for v in violations if v['type'] == 'mock_data_in_production']
        assert len(mock_violations) >= 1
    
    def test_allow_mock_in_test_files(self, temp_project, cleaner):
        """Test that mocks are allowed in test files."""
        test_file = temp_project / 'tests' / 'test_service.py'
        test_file.write_text("""
from unittest.mock import Mock, patch

def test_user_service():
    mock_user = Mock()
    mock_user.name = "Test User"
    assert mock_user.name == "Test User"
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['tests'],
            'fail_on_critical': False
        })
        
        # Mocks in test files should not be flagged as production violations
        violations = result.data['violations']
        mock_violations = [v for v in violations if v['type'] == 'mock_data_in_production']
        assert len(mock_violations) == 0
    
    def test_detect_fallback_with_get(self, temp_project, cleaner):
        """Test detection of .get() with hardcoded fallback values."""
        test_file = temp_project / 'src' / 'config.py'
        test_file.write_text("""
def get_database_url():
    config = load_config()
    return config.get('database_url', 'postgresql://localhost/default')
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        metrics = result.data['metrics']
        assert metrics['violations_found'] >= 1
        
        violations = result.data['violations']
        fallback_violations = [v for v in violations if v['type'] == 'fallback_value']
        assert len(fallback_violations) >= 1
        assert fallback_violations[0]['severity'] == 'HIGH'
    
    def test_detect_hardcoded_return_dict(self, temp_project, cleaner):
        """Test detection of functions returning large hardcoded dicts."""
        test_file = temp_project / 'src' / 'defaults.py'
        test_file.write_text("""
def get_default_settings():
    return {
        'theme': 'dark',
        'language': 'en',
        'timeout': 30,
        'retries': 3,
        'cache': True,
        'debug': False
    }
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        metrics = result.data['metrics']
        assert metrics['violations_found'] >= 1
        
        violations = result.data['violations']
        return_violations = [v for v in violations if v['type'] == 'hardcoded_return_value']
        assert len(return_violations) >= 1
        assert return_violations[0]['severity'] == 'HIGH'
    
    def test_detect_placeholder_keywords(self, temp_project, cleaner):
        """Test detection of placeholder keywords like 'test', 'dummy', 'fake'."""
        test_file = temp_project / 'src' / 'api.py'
        test_file.write_text("""
def connect_to_api():
    api_key = "test"
    endpoint = "dummy"
    return connect(endpoint, api_key)
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        metrics = result.data['metrics']
        assert metrics['violations_found'] >= 1
        
        violations = result.data['violations']
        placeholder_violations = [v for v in violations if v['type'] == 'placeholder_data']
        assert len(placeholder_violations) >= 1
    
    def test_exclude_paths_with_path_constructor(self, temp_project, cleaner):
        """Test that paths using Path() are not flagged."""
        test_file = temp_project / 'src' / 'good_code.py'
        test_file.write_text("""
from pathlib import Path

def get_config_path():
    return Path("config") / "settings.json"
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        violations = result.data['violations']
        path_violations = [v for v in violations if 'config' in v['code'] and v['type'] == 'hardcoded_path']
        # Should not flag relative paths in Path()
        assert len(path_violations) == 0
    
    def test_fail_on_critical_violations(self, temp_project, cleaner):
        """Test that fail_on_critical=True fails when critical violations found."""
        test_file = temp_project / 'src' / 'bad.py'
        test_file.write_text("""
path = "D:\\\\PROJECTS\\\\CORTEX\\\\data.json"
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': True
        })
        
        assert result.success is False
        assert result.status == OperationStatus.FAILED
        assert 'CRITICAL' in result.message
    
    def test_no_violations_returns_success(self, temp_project, cleaner):
        """Test that clean code returns success."""
        test_file = temp_project / 'src' / 'clean.py'
        test_file.write_text("""
from pathlib import Path

def load_config(config_path: Path):
    with open(config_path, 'r') as f:
        return json.load(f)
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': True
        })
        
        assert result.success is True
        metrics = result.data['metrics']
        assert metrics['violations_found'] == 0
        assert metrics['clean_files'] >= 1
    
    def test_exclude_patterns_work(self, temp_project, cleaner):
        """Test that exclude patterns prevent scanning."""
        # Create __pycache__ directory with bad code
        cache_dir = temp_project / 'src' / '__pycache__'
        cache_dir.mkdir()
        bad_file = cache_dir / 'cached.py'
        bad_file.write_text("""
path = "C:\\\\Users\\\\bad\\\\path.txt"
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'exclude_patterns': ['__pycache__'],
            'fail_on_critical': True
        })
        
        # Should succeed because __pycache__ is excluded
        assert result.success is True
        metrics = result.data['metrics']
        # Violation should not be found due to exclusion
        violations = result.data['violations']
        assert not any('__pycache__' in str(v['file']) for v in violations)
    
    def test_multiple_violations_in_single_file(self, temp_project, cleaner):
        """Test detection of multiple violations in one file."""
        test_file = temp_project / 'src' / 'multi_bad.py'
        test_file.write_text("""
from unittest.mock import Mock

def bad_function():
    path = "C:\\\\hardcoded\\\\path.txt"
    mock_obj = Mock()
    fallback = config.get('value', 'hardcoded_default')
    placeholder = "test"
    return {
        'path': path,
        'mock': mock_obj,
        'fallback': fallback,
        'placeholder': placeholder,
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
        'key4': 'value4'
    }
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        metrics = result.data['metrics']
        assert metrics['violations_found'] >= 4
        
        violations = result.data['violations']
        violation_types = {v['type'] for v in violations}
        
        # Should detect multiple types
        assert 'hardcoded_path' in violation_types or 'mock_data_in_production' in violation_types
    
    def test_report_generation(self, temp_project, cleaner):
        """Test that report is generated with violations."""
        test_file = temp_project / 'src' / 'example.py'
        test_file.write_text("""
path = "C:\\\\Users\\\\example\\\\data.json"
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        report = result.data.get('report', '')
        assert len(report) > 0
        assert '# Hardcoded Data Scan Report' in report
        assert 'Summary' in report
        assert 'Violations by Type' in report
    
    def test_suggested_fixes_provided(self, temp_project, cleaner):
        """Test that violations include suggested fixes."""
        test_file = temp_project / 'src' / 'example.py'
        test_file.write_text("""
def get_path():
    return "D:\\\\PROJECTS\\\\data\\\\file.txt"
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        violations = result.data['violations']
        assert len(violations) >= 1
        
        for violation in violations:
            assert 'fix' in violation
            assert len(violation['fix']) > 0
            # Suggested fix should mention Path or config
            assert 'Path' in violation['fix'] or 'config' in violation['fix']
    
    def test_severity_categorization(self, temp_project, cleaner):
        """Test that violations are categorized by severity correctly."""
        test_file = temp_project / 'src' / 'mixed.py'
        test_file.write_text("""
from unittest.mock import Mock

# CRITICAL: Hardcoded path
path = "C:\\\\Users\\\\data.json"

# CRITICAL: Mock in production
mock = Mock()

# HIGH: Fallback value
value = config.get('key', 'hardcoded')

# MEDIUM: Placeholder
name = "test"
""")
        
        result = cleaner.execute({
            'project_root': temp_project,
            'scan_paths': ['src'],
            'fail_on_critical': False
        })
        
        metrics = result.data['metrics']
        assert metrics['critical_violations'] >= 1
        assert metrics['high_violations'] >= 1
        assert metrics['medium_violations'] >= 1
    
    def test_prerequisite_validation(self, cleaner, temp_project):
        """Test prerequisite validation."""
        is_valid, issues = cleaner.validate_prerequisites({
            'project_root': temp_project
        })
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_prerequisite_validation_failure(self):
        """Test prerequisite validation with invalid project root."""
        cleaner = HardcodedDataCleanerModule()
        
        # Test with nonexistent path (use absolute Windows path that definitely doesn't exist)
        is_valid, issues = cleaner.validate_prerequisites({
            'project_root': Path('Z:/this/path/does/not/exist/anywhere')
        })
        
        assert is_valid is False
        assert len(issues) > 0
        
        # Test with missing project_root key
        is_valid2, issues2 = cleaner.validate_prerequisites({})
        assert is_valid2 is False
        assert len(issues2) > 0
    
    def test_rollback_returns_true(self, cleaner):
        """Test rollback (no-op for scanner)."""
        result = cleaner.rollback({})
        assert result is True


class TestHardcodedPathPatterns:
    """Test specific path pattern detection."""
    
    @pytest.fixture
    def cleaner(self, tmp_path):
        return HardcodedDataCleanerModule()
    
    def test_detect_project_path(self, tmp_path, cleaner):
        """Test detection of hardcoded PROJECTS directory paths."""
        test_file = tmp_path / 'src'
        test_file.mkdir()
        test_file = test_file / 'code.py'
        test_file.write_text("""
path = "D:\\\\PROJECTS\\\\CORTEX\\\\data.json"
""")
        
        result = cleaner.execute({
            'project_root': tmp_path,
            'scan_paths': ['src']
        })
        
        violations = result.data['violations']
        assert any('PROJECTS' in v['code'] for v in violations)
    
    def test_ignore_relative_paths(self, tmp_path, cleaner):
        """Test that relative paths are not flagged."""
        test_file = tmp_path / 'src'
        test_file.mkdir()
        test_file = test_file / 'code.py'
        test_file.write_text("""
path = "data/file.json"
another = "config/settings.yaml"
""")
        
        result = cleaner.execute({
            'project_root': tmp_path,
            'scan_paths': ['src']
        })
        
        metrics = result.data['metrics']
        # Relative paths should not be flagged
        assert metrics['violations_found'] == 0 or all(
            v['type'] != 'hardcoded_path' for v in result.data['violations']
        )


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def cleaner(self, tmp_path):
        return HardcodedDataCleanerModule()
    
    def test_handle_syntax_error_file(self, tmp_path, cleaner):
        """Test graceful handling of files with syntax errors."""
        test_file = tmp_path / 'src'
        test_file.mkdir()
        test_file = test_file / 'broken.py'
        test_file.write_text("""
def broken_function(
    # Missing closing parenthesis
""")
        
        result = cleaner.execute({
            'project_root': tmp_path,
            'scan_paths': ['src']
        })
        
        # Should complete without crashing
        assert result.success is True or result.status == OperationStatus.FAILED
    
    def test_handle_empty_file(self, tmp_path, cleaner):
        """Test handling of empty files."""
        test_file = tmp_path / 'src'
        test_file.mkdir()
        test_file = test_file / 'empty.py'
        test_file.write_text("")
        
        result = cleaner.execute({
            'project_root': tmp_path,
            'scan_paths': ['src']
        })
        
        assert result.success is True
        metrics = result.data['metrics']
        assert metrics['files_scanned'] >= 1
    
    def test_handle_nonexistent_scan_path(self, tmp_path, cleaner):
        """Test handling of nonexistent scan paths."""
        result = cleaner.execute({
            'project_root': tmp_path,
            'scan_paths': ['nonexistent']
        })
        
        # Should complete without crashing
        assert result is not None
