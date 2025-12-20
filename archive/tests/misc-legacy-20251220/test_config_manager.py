"""
Unit Tests for Configuration Manager

Tests Phase 5: Configuration Management.

Version: 1.0.0
Author: Asif Hussain
"""

import pytest
import tempfile
import yaml
import json
from pathlib import Path
from src.orchestrators.config_manager import (
    OrchestratorConfig,
    create_development_config,
    create_production_config,
    create_ci_cd_config
)


# ============================================================================
# OrchestratorConfig Tests
# ============================================================================

def test_orchestrator_config_creation():
    """Test basic config creation."""
    config = OrchestratorConfig(cortex_root=Path("/test/cortex"))
    
    assert config.cortex_root == Path("/test/cortex")
    assert config.brain_path == Path("/test/cortex/cortex-brain")
    assert config.enable_tdd is True


def test_orchestrator_config_custom_paths():
    """Test custom path configuration."""
    config = OrchestratorConfig(
        cortex_root=Path("/test/cortex"),
        project_root=Path("/test/project"),
        brain_path=Path("/custom/brain")
    )
    
    assert config.project_root == Path("/test/project")
    assert config.brain_path == Path("/custom/brain")


def test_orchestrator_config_feature_flags():
    """Test feature flag configuration."""
    config = OrchestratorConfig(
        cortex_root=Path("/test/cortex"),
        enable_tdd=False,
        enable_git_checkpoints=False
    )
    
    assert config.enable_tdd is False
    assert config.enable_git_checkpoints is False


# ============================================================================
# Serialization Tests
# ============================================================================

def test_config_to_dict():
    """Test config to_dict() serialization."""
    config = OrchestratorConfig(
        cortex_root=Path("/test/cortex"),
        enable_tdd=True,
        tdd_auto_debug=False
    )
    
    config_dict = config.to_dict()
    
    # On Windows, paths use backslashes
    assert Path(config_dict["cortex_root"]) == Path("/test/cortex")
    assert config_dict["enable_tdd"] is True
    assert config_dict["tdd_auto_debug"] is False


def test_config_to_yaml():
    """Test config to_yaml() serialization."""
    config = OrchestratorConfig(
        cortex_root=Path("/test/cortex"),
        environment="production"
    )
    
    yaml_str = config.to_yaml()
    
    assert "cortex_root" in yaml_str
    assert "production" in yaml_str


def test_config_to_json():
    """Test config to_json() serialization."""
    config = OrchestratorConfig(
        cortex_root=Path("/test/cortex"),
        log_level="DEBUG"
    )
    
    json_str = config.to_json()
    
    assert "cortex_root" in json_str
    assert "DEBUG" in json_str


# ============================================================================
# File Persistence Tests
# ============================================================================

def test_config_save_and_load_yaml():
    """Test saving and loading YAML config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test-config.yaml"
        
        # Create and save config
        config = OrchestratorConfig(
            cortex_root=Path("/test/cortex"),
            enable_tdd=False,
            log_level="WARNING"
        )
        config.save_to_file(config_path)
        
        # Load config
        loaded_config = OrchestratorConfig.from_file(config_path)
        
        assert loaded_config.cortex_root == Path("/test/cortex")
        assert loaded_config.enable_tdd is False
        assert loaded_config.log_level == "WARNING"


def test_config_save_and_load_json():
    """Test saving and loading JSON config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test-config.json"
        
        config = OrchestratorConfig(
            cortex_root=Path("/test/cortex"),
            tdd_test_timeout_seconds=60
        )
        config.save_to_file(config_path)
        
        loaded_config = OrchestratorConfig.from_file(config_path)
        
        assert loaded_config.tdd_test_timeout_seconds == 60


def test_config_from_dict():
    """Test creating config from dictionary."""
    config_dict = {
        "cortex_root": "/test/cortex",
        "enable_tdd": False,
        "log_level": "ERROR"
    }
    
    config = OrchestratorConfig.from_dict(config_dict)
    
    assert config.cortex_root == Path("/test/cortex")
    assert config.enable_tdd is False
    assert config.log_level == "ERROR"


# ============================================================================
# Environment-Specific Config Tests
# ============================================================================

def test_load_for_environment_default():
    """Test loading default environment config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cortex_root = Path(tmpdir)
        config_dir = cortex_root / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        # Create environment-specific config
        env_config = {
            "cortex_root": str(cortex_root),
            "enable_tdd": False,
            "log_level": "DEBUG"
        }
        
        config_path = config_dir / "orchestrator-config-staging.yaml"
        with open(config_path, "w") as f:
            yaml.dump(env_config, f)
        
        # Load for staging environment
        config = OrchestratorConfig.load_for_environment(
            cortex_root,
            environment="staging"
        )
        
        assert config.environment == "staging"
        assert config.enable_tdd is False
        assert config.log_level == "DEBUG"


def test_load_for_environment_production_defaults():
    """Test production environment defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cortex_root = Path(tmpdir)
        
        # Load production config (no file exists, use defaults)
        config = OrchestratorConfig.load_for_environment(
            cortex_root,
            environment="production"
        )
        
        assert config.environment == "production"
        assert config.tdd_auto_debug is False
        assert config.log_level == "WARNING"
        assert config.git_auto_checkpoint is False
        assert config.validation_strict_mode is True


def test_merge_overrides():
    """Test configuration override merging."""
    config = OrchestratorConfig(
        cortex_root=Path("/test/cortex"),
        enable_tdd=True,
        log_level="INFO"
    )
    
    overrides = {
        "enable_tdd": False,
        "log_level": "ERROR",
        "tdd_test_timeout_seconds": 120
    }
    
    config.merge_overrides(overrides)
    
    assert config.enable_tdd is False
    assert config.log_level == "ERROR"
    assert config.tdd_test_timeout_seconds == 120


# ============================================================================
# Template Config Tests
# ============================================================================

def test_create_development_config():
    """Test development config template."""
    config = create_development_config(Path("/test/cortex"))
    
    assert config.environment == "development"
    assert config.tdd_auto_debug is True
    assert config.log_level == "DEBUG"
    assert config.validation_strict_mode is False


def test_create_production_config():
    """Test production config template."""
    config = create_production_config(Path("/test/cortex"))
    
    assert config.environment == "production"
    assert config.tdd_auto_debug is False
    assert config.log_level == "WARNING"
    assert config.git_auto_checkpoint is False


def test_create_ci_cd_config():
    """Test CI/CD config template."""
    config = create_ci_cd_config(Path("/test/cortex"))
    
    assert config.environment == "ci_cd"
    assert config.enable_git_checkpoints is False
    assert config.log_to_file is False
    assert config.execution_default_mode == "autonomous"
    assert config.validation_fail_on_warnings is True


# ============================================================================
# Edge Cases Tests
# ============================================================================

def test_config_string_paths_converted():
    """Test string paths are converted to Path objects."""
    config = OrchestratorConfig(
        cortex_root="/test/cortex",  # String, not Path
        project_root="/test/project"
    )
    
    assert isinstance(config.cortex_root, Path)
    assert isinstance(config.project_root, Path)


def test_config_invalid_file_format():
    """Test loading invalid file format raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test-config.txt"
        config_path.write_text("invalid config")
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            OrchestratorConfig.from_file(config_path)


def test_config_missing_file():
    """Test loading missing file raises error."""
    with pytest.raises(FileNotFoundError):
        OrchestratorConfig.from_file(Path("/nonexistent/config.yaml"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
