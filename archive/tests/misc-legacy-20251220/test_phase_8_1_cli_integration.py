"""
Phase 8.1: CLI Integration Tests (TDD RED Phase)

Tests for Phase 8 CLI operations:
- integration-cleanup command
- completion-report command
- phase8-status command

Author: Asif Hussain
Date: December 2, 2025
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import main


class TestPhase8CLIIntegration:
    """Test Phase 8 CLI operations."""
    
    def test_help_shows_phase8_operations(self):
        """
        RED TEST: Verify help command lists Phase 8 operations.
        
        Expected Phase 8 operations:
        - integration-cleanup: Final cleanup before deployment
        - completion-report: Generate Phase 8 completion report
        - phase8-status: Show Phase 8 progress
        """
        # Arrange
        with patch('sys.argv', ['cortex', 'help', '--format', 'text']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                
                # Act
                try:
                    exit_code = main()
                except SystemExit as e:
                    exit_code = e.code
                
                # Assert
                output = mock_stdout.getvalue()
                
                # Should list Phase 8 operations
                assert 'integration-cleanup' in output.lower(), \
                    "Help should list 'integration-cleanup' operation"
                assert 'completion-report' in output.lower(), \
                    "Help should list 'completion-report' operation"
                assert 'phase8-status' in output.lower(), \
                    "Help should list 'phase8-status' operation"
                
                # Should describe what Phase 8 is
                assert 'phase 8' in output.lower() or 'final integration' in output.lower(), \
                    "Help should mention Phase 8 or Final Integration"
    
    def test_integration_cleanup_dry_run_mode(self):
        """
        RED TEST: Verify integration-cleanup --dry-run executes safely.
        
        Should:
        - Accept --dry-run flag
        - Not modify any files
        - Return summary of what would be cleaned
        """
        # Arrange
        mock_handler = MagicMock()
        mock_handler.handle_integration_cleanup.return_value = "DRY RUN: Would clean 5 files"
        
        with patch('sys.argv', ['cortex', 'integration-cleanup', '--dry-run']):
            with patch('src.orchestrators.phase8_operation_handler.Phase8OperationHandler', return_value=mock_handler):
                with patch('src.entry_point.cortex_entry.CortexEntry'):
                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        
                        # Act
                        try:
                            exit_code = main()
                        except SystemExit as e:
                            exit_code = e.code
                        
                        # Assert
                        output = mock_stdout.getvalue()
                        
                        assert exit_code == 0, "Dry-run should succeed"
                        assert 'dry run' in output.lower() or 'dry-run' in output.lower(), \
                            "Output should indicate dry-run mode"
                        assert 'would' in output.lower(), \
                            "Dry-run should use conditional language (would do X)"
    
    def test_integration_cleanup_requires_confirmation(self):
        """
        RED TEST: Verify integration-cleanup asks for confirmation in live mode.
        
        Should:
        - Prompt user for confirmation
        - Abort if user says no
        - Proceed if user says yes
        """
        # Arrange - user declines
        mock_handler = MagicMock()
        mock_handler.handle_integration_cleanup.return_value = "Operation cancelled by user"
        
        with patch('sys.argv', ['cortex', 'integration-cleanup']):
            with patch('src.orchestrators.phase8_operation_handler.Phase8OperationHandler', return_value=mock_handler):
                with patch('src.entry_point.cortex_entry.CortexEntry'):
                    with patch('builtins.input', return_value='n'):
                        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                            
                            # Act
                            try:
                                exit_code = main()
                            except SystemExit as e:
                                exit_code = e.code
                            
                            # Assert
                            output = mock_stdout.getvalue()
                            
                            assert 'confirm' in output.lower() or 'continue' in output.lower() or 'cancelled' in output.lower(), \
                                "Should ask for confirmation or show cancellation"
                            assert 'cancelled' in output.lower() or 'aborted' in output.lower(), \
                                "Should indicate operation was cancelled"
    
    def test_completion_report_generates_markdown(self):
        """
        RED TEST: Verify completion-report generates Markdown report.
        
        Should:
        - Generate report at cortex-brain/documents/reports/PHASE-8-COMPLETION-REPORT.md
        - Include completion date
        - Include all deliverable statuses
        - Include test coverage summary
        """
        # Arrange
        mock_handler = MagicMock()
        mock_handler.handle_completion_report.return_value = "Report generated: PHASE-8-COMPLETION-REPORT.md"
        
        with patch('sys.argv', ['cortex', 'completion-report', '--format', 'markdown']):
            with patch('src.orchestrators.phase8_operation_handler.Phase8OperationHandler', return_value=mock_handler):
                with patch('src.entry_point.cortex_entry.CortexEntry'):
                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        
                        # Act
                        try:
                            exit_code = main()
                        except SystemExit as e:
                            exit_code = e.code
                        
                        # Assert
                        output = mock_stdout.getvalue()
                        
                        assert exit_code == 0, "Report generation should succeed"
                        assert 'report generated' in output.lower(), \
                            "Should confirm report generation"
                        assert 'PHASE-8-COMPLETION-REPORT.md' in output, \
                            "Should show report filename"
    
    def test_phase8_status_shows_progress(self):
        """
        RED TEST: Verify phase8-status shows completion progress.
        
        Should show:
        - Deliverables completed (X/Y)
        - Current deliverable in progress
        - Estimated time remaining
        - Blockers (if any)
        """
        # Arrange
        mock_handler = MagicMock()
        mock_handler.handle_phase8_status.return_value = "Phase 8 Progress: 3/5 deliverables complete (60%)"
        
        with patch('sys.argv', ['cortex', 'phase8-status']):
            with patch('src.orchestrators.phase8_operation_handler.Phase8OperationHandler', return_value=mock_handler):
                with patch('src.entry_point.cortex_entry.CortexEntry'):
                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        
                        # Act
                        try:
                            exit_code = main()
                        except SystemExit as e:
                            exit_code = e.code
                        
                        # Assert
                        output = mock_stdout.getvalue()
                        
                        assert exit_code == 0, "Status check should succeed"
                        assert 'deliverable' in output.lower(), \
                            "Should mention deliverables"
                        assert 'progress' in output.lower() or '%' in output, \
                            "Should show progress indicator"
    
    def test_phase8_operations_require_cortex_brain(self):
        """
        RED TEST: Verify Phase 8 operations fail gracefully if cortex-brain missing.
        
        Should:
        - Detect missing cortex-brain directory
        - Show helpful error message
        - Suggest running setup first
        """
        # Arrange - simulate missing brain
        with patch('sys.argv', ['cortex', 'integration-cleanup', '--dry-run']):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    
                    # Act
                    try:
                        exit_code = main()
                    except SystemExit as e:
                        exit_code = e.code
                    
                    # Assert
                    output = mock_stdout.getvalue()
                    
                    assert exit_code != 0, "Should fail if brain missing"
                    assert 'cortex-brain' in output.lower(), \
                        "Error should mention cortex-brain"
                    assert 'setup' in output.lower(), \
                        "Should suggest running setup"


class TestPhase8CLIArguments:
    """Test Phase 8 CLI argument parsing."""
    
    def test_integration_cleanup_accepts_profile_flag(self):
        """
        RED TEST: Verify --operation-profile flag for integration-cleanup.
        
        Should accept: --operation-profile quick|standard|comprehensive
        """
        # Arrange
        with patch('sys.argv', ['cortex', 'integration-cleanup', '--operation-profile', 'quick', '--dry-run']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                
                # Act
                try:
                    exit_code = main()
                except SystemExit as e:
                    exit_code = e.code
                
                # Assert
                output = mock_stdout.getvalue()
                
                assert 'quick' in output.lower(), \
                    "Should acknowledge 'quick' profile"
    
    def test_completion_report_accepts_output_path(self):
        """
        RED TEST: Verify --output flag for completion-report.
        
        Should accept: --output /custom/path/report.md
        """
        # Arrange
        custom_path = '/tmp/custom-report.md'
        mock_handler = MagicMock()
        mock_handler.handle_completion_report.return_value = f"Report generated: {custom_path}"
        
        with patch('sys.argv', ['cortex', 'completion-report', '--output', custom_path]):
            with patch('src.orchestrators.phase8_operation_handler.Phase8OperationHandler', return_value=mock_handler):
                with patch('src.entry_point.cortex_entry.CortexEntry'):
                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        
                        # Act
                        try:
                            exit_code = main()
                        except SystemExit as e:
                            exit_code = e.code
                        
                        # Assert
                        output = mock_stdout.getvalue()
                        
                        assert custom_path in output or 'custom-report.md' in output, \
                            "Should acknowledge custom output path"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
