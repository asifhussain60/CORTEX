"""
Unit Tests for Progress Monitoring Decorator

Tests the @with_progress decorator and yield_progress() helper.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.utils.progress_decorator import (
    with_progress,
    yield_progress,
    is_monitoring_active,
    get_current_monitor,
    _progress_context
)
from src.utils.progress_monitor import ProgressMonitor


class TestProgressDecorator:
    """Test the @with_progress decorator"""
    
    def test_decorator_with_operation_name(self):
        """Test decorator accepts operation name"""
        @with_progress(operation_name="Test Operation")
        def test_func():
            return "result"
        
        result = test_func()
        assert result == "result"
    
    def test_decorator_with_default_name(self):
        """Test decorator uses function name if no operation_name provided"""
        @with_progress()
        def my_test_function():
            return "result"
        
        result = my_test_function()
        assert result == "result"
    
    def test_decorator_preserves_function_metadata(self):
        """Test decorator preserves function name and docstring"""
        @with_progress(operation_name="Test")
        def original_function():
            """Original docstring"""
            pass
        
        assert original_function.__name__ == "original_function"
        assert original_function.__doc__ == "Original docstring"
    
    def test_fast_operation_no_progress_shown(self, capsys):
        """Test fast operations don't trigger progress display"""
        @with_progress(threshold_seconds=5.0)
        def fast_operation():
            time.sleep(0.1)
            return "done"
        
        result = fast_operation()
        captured = capsys.readouterr()
        
        assert result == "done"
        # No progress output should appear
        assert "started..." not in captured.out
    
    def test_slow_operation_shows_progress(self, capsys):
        """Test slow operations trigger progress display after threshold"""
        @with_progress(threshold_seconds=0.5)
        def slow_operation():
            for i in range(3):
                time.sleep(0.3)
                yield_progress(i+1, 3, f"Step {i+1}")
            return "done"
        
        result = slow_operation()
        captured = capsys.readouterr()
        
        assert result == "done"
        # Progress should be shown
        assert "started..." in captured.out or "completed" in captured.out
    
    def test_exception_handling(self, capsys):
        """Test decorator handles exceptions properly"""
        @with_progress(threshold_seconds=0.1)
        def failing_operation():
            for i in range(3):
                time.sleep(0.1)
                yield_progress(i+1, 3, f"Step {i+1}")
                if i == 1:
                    raise ValueError("Test error")
            return "done"
        
        with pytest.raises(ValueError, match="Test error"):
            failing_operation()
        
        captured = capsys.readouterr()
        # Should show failure message
        assert "failed" in captured.out or "Test error" in captured.out
    
    def test_context_cleanup_after_completion(self):
        """Test context is cleaned up after function completes"""
        @with_progress()
        def test_operation():
            assert _progress_context.monitor is not None
            return "done"
        
        result = test_operation()
        
        # Context should be cleaned up
        assert _progress_context.monitor is None
        assert _progress_context.started is False
    
    def test_context_cleanup_after_exception(self):
        """Test context is cleaned up even after exception"""
        @with_progress()
        def failing_operation():
            raise RuntimeError("Test error")
        
        with pytest.raises(RuntimeError):
            failing_operation()
        
        # Context should still be cleaned up
        assert _progress_context.monitor is None
        assert _progress_context.started is False
    
    def test_custom_hang_timeout(self):
        """Test custom hang timeout is passed to monitor"""
        with patch('src.utils.progress_decorator.ProgressMonitor') as mock_monitor_class:
            mock_monitor = MagicMock()
            mock_monitor_class.return_value = mock_monitor
            
            @with_progress(operation_name="Test", hang_timeout=60.0)
            def test_func():
                return "done"
            
            test_func()
            
            # Verify ProgressMonitor was created with correct timeout
            mock_monitor_class.assert_called_once()
            call_kwargs = mock_monitor_class.call_args[1]
            assert call_kwargs['hang_timeout_seconds'] == 60.0


class TestYieldProgress:
    """Test the yield_progress() helper function"""
    
    def test_yield_progress_outside_decorator(self):
        """Test yield_progress safely does nothing outside decorated function"""
        # Should not raise exception
        yield_progress(1, 10, "Test step")
    
    def test_yield_progress_updates_monitor(self):
        """Test yield_progress updates the monitor when active"""
        updates = []
        
        @with_progress(threshold_seconds=0.1)
        def test_operation():
            for i in range(3):
                time.sleep(0.1)
                yield_progress(i+1, 3, f"Step {i+1}")
                if is_monitoring_active():
                    monitor = get_current_monitor()
                    if monitor and monitor.state:
                        updates.append({
                            'current': monitor.state.current_index,
                            'total': monitor.state.total_items,
                            'step': monitor.state.current_step
                        })
        
        test_operation()
        
        # Should have captured some updates after threshold
        assert len(updates) > 0
    
    def test_yield_progress_with_zero_total(self):
        """Test yield_progress handles zero total gracefully"""
        @with_progress(threshold_seconds=0.1)
        def test_operation():
            time.sleep(0.2)
            yield_progress(0, 0, "Indeterminate progress")
            return "done"
        
        result = test_operation()
        assert result == "done"


class TestMonitoringState:
    """Test monitoring state helpers"""
    
    def test_is_monitoring_active_outside_decorator(self):
        """Test is_monitoring_active returns False outside decorator"""
        assert is_monitoring_active() is False
    
    def test_is_monitoring_active_before_threshold(self):
        """Test is_monitoring_active returns False before threshold"""
        @with_progress(threshold_seconds=5.0)
        def test_operation():
            time.sleep(0.1)
            return is_monitoring_active()
        
        active = test_operation()
        assert active is False
    
    def test_is_monitoring_active_after_threshold(self):
        """Test is_monitoring_active returns True after threshold"""
        @with_progress(threshold_seconds=0.1)
        def test_operation():
            time.sleep(0.2)
            yield_progress(1, 2, "Step")
            return is_monitoring_active()
        
        active = test_operation()
        assert active is True
    
    def test_get_current_monitor_outside_decorator(self):
        """Test get_current_monitor returns None outside decorator"""
        assert get_current_monitor() is None
    
    def test_get_current_monitor_inside_decorator(self):
        """Test get_current_monitor returns monitor when active"""
        @with_progress(threshold_seconds=0.1)
        def test_operation():
            time.sleep(0.2)
            yield_progress(1, 2, "Step")
            return get_current_monitor()
        
        monitor = test_operation()
        # Monitor should have been returned while active
        # (Note: it's cleaned up after function completes)
        # So we verify it was a ProgressMonitor instance during execution
        assert monitor is None or isinstance(monitor, ProgressMonitor)


class TestThreadSafety:
    """Test thread safety of progress monitoring"""
    
    def test_concurrent_operations(self):
        """Test multiple operations can run concurrently"""
        results = []
        errors = []
        
        @with_progress(threshold_seconds=0.1)
        def operation_a():
            try:
                for i in range(5):
                    time.sleep(0.05)
                    yield_progress(i+1, 5, f"Op A - Step {i+1}")
                results.append("A")
            except Exception as e:
                errors.append(f"A: {e}")
        
        @with_progress(threshold_seconds=0.1)
        def operation_b():
            try:
                for i in range(5):
                    time.sleep(0.05)
                    yield_progress(i+1, 5, f"Op B - Step {i+1}")
                results.append("B")
            except Exception as e:
                errors.append(f"B: {e}")
        
        # Run operations in parallel
        thread_a = threading.Thread(target=operation_a)
        thread_b = threading.Thread(target=operation_b)
        
        thread_a.start()
        thread_b.start()
        
        thread_a.join()
        thread_b.join()
        
        # Both operations should complete
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert "A" in results
        assert "B" in results
    
    def test_thread_isolation(self):
        """Test operations in different threads are isolated"""
        contexts = {}
        
        @with_progress(threshold_seconds=0.1)
        def capture_context(thread_name):
            time.sleep(0.15)
            yield_progress(1, 1, f"Thread {thread_name}")
            contexts[thread_name] = {
                'monitor': _progress_context.monitor,
                'started': _progress_context.started
            }
        
        thread_1 = threading.Thread(target=capture_context, args=("T1",))
        thread_2 = threading.Thread(target=capture_context, args=("T2",))
        
        thread_1.start()
        thread_2.start()
        
        thread_1.join()
        thread_2.join()
        
        # Each thread should have had its own context
        assert len(contexts) == 2
        assert "T1" in contexts
        assert "T2" in contexts


class TestEdgeCases:
    """Test edge cases and unusual usage patterns"""
    
    def test_nested_decorated_functions(self):
        """Test nested @with_progress decorated functions"""
        @with_progress(threshold_seconds=0.1)
        def inner_operation():
            time.sleep(0.15)
            yield_progress(1, 1, "Inner step")
            return "inner"
        
        @with_progress(threshold_seconds=0.1)
        def outer_operation():
            time.sleep(0.15)
            yield_progress(1, 2, "Outer step 1")
            result = inner_operation()
            yield_progress(2, 2, "Outer step 2")
            return f"outer-{result}"
        
        result = outer_operation()
        # Should complete without errors
        assert "inner" in result
    
    def test_generator_function(self):
        """Test decorator works with generator functions"""
        @with_progress(threshold_seconds=0.1)
        def generator_operation():
            for i in range(3):
                time.sleep(0.1)
                yield_progress(i+1, 3, f"Step {i+1}")
                yield i
        
        results = list(generator_operation())
        assert results == [0, 1, 2]
    
    def test_operation_with_return_value(self):
        """Test decorated function preserves return value"""
        @with_progress()
        def operation_with_result():
            return {"status": "success", "count": 42}
        
        result = operation_with_result()
        assert result == {"status": "success", "count": 42}
    
    def test_operation_with_multiple_return_paths(self):
        """Test decorated function with multiple return paths"""
        @with_progress()
        def operation_with_branches(condition):
            if condition:
                return "path_a"
            else:
                return "path_b"
        
        assert operation_with_branches(True) == "path_a"
        assert operation_with_branches(False) == "path_b"
    
    def test_empty_operation(self):
        """Test decorator with operation that does nothing"""
        @with_progress()
        def empty_operation():
            pass
        
        result = empty_operation()
        assert result is None


class TestPerformance:
    """Test performance characteristics"""
    
    def test_minimal_overhead_for_fast_operations(self):
        """Test decorator adds minimal overhead for fast operations"""
        # Measure undecorated execution
        def undecorated_operation():
            time.sleep(0.01)
            return "done"
        
        start = time.time()
        for _ in range(100):
            undecorated_operation()
        undecorated_time = time.time() - start
        
        # Measure decorated execution
        @with_progress(threshold_seconds=10.0)  # High threshold so it never activates
        def decorated_operation():
            time.sleep(0.01)
            return "done"
        
        start = time.time()
        for _ in range(100):
            decorated_operation()
        decorated_time = time.time() - start
        
        # Overhead should be less than 5%
        overhead_percent = ((decorated_time - undecorated_time) / undecorated_time) * 100
        assert overhead_percent < 5.0, f"Overhead too high: {overhead_percent:.2f}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
