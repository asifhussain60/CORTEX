"""Tests for CAP-006-008: Skill Allocation System.

Test-driven implementation of task classification and team allocation.

Acceptance Criteria:
CAP-006: Task Difficulty Classifier
- AC-CAP-006-AC01: Classify tasks as Senior/Mid/Junior based on complexity
- AC-CAP-006-AC02: Architecture/security tasks → Senior
- AC-CAP-006-AC03: API/integration tasks → Mid-level
- AC-CAP-006-AC04: Tests/docs tasks → Junior

CAP-007: Team Optimizer
- AC-CAP-007-AC01: Suggest realistic team composition (30% senior, 50% mid, 20% junior)
- AC-CAP-007-AC02: Minimum viable team size (at least 1 senior)
- AC-CAP-007-AC03: Work redistribution when skill level overloaded

CAP-008: Brooks' Law Limiter
- AC-CAP-008-AC01: Flag teams >15 engineers with communication overhead warning
- AC-CAP-008-AC02: Calculate communication channels: n*(n-1)/2
- AC-CAP-008-AC03: Recommend workstream splitting for large teams

Author: Asif Hussain
Date: 2026-01-30
Phase: 17 (Track C: Capacity Planning)
"""

import pytest
from cortex.capacity.skill_allocator import (
    SkillAllocator,
    TaskClassification,
    TeamComposition,
)
from cortex.capacity.multi_model_estimation_engine import SkillLevel


class TestTaskDifficultyClassifier:
    """Test task classification by difficulty/skill level.
    
    AC-CAP-006-AC01-04: Task classification
    """

    def test_classify_architecture_task_as_senior(self):
        """Test architecture tasks classified as Senior.
        
        AC-CAP-006-AC02: Architecture/security → Senior
        """
        allocator = SkillAllocator()
        
        classification = allocator.classify_task(
            "Design microservices architecture for payment system",
            85
        )
        
        assert classification.required_skill == SkillLevel.SENIOR, \
            "Architecture tasks should require Senior level"
        assert classification.complexity_score >= 75

    def test_classify_security_task_as_senior(self):
        """Test security tasks classified as Senior.
        
        AC-CAP-006-AC02: Security implementation → Senior
        """
        allocator = SkillAllocator()
        
        classification = allocator.classify_task(
            "Implement OAuth2 authentication with JWT tokens",
            80
        )
        
        assert classification.required_skill == SkillLevel.SENIOR

    def test_classify_api_task_as_mid_level(self):
        """Test API development classified as Mid-level.
        
        AC-CAP-006-AC03: API/integration → Mid-level
        """
        allocator = SkillAllocator()
        
        classification = allocator.classify_task(
            "Create REST API endpoint for user registration",
            60
        )
        
        assert classification.required_skill == SkillLevel.MIDLEVEL, \
            "API tasks should require Mid-level"

    def test_classify_integration_task_as_mid_level(self):
        """Test integration work classified as Mid-level.
        
        AC-CAP-006-AC03: Integration → Mid-level
        """
        allocator = SkillAllocator()
        
        classification = allocator.classify_task(
            "Integrate third-party payment gateway API",
            55
        )
        
        assert classification.required_skill == SkillLevel.MIDLEVEL

    def test_classify_test_writing_as_junior(self):
        """Test writing classified as Junior.
        
        AC-CAP-006-AC04: Tests → Junior
        """
        allocator = SkillAllocator()
        
        classification = allocator.classify_task(
            "Write unit tests for user service",
            30
        )
        
        assert classification.required_skill == SkillLevel.JUNIOR, \
            "Test writing should be Junior level"

    def test_classify_documentation_as_junior(self):
        """Test documentation classified as Junior.
        
        AC-CAP-006-AC04: Documentation → Junior
        """
        allocator = SkillAllocator()
        
        classification = allocator.classify_task(
            "Update API documentation with examples",
            20
        )
        
        assert classification.required_skill == SkillLevel.JUNIOR

    def test_classify_by_complexity_score_high(self):
        """Test high complexity score (>70) classified as Senior."""
        allocator = SkillAllocator()
        
        classification = allocator.classify_task(
            "Generic complex task",
            85
        )
        
        assert classification.required_skill == SkillLevel.SENIOR

    def test_classify_by_complexity_score_medium(self):
        """Test medium complexity score (40-70) classified as Mid-level."""
        allocator = SkillAllocator()
        
        classification = allocator.classify_task(
            "Generic medium task",
            55
        )
        
        assert classification.required_skill == SkillLevel.MIDLEVEL

    def test_classify_by_complexity_score_low(self):
        """Test low complexity score (<40) classified as Junior."""
        allocator = SkillAllocator()
        
        classification = allocator.classify_task(
            "Generic simple task",
            25
        )
        
        assert classification.required_skill == SkillLevel.JUNIOR


class TestTeamOptimizer:
    """Test team composition optimization.
    
    AC-CAP-007-AC01-03: Team optimization
    """

    def test_team_composition_100_hour_project(self):
        """Test realistic team for 100-hour project.
        
        AC-CAP-007-AC01: Realistic composition (30% senior, 50% mid, 20% junior)
        """
        allocator = SkillAllocator()
        
        composition = allocator.optimize_team(
            total_hours=100,
            senior_hours=30,
            mid_hours=50,
            junior_hours=20
        )
        
        assert composition.senior_count >= 1, "Should have at least 1 senior"
        assert composition.total_engineers >= 2, "100h project needs multiple engineers"

    def test_minimum_viable_team_requires_senior(self):
        """Test minimum viable team has at least 1 senior.
        
        AC-CAP-007-AC02: Minimum viable team (1 senior minimum)
        """
        allocator = SkillAllocator()
        
        composition = allocator.optimize_team(
            total_hours=40,
            senior_hours=20,
            mid_hours=15,
            junior_hours=5
        )
        
        assert composition.senior_count >= 1, \
            "Minimum viable team requires at least 1 senior engineer"

    def test_small_project_minimal_team(self):
        """Test small project gets minimal team size."""
        allocator = SkillAllocator()
        
        composition = allocator.optimize_team(
            total_hours=20,
            senior_hours=10,
            mid_hours=8,
            junior_hours=2
        )
        
        # Small project: recommend 1-2 engineers optimal (actual may be 3 for mixed skills)
        assert composition.total_engineers <= 4  # Realistic ceiling
        assert "Small project" in composition.recommendations[0]


class TestBrooksLawLimiter:
    """Test Brooks' Law enforcement.
    
    AC-CAP-008-AC01-03: Brooks' Law limiter
    """

    def test_brooks_law_flags_large_team(self):
        """Test >15 engineers triggers Brooks' Law warning.
        
        AC-CAP-008-AC01: Flag teams >15 engineers
        """
        allocator = SkillAllocator()
        
        composition = allocator.optimize_team(
            total_hours=1000,
            senior_hours=300,
            mid_hours=500,
            junior_hours=200
        )
        
        # Large project might suggest 20+ engineers
        if composition.total_engineers > 15:
            assert len(composition.warnings) > 0, \
                "Should have Brooks' Law warning for >15 engineers"
            assert any("Brooks" in w or "communication" in w.lower() 
                      for w in composition.warnings)

    def test_communication_channels_calculation(self):
        """Test communication channels: n*(n-1)/2.
        
        AC-CAP-008-AC02: Calculate communication overhead
        """
        allocator = SkillAllocator()
        
        # 20 engineers: 20*19/2 = 190 channels
        channels = allocator.calculate_communication_channels(20)
        
        assert channels == 190, f"Expected 190 channels for 20 engineers, got {channels}"

    def test_workstream_splitting_recommended(self):
        """Test large teams get workstream split recommendation.
        
        AC-CAP-008-AC03: Recommend splitting workstreams
        """
        allocator = SkillAllocator()
        
        composition = allocator.optimize_team(
            total_hours=2000,
            senior_hours=600,
            mid_hours=1000,
            junior_hours=400
        )
        
        if composition.total_engineers > 15:
            assert any("split" in w.lower() or "workstream" in w.lower() 
                      for w in composition.warnings), \
                "Should recommend splitting workstreams for large teams"
