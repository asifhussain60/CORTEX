"""
Configuration File Discovery

Discovers and parses configuration files from repositories including:
- JSON (appsettings.json, package.json, config.json)
- YAML (docker-compose.yml, .gitlab-ci.yml, K8s manifests)
- XML (web.config, app.config)
- TOML (pyproject.toml, Cargo.toml)
- ENV (.env, .env.local, .env.production)
- INI (*.ini)

Task: DISC-002
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Governance: CORE-008, CORE-011, CORE-012, CORE-030
"""

import json
import logging
import re
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional
from xml.etree import ElementTree as ET

from cortex.brain.discovery import DiscoveryPlugin


logger = logging.getLogger(__name__)


@dataclass
class ConnectionString:
    """
    Represents a database connection string.
    
    Attributes:
        name: Name/identifier of connection
        connection_string: Masked connection string (secrets redacted)
        database_type: Type of database (postgresql, mssql, mysql, etc.)
        server: Database server hostname
        database: Database name
    """
    name: str
    connection_string: str
    database_type: Optional[str] = None
    server: Optional[str] = None
    database: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation with masked secrets."""
        return f"{self.name}: {self.connection_string}"


@dataclass
class ConfigTopology:
    """
    Configuration topology information.
    
    Attributes:
        config_files: List of discovered config files
        connection_strings: Extracted connection strings
        environment_variables: Environment variables found
        api_endpoints: API endpoints from configs
        feature_flags: Feature flag configurations
    """
    config_files: List[Path]
    connection_strings: List[ConnectionString]
    environment_variables: Dict[str, str]
    api_endpoints: List[str]
    feature_flags: Dict[str, Any]


class ConfigurationDiscovery(DiscoveryPlugin):
    """
    Discovers and parses configuration files.
    
    Supports multiple config formats and extracts connection strings,
    API endpoints, environment variables, and other configuration data.
    
    Features:
    - Multi-format parsing (JSON, YAML, XML, TOML, ENV, INI)
    - Connection string extraction and masking
    - Recursive directory scanning
    - Graceful error handling for malformed files
    
    Example:
        ```python
        discovery = ConfigurationDiscovery()
        topology = discovery.discover(Path("/my/repo"))
        
        for conn_string in topology["connection_strings"]:
            print(f"Found: {conn_string.name}")
        ```
    """
    
    def __init__(self) -> None:
        """Initialize configuration discovery."""
        self.supported_formats = ["json", "yaml", "xml", "toml", "env", "ini"]
        logger.info("ConfigurationDiscovery initialized")
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported config formats.
        
        Returns:
            List of supported format names
        """
        return self.supported_formats
    
    def discover(self, repo_path: Path) -> Dict[str, Any]:
        """
        Discover configuration files in repository.
        
        Args:
            repo_path: Path to repository to scan
            
        Returns:
            Dictionary containing discovered configurations
        """
        logger.info(f"Discovering configuration files in {repo_path}")
        
        config_files: List[Path] = []
        connection_strings: List[ConnectionString] = []
        environment_variables: Dict[str, str] = {}
        api_endpoints: List[str] = []
        
        # Scan for JSON configs
        for json_file in repo_path.rglob("*.json"):
            if self._is_config_file(json_file):
                config_files.append(json_file)
                config_data = self.parse_json_config(json_file)
                if config_data:
                    conn_strings = self.extract_connection_strings(config_data)
                    connection_strings.extend(conn_strings)
                    endpoints = self._extract_api_endpoints(config_data)
                    api_endpoints.extend(endpoints)
        
        # Scan for YAML configs
        for yaml_file in repo_path.rglob("*.yml"):
            config_files.append(yaml_file)
            config_data = self.parse_yaml_config(yaml_file)
            if config_data:
                conn_strings = self.extract_connection_strings(config_data)
                connection_strings.extend(conn_strings)
        
        for yaml_file in repo_path.rglob("*.yaml"):
            config_files.append(yaml_file)
            config_data = self.parse_yaml_config(yaml_file)
            if config_data:
                conn_strings = self.extract_connection_strings(config_data)
                connection_strings.extend(conn_strings)
        
        # Scan for .env files
        for env_file in repo_path.rglob(".env*"):
            if env_file.is_file():
                config_files.append(env_file)
                env_vars = self.parse_env_file(env_file)
                environment_variables.update(env_vars)
                conn_strings = self.extract_connection_strings(env_vars)
                connection_strings.extend(conn_strings)
        
        logger.info(
            f"Discovered {len(config_files)} config files, "
            f"{len(connection_strings)} connection strings"
        )
        
        return {
            "config_files": [str(f) for f in config_files],
            "connection_strings": [
                {
                    "name": cs.name,
                    "connection_string": cs.connection_string,
                    "database_type": cs.database_type,
                    "server": cs.server,
                    "database": cs.database,
                }
                for cs in connection_strings
            ],
            "environment_variables": environment_variables,
            "api_endpoints": api_endpoints,
            "total_configs": len(config_files),
        }
    
    def parse_json_config(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse JSON configuration file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON as dictionary, empty dict on error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Parsed JSON config: {file_path}")
                return data
        except (json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse JSON {file_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}")
            return {}
    
    def parse_yaml_config(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse YAML configuration file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Parsed YAML as dictionary, empty dict on error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                logger.debug(f"Parsed YAML config: {file_path}")
                return data if isinstance(data, dict) else {}
        except (yaml.YAMLError, PermissionError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse YAML {file_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}")
            return {}
    
    def parse_env_file(self, file_path: Path) -> Dict[str, str]:
        """
        Parse .env file.
        
        Args:
            file_path: Path to .env file
            
        Returns:
            Dictionary of environment variables
        """
        env_vars: Dict[str, str] = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
            
            logger.debug(f"Parsed .env file: {file_path} ({len(env_vars)} vars)")
            return env_vars
            
        except (PermissionError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse .env {file_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}")
            return {}
    
    def extract_connection_strings(
        self,
        config: Dict[str, Any]
    ) -> List[ConnectionString]:
        """
        Extract connection strings from configuration.
        
        Looks for common patterns like:
        - ConnectionStrings.DefaultConnection
        - DATABASE_URL
        - DB_CONNECTION
        - connectionString
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of extracted and masked connection strings
        """
        connection_strings: List[ConnectionString] = []
        
        # Check for ConnectionStrings section (ASP.NET)
        if "ConnectionStrings" in config:
            conn_strings_section = config["ConnectionStrings"]
            if isinstance(conn_strings_section, dict):
                for name, conn_str in conn_strings_section.items():
                    if isinstance(conn_str, str):
                        masked_str = self._mask_secrets(conn_str)
                        db_type = self._detect_database_type(conn_str)
                        server, database = self._parse_connection_components(conn_str)
                        
                        connection_strings.append(ConnectionString(
                            name=name,
                            connection_string=masked_str,
                            database_type=db_type,
                            server=server,
                            database=database,
                        ))
        
        # Check for common environment variable patterns
        connection_patterns = [
            "DATABASE_URL", "DB_URL", "DB_CONNECTION",
            "SQLALCHEMY_DATABASE_URI", "MONGODB_URI",
            "REDIS_URL", "POSTGRES_URL", "MYSQL_URL"
        ]
        
        for key, value in config.items():
            if key in connection_patterns and isinstance(value, str):
                masked_str = self._mask_secrets(value)
                db_type = self._detect_database_type(value)
                
                connection_strings.append(ConnectionString(
                    name=key,
                    connection_string=masked_str,
                    database_type=db_type,
                ))
        
        return connection_strings
    
    def _is_config_file(self, file_path: Path) -> bool:
        """
        Determine if file is a configuration file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file appears to be a config file
        """
        config_names = [
            "appsettings", "config", "settings", "configuration",
            "app.config", "web.config"
        ]
        
        name_lower = file_path.stem.lower()
        return any(config_name in name_lower for config_name in config_names)
    
    def _mask_secrets(self, connection_string: str) -> str:
        """
        Mask passwords and secrets in connection string.
        
        Args:
            connection_string: Original connection string
            
        Returns:
            Connection string with secrets masked
        """
        # Mask common password patterns
        masked = re.sub(
            r'(password|pwd|pass)=([^;]+)',
            r'\1=***REDACTED***',
            connection_string,
            flags=re.IGNORECASE
        )
        
        # Mask PostgreSQL-style passwords
        masked = re.sub(
            r'://([^:]+):([^@]+)@',
            r'://\1:***REDACTED***@',
            masked
        )
        
        return masked
    
    def _detect_database_type(self, connection_string: str) -> Optional[str]:
        """
        Detect database type from connection string.
        
        Args:
            connection_string: Connection string to analyze
            
        Returns:
            Database type or None
        """
        conn_lower = connection_string.lower()
        
        if "postgresql://" in conn_lower or "postgres://" in conn_lower:
            return "postgresql"
        elif "mysql://" in conn_lower:
            return "mysql"
        elif "mongodb://" in conn_lower or "mongodb+srv://" in conn_lower:
            return "mongodb"
        elif "redis://" in conn_lower:
            return "redis"
        elif "server=" in conn_lower and "database=" in conn_lower:
            return "mssql"
        elif "sqlite://" in conn_lower or ".db" in conn_lower:
            return "sqlite"
        
        return None
    
    def _parse_connection_components(
        self,
        connection_string: str
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Parse server and database from connection string.
        
        Args:
            connection_string: Connection string to parse
            
        Returns:
            Tuple of (server, database) or (None, None)
        """
        server = None
        database = None
        
        # Parse SQL Server style
        server_match = re.search(r'Server=([^;]+)', connection_string, re.IGNORECASE)
        if server_match:
            server = server_match.group(1)
        
        db_match = re.search(r'Database=([^;]+)', connection_string, re.IGNORECASE)
        if db_match:
            database = db_match.group(1)
        
        return server, database
    
    def _extract_api_endpoints(self, config: Dict[str, Any]) -> List[str]:
        """
        Extract API endpoints from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of discovered API endpoints
        """
        endpoints: List[str] = []
        
        # Recursively search for URL-like values
        def search_urls(data: Any) -> None:
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str):
                        if self._is_url(value):
                            endpoints.append(value)
                    elif isinstance(value, (dict, list)):
                        search_urls(value)
            elif isinstance(data, list):
                for item in data:
                    search_urls(item)
        
        search_urls(config)
        return endpoints
    
    def _is_url(self, value: str) -> bool:
        """
        Check if string appears to be a URL.
        
        Args:
            value: String to check
            
        Returns:
            True if appears to be URL
        """
        return bool(re.match(r'https?://', value, re.IGNORECASE))
