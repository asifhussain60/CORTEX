"""
Database Schema Inference Engine for CORTEX

Infers database schema from application code WITHOUT database access.
Extracts knowledge from ColdFusion queries, ORM models, and DAO patterns.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TableInfo:
    """Information about a database table inferred from code"""
    name: str
    columns: Set[str] = field(default_factory=set)
    primary_key: Optional[str] = None
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    operations: List[str] = field(default_factory=list)
    file_references: List[str] = field(default_factory=list)
    confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'columns': list(self.columns),
            'primary_key': self.primary_key,
            'relationships': self.relationships,
            'operations': self.operations,
            'file_references': self.file_references,
            'confidence': self.confidence
        }


class DatabaseSchemaInferenceEngine:
    """
    Infers database schema from application code WITHOUT database access.
    
    Sources:
    - ColdFusion <cfquery> tags and query parameters
    - ORM model definitions (Hibernate, ColdFusion ORM)
    - Data access layer files (DAOs, Services)
    - SQL queries in stored procedure calls
    - Configuration files (datasource definitions)
    
    Confidence Scoring:
    - ORM models: 0.95 (explicit definitions)
    - Multiple file references: +0.05 per additional file
    - Primary key detected: +0.15
    - Relationships detected: +0.10
    - Query operations: +0.05 per operation type
    """
    
    # SQL operation patterns
    SELECT_PATTERN = re.compile(r'\bSELECT\b', re.IGNORECASE)
    INSERT_PATTERN = re.compile(r'\bINSERT\s+INTO\b', re.IGNORECASE)
    UPDATE_PATTERN = re.compile(r'\bUPDATE\b', re.IGNORECASE)
    DELETE_PATTERN = re.compile(r'\bDELETE\s+FROM\b', re.IGNORECASE)
    
    # Table name patterns
    FROM_PATTERN = re.compile(r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.IGNORECASE)
    JOIN_PATTERN = re.compile(r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.IGNORECASE)
    UPDATE_TABLE_PATTERN = re.compile(r'\bUPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.IGNORECASE)
    INSERT_TABLE_PATTERN = re.compile(r'\bINSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.IGNORECASE)
    DELETE_TABLE_PATTERN = re.compile(r'\bDELETE\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.IGNORECASE)
    
    # Column patterns
    SELECT_COLUMNS_PATTERN = re.compile(r'SELECT\s+(.*?)\s+FROM', re.IGNORECASE | re.DOTALL)
    INSERT_COLUMNS_PATTERN = re.compile(r'\((.*?)\)\s+VALUES', re.IGNORECASE | re.DOTALL)
    
    def __init__(self, app_path: Path):
        """
        Initialize database schema inference engine.
        
        Args:
            app_path: Path to application root
        """
        self.app_path = app_path
        self.tables: Dict[str, TableInfo] = {}
    
    def infer_schema(self) -> Dict[str, Any]:
        """
        Infer database schema from application code.
        
        Returns:
            Dictionary with inferred schema information
        """
        logger.info(f"Starting database schema inference for {self.app_path}")
        
        # 1. Parse ColdFusion queries
        self._parse_cfquery_tags()
        
        # 2. Analyze ORM models (if using ColdFusion ORM)
        self._analyze_orm_models()
        
        # 3. Parse data access layer files
        self._parse_dao_files()
        
        # 4. Calculate confidence scores
        self._calculate_confidence_scores()
        
        # Build schema result
        schema = {
            'tables': {name: table.to_dict() for name, table in self.tables.items()},
            'total_tables': len(self.tables),
            'high_confidence_tables': len([t for t in self.tables.values() if t.confidence >= 0.8]),
            'relationships': self._extract_relationships(),
            'datasources': self._detect_datasources()
        }
        
        logger.info(f"Inferred schema: {len(self.tables)} tables, "
                   f"{schema['high_confidence_tables']} high confidence")
        
        return schema
    
    def _parse_cfquery_tags(self) -> None:
        """Extract SQL from <cfquery> tags"""
        cfm_files = list(self.app_path.rglob('*.cfm')) + list(self.app_path.rglob('*.cfc'))
        
        logger.info(f"Parsing {len(cfm_files)} ColdFusion files for queries")
        
        for cf_file in cfm_files:
            try:
                content = cf_file.read_text(encoding='utf-8', errors='ignore')
                rel_path = str(cf_file.relative_to(self.app_path))
                
                # Find <cfquery> blocks
                query_pattern = r'<cfquery[^>]*>(.*?)</cfquery>'
                matches = re.findall(query_pattern, content, re.DOTALL | re.IGNORECASE)
                
                for sql in matches:
                    self._analyze_sql_query(sql, rel_path)
            
            except Exception as e:
                logger.debug(f"Error parsing {cf_file}: {e}")
    
    def _analyze_sql_query(self, sql: str, file_path: str) -> None:
        """
        Analyze SQL query to extract table and column information.
        
        Args:
            sql: SQL query string
            file_path: Path to file containing query
        """
        # Detect query type
        query_type = self._detect_query_type(sql)
        
        # Extract table names
        tables = self._extract_table_names(sql)
        
        # Extract columns
        columns = self._extract_column_names(sql, query_type)
        
        # Update table information
        for table_name in tables:
            if table_name not in self.tables:
                self.tables[table_name] = TableInfo(name=table_name)
            
            table = self.tables[table_name]
            table.columns.update(columns)
            if query_type not in table.operations:
                table.operations.append(query_type)
            if file_path not in table.file_references:
                table.file_references.append(file_path)
    
    def _detect_query_type(self, sql: str) -> str:
        """Detect SQL query type"""
        if self.SELECT_PATTERN.search(sql):
            return 'SELECT'
        elif self.INSERT_PATTERN.search(sql):
            return 'INSERT'
        elif self.UPDATE_PATTERN.search(sql):
            return 'UPDATE'
        elif self.DELETE_PATTERN.search(sql):
            return 'DELETE'
        else:
            return 'UNKNOWN'
    
    def _extract_table_names(self, sql: str) -> List[str]:
        """Extract table names from SQL query"""
        tables = set()
        
        # FROM clauses
        tables.update(self.FROM_PATTERN.findall(sql))
        
        # JOIN clauses
        tables.update(self.JOIN_PATTERN.findall(sql))
        
        # UPDATE statements
        tables.update(self.UPDATE_TABLE_PATTERN.findall(sql))
        
        # INSERT statements
        tables.update(self.INSERT_TABLE_PATTERN.findall(sql))
        
        # DELETE statements
        tables.update(self.DELETE_TABLE_PATTERN.findall(sql))
        
        # Filter out SQL keywords
        sql_keywords = {'WHERE', 'AND', 'OR', 'ON', 'AS', 'SELECT', 'FROM', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER'}
        tables = {t for t in tables if t.upper() not in sql_keywords}
        
        return list(tables)
    
    def _extract_column_names(self, sql: str, query_type: str) -> Set[str]:
        """Extract column names from SQL query"""
        columns = set()
        
        try:
            if query_type == 'SELECT':
                # Extract columns from SELECT clause
                match = self.SELECT_COLUMNS_PATTERN.search(sql)
                if match:
                    column_str = match.group(1)
                    # Handle SELECT *
                    if '*' not in column_str:
                        # Split by comma and clean
                        raw_columns = column_str.split(',')
                        for col in raw_columns:
                            # Remove aliases (AS keyword)
                            col = re.sub(r'\s+AS\s+.*', '', col, flags=re.IGNORECASE)
                            # Extract column name (after table prefix if exists)
                            col = col.strip().split('.')[-1]
                            # Remove quotes
                            col = col.strip('\'"')
                            if col and col.isidentifier():
                                columns.add(col)
            
            elif query_type == 'INSERT':
                # Extract columns from INSERT clause
                match = self.INSERT_COLUMNS_PATTERN.search(sql)
                if match:
                    column_str = match.group(1)
                    raw_columns = column_str.split(',')
                    for col in raw_columns:
                        col = col.strip().strip('\'"')
                        if col and col.isidentifier():
                            columns.add(col)
        
        except Exception as e:
            logger.debug(f"Error extracting columns: {e}")
        
        return columns
    
    def _analyze_orm_models(self) -> None:
        """Analyze ORM model definitions"""
        # Look for ColdFusion ORM components
        cfc_files = list(self.app_path.rglob('*.cfc'))
        
        logger.info(f"Analyzing {len(cfc_files)} CFC files for ORM models")
        
        for cfc_file in cfc_files:
            try:
                content = cfc_file.read_text(encoding='utf-8', errors='ignore')
                rel_path = str(cfc_file.relative_to(self.app_path))
                
                # Check for ORM entity definition
                if 'persistent="true"' in content or 'persistent=true' in content:
                    self._parse_orm_entity(content, rel_path)
            
            except Exception as e:
                logger.debug(f"Error analyzing ORM in {cfc_file}: {e}")
    
    def _parse_orm_entity(self, content: str, file_path: str) -> None:
        """
        Parse ColdFusion ORM entity definition.
        
        Extracts:
        - Table name
        - Properties (columns)
        - Primary key
        - Relationships
        """
        try:
            # Extract table name
            table_match = re.search(r'table="([^"]+)"', content, re.IGNORECASE)
            table_name = table_match.group(1) if table_match else None
            
            if not table_name:
                # Try component name as table name
                comp_match = re.search(r'component\s+name="([^"]+)"', content, re.IGNORECASE)
                if comp_match:
                    table_name = comp_match.group(1)
            
            if not table_name:
                return
            
            # Create or get table info
            if table_name not in self.tables:
                self.tables[table_name] = TableInfo(name=table_name, confidence=0.95)  # ORM = high confidence
            
            table = self.tables[table_name]
            table.file_references.append(file_path)
            
            # Extract properties (columns)
            property_pattern = r'property\s+name="([^"]+)"'
            properties = re.findall(property_pattern, content, re.IGNORECASE)
            table.columns.update(properties)
            
            # Extract primary key
            pk_pattern = r'property\s+name="([^"]+)"[^;]*fieldtype="id"'
            pk_match = re.search(pk_pattern, content, re.IGNORECASE)
            if pk_match:
                table.primary_key = pk_match.group(1)
            
            # Extract relationships
            rel_patterns = [
                (r'fieldtype="one-to-many"[^;]*cfc="([^"]+)"', 'one-to-many'),
                (r'fieldtype="many-to-one"[^;]*cfc="([^"]+)"', 'many-to-one'),
                (r'fieldtype="many-to-many"[^;]*cfc="([^"]+)"', 'many-to-many')
            ]
            
            for pattern, rel_type in rel_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for target_cfc in matches:
                    table.relationships.append({
                        'type': rel_type,
                        'target': target_cfc
                    })
        
        except Exception as e:
            logger.debug(f"Error parsing ORM entity: {e}")
    
    def _parse_dao_files(self) -> None:
        """Parse data access object files for query patterns"""
        # Look for common DAO naming patterns
        dao_patterns = ['*DAO.cfc', '*Service.cfc', '*Repository.cfc', '*Gateway.cfc']
        dao_files = []
        
        for pattern in dao_patterns:
            dao_files.extend(self.app_path.rglob(pattern))
        
        logger.info(f"Parsing {len(dao_files)} DAO files")
        
        for dao_file in dao_files:
            try:
                content = dao_file.read_text(encoding='utf-8', errors='ignore')
                rel_path = str(dao_file.relative_to(self.app_path))
                
                # Find SQL queries in DAO methods
                query_pattern = r'["\'](SELECT|INSERT|UPDATE|DELETE).*?["\']'
                matches = re.findall(query_pattern, content, re.IGNORECASE | re.DOTALL)
                
                for sql in matches:
                    if len(sql) < 10000:  # Skip massive queries
                        self._analyze_sql_query(sql, rel_path)
            
            except Exception as e:
                logger.debug(f"Error parsing DAO {dao_file}: {e}")
    
    def _calculate_confidence_scores(self) -> None:
        """Calculate confidence scores for all tables"""
        for table in self.tables.values():
            # Start with base confidence
            confidence = 0.5
            
            # Boost for ORM models (already set to 0.95)
            if table.confidence >= 0.95:
                continue
            
            # Multiple file references boost
            if len(table.file_references) > 1:
                confidence += min(0.05 * (len(table.file_references) - 1), 0.25)
            
            # Primary key detected
            if table.primary_key:
                confidence += 0.15
            
            # Relationships detected
            if table.relationships:
                confidence += min(0.10 * len(table.relationships), 0.20)
            
            # Multiple operation types
            if len(table.operations) > 1:
                confidence += 0.05 * (len(table.operations) - 1)
            
            # Column information
            if len(table.columns) > 3:
                confidence += 0.10
            
            table.confidence = min(confidence, 1.0)
    
    def _extract_relationships(self) -> List[Dict[str, Any]]:
        """Extract cross-table relationships"""
        relationships = []
        
        for table in self.tables.values():
            for rel in table.relationships:
                relationships.append({
                    'source_table': table.name,
                    'target_table': rel.get('target', 'unknown'),
                    'relationship_type': rel.get('type', 'unknown')
                })
        
        return relationships
    
    def _detect_datasources(self) -> List[Dict[str, str]]:
        """Detect datasource configurations"""
        datasources = []
        
        # Look for common datasource config files
        config_files = [
            'Application.cfc',
            'Application.cfm',
            'datasource.cfm',
            'config/datasource.cfm'
        ]
        
        for config_file in config_files:
            config_path = self.app_path / config_file
            if config_path.exists():
                try:
                    content = config_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Look for datasource definitions
                    ds_pattern = r'datasource\s*=\s*["\']([^"\']+)["\']'
                    matches = re.findall(ds_pattern, content, re.IGNORECASE)
                    
                    for ds_name in matches:
                        datasources.append({
                            'name': ds_name,
                            'file': config_file
                        })
                
                except Exception as e:
                    logger.debug(f"Error detecting datasources in {config_file}: {e}")
        
        return datasources
    
    def get_table_info(self, table_name: str) -> Optional[TableInfo]:
        """Get information about a specific table"""
        return self.tables.get(table_name)
    
    def get_high_confidence_tables(self) -> List[TableInfo]:
        """Get tables with high confidence scores (>=0.8)"""
        return [t for t in self.tables.values() if t.confidence >= 0.8]
