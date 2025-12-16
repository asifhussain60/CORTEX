"""
Semantic index builder using SQLite FTS5
"""
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import CodeElement

logger = logging.getLogger(__name__)


class SemanticIndexBuilder:
    """Build and maintain FTS5 semantic search index"""
    
    def __init__(self, db_path: Path):
        """
        Initialize semantic index builder
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database with FTS5 schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        
        # Create FTS5 virtual table
        self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS code_index USING fts5(
                element_id,
                element_type,
                element_name,
                file_path,
                signature,
                code_content,
                tokenize='porter unicode61'
            )
        """)
        
        # Create metadata table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS element_metadata (
                element_id TEXT PRIMARY KEY,
                element_type TEXT,
                file_path TEXT,
                line_start INTEGER,
                line_end INTEGER,
                complexity_score INTEGER,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def build_index(self, elements: List[CodeElement]) -> dict:
        """
        Build FTS5 index from code elements
        
        Args:
            elements: List of code elements to index
            
        Returns:
            Index metadata dictionary
        """
        start_time = datetime.now()
        indexed_count = 0
        
        for element in elements:
            try:
                self.index_element(element)
                indexed_count += 1
            except Exception as e:
                logger.error(f"Error indexing element {element.name}: {e}")
        
        self.conn.commit()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            'indexed_elements': indexed_count,
            'elapsed_time': elapsed,
            'db_path': str(self.db_path),
            'created_at': start_time.isoformat()
        }
    
    def index_element(self, element: CodeElement) -> None:
        """
        Index a single code element
        
        Args:
            element: Code element to index
        """
        element_id = f"{element.file_path.name}:{element.name}"
        
        # Insert into FTS5 index
        self.conn.execute("""
            INSERT INTO code_index (element_id, element_type, element_name, file_path, signature, code_content)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            element_id,
            element.type,
            element.name,
            str(element.file_path),
            element.signature,
            f"{element.signature} {element.docstring or ''}"
        ))
        
        # Insert metadata
        complexity_score = 0
        if element.complexity:
            if hasattr(element.complexity, 'cyclomatic_complexity'):
                complexity_score = element.complexity.cyclomatic_complexity
            else:
                complexity_score = element.complexity
        
        self.conn.execute("""
            INSERT OR REPLACE INTO element_metadata 
            (element_id, element_type, file_path, line_start, line_end, complexity_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            element_id,
            element.type,
            str(element.file_path),
            element.line_start,
            element.line_end,
            complexity_score
        ))
    
    def update_element(self, element: CodeElement) -> None:
        """
        Update indexed element
        
        Args:
            element: Code element with updates
        """
        element_id = f"{element.file_path.name}:{element.name}"
        
        # Delete old entry
        self.remove_element(element_id)
        
        # Re-index
        self.index_element(element)
    
    def remove_element(self, element_id: str) -> None:
        """
        Remove element from index
        
        Args:
            element_id: ID of element to remove
        """
        self.conn.execute("DELETE FROM code_index WHERE element_id = ?", (element_id,))
        self.conn.execute("DELETE FROM element_metadata WHERE element_id = ?", (element_id,))
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
