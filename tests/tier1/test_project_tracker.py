"""
Tests for ProjectTracker - Active planning project state management.

Part of CORTEX v5 Option B: Planning Orchestrator Integration with Tier 1.
"""

import pytest
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from src.tier1.project_tracker import ProjectTracker, ActiveProject


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing."""
    db_path = tmp_path / "test_projects.db"
    return db_path


@pytest.fixture
def tracker(temp_db):
    """Create ProjectTracker instance with temp database."""
    return ProjectTracker(temp_db)


class TestProjectTrackerInitialization:
    """Test ProjectTracker initialization and schema creation."""
    
    def test_init_creates_schema(self, temp_db):
        """Test that initialization creates tier1_active_projects table."""
        tracker = ProjectTracker(temp_db)
        
        # Verify table exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tier1_active_projects'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'tier1_active_projects'
    
    def test_init_creates_indexes(self, temp_db):
        """Test that initialization creates required indexes."""
        tracker = ProjectTracker(temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_active_projects%'
        """)
        indexes = cursor.fetchall()
        conn.close()
        
        index_names = [idx[0] for idx in indexes]
        assert 'idx_active_projects_status' in index_names
        assert 'idx_active_projects_updated' in index_names


class TestProjectCreation:
    """Test project creation and updates."""
    
    def test_create_new_project(self, tracker):
        """Test creating a new project."""
        success = tracker.create_or_update_project(
            project_id="test-project",
            plan_name="Test Project",
            plan_path="/path/to/plan",
            current_phase="Phase 1",
            current_task="Task 1.1",
            progress_percentage=25,
            next_action="/CORTEX Plan Task 1.2"
        )
        
        assert success is True
        
        # Verify project was created
        project = tracker.get_project_by_id("test-project")
        assert project is not None
        assert project.project_id == "test-project"
        assert project.plan_name == "Test Project"
        assert project.current_phase == "Phase 1"
        assert project.current_task == "Task 1.1"
        assert project.progress_percentage == 25
        assert project.next_action == "/CORTEX Plan Task 1.2"
        assert project.status == "active"
    
    def test_update_existing_project(self, tracker):
        """Test updating an existing project."""
        # Create initial project
        tracker.create_or_update_project(
            project_id="test-project",
            plan_name="Test Project",
            plan_path="/path/to/plan",
            current_phase="Phase 1",
            progress_percentage=25
        )
        
        # Update project
        success = tracker.create_or_update_project(
            project_id="test-project",
            plan_name="Test Project Updated",
            plan_path="/path/to/plan",
            current_phase="Phase 2",
            current_task="Task 2.1",
            last_completed="Phase 1",
            progress_percentage=50
        )
        
        assert success is True
        
        # Verify updates
        project = tracker.get_project_by_id("test-project")
        assert project.plan_name == "Test Project Updated"
        assert project.current_phase == "Phase 2"
        assert project.current_task == "Task 2.1"
        assert project.last_completed == "Phase 1"
        assert project.progress_percentage == 50
    
    def test_create_with_artifacts(self, tracker):
        """Test creating project with artifacts list."""
        artifacts = ["00-master-plan.md", "progress.json", "phase-1-report.md"]
        
        tracker.create_or_update_project(
            project_id="test-project",
            plan_name="Test Project",
            plan_path="/path/to/plan",
            artifacts_path=artifacts
        )
        
        project = tracker.get_project_by_id("test-project")
        assert project.artifacts_path == artifacts


class TestProjectRetrieval:
    """Test project retrieval methods."""
    
    def test_get_active_project_single(self, tracker):
        """Test getting most recent active project."""
        tracker.create_or_update_project(
            project_id="project-1",
            plan_name="Project 1",
            plan_path="/path/1"
        )
        
        project = tracker.get_active_project()
        assert project is not None
        assert project.project_id == "project-1"
    
    def test_get_active_project_multiple(self, tracker):
        """Test getting most recent when multiple active projects exist."""
        import time
        
        # Create first project
        tracker.create_or_update_project(
            project_id="project-1",
            plan_name="Project 1",
            plan_path="/path/1"
        )
        
        time.sleep(0.1)  # Ensure different timestamps
        
        # Create second project (more recent)
        tracker.create_or_update_project(
            project_id="project-2",
            plan_name="Project 2",
            plan_path="/path/2"
        )
        
        project = tracker.get_active_project()
        assert project is not None
        assert project.project_id == "project-2"  # Most recent
    
    def test_get_active_project_none_active(self, tracker):
        """Test getting active project when none exist."""
        project = tracker.get_active_project()
        assert project is None
    
    def test_get_project_by_id_exists(self, tracker):
        """Test getting specific project by ID."""
        tracker.create_or_update_project(
            project_id="specific-project",
            plan_name="Specific Project",
            plan_path="/path/specific"
        )
        
        project = tracker.get_project_by_id("specific-project")
        assert project is not None
        assert project.project_id == "specific-project"
    
    def test_get_project_by_id_not_exists(self, tracker):
        """Test getting non-existent project returns None."""
        project = tracker.get_project_by_id("nonexistent")
        assert project is None
    
    def test_get_all_active_projects(self, tracker):
        """Test getting all active projects."""
        tracker.create_or_update_project("project-1", "P1", "/path/1")
        tracker.create_or_update_project("project-2", "P2", "/path/2")
        tracker.create_or_update_project("project-3", "P3", "/path/3")
        
        projects = tracker.get_all_active_projects()
        assert len(projects) == 3
        assert all(p.status == 'active' for p in projects)


class TestProjectStatusManagement:
    """Test project status changes (pause, resume, complete)."""
    
    def test_mark_project_complete(self, tracker):
        """Test marking project as complete."""
        tracker.create_or_update_project(
            project_id="test-project",
            plan_name="Test Project",
            plan_path="/path/to/plan",
            progress_percentage=90
        )
        
        success = tracker.mark_project_complete("test-project")
        assert success is True
        
        project = tracker.get_project_by_id("test-project")
        assert project.status == 'complete'
        assert project.progress_percentage == 100
        assert project.completed_at is not None
    
    def test_mark_nonexistent_project_complete(self, tracker):
        """Test marking non-existent project as complete fails gracefully."""
        success = tracker.mark_project_complete("nonexistent")
        assert success is False
    
    def test_pause_project(self, tracker):
        """Test pausing an active project."""
        tracker.create_or_update_project(
            project_id="test-project",
            plan_name="Test Project",
            plan_path="/path/to/plan"
        )
        
        success = tracker.pause_project("test-project")
        assert success is True
        
        project = tracker.get_project_by_id("test-project")
        assert project.status == 'paused'
    
    def test_resume_project(self, tracker):
        """Test resuming a paused project."""
        tracker.create_or_update_project(
            project_id="test-project",
            plan_name="Test Project",
            plan_path="/path/to/plan"
        )
        tracker.pause_project("test-project")
        
        success = tracker.resume_project("test-project")
        assert success is True
        
        project = tracker.get_project_by_id("test-project")
        assert project.status == 'active'
    
    def test_get_active_project_excludes_paused(self, tracker):
        """Test get_active_project doesn't return paused projects."""
        tracker.create_or_update_project(
            project_id="project-1",
            plan_name="Project 1",
            plan_path="/path/1"
        )
        tracker.pause_project("project-1")
        
        project = tracker.get_active_project()
        assert project is None
    
    def test_get_active_project_excludes_complete(self, tracker):
        """Test get_active_project doesn't return completed projects."""
        tracker.create_or_update_project(
            project_id="project-1",
            plan_name="Project 1",
            plan_path="/path/1"
        )
        tracker.mark_project_complete("project-1")
        
        project = tracker.get_active_project()
        assert project is None


class TestLightweightContext:
    """Test lightweight context generation for middleware."""
    
    def test_get_lightweight_context_active_project(self, tracker):
        """Test getting lightweight context for active project."""
        tracker.create_or_update_project(
            project_id="cortex-v5-refactor",
            plan_name="CORTEX v5 Holistic Refactor",
            plan_path="/path/to/plan",
            current_phase="Phase 5",
            current_task="Task 5.1",
            last_completed="Phase 5.1a",
            progress_percentage=40,
            next_action="/CORTEX Plan ADO Orchestrator v2 Migration",
            orchestrator_used="planning_v5"
        )
        
        context = tracker.get_lightweight_project_context()
        
        assert context is not None
        assert context['project_id'] == "cortex-v5-refactor"
        assert context['plan_name'] == "CORTEX v5 Holistic Refactor"
        assert context['current_phase'] == "Phase 5"
        assert context['current_task'] == "Task 5.1"
        assert context['last_completed'] == "Phase 5.1a"
        assert context['progress'] == 40
        assert context['next_action'] == "/CORTEX Plan ADO Orchestrator v2 Migration"
        assert context['orchestrator'] == "planning_v5"
    
    def test_get_lightweight_context_no_active_project(self, tracker):
        """Test getting lightweight context when no active project."""
        context = tracker.get_lightweight_project_context()
        assert context is None
    
    def test_lightweight_context_token_budget(self, tracker):
        """Test lightweight context stays under 200 token budget."""
        tracker.create_or_update_project(
            project_id="test-project-with-long-names",
            plan_name="Very Long Project Name That Might Exceed Token Budget",
            plan_path="/very/long/path/to/planning/folder/structure",
            current_phase="Phase 99",
            current_task="Task 99.99",
            last_completed="Phase 98.99",
            progress_percentage=75,
            next_action="/CORTEX Plan Very Long Action Description Here",
            orchestrator_used="planning_v5"
        )
        
        context = tracker.get_lightweight_project_context()
        
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        context_json = json.dumps(context)
        estimated_tokens = len(context_json) // 4
        
        assert estimated_tokens < 200, f"Context uses {estimated_tokens} tokens (budget: 200)"


class TestConstraints:
    """Test database constraints and validation."""
    
    def test_status_constraint(self, tracker, temp_db):
        """Test status constraint only allows valid values."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO tier1_active_projects (
                    project_id, plan_name, plan_path, status
                ) VALUES (?, ?, ?, ?)
            """, ("test", "Test", "/path", "invalid_status"))
        
        conn.close()
    
    def test_progress_percentage_constraint(self, tracker, temp_db):
        """Test progress percentage constraint (0-100)."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Test negative value
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO tier1_active_projects (
                    project_id, plan_name, plan_path, progress_percentage
                ) VALUES (?, ?, ?, ?)
            """, ("test", "Test", "/path", -1))
        
        # Test >100 value
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO tier1_active_projects (
                    project_id, plan_name, plan_path, progress_percentage
                ) VALUES (?, ?, ?, ?)
            """, ("test2", "Test", "/path", 101))
        
        conn.close()
