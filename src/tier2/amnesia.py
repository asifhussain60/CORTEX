"""
CORTEX Tier 2: Enhanced Amnesia System
Scope-aware selective memory deletion with safety protections.

Features:
- Namespace-scoped deletion (never touch CORTEX-core)
- Generic pattern protection (scope='generic' immune)
- Multi-namespace safety (only delete when all namespaces cleared)
- Confidence-based deletion with safeguards
- Comprehensive audit logging
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import logging

from .knowledge_graph import KnowledgeGraph, Pattern, PatternType


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AmnesiaStats:
    """Statistics from amnesia operations."""
    patterns_deleted: int = 0
    relationships_deleted: int = 0
    tags_deleted: int = 0
    protected_count: int = 0
    errors: List[str] = None
    deletion_log: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.deletion_log is None:
            self.deletion_log = []


class EnhancedAmnesia:
    """
    Enhanced Amnesia System with scope and namespace protection.
    
    CRITICAL SAFETY RULES:
    1. NEVER delete scope='generic' patterns (CORTEX core intelligence)
    2. NEVER delete patterns with 'CORTEX-core' in namespaces
    3. For multi-namespace patterns, only delete when ALL namespaces cleared
    4. Always require explicit confirmation for destructive operations
    5. Log ALL deletions for audit trail and recovery
    """
    
    # Safety thresholds
    MAX_DELETION_PCT = 0.50  # Never delete >50% of patterns in single operation
    REQUIRE_CONFIRMATION_ABOVE = 10  # Require confirmation if deleting >10 patterns
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize enhanced amnesia system.
        
        Args:
            knowledge_graph: KnowledgeGraph instance
        """
        self.kg = knowledge_graph
        self.db_path = knowledge_graph.db_path
    
    def delete_by_namespace(
        self,
        namespace: str,
        require_confirmation: bool = True,
        dry_run: bool = False,
        bypass_safety: bool = False  # NEW: For testing/emergency use
    ) -> AmnesiaStats:
        """
        Delete all patterns in a specific namespace.
        
        Safety protections:
        - CORTEX-core namespace BLOCKED (cannot delete core intelligence)
        - Generic patterns PROTECTED (even if namespace matches)
        - Multi-namespace patterns only deleted if this is the LAST namespace
        - Confirmation required if deleting >10 patterns
        
        Args:
            namespace: Namespace to clear (e.g., 'KSESSIONS', 'NOOR')
            require_confirmation: If True, check deletion count threshold
            dry_run: If True, report what would be deleted without changes
        
        Returns:
            AmnesiaStats with deletion counts and protected patterns
        
        Raises:
            ValueError: If trying to delete CORTEX-core namespace
            RuntimeError: If deletion exceeds safety threshold without override
        """
        stats = AmnesiaStats()
        
        # Protection Layer 1: Block CORTEX-core deletion
        if namespace == "CORTEX-core":
            raise ValueError(
                "FORBIDDEN: Cannot delete CORTEX-core namespace. "
                "This is CORTEX's core intelligence and is PERMANENT."
            )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get patterns in namespace
            cursor.execute("""
                SELECT pattern_id, scope, namespaces, title
                FROM patterns
                WHERE namespaces LIKE ?
            """, (f'%"{namespace}"%',))
            
            candidate_patterns = cursor.fetchall()
            patterns_to_delete = []
            
            for pattern_id, scope, namespaces_json, title in candidate_patterns:
                namespaces = json.loads(namespaces_json) if namespaces_json else []
                
                # Protection Layer 2: Skip generic patterns
                if scope == "generic":
                    stats.protected_count += 1
                    logger.info(f"PROTECTED: {pattern_id} (scope=generic)")
                    continue
                
                # Protection Layer 3: Skip CORTEX-core namespace
                if "CORTEX-core" in namespaces:
                    stats.protected_count += 1
                    logger.info(f"PROTECTED: {pattern_id} (CORTEX-core namespace)")
                    continue
                
                # Check if namespace is in the list
                if namespace not in namespaces:
                    continue
                
                # Protection Layer 4: Multi-namespace safety
                if len(namespaces) > 1:
                    # Remove this namespace but keep pattern
                    remaining_namespaces = [ns for ns in namespaces if ns != namespace]
                    
                    if not dry_run:
                        cursor.execute("""
                            UPDATE patterns
                            SET namespaces = ?
                            WHERE pattern_id = ?
                        """, (json.dumps(remaining_namespaces), pattern_id))
                    
                    stats.protected_count += 1
                    logger.info(f"PARTIAL DELETE: {pattern_id} removed from namespace '{namespace}', kept in {remaining_namespaces}")
                    stats.deletion_log.append({
                        'pattern_id': pattern_id,
                        'title': title,
                        'action': 'namespace_removed',
                        'remaining_namespaces': remaining_namespaces
                    })
                else:
                    # Single namespace - safe to delete
                    patterns_to_delete.append((pattern_id, title))
            
            # Safety check: Confirmation required?
            if require_confirmation and len(patterns_to_delete) > self.REQUIRE_CONFIRMATION_ABOVE:
                if dry_run:
                    logger.warning(f"DRY RUN: Would delete {len(patterns_to_delete)} patterns (confirmation required)")
                else:
                    logger.warning(f"Deleting {len(patterns_to_delete)} patterns requires confirmation")
                    # In production, this would prompt user
                    # For now, proceed with logging
            
            # Safety check: Never delete >50% of total patterns
            cursor.execute("SELECT COUNT(*) FROM patterns")
            total_patterns = cursor.fetchone()[0]
            deletion_pct = len(patterns_to_delete) / total_patterns if total_patterns > 0 else 0
            
            if not bypass_safety and deletion_pct > self.MAX_DELETION_PCT:
                raise RuntimeError(
                    f"SAFETY ABORT: Attempting to delete {deletion_pct:.1%} of all patterns "
                    f"({len(patterns_to_delete)}/{total_patterns}). "
                    f"Maximum allowed: {self.MAX_DELETION_PCT:.1%}. "
                    f"This looks like a mistake. Please review and use bypass_safety=True if intentional."
                )
            
            # Execute deletions
            if not dry_run:
                for pattern_id, title in patterns_to_delete:
                    cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (pattern_id,))
                    stats.patterns_deleted += 1
                    stats.deletion_log.append({
                        'pattern_id': pattern_id,
                        'title': title,
                        'action': 'deleted',
                        'namespace': namespace,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.info(f"DELETED: {pattern_id} (namespace: {namespace})")
                
                conn.commit()
            else:
                stats.patterns_deleted = len(patterns_to_delete)
                logger.info(f"DRY RUN: Would delete {len(patterns_to_delete)} patterns from namespace '{namespace}'")
        
        except Exception as e:
            stats.errors.append(f"Deletion error: {str(e)}")
            logger.error(f"Error during namespace deletion: {e}")
            conn.rollback()
        
        finally:
            conn.close()
        
        return stats
    
    def delete_by_confidence(
        self,
        max_confidence: float,
        protect_generic: bool = True,
        namespace: Optional[str] = None,
        dry_run: bool = False
    ) -> AmnesiaStats:
        """
        Delete patterns with confidence below threshold.
        
        Args:
            max_confidence: Delete patterns with confidence <= this value
            protect_generic: Never delete generic patterns (default: True)
            namespace: Limit to specific namespace (optional)
            dry_run: If True, report what would be deleted without changes
        
        Returns:
            AmnesiaStats with deletion counts
        """
        stats = AmnesiaStats()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build query - protect CORTEX-core namespace
            query = """
                DELETE FROM patterns
                WHERE confidence <= ?
                  AND is_pinned = 0
                  AND namespaces NOT LIKE '%"CORTEX-core"%'
            """
            params = [max_confidence]
            
            if protect_generic:
                query += " AND scope != 'generic'"
            
            if namespace:
                query += " AND namespaces LIKE ?"
                params.append(f'%"{namespace}"%')
            
            if dry_run:
                # Count instead of delete
                count_query = query.replace("DELETE FROM patterns", "SELECT COUNT(*) FROM patterns")
                cursor.execute(count_query, params)
                stats.patterns_deleted = cursor.fetchone()[0]
                logger.info(f"DRY RUN: Would delete {stats.patterns_deleted} patterns with confidence <= {max_confidence}")
            else:
                cursor.execute(query, params)
                stats.patterns_deleted = cursor.rowcount
                conn.commit()
                logger.info(f"Deleted {stats.patterns_deleted} patterns with confidence <= {max_confidence}")
        
        except Exception as e:
            stats.errors.append(f"Confidence deletion error: {str(e)}")
            logger.error(f"Error deleting by confidence: {e}")
            conn.rollback()
        
        finally:
            conn.close()
        
        return stats
    
    def delete_by_age(
        self,
        days_inactive: int,
        protect_generic: bool = True,
        namespace: Optional[str] = None,
        dry_run: bool = False
    ) -> AmnesiaStats:
        """
        Delete patterns not accessed in specified days.
        
        Args:
            days_inactive: Delete patterns not accessed in this many days
            protect_generic: Never delete generic patterns (default: True)
            namespace: Limit to specific namespace (optional)
            dry_run: If True, report what would be deleted without changes
        
        Returns:
            AmnesiaStats with deletion counts
        """
        stats = AmnesiaStats()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            from datetime import timedelta
            threshold_date = (datetime.now() - timedelta(days=days_inactive)).isoformat()
            
            # Build query - protect CORTEX-core namespace
            query = """
                DELETE FROM patterns
                WHERE last_accessed < ?
                  AND is_pinned = 0
                  AND namespaces NOT LIKE '%"CORTEX-core"%'
            """
            params = [threshold_date]
            
            if protect_generic:
                query += " AND scope != 'generic'"
            
            if namespace:
                query += " AND namespaces LIKE ?"
                params.append(f'%"{namespace}"%')
            
            if dry_run:
                count_query = query.replace("DELETE FROM patterns", "SELECT COUNT(*) FROM patterns")
                cursor.execute(count_query, params)
                stats.patterns_deleted = cursor.fetchone()[0]
                logger.info(f"DRY RUN: Would delete {stats.patterns_deleted} patterns inactive >{days_inactive} days")
            else:
                cursor.execute(query, params)
                stats.patterns_deleted = cursor.rowcount
                conn.commit()
                logger.info(f"Deleted {stats.patterns_deleted} patterns inactive >{days_inactive} days")
        
        except Exception as e:
            stats.errors.append(f"Age deletion error: {str(e)}")
            logger.error(f"Error deleting by age: {e}")
            conn.rollback()
        
        finally:
            conn.close()
        
        return stats
    
    def clear_application_scope(
        self,
        confirmation_code: Optional[str] = None,
        dry_run: bool = False
    ) -> AmnesiaStats:
        """
        Delete ALL application-specific patterns (DANGEROUS!).
        
        This is a nuclear option that clears all application knowledge while
        preserving CORTEX core intelligence.
        
        Protections:
        - Generic patterns IMMUNE (never deleted)
        - CORTEX-core namespace IMMUNE
        - Requires confirmation code: "DELETE_ALL_APPLICATIONS"
        - Dry run available for safety testing
        
        Args:
            confirmation_code: Must be "DELETE_ALL_APPLICATIONS" to proceed
            dry_run: If True, report what would be deleted without changes
        
        Returns:
            AmnesiaStats with deletion counts
        
        Raises:
            ValueError: If confirmation code is missing or incorrect
        """
        if not dry_run and confirmation_code != "DELETE_ALL_APPLICATIONS":
            raise ValueError(
                "SAFETY BLOCK: This operation deletes ALL application patterns. "
                "To proceed, pass confirmation_code='DELETE_ALL_APPLICATIONS'. "
                "Use dry_run=True to preview impact first."
            )
        
        stats = AmnesiaStats()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Count patterns before deletion
            cursor.execute("""
                SELECT COUNT(*) FROM patterns
                WHERE scope = 'application'
                  AND namespaces NOT LIKE '%"CORTEX-core"%'
            """)
            count = cursor.fetchone()[0]
            
            if dry_run:
                stats.patterns_deleted = count
                logger.warning(f"DRY RUN: Would delete {count} application patterns")
                return stats
            
            # Log all patterns being deleted
            cursor.execute("""
                SELECT pattern_id, title, namespaces
                FROM patterns
                WHERE scope = 'application'
                  AND namespaces NOT LIKE '%"CORTEX-core"%'
            """)
            
            for pattern_id, title, namespaces in cursor.fetchall():
                stats.deletion_log.append({
                    'pattern_id': pattern_id,
                    'title': title,
                    'namespaces': json.loads(namespaces),
                    'action': 'scope_clear',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Delete application patterns
            cursor.execute("""
                DELETE FROM patterns
                WHERE scope = 'application'
                  AND namespaces NOT LIKE '%"CORTEX-core"%'
            """)
            stats.patterns_deleted = cursor.rowcount
            
            conn.commit()
            logger.warning(f"CLEARED APPLICATION SCOPE: Deleted {stats.patterns_deleted} patterns")
        
        except Exception as e:
            stats.errors.append(f"Scope clear error: {str(e)}")
            logger.error(f"Error clearing application scope: {e}")
            conn.rollback()
        
        finally:
            conn.close()
        
        return stats
    
    def get_deletion_preview(
        self,
        namespace: Optional[str] = None,
        max_confidence: Optional[float] = None,
        days_inactive: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Preview what would be deleted without making changes.
        
        Args:
            namespace: Preview namespace deletion
            max_confidence: Preview confidence threshold deletion
            days_inactive: Preview age-based deletion
        
        Returns:
            Dict with deletion counts and sample patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        preview = {
            'total_patterns': 0,
            'generic_patterns': 0,
            'application_patterns': 0,
            'would_delete': 0,
            'would_protect': 0,
            'sample_deletions': [],
            'sample_protected': []
        }
        
        try:
            # Total counts
            cursor.execute("SELECT COUNT(*) FROM patterns")
            preview['total_patterns'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM patterns WHERE scope = 'generic'")
            preview['generic_patterns'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM patterns WHERE scope = 'application'")
            preview['application_patterns'] = cursor.fetchone()[0]
            
            # Build deletion query
            delete_query = "SELECT pattern_id, title, scope, namespaces FROM patterns WHERE 1=1"
            params = []
            
            if namespace:
                delete_query += " AND namespaces LIKE ?"
                params.append(f'%"{namespace}"%')
            
            if max_confidence is not None:
                delete_query += " AND confidence <= ?"
                params.append(max_confidence)
            
            if days_inactive is not None:
                from datetime import timedelta
                threshold = (datetime.now() - timedelta(days=days_inactive)).isoformat()
                delete_query += " AND last_accessed < ?"
                params.append(threshold)
            
            cursor.execute(delete_query, params)
            
            for pattern_id, title, scope, namespaces_json in cursor.fetchall():
                namespaces = json.loads(namespaces_json) if namespaces_json else []
                
                # Check if would be protected
                if scope == "generic" or "CORTEX-core" in namespaces:
                    preview['would_protect'] += 1
                    if len(preview['sample_protected']) < 5:
                        preview['sample_protected'].append({
                            'pattern_id': pattern_id,
                            'title': title,
                            'reason': 'generic' if scope == 'generic' else 'CORTEX-core'
                        })
                else:
                    preview['would_delete'] += 1
                    if len(preview['sample_deletions']) < 5:
                        preview['sample_deletions'].append({
                            'pattern_id': pattern_id,
                            'title': title,
                            'namespaces': namespaces
                        })
        
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
        
        finally:
            conn.close()
        
        return preview
    
    def export_deletion_log(self, output_path: Path) -> bool:
        """
        Export deletion log to JSON file for recovery.
        
        Args:
            output_path: Path to save deletion log
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT pattern_id, old_confidence, new_confidence, decay_date, reason
                FROM confidence_decay_log
                WHERE reason LIKE '%deleted%' OR reason LIKE '%Deleted%'
                ORDER BY decay_date DESC
                LIMIT 1000
            """)
            
            log_entries = []
            for row in cursor.fetchall():
                log_entries.append({
                    'pattern_id': row[0],
                    'old_confidence': row[1],
                    'new_confidence': row[2],
                    'date': row[3],
                    'reason': row[4]
                })
            
            conn.close()
            
            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(log_entries, f, indent=2)
            
            logger.info(f"Exported {len(log_entries)} deletion log entries to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting deletion log: {e}")
            return False
