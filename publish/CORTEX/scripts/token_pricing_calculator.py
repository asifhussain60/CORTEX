"""
GitHub Copilot Token Pricing Calculator

Implements accurate token-unit formula from GitHub Copilot pricing:
Token Units = (input_tokens × input_multiplier) + (output_tokens × output_multiplier)
Cost = Token Units × $0.00001

Author: Asif Hussain
Created: 2025-11-13
Purpose: Calculate real cost savings for CORTEX token optimization
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
import json


@dataclass
class TokenMetrics:
    """Token usage metrics for a single interaction"""
    input_tokens: int
    output_tokens: int
    input_multiplier: float = 1.0  # GitHub's input token multiplier
    output_multiplier: float = 1.5  # GitHub's output token multiplier (typically higher)
    
    @property
    def token_units(self) -> float:
        """Calculate billable token units using GitHub's formula"""
        return (self.input_tokens * self.input_multiplier) + (self.output_tokens * self.output_multiplier)
    
    @property
    def cost_usd(self) -> float:
        """Calculate cost in USD"""
        return self.token_units * 0.00001
    
    def __repr__(self) -> str:
        return (f"TokenMetrics(input={self.input_tokens:,}, output={self.output_tokens:,}, "
                f"units={self.token_units:,.0f}, cost=${self.cost_usd:.4f})")


@dataclass
class ConversationMetrics:
    """Metrics for multi-turn conversation"""
    turns: List[TokenMetrics]
    
    @property
    def total_input_tokens(self) -> int:
        return sum(turn.input_tokens for turn in self.turns)
    
    @property
    def total_output_tokens(self) -> int:
        return sum(turn.output_tokens for turn in self.turns)
    
    @property
    def total_token_units(self) -> float:
        return sum(turn.token_units for turn in self.turns)
    
    @property
    def total_cost_usd(self) -> float:
        return sum(turn.cost_usd for turn in self.turns)
    
    def __repr__(self) -> str:
        return (f"ConversationMetrics(turns={len(self.turns)}, "
                f"input={self.total_input_tokens:,}, output={self.total_output_tokens:,}, "
                f"units={self.total_token_units:,.0f}, cost=${self.total_cost_usd:.4f})")


class TokenPricingCalculator:
    """Calculate accurate GitHub Copilot costs"""
    
    def __init__(self, input_multiplier: float = 1.0, output_multiplier: float = 1.5):
        """
        Initialize calculator with GitHub's multipliers.
        
        Args:
            input_multiplier: Multiplier for input tokens (default 1.0)
            output_multiplier: Multiplier for output tokens (default 1.5)
            
        Note: These multipliers are based on typical GitHub Copilot pricing.
        Verify current values from GitHub documentation.
        """
        self.input_multiplier = input_multiplier
        self.output_multiplier = output_multiplier
    
    def calculate_single_request(self, input_tokens: int, output_tokens: int) -> TokenMetrics:
        """Calculate metrics for a single request"""
        return TokenMetrics(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_multiplier=self.input_multiplier,
            output_multiplier=self.output_multiplier
        )
    
    def calculate_conversation(self, turns: List[Tuple[int, int]]) -> ConversationMetrics:
        """
        Calculate metrics for multi-turn conversation.
        
        Args:
            turns: List of (input_tokens, output_tokens) tuples for each turn
            
        Note: In real conversations, input tokens accumulate (previous messages resent)
        """
        metrics = [
            self.calculate_single_request(input_tokens, output_tokens)
            for input_tokens, output_tokens in turns
        ]
        return ConversationMetrics(turns=metrics)
    
    def calculate_conversation_with_context(
        self, 
        initial_input: int, 
        output_per_turn: int, 
        num_turns: int
    ) -> ConversationMetrics:
        """
        Calculate conversation metrics accounting for context accumulation.
        
        Args:
            initial_input: Input tokens in first turn
            output_per_turn: Average output tokens per turn
            num_turns: Number of conversation turns
            
        Note: Each turn includes previous messages in context
        """
        turns = []
        cumulative_context = initial_input
        
        for turn_num in range(num_turns):
            # Each turn includes all previous context + output becomes part of next input
            input_tokens = cumulative_context
            output_tokens = output_per_turn
            
            turns.append((input_tokens, output_tokens))
            
            # Add this turn's output to next turn's input context
            cumulative_context += output_tokens
        
        return self.calculate_conversation(turns)
    
    def compare_architectures(
        self,
        old_input: int,
        new_input: int,
        output_tokens: int,
        num_requests: int = 1000
    ) -> Dict:
        """
        Compare costs between old and new architectures.
        
        Args:
            old_input: Input tokens for old architecture
            new_input: Input tokens for new architecture
            output_tokens: Output tokens (same for both)
            num_requests: Number of requests to project (default 1000/month)
            
        Returns:
            Dictionary with comparison metrics
        """
        old_metrics = self.calculate_single_request(old_input, output_tokens)
        new_metrics = self.calculate_single_request(new_input, output_tokens)
        
        # Calculate reduction percentages
        input_reduction = ((old_input - new_input) / old_input) * 100
        units_reduction = ((old_metrics.token_units - new_metrics.token_units) / old_metrics.token_units) * 100
        cost_reduction = ((old_metrics.cost_usd - new_metrics.cost_usd) / old_metrics.cost_usd) * 100
        
        # Project monthly and annual costs
        old_monthly = old_metrics.cost_usd * num_requests
        new_monthly = new_metrics.cost_usd * num_requests
        monthly_savings = old_monthly - new_monthly
        annual_savings = monthly_savings * 12
        
        return {
            "old_architecture": {
                "input_tokens": old_input,
                "output_tokens": output_tokens,
                "token_units": old_metrics.token_units,
                "cost_per_request": old_metrics.cost_usd,
                "monthly_cost": old_monthly,
                "annual_cost": old_monthly * 12
            },
            "new_architecture": {
                "input_tokens": new_input,
                "output_tokens": output_tokens,
                "token_units": new_metrics.token_units,
                "cost_per_request": new_metrics.cost_usd,
                "monthly_cost": new_monthly,
                "annual_cost": new_monthly * 12
            },
            "reductions": {
                "input_tokens_percent": input_reduction,
                "token_units_percent": units_reduction,
                "cost_percent": cost_reduction
            },
            "savings": {
                "per_request": old_metrics.cost_usd - new_metrics.cost_usd,
                "monthly": monthly_savings,
                "annual": annual_savings
            },
            "assumptions": {
                "requests_per_month": num_requests,
                "input_multiplier": self.input_multiplier,
                "output_multiplier": self.output_multiplier,
                "price_per_token_unit": 0.00001
            }
        }


def analyze_cortex_optimization():
    """Analyze CORTEX token optimization with real pricing"""
    
    print("=" * 80)
    print("CORTEX Token Optimization - Real Pricing Analysis")
    print("=" * 80)
    print()
    
    calculator = TokenPricingCalculator(input_multiplier=1.0, output_multiplier=1.5)
    
    # Current claimed metrics
    OLD_INPUT = 74047
    NEW_INPUT = 2078
    
    # Estimate output tokens (conservative - assume 2000 token response)
    OUTPUT_TOKENS = 2000
    
    print("SCENARIO 1: Single Request (Conservative Output Estimate)")
    print("-" * 80)
    comparison = calculator.compare_architectures(
        old_input=OLD_INPUT,
        new_input=NEW_INPUT,
        output_tokens=OUTPUT_TOKENS,
        num_requests=1000
    )
    
    print(f"\nOld Architecture:")
    print(f"  Input tokens:     {comparison['old_architecture']['input_tokens']:>10,}")
    print(f"  Output tokens:    {comparison['old_architecture']['output_tokens']:>10,}")
    print(f"  Token units:      {comparison['old_architecture']['token_units']:>10,.0f}")
    print(f"  Cost per request: ${comparison['old_architecture']['cost_per_request']:>9.4f}")
    
    print(f"\nNew Architecture:")
    print(f"  Input tokens:     {comparison['new_architecture']['input_tokens']:>10,}")
    print(f"  Output tokens:    {comparison['new_architecture']['output_tokens']:>10,}")
    print(f"  Token units:      {comparison['new_architecture']['token_units']:>10,.0f}")
    print(f"  Cost per request: ${comparison['new_architecture']['cost_per_request']:>9.4f}")
    
    print(f"\nReductions:")
    print(f"  Input tokens:     {comparison['reductions']['input_tokens_percent']:>9.2f}%")
    print(f"  Token units:      {comparison['reductions']['token_units_percent']:>9.2f}%")
    print(f"  Cost:             {comparison['reductions']['cost_percent']:>9.2f}%")
    
    print(f"\nProjected Savings (1,000 requests/month):")
    print(f"  Per request:      ${comparison['savings']['per_request']:>9.4f}")
    print(f"  Monthly:          ${comparison['savings']['monthly']:>9.2f}")
    print(f"  Annual:           ${comparison['savings']['annual']:>9,.2f}")
    
    print("\n" + "=" * 80)
    print("SCENARIO 2: Multi-Turn Conversation (5 turns)")
    print("-" * 80)
    
    # 5-turn conversation with context accumulation
    old_conv = calculator.calculate_conversation_with_context(
        initial_input=OLD_INPUT,
        output_per_turn=2000,
        num_turns=5
    )
    
    new_conv = calculator.calculate_conversation_with_context(
        initial_input=NEW_INPUT,
        output_per_turn=2000,
        num_turns=5
    )
    
    print(f"\nOld Architecture (5 turns):")
    print(f"  Total input:      {old_conv.total_input_tokens:>10,} tokens")
    print(f"  Total output:     {old_conv.total_output_tokens:>10,} tokens")
    print(f"  Total units:      {old_conv.total_token_units:>10,.0f}")
    print(f"  Total cost:       ${old_conv.total_cost_usd:>9.4f}")
    
    print(f"\nNew Architecture (5 turns):")
    print(f"  Total input:      {new_conv.total_input_tokens:>10,} tokens")
    print(f"  Total output:     {new_conv.total_output_tokens:>10,} tokens")
    print(f"  Total units:      {new_conv.total_token_units:>10,.0f}")
    print(f"  Total cost:       ${new_conv.total_cost_usd:>9.4f}")
    
    conv_savings = old_conv.total_cost_usd - new_conv.total_cost_usd
    conv_reduction = ((old_conv.total_cost_usd - new_conv.total_cost_usd) / old_conv.total_cost_usd) * 100
    
    print(f"\nConversation Savings:")
    print(f"  Per conversation: ${conv_savings:>9.4f}")
    print(f"  Cost reduction:   {conv_reduction:>9.2f}%")
    
    print("\n" + "=" * 80)
    print("SCENARIO 3: Different Output Sizes")
    print("-" * 80)
    
    for output_size in [500, 1000, 2000, 4000]:
        comp = calculator.compare_architectures(
            old_input=OLD_INPUT,
            new_input=NEW_INPUT,
            output_tokens=output_size,
            num_requests=1000
        )
        print(f"\nOutput: {output_size:>5,} tokens | "
              f"Old: ${comp['old_architecture']['cost_per_request']:.4f} | "
              f"New: ${comp['new_architecture']['cost_per_request']:.4f} | "
              f"Reduction: {comp['reductions']['cost_percent']:>6.2f}% | "
              f"Annual Savings: ${comp['savings']['annual']:>10,.2f}")
    
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    print()
    print("1. INPUT TOKEN REDUCTION: 97.2% is ACCURATE")
    print(f"   ({OLD_INPUT:,} → {NEW_INPUT:,} tokens)")
    print()
    print("2. COST REDUCTION: Varies by output size (not 97.2%)")
    print(f"   - Small responses (500 tokens):  ~96% reduction")
    print(f"   - Medium responses (2000 tokens): ~{comparison['reductions']['cost_percent']:.1f}% reduction")
    print(f"   - Large responses (4000 tokens):  ~90% reduction")
    print()
    print("3. TOKEN UNITS ≠ TOKENS")
    print(f"   Output tokens weighted {calculator.output_multiplier}x higher than input")
    print(f"   This reduces overall cost savings percentage")
    print()
    print("4. ANNUAL SAVINGS: Highly dependent on usage")
    print(f"   At 1,000 requests/month, 2,000 token responses:")
    print(f"   Annual savings: ${comparison['savings']['annual']:,.2f}")
    print()
    print("5. CONVERSATION ACCUMULATION: Amplifies savings")
    print(f"   Each turn adds context, making input reduction more valuable")
    print()
    print("=" * 80)
    print("RECOMMENDATION: Update metrics to reflect ACTUAL pricing model")
    print("=" * 80)
    
    # Generate corrected metrics
    return {
        "accurate_metric": {
            "description": "Input token reduction (what we actually optimized)",
            "value": "97.2%",
            "claim": f"{OLD_INPUT:,} → {NEW_INPUT:,} input tokens"
        },
        "cost_reduction": {
            "description": "Actual cost reduction (depends on output size)",
            "range": "90-96%",
            "typical": f"{comparison['reductions']['cost_percent']:.1f}% (for 2,000 token responses)"
        },
        "annual_savings": {
            "description": "Projected annual savings",
            "assumptions": "1,000 requests/month, 2,000 token responses",
            "value": f"${comparison['savings']['annual']:,.2f}"
        }
    }


if __name__ == "__main__":
    results = analyze_cortex_optimization()
    
    # Save results for documentation updates
    with open("d:\\PROJECTS\\CORTEX\\scripts\\token_pricing_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to: scripts/token_pricing_analysis.json")
