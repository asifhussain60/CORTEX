"""
Tests for SQL Server DatabaseCrawlerPlugin implementation.

Authority: Phase 19 Component #5
Rule: CORE-008 (TDD First)
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from cortex.lens.analyzers.database_crawler_plugin import (
    DatabaseConnection,
    SchemaEntity,
)


# Mock pyodbc module before importing SQLServerPlugin
@pytest.fixture(autouse=True)
def mock_pyodbc_module():
    """Mock pyodbc module for all tests."""
    mock_pyodbc = MagicMock()
    sys.modules['pyodbc'] = mock_pyodbc
    yield mock_pyodbc
    sys.modules.pop('pyodbc', None)


from cortex.lens.analyzers.sqlserver_plugin import SQLServerPlugin


class TestSQLServerPlugin:
    """Test SQL Server plugin implementation."""
    
    @pytest.fixture
    def plugin(self) -> SQLServerPlugin:
        """Create SQLServerPlugin instance."""
        return SQLServerPlugin()
    
    @pytest.fixture
    def mock_connection(self) -> Mock:
        """Create mock pyodbc connection."""
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = None
        return conn
    
    def test_plugin_initializes(self, plugin: SQLServerPlugin):
        """Test plugin initializes correctly."""
        assert plugin is not None
        assert plugin.connection is None
        assert plugin.connection_info is None
    
    @patch("pyodbc.connect")
    def test_connect_success(self, mock_connect: Mock, plugin: SQLServerPlugin):
        """Test successful connection to SQL Server."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=testdb;Trusted_Connection=yes;"
        result = plugin.connect(connection_string)
        
        assert isinstance(result, DatabaseConnection)
        assert result.database_type == "sqlserver"
        assert result.is_connected is True
        assert plugin.connection is not None
    
    @patch("pyodbc.connect")
    def test_connect_failure(self, mock_connect: Mock, plugin: SQLServerPlugin):
        """Test connection failure handling."""
        mock_connect.side_effect = Exception("Connection failed")
        
        connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=invalid;"
        
        with pytest.raises(ConnectionError, match="Failed to connect"):
            plugin.connect(connection_string)
    
    def test_disconnect(self, plugin: SQLServerPlugin, mock_connection: Mock):
        """Test disconnect closes connection."""
        plugin.connection = mock_connection
        plugin.disconnect()
        
        mock_connection.close.assert_called_once()
        assert plugin.connection is None
    
    def test_test_connection_success(self, plugin: SQLServerPlugin, mock_connection: Mock):
        """Test connection health check success."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        cursor.fetchone.return_value = (1,)
        
        result = plugin.test_connection()
        
        assert result is True
        cursor.execute.assert_called_with("SELECT 1")
    
    def test_test_connection_failure(self, plugin: SQLServerPlugin, mock_connection: Mock):
        """Test connection health check failure."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        cursor.execute.side_effect = Exception("Connection lost")
        
        result = plugin.test_connection()
        
        assert result is False
    
    def test_get_tables(self, plugin: SQLServerPlugin, mock_connection: Mock):
        """Test get_tables retrieves table list."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        
        # Mock both tables query and subsequent get_columns calls
        cursor.fetchall.side_effect = [
            [("dbo", "users"), ("dbo", "orders"), ("public", "products")],  # tables query
            [("id", "int", "NO", None, "PK")],  # columns for users
            [("id", "int", "NO", None, "PK")],  # columns for orders
            [("id", "int", "NO", None, "PK")],  # columns for products
        ]
        
        tables = plugin.get_tables()
        
        assert len(tables) == 3
        assert all(isinstance(t, SchemaEntity) for t in tables)
        assert tables[0].name == "users"
        assert tables[0].schema == "dbo"
        assert tables[0].entity_type == "table"
    
    def test_get_tables_with_schema_filter(self, plugin: SQLServerPlugin, mock_connection: Mock):
        """Test get_tables with schema filter."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        
        # Mock both tables query and subsequent get_columns call
        cursor.fetchall.side_effect = [
            [("dbo", "users")],  # tables query
            [("id", "int", "NO", None, "PK")],  # columns for users
        ]
        
        tables = plugin.get_tables(schema="dbo")
        
        assert len(tables) == 1
        # Verify WHERE clause was added
        call_args = cursor.execute.call_args[0][0]
        assert "WHERE" in call_args
        assert "table_schema" in call_args.lower()
    
    def test_get_columns(self, plugin: SQLServerPlugin, mock_connection: Mock):
        """Test get_columns retrieves column definitions."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        cursor.fetchall.return_value = [
            ("id", "int", "NO", None, "PK"),
            ("email", "varchar", "NO", None, None),
            ("created_at", "datetime", "YES", "GETDATE()", None),
        ]
        
        columns = plugin.get_columns("users", schema="dbo")
        
        assert len(columns) == 3
        assert columns[0]["name"] == "id"
        assert columns[0]["type"] == "int"
        assert columns[0]["nullable"] is False
        assert columns[0]["constraints"] == "PK"
        assert columns[2]["default"] == "GETDATE()"
    
    def test_get_relationships(self, plugin: SQLServerPlugin, mock_connection: Mock):
        """Test get_relationships retrieves foreign keys."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        cursor.fetchall.return_value = [
            ("FK_orders_users", "orders", "user_id", "users", "id"),
            ("FK_orders_products", "orders", "product_id", "products", "id"),
        ]
        
        relationships = plugin.get_relationships()
        
        assert len(relationships) == 2
        assert relationships[0]["constraint_name"] == "FK_orders_users"
        assert relationships[0]["source_table"] == "orders"
        assert relationships[0]["source_column"] == "user_id"
        assert relationships[0]["target_table"] == "users"
        assert relationships[0]["target_column"] == "id"
    
    def test_extract_schema(self, plugin: SQLServerPlugin, mock_connection: Mock):
        """Test extract_schema returns complete schema."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        
        # Mock tables query + get_columns
        # Mock views query
        # Mock procedures query
        # Mock functions query
        # Mock relationships query
        # Mock metadata query
        cursor.fetchall.side_effect = [
            [("dbo", "users")],  # tables query
            [("id", "int", "NO", None, "PK")],  # get_columns for users
            [("dbo", "vw_user_stats")],  # views query
            [("dbo", "sp_get_users")],  # procedures query
            [("dbo", "fn_calculate")],  # functions query
            [("FK_test", "orders", "user_id", "users", "id")],  # relationships query
        ]
        cursor.fetchone.return_value = ("Microsoft SQL Server 2019",)
        
        schema = plugin.extract_schema()
        
        assert "tables" in schema
        assert "views" in schema
        assert "procedures" in schema
        assert "functions" in schema
        assert "relationships" in schema
        assert "metadata" in schema
        assert len(schema["tables"]) == 1
        assert schema["metadata"]["database_version"] == "Microsoft SQL Server 2019"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
