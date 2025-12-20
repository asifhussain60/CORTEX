"""
Test suite for ProgressRenderer utility

Tests visual progress bars for autonomous execution in Copilot Chat.
Validates emoji-rich formatting, real-time updates, and performance.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from src.operations.utilities.progress_renderer import ProgressRenderer


class TestProgressRendererTaskProgress:
    """Test suite for task-level progress rendering"""
    
    def test_render_task_progress_basic(self):
        """Test basic task progress rendering with all parameters"""
        renderer = ProgressRenderer(bar_width=10)
        
        output = renderer.render_task_progress(
            current=5,
            total=10,
            phase_name="Development",
            current_phase=2,
            total_phases=4,
            task_name="Implement authentication",
            elapsed_time="2m 15s"
        )
        
        # Should contain phase indicator
        assert "Phase 2 of 4: Development" in output
        
        # Should contain progress percentage
        assert "50%" in output
        
        # Should contain task count
        assert "(5/10 tasks)" in output
        
        # Should contain elapsed time
        assert "2m 15s" in output
        
        # Should contain current task name
        assert "Implement authentication" in output
        
        # Should contain emojis
        assert "🔄" in output
        assert "⏱️" in output
        assert "📋" in output
    
    def test_render_task_progress_zero_total_handles_gracefully(self):
        """Test handling of zero total tasks (edge case)"""
        renderer = ProgressRenderer()
        
        output = renderer.render_task_progress(
            current=0,
            total=0,
            phase_name="Setup",
            current_phase=1,
            total_phases=3,
            task_name="Initialize",
            elapsed_time="0s"
        )
        
        # Should handle division by zero gracefully
        assert "0%" in output
        assert "(0/0 tasks)" in output


class TestProgressRendererBarFormatting:
    """Test suite for progress bar formatting"""
    
    def test_progress_bar_formatting_0_percent(self):
        """Test progress bar at 0% completion"""
        renderer = ProgressRenderer(bar_width=10)
        
        output = renderer.render_task_progress(
            current=0,
            total=10,
            phase_name="Phase 1",
            current_phase=1,
            total_phases=3,
            task_name="Task 1",
            elapsed_time="0s"
        )
        
        # Should be all empty blocks
        assert "[░░░░░░░░░░]" in output
        assert "0%" in output
    
    def test_progress_bar_formatting_50_percent(self):
        """Test progress bar at 50% completion"""
        renderer = ProgressRenderer(bar_width=10)
        
        output = renderer.render_task_progress(
            current=5,
            total=10,
            phase_name="Phase 2",
            current_phase=2,
            total_phases=3,
            task_name="Task 5",
            elapsed_time="1m"
        )
        
        # Should be half filled
        assert "[█████░░░░░]" in output
        assert "50%" in output
    
    def test_progress_bar_formatting_100_percent(self):
        """Test progress bar at 100% completion"""
        renderer = ProgressRenderer(bar_width=10)
        
        output = renderer.render_task_progress(
            current=10,
            total=10,
            phase_name="Phase 3",
            current_phase=3,
            total_phases=3,
            task_name="Final Task",
            elapsed_time="5m"
        )
        
        # Should be fully filled
        assert "[██████████]" in output
        assert "100%" in output
    
    def test_progress_bar_custom_width(self):
        """Test progress bar with custom width"""
        renderer = ProgressRenderer(bar_width=20)
        
        output = renderer.render_task_progress(
            current=5,
            total=10,
            phase_name="Phase",
            current_phase=1,
            total_phases=2,
            task_name="Task",
            elapsed_time="1s"
        )
        
        # Should use custom width (20 characters)
        # 50% of 20 = 10 filled blocks
        assert "[██████████░░░░░░░░░░]" in output


class TestProgressRendererPhaseTransition:
    """Test suite for phase transition rendering"""
    
    def test_phase_transition_basic(self):
        """Test basic phase transition message"""
        renderer = ProgressRenderer()
        
        output = renderer.render_phase_transition(
            from_phase="Phase 1: Foundation",
            to_phase="Phase 2: Development",
            completed_tasks=5,
            duration="3m 10s"
        )
        
        # Should contain completion message
        assert "Foundation Complete!" in output
        
        # Should contain task count
        assert "5 tasks" in output
        
        # Should contain duration
        assert "3m 10s" in output
        
        # Should contain next phase
        assert "Starting Phase 2: Development" in output
        
        # Should contain transition emojis
        assert "✅" in output
        assert "🔄" in output
    
    def test_phase_transition_with_git_checkpoint(self):
        """Test phase transition with git checkpoint created"""
        renderer = ProgressRenderer()
        
        checkpoint_name = "cortex-checkpoint-phase-1-foundation-20251213-143022"
        
        output = renderer.render_phase_transition(
            from_phase="Phase 1: Foundation",
            to_phase="Phase 2: Development",
            completed_tasks=8,
            duration="5m 30s",
            checkpoint_created=True,
            checkpoint_name=checkpoint_name
        )
        
        # Should contain checkpoint confirmation
        assert "Git checkpoint created" in output
        assert checkpoint_name in output
    
    def test_phase_transition_without_git_checkpoint(self):
        """Test phase transition without git checkpoint"""
        renderer = ProgressRenderer()
        
        output = renderer.render_phase_transition(
            from_phase="Phase 2: Development",
            to_phase="Phase 3: Validation",
            completed_tasks=12,
            duration="8m 45s",
            checkpoint_created=False
        )
        
        # Should NOT contain checkpoint message
        assert "Git checkpoint" not in output


class TestProgressRendererPerformance:
    """Test suite for performance requirements"""
    
    def test_render_task_progress_performance(self):
        """Test render_task_progress completes in <10ms"""
        renderer = ProgressRenderer()
        
        start_time = time.time()
        
        for _ in range(100):  # Run 100 iterations
            renderer.render_task_progress(
                current=50,
                total=100,
                phase_name="Performance Test",
                current_phase=2,
                total_phases=4,
                task_name="Task 50",
                elapsed_time="5m"
            )
        
        end_time = time.time()
        avg_time_ms = ((end_time - start_time) / 100) * 1000
        
        # Average time per render should be <10ms
        assert avg_time_ms < 10, f"Average render time {avg_time_ms:.2f}ms exceeds 10ms limit"
    
    def test_render_phase_transition_performance(self):
        """Test render_phase_transition completes in <10ms"""
        renderer = ProgressRenderer()
        
        start_time = time.time()
        
        for _ in range(100):  # Run 100 iterations
            renderer.render_phase_transition(
                from_phase="Phase 1",
                to_phase="Phase 2",
                completed_tasks=10,
                duration="5m",
                checkpoint_created=True,
                checkpoint_name="checkpoint-name"
            )
        
        end_time = time.time()
        avg_time_ms = ((end_time - start_time) / 100) * 1000
        
        # Average time per render should be <10ms
        assert avg_time_ms < 10, f"Average render time {avg_time_ms:.2f}ms exceeds 10ms limit"


class TestProgressRendererEmojiSupport:
    """Test suite for emoji rendering"""
    
    def test_emoji_rendering_in_task_progress(self):
        """Test that all required emojis appear in task progress"""
        renderer = ProgressRenderer()
        
        output = renderer.render_task_progress(
            current=5,
            total=10,
            phase_name="Test Phase",
            current_phase=1,
            total_phases=2,
            task_name="Test Task",
            elapsed_time="1m"
        )
        
        # Check for all required emojis
        required_emojis = ["🔄", "⏱️", "📋"]
        for emoji in required_emojis:
            assert emoji in output, f"Missing emoji: {emoji}"
    
    def test_emoji_rendering_in_phase_transition(self):
        """Test that all required emojis appear in phase transition"""
        renderer = ProgressRenderer()
        
        output = renderer.render_phase_transition(
            from_phase="Phase 1",
            to_phase="Phase 2",
            completed_tasks=5,
            duration="3m",
            checkpoint_created=True,
            checkpoint_name="checkpoint"
        )
        
        # Check for all required emojis
        required_emojis = ["✅", "🔄"]
        for emoji in required_emojis:
            assert emoji in output, f"Missing emoji: {emoji}"


class TestProgressRendererTerminalWidth:
    """Test suite for terminal width adaptation"""
    
    @patch('shutil.get_terminal_size')
    def test_terminal_width_detection(self, mock_terminal_size):
        """Test terminal width detection on initialization"""
        mock_terminal_size.return_value = MagicMock(columns=120)
        
        renderer = ProgressRenderer()
        
        assert renderer.terminal_width == 120
    
    @patch('shutil.get_terminal_size')
    def test_terminal_width_fallback_on_error(self, mock_terminal_size):
        """Test fallback to 80 when terminal size cannot be detected"""
        mock_terminal_size.side_effect = Exception("Terminal size unavailable")
        
        renderer = ProgressRenderer()
        
        # Should fallback to 80
        assert renderer.terminal_width == 80


class TestProgressRendererStdoutCapture:
    """Test suite for stdout capture (Copilot Chat compatibility)"""
    
    def test_task_progress_returns_string_for_print(self):
        """Test that render_task_progress returns string suitable for print()"""
        renderer = ProgressRenderer()
        
        output = renderer.render_task_progress(
            current=5,
            total=10,
            phase_name="Test",
            current_phase=1,
            total_phases=2,
            task_name="Task",
            elapsed_time="1m"
        )
        
        # Should be a string
        assert isinstance(output, str)
        
        # Should contain newlines for proper formatting
        assert "\n" in output
        
        # Should be printable without errors
        try:
            print(output)
            success = True
        except Exception:
            success = False
        
        assert success, "Output should be printable to stdout"
    
    def test_phase_transition_returns_string_for_print(self):
        """Test that render_phase_transition returns string suitable for print()"""
        renderer = ProgressRenderer()
        
        output = renderer.render_phase_transition(
            from_phase="Phase 1",
            to_phase="Phase 2",
            completed_tasks=5,
            duration="3m"
        )
        
        # Should be a string
        assert isinstance(output, str)
        
        # Should contain newlines
        assert "\n" in output
        
        # Should be printable
        try:
            print(output)
            success = True
        except Exception:
            success = False
        
        assert success, "Output should be printable to stdout"


class TestProgressRendererNoSpam:
    """Test suite for preventing progress spam"""
    
    def test_task_progress_concise_output(self):
        """Test that task progress output is concise (not spammy)"""
        renderer = ProgressRenderer()
        
        output = renderer.render_task_progress(
            current=5,
            total=10,
            phase_name="Test",
            current_phase=1,
            total_phases=2,
            task_name="Task",
            elapsed_time="1m"
        )
        
        # Output should be short (less than 500 characters)
        assert len(output) < 500, "Progress output too verbose"
        
        # Should be max 3 lines (including newlines)
        lines = [line for line in output.split('\n') if line.strip()]
        assert len(lines) <= 3, f"Too many lines ({len(lines)}), should be ≤3"
    
    def test_phase_transition_concise_output(self):
        """Test that phase transition output is concise"""
        renderer = ProgressRenderer()
        
        output = renderer.render_phase_transition(
            from_phase="Phase 1",
            to_phase="Phase 2",
            completed_tasks=5,
            duration="3m",
            checkpoint_created=True,
            checkpoint_name="checkpoint-name"
        )
        
        # Output should be short
        assert len(output) < 500, "Phase transition output too verbose"
        
        # Should be max 4 lines
        lines = [line for line in output.split('\n') if line.strip()]
        assert len(lines) <= 4, f"Too many lines ({len(lines)}), should be ≤4"
