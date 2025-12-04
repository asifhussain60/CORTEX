"""
Tests for plan index generator.

This module tests auto-generation of planning/INDEX.md with plans grouped
by status in table format.
"""

import pytest
from pathlib import Path
from src.workflows.plan_index_generator import PlanIndexGenerator


@pytest.fixture
def generator(tmp_path):
    """Create a plan index generator with temporary brain path."""
    brain_path = tmp_path / "cortex-brain"
    brain_path.mkdir(parents=True)
    return PlanIndexGenerator(brain_path)


@pytest.fixture
def registry_with_multiple_plans(tmp_path):
    """Create registry with plans in different statuses."""
    from src.workflows.plan_registry import PlanRegistry
    
    brain_path = tmp_path / "cortex-brain"
    planning_dir = brain_path / "documents" / "planning"
    planning_dir.mkdir(parents=True)
    
    # Create plans with different statuses
    plans = [
        ("active-plan.md", "in-progress", "high", "Active Feature"),
        ("completed-plan.md", "completed", "medium", "Completed Feature"),
        ("proposed-plan.md", "proposed", "low", "Proposed Feature"),
        ("cancelled-plan.md", "cancelled", "low", "Cancelled Feature"),
    ]
    
    for filename, status, priority, title in plans:
        plan_file = planning_dir / filename
        plan_id = filename.replace(".md", "").upper()
        plan_file.write_text(f"""---
plan_id: {plan_id}
title: {title}
status: {status}
priority: {priority}
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
    
    registry = PlanRegistry(brain_path)
    registry.scan_and_index()
    return brain_path, registry


class TestPlanIndexGeneratorInit:
    """Test index generator initialization."""
    
    def test_generator_stores_brain_path(self, generator):
        """Should store brain path."""
        assert generator.brain_path.exists()
    
    def test_generator_knows_index_location(self, generator):
        """Should know where to write INDEX.md."""
        expected = generator.brain_path / "documents" / "planning" / "INDEX.md"
        assert generator.index_path == expected


class TestPlanIndexGeneratorGenerate:
    """Test index generation."""
    
    def test_generate_creates_index_file(self, registry_with_multiple_plans):
        """Should create INDEX.md file."""
        brain_path, registry = registry_with_multiple_plans
        generator = PlanIndexGenerator(brain_path)
        
        generator.generate(registry)
        
        index_path = brain_path / "documents" / "planning" / "INDEX.md"
        assert index_path.exists()
    
    def test_generate_includes_header(self, registry_with_multiple_plans):
        """Should include header with title and date."""
        brain_path, registry = registry_with_multiple_plans
        generator = PlanIndexGenerator(brain_path)
        
        generator.generate(registry)
        
        index_path = brain_path / "documents" / "planning" / "INDEX.md"
        content = index_path.read_text()
        
        assert "# Planning Index" in content
        assert "Last Updated:" in content
    
    def test_generate_groups_by_status(self, registry_with_multiple_plans):
        """Should group plans by status with headers."""
        brain_path, registry = registry_with_multiple_plans
        generator = PlanIndexGenerator(brain_path)
        
        generator.generate(registry)
        
        index_path = brain_path / "documents" / "planning" / "INDEX.md"
        content = index_path.read_text()
        
        assert "## In Progress" in content
        assert "## Completed" in content
        assert "## Proposed" in content
        assert "## Cancelled" in content
    
    def test_generate_includes_table_format(self, registry_with_multiple_plans):
        """Should format plans as markdown table."""
        brain_path, registry = registry_with_multiple_plans
        generator = PlanIndexGenerator(brain_path)
        
        generator.generate(registry)
        
        index_path = brain_path / "documents" / "planning" / "INDEX.md"
        content = index_path.read_text()
        
        # Check for table headers
        assert "| ID | Title | Priority | Link |" in content
        assert "|---|---|---|---|" in content
    
    def test_generate_includes_plan_details(self, registry_with_multiple_plans):
        """Should include plan details in table rows."""
        brain_path, registry = registry_with_multiple_plans
        generator = PlanIndexGenerator(brain_path)
        
        generator.generate(registry)
        
        index_path = brain_path / "documents" / "planning" / "INDEX.md"
        content = index_path.read_text()
        
        # Check for plan data
        assert "ACTIVE-PLAN" in content
        assert "Active Feature" in content
        assert "high" in content
        assert "[View](active-plan.md)" in content
    
    def test_generate_orders_by_priority(self, tmp_path):
        """Should order plans by priority within each status."""
        from src.workflows.plan_registry import PlanRegistry
        
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Create plans with same status, different priorities
        priorities = [("low", "Low Plan"), ("high", "High Plan"), ("medium", "Medium Plan")]
        for i, (priority, title) in enumerate(priorities):
            plan_file = planning_dir / f"plan-{i}.md"
            plan_file.write_text(f"""---
plan_id: PLAN-{i}
title: {title}
status: in-progress
priority: {priority}
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        generator = PlanIndexGenerator(brain_path)
        generator.generate(registry)
        
        content = (brain_path / "documents" / "planning" / "INDEX.md").read_text()
        
        # High should appear before medium, medium before low
        high_pos = content.find("High Plan")
        medium_pos = content.find("Medium Plan")
        low_pos = content.find("Low Plan")
        
        assert high_pos < medium_pos < low_pos


class TestPlanIndexGeneratorEmptyStates:
    """Test handling of empty states."""
    
    def test_generate_with_no_plans(self, tmp_path):
        """Should handle empty registry gracefully."""
        from src.workflows.plan_registry import PlanRegistry
        
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True)
        
        registry = PlanRegistry(brain_path)
        generator = PlanIndexGenerator(brain_path)
        
        generator.generate(registry)
        
        index_path = brain_path / "documents" / "planning" / "INDEX.md"
        assert index_path.exists()
        
        content = index_path.read_text()
        assert "# Planning Index" in content
    
    def test_generate_skips_empty_status_sections(self, tmp_path):
        """Should not show status sections with no plans."""
        from src.workflows.plan_registry import PlanRegistry
        
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Create only one plan
        plan_file = planning_dir / "only-plan.md"
        plan_file.write_text("""---
plan_id: ONLY-001
title: Only Plan
status: in-progress
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        generator = PlanIndexGenerator(brain_path)
        generator.generate(registry)
        
        content = (brain_path / "documents" / "planning" / "INDEX.md").read_text()
        
        # Should have In Progress section
        assert "## In Progress" in content
        
        # Should NOT have empty Completed/Proposed/Cancelled sections
        completed_count = content.count("## Completed")
        assert completed_count == 0
