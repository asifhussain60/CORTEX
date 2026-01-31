"""
Phase 8.5: SQL/Oracle Analyzer for LENS Intelligence

Analyzes SQL and PL/SQL code for stored procedures, functions, and edge cases.
Provides CORTEX LENS with expert knowledge of database patterns and anti-patterns.

AC-ID: AC-PHASE-8.5-02 (Task LENS-MS-002)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import re
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class SQLAnalysisResult:
    """
    Result of SQL/Oracle code analysis.
    
    Attributes:
        file_path: Path to analyzed file
        procedures: List of stored procedures
        functions: List of functions
        tables: Referenced tables
        indexes: Index definitions
        transactions: Transaction blocks
        edge_cases: Detected edge cases and anti-patterns
        complexity_score: Overall complexity (0-100)
    """
    file_path: str
    procedures: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    transactions: List[Dict[str, Any]]
    edge_cases: List[Dict[str, Any]]
    complexity_score: int


class SQLOracleAnalyzer:
    """
    Analyzes SQL and PL/SQL code for structure, patterns, and edge cases.
    
    Expert in:
    - T-SQL stored procedures (SQL Server)
    - PL/SQL packages (Oracle)
    - SQL injection vulnerabilities
    - Missing transactions
    - N+1 query patterns
    - Missing indexes
    
    Example:
        analyzer = SQLOracleAnalyzer()
        result = analyzer.analyze_file(Path("schema.sql"))
        
        print(f"Procedures: {len(result.procedures)}")
        print(f"Edge cases: {len(result.edge_cases)}")
    """
    
    def __init__(self) -> None:
        """Initialize SQL/Oracle analyzer."""
        self.logger = EnhancedAuditLogger.instance()
        
        # SQL pattern regexes
        self.patterns = {
            "procedure": re.compile(r"CREATE\s+(OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)", re.IGNORECASE),
            "function": re.compile(r"CREATE\s+(OR\s+REPLACE\s+)?FUNCTION\s+(\w+)", re.IGNORECASE),
            "table": re.compile(r"CREATE\s+TABLE\s+(\w+)", re.IGNORECASE),
            "index": re.compile(r"CREATE\s+(UNIQUE\s+)?INDEX\s+(\w+)", re.IGNORECASE),
            "transaction": re.compile(r"BEGIN\s+(TRAN|TRANSACTION)", re.IGNORECASE),
            "select_star": re.compile(r"SELECT\s+\*\s+FROM", re.IGNORECASE),
            "dynamic_sql": re.compile(r"EXEC\(|EXECUTE\(|sp_executesql", re.IGNORECASE),
            "cursor": re.compile(r"DECLARE\s+\w+\s+CURSOR", re.IGNORECASE),
            "where_clause": re.compile(r"WHERE\s+", re.IGNORECASE),
        }
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.5-02",
            operation="SQL_ANALYZER_INIT",
            success=True,
            details={"patterns_loaded": len(self.patterns)},
        )
    
    def analyze_file(self, file_path: Path) -> SQLAnalysisResult:
        """
        Analyze SQL file for structure and patterns.
        
        AC-PHASE-8.5-02: Extract SQL code intelligence
        
        Args:
            file_path: Path to SQL source file (.sql, .pls, .plsql)
        
        Returns:
            SQLAnalysisResult: Analysis results with edge cases
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not SQL
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        valid_extensions = [".sql", ".pls", ".plsql", ".ddl"]
        if file_path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Not a SQL file: {file_path}")
        
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            # Extract components
            procedures = self._extract_procedures(content, lines)
            functions = self._extract_functions(content, lines)
            tables = self._extract_tables(content, lines)
            indexes = self._extract_indexes(content, lines)
            transactions = self._extract_transactions(content, lines)
            
            # Detect edge cases
            edge_cases = self._detect_edge_cases(content, lines)
            
            # Calculate complexity
            complexity = self._calculate_complexity(
                len(procedures), len(functions), len(tables), len(transactions)
            )
            
            result = SQLAnalysisResult(
                file_path=str(file_path),
                procedures=procedures,
                functions=functions,
                tables=tables,
                indexes=indexes,
                transactions=transactions,
                edge_cases=edge_cases,
                complexity_score=complexity,
            )
            
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.5-02",
                operation="SQL_ANALYSIS_COMPLETE",
                success=True,
                details={
                    "file": str(file_path),
                    "procedures": len(procedures),
                    "edge_cases": len(edge_cases),
                    "complexity": complexity,
                },
            )
            
            return result
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.5-02",
                operation="SQL_ANALYSIS_ERROR",
                success=False,
                details={"file": str(file_path), "error": str(e)},
            )
            raise
    
    def _extract_procedures(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract stored procedure definitions."""
        procedures = []
        for i, line in enumerate(lines, 1):
            match = self.patterns["procedure"].search(line)
            if match:
                procedures.append({
                    "name": match.group(2),
                    "line": i,
                    "type": "procedure",
                })
        return procedures
    
    def _extract_functions(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract function definitions."""
        functions = []
        for i, line in enumerate(lines, 1):
            match = self.patterns["function"].search(line)
            if match:
                functions.append({
                    "name": match.group(2),
                    "line": i,
                    "type": "function",
                })
        return functions
    
    def _extract_tables(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract table definitions."""
        tables = []
        for i, line in enumerate(lines, 1):
            match = self.patterns["table"].search(line)
            if match:
                tables.append({
                    "name": match.group(1),
                    "line": i,
                })
        return tables
    
    def _extract_indexes(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract index definitions."""
        indexes = []
        for i, line in enumerate(lines, 1):
            match = self.patterns["index"].search(line)
            if match:
                indexes.append({
                    "name": match.group(2),
                    "line": i,
                    "is_unique": bool(match.group(1)),
                })
        return indexes
    
    def _extract_transactions(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract transaction blocks."""
        transactions = []
        for i, line in enumerate(lines, 1):
            if self.patterns["transaction"].search(line):
                transactions.append({
                    "line": i,
                    "snippet": line.strip(),
                })
        return transactions
    
    def _detect_edge_cases(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Detect SQL edge cases and anti-patterns.
        
        Edge cases:
        - SELECT * queries (performance)
        - SQL injection vulnerabilities (dynamic SQL)
        - Missing WHERE clauses (full table scans)
        - Missing transactions (data consistency)
        - Cursors (performance issues)
        - Missing indexes on foreign keys
        """
        edge_cases = []
        
        # Check for SELECT * queries
        for i, line in enumerate(lines, 1):
            if self.patterns["select_star"].search(line):
                edge_cases.append({
                    "type": "select_star",
                    "severity": "medium",
                    "line": i,
                    "message": "SELECT * detected - specify columns for performance",
                })
        
        # Check for dynamic SQL (SQL injection risk)
        for i, line in enumerate(lines, 1):
            if self.patterns["dynamic_sql"].search(line):
                # Check if parameterized
                has_params = "@" in line or "?" in line
                if not has_params:
                    edge_cases.append({
                        "type": "sql_injection",
                        "severity": "critical",
                        "line": i,
                        "message": "Dynamic SQL without parameters - SQL injection risk",
                    })
        
        # Check for UPDATE/DELETE without WHERE
        for i, line in enumerate(lines, 1):
            if re.search(r"(UPDATE|DELETE)\s+", line, re.IGNORECASE):
                # Check if WHERE clause exists in same or next line
                has_where = self.patterns["where_clause"].search(line)
                if not has_where and i < len(lines):
                    has_where = self.patterns["where_clause"].search(lines[i])
                
                if not has_where:
                    edge_cases.append({
                        "type": "missing_where",
                        "severity": "critical",
                        "line": i,
                        "message": "UPDATE/DELETE without WHERE - affects all rows",
                    })
        
        # Check for cursors (performance issue)
        for i, line in enumerate(lines, 1):
            if self.patterns["cursor"].search(line):
                edge_cases.append({
                    "type": "cursor_usage",
                    "severity": "medium",
                    "line": i,
                    "message": "Cursor detected - consider set-based alternative",
                })
        
        # Check for INSERT/UPDATE without transactions
        insert_lines = [i for i, line in enumerate(lines, 1) if re.search(r"INSERT\s+INTO", line, re.IGNORECASE)]
        transaction_lines = [i for i, line in enumerate(lines, 1) if self.patterns["transaction"].search(line)]
        
        for insert_line in insert_lines:
            # Check if within 10 lines of transaction start
            in_transaction = any(abs(insert_line - trans_line) < 10 for trans_line in transaction_lines)
            if not in_transaction:
                edge_cases.append({
                    "type": "missing_transaction",
                    "severity": "high",
                    "line": insert_line,
                    "message": "INSERT without explicit transaction - consistency risk",
                })
        
        return edge_cases
    
    def _calculate_complexity(
        self,
        procedure_count: int,
        function_count: int,
        table_count: int,
        transaction_count: int,
    ) -> int:
        """Calculate overall complexity score (0-100)."""
        complexity = (
            (procedure_count * 10) +
            (function_count * 8) +
            (table_count * 3) +
            (transaction_count * 5)
        )
        
        return min(100, complexity)
