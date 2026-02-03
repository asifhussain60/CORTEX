"""
Tests for PostgreSQL DatabaseCrawlerPlugin implementation.

Authority: Phase 19 Component #6
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


# Mock psycopg2 module before importing PostgreSQLPlugin
@pytest.fixture(autouse=True)
def mock_psycopg2_module():
    """Mock psycopg2 module for all tests."""
    mock_psycopg2 = MagicMock()
    sys.modules['psycopg2'] = mock_psycopg2
    sys.modules['psycopg2.extras'] = MagicMock()
    yield mock_psycopg2
    sys.modules.pop('psycopg2', None)
    sys.modules.pop('psycopg2.extras', None)


from cortex.lens.analyzers.postgresql_plugin import PostgreSQLPlugin


class TestPostgreSQLPlugin:
    """Test PostgreSQL plugin implementation."""
    
    @pytest.fixture
    def plugin(self) -> PostgreSQLPlugin:
        """Create PostgreSQLPlugin instance."""
        return PostgreSQLPlugin()
    
    @pytest.fixture
    def mock_connection(self) -> Mock:
        """Create mock psycopg2 connection."""
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = None
        return conn
    
    def test_plugin_initializes(self, plugin: PostgreSQLPlugin):
        """Test plugin initializes correctly."""
        assert plugin is not None
        assert plugin.connection is None
        assert plugin.connection_info is None
    
    @patch("psycopg2.connect")
    def test_connect_success(self, mock_connect: Mock, plugin: PostgreSQLPlugin):
        """Test successful connection to PostgreSQL."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        connection_string = "postgresql://localhost:5432/testdb"
        result = plugin.connect(connection_string)
        
        assert isinstance(result, DatabaseConnection)
        assert result.database_type == "postgresql"
        assert result.is_connected is True
        assert plugin.connection is not None
    
    @patch("psycopg2.connect")
    def test_connect_failure(self, mock_connect: Mock, plugin: PostgreSQLPlugin):
        """Test connection failure handling."""
        mock_connect.side_effect = Exception("Connection failed")
        
        connection_string = "postgresql://invalid:5432/db"
        
        with pytest.raises(ConnectionError, match="Failed to connect"):
            plugin.connect(connection_string)
    
    def test_disconnect(self, plugin: PostgreSQLPlugin, mock_connection: Mock):
        """Test disconnect closes connection."""
        plugin.connection = mock_connection
        plugin.disconnect()
        
        mock_connection.close.assert_called_once()
        assert plugin.connection is None
    
    def test_test_connection_success(self, plugin: PostgreSQLPlugin, mock_connection: Mock):
        """Test connection health check success."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        cursor.fetchone.return_value = (1,)
        
        result = plugin.test_connection()
        
        assert result is True
        cursor.execute.assert_called_with("SELECT 1")
    
    def test_test_connection_failure(self, plugin: PostgreSQLPlugin, mock_connection: Mock):
        """Test connection health check failure."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        cursor.execute.side_effect = Exception("Connection lost")
        
        result = plugin.test_connection()
        
        assert result is False
    
    def test_get_tables(self, plugin: PostgreSQLPlugin, mock_connection: Mock):
        """Test get_tables retrieves table list."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        
        # Mock both tables query and subsequent get_columns calls
        cursor.fetchall.side_effect = [
            [{"table_schema": "public", "table_name": "users"}],  # tables query
            [{"column_name": "id", "data_type": "integer", "is_nullable": "NO", "column_default": None, "constraint_type": "PRIMARY KEY"}],  # columns for users
        ]
        
        tables = plugin.get_tables()
        
        assert len(tables) == 1
        assert isinstance(tables[0], SchemaEntity)
        assert tables[0].name == "users"
        assert tables[0].schema == "public"
        assert tables[0].entity_type == "table"
    
    def test_get_tables_with_schema_filter(self, plugin: PostgreSQLPlugin, mock_connection: Mock):
        """Test get_tables with schema filter."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        
        # Mock both tables query and subsequent get_columns call
        cursor.fetchall.side_effect = [
            [{"table_schema": "public", "table_name": "users"}],  # tables query
            [{"column_name": "id", "data_type": "integer", "is_nullable": "NO", "column_default": None, "constraint_type": "PRIMARY KEY"}],  # columns
        ]
        
        tables = plugin.get_tables(schema="public")
        
        assert len(tables) == 1
        # Verify WHERE clause was added
        call_args = cursor.execute.call_args[0][0]
        assert "WHERE" in call_args
        assert "table_schema" in call_args
    
    def test_get_columns(self, plugin: PostgreSQLPlugin, mock_connection: Mock):
        """Test get_columns retrieves column definitions."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        cursor.fetchall.return_value = [
            {"column_name": "id", "data_type": "integer", "is_nullable": "NO", "column_default": None, "constraint_type": "PRIMARY KEY"},
            {"column_name": "email", "data_type": "varchar", "is_nullable": "NO", "column_default": None, "constraint_type": None},
            {"column_name": "created_at", "data_type": "timestamp", "is_nullable": "YES", "column_default": "now()", "constraint_type": None},
        ]
        
        columns = plugin.get_columns("users", schema="public")
        
        assert len(columns) == 3
        assert columns[0]["name"] == "id"
        assert columns[0]["type"] == "integer"
        assert columns[0]["nullable"] is False
        assert columns[0]["constraints"] == "PRIMARY KEY"
        assert columns[2]["default"] == "now()"
    
    def test_get_relationships(self, plugin: PostgreSQLPlugin, mock_connection: Mock):
        """Test get_relationships retrieves foreign keys."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        cursor.fetchall.return_value = [
            {"constraint_name": "fk_orders_users", "table_name": "orders", "column_name": "user_id", "foreign_table_name": "users", "foreign_column_name": "id"},
        ]
        
        relationships = plugin.get_relationships()
        
        assert len(relationships) == 1
        assert relationships[0]["constraint_name"] == "fk_orders_users"
        assert relationships[0]["source_table"] == "orders"
        assert relationships[0]["source_column"] == "user_id"
        assert relationships[0]["target_table"] == "users"
        assert relationships[0]["target_column"] == "id"
    
    def test_extract_schema(self, plugin: PostgreSQLPlugin, mock_connection: Mock):
        """Test extract_schema returns complete schema."""
        plugin.connection = mock_connection
        cursor = mock_connection.cursor.return_value
        
        # Mock tables + columns, views, functions, relationships, metadata
        cursor.fetchall.side_effect = [
            [{"table_schema": "public", "table_name": "users"}],  # tables query
            [{"column_name": "id", "data_type": "integer", "is_nullable": "NO", "column_default": None, "constraint_type": "PRIMARY KEY"}],  # columns
            [{"table_schema": "public", "table_name": "vw_stats"}],  # views query
            [{"schema_name": "public", "function_name": "fn_calc"}],  # functions query
            [{"constraint_name": "fk_test", "table_name": "orders", "column_name": "user_id", "foreign_table_name": "users", "foreign_column_name": "id"}],  # relationships
        ]
        cursor.fetchone.return_value = {"version": "PostgreSQL 14.5"}
        
        schema = plugin.extract_schema()
        
        assert "tables" in schema
        assert "views" in schema
        assert "functions" in schema
        assert "relationships" in schema
        assert "metadata" in schema
        assert len(schema["tables"]) == 1
        assert schema["metadata"]["database_version"] == "PostgreSQL 14.5"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
