"""
Phase 8.3: Completion Report Generation Tests (TDD RED Phase)

Tests for Phase 8 completion report generation:
- Report structure and format
- Deliverable status tracking
- Test coverage summary
- Git checkpoint inclusion
- Custom output paths

Author: Asif Hussain
Date: December 2, 2025
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrators.phase8_operation_handler import Phase8OperationHandler


class TestCompletionReportGeneration:
    """Test completion report generation."""
    
    @pytest.fixture
    def temp_brain(self, tmp_path):
        """Create temporary brain structure for testing."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        # Create reports directory
        (brain_path / "documents" / "reports").mkdir(parents=True)
        
        return brain_path
    
    def test_report_generates_markdown_file(self, temp_brain):
        """
        RED TEST: Verify report generates Markdown file.
        
        Should:
        - Create report file in documents/reports/
        - Use Markdown format
        - Return success message with path
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {}
        
        # Act
        result = handler.handle_completion_report(context)
        
        # Assert
        assert 'report generated' in result.lower(), \
            "Should confirm report generation"
        
        # Check file exists
        report_path = temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md"
        assert report_path.exists(), \
            "Should create report file"
        
        # Check is Markdown
        content = report_path.read_text()
        assert content.startswith('#'), \
            "Should be Markdown format (starts with #)"
    
    def test_report_includes_deliverable_checklist(self, temp_brain):
        """
        RED TEST: Verify report includes deliverable checklist.
        
        Should include:
        - [ ] notation for incomplete items
        - [x] notation for complete items
        - All 13 deliverables listed
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {}
        
        # Act
        handler.handle_completion_report(context)
        
        # Assert
        report_path = temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md"
        content = report_path.read_text()
        
        assert '- [x]' in content, \
            "Should include completed deliverables (checkbox notation)"
        assert '- [ ]' in content, \
            "Should include incomplete deliverables"
        assert '8.1.1' in content and '8.4' in content, \
            "Should list all deliverables (8.1.1 through 8.4)"
    
    def test_report_includes_test_coverage_summary(self, temp_brain):
        """
        RED TEST: Verify report includes test coverage summary.
        
        Should report:
        - Phase 8 test count
        - Pass rate percentage
        - Total CORTEX test count
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {}
        
        # Act
        handler.handle_completion_report(context)
        
        # Assert
        report_path = temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md"
        content = report_path.read_text()
        
        assert 'test' in content.lower() and 'coverage' in content.lower(), \
            "Should mention test coverage"
        assert any(char.isdigit() for char in content), \
            "Should include numeric test counts"
    
    def test_report_includes_implementation_notes(self, temp_brain):
        """
        RED TEST: Verify report includes implementation notes section.
        
        Should include:
        - Section header "Implementation Notes"
        - Notes for each completed phase
        - Cross-platform readiness notes
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {}
        
        # Act
        handler.handle_completion_report(context)
        
        # Assert
        report_path = temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md"
        content = report_path.read_text()
        
        assert 'implementation notes' in content.lower(), \
            "Should have Implementation Notes section"
        assert 'cross-platform' in content.lower(), \
            "Should mention cross-platform readiness"
    
    def test_report_includes_git_checkpoints(self, temp_brain):
        """
        RED TEST: Verify report includes git checkpoint information.
        
        Should list:
        - Major checkpoints (RED, GREEN, REFACTOR)
        - Commit descriptions
        - Section header "Git Checkpoints"
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {}
        
        # Act
        handler.handle_completion_report(context)
        
        # Assert
        report_path = temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md"
        content = report_path.read_text()
        
        assert 'git checkpoint' in content.lower() or 'checkpoint' in content.lower(), \
            "Should have Git Checkpoints section"
        assert 'red' in content.lower() or 'green' in content.lower(), \
            "Should mention TDD phases"
    
    def test_report_accepts_custom_output_path(self, temp_brain):
        """
        RED TEST: Verify report can be generated at custom path.
        
        Should:
        - Accept output_path in context
        - Create file at specified path
        - Create parent directories if needed
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        custom_path = temp_brain / "custom" / "my-report.md"
        context = {'output_path': str(custom_path)}
        
        # Act
        result = handler.handle_completion_report(context)
        
        # Assert
        assert custom_path.exists(), \
            "Should create report at custom path"
        assert str(custom_path) in result, \
            "Should confirm custom path in response"
    
    def test_report_includes_progress_percentage(self, temp_brain):
        """
        RED TEST: Verify report includes overall progress percentage.
        
        Should show:
        - XX% complete
        - X/Y deliverables format
        - Progress indicator
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {}
        
        # Act
        handler.handle_completion_report(context)
        
        # Assert
        report_path = temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md"
        content = report_path.read_text()
        
        assert '%' in content, \
            "Should include percentage"
        assert 'progress' in content.lower(), \
            "Should mention progress"
    
    def test_report_includes_next_steps(self, temp_brain):
        """
        RED TEST: Verify report includes next steps section.
        
        Should list:
        - Immediate next deliverable
        - Numbered action items
        - Clear guidance for continuation
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {}
        
        # Act
        handler.handle_completion_report(context)
        
        # Assert
        report_path = temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md"
        content = report_path.read_text()
        
        assert 'next step' in content.lower(), \
            "Should have Next Steps section"
        # Should have numbered list (1., 2., 3.)
        assert '1.' in content or '2.' in content, \
            "Should include numbered action items"
    
    def test_report_format_matches_cortex_standard(self, temp_brain):
        """
        RED TEST: Verify report follows CORTEX response format.
        
        Should include:
        - Author attribution
        - GitHub link
        - Proper section structure
        - Professional formatting
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {}
        
        # Act
        handler.handle_completion_report(context)
        
        # Assert
        report_path = temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md"
        content = report_path.read_text()
        
        assert 'author' in content.lower() or 'asif hussain' in content.lower(), \
            "Should include author attribution"
        assert '##' in content, \
            "Should use proper Markdown heading structure"


class TestReportUpdates:
    """Test report updating functionality."""
    
    @pytest.fixture
    def temp_brain(self, tmp_path):
        """Create temporary brain structure."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "documents" / "reports").mkdir(parents=True)
        return brain_path
    
    def test_report_overwrites_previous_version(self, temp_brain):
        """
        RED TEST: Verify generating report twice overwrites old version.
        
        Should:
        - Replace old report with new one
        - Update timestamps
        - Not create duplicate files
        """
        # Arrange
        handler = Phase8OperationHandler(temp_brain)
        context = {}
        
        # Act
        handler.handle_completion_report(context)
        first_content = (temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md").read_text()
        
        handler.handle_completion_report(context)
        second_content = (temp_brain / "documents" / "reports" / "PHASE-8-COMPLETION-REPORT.md").read_text()
        
        # Assert
        # Should be only one report file
        reports = list((temp_brain / "documents" / "reports").glob("PHASE-8-*.md"))
        assert len(reports) == 1, \
            "Should not create duplicate reports"
