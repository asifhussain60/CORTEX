"""
CORTEX 4.0 Configuration Management

Provides centralized configuration loading, validation, and access with:
- Multi-source configuration (file, environment variables, defaults)
- Schema validation
- IDE detection and context-aware settings
- Path resolution (absolute, relative, environment-specific)
- Configuration hot-reloading support

Design Principles:
1. Single source of truth for all CORTEX settings
2. Environment-specific overrides (dev/test/prod)
3. IDE-aware configuration (VSCode vs Visual Studio)
4. Graceful degradation with sensible defaults
5. Validation at load time
"""

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class IDEType(Enum):
    """Supported IDE types."""
    VSCODE = "vscode"
    VISUAL_STUDIO = "visualstudio"
    UNKNOWN = "unknown"


class Environment(Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class PathConfig:
    """Path configuration with resolution."""
    orchestrators: Path
    brain: Path
    templates: Path
    mcp_gateway: Path
    logs: Path
    cache: Path
    
    def resolve_all(self, root: Path) -> None:
        """Resolve all paths relative to root if they're not absolute."""
        for key in self.__dataclass_fields__.keys():
            path_value = getattr(self, key)
            if not path_value.is_absolute():
                setattr(self, key, root / path_value)


@dataclass
class BrainConfig:
    """Brain tier configuration."""
    tier1_db: str  # Path template, e.g., "{repo}/cortex-brain/tier1/conversations.db"
    tier2_db: str  # Path template, e.g., "~/.cortex/shared/tier2/knowledge-graph.db"
    tier3_db: str  # Path template, e.g., "{repo}/cortex-brain/tier3/metrics.db"
    tier0_rules: str  # Path template, e.g., "~/.cortex/shared/skull_rules.yaml"
    max_conversations: int = 70
    pattern_confidence_threshold: float = 0.5
    enable_cross_repo_learning: bool = True
    
    def resolve_path(self, template: str, repo_path: Path) -> Path:
        """Resolve path template with variables."""
        resolved = template.replace("{repo}", str(repo_path))
        resolved = resolved.replace("~", str(Path.home()))
        return Path(resolved)


@dataclass
class IDEConfig:
    """IDE-specific configuration."""
    detected_ide: IDEType = IDEType.UNKNOWN
    vscode_config_path: Optional[Path] = None
    visual_studio_config_path: Optional[Path] = None
    auto_detect: bool = True
    
    def get_config_path(self) -> Optional[Path]:
        """Get configuration path for detected IDE."""
        if self.detected_ide == IDEType.VSCODE:
            return self.vscode_config_path
        elif self.detected_ide == IDEType.VISUAL_STUDIO:
            return self.visual_studio_config_path
        return None


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file_path: Optional[Path] = None
    console_output: bool = True
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_file_size_mb: int = 10
    backup_count: int = 5


@dataclass
class CortexConfig:
    """Complete CORTEX 4.0 configuration."""
    version: str = "4.0"
    environment: Environment = Environment.DEVELOPMENT
    paths: PathConfig = field(default_factory=lambda: PathConfig(
        orchestrators=Path("src/orchestrators"),
        brain=Path("src/brain"),
        templates=Path("src/templates"),
        mcp_gateway=Path("src/mcp"),
        logs=Path("logs"),
        cache=Path(".cortex/cache")
    ))
    brain: BrainConfig = field(default_factory=lambda: BrainConfig(
        tier1_db="{repo}/cortex-brain/tier1/conversations.db",
        tier2_db="~/.cortex/shared/tier2/knowledge-graph.db",
        tier3_db="{repo}/cortex-brain/tier3/metrics.db",
        tier0_rules="~/.cortex/shared/skull_rules.yaml"
    ))
    ide: IDEConfig = field(default_factory=IDEConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    features: Dict[str, bool] = field(default_factory=lambda: {
        "mcp_gateway_enabled": False,  # Stub only in Phase 1
        "response_templates_v4": False,  # Not yet implemented
        "dependency_injection": False,  # Not yet implemented
        "documentation_engine": False  # Phase 1.5
    })
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate version
        if not self.version.startswith("4."):
            errors.append(f"Invalid version: {self.version}. Expected 4.x")
        
        # Validate paths exist (for production)
        if self.environment == Environment.PRODUCTION:
            required_paths = [
                self.paths.orchestrators,
                self.paths.brain,
                self.paths.templates
            ]
            for path in required_paths:
                if not path.exists():
                    errors.append(f"Required path does not exist: {path}")
        
        # Validate brain config
        if self.brain.max_conversations < 1:
            errors.append("Brain max_conversations must be >= 1")
        
        if not (0.0 <= self.brain.pattern_confidence_threshold <= 1.0):
            errors.append("Brain pattern_confidence_threshold must be between 0.0 and 1.0")
        
        # Validate logging config
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging.level not in valid_levels:
            errors.append(f"Invalid logging level: {self.logging.level}. Must be one of {valid_levels}")
        
        return errors
    
    @property
    def brain_path(self) -> Path:
        """
        Backward compatibility property for legacy code.
        Returns: Path to cortex-brain directory
        """
        # Assume workspace structure: {repo}/cortex-brain
        return Path.cwd() / "cortex-brain"
    
    def ensure_paths_exist(self) -> None:
        """
        Create essential CORTEX directories if they don't exist.
        Backward compatibility method for legacy code.
        
        Creates:
        - cortex-brain/tier1
        - cortex-brain/tier2
        - cortex-brain/tier3
        - cortex-brain/tier0
        - logs/
        - cache/
        """
        dirs_to_create = [
            self.brain_path / "tier0",
            self.brain_path / "tier1",
            self.brain_path / "tier2",
            self.brain_path / "tier3",
            self.brain_path / "corpus-callosum",
            Path("logs"),
            Path(".cortex/cache"),
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """
    Manages CORTEX configuration with support for:
    - File-based configuration (cortex.config.json)
    - Environment variable overrides
    - IDE-specific configurations
    - Default fallbacks
    - Configuration validation
    """
    
    def __init__(self, config_path: Union[str, Path] = "cortex.config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to main configuration file
        """
        self.config_path = Path(config_path)
        self.root_path = self._find_project_root()
        self.config = self._load_configuration()
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        errors = self.config.validate()
        if errors:
            error_msg = "Configuration validation failed:\\n" + "\\n".join(f"  - {e}" for e in errors)
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Resolve paths
        self.config.paths.resolve_all(self.root_path)
        
        # Detect IDE if auto-detection enabled
        if self.config.ide.auto_detect:
            self.config.ide.detected_ide = self._detect_ide()
    
    def _find_project_root(self) -> Path:
        """Find project root directory (contains cortex.config.json or .git)."""
        current = Path.cwd()
        
        # Try to find cortex.config.json
        while current != current.parent:
            if (current / "cortex.config.json").exists():
                return current
            if (current / ".git").exists():
                return current
            current = current.parent
        
        # Fallback to current directory
        return Path.cwd()
    
    def _load_configuration(self) -> CortexConfig:
        """Load configuration from file with environment overrides."""
        # Start with defaults
        config_dict = {}
        
        # Load from file if exists
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse {self.config_path}: {e}. Using defaults.")
        else:
            logging.warning(f"Configuration file {self.config_path} not found. Using defaults.")
        
        # Apply environment variable overrides
        config_dict = self._apply_env_overrides(config_dict)
        
        # Build config object
        return self._dict_to_config(config_dict)
    
    def _apply_env_overrides(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        # CORTEX_ENV - override environment
        if "CORTEX_ENV" in os.environ:
            env_value = os.environ["CORTEX_ENV"].lower()
            if env_value in ["development", "testing", "production"]:
                config_dict["environment"] = env_value
        
        # CORTEX_LOG_LEVEL - override logging level
        if "CORTEX_LOG_LEVEL" in os.environ:
            if "logging" not in config_dict:
                config_dict["logging"] = {}
            config_dict["logging"]["level"] = os.environ["CORTEX_LOG_LEVEL"]
        
        # CORTEX_IDE - override IDE detection
        if "CORTEX_IDE" in os.environ:
            if "ide" not in config_dict:
                config_dict["ide"] = {}
            config_dict["ide"]["detected_ide"] = os.environ["CORTEX_IDE"].lower()
        
        return config_dict
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> CortexConfig:
        """Convert dictionary to CortexConfig object."""
        # Extract sections
        version = config_dict.get("version", "4.0")
        environment = Environment(config_dict.get("environment", "development"))
        
        # Paths
        paths_dict = config_dict.get("paths", {})
        paths = PathConfig(
            orchestrators=Path(paths_dict.get("orchestrators", "src/orchestrators")),
            brain=Path(paths_dict.get("brain", "src/brain")),
            templates=Path(paths_dict.get("templates", "src/templates")),
            mcp_gateway=Path(paths_dict.get("mcp_gateway", "src/mcp")),
            logs=Path(paths_dict.get("logs", "logs")),
            cache=Path(paths_dict.get("cache", ".cortex/cache"))
        )
        
        # Brain
        brain_dict = config_dict.get("brain", {})
        brain = BrainConfig(
            tier1_db=brain_dict.get("tier1_db", "{repo}/cortex-brain/tier1/conversations.db"),
            tier2_db=brain_dict.get("tier2_db", "~/.cortex/shared/tier2/knowledge-graph.db"),
            tier3_db=brain_dict.get("tier3_db", "{repo}/cortex-brain/tier3/metrics.db"),
            tier0_rules=brain_dict.get("tier0_rules", "~/.cortex/shared/skull_rules.yaml"),
            max_conversations=brain_dict.get("max_conversations", 70),
            pattern_confidence_threshold=brain_dict.get("pattern_confidence_threshold", 0.5),
            enable_cross_repo_learning=brain_dict.get("enable_cross_repo_learning", True)
        )
        
        # IDE
        ide_dict = config_dict.get("ide", {})
        ide = IDEConfig(
            detected_ide=IDEType(ide_dict.get("detected_ide", "unknown")),
            vscode_config_path=Path(ide_dict["vscode_config_path"]) if "vscode_config_path" in ide_dict else None,
            visual_studio_config_path=Path(ide_dict["visual_studio_config_path"]) if "visual_studio_config_path" in ide_dict else None,
            auto_detect=ide_dict.get("auto_detect", True)
        )
        
        # Logging
        logging_dict = config_dict.get("logging", {})
        logging_config = LoggingConfig(
            level=logging_dict.get("level", "INFO"),
            file_path=Path(logging_dict["file_path"]) if "file_path" in logging_dict else None,
            console_output=logging_dict.get("console_output", True),
            format=logging_dict.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            max_file_size_mb=logging_dict.get("max_file_size_mb", 10),
            backup_count=logging_dict.get("backup_count", 5)
        )
        
        # Features
        features = config_dict.get("features", {})
        
        return CortexConfig(
            version=version,
            environment=environment,
            paths=paths,
            brain=brain,
            ide=ide,
            logging=logging_config,
            features=features
        )
    
    def _detect_ide(self) -> IDEType:
        """Detect active IDE from environment and file system."""
        # Check environment variables
        if "VSCODE_INJECTION" in os.environ or "VSCODE_PID" in os.environ:
            return IDEType.VSCODE
        
        # Check for IDE-specific directories
        if (self.root_path / ".vscode").exists():
            return IDEType.VSCODE
        
        if (self.root_path / ".vs").exists():
            return IDEType.VISUAL_STUDIO
        
        return IDEType.UNKNOWN
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Examples:
            config.get("paths.orchestrators")
            config.get("brain.max_conversations")
            config.get("features.mcp_gateway_enabled")
        
        Args:
            key: Dot-notation configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        parts = key.split(".")
        value = self.config
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def get_path(self, path_key: str) -> Path:
        """
        Get resolved path by key.
        
        Args:
            path_key: Path key (orchestrators, brain, templates, etc.)
        
        Returns:
            Resolved absolute path
        """
        return getattr(self.config.paths, path_key)
    
    def get_brain_path(self, tier: str) -> Path:
        """
        Get resolved brain tier path.
        
        Args:
            tier: Tier name (tier1, tier2, tier3, tier0)
        
        Returns:
            Resolved absolute path for brain tier database
        """
        template_key = f"{tier}_db" if tier != "tier0" else "tier0_rules"
        template = getattr(self.config.brain, template_key)
        return self.config.brain.resolve_path(template, self.root_path)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if feature is enabled.
        
        Args:
            feature: Feature name
        
        Returns:
            True if feature enabled, False otherwise
        """
        return self.config.features.get(feature, False)
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self.config = self._load_configuration()
        self.config.paths.resolve_all(self.root_path)


# Singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get singleton ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> CortexConfig:
    """Get current configuration."""
    return get_config_manager().config
