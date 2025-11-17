"""
CORTEX 3.0 - Token Usage Collector
=================================

Collects real-time metrics on token consumption and optimization.
Monitors input/output tokens, cost efficiency, and optimization patterns.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #3 (Week 1)
Effort: 1 hour (token usage collector)
Target: Token optimization and cost monitoring
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import json
from pathlib import Path

from .base_collector import BaseCollector, CollectorMetric, CollectorPriority


class TokenUsageCollector(BaseCollector):
    """
    Collects metrics on token usage and cost optimization.
    
    Metrics collected:
    - Input/output token counts per operation
    - Token cost calculations (using GitHub Copilot pricing)
    - Optimization effectiveness (before/after comparisons)
    - Token usage patterns and trends
    - Cost savings from optimizations
    """
    
    def __init__(self, brain_path: Optional[str] = None):
        super().__init__(
            collector_id="token_usage",
            name="Token Usage Monitor",
            priority=CollectorPriority.HIGH,
            collection_interval_seconds=30.0,  # Frequent monitoring for cost control
            brain_path=brain_path
        )
        
        # Token tracking
        self.input_tokens = []
        self.output_tokens = []
        self.operation_costs = {}
        self.optimization_savings = {}
        self.daily_usage = {}
        
        # GitHub Copilot pricing (token-unit formula)
        self.token_unit_cost = 0.00001  # $0.00001 per token-unit
        self.input_multiplier = 1.0     # Input tokens multiplier
        self.output_multiplier = 1.5    # Output tokens multiplier (50% more expensive)
        
        # Optimization tracking
        self.total_savings = 0.0
        self.optimization_count = 0
    
    def _initialize(self) -> bool:
        """Initialize token usage collector"""
        try:
            # Load any existing optimization data
            self._load_optimization_history()
            
            self.logger.info("Token usage collector initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize token usage collector: {e}")
            return False
    
    def _load_optimization_history(self) -> None:
        """Load historical optimization data if available"""
        try:
            if not self.brain_path:
                return
            
            optimization_file = self.brain_path / "metrics-history" / "token-optimizations.json"
            if optimization_file.exists():
                with open(optimization_file, 'r') as f:
                    data = json.load(f)
                    self.total_savings = data.get('total_savings', 0.0)
                    self.optimization_count = data.get('optimization_count', 0)
                    self.optimization_savings = data.get('optimization_savings', {})
                    
        except Exception as e:
            self.logger.warning(f"Failed to load optimization history: {e}")
    
    def _collect_metrics(self) -> List[CollectorMetric]:
        """Collect token usage metrics"""
        metrics = []
        timestamp = datetime.now(timezone.utc)
        
        # Recent token usage
        metrics.extend(self._collect_usage_metrics(timestamp))
        
        # Cost calculations
        metrics.extend(self._collect_cost_metrics(timestamp))
        
        # Optimization effectiveness
        metrics.extend(self._collect_optimization_metrics(timestamp))
        
        # Daily usage trends
        metrics.extend(self._collect_trend_metrics(timestamp))
        
        return metrics
    
    def _collect_usage_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect basic token usage metrics"""
        metrics = []
        
        # Recent input token usage
        if self.input_tokens:
            recent_input = self.input_tokens[-100:]  # Last 100 operations
            metrics.append(CollectorMetric(
                name="recent_input_tokens",
                value={
                    "total": sum(recent_input),
                    "average": sum(recent_input) / len(recent_input),
                    "min": min(recent_input),
                    "max": max(recent_input),
                    "count": len(recent_input)
                },
                timestamp=timestamp,
                tags={"type": "usage", "token_type": "input"}
            ))
        
        # Recent output token usage
        if self.output_tokens:
            recent_output = self.output_tokens[-100:]  # Last 100 operations
            metrics.append(CollectorMetric(
                name="recent_output_tokens",
                value={
                    "total": sum(recent_output),
                    "average": sum(recent_output) / len(recent_output),
                    "min": min(recent_output),
                    "max": max(recent_output),
                    "count": len(recent_output)
                },
                timestamp=timestamp,
                tags={"type": "usage", "token_type": "output"}
            ))
        
        # Total session tokens
        total_input = sum(self.input_tokens)
        total_output = sum(self.output_tokens)
        metrics.append(CollectorMetric(
            name="session_total_tokens",
            value={
                "input": total_input,
                "output": total_output,
                "combined": total_input + total_output
            },
            timestamp=timestamp,
            tags={"type": "usage", "scope": "session"}
        ))
        
        return metrics
    
    def _collect_cost_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect cost-related metrics"""
        metrics = []
        
        # Calculate recent cost
        if self.input_tokens and self.output_tokens:
            recent_input = sum(self.input_tokens[-100:])
            recent_output = sum(self.output_tokens[-100:])
            
            # GitHub Copilot token-unit formula
            recent_cost = self._calculate_cost(recent_input, recent_output)
            
            metrics.append(CollectorMetric(
                name="recent_operation_cost",
                value=recent_cost,
                timestamp=timestamp,
                tags={"type": "cost", "currency": "USD", "scope": "recent"}
            ))
        
        # Session total cost
        total_input = sum(self.input_tokens)
        total_output = sum(self.output_tokens)
        session_cost = self._calculate_cost(total_input, total_output)
        
        metrics.append(CollectorMetric(
            name="session_total_cost",
            value=session_cost,
            timestamp=timestamp,
            tags={"type": "cost", "currency": "USD", "scope": "session"}
        ))
        
        # Cost efficiency (tokens per dollar)
        if session_cost > 0:
            tokens_per_dollar = (total_input + total_output) / session_cost
            metrics.append(CollectorMetric(
                name="cost_efficiency",
                value=tokens_per_dollar,
                timestamp=timestamp,
                tags={"type": "efficiency", "unit": "tokens_per_dollar"}
            ))
        
        return metrics
    
    def _collect_optimization_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect optimization effectiveness metrics"""
        metrics = []
        
        # Total savings from optimizations
        metrics.append(CollectorMetric(
            name="total_optimization_savings",
            value=self.total_savings,
            timestamp=timestamp,
            tags={"type": "optimization", "currency": "USD"}
        ))
        
        # Number of optimizations applied
        metrics.append(CollectorMetric(
            name="optimization_count",
            value=self.optimization_count,
            timestamp=timestamp,
            tags={"type": "optimization", "unit": "count"}
        ))
        
        # Average savings per optimization
        if self.optimization_count > 0:
            avg_savings = self.total_savings / self.optimization_count
            metrics.append(CollectorMetric(
                name="average_optimization_savings",
                value=avg_savings,
                timestamp=timestamp,
                tags={"type": "optimization", "currency": "USD", "unit": "per_optimization"}
            ))
        
        # Optimization efficiency (savings as % of potential cost)
        if self.optimization_savings:
            efficiency_scores = []
            for opt_name, savings_data in self.optimization_savings.items():
                if 'before_cost' in savings_data and savings_data['before_cost'] > 0:
                    efficiency = (savings_data['savings'] / savings_data['before_cost']) * 100
                    efficiency_scores.append(efficiency)
            
            if efficiency_scores:
                metrics.append(CollectorMetric(
                    name="optimization_efficiency_percent",
                    value={
                        "average": sum(efficiency_scores) / len(efficiency_scores),
                        "max": max(efficiency_scores),
                        "min": min(efficiency_scores)
                    },
                    timestamp=timestamp,
                    tags={"type": "optimization", "unit": "percent"}
                ))
        
        return metrics
    
    def _collect_trend_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect usage trend metrics"""
        metrics = []
        
        # Daily usage summary
        today = timestamp.strftime("%Y-%m-%d")
        if today not in self.daily_usage:
            self.daily_usage[today] = {"input": 0, "output": 0, "cost": 0.0}
        
        # Update today's usage
        if self.input_tokens:
            self.daily_usage[today]["input"] += self.input_tokens[-1] if self.input_tokens else 0
        if self.output_tokens:
            self.daily_usage[today]["output"] += self.output_tokens[-1] if self.output_tokens else 0
            
        # Recalculate today's cost
        daily_input = self.daily_usage[today]["input"]
        daily_output = self.daily_usage[today]["output"]
        self.daily_usage[today]["cost"] = self._calculate_cost(daily_input, daily_output)
        
        metrics.append(CollectorMetric(
            name="daily_usage_summary",
            value=self.daily_usage[today],
            timestamp=timestamp,
            tags={"type": "trend", "scope": "daily", "date": today}
        ))
        
        return metrics
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost using GitHub Copilot pricing formula"""
        input_cost = input_tokens * self.input_multiplier * self.token_unit_cost
        output_cost = output_tokens * self.output_multiplier * self.token_unit_cost
        return input_cost + output_cost
    
    # Public methods for tracking token usage (called by CORTEX operations)
    
    def track_operation(self, operation_name: str, input_tokens: int, output_tokens: int) -> None:
        """Track token usage for a specific operation"""
        self.input_tokens.append(input_tokens)
        self.output_tokens.append(output_tokens)
        
        # Calculate operation cost
        operation_cost = self._calculate_cost(input_tokens, output_tokens)
        
        if operation_name not in self.operation_costs:
            self.operation_costs[operation_name] = []
        self.operation_costs[operation_name].append(operation_cost)
        
        # Keep only recent operation costs (last 100)
        if len(self.operation_costs[operation_name]) > 100:
            self.operation_costs[operation_name] = self.operation_costs[operation_name][-100:]
        
        # Keep only recent token lists (last 1000)
        if len(self.input_tokens) > 1000:
            self.input_tokens = self.input_tokens[-1000:]
        if len(self.output_tokens) > 1000:
            self.output_tokens = self.output_tokens[-1000:]
    
    def track_optimization(self, optimization_name: str, before_tokens: Tuple[int, int], 
                          after_tokens: Tuple[int, int]) -> float:
        """
        Track the impact of an optimization.
        
        Args:
            optimization_name: Name of the optimization applied
            before_tokens: (input_tokens, output_tokens) before optimization
            after_tokens: (input_tokens, output_tokens) after optimization
            
        Returns:
            float: Cost savings from the optimization
        """
        before_cost = self._calculate_cost(before_tokens[0], before_tokens[1])
        after_cost = self._calculate_cost(after_tokens[0], after_tokens[1])
        savings = before_cost - after_cost
        
        # Track the optimization
        self.optimization_savings[optimization_name] = {
            "before_cost": before_cost,
            "after_cost": after_cost,
            "savings": savings,
            "token_reduction": {
                "input": before_tokens[0] - after_tokens[0],
                "output": before_tokens[1] - after_tokens[1]
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.total_savings += savings
        self.optimization_count += 1
        
        # Persist optimization data
        self._save_optimization_history()
        
        return savings
    
    def _save_optimization_history(self) -> None:
        """Save optimization history to brain"""
        try:
            if not self.brain_path:
                return
            
            metrics_dir = self.brain_path / "metrics-history"
            metrics_dir.mkdir(exist_ok=True)
            
            optimization_file = metrics_dir / "token-optimizations.json"
            data = {
                "total_savings": self.total_savings,
                "optimization_count": self.optimization_count,
                "optimization_savings": self.optimization_savings,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            with open(optimization_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to save optimization history: {e}")
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of token usage and costs"""
        total_input = sum(self.input_tokens)
        total_output = sum(self.output_tokens)
        total_cost = self._calculate_cost(total_input, total_output)
        
        return {
            "session_tokens": {
                "input": total_input,
                "output": total_output,
                "total": total_input + total_output
            },
            "session_cost": total_cost,
            "optimization_savings": self.total_savings,
            "net_cost": total_cost - self.total_savings,
            "cost_reduction_percent": (self.total_savings / max(total_cost, 0.01)) * 100,
            "operations_tracked": len(self.input_tokens),
            "optimizations_applied": self.optimization_count
        }