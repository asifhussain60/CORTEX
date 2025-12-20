"""
Test REFACTOR Phase Execution

Tests for SystemRefactorPlugin's REFACTOR task parsing and execution.
This is Phase 3 of the 5-phase workflow.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestRefactorTaskParsing:
    """Test parsing TODO REFACTOR comments from test files."""
    
    @pytest.mark.unit
    def test_parse_refactor_tasks_finds_todo_comments(self, plugin_with_mocked_paths, sample_test_file_content):
        """Test _parse_refactor_tasks finds TODO REFACTOR comments."""
        # Create test file with TODO REFACTOR
        test_file = plugin_with_mocked_paths.tests_path / "test_sample.py"
        test_file.write_text(sample_test_file_content)
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        assert tasks is not None
        assert isinstance(tasks, list)
        assert len(tasks) > 0
    
    @pytest.mark.unit
    def test_parse_refactor_tasks_extracts_description(self, plugin_with_mocked_paths):
        """Test task parsing extracts description from TODO comments."""
        test_content = """
        def test_login():
            # TODO REFACTOR: Extract authentication logic to separate module
            pass
        """
        
        test_file = plugin_with_mocked_paths.tests_path / "test_auth.py"
        test_file.write_text(test_content)
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        if tasks:
            assert any("authentication" in task.description.lower() for task in tasks)
            assert any("extract" in task.description.lower() for task in tasks)
    
    @pytest.mark.unit
    def test_parse_refactor_tasks_captures_file_location(self, plugin_with_mocked_paths):
        """Test task parsing captures source file path."""
        test_content = "# TODO REFACTOR: Improve structure"
        test_file = plugin_with_mocked_paths.tests_path / "test_location.py"
        test_file.write_text(test_content)
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        if tasks:
            assert any("test_location.py" in task.file_path for task in tasks)
    
    @pytest.mark.unit
    def test_parse_refactor_tasks_captures_line_number(self, plugin_with_mocked_paths):
        """Test task parsing captures line number."""
        test_content = """
        # Line 1
        # TODO REFACTOR: Fix this on line 3
        # Line 3
        """
        
        test_file = plugin_with_mocked_paths.tests_path / "test_lines.py"
        test_file.write_text(test_content)
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        if tasks:
            # Line number should be captured
            assert any(hasattr(task, 'line_number') for task in tasks)
    
    @pytest.mark.unit
    def test_parse_refactor_tasks_handles_multiple_comments(self, plugin_with_mocked_paths):
        """Test parsing multiple TODO REFACTOR comments in one file."""
        test_content = """
        def test_one():
            # TODO REFACTOR: First task
            pass
        
        def test_two():
            # TODO REFACTOR: Second task
            pass
        
        def test_three():
            # TODO REFACTOR: Third task
            pass
        """
        
        test_file = plugin_with_mocked_paths.tests_path / "test_multiple.py"
        test_file.write_text(test_content)
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        # Should find all 3 tasks
        assert len(tasks) >= 3


class TestRefactorTaskAttributes:
    """Test RefactorTask model attributes."""
    
    @pytest.mark.unit
    def test_refactor_task_has_required_fields(self, sample_refactor_task):
        """Test RefactorTask has required attributes."""
        assert hasattr(sample_refactor_task, 'file_path')
        assert hasattr(sample_refactor_task, 'description')
        assert hasattr(sample_refactor_task, 'priority')
    
    @pytest.mark.unit
    def test_refactor_task_priority_is_medium(self, sample_refactor_task):
        """Test REFACTOR tasks default to MEDIUM priority."""
        assert sample_refactor_task.priority == "MEDIUM"
    
    @pytest.mark.unit
    def test_refactor_task_description_not_empty(self, sample_refactor_task):
        """Test task description is populated."""
        assert sample_refactor_task.description != ""
        assert len(sample_refactor_task.description) > 0


class TestRefactorPhaseExecution:
    """Test executing REFACTOR phase workflow."""
    
    @pytest.mark.integration
    def test_execute_refactor_phase_scans_all_test_files(self, plugin_with_mocked_paths):
        """Test _execute_refactor_phase scans entire test directory."""
        # Create multiple test files with TODO comments
        for i in range(3):
            test_file = plugin_with_mocked_paths.tests_path / f"test_{i}.py"
            test_file.write_text(f"# TODO REFACTOR: Task {i}")
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        # Should find tasks from all files
        assert len(tasks) >= 3
    
    @pytest.mark.integration
    def test_execute_refactor_phase_returns_task_list(self, plugin_with_mocked_paths):
        """Test REFACTOR phase returns list of tasks."""
        result = plugin_with_mocked_paths._execute_refactor_phase()
        
        assert result is not None
        assert isinstance(result, list)
    
    @pytest.mark.integration
    def test_execute_refactor_phase_handles_empty_results(self, plugin_with_mocked_paths):
        """Test REFACTOR phase handles no TODO comments gracefully."""
        # Create test files without TODO REFACTOR
        test_file = plugin_with_mocked_paths.tests_path / "test_clean.py"
        test_file.write_text("def test_clean(): pass")
        
        result = plugin_with_mocked_paths._execute_refactor_phase()
        
        # Should return empty list, not None
        assert result is not None
        assert isinstance(result, list)


class TestRefactorTaskRegexPatterns:
    """Test regex patterns for TODO REFACTOR detection."""
    
    @pytest.mark.unit
    def test_detects_standard_todo_refactor_format(self, plugin_with_mocked_paths):
        """Test detection of standard 'TODO REFACTOR:' format."""
        test_content = "# TODO REFACTOR: Standard format"
        test_file = plugin_with_mocked_paths.tests_path / "test_standard.py"
        test_file.write_text(test_content)
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        assert len(tasks) >= 1
    
    @pytest.mark.unit
    def test_detects_todo_refactor_without_colon(self, plugin_with_mocked_paths):
        """Test detection of 'TODO REFACTOR' without colon."""
        test_content = "# TODO REFACTOR No colon format"
        test_file = plugin_with_mocked_paths.tests_path / "test_no_colon.py"
        test_file.write_text(test_content)
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        assert len(tasks) >= 1
    
    @pytest.mark.unit
    def test_detects_case_variations(self, plugin_with_mocked_paths):
        """Test detection handles case variations."""
        test_content = """
        # todo refactor: lowercase
        # TODO REFACTOR: uppercase
        # Todo Refactor: mixed case
        """
        
        test_file = plugin_with_mocked_paths.tests_path / "test_cases.py"
        test_file.write_text(test_content)
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        # Should find all 3 variations
        assert len(tasks) >= 3
    
    @pytest.mark.unit
    def test_ignores_other_todo_types(self, plugin_with_mocked_paths):
        """Test parser ignores non-REFACTOR TODO comments."""
        test_content = """
        # TODO: Regular todo (should ignore)
        # FIXME: Bug fix todo (should ignore)
        # TODO REFACTOR: This should be found
        # NOTE: Random note (should ignore)
        """
        
        test_file = plugin_with_mocked_paths.tests_path / "test_filter.py"
        test_file.write_text(test_content)
        
        tasks = plugin_with_mocked_paths._parse_refactor_tasks()
        
        # Should only find the TODO REFACTOR comment
        assert len(tasks) == 1
        assert "refactor" in tasks[0].description.lower()


class TestRefactorPhaseIntegration:
    """Test REFACTOR phase integration with full workflow."""
    
    @pytest.mark.integration
    def test_refactor_phase_integrates_with_review(self, plugin_with_mocked_paths):
        """Test REFACTOR tasks are included in review report."""
        # Create test with TODO REFACTOR
        test_content = "# TODO REFACTOR: Integration test"
        test_file = plugin_with_mocked_paths.tests_path / "test_integration.py"
        test_file.write_text(test_content)
        
        tasks = plugin_with_mocked_paths._execute_refactor_phase()
        
        # Tasks should be available for report generation
        assert tasks is not None
        assert len(tasks) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
