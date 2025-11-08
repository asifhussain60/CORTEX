"""
Tests for Configuration Wizard Plugin

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.plugins.configuration_wizard_plugin import (
    Plugin, DatabaseConnection, APIEndpoint
)


class TestConfigurationWizardPlugin:
    """Test configuration wizard plugin functionality."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return Plugin()
    
    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create temporary repository structure."""
        repo = tmp_path / "test_repo"
        repo.mkdir()
        
        # Create some code files
        (repo / "app.py").write_text("""
import oracledb
conn = oracledb.connect('user/pass@localhost:1521/xe')
""")
        
        (repo / "api.py").write_text("""
import requests
BASE_URL = "https://api.example.com"
response = requests.get(f"{BASE_URL}/users")
""")
        
        # Create config file
        config = repo / "cortex.config.json"
        config.write_text(json.dumps({"project": {"name": "test"}}))
        
        return repo
    
    def test_plugin_initialization(self, plugin):
        """Test plugin initializes successfully."""
        assert plugin.initialize() is True
        assert plugin.discovered_databases == []
        assert plugin.discovered_apis == []
    
    def test_discover_mode(self, plugin, temp_repo):
        """Test auto-discovery mode without prompts."""
        result = plugin.execute({
            'mode': 'discover',
            'repo_path': str(temp_repo),
            'config_path': str(temp_repo / 'cortex.config.json'),
            'interactive': False
        })
        
        assert result['success'] is True
        assert 'databases_discovered' in result
        assert 'apis_discovered' in result
    
    def test_discover_oracle_from_code(self, plugin, temp_repo):
        """Test discovering Oracle connections from code."""
        plugin.repo_path = temp_repo
        plugin._discover_code_connections()
        
        # Should find oracle connection in app.py
        assert len(plugin.discovered_databases) > 0
        oracle_dbs = [db for db in plugin.discovered_databases if db.db_type == 'oracle']
        assert len(oracle_dbs) > 0
    
    def test_discover_apis_from_code(self, plugin, temp_repo):
        """Test discovering API endpoints from code."""
        plugin.repo_path = temp_repo
        plugin._discover_code_apis()
        
        # Should find API URL in api.py
        assert len(plugin.discovered_apis) > 0
        api_urls = [api.base_url for api in plugin.discovered_apis]
        assert any('api.example.com' in url for url in api_urls)
    
    @patch.dict('os.environ', {'ORACLE_CONNECTION_STRING': 'user/pass@host:1521/db'})
    def test_discover_from_environment(self, plugin):
        """Test discovering connections from environment variables."""
        plugin.repo_path = Path.cwd()
        plugin._discover_env_connections()
        
        # Should find Oracle connection from env var
        env_dbs = [db for db in plugin.discovered_databases 
                   if db.nickname == 'oracle_connection_string']
        assert len(env_dbs) > 0
    
    @patch.dict('os.environ', {'API_BASE_URL': 'https://api.test.com'})
    def test_discover_apis_from_environment(self, plugin):
        """Test discovering APIs from environment variables."""
        plugin.repo_path = Path.cwd()
        plugin._discover_env_apis()
        
        # Should find API from env var
        env_apis = [api for api in plugin.discovered_apis 
                    if api.nickname == 'api_base_url']
        assert len(env_apis) > 0
    
    def test_parse_tnsnames(self, plugin, tmp_path):
        """Test parsing Oracle tnsnames.ora file."""
        tnsnames = tmp_path / "tnsnames.ora"
        tnsnames.write_text("""
PROD_DB =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = prod-host)(PORT = 1521))
    (CONNECT_DATA =
      (SERVICE_NAME = production)
    )
  )

TEST_DB =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = test-host)(PORT = 1521))
    (CONNECT_DATA =
      (SERVICE_NAME = testing)
    )
  )
""")
        
        plugin._parse_tnsnames(tnsnames)
        
        # Should find both connections
        assert len(plugin.discovered_databases) == 2
        nicknames = [db.nickname for db in plugin.discovered_databases]
        assert 'PROD_DB' in nicknames
        assert 'TEST_DB' in nicknames
    
    def test_save_to_config(self, plugin, temp_repo):
        """Test saving configuration to cortex.config.json."""
        plugin.config_path = temp_repo / "cortex.config.json"
        
        databases = [
            DatabaseConnection(
                nickname='test_db',
                db_type='oracle',
                connection_string='user/pass@localhost:1521/test',
                validated=True
            )
        ]
        
        apis = [
            APIEndpoint(
                nickname='test_api',
                base_url='https://api.test.com',
                validated=True
            )
        ]
        
        plugin._save_to_config(databases, apis)
        
        # Verify config was saved
        assert plugin.config_path.exists()
        config = json.loads(plugin.config_path.read_text())
        
        assert 'crawlers' in config
        assert 'databases' in config['crawlers']
        assert 'apis' in config['crawlers']
        assert len(config['crawlers']['databases']) == 1
        assert len(config['crawlers']['apis']) == 1
        assert config['crawlers']['databases'][0]['nickname'] == 'test_db'
        assert config['crawlers']['apis'][0]['nickname'] == 'test_api'
    
    def test_database_connection_dataclass(self):
        """Test DatabaseConnection dataclass."""
        db = DatabaseConnection(
            nickname='my_db',
            db_type='oracle',
            connection_string='user/pass@host:1521/service',
            purpose='dev',
            username='testuser',
            auto_discovered=True,
            validated=False
        )
        
        assert db.nickname == 'my_db'
        assert db.db_type == 'oracle'
        assert db.auto_discovered is True
        assert db.validated is False
    
    def test_api_endpoint_dataclass(self):
        """Test APIEndpoint dataclass."""
        api = APIEndpoint(
            nickname='my_api',
            base_url='https://api.example.com',
            auth_type='bearer',
            auth_config={'token': 'secret'},
            openapi_spec='/path/to/spec.yaml',
            auto_discovered=True,
            validated=True
        )
        
        assert api.nickname == 'my_api'
        assert api.base_url == 'https://api.example.com'
        assert api.auth_type == 'bearer'
        assert api.validated is True
    
    def test_discover_openapi_specs(self, plugin, tmp_path):
        """Test discovering OpenAPI specification files."""
        repo = tmp_path / "repo"
        repo.mkdir()
        plugin.repo_path = repo
        
        # Create OpenAPI spec
        spec_dir = repo / "api"
        spec_dir.mkdir()
        spec_file = spec_dir / "openapi.json"
        spec_file.write_text(json.dumps({
            "openapi": "3.0.0",
            "servers": [
                {"url": "https://api.example.com/v1"},
                {"url": "https://api.example.com/v2"}
            ]
        }))
        
        plugin._discover_openapi_specs()
        
        # Should find APIs from spec
        assert len(plugin.discovered_apis) >= 2
        urls = [api.base_url for api in plugin.discovered_apis]
        assert "https://api.example.com/v1" in urls
    
    @patch('src.plugins.configuration_wizard_plugin.requests')
    def test_validate_api_connection(self, mock_requests, plugin):
        """Test API connection validation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response
        
        api = APIEndpoint(
            nickname='test_api',
            base_url='https://api.test.com',
            validated=False
        )
        
        is_valid = plugin._test_api_connection(api)
        assert is_valid is True
        mock_requests.get.assert_called_once()
    
    def test_non_interactive_mode(self, plugin, temp_repo):
        """Test non-interactive mode with auto-save."""
        result = plugin.execute({
            'mode': 'wizard',
            'repo_path': str(temp_repo),
            'config_path': str(temp_repo / 'cortex.config.json'),
            'interactive': False
        })
        
        # Should complete without user input
        assert result['success'] is True
    
    def test_extract_namespace_from_dsn(self, plugin):
        """Test namespace extraction from Oracle DSN."""
        namespace = plugin._extract_namespace_from_dsn('localhost:1521/KSESSIONS')
        assert namespace == 'KSESSIONS_DB'
        
        namespace = plugin._extract_namespace_from_dsn('prod-host:1521/production')
        assert namespace == 'PRODUCTION_DB'
    
    def test_discover_all_integration(self, plugin, temp_repo):
        """Test full discovery integration."""
        plugin.repo_path = temp_repo
        plugin._discover_all()
        
        # Should have discovered something
        total_discovered = len(plugin.discovered_databases) + len(plugin.discovered_apis)
        assert total_discovered > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
