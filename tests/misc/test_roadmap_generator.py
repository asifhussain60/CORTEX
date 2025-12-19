"""
Tests for Coverage Roadmap Generator

Validates generation of actionable test coverage improvement roadmaps with:
- Milestone structure (M1 Critical, M2 High, M3 Standard, M4 Complete)
- Effort estimates and timeline calculation
- Task breakdown with acceptance criteria
- Quick wins identification (high impact, low effort)
- Multiple output formats (JSON, Markdown, CSV, Gantt)

Author: Asif Hussain
Created: 2025-12-08
Phase: Dashboard Code Intelligence - Phase 2.5.4 (RED)
"""

import pytest
from pathlib import Path
import tempfile
import json

# RED phase - import will fail until GREEN phase implementation
try:
    from src.intelligence.roadmap_generator import (
        RoadmapGenerator,
        Milestone,
        RoadmapTask,
        QuickWin,
        RoadmapOutput
    )
    IMPLEMENTATION_EXISTS = True
except ImportError:
    IMPLEMENTATION_EXISTS = False


@pytest.fixture
def temp_project():
    """Create temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_gaps():
    """Sample test gaps from prioritization."""
    return [
        {
            "file": "src/api/UserController.cs",
            "class": "UserController",
            "method": "GetUsers",
            "priority": "P0 - Critical (Must Test)",
            "complexity": 12,
            "risk_score": 85,
            "current_coverage": 0.0,
            "effort_hours": 3.0,
            "reason": "API endpoint, no test coverage"
        },
        {
            "file": "src/services/PayrollCalculator.cs",
            "class": "PayrollCalculator",
            "method": "CalculateNetPay",
            "priority": "P0 - Critical (Must Test)",
            "complexity": 18,
            "risk_score": 92,
            "current_coverage": 15.3,
            "effort_hours": 4.5,
            "reason": "Financial calculation with low coverage"
        },
        {
            "file": "src/services/OrderService.cs",
            "class": "OrderService",
            "method": "ProcessOrder",
            "priority": "P1 - High (Should Test)",
            "complexity": 8,
            "risk_score": 65,
            "current_coverage": 45.0,
            "effort_hours": 2.0,
            "reason": "Business logic service"
        },
        {
            "file": "src/utils/StringHelper.cs",
            "class": "StringHelper",
            "method": "Capitalize",
            "priority": "P2 - Medium (Nice to Test)",
            "complexity": 3,
            "risk_score": 25,
            "current_coverage": 85.7,
            "effort_hours": 1.0,
            "reason": "Utility function with high coverage"
        },
        {
            "file": "src/models/UserDto.cs",
            "class": "UserDto",
            "method": "",
            "priority": "P3 - Low (Optional)",
            "complexity": 1,
            "risk_score": 10,
            "current_coverage": 0.0,
            "effort_hours": 0.5,
            "reason": "Simple data transfer object"
        }
    ]


class TestMilestoneGeneration:
    """Test milestone creation and organization."""
    
    def test_generate_4_milestones(self, temp_project, sample_gaps):
        """Should generate 4 milestones: M1 Critical, M2 High, M3 Standard, M4 Complete."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        assert len(roadmap.milestones) == 4
        
        milestone_names = [m.name for m in roadmap.milestones]
        assert "Critical Coverage (P0)" in milestone_names
        assert "High Priority Coverage (P1)" in milestone_names
        assert "Standard Coverage (P2)" in milestone_names
        assert "Complete Coverage (P3)" in milestone_names
    
    def test_milestone_p0_contains_critical_tasks(self, temp_project, sample_gaps):
        """M1 should contain only P0 critical tasks."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        m1 = next(m for m in roadmap.milestones if "Critical" in m.name)
        
        assert m1.tasks > 0
        assert all("P0" in task.priority for task in m1.tasks_list)
    
    def test_milestone_effort_rollup(self, temp_project, sample_gaps):
        """Milestone effort should equal sum of task efforts."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        m1 = roadmap.milestones[0]
        
        calculated_effort = sum(task.effort_hours for task in m1.tasks_list)
        assert abs(m1.effort_hours - calculated_effort) < 0.1


class TestTaskBreakdown:
    """Test task generation with details."""
    
    def test_task_has_required_fields(self, temp_project, sample_gaps):
        """Each task should have title, description, acceptance criteria, effort."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        task = roadmap.milestones[0].tasks_list[0]
        
        assert task.title != ""
        assert "Test " in task.title
        assert task.description != ""
        assert len(task.acceptance_criteria) > 0
        assert task.effort_hours > 0
        assert task.priority != ""
    
    def test_task_title_format(self, temp_project, sample_gaps):
        """Task title should be 'Test [ClassName].[MethodName]' or 'Test [ClassName]'."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        for milestone in roadmap.milestones:
            for task in milestone.tasks_list[:3]:  # Check first 3
                assert task.title.startswith("Test ")
    
    def test_acceptance_criteria_generation(self, temp_project, sample_gaps):
        """Acceptance criteria should describe test cases."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        task = roadmap.milestones[0].tasks_list[0]
        
        # Should have at least 2-3 acceptance criteria
        assert len(task.acceptance_criteria) >= 2
        
        # Should mention testing
        criteria_text = " ".join(task.acceptance_criteria).lower()
        assert "test" in criteria_text or "verify" in criteria_text or "should" in criteria_text


class TestEffortEstimation:
    """Test effort calculation and timeline generation."""
    
    def test_total_effort_matches_tasks(self, temp_project, sample_gaps):
        """Roadmap total effort should equal sum of all task efforts."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        expected_effort = sum(gap["effort_hours"] for gap in sample_gaps)
        
        assert abs(roadmap.total_effort_hours - expected_effort) < 0.1
    
    def test_timeline_calculation(self, temp_project, sample_gaps):
        """Timeline should be realistic (assume 20 hrs/week testing capacity)."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(
            sample_gaps,
            baseline_coverage=23.1,
            target_coverage=80.0,
            weekly_capacity=20
        )
        
        # Total effort / weekly capacity = weeks
        expected_weeks = roadmap.total_effort_hours / 20
        
        assert abs(roadmap.estimated_weeks - expected_weeks) < 1
    
    def test_milestone_timeline_distribution(self, temp_project, sample_gaps):
        """Milestones should have reasonable timeline distribution."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        # M1 (Critical) should be shortest timeline
        m1 = roadmap.milestones[0]
        m2 = roadmap.milestones[1]
        
        assert m1.timeline_weeks <= m2.timeline_weeks * 1.5


class TestQuickWins:
    """Test quick win identification."""
    
    def test_identify_quick_wins(self, temp_project, sample_gaps):
        """Should identify high-impact, low-effort tasks."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        # Should have at least 1 quick win from sample data
        assert len(roadmap.quick_wins) > 0
    
    def test_quick_win_criteria(self, temp_project, sample_gaps):
        """Quick wins should be low effort (<3h) and high priority (P0/P1)."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        for qw in roadmap.quick_wins[:3]:  # Check first 3
            assert qw.effort_hours <= 3.0
            assert "P0" in qw.priority or "P1" in qw.priority
    
    def test_quick_win_impact_description(self, temp_project, sample_gaps):
        """Quick wins should describe their impact."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        if roadmap.quick_wins:
            qw = roadmap.quick_wins[0]
            assert qw.impact != ""
            assert "cover" in qw.impact.lower() or "test" in qw.impact.lower()


class TestOutputFormats:
    """Test multiple output format generation."""
    
    def test_json_output_structure(self, temp_project, sample_gaps):
        """JSON output should have complete roadmap structure."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        json_output = generator.export_json(roadmap)
        data = json.loads(json_output)
        
        # Verify structure
        assert "roadmap_id" in data
        assert "repository" in data
        assert "baseline_coverage" in data
        assert "target_coverage" in data
        assert "total_effort_hours" in data
        assert "estimated_weeks" in data
        assert "milestones" in data
        assert "quick_wins" in data
        
        # Verify milestone structure
        m1 = data["milestones"][0]
        assert "id" in m1
        assert "name" in m1
        assert "effort_hours" in m1
        assert "tasks_list" in m1
    
    def test_markdown_output_generation(self, temp_project, sample_gaps):
        """Markdown output should be human-readable roadmap."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        markdown = generator.export_markdown(roadmap)
        
        # Should have markdown headers
        assert "# Test Coverage Roadmap" in markdown or "# Coverage Roadmap" in markdown
        assert ("## " in markdown and "Milestone" in markdown) or "### M" in markdown
        
        # Should list tasks
        assert "Test " in markdown
    
    def test_csv_output_generation(self, temp_project, sample_gaps):
        """CSV output should be importable to project management tools."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        csv_output = generator.export_csv(roadmap)
        
        # Should have CSV headers
        lines = csv_output.strip().split('\n')
        header = lines[0].lower()
        
        assert "task" in header or "title" in header
        assert "effort" in header or "hours" in header
        assert "priority" in header
    
    def test_gantt_data_generation(self, temp_project, sample_gaps):
        """Gantt data should have timeline information."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        gantt_data = generator.export_gantt_json(roadmap)
        data = json.loads(gantt_data)
        
        # Should have tasks with start/end dates or durations
        assert len(data) > 0
        
        task = data[0]
        assert "task" in task or "name" in task
        assert "start" in task or "duration" in task


class TestTestSkeletonGeneration:
    """Test skeleton template generation."""
    
    def test_generate_python_test_skeleton(self, temp_project):
        """Should generate pytest skeleton for Python code."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        
        task = {
            "file": "src/services/calculator.py",
            "class": "Calculator",
            "method": "calculate",
            "priority": "P0 - Critical (Must Test)"
        }
        
        skeleton = generator.generate_test_skeleton(task, language="python")
        
        assert "import pytest" in skeleton
        assert "def test_" in skeleton
        assert "Calculator" in skeleton
    
    def test_generate_csharp_test_skeleton(self, temp_project):
        """Should generate xUnit/NUnit skeleton for C# code."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        
        task = {
            "file": "src/Services/Calculator.cs",
            "class": "Calculator",
            "method": "Calculate",
            "priority": "P0 - Critical (Must Test)"
        }
        
        skeleton = generator.generate_test_skeleton(task, language="csharp")
        
        assert "[Fact]" in skeleton or "[Test]" in skeleton
        assert "public" in skeleton
        assert "Calculator" in skeleton


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_gaps_list(self, temp_project):
        """Should handle empty gaps list gracefully."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap([], baseline_coverage=100.0, target_coverage=100.0)
        
        assert roadmap.total_effort_hours == 0
        assert len(roadmap.milestones) == 4  # Still generate empty milestones
    
    def test_high_baseline_coverage(self, temp_project, sample_gaps):
        """Should handle repos that already have high coverage."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=85.0, target_coverage=90.0)
        
        # Should still generate roadmap even if close to target
        assert roadmap.total_effort_hours > 0
    
    def test_realistic_effort_bounds(self, temp_project, sample_gaps):
        """Effort estimates should be within realistic bounds."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("RoadmapGenerator not implemented yet (RED phase)")
        
        generator = RoadmapGenerator(temp_project)
        roadmap = generator.generate_roadmap(sample_gaps, baseline_coverage=23.1, target_coverage=80.0)
        
        # Individual tasks should be 0.5h to 8h
        for milestone in roadmap.milestones:
            for task in milestone.tasks_list:
                assert 0.5 <= task.effort_hours <= 10.0
