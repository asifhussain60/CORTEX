"""
Brain Analytics Collector Module

Comprehensive analytics collection from CORTEX brain tiers:
- Tier 1: Working Memory (conversations, tokens, entities)
- Tier 2: Knowledge Graph (patterns, confidence, decay)
- Tier 3: Development Context (code metrics, git activity)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
Version: 1.0.0
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BrainAnalyticsCollector:
    """
    Collects comprehensive analytics from all brain tiers.
    
    Features:
    - Tier 1 statistics (conversation retention, token usage, entity extraction)
    - Tier 2 statistics (pattern counts, confidence distribution, decay analysis)
    - Tier 3 statistics (code hotspots, git activity, developer patterns)
    - Health scoring algorithm
    - Trend analysis
    """
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize brain analytics collector.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        if brain_path is None:
            brain_path = Path.cwd() / "cortex-brain"
        
        self.brain_path = brain_path
        self.tier1_db = brain_path / "tier1" / "working_memory.db"
        self.tier2_db = brain_path / "tier2" / "knowledge_graph.db"
        self.tier3_db = brain_path / "tier3" / "development_context.db"
    
    def collect_all_analytics(self) -> Dict[str, Any]:
        """
        Collect analytics from all brain tiers.
        
        Returns:
            Dict with analytics from all tiers and overall health score
        """
        analytics = {
            'timestamp': datetime.now().isoformat(),
            'tier1': self.get_tier1_stats(),
            'tier2': self.get_tier2_stats(),
            'tier3': self.get_tier3_stats(),
            'health_score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        # Calculate overall brain health score
        analytics['health_score'] = self._calculate_brain_health_score(analytics)
        
        # Generate recommendations
        analytics['recommendations'] = self._generate_recommendations(analytics)
        
        return analytics
    
    def get_tier1_stats(self) -> Dict[str, Any]:
        """
        Get Tier 1 (Working Memory) statistics.
        
        Returns:
            Dict with conversation, token, and entity statistics
        """
        if not self.tier1_db.exists():
            return {
                'status': 'not_found',
                'error': 'Tier 1 database not found'
            }
        
        try:
            conn = sqlite3.connect(str(self.tier1_db))
            cursor = conn.cursor()
            
            stats = {
                'status': 'healthy',
                'conversations': self._get_conversation_stats(cursor),
                'tokens': self._get_token_stats(cursor),
                'entities': self._get_entity_stats(cursor),
                'sessions': self._get_session_stats(cursor),
            }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to collect Tier 1 stats: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_tier2_stats(self) -> Dict[str, Any]:
        """
        Get Tier 2 (Knowledge Graph) statistics.
        
        Returns:
            Dict with pattern, confidence, and decay statistics
        """
        if not self.tier2_db.exists():
            return {
                'status': 'not_found',
                'error': 'Tier 2 database not found'
            }
        
        try:
            conn = sqlite3.connect(str(self.tier2_db))
            cursor = conn.cursor()
            
            stats = {
                'status': 'healthy',
                'patterns': self._get_pattern_stats(cursor),
                'confidence': self._get_confidence_distribution(cursor),
                'decay': self._get_decay_analysis(cursor),
                'relationships': self._get_relationship_stats(cursor),
            }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to collect Tier 2 stats: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_tier3_stats(self) -> Dict[str, Any]:
        """
        Get Tier 3 (Development Context) statistics.
        
        Returns:
            Dict with code metrics, git activity, and developer patterns
        """
        if not self.tier3_db.exists():
            return {
                'status': 'not_found',
                'error': 'Tier 3 database not found'
            }
        
        try:
            conn = sqlite3.connect(str(self.tier3_db))
            cursor = conn.cursor()
            
            stats = {
                'status': 'healthy',
                'code_metrics': self._get_code_metrics(cursor),
                'git_activity': self._get_git_activity(cursor),
                'developer_patterns': self._get_developer_patterns(cursor),
            }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to collect Tier 3 stats: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    # ============ Tier 1 Helper Methods ============
    
    def _get_conversation_stats(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get conversation statistics from Tier 1."""
        try:
            # Total conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]
            
            # Active conversations (last 7 days)
            seven_days_ago = (datetime.now() - timedelta(days=7)).timestamp()
            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE created_at > ?",
                (seven_days_ago,)
            )
            active_conversations = cursor.fetchone()[0]
            
            # Average conversation length
            cursor.execute(
                "SELECT AVG(message_count) FROM ("
                "SELECT conversation_id, COUNT(*) as message_count "
                "FROM messages GROUP BY conversation_id)"
            )
            avg_length_result = cursor.fetchone()[0]
            avg_conversation_length = round(avg_length_result, 1) if avg_length_result else 0
            
            # Retention rate (conversations accessed in last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).timestamp()
            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE last_activity > ?",
                (thirty_days_ago,)
            )
            recent_access = cursor.fetchone()[0]
            retention_rate = (recent_access / total_conversations * 100) if total_conversations > 0 else 0
            
            return {
                'total_conversations': total_conversations,
                'active_conversations': active_conversations,
                'avg_conversation_length': avg_conversation_length,
                'retention_rate': round(retention_rate, 1),
            }
            
        except Exception as e:
            logger.warning(f"Conversation stats collection failed: {e}")
            return {'error': str(e)}
    
    def _get_token_stats(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get token usage statistics from Tier 1."""
        try:
            # Check if token_metrics table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='token_metrics'"
            )
            if not cursor.fetchone():
                return {'status': 'not_available', 'note': 'Token metrics tracking not initialized'}
            
            # Total tokens used
            cursor.execute("SELECT SUM(total_tokens) FROM token_metrics")
            total_tokens_result = cursor.fetchone()[0]
            total_tokens = total_tokens_result if total_tokens_result else 0
            
            # Average tokens per request
            cursor.execute("SELECT AVG(total_tokens) FROM token_metrics")
            avg_tokens_result = cursor.fetchone()[0]
            avg_tokens = round(avg_tokens_result, 0) if avg_tokens_result else 0
            
            # Token budget usage (assume 3M limit)
            TOKEN_BUDGET = 3_000_000
            budget_usage_pct = (total_tokens / TOKEN_BUDGET * 100) if total_tokens > 0 else 0
            
            return {
                'total_tokens': total_tokens,
                'avg_tokens_per_request': avg_tokens,
                'budget_usage_pct': round(budget_usage_pct, 1),
                'budget_limit': TOKEN_BUDGET,
            }
            
        except Exception as e:
            logger.warning(f"Token stats collection failed: {e}")
            return {'error': str(e)}
    
    def _get_entity_stats(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get entity extraction statistics from Tier 1."""
        try:
            # Total entities
            cursor.execute("SELECT COUNT(*) FROM entities")
            total_entities = cursor.fetchone()[0]
            
            # Entities by type
            cursor.execute(
                "SELECT entity_type, COUNT(*) as count FROM entities "
                "GROUP BY entity_type ORDER BY count DESC"
            )
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Recent entities (last 7 days)
            seven_days_ago = (datetime.now() - timedelta(days=7)).timestamp()
            cursor.execute(
                "SELECT COUNT(*) FROM entities WHERE first_seen > ?",
                (seven_days_ago,)
            )
            recent_entities = cursor.fetchone()[0]
            
            return {
                'total_entities': total_entities,
                'by_type': by_type,
                'recent_entities': recent_entities,
            }
            
        except Exception as e:
            logger.warning(f"Entity stats collection failed: {e}")
            return {'error': str(e)}
    
    def _get_session_stats(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get session statistics from Tier 1."""
        try:
            # Check if sessions table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
            )
            if not cursor.fetchone():
                return {'status': 'not_available'}
            
            # Total sessions
            cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]
            
            # Active sessions
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE is_active = 1")
            active_sessions = cursor.fetchone()[0]
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
            }
            
        except Exception as e:
            logger.warning(f"Session stats collection failed: {e}")
            return {'error': str(e)}
    
    # ============ Tier 2 Helper Methods ============
    
    def _get_pattern_stats(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get pattern statistics from Tier 2."""
        try:
            # Total patterns
            cursor.execute("SELECT COUNT(*) FROM patterns")
            total_patterns = cursor.fetchone()[0]
            
            # Patterns by type
            cursor.execute(
                "SELECT pattern_type, COUNT(*) as count FROM patterns "
                "GROUP BY pattern_type ORDER BY count DESC"
            )
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Recent patterns (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).timestamp()
            cursor.execute(
                "SELECT COUNT(*) FROM patterns WHERE created_at > ?",
                (thirty_days_ago,)
            )
            recent_patterns = cursor.fetchone()[0]
            
            # Pinned patterns
            cursor.execute("SELECT COUNT(*) FROM patterns WHERE is_pinned = 1")
            pinned_patterns = cursor.fetchone()[0]
            
            return {
                'total_patterns': total_patterns,
                'by_type': by_type,
                'recent_patterns': recent_patterns,
                'pinned_patterns': pinned_patterns,
            }
            
        except Exception as e:
            logger.warning(f"Pattern stats collection failed: {e}")
            return {'error': str(e)}
    
    def _get_confidence_distribution(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get confidence score distribution from Tier 2."""
        try:
            # High confidence (>0.80)
            cursor.execute(
                "SELECT COUNT(*) FROM patterns WHERE confidence > 0.80"
            )
            high_confidence = cursor.fetchone()[0]
            
            # Medium confidence (0.50-0.80)
            cursor.execute(
                "SELECT COUNT(*) FROM patterns WHERE confidence > 0.50 AND confidence <= 0.80"
            )
            medium_confidence = cursor.fetchone()[0]
            
            # Low confidence (<0.50)
            cursor.execute(
                "SELECT COUNT(*) FROM patterns WHERE confidence <= 0.50"
            )
            low_confidence = cursor.fetchone()[0]
            
            total = high_confidence + medium_confidence + low_confidence
            
            return {
                'high_confidence': high_confidence,
                'medium_confidence': medium_confidence,
                'low_confidence': low_confidence,
                'distribution': {
                    'high_pct': round(high_confidence / total * 100, 1) if total > 0 else 0,
                    'medium_pct': round(medium_confidence / total * 100, 1) if total > 0 else 0,
                    'low_pct': round(low_confidence / total * 100, 1) if total > 0 else 0,
                }
            }
            
        except Exception as e:
            logger.warning(f"Confidence distribution collection failed: {e}")
            return {'error': str(e)}
    
    def _get_decay_analysis(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get pattern decay analysis from Tier 2."""
        try:
            # Check if decay tracking exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='pattern_decay_history'"
            )
            if not cursor.fetchone():
                return {'status': 'not_available'}
            
            # Recent decay events (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).timestamp()
            cursor.execute(
                "SELECT COUNT(*) FROM pattern_decay_history WHERE decay_timestamp > ?",
                (thirty_days_ago,)
            )
            recent_decay_events = cursor.fetchone()[0]
            
            # Average decay rate
            cursor.execute(
                "SELECT AVG(confidence_delta) FROM pattern_decay_history WHERE decay_timestamp > ?",
                (thirty_days_ago,)
            )
            avg_decay_result = cursor.fetchone()[0]
            avg_decay_rate = abs(round(avg_decay_result, 3)) if avg_decay_result else 0
            
            return {
                'recent_decay_events': recent_decay_events,
                'avg_decay_rate': avg_decay_rate,
                'decay_tracking': 'enabled',
            }
            
        except Exception as e:
            logger.warning(f"Decay analysis collection failed: {e}")
            return {'error': str(e)}
    
    def _get_relationship_stats(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get relationship statistics from Tier 2."""
        try:
            # Check if relationships table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='relationships'"
            )
            if not cursor.fetchone():
                return {'status': 'not_available'}
            
            # Total relationships
            cursor.execute("SELECT COUNT(*) FROM relationships")
            total_relationships = cursor.fetchone()[0]
            
            # Relationships by type
            cursor.execute(
                "SELECT relationship_type, COUNT(*) as count FROM relationships "
                "GROUP BY relationship_type ORDER BY count DESC"
            )
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'total_relationships': total_relationships,
                'by_type': by_type,
            }
            
        except Exception as e:
            logger.warning(f"Relationship stats collection failed: {e}")
            return {'error': str(e)}
    
    # ============ Tier 3 Helper Methods ============
    
    def _get_code_metrics(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get code metrics from Tier 3."""
        try:
            # Check if code_metrics table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='code_metrics'"
            )
            if not cursor.fetchone():
                return {'status': 'not_available'}
            
            # Total files tracked
            cursor.execute("SELECT COUNT(DISTINCT file_path) FROM code_metrics")
            total_files = cursor.fetchone()[0]
            
            # Code hotspots (files with high churn)
            cursor.execute(
                "SELECT COUNT(*) FROM code_metrics WHERE churn_rate > 0.1"
            )
            hotspots = cursor.fetchone()[0]
            
            return {
                'total_files_tracked': total_files,
                'hotspots': hotspots,
            }
            
        except Exception as e:
            logger.warning(f"Code metrics collection failed: {e}")
            return {'error': str(e)}
    
    def _get_git_activity(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get git activity from Tier 3."""
        try:
            # Check if git_activity table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='git_activity'"
            )
            if not cursor.fetchone():
                return {'status': 'not_available'}
            
            # Recent commits (last 7 days)
            seven_days_ago = (datetime.now() - timedelta(days=7)).timestamp()
            cursor.execute(
                "SELECT COUNT(*) FROM git_activity WHERE commit_timestamp > ?",
                (seven_days_ago,)
            )
            recent_commits = cursor.fetchone()[0]
            
            return {
                'recent_commits': recent_commits,
            }
            
        except Exception as e:
            logger.warning(f"Git activity collection failed: {e}")
            return {'error': str(e)}
    
    def _get_developer_patterns(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get developer patterns from Tier 3."""
        try:
            # Check if developer_patterns table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='developer_patterns'"
            )
            if not cursor.fetchone():
                return {'status': 'not_available'}
            
            # Total patterns learned
            cursor.execute("SELECT COUNT(*) FROM developer_patterns")
            total_patterns = cursor.fetchone()[0]
            
            return {
                'total_patterns_learned': total_patterns,
            }
            
        except Exception as e:
            logger.warning(f"Developer patterns collection failed: {e}")
            return {'error': str(e)}
    
    # ============ Health Scoring & Recommendations ============
    
    def _calculate_brain_health_score(self, analytics: Dict[str, Any]) -> float:
        """
        Calculate overall brain health score (0-100).
        
        Scoring criteria:
        - Tier 1 health: 30 points
        - Tier 2 health: 40 points
        - Tier 3 health: 20 points
        - Data quality: 10 points
        """
        score = 0.0
        
        # Tier 1 scoring (30 points)
        tier1 = analytics.get('tier1', {})
        if tier1.get('status') == 'healthy':
            score += 15  # Base health
            
            # Retention rate bonus
            conversations = tier1.get('conversations', {})
            retention_rate = conversations.get('retention_rate', 0)
            if retention_rate > 80:
                score += 10
            elif retention_rate > 60:
                score += 5
            
            # Token budget bonus
            tokens = tier1.get('tokens', {})
            budget_usage = tokens.get('budget_usage_pct', 0)
            if budget_usage < 80:
                score += 5
        
        # Tier 2 scoring (40 points)
        tier2 = analytics.get('tier2', {})
        if tier2.get('status') == 'healthy':
            score += 20  # Base health
            
            # Confidence distribution bonus
            confidence = tier2.get('confidence', {})
            dist = confidence.get('distribution', {})
            high_pct = dist.get('high_pct', 0)
            if high_pct > 60:
                score += 15
            elif high_pct > 40:
                score += 10
            elif high_pct > 20:
                score += 5
        
        # Tier 3 scoring (20 points)
        tier3 = analytics.get('tier3', {})
        if tier3.get('status') == 'healthy':
            score += 10  # Base health
            
            # Activity bonus
            git = tier3.get('git_activity', {})
            if git.get('recent_commits', 0) > 0:
                score += 10
        
        # Data quality bonus (10 points)
        if tier1.get('status') == 'healthy' and tier2.get('status') == 'healthy':
            score += 10
        
        return round(min(100.0, score), 1)
    
    def _generate_recommendations(self, analytics: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations based on analytics.
        
        Args:
            analytics: Complete analytics data
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Tier 1 recommendations
        tier1 = analytics.get('tier1', {})
        if tier1.get('status') == 'healthy':
            tokens = tier1.get('tokens', {})
            budget_usage = tokens.get('budget_usage_pct', 0)
            if budget_usage > 80:
                recommendations.append(
                    "High token budget usage (>80%) - consider running 'optimize' to clean up old conversations"
                )
            
            conversations = tier1.get('conversations', {})
            retention_rate = conversations.get('retention_rate', 0)
            if retention_rate < 60:
                recommendations.append(
                    "Low conversation retention rate (<60%) - conversations may not be accessed frequently"
                )
        
        # Tier 2 recommendations
        tier2 = analytics.get('tier2', {})
        if tier2.get('status') == 'healthy':
            confidence = tier2.get('confidence', {})
            low_confidence = confidence.get('low_confidence', 0)
            if low_confidence > 50:
                recommendations.append(
                    f"High number of low-confidence patterns ({low_confidence}) - consider running pattern cleanup"
                )
            
            patterns = tier2.get('patterns', {})
            total_patterns = patterns.get('total_patterns', 0)
            if total_patterns > 5000:
                recommendations.append(
                    "Large pattern database (>5000) - consider archiving old patterns to improve performance"
                )
        
        # Tier 3 recommendations
        tier3 = analytics.get('tier3', {})
        if tier3.get('status') == 'healthy':
            code_metrics = tier3.get('code_metrics', {})
            hotspots = code_metrics.get('hotspots', 0)
            if hotspots > 20:
                recommendations.append(
                    f"High number of code hotspots ({hotspots}) - these files change frequently and may need refactoring"
                )
        
        return recommendations
