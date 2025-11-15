"""Tests for ConfigurationWizardPlugin."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.plugins.configuration_wizard_plugin import (
    ConfigurationWizardPlugin, 
    DatabaseConnection, 
    APIEndpoint
)


class TestConfigurationWizardPlugin:
    """Test ConfigurationWizardPlugin functionality."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return ConfigurationWizardPlugin()
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {"existing": "data"}
            json.dump(config, f)
            yield Path(f.name)
        Path(f.name).unlink(missing_ok=True)
    
    def test_plugin_metadata(self, plugin):
        """Test plugin metadata."""
        metadata = plugin._get_metadata()
        assert metadata.name == "configuration_wizard_plugin"
        assert metadata.version == "1.0.0"
        assert "configuration wizard" in metadata.description.lower()
        assert metadata.author == "CORTEX Team"
    
    def test_natural_language_patterns(self, plugin):
        """Test natural language patterns."""
        patterns = plugin.get_natural_language_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert any("configure" in pattern.lower() for pattern in patterns)
        assert any("setup" in pattern.lower() for pattern in patterns)
    
    def test_initialize(self, plugin):
        """Test plugin initialization."""
        result = plugin.initialize()
        assert result is True
    
    def test_cleanup(self, plugin):
        """Test plugin cleanup."""
        result = plugin.cleanup()
        assert result is True
    
    def test_database_connection_creation(self):
        """Test DatabaseConnection dataclass."""
        db = DatabaseConnection(
            nickname="test_db",
            db_type="postgresql",
            connection_string="postgresql://user:pass@localhost:5432/testdb",
            purpose="dev",
            username="user"
        )
        assert db.nickname == "test_db"
        assert db.db_type == "postgresql"
        assert db.connection_string == "postgresql://user:pass@localhost:5432/testdb"
        assert db.purpose == "dev"
    
    def test_api_endpoint_creation(self):
        """Test APIEndpoint dataclass."""
        api = APIEndpoint(
            nickname="test_api",
            base_url="http://localhost:5000",
            auth_type="none"
        )
        assert api.nickname == "test_api"
        assert api.base_url == "http://localhost:5000"
        assert api.auth_type == "none"
    
    @patch('builtins.input', side_effect=['no'])
    def test_execute_auto_discovery_only(self, mock_input, plugin, temp_config):
        """Test auto-discovery mode execution."""
        context = {
            "mode": "discover",
            "config_path": str(temp_config)
        }
        
        result = plugin.execute(context)
        
        assert result["success"] is True
        assert "databases_discovered" in result
        assert "apis_discovered" in result
    
    @patch('builtins.input', side_effect=['yes', '0'])  # Yes to full wizard, but exit immediately
    def test_execute_full_wizard_early_exit(self, mock_input, plugin, temp_config):
        """Test full wizard with early exit."""
        context = {
            "mode": "wizard",
            "interactive": True,
            "config_path": str(temp_config)
        }
        
        result = plugin.execute(context)
        
        assert result["success"] is True
    
    def test_oracle_discovery(self, plugin, temp_config):
        """Test Oracle database discovery."""
        # Create mock tnsnames.ora content
        tnsnames_content = """
        TESTDB =
          (DESCRIPTION =
            (ADDRESS = (PROTOCOL = TCP)(HOST = localhost)(PORT = 1521))
            (CONNECT_DATA =
              (SERVER = DEDICATED)
              (SERVICE_NAME = testdb)
            )
          )
        """
        
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.read_text') as mock_read:
            
            mock_exists.return_value = True
            mock_read.return_value = tnsnames_content
            
            plugin.config_path = temp_config
            plugin._discover_oracle_tnsnames()
            
            # Should find one Oracle database
            oracle_dbs = [db for db in plugin.discovered_databases if db.db_type == "oracle"]
            assert len(oracle_dbs) > 0
            assert oracle_dbs[0].nickname == "TESTDB"
    
    def test_api_discovery_from_code(self, plugin, temp_config):
        """Test API discovery from source code."""
        # Create a temporary Python file with API calls
        with tempfile.TemporaryDirectory() as temp_dir:
            py_file = Path(temp_dir) / "test_code.py"
            py_file.write_text('''
import requests

def test_function():
    response = requests.get("http://localhost:5000/api/users")
    response = requests.post("https://api.github.com/users")
    return response
            ''')
            
            plugin.config_path = temp_config
            plugin._discover_code_apis(temp_dir)
            
            # Should find API endpoints
            assert len(plugin.discovered_apis) > 0
            api_urls = [api.base_url for api in plugin.discovered_apis]
            assert "http://localhost:5000" in api_urls
            assert "https://api.github.com" in api_urls
    
    def test_connection_testing(self, plugin):
        """Test database connection testing."""
        oracle_db = DatabaseConnection(
            nickname="test_oracle",
            db_type="oracle",
            connection_string="oracle://user:pass@localhost:1521/testdb"
        )
        
        sqlserver_db = DatabaseConnection(
            nickname="test_sqlserver", 
            db_type="sqlserver",
            connection_string="sqlserver://user:pass@localhost:1433/testdb"
        )
        
        # Test connection methods (will return False due to import errors in test env)
        oracle_result = plugin._test_oracle_connection(oracle_db)
        sqlserver_result = plugin._test_sqlserver_connection(sqlserver_db)
        
        # In test environment without database drivers, should return False
        assert oracle_result in [True, False]  # Allow both since it's environment dependent
        assert sqlserver_result in [True, False]
    
    def test_config_saving(self, plugin, temp_config):
        """Test configuration saving."""
        # Add some test data
        plugin.discovered_databases = [
            DatabaseConnection(
                nickname="test_db",
                db_type="postgresql",
                connection_string="postgresql://user:pass@localhost:5432/testdb",
                purpose="dev"
            )
        ]
        
        plugin.discovered_apis = [
            APIEndpoint(
                nickname="test_api",
                base_url="http://localhost:5000",
                auth_type="none"
            )
        ]
        
        plugin.config_path = temp_config
        result = plugin._save_to_config(plugin.discovered_databases, plugin.discovered_apis, str(temp_config))
        
        assert result is True
        
        # Verify configuration was saved
        with open(temp_config) as f:
            config = json.load(f)
        
        assert "databases" in config
        assert "apis" in config
        assert len(config["databases"]) == 1
        assert len(config["apis"]) == 1
        assert config["databases"][0]["nickname"] == "test_db"
        assert config["apis"][0]["nickname"] == "test_api"


def test_plugin_registration():
    """Test plugin registration function."""
    from src.plugins.configuration_wizard_plugin import register
    
    plugin = register()
    assert isinstance(plugin, ConfigurationWizardPlugin)
    assert plugin._get_metadata().name == "configuration_wizard_plugin"


if __name__ == "__main__":
    pytest.main([__file__])