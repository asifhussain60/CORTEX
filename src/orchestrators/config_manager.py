"""
Extended Orchestrator Configuration

Adds Phase 5 configuration management features to OrchestratorConfig.
Supports environment-specific configs, file-based loading, feature flags.

Version: 2.0.0
Author: Asif Hussain
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorConfig:
    """
    Extended orchestrator configuration with environment support.
    
    Supports loading from YAML/JSON files, environment-specific overrides,
    and centralized feature flag management.
    """
    # Core paths
    cortex_root: Path
    project_root: Optional[Path] = None
    brain_path: Optional[Path] = None
    
    # Feature flags
    enable_tdd: bool = True
    enable_git_checkpoints: bool = True
    enable_cleanup: bool = True
    enable_code_executor: bool = True
    
    # TDD configuration
    tdd_auto_debug: bool = True
    tdd_performance_refactoring: bool = True
    tdd_test_timeout_seconds: int = 30
    tdd_max_retries: int = 3
    
    # Git configuration
    git_auto_checkpoint: bool = True
    git_rollback_enabled: bool = True
    git_commit_message_template: str = "CORTEX: {operation} - {description}"
    
    # Planning configuration
    planning_enforce_dor: bool = True
    planning_enforce_dod: bool = True
    planning_skip_validation_for_admins: bool = False
    planning_auto_tdd_inclusion: bool = True
    
    # Execution configuration
    execution_default_mode: str = "approval_gated"  # approval_gated, autonomous, dry_run
    execution_max_concurrent_tasks: int = 4
    execution_task_timeout_minutes: int = 30
    
    # Performance tuning
    enable_caching: bool = True
    cache_ttl_minutes: int = 30
    enable_parallel_execution: bool = True
    
    # Logging configuration
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file_path: Optional[Path] = None
    log_rotation_mb: int = 10
    
    # Validation configuration
    validation_strict_mode: bool = False
    validation_fail_on_warnings: bool = False
    
    # Environment
    environment: str = "development"  # development, staging, production
    
    # Custom extensions
    extensions: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization: set defaults."""
        # Ensure Path types
        if isinstance(self.cortex_root, str):
            self.cortex_root = Path(self.cortex_root)
        
        if self.project_root is None:
            self.project_root = self.cortex_root
        elif isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)
        
        if self.brain_path is None:
            self.brain_path = self.cortex_root / "cortex-brain"
        elif isinstance(self.brain_path, str):
            self.brain_path = Path(self.brain_path)
        
        if self.log_file_path is None:
            self.log_file_path = self.cortex_root / "logs" / "orchestrator.log"
        elif isinstance(self.log_file_path, str):
            self.log_file_path = Path(self.log_file_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        # Convert Path objects to strings
        for key, value in data.items():
            if isinstance(value, Path):
                data[key] = str(value)
        return data
    
    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, file_path: Path) -> None:
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save config (YAML or JSON based on extension)
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.suffix in [".yaml", ".yml"]:
            with open(file_path, "w") as f:
                f.write(self.to_yaml())
            logger.info(f"Configuration saved to {file_path}")
        elif file_path.suffix == ".json":
            with open(file_path, "w") as f:
                f.write(self.to_json())
            logger.info(f"Configuration saved to {file_path}")
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrchestratorConfig':
        """
        Deserialize from dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            OrchestratorConfig instance
        """
        # Convert string paths to Path objects
        if "cortex_root" in data and isinstance(data["cortex_root"], str):
            data["cortex_root"] = Path(data["cortex_root"])
        if "project_root" in data and isinstance(data["project_root"], str):
            data["project_root"] = Path(data["project_root"])
        if "brain_path" in data and isinstance(data["brain_path"], str):
            data["brain_path"] = Path(data["brain_path"])
        if "log_file_path" in data and isinstance(data["log_file_path"], str):
            data["log_file_path"] = Path(data["log_file_path"])
        
        return cls(**data)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'OrchestratorConfig':
        """
        Deserialize from YAML string.
        
        Args:
            yaml_str: YAML string
            
        Returns:
            OrchestratorConfig instance
        """
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'OrchestratorConfig':
        """
        Deserialize from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            OrchestratorConfig instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'OrchestratorConfig':
        """
        Load configuration from file.
        
        Args:
            file_path: Path to config file (YAML or JSON)
            
        Returns:
            OrchestratorConfig instance
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, "r") as f:
            content = f.read()
        
        if file_path.suffix in [".yaml", ".yml"]:
            return cls.from_yaml(content)
        elif file_path.suffix == ".json":
            return cls.from_json(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    @classmethod
    def load_for_environment(
        cls,
        cortex_root: Path,
        environment: str = "development"
    ) -> 'OrchestratorConfig':
        """
        Load environment-specific configuration.
        
        Looks for config files in this order:
        1. cortex-brain/config/orchestrator-config-{environment}.yaml
        2. cortex-brain/config/orchestrator-config.yaml
        3. Default configuration
        
        Args:
            cortex_root: CORTEX root path
            environment: Environment name (development, staging, production)
            
        Returns:
            OrchestratorConfig instance
        """
        cortex_root = Path(cortex_root)
        config_dir = cortex_root / "cortex-brain" / "config"
        
        # Try environment-specific config
        env_config_path = config_dir / f"orchestrator-config-{environment}.yaml"
        if env_config_path.exists():
            logger.info(f"Loading environment-specific config: {env_config_path}")
            config = cls.from_file(env_config_path)
            config.environment = environment
            return config
        
        # Try default config
        default_config_path = config_dir / "orchestrator-config.yaml"
        if default_config_path.exists():
            logger.info(f"Loading default config: {default_config_path}")
            config = cls.from_file(default_config_path)
            config.environment = environment
            return config
        
        # Use defaults
        logger.info(f"Using default configuration for environment: {environment}")
        config = cls(cortex_root=cortex_root, environment=environment)
        
        # Apply environment-specific defaults
        if environment == "production":
            config.tdd_auto_debug = False
            config.log_level = "WARNING"
            config.git_auto_checkpoint = False
            config.validation_strict_mode = True
        elif environment == "staging":
            config.log_level = "INFO"
            config.validation_strict_mode = True
        
        return config
    
    def merge_overrides(self, overrides: Dict[str, Any]) -> None:
        """
        Merge configuration overrides.
        
        Args:
            overrides: Dictionary of configuration overrides
        """
        for key, value in overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.debug(f"Configuration override: {key} = {value}")
            else:
                logger.warning(f"Unknown configuration key: {key}")


# ============================================================================
# Configuration Templates
# ============================================================================

def create_development_config(cortex_root: Path) -> OrchestratorConfig:
    """Create development configuration template."""
    return OrchestratorConfig(
        cortex_root=cortex_root,
        environment="development",
        enable_tdd=True,
        enable_git_checkpoints=True,
        tdd_auto_debug=True,
        log_level="DEBUG",
        validation_strict_mode=False
    )


def create_production_config(cortex_root: Path) -> OrchestratorConfig:
    """Create production configuration template."""
    return OrchestratorConfig(
        cortex_root=cortex_root,
        environment="production",
        enable_tdd=True,
        enable_git_checkpoints=False,  # Don't auto-checkpoint in CI/CD
        tdd_auto_debug=False,
        git_auto_checkpoint=False,  # Explicit: no auto-checkpoint in production
        log_level="WARNING",
        validation_strict_mode=True,
        validation_fail_on_warnings=False
    )


def create_ci_cd_config(cortex_root: Path) -> OrchestratorConfig:
    """Create CI/CD configuration template."""
    return OrchestratorConfig(
        cortex_root=cortex_root,
        environment="ci_cd",
        enable_tdd=True,
        enable_git_checkpoints=False,
        tdd_auto_debug=False,
        log_level="INFO",
        log_to_file=False,  # Log to stdout in CI/CD
        validation_strict_mode=True,
        validation_fail_on_warnings=True,
        execution_default_mode="autonomous"  # No approval gates in CI/CD
    )


# ============================================================================
# Export Public API
# ============================================================================

__all__ = [
    "OrchestratorConfig",
    "create_development_config",
    "create_production_config",
    "create_ci_cd_config",
]
