"""
Pattern Suggestion Engine

Automatically suggests relevant patterns before task execution to increase utilization.

Purpose:
    - Search for relevant patterns based on task context
    - Rank patterns by relevance (BM25 + confidence + access history)
    - Display top 3 suggestions to user before task execution
    - Track pattern acceptance/rejection for feedback loop

Responsibilities:
    - Pattern retrieval based on intent keywords
    - Relevance scoring with multiple factors
    - Pattern suggestion formatting
    - Usage tracking (acceptance rate, effectiveness)

Integration Points:
    - Called by IntentRouter before agent execution
    - Uses PatternSearch for retrieval
    - Updates pattern access counts via PatternStore

Performance Targets:
    - Suggestion generation: <100ms
    - Pattern search: <50ms
    - Relevance scoring: <30ms

Example:
    >>> from tier2.pattern_suggestion_engine import PatternSuggestionEngine
    >>> engine = PatternSuggestionEngine()
    >>> suggestions = engine.suggest_patterns("implement authentication feature", limit=3)
    >>> for suggestion in suggestions:
    ...     print(f"{suggestion['title']}: {suggestion['relevance_score']:.2f}")

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tier2.knowledge_graph.patterns.pattern_search import PatternSearch
from src.tier2.knowledge_graph.patterns.pattern_store import PatternStore

logger = logging.getLogger(__name__)


class PatternSuggestionEngine:
    """
    Suggests relevant patterns before task execution.
    
    Uses multi-factor relevance scoring:
    - BM25 score from FTS5 search (content relevance)
    - Confidence score (pattern quality)
    - Historical access count (proven usefulness)
    - Recency (last accessed timestamp)
    """
    
    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize Pattern Suggestion Engine.
        
        Args:
            database_path: Path to Tier 2 knowledge graph database
                          (default: cortex-brain/tier2-knowledge-graph.db)
        """
        if database_path is None:
            brain_dir = os.path.join(os.path.dirname(__file__), '../../..', 'cortex-brain')
            database_path = os.path.join(brain_dir, 'tier2-knowledge-graph.db')
        
        self.database_path = database_path
        
        # Create simple database connection object
        class SimpleDB:
            def __init__(self, path):
                self.db_path = path
                self._conn = None
            
            def get_connection(self):
                if self._conn is None:
                    import sqlite3
                    self._conn = sqlite3.connect(self.db_path)
                return self._conn
        
        self.db = SimpleDB(database_path)
        self.pattern_search = PatternSearch(self.db)
        self.pattern_store = PatternStore(self.db)
    
    def suggest_patterns(
        self,
        task_description: str,
        intent_type: Optional[str] = None,
        current_namespace: Optional[str] = None,
        min_confidence: float = 0.6,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Suggest relevant patterns for a given task.
        
        Args:
            task_description: Natural language task description
            intent_type: Intent type (PLAN, EXECUTE, TEST, etc.)
            current_namespace: Current application context
            min_confidence: Minimum confidence threshold
            limit: Maximum suggestions to return (default: 3)
        
        Returns:
            List of pattern suggestions with relevance scores
        
        Performance: <100ms
        """
        logger.info(f"Suggesting patterns for task: {task_description[:50]}...")
        
        # Extract search keywords from task description
        search_query = self._extract_keywords(task_description, intent_type)
        logger.debug(f"Search query: {search_query}")
        
        # Search patterns with namespace priority
        patterns = self.pattern_search.search_with_namespace_priority(
            query=search_query,
            current_namespace=current_namespace,
            include_cortex=True,
            min_confidence=min_confidence,
            limit=limit * 3  # Get more for reranking
        )
        
        if not patterns:
            logger.info("No patterns found matching search criteria")
            return []
        
        # Calculate relevance scores
        scored_patterns = []
        for pattern in patterns:
            relevance_score = self._calculate_relevance_score(
                pattern=pattern,
                task_description=task_description,
                intent_type=intent_type
            )
            
            pattern['relevance_score'] = relevance_score
            scored_patterns.append(pattern)
        
        # Sort by relevance score (descending) and limit
        scored_patterns.sort(key=lambda p: p['relevance_score'], reverse=True)
        top_suggestions = scored_patterns[:limit]
        
        logger.info(f"Returning {len(top_suggestions)} pattern suggestions")
        return top_suggestions
    
    def _extract_keywords(self, task_description: str, intent_type: Optional[str]) -> str:
        """
        Extract search keywords from task description.
        
        Uses intent type to add context-specific keywords.
        
        Args:
            task_description: Raw task description
            intent_type: Intent type (optional)
        
        Returns:
            FTS5-compatible search query
        """
        # Start with task description
        keywords = task_description
        
        # Add intent-specific keywords
        if intent_type:
            intent_keywords = {
                'PLAN': 'planning design architecture roadmap',
                'EXECUTE': 'implementation code development',
                'TEST': 'testing validation verification',
                'REFACTOR': 'refactoring optimization cleanup',
                'DEBUG': 'debugging troubleshooting fix',
                'DOCUMENT': 'documentation guide tutorial'
            }
            
            if intent_type in intent_keywords:
                keywords = f"{keywords} {intent_keywords[intent_type]}"
        
        return keywords
    
    def _calculate_relevance_score(
        self,
        pattern: Dict[str, Any],
        task_description: str,
        intent_type: Optional[str]
    ) -> float:
        """
        Calculate multi-factor relevance score.
        
        Scoring factors:
        - BM25 score (40%): Content similarity
        - Confidence (30%): Pattern quality
        - Access history (20%): Proven usefulness
        - Recency (10%): Recently used patterns
        
        Args:
            pattern: Pattern dictionary from search
            task_description: Task description
            intent_type: Intent type
        
        Returns:
            Relevance score (0.0-1.0)
        """
        # BM25 score (normalized, lower is better so invert)
        # Typical BM25 scores: -10 to 0 (negative)
        bm25_raw = pattern.get('score', 0)
        bm25_normalized = max(0, 1 + (bm25_raw / 10))  # Normalize to 0-1
        bm25_weight = 0.40
        
        # Confidence score
        confidence = pattern.get('confidence', 0.5)
        confidence_weight = 0.30
        
        # Access history (normalized)
        access_count = pattern.get('access_count', 0)
        # Normalize: 0 accesses = 0, 10+ accesses = 1.0
        access_normalized = min(1.0, access_count / 10.0)
        access_weight = 0.20
        
        # Recency (normalized)
        last_accessed = pattern.get('last_accessed')
        if last_accessed:
            try:
                last_accessed_dt = datetime.fromisoformat(last_accessed)
                days_since = (datetime.now() - last_accessed_dt).days
                # Normalize: 0 days = 1.0, 30+ days = 0.0
                recency_normalized = max(0, 1 - (days_since / 30))
            except Exception:
                recency_normalized = 0.5  # Default if parsing fails
        else:
            recency_normalized = 0.0  # Never accessed
        recency_weight = 0.10
        
        # Calculate weighted score
        relevance_score = (
            (bm25_normalized * bm25_weight) +
            (confidence * confidence_weight) +
            (access_normalized * access_weight) +
            (recency_normalized * recency_weight)
        )
        
        return min(1.0, relevance_score)  # Cap at 1.0
    
    def format_suggestion(self, pattern: Dict[str, Any]) -> str:
        """
        Format pattern suggestion for display to user.
        
        Args:
            pattern: Pattern dictionary
        
        Returns:
            Formatted suggestion string
        """
        title = pattern.get('title', 'Untitled Pattern')
        pattern_type = pattern.get('pattern_type', 'unknown')
        confidence = pattern.get('confidence', 0.0)
        access_count = pattern.get('access_count', 0)
        relevance_score = pattern.get('relevance_score', 0.0)
        
        # Truncate content to first 100 characters
        content = pattern.get('content', '')
        content_preview = content[:100] + '...' if len(content) > 100 else content
        
        formatted = (
            f"📌 **{title}** ({pattern_type})\n"
            f"   Relevance: {relevance_score:.2f} | Confidence: {confidence:.2f} | "
            f"Used {access_count}x\n"
            f"   {content_preview}"
        )
        
        return formatted
    
    def display_suggestions(
        self,
        task_description: str,
        intent_type: Optional[str] = None,
        current_namespace: Optional[str] = None
    ) -> str:
        """
        Display pattern suggestions to user before task execution.
        
        Args:
            task_description: Task description
            intent_type: Intent type
            current_namespace: Current namespace
        
        Returns:
            Formatted suggestions text
        """
        suggestions = self.suggest_patterns(
            task_description=task_description,
            intent_type=intent_type,
            current_namespace=current_namespace,
            limit=3
        )
        
        if not suggestions:
            return "💡 **Pattern Suggestions:** No relevant patterns found. This will be a learning opportunity!"
        
        output = "💡 **Pattern Suggestions (Top 3):**\n\n"
        for i, pattern in enumerate(suggestions, 1):
            output += f"{i}. {self.format_suggestion(pattern)}\n\n"
        
        output += "Would you like to apply any of these patterns? (Say 'apply pattern 1' or proceed without)"
        
        return output
    
    def track_pattern_acceptance(
        self,
        pattern_id: str,
        accepted: bool,
        task_outcome: Optional[str] = None
    ) -> bool:
        """
        Track whether user accepted/rejected a pattern suggestion.
        
        Updates:
        - Access count (if accepted)
        - Last accessed timestamp (if accepted)
        - Pattern effectiveness metadata
        
        Args:
            pattern_id: Pattern ID
            accepted: True if user applied pattern
            task_outcome: Task outcome (success/failure/partial)
        
        Returns:
            True if tracking successful
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if accepted:
                # Increment access count and update last_accessed
                cursor.execute("""
                    UPDATE patterns
                    SET access_count = access_count + 1,
                        last_accessed = ?
                    WHERE pattern_id = ?
                """, (datetime.now().isoformat(), pattern_id))
                
                # Update metadata with task outcome
                if task_outcome:
                    cursor.execute("""
                        SELECT metadata FROM patterns WHERE pattern_id = ?
                    """, (pattern_id,))
                    
                    row = cursor.fetchone()
                    if row and row[0]:
                        import json
                        metadata = json.loads(row[0])
                    else:
                        metadata = {}
                    
                    # Track outcomes
                    if 'outcomes' not in metadata:
                        metadata['outcomes'] = {'success': 0, 'failure': 0, 'partial': 0}
                    
                    if task_outcome in metadata['outcomes']:
                        metadata['outcomes'][task_outcome] += 1
                    
                    cursor.execute("""
                        UPDATE patterns
                        SET metadata = ?
                        WHERE pattern_id = ?
                    """, (json.dumps(metadata), pattern_id))
                
                conn.commit()
                logger.info(f"Pattern {pattern_id} accepted and tracked")
            else:
                logger.info(f"Pattern {pattern_id} rejected (not applied)")
            
            return True
        
        except Exception as e:
            logger.error(f"Error tracking pattern acceptance: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    engine = PatternSuggestionEngine()
    
    # Test suggestion
    suggestions_text = engine.display_suggestions(
        task_description="implement user authentication with JWT tokens",
        intent_type="EXECUTE",
        current_namespace="workspace.myapp"
    )
    
    print(suggestions_text)
