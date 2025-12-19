"""
Test Path Cleanup Functionality

Tests automatic replacement of hardcoded absolute paths with CORTEX_ROOT variable.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import pytest
from pathlib import Path
from src.operations.modules.optimization.hardcoded_data_cleaner_module import (
    HardcodedDataCleanerModule,
    HardcodedViolation
)


class TestPathReplacement:
    """Test path replacement logic."""
    
    def test_windows_absolute_path_replacement(self):
        """Test Windows absolute path gets replaced with CORTEX_ROOT."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'base_path = "D:\\PROJECTS\\CORTEX\\src\\config.py"'
        context = 'Hardcoded path: D:\\PROJECTS\\CORTEX\\src\\config.py'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        assert 'CORTEX_ROOT' in result
        assert 'D:\\PROJECTS\\CORTEX' not in result
        assert 'Path(CORTEX_ROOT)' in result
        assert 'src/config.py' in result
    
    def test_unix_absolute_path_replacement(self):
        """Test Unix absolute path gets replaced with CORTEX_ROOT."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'base_path = "/Users/asifhussain/PROJECTS/CORTEX/src/config.py"'
        context = 'Hardcoded path: /Users/asifhussain/PROJECTS/CORTEX/src/config.py'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        assert 'CORTEX_ROOT' in result
        assert '/Users/asifhussain/PROJECTS/CORTEX' not in result
        assert 'Path(CORTEX_ROOT)' in result
        assert 'src/config.py' in result
    
    def test_unix_home_path_replacement(self):
        """Test Unix /home/ path gets replaced with CORTEX_ROOT."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'base_path = "/home/developer/PROJECTS/CORTEX/tests/test.py"'
        context = 'Hardcoded path: /home/developer/PROJECTS/CORTEX/tests/test.py'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        assert 'CORTEX_ROOT' in result
        assert '/home/developer/PROJECTS/CORTEX' not in result
        assert 'Path(CORTEX_ROOT)' in result
        assert 'tests/test.py' in result
    
    def test_single_quote_path_replacement(self):
        """Test path replacement works with single quotes."""
        cleaner = HardcodedDataCleanerModule()
        
        line = "config_file = 'D:\\PROJECTS\\CORTEX\\cortex.config.json'"
        context = 'Hardcoded path: D:\\PROJECTS\\CORTEX\\cortex.config.json'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        assert 'CORTEX_ROOT' in result
        assert 'D:\\PROJECTS\\CORTEX' not in result
    
    def test_path_with_subdirectories(self):
        """Test path replacement preserves subdirectory structure."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'file_path = "D:\\PROJECTS\\CORTEX\\cortex-brain\\documents\\reports\\summary.md"'
        context = 'Hardcoded path: D:\\PROJECTS\\CORTEX\\cortex-brain\\documents\\reports\\summary.md'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        assert 'CORTEX_ROOT' in result
        assert 'cortex-brain/documents/reports/summary.md' in result
    
    def test_no_replacement_for_unrecognized_pattern(self):
        """Test that unrecognized path patterns are not replaced."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'random_path = "/var/log/application.log"'
        context = 'Hardcoded path: /var/log/application.log'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        # Should remain unchanged (not a CORTEX path)
        assert result == line
    
    def test_no_replacement_without_context(self):
        """Test that line is unchanged if context doesn't match."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'base_path = "D:\\PROJECTS\\CORTEX\\src\\config.py"'
        context = 'Invalid context format'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        # Should remain unchanged
        assert result == line


class TestFixPathViolations:
    """Test the complete path fixing workflow."""
    
    def test_fix_violations_groups_by_file(self, tmp_path):
        """Test that violations are grouped by file for efficient processing."""
        cleaner = HardcodedDataCleanerModule()
        
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text(
            'path1 = "D:\\PROJECTS\\CORTEX\\src\\file1.py"\n'
            'path2 = "D:\\PROJECTS\\CORTEX\\src\\file2.py"\n'
        )
        
        violations = [
            HardcodedViolation(
                file_path=test_file,
                line_number=1,
                violation_type='hardcoded_path',
                severity='CRITICAL',
                code_snippet='path1 = "D:\\PROJECTS\\CORTEX\\src\\file1.py"',
                suggested_fix='Use CORTEX_ROOT',
                context='Hardcoded path: D:\\PROJECTS\\CORTEX\\src\\file1.py'
            ),
            HardcodedViolation(
                file_path=test_file,
                line_number=2,
                violation_type='hardcoded_path',
                severity='CRITICAL',
                code_snippet='path2 = "D:\\PROJECTS\\CORTEX\\src\\file2.py"',
                suggested_fix='Use CORTEX_ROOT',
                context='Hardcoded path: D:\\PROJECTS\\CORTEX\\src\\file2.py'
            )
        ]
        
        result = cleaner._fix_path_violations(violations, 'CORTEX_ROOT')
        
        assert result['files_modified'] == 1
        assert result['paths_replaced'] == 2
        assert len(result['errors']) == 0
        
        # Verify file was modified
        content = test_file.read_text()
        assert 'CORTEX_ROOT' in content
        assert 'D:\\PROJECTS\\CORTEX' not in content
    
    def test_fix_violations_handles_errors_gracefully(self):
        """Test that errors during fixing are captured and reported."""
        cleaner = HardcodedDataCleanerModule()
        
        # Create violation for non-existent file
        violations = [
            HardcodedViolation(
                file_path=Path('/nonexistent/file.py'),
                line_number=1,
                violation_type='hardcoded_path',
                severity='CRITICAL',
                code_snippet='path = "D:\\PROJECTS\\CORTEX\\src\\file.py"',
                suggested_fix='Use CORTEX_ROOT',
                context='Hardcoded path: D:\\PROJECTS\\CORTEX\\src\\file.py'
            )
        ]
        
        result = cleaner._fix_path_violations(violations, 'CORTEX_ROOT')
        
        assert result['files_modified'] == 0
        assert result['paths_replaced'] == 0
        assert len(result['errors']) > 0
    
    def test_fix_violations_skips_non_path_violations(self, tmp_path):
        """Test that only hardcoded_path violations are processed."""
        cleaner = HardcodedDataCleanerModule()
        
        test_file = tmp_path / "test.py"
        test_file.write_text('mock_data = {"test": "value"}')
        
        violations = [
            HardcodedViolation(
                file_path=test_file,
                line_number=1,
                violation_type='mock_data',  # Not a path violation
                severity='HIGH',
                code_snippet='mock_data = {"test": "value"}',
                suggested_fix='Remove mock data',
                context='Mock data in production'
            )
        ]
        
        result = cleaner._fix_path_violations(violations, 'CORTEX_ROOT')
        
        # Should skip non-path violations
        assert result['files_modified'] == 0
        assert result['paths_replaced'] == 0


class TestExecuteWithPathFixing:
    """Test the execute method with path fixing enabled."""
    
    def test_execute_with_fix_paths_enabled(self, tmp_path):
        """Test execute method with fix_paths=True."""
        cleaner = HardcodedDataCleanerModule()
        
        # Create test file with hardcoded path
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        test_file = src_dir / "test.py"
        test_file.write_text('config = "D:\\PROJECTS\\CORTEX\\cortex.config.json"')
        
        result = cleaner.execute(context={
            'project_root': tmp_path,
            'scan_paths': ['src'],
            'exclude_patterns': ['__pycache__'],
            'fail_on_critical': False,
            'fix_paths': True,
            'base_path_var': 'CORTEX_ROOT'
        })
        
        assert result.success
        assert 'fix_results' in result.data
        
        fix_results = result.data['fix_results']
        assert 'files_modified' in fix_results
        assert 'paths_replaced' in fix_results
        assert 'errors' in fix_results
    
    def test_execute_with_fix_paths_disabled(self, tmp_path):
        """Test execute method with fix_paths=False (default)."""
        cleaner = HardcodedDataCleanerModule()
        
        # Create test file with hardcoded path
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        test_file = src_dir / "test.py"
        original_content = 'config = "D:\\PROJECTS\\CORTEX\\cortex.config.json"'
        test_file.write_text(original_content)
        
        result = cleaner.execute(context={
            'project_root': tmp_path,
            'scan_paths': ['src'],
            'exclude_patterns': ['__pycache__'],
            'fail_on_critical': False,
            'fix_paths': False  # Disabled
        })
        
        assert result.success
        
        # File should not be modified
        content = test_file.read_text()
        assert content == original_content
        
        # Should still have fix_results with zero replacements
        fix_results = result.data['fix_results']
        assert fix_results['paths_replaced'] == 0


class TestCrossplatformPathHandling:
    """Test handling of different platform path formats."""
    
    def test_windows_c_drive_path(self):
        """Test C: drive path replacement."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'path = "C:\\Users\\Developer\\PROJECTS\\CORTEX\\src\\file.py"'
        context = 'Hardcoded path: C:\\Users\\Developer\\PROJECTS\\CORTEX\\src\\file.py'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        assert 'CORTEX_ROOT' in result
        assert 'C:\\Users\\Developer\\PROJECTS\\CORTEX' not in result
    
    def test_windows_network_path_not_replaced(self):
        """Test that UNC network paths are not replaced."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'path = "\\\\server\\share\\CORTEX\\file.py"'
        context = 'Hardcoded path: \\\\server\\share\\CORTEX\\file.py'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        # UNC paths should not be replaced (not a standard CORTEX path)
        assert result == line
    
    def test_mac_users_path(self):
        """Test macOS /Users/ path replacement."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'config = "/Users/asifhussain/PROJECTS/CORTEX/cortex.config.json"'
        context = 'Hardcoded path: /Users/asifhussain/PROJECTS/CORTEX/cortex.config.json'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        assert 'CORTEX_ROOT' in result
        assert '/Users/asifhussain' not in result
    
    def test_linux_home_path(self):
        """Test Linux /home/ path replacement."""
        cleaner = HardcodedDataCleanerModule()
        
        line = 'path = "/home/developer/PROJECTS/CORTEX/tests/test.py"'
        context = 'Hardcoded path: /home/developer/PROJECTS/CORTEX/tests/test.py'
        
        result = cleaner._replace_hardcoded_path(line, context, 'CORTEX_ROOT')
        
        assert 'CORTEX_ROOT' in result
        assert '/home/developer' not in result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_violations_list(self):
        """Test that empty violations list is handled gracefully."""
        cleaner = HardcodedDataCleanerModule()
        
        result = cleaner._fix_path_violations([], 'CORTEX_ROOT')
        
        assert result['files_modified'] == 0
        assert result['paths_replaced'] == 0
        assert len(result['errors']) == 0
    
    def test_path_at_line_boundary(self, tmp_path):
        """Test path at first and last lines of file."""
        cleaner = HardcodedDataCleanerModule()
        
        test_file = tmp_path / "test.py"
        test_file.write_text(
            'first = "D:\\PROJECTS\\CORTEX\\file1.py"\n'
            'middle = "something"\n'
            'last = "D:\\PROJECTS\\CORTEX\\file2.py"'
        )
        
        violations = [
            HardcodedViolation(
                file_path=test_file,
                line_number=1,
                violation_type='hardcoded_path',
                severity='CRITICAL',
                code_snippet='first = "D:\\PROJECTS\\CORTEX\\file1.py"',
                suggested_fix='Use CORTEX_ROOT',
                context='Hardcoded path: D:\\PROJECTS\\CORTEX\\file1.py'
            ),
            HardcodedViolation(
                file_path=test_file,
                line_number=3,
                violation_type='hardcoded_path',
                severity='CRITICAL',
                code_snippet='last = "D:\\PROJECTS\\CORTEX\\file2.py"',
                suggested_fix='Use CORTEX_ROOT',
                context='Hardcoded path: D:\\PROJECTS\\CORTEX\\file2.py'
            )
        ]
        
        result = cleaner._fix_path_violations(violations, 'CORTEX_ROOT')
        
        assert result['paths_replaced'] == 2
        
        content = test_file.read_text()
        assert content.count('CORTEX_ROOT') == 2
    
    def test_multiple_paths_same_line(self, tmp_path):
        """Test handling of multiple paths on the same line."""
        cleaner = HardcodedDataCleanerModule()
        
        test_file = tmp_path / "test.py"
        test_file.write_text('paths = ["D:\\PROJECTS\\CORTEX\\file1.py", "D:\\PROJECTS\\CORTEX\\file2.py"]')
        
        violations = [
            HardcodedViolation(
                file_path=test_file,
                line_number=1,
                violation_type='hardcoded_path',
                severity='CRITICAL',
                code_snippet='paths = ["D:\\PROJECTS\\CORTEX\\file1.py", "D:\\PROJECTS\\CORTEX\\file2.py"]',
                suggested_fix='Use CORTEX_ROOT',
                context='Hardcoded path: D:\\PROJECTS\\CORTEX\\file1.py'
            )
        ]
        
        result = cleaner._fix_path_violations(violations, 'CORTEX_ROOT')
        
        # Should replace at least one path
        assert result['paths_replaced'] >= 1
        
        content = test_file.read_text()
        assert 'CORTEX_ROOT' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
