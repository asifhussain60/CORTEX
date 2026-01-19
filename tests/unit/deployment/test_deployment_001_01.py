"""
Tests for AC-DEPLOY-001-01: Environment-Specific Configuration Management

Tests environment config for dev/staging/prod, .env file support, and configuration inheritance.
"""
import pytest
from dataclasses import dataclass
from typing import Dict, Optional, Any
from enum import Enum


class EnvironmentType(Enum):
    """Environment type enumeration."""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration."""
    environment: EnvironmentType
    debug: bool
    log_level: str
    database_url: str
    api_key: Optional[str] = None
    timeout_seconds: int = 30
    max_retries: int = 3
    parent: Optional['EnvironmentConfig'] = None
    
    def get_inherited_value(self, key: str) -> Any:
        """Get value with inheritance from parent."""
        if hasattr(self, key) and getattr(self, key) is not None:
            return getattr(self, key)
        if self.parent:
            return self.parent.get_inherited_value(key)
        return None


class ConfigurationManager:
    """Manages environment-specific configurations."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.configs: Dict[EnvironmentType, EnvironmentConfig] = {}
        self.current_environment: Optional[EnvironmentType] = None
    
    def register_config(self, config: EnvironmentConfig) -> None:
        """Register environment configuration."""
        self.configs[config.environment] = config
    
    def load_from_env_file(self, env_file_path: str) -> EnvironmentConfig:
        """Load configuration from .env file."""
        config_dict = {}
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config_dict[key] = value
        
        env_type = EnvironmentType(config_dict.get('ENVIRONMENT', 'dev'))
        config = EnvironmentConfig(
            environment=env_type,
            debug=config_dict.get('DEBUG', 'false').lower() == 'true',
            log_level=config_dict.get('LOG_LEVEL', 'info'),
            database_url=config_dict.get('DATABASE_URL', 'sqlite:///:memory:'),
            api_key=config_dict.get('API_KEY'),
            timeout_seconds=int(config_dict.get('TIMEOUT_SECONDS', '30')),
            max_retries=int(config_dict.get('MAX_RETRIES', '3'))
        )
        return config
    
    def get_config(self, environment: EnvironmentType) -> Optional[EnvironmentConfig]:
        """Get configuration for environment."""
        return self.configs.get(environment)
    
    def set_current_environment(self, environment: EnvironmentType) -> None:
        """Set current environment."""
        self.current_environment = environment
    
    def get_current_config(self) -> Optional[EnvironmentConfig]:
        """Get current environment configuration."""
        if self.current_environment:
            return self.configs.get(self.current_environment)
        return None
    
    def validate_config(self, config: EnvironmentConfig) -> bool:
        """Validate configuration completeness."""
        required_fields = ['environment', 'debug', 'log_level', 'database_url']
        for field in required_fields:
            if getattr(config, field) is None:
                return False
        return True


# Test Cases

class TestEnvironmentConfigStructure:
    """Test environment config structure and initialization."""
    
    def test_config_creation(self):
        """Test creating environment config."""
        config = EnvironmentConfig(
            environment=EnvironmentType.DEV,
            debug=True,
            log_level='debug',
            database_url='sqlite:///:memory:'
        )
        assert config.environment == EnvironmentType.DEV
        assert config.debug is True
        assert config.log_level == 'debug'
    
    def test_config_with_all_fields(self):
        """Test config with all optional fields."""
        config = EnvironmentConfig(
            environment=EnvironmentType.PROD,
            debug=False,
            log_level='error',
            database_url='postgresql://prod.db',
            api_key='secret123',
            timeout_seconds=60,
            max_retries=5
        )
        assert config.api_key == 'secret123'
        assert config.timeout_seconds == 60
        assert config.max_retries == 5
    
    def test_environment_types(self):
        """Test all environment types."""
        assert EnvironmentType.DEV.value == 'dev'
        assert EnvironmentType.STAGING.value == 'staging'
        assert EnvironmentType.PROD.value == 'prod'


class TestConfigurationManager:
    """Test configuration manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = ConfigurationManager()
        assert len(manager.configs) == 0
        assert manager.current_environment is None
    
    def test_register_config(self):
        """Test registering configuration."""
        manager = ConfigurationManager()
        config = EnvironmentConfig(
            environment=EnvironmentType.DEV,
            debug=True,
            log_level='debug',
            database_url='sqlite:///:memory:'
        )
        manager.register_config(config)
        assert len(manager.configs) == 1
        assert manager.configs[EnvironmentType.DEV] == config
    
    def test_get_config(self):
        """Test getting configuration."""
        manager = ConfigurationManager()
        config = EnvironmentConfig(
            environment=EnvironmentType.PROD,
            debug=False,
            log_level='error',
            database_url='postgresql://prod.db'
        )
        manager.register_config(config)
        retrieved = manager.get_config(EnvironmentType.PROD)
        assert retrieved == config
    
    def test_get_nonexistent_config(self):
        """Test getting non-existent configuration."""
        manager = ConfigurationManager()
        result = manager.get_config(EnvironmentType.STAGING)
        assert result is None


class TestConfigurationInheritance:
    """Test configuration inheritance."""
    
    def test_inherit_from_parent(self):
        """Test inheriting values from parent config."""
        parent = EnvironmentConfig(
            environment=EnvironmentType.DEV,
            debug=True,
            log_level='debug',
            database_url='sqlite:///:memory:',
            timeout_seconds=30
        )
        child = EnvironmentConfig(
            environment=EnvironmentType.STAGING,
            debug=True,
            log_level='info',
            database_url='sqlite:///staging.db',
            parent=parent
        )
        assert child.get_inherited_value('log_level') == 'info'
        assert child.get_inherited_value('timeout_seconds') == 30
    
    def test_multi_level_inheritance(self):
        """Test multi-level configuration inheritance."""
        grandparent = EnvironmentConfig(
            environment=EnvironmentType.DEV,
            debug=True,
            log_level='debug',
            database_url='sqlite:///:memory:',
            timeout_seconds=30
        )
        parent = EnvironmentConfig(
            environment=EnvironmentType.STAGING,
            debug=True,
            log_level='info',
            database_url='sqlite:///staging.db',
            parent=grandparent
        )
        child = EnvironmentConfig(
            environment=EnvironmentType.PROD,
            debug=False,
            log_level='error',
            database_url='postgresql://prod.db',
            parent=parent
        )
        assert child.get_inherited_value('timeout_seconds') == 30


class TestEnvFileLoading:
    """Test .env file loading."""
    
    def test_load_from_env_file(self, tmp_path):
        """Test loading configuration from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "ENVIRONMENT=prod\n"
            "DEBUG=false\n"
            "LOG_LEVEL=error\n"
            "DATABASE_URL=postgresql://prod.db\n"
            "API_KEY=prod-secret\n"
            "TIMEOUT_SECONDS=60\n"
        )
        manager = ConfigurationManager()
        config = manager.load_from_env_file(str(env_file))
        assert config.environment == EnvironmentType.PROD
        assert config.debug is False
        assert config.log_level == 'error'
        assert config.api_key == 'prod-secret'
        assert config.timeout_seconds == 60
    
    def test_load_env_file_with_comments(self, tmp_path):
        """Test loading .env file with comments."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "# Production configuration\n"
            "ENVIRONMENT=prod\n"
            "# Database settings\n"
            "DATABASE_URL=postgresql://prod.db\n"
        )
        manager = ConfigurationManager()
        config = manager.load_from_env_file(str(env_file))
        assert config.environment == EnvironmentType.PROD
        assert config.database_url == 'postgresql://prod.db'
    
    def test_load_env_file_defaults(self, tmp_path):
        """Test .env file uses defaults for missing values."""
        env_file = tmp_path / ".env"
        env_file.write_text("DATABASE_URL=sqlite:///:memory:\n")
        manager = ConfigurationManager()
        config = manager.load_from_env_file(str(env_file))
        assert config.environment == EnvironmentType.DEV
        assert config.debug is False
        assert config.log_level == 'info'


class TestConfigurationValidation:
    """Test configuration validation."""
    
    def test_validate_complete_config(self):
        """Test validating complete configuration."""
        manager = ConfigurationManager()
        config = EnvironmentConfig(
            environment=EnvironmentType.DEV,
            debug=True,
            log_level='debug',
            database_url='sqlite:///:memory:'
        )
        assert manager.validate_config(config) is True
    
    def test_validate_incomplete_config(self):
        """Test validating incomplete configuration."""
        manager = ConfigurationManager()
        config = EnvironmentConfig(
            environment=EnvironmentType.DEV,
            debug=True,
            log_level='debug',
            database_url=None  # Missing required field
        )
        assert manager.validate_config(config) is False
    
    def test_validate_after_registration(self):
        """Test validating before registration."""
        manager = ConfigurationManager()
        config = EnvironmentConfig(
            environment=EnvironmentType.PROD,
            debug=False,
            log_level='error',
            database_url='postgresql://prod.db'
        )
        assert manager.validate_config(config) is True
        manager.register_config(config)
        assert manager.get_config(EnvironmentType.PROD) is not None


class TestCurrentEnvironment:
    """Test current environment management."""
    
    def test_set_current_environment(self):
        """Test setting current environment."""
        manager = ConfigurationManager()
        manager.set_current_environment(EnvironmentType.PROD)
        assert manager.current_environment == EnvironmentType.PROD
    
    def test_get_current_config(self):
        """Test getting current environment config."""
        manager = ConfigurationManager()
        config = EnvironmentConfig(
            environment=EnvironmentType.STAGING,
            debug=True,
            log_level='info',
            database_url='sqlite:///staging.db'
        )
        manager.register_config(config)
        manager.set_current_environment(EnvironmentType.STAGING)
        current = manager.get_current_config()
        assert current == config
    
    def test_get_current_config_not_set(self):
        """Test getting current config when not set."""
        manager = ConfigurationManager()
        assert manager.get_current_config() is None
    
    def test_switch_environments(self):
        """Test switching between environments."""
        manager = ConfigurationManager()
        dev_config = EnvironmentConfig(
            environment=EnvironmentType.DEV,
            debug=True,
            log_level='debug',
            database_url='sqlite:///:memory:'
        )
        prod_config = EnvironmentConfig(
            environment=EnvironmentType.PROD,
            debug=False,
            log_level='error',
            database_url='postgresql://prod.db'
        )
        manager.register_config(dev_config)
        manager.register_config(prod_config)
        manager.set_current_environment(EnvironmentType.DEV)
        assert manager.get_current_config().debug is True
        manager.set_current_environment(EnvironmentType.PROD)
        assert manager.get_current_config().debug is False


class TestSecretManagement:
    """Test secret management in configs."""
    
    def test_api_key_in_config(self):
        """Test API key storage in config."""
        config = EnvironmentConfig(
            environment=EnvironmentType.PROD,
            debug=False,
            log_level='error',
            database_url='postgresql://prod.db',
            api_key='secret-prod-key'
        )
        assert config.api_key == 'secret-prod-key'
    
    def test_api_key_optional(self):
        """Test API key is optional."""
        config = EnvironmentConfig(
            environment=EnvironmentType.DEV,
            debug=True,
            log_level='debug',
            database_url='sqlite:///:memory:'
        )
        assert config.api_key is None
    
    def test_api_key_from_env_file(self, tmp_path):
        """Test loading API key from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "ENVIRONMENT=prod\n"
            "DEBUG=false\n"
            "LOG_LEVEL=error\n"
            "DATABASE_URL=postgresql://prod.db\n"
            "API_KEY=env-secret-key\n"
        )
        manager = ConfigurationManager()
        config = manager.load_from_env_file(str(env_file))
        assert config.api_key == 'env-secret-key'
