"""
Tests for Oracle Database Schema Crawler

Test Strategy:
- Mock oracledb module to avoid requiring actual Oracle instance
- Test metadata extraction logic (tables, columns, indexes, constraints)
- Validate pattern conversion (Oracle schema -> CORTEX knowledge pattern)
- Verify Tier 2 integration (scope='application', namespace handling)
- Test error handling (connection failures, missing metadata)

Run: python -m pytest CORTEX/tests/tier2/test_oracle_crawler.py -v
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import json
import sys

# Mock oracledb module before importing oracle_crawler
sys.modules['oracledb'] = MagicMock()

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tier2.oracle_crawler import (
    OracleCrawler,
    OracleTable,
    OracleColumn,
    OracleIndex,
    OracleConstraint
)


class TestOracleCrawlerInit:
    """Test Oracle crawler initialization."""
    
    def test_initializes_with_connection_params(self):
        """Should store connection parameters."""
        crawler = OracleCrawler(
            user="testuser",
            password="testpass",
            dsn="localhost:1521/TESTDB"
        )
        
        assert crawler.user == "testuser"
        assert crawler.password == "testpass"
        assert crawler.dsn == "localhost:1521/TESTDB"
        assert crawler.connection is None
    
    def test_extracts_namespace_from_dsn(self):
        """Should extract database name from DSN for namespace."""
        crawler = OracleCrawler(
            user="user",
            password="pass",
            dsn="host:1521/MYDB"
        )
        
        assert crawler.namespace == "MYDB_DB"
    
    def test_accepts_custom_namespace(self):
        """Should allow custom namespace override."""
        crawler = OracleCrawler(
            user="user",
            password="pass",
            dsn="host:1521/TESTDB",
            namespace="CUSTOM_NAMESPACE"
        )
        
        assert crawler.namespace == "CUSTOM_NAMESPACE"


class TestOracleConnection:
    """Test Oracle database connection handling."""
    
    @patch('tier2.oracle_crawler.oracledb')
    def test_connects_to_oracle(self, mock_oracledb):
        """Should establish Oracle connection."""
        mock_conn = Mock()
        mock_oracledb.connect.return_value = mock_conn
        
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        crawler.connect()
        
        mock_oracledb.connect.assert_called_once_with(
            user="user",
            password="pass",
            dsn="host:1521/DB"
        )
        assert crawler.connection == mock_conn
    
    @patch('tier2.oracle_crawler.oracledb')
    def test_handles_connection_failure(self, mock_oracledb):
        """Should raise ConnectionError on failure."""
        mock_oracledb.connect.side_effect = Exception("Connection failed")
        
        crawler = OracleCrawler("user", "pass", "invalid:1521/DB")
        
        with pytest.raises(ConnectionError, match="Failed to connect"):
            crawler.connect()
    
    @patch('tier2.oracle_crawler.oracledb')
    def test_disconnects_from_oracle(self, mock_oracledb):
        """Should close Oracle connection."""
        mock_conn = Mock()
        mock_oracledb.connect.return_value = mock_conn
        
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        crawler.connect()
        crawler.disconnect()
        
        mock_conn.close.assert_called_once()
        assert crawler.connection is None


class TestSchemaExtraction:
    """Test Oracle schema metadata extraction."""
    
    @patch('tier2.oracle_crawler.oracledb')
    def test_extracts_tables_for_current_user(self, mock_oracledb):
        """Should extract tables for current user by default."""
        # Mock connection and cursors
        mock_conn = Mock()
        mock_oracledb.connect.return_value = mock_conn
        
        # Mock USER query
        user_cursor = Mock()
        user_cursor.fetchone.return_value = ["TESTUSER"]
        
        # Mock tables query - use fetchall instead of iter
        tables_cursor = Mock()
        tables_cursor.fetchall.return_value = [
            ["TESTUSER", "EMPLOYEES", "USERS", 100]
        ]
        # Also mock __iter__ for the for loop
        tables_cursor.__iter__ = Mock(return_value=iter([
            ["TESTUSER", "EMPLOYEES", "USERS", 100]
        ]))
        
        # Mock subsequent queries (empty for simplicity)
        empty_cursor = Mock()
        empty_cursor.fetchone.return_value = None
        empty_cursor.__iter__ = Mock(return_value=iter([]))
        
        mock_conn.cursor.side_effect = [
            user_cursor,
            tables_cursor,
            empty_cursor,  # comments
            empty_cursor,  # columns
            empty_cursor,  # indexes
            empty_cursor,  # constraints
        ]
        
        crawler = OracleCrawler("testuser", "pass", "host:1521/DB")
        crawler.connect()
        tables = crawler.extract_schema()
        
        assert len(tables) == 1
        assert tables[0].owner == "TESTUSER"
        assert tables[0].table_name == "EMPLOYEES"
    
    @patch('tier2.oracle_crawler.oracledb')
    def test_extracts_columns_with_metadata(self, mock_oracledb):
        """Should extract column metadata including types and comments."""
        mock_conn = Mock()
        mock_oracledb.connect.return_value = mock_conn
        
        # Mock column query
        cursor = Mock()
        cursor.__iter__ = Mock(return_value=iter([
            ["EMPLOYEE_ID", "NUMBER", None, 10, 0, "N", None, "Primary key"],
            ["FIRST_NAME", "VARCHAR2", 50, None, None, "Y", None, "Employee first name"],
        ]))
        mock_conn.cursor.return_value = cursor
        
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        crawler.connection = mock_conn
        
        columns = crawler._get_columns("TESTUSER", "EMPLOYEES")
        
        assert len(columns) == 2
        assert columns[0].column_name == "EMPLOYEE_ID"
        assert columns[0].data_type == "NUMBER"
        assert columns[0].data_precision == 10
        assert columns[0].nullable == "N"
        assert columns[0].comments == "Primary key"
        
        assert columns[1].column_name == "FIRST_NAME"
        assert columns[1].data_type == "VARCHAR2"
        assert columns[1].data_length == 50
        assert columns[1].nullable == "Y"
    
    @patch('tier2.oracle_crawler.oracledb')
    def test_extracts_indexes_with_columns(self, mock_oracledb):
        """Should extract indexes with column information."""
        mock_conn = Mock()
        mock_oracledb.connect.return_value = mock_conn
        
        # Mock index metadata query
        idx_cursor = Mock()
        idx_cursor.__iter__ = Mock(return_value=iter([
            ["PK_EMPLOYEES", "NORMAL", "UNIQUE"],
            ["IDX_LAST_NAME", "NORMAL", "NONUNIQUE"]
        ]))
        
        # Mock index columns queries
        pk_cols_cursor = Mock()
        pk_cols_cursor.__iter__ = Mock(return_value=iter([["EMPLOYEE_ID"]]))
        
        idx_cols_cursor = Mock()
        idx_cols_cursor.__iter__ = Mock(return_value=iter([["LAST_NAME"]]))
        
        mock_conn.cursor.side_effect = [
            idx_cursor,
            pk_cols_cursor,
            idx_cols_cursor
        ]
        
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        crawler.connection = mock_conn
        
        indexes = crawler._get_indexes("TESTUSER", "EMPLOYEES")
        
        assert len(indexes) == 2
        assert indexes[0].index_name == "PK_EMPLOYEES"
        assert indexes[0].uniqueness == "UNIQUE"
        assert indexes[0].columns == ["EMPLOYEE_ID"]
        
        assert indexes[1].index_name == "IDX_LAST_NAME"
        assert indexes[1].uniqueness == "NONUNIQUE"
        assert indexes[1].columns == ["LAST_NAME"]
    
    @patch('tier2.oracle_crawler.oracledb')
    def test_extracts_foreign_key_constraints(self, mock_oracledb):
        """Should extract FK constraints with referenced table info."""
        mock_conn = Mock()
        mock_oracledb.connect.return_value = mock_conn
        
        # Mock constraint metadata
        cons_cursor = Mock()
        cons_cursor.__iter__ = Mock(return_value=iter([
            ["FK_DEPT_ID", "R", "TESTUSER", "PK_DEPARTMENTS"]
        ]))
        
        # Mock constraint columns (for FK columns)
        cons_cols_cursor = Mock()
        cons_cols_cursor.__iter__ = Mock(return_value=iter([["DEPARTMENT_ID"]]))
        
        # Mock ref_cursor - needs to support both fetchone() and __iter__()
        # It's reused for both referenced table query and referenced columns query
        ref_cursor = Mock()
        ref_cursor.fetchone.return_value = ["DEPARTMENTS"]
        ref_cursor.__iter__ = Mock(return_value=iter([["DEPT_ID"]]))
        
        mock_conn.cursor.side_effect = [
            cons_cursor,      # Main constraints query
            cons_cols_cursor, # FK column names
            ref_cursor        # Referenced table AND referenced columns (reused cursor)
        ]
        
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        crawler.connection = mock_conn
        
        constraints = crawler._get_constraints("TESTUSER", "EMPLOYEES")
        
        assert len(constraints) == 1
        fk = constraints[0]
        assert fk.constraint_name == "FK_DEPT_ID"
        assert fk.constraint_type == "R"
        assert fk.columns == ["DEPARTMENT_ID"]
        assert fk.r_owner == "TESTUSER"
        assert fk.r_table == "DEPARTMENTS"
        assert fk.r_columns == ["DEPT_ID"]


class TestPatternConversion:
    """Test conversion of Oracle schema to CORTEX patterns."""
    
    def test_converts_table_to_pattern(self):
        """Should convert OracleTable to knowledge pattern."""
        table = OracleTable(
            owner="TESTUSER",
            table_name="EMPLOYEES",
            tablespace_name="USERS",
            num_rows=150,
            comments="Employee master table",
            columns=[
                OracleColumn(
                    column_name="EMPLOYEE_ID",
                    data_type="NUMBER",
                    data_length=None,
                    data_precision=10,
                    data_scale=0,
                    nullable="N",
                    default_value=None,
                    comments="Primary key"
                )
            ],
            indexes=[
                OracleIndex(
                    index_name="PK_EMPLOYEES",
                    index_type="NORMAL",
                    uniqueness="UNIQUE",
                    columns=["EMPLOYEE_ID"]
                )
            ],
            constraints=[
                OracleConstraint(
                    constraint_name="PK_EMPLOYEES",
                    constraint_type="P",
                    columns=["EMPLOYEE_ID"],
                    r_owner=None,
                    r_table=None,
                    r_columns=None
                )
            ]
        )
        
        crawler = OracleCrawler("user", "pass", "host:1521/TESTDB")
        pattern = crawler.table_to_pattern(table)
        
        assert pattern["title"] == "Oracle: TESTUSER.EMPLOYEES schema"
        assert pattern["scope"] == "application"
        assert pattern["namespaces"] == ["TESTDB_DB"]
        assert "oracle" in pattern["tags"]
        assert "employees" in pattern["tags"]
        assert pattern["confidence"] == 0.95
        
        # Validate content structure
        content = json.loads(pattern["content"])
        assert content["database_type"] == "Oracle"
        assert content["owner"] == "TESTUSER"
        assert content["table_name"] == "EMPLOYEES"
        assert content["row_count"] == 150
        assert len(content["columns"]) == 1
        assert content["columns"][0]["name"] == "EMPLOYEE_ID"
        assert content["columns"][0]["type"] == "NUMBER"
        assert len(content["indexes"]) == 1
        assert content["indexes"][0]["unique"] is True
    
    def test_pattern_includes_foreign_key_references(self):
        """Should include FK reference information in pattern."""
        table = OracleTable(
            owner="TESTUSER",
            table_name="EMPLOYEES",
            tablespace_name="USERS",
            num_rows=100,
            comments=None,
            columns=[],
            indexes=[],
            constraints=[
                OracleConstraint(
                    constraint_name="FK_DEPT",
                    constraint_type="R",
                    columns=["DEPARTMENT_ID"],
                    r_owner="TESTUSER",
                    r_table="DEPARTMENTS",
                    r_columns=["DEPT_ID"]
                )
            ]
        )
        
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        pattern = crawler.table_to_pattern(table)
        
        content = json.loads(pattern["content"])
        fk = content["constraints"][0]
        
        assert fk["type"] == "Foreign Key"
        assert fk["columns"] == ["DEPARTMENT_ID"]
        assert fk["references"]["owner"] == "TESTUSER"
        assert fk["references"]["table"] == "DEPARTMENTS"
        assert fk["references"]["columns"] == ["DEPT_ID"]


class TestTier2Integration:
    """Test integration with CORTEX Tier 2 knowledge graph."""
    
    def test_stores_patterns_in_knowledge_graph(self):
        """Should store patterns with correct scope and namespace."""
        table = OracleTable(
            owner="TESTUSER",
            table_name="EMPLOYEES",
            tablespace_name="USERS",
            num_rows=50,
            comments=None,
            columns=[],
            indexes=[],
            constraints=[]
        )
        
        # Mock knowledge graph
        mock_kg = Mock()
        mock_kg.add_pattern.return_value = 1
        
        crawler = OracleCrawler("user", "pass", "host:1521/ORCL")
        stored = crawler.store_patterns([table], mock_kg)
        
        assert stored == 1
        mock_kg.add_pattern.assert_called_once()
        
        # Verify pattern parameters
        call_args = mock_kg.add_pattern.call_args
        assert call_args.kwargs["title"] == "Oracle: TESTUSER.EMPLOYEES schema"
        assert call_args.kwargs["scope"] == "application"
        assert call_args.kwargs["namespaces"] == ["ORCL_DB"]
        assert call_args.kwargs["confidence"] == 0.95
        assert "oracle_crawler:host:1521/ORCL" in call_args.kwargs["source"]
    
    def test_handles_multiple_tables(self):
        """Should store multiple table schemas as separate patterns."""
        tables = [
            OracleTable("USER", "TABLE1", "USERS", 10, None, [], [], []),
            OracleTable("USER", "TABLE2", "USERS", 20, None, [], [], []),
            OracleTable("USER", "TABLE3", "USERS", 30, None, [], [], [])
        ]
        
        mock_kg = Mock()
        mock_kg.add_pattern.return_value = 1
        
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        stored = crawler.store_patterns(tables, mock_kg)
        
        assert stored == 3
        assert mock_kg.add_pattern.call_count == 3
    
    def test_uses_custom_namespace(self):
        """Should use custom namespace when provided."""
        table = OracleTable("USER", "TABLE1", "USERS", 10, None, [], [], [])
        
        mock_kg = Mock()
        mock_kg.add_pattern.return_value = 1
        
        crawler = OracleCrawler(
            "user", "pass", "host:1521/DB",
            namespace="KSESSIONS_PROD"
        )
        crawler.store_patterns([table], mock_kg)
        
        call_args = mock_kg.add_pattern.call_args
        assert call_args.kwargs["namespaces"] == ["KSESSIONS_PROD"]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_requires_connection_before_extract(self):
        """Should raise error if extracting without connection."""
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        
        with pytest.raises(RuntimeError, match="Not connected"):
            crawler.extract_schema()
    
    @patch('tier2.oracle_crawler.oracledb')
    def test_handles_empty_schema(self, mock_oracledb):
        """Should handle schema with no tables gracefully."""
        mock_conn = Mock()
        mock_oracledb.connect.return_value = mock_conn
        
        # Mock USER query
        user_cursor = Mock()
        user_cursor.fetchone.return_value = ["EMPTYUSER"]
        
        # Mock empty tables query
        tables_cursor = Mock()
        tables_cursor.__iter__ = Mock(return_value=iter([]))
        
        mock_conn.cursor.side_effect = [user_cursor, tables_cursor]
        
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        crawler.connect()
        tables = crawler.extract_schema()
        
        assert len(tables) == 0
    
    def test_handles_storage_failure(self):
        """Should continue storing even if one pattern fails."""
        tables = [
            OracleTable("USER", "TABLE1", "USERS", 10, None, [], [], []),
            OracleTable("USER", "TABLE2", "USERS", 20, None, [], [], []),
        ]
        
        mock_kg = Mock()
        # First succeeds, second fails
        mock_kg.add_pattern.side_effect = [1, None]
        
        crawler = OracleCrawler("user", "pass", "host:1521/DB")
        stored = crawler.store_patterns(tables, mock_kg)
        
        assert stored == 1  # Only one succeeded


# Integration test (requires actual Oracle database - skip by default)
@pytest.mark.skip(reason="Requires Oracle database instance")
class TestOracleIntegration:
    """Integration tests with real Oracle database."""
    
    def test_real_oracle_connection(self):
        """Test with actual Oracle instance."""
        crawler = OracleCrawler(
            user="testuser",
            password="testpass",
            dsn="localhost:1521/ORCL"
        )
        
        try:
            crawler.connect()
            tables = crawler.extract_schema()
            assert len(tables) >= 0
        finally:
            crawler.disconnect()

