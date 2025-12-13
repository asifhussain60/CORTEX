"""
SQL Analyzer using sqlparse Library

Parses SQL files to extract schema, queries, and database operations.
Supports multiple SQL dialects (T-SQL, PostgreSQL, MySQL, SQLite).
"""

import logging
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Function, Where, Comparison
from sqlparse.tokens import Keyword, DML, DDL
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
from .base import BaseAnalyzer

logger = logging.getLogger(__name__)


class SQLAnalyzer(BaseAnalyzer):
    """
    SQL code analyzer using sqlparse library
    
    Capabilities:
    - Table definitions (CREATE TABLE)
    - View definitions (CREATE VIEW)
    - Stored procedures and functions
    - Index definitions
    - Foreign key constraints
    - DML operations (SELECT, INSERT, UPDATE, DELETE)
    - JOIN analysis
    - Subquery detection
    - SQL dialect detection
    
    Supported Dialects:
    - T-SQL (SQL Server)
    - PostgreSQL
    - MySQL/MariaDB
    - SQLite
    - Oracle PL/SQL
    """
    
    SUPPORTED_EXTENSIONS = {'.sql', '.tsql', '.pgsql', '.mysql', '.ddl'}
    
    # SQL keywords by category
    DDL_KEYWORDS = {'CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME'}
    DML_KEYWORDS = {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE'}
    DCL_KEYWORDS = {'GRANT', 'REVOKE', 'DENY'}
    TCL_KEYWORDS = {'COMMIT', 'ROLLBACK', 'SAVEPOINT'}
    
    def __init__(self):
        """Initialize SQL analyzer"""
        super().__init__()
        logger.info("SQL analyzer initialized with sqlparse")
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze SQL file
        
        Args:
            file_path: Path to SQL file
            
        Returns:
            {
                'tables': [...],
                'views': [...],
                'procedures': [...],
                'functions': [...],
                'indexes': [...],
                'constraints': [...],
                'queries': [...],
                'operations': {...},
                'dialect': str,
                'metadata': {...}
            }
        """
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return self._generate_fallback_structure(file_path)
        
        # Parse SQL
        try:
            statements = sqlparse.parse(code)
        except Exception as e:
            logger.error(f"Failed to parse SQL in {file_path}: {e}")
            return self._generate_fallback_structure(file_path)
        
        # Extract schema objects
        tables = []
        views = []
        procedures = []
        functions = []
        indexes = []
        constraints = []
        queries = []
        
        operations = defaultdict(int)
        
        for stmt in statements:
            # Classify statement
            stmt_type = self._classify_statement(stmt)
            if stmt_type:
                operations[stmt_type] += 1
            
            # Extract objects based on type
            if stmt_type == 'CREATE_TABLE':
                table_info = self._extract_create_table(stmt)
                if table_info:
                    tables.append(table_info)
            
            elif stmt_type == 'CREATE_VIEW':
                view_info = self._extract_create_view(stmt)
                if view_info:
                    views.append(view_info)
            
            elif stmt_type == 'CREATE_PROCEDURE':
                proc_info = self._extract_create_procedure(stmt)
                if proc_info:
                    procedures.append(proc_info)
            
            elif stmt_type == 'CREATE_FUNCTION':
                func_info = self._extract_create_function(stmt)
                if func_info:
                    functions.append(func_info)
            
            elif stmt_type == 'CREATE_INDEX':
                index_info = self._extract_create_index(stmt)
                if index_info:
                    indexes.append(index_info)
            
            elif stmt_type in self.DML_KEYWORDS:
                query_info = self._extract_query_info(stmt, stmt_type)
                queries.append(query_info)
        
        # Detect SQL dialect
        dialect = self._detect_dialect(code, statements)
        
        # Calculate metrics
        lines = code.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('--')])
        
        return {
            'tables': tables,
            'views': views,
            'procedures': procedures,
            'functions': functions,
            'indexes': indexes,
            'constraints': constraints,
            'queries': queries,
            'operations': dict(operations),
            'dialect': dialect,
            'metadata': {
                'file_path': str(file_path),
                'lines_of_code': loc,
                'total_lines': len(lines),
                'statement_count': len(statements),
                'table_count': len(tables),
                'view_count': len(views),
                'procedure_count': len(procedures),
                'query_count': len(queries)
            }
        }
    
    def _classify_statement(self, stmt) -> Optional[str]:
        """Classify SQL statement type"""
        # Get first significant token
        first_token = stmt.token_first(skip_ws=True, skip_cm=True)
        if not first_token:
            return None
        
        token_value = first_token.value.upper()
        
        # DDL statements
        if token_value == 'CREATE':
            # Check what's being created
            next_token = stmt.token_next(stmt.token_index(first_token), skip_ws=True, skip_cm=True)
            if next_token:
                obj_type = next_token[1].value.upper()
                if obj_type == 'TABLE':
                    return 'CREATE_TABLE'
                elif obj_type == 'VIEW':
                    return 'CREATE_VIEW'
                elif obj_type in ('PROCEDURE', 'PROC'):
                    return 'CREATE_PROCEDURE'
                elif obj_type == 'FUNCTION':
                    return 'CREATE_FUNCTION'
                elif obj_type == 'INDEX':
                    return 'CREATE_INDEX'
                else:
                    return f'CREATE_{obj_type}'
        
        elif token_value == 'ALTER':
            return 'ALTER'
        elif token_value == 'DROP':
            return 'DROP'
        
        # DML statements
        elif token_value in self.DML_KEYWORDS:
            return token_value
        
        # DCL/TCL
        elif token_value in self.DCL_KEYWORDS:
            return token_value
        elif token_value in self.TCL_KEYWORDS:
            return token_value
        
        return 'UNKNOWN'
    
    def _extract_create_table(self, stmt) -> Optional[Dict[str, Any]]:
        """Extract table definition"""
        tokens = list(stmt.flatten())
        
        # Find table name
        table_name = None
        found_table_keyword = False
        
        for token in tokens:
            if token.ttype is Keyword and token.value.upper() == 'TABLE':
                found_table_keyword = True
            elif found_table_keyword and token.ttype is not None:
                if str(token.ttype) not in ('Token.Text.Whitespace', 'Token.Punctuation'):
                    table_name = token.value.strip('[]`"')
                    break
        
        if not table_name:
            return None
        
        # Extract columns (simplified - full parsing would be more complex)
        sql_text = stmt.value
        columns = self._extract_columns_from_create_table(sql_text)
        
        return {
            'name': table_name,
            'columns': columns,
            'type': 'table'
        }
    
    def _extract_columns_from_create_table(self, sql_text: str) -> List[str]:
        """Extract column names from CREATE TABLE (simplified)"""
        # Find content between parentheses
        start = sql_text.find('(')
        end = sql_text.rfind(')')
        
        if start == -1 or end == -1:
            return []
        
        columns_text = sql_text[start+1:end]
        
        # Simple extraction (not handling nested parentheses)
        columns = []
        for line in columns_text.split(','):
            line = line.strip()
            if line and not line.upper().startswith(('CONSTRAINT', 'PRIMARY', 'FOREIGN', 'CHECK', 'UNIQUE')):
                # Get first word as column name
                parts = line.split()
                if parts:
                    col_name = parts[0].strip('[]`"')
                    columns.append(col_name)
        
        return columns
    
    def _extract_create_view(self, stmt) -> Optional[Dict[str, Any]]:
        """Extract view definition"""
        tokens = list(stmt.flatten())
        
        # Find view name
        view_name = None
        found_view_keyword = False
        
        for token in tokens:
            if token.ttype is Keyword and token.value.upper() == 'VIEW':
                found_view_keyword = True
            elif found_view_keyword and token.ttype is not None:
                if str(token.ttype) not in ('Token.Text.Whitespace', 'Token.Punctuation', 'Token.Keyword'):
                    view_name = token.value.strip('[]`"')
                    break
        
        if not view_name:
            return None
        
        return {
            'name': view_name,
            'type': 'view'
        }
    
    def _extract_create_procedure(self, stmt) -> Optional[Dict[str, Any]]:
        """Extract stored procedure definition"""
        tokens = list(stmt.flatten())
        
        # Find procedure name
        proc_name = None
        found_proc_keyword = False
        
        for token in tokens:
            if token.ttype is Keyword and token.value.upper() in ('PROCEDURE', 'PROC'):
                found_proc_keyword = True
            elif found_proc_keyword and token.ttype is not None:
                if str(token.ttype) not in ('Token.Text.Whitespace', 'Token.Punctuation', 'Token.Keyword'):
                    proc_name = token.value.strip('[]`"')
                    break
        
        if not proc_name:
            return None
        
        return {
            'name': proc_name,
            'type': 'procedure'
        }
    
    def _extract_create_function(self, stmt) -> Optional[Dict[str, Any]]:
        """Extract function definition"""
        tokens = list(stmt.flatten())
        
        # Find function name
        func_name = None
        found_func_keyword = False
        
        for token in tokens:
            if token.ttype is Keyword and token.value.upper() == 'FUNCTION':
                found_func_keyword = True
            elif found_func_keyword and token.ttype is not None:
                if str(token.ttype) not in ('Token.Text.Whitespace', 'Token.Punctuation', 'Token.Keyword'):
                    func_name = token.value.strip('[]`"')
                    break
        
        if not func_name:
            return None
        
        return {
            'name': func_name,
            'type': 'function'
        }
    
    def _extract_create_index(self, stmt) -> Optional[Dict[str, Any]]:
        """Extract index definition"""
        tokens = list(stmt.flatten())
        
        # Find index name
        index_name = None
        found_index_keyword = False
        
        for token in tokens:
            if token.ttype is Keyword and token.value.upper() == 'INDEX':
                found_index_keyword = True
            elif found_index_keyword and token.ttype is not None:
                if str(token.ttype) not in ('Token.Text.Whitespace', 'Token.Punctuation', 'Token.Keyword'):
                    index_name = token.value.strip('[]`"')
                    break
        
        if not index_name:
            return None
        
        return {
            'name': index_name,
            'type': 'index'
        }
    
    def _extract_query_info(self, stmt, query_type: str) -> Dict[str, Any]:
        """Extract query metadata"""
        sql_text = stmt.value
        
        # Count JOINs
        join_count = sql_text.upper().count('JOIN')
        
        # Check for subqueries
        has_subquery = sql_text.count('(SELECT') > 0 or sql_text.count('( SELECT') > 0
        
        # Extract table references (simplified)
        tables_referenced = self._extract_table_references(stmt)
        
        return {
            'type': query_type,
            'tables': tables_referenced,
            'join_count': join_count,
            'has_subquery': has_subquery,
            'length': len(sql_text)
        }
    
    def _extract_table_references(self, stmt) -> List[str]:
        """Extract table names from query"""
        tables = []
        
        # Simple extraction using sqlparse
        for token in stmt.tokens:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    tables.append(str(identifier).strip('[]`"'))
            elif isinstance(token, Identifier):
                tables.append(str(token).strip('[]`"'))
        
        return tables
    
    def _detect_dialect(self, code: str, statements) -> str:
        """Detect SQL dialect based on syntax patterns"""
        code_upper = code.upper()
        
        # T-SQL indicators (check IDENTITY first as it's most distinctive)
        if any(keyword in code_upper for keyword in ['IDENTITY(', 'BEGIN TRY', 'RAISERROR', 'NVARCHAR', 'GETDATE()']):
            return 'T-SQL'
        
        # PostgreSQL indicators
        if any(keyword in code_upper for keyword in ['SERIAL', 'RETURNING', 'GENERATE_SERIES']):
            return 'PostgreSQL'
        
        # MySQL indicators
        if any(keyword in code_upper for keyword in ['AUTO_INCREMENT', 'UNSIGNED', 'ENUM']):
            return 'MySQL'
        
        # Oracle indicators
        if any(keyword in code_upper for keyword in ['VARCHAR2', 'NUMBER', 'SYSDATE', 'DUAL']):
            return 'Oracle'
        
        # SQLite indicators
        if 'AUTOINCREMENT' in code_upper:
            return 'SQLite'
        
        return 'Standard SQL'
    
    def _generate_fallback_structure(self, file_path: Path) -> Dict[str, Any]:
        """Generate fallback structure on error"""
        return {
            'tables': [],
            'views': [],
            'procedures': [],
            'functions': [],
            'indexes': [],
            'constraints': [],
            'queries': [],
            'operations': {},
            'dialect': 'unknown',
            'metadata': {
                'file_path': str(file_path),
                'error': 'Failed to parse SQL'
            }
        }
    
    def analyze_batch(
        self,
        file_paths: List[Path],
        max_workers: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Batch analyze SQL files with parallel execution
        
        Similar to PythonAnalyzer.analyze_batch()
        """
        if not file_paths:
            return {
                'files': {},
                'summary': {
                    'total_files': 0,
                    'success_count': 0,
                    'failure_count': 0
                }
            }
        
        results = {}
        total = len(file_paths)
        
        # Sequential for small batches
        if total <= 10:
            for i, fp in enumerate(file_paths, 1):
                if progress_callback:
                    progress_callback(i, total, fp.name)
                results[str(fp)] = self.analyze(fp)
            
            success_count = sum(1 for r in results.values() if 'error' not in r.get('metadata', {}))
            
            return {
                'files': results,
                'summary': {
                    'total_files': total,
                    'success_count': success_count,
                    'failure_count': total - success_count
                }
            }
        
        # Parallel for large batches
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import multiprocessing
        
        if max_workers is None:
            max_workers = max(1, multiprocessing.cpu_count() - 1)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.analyze, fp): fp
                for fp in file_paths
            }
            
            completed = 0
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, total, file_path.name)
                
                try:
                    results[str(file_path)] = future.result()
                except Exception as e:
                    logger.error(f"Failed to analyze {file_path}: {e}")
                    results[str(file_path)] = {
                        'metadata': {'error': str(e)}
                    }
        
        success_count = sum(1 for r in results.values() if 'error' not in r.get('metadata', {}))
        
        return {
            'files': results,
            'summary': {
                'total_files': total,
                'success_count': success_count,
                'failure_count': total - success_count
            }
        }
