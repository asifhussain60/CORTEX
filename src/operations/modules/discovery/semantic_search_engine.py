"""
Semantic search engine with FTS5 ranking
"""
import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .models import CodeElement

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with ranking"""
    element_name: str
    element_type: str
    file_path: Path
    line_start: int
    line_end: int
    score: float
    snippet: str
    rank: int


class SemanticSearchEngine:
    """Search semantic index with ranking"""
    
    def __init__(self, db_path: Path):
        """
        Initialize search engine
        
        Args:
            db_path: Path to SQLite FTS5 database
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        if db_path.exists():
            self.conn = sqlite3.connect(str(db_path))
            self.conn.row_factory = sqlite3.Row
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search index with ranking
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of ranked search results
        """
        if not self.conn:
            return []
        
        cursor = self.conn.execute("""
            SELECT 
                ci.element_id,
                ci.element_name,
                ci.element_type,
                em.file_path,
                em.line_start,
                em.line_end,
                ci.signature,
                rank
            FROM code_index ci
            JOIN element_metadata em ON ci.element_id = em.element_id
            WHERE code_index MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        
        results = []
        rank = 1
        for row in cursor:
            results.append(SearchResult(
                element_name=row['element_name'],
                element_type=row['element_type'],
                file_path=Path(row['file_path']),
                line_start=row['line_start'],
                line_end=row['line_end'],
                score=abs(row['rank']),  # FTS5 rank is negative
                snippet=row['signature'],
                rank=rank
            ))
            rank += 1
        
        return results
    
    def search_by_type(self, query: str, element_type: str, limit: int = 10) -> List[SearchResult]:
        """
        Search by element type
        
        Args:
            query: Search query
            element_type: Filter by type (class, function, method)
            limit: Maximum results
            
        Returns:
            List of filtered search results
        """
        if not self.conn:
            return []
        
        cursor = self.conn.execute("""
            SELECT 
                ci.element_id,
                ci.element_name,
                ci.element_type,
                em.file_path,
                em.line_start,
                em.line_end,
                ci.signature,
                rank
            FROM code_index ci
            JOIN element_metadata em ON ci.element_id = em.element_id
            WHERE code_index MATCH ? AND ci.element_type = ?
            ORDER BY rank
            LIMIT ?
        """, (query, element_type, limit))
        
        results = []
        rank = 1
        for row in cursor:
            results.append(SearchResult(
                element_name=row['element_name'],
                element_type=row['element_type'],
                file_path=Path(row['file_path']),
                line_start=row['line_start'],
                line_end=row['line_end'],
                score=abs(row['rank']),
                snippet=row['signature'],
                rank=rank
            ))
            rank += 1
        
        return results
    
    def find_symbol(self, symbol_name: str) -> Optional[SearchResult]:
        """
        Find symbol by exact name
        
        Args:
            symbol_name: Exact symbol name
            
        Returns:
            Search result or None
        """
        if not self.conn:
            return None
        
        cursor = self.conn.execute("""
            SELECT 
                ci.element_id,
                ci.element_name,
                ci.element_type,
                em.file_path,
                em.line_start,
                em.line_end,
                ci.signature
            FROM code_index ci
            JOIN element_metadata em ON ci.element_id = em.element_id
            WHERE ci.element_name = ?
            LIMIT 1
        """, (symbol_name,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return SearchResult(
            element_name=row['element_name'],
            element_type=row['element_type'],
            file_path=Path(row['file_path']),
            line_start=row['line_start'],
            line_end=row['line_end'],
            score=1.0,
            snippet=row['signature'],
            rank=1
        )
    
    def find_references(self, symbol_name: str) -> List[SearchResult]:
        """
        Find references to symbol
        
        Args:
            symbol_name: Symbol to find references to
            
        Returns:
            List of elements referencing the symbol
        """
        # Simplified: search for symbol name in code content
        return self.search(symbol_name, limit=50)
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
