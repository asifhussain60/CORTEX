"""Tests for CAP-003: Story Points to Hours Converter.

Test-driven implementation of story point estimation with skill-level conversion.

Acceptance Criteria:
- AC-CAP-003-AC01: Junior: 6-8 hours/point conversion
- AC-CAP-003-AC02: Mid-level: 4-5 hours/point conversion
- AC-CAP-003-AC03: Senior: 2-3 hours/point conversion
- AC-CAP-003-AC04: Architect: 1-2 hours/point conversion
- AC-CAP-003-AC05: Range calculation for confidence intervals

Author: Asif Hussain
Date: 2026-01-30
Phase: 17 (Track C: Capacity Planning)
"""

import pytest
from cortex.capacity.multi_model_estimation_engine import (
    StoryPointEstimator,
    SkillLevel,
)


class TestStoryPointSeniorConversion:
    """Test story point conversion for Senior engineers.
    
    AC-CAP-003-AC03: Senior: 2-3 hours/point
    """

    def test_senior_1_point_converts_to_2_5_hours(self):
        """Test 1 story point for senior = 2.5 hours (average).
        
        AC-CAP-003-AC03: Senior 2-3h/pt, avg 2.5h
        """
        hours = StoryPointEstimator.estimate_hours(
            story_points=1,
            skill_level=SkillLevel.SENIOR
        )
        
        assert hours == 2.5, f"Expected 2.5 hours, got {hours}"

    def test_senior_5_points_converts_to_12_5_hours(self):
        """Test 5 story points for senior = 12.5 hours."""
        hours = StoryPointEstimator.estimate_hours(
            story_points=5,
            skill_level=SkillLevel.SENIOR
        )
        
        assert hours == 12.5, f"Expected 12.5 hours (5 * 2.5), got {hours}"

    def test_senior_range_1_point(self):
        """Test range for 1 story point senior: 2-3 hours.
        
        AC-CAP-003-AC05: Range calculation
        """
        min_hours, max_hours = StoryPointEstimator.estimate_range(
            story_points=1,
            skill_level=SkillLevel.SENIOR
        )
        
        assert min_hours == 2.0, f"Expected min 2.0, got {min_hours}"
        assert max_hours == 3.0, f"Expected max 3.0, got {max_hours}"

    def test_senior_range_8_points(self):
        """Test range for 8 story points senior: 16-24 hours."""
        min_hours, max_hours = StoryPointEstimator.estimate_range(
            story_points=8,
            skill_level=SkillLevel.SENIOR
        )
        
        assert min_hours == 16.0  # 8 * 2
        assert max_hours == 24.0  # 8 * 3


class TestStoryPointMidLevelConversion:
    """Test story point conversion for Mid-level engineers.
    
    AC-CAP-003-AC02: Mid-level: 4-5 hours/point
    """

    def test_mid_level_1_point_converts_to_4_5_hours(self):
        """Test 1 story point for mid-level = 4.5 hours (average).
        
        AC-CAP-003-AC02: Mid-level 4-5h/pt, avg 4.5h
        """
        hours = StoryPointEstimator.estimate_hours(
            story_points=1,
            skill_level=SkillLevel.MIDLEVEL
        )
        
        assert hours == 4.5, f"Expected 4.5 hours, got {hours}"

    def test_mid_level_5_points_converts_to_22_5_hours(self):
        """Test 5 story points for mid-level = 22.5 hours."""
        hours = StoryPointEstimator.estimate_hours(
            story_points=5,
            skill_level=SkillLevel.MIDLEVEL
        )
        
        assert hours == 22.5, f"Expected 22.5 hours (5 * 4.5), got {hours}"

    def test_mid_level_range_1_point(self):
        """Test range for 1 story point mid-level: 4-5 hours.
        
        AC-CAP-003-AC05: Range calculation
        """
        min_hours, max_hours = StoryPointEstimator.estimate_range(
            story_points=1,
            skill_level=SkillLevel.MIDLEVEL
        )
        
        assert min_hours == 4.0
        assert max_hours == 5.0


class TestStoryPointJuniorConversion:
    """Test story point conversion for Junior engineers.
    
    AC-CAP-003-AC01: Junior: 6-8 hours/point
    """

    def test_junior_1_point_converts_to_7_hours(self):
        """Test 1 story point for junior = 7 hours (average).
        
        AC-CAP-003-AC01: Junior 6-8h/pt, avg 7h
        """
        hours = StoryPointEstimator.estimate_hours(
            story_points=1,
            skill_level=SkillLevel.JUNIOR
        )
        
        assert hours == 7.0, f"Expected 7.0 hours, got {hours}"

    def test_junior_5_points_converts_to_35_hours(self):
        """Test 5 story points for junior = 35 hours."""
        hours = StoryPointEstimator.estimate_hours(
            story_points=5,
            skill_level=SkillLevel.JUNIOR
        )
        
        assert hours == 35.0, f"Expected 35.0 hours (5 * 7), got {hours}"

    def test_junior_range_1_point(self):
        """Test range for 1 story point junior: 6-8 hours.
        
        AC-CAP-003-AC05: Range calculation
        """
        min_hours, max_hours = StoryPointEstimator.estimate_range(
            story_points=1,
            skill_level=SkillLevel.JUNIOR
        )
        
        assert min_hours == 6.0
        assert max_hours == 8.0


class TestStoryPointArchitectConversion:
    """Test story point conversion for Architect level.
    
    AC-CAP-003-AC04: Architect: 1-2 hours/point
    """

    def test_architect_1_point_converts_to_1_5_hours(self):
        """Test 1 story point for architect = 1.5 hours (average).
        
        AC-CAP-003-AC04: Architect 1-2h/pt, avg 1.5h
        """
        hours = StoryPointEstimator.estimate_hours(
            story_points=1,
            skill_level=SkillLevel.ARCHITECT
        )
        
        assert hours == 1.5, f"Expected 1.5 hours, got {hours}"

    def test_architect_8_points_converts_to_12_hours(self):
        """Test 8 story points for architect = 12 hours."""
        hours = StoryPointEstimator.estimate_hours(
            story_points=8,
            skill_level=SkillLevel.ARCHITECT
        )
        
        assert hours == 12.0, f"Expected 12.0 hours (8 * 1.5), got {hours}"

    def test_architect_range_1_point(self):
        """Test range for 1 story point architect: 1-2 hours.
        
        AC-CAP-003-AC05: Range calculation
        """
        min_hours, max_hours = StoryPointEstimator.estimate_range(
            story_points=1,
            skill_level=SkillLevel.ARCHITECT
        )
        
        assert min_hours == 1.0
        assert max_hours == 2.0


class TestStoryPointSkillLevelComparison:
    """Test relative skill level velocities.
    
    Verify that higher skill levels complete work faster.
    """

    def test_senior_faster_than_junior(self):
        """Test senior completes same work faster than junior."""
        story_points = 5
        
        senior_hours = StoryPointEstimator.estimate_hours(story_points, SkillLevel.SENIOR)
        junior_hours = StoryPointEstimator.estimate_hours(story_points, SkillLevel.JUNIOR)
        
        assert senior_hours < junior_hours, \
            f"Senior ({senior_hours}h) should be faster than junior ({junior_hours}h)"

    def test_architect_faster_than_senior(self):
        """Test architect completes same work faster than senior."""
        story_points = 5
        
        architect_hours = StoryPointEstimator.estimate_hours(story_points, SkillLevel.ARCHITECT)
        senior_hours = StoryPointEstimator.estimate_hours(story_points, SkillLevel.SENIOR)
        
        assert architect_hours < senior_hours, \
            f"Architect ({architect_hours}h) should be faster than senior ({senior_hours}h)"

    def test_skill_level_velocity_ordering(self):
        """Test all skill levels ordered by velocity (fastest to slowest)."""
        story_points = 10
        
        architect = StoryPointEstimator.estimate_hours(story_points, SkillLevel.ARCHITECT)
        senior = StoryPointEstimator.estimate_hours(story_points, SkillLevel.SENIOR)
        mid = StoryPointEstimator.estimate_hours(story_points, SkillLevel.MIDLEVEL)
        junior = StoryPointEstimator.estimate_hours(story_points, SkillLevel.JUNIOR)
        
        # Assert ordering: Architect < Senior < Mid < Junior
        assert architect < senior < mid < junior, \
            f"Expected ordering: Architect({architect}) < Senior({senior}) < Mid({mid}) < Junior({junior})"


class TestStoryPointEdgeCases:
    """Test edge cases for story point conversion."""

    def test_zero_story_points_returns_zero_hours(self):
        """Test 0 story points = 0 hours."""
        hours = StoryPointEstimator.estimate_hours(0, SkillLevel.SENIOR)
        assert hours == 0.0

    def test_13_point_epic_warning(self):
        """Test that 13+ points suggests task should be split.
        
        Note: This test verifies large story point handling.
        In practice, 13+ point tasks should be decomposed.
        """
        hours = StoryPointEstimator.estimate_hours(13, SkillLevel.SENIOR)
        
        # 13 * 2.5 = 32.5 hours (still calculable, but large)
        assert hours == 32.5
        
        # In production, this would trigger a warning/recommendation
        # to split the epic into smaller stories
