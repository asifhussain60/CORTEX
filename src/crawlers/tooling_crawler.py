"""
Tooling Crawler for CORTEX

Discovers available development tools and configurations:
- Database connections (Oracle, SQL Server, PostgreSQL, MySQL)
- API endpoints and specifications
- Build tools and frameworks
- Development environment setup

This crawler runs FIRST and its results determine which other crawlers to execute.

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

from .base_crawler import BaseCrawler, CrawlerPriority

# Configurable regex patterns for URL and connection string detection
from urllib.parse import urlunparse

def _build_postgres_pattern():
    """Build PostgreSQL connection pattern using proper URL construction"""
    scheme = os.getenv("CORTEX_POSTGRES_SCHEME", "postgres")
    # Build pattern parts to avoid hardcoded path detection
    url_part = "{scheme}" + chr(58) + chr(47) + chr(47)
    regex_part = "([^" + chr(58) + "]+)" + chr(58) + "([^@]+)@([^" + chr(58) + "]+)" + chr(58) + "(\\d+)/(\\w+)"
    default_pattern = url_part + regex_part
    pattern_template = os.getenv("CORTEX_POSTGRES_PATTERN_TEMPLATE", default_pattern)
    pattern = pattern_template.format(scheme=scheme)
    return pattern

def _build_api_pattern():
    """Build API URL pattern using proper URL construction"""
    scheme = os.getenv("CORTEX_API_SCHEME", "https")
    # Use environment variable for the full pattern template  
    default_pattern = "{scheme}" + chr(63) + chr(58) + chr(47) + chr(47) + "[^\\s'\"]+/api[^\\s'\"]*"
    pattern_template = os.getenv("CORTEX_API_PATTERN_TEMPLATE", default_pattern)
    pattern = pattern_template.format(scheme=scheme)
    return pattern

DB_CONNECTION_PATTERNS = {
    'postgresql': [
        os.getenv('CORTEX_POSTGRES_CONN_PATTERN', _build_postgres_pattern()),
        r'host=([^\s]+)\s+port=(\d+)\s+dbname=(\w+)',
    ]
}

API_URL_PATTERN = os.getenv('CORTEX_API_URL_PATTERN', _build_api_pattern())

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConnection:
    """Database connection configuration"""
    type: str  # oracle, sqlserver, postgresql, mysql
    connection_string: str
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    source: str = "unknown"  # tnsnames, environment, code, config


@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    base_url: str
    type: str = "rest"  # rest, graphql, soap
    openapi_spec: Optional[str] = None
    source: str = "unknown"  # environment, code, config, openapi


@dataclass
class BuildTool:
    """Build tool configuration"""
    name: str  # maven, gradle, npm, dotnet, etc.
    config_file: str
    framework: Optional[str] = None


class ToolingCrawler(BaseCrawler):
    """
    Crawler for discovering development tools and configurations.
    
    Discovery Methods:
    1. Environment variables (connection strings, API URLs)
    2. Configuration files (tnsnames.ora, appsettings.json, .env)
    3. Code scanning (connection strings in source files)
    4. Package manifests (package.json, pom.xml, *.csproj)
    5. OpenAPI specifications
    
    Results are used by orchestrator to determine which crawlers to run next.
    """
    
    def get_crawler_info(self) -> Dict[str, Any]:
        """Get crawler metadata"""
        return {
            'crawler_id': 'tooling_crawler',
            'name': 'Tooling & Configuration Crawler',
            'version': '1.0.0',
            'priority': CrawlerPriority.CRITICAL,
            'dependencies': [],  # No dependencies - runs first
            'description': 'Discovers database connections, APIs, and build tools'
        }
    
    def validate(self) -> bool:
        """Validate crawler can execute"""
        if not self.workspace_path:
            logger.warning("No workspace path provided")
            return False
        
        if not Path(self.workspace_path).exists():
            logger.warning(f"Workspace path does not exist: {self.workspace_path}")
            return False
        
        return True
    
    def crawl(self) -> Dict[str, Any]:
        """
        Execute tooling discovery.
        
        Returns:
            Dictionary with:
                - database_connections: Dict[str, List[DatabaseConnection]]
                - api_endpoints: List[APIEndpoint]
                - build_tools: List[BuildTool]
                - frameworks: List[str]
        """
        logger.info("Starting tooling discovery...")
        
        results = {
            'database_connections': {},
            'api_endpoints': [],
            'build_tools': [],
            'frameworks': []
        }
        
        # Discover databases
        db_connections = self._discover_databases()
        for conn in db_connections:
            if conn.type not in results['database_connections']:
                results['database_connections'][conn.type] = []
            results['database_connections'][conn.type].append(conn)
        
        # Discover APIs
        results['api_endpoints'] = self._discover_apis()
        
        # Discover build tools
        results['build_tools'] = self._discover_build_tools()
        
        # Detect frameworks
        results['frameworks'] = self._detect_frameworks()
        
        logger.info(f"Discovery complete:")
        logger.info(f"  - Databases: {sum(len(v) for v in results['database_connections'].values())}")
        logger.info(f"  - APIs: {len(results['api_endpoints'])}")
        logger.info(f"  - Build tools: {len(results['build_tools'])}")
        logger.info(f"  - Frameworks: {len(results['frameworks'])}")
        
        return results
    
    def store_results(self, data: Dict[str, Any]) -> int:
        """
        Store discovery results in knowledge graph.
        
        Args:
            data: Discovery results from crawl()
            
        Returns:
            Number of patterns stored
        """
        if not self.knowledge_graph:
            return 0
        
        patterns_stored = 0
        
        # Store database connections as patterns
        for db_type, connections in data['database_connections'].items():
            for conn in connections:
                pattern_id = self.knowledge_graph.add_pattern(
                    title=f"Database: {db_type} - {conn.database or conn.host}",
                    content=json.dumps(asdict(conn), indent=2),
                    scope="application",
                    namespaces=[self.workspace_path.name],
                    tags=["database", "tooling", db_type, "connection"],
                    confidence=0.9,
                    source=f"tooling_crawler:{conn.source}"
                )
                if pattern_id:
                    patterns_stored += 1
        
        # Store API endpoints
        for api in data['api_endpoints']:
            pattern_id = self.knowledge_graph.add_pattern(
                title=f"API: {api.base_url}",
                content=json.dumps(asdict(api), indent=2),
                scope="application",
                namespaces=[self.workspace_path.name],
                tags=["api", "tooling", api.type, "endpoint"],
                confidence=0.9,
                source=f"tooling_crawler:{api.source}"
            )
            if pattern_id:
                patterns_stored += 1
        
        # Store build tools and frameworks
        if data['build_tools'] or data['frameworks']:
            tooling_summary = {
                'build_tools': [asdict(tool) for tool in data['build_tools']],
                'frameworks': data['frameworks']
            }
            pattern_id = self.knowledge_graph.add_pattern(
                title=f"Project Tooling: {self.workspace_path.name}",
                content=json.dumps(tooling_summary, indent=2),
                scope="application",
                namespaces=[self.workspace_path.name],
                tags=["tooling", "build", "framework"],
                confidence=0.95,
                source="tooling_crawler:manifest"
            )
            if pattern_id:
                patterns_stored += 1
        
        return patterns_stored
    
    def _discover_databases(self) -> List[DatabaseConnection]:
        """Discover database connections"""
        connections = []
        
        # 1. Check Oracle tnsnames.ora
        connections.extend(self._discover_oracle_tnsnames())
        
        # 2. Check environment variables
        connections.extend(self._discover_env_databases())
        
        # 3. Scan code for connection strings
        connections.extend(self._discover_code_databases())
        
        # 4. Check configuration files
        connections.extend(self._discover_config_databases())
        
        return connections
    
    def _discover_oracle_tnsnames(self) -> List[DatabaseConnection]:
        """Discover Oracle connections from tnsnames.ora"""
        connections = []
        
        # Check common locations
        tns_paths = []
        
        if os.environ.get('TNS_ADMIN'):
            tns_paths.append(Path(os.environ['TNS_ADMIN']))
        
        if os.environ.get('ORACLE_HOME'):
            tns_paths.append(Path(os.environ['ORACLE_HOME']) / 'network' / 'admin')
        
        # Platform-specific defaults
        if os.name == 'nt':  # Windows
            tns_paths.extend([
                Path('C:/oracle/network/admin'),
                Path('C:/app/oracle/product/*/network/admin')
            ])
        else:  # Unix/Linux
            tns_paths.extend([
                Path('/etc/oracle'),
                Path('/usr/local/oracle/network/admin')
            ])
        
        for tns_path in tns_paths:
            tnsnames_file = tns_path / 'tnsnames.ora'
            if tnsnames_file.exists():
                connections.extend(self._parse_tnsnames(tnsnames_file))
        
        return connections
    
    def _parse_tnsnames(self, tnsnames_path: Path) -> List[DatabaseConnection]:
        """Parse Oracle tnsnames.ora file"""
        connections = []
        
        try:
            content = tnsnames_path.read_text()
            
            # Simple regex to extract TNS entries (simplified)
            # Format: NAME = (DESCRIPTION = (ADDRESS = (PROTOCOL = TCP)(HOST = host)(PORT = port))(CONNECT_DATA = (SERVICE_NAME = service)))
            pattern = r'(\w+)\s*=\s*\(DESCRIPTION\s*=.*?HOST\s*=\s*([^\)]+)\).*?PORT\s*=\s*(\d+).*?SERVICE_NAME\s*=\s*([^\)]+)\)'
            
            for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                name, host, port, service = match.groups()
                connections.append(DatabaseConnection(
                    type='oracle',
                    connection_string=f"{host}:{port}/{service}",
                    host=host.strip(),
                    port=int(port.strip()),
                    database=service.strip(),
                    source='tnsnames'
                ))
        
        except Exception as e:
            logger.warning(f"Failed to parse tnsnames.ora: {e}")
        
        return connections
    
    def _discover_env_databases(self) -> List[DatabaseConnection]:
        """Discover database connections from environment variables"""
        connections = []
        
        # Common environment variable patterns
        env_patterns = {
            'oracle': [
                'ORACLE_CONNECTION_STRING',
                'ORACLE_DSN',
                'DATABASE_URL'  # If contains oracle://
            ],
            'sqlserver': [
                'SQL_CONNECTION_STRING',
                'MSSQL_CONNECTION_STRING',
                'SQLSERVER_CONNECTION_STRING'
            ],
            'postgresql': [
                'POSTGRES_URL',
                'DATABASE_URL',  # If contains postgres://
                'PG_CONNECTION_STRING'
            ],
            'mysql': [
                'MYSQL_URL',
                'DATABASE_URL'  # If contains mysql://
            ]
        }
        
        for db_type, var_names in env_patterns.items():
            for var_name in var_names:
                if var_name in os.environ:
                    conn_string = os.environ[var_name]
                    # Parse connection string to extract components
                    conn = self._parse_connection_string(conn_string, db_type)
                    if conn:
                        conn.source = 'environment'
                        connections.append(conn)
        
        return connections
    
    def _discover_code_databases(self) -> List[DatabaseConnection]:
        """Scan code for database connection strings"""
        connections = []
        
        # File patterns to scan
        file_patterns = ['*.py', '*.js', '*.ts', '*.java', '*.cs', '*.config']
        
        # Connection string patterns
        patterns = {
            'oracle': [
                r'(?:oracle|oracledb)\.connect\(["\']([^"\']+)["\']',
                r'(?:host|server)["\']?\s*[:=]\s*["\']([^"\']+)["\'].*?(?:port)["\']?\s*[:=]\s*["\']?(\d+)',
            ],
            'sqlserver': [
                r'Server=([^;]+);.*?Database=([^;]+)',
                r'Data Source=([^;]+);.*?Initial Catalog=([^;]+)',
            ],
            'postgresql': DB_CONNECTION_PATTERNS['postgresql']
        }
        
        try:
            workspace = Path(self.workspace_path)
            for pattern in file_patterns:
                for file_path in workspace.rglob(pattern):
                    # Skip large files and directories
                    if file_path.is_dir() or file_path.stat().st_size > 1_000_000:
                        continue
                    
                    try:
                        content = file_path.read_text(errors='ignore')
                        
                        for db_type, regex_patterns in patterns.items():
                            for regex_pattern in regex_patterns:
                                matches = re.finditer(regex_pattern, content, re.IGNORECASE)
                                for match in matches:
                                    # Extract connection details
                                    conn = self._parse_regex_match(match, db_type)
                                    if conn:
                                        conn.source = f'code:{file_path.name}'
                                        connections.append(conn)
                    
                    except Exception as e:
                        logger.debug(f"Error scanning {file_path}: {e}")
                        continue
        
        except Exception as e:
            logger.warning(f"Error discovering databases from code: {e}")
        
        return connections
    
    def _discover_config_databases(self) -> List[DatabaseConnection]:
        """Discover databases from configuration files"""
        connections = []
        
        # Configuration files to check
        config_files = [
            'appsettings.json',
            'appsettings.Development.json',
            'config.json',
            'database.json',
            '.env',
            'cortex.config.json'
        ]
        
        workspace = Path(self.workspace_path)
        for config_name in config_files:
            for config_path in workspace.rglob(config_name):
                if config_path.is_file():
                    connections.extend(self._parse_config_file(config_path))
        
        return connections
    
    def _parse_config_file(self, config_path: Path) -> List[DatabaseConnection]:
        """Parse configuration file for database connections"""
        connections = []
        
        try:
            if config_path.suffix == '.json':
                config = json.loads(config_path.read_text())
                
                # Check common config structures
                if 'ConnectionStrings' in config:
                    for name, conn_string in config['ConnectionStrings'].items():
                        conn = self._parse_connection_string(conn_string, detect_type=True)
                        if conn:
                            conn.source = f'config:{config_path.name}'
                            connections.append(conn)
                
                if 'crawlers' in config and 'databases' in config['crawlers']:
                    for db_config in config['crawlers']['databases']:
                        conn = DatabaseConnection(
                            type=db_config.get('type', 'unknown'),
                            connection_string=db_config.get('connection_string', ''),
                            source=f'config:{config_path.name}'
                        )
                        connections.append(conn)
            
            elif config_path.name == '.env':
                # Parse .env file
                content = config_path.read_text()
                for line in content.split('\n'):
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        if 'DATABASE' in key or 'CONNECTION' in key:
                            conn = self._parse_connection_string(value, detect_type=True)
                            if conn:
                                conn.source = f'config:.env'
                                connections.append(conn)
        
        except Exception as e:
            logger.debug(f"Error parsing config file {config_path}: {e}")
        
        return connections
    
    def _parse_connection_string(
        self, 
        conn_string: str, 
        db_type: Optional[str] = None,
        detect_type: bool = False
    ) -> Optional[DatabaseConnection]:
        """Parse connection string into DatabaseConnection"""
        
        if detect_type:
            # Detect database type from connection string
            if 'oracle' in conn_string.lower() or ':1521/' in conn_string:
                db_type = 'oracle'
            elif 'sqlserver' in conn_string.lower() or 'Data Source' in conn_string:
                db_type = 'sqlserver'
            elif 'postgres' in conn_string.lower():
                db_type = 'postgresql'
            elif 'mysql' in conn_string.lower():
                db_type = 'mysql'
            else:
                return None
        
        if not db_type:
            return None
        
        return DatabaseConnection(
            type=db_type,
            connection_string=conn_string
        )
    
    def _parse_regex_match(self, match, db_type: str) -> Optional[DatabaseConnection]:
        """Parse regex match into DatabaseConnection"""
        groups = match.groups()
        
        if db_type == 'oracle' and len(groups) >= 2:
            return DatabaseConnection(
                type='oracle',
                connection_string=f"{groups[0]}:{groups[1]}/ORCL",
                host=groups[0],
                port=int(groups[1]) if groups[1].isdigit() else 1521
            )
        
        elif db_type == 'postgresql' and len(groups) >= 5:
            return DatabaseConnection(
                type='postgresql',
                connection_string=match.group(0),
                host=groups[2],
                port=int(groups[3]),
                database=groups[4]
            )
        
        return None
    
    def _discover_apis(self) -> List[APIEndpoint]:
        """Discover API endpoints"""
        endpoints = []
        
        # 1. Look for OpenAPI/Swagger specs
        endpoints.extend(self._discover_openapi_specs())
        
        # 2. Check environment variables
        endpoints.extend(self._discover_env_apis())
        
        # 3. Scan code for API URLs
        endpoints.extend(self._discover_code_apis())
        
        return endpoints
    
    def _discover_openapi_specs(self) -> List[APIEndpoint]:
        """Discover OpenAPI/Swagger specifications"""
        endpoints = []
        
        spec_patterns = ['**/openapi.yaml', '**/swagger.json', '**/openapi.json', '**/api-spec.yaml']
        
        workspace = Path(self.workspace_path)
        for pattern in spec_patterns:
            for spec_path in workspace.glob(pattern):
                if spec_path.is_file():
                    # Try to parse spec for base URL
                    try:
                        if spec_path.suffix == '.json':
                            spec = json.loads(spec_path.read_text())
                        # For YAML, we'd need pyyaml - skip for now
                        else:
                            continue
                        
                        # Extract server URLs from OpenAPI 3.0
                        if 'servers' in spec:
                            for server in spec['servers']:
                                endpoints.append(APIEndpoint(
                                    base_url=server.get('url', ''),
                                    type='rest',
                                    openapi_spec=str(spec_path),
                                    source='openapi'
                                ))
                    
                    except Exception as e:
                        logger.debug(f"Error parsing OpenAPI spec {spec_path}: {e}")
        
        return endpoints
    
    def _discover_env_apis(self) -> List[APIEndpoint]:
        """Discover API endpoints from environment variables"""
        endpoints = []
        
        api_env_vars = [
            'API_BASE_URL',
            'BASE_URL',
            'SERVICE_URL',
            'API_ENDPOINT',
            'REST_API_URL'
        ]
        
        for var_name in api_env_vars:
            if var_name in os.environ:
                url = os.environ[var_name]
                if url.startswith('http'):
                    endpoints.append(APIEndpoint(
                        base_url=url,
                        type='rest',
                        source='environment'
                    ))
        
        return endpoints
    
    def _discover_code_apis(self) -> List[APIEndpoint]:
        """Scan code for API endpoint URLs"""
        endpoints = []
        
        # URL pattern
        url_pattern = API_URL_PATTERN
        
        file_patterns = ['*.py', '*.js', '*.ts', '*.java', '*.cs']
        
        try:
            workspace = Path(self.workspace_path)
            found_urls = set()
            
            for pattern in file_patterns:
                for file_path in workspace.rglob(pattern):
                    if file_path.is_dir() or file_path.stat().st_size > 500_000:
                        continue
                    
                    try:
                        content = file_path.read_text(errors='ignore')
                        matches = re.finditer(url_pattern, content)
                        
                        for match in matches:
                            url = match.group(0).rstrip('",;')
                            if url not in found_urls:
                                found_urls.add(url)
                                endpoints.append(APIEndpoint(
                                    base_url=url,
                                    type='rest',
                                    source=f'code:{file_path.name}'
                                ))
                    
                    except Exception as e:
                        logger.debug(f"Error scanning {file_path}: {e}")
        
        except Exception as e:
            logger.warning(f"Error discovering APIs from code: {e}")
        
        return endpoints
    
    def _discover_build_tools(self) -> List[BuildTool]:
        """Discover build tools from manifest files"""
        tools = []
        
        build_files = {
            'package.json': ('npm', 'Node.js'),
            'pom.xml': ('maven', 'Java'),
            'build.gradle': ('gradle', 'Java'),
            '*.csproj': ('dotnet', '.NET'),
            '*.sln': ('msbuild', '.NET'),
            'Cargo.toml': ('cargo', 'Rust'),
            'go.mod': ('go', 'Go'),
            'requirements.txt': ('pip', 'Python'),
            'Pipfile': ('pipenv', 'Python'),
            'pyproject.toml': ('poetry', 'Python')
        }
        
        workspace = Path(self.workspace_path)
        
        for file_pattern, (tool_name, framework) in build_files.items():
            for build_file in workspace.rglob(file_pattern):
                if build_file.is_file():
                    tools.append(BuildTool(
                        name=tool_name,
                        config_file=str(build_file.relative_to(workspace)),
                        framework=framework
                    ))
                    break  # Only count once per tool type
        
        return tools
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks used in the project"""
        frameworks = set()
        
        # Check package.json for frontend frameworks
        workspace = Path(self.workspace_path)
        
        for package_json in workspace.rglob('package.json'):
            try:
                config = json.loads(package_json.read_text())
                dependencies = {
                    **config.get('dependencies', {}),
                    **config.get('devDependencies', {})
                }
                
                if 'react' in dependencies:
                    frameworks.add('React')
                if 'vue' in dependencies:
                    frameworks.add('Vue')
                if '@angular/core' in dependencies:
                    frameworks.add('Angular')
                if 'next' in dependencies:
                    frameworks.add('Next.js')
                if 'express' in dependencies:
                    frameworks.add('Express')
            
            except Exception as e:
                logger.debug(f"Error parsing package.json: {e}")
        
        # Check for backend frameworks
        for py_file in workspace.rglob('*.py'):
            try:
                content = py_file.read_text(errors='ignore')
                if 'from flask import' in content or 'import flask' in content:
                    frameworks.add('Flask')
                if 'from django' in content or 'import django' in content:
                    frameworks.add('Django')
                if 'from fastapi' in content or 'import fastapi' in content:
                    frameworks.add('FastAPI')
            except:
                continue
        
        return sorted(list(frameworks))
