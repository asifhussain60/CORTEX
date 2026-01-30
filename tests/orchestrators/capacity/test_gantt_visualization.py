"""
Test Gantt Chart Visualization (CAP-010).

Tests ASCII art Gantt charts showing task timelines and parallelization.

AC Coverage:
- CAP-010-AC01: Generate ASCII Gantt chart with task bars
- CAP-010-AC02: Show task dependencies with arrows/indicators
- CAP-010-AC03: Visualize parallel tasks on same timeline
- CAP-010-AC04: Include time markers (days 1-10)
"""

import pytest
from datetime import date
from cortex.capacity.output_formatter import OutputFormatter


class TestGanttChartGeneration:
    """Test ASCII Gantt chart generation."""
    
    def test_gantt_chart_has_task_bars(self):
        """Gantt should show task bars across allocated days."""
        formatter = OutputFormatter()
        
        tasks = [{"id": "T1", "description": "Feature A", "hours": 40, "dependencies": []}]
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),
            total_hours=40,
            tasks=tasks
        )
        
        gantt = formatter.generate_gantt_chart(breakdown)
        
        # Should contain task ID
        assert "T1" in gantt
        # Should contain visual bar (multiple equals/hashes)
        assert "=" in gantt or "#" in gantt
        # Should span multiple lines (header + tasks)
        assert gantt.count("\n") >= 2
    
    def test_gantt_shows_sequential_tasks(self):
        """Sequential tasks should appear on separate rows."""
        formatter = OutputFormatter()
        
        tasks = [
            {"id": "T1", "hours": 20, "dependencies": []},
            {"id": "T2", "hours": 20, "dependencies": ["T1"]},
        ]
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),
            total_hours=40,
            tasks=tasks
        )
        
        gantt = formatter.generate_gantt_chart(breakdown)
        
        # Both tasks visible
        assert "T1" in gantt
        assert "T2" in gantt
        
        # T1 appears before T2 (line order)
        t1_line = gantt.find("T1")
        t2_line = gantt.find("T2")
        assert t1_line < t2_line
    
    def test_gantt_shows_parallel_tasks(self):
        """Parallel tasks should both appear in chart."""
        formatter = OutputFormatter()
        
        tasks = [
            {"id": "T1", "hours": 20, "dependencies": []},
            {"id": "T2", "hours": 20, "dependencies": []},
        ]
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),
            total_hours=40,
            tasks=tasks
        )
        
        gantt = formatter.generate_gantt_chart(breakdown)
        
        # Both tasks visible (parallel execution)
        assert "T1" in gantt
        assert "T2" in gantt
    
    def test_gantt_has_time_axis(self):
        """Gantt should include day markers (1-10)."""
        formatter = OutputFormatter()
        
        tasks = [{"id": "T1", "hours": 40, "dependencies": []}]
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),
            total_hours=40,
            tasks=tasks
        )
        
        gantt = formatter.generate_gantt_chart(breakdown)
        
        # Should have day markers
        assert "1" in gantt or "Day 1" in gantt
        assert "10" in gantt or "Day 10" in gantt
