"""
Context Display Module - Makes Tier 1 context visible to users

This module provides visibility into what CORTEX remembers from past conversations,
showing relevance scores, entity overlap, and memory health indicators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.operations.base_operation_module import (
    BaseOperationModule, 
    OperationResult,
    OperationModuleMetadata,
    OperationPhase,
    OperationStatus
)


class ContextDisplayModule(BaseOperationModule):
    """
    Displays loaded Tier 1 context with transparency and control.
    
    Features:
    - Show loaded conversations with relevance scores
    - Display entity overlap breakdown
    - Context quality indicators
    - Memory health status
    """
    
    def __init__(self):
        super().__init__()
        self.module_name = "context_display"
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="context_display",
            name="Context Display Module",
            description="Displays loaded Tier 1 context with transparency and control",
            phase=OperationPhase.PROCESSING,
            priority=50,
            version="1.0",
            author="Asif Hussain",
            tags=["tier1", "context", "display"]
        )
    
    def execute(self, operation_data: Dict[str, Any]) -> OperationResult:
        """
        Display loaded Tier 1 context with formatted output.
        
        Args:
            operation_data: Contains:
                - command: "show context" | "context status" | "memory health"
                - context_data: Dict with loaded conversations and scores
                - user_request: Optional - current request for relevance
        
        Returns:
            OperationResult with formatted context display
        """
        command = operation_data.get('command', 'show context')
        context_data = operation_data.get('context_data', {})
        user_request = operation_data.get('user_request', '')
        
        if command == "show context":
            display = self._format_context_display(context_data, user_request)
        elif command == "context status":
            display = self._format_context_status(context_data)
        elif command == "memory health":
            display = self._format_memory_health(context_data)
        else:
            display = "Unknown command. Use: show context, context status, memory health"
        
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Context display generated",
            data={"display": display},
            duration_seconds=0.0
        )
    
    def _format_context_display(self, context_data: Dict[str, Any], user_request: str) -> str:
        """
        Format full context display with conversations and scores.
        
        Args:
            context_data: Loaded context with conversations and relevance scores
            user_request: Current user request for context
        
        Returns:
            Formatted markdown display
        """
        conversations = context_data.get('relevant_conversations', [])
        relevance_scores = context_data.get('relevance_scores', [])
        
        if not conversations:
            return self._format_empty_context()
        
        # Header
        display = ["# 🧠 CORTEX Context Memory\n"]
        display.append(f"**Current Request:** {user_request}\n")
        display.append(f"**Loaded Conversations:** {len(conversations)}\n")
        
        # Quality indicators
        quality = self._calculate_quality_indicators(context_data)
        display.append(f"**Quality Score:** {quality['overall_score']:.1f}/10 {quality['quality_emoji']}\n")
        display.append(f"**Freshness:** {quality['freshness_label']} ({quality['hours_since_last']}h ago)\n")
        display.append(f"**Entity Coverage:** {quality['entity_coverage']}%\n\n")
        
        display.append("---\n\n")
        
        # Individual conversations
        display.append("## 📚 Loaded Conversations\n\n")
        
        for i, (conv, score_info) in enumerate(zip(conversations, relevance_scores), 1):
            display.append(self._format_conversation_entry(i, conv, score_info))
            display.append("\n")
        
        # Footer with commands
        display.append("---\n\n")
        display.append("**💡 Control Commands:**\n")
        display.append("- `forget [topic]` - Remove conversations about specific topic\n")
        display.append("- `clear context` - Clear all Tier 1 memory (requires confirmation)\n")
        display.append("- `context status` - Quick status overview\n")
        
        return "".join(display)
    
    def _format_conversation_entry(self, index: int, conv: Dict[str, Any], score_info: Dict[str, Any]) -> str:
        """
        Format individual conversation entry.
        
        Args:
            index: Conversation number (1-based)
            conv: Conversation data
            score_info: Relevance score breakdown
        
        Returns:
            Formatted conversation entry
        """
        score = score_info.get('score', 0.0)
        conv_id = conv.get('conversation_id', 'unknown')
        summary = conv.get('summary', 'No summary available')
        timestamp = conv.get('timestamp', datetime.now())
        entities = conv.get('entities', {})
        intent = conv.get('intent', 'UNKNOWN')
        
        # Format timestamp
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        time_ago = self._format_time_ago(timestamp)
        
        # Relevance indicator
        relevance_emoji = self._get_relevance_emoji(score)
        relevance_bar = self._get_relevance_bar(score)
        
        entry = [f"### {index}. {relevance_emoji} Conversation {conv_id[-8:]} ({time_ago})\n\n"]
        entry.append(f"**Relevance:** {relevance_bar} {score:.2f}\n")
        entry.append(f"**Intent:** {intent}\n")
        entry.append(f"**Summary:** {summary}\n\n")
        
        # Entity overlap
        if entities:
            entry.append("**Entities:**\n")
            for entity_type, entity_list in entities.items():
                if entity_list:
                    entry.append(f"- **{entity_type}:** {', '.join(entity_list[:3])}")
                    if len(entity_list) > 3:
                        entry.append(f" (+{len(entity_list) - 3} more)")
                    entry.append("\n")
        
        return "".join(entry)
    
    def _format_context_status(self, context_data: Dict[str, Any]) -> str:
        """
        Format quick context status overview.
        
        Args:
            context_data: Loaded context data
        
        Returns:
            Quick status summary
        """
        conversations = context_data.get('relevant_conversations', [])
        quality = self._calculate_quality_indicators(context_data)
        
        if not conversations:
            return "📭 **Context Memory:** Empty\n\nNo recent conversations loaded."
        
        status = ["# 📊 Context Status\n\n"]
        status.append(f"**Conversations Loaded:** {len(conversations)}\n")
        status.append(f"**Quality Score:** {quality['overall_score']:.1f}/10 {quality['quality_emoji']}\n")
        status.append(f"**Freshness:** {quality['freshness_label']}\n")
        status.append(f"**Entity Coverage:** {quality['entity_coverage']}%\n")
        status.append(f"**Memory Health:** {quality['memory_health']}\n\n")
        status.append(f"*Use `show context` for detailed view*\n")
        
        return "".join(status)
    
    def _format_memory_health(self, context_data: Dict[str, Any]) -> str:
        """
        Format detailed memory health report.
        
        Args:
            context_data: Loaded context data
        
        Returns:
            Memory health report
        """
        conversations = context_data.get('relevant_conversations', [])
        relevance_scores = context_data.get('relevance_scores', [])
        
        if not conversations:
            return "🟢 **Memory Health:** Optimal (Empty state)\n\nNo conversations to analyze."
        
        # Calculate health metrics
        scores = [s.get('score', 0.0) for s in relevance_scores]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        timestamps = []
        for conv in conversations:
            ts = conv.get('timestamp', datetime.now())
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            timestamps.append(ts)
        
        oldest = min(timestamps) if timestamps else datetime.now()
        newest = max(timestamps) if timestamps else datetime.now()
        span_hours = (newest - oldest).total_seconds() / 3600
        
        # Health determination
        if avg_score >= 0.7:
            health_emoji = "🟢"
            health_status = "Excellent"
        elif avg_score >= 0.5:
            health_emoji = "🟡"
            health_status = "Good"
        else:
            health_emoji = "🟠"
            health_status = "Fair"
        
        report = [f"# {health_emoji} Memory Health Report\n\n"]
        report.append(f"**Status:** {health_status}\n")
        report.append(f"**Average Relevance:** {avg_score:.2f}\n")
        report.append(f"**Conversation Span:** {span_hours:.1f} hours\n")
        report.append(f"**Total Conversations:** {len(conversations)}\n\n")
        
        report.append("## 📈 Metrics\n\n")
        report.append(f"- **High Relevance (≥0.7):** {sum(1 for s in scores if s >= 0.7)}\n")
        report.append(f"- **Medium Relevance (0.4-0.7):** {sum(1 for s in scores if 0.4 <= s < 0.7)}\n")
        report.append(f"- **Low Relevance (<0.4):** {sum(1 for s in scores if s < 0.4)}\n\n")
        
        report.append("## 💡 Recommendations\n\n")
        if avg_score < 0.5:
            report.append("- Consider clearing old conversations: `clear context`\n")
        if span_hours > 168:  # 1 week
            report.append("- Some conversations are over a week old\n")
        if len(conversations) < 3:
            report.append("- Limited conversation history available\n")
        else:
            report.append("- Memory health is optimal ✅\n")
        
        return "".join(report)
    
    def _format_empty_context(self) -> str:
        """Format display for empty context."""
        return """# 📭 Context Memory: Empty

No recent conversations loaded.

**This means:**
- Fresh start with no prior context
- CORTEX will respond based on your current request only
- Conversations will be captured as you interact

**💡 Tip:** Say "remember this" to capture important conversations for future reference.
"""
    
    def _calculate_quality_indicators(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate context quality indicators.
        
        Args:
            context_data: Loaded context data
        
        Returns:
            Dict with quality metrics
        """
        conversations = context_data.get('relevant_conversations', [])
        relevance_scores = context_data.get('relevance_scores', [])
        
        if not conversations:
            return {
                'overall_score': 0.0,
                'quality_emoji': '📭',
                'freshness_label': 'N/A',
                'hours_since_last': 0,
                'entity_coverage': 0,
                'memory_health': 'Empty'
            }
        
        # Calculate average relevance score
        scores = [s.get('score', 0.0) for s in relevance_scores]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        overall_score = avg_score * 10  # Scale to 0-10
        
        # Quality emoji
        if overall_score >= 7:
            quality_emoji = '🟢'
        elif overall_score >= 5:
            quality_emoji = '🟡'
        else:
            quality_emoji = '🟠'
        
        # Freshness (time since most recent conversation)
        timestamps = []
        for conv in conversations:
            ts = conv.get('timestamp', datetime.now())
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            timestamps.append(ts)
        
        newest = max(timestamps) if timestamps else datetime.now()
        hours_since = (datetime.now() - newest).total_seconds() / 3600
        
        if hours_since < 1:
            freshness_label = "Very Fresh"
        elif hours_since < 24:
            freshness_label = "Fresh"
        elif hours_since < 168:  # 1 week
            freshness_label = "Recent"
        else:
            freshness_label = "Stale"
        
        # Entity coverage (simplified - would need user request entities to calculate properly)
        entity_coverage = min(100, len(conversations) * 20)  # Rough estimate
        
        # Memory health
        if overall_score >= 7 and hours_since < 24:
            memory_health = "🟢 Excellent"
        elif overall_score >= 5:
            memory_health = "🟡 Good"
        else:
            memory_health = "🟠 Fair"
        
        return {
            'overall_score': overall_score,
            'quality_emoji': quality_emoji,
            'freshness_label': freshness_label,
            'hours_since_last': int(hours_since),
            'entity_coverage': entity_coverage,
            'memory_health': memory_health
        }
    
    def _get_relevance_emoji(self, score: float) -> str:
        """Get emoji for relevance score."""
        if score >= 0.7:
            return "🔥"
        elif score >= 0.5:
            return "✨"
        elif score >= 0.3:
            return "💡"
        else:
            return "📄"
    
    def _get_relevance_bar(self, score: float) -> str:
        """Get visual bar for relevance score."""
        filled = int(score * 10)
        bar = "█" * filled + "░" * (10 - filled)
        return bar
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as relative time."""
        delta = datetime.now() - timestamp
        
        if delta < timedelta(minutes=1):
            return "just now"
        elif delta < timedelta(hours=1):
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m ago"
        elif delta < timedelta(days=1):
            hours = int(delta.total_seconds() / 3600)
            return f"{hours}h ago"
        elif delta < timedelta(weeks=1):
            days = delta.days
            return f"{days}d ago"
        else:
            weeks = delta.days // 7
            return f"{weeks}w ago"
    
    def can_handle(self, operation_type: str) -> bool:
        """Check if this module can handle the operation."""
        return operation_type in [
            "show_context",
            "context_status",
            "memory_health"
        ]
