"""
Relevance Scorer - Calculate pattern relevance for queries

Scoring factors:
- Text similarity (TF-IDF or simple word overlap)
- Namespace overlap (matching context tags)
- Pattern confidence (stored confidence score)
- Recency (prefer recently used patterns)

Composite score combines all factors for ranking.

Author: Asif Hussain
"""

import re
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import Counter


class RelevanceScorer:
    """Calculate and rank pattern relevance"""
    
    def __init__(self, knowledge_graph):
        """
        Initialize relevance scorer
        
        Args:
            knowledge_graph: Tier 2 KnowledgeGraph instance
        """
        self.knowledge_graph = knowledge_graph
    
    def calculate_text_similarity(
        self,
        query: str,
        pattern_content: str
    ) -> float:
        """
        Calculate text similarity using word overlap
        
        Args:
            query: Search query
            pattern_content: Pattern content to compare
            
        Returns:
            Similarity score (0.0-1.0)
        """
        # Tokenize and normalize
        query_words = set(self._tokenize(query.lower()))
        content_words = set(self._tokenize(pattern_content.lower()))
        
        if not query_words or not content_words:
            return 0.0
        
        # Calculate Jaccard similarity (intersection over union)
        intersection = len(query_words & content_words)
        union = len(query_words | content_words)
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_namespace_overlap(
        self,
        query_namespaces: List[str],
        pattern_namespaces: List[str]
    ) -> float:
        """
        Calculate namespace overlap score
        
        Args:
            query_namespaces: Context namespaces from query
            pattern_namespaces: Pattern's namespaces
            
        Returns:
            Overlap score (0.0-1.0)
        """
        if not query_namespaces or not pattern_namespaces:
            return 0.0
        
        query_set = set(query_namespaces)
        pattern_set = set(pattern_namespaces)
        
        intersection = len(query_set & pattern_set)
        union = len(query_set | pattern_set)
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_recency_score(
        self,
        last_used: Optional[str] = None
    ) -> float:
        """
        Calculate recency score (prefer recently used patterns)
        
        Args:
            last_used: ISO timestamp of last use
            
        Returns:
            Recency score (0.0-1.0)
        """
        if not last_used:
            return 0.3  # Base score for never-used patterns
        
        try:
            last_used_dt = datetime.fromisoformat(last_used.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Calculate days since last use
            days_ago = (now - last_used_dt).days
            
            # Exponential decay: score = e^(-days/30)
            # Recent (0-7 days): 0.8-1.0
            # Medium (7-30 days): 0.4-0.8
            # Old (30+ days): 0.1-0.4
            score = math.exp(-days_ago / 30.0)
            
            return max(0.1, min(1.0, score))
        
        except (ValueError, AttributeError):
            return 0.3
    
    def calculate_relevance(
        self,
        query: str,
        pattern_id: str,
        context_namespaces: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate composite relevance score
        
        Args:
            query: Search query
            pattern_id: Pattern to score
            context_namespaces: Optional context namespaces
            
        Returns:
            Dict with individual scores and composite score
        """
        # Get pattern from knowledge graph
        pattern = self.knowledge_graph.get_pattern(pattern_id)
        
        if not pattern:
            return {
                'pattern_id': pattern_id,
                'composite_score': 0.0,
                'error': 'Pattern not found'
            }
        
        # Extract pattern data
        pattern_content = pattern.get('content', '')
        pattern_title = pattern.get('title', '')
        combined_text = f"{pattern_title} {pattern_content}"
        
        pattern_namespaces = []
        if pattern.get('namespaces'):
            import json
            try:
                pattern_namespaces = json.loads(pattern['namespaces'])
            except:
                pattern_namespaces = pattern['namespaces'].split(',') if isinstance(pattern['namespaces'], str) else []
        
        pattern_confidence = pattern.get('confidence', 0.5)
        pattern_last_used = pattern.get('last_used')
        
        # Calculate individual scores
        text_sim = self.calculate_text_similarity(query, combined_text)
        namespace_overlap = self.calculate_namespace_overlap(
            context_namespaces or [],
            pattern_namespaces
        )
        recency = self.calculate_recency_score(pattern_last_used)
        
        # Composite score (weighted average)
        # Text similarity: 40%, Confidence: 25%, Namespace: 20%, Recency: 15%
        composite = (
            text_sim * 0.40 +
            pattern_confidence * 0.25 +
            namespace_overlap * 0.20 +
            recency * 0.15
        )
        
        return {
            'pattern_id': pattern_id,
            'text_similarity': text_sim,
            'namespace_overlap': namespace_overlap,
            'confidence': pattern_confidence,
            'recency': recency,
            'composite_score': composite
        }
    
    def rank_patterns(
        self,
        query: str,
        pattern_ids: List[str],
        context_namespaces: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank patterns by relevance
        
        Args:
            query: Search query
            pattern_ids: List of pattern IDs to rank
            context_namespaces: Optional context namespaces
            
        Returns:
            List of patterns ranked by composite score (highest first)
        """
        scored_patterns = []
        
        for pattern_id in pattern_ids:
            relevance = self.calculate_relevance(
                query=query,
                pattern_id=pattern_id,
                context_namespaces=context_namespaces
            )
            scored_patterns.append(relevance)
        
        # Sort by composite score (descending)
        scored_patterns.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return scored_patterns
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Remove punctuation and split on whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        return [word for word in text.split() if len(word) > 2]
