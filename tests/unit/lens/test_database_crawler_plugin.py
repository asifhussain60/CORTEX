"""
Tests for DatabaseCrawlerPlugin interface.

Authority: Phase 19 Component #4
Rule: CORE-008 (TDD First)
"""

import pytest
from abc import ABC
from typing import Dict, Any, List
from unittest.mock import Mock

from cortex.lens.analyzers.database_crawler_plugin import (
    DatabaseCrawlerPlugin,
    SchemaEntity,
    DatabaseConnection,
)


class TestDatabaseCrawlerPlugin:
    """Test DatabaseCrawlerPlugin interface."""
    
    def test_interface_is_abstract(self):
        """Test that DatabaseCrawlerPlugin cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            DatabaseCrawlerPlugin()
    
    def test_interface_has_required_methods(self):
        """Test that interface defines all required abstract methods."""
        abstract_methods = DatabaseCrawlerPlugin.__abstractmethods__
        
        expected_methods = {
            "connect",
            "disconnect",
            "extract_schema",
            "get_tables",
            "get_columns",
            "get_relationships",
            "test_connection",
        }
        
        assert expected_methods.issubset(abstract_methods)
    
    def test_concrete_implementation_requires_all_methods(self):
        """Test that concrete implementation must implement all abstract methods."""
        # Missing implementations
        class IncompletePlugin(DatabaseCrawlerPlugin):
            def connect(self, connection_string: str) -> DatabaseConnection:
                pass
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompletePlugin()


class TestSchemaEntity:
    """Test SchemaEntity data class."""
    
    def test_schema_entity_initialization(self):
        """Test SchemaEntity can be created with required fields."""
        entity = SchemaEntity(
            name="users",
            entity_type="table",
            schema="public",
            columns=[
                {"name": "id", "type": "integer", "nullable": False},
                {"name": "email", "type": "varchar", "nullable": False},
            ],
            metadata={"row_count": 1500}
        )
        
        assert entity.name == "users"
        assert entity.entity_type == "table"
        assert entity.schema == "public"
        assert len(entity.columns) == 2
        assert entity.metadata["row_count"] == 1500
    
    def test_schema_entity_equality(self):
        """Test SchemaEntity equality comparison."""
        entity1 = SchemaEntity(
            name="users",
            entity_type="table",
            schema="public",
            columns=[],
            metadata={}
        )
        entity2 = SchemaEntity(
            name="users",
            entity_type="table",
            schema="public",
            columns=[],
            metadata={}
        )
        
        assert entity1 == entity2


class TestDatabaseConnection:
    """Test DatabaseConnection data class."""
    
    def test_connection_initialization(self):
        """Test DatabaseConnection can be created."""
        conn = DatabaseConnection(
            connection_id="conn-123",
            database_type="postgresql",
            host="localhost",
            port=5432,
            database="mydb",
            is_connected=True
        )
        
        assert conn.connection_id == "conn-123"
        assert conn.database_type == "postgresql"
        assert conn.host == "localhost"
        assert conn.port == 5432
        assert conn.database == "mydb"
        assert conn.is_connected is True
    
    def test_connection_with_optional_fields(self):
        """Test DatabaseConnection with optional metadata."""
        conn = DatabaseConnection(
            connection_id="conn-456",
            database_type="sqlserver",
            host="sql.example.com",
            port=1433,
            database="production",
            is_connected=False,
            username="admin",
            metadata={"version": "15.0"}
        )
        
        assert conn.username == "admin"
        assert conn.metadata["version"] == "15.0"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
