"""
Oracle Database Schema Crawler for CORTEX Knowledge Extraction

This crawler connects to Oracle databases, extracts schema metadata (tables, columns,
relationships, indexes), and stores them as knowledge patterns in Tier 2 knowledge graph.

CORTEX Tier 2 Integration:
- Scope: 'application' (database schemas are application-specific)
- Namespace: Database name (e.g., ['KSESSIONS_DB'])
- Pattern Title: "Oracle: {table_name} schema"
- Confidence: 0.95 (high confidence from direct schema introspection)

Usage:
    crawler = OracleCrawler(connection_string="user/pass@host:port/service")
    patterns = crawler.extract_schema()
    crawler.store_patterns(patterns, knowledge_graph)
"""

import oracledb
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import sys

# Add CORTEX to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from tier2.knowledge_graph import KnowledgeGraph


@dataclass
class OracleTable:
    """Represents an Oracle table with metadata."""
    owner: str
    table_name: str
    tablespace_name: Optional[str]
    num_rows: Optional[int]
    comments: Optional[str]
    columns: List['OracleColumn']
    indexes: List['OracleIndex']
    constraints: List['OracleConstraint']


@dataclass
class OracleColumn:
    """Represents a table column."""
    column_name: str
    data_type: str
    data_length: Optional[int]
    data_precision: Optional[int]
    data_scale: Optional[int]
    nullable: str  # 'Y' or 'N'
    default_value: Optional[str]
    comments: Optional[str]


@dataclass
class OracleIndex:
    """Represents a table index."""
    index_name: str
    index_type: str  # NORMAL, BITMAP, FUNCTION-BASED, etc.
    uniqueness: str  # UNIQUE or NONUNIQUE
    columns: List[str]


@dataclass
class OracleConstraint:
    """Represents a table constraint."""
    constraint_name: str
    constraint_type: str  # P=Primary Key, R=Foreign Key, U=Unique, C=Check
    columns: List[str]
    r_owner: Optional[str]  # Referenced table owner (for FK)
    r_table: Optional[str]  # Referenced table (for FK)
    r_columns: Optional[List[str]]  # Referenced columns (for FK)


class OracleCrawler:
    """
    Extracts schema metadata from Oracle databases.
    
    Architecture:
    - Uses oracledb (python-oracledb) for connectivity
    - Queries data dictionary views (ALL_TABLES, ALL_TAB_COLUMNS, etc.)
    - Converts metadata to CORTEX knowledge patterns
    - Stores in Tier 2 with scope='application', namespace=[db_name]
    """
    
    def __init__(
        self,
        user: str,
        password: str,
        dsn: str,
        namespace: Optional[str] = None
    ):
        """
        Initialize Oracle crawler.
        
        Args:
            user: Oracle database user
            password: User password
            dsn: Data Source Name (host:port/service_name)
            namespace: Override namespace (default: extracts from DSN)
        """
        self.user = user
        self.password = password
        self.dsn = dsn
        self.namespace = namespace or self._extract_namespace_from_dsn(dsn)
        self.connection: Optional[oracledb.Connection] = None
    
    def _extract_namespace_from_dsn(self, dsn: str) -> str:
        """Extract database name from DSN for namespace."""
        # DSN format: host:port/service_name
        if '/' in dsn:
            service_name = dsn.split('/')[-1]
            return f"{service_name.upper()}_DB"
        return "ORACLE_DB"
    
    def connect(self) -> None:
        """Establish connection to Oracle database."""
        try:
            self.connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            )
            print(f"✅ Connected to Oracle: {self.dsn}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Oracle: {e}")
    
    def disconnect(self) -> None:
        """Close Oracle connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print(f"✅ Disconnected from Oracle")
    
    def extract_schema(
        self,
        owners: Optional[List[str]] = None,
        include_system: bool = False
    ) -> List[OracleTable]:
        """
        Extract schema metadata from Oracle.
        
        Args:
            owners: List of schema owners to extract (default: current user)
            include_system: Include Oracle system schemas (SYS, SYSTEM, etc.)
        
        Returns:
            List of OracleTable objects with full metadata
        """
        if not self.connection:
            raise RuntimeError("Not connected to Oracle. Call connect() first.")
        
        # Default to current user if no owners specified
        if owners is None:
            cursor = self.connection.cursor()
            cursor.execute("SELECT USER FROM DUAL")
            current_user = cursor.fetchone()[0]
            owners = [current_user]
            cursor.close()
        
        tables = []
        for owner in owners:
            tables.extend(self._extract_tables_for_owner(owner, include_system))
        
        return tables
    
    def _extract_tables_for_owner(
        self,
        owner: str,
        include_system: bool
    ) -> List[OracleTable]:
        """Extract all tables for a specific schema owner."""
        cursor = self.connection.cursor()
        
        # Query: Get all tables for owner
        query = """
            SELECT 
                owner,
                table_name,
                tablespace_name,
                num_rows
            FROM all_tables
            WHERE owner = :owner
        """
        
        # Exclude system schemas unless requested
        if not include_system:
            query += """
                AND owner NOT IN (
                    'SYS', 'SYSTEM', 'OUTLN', 'DBSNMP', 'APPQOSSYS',
                    'WMSYS', 'EXFSYS', 'CTXSYS', 'XDB', 'ANONYMOUS',
                    'ORACLE_OCM', 'APEX_PUBLIC_USER', 'FLOWS_FILES',
                    'APEX_040000', 'APEX_040200'
                )
            """
        
        cursor.execute(query, owner=owner.upper())
        
        tables = []
        for row in cursor:
            table = OracleTable(
                owner=row[0],
                table_name=row[1],
                tablespace_name=row[2],
                num_rows=row[3],
                comments=self._get_table_comments(row[0], row[1]),
                columns=self._get_columns(row[0], row[1]),
                indexes=self._get_indexes(row[0], row[1]),
                constraints=self._get_constraints(row[0], row[1])
            )
            tables.append(table)
        
        cursor.close()
        return tables
    
    def _get_table_comments(self, owner: str, table_name: str) -> Optional[str]:
        """Get table comments from data dictionary."""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT comments 
            FROM all_tab_comments 
            WHERE owner = :owner AND table_name = :table_name
            """,
            owner=owner,
            table_name=table_name
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result and result[0] else None
    
    def _get_columns(self, owner: str, table_name: str) -> List[OracleColumn]:
        """Get all columns for a table."""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT 
                c.column_name,
                c.data_type,
                c.data_length,
                c.data_precision,
                c.data_scale,
                c.nullable,
                c.data_default,
                cm.comments
            FROM all_tab_columns c
            LEFT JOIN all_col_comments cm
                ON c.owner = cm.owner 
                AND c.table_name = cm.table_name 
                AND c.column_name = cm.column_name
            WHERE c.owner = :owner 
                AND c.table_name = :table_name
            ORDER BY c.column_id
            """,
            owner=owner,
            table_name=table_name
        )
        
        columns = []
        for row in cursor:
            col = OracleColumn(
                column_name=row[0],
                data_type=row[1],
                data_length=row[2],
                data_precision=row[3],
                data_scale=row[4],
                nullable=row[5],
                default_value=row[6],
                comments=row[7]
            )
            columns.append(col)
        
        cursor.close()
        return columns
    
    def _get_indexes(self, owner: str, table_name: str) -> List[OracleIndex]:
        """Get all indexes for a table."""
        cursor = self.connection.cursor()
        
        # Get index metadata
        cursor.execute(
            """
            SELECT 
                index_name,
                index_type,
                uniqueness
            FROM all_indexes
            WHERE table_owner = :owner 
                AND table_name = :table_name
            """,
            owner=owner,
            table_name=table_name
        )
        
        indexes = []
        for row in cursor:
            index_name = row[0]
            
            # Get columns for this index
            col_cursor = self.connection.cursor()
            col_cursor.execute(
                """
                SELECT column_name
                FROM all_ind_columns
                WHERE index_owner = :owner
                    AND index_name = :index_name
                ORDER BY column_position
                """,
                owner=owner,
                index_name=index_name
            )
            columns = [col[0] for col in col_cursor]
            col_cursor.close()
            
            idx = OracleIndex(
                index_name=index_name,
                index_type=row[1],
                uniqueness=row[2],
                columns=columns
            )
            indexes.append(idx)
        
        cursor.close()
        return indexes
    
    def _get_constraints(self, owner: str, table_name: str) -> List[OracleConstraint]:
        """Get all constraints for a table."""
        cursor = self.connection.cursor()
        
        # Get constraint metadata
        cursor.execute(
            """
            SELECT 
                constraint_name,
                constraint_type,
                r_owner,
                r_constraint_name
            FROM all_constraints
            WHERE owner = :owner 
                AND table_name = :table_name
                AND constraint_type IN ('P', 'R', 'U', 'C')
            """,
            owner=owner,
            table_name=table_name
        )
        
        constraints = []
        for row in cursor:
            constraint_name = row[0]
            constraint_type = row[1]
            r_owner = row[2]
            r_constraint_name = row[3]
            
            # Get columns for this constraint
            col_cursor = self.connection.cursor()
            col_cursor.execute(
                """
                SELECT column_name
                FROM all_cons_columns
                WHERE owner = :owner
                    AND constraint_name = :constraint_name
                ORDER BY position
                """,
                owner=owner,
                constraint_name=constraint_name
            )
            columns = [col[0] for col in col_cursor]
            col_cursor.close()
            
            # For foreign keys, get referenced table/columns
            r_table = None
            r_columns = None
            if constraint_type == 'R' and r_constraint_name:
                ref_cursor = self.connection.cursor()
                
                # Get referenced table
                ref_cursor.execute(
                    """
                    SELECT table_name
                    FROM all_constraints
                    WHERE owner = :owner
                        AND constraint_name = :constraint_name
                    """,
                    owner=r_owner,
                    constraint_name=r_constraint_name
                )
                r_table_row = ref_cursor.fetchone()
                r_table = r_table_row[0] if r_table_row else None
                
                # Get referenced columns
                ref_cursor.execute(
                    """
                    SELECT column_name
                    FROM all_cons_columns
                    WHERE owner = :owner
                        AND constraint_name = :constraint_name
                    ORDER BY position
                    """,
                    owner=r_owner,
                    constraint_name=r_constraint_name
                )
                r_columns = [col[0] for col in ref_cursor]
                ref_cursor.close()
            
            cons = OracleConstraint(
                constraint_name=constraint_name,
                constraint_type=constraint_type,
                columns=columns,
                r_owner=r_owner,
                r_table=r_table,
                r_columns=r_columns
            )
            constraints.append(cons)
        
        cursor.close()
        return constraints
    
    def table_to_pattern(self, table: OracleTable) -> Dict[str, Any]:
        """
        Convert OracleTable to CORTEX knowledge pattern.
        
        Pattern Structure:
        - Title: "Oracle: {owner}.{table_name} schema"
        - Content: Detailed JSON with columns, indexes, constraints
        - Scope: 'application' (database-specific)
        - Namespace: [database_name]
        - Tags: ['oracle', 'database', 'schema', owner, table_name]
        - Confidence: 0.95 (high - direct introspection)
        """
        # Build detailed content
        content = {
            "database_type": "Oracle",
            "owner": table.owner,
            "table_name": table.table_name,
            "tablespace": table.tablespace_name,
            "row_count": table.num_rows,
            "comments": table.comments,
            "columns": [
                {
                    "name": col.column_name,
                    "type": col.data_type,
                    "length": col.data_length,
                    "precision": col.data_precision,
                    "scale": col.data_scale,
                    "nullable": col.nullable == 'Y',
                    "default": col.default_value,
                    "comments": col.comments
                }
                for col in table.columns
            ],
            "indexes": [
                {
                    "name": idx.index_name,
                    "type": idx.index_type,
                    "unique": idx.uniqueness == 'UNIQUE',
                    "columns": idx.columns
                }
                for idx in table.indexes
            ],
            "constraints": [
                {
                    "name": cons.constraint_name,
                    "type": {
                        'P': 'Primary Key',
                        'R': 'Foreign Key',
                        'U': 'Unique',
                        'C': 'Check'
                    }.get(cons.constraint_type, cons.constraint_type),
                    "columns": cons.columns,
                    "references": {
                        "owner": cons.r_owner,
                        "table": cons.r_table,
                        "columns": cons.r_columns
                    } if cons.constraint_type == 'R' else None
                }
                for cons in table.constraints
            ]
        }
        
        return {
            "title": f"Oracle: {table.owner}.{table.table_name} schema",
            "content": json.dumps(content, indent=2),
            "scope": "application",
            "namespaces": [self.namespace],
            "tags": [
                "oracle",
                "database",
                "schema",
                table.owner.lower(),
                table.table_name.lower()
            ],
            "confidence": 0.95,
            "source": f"oracle_crawler:{self.dsn}"
        }
    
    def store_patterns(
        self,
        tables: List[OracleTable],
        knowledge_graph: KnowledgeGraph
    ) -> int:
        """
        Store extracted schema as knowledge patterns in Tier 2.
        
        Args:
            tables: List of OracleTable objects from extract_schema()
            knowledge_graph: KnowledgeGraph instance for storage
        
        Returns:
            Number of patterns stored
        """
        stored = 0
        for table in tables:
            pattern = self.table_to_pattern(table)
            
            pattern_id = knowledge_graph.add_pattern(
                title=pattern["title"],
                content=pattern["content"],
                scope=pattern["scope"],
                namespaces=pattern["namespaces"],
                tags=pattern["tags"],
                confidence=pattern["confidence"],
                source=pattern["source"]
            )
            
            if pattern_id:
                stored += 1
                print(f"✅ Stored: {pattern['title']}")
        
        return stored


# Example usage
if __name__ == "__main__":
    """
    Example: Extract schema from Oracle and store in CORTEX Tier 2.
    
    Usage:
        python oracle_crawler.py <user> <password> <dsn>
    
    Example:
        python oracle_crawler.py myuser mypass localhost:1521/ORCL
    """
    if len(sys.argv) < 4:
        print("Usage: python oracle_crawler.py <user> <password> <dsn>")
        print("Example: python oracle_crawler.py scott tiger localhost:1521/ORCL")
        sys.exit(1)
    
    user = sys.argv[1]
    password = sys.argv[2]
    dsn = sys.argv[3]
    
    # Initialize crawler
    crawler = OracleCrawler(user=user, password=password, dsn=dsn)
    
    try:
        # Connect to Oracle
        crawler.connect()
        
        # Extract schema (current user only, exclude system schemas)
        print(f"\n📊 Extracting schema for {user}...")
        tables = crawler.extract_schema(include_system=False)
        print(f"✅ Found {len(tables)} tables")
        
        # Initialize knowledge graph
        brain_dir = Path(__file__).parent.parent.parent.parent / "cortex-brain"
        kg = KnowledgeGraph(brain_dir=brain_dir)
        
        # Store patterns
        print(f"\n💾 Storing schema patterns in Tier 2...")
        stored = crawler.store_patterns(tables, kg)
        print(f"\n✅ COMPLETE: Stored {stored}/{len(tables)} schema patterns")
        print(f"   Namespace: {crawler.namespace}")
        print(f"   Scope: application")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        # Always disconnect
        crawler.disconnect()
