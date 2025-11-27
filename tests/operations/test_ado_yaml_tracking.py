"""
Test ADO YAML Tracking System (Phase 2)

Tests:
- YAML file generation
- Schema compliance
- Resume capability (round-trip metadata → YAML → metadata)
- Status transitions (active → completed → active)
- Directory management
- Synchronization (YAML ↔ Markdown)

Author: Asif Hussain
Created: 2025-11-27
"""

import pytest
import yaml
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from src.orchestrators.ado_work_item_orchestrator import (
    ADOWorkItemOrchestrator,
    WorkItemType,
    WorkItemMetadata
)


@pytest.fixture
def temp_ado_dir():
    """Create temporary CORTEX root with ADO directory structure."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create CORTEX structure
    cortex_brain = temp_dir / "cortex-brain" / "documents" / "planning" / "ado"
    cortex_brain.mkdir(parents=True)
    (cortex_brain / "active").mkdir()
    (cortex_brain / "completed").mkdir()
    (cortex_brain / "blocked").mkdir()
    
    summaries = temp_dir / "cortex-brain" / "documents" / "summaries" / "ado"
    summaries.mkdir(parents=True)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def orchestrator(temp_ado_dir):
    """Create ADO orchestrator with temporary directory."""
    return ADOWorkItemOrchestrator(cortex_root=str(temp_ado_dir))


class TestYAMLGeneration:
    """Test YAML file generation."""
    
    def test_yaml_file_created(self, orchestrator):
        """Test that YAML file is created alongside markdown."""
        success, message, metadata = orchestrator.create_work_item(
            title="Test OAuth Login Bug",
            description="Users cannot log in with OAuth",
            work_item_type=WorkItemType.BUG,
            priority=1
        )
        
        assert success
        assert metadata is not None
        
        # Check YAML file exists
        yaml_files = list(orchestrator.active_dir.glob(f"{metadata.work_item_id}*.yaml"))
        assert len(yaml_files) == 1
        
        yaml_file = yaml_files[0]
        assert yaml_file.exists()
    
    def test_yaml_content_structure(self, orchestrator):
        """Test YAML file has correct structure."""
        success, message, metadata = orchestrator.create_work_item(
            title="Add user settings page",
            description="Create settings page for user preferences",
            work_item_type=WorkItemType.STORY,
            priority=2,
            acceptance_criteria=["Settings page loads", "User can save preferences"]
        )
        
        assert success
        
        # Load YAML
        yaml_files = list(orchestrator.active_dir.glob(f"{metadata.work_item_id}*.yaml"))
        yaml_file = yaml_files[0]
        
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Verify required fields
        assert 'work_item_id' in data
        assert 'work_item_type' in data
        assert 'title' in data
        assert 'description' in data
        assert 'status' in data
        assert 'priority' in data
        assert 'created_date' in data
        assert 'updated_date' in data
        assert 'schema_version' in data
        
        # Verify values
        assert data['work_item_id'] == metadata.work_item_id
        assert data['work_item_type'] == 'User Story'  # STORY enum value is "User Story"
        assert data['title'] == "Add user settings page"
        assert data['status'] == 'active'
        assert data['priority'] == 2
        assert data['schema_version'] == '1.0'
    
    def test_yaml_datetime_serialization(self, orchestrator):
        """Test datetime fields are ISO 8601 formatted."""
        success, message, metadata = orchestrator.create_work_item(
            title="Test datetime serialization",
            description="Testing",
            work_item_type=WorkItemType.BUG
        )
        
        assert success
        
        # Load YAML
        yaml_files = list(orchestrator.active_dir.glob(f"{metadata.work_item_id}*.yaml"))
        yaml_file = yaml_files[0]
        
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Verify ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm)
        created = data['created_date']
        updated = data['updated_date']
        
        assert isinstance(created, str)
        assert isinstance(updated, str)
        assert 'T' in created  # ISO format separator
        assert 'T' in updated
    
    def test_yaml_enum_serialization(self, orchestrator):
        """Test WorkItemType enum is serialized correctly."""
        for work_item_type in [WorkItemType.BUG, WorkItemType.STORY, WorkItemType.FEATURE]:
            success, message, metadata = orchestrator.create_work_item(
                title=f"Test {work_item_type.value}",
                description="Testing enum serialization",
                work_item_type=work_item_type
            )
            
            assert success
            
            # Load YAML
            yaml_files = list(orchestrator.active_dir.glob(f"{metadata.work_item_id}*.yaml"))
            yaml_file = yaml_files[0]
            
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            # Verify enum value (should be string, not enum)
            assert data['work_item_type'] == work_item_type.value
            assert isinstance(data['work_item_type'], str)


class TestResumeCapability:
    """Test work item resume from YAML."""
    
    def test_resume_existing_work_item(self, orchestrator):
        """Test resuming work item loads metadata correctly."""
        # Create work item
        success, message, metadata = orchestrator.create_work_item(
            title="Implement payment gateway",
            description="Add Stripe integration",
            work_item_type=WorkItemType.FEATURE,
            priority=1,
            tags=["payment", "stripe"]
        )
        
        assert success
        work_item_id = metadata.work_item_id
        
        # Resume work item
        resume_success, resume_message, resumed_metadata = orchestrator.resume_work_item(work_item_id)
        
        assert resume_success
        assert resumed_metadata is not None
        
        # Verify metadata matches
        assert resumed_metadata.work_item_id == metadata.work_item_id
        assert resumed_metadata.title == metadata.title
        assert resumed_metadata.description == metadata.description
        assert resumed_metadata.work_item_type == metadata.work_item_type
        assert resumed_metadata.priority == metadata.priority
        assert resumed_metadata.tags == metadata.tags
    
    def test_resume_nonexistent_work_item(self, orchestrator):
        """Test resuming nonexistent work item returns error."""
        success, message, metadata = orchestrator.resume_work_item("FAKE-12345")
        
        assert not success
        assert "not found" in message.lower()
        assert metadata is None
    
    def test_resume_datetime_parsing(self, orchestrator):
        """Test datetime fields are parsed correctly."""
        # Create work item
        success, message, metadata = orchestrator.create_work_item(
            title="Test datetime parsing",
            description="Testing",
            work_item_type=WorkItemType.BUG
        )
        
        assert success
        original_created = metadata.created_date
        original_updated = metadata.updated_date
        
        # Resume work item
        resume_success, resume_message, resumed_metadata = orchestrator.resume_work_item(metadata.work_item_id)
        
        assert resume_success
        
        # Verify datetimes are datetime objects
        assert isinstance(resumed_metadata.created_date, datetime)
        assert isinstance(resumed_metadata.updated_date, datetime)
        
        # Verify values match (within 1 second tolerance)
        assert abs((resumed_metadata.created_date - original_created).total_seconds()) < 1
        assert abs((resumed_metadata.updated_date - original_updated).total_seconds()) < 1
    
    def test_resume_enum_parsing(self, orchestrator):
        """Test WorkItemType enum is parsed correctly."""
        for work_item_type in [WorkItemType.BUG, WorkItemType.STORY, WorkItemType.FEATURE]:
            # Create work item
            success, message, metadata = orchestrator.create_work_item(
                title=f"Test {work_item_type.value} enum parsing",
                description="Testing",
                work_item_type=work_item_type
            )
            
            assert success
            
            # Resume work item
            resume_success, resume_message, resumed_metadata = orchestrator.resume_work_item(metadata.work_item_id)
            
            assert resume_success
            assert resumed_metadata.work_item_type == work_item_type
            assert isinstance(resumed_metadata.work_item_type, WorkItemType)


class TestStatusTransitions:
    """Test work item status transitions."""
    
    def test_update_status_to_completed(self, orchestrator):
        """Test moving work item to completed status."""
        # Create work item
        success, message, metadata = orchestrator.create_work_item(
            title="Fix login redirect bug",
            description="Users redirected to wrong page after login",
            work_item_type=WorkItemType.BUG
        )
        
        assert success
        work_item_id = metadata.work_item_id
        
        # Verify in active directory
        active_files = list(orchestrator.active_dir.glob(f"{work_item_id}*.md"))
        assert len(active_files) == 1
        
        # Update status to completed
        update_success, update_message = orchestrator.update_work_item_status(work_item_id, "completed")
        
        assert update_success
        assert "completed" in update_message.lower()
        
        # Verify moved to completed directory
        completed_files = list(orchestrator.completed_dir.glob(f"{work_item_id}*.md"))
        assert len(completed_files) == 1
        
        # Verify removed from active directory
        active_files = list(orchestrator.active_dir.glob(f"{work_item_id}*.md"))
        assert len(active_files) == 0
    
    def test_update_status_to_blocked(self, orchestrator):
        """Test moving work item to blocked status."""
        # Create work item
        success, message, metadata = orchestrator.create_work_item(
            title="Add analytics dashboard",
            description="Create dashboard for analytics",
            work_item_type=WorkItemType.FEATURE
        )
        
        assert success
        work_item_id = metadata.work_item_id
        
        # Update status to blocked
        update_success, update_message = orchestrator.update_work_item_status(work_item_id, "blocked")
        
        assert update_success
        
        # Verify moved to blocked directory
        blocked_files = list(orchestrator.blocked_dir.glob(f"{work_item_id}*.md"))
        assert len(blocked_files) == 1
    
    def test_update_status_reopen(self, orchestrator):
        """Test reopening completed work item."""
        # Create and complete work item
        success, message, metadata = orchestrator.create_work_item(
            title="Test reopen",
            description="Testing",
            work_item_type=WorkItemType.BUG
        )
        
        assert success
        work_item_id = metadata.work_item_id
        
        # Complete
        orchestrator.update_work_item_status(work_item_id, "completed")
        
        # Reopen
        reopen_success, reopen_message = orchestrator.update_work_item_status(work_item_id, "active")
        
        assert reopen_success
        
        # Verify back in active directory
        active_files = list(orchestrator.active_dir.glob(f"{work_item_id}*.md"))
        assert len(active_files) == 1
    
    def test_update_status_invalid(self, orchestrator):
        """Test invalid status is rejected."""
        # Create work item
        success, message, metadata = orchestrator.create_work_item(
            title="Test invalid status",
            description="Testing",
            work_item_type=WorkItemType.BUG
        )
        
        assert success
        
        # Try invalid status
        update_success, update_message = orchestrator.update_work_item_status(metadata.work_item_id, "invalid_status")
        
        assert not update_success
        assert "invalid status" in update_message.lower()
    
    def test_yaml_status_field_updated(self, orchestrator):
        """Test YAML file status field is updated on transition."""
        # Create work item
        success, message, metadata = orchestrator.create_work_item(
            title="Test YAML status update",
            description="Testing",
            work_item_type=WorkItemType.BUG
        )
        
        assert success
        work_item_id = metadata.work_item_id
        
        # Update status
        orchestrator.update_work_item_status(work_item_id, "completed")
        
        # Load YAML from completed directory
        yaml_files = list(orchestrator.completed_dir.glob(f"{work_item_id}*.yaml"))
        assert len(yaml_files) == 1
        
        with open(yaml_files[0], 'r') as f:
            data = yaml.safe_load(f)
        
        # Verify status field updated
        assert data['status'] == 'completed'


class TestDirectoryManagement:
    """Test directory-based file organization."""
    
    def test_active_directory_default(self, orchestrator):
        """Test new work items go to active directory."""
        success, message, metadata = orchestrator.create_work_item(
            title="New work item",
            description="Testing",
            work_item_type=WorkItemType.STORY
        )
        
        assert success
        
        # Verify in active directory
        active_md = list(orchestrator.active_dir.glob(f"{metadata.work_item_id}*.md"))
        active_yaml = list(orchestrator.active_dir.glob(f"{metadata.work_item_id}*.yaml"))
        
        assert len(active_md) == 1
        assert len(active_yaml) == 1
    
    def test_files_move_together(self, orchestrator):
        """Test MD and YAML files move together on status change."""
        # Create work item
        success, message, metadata = orchestrator.create_work_item(
            title="Test file movement",
            description="Testing",
            work_item_type=WorkItemType.BUG
        )
        
        assert success
        work_item_id = metadata.work_item_id
        
        # Verify both files in active
        assert len(list(orchestrator.active_dir.glob(f"{work_item_id}*.md"))) == 1
        assert len(list(orchestrator.active_dir.glob(f"{work_item_id}*.yaml"))) == 1
        
        # Move to completed
        orchestrator.update_work_item_status(work_item_id, "completed")
        
        # Verify both files in completed
        assert len(list(orchestrator.completed_dir.glob(f"{work_item_id}*.md"))) == 1
        assert len(list(orchestrator.completed_dir.glob(f"{work_item_id}*.yaml"))) == 1
        
        # Verify both removed from active
        assert len(list(orchestrator.active_dir.glob(f"{work_item_id}*.md"))) == 0
        assert len(list(orchestrator.active_dir.glob(f"{work_item_id}*.yaml"))) == 0


class TestSynchronization:
    """Test YAML ↔ Markdown synchronization."""
    
    def test_yaml_matches_markdown_title(self, orchestrator):
        """Test YAML title matches markdown title."""
        title = "Implement user authentication"
        success, message, metadata = orchestrator.create_work_item(
            title=title,
            description="Add OAuth authentication",
            work_item_type=WorkItemType.FEATURE
        )
        
        assert success
        
        # Load YAML
        yaml_files = list(orchestrator.active_dir.glob(f"{metadata.work_item_id}*.yaml"))
        with open(yaml_files[0], 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        # Load markdown
        md_files = list(orchestrator.active_dir.glob(f"{metadata.work_item_id}*.md"))
        with open(md_files[0], 'r') as f:
            md_content = f.read()
        
        # Verify titles match
        assert yaml_data['title'] == title
        assert title in md_content
    
    def test_yaml_contains_markdown_data(self, orchestrator):
        """Test YAML contains all essential markdown data."""
        success, message, metadata = orchestrator.create_work_item(
            title="Test synchronization",
            description="This is a test description",
            work_item_type=WorkItemType.BUG,
            priority=1,
            tags=["test", "sync"],
            acceptance_criteria=["Criterion 1", "Criterion 2"]
        )
        
        assert success
        
        # Load YAML
        yaml_files = list(orchestrator.active_dir.glob(f"{metadata.work_item_id}*.yaml"))
        with open(yaml_files[0], 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        # Verify YAML contains all data
        assert yaml_data['title'] == "Test synchronization"
        assert yaml_data['description'] == "This is a test description"
        assert yaml_data['work_item_type'] == "Bug"  # BUG enum value is "Bug"
        assert yaml_data['priority'] == 1
        assert yaml_data['tags'] == ["test", "sync"]
        assert yaml_data['acceptance_criteria'] == ["Criterion 1", "Criterion 2"]
