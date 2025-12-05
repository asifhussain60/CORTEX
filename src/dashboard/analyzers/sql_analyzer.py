"""
SQL Language Analyzer for dashboard data collection.
Extracts T-SQL/PL-SQL schema (tables, views, procedures, functions, triggers, indexes, foreign keys).
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from .language_analyzer_base import LanguageAnalyzer, AnalysisResult


class SQLAnalyzer(LanguageAnalyzer):
    """
    Analyzer for SQL source files (.sql).
    
    Supports:
    - T-SQL (SQL Server)
    - PL/SQL (Oracle)
    
    Extracts:
    - Table definitions (CREATE TABLE)
    - View definitions (CREATE VIEW)
    - Stored procedures (CREATE PROCEDURE)
    - Functions (CREATE FUNCTION)
    - Triggers (CREATE TRIGGER)
    - Indexes (CREATE INDEX)
    - Foreign keys (ALTER TABLE ADD CONSTRAINT)
    - SQL complexity metrics
    """
    
    SUPPORTED_EXTENSIONS = {'.sql'}
    
    def __init__(self, encoding: str = 'utf-8', db_type: str = 'sql_server'):
        """
        Initialize SQL analyzer.
        
        Args:
            encoding: File encoding
            db_type: Database type ('sql_server' or 'oracle')
        """
        super().__init__(encoding)
        self.db_type = db_type
        
        # Regex patterns for SQL constructs
        self.table_pattern = re.compile(
            r'CREATE\s+TABLE\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?',
            re.IGNORECASE | re.MULTILINE
        )
        self.view_pattern = re.compile(
            r'CREATE\s+VIEW\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?',
            re.IGNORECASE | re.MULTILINE
        )
        self.procedure_pattern = re.compile(
            r'CREATE\s+(?:OR\s+REPLACE\s+)?PROC(?:EDURE)?\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?',
            re.IGNORECASE | re.MULTILINE
        )
        self.function_pattern = re.compile(
            r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?',
            re.IGNORECASE | re.MULTILINE
        )
        self.trigger_pattern = re.compile(
            r'CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?',
            re.IGNORECASE | re.MULTILINE
        )
        self.index_pattern = re.compile(
            r'CREATE\s+(?:UNIQUE\s+)?(?:CLUSTERED\s+|NONCLUSTERED\s+)?INDEX\s+\[?(\w+)\]?\s+ON\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?',
            re.IGNORECASE | re.MULTILINE
        )
        self.fk_pattern = re.compile(
            r'(?:CONSTRAINT\s+\[?(\w+)\]?\s+)?FOREIGN\s+KEY\s*\([^)]+\)\s*REFERENCES\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?',
            re.IGNORECASE | re.MULTILINE
        )
    
    def supports_file(self, file_path: Path) -> bool:
        """Check if file is a SQL source file."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def analyze(self, file_path: Path) -> AnalysisResult:
        """
        Analyze SQL source file.
        
        Args:
            file_path: Path to .sql file
            
        Returns:
            AnalysisResult with SQL metrics
        """
        content = self.read_file(file_path)
        
        if not content:
            return AnalysisResult(
                file_path=str(file_path),
                language='sql',
                classes=[],
                methods=[],
                complexity={},
                dependencies=[],
                patterns={},
                metrics={},
                errors=self.errors.copy()
            )
        
        # Remove comments for cleaner parsing
        content_clean = self._remove_comments(content)
        
        # Extract SQL objects
        tables = self._extract_tables(content_clean, content)
        views = self._extract_views(content_clean, content)
        procedures = self._extract_procedures(content_clean, content)
        functions = self._extract_functions(content_clean, content)
        triggers = self._extract_triggers(content_clean, content)
        indexes = self._extract_indexes(content_clean)
        foreign_keys = self._extract_foreign_keys(content_clean)
        
        # Detect patterns
        patterns = self._detect_patterns(content_clean)
        
        # Calculate complexity
        complexity = self._calculate_complexity(content_clean, procedures + functions)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(content_clean, tables, views)
        
        # Calculate metrics
        metrics = self._calculate_metrics(
            content, tables, views, procedures, functions, triggers, indexes
        )
        
        return AnalysisResult(
            file_path=str(file_path),
            language='sql',
            classes=tables + views,  # Tables and views as "classes"
            methods=procedures + functions + triggers,  # Procedures/functions as "methods"
            complexity=complexity,
            dependencies=dependencies,
            patterns=patterns,
            metrics=metrics,
            errors=self.errors.copy()
        )
    
    def _remove_comments(self, content: str) -> str:
        """Remove SQL comments for cleaner parsing."""
        # Remove single-line comments
        content = re.sub(r'--[^\n]*', '', content)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        return content
    
    def _extract_tables(self, content_clean: str, content_original: str) -> List[Dict[str, Any]]:
        """Extract table definitions."""
        tables = []
        
        for match in self.table_pattern.finditer(content_clean):
            schema = match.group(1) or 'dbo'
            table_name = match.group(2)
            
            # Try to extract columns from CREATE TABLE statement
            columns = self._extract_table_columns(content_original, table_name)
            
            tables.append({
                'name': f'{schema}.{table_name}',
                'type': 'table',
                'schema': schema,
                'table_name': table_name,
                'column_count': len(columns),
                'columns': columns,
                'line': content_clean[:match.start()].count('\n') + 1
            })
        
        return tables
    
    def _extract_table_columns(self, content: str, table_name: str) -> List[Dict[str, str]]:
        """Extract column definitions from CREATE TABLE statement."""
        columns = []
        
        # Find CREATE TABLE block
        pattern = re.compile(
            rf'CREATE\s+TABLE\s+[^\s]+{table_name}[^\s]*\s*\(([^;]+)\)',
            re.IGNORECASE | re.DOTALL
        )
        match = pattern.search(content)
        
        if match:
            columns_text = match.group(1)
            
            # Parse column definitions (simplified)
            col_pattern = re.compile(
                r'\[?(\w+)\]?\s+([\w()]+)',
                re.IGNORECASE
            )
            
            for col_match in col_pattern.finditer(columns_text):
                col_name = col_match.group(1)
                col_type = col_match.group(2)
                
                # Skip constraints
                if col_name.upper() in ['PRIMARY', 'FOREIGN', 'CONSTRAINT', 'KEY', 'REFERENCES']:
                    continue
                
                columns.append({
                    'name': col_name,
                    'type': col_type
                })
        
        return columns
    
    def _extract_views(self, content_clean: str, content_original: str) -> List[Dict[str, Any]]:
        """Extract view definitions."""
        views = []
        
        for match in self.view_pattern.finditer(content_clean):
            schema = match.group(1) or 'dbo'
            view_name = match.group(2)
            
            # Try to extract view complexity
            view_sql = self._extract_object_sql(content_original, 'VIEW', view_name)
            complexity = self._calculate_sql_complexity(view_sql)
            
            views.append({
                'name': f'{schema}.{view_name}',
                'type': 'view',
                'schema': schema,
                'view_name': view_name,
                'complexity': complexity,
                'line': content_clean[:match.start()].count('\n') + 1
            })
        
        return views
    
    def _extract_procedures(self, content_clean: str, content_original: str) -> List[Dict[str, Any]]:
        """Extract stored procedure definitions."""
        procedures = []
        
        for match in self.procedure_pattern.finditer(content_clean):
            schema = match.group(1) or 'dbo'
            proc_name = match.group(2)
            
            # Extract procedure SQL
            proc_sql = self._extract_object_sql(content_original, 'PROC', proc_name)
            
            # Extract parameters
            params = self._extract_parameters(proc_sql)
            
            # Calculate complexity
            complexity = self._calculate_sql_complexity(proc_sql)
            loc = len(proc_sql.split('\n')) if proc_sql else 0
            
            procedures.append({
                'name': f'{schema}.{proc_name}',
                'type': 'procedure',
                'schema': schema,
                'proc_name': proc_name,
                'parameter_count': len(params),
                'parameters': params,
                'loc': loc,
                'complexity': complexity,
                'line': content_clean[:match.start()].count('\n') + 1
            })
        
        return procedures
    
    def _extract_functions(self, content_clean: str, content_original: str) -> List[Dict[str, Any]]:
        """Extract function definitions."""
        functions = []
        
        for match in self.function_pattern.finditer(content_clean):
            schema = match.group(1) or 'dbo'
            func_name = match.group(2)
            
            # Extract function SQL
            func_sql = self._extract_object_sql(content_original, 'FUNCTION', func_name)
            
            # Extract parameters
            params = self._extract_parameters(func_sql)
            
            # Determine function type (scalar or table-valued)
            func_type = 'table_valued' if 'RETURNS TABLE' in func_sql.upper() else 'scalar'
            
            # Calculate complexity
            complexity = self._calculate_sql_complexity(func_sql)
            loc = len(func_sql.split('\n')) if func_sql else 0
            
            functions.append({
                'name': f'{schema}.{func_name}',
                'type': 'function',
                'schema': schema,
                'func_name': func_name,
                'func_type': func_type,
                'parameter_count': len(params),
                'parameters': params,
                'loc': loc,
                'complexity': complexity,
                'line': content_clean[:match.start()].count('\n') + 1
            })
        
        return functions
    
    def _extract_triggers(self, content_clean: str, content_original: str) -> List[Dict[str, Any]]:
        """Extract trigger definitions."""
        triggers = []
        
        for match in self.trigger_pattern.finditer(content_clean):
            schema = match.group(1) or 'dbo'
            trigger_name = match.group(2)
            
            # Extract trigger SQL
            trigger_sql = self._extract_object_sql(content_original, 'TRIGGER', trigger_name)
            
            # Detect trigger type
            trigger_type = []
            if 'AFTER INSERT' in trigger_sql.upper() or 'FOR INSERT' in trigger_sql.upper():
                trigger_type.append('INSERT')
            if 'AFTER UPDATE' in trigger_sql.upper() or 'FOR UPDATE' in trigger_sql.upper():
                trigger_type.append('UPDATE')
            if 'AFTER DELETE' in trigger_sql.upper() or 'FOR DELETE' in trigger_sql.upper():
                trigger_type.append('DELETE')
            if 'INSTEAD OF' in trigger_sql.upper():
                trigger_type.append('INSTEAD_OF')
            
            triggers.append({
                'name': f'{schema}.{trigger_name}',
                'type': 'trigger',
                'schema': schema,
                'trigger_name': trigger_name,
                'trigger_type': ', '.join(trigger_type) if trigger_type else 'UNKNOWN',
                'line': content_clean[:match.start()].count('\n') + 1
            })
        
        return triggers
    
    def _extract_indexes(self, content_clean: str) -> List[Dict[str, Any]]:
        """Extract index definitions."""
        indexes = []
        
        for match in self.index_pattern.finditer(content_clean):
            index_name = match.group(1)
            schema = match.group(2) or 'dbo'
            table_name = match.group(3)
            
            # Detect index type
            index_def = content_clean[max(0, match.start()-50):match.start()+100]
            is_unique = 'UNIQUE' in index_def.upper()
            is_clustered = 'CLUSTERED' in index_def.upper() and 'NONCLUSTERED' not in index_def.upper()
            
            indexes.append({
                'name': index_name,
                'table': f'{schema}.{table_name}',
                'is_unique': is_unique,
                'is_clustered': is_clustered
            })
        
        return indexes
    
    def _extract_foreign_keys(self, content_clean: str) -> List[Dict[str, Any]]:
        """Extract foreign key definitions."""
        foreign_keys = []
        
        for match in self.fk_pattern.finditer(content_clean):
            fk_name = match.group(1) or 'Unnamed'
            ref_schema = match.group(2) or 'dbo'
            ref_table = match.group(3)
            
            foreign_keys.append({
                'name': fk_name,
                'references': f'{ref_schema}.{ref_table}'
            })
        
        return foreign_keys
    
    def _extract_object_sql(self, content: str, obj_type: str, obj_name: str) -> str:
        """Extract SQL for a specific database object."""
        # Build pattern to find object definition
        pattern = re.compile(
            rf'CREATE\s+(?:OR\s+REPLACE\s+)?{obj_type}\s+[^\s]+{obj_name}[^\s]*\s*(.*?)(?=CREATE|ALTER|DROP|GO|\Z)',
            re.IGNORECASE | re.DOTALL
        )
        
        match = pattern.search(content)
        if match:
            return match.group(0)
        
        return ''
    
    def _extract_parameters(self, sql: str) -> List[Dict[str, str]]:
        """Extract parameters from procedure/function SQL."""
        parameters = []
        
        # Find parameter list (between name and AS/IS)
        param_pattern = re.compile(
            r'@(\w+)\s+([\w()]+)',
            re.IGNORECASE
        )
        
        for match in param_pattern.finditer(sql):
            param_name = match.group(1)
            param_type = match.group(2)
            
            parameters.append({
                'name': f'@{param_name}',
                'type': param_type
            })
        
        return parameters
    
    def _calculate_sql_complexity(self, sql: str) -> int:
        """Calculate SQL statement complexity."""
        if not sql:
            return 0
        
        complexity = 1  # Base complexity
        
        # Count decision points
        keywords = ['IF', 'ELSE', 'CASE', 'WHEN', 'WHILE', 'FOR', 'AND', 'OR', 'JOIN']
        sql_upper = sql.upper()
        
        for keyword in keywords:
            complexity += sql_upper.count(keyword)
        
        return complexity
    
    def _detect_patterns(self, content: str) -> Dict[str, Any]:
        """Detect SQL patterns and practices."""
        patterns = {
            'has_transactions': False,
            'has_error_handling': False,
            'has_cursors': False,
            'has_dynamic_sql': False,
            'has_temp_tables': False
        }
        
        content_upper = content.upper()
        
        # Check for transactions
        if 'BEGIN TRAN' in content_upper or 'BEGIN TRANSACTION' in content_upper:
            patterns['has_transactions'] = True
        
        # Check for error handling
        if 'TRY' in content_upper and 'CATCH' in content_upper:
            patterns['has_error_handling'] = True
        elif 'EXCEPTION' in content_upper:  # Oracle
            patterns['has_error_handling'] = True
        
        # Check for cursors
        if 'DECLARE CURSOR' in content_upper or 'OPEN CURSOR' in content_upper:
            patterns['has_cursors'] = True
        
        # Check for dynamic SQL
        if 'EXEC(' in content_upper or 'EXECUTE(' in content_upper or 'SP_EXECUTESQL' in content_upper:
            patterns['has_dynamic_sql'] = True
        
        # Check for temp tables
        if '#' in content or 'CREATE TABLE #' in content_upper:
            patterns['has_temp_tables'] = True
        
        return patterns
    
    def _extract_dependencies(
        self,
        content: str,
        tables: List[Dict[str, Any]],
        views: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract table/view dependencies."""
        dependencies = []
        
        # Extract FROM and JOIN clauses
        from_pattern = re.compile(
            r'(?:FROM|JOIN)\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?',
            re.IGNORECASE | re.MULTILINE
        )
        
        for match in from_pattern.finditer(content):
            schema = match.group(1) or 'dbo'
            obj_name = match.group(2)
            
            # Skip common SQL keywords
            if obj_name.upper() in ['SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING']:
                continue
            
            dependencies.append(f'{schema}.{obj_name}')
        
        return list(set(dependencies))  # Remove duplicates
    
    def _calculate_complexity(
        self,
        content: str,
        procedures_and_functions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate overall complexity metrics."""
        total_complexity = 0
        
        for obj in procedures_and_functions:
            total_complexity += obj.get('complexity', 0)
        
        avg_complexity = 0
        if procedures_and_functions:
            avg_complexity = total_complexity / len(procedures_and_functions)
        
        return {
            'total': total_complexity,
            'average': avg_complexity,
            'max': max([obj.get('complexity', 0) for obj in procedures_and_functions], default=0)
        }
    
    def _calculate_metrics(
        self,
        content: str,
        tables: List[Dict[str, Any]],
        views: List[Dict[str, Any]],
        procedures: List[Dict[str, Any]],
        functions: List[Dict[str, Any]],
        triggers: List[Dict[str, Any]],
        indexes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate general SQL metrics."""
        lines = content.split('\n')
        
        # Calculate total LOC for procedures/functions
        total_proc_loc = sum(p.get('loc', 0) for p in procedures)
        total_func_loc = sum(f.get('loc', 0) for f in functions)
        
        return {
            'loc': len(lines),
            'table_count': len(tables),
            'view_count': len(views),
            'procedure_count': len(procedures),
            'function_count': len(functions),
            'trigger_count': len(triggers),
            'index_count': len(indexes),
            'total_proc_loc': total_proc_loc,
            'total_func_loc': total_func_loc,
            'avg_proc_loc': total_proc_loc / len(procedures) if procedures else 0,
            'avg_func_loc': total_func_loc / len(functions) if functions else 0
        }
