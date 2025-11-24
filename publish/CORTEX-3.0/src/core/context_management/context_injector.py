"""
CORTEX Context Injector
Standardized context injection for all agent responses

Phase 2: Quality & Monitoring
- Ensures EVERY response shows what context was loaded
- Why it was relevant (confidence scores)
- How it influenced the response
- Token usage transparency

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class ContextInjector:
    """
    Standardized context injection for all agent responses
    
    Ensures EVERY response shows:
    - What context was loaded (T1/T2/T3)
    - Why it was relevant (confidence scores)
    - How it influenced the response
    - Token usage transparency
    """
    
    def __init__(self, format_style: str = 'detailed'):
        """
        Initialize context injector
        
        Args:
            format_style: 'detailed', 'compact', or 'minimal'
        """
        self.format_style = format_style
    
    def inject_context_summary(
        self,
        response_text: str,
        context_data: Dict[str, Any],
        position: str = 'before'
    ) -> str:
        """
        Inject context summary into agent response
        
        Args:
            response_text: Original agent response
            context_data: Context data from UnifiedContextManager
            position: 'before' or 'after' response text
            
        Returns:
            Response with injected context summary
        """
        if self.format_style == 'detailed':
            summary = self._format_detailed_summary(context_data)
        elif self.format_style == 'compact':
            summary = self._format_compact_summary(context_data)
        else:  # minimal
            summary = self._format_minimal_summary(context_data)
        
        if position == 'before':
            return f"{summary}\n\n{response_text}"
        else:
            return f"{response_text}\n\n{summary}"
    
    def _format_detailed_summary(self, context_data: Dict[str, Any]) -> str:
        """Format detailed context summary (default)"""
        lines = []
        lines.append("<details>")
        lines.append("<summary>🧠 Context Used (Quality: {:.1f}/10)</summary>".format(
            self._calculate_quality_score(context_data)
        ))
        lines.append("")
        
        # Tier 1 summary
        tier1 = context_data.get('tier1_context', {})
        relevance1 = context_data.get('relevance_scores', {}).get('tier1', 0.0)
        if relevance1 > 0.5:
            conv_count = tier1.get('recent_conversations', 0)
            if conv_count > 0:
                lines.append(f"**Recent Work (Tier 1):** {conv_count} related conversations")
                lines.append(f"  *Relevance: {relevance1:.2f} (High)*")
                
                # Show top conversation titles
                convs = tier1.get('conversations', [])
                for conv in convs[:2]:
                    title = conv.get('title', 'Untitled')
                    age = self._format_age(conv.get('created_at'))
                    lines.append(f"  • {title} ({age})")
                lines.append("")
        
        # Tier 2 summary
        tier2 = context_data.get('tier2_context', {})
        relevance2 = context_data.get('relevance_scores', {}).get('tier2', 0.0)
        if relevance2 > 0.5:
            pattern_count = tier2.get('matched_patterns', 0)
            if pattern_count > 0:
                lines.append(f"**Learned Patterns (Tier 2):** {pattern_count} matched")
                lines.append(f"  *Relevance: {relevance2:.2f} (High)*")
                
                # Show top patterns
                patterns = tier2.get('patterns', [])
                for pattern in patterns[:2]:
                    title = pattern.get('title', 'Untitled')
                    confidence = pattern.get('confidence', 0.0)
                    lines.append(f"  • {title} (confidence: {confidence:.2f})")
                lines.append("")
        
        # Tier 3 summary
        tier3 = context_data.get('tier3_context', {})
        relevance3 = context_data.get('relevance_scores', {}).get('tier3', 0.0)
        if relevance3 > 0.5:
            insight_count = tier3.get('insights_count', 0)
            if insight_count > 0:
                lines.append(f"**Metrics (Tier 3):** {insight_count} insights")
                lines.append(f"  *Relevance: {relevance3:.2f} (High)*")
                
                # Show top insights
                insights = tier3.get('insights', [])
                for insight in insights[:2]:
                    insight_type = insight.get('insight_type', 'unknown')
                    severity = insight.get('severity', 'INFO')
                    lines.append(f"  • {insight_type.replace('_', ' ').title()} ({severity})")
                lines.append("")
        
        # Token usage
        token_usage = context_data.get('token_usage', {})
        total = token_usage.get('total', 0)
        budget = token_usage.get('budget', 500)
        within_budget = token_usage.get('within_budget', True)
        
        usage_emoji = "✅" if within_budget else "⚠️"
        lines.append(f"**Token Usage:** {usage_emoji} {total}/{budget} tokens ({total/budget*100:.0f}%)")
        
        lines.append("</details>")
        
        return "\n".join(lines)
    
    def _format_compact_summary(self, context_data: Dict[str, Any]) -> str:
        """Format compact context summary"""
        parts = []
        
        # Relevance scores
        relevance = context_data.get('relevance_scores', {})
        tier1_rel = relevance.get('tier1', 0.0)
        tier2_rel = relevance.get('tier2', 0.0)
        tier3_rel = relevance.get('tier3', 0.0)
        
        # Build summary
        if tier1_rel > 0.5:
            conv_count = context_data.get('tier1_context', {}).get('recent_conversations', 0)
            parts.append(f"T1: {conv_count} convs")
        
        if tier2_rel > 0.5:
            pattern_count = context_data.get('tier2_context', {}).get('matched_patterns', 0)
            parts.append(f"T2: {pattern_count} patterns")
        
        if tier3_rel > 0.5:
            insight_count = context_data.get('tier3_context', {}).get('insights_count', 0)
            parts.append(f"T3: {insight_count} insights")
        
        # Token usage
        token_usage = context_data.get('token_usage', {})
        total = token_usage.get('total', 0)
        budget = token_usage.get('budget', 500)
        
        summary = " | ".join(parts) if parts else "No context loaded"
        return f"🧠 **Context:** {summary} | {total}/{budget} tokens"
    
    def _format_minimal_summary(self, context_data: Dict[str, Any]) -> str:
        """Format minimal context summary"""
        quality = self._calculate_quality_score(context_data)
        token_usage = context_data.get('token_usage', {})
        total = token_usage.get('total', 0)
        
        if quality >= 8.0:
            quality_emoji = "🟢"
        elif quality >= 6.0:
            quality_emoji = "🟡"
        else:
            quality_emoji = "🔴"
        
        return f"{quality_emoji} Context: {quality:.1f}/10 | {total} tokens"
    
    def _calculate_quality_score(self, context_data: Dict[str, Any]) -> float:
        """Calculate context quality score (0-10)"""
        relevance = context_data.get('relevance_scores', {})
        
        # Average relevance across tiers
        scores = [
            relevance.get('tier1', 0.0),
            relevance.get('tier2', 0.0),
            relevance.get('tier3', 0.0)
        ]
        
        # Weight by what data is actually available
        weighted_scores = []
        if context_data.get('tier1_context', {}).get('recent_conversations', 0) > 0:
            weighted_scores.append(scores[0])
        if context_data.get('tier2_context', {}).get('matched_patterns', 0) > 0:
            weighted_scores.append(scores[1])
        if context_data.get('tier3_context', {}).get('insights_count', 0) > 0:
            weighted_scores.append(scores[2])
        
        if not weighted_scores:
            return 0.0
        
        avg_relevance = sum(weighted_scores) / len(weighted_scores)
        
        # Token efficiency bonus
        token_usage = context_data.get('token_usage', {})
        within_budget = token_usage.get('within_budget', False)
        efficiency_bonus = 0.2 if within_budget else 0.0
        
        # Cache hit bonus
        cache_hit = context_data.get('cache_hit', False)
        cache_bonus = 0.1 if cache_hit else 0.0
        
        quality = (avg_relevance + efficiency_bonus + cache_bonus) * 10
        return min(10.0, quality)
    
    def _format_age(self, timestamp_str: Optional[str]) -> str:
        """Format timestamp as human-readable age"""
        if not timestamp_str:
            return "unknown age"
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.now() - timestamp
            
            if age.days > 0:
                return f"{age.days}d ago"
            elif age.seconds > 3600:
                hours = age.seconds // 3600
                return f"{hours}h ago"
            else:
                minutes = age.seconds // 60
                return f"{minutes}m ago"
        except:
            return "unknown age"
    
    def format_for_agent(
        self,
        agent_name: str,
        response_text: str,
        context_data: Dict[str, Any]
    ) -> str:
        """
        Format context injection specifically for an agent
        
        Args:
            agent_name: Name of the agent (e.g., 'Code Executor', 'Test Generator')
            response_text: Agent's response
            context_data: Context data
            
        Returns:
            Formatted response with agent-specific context
        """
        # Agent-specific context emphasis
        agent_contexts = {
            'Code Executor': ['tier1', 'tier3'],     # Recent work + metrics
            'Test Generator': ['tier2', 'tier3'],    # Patterns + coverage
            'Validator': ['tier2', 'tier3'],         # Patterns + metrics
            'Work Planner': ['tier1', 'tier2'],      # History + patterns
            'Architect': ['tier2', 'tier3'],         # Patterns + architecture
        }
        
        relevant_tiers = agent_contexts.get(agent_name, ['tier1', 'tier2', 'tier3'])
        
        # Filter context to relevant tiers
        filtered_context = context_data.copy()
        relevance_scores = filtered_context.get('relevance_scores', {})
        
        # Emphasize relevant tiers in summary
        for tier in ['tier1', 'tier2', 'tier3']:
            if tier not in relevant_tiers:
                relevance_scores[tier] = relevance_scores.get(tier, 0.0) * 0.5  # De-emphasize
        
        filtered_context['relevance_scores'] = relevance_scores
        
        return self.inject_context_summary(response_text, filtered_context, position='before')
    
    def create_context_badge(self, context_data: Dict[str, Any]) -> str:
        """
        Create a compact badge showing context status
        
        Returns:
            Badge string like "🟢 Context: 8.5/10 | 234/500 tokens"
        """
        quality = self._calculate_quality_score(context_data)
        token_usage = context_data.get('token_usage', {})
        total = token_usage.get('total', 0)
        budget = token_usage.get('budget', 500)
        
        if quality >= 8.0:
            badge_color = "🟢"
        elif quality >= 6.0:
            badge_color = "🟡"
        else:
            badge_color = "🔴"
        
        return f"{badge_color} Context: {quality:.1f}/10 | {total}/{budget} tokens"


def create_standard_context_display(context_data: Dict[str, Any]) -> str:
    """
    Create standard context display for CORTEX responses
    
    This is a convenience function that creates a consistently formatted
    context display that can be included in any CORTEX agent response.
    
    Args:
        context_data: Context data from UnifiedContextManager.build_context()
    
    Returns:
        Formatted context display string
    """
    injector = ContextInjector(format_style='detailed')
    return injector._format_detailed_summary(context_data)


def create_compact_context_display(context_data: Dict[str, Any]) -> str:
    """
    Create compact context display for space-constrained responses
    
    Args:
        context_data: Context data from UnifiedContextManager.build_context()
    
    Returns:
        Compact context display string
    """
    injector = ContextInjector(format_style='compact')
    return injector._format_compact_summary(context_data)
