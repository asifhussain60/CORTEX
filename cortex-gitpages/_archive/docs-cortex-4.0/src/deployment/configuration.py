"""
Configuration Management System

Manages environment-specific configurations for dev/staging/prod environments.
Supports .env file loading and configuration inheritance.
"""
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
    """Environment-specific configuration.
    
    Args:
        environment: Target environment (dev/staging/prod)
        debug: Enable debug mode
        log_level: Logging level (debug/info/warning/error)
        database_url: Database connection URL
        api_key: Optional API key for external services
        timeout_seconds: Request timeout in seconds
        max_retries: Maximum number of retries for failed operations
        parent: Optional parent config for inheritance
    """
    environment: EnvironmentType
    debug: bool
    log_level: str
    database_url: str
    api_key: Optional[str] = None
    timeout_seconds: int = 30
    max_retries: int = 3
    parent: Optional['EnvironmentConfig'] = None
    
    def get_inherited_value(self, key: str) -> Any:
        """Get value with inheritance from parent.
        
        Attempts to get value from this config, then falls back to parent
        if available and current value is None.
        
        Args:
            key: Configuration key to retrieve
            
        Returns:
            Configuration value or None if not found
        """
        if hasattr(self, key) and getattr(self, key) is not None:
            return getattr(self, key)
        if self.parent:
            return self.parent.get_inherited_value(key)
        return None


class ConfigurationManager:
    """Manages environment-specific configurations.
    
    Handles registration, retrieval, and management of environment configs
    with support for .env file loading and environment switching.
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self.configs: Dict[EnvironmentType, EnvironmentConfig] = {}
        self.current_environment: Optional[EnvironmentType] = None
    
    def register_config(self, config: EnvironmentConfig) -> None:
        """Register environment configuration.
        
        Args:
            config: Environment configuration to register
        """
        self.configs[config.environment] = config
    
    def load_from_env_file(self, env_file_path: str) -> EnvironmentConfig:
        """Load configuration from .env file.
        
        Reads a .env file and creates an EnvironmentConfig from the values.
        Supports comments (#) and default values for missing keys.
        
        Args:
            env_file_path: Path to .env file
            
        Returns:
            Loaded environment configuration
            
        Raises:
            FileNotFoundError: If .env file not found
            IOError: If error reading .env file
        """
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
        """Get configuration for specific environment.
        
        Args:
            environment: Target environment
            
        Returns:
            Environment configuration or None if not registered
        """
        return self.configs.get(environment)
    
    def set_current_environment(self, environment: EnvironmentType) -> None:
        """Set current active environment.
        
        Args:
            environment: Environment to activate
        """
        self.current_environment = environment
    
    def get_current_config(self) -> Optional[EnvironmentConfig]:
        """Get current environment configuration.
        
        Returns:
            Current environment configuration or None if not set
        """
        if self.current_environment:
            return self.configs.get(self.current_environment)
        return None
    
    def validate_config(self, config: EnvironmentConfig) -> bool:
        """Validate configuration completeness.
        
        Checks that all required fields are present and not None.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if config is valid, False otherwise
        """
        required_fields = ['environment', 'debug', 'log_level', 'database_url']
        for field in required_fields:
            if getattr(config, field) is None:
                return False
        return True
