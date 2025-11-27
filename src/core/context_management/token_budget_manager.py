"""
CORTEX Token Budget Manager
Enforces token budget across all tiers with dynamic allocation

Phase 1: Foundation
- Allocate tokens dynamically based on relevance
- High relevance tier gets more tokens
- Gracefully degrade (remove least relevant first)
- Warn user when context was truncated

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class BudgetAllocation:
    """Token budget allocation for a single tier"""
    tier_name: str
    allocated_tokens: int
    relevance_score: float
    priority: int


class TokenBudgetManager:
    """
    Enforce token budget across all tiers
    
    Strategy:
    - Allocate tokens proportionally based on relevance
    - High relevance tier gets more tokens
    - Gracefully degrade (remove least relevant first)
    - Warn user when context was truncated
    """
    
    def __init__(self, total_budget: int = 500):
        """
        Initialize token budget manager
        
        Args:
            total_budget: Maximum tokens allowed for context (default: 500)
        """
        self.total_budget = total_budget
        self.min_tier_allocation = 50  # Minimum tokens per tier
        self.reserved_tokens = 50  # Reserve for summary overhead
    
    def allocate_budget(
        self,
        tier_relevance_scores: Dict[str, float],
        custom_priorities: Optional[Dict[str, int]] = None
    ) -> Dict[str, int]:
        """
        Allocate budget proportionally based on relevance scores
        
        Args:
            tier_relevance_scores: Dict mapping tier name to relevance (0.0-1.0)
                Example: {'tier1': 0.9, 'tier2': 0.7, 'tier3': 0.4}
            custom_priorities: Optional custom priority overrides
                Example: {'tier1': 1, 'tier2': 2, 'tier3': 3}
        
        Returns:
            Dict mapping tier name to allocated token budget
            Example: {'tier1': 225, 'tier2': 175, 'tier3': 100}
        """
        available_budget = self.total_budget - self.reserved_tokens
        
        # Filter out tiers with very low relevance (< 0.2)
        active_tiers = {
            tier: score
            for tier, score in tier_relevance_scores.items()
            if score >= 0.2
        }
        
        if not active_tiers:
            # No relevant tiers, give equal minimum allocation
            equal_share = available_budget // len(tier_relevance_scores)
            return {tier: equal_share for tier in tier_relevance_scores}
        
        # Calculate total relevance
        total_relevance = sum(active_tiers.values())
        
        # Allocate proportionally
        allocations = {}
        for tier, score in tier_relevance_scores.items():
            if tier in active_tiers:
                proportion = score / total_relevance
                allocation = int(available_budget * proportion)
                allocations[tier] = max(self.min_tier_allocation, allocation)
            else:
                allocations[tier] = 0
        
        # Adjust if total exceeds budget
        total_allocated = sum(allocations.values())
        if total_allocated > available_budget:
            # Scale down proportionally
            scale_factor = available_budget / total_allocated
            allocations = {
                tier: int(tokens * scale_factor)
                for tier, tokens in allocations.items()
            }
        
        return allocations
    
    def check_budget_compliance(
        self,
        tier_usage: Dict[str, int],
        tier_budgets: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Check if tier token usage complies with allocated budgets
        
        Args:
            tier_usage: Actual token usage per tier
            tier_budgets: Allocated budgets per tier
        
        Returns:
            {
                'compliant': bool,
                'total_usage': int,
                'total_budget': int,
                'overages': {...},  # Tiers that exceeded budget
                'warnings': [...]   # Warning messages
            }
        """
        total_usage = sum(tier_usage.values())
        overages = {}
        warnings = []
        
        for tier, usage in tier_usage.items():
            budget = tier_budgets.get(tier, 0)
            if usage > budget:
                overage = usage - budget
                overages[tier] = {
                    'budget': budget,
                    'usage': usage,
                    'overage': overage,
                    'overage_percent': (overage / budget * 100) if budget > 0 else 0
                }
                warnings.append(
                    f"{tier}: Exceeded budget by {overage} tokens "
                    f"({overage / budget * 100:.1f}%)"
                )
        
        if total_usage > self.total_budget:
            warnings.append(
                f"Total usage ({total_usage}) exceeds total budget ({self.total_budget}) "
                f"by {total_usage - self.total_budget} tokens"
            )
        
        return {
            'compliant': len(overages) == 0 and total_usage <= self.total_budget,
            'total_usage': total_usage,
            'total_budget': self.total_budget,
            'overages': overages,
            'warnings': warnings,
            'within_budget_percent': (self.total_budget - total_usage) / self.total_budget * 100 if total_usage < self.total_budget else 0
        }
    
    def suggest_optimization(
        self,
        tier_usage: Dict[str, int],
        tier_budgets: Dict[str, int],
        tier_relevance: Dict[str, float]
    ) -> List[str]:
        """
        Suggest optimizations when budget is exceeded
        
        Args:
            tier_usage: Actual token usage per tier
            tier_budgets: Allocated budgets per tier
            tier_relevance: Relevance scores per tier
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        compliance = self.check_budget_compliance(tier_usage, tier_budgets)
        
        if compliance['compliant']:
            return ["Context is within budget. No optimizations needed."]
        
        # Find least relevant tier with overage
        for tier, overage_info in compliance['overages'].items():
            relevance = tier_relevance.get(tier, 0.0)
            
            if relevance < 0.5:
                suggestions.append(
                    f"Consider excluding {tier} (low relevance: {relevance:.2f}) "
                    f"to save {overage_info['usage']} tokens"
                )
            else:
                suggestions.append(
                    f"Reduce {tier} context by {overage_info['overage']} tokens "
                    f"(currently using {overage_info['usage']}/{overage_info['budget']})"
                )
        
        # Suggest caching
        if compliance['total_usage'] > self.total_budget * 0.8:
            suggestions.append(
                "Consider enabling context caching to reduce redundant queries"
            )
        
        # Suggest summary instead of full context
        if any(usage > 200 for usage in tier_usage.values()):
            suggestions.append(
                "Use summarized context instead of full details for high-token tiers"
            )
        
        return suggestions
    
    def truncate_context(
        self,
        context: Dict[str, Any],
        target_tokens: int,
        current_tokens: int
    ) -> Tuple[Dict[str, Any], int, List[str]]:
        """
        Truncate context to fit within target token budget
        
        Args:
            context: Context data to truncate
            target_tokens: Target token budget
            current_tokens: Current token usage
        
        Returns:
            (truncated_context, new_token_count, removed_items)
        """
        if current_tokens <= target_tokens:
            return context, current_tokens, []
        
        removed_items = []
        truncated = context.copy()
        
        # Strategy: Remove least important items first
        # 1. Remove detailed messages, keep summaries
        if 'tier1_context' in truncated and 'conversations' in truncated['tier1_context']:
            convs = truncated['tier1_context']['conversations']
            if len(convs) > 3:
                removed_count = len(convs) - 3
                truncated['tier1_context']['conversations'] = convs[:3]
                removed_items.append(f"Removed {removed_count} older conversations")
        
        # 2. Limit pattern details
        if 'tier2_context' in truncated and 'patterns' in truncated['tier2_context']:
            patterns = truncated['tier2_context']['patterns']
            if len(patterns) > 2:
                removed_count = len(patterns) - 2
                truncated['tier2_context']['patterns'] = patterns[:2]
                removed_items.append(f"Removed {removed_count} lower-confidence patterns")
        
        # 3. Limit metrics
        if 'tier3_context' in truncated and 'insights' in truncated['tier3_context']:
            insights = truncated['tier3_context']['insights']
            if len(insights) > 2:
                removed_count = len(insights) - 2
                truncated['tier3_context']['insights'] = insights[:2]
                removed_items.append(f"Removed {removed_count} lower-priority insights")
        
        # Estimate new token count (rough)
        import json
        new_tokens = len(json.dumps(truncated)) // 4
        
        return truncated, new_tokens, removed_items
    
    def get_budget_status(
        self,
        tier_usage: Dict[str, int],
        tier_budgets: Dict[str, int]
    ) -> str:
        """
        Get human-readable budget status
        
        Args:
            tier_usage: Actual token usage per tier
            tier_budgets: Allocated budgets per tier
        
        Returns:
            Status string with emoji indicator
        """
        compliance = self.check_budget_compliance(tier_usage, tier_budgets)
        
        if compliance['compliant']:
            usage_percent = (compliance['total_usage'] / compliance['total_budget']) * 100
            if usage_percent < 70:
                return f"✅ Excellent ({usage_percent:.0f}% of budget)"
            elif usage_percent < 90:
                return f"🟢 Good ({usage_percent:.0f}% of budget)"
            else:
                return f"🟡 Near Limit ({usage_percent:.0f}% of budget)"
        else:
            overage = compliance['total_usage'] - compliance['total_budget']
            overage_percent = (overage / compliance['total_budget']) * 100
            return f"🔴 Over Budget (+{overage_percent:.0f}%, {overage} tokens)"
    
    def calculate_optimal_budget(
        self,
        historical_usage: List[Dict[str, int]],
        target_compliance_rate: float = 0.95
    ) -> int:
        """
        Calculate optimal total budget based on historical usage
        
        Args:
            historical_usage: List of past tier usage dicts
            target_compliance_rate: Desired compliance rate (default: 95%)
        
        Returns:
            Recommended total budget
        """
        if not historical_usage:
            return self.total_budget
        
        # Calculate total usage for each historical entry
        total_usages = [sum(usage.values()) for usage in historical_usage]
        
        # Sort and find percentile
        total_usages.sort()
        percentile_index = int(len(total_usages) * target_compliance_rate)
        recommended_budget = total_usages[percentile_index] if percentile_index < len(total_usages) else total_usages[-1]
        
        # Add safety margin (10%)
        recommended_budget = int(recommended_budget * 1.1)
        
        return recommended_budget
