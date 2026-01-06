"""
Test Suite for Vacuum Orchestrator v3 Core Framework

Tests the core infrastructure:
- Configuration loading from vacuum-v3-manifest.yaml
- Logging infrastructure
- Error handling with rollback capability
- Base orchestrator class
- Command invocation
"""

import pytest
import os
import yaml
import logging
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import the module (will fail initially - RED phase)
try:
    from src.orchestrators.vacuum.vacuum_orchestrator_v3 import (
        VacuumOrchestratorV3,
        VacuumConfig,
        VacuumOperation
    )
except ImportError:
    pytest.skip("VacuumOrchestratorV3 not yet implemented", allow_module_level=True)


class TestVacuumConfig:
    """Test configuration loading and validation."""
    
    def test_config_loads_from_yaml(self, tmp_path):
        """Test that configuration loads from YAML manifest."""
        # Arrange
        manifest_path = tmp_path / "vacuum-v3-manifest.yaml"
        config_data = {
            "orchestrator": {
                "name": "Vacuum v3",
                "version": "3.0.0",
                "enabled": True
            },
            "operations": {
                "backup_enabled": True,
                "dry_run_default": False,
                "max_parallel_tasks": 4
            },
            "paths": {
                "backup_dir": "cortex-brain/backups/",
                "compliance_db": "cortex-brain/tier0/vacuum-compliance.db"
            }
        }
        
        with open(manifest_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Act
        config = VacuumConfig.from_yaml(manifest_path)
        
        # Assert
        assert config.name == "Vacuum v3"
        assert config.version == "3.0.0"
        assert config.enabled is True
        assert config.backup_enabled is True
        assert config.max_parallel_tasks == 4
    
    def test_config_validates_required_fields(self):
        """Test that configuration validation catches missing required fields."""
        # Arrange
        invalid_config = {}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Missing required field"):
            VacuumConfig.from_dict(invalid_config)
    
    def test_config_uses_defaults_for_optional_fields(self):
        """Test that optional fields use sensible defaults."""
        # Arrange
        minimal_config = {
            "orchestrator": {
                "name": "Vacuum v3",
                "version": "3.0.0"
            }
        }
        
        # Act
        config = VacuumConfig.from_dict(minimal_config)
        
        # Assert
        assert config.enabled is True  # Default
        assert config.backup_enabled is True  # Default
        assert config.dry_run_default is False  # Default
        assert config.max_parallel_tasks == 4  # Default


class TestVacuumOrchestratorV3Initialization:
    """Test orchestrator initialization and setup."""
    
    def test_orchestrator_initializes_with_valid_config(self, tmp_path):
        """Test that orchestrator initializes with valid configuration."""
        # Arrange
        manifest_path = tmp_path / "vacuum-v3-manifest.yaml"
        self._create_valid_manifest(manifest_path)
        
        # Act
        orchestrator = VacuumOrchestratorV3(manifest_path=manifest_path)
        
        # Assert
        assert orchestrator is not None
        assert orchestrator.config.name == "Vacuum v3"
        assert orchestrator.is_initialized is True
    
    def test_orchestrator_sets_up_logging(self, tmp_path):
        """Test that orchestrator sets up logging infrastructure."""
        # Arrange
        manifest_path = tmp_path / "vacuum-v3-manifest.yaml"
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        self._create_valid_manifest(manifest_path)
        
        # Act
        orchestrator = VacuumOrchestratorV3(
            manifest_path=manifest_path,
            log_dir=log_dir
        )
        
        # Assert
        assert orchestrator.logger is not None
        assert orchestrator.logger.level == logging.INFO
        
        # Check log file was created
        log_files = list(log_dir.glob("vacuum-v3-*.log"))
        assert len(log_files) > 0
    
    def test_orchestrator_fails_with_invalid_config(self):
        """Test that orchestrator raises error with invalid configuration."""
        # Arrange
        invalid_manifest = Path("/nonexistent/manifest.yaml")
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            VacuumOrchestratorV3(manifest_path=invalid_manifest)
    
    @staticmethod
    def _create_valid_manifest(path: Path):
        """Helper to create a valid manifest file."""
        config = {
            "orchestrator": {
                "name": "Vacuum v3",
                "version": "3.0.0",
                "enabled": True
            },
            "operations": {
                "backup_enabled": True,
                "dry_run_default": False,
                "max_parallel_tasks": 4
            }
        }
        with open(path, 'w') as f:
            yaml.dump(config, f)


class TestVacuumOrchestratorV3ErrorHandling:
    """Test error handling and rollback capability."""
    
    def test_orchestrator_creates_backup_before_operation(self, tmp_path):
        """Test that backup is created before any destructive operation."""
        # Arrange
        manifest_path = tmp_path / "vacuum-v3-manifest.yaml"
        self._create_valid_manifest(manifest_path)
        orchestrator = VacuumOrchestratorV3(manifest_path=manifest_path)
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("original content")
        
        # Act
        with orchestrator.operation_context("delete_file"):
            backup_created = orchestrator.has_backup_for_current_operation()
        
        # Assert
        assert backup_created is True
    
    def test_orchestrator_rolls_back_on_error(self, tmp_path):
        """Test that orchestrator rolls back changes on error."""
        # Arrange
        manifest_path = tmp_path / "vacuum-v3-manifest.yaml"
        self._create_valid_manifest(manifest_path)
        orchestrator = VacuumOrchestratorV3(manifest_path=manifest_path, workspace_root=tmp_path)
        
        test_file = tmp_path / "test.txt"
        original_content = "original content"
        test_file.write_text(original_content)
        
        # Act
        try:
            with orchestrator.operation_context("modify_file"):
                # Backup file before modification
                orchestrator.backup_file(test_file)
                # Modify
                test_file.write_text("modified content")
                # Trigger error
                raise Exception("Simulated error")
        except Exception:
            pass
        
        # Assert - file should be restored to original
        assert test_file.read_text() == original_content
    
    def test_orchestrator_logs_errors_with_context(self, tmp_path, caplog):
        """Test that errors are logged with full context."""
        # Arrange
        manifest_path = tmp_path / "vacuum-v3-manifest.yaml"
        self._create_valid_manifest(manifest_path)
        orchestrator = VacuumOrchestratorV3(manifest_path=manifest_path, workspace_root=tmp_path)
        
        # Act
        with caplog.at_level(logging.ERROR):
            try:
                with orchestrator.operation_context("test_operation"):
                    raise ValueError("Test error")
            except ValueError:
                pass
        
        # Assert - Check that error was logged
        assert "test_operation" in caplog.text
        assert "Test error" in caplog.text
    
    @staticmethod
    def _create_valid_manifest(path: Path):
        """Helper to create a valid manifest file."""
        config = {
            "orchestrator": {
                "name": "Vacuum v3",
                "version": "3.0.0",
                "enabled": True
            },
            "operations": {
                "backup_enabled": True,
                "dry_run_default": False,
                "max_parallel_tasks": 4
            }
        }
        with open(path, 'w') as f:
            yaml.dump(config, f)


class TestVacuumOrchestratorV3Invocation:
    """Test orchestrator invocation via CLI."""
    
    @pytest.mark.skip(reason="CLI integration pending - will implement with src.main.py routing")
    @patch('src.orchestrators.vacuum.vacuum_orchestrator_v3.VacuumOrchestratorV3')
    def test_vacuum_command_invokes_orchestrator(self, mock_orchestrator):
        """Test that 'python3 -m src.main vacuum' invokes orchestrator."""
        # Arrange
        mock_instance = MagicMock()
        mock_orchestrator.return_value = mock_instance
        
        # Act
        # This will be implemented in src.main.py routing
        from src.main import route_command
        result = route_command("vacuum")
        
        # Assert
        mock_orchestrator.assert_called_once()
        mock_instance.execute.assert_called_once()
        assert result.status == "success"
    
    @pytest.mark.skip(reason="CLI integration pending - will implement with src.main.py routing")
    @patch('src.orchestrators.vacuum.vacuum_orchestrator_v3.VacuumOrchestratorV3')
    def test_vacuum_command_accepts_dry_run_flag(self, mock_orchestrator):
        """Test that vacuum command accepts --dry-run flag."""
        # Arrange
        mock_instance = MagicMock()
        mock_orchestrator.return_value = mock_instance
        
        # Act
        from src.main import route_command
        result = route_command("vacuum --dry-run")
        
        # Assert
        assert mock_instance.dry_run is True


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace for testing."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    
    # Create sample structure
    (workspace / "cortex-brain").mkdir()
    (workspace / "cortex-brain" / "backups").mkdir()
    (workspace / "logs").mkdir()
    
    return workspace


# Fixtures
@pytest.fixture
def valid_manifest(tmp_path):
    """Provide a valid manifest file for testing."""
    manifest_path = tmp_path / "vacuum-v3-manifest.yaml"
    config = {
        "orchestrator": {
            "name": "Vacuum v3",
            "version": "3.0.0",
            "enabled": True
        },
        "operations": {
            "backup_enabled": True,
            "dry_run_default": False,
            "max_parallel_tasks": 4
        },
        "paths": {
            "backup_dir": "cortex-brain/backups/",
            "compliance_db": "cortex-brain/tier0/vacuum-compliance.db"
        }
    }
    
    with open(manifest_path, 'w') as f:
        yaml.dump(config, f)
    
    return manifest_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
