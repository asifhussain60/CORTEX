"""
Tests for Plan Registry system.

Tests SQLite database creation, plan scanning, and indexing.
"""
import pytest
from pathlib import Path
from datetime import datetime
from src.workflows.plan_registry import PlanRegistry, PlanRegistryError
from src.workflows.plan_metadata import PlanMetadata


class TestPlanRegistryInitialization:
    """Test PlanRegistry initialization and database setup."""
    
    def test_registry_creates_database(self, tmp_path):
        """Should create database file on initialization."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        registry = PlanRegistry(brain_path)
        
        db_path = brain_path / "planning-registry.db"
        assert db_path.exists()
    
    def test_registry_creates_plans_table(self, tmp_path):
        """Should create plans table with correct schema."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        registry = PlanRegistry(brain_path)
        
        # Verify table exists by querying
        result = registry._execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='plans'"
        )
        assert len(result) == 1
    
    def test_registry_schema_has_required_columns(self, tmp_path):
        """Should have all required columns in plans table."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        registry = PlanRegistry(brain_path)
        
        # Get table info
        result = registry._execute_query("PRAGMA table_info(plans)")
        column_names = [row[1] for row in result]
        
        required_columns = {
            "plan_id", "title", "status", "priority", 
            "file_path", "created_date", "updated_date"
        }
        assert required_columns.issubset(set(column_names))
    
    def test_registry_plan_id_is_primary_key(self, tmp_path):
        """Should have plan_id as primary key."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        registry = PlanRegistry(brain_path)
        
        # Get table info
        result = registry._execute_query("PRAGMA table_info(plans)")
        
        # Find plan_id column
        plan_id_info = [row for row in result if row[1] == "plan_id"][0]
        is_primary_key = plan_id_info[5]  # pk field is index 5
        
        assert is_primary_key == 1


class TestPlanRegistryScanning:
    """Test plan file scanning and indexing."""
    
    def test_scan_finds_plan_files(self, tmp_path):
        """Should find all markdown files in planning directory."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Create test plan files
        for i in range(3):
            plan_file = planning_dir / f"plan-{i}.md"
            plan_file.write_text(f"""---
plan_id: TEST-00{i}
title: Test Plan {i}
status: proposed
priority: high
created_date: 2025-12-03
estimated_hours: 10
---

# Plan {i} Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        # Verify 3 plans indexed
        plans = registry._execute_query("SELECT COUNT(*) FROM plans")
        assert plans[0][0] == 3
    
    def test_scan_extracts_metadata_correctly(self, tmp_path):
        """Should extract and store plan metadata correctly."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        plan_file = planning_dir / "test-plan.md"
        plan_file.write_text("""---
plan_id: TEST-001
title: Test Plan
status: in-progress
priority: critical
created_date: 2025-12-03T10:30:00Z
estimated_hours: 20
---

# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        # Query plan
        result = registry._execute_query(
            "SELECT plan_id, title, status, priority FROM plans WHERE plan_id='TEST-001'"
        )
        
        assert result[0][0] == "TEST-001"
        assert result[0][1] == "Test Plan"
        assert result[0][2] == "in-progress"
        assert result[0][3] == "critical"
    
    def test_scan_stores_file_path(self, tmp_path):
        """Should store relative file path for each plan."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        plan_file = planning_dir / "my-plan.md"
        plan_file.write_text("""---
plan_id: TEST-002
title: Path Test
status: proposed
priority: low
created_date: 2025-12-03
estimated_hours: 5
---

# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        # Query file path
        result = registry._execute_query(
            "SELECT file_path FROM plans WHERE plan_id='TEST-002'"
        )
        
        assert "my-plan.md" in result[0][0]
    
    def test_scan_skips_files_without_frontmatter(self, tmp_path):
        """Should skip markdown files without YAML frontmatter."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Valid plan
        valid_plan = planning_dir / "valid.md"
        valid_plan.write_text("""---
plan_id: TEST-003
title: Valid Plan
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---

# Content
""")
        
        # Invalid plan (no frontmatter)
        invalid_plan = planning_dir / "invalid.md"
        invalid_plan.write_text("# Just a regular markdown file\n\nNo frontmatter.")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        # Should only index the valid plan
        plans = registry._execute_query("SELECT COUNT(*) FROM plans")
        assert plans[0][0] == 1
    
    def test_scan_updates_existing_plans(self, tmp_path):
        """Should update plans if they already exist in registry."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        plan_file = planning_dir / "update-test.md"
        plan_file.write_text("""---
plan_id: TEST-004
title: Original Title
status: proposed
priority: low
created_date: 2025-12-03
estimated_hours: 10
---

# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        # Update plan file
        plan_file.write_text("""---
plan_id: TEST-004
title: Updated Title
status: in-progress
priority: high
created_date: 2025-12-03
estimated_hours: 15
---

# Content
""")
        
        # Rescan
        registry.scan_and_index()
        
        # Verify updated
        result = registry._execute_query(
            "SELECT title, status, priority FROM plans WHERE plan_id='TEST-004'"
        )
        
        assert result[0][0] == "Updated Title"
        assert result[0][1] == "in-progress"
        assert result[0][2] == "high"
        
        # Should still have only 1 plan (not duplicated)
        count = registry._execute_query("SELECT COUNT(*) FROM plans")
        assert count[0][0] == 1
    
    def test_scan_handles_nested_directories(self, tmp_path):
        """Should scan nested directories recursively."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        features_dir = planning_dir / "features"
        archived_dir = planning_dir / "archived"
        features_dir.mkdir(parents=True)
        archived_dir.mkdir(parents=True)
        
        # Plans in different directories
        (planning_dir / "root-plan.md").write_text("""---
plan_id: ROOT-001
title: Root Plan
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        (features_dir / "feature-plan.md").write_text("""---
plan_id: FEAT-001
title: Feature Plan
status: in-progress
priority: high
created_date: 2025-12-03
estimated_hours: 20
---
# Content
""")
        
        (archived_dir / "old-plan.md").write_text("""---
plan_id: ARCH-001
title: Archived Plan
status: completed
priority: low
created_date: 2025-12-01
estimated_hours: 5
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        # Should find all 3 plans
        count = registry._execute_query("SELECT COUNT(*) FROM plans")
        assert count[0][0] == 3


class TestPlanRegistryAddPlan:
    """Test adding individual plans to registry."""
    
    def test_add_plan_from_metadata(self, tmp_path):
        """Should add plan from PlanMetadata object."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        registry = PlanRegistry(brain_path)
        
        metadata = PlanMetadata(
            plan_id="ADD-001",
            title="Added Plan",
            status="proposed",
            priority="medium",
            created_date=datetime(2025, 12, 3),
            estimated_hours=15
        )
        
        registry.add_plan(metadata, Path("test/plan.md"))
        
        # Verify added
        result = registry._execute_query(
            "SELECT plan_id, title FROM plans WHERE plan_id='ADD-001'"
        )
        
        assert result[0][0] == "ADD-001"
        assert result[0][1] == "Added Plan"
    
    def test_add_plan_with_relative_path(self, tmp_path):
        """Should store relative path from brain path."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        registry = PlanRegistry(brain_path)
        
        metadata = PlanMetadata(
            plan_id="PATH-001",
            title="Path Test",
            status="proposed",
            priority="low",
            created_date=datetime(2025, 12, 3),
            estimated_hours=10
        )
        
        full_path = brain_path / "documents" / "planning" / "test.md"
        registry.add_plan(metadata, full_path)
        
        # Verify relative path stored
        result = registry._execute_query(
            "SELECT file_path FROM plans WHERE plan_id='PATH-001'"
        )
        
        assert "documents/planning/test.md" in result[0][0]


class TestPlanRegistryGetPlan:
    """Test retrieving plans from registry."""
    
    def test_get_plan_by_id(self, tmp_path):
        """Should retrieve plan by plan_id."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        plan_file = planning_dir / "get-test.md"
        plan_file.write_text("""---
plan_id: GET-001
title: Get Test Plan
status: in-progress
priority: high
created_date: 2025-12-03
estimated_hours: 25
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        plan = registry.get_plan("GET-001")
        
        assert plan is not None
        assert plan["plan_id"] == "GET-001"
        assert plan["title"] == "Get Test Plan"
        assert plan["status"] == "in-progress"
    
    def test_get_plan_returns_none_if_not_found(self, tmp_path):
        """Should return None if plan doesn't exist."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        registry = PlanRegistry(brain_path)
        
        plan = registry.get_plan("NONEXISTENT")
        
        assert plan is None


class TestPlanRegistryListPlans:
    """Test listing plans with filters."""
    
    def test_list_all_plans(self, tmp_path):
        """Should list all plans when no filters applied."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Create multiple plans
        for i, status in enumerate(["proposed", "in-progress", "completed"]):
            plan_file = planning_dir / f"plan-{i}.md"
            plan_file.write_text(f"""---
plan_id: LIST-00{i}
title: Plan {i}
status: {status}
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        plans = registry.list_plans()
        
        assert len(plans) == 3
    
    def test_list_plans_filtered_by_status(self, tmp_path):
        """Should filter plans by status."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Create plans with different statuses
        for i, status in enumerate(["proposed", "proposed", "in-progress"]):
            plan_file = planning_dir / f"plan-{i}.md"
            plan_file.write_text(f"""---
plan_id: STATUS-00{i}
title: Plan {i}
status: {status}
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        proposed_plans = registry.list_plans(status="proposed")
        
        assert len(proposed_plans) == 2
        assert all(p["status"] == "proposed" for p in proposed_plans)
    
    def test_list_plans_filtered_by_priority(self, tmp_path):
        """Should filter plans by priority."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Create plans with different priorities
        for i, priority in enumerate(["high", "high", "low"]):
            plan_file = planning_dir / f"plan-{i}.md"
            plan_file.write_text(f"""---
plan_id: PRIO-00{i}
title: Plan {i}
status: proposed
priority: {priority}
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        high_priority_plans = registry.list_plans(priority="high")
        
        assert len(high_priority_plans) == 2
        assert all(p["priority"] == "high" for p in high_priority_plans)
    
    def test_list_plans_filtered_by_both(self, tmp_path):
        """Should filter by both status and priority."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Create various plans
        combinations = [
            ("proposed", "high"),
            ("proposed", "low"),
            ("in-progress", "high"),
            ("in-progress", "low")
        ]
        
        for i, (status, priority) in enumerate(combinations):
            plan_file = planning_dir / f"plan-{i}.md"
            plan_file.write_text(f"""---
plan_id: BOTH-00{i}
title: Plan {i}
status: {status}
priority: {priority}
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        filtered_plans = registry.list_plans(status="proposed", priority="high")
        
        assert len(filtered_plans) == 1
        assert filtered_plans[0]["status"] == "proposed"
        assert filtered_plans[0]["priority"] == "high"


class TestPlanRegistrySearch:
    """Test searching plans."""
    
    def test_search_by_title(self, tmp_path):
        """Should find plans by title keyword."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        # Create plans with different titles
        titles = ["Environment Setup", "Database Migration", "UI Components"]
        for i, title in enumerate(titles):
            plan_file = planning_dir / f"plan-{i}.md"
            plan_file.write_text(f"""---
plan_id: SEARCH-00{i}
title: {title}
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        results = registry.search_plans("Environment")
        
        assert len(results) == 1
        assert results[0]["title"] == "Environment Setup"
    
    def test_search_by_plan_id(self, tmp_path):
        """Should find plans by plan_id keyword."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        plan_file = planning_dir / "test-plan.md"
        plan_file.write_text("""---
plan_id: UNIQUE-123
title: Test Plan
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        results = registry.search_plans("UNIQUE")
        
        assert len(results) == 1
        assert results[0]["plan_id"] == "UNIQUE-123"
    
    def test_search_case_insensitive(self, tmp_path):
        """Should search case-insensitively."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        plan_file = planning_dir / "test-plan.md"
        plan_file.write_text("""---
plan_id: CASE-001
title: Environment Setup
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        results = registry.search_plans("ENVIRONMENT")
        
        assert len(results) == 1
        assert results[0]["title"] == "Environment Setup"
    
    def test_search_no_matches(self, tmp_path):
        """Should return empty list when no matches."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        plan_file = planning_dir / "test-plan.md"
        plan_file.write_text("""---
plan_id: NOMATCH-001
title: Test Plan
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        results = registry.search_plans("nonexistent")
        
        assert len(results) == 0


class TestPlanRegistryUpdateStatus:
    """Test updating plan status."""
    
    def test_update_existing_plan(self, tmp_path):
        """Should update status of existing plan."""
        brain_path = tmp_path / "cortex-brain"
        planning_dir = brain_path / "documents" / "planning"
        planning_dir.mkdir(parents=True)
        
        plan_file = planning_dir / "test-plan.md"
        plan_file.write_text("""---
plan_id: UPDATE-001
title: Test Plan
status: proposed
priority: medium
created_date: 2025-12-03
estimated_hours: 10
---
# Content
""")
        
        registry = PlanRegistry(brain_path)
        registry.scan_and_index()
        
        result = registry.update_plan_status("UPDATE-001", "completed")
        
        assert result is True
        
        # Verify update
        plan = registry.get_plan("UPDATE-001")
        assert plan["status"] == "completed"
        assert plan["updated_date"] is not None
    
    def test_update_nonexistent_plan(self, tmp_path):
        """Should return False for nonexistent plan."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True)
        
        registry = PlanRegistry(brain_path)
        
        result = registry.update_plan_status("nonexistent", "completed")
        
        assert result is False
