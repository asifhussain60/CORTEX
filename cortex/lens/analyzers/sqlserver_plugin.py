"""
CORTEX SQL Server DatabaseCrawlerPlugin Implementation

Extracts schema metadata from Microsoft SQL Server databases.

Dependencies:
    - pyodbc: SQL Server connectivity

Authority: Phase 19 Component #5
Rule: CORE-035 (Single Implementation)
"""

from typing import Dict, Any, List, Optional
import re
from dataclasses import dataclass

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

from cortex.lens.analyzers.database_crawler_plugin import (
    DatabaseCrawlerPlugin,
    DatabaseConnection,
    SchemaEntity,
)


class SQLServerPlugin(DatabaseCrawlerPlugin):
    """
    SQL Server schema extraction plugin.
    
    Extracts:
        - Tables with columns, types, constraints
        - Views
        - Stored procedures
        - Functions
        - Foreign key relationships
        - Database metadata (version, collation)
    
    Connection String Format:
        Driver={ODBC Driver 17 for SQL Server};Server=hostname;Database=dbname;Trusted_Connection=yes;
        or
        Driver={ODBC Driver 17 for SQL Server};Server=hostname;Database=dbname;UID=user;PWD=password;
    
    Authority: Phase 19 Component #5
    """
    
    def __init__(self):
        """Initialize SQL Server plugin."""
        # Check pyodbc availability at initialization, not import time
        try:
            import pyodbc  # noqa: F401
        except ImportError:
            raise ImportError(
                "pyodbc is required for SQL Server plugin. "
                "Install with: pip install pyodbc"
            )
        
        self.connection: Optional[Any] = None
        self.connection_info: Optional[DatabaseConnection] = None
    
    def connect(self, connection_string: str) -> DatabaseConnection:
        """
        Establish connection to SQL Server.
        
        Args:
            connection_string: ODBC connection string
            
        Returns:
            DatabaseConnection object
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            import pyodbc
            self.connection = pyodbc.connect(connection_string)
            
            # Parse connection string for metadata
            server = self._parse_connection_param(connection_string, "Server")
            database = self._parse_connection_param(connection_string, "Database")
            uid = self._parse_connection_param(connection_string, "UID")
            
            self.connection_info = DatabaseConnection(
                connection_id=f"sqlserver-{server}-{database}",
                database_type="sqlserver",
                host=server or "localhost",
                port=1433,  # Default SQL Server port
                database=database or "master",
                is_connected=True,
                username=uid,
                metadata={"connection_string": connection_string}
            )
            
            return self.connection_info
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SQL Server: {str(e)}") from e
    
    def disconnect(self) -> None:
        """Close SQL Server connection."""
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
        Extract complete SQL Server schema.
        
        Returns:
            Dict with tables, views, procedures, functions, relationships, metadata
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        schema = {
            "tables": self.get_tables(),
            "views": self._get_views(),
            "procedures": self._get_procedures(),
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
        
        query = """
        SELECT 
            table_schema,
            table_name
        FROM INFORMATION_SCHEMA.TABLES
        WHERE table_type = 'BASE TABLE'
        """
        
        if schema:
            query += " AND table_schema = ?"
        
        cursor = self.connection.cursor()
        if schema:
            cursor.execute(query, schema)
        else:
            cursor.execute(query)
        
        tables = []
        for row in cursor.fetchall():
            table_schema, table_name = row
            
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
        
        query = """
        SELECT 
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            CASE 
                WHEN pk.column_name IS NOT NULL THEN 'PK'
                ELSE NULL
            END as constraint_type
        FROM INFORMATION_SCHEMA.COLUMNS c
        LEFT JOIN (
            SELECT ku.column_name
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                ON tc.constraint_name = ku.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND ku.table_name = ?
        """ + ("AND ku.table_schema = ?" if schema else "") + """
        ) pk ON c.column_name = pk.column_name
        WHERE c.table_name = ?
        """
        
        if schema:
            query += " AND c.table_schema = ?"
        
        cursor = self.connection.cursor()
        if schema:
            cursor.execute(query, table_name, schema, table_name, schema)
        else:
            cursor.execute(query, table_name, table_name)
        
        columns = []
        for row in cursor.fetchall():
            col_name, data_type, is_nullable, default, constraint = row
            
            columns.append({
                "name": col_name,
                "type": data_type,
                "nullable": is_nullable == "YES",
                "default": default,
                "constraints": constraint,
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
        
        query = """
        SELECT 
            fk.name AS constraint_name,
            tp.name AS source_table,
            cp.name AS source_column,
            tr.name AS target_table,
            cr.name AS target_column
        FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc 
            ON fk.object_id = fkc.constraint_object_id
        INNER JOIN sys.tables tp 
            ON fkc.parent_object_id = tp.object_id
        INNER JOIN sys.columns cp 
            ON fkc.parent_object_id = cp.object_id 
            AND fkc.parent_column_id = cp.column_id
        INNER JOIN sys.tables tr 
            ON fkc.referenced_object_id = tr.object_id
        INNER JOIN sys.columns cr 
            ON fkc.referenced_object_id = cr.object_id 
            AND fkc.referenced_column_id = cr.column_id
        """
        
        if schema:
            query += """
            WHERE SCHEMA_NAME(tp.schema_id) = ?
            """
        
        cursor = self.connection.cursor()
        if schema:
            cursor.execute(query, schema)
        else:
            cursor.execute(query)
        
        relationships = []
        for row in cursor.fetchall():
            constraint_name, source_table, source_col, target_table, target_col = row
            
            relationships.append({
                "constraint_name": constraint_name,
                "source_table": source_table,
                "source_column": source_col,
                "target_table": target_table,
                "target_column": target_col,
            })
        
        return relationships
    
    def _get_views(self) -> List[SchemaEntity]:
        """Get all views in database."""
        query = """
        SELECT 
            table_schema,
            table_name
        FROM INFORMATION_SCHEMA.TABLES
        WHERE table_type = 'VIEW'
        """
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        views = []
        for row in cursor.fetchall():
            schema, view_name = row
            
            views.append(SchemaEntity(
                name=view_name,
                entity_type="view",
                schema=schema,
                columns=[],
                metadata={}
            ))
        
        return views
    
    def _get_procedures(self) -> List[SchemaEntity]:
        """Get all stored procedures."""
        query = """
        SELECT 
            SCHEMA_NAME(schema_id) AS schema_name,
            name AS procedure_name
        FROM sys.procedures
        """
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        procedures = []
        for row in cursor.fetchall():
            schema, proc_name = row
            
            procedures.append(SchemaEntity(
                name=proc_name,
                entity_type="procedure",
                schema=schema,
                columns=[],
                metadata={}
            ))
        
        return procedures
    
    def _get_functions(self) -> List[SchemaEntity]:
        """Get all functions."""
        query = """
        SELECT 
            SCHEMA_NAME(schema_id) AS schema_name,
            name AS function_name
        FROM sys.objects
        WHERE type IN ('FN', 'IF', 'TF')
        """
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        functions = []
        for row in cursor.fetchall():
            schema, func_name = row
            
            functions.append(SchemaEntity(
                name=func_name,
                entity_type="function",
                schema=schema,
                columns=[],
                metadata={}
            ))
        
        return functions
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get database metadata."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        
        return {
            "database_version": version,
            "database_type": "sqlserver",
        }
    
    def _parse_connection_param(self, connection_string: str, param: str) -> Optional[str]:
        """Parse parameter from ODBC connection string."""
        pattern = rf"{param}=([^;]+)"
        match = re.search(pattern, connection_string, re.IGNORECASE)
        return match.group(1) if match else None
