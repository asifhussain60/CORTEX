"""
CORTEX Tier 1: Token Metrics Collector
Collect and track token usage metrics for cost monitoring and optimization analysis.

Provides real-time visibility into token consumption, cost estimation,
and optimization effectiveness.
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import json


class TokenMetricsCollector:
    """
    Collect token usage metrics for dashboard and monitoring.
    
    Key Features:
    - Session token tracking
    - Cost estimation ($0.000003 per token)
    - Optimization rate calculation
    - Database size monitoring
    - Real-time metrics for dashboard
    """
    
    # Cost per token (Claude Sonnet pricing)
    COST_PER_TOKEN = 0.000003  # $0.000003 per token
    
    def __init__(self, working_memory, knowledge_graph=None):
        """
        Initialize metrics collector.
        
        Args:
            working_memory: WorkingMemory instance
            knowledge_graph: Optional KnowledgeGraph instance
        """
        self.working_memory = working_memory
        self.knowledge_graph = knowledge_graph
        
        # Session tracking
        self._session_start = datetime.now()
        self._session_id = self._generate_session_id()
        
        # Token counters
        self._session_tokens_original = 0  # Before optimization
        self._session_tokens_optimized = 0  # After optimization
        self._request_count = 0
        
        # Detailed tracking
        self._requests: List[Dict[str, Any]] = []
        
        # Metrics cache (refresh every 10 seconds)
        self._metrics_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 10
    
    def record_request(
        self,
        original_tokens: int,
        optimized_tokens: int,
        optimization_method: str = "unknown",
        quality_score: Optional[float] = None
    ) -> None:
        """
        Record tokens for a single request.
        
        Args:
            original_tokens: Token count before optimization
            optimized_tokens: Token count after optimization
            optimization_method: Method used for optimization
            quality_score: Optional quality score (0.0 to 1.0)
            
        Example:
            >>> collector = TokenMetricsCollector(working_memory)
            >>> collector.record_request(
            ...     original_tokens=25000,
            ...     optimized_tokens=10000,
            ...     optimization_method="ml_context_compression",
            ...     quality_score=0.95
            ... )
        """
        self._session_tokens_original += original_tokens
        self._session_tokens_optimized += optimized_tokens
        self._request_count += 1
        
        # Store detailed request info
        request_info = {
            "timestamp": datetime.now().isoformat(),
            "request_number": self._request_count,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": original_tokens - optimized_tokens,
            "reduction_percentage": (
                (original_tokens - optimized_tokens) / original_tokens * 100
                if original_tokens > 0 else 0
            ),
            "optimization_method": optimization_method,
            "quality_score": quality_score
        }
        
        self._requests.append(request_info)
        
        # Invalidate cache
        self._metrics_cache = None
    
    def get_current_metrics(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get current token metrics for dashboard.
        
        Args:
            force_refresh: Force refresh even if cache is valid
        
        Returns:
            Dict with comprehensive metrics
            
        Example:
            >>> collector = TokenMetricsCollector(working_memory)
            >>> metrics = collector.get_current_metrics()
            >>> print(f"Session cost: ${metrics['session_cost_usd']:.4f}")
        """
        # Check cache
        now = datetime.now()
        if not force_refresh and self._metrics_cache and self._cache_timestamp:
            cache_age = (now - self._cache_timestamp).total_seconds()
            if cache_age < self._cache_ttl_seconds:
                return self._metrics_cache
        
        # Calculate metrics
        conversations = self.working_memory.get_recent_conversations(limit=50)
        cache_tokens = self._count_conversation_tokens(conversations)
        
        # Get pattern count if knowledge graph available
        pattern_count = 0
        if self.knowledge_graph:
            try:
                patterns = self.knowledge_graph.get_all_patterns()
                pattern_count = len(patterns)
            except Exception:
                pattern_count = 0
        
        # Get database sizes
        tier1_size = self._get_database_size(self.working_memory.db_path)
        tier2_size = 0
        if self.knowledge_graph and hasattr(self.knowledge_graph, 'db_path'):
            tier2_size = self._get_database_size(self.knowledge_graph.db_path)
        
        # Calculate session metrics
        session_duration = (now - self._session_start).total_seconds()
        
        metrics = {
            # Session tracking
            "session_id": self._session_id,
            "session_start": self._session_start.isoformat(),
            "session_duration_seconds": session_duration,
            "session_duration_minutes": session_duration / 60,
            
            # Token metrics
            "session_tokens_original": self._session_tokens_original,
            "session_tokens_optimized": self._session_tokens_optimized,
            "session_tokens_saved": self._session_tokens_original - self._session_tokens_optimized,
            "cache_tokens": cache_tokens,
            
            # Cost metrics
            "session_cost_original_usd": self._session_tokens_original * self.COST_PER_TOKEN,
            "session_cost_optimized_usd": self._session_tokens_optimized * self.COST_PER_TOKEN,
            "session_cost_saved_usd": (
                (self._session_tokens_original - self._session_tokens_optimized) 
                * self.COST_PER_TOKEN
            ),
            
            # Optimization metrics
            "optimization_percentage": self._calculate_optimization_rate(),
            "request_count": self._request_count,
            "average_tokens_per_request": (
                self._session_tokens_optimized / self._request_count
                if self._request_count > 0 else 0
            ),
            
            # Memory metrics
            "conversation_count": len(conversations),
            "pattern_count": pattern_count,
            "tier1_bytes": tier1_size,
            "tier1_mb": tier1_size / (1024 * 1024),
            "tier2_bytes": tier2_size,
            "tier2_mb": tier2_size / (1024 * 1024),
            "total_db_mb": (tier1_size + tier2_size) / (1024 * 1024),
            
            # Cache health
            "cache_utilization_percentage": (cache_tokens / 40_000) * 100,  # Soft limit
            "cache_status": self._get_cache_status(cache_tokens),
            
            # Timestamp
            "metrics_timestamp": now.isoformat(),
            "metrics_cache_age_seconds": 0
        }
        
        # Cache the result
        self._metrics_cache = metrics
        self._cache_timestamp = now
        
        return metrics
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get session summary with detailed breakdown.
        
        Returns:
            Dict with session summary
        """
        metrics = self.get_current_metrics()
        
        # Calculate additional summary stats
        if self._requests:
            best_reduction = max(
                self._requests, 
                key=lambda r: r['reduction_percentage']
            )
            worst_reduction = min(
                self._requests,
                key=lambda r: r['reduction_percentage']
            )
            
            # Calculate average quality (only for requests with quality scores)
            quality_scores = [
                r['quality_score'] for r in self._requests 
                if r['quality_score'] is not None
            ]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None
        else:
            best_reduction = None
            worst_reduction = None
            avg_quality = None
        
        summary = {
            "session_id": self._session_id,
            "session_duration": metrics['session_duration_minutes'],
            "total_requests": self._request_count,
            "tokens": {
                "original_total": self._session_tokens_original,
                "optimized_total": self._session_tokens_optimized,
                "saved_total": self._session_tokens_original - self._session_tokens_optimized,
                "average_per_request": metrics['average_tokens_per_request']
            },
            "cost": {
                "original_usd": metrics['session_cost_original_usd'],
                "optimized_usd": metrics['session_cost_optimized_usd'],
                "saved_usd": metrics['session_cost_saved_usd']
            },
            "optimization": {
                "average_reduction_percentage": metrics['optimization_percentage'],
                "best_reduction": best_reduction,
                "worst_reduction": worst_reduction,
                "average_quality_score": avg_quality
            },
            "memory": {
                "conversations": metrics['conversation_count'],
                "patterns": metrics['pattern_count'],
                "database_size_mb": metrics['total_db_mb']
            }
        }
        
        return summary
    
    def get_request_history(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get request history.
        
        Args:
            limit: Optional limit on number of requests to return
        
        Returns:
            List of request dicts
        """
        if limit is None:
            return self._requests.copy()
        return self._requests[-limit:]
    
    def export_session_data(self, output_path: Optional[Path] = None) -> Path:
        """
        Export session data to JSON file.
        
        Args:
            output_path: Optional output file path
        
        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = Path(f"cortex-metrics-{self._session_id}.json")
        
        data = {
            "session_summary": self.get_session_summary(),
            "current_metrics": self.get_current_metrics(force_refresh=True),
            "request_history": self._requests
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def reset_session(self) -> None:
        """Reset session metrics (start new session)."""
        self._session_start = datetime.now()
        self._session_id = self._generate_session_id()
        self._session_tokens_original = 0
        self._session_tokens_optimized = 0
        self._request_count = 0
        self._requests = []
        self._metrics_cache = None
        self._cache_timestamp = None
    
    # ========== Helper Methods ==========
    
    def _calculate_optimization_rate(self) -> float:
        """
        Calculate optimization percentage.
        
        Returns:
            Optimization rate (0.0 to 100.0)
        """
        if self._session_tokens_original == 0:
            return 0.0
        
        tokens_saved = self._session_tokens_original - self._session_tokens_optimized
        return (tokens_saved / self._session_tokens_original) * 100
    
    def _count_conversation_tokens(self, conversations: List[Any]) -> int:
        """
        Count total tokens across all conversations.
        
        Args:
            conversations: List of Conversation objects or dicts
        
        Returns:
            Total estimated token count
        """
        from dataclasses import is_dataclass
        
        total = 0
        for conv in conversations:
            # Handle Conversation dataclass objects
            if is_dataclass(conv) and not isinstance(conv, type):
                # Fetch messages from working_memory
                messages = self.working_memory.get_messages(conv.conversation_id)
                
                for msg in messages:
                    content = msg.get('content', '')
                    if isinstance(content, str):
                        total += TokenMetricsCollector._count_tokens(content)
            
            # Handle dict conversations (legacy)
            elif isinstance(conv, dict):
                messages = conv.get('messages', [])
                for msg in messages:
                    content = msg.get('content', '')
                    if isinstance(content, str):
                        total += TokenMetricsCollector._count_tokens(content)
        
        return total
    
    @staticmethod
    def _count_tokens(text: str) -> int:
        """
        Estimate token count (rough: 1 token ≈ 4 characters).
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Estimated token count
        """
        if not text or not isinstance(text, str):
            return 0
        return max(1, len(text) // 4)
    
    @staticmethod
    def _get_database_size(db_path: Path) -> int:
        """
        Get database file size in bytes.
        
        Args:
            db_path: Path to database file
        
        Returns:
            File size in bytes (0 if not exists)
        """
        try:
            if os.path.exists(db_path):
                return os.path.getsize(db_path)
        except Exception:
            pass
        return 0
    
    @staticmethod
    def _get_cache_status(token_count: int) -> str:
        """
        Get cache status string.
        
        Args:
            token_count: Current token count
        
        Returns:
            Status string
        """
        if token_count >= 50_000:
            return "CRITICAL"
        elif token_count >= 40_000:
            return "WARNING"
        elif token_count >= 30_000:
            return "ELEVATED"
        else:
            return "OK"
    
    @staticmethod
    def _generate_session_id() -> str:
        """
        Generate unique session ID with microseconds for uniqueness.
        
        Returns:
            Session ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        return f"session-{timestamp}"


class TokenMetricsFormatter:
    """Format token metrics for display."""
    
    @staticmethod
    def format_tokens(token_count: int) -> str:
        """
        Format token count with commas.
        
        Args:
            token_count: Number of tokens
        
        Returns:
            Formatted string
        """
        return f"{token_count:,}"
    
    @staticmethod
    def format_cost(cost_usd: float) -> str:
        """
        Format cost in USD.
        
        Args:
            cost_usd: Cost in USD
        
        Returns:
            Formatted string
        """
        return f"${cost_usd:.4f}"
    
    @staticmethod
    def format_percentage(percentage: float) -> str:
        """
        Format percentage.
        
        Args:
            percentage: Percentage value
        
        Returns:
            Formatted string
        """
        return f"{percentage:.1f}%"
    
    @staticmethod
    def format_filesize(bytes_count: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            bytes_count: Size in bytes
        
        Returns:
            Formatted string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
        
        Returns:
            Formatted string
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def format_metrics_summary(metrics: Dict[str, Any]) -> str:
        """
        Format metrics as human-readable summary.
        
        Args:
            metrics: Metrics dict from get_current_metrics()
        
        Returns:
            Multi-line summary string
        """
        lines = [
            "=== CORTEX Token Metrics ===",
            f"Session: {metrics['session_id']}",
            f"Duration: {TokenMetricsFormatter.format_duration(metrics['session_duration_seconds'])}",
            "",
            "Tokens:",
            f"  Original:  {TokenMetricsFormatter.format_tokens(metrics['session_tokens_original'])}",
            f"  Optimized: {TokenMetricsFormatter.format_tokens(metrics['session_tokens_optimized'])}",
            f"  Saved:     {TokenMetricsFormatter.format_tokens(metrics['session_tokens_saved'])} "
            f"({TokenMetricsFormatter.format_percentage(metrics['optimization_percentage'])})",
            "",
            "Cost:",
            f"  Original:  {TokenMetricsFormatter.format_cost(metrics['session_cost_original_usd'])}",
            f"  Optimized: {TokenMetricsFormatter.format_cost(metrics['session_cost_optimized_usd'])}",
            f"  Saved:     {TokenMetricsFormatter.format_cost(metrics['session_cost_saved_usd'])}",
            "",
            "Memory:",
            f"  Conversations: {metrics['conversation_count']}",
            f"  Patterns:      {metrics['pattern_count']}",
            f"  Database:      {TokenMetricsFormatter.format_filesize(metrics['tier1_bytes'] + metrics['tier2_bytes'])}",
            "",
            f"Cache: {metrics['cache_status']} ({TokenMetricsFormatter.format_tokens(metrics['cache_tokens'])} tokens)",
            "=" * 29
        ]
        
        return "\n".join(lines)
