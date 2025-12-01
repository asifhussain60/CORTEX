"""
Test suite for verify_no_mocks.py script
Phase 0.2 - RED state: These tests MUST fail before implementation
"""

import ast
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMockDetection:
    """Test AST-based mock detection in Python files"""
    
    def test_detect_unittest_mock_import(self):
        """RED: Should detect 'import unittest.mock' in source code"""
        from scripts.verify_no_mocks import detect_mocks_in_file
        
        test_code = """
import unittest.mock

def my_function():
    return True
"""
        # This should return mock violations
        violations = detect_mocks_in_file(test_code, "test_file.py")
        assert len(violations) > 0, "Should detect unittest.mock import"
        assert "unittest.mock" in violations[0]['message']
    
    def test_detect_mock_import_from(self):
        """RED: Should detect 'from unittest.mock import Mock'"""
        from scripts.verify_no_mocks import detect_mocks_in_file
        
        test_code = """
from unittest.mock import Mock, patch

def my_function():
    mock_obj = Mock()
    return mock_obj
"""
        violations = detect_mocks_in_file(test_code, "test_file.py")
        assert len(violations) > 0, "Should detect unittest.mock import"
        assert "Mock" in str(violations) or "mock" in str(violations)
    
    def test_no_false_positives_for_clean_code(self):
        """RED: Should NOT flag clean code without mocks"""
        from scripts.verify_no_mocks import detect_mocks_in_file
        
        test_code = """
import os
import sys

def calculate_total(items):
    return sum(items)
"""
        violations = detect_mocks_in_file(test_code, "test_file.py")
        assert len(violations) == 0, "Should not flag clean code"
    
    def test_allows_mocks_in_test_files(self):
        """RED: Should allow mocks in tests/ directory"""
        from scripts.verify_no_mocks import should_check_file
        
        test_file = Path("tests/test_something.py")
        assert should_check_file(test_file) is False, "Should skip test files"
    
    def test_checks_src_directory(self):
        """RED: Should check files in src/ directory"""
        from scripts.verify_no_mocks import should_check_file
        
        src_file = Path("src/tier1/working_memory.py")
        assert should_check_file(src_file) is True, "Should check src/ files"
    
    def test_exception_list_support(self):
        """RED: Should support exception list for specific files"""
        from scripts.verify_no_mocks import should_check_file
        
        # Some test utilities might legitimately use mocks
        test_util = Path("src/test_utils/mock_factory.py")
        # This should be configurable via exception list
        # Implementation will determine exact behavior


class TestVerificationPipeline:
    """Test full pipeline verification workflow"""
    
    def test_scan_directory_returns_violations(self):
        """GREEN: Should scan directory and return all violations"""
        from scripts.verify_no_mocks import scan_directory
        
        # Should work now that implementation exists
        violations = scan_directory(Path("src"))
        assert isinstance(violations, list), "Should return list of violations"
    
    def test_cli_exit_code_on_violations(self):
        """GREEN: Should exit with code 1 when violations found"""
        from scripts.verify_no_mocks import main
        
        # Mock sys.argv to avoid pytest argument conflicts
        with patch('sys.argv', ['verify_no_mocks.py']):
            with pytest.raises(SystemExit) as exc_info:
                # Mock violations found
                with patch('scripts.verify_no_mocks.scan_directory') as mock_scan:
                    mock_scan.return_value = [
                        {'file': 'src/test.py', 'line': 1, 'message': 'mock found'}
                    ]
                    main()
            
            assert exc_info.value.code == 1, "Should exit with code 1 on violations"
    
    def test_cli_exit_code_success(self):
        """GREEN: Should exit with code 0 when no violations"""
        from scripts.verify_no_mocks import main
        
        # Mock sys.argv to avoid pytest argument conflicts
        with patch('sys.argv', ['verify_no_mocks.py']):
            with pytest.raises(SystemExit) as exc_info:
                # No violations
                with patch('scripts.verify_no_mocks.scan_directory') as mock_scan:
                    mock_scan.return_value = []
                    main()
            
            assert exc_info.value.code == 0, "Should exit with code 0 on success"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_handles_syntax_errors_gracefully(self):
        """RED: Should handle files with syntax errors"""
        from scripts.verify_no_mocks import detect_mocks_in_file
        
        invalid_code = """
def broken_function(
    # Missing closing parenthesis
"""
        # Should return error violation, not crash
        violations = detect_mocks_in_file(invalid_code, "broken.py")
        assert len(violations) > 0, "Should report syntax error as violation"
    
    def test_handles_missing_files(self):
        """RED: Should handle missing files gracefully"""
        from scripts.verify_no_mocks import scan_directory
        
        violations = scan_directory(Path("nonexistent_directory"))
        # Should return empty list or handle gracefully, not crash
        assert isinstance(violations, list), "Should return list even for missing dir"


if __name__ == "__main__":
    # Run tests to verify RED state
    pytest.main([__file__, "-v", "--tb=short"])
