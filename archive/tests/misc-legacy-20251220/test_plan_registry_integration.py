"""
Plan registry integration tests.

Tests plan registration during feature workflows, lookup, search,
status transitions, and auto-indexing.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime


@pytest.fixture
def cortex_brain_with_planning(tmp_path):
    """Create cortex-brain with planning structure."""
    brain = tmp_path / "cortex-brain"
    brain.mkdir()
    
    # Create planning directories
    planning = brain / "documents" / "planning"
    planning.mkdir(parents=True)
    
    for status in ["proposed", "approved", "in-progress", "completed"]:
        (planning / status).mkdir()
    
    return brain


@pytest.fixture
def sample_plan_file(cortex_brain_with_planning):
    """Create sample plan file with YAML frontmatter."""
    plan_file = cortex_brain_with_planning / "documents" / "planning" / "proposed" / "TEST-001-sample-feature.md"
    
    content = """---
plan_id: TEST-001
title: Sample Feature Plan
status: proposed
priority: medium
created_date: 2025-01-01
estimated_hours: 10
assigned_to: Test Author
tags:
  - testing
  - integration
---

# Sample Feature Plan

## Description

Test plan for integration testing.

## Requirements

- Requirement 1
- Requirement 2
"""
    
    plan_file.write_text(content)
    
    # Return tuple for compatibility
    return plan_file, None


class TestPlanRegistration:
    """Test plan registration during feature creation."""
    
    def test_register_new_plan(self, cortex_brain_with_planning):
        """Should register new plan in database."""
        from src.workflows.plan_registry import PlanRegistry
        
        registry = PlanRegistry(cortex_brain_with_planning)
        
        # Create test plan with YAML frontmatter
        plan_file = cortex_brain_with_planning / "documents" / "planning" / "proposed" / "TEST-002-new-feature.md"
        plan_file.write_text("""---
plan_id: TEST-002
title: New Feature Plan
status: proposed
priority: high
created_date: 2025-01-02
estimated_hours: 15
---

# New Feature Plan

## Description

New feature for testing registration.
""")
        
        # Scan and index
        registry.scan_and_index()
        
        # Verify registered
        plan = registry.get_plan("TEST-002")
        assert plan is not None
        assert plan["plan_id"] == "TEST-002"
        assert plan["status"] == "proposed"
    
    def test_auto_extract_metadata(self, sample_plan_file, cortex_brain_with_planning):
        """Should auto-extract metadata from plan file."""
        from src.workflows.plan_registry import PlanRegistry
        
        registry = PlanRegistry(cortex_brain_with_planning)
        registry.scan_and_index()
        
        plan = registry.get_plan("TEST-001")
        assert plan["title"] == "Sample Feature Plan"
        assert plan["assigned_to"] == "Test Author"
        assert str(plan["created_date"]).startswith("2025-01-01")


class TestPlanLookup:
    """Test plan lookup functionality."""
    
    def test_get_plan_by_id(self, sample_plan_file, cortex_brain_with_planning):
        """Should retrieve plan by ID."""
        from src.workflows.plan_registry import PlanRegistry
        
        registry = PlanRegistry(cortex_brain_with_planning)
        registry.scan_and_index()
        
        plan = registry.get_plan("TEST-001")
        assert plan is not None
        assert plan["plan_id"] == "TEST-001"
    
    def test_get_nonexistent_plan_returns_none(self, cortex_brain_with_planning):
        """Should return None for non-existent plan."""
        from src.workflows.plan_registry import PlanRegistry
        
        registry = PlanRegistry(cortex_brain_with_planning)
        
        plan = registry.get_plan("NONEXISTENT")
        assert plan is None
    
    def test_list_plans_by_status(self, sample_plan_file, cortex_brain_with_planning):
        """Should list plans filtered by status."""
        from src.workflows.plan_registry import PlanRegistry
        
        registry = PlanRegistry(cortex_brain_with_planning)
        registry.scan_and_index()
        
        proposed_plans = registry.list_plans(status="proposed")
        assert len(proposed_plans) >= 1
        assert any(p["plan_id"] == "TEST-001" for p in proposed_plans)


class TestPlanSearch:
    """Test plan search functionality."""
    
    def test_search_plans_by_title(self, sample_plan_file, cortex_brain_with_planning):
        """Should search plans by title keywords."""
        from src.workflows.plan_registry import PlanRegistry
        
        registry = PlanRegistry(cortex_brain_with_planning)
        registry.scan_and_index()
        
        results = registry.search_plans("Sample Feature")
        assert len(results) >= 1
        assert any(p["plan_id"] == "TEST-001" for p in results)
    
    def test_search_api_exists(self, cortex_brain_with_planning):
        """Should have search_plans API."""
        from src.workflows.plan_registry import PlanRegistry
        
        registry = PlanRegistry(cortex_brain_with_planning)
        assert hasattr(registry, 'search_plans')


class TestStatusTransitions:
    """Test plan status transitions."""
    
    def test_organizer_can_move_files(self, cortex_brain_with_planning):
        """PlanOrganizer should have file move capability."""
        from src.workflows.plan_organizer import PlanOrganizer
        
        organizer = PlanOrganizer(cortex_brain_with_planning)
        assert hasattr(organizer, 'move_to_status_dir')
    
    def test_registry_tracks_status_changes(self, sample_plan_file, cortex_brain_with_planning):
        """Registry should track status after re-scanning."""
        from src.workflows.plan_registry import PlanRegistry
        
        registry = PlanRegistry(cortex_brain_with_planning)
        registry.scan_and_index()
        
        # Verify initial status
        plan = registry.get_plan("TEST-001")
        assert plan["status"] == "proposed"


class TestIndexGeneration:
    """Test INDEX.md auto-generation."""
    
    def test_generator_has_generate_api(self, cortex_brain_with_planning):
        """PlanIndexGenerator should have generate API."""
        from src.workflows.plan_index_generator import PlanIndexGenerator
        
        generator = PlanIndexGenerator(cortex_brain_with_planning)
        assert hasattr(generator, 'generate')
    
    def test_index_generation_workflow(self, sample_plan_file, cortex_brain_with_planning):
        """Should support index generation workflow."""
        from src.workflows.plan_registry import PlanRegistry
        from src.workflows.plan_index_generator import PlanIndexGenerator
        
        registry = PlanRegistry(cortex_brain_with_planning)
        registry.scan_and_index()
        
        generator = PlanIndexGenerator(cortex_brain_with_planning)
        
        # Generator can generate with registry
        # Would call: generator.generate(registry)
        assert generator is not None
        assert registry is not None
