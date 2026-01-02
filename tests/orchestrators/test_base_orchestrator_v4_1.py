"""
Tests for BaseOrchestrator v4.1.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.base.base_orchestrator_v4_1 import (
    BaseOrchestratorV4_1,
    PhaseStatus,
    PhaseResult,
    ArtifactMetadata
)
from src.database.planning_state_db import PlanningStateDB


# Test Orchestrator Implementation
class TestOrchestrator(BaseOrchestratorV4_1):
    """Minimal orchestrator for testing."""
    
    def execute(self, user_request: str, **kwargs):
        """Simple test execution."""
        from src.orchestrators.base.base_orchestrator import (
            OrchestratorResult,
            OrchestratorStatus
        )
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Test execution complete",
            data={'user_request': user_request}
        )
    
    def _execute_phase_logic(self, phase_number, phase_config, **kwargs):
        """Test phase execution."""
        # Create a test artifact
        artifact_path = f"test_artifact_{phase_number}.txt"
        return [artifact_path]


@pytest.fixture
def temp_config():
    """Create temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config = {
            'schema_version': '5.0',
            'orchestrator': {
                'name': 'test_orchestrator',
                'version': '5.0',
                'type': 'autonomous'
            },
            'templates': {
                'base_path': 'cortex-brain/templates'
            }
        }
        yaml.dump(config, f)
        yield f.name
    
    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def temp_db():
    """Create temporary database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = PlanningStateDB(db_path=db_path)
    yield db
    
    # Cleanup
    db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def test_orchestrator(temp_config, temp_db):
    """Create test orchestrator instance."""
    orch = TestOrchestrator(
        config_path=temp_config,
        state_db=temp_db,
        plan_id='test-plan-123'
    )
    return orch


class TestBaseOrchestratorV4_1Initialization:
    """Test orchestrator initialization."""
    
    def test_init_with_valid_config(self, temp_config, temp_db):
        """Test initialization with valid config."""
        orch = TestOrchestrator(
            config_path=temp_config,
            state_db=temp_db,
            plan_id='test-plan'
        )
        
        assert orch.name == 'test_orchestrator'
        assert orch.version == '5.0'
        assert orch.plan_id == 'test-plan'
        assert orch.state_db == temp_db
    
    def test_init_missing_config(self, temp_db):
        """Test initialization with missing config file."""
        with pytest.raises(FileNotFoundError):
            TestOrchestrator(
                config_path='nonexistent.yaml',
                state_db=temp_db
            )
    
    def test_init_invalid_config(self, temp_db):
        """Test initialization with invalid config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'invalid': 'config'}, f)
            config_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Missing required config section"):
                TestOrchestrator(
                    config_path=config_path,
                    state_db=temp_db
                )
        finally:
            Path(config_path).unlink(missing_ok=True)


class TestConfigLoading:
    """Test configuration loading and validation."""
    
    def test_load_valid_config(self, test_orchestrator):
        """Test loading valid configuration."""
        config = test_orchestrator.config
        
        assert config['schema_version'] == '5.0'
        assert config['orchestrator']['name'] == 'test_orchestrator'
        assert config['orchestrator']['type'] == 'autonomous'
    
    def test_validate_config_missing_section(self, temp_db):
        """Test config validation with missing section."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'schema_version': '5.0'}, f)  # Missing 'orchestrator'
            config_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Missing required config section: orchestrator"):
                TestOrchestrator(config_path=config_path, state_db=temp_db)
        finally:
            Path(config_path).unlink(missing_ok=True)
    
    def test_validate_config_invalid_type(self, temp_db):
        """Test config validation with invalid orchestrator type."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config = {
                'schema_version': '5.0',
                'orchestrator': {
                    'name': 'test',
                    'version': '1.0',
                    'type': 'invalid_type'
                }
            }
            yaml.dump(config, f)
            config_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid orchestrator type"):
                TestOrchestrator(config_path=config_path, state_db=temp_db)
        finally:
            Path(config_path).unlink(missing_ok=True)


class TestPhaseExecution:
    """Test phase execution."""
    
    def test_execute_phase_success(self, test_orchestrator, temp_db):
        """Test successful phase execution."""
        # Create plan first
        plan_id = temp_db.create_plan('test-feature', {})
        test_orchestrator.plan_id = plan_id
        
        phase_config = {
            'name': 'Test Phase',
            'description': 'A test phase'
        }
        
        result = test_orchestrator.execute_phase(0, phase_config)
        
        assert result.status == PhaseStatus.COMPLETED
        assert result.phase_number == 0
        assert result.name == 'Test Phase'
        assert result.duration_seconds > 0
        assert len(result.artifacts) == 1
    
    def test_execute_phase_failure(self, test_orchestrator, temp_db):
        """Test phase execution with error."""
        # Create plan
        plan_id = temp_db.create_plan('test-feature', {})
        test_orchestrator.plan_id = plan_id
        
        # Mock _execute_phase_logic to raise error
        def raise_error(*args, **kwargs):
            raise RuntimeError("Test error")
        
        test_orchestrator._execute_phase_logic = raise_error
        
        phase_config = {'name': 'Failing Phase'}
        
        with pytest.raises(RuntimeError):
            test_orchestrator.execute_phase(0, phase_config)


class TestArtifactManagement:
    """Test artifact creation and registry."""
    
    def test_create_artifact(self, test_orchestrator, temp_db):
        """Test artifact creation."""
        # Create plan
        plan_id = temp_db.create_plan('test-feature', {})
        test_orchestrator.plan_id = plan_id
        
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "test_artifact.txt"
            
            artifact_id = test_orchestrator.create_artifact(
                path=str(artifact_path),
                content="Test content",
                artifact_type="test",
                phase_id=None
            )
            
            assert artifact_id is not None
            assert artifact_path.exists()
            assert artifact_path.read_text() == "Test content"
            assert len(test_orchestrator.artifacts) == 1
    
    def test_artifact_metadata(self, test_orchestrator, temp_db):
        """Test artifact metadata tracking."""
        plan_id = temp_db.create_plan('test-feature', {})
        test_orchestrator.plan_id = plan_id
        
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "metadata_test.txt"
            content = "Test content for metadata"
            
            test_orchestrator.create_artifact(
                path=str(artifact_path),
                content=content,
                artifact_type="test"
            )
            
            artifact = test_orchestrator.artifacts[0]
            assert artifact.type == "test"
            assert artifact.size_bytes == len(content.encode('utf-8'))
            assert artifact.checksum is not None


class TestProgressTracking:
    """Test progress tracking."""
    
    def test_get_progress_status(self, test_orchestrator, temp_db):
        """Test progress status retrieval."""
        plan_id = temp_db.create_plan('test-feature', {})
        test_orchestrator.plan_id = plan_id
        
        status = test_orchestrator.get_progress_status()
        
        assert status['plan_id'] == plan_id
        assert status['orchestrator'] == 'test_orchestrator'
        assert 'progress_percent' in status
        assert 'completed_phases' in status
    
    def test_generate_progress_bar(self, test_orchestrator):
        """Test progress bar generation."""
        bar = test_orchestrator.generate_progress_bar(5, 10, width=10)
        
        assert len(bar) == 10
        assert bar.count('█') == 5
        assert bar.count('░') == 5
    
    def test_generate_progress_bar_empty(self, test_orchestrator):
        """Test progress bar with zero progress."""
        bar = test_orchestrator.generate_progress_bar(0, 10, width=10)
        
        assert bar == '░' * 10
    
    def test_generate_progress_bar_full(self, test_orchestrator):
        """Test progress bar with 100% progress."""
        bar = test_orchestrator.generate_progress_bar(10, 10, width=10)
        
        assert bar == '█' * 10


class TestCheckpointRollback:
    """Test checkpoint and rollback functionality."""
    
    def test_create_checkpoint(self, test_orchestrator, temp_db):
        """Test checkpoint creation."""
        plan_id = temp_db.create_plan('test-feature', {})
        phase_id = temp_db.start_phase(plan_id, 0, {'name': 'Phase 0'})
        test_orchestrator.plan_id = plan_id
        
        snapshot_id = test_orchestrator.create_checkpoint(
            phase_id,
            metadata={'test': 'data'}
        )
        
        assert snapshot_id is not None
    
    def test_rollback_to_checkpoint(self, test_orchestrator, temp_db):
        """Test rollback to checkpoint."""
        plan_id = temp_db.create_plan('test-feature', {})
        phase_id = temp_db.start_phase(plan_id, 0, {'name': 'Phase 0'})
        test_orchestrator.plan_id = plan_id
        
        # Create artifact and checkpoint
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "test.txt"
            test_orchestrator.create_artifact(
                str(artifact_path),
                "content",
                "test"
            )
            
            snapshot_id = test_orchestrator.create_checkpoint(phase_id)
            
            # Clear artifacts
            test_orchestrator.artifacts.clear()
            assert len(test_orchestrator.artifacts) == 0
            
            # Rollback
            success = test_orchestrator.rollback_to_checkpoint(snapshot_id)
            
            assert success
            # Note: Artifacts restored as metadata, not actual files


class TestTemplateRendering:
    """Test template rendering."""
    
    def test_render_template_not_found(self, test_orchestrator):
        """Test rendering non-existent template."""
        from jinja2 import TemplateNotFound
        
        with pytest.raises(TemplateNotFound):
            test_orchestrator.render_template(
                'nonexistent.jinja2',
                {'data': 'value'}
            )


class TestContinuationPrompt:
    """Test continuation prompt generation."""
    
    @patch('src.orchestrators.base.base_orchestrator_v4_1.Path')
    def test_update_continuation_prompt(self, mock_path, test_orchestrator, temp_db):
        """Test continuation prompt update."""
        plan_id = temp_db.create_plan('test-feature', {})
        phase_id = temp_db.start_phase(plan_id, 0, {'name': 'Phase 0'})
        test_orchestrator.plan_id = plan_id
        
        # Mock file operations
        mock_file = MagicMock()
        mock_path.return_value.parent.mkdir.return_value = None
        mock_path.return_value.write_text.return_value = None
        
        # Should not raise exception even if template missing
        test_orchestrator.update_continuation_prompt(phase_id)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
