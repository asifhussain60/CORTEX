"""
CORTEX PostgreSQL DatabaseCrawlerPlugin Implementation

Extracts schema metadata from PostgreSQL databases.

Dependencies:
    - psycopg2: PostgreSQL connectivity

Authority: Phase 19 Component #6
Rule: CORE-035 (Single Implementation)
"""

from typing import Dict, Any, List, Optional
import re
from urllib.parse import urlparse

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

from cortex.lens.analyzers.database_crawler_plugin import (
    DatabaseCrawlerPlugin,
    DatabaseConnection,
    SchemaEntity,
)


class PostgreSQLPlugin(DatabaseCrawlerPlugin):
    """
    PostgreSQL schema extraction plugin.
    
    Extracts:
        - Tables with columns, types, constraints
        - Views
        - Functions
        - Foreign key relationships
        - Database metadata (version, encoding)
    
    Connection String Format:
        postgresql://user:password@hostname:port/database
        or
        postgres://user:password@hostname:port/database
    
    Authority: Phase 19 Component #6
    """
    
    def __init__(self):
        """Initialize PostgreSQL plugin."""
        # Check psycopg2 availability at initialization
        try:
            import psycopg2  # noqa: F401
        except ImportError:
            raise ImportError(
                "psycopg2 is required for PostgreSQL plugin. "
                "Install with: pip install psycopg2-binary"
            )
        
        self.connection: Optional[Any] = None
        self.connection_info: Optional[DatabaseConnection] = None
    
    def connect(self, connection_string: str) -> DatabaseConnection:
        """
        Establish connection to PostgreSQL.
        
        Args:
            connection_string: PostgreSQL connection URL
            
        Returns:
            DatabaseConnection object
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            import psycopg2
            self.connection = psycopg2.connect(connection_string)
            
            # Parse connection string for metadata
            parsed = urlparse(connection_string)
            
            self.connection_info = DatabaseConnection(
                connection_id=f"postgresql-{parsed.hostname}-{parsed.path[1:]}",
                database_type="postgresql",
                host=parsed.hostname or "localhost",
                port=parsed.port or 5432,
                database=parsed.path[1:] if parsed.path else "postgres",
                is_connected=True,
                username=parsed.username,
                metadata={"connection_string": connection_string}
            )
            
            return self.connection_info
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}") from e
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                raise RuntimeError(f"Failed to disconnect: {str(e)}") from e
            finally:
                self.connection = None
                self.connection_info = None
    
    def test_connection(self) -> bool:
        """Test if connection is active."""
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception:
            return False
    
    def extract_schema(self) -> Dict[str, Any]:
        """
        Extract complete PostgreSQL schema.
        
        Returns:
            Dict with tables, views, functions, relationships, metadata
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        schema = {
            "tables": self.get_tables(),
            "views": self._get_views(),
            "functions": self._get_functions(),
            "relationships": self.get_relationships(),
            "metadata": self._get_metadata(),
        }
        
        return schema
    
    def get_tables(self, schema: Optional[str] = None) -> List[SchemaEntity]:
        """
        Get all tables in database or specific schema.
        
        Args:
            schema: Optional schema filter
            
        Returns:
            List of SchemaEntity objects
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        import psycopg2.extras
        
        query = """
        SELECT 
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
        AND table_schema NOT IN ('pg_catalog', 'information_schema')
        """
        
        if schema:
            query += " AND table_schema = %s"
        
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if schema:
            cursor.execute(query, (schema,))
        else:
            cursor.execute(query)
        
        tables = []
        for row in cursor.fetchall():
            table_schema = row["table_schema"]
            table_name = row["table_name"]
            
            # Get columns for this table
            columns = self.get_columns(table_name, schema=table_schema)
            
            tables.append(SchemaEntity(
                name=table_name,
                entity_type="table",
                schema=table_schema,
                columns=columns,
                metadata={}
            ))
        
        return tables
    
    def get_columns(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get column definitions for a table.
        
        Args:
            table_name: Table name
            schema: Optional schema name
            
        Returns:
            List of column definitions
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        import psycopg2.extras
        
        query = """
        SELECT 
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            tc.constraint_type
        FROM information_schema.columns c
        LEFT JOIN information_schema.key_column_usage kcu
            ON c.table_schema = kcu.table_schema
            AND c.table_name = kcu.table_name
            AND c.column_name = kcu.column_name
        LEFT JOIN information_schema.table_constraints tc
            ON kcu.constraint_name = tc.constraint_name
            AND tc.constraint_type = 'PRIMARY KEY'
        WHERE c.table_name = %s
        """
        
        params = [table_name]
        if schema:
            query += " AND c.table_schema = %s"
            params.append(schema)
        
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, tuple(params))
        
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row["column_name"],
                "type": row["data_type"],
                "nullable": row["is_nullable"] == "YES",
                "default": row["column_default"],
                "constraints": row["constraint_type"],
            })
        
        return columns
    
    def get_relationships(self, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get foreign key relationships.
        
        Args:
            schema: Optional schema filter
            
        Returns:
            List of relationship definitions
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        import psycopg2.extras
        
        query = """
        SELECT
            tc.constraint_name,
            kcu.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        """
        
        if schema:
            query += " AND tc.table_schema = %s"
        
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if schema:
            cursor.execute(query, (schema,))
        else:
            cursor.execute(query)
        
        relationships = []
        for row in cursor.fetchall():
            relationships.append({
                "constraint_name": row["constraint_name"],
                "source_table": row["table_name"],
                "source_column": row["column_name"],
                "target_table": row["foreign_table_name"],
                "target_column": row["foreign_column_name"],
            })
        
        return relationships
    
    def _get_views(self) -> List[SchemaEntity]:
        """Get all views in database."""
        import psycopg2.extras
        
        query = """
        SELECT 
            table_schema,
            table_name
        FROM information_schema.views
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """
        
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query)
        
        views = []
        for row in cursor.fetchall():
            views.append(SchemaEntity(
                name=row["table_name"],
                entity_type="view",
                schema=row["table_schema"],
                columns=[],
                metadata={}
            ))
        
        return views
    
    def _get_functions(self) -> List[SchemaEntity]:
        """Get all functions."""
        import psycopg2.extras
        
        query = """
        SELECT 
            n.nspname AS schema_name,
            p.proname AS function_name
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
        """
        
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query)
        
        functions = []
        for row in cursor.fetchall():
            functions.append(SchemaEntity(
                name=row["function_name"],
                entity_type="function",
                schema=row["schema_name"],
                columns=[],
                metadata={}
            ))
        
        return functions
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get database metadata."""
        import psycopg2.extras
        
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT version()")
        row = cursor.fetchone()
        version = row["version"] if row else "Unknown"
        
        return {
            "database_version": version,
            "database_type": "postgresql",
        }
