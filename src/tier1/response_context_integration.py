"""
Response Context Integration - Injects context summaries into CORTEX responses

This module integrates context visibility into standard response templates,
showing users what CORTEX remembers when responding.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, Optional


class ResponseContextIntegration:
    """
    Integrates context summaries into CORTEX response templates.
    
    Features:
    - Collapsible context summary section
    - Quality indicators
    - Show only when context is loaded
    - Non-intrusive optional display
    """
    
    @staticmethod
    def inject_context_summary(response: str, context_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Inject context summary into response template.
        
        Args:
            response: Original response text
            context_data: Loaded context data (from context_injector)
        
        Returns:
            Response with context summary injected (if context available)
        """
        if not context_data or not context_data.get('relevant_conversations'):
            # No context loaded - remove placeholder
            return response.replace('[CONTEXT_SUMMARY]\n\n', '')
        
        # Generate context summary
        summary = ResponseContextIntegration._generate_context_summary(context_data)
        
        # Inject into response
        return response.replace('[CONTEXT_SUMMARY]', summary)
    
    @staticmethod
    def _generate_context_summary(context_data: Dict[str, Any]) -> str:
        """
        Generate collapsible context summary section.
        
        Args:
            context_data: Loaded context data
        
        Returns:
            Formatted context summary markdown
        """
        conversations = context_data.get('relevant_conversations', [])
        relevance_scores = context_data.get('relevance_scores', [])
        
        # Calculate quality indicators
        quality = ResponseContextIntegration._calculate_quality_indicators(
            conversations, relevance_scores
        )
        
        # Build collapsible summary
        summary = [
            "\n<details>",
            f"<summary>🧠 <b>Context Memory ({len(conversations)} conversations loaded, "
            f"Quality: {quality['overall_score']:.1f}/10 {quality['quality_emoji']})</b></summary>",
            "",
            f"**Freshness:** {quality['freshness_label']} ({quality['hours_since_last']}h ago)  ",
            f"**Entity Coverage:** {quality['entity_coverage']}%  ",
            f"**Memory Health:** {quality['memory_health']}",
            "",
            "*Use `show context` for detailed view*",
            "</details>",
            ""
        ]
        
        return "\n".join(summary)
    
    @staticmethod
    def _calculate_quality_indicators(conversations: list, relevance_scores: list) -> Dict[str, Any]:
        """
        Calculate quality indicators for context summary.
        
        Args:
            conversations: List of loaded conversations
            relevance_scores: List of relevance score dicts
        
        Returns:
            Dict with quality metrics
        """
        from datetime import datetime
        
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
                try:
                    ts = datetime.fromisoformat(ts)
                except (ValueError, TypeError):
                    ts = datetime.now()
            timestamps.append(ts)
        
        newest = max(timestamps) if timestamps else datetime.now()
        hours_since = int((datetime.now() - newest).total_seconds() / 3600)
        
        if hours_since < 1:
            freshness_label = "Very Fresh"
        elif hours_since < 24:
            freshness_label = "Fresh"
        elif hours_since < 168:  # 1 week
            freshness_label = "Recent"
        else:
            freshness_label = "Stale"
        
        # Entity coverage (simplified estimate)
        entity_coverage = min(100, len(conversations) * 20)
        
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
            'hours_since_last': hours_since,
            'entity_coverage': entity_coverage,
            'memory_health': memory_health
        }
    
    @staticmethod
    def should_show_context(context_data: Optional[Dict[str, Any]]) -> bool:
        """
        Determine if context summary should be shown.
        
        Args:
            context_data: Loaded context data
        
        Returns:
            True if context should be displayed
        """
        if not context_data:
            return False
        
        conversations = context_data.get('relevant_conversations', [])
        return len(conversations) > 0
