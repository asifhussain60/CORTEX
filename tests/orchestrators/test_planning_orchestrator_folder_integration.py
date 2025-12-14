"""
Test suite for Planning Orchestrator folder structure integration (Phase 5).

Tests verify that planning_orchestrator.py properly integrates PlanFolderManager
to create organized folder structures when saving plans and artifacts.

Author: CORTEX Planning System 2.0
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestOrchestratorFolderIntegration:
    """Test orchestrator integration with PlanFolderManager."""
    
    @pytest.fixture
    def mock_cortex_root(self, tmp_path):
        """Create mock CORTEX root with required structure."""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        # Create required directories
        brain = cortex_root / "cortex-brain"
        brain.mkdir()
        (brain / "config").mkdir()
        (brain / "documents").mkdir()
        (brain / "documents" / "planning").mkdir()
        (brain / "documents" / "planning" / "features").mkdir()
        (brain / "documents" / "planning" / "features" / "active").mkdir()
        (brain / "documents" / "planning" / "features" / "completed").mkdir()
        
        # Create minimal schema
        schema_path = brain / "config" / "plan-schema.yaml"
        schema = {
            "type": "object",
            "required": ["metadata", "phases"],
            "properties": {
                "metadata": {
                    "type": "object",
                    "required": ["plan_id", "title", "status"]
                },
                "phases": {"type": "array"}
            }
        }
        with open(schema_path, 'w') as f:
            yaml.dump(schema, f)
        
        # Create planning manifest
        manifest_path = brain / "orchestrator-manifests" / "planning-system-2.0-manifest.yaml"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "manifest_version": "2.0.0",
            "orchestrator": "planning-system-2.0",
            "features": {"tdd_integration": True, "folder_structure": {"enabled": False}}
        }
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f)
        
        return cortex_root
    
    @pytest.fixture
    def orchestrator(self, mock_cortex_root):
        """Create orchestrator instance with mocked dependencies."""
        with patch('src.orchestrators.planning_orchestrator.ManifestValidator'):
            with patch('src.orchestrators.planning_orchestrator.GitCheckpointOrchestrator'):
                with patch('src.orchestrators.planning_orchestrator.ThreatModelerAgent'):
                    with patch('src.orchestrators.planning_orchestrator.ResponseTemplateManager'):
                        orchestrator = PlanningOrchestrator(cortex_root=str(mock_cortex_root))
                        return orchestrator
    
    @pytest.fixture
    def valid_plan(self):
        """Valid plan data for testing."""
        return {
            "metadata": {
                "plan_id": "TEST-001",
                "title": "Test Plan",
                "description": "Test plan for orchestrator integration",
                "author": "CORTEX Test Suite",
                "status": "active",
                "version": "1.0"
            },
            "phases": [
                {
                    "phase_id": "phase-1",
                    "name": "Implementation",
                    "tasks": [
                        {
                            "task_id": "task-1",
                            "description": "Test task"
                        }
                    ]
                }
            ]
        }
    
    def test_folder_manager_initialized(self, orchestrator):
        """Test PlanFolderManager is initialized on orchestrator creation."""
        assert hasattr(orchestrator, 'folder_manager')
        assert orchestrator.folder_manager is not None
    
    def test_save_plan_with_folder_structure_enabled(self, orchestrator, valid_plan, tmp_path):
        """Test save_plan creates folder structure when enabled."""
        # Enable folder structure
        orchestrator.folder_manager.is_folder_structure_enabled = MagicMock(return_value=True)
        
        # Mock create_plan_structure to return folder path
        plan_folder = tmp_path / "features" / "active" / "TEST-001"
        plan_folder.mkdir(parents=True, exist_ok=True)
        orchestrator.folder_manager.create_plan_structure = MagicMock(return_value=plan_folder)
        
        # Mock validation to pass
        orchestrator.validate_plan = MagicMock(return_value=(True, []))
        
        # Mock document organizer
        orchestrator.document_organizer = None
        
        # Save plan
        success, message = orchestrator.save_plan(valid_plan)
        
        # Verify folder structure was created
        assert success
        assert orchestrator.folder_manager.create_plan_structure.called
        assert "TEST-001" in message
    
    def test_save_plan_with_folder_structure_disabled(self, orchestrator, valid_plan):
        """Test save_plan uses flat structure when disabled."""
        # Disable folder structure
        orchestrator.folder_manager.is_folder_structure_enabled = MagicMock(return_value=False)
        
        # Mock validation to pass
        orchestrator.validate_plan = MagicMock(return_value=(True, []))
        
        # Mock document organizer to prevent actual file operations
        orchestrator.document_organizer = MagicMock()
        orchestrator.document_organizer.organize_document.return_value = (None, "Skipped")
        
        # Save plan
        success, message = orchestrator.save_plan(valid_plan)
        
        # Verify folder structure was NOT created (flat structure used)
        assert success
    
    def test_save_plan_folder_creation_failure_fallback(self, orchestrator, valid_plan):
        """Test save_plan falls back to flat structure if folder creation fails."""
        # Enable folder structure
        orchestrator.folder_manager.is_folder_structure_enabled = MagicMock(return_value=True)
        
        # Mock create_plan_structure to raise exception
        orchestrator.folder_manager.create_plan_structure = MagicMock(side_effect=Exception("Folder creation failed"))
        
        # Mock validation to pass
        orchestrator.validate_plan = MagicMock(return_value=(True, []))
        
        # Mock document organizer
        orchestrator.document_organizer = MagicMock()
        orchestrator.document_organizer.organize_document.return_value = (None, "Skipped")
        
        # Save plan
        success, message = orchestrator.save_plan(valid_plan)
        
        # Should still succeed using fallback
        assert success
    
    def test_save_plan_completed_status(self, orchestrator, valid_plan, tmp_path):
        """Test save_plan creates folder in completed directory for completed plans."""
        # Set status to completed
        valid_plan["metadata"]["status"] = "completed"
        
        # Enable folder structure
        orchestrator.folder_manager.is_folder_structure_enabled = MagicMock(return_value=True)
        
        # Mock create_plan_structure with completed status
        plan_folder = tmp_path / "features" / "completed" / "TEST-001"
        plan_folder.mkdir(parents=True, exist_ok=True)
        orchestrator.folder_manager.create_plan_structure = MagicMock(return_value=plan_folder)
        
        # Mock validation to pass
        orchestrator.validate_plan = MagicMock(return_value=(True, []))
        
        # Mock document organizer
        orchestrator.document_organizer = None
        
        # Save plan
        success, message = orchestrator.save_plan(valid_plan)
        
        # Verify completed status was passed
        assert success
        call_args = orchestrator.folder_manager.create_plan_structure.call_args
        assert call_args[1]["status"] == "completed"


class TestArtifactSaving:
    """Test artifact saving with folder structure."""
    
    @pytest.fixture
    def mock_cortex_root(self, tmp_path):
        """Create mock CORTEX root."""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain = cortex_root / "cortex-brain"
        brain.mkdir()
        (brain / "config").mkdir()
        (brain / "documents").mkdir()
        (brain / "documents" / "planning").mkdir()
        (brain / "documents" / "planning" / "features").mkdir()
        (brain / "documents" / "planning" / "features" / "active").mkdir()
        
        # Create minimal schema
        schema_path = brain / "config" / "plan-schema.yaml"
        schema = {
            "type": "object",
            "required": ["metadata"],
            "properties": {"metadata": {"type": "object"}}
        }
        with open(schema_path, 'w') as f:
            yaml.dump(schema, f)
        
        # Create planning manifest
        manifest_path = brain / "orchestrator-manifests" / "planning-system-2.0-manifest.yaml"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "manifest_version": "2.0.0",
            "orchestrator": "planning-system-2.0",
            "features": {"tdd_integration": True, "folder_structure": {"enabled": True}}
        }
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f)
        
        return cortex_root
    
    @pytest.fixture
    def orchestrator(self, mock_cortex_root):
        """Create orchestrator instance."""
        with patch('src.orchestrators.planning_orchestrator.ManifestValidator'):
            with patch('src.orchestrators.planning_orchestrator.GitCheckpointOrchestrator'):
                with patch('src.orchestrators.planning_orchestrator.ThreatModelerAgent'):
                    with patch('src.orchestrators.planning_orchestrator.ResponseTemplateManager'):
                        return PlanningOrchestrator(cortex_root=str(mock_cortex_root))
    
    def test_save_artifact_tracker(self, orchestrator, tmp_path):
        """Test save_artifact creates tracker in correct folder."""
        artifact_path = tmp_path / "features" / "active" / "TEST-001" / "trackers" / "progress.md"
        
        # Mock get_artifact_path
        orchestrator.folder_manager.get_artifact_path = MagicMock(return_value=artifact_path)
        
        # Save artifact
        success, message = orchestrator.save_artifact(
            plan_id="TEST-001",
            artifact_type="tracker",
            content="# Progress Tracker\n",
            filename="progress.md",
            status="active"
        )
        
        # Verify
        assert success
        assert orchestrator.folder_manager.get_artifact_path.called
        assert artifact_path.exists()
        assert artifact_path.read_text() == "# Progress Tracker\n"
    
    def test_save_artifact_report(self, orchestrator, tmp_path):
        """Test save_artifact creates report in correct folder."""
        artifact_path = tmp_path / "features" / "active" / "TEST-001" / "reports" / "analysis.md"
        
        # Mock get_artifact_path
        orchestrator.folder_manager.get_artifact_path = MagicMock(return_value=artifact_path)
        
        # Save artifact
        success, message = orchestrator.save_artifact(
            plan_id="TEST-001",
            artifact_type="report",
            content="# Analysis Report\n",
            filename="analysis.md"
        )
        
        # Verify
        assert success
        assert artifact_path.exists()
        assert artifact_path.read_text() == "# Analysis Report\n"
    
    def test_save_artifact_sub_plan(self, orchestrator, tmp_path):
        """Test save_artifact creates sub-plan in correct folder."""
        artifact_path = tmp_path / "features" / "active" / "TEST-001" / "sub-plans" / "phase1.yaml"
        
        # Mock get_artifact_path
        orchestrator.folder_manager.get_artifact_path = MagicMock(return_value=artifact_path)
        
        # Save artifact
        success, message = orchestrator.save_artifact(
            plan_id="TEST-001",
            artifact_type="sub-plan",
            content="phase: 1\ntasks: []",
            filename="phase1.yaml"
        )
        
        # Verify
        assert success
        assert artifact_path.exists()
    
    def test_save_artifact_invalid_path(self, orchestrator):
        """Test save_artifact handles invalid path gracefully."""
        # Mock get_artifact_path to return None
        orchestrator.folder_manager.get_artifact_path = MagicMock(return_value=None)
        
        # Save artifact
        success, message = orchestrator.save_artifact(
            plan_id="TEST-001",
            artifact_type="invalid",
            content="test",
            filename="test.txt"
        )
        
        # Verify failure
        assert not success
        assert "Failed to determine artifact path" in message
    
    def test_save_artifact_write_error(self, orchestrator, tmp_path):
        """Test save_artifact handles write errors gracefully."""
        # Mock get_artifact_path to return read-only path
        artifact_path = tmp_path / "readonly" / "test.txt"
        orchestrator.folder_manager.get_artifact_path = MagicMock(return_value=artifact_path)
        
        # Make parent directory read-only (simulate permission error)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            success, message = orchestrator.save_artifact(
                plan_id="TEST-001",
                artifact_type="tracker",
                content="test",
                filename="test.txt"
            )
            
            # Verify failure
            assert not success
            assert "Failed to save artifact" in message


class TestBackwardCompatibility:
    """Test backward compatibility with flat structure."""
    
    @pytest.fixture
    def mock_cortex_root(self, tmp_path):
        """Create mock CORTEX root."""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain = cortex_root / "cortex-brain"
        brain.mkdir()
        (brain / "config").mkdir()
        (brain / "documents").mkdir()
        (brain / "documents" / "planning").mkdir()
        (brain / "documents" / "planning" / "features").mkdir()
        (brain / "documents" / "planning" / "features" / "active").mkdir()
        
        # Create minimal schema
        schema_path = brain / "config" / "plan-schema.yaml"
        schema = {
            "type": "object",
            "required": ["metadata"],
            "properties": {"metadata": {"type": "object"}}
        }
        with open(schema_path, 'w') as f:
            yaml.dump(schema, f)
        
        # Create planning manifest with folder structure DISABLED
        manifest_path = brain / "orchestrator-manifests" / "planning-system-2.0-manifest.yaml"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "manifest_version": "2.0.0",
            "orchestrator": "planning-system-2.0",
            "features": {"tdd_integration": True, "folder_structure": {"enabled": False}}
        }
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f)
        
        return cortex_root
    
    @pytest.fixture
    def orchestrator(self, mock_cortex_root):
        """Create orchestrator instance."""
        with patch('src.orchestrators.planning_orchestrator.ManifestValidator'):
            with patch('src.orchestrators.planning_orchestrator.GitCheckpointOrchestrator'):
                with patch('src.orchestrators.planning_orchestrator.ThreatModelerAgent'):
                    with patch('src.orchestrators.planning_orchestrator.ResponseTemplateManager'):
                        return PlanningOrchestrator(cortex_root=str(mock_cortex_root))
    
    @pytest.fixture
    def valid_plan(self):
        """Valid plan data."""
        return {
            "metadata": {
                "plan_id": "TEST-001",
                "title": "Test Plan",
                "description": "Test plan for backward compatibility",
                "author": "CORTEX Test Suite",
                "status": "active"
            },
            "phases": [
                {
                    "phase_id": "phase-1",
                    "name": "Implementation",
                    "tasks": [
                        {
                            "task_id": "task-1",
                            "description": "Test task"
                        }
                    ]
                }
            ]
        }
    
    def test_flat_structure_when_disabled(self, orchestrator, valid_plan):
        """Test orchestrator uses flat structure when feature disabled."""
        # Disable folder structure
        orchestrator.folder_manager.is_folder_structure_enabled = MagicMock(return_value=False)
        
        # Mock validation to pass
        orchestrator.validate_plan = MagicMock(return_value=(True, []))
        
        # Mock document organizer
        orchestrator.document_organizer = MagicMock()
        orchestrator.document_organizer.organize_document.return_value = (None, "Skipped")
        
        # Save plan
        success, message = orchestrator.save_plan(valid_plan)
        
        # Verify flat structure used (no folder creation)
        assert success
        
        # Verify plan saved to flat directory
        active_dir = orchestrator.active_plans_dir
        assert (active_dir / "TEST-001.yaml").exists()
    
    def test_no_artifact_organization_when_disabled(self, orchestrator):
        """Test artifacts fail gracefully when folder structure disabled."""
        # Disable folder structure
        orchestrator.folder_manager.is_folder_structure_enabled = MagicMock(return_value=False)
        
        # Mock get_artifact_path to return None (no folder structure)
        orchestrator.folder_manager.get_artifact_path = MagicMock(return_value=None)
        
        # Attempt to save artifact
        success, message = orchestrator.save_artifact(
            plan_id="TEST-001",
            artifact_type="tracker",
            content="test",
            filename="test.txt"
        )
        
        # Should fail gracefully
        assert not success
