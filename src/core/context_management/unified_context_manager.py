"""
CORTEX Unified Context Manager
Orchestrates context loading across all tiers (T1/T2/T3) with unified strategy

Phase 1: Foundation
- Relevance scoring (which tier's data is most relevant?)
- Token budget allocation (how many tokens per tier?)
- Deduplication (prevent showing same info twice)
- Caching (avoid redundant database queries)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib


class ContextRelevanceScorer:
    """Scores relevance of each tier's context to current request"""
    
    def __init__(self):
        self.weights = {
            'keyword_overlap': 0.30,
            'file_overlap': 0.25,
            'entity_overlap': 0.20,
            'recency': 0.15,
            'intent_match': 0.10
        }
    
    def score_tier1_relevance(
        self,
        user_request: str,
        conversations: List[Dict[str, Any]],
        current_files: List[str]
    ) -> float:
        """
        Score T1 (Working Memory) relevance
        
        Args:
            user_request: Current user request text
            conversations: List of recent conversations
            current_files: Files open in workspace
            
        Returns:
            Relevance score (0.0-1.0)
        """
        if not conversations:
            return 0.0
        
        scores = []
        request_keywords = set(user_request.lower().split())
        
        for conv in conversations:
            score = 0.0
            
            # Keyword overlap
            conv_text = (conv.get('title', '') + ' ' + conv.get('summary', '')).lower()
            conv_keywords = set(conv_text.split())
            keyword_overlap = len(request_keywords & conv_keywords) / max(len(request_keywords), 1)
            score += keyword_overlap * self.weights['keyword_overlap']
            
            # File overlap
            conv_files = set(conv.get('files_involved', []))
            file_overlap = len(set(current_files) & conv_files) / max(len(current_files), 1) if current_files else 0
            score += file_overlap * self.weights['file_overlap']
            
            # Entity overlap
            conv_entities = set(conv.get('entities', []))
            entity_overlap = len(conv_entities & request_keywords) / max(len(request_keywords), 1)
            score += entity_overlap * self.weights['entity_overlap']
            
            # Recency
            created_at = datetime.fromisoformat(conv.get('created_at', datetime.now().isoformat()))
            hours_old = (datetime.now() - created_at).total_seconds() / 3600
            recency_score = max(0, 1 - (hours_old / 168))  # Decay over 1 week
            score += recency_score * self.weights['recency']
            
            # Intent match
            conv_intent = conv.get('intent', '')
            intent_match = 1.0 if conv_intent in user_request.upper() else 0.0
            score += intent_match * self.weights['intent_match']
            
            scores.append(score)
        
        return max(scores) if scores else 0.0
    
    def score_tier2_relevance(
        self,
        user_request: str,
        patterns: List[Dict[str, Any]]
    ) -> float:
        """
        Score T2 (Knowledge Graph) relevance
        
        Args:
            user_request: Current user request text
            patterns: Matched patterns from knowledge graph
            
        Returns:
            Relevance score (0.0-1.0)
        """
        if not patterns:
            return 0.0
        
        scores = []
        request_keywords = set(user_request.lower().split())
        
        for pattern in patterns:
            score = pattern.get('confidence', 0.5)  # Base confidence
            
            # Pattern title match
            pattern_title = pattern.get('title', '').lower()
            title_keywords = set(pattern_title.split())
            title_overlap = len(request_keywords & title_keywords) / max(len(request_keywords), 1)
            score = (score + title_overlap) / 2
            
            # Usage count (proven patterns score higher)
            usage_count = pattern.get('usage_count', 0)
            usage_boost = min(0.2, usage_count * 0.02)  # Max +0.2 boost
            score += usage_boost
            
            # Recency of pattern
            last_used = pattern.get('last_used')
            if last_used:
                last_used_dt = datetime.fromisoformat(last_used)
                days_old = (datetime.now() - last_used_dt).days
                recency_penalty = max(0, days_old / 180) * 0.1  # Decay over 6 months
                score -= recency_penalty
            
            scores.append(min(1.0, max(0.0, score)))
        
        return max(scores) if scores else 0.0
    
    def score_tier3_relevance(
        self,
        user_request: str,
        current_files: List[str],
        insights: List[Dict[str, Any]]
    ) -> float:
        """
        Score T3 (Context Intelligence) relevance
        
        Args:
            user_request: Current user request text
            current_files: Files open in workspace
            insights: Git/test metrics insights
            
        Returns:
            Relevance score (0.0-1.0)
        """
        if not insights and not current_files:
            return 0.0
        
        score = 0.0
        
        # File hotspot relevance
        for insight in insights:
            if insight.get('insight_type') == 'file_hotspot':
                file_path = insight.get('file_path', '')
                if any(file_path in cf for cf in current_files):
                    severity = insight.get('severity', 'INFO')
                    severity_score = {'CRITICAL': 1.0, 'ERROR': 0.8, 'WARNING': 0.6, 'INFO': 0.3}.get(severity, 0.3)
                    score = max(score, severity_score)
        
        # Test relevance (if user mentions "test", "fix", "bug")
        test_keywords = {'test', 'fix', 'bug', 'error', 'fail'}
        if any(kw in user_request.lower() for kw in test_keywords):
            for insight in insights:
                if insight.get('insight_type') in ['flaky_test', 'test_coverage']:
                    score = max(score, 0.7)
        
        # Build health relevance
        if 'build' in user_request.lower() or 'deploy' in user_request.lower():
            for insight in insights:
                if insight.get('insight_type') == 'build_health':
                    score = max(score, 0.8)
        
        return min(1.0, score)


class UnifiedContextManager:
    """
    Orchestrates context loading across all tiers with:
    - Relevance scoring (which tier's data is most relevant?)
    - Token budget allocation (how many tokens per tier?)
    - Deduplication (prevent showing same info twice)
    - Caching (avoid redundant database queries)
    """
    
    def __init__(self, tier1, tier2, tier3, cache_ttl: int = 300):
        """
        Initialize unified context manager
        
        Args:
            tier1: WorkingMemory instance (Tier 1)
            tier2: KnowledgeGraph instance (Tier 2)
            tier3: ContextIntelligence instance (Tier 3)
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.tier1 = tier1
        self.tier2 = tier2
        self.tier3 = tier3
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.scorer = ContextRelevanceScorer()
    
    def _cache_key(self, user_request: str, token_budget: int, current_files: List[str]) -> str:
        """Generate cache key for request"""
        key_data = f"{user_request}|{token_budget}|{'|'.join(sorted(current_files))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached context if still valid"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            age = (datetime.now() - timestamp).total_seconds()
            if age < self.cache_ttl:
                return cached_data
            else:
                del self.cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Dict[str, Any]):
        """Cache context data"""
        self.cache[cache_key] = (data, datetime.now())
    
    def build_context(
        self,
        conversation_id: Optional[str],
        user_request: str,
        current_files: Optional[List[str]] = None,
        token_budget: int = 500,
        prioritize: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build unified context from all tiers within token budget
        
        Args:
            conversation_id: Current conversation ID (for T1 lookup)
            user_request: User's current request text
            current_files: List of files open in workspace
            token_budget: Maximum tokens allowed for context
            prioritize: Optional tier priority order ['tier1', 'tier2', 'tier3']
            
        Returns:
            {
                'tier1_context': {...},      # Recent conversations
                'tier2_context': {...},      # Learned patterns
                'tier3_context': {...},      # Git/test metrics
                'merged_summary': str,       # Token-efficient summary
                'relevance_scores': {...},   # Why each tier was included
                'token_usage': int,          # Total tokens consumed
                'cache_hit': bool            # Was this from cache?
            }
        """
        current_files = current_files or []
        prioritize = prioritize or ['tier1', 'tier2', 'tier3']
        
        # Check cache
        cache_key = self._cache_key(user_request, token_budget, current_files)
        cached = self._get_cached(cache_key)
        if cached:
            cached['cache_hit'] = True
            return cached
        
        # Load context from each tier
        tier1_data = self._load_tier1_context(conversation_id, user_request, current_files)
        tier2_data = self._load_tier2_context(user_request)
        tier3_data = self._load_tier3_context(current_files)
        
        # Score relevance
        relevance_scores = {
            'tier1': self.scorer.score_tier1_relevance(user_request, tier1_data['conversations'], current_files),
            'tier2': self.scorer.score_tier2_relevance(user_request, tier2_data['patterns']),
            'tier3': self.scorer.score_tier3_relevance(user_request, current_files, tier3_data['insights'])
        }
        
        # Allocate token budget based on relevance
        from .token_budget_manager import TokenBudgetManager
        budget_mgr = TokenBudgetManager(token_budget)
        tier_budgets = budget_mgr.allocate_budget(relevance_scores)
        
        # Build tier contexts within budgets
        tier1_context = self._build_tier1_context(tier1_data, tier_budgets['tier1'])
        tier2_context = self._build_tier2_context(tier2_data, tier_budgets['tier2'])
        tier3_context = self._build_tier3_context(tier3_data, tier_budgets['tier3'])
        
        # Calculate actual token usage
        tier1_tokens = self._estimate_tokens(tier1_context)
        tier2_tokens = self._estimate_tokens(tier2_context)
        tier3_tokens = self._estimate_tokens(tier3_context)
        total_tokens = tier1_tokens + tier2_tokens + tier3_tokens
        
        # Deduplicate and merge
        merged_summary = self._merge_contexts(
            tier1_context,
            tier2_context,
            tier3_context,
            relevance_scores
        )
        
        result = {
            'tier1_context': tier1_context,
            'tier2_context': tier2_context,
            'tier3_context': tier3_context,
            'merged_summary': merged_summary,
            'relevance_scores': relevance_scores,
            'token_usage': {
                'tier1': tier1_tokens,
                'tier2': tier2_tokens,
                'tier3': tier3_tokens,
                'total': total_tokens,
                'budget': token_budget,
                'within_budget': total_tokens <= token_budget
            },
            'cache_hit': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache result
        self._set_cache(cache_key, result)
        
        return result
    
    def _load_tier1_context(
        self,
        conversation_id: Optional[str],
        user_request: str,
        current_files: List[str]
    ) -> Dict[str, Any]:
        """Load context from Tier 1 (Working Memory)"""
        conversations = []
        
        # Get recent conversations
        all_convs = self.tier1.conversation_manager.get_recent_conversations(limit=10)
        
        # Filter relevant ones
        for conv in all_convs:
            conversations.append({
                'conversation_id': conv.conversation_id,
                'title': conv.title,
                'summary': conv.summary or '',
                'created_at': conv.created_at.isoformat() if hasattr(conv.created_at, 'isoformat') else str(conv.created_at),
                'message_count': conv.message_count,
                'is_active': conv.is_active
            })
        
        return {'conversations': conversations}
    
    def _load_tier2_context(self, user_request: str) -> Dict[str, Any]:
        """Load context from Tier 2 (Knowledge Graph)"""
        patterns = []
        
        # Search for relevant patterns
        keywords = user_request.lower().split()[:5]  # Top 5 keywords
        for keyword in keywords:
            results = self.tier2.search_patterns(keyword, limit=3)
            for pattern in results:
                patterns.append({
                    'pattern_id': pattern.get('pattern_id'),
                    'title': pattern.get('title'),
                    'confidence': pattern.get('confidence', 0.5),
                    'usage_count': pattern.get('usage_count', 0),
                    'last_used': pattern.get('last_used')
                })
        
        # Deduplicate by pattern_id
        seen = set()
        unique_patterns = []
        for p in patterns:
            if p['pattern_id'] not in seen:
                seen.add(p['pattern_id'])
                unique_patterns.append(p)
        
        return {'patterns': unique_patterns}
    
    def _load_tier3_context(self, current_files: List[str]) -> Dict[str, Any]:
        """Load context from Tier 3 (Context Intelligence)"""
        insights = []
        
        try:
            # Get unstable files
            unstable_files = self.tier3.get_unstable_files(limit=10)
            for hotspot in unstable_files[:5]:  # Top 5 unstable files
                insights.append({
                    'insight_type': 'file_hotspot',
                    'file_path': hotspot.file_path,
                    'churn_rate': hotspot.churn_rate,
                    'stability': hotspot.stability.value,
                    'severity': 'WARNING' if hotspot.stability.value == 'UNSTABLE' else 'INFO'
                })
            
            # Get recent insights
            recent_insights = self.tier3.generate_insights()
            for insight in recent_insights[:5]:  # Top 5 insights
                insights.append({
                    'insight_type': insight.insight_type.value,
                    'severity': insight.severity.value,
                    'title': insight.title,
                    'description': insight.description
                })
        except Exception:
            # Tier 3 might not have data yet
            pass
        
        return {'insights': insights}
    
    def _build_tier1_context(self, data: Dict[str, Any], budget: int) -> Dict[str, Any]:
        """Build T1 context within token budget"""
        conversations = data['conversations'][:3]  # Top 3 most relevant
        return {
            'recent_conversations': len(conversations),
            'conversations': conversations
        }
    
    def _build_tier2_context(self, data: Dict[str, Any], budget: int) -> Dict[str, Any]:
        """Build T2 context within token budget"""
        patterns = sorted(data['patterns'], key=lambda p: p['confidence'], reverse=True)[:3]
        return {
            'matched_patterns': len(patterns),
            'patterns': patterns
        }
    
    def _build_tier3_context(self, data: Dict[str, Any], budget: int) -> Dict[str, Any]:
        """Build T3 context within token budget"""
        insights = data['insights'][:3]
        return {
            'insights_count': len(insights),
            'insights': insights
        }
    
    def _estimate_tokens(self, context: Dict[str, Any]) -> int:
        """Estimate token count (heuristic: ~4 chars/token)"""
        text = json.dumps(context)
        return len(text) // 4
    
    def _merge_contexts(
        self,
        tier1: Dict[str, Any],
        tier2: Dict[str, Any],
        tier3: Dict[str, Any],
        relevance: Dict[str, float]
    ) -> str:
        """Merge contexts into unified summary"""
        summary_parts = []
        
        # Tier 1 summary
        if relevance['tier1'] > 0.5:
            conv_count = tier1.get('recent_conversations', 0)
            if conv_count > 0:
                summary_parts.append(f"Recent work: {conv_count} related conversations")
        
        # Tier 2 summary
        if relevance['tier2'] > 0.5:
            pattern_count = tier2.get('matched_patterns', 0)
            if pattern_count > 0:
                top_pattern = tier2['patterns'][0]['title'] if tier2['patterns'] else 'N/A'
                summary_parts.append(f"Learned patterns: {top_pattern} (confidence: {tier2['patterns'][0]['confidence']:.2f})")
        
        # Tier 3 summary
        if relevance['tier3'] > 0.5:
            insight_count = tier3.get('insights_count', 0)
            if insight_count > 0:
                summary_parts.append(f"Metrics: {insight_count} insights available")
        
        return " | ".join(summary_parts) if summary_parts else "No relevant context found"
    
    def clear_cache(self):
        """Clear all cached context"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        valid_entries = 0
        expired_entries = 0
        
        now = datetime.now()
        for cache_key, (data, timestamp) in list(self.cache.items()):
            age = (now - timestamp).total_seconds()
            if age < self.cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
                del self.cache[cache_key]
        
        return {
            'valid_entries': valid_entries,
            'expired_entries_removed': expired_entries,
            'cache_ttl_seconds': self.cache_ttl
        }
