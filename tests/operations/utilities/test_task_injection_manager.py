"""
Test suite for TaskInjectionManager - Feature 12 (Context-Aware Task Injection)

Tests context-aware task injection during orchestrator execution:
- Mid-execution task injection (no workflow interruption)
- Priority handling (HIGH → MEDIUM → LOW)
- Thread safety (parallel injection)
- ProgressRenderer integration (visual feedback)
- Completion tracking (pending/in-progress/completed)
- Keyboard interrupt handling (Ctrl+T simulation)
- Performance (<10ms injection overhead)

Author: Asif Hussain
Feature: Orchestrator Enhancement Plan v2.0 - Feature 12
"""

import pytest
import time
import threading
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


class TestTaskInjectionBasicOperations:
    """Test suite for basic task injection operations"""
    
    def test_inject_task_basic(self):
        """Test basic task injection"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        task_id = manager.inject_task(
            description="Implement user authentication",
            priority="MEDIUM"
        )
        
        assert task_id is not None
        assert isinstance(task_id, str)
        assert len(task_id) > 0
    
    def test_get_next_task_fifo_order(self):
        """Test that get_next_task returns tasks in FIFO order for same priority"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Inject 3 tasks with same priority
        task_id_1 = manager.inject_task("Task 1", priority="MEDIUM")
        time.sleep(0.01)  # Small delay to ensure timestamp ordering
        task_id_2 = manager.inject_task("Task 2", priority="MEDIUM")
        time.sleep(0.01)
        task_id_3 = manager.inject_task("Task 3", priority="MEDIUM")
        
        # Should get tasks in FIFO order
        task_1 = manager.get_next_task()
        task_2 = manager.get_next_task()
        task_3 = manager.get_next_task()
        
        assert task_1["task_id"] == task_id_1
        assert task_2["task_id"] == task_id_2
        assert task_3["task_id"] == task_id_3
    
    def test_get_next_task_empty_queue(self):
        """Test get_next_task returns None when queue is empty"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        task = manager.get_next_task()
        
        assert task is None
    
    def test_mark_complete_updates_status(self):
        """Test marking task as complete"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        task_id = manager.inject_task("Test task", priority="HIGH")
        success = manager.mark_complete(task_id, result="Success")
        
        assert success is True
        
        # Task should be marked as completed
        status = manager.get_task_status(task_id)
        assert status["status"] == "completed"
        assert status["result"] == "Success"


class TestTaskPriorityHandling:
    """Test suite for task priority handling"""
    
    def test_high_priority_tasks_first(self):
        """Test that HIGH priority tasks are retrieved before MEDIUM/LOW"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Inject tasks in reverse priority order
        low_id = manager.inject_task("Low priority", priority="LOW")
        medium_id = manager.inject_task("Medium priority", priority="MEDIUM")
        high_id = manager.inject_task("High priority", priority="HIGH")
        
        # Should get HIGH first
        task_1 = manager.get_next_task()
        assert task_1["task_id"] == high_id
        assert task_1["priority"] == "HIGH"
        
        # Then MEDIUM
        task_2 = manager.get_next_task()
        assert task_2["task_id"] == medium_id
        assert task_2["priority"] == "MEDIUM"
        
        # Then LOW
        task_3 = manager.get_next_task()
        assert task_3["task_id"] == low_id
        assert task_3["priority"] == "LOW"
    
    def test_priority_ordering_with_mixed_injection(self):
        """Test priority ordering with tasks injected in mixed order"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Inject tasks in mixed priority order
        manager.inject_task("Task 1", priority="MEDIUM")
        manager.inject_task("Task 2", priority="HIGH")
        manager.inject_task("Task 3", priority="LOW")
        manager.inject_task("Task 4", priority="HIGH")
        manager.inject_task("Task 5", priority="MEDIUM")
        
        # Get all tasks - should be ordered: HIGH, HIGH, MEDIUM, MEDIUM, LOW
        priorities = []
        while True:
            task = manager.get_next_task()
            if task is None:
                break
            priorities.append(task["priority"])
        
        assert priorities == ["HIGH", "HIGH", "MEDIUM", "MEDIUM", "LOW"]
    
    def test_default_priority_is_medium(self):
        """Test that default priority is MEDIUM when not specified"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        task_id = manager.inject_task("Default priority task")
        task = manager.get_next_task()
        
        assert task["priority"] == "MEDIUM"


class TestParallelTaskInjection:
    """Test suite for parallel task injection (thread safety)"""
    
    def test_concurrent_task_injection(self):
        """Test that multiple threads can inject tasks concurrently"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        results = []
        
        def inject_tasks(thread_id, count):
            for i in range(count):
                task_id = manager.inject_task(
                    f"Thread {thread_id} Task {i}",
                    priority="MEDIUM"
                )
                results.append(task_id)
        
        # Create 5 threads, each injecting 10 tasks
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=inject_tasks, args=(thread_id, 10))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have 50 unique task IDs
        assert len(results) == 50
        assert len(set(results)) == 50  # All unique
    
    def test_concurrent_get_next_task(self):
        """Test that multiple threads can retrieve tasks concurrently"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Inject 20 tasks
        for i in range(20):
            manager.inject_task(f"Task {i}", priority="MEDIUM")
        
        retrieved_tasks = []
        lock = threading.Lock()
        
        def retrieve_tasks(count):
            for _ in range(count):
                task = manager.get_next_task()
                if task:
                    with lock:
                        retrieved_tasks.append(task["task_id"])
        
        # Create 4 threads, each retrieving 5 tasks
        threads = []
        for _ in range(4):
            thread = threading.Thread(target=retrieve_tasks, args=(5,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have retrieved 20 unique tasks
        assert len(retrieved_tasks) == 20
        assert len(set(retrieved_tasks)) == 20  # All unique


class TestProgressRendererIntegration:
    """Test suite for ProgressRenderer integration"""
    
    def test_injected_task_shows_in_progress_renderer(self):
        """Test that injected tasks are visible in ProgressRenderer"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        from src.operations.utilities.progress_renderer import ProgressRenderer
        
        manager = TaskInjectionManager()
        renderer = ProgressRenderer(bar_width=10)
        
        # Inject task
        task_id = manager.inject_task("Test task", priority="HIGH")
        
        # Render task progress with injected tasks
        output = manager.render_task_list_for_progress(renderer)
        
        assert output is not None
        assert "Test task" in output
        assert "[INJECTED]" in output or "💉" in output  # Visual indicator
    
    def test_completed_injected_task_marked_in_renderer(self):
        """Test that completed injected tasks are marked in ProgressRenderer"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        from src.operations.utilities.progress_renderer import ProgressRenderer
        
        manager = TaskInjectionManager()
        renderer = ProgressRenderer(bar_width=10)
        
        # Inject and complete task
        task_id = manager.inject_task("Completed task", priority="HIGH")
        manager.mark_complete(task_id, result="Done")
        
        # Render should show completion
        output = manager.render_task_list_for_progress(renderer)
        
        assert "✅" in output or "COMPLETED" in output
    
    def test_multiple_injected_tasks_render_correctly(self):
        """Test that multiple injected tasks render with correct priority order"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        from src.operations.utilities.progress_renderer import ProgressRenderer
        
        manager = TaskInjectionManager()
        renderer = ProgressRenderer(bar_width=10)
        
        # Inject tasks with different priorities
        manager.inject_task("Low task", priority="LOW")
        manager.inject_task("High task", priority="HIGH")
        manager.inject_task("Medium task", priority="MEDIUM")
        
        output = manager.render_task_list_for_progress(renderer)
        
        # Should show all 3 tasks
        assert "Low task" in output
        assert "High task" in output
        assert "Medium task" in output
        
        # HIGH should appear before MEDIUM and LOW in output
        high_pos = output.index("High task")
        medium_pos = output.index("Medium task")
        low_pos = output.index("Low task")
        
        assert high_pos < medium_pos < low_pos


class TestTaskCompletionTracking:
    """Test suite for task completion tracking"""
    
    def test_task_status_lifecycle(self):
        """Test task status transitions: pending → in_progress → completed"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Inject task (should be pending)
        task_id = manager.inject_task("Lifecycle test", priority="MEDIUM")
        status = manager.get_task_status(task_id)
        assert status["status"] == "pending"
        
        # Get task (should transition to in_progress)
        task = manager.get_next_task()
        status = manager.get_task_status(task_id)
        assert status["status"] == "in_progress"
        
        # Mark complete (should transition to completed)
        manager.mark_complete(task_id, result="Success")
        status = manager.get_task_status(task_id)
        assert status["status"] == "completed"
    
    def test_get_all_tasks_returns_correct_statuses(self):
        """Test that get_all_tasks returns tasks with correct statuses"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Create tasks in different states
        pending_id = manager.inject_task("Pending task", priority="LOW")
        in_progress_id = manager.inject_task("In progress task", priority="MEDIUM")
        completed_id = manager.inject_task("Completed task", priority="HIGH")
        
        # Transition states
        manager.get_next_task()  # Get completed_id (HIGH priority)
        manager.mark_complete(completed_id, result="Done")
        
        manager.get_next_task()  # Get in_progress_id (MEDIUM priority)
        # Leave in_progress_id in "in_progress" state
        
        # Get all tasks
        all_tasks = manager.get_all_tasks()
        
        # Should have 3 tasks with correct statuses
        assert len(all_tasks) == 3
        
        status_counts = {"pending": 0, "in_progress": 0, "completed": 0}
        for task in all_tasks:
            status_counts[task["status"]] += 1
        
        assert status_counts["pending"] == 1
        assert status_counts["in_progress"] == 1
        assert status_counts["completed"] == 1


class TestKeyboardInterruptHandling:
    """Test suite for keyboard interrupt handling (Ctrl+T injection)"""
    
    @patch('builtins.input', return_value='Add new test for edge case')
    def test_keyboard_interrupt_triggers_injection_prompt(self, mock_input):
        """Test that keyboard interrupt triggers task injection prompt"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Simulate keyboard interrupt handler
        task_id = manager.handle_keyboard_injection()
        
        assert task_id is not None
        assert mock_input.called
        
        # Task should be in queue
        task = manager.get_next_task()
        assert task is not None
        assert "Add new test for edge case" in task["description"]
    
    @patch('builtins.input', return_value='')
    def test_keyboard_interrupt_with_empty_input_cancels(self, mock_input):
        """Test that empty input cancels keyboard injection"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        task_id = manager.handle_keyboard_injection()
        
        assert task_id is None
        assert mock_input.called
    
    def test_keyboard_interrupt_preserves_execution_context(self):
        """Test that keyboard injection doesn't disrupt orchestrator execution"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Simulate orchestrator with tasks
        manager.inject_task("Original task 1", priority="MEDIUM")
        manager.inject_task("Original task 2", priority="MEDIUM")
        
        # Get first task
        task_1 = manager.get_next_task()
        assert "Original task 1" in task_1["description"]
        
        # Simulate keyboard injection during execution
        injected_id = manager.inject_task("Injected task", priority="HIGH")
        
        # HIGH priority task should come next
        task_2 = manager.get_next_task()
        assert task_2["task_id"] == injected_id
        
        # Then resume with original task 2
        task_3 = manager.get_next_task()
        assert "Original task 2" in task_3["description"]


class TestTaskInjectionPerformance:
    """Test suite for performance validation"""
    
    def test_inject_task_performance_under_10ms(self):
        """Test that inject_task completes in <10ms"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Measure injection time
        start = time.time()
        manager.inject_task("Performance test", priority="MEDIUM")
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 10, f"inject_task took {elapsed_ms:.2f}ms (should be <10ms)"
    
    def test_get_next_task_performance_under_10ms(self):
        """Test that get_next_task completes in <10ms"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Pre-populate with tasks
        for i in range(10):
            manager.inject_task(f"Task {i}", priority="MEDIUM")
        
        # Measure retrieval time
        start = time.time()
        manager.get_next_task()
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 10, f"get_next_task took {elapsed_ms:.2f}ms (should be <10ms)"
    
    def test_bulk_injection_performance(self):
        """Test performance with bulk task injection (100 tasks)"""
        from src.operations.utilities.task_injection_manager import TaskInjectionManager
        
        manager = TaskInjectionManager()
        
        # Inject 100 tasks
        start = time.time()
        for i in range(100):
            manager.inject_task(f"Bulk task {i}", priority="MEDIUM")
        elapsed_ms = (time.time() - start) * 1000
        
        # Should average <10ms per task
        avg_ms = elapsed_ms / 100
        assert avg_ms < 10, f"Average injection time: {avg_ms:.2f}ms (should be <10ms)"
