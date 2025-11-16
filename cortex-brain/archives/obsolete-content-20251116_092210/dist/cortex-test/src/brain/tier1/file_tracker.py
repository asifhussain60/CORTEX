"""
CORTEX Brain - Tier 1: FileTracker

Purpose: Track file modifications per conversation and detect co-modification patterns

Features:
- Track which files are modified in each conversation
- Detect files frequently modified together (co-modification)
- Build file relationship graph for Tier 2 learning
- Support file categorization (source, tests, config, docs)
- Enable file-based conversation retrieval

Use Cases:
- "Show me conversations about HostControlPanel.razor"
- "What files are usually modified with this file?"
- "Which conversations touched the authentication system?"

Author: CORTEX Development Team
Version: 1.0.0
"""

import sqlite3
from typing import List, Dict, Any, Set, Tuple, Optional
from pathlib import Path
from datetime import datetime
from collections import Counter


class FileTracker:
    """
    Tracks file modifications and relationships across conversations.
    
    Builds co-modification patterns for Tier 2 knowledge graph.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize FileTracker
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ========================================================================
    # FILE TRACKING OPERATIONS
    # ========================================================================
    
    def track_files(
        self,
        conversation_id: str,
        filepaths: List[str],
        categorize: bool = True
    ) -> None:
        """
        Track files modified in a conversation
        
        Args:
            conversation_id: Conversation UUID
            filepaths: List of file paths
            categorize: Whether to categorize files by type
        
        Raises:
            ValueError: If conversation not found
        """
        import json
        from .entity_extractor import EntityExtractor
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Verify conversation exists
            cursor.execute("SELECT 1 FROM tier1_conversations WHERE conversation_id = ?", (conversation_id,))
            if not cursor.fetchone():
                raise ValueError(f"Conversation not found: {conversation_id}")
            
            # Deduplicate filepaths
            unique_files = list(set(filepaths))
            
            # Categorize if requested
            if categorize:
                extractor = EntityExtractor()
                categories = extractor.categorize_files(unique_files)
            else:
                categories = None
            
            # Update conversation's related_files
            cursor.execute("""
                UPDATE tier1_conversations
                SET related_files = ?
                WHERE conversation_id = ?
            """, (json.dumps(unique_files), conversation_id))
            
            conn.commit()
        
        finally:
            conn.close()
    
    def get_conversation_files(self, conversation_id: str) -> List[str]:
        """
        Get all files associated with a conversation
        
        Args:
            conversation_id: Conversation UUID
        
        Returns:
            List of file paths
        """
        import json
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT related_files FROM tier1_conversations
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            if not row or not row[0]:
                return []
            
            return json.loads(row[0])
        
        finally:
            conn.close()
    
    def find_conversations_by_file(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Find all conversations that modified a specific file
        
        Args:
            filepath: File path to search for
        
        Returns:
            List of conversation dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM tier1_conversations
                WHERE related_files LIKE ?
                ORDER BY created_at DESC
            """, (f'%{filepath}%',))
            
            return [dict(row) for row in cursor.fetchall()]
        
        finally:
            conn.close()
    
    # ========================================================================
    # CO-MODIFICATION DETECTION
    # ========================================================================
    
    def detect_co_modifications(
        self,
        min_occurrences: int = 2,
        min_confidence: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Detect files frequently modified together
        
        Args:
            min_occurrences: Minimum co-modification count to report
            min_confidence: Minimum confidence score (0.0-1.0)
        
        Returns:
            List of co-modification patterns:
            [{
                'file_a': 'path/to/file1.py',
                'file_b': 'path/to/file2.py',
                'co_modification_count': 5,
                'confidence': 0.83,
                'conversations': ['conv-abc', 'conv-def', ...]
            }, ...]
        """
        import json
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get all conversations with related files
            cursor.execute("""
                SELECT conversation_id, related_files FROM tier1_conversations
                WHERE related_files IS NOT NULL AND related_files != '[]'
            """)
            
            # Build co-modification matrix
            co_modifications: Dict[Tuple[str, str], List[str]] = {}
            file_counts: Counter = Counter()
            
            for row in cursor.fetchall():
                conv_id = row[0]
                files = json.loads(row[1])
                
                # Count file occurrences
                for filepath in files:
                    file_counts[filepath] += 1
                
                # Record all pairs
                for i, file_a in enumerate(files):
                    for file_b in files[i+1:]:
                        # Normalize pair order (alphabetically)
                        pair = tuple(sorted([file_a, file_b]))
                        
                        if pair not in co_modifications:
                            co_modifications[pair] = []
                        
                        co_modifications[pair].append(conv_id)
            
            # Build results with confidence scores
            results = []
            
            for (file_a, file_b), conversations in co_modifications.items():
                count = len(conversations)
                
                if count < min_occurrences:
                    continue
                
                # Calculate confidence: co-modifications / min(file_a_count, file_b_count)
                confidence = count / min(file_counts[file_a], file_counts[file_b])
                
                if confidence < min_confidence:
                    continue
                
                results.append({
                    'file_a': file_a,
                    'file_b': file_b,
                    'co_modification_count': count,
                    'confidence': round(confidence, 3),
                    'conversations': conversations,
                    'file_a_total_modifications': file_counts[file_a],
                    'file_b_total_modifications': file_counts[file_b]
                })
            
            # Sort by confidence (descending)
            results.sort(key=lambda x: x['confidence'], reverse=True)
            
            return results
        
        finally:
            conn.close()
    
    def get_related_files(
        self,
        filepath: str,
        min_confidence: float = 0.5,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get files frequently modified with a specific file
        
        Args:
            filepath: File path to find related files for
            min_confidence: Minimum confidence score
            limit: Maximum number of results
        
        Returns:
            List of related files with confidence scores
        """
        co_mods = self.detect_co_modifications(min_confidence=min_confidence)
        
        related = []
        for pattern in co_mods:
            if pattern['file_a'] == filepath:
                related.append({
                    'file': pattern['file_b'],
                    'confidence': pattern['confidence'],
                    'co_modification_count': pattern['co_modification_count']
                })
            elif pattern['file_b'] == filepath:
                related.append({
                    'file': pattern['file_a'],
                    'confidence': pattern['confidence'],
                    'co_modification_count': pattern['co_modification_count']
                })
        
        # Sort by confidence and limit
        related.sort(key=lambda x: x['confidence'], reverse=True)
        return related[:limit]
    
    # ========================================================================
    # FILE STATISTICS
    # ========================================================================
    
    def get_file_statistics(self) -> Dict[str, Any]:
        """
        Get overall file tracking statistics
        
        Returns:
            Dictionary with statistics:
            - total_files_tracked
            - total_conversations_with_files
            - most_modified_files (top 10)
            - file_categories
        """
        import json
        from .entity_extractor import EntityExtractor
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Count conversations with files
            cursor.execute("""
                SELECT COUNT(*) FROM tier1_conversations
                WHERE related_files IS NOT NULL AND related_files != '[]'
            """)
            conversations_with_files = cursor.fetchone()[0]
            
            # Get all files
            cursor.execute("""
                SELECT related_files FROM tier1_conversations
                WHERE related_files IS NOT NULL AND related_files != '[]'
            """)
            
            file_counts: Counter = Counter()
            all_files: Set[str] = set()
            
            for row in cursor.fetchall():
                files = json.loads(row[0])
                all_files.update(files)
                
                for filepath in files:
                    file_counts[filepath] += 1
            
            # Get most modified files
            most_modified = [
                {'file': filepath, 'modification_count': count}
                for filepath, count in file_counts.most_common(10)
            ]
            
            # Categorize all files
            extractor = EntityExtractor()
            categories = extractor.categorize_files(list(all_files))
            
            return {
                'total_files_tracked': len(all_files),
                'total_conversations_with_files': conversations_with_files,
                'most_modified_files': most_modified,
                'file_categories': {
                    cat: len(files) for cat, files in categories.items()
                }
            }
        
        finally:
            conn.close()
    
    def get_file_modification_history(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Get modification history for a specific file
        
        Args:
            filepath: File path to get history for
        
        Returns:
            List of conversation summaries that modified this file
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT conversation_id, topic, created_at, intent, outcome
                FROM tier1_conversations
                WHERE related_files LIKE ?
                ORDER BY created_at DESC
            """, (f'%{filepath}%',))
            
            return [
                {
                    'conversation_id': row[0],
                    'topic': row[1],
                    'timestamp': row[2],
                    'intent': row[3],
                    'outcome': row[4]
                }
                for row in cursor.fetchall()
            ]
        
        finally:
            conn.close()
    
    # ========================================================================
    # TIER 2 INTEGRATION (Knowledge Graph Export)
    # ========================================================================
    
    def export_for_tier2(self) -> Dict[str, Any]:
        """
        Export co-modification data for Tier 2 knowledge graph
        
        Returns:
            Dictionary formatted for tier2_file_relationships table:
            {
                'relationships': [
                    {
                        'file_a': 'path/to/file1.py',
                        'file_b': 'path/to/file2.py',
                        'co_modification_count': 5,
                        'co_modification_rate': 0.83,
                        'last_seen': '2025-11-06T12:00:00Z'
                    }, ...
                ]
            }
        """
        co_mods = self.detect_co_modifications(min_occurrences=2, min_confidence=0.3)
        
        relationships = []
        
        for pattern in co_mods:
            relationships.append({
                'file_a': pattern['file_a'],
                'file_b': pattern['file_b'],
                'co_modification_count': pattern['co_modification_count'],
                'co_modification_rate': pattern['confidence'],
                'dependency_type': 'co-modification',
                'last_seen': datetime.now().isoformat()
            })
        
        return {
            'relationships': relationships,
            'total_relationships': len(relationships),
            'export_timestamp': datetime.now().isoformat()
        }
    
    def sync_to_tier2(self, tier2_db_path: Optional[str] = None) -> int:
        """
        Sync file relationships to Tier 2 database
        
        Args:
            tier2_db_path: Path to Tier 2 database (defaults to same as Tier 1)
        
        Returns:
            Number of relationships synced
        """
        if tier2_db_path is None:
            tier2_db_path = self.db_path
        
        export_data = self.export_for_tier2()
        
        conn = sqlite3.connect(tier2_db_path)
        cursor = conn.cursor()
        
        try:
            synced = 0
            
            for rel in export_data['relationships']:
                cursor.execute("""
                    INSERT OR REPLACE INTO tier2_file_relationships (
                        file_a, file_b, co_modification_count, co_modification_rate,
                        dependency_type, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    rel['file_a'],
                    rel['file_b'],
                    rel['co_modification_count'],
                    rel['co_modification_rate'],
                    rel['dependency_type'],
                    rel['last_seen']
                ))
                
                synced += 1
            
            conn.commit()
            return synced
        
        finally:
            conn.close()
