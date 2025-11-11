"""
Tests for Execution Mode Detection and Dry-Run Support

Tests:
    - Natural language pattern detection
    - Execution mode parsing
    - Copyright header rendering
    - Dry-run orchestrator mixin
    - Module execution mode propagation

Author: Asif Hussain
Version: 1.0
"""

import pytest
from src.operations.base_operation_module import ExecutionMode
from src.operations.execution_mode_parser import (
    detect_execution_mode,
    parse_mode_from_args,
    format_mode_message,
    should_prompt_confirmation
)
from src.operations.dry_run_mixin import DryRunOrchestratorMixin


class TestExecutionModeDetection:
    """Test natural language execution mode detection."""
    
    def test_detect_dry_run_preview(self):
        """Test 'preview' keyword detection."""
        mode, reason = detect_execution_mode("preview cleanup changes")
        assert mode == ExecutionMode.DRY_RUN
        assert 'preview' in reason.lower()
    
    def test_detect_dry_run_hyphenated(self):
        """Test 'dry-run' keyword detection."""
        mode, reason = detect_execution_mode("dry-run optimization")
        assert mode == ExecutionMode.DRY_RUN
        assert 'dry' in reason.lower()
    
    def test_detect_dry_run_spaced(self):
        """Test 'dry run' keyword detection."""
        mode, reason = detect_execution_mode("dry run cleanup")
        assert mode == ExecutionMode.DRY_RUN
    
    def test_detect_dry_run_simulate(self):
        """Test 'simulate' keyword detection."""
        mode, reason = detect_execution_mode("simulate story refresh")
        assert mode == ExecutionMode.DRY_RUN
    
    def test_detect_dry_run_test(self):
        """Test 'test' keyword detection."""
        mode, reason = detect_execution_mode("test the cleanup process")
        assert mode == ExecutionMode.DRY_RUN
    
    def test_detect_dry_run_what_would(self):
        """Test 'what would' keyword detection."""
        mode, reason = detect_execution_mode("what would happen if I cleanup")
        assert mode == ExecutionMode.DRY_RUN
    
    def test_detect_dry_run_show_me(self):
        """Test 'show me what' keyword detection."""
        mode, reason = detect_execution_mode("show me what cleanup would do")
        assert mode == ExecutionMode.DRY_RUN
    
    def test_detect_live_run_execute(self):
        """Test 'execute' keyword detection."""
        mode, reason = detect_execution_mode("execute cleanup")
        assert mode == ExecutionMode.LIVE
        assert 'execute' in reason.lower()
    
    def test_detect_live_run_apply(self):
        """Test 'apply' keyword detection."""
        mode, reason = detect_execution_mode("apply optimization")
        assert mode == ExecutionMode.LIVE
    
    def test_detect_live_run_actually(self):
        """Test 'actually run' keyword detection."""
        mode, reason = detect_execution_mode("actually run cleanup")
        assert mode == ExecutionMode.LIVE
    
    def test_detect_live_run_for_real(self):
        """Test 'for real' keyword detection."""
        mode, reason = detect_execution_mode("run cleanup for real")
        assert mode == ExecutionMode.LIVE
    
    def test_detect_default_live(self):
        """Test default to live mode when no keywords."""
        mode, reason = detect_execution_mode("cleanup workspace")
        assert mode == ExecutionMode.LIVE
        assert 'default' in reason.lower()
    
    def test_detect_case_insensitive(self):
        """Test case-insensitive detection."""
        mode1, _ = detect_execution_mode("PREVIEW cleanup")
        mode2, _ = detect_execution_mode("Preview Cleanup")
        mode3, _ = detect_execution_mode("preview cleanup")
        assert mode1 == mode2 == mode3 == ExecutionMode.DRY_RUN


class TestExecutionModeArgs:
    """Test CLI argument parsing."""
    
    def test_parse_dry_run_true(self):
        """Test --dry-run flag set."""
        mode = parse_mode_from_args({'dry_run': True})
        assert mode == ExecutionMode.DRY_RUN
    
    def test_parse_dry_run_false(self):
        """Test --dry-run flag not set."""
        mode = parse_mode_from_args({'dry_run': False})
        assert mode == ExecutionMode.LIVE
    
    def test_parse_dry_run_missing(self):
        """Test --dry-run flag missing."""
        mode = parse_mode_from_args({})
        assert mode == ExecutionMode.LIVE
    
    def test_parse_with_other_args(self):
        """Test parsing with other CLI args present."""
        mode = parse_mode_from_args({
            'dry_run': True,
            'profile': 'standard',
            'verbose': True
        })
        assert mode == ExecutionMode.DRY_RUN


class TestExecutionModeFormatting:
    """Test mode message formatting."""
    
    def test_format_dry_run(self):
        """Test dry-run mode message."""
        msg = format_mode_message(ExecutionMode.DRY_RUN)
        assert 'DRY RUN' in msg or 'dry run' in msg.lower()
        assert 'preview' in msg.lower() or 'no changes' in msg.lower()
    
    def test_format_live(self):
        """Test live mode message."""
        msg = format_mode_message(ExecutionMode.LIVE)
        assert 'LIVE' in msg or 'live' in msg.lower()
        assert 'changes' in msg.lower()


class TestConfirmationPrompt:
    """Test confirmation prompt logic."""
    
    def test_no_confirmation_dry_run(self):
        """Test no confirmation needed for dry-run."""
        assert not should_prompt_confirmation(ExecutionMode.DRY_RUN, "cleanup")
        assert not should_prompt_confirmation(ExecutionMode.DRY_RUN, "optimize")
        assert not should_prompt_confirmation(ExecutionMode.DRY_RUN, "delete")
    
    def test_confirmation_for_destructive_live(self):
        """Test confirmation required for destructive operations in live mode."""
        assert should_prompt_confirmation(ExecutionMode.LIVE, "cleanup")
        assert should_prompt_confirmation(ExecutionMode.LIVE, "optimize")
        assert should_prompt_confirmation(ExecutionMode.LIVE, "delete")
        assert should_prompt_confirmation(ExecutionMode.LIVE, "reset")
    
    def test_no_confirmation_for_safe_live(self):
        """Test no confirmation for safe operations in live mode."""
        assert not should_prompt_confirmation(ExecutionMode.LIVE, "status")
        assert not should_prompt_confirmation(ExecutionMode.LIVE, "list")
        assert not should_prompt_confirmation(ExecutionMode.LIVE, "show")
        assert not should_prompt_confirmation(ExecutionMode.LIVE, "help")


class TestDryRunMixin:
    """Test DryRunOrchestratorMixin functionality."""
    
    def test_detect_mode_from_request(self):
        """Test mode detection method."""
        mixin = DryRunOrchestratorMixin()
        
        assert mixin.detect_mode_from_request("preview cleanup") == ExecutionMode.DRY_RUN
        assert mixin.detect_mode_from_request("run cleanup") == ExecutionMode.LIVE
    
    def test_is_dry_run_check(self):
        """Test dry-run check method."""
        mixin = DryRunOrchestratorMixin()
        
        assert mixin.is_dry_run(ExecutionMode.DRY_RUN) == True
        assert mixin.is_dry_run(ExecutionMode.LIVE) == False
    
    def test_print_copyright_header(self, capsys):
        """Test copyright header printing."""
        mixin = DryRunOrchestratorMixin()
        
        mixin.print_copyright_header(
            "Test Operation",
            "1.0",
            ExecutionMode.LIVE,
            "standard"
        )
        
        captured = capsys.readouterr()
        assert "CORTEX" in captured.out
        assert "Asif Hussain" in captured.out
        assert "©" in captured.out or "Copyright" in captured.out
    
    def test_print_copyright_header_dry_run(self, capsys):
        """Test copyright header with dry-run indicator."""
        mixin = DryRunOrchestratorMixin()
        
        mixin.print_copyright_header(
            "Cleanup",
            "2.0",
            ExecutionMode.DRY_RUN,
            "comprehensive"
        )
        
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out or "Preview" in captured.out
        assert "Asif Hussain" in captured.out
    
    def test_format_dry_run_result(self):
        """Test dry-run result formatting."""
        mixin = DryRunOrchestratorMixin()
        
        preview_data = {
            'files_to_delete': ['backup1.txt', 'backup2.txt'],
            'space_freed_mb': 125.5,
            'operations': {
                'cleanup': 'Remove old backups',
                'organize': 'Reorganize files'
            }
        }
        
        result = mixin.format_dry_run_result("Cleanup", preview_data)
        
        assert 'DRY RUN' in result or 'PREVIEW' in result
        assert 'backup1.txt' in result
        assert 'backup2.txt' in result
        assert '125.5' in result or 'space_freed_mb' in result
    
    def test_should_confirm(self):
        """Test should confirm check."""
        mixin = DryRunOrchestratorMixin()
        
        # Dry-run never confirms
        assert not mixin.should_confirm("cleanup", ExecutionMode.DRY_RUN)
        
        # Live mode destructive operations confirm
        assert mixin.should_confirm("cleanup", ExecutionMode.LIVE)
        assert mixin.should_confirm("optimize", ExecutionMode.LIVE)


class MockModule:
    """Mock module for testing mode propagation."""
    def __init__(self):
        self.execution_mode = ExecutionMode.LIVE


class TestModeMixinIntegration:
    """Test mixin integration with modules."""
    
    def test_apply_mode_to_modules(self):
        """Test applying execution mode to modules."""
        mixin = DryRunOrchestratorMixin()
        
        modules = [MockModule(), MockModule(), MockModule()]
        
        # Initially all LIVE
        assert all(m.execution_mode == ExecutionMode.LIVE for m in modules)
        
        # Apply DRY_RUN
        mixin.apply_mode_to_modules(modules, ExecutionMode.DRY_RUN)
        
        # All should be DRY_RUN now
        assert all(m.execution_mode == ExecutionMode.DRY_RUN for m in modules)
        
        # Apply LIVE again
        mixin.apply_mode_to_modules(modules, ExecutionMode.LIVE)
        
        # All should be LIVE
        assert all(m.execution_mode == ExecutionMode.LIVE for m in modules)


# Integration test with example requests
class TestRealWorldExamples:
    """Test real-world request examples."""
    
    @pytest.mark.parametrize("user_request,expected_mode", [
        ("cleanup workspace", ExecutionMode.LIVE),
        ("preview cleanup workspace", ExecutionMode.DRY_RUN),
        ("dry-run cleanup", ExecutionMode.DRY_RUN),
        ("test cleanup before running", ExecutionMode.DRY_RUN),
        ("what would cleanup do", ExecutionMode.DRY_RUN),
        ("show me what would be cleaned", ExecutionMode.DRY_RUN),
        ("actually run cleanup now", ExecutionMode.LIVE),
        ("execute cleanup for real", ExecutionMode.LIVE),
        ("optimize cortex", ExecutionMode.LIVE),
        ("simulate optimization", ExecutionMode.DRY_RUN),
        ("refresh story", ExecutionMode.LIVE),
        ("preview story changes", ExecutionMode.DRY_RUN),
    ])
    def test_real_world_detection(self, user_request, expected_mode):
        """Test detection on real-world requests."""
        mode, _ = detect_execution_mode(user_request)
        assert mode == expected_mode, f"Failed for request: '{user_request}'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
