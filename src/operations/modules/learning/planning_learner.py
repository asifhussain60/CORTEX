"""
Planning Learner - Continuous improvement for routing accuracy.

Tracks routing decisions, collects feedback, and adapts complexity
scoring to improve Planning System tier classification.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class RoutingDecision:
    """Record of a routing decision for learning."""
    request: str
    predicted_tier: int
    actual_tier: Optional[int]
    complexity_score: float
    timestamp: str
    feedback: Optional[str] = None
    was_correct: Optional[bool] = None


class PlanningLearner:
    """Learns from routing decisions to improve accuracy."""
    
    def __init__(self, brain_path: Path):
        """
        Initialize planning learner.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        self.brain_path = brain_path
        self.learning_db = brain_path / "tier2" / "routing_decisions.jsonl"
        self.metrics_file = brain_path / "metrics" / "routing_accuracy.json"
        self.calibration_file = brain_path / "tier2" / "calibration_factors.json"
        
        # Learning parameters
        self.calibration_factors = self._load_calibration()
        
        # Ensure directories exist
        self.learning_db.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _load_calibration(self) -> Dict[str, float]:
        """Load calibration factors from disk or use defaults."""
        if self.calibration_file.exists():
            try:
                with open(self.calibration_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load calibration: {e}, using defaults")
        
        # Default weights
        return {
            'scope_weight': 0.3,
            'dependencies_weight': 0.25,
            'risk_weight': 0.25,
            'uncertainty_weight': 0.2
        }
    
    def _save_calibration(self):
        """Persist calibration factors to disk."""
        try:
            self.calibration_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.calibration_file, 'w', encoding='utf-8') as f:
                json.dump(self.calibration_factors, f, indent=2)
            logger.info("Calibration factors saved")
        except Exception as e:
            logger.error(f"Failed to save calibration: {e}")
        
    def record_decision(self, request: str, tier: int, complexity: float):
        """
        Record a routing decision for future learning.
        
        Args:
            request: User request text
            tier: Predicted tier (1-4)
            complexity: Overall complexity score
        """
        decision = RoutingDecision(
            request=request[:500],  # Limit request length
            predicted_tier=tier,
            actual_tier=None,  # Will be set via feedback
            complexity_score=complexity,
            timestamp=datetime.now().isoformat()
        )
        
        self._append_to_db(decision)
        logger.debug(f"Recorded decision: Tier {tier}, Complexity {complexity:.2f}")
        
    def provide_feedback(self, request: str, correct_tier: int, reason: str = None):
        """
        User provides feedback on routing accuracy.
        
        Args:
            request: Original request text
            correct_tier: Actual correct tier (1-4)
            reason: Optional explanation for correction
        """
        decisions = self._load_recent_decisions(limit=100)
        
        for decision in decisions:
            if decision.request.startswith(request[:100]) and decision.actual_tier is None:
                decision.actual_tier = correct_tier
                decision.was_correct = (decision.predicted_tier == correct_tier)
                decision.feedback = reason
                self._update_decision(decision)
                self._recalibrate_weights(decision)
                
                logger.info(f"Feedback recorded: {decision.predicted_tier}→{correct_tier}, "
                           f"Correct: {decision.was_correct}")
                break
                
    def get_accuracy_metrics(self) -> Dict[str, Any]:
        """
        Calculate current routing accuracy metrics.
        
        Returns:
            Dictionary with accuracy metrics and breakdown
        """
        decisions = self._load_all_decisions()
        
        if not decisions:
            return {
                'accuracy': 0.0,
                'total_decisions': 0,
                'decisions_with_feedback': 0,
                'correct_predictions': 0
            }
            
        with_feedback = [d for d in decisions if d.actual_tier is not None]
        correct = [d for d in with_feedback if d.was_correct]
        
        return {
            'accuracy': len(correct) / len(with_feedback) if with_feedback else 0.0,
            'total_decisions': len(decisions),
            'decisions_with_feedback': len(with_feedback),
            'correct_predictions': len(correct),
            'tier_breakdown': self._calculate_tier_accuracy(with_feedback)
        }
        
    def _recalibrate_weights(self, decision: RoutingDecision):
        """
        Adjust complexity weights based on feedback.
        
        Args:
            decision: Decision with feedback to learn from
        """
        if decision.was_correct:
            return  # No adjustment needed
        
        # Learning rate decreases over time
        feedback_count = len([d for d in self._load_all_decisions() 
                             if d.actual_tier is not None])
        learning_rate = 0.05 / (1 + feedback_count / 100)  # Decay
        
        # If predicted tier was too high, reduce weights
        # If predicted tier was too low, increase weights
        adjustment = learning_rate if decision.predicted_tier < decision.actual_tier else -learning_rate
        
        # Apply adjustment to all weights proportionally
        for key in self.calibration_factors:
            self.calibration_factors[key] = max(0.1, min(0.4, 
                self.calibration_factors[key] + adjustment
            ))
            
        # Normalize weights to sum to 1.0
        total = sum(self.calibration_factors.values())
        self.calibration_factors = {
            k: v / total for k, v in self.calibration_factors.items()
        }
        
        self._save_calibration()
        logger.info(f"Weights recalibrated: {self.calibration_factors}")
    
    def _calculate_tier_accuracy(self, decisions: List[RoutingDecision]) -> Dict[str, float]:
        """Calculate accuracy breakdown by tier."""
        tier_stats = {i: {'correct': 0, 'total': 0} for i in range(1, 5)}
        
        for d in decisions:
            if d.actual_tier:
                tier_stats[d.actual_tier]['total'] += 1
                if d.was_correct:
                    tier_stats[d.actual_tier]['correct'] += 1
        
        return {
            f'tier_{i}': (stats['correct'] / stats['total'] if stats['total'] > 0 else 0.0)
            for i, stats in tier_stats.items()
        }
    
    def _append_to_db(self, decision: RoutingDecision):
        """Append decision to JSONL database."""
        try:
            with open(self.learning_db, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(decision)) + '\n')
        except Exception as e:
            logger.error(f"Failed to append decision: {e}")
    
    def _update_decision(self, decision: RoutingDecision):
        """Update an existing decision in the database."""
        try:
            decisions = self._load_all_decisions()
            
            # Find and update matching decision
            for i, d in enumerate(decisions):
                if (d.request == decision.request and 
                    d.timestamp == decision.timestamp):
                    decisions[i] = decision
                    break
            
            # Rewrite entire file
            with open(self.learning_db, 'w', encoding='utf-8') as f:
                for d in decisions:
                    f.write(json.dumps(asdict(d)) + '\n')
                    
        except Exception as e:
            logger.error(f"Failed to update decision: {e}")
    
    def _load_recent_decisions(self, limit: int = 100) -> List[RoutingDecision]:
        """Load most recent N decisions."""
        all_decisions = self._load_all_decisions()
        return all_decisions[-limit:] if all_decisions else []
    
    def _load_all_decisions(self) -> List[RoutingDecision]:
        """Load all decisions from database."""
        if not self.learning_db.exists():
            return []
        
        decisions = []
        try:
            with open(self.learning_db, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        decisions.append(RoutingDecision(**data))
        except Exception as e:
            logger.error(f"Failed to load decisions: {e}")
        
        return decisions
    
    def get_calibration_summary(self) -> str:
        """
        Get human-readable calibration summary.
        
        Returns:
            Formatted string with current weights
        """
        lines = ["Current Calibration Factors:"]
        for key, value in self.calibration_factors.items():
            lines.append(f"  {key}: {value:.3f}")
        
        metrics = self.get_accuracy_metrics()
        lines.append(f"\nRouting Accuracy: {metrics['accuracy']:.1%}")
        lines.append(f"Total Decisions: {metrics['total_decisions']}")
        lines.append(f"With Feedback: {metrics['decisions_with_feedback']}")
        
        return '\n'.join(lines)
