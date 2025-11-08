"""
CORTEX Tier 2: Pattern Cleanup System
Automated maintenance for knowledge graph patterns.

Features:
- Confidence decay for unused patterns
- Pattern consolidation (merge similar patterns)
- Scope-aware protection (never touch generic/CORTEX-core)
- Stale pattern detection and removal
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import logging

from .knowledge_graph import KnowledgeGraph, Pattern, PatternType


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CleanupStats:
    """Statistics from cleanup operations."""
    decayed_count: int = 0
    deleted_count: int = 0
    consolidated_count: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class PatternCleanup:
    """
    Pattern Cleanup System for automated knowledge graph maintenance.
    
    Key Principles:
    - NEVER modify scope='cortex' patterns (CORTEX core protection)
    - NEVER modify patterns in CORTEX-core namespace
    - Only affect application-specific patterns
    - Respect confidence thresholds
    - Log all cleanup actions for audit trail
    """
    
    # Cleanup thresholds
    DECAY_RATE = 0.01  # 1% per day
    DECAY_THRESHOLD_DAYS = 30  # Start decay after 30 days of inactivity
    MIN_CONFIDENCE = 0.3  # Delete patterns below this
    STALE_THRESHOLD_DAYS = 90  # Mark as stale after 90 days
    SIMILARITY_THRESHOLD = 0.70  # Consolidate if similarity > 70%
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize pattern cleanup system.
        
        Args:
            knowledge_graph: KnowledgeGraph instance to clean
        """
        self.kg = knowledge_graph
        self.db_path = knowledge_graph.db_path
    
    def apply_automatic_decay(self, protect_generic: bool = True) -> CleanupStats:
        """
        Apply confidence decay to application patterns only.
        
        Rules:
    - Generic patterns (scope='cortex') NEVER decay
        - CORTEX-core namespace patterns NEVER decay
        - Application patterns decay 1% per day after 30 days
        - Patterns below 0.3 confidence are deleted
        - Pinned patterns are protected
        
        Args:
            protect_generic: If True, skip all scope='cortex' patterns (default: True)
        
        Returns:
            CleanupStats with decayed and deleted counts
        """
        stats = CleanupStats()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now()
            decay_threshold_date = (now - timedelta(days=self.DECAY_THRESHOLD_DAYS)).isoformat()
            
            # First: Delete patterns already below minimum confidence
            delete_query = """
                SELECT pattern_id, confidence, scope, namespaces
                FROM patterns
                WHERE is_pinned = 0
                  AND confidence < ?
            """
            
            if protect_generic:
                delete_query += " AND scope != 'cortex'"
            
            cursor.execute(delete_query, (self.MIN_CONFIDENCE,))
            
            for pattern_id, confidence, scope, namespaces_json in cursor.fetchall():
                # Parse namespaces
                namespaces = json.loads(namespaces_json) if namespaces_json else []
                
                # Extra protection: Never touch CORTEX-core namespace
                if "CORTEX-core" in namespaces:
                    logger.info(f"Skipping pattern {pattern_id}: Protected by CORTEX-core namespace")
                    continue
                
                # Delete pattern
                cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (pattern_id,))
                stats.deleted_count += 1
                
                # Log deletion
                cursor.execute("""
                    INSERT INTO confidence_decay_log (pattern_id, old_confidence, new_confidence, reason)
                    VALUES (?, ?, ?, ?)
                """, (pattern_id, confidence, 0.0, "Auto-deleted: Already below minimum confidence"))
                
                logger.info(f"Deleted pattern {pattern_id}: confidence {confidence:.2f} (below {self.MIN_CONFIDENCE})")
            
            # Second: Apply decay to old patterns
            query = """
                SELECT pattern_id, confidence, last_accessed, scope, namespaces
                FROM patterns
                WHERE is_pinned = 0
                  AND last_accessed < ?
            """
            
            if protect_generic:
                query += " AND scope != 'cortex'"
            
            cursor.execute(query, (decay_threshold_date,))
            
            for pattern_id, confidence, last_accessed, scope, namespaces_json in cursor.fetchall():
                # Parse namespaces
                namespaces = json.loads(namespaces_json) if namespaces_json else []
                
                # Extra protection: Never touch CORTEX-core namespace
                if "CORTEX-core" in namespaces:
                    logger.info(f"Skipping pattern {pattern_id}: Protected by CORTEX-core namespace")
                    continue
                
                # Calculate decay
                last_access_date = datetime.fromisoformat(last_accessed)
                days_since_access = (now - last_access_date).days
                days_to_decay = max(0, days_since_access - self.DECAY_THRESHOLD_DAYS)
                
                if days_to_decay == 0:
                    continue
                
                # Apply decay
                decay_amount = self.DECAY_RATE * days_to_decay
                new_confidence = max(0.0, confidence - decay_amount)
                
                if new_confidence < self.MIN_CONFIDENCE:
                    # Delete pattern
                    cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (pattern_id,))
                    stats.deleted_count += 1
                    
                    # Log deletion
                    cursor.execute("""
                        INSERT INTO confidence_decay_log (pattern_id, old_confidence, new_confidence, reason)
                        VALUES (?, ?, ?, ?)
                    """, (pattern_id, confidence, new_confidence, f"Auto-deleted: Decayed below minimum ({days_to_decay} days inactive)"))
                    
                    logger.info(f"Deleted pattern {pattern_id}: confidence {confidence:.2f} → {new_confidence:.2f} (below {self.MIN_CONFIDENCE})")
                else:
                    # Update confidence
                    cursor.execute("""
                        UPDATE patterns SET confidence = ? WHERE pattern_id = ?
                    """, (new_confidence, pattern_id))
                    stats.decayed_count += 1
                    
                    # Log decay
                    cursor.execute("""
                        INSERT INTO confidence_decay_log (pattern_id, old_confidence, new_confidence, reason)
                        VALUES (?, ?, ?, ?)
                    """, (pattern_id, confidence, new_confidence, f"Auto-decayed: {days_to_decay} days since last access"))
                    
                    logger.debug(f"Decayed pattern {pattern_id}: {confidence:.2f} → {new_confidence:.2f}")
            
            conn.commit()
        
        except Exception as e:
            stats.errors.append(f"Decay error: {str(e)}")
            logger.error(f"Error during decay: {e}")
            conn.rollback()
        
        finally:
            conn.close()
        
        return stats
    
    def consolidate_similar_patterns(
        self,
        namespace: Optional[str] = None,
        dry_run: bool = False
    ) -> CleanupStats:
        """
        Merge similar patterns to reduce duplication.
        
        Rules:
        - Only consolidate patterns with same scope and overlapping namespaces
        - Never consolidate generic patterns (they're immutable)
        - Preserve highest confidence and most recent evidence
        - Combine access counts
        - Keep all tags
        
        Args:
            namespace: Limit consolidation to specific namespace (optional)
            dry_run: If True, report what would be consolidated without changes
        
        Returns:
            CleanupStats with consolidated count
        """
        stats = CleanupStats()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get application patterns only (generic never consolidated)
            query = """
                SELECT pattern_id, title, content, pattern_type, confidence,
                       created_at, last_accessed, access_count, metadata, namespaces
                FROM patterns
                WHERE scope = 'application'
            """
            
            if namespace:
                query += f" AND namespaces LIKE '%\"{namespace}\"%'"
            
            query += " ORDER BY pattern_type, confidence DESC"
            
            cursor.execute(query)
            patterns = cursor.fetchall()
            
            # Group by pattern type for comparison
            by_type: Dict[str, List[Tuple]] = {}
            for p in patterns:
                ptype = p[3]  # pattern_type
                if ptype not in by_type:
                    by_type[ptype] = []
                by_type[ptype].append(p)
            
            # Find and consolidate similar patterns within each type
            for ptype, pattern_list in by_type.items():
                i = 0
                while i < len(pattern_list):
                    p1 = pattern_list[i]
                    p1_id, p1_title, p1_content = p1[0], p1[1], p1[2]
                    
                    j = i + 1
                    while j < len(pattern_list):
                        p2 = pattern_list[j]
                        p2_id, p2_title, p2_content = p2[0], p2[1], p2[2]
                        
                        # Calculate similarity (simple Jaccard-style)
                        similarity = self._calculate_similarity(p1_title, p1_content, p2_title, p2_content)
                        
                        if similarity >= self.SIMILARITY_THRESHOLD:
                            # Consolidate p2 into p1
                            if not dry_run:
                                self._merge_patterns(cursor, p1, p2)
                            
                            stats.consolidated_count += 1
                            logger.info(f"Consolidated {p2_id} → {p1_id} (similarity: {similarity:.2f})")
                            
                            # Remove p2 from list
                            pattern_list.pop(j)
                        else:
                            j += 1
                    
                    i += 1
            
            if not dry_run:
                conn.commit()
            else:
                logger.info(f"DRY RUN: Would consolidate {stats.consolidated_count} patterns")
        
        except Exception as e:
            stats.errors.append(f"Consolidation error: {str(e)}")
            logger.error(f"Error during consolidation: {e}")
            conn.rollback()
        
        finally:
            conn.close()
        
        return stats
    
    def remove_stale_patterns(
        self,
        stale_days: int = 90,
        protect_generic: bool = True
    ) -> CleanupStats:
        """
        Remove patterns not accessed in a long time.
        
        Args:
            stale_days: Days of inactivity to consider stale (default: 90)
            protect_generic: Never remove generic patterns (default: True)
        
        Returns:
            CleanupStats with deleted count
        """
        stats = CleanupStats()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            stale_threshold = (datetime.now() - timedelta(days=stale_days)).isoformat()
            
            query = """
                DELETE FROM patterns
                WHERE last_accessed < ?
                  AND is_pinned = 0
                  AND confidence < ?
            """
            
            if protect_generic:
                query += " AND scope != 'cortex'"
            
            cursor.execute(query, (stale_threshold, self.MIN_CONFIDENCE))
            stats.deleted_count = cursor.rowcount
            
            conn.commit()
            logger.info(f"Removed {stats.deleted_count} stale patterns (>{stale_days} days inactive)")
        
        except Exception as e:
            stats.errors.append(f"Stale removal error: {str(e)}")
            logger.error(f"Error removing stale patterns: {e}")
            conn.rollback()
        
        finally:
            conn.close()
        
        return stats
    
    def optimize_database(self) -> bool:
        """
        Optimize database performance.
        
        - Run VACUUM to reclaim space
        - Rebuild FTS5 index
        - Analyze query performance
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vacuum to reclaim space
            logger.info("Running VACUUM...")
            cursor.execute("VACUUM")
            
            # Rebuild FTS5 index
            logger.info("Rebuilding FTS5 index...")
            cursor.execute("INSERT INTO pattern_fts(pattern_fts) VALUES('rebuild')")
            
            # Analyze for query optimization
            logger.info("Analyzing database...")
            cursor.execute("ANALYZE")
            
            conn.commit()
            conn.close()
            
            logger.info("Database optimization complete")
            return True
        
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return False
    
    def get_cleanup_recommendations(self) -> Dict[str, Any]:
        """
        Analyze patterns and recommend cleanup actions.
        
        Returns:
            Dict with recommendations for decay, consolidation, deletion
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        recommendations = {
            'decay_candidates': 0,
            'stale_candidates': 0,
            'low_confidence_candidates': 0,
            'consolidation_candidates': 0,
            'total_patterns': 0,
            'generic_patterns': 0,
            'application_patterns': 0
        }
        
        try:
            # Total patterns
            cursor.execute("SELECT COUNT(*) FROM patterns")
            recommendations['total_patterns'] = cursor.fetchone()[0]
            
            # Generic vs application
            cursor.execute("SELECT COUNT(*) FROM patterns WHERE scope = 'cortex'")
            recommendations['generic_patterns'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM patterns WHERE scope = 'application'")
            recommendations['application_patterns'] = cursor.fetchone()[0]
            
            # Decay candidates (application patterns not accessed in 30+ days)
            decay_threshold = (datetime.now() - timedelta(days=self.DECAY_THRESHOLD_DAYS)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM patterns
                WHERE scope = 'application'
                  AND last_accessed < ?
                  AND is_pinned = 0
            """, (decay_threshold,))
            recommendations['decay_candidates'] = cursor.fetchone()[0]
            
            # Stale candidates (90+ days inactive)
            stale_threshold = (datetime.now() - timedelta(days=self.STALE_THRESHOLD_DAYS)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM patterns
                WHERE scope = 'application'
                  AND last_accessed < ?
                  AND is_pinned = 0
            """, (stale_threshold,))
            recommendations['stale_candidates'] = cursor.fetchone()[0]
            
            # Low confidence candidates
            cursor.execute("""
                SELECT COUNT(*) FROM patterns
                WHERE scope = 'application'
                  AND confidence < ?
                  AND is_pinned = 0
            """, (self.MIN_CONFIDENCE,))
            recommendations['low_confidence_candidates'] = cursor.fetchone()[0]
        
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
        
        finally:
            conn.close()
        
        return recommendations
    
    def _calculate_similarity(
        self,
        title1: str,
        content1: str,
        title2: str,
        content2: str
    ) -> float:
        """
        Calculate similarity between two patterns (Jaccard similarity).
        
        Args:
            title1, content1: First pattern
            title2, content2: Second pattern
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Combine title and content into word sets
        words1 = set((title1 + " " + content1).lower().split())
        words2 = set((title2 + " " + content2).lower().split())
        
        # Jaccard similarity: intersection / union
        if not words1 and not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _merge_patterns(self, cursor: sqlite3.Cursor, p1: Tuple, p2: Tuple):
        """
        Merge two patterns (p2 into p1).
        
        Args:
            cursor: Database cursor
            p1: Pattern to keep (tuple from SELECT)
            p2: Pattern to merge and delete
        """
        p1_id, p1_title, p1_content, p1_type, p1_confidence = p1[0], p1[1], p1[2], p1[3], p1[4]
        p1_created, p1_accessed, p1_count, p1_meta, p1_ns = p1[5], p1[6], p1[7], p1[8], p1[9]
        
        p2_id, p2_title, p2_content, p2_type, p2_confidence = p2[0], p2[1], p2[2], p2[3], p2[4]
        p2_created, p2_accessed, p2_count, p2_meta, p2_ns = p2[5], p2[6], p2[7], p2[8], p2[9]
        
        # Merge confidence (weighted average by access count)
        total_count = p1_count + p2_count
        if total_count > 0:
            new_confidence = (p1_confidence * p1_count + p2_confidence * p2_count) / total_count
        else:
            new_confidence = max(p1_confidence, p2_confidence)
        
        # Keep most recent access time
        new_accessed = max(p1_accessed, p2_accessed)
        
        # Combine access counts
        new_count = p1_count + p2_count
        
        # Merge metadata
        p1_metadata = json.loads(p1_meta) if p1_meta else {}
        p2_metadata = json.loads(p2_meta) if p2_meta else {}
        merged_metadata = {**p1_metadata, **p2_metadata, "merged_from": p2_id}
        
        # Merge namespaces (union)
        p1_namespaces = set(json.loads(p1_ns) if p1_ns else [])
        p2_namespaces = set(json.loads(p2_ns) if p2_ns else [])
        merged_namespaces = list(p1_namespaces | p2_namespaces)
        
        # Update p1 with merged data
        cursor.execute("""
            UPDATE patterns
            SET confidence = ?,
                last_accessed = ?,
                access_count = ?,
                metadata = ?,
                namespaces = ?
            WHERE pattern_id = ?
        """, (
            new_confidence,
            new_accessed,
            new_count,
            json.dumps(merged_metadata),
            json.dumps(merged_namespaces),
            p1_id
        ))
        
        # Copy tags from p2 to p1
        cursor.execute("""
            INSERT OR IGNORE INTO pattern_tags (pattern_id, tag)
            SELECT ?, tag FROM pattern_tags WHERE pattern_id = ?
        """, (p1_id, p2_id))
        
        # Delete p2
        cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (p2_id,))
        
        logger.debug(f"Merged {p2_id} into {p1_id}: confidence {p1_confidence:.2f} → {new_confidence:.2f}")
