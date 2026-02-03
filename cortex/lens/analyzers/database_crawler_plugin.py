"""
CORTEX DatabaseCrawlerPlugin Interface

Abstract base for database schema extraction plugins.
Each database vendor (SQL Server, PostgreSQL, MySQL, etc.) implements this interface.

Authority: Phase 19 Component #4
Rule: CORE-035 (Single Implementation)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class SchemaEntity:
    """
    Represents a database entity (table, view, stored procedure, etc.).
    
    Attributes:
        name: Entity name
        entity_type: Type (table, view, procedure, function)
        schema: Schema/namespace
        columns: Column definitions
        metadata: Additional metadata (row_count, indexes, etc.)
    """
    name: str
    entity_type: str
    schema: str
    columns: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __eq__(self, other: Any) -> bool:
        """Equality based on name, type, and schema."""
        if not isinstance(other, SchemaEntity):
            return False
        return (
            self.name == other.name
            and self.entity_type == other.entity_type
            and self.schema == other.schema
        )


@dataclass
class DatabaseConnection:
    """
    Represents an active database connection.
    
    Attributes:
        connection_id: Unique connection identifier
        database_type: Database type (postgresql, sqlserver, mysql)
        host: Database host
        port: Database port
        database: Database name
        is_connected: Connection status
        username: Optional username
        metadata: Optional connection metadata
    """
    connection_id: str
    database_type: str
    host: str
    port: int
    database: str
    is_connected: bool
    username: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DatabaseCrawlerPlugin(ABC):
    """
    Abstract base for database schema extraction plugins.
    
    Each plugin implements vendor-specific schema extraction logic.
    Used by RepositoryOnboardingOrchestrator for database intelligence.
    
    Lifecycle:
        1. connect() → Establish connection
        2. test_connection() → Verify connection
        3. extract_schema() → Full schema extraction
        4. get_tables() / get_columns() / get_relationships() → Targeted queries
        5. disconnect() → Clean up
    
    Authority: Phase 19 Component #4
    """
    
    @abstractmethod
    def connect(self, connection_string: str) -> DatabaseConnection:
        """
        Establish connection to database.
        
        Args:
            connection_string: Database connection string
            
        Returns:
            DatabaseConnection object with connection details
            
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Close database connection and clean up resources.
        
        Raises:
            RuntimeError: If disconnect fails
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if connection is active and responsive.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_schema(self) -> Dict[str, Any]:
        """
        Extract complete database schema.
        
        Returns:
            Dict with:
                - tables: List[SchemaEntity] (tables)
                - views: List[SchemaEntity] (views)
                - procedures: List[SchemaEntity] (stored procedures)
                - functions: List[SchemaEntity] (functions)
                - relationships: List[Dict] (foreign keys, etc.)
                - metadata: Dict (database version, collation, etc.)
        """
        pass
    
    @abstractmethod
    def get_tables(self, schema: Optional[str] = None) -> List[SchemaEntity]:
        """
        Get all tables in database or specific schema.
        
        Args:
            schema: Optional schema filter
            
        Returns:
            List of SchemaEntity objects representing tables
        """
        pass
    
    @abstractmethod
    def get_columns(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get column definitions for a table.
        
        Args:
            table_name: Table name
            schema: Optional schema name
            
        Returns:
            List of column definitions with:
                - name: Column name
                - type: Data type
                - nullable: Is nullable
                - default: Default value
                - constraints: Constraints (PK, FK, etc.)
        """
        pass
    
    @abstractmethod
    def get_relationships(self, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get foreign key relationships between tables.
        
        Args:
            schema: Optional schema filter
            
        Returns:
            List of relationship definitions with:
                - source_table: Source table
                - source_column: Source column
                - target_table: Target table
                - target_column: Target column
                - constraint_name: FK constraint name
        """
        pass


def get_database_crawler_plugin(database_type: str) -> Optional[DatabaseCrawlerPlugin]:
    """
    Factory function to get plugin for database type.
    
    Args:
        database_type: Database type (sqlserver, postgresql, mysql)
        
    Returns:
        Plugin instance or None if not supported
        
    Example:
        >>> plugin = get_database_crawler_plugin("postgresql")
        >>> conn = plugin.connect("postgresql://localhost:5432/mydb")
        >>> schema = plugin.extract_schema()
    """
    # Will be populated in Phase 19 Components #5-6
    plugins = {}
    
    try:
        from cortex.lens.analyzers.sqlserver_plugin import SQLServerPlugin
        plugins["sqlserver"] = SQLServerPlugin
        plugins["mssql"] = SQLServerPlugin
    except ImportError:
        pass  # Plugin not yet implemented
    
    try:
        from cortex.lens.analyzers.postgresql_plugin import PostgreSQLPlugin
        plugins["postgresql"] = PostgreSQLPlugin
        plugins["postgres"] = PostgreSQLPlugin
    except ImportError:
        pass  # Plugin not yet implemented
    
    plugin_class = plugins.get(database_type.lower())
    if plugin_class:
        return plugin_class()
    return None
