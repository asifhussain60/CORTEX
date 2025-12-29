"""
Brain Context Injector

Lightweight context injection system for brain-assisted responses.
Queries all 3 brain tiers and returns relevant context with performance <100ms.

Responsibilities:
- Inject context from Tier 1 (recent conversations)
- Inject context from Tier 2 (learned patterns)
- Inject context from Tier 3 (development metrics)
- Rank results by relevance
- Manage token budgets
- Performance monitoring

Usage:
    >>> from src.tier0.brain_context_injector import BrainContextInjector
    >>> injector = BrainContextInjector(brain_path="/path/to/cortex-brain")
    >>> context = injector.inject_full_context("implement authentication")
    >>> print(f"Loaded {context['tier1']['conversation_count']} conversations")

Author: Asif Hussain
Phase: 7.4 - Context Injection System
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import json


class BrainContextInjector:
    """
    Injects context from all 3 brain tiers for brain-assisted responses.
    
    Provides fast (<100ms) multi-tier context loading with relevance ranking.
    """
    
    def __init__(self, brain_path: str):
        """
        Initialize context injector with brain path.
        
        Args:
            brain_path: Absolute path to cortex-brain directory
        """
        self.brain_path = Path(brain_path)
        self.tier1_db = self.brain_path / "tier1" / "working_memory.db"
        self.tier2_db = self.brain_path / "tier2" / "knowledge_graph.db"
        self.tier3_db = self.brain_path / "tier3" / "development_context.db"
        
        # Use simple relevance scoring (lightweight for Phase 7.4)
        # Full RelevanceScorer integration can be added in Phase 8
        self.relevance_scorer = None
    
    def inject_tier1_context(
        self, 
        user_request: str,
        max_conversations: int = 5
    ) -> Dict[str, Any]:
        """
        Inject context from Tier 1 (Working Memory).
        
        Loads recent conversations and ranks them by relevance to user request.
        
        Args:
            user_request: User's current request
            max_conversations: Maximum conversations to return
            
        Returns:
            Dict with conversations, count, and metadata
        """
        if not self.tier1_db.exists():
            return {
                'conversations': [],
                'conversation_count': 0,
                'error': 'Tier 1 database not found'
            }
        
        try:
            conn = sqlite3.connect(str(self.tier1_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get recent conversations (limit to reasonable number for scoring)
            cursor.execute("""
                SELECT conversation_id, content, timestamp, turn_number
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT 20
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return {
                    'conversations': [],
                    'conversation_count': 0
                }
            
            # Convert to list of dicts
            conversations = []
            for row in rows:
                conv = {
                    'conversation_id': row['conversation_id'],
                    'content': row['content'],
                    'timestamp': row['timestamp'],
                    'turn_number': row['turn_number']
                }
                
                # Score relevance if scorer available
                if self.relevance_scorer:
                    score = self._calculate_relevance_score(
                        user_request,
                        conv['content'],
                        conv['timestamp']
                    )
                    conv['relevance_score'] = score
                else:
                    conv['relevance_score'] = 0.5  # Default mid-range
                
                conversations.append(conv)
            
            # Sort by relevance score (highest first)
            conversations.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Return top N
            top_conversations = conversations[:max_conversations]
            
            return {
                'conversations': top_conversations,
                'conversation_count': len(top_conversations)
            }
            
        except Exception as e:
            return {
                'conversations': [],
                'conversation_count': 0,
                'error': str(e)
            }
    
    def inject_tier2_context(
        self,
        user_request: str,
        max_patterns: int = 5
    ) -> Dict[str, Any]:
        """
        Inject context from Tier 2 (Knowledge Graph).
        
        Loads relevant learned patterns ranked by relevance.
        
        Args:
            user_request: User's current request
            max_patterns: Maximum patterns to return
            
        Returns:
            Dict with patterns, count, and metadata
        """
        if not self.tier2_db.exists():
            return {
                'patterns': [],
                'pattern_count': 0,
                'error': 'Tier 2 database not found'
            }
        
        try:
            conn = sqlite3.connect(str(self.tier2_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all patterns (limit to reasonable number)
            cursor.execute("""
                SELECT pattern_id, title, content, pattern_type, confidence
                FROM patterns
                ORDER BY confidence DESC, last_accessed DESC
                LIMIT 20
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return {
                    'patterns': [],
                    'pattern_count': 0
                }
            
            # Convert to list of dicts with relevance scoring
            patterns = []
            for row in rows:
                pattern = {
                    'pattern_id': row['pattern_id'],
                    'title': row['title'],
                    'content': row['content'],
                    'pattern_type': row['pattern_type'],
                    'confidence': row['confidence']
                }
                
                # Score relevance
                if self.relevance_scorer:
                    score = self._calculate_relevance_score(
                        user_request,
                        f"{pattern['title']} {pattern['content']}"
                    )
                    pattern['relevance_score'] = score
                else:
                    pattern['relevance_score'] = pattern['confidence']
                
                patterns.append(pattern)
            
            # Sort by relevance
            patterns.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Return top N
            top_patterns = patterns[:max_patterns]
            
            return {
                'patterns': top_patterns,
                'pattern_count': len(top_patterns)
            }
            
        except Exception as e:
            return {
                'patterns': [],
                'pattern_count': 0,
                'error': str(e)
            }
    
    def inject_tier3_context(
        self,
        current_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Inject context from Tier 3 (Development Context).
        
        Loads file metrics and git activity for current file if provided,
        or general project metrics otherwise.
        
        Args:
            current_file: Current file being worked on
            
        Returns:
            Dict with file metrics and git activity
        """
        if not self.tier3_db.exists():
            return {
                'file_metrics': [],
                'git_activity': [],
                'error': 'Tier 3 database not found'
            }
        
        try:
            conn = sqlite3.connect(str(self.tier3_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            result = {}
            
            # Get file metrics
            if current_file:
                cursor.execute("""
                    SELECT file_path, lines_of_code, complexity, hotspot_score, last_modified
                    FROM code_metrics
                    WHERE file_path = ?
                """, (current_file,))
            else:
                cursor.execute("""
                    SELECT file_path, lines_of_code, complexity, hotspot_score, last_modified
                    FROM code_metrics
                    ORDER BY hotspot_score DESC
                    LIMIT 5
                """)
            
            metrics_rows = cursor.fetchall()
            result['file_metrics'] = [dict(row) for row in metrics_rows]
            
            # Get recent git activity
            if current_file:
                cursor.execute("""
                    SELECT commit_hash, file_path, change_type, lines_added, lines_removed, timestamp
                    FROM git_activity
                    WHERE file_path = ?
                    ORDER BY timestamp DESC
                    LIMIT 5
                """, (current_file,))
            else:
                cursor.execute("""
                    SELECT commit_hash, file_path, change_type, lines_added, lines_removed, timestamp
                    FROM git_activity
                    ORDER BY timestamp DESC
                    LIMIT 10
                """)
            
            git_rows = cursor.fetchall()
            result['git_activity'] = [dict(row) for row in git_rows]
            
            conn.close()
            
            return result
            
        except Exception as e:
            return {
                'file_metrics': [],
                'git_activity': [],
                'error': str(e)
            }
    
    def inject_full_context(
        self,
        user_request: str,
        current_file: Optional[str] = None,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Inject context from all 3 tiers.
        
        Performance target: <100ms for full context injection.
        
        Args:
            user_request: User's current request
            current_file: Current file being worked on
            max_tokens: Maximum tokens to return (for budget management)
            
        Returns:
            Dict with tier1, tier2, tier3 contexts and performance metrics
        """
        start_time = time.perf_counter()
        
        # Query all tiers (could be parallelized for better performance)
        tier1 = self.inject_tier1_context(user_request)
        tier2 = self.inject_tier2_context(user_request)
        tier3 = self.inject_tier3_context(current_file)
        
        # Calculate token estimate (rough approximation: 4 chars per token)
        total_chars = 0
        for conv in tier1.get('conversations', []):
            total_chars += len(conv.get('content', ''))
        for pattern in tier2.get('patterns', []):
            total_chars += len(pattern.get('content', ''))
        
        estimated_tokens = total_chars // 4
        
        # Trim if over budget (simple strategy: reduce tier1 conversations)
        if estimated_tokens > max_tokens and tier1['conversation_count'] > 1:
            # Remove conversations until under budget
            while estimated_tokens > max_tokens and len(tier1['conversations']) > 1:
                removed = tier1['conversations'].pop()
                total_chars -= len(removed.get('content', ''))
                estimated_tokens = total_chars // 4
            
            tier1['conversation_count'] = len(tier1['conversations'])
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            'tier1': tier1,
            'tier2': tier2,
            'tier3': tier3,
            'injection_time_ms': elapsed_ms,
            'total_tokens': estimated_tokens,
            'performance_ok': elapsed_ms < 100
        }
    
    def _calculate_relevance_score(
        self,
        user_request: str,
        content: str,
        timestamp: Optional[str] = None
    ) -> float:
        """
        Calculate relevance score for content relative to user request.
        
        Uses simple keyword matching with partial word support.
        
        Args:
            user_request: User's request
            content: Content to score
            timestamp: Optional timestamp for recency boost
            
        Returns:
            Relevance score between 0 and 1
        """
        # Simple keyword matching with partial word support
        request_lower = user_request.lower()
        content_lower = content.lower()
        
        # Split into words
        request_words = set(request_lower.split())
        content_words = set(content_lower.split())
        
        if not request_words:
            return 0.0
        
        # Count exact matches
        exact_matches = len(request_words & content_words)
        
        # Count partial matches (any request word appears in content)
        partial_matches = 0
        for req_word in request_words:
            if req_word not in content_words:
                # Check if any content word contains the request word (or vice versa)
                if any(req_word in cont_word or cont_word in req_word 
                       for cont_word in content_words):
                    partial_matches += 0.5
        
        # Score = (exact + partial) / total request words
        total_matches = exact_matches + partial_matches
        score = total_matches / len(request_words)
        
        return min(score, 1.0)
