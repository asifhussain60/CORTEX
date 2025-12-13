"""
Test Suite for ProgressRenderer

RED phase: All tests should FAIL initially (TDD workflow)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import time
from src.operations.utilities.progress_renderer import ProgressRenderer, format_elapsed_time


class TestProgressRendererTaskProgress:
    """Test task-level progress rendering"""
    
    def test_progress_renderer_task_progress(self):
        """Test rendering task progress with percentage"""
        renderer = ProgressRenderer(bar_width=10)
        
        result = renderer.render_task_progress(
            current=5,
            total=10,
            phase_name="Development",
            current_phase=2,
            total_phases=4,
            task_name="Implement authentication",
            elapsed_time="2m 15s"
        )
        
        # Assertions
        assert "🔄" in result
        assert "Phase 2 of 4" in result
        assert "Development" in result
        assert "50%" in result
        assert "(5/10 tasks)" in result
        assert "⏱️ 2m 15s" in result
        assert "📋 Current: Implement authentication" in result
        assert "[" in result and "]" in result  # Progress bar
    
    def test_progress_renderer_bar_formatting(self):
        """Test emoji bar correct length"""
        renderer = ProgressRenderer(bar_width=10)
        
        # Test 0%
        result_0 = renderer.render_task_progress(
            current=0, total=10, phase_name="Test", current_phase=1,
            total_phases=3, task_name="Starting", elapsed_time="0s"
        )
        assert "[░░░░░░░░░░]" in result_0
        assert "0%" in result_0
        
        # Test 50%
        result_50 = renderer.render_task_progress(
            current=5, total=10, phase_name="Test", current_phase=1,
            total_phases=3, task_name="Halfway", elapsed_time="1m"
        )
        assert "[█████░░░░░]" in result_50
        assert "50%" in result_50
        
        # Test 100%
        result_100 = renderer.render_task_progress(
            current=10, total=10, phase_name="Test", current_phase=1,
            total_phases=3, task_name="Complete", elapsed_time="2m"
        )
        assert "[██████████]" in result_100
        assert "100%" in result_100


class TestProgressRendererPhaseTransition:
    """Test phase transition rendering"""
    
    def test_progress_renderer_phase_transition(self):
        """Test transition message format"""
        renderer = ProgressRenderer()
        
        result = renderer.render_phase_transition(
            from_phase="Foundation",
            to_phase="Development",
            completed_tasks=5,
            duration="3m 10s",
            checkpoint_created=True,
            checkpoint_name="cortex-checkpoint-phase-1-foundation-20251213-143022"
        )
        
        # Assertions
        assert "✅" in result
        assert "Foundation Complete!" in result
        assert "(5 tasks, 3m 10s)" in result
        assert "Git checkpoint created" in result
        assert "cortex-checkpoint-phase-1-foundation-20251213-143022" in result
        assert "🔄" in result
        assert "Starting Development" in result
    
    def test_progress_renderer_phase_transition_no_checkpoint(self):
        """Test transition without checkpoint"""
        renderer = ProgressRenderer()
        
        result = renderer.render_phase_transition(
            from_phase="Foundation",
            to_phase="Development",
            completed_tasks=5,
            duration="3m 10s",
            checkpoint_created=False
        )
        
        # Should not mention checkpoint
        assert "Git checkpoint created" not in result
        assert "✅" in result  # Still shows completion
        assert "🔄" in result  # Still shows transition


class TestElapsedTimeFormatting:
    """Test time formatting utility"""
    
    def test_progress_renderer_elapsed_time(self):
        """Test time formatting (2m 15s)"""
        
        # Test seconds only
        assert format_elapsed_time(45) == "45s"
        
        # Test minutes and seconds
        assert format_elapsed_time(135) == "2m 15s"
        
        # Test hours and minutes
        assert format_elapsed_time(3725) == "1h 2m"
        
        # Test exact minute
        assert format_elapsed_time(120) == "2m 0s"
        
        # Test exact hour
        assert format_elapsed_time(3600) == "1h 0m"


class TestProgressRendererIntegration:
    """Test integration with planning orchestrator"""
    
    def test_progress_integration_autonomous_execution(self):
        """Test full plan execution with progress rendering"""
        renderer = ProgressRenderer(bar_width=10)
        
        # Simulate 3-phase plan with 15 tasks
        phases = [
            {"name": "Foundation", "tasks": 5},
            {"name": "Development", "tasks": 7},
            {"name": "Validation", "tasks": 3}
        ]
        
        total_tasks = sum(p["tasks"] for p in phases)
        completed = 0
        outputs = []
        
        for phase_idx, phase in enumerate(phases, 1):
            # Phase tasks
            for task_idx in range(phase["tasks"]):
                completed += 1
                progress_msg = renderer.render_task_progress(
                    current=completed,
                    total=total_tasks,
                    phase_name=phase["name"],
                    current_phase=phase_idx,
                    total_phases=len(phases),
                    task_name=f"Task {completed}",
                    elapsed_time=f"{completed * 10}s"
                )
                outputs.append(progress_msg)
            
            # Phase transition
            if phase_idx < len(phases):
                transition_msg = renderer.render_phase_transition(
                    from_phase=phase["name"],
                    to_phase=phases[phase_idx]["name"],
                    completed_tasks=phase["tasks"],
                    duration=f"{phase['tasks'] * 30}s",
                    checkpoint_created=True,
                    checkpoint_name=f"checkpoint-phase-{phase_idx}"
                )
                outputs.append(transition_msg)
        
        # Assertions
        assert len(outputs) == total_tasks + (len(phases) - 1)  # Tasks + transitions
        assert all("🔄" in o or "✅" in o for o in outputs)
    
    def test_progress_updates_after_each_task(self):
        """Test no batching - updates after each task"""
        renderer = ProgressRenderer()
        
        updates = []
        for i in range(1, 11):
            msg = renderer.render_task_progress(
                current=i, total=10, phase_name="Test", current_phase=1,
                total_phases=1, task_name=f"Task {i}", elapsed_time=f"{i}s"
            )
            updates.append(msg)
        
        # Should have 10 distinct updates
        assert len(updates) == 10
        assert len(set(updates)) == 10  # All unique
    
    def test_progress_no_spam(self):
        """Test max 1 update per task, not per sub-operation"""
        renderer = ProgressRenderer()
        
        # Render same task state twice - should be identical (idempotent)
        msg1 = renderer.render_task_progress(
            current=5, total=10, phase_name="Test", current_phase=1,
            total_phases=1, task_name="Task 5", elapsed_time="5s"
        )
        msg2 = renderer.render_task_progress(
            current=5, total=10, phase_name="Test", current_phase=1,
            total_phases=1, task_name="Task 5", elapsed_time="5s"
        )
        
        assert msg1 == msg2  # Idempotent


class TestProgressRendererCheckpoints:
    """Test git checkpoint status rendering"""
    
    def test_progress_phase_boundaries(self):
        """Test git checkpoint shown at phase boundaries"""
        renderer = ProgressRenderer()
        
        result = renderer.render_checkpoint_status(
            success=True,
            checkpoint_name="cortex-checkpoint-phase-1-foundation-20251213-143022"
        )
        
        assert "✅" in result
        assert "Git checkpoint created" in result
        assert "cortex-checkpoint-phase-1-foundation-20251213-143022" in result
    
    def test_progress_checkpoint_failure(self):
        """Test checkpoint failure rendering"""
        renderer = ProgressRenderer()
        
        result = renderer.render_checkpoint_status(
            success=False,
            error_message="No changes to commit"
        )
        
        assert "⚠️" in result
        assert "Git checkpoint failed" in result
        assert "No changes to commit" in result


class TestProgressRendererPerformance:
    """Test performance requirements"""
    
    def test_progress_performance(self):
        """Test <10ms per update requirement"""
        renderer = ProgressRenderer(bar_width=10)
        
        start_time = time.perf_counter()
        
        # Render 100 progress updates
        for i in range(1, 101):
            renderer.render_task_progress(
                current=i, total=100, phase_name="Performance Test",
                current_phase=1, total_phases=1, task_name=f"Task {i}",
                elapsed_time=f"{i}s"
            )
        
        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) / 100) * 1000
        
        # Must be <10ms per update
        assert avg_time_ms < 10, f"Average render time {avg_time_ms:.2f}ms exceeds 10ms requirement"


class TestProgressRendererOutputCapture:
    """Test stdout capture for Copilot Chat"""
    
    def test_progress_stdout_capture(self):
        """Test Copilot Chat captures output"""
        renderer = ProgressRenderer()
        
        # Render progress
        msg = renderer.render_task_progress(
            current=5, total=10, phase_name="Test", current_phase=1,
            total_phases=1, task_name="Task 5", elapsed_time="5s"
        )
        
        # Should be a string (can be printed to stdout)
        assert isinstance(msg, str)
        assert len(msg) > 0


class TestProgressRendererEmojiRendering:
    """Test emoji display"""
    
    def test_progress_emoji_rendering(self):
        """Test emojis display correctly"""
        renderer = ProgressRenderer()
        
        msg = renderer.render_task_progress(
            current=5, total=10, phase_name="Test", current_phase=1,
            total_phases=1, task_name="Task 5", elapsed_time="5s"
        )
        
        # Check all required emojis present
        required_emojis = ["🔄", "⏱️", "📋"]
        for emoji in required_emojis:
            assert emoji in msg, f"Missing emoji: {emoji}"


class TestProgressRendererTerminalWidth:
    """Test terminal width adaptation"""
    
    def test_progress_terminal_width(self):
        """Test adapts to terminal size"""
        # Small terminal
        renderer_small = ProgressRenderer(bar_width=5)
        msg_small = renderer_small.render_task_progress(
            current=5, total=10, phase_name="Test", current_phase=1,
            total_phases=1, task_name="Task 5", elapsed_time="5s"
        )
        
        # Large terminal
        renderer_large = ProgressRenderer(bar_width=20)
        msg_large = renderer_large.render_task_progress(
            current=5, total=10, phase_name="Test", current_phase=1,
            total_phases=1, task_name="Task 5", elapsed_time="5s"
        )
        
        # Different bar widths
        assert len(msg_small) < len(msg_large)


class TestProgressRendererCompletionSummary:
    """Test final completion summary"""
    
    def test_progress_completion_summary(self):
        """Test completion summary rendering"""
        renderer = ProgressRenderer()
        
        result = renderer.render_completion_summary(
            total_phases=4,
            total_tasks=47,
            total_duration="15m 30s",
            checkpoints_created=4
        )
        
        assert "🎉" in result
        assert "Autonomous Execution Complete!" in result
        assert "Phases: 4/4" in result
        assert "Tasks: 47/47" in result
        assert "Duration: 15m 30s" in result
        assert "Checkpoints: 4" in result
