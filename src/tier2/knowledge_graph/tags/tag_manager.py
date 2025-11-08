"""
Tag Manager Module

Manages pattern tags for organization and filtering.

Tag Features:
    - Many-to-many pattern-tag associations
    - Tag-based filtering and search
    - Tag popularity tracking
    - Namespace-aware tag queries

Responsibilities:
    - Add/remove tags from patterns
    - Query patterns by tags
    - List all tags with counts
    - Tag validation and normalization

Performance Targets:
    - Add tag: <10ms
    - Query by tag: <40ms
    - List all tags: <30ms

Example:
    >>> from tier2.knowledge_graph.tags.tag_manager import TagManager
    >>> tag_mgr = TagManager(db)
    >>> tag_mgr.add_tag("tdd-pattern-001", "testing")
    >>> tag_mgr.add_tag("tdd-pattern-001", "best-practice")
    >>> patterns = tag_mgr.get_patterns_by_tag("testing")
"""

from typing import List, Dict, Any
import re
from datetime import datetime


class TagManager:
    """
    Manages pattern tags for organization.
    
    Provides tag-based organization and filtering for patterns
    in the knowledge graph.
    """
    
    def __init__(self, db):
        """
        Initialize Tag Manager.
        
        Args:
            db: DatabaseConnection instance
        """
        self.db = db
    
    def add_tag(self, pattern_id: str, tag: str) -> bool:
        """
        Add a tag to a pattern.
        
        Args:
            pattern_id: Pattern to tag
            tag: Tag string (normalized to lowercase)
        
        Returns:
            True if added, False if already exists
        
        Tag Normalization:
            - Convert to lowercase
            - Replace spaces with hyphens
            - Remove special characters
        
        Performance: <10ms
        """
        normalized = self._normalize_tag(tag)
        if not normalized:
            return False
        conn = self.db.get_connection()
        cursor = conn.cursor()
        # Ensure pattern exists
        cursor.execute("SELECT 1 FROM patterns WHERE pattern_id = ?", (pattern_id,))
        if cursor.fetchone() is None:
            return False
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO pattern_tags (pattern_id, tag) VALUES (?, ?)",
                (pattern_id, normalized)
            )
            added = cursor.rowcount > 0
            conn.commit()
            return added
        except Exception:
            conn.rollback()
            raise
    
    def remove_tag(self, pattern_id: str, tag: str) -> bool:
        """
        Remove a tag from a pattern.
        
        Args:
            pattern_id: Pattern to untag
            tag: Tag to remove
        
        Returns:
            True if removed, False if tag didn't exist
        
        Performance: <10ms
        """
        normalized = self._normalize_tag(tag)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM pattern_tags WHERE pattern_id = ? AND tag = ?",
            (pattern_id, normalized)
        )
        removed = cursor.rowcount > 0
        conn.commit()
        return removed
    
    def get_tags(self, pattern_id: str) -> List[str]:
        """
        Get all tags for a pattern.
        
        Args:
            pattern_id: Pattern to query
        
        Returns:
            List of tag strings
        
        Performance: <15ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tag FROM pattern_tags WHERE pattern_id = ? ORDER BY tag ASC",
            (pattern_id,)
        )
        return [r[0] for r in cursor.fetchall()]
    
    def get_patterns_by_tag(
        self,
        tag: str,
        min_confidence: float = 0.0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find patterns with a specific tag.
        
        Args:
            tag: Tag to search for
            min_confidence: Minimum confidence filter
            limit: Maximum results
        
        Returns:
            List of pattern dictionaries
        
        Performance: <40ms
        """
        normalized = self._normalize_tag(tag)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.pattern_id, p.title, p.content, p.pattern_type, p.confidence,
                   p.created_at, p.last_accessed, p.access_count, p.source, p.metadata,
                   p.is_pinned, p.scope, p.namespaces
            FROM patterns p
            JOIN pattern_tags t ON p.pattern_id = t.pattern_id
            WHERE t.tag = ? AND p.confidence >= ?
            ORDER BY p.confidence DESC, p.last_accessed DESC
            LIMIT ?
            """,
            (normalized, min_confidence, limit)
        )
        rows = cursor.fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            metadata = row[9]
            namespaces = row[12]
            # Defer JSON parsing until needed; caller can parse if required
            results.append({
                "pattern_id": row[0],
                "title": row[1],
                "content": row[2],
                "pattern_type": row[3],
                "confidence": row[4],
                "created_at": row[5],
                "last_accessed": row[6],
                "access_count": row[7],
                "source": row[8],
                "metadata": metadata,
                "is_pinned": bool(row[10]),
                "scope": row[11],
                "namespaces": namespaces,
                "tag": normalized
            })
        return results
    
    def list_all_tags(self) -> List[Dict[str, int]]:
        """
        List all tags with usage counts.
        
        Returns:
            List of dictionaries with:
                - tag: Tag string
                - count: Number of patterns with this tag
        
        Sorted by count (descending)
        
        Performance: <30ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tag, COUNT(*) as count FROM pattern_tags GROUP BY tag ORDER BY count DESC"
        )
        return [{"tag": r[0], "count": r[1]} for r in cursor.fetchall()]

    @staticmethod
    def _normalize_tag(tag: str) -> str:
        """Normalize a tag value.

        Steps:
            - Lowercase
            - Replace spaces with hyphens
            - Remove characters except a-z0-9- (collapse multiple hyphens)
        """
        tag = tag.strip().lower().replace(" ", "-")
        tag = re.sub(r"[^a-z0-9-]", "", tag)
        tag = re.sub(r"-+", "-", tag)
        return tag
