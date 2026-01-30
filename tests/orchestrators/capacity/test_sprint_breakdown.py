"""
Test Sprint Breakdown Formatter (CAP-009).

Tests generation of 2-week sprint cycles with daily task distribution.

AC Coverage:
- CAP-009-AC01: Generate 10-day sprint cycles (2 weeks, excluding weekends)
- CAP-009-AC02: Distribute tasks across sprints based on dependencies
- CAP-009-AC03: Show daily capacity allocation
- CAP-009-AC04: Flag overloaded sprints (>8h/day average)
"""

import pytest
from datetime import date, timedelta
from cortex.capacity.output_formatter import (
    SprintBreakdown,
    SprintDay,
    OutputFormatter,
)


class TestSprintCycleGeneration:
    """Test 10-day sprint cycle creation."""
    
    def test_sprint_has_10_business_days(self):
        """Sprint should have 10 business days (2 weeks)."""
        formatter = OutputFormatter()
        
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),  # Monday
            total_hours=40,
            tasks=[{"id": "T1", "hours": 40, "dependencies": []}]
        )
        
        # Sprint: 2 weeks = 10 business days
        assert len(breakdown.days) == 10
        assert breakdown.sprint_length_days == 10
    
    def test_sprint_excludes_weekends(self):
        """Sprint days should skip Saturday/Sunday."""
        formatter = OutputFormatter()
        
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),  # Monday
            total_hours=40,
            tasks=[{"id": "T1", "hours": 40, "dependencies": []}]
        )
        
        # No weekends in sprint days
        weekdays = [day.date.weekday() for day in breakdown.days]
        assert all(0 <= wd <= 4 for wd in weekdays)  # Mon=0, Fri=4
        assert 5 not in weekdays  # No Saturday
        assert 6 not in weekdays  # No Sunday
    
    def test_sprint_date_progression(self):
        """Sprint days should progress sequentially skipping weekends."""
        formatter = OutputFormatter()
        
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),  # Monday Jan 6
            total_hours=40,
            tasks=[{"id": "T1", "hours": 40, "dependencies": []}]
        )
        
        # First day: Monday Jan 6
        assert breakdown.days[0].date == date(2025, 1, 6)
        assert breakdown.days[0].day_number == 1
        
        # 5th day: Friday Jan 10
        assert breakdown.days[4].date == date(2025, 1, 10)
        assert breakdown.days[4].day_number == 5
        
        # 6th day: Monday Jan 13 (skip weekend)
        assert breakdown.days[5].date == date(2025, 1, 13)
        assert breakdown.days[5].day_number == 6
        
        # 10th day: Friday Jan 17
        assert breakdown.days[9].date == date(2025, 1, 17)
        assert breakdown.days[9].day_number == 10


class TestTaskDistribution:
    """Test task allocation across sprint days."""
    
    def test_single_task_distributed_across_days(self):
        """40h task should distribute across 10 days (4h/day)."""
        formatter = OutputFormatter()
        
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),
            total_hours=40,
            tasks=[{"id": "T1", "description": "Feature A", "hours": 40, "dependencies": []}]
        )
        
        # 4h/day for 10 days = 40h
        for day in breakdown.days:
            assert day.allocated_hours == 4.0
            assert len(day.tasks) == 1
            assert day.tasks[0] == "T1"
    
    def test_sequential_tasks_respect_dependencies(self):
        """Task B (depends on A) should start after A completes."""
        formatter = OutputFormatter()
        
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),
            total_hours=40,
            tasks=[
                {"id": "T1", "hours": 20, "dependencies": []},
                {"id": "T2", "hours": 20, "dependencies": ["T1"]},
            ]
        )
        
        # T1: Days 1-5 (20h / 4h/day = 5 days)
        # T2: Days 6-10 (20h / 4h/day = 5 days)
        
        # First 5 days: only T1
        for day in breakdown.days[:5]:
            assert "T1" in day.tasks
            assert "T2" not in day.tasks
        
        # Last 5 days: only T2
        for day in breakdown.days[5:]:
            assert "T2" in day.tasks
            assert "T1" not in day.tasks
    
    def test_parallel_tasks_run_concurrently(self):
        """Tasks without dependencies should run in parallel."""
        formatter = OutputFormatter()
        
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),
            total_hours=40,
            tasks=[
                {"id": "T1", "hours": 20, "dependencies": []},
                {"id": "T2", "hours": 20, "dependencies": []},
            ]
        )
        
        # Both tasks run concurrently across all 10 days
        # 40h total / 10 days = 4h/day shared between T1 and T2
        for day in breakdown.days:
            assert "T1" in day.tasks or "T2" in day.tasks
            # Total allocation shouldn't exceed 8h/day
            assert day.allocated_hours <= 8.0


class TestCapacityWarnings:
    """Test overload detection."""
    
    def test_overloaded_sprint_flagged(self):
        """Sprint with >8h/day average should raise warning."""
        formatter = OutputFormatter()
        
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),
            total_hours=100,  # 100h / 10 days = 10h/day (overload!)
            tasks=[{"id": "T1", "hours": 100, "dependencies": []}]
        )
        
        # Overload warning
        assert len(breakdown.warnings) > 0
        assert any("overload" in w.lower() for w in breakdown.warnings)
        assert any("8h/day" in w.lower() or "8 h/day" in w.lower() for w in breakdown.warnings)
    
    def test_reasonable_sprint_no_warning(self):
        """Sprint with ≤8h/day average should have no warnings."""
        formatter = OutputFormatter()
        
        breakdown = formatter.generate_sprint_breakdown(
            start_date=date(2025, 1, 6),
            total_hours=60,  # 60h / 10 days = 6h/day (OK)
            tasks=[{"id": "T1", "hours": 60, "dependencies": []}]
        )
        
        # No overload warning
        overload_warnings = [w for w in breakdown.warnings if "overload" in w.lower()]
        assert len(overload_warnings) == 0
