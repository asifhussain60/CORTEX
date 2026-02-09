"""
Quantitative Metrics Calculator for DIGEST Mode.

Phase 41 Stage 2 (ENH-055):
Implements 5 quantitative metrics:
1. Efficiency Score: Task completion efficiency
2. Accuracy Score: Response correctness
3. Tool Success Rate: Tool invocation success
4. Learning Velocity: Enhancement extraction rate
5. Context Efficiency: Token utilization efficiency

Author: Asif Hussain
Date: 2026-02-07
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from cortex.learning.digest.metrics_schema import (
    EfficiencyMetrics,
    AccuracyMetrics,
    ToolSuccessMetrics,
    LearningVelocityMetrics,
    ContextEfficiencyMetrics,
    DigestMetrics,
)


class MetricsCalculator:
    """
    Calculate quantitative metrics for DIGEST sessions.
    
    Provides 5 core metrics:
    - Efficiency: (expected / actual) × 100, capped at 100%
    - Accuracy: ((total - corrections) / total) × 100
    - Tool Success: (successful / total) × 100
    - Learning Velocity: enhancements / sessions
    - Context Efficiency: (meaningful / total) × 100
    
    Usage:
        calculator = MetricsCalculator()
        metrics = calculator.calculate_all_metrics(chat_session_data)
    """
    
    # Complexity → expected turn ranges
    COMPLEXITY_RANGES = {
        "simple": (2, 3),
        "medium": (3, 5),
        "complex": (5, 8)
    }
    
    # Correction keywords
    CORRECTION_KEYWORDS = [
        "wrong", "incorrect", "error", "mistake", "fix", "correct",
        "actually", "no,", "that's not", "should be", "instead"
    ]
    
    # Token waste patterns
    WASTE_PATTERNS = {
        "narration": r"(?:I'll now|Let me|First,|Here's what|I understand|I see that)",
        "repetition": r"(.{20,})\1{2,}",  # Same phrase 3+ times
        "filler": r"(?:um|uh)|well|so|basically|essentially)",
    }
    
    def calculate_efficiency(
        self,
        actual_turns: int,
        expected_turns: Optional[int] = None,
        task_complexity: Optional[str] = None
    ) -> EfficiencyMetrics:
        """
        Calculate efficiency score.
        
        Args:
            actual_turns: Actual conversation turns taken
            expected_turns: Expected turns (if known)
            task_complexity: Task complexity level (simple, medium, complex)
        
        Returns:
            EfficiencyMetrics with score capped at 100%
        """
        # Estimate expected turns from complexity if not provided
        if expected_turns is None and task_complexity:
            min_turns, max_turns = self.COMPLEXITY_RANGES.get(
                task_complexity.lower(), (3, 5)
            )
            expected_turns = max_turns  # Use max of range
        
        if expected_turns is None:
            expected_turns = actual_turns  # Fallback: 100% efficiency
        
        # Calculate score, cap at 100%
        raw_score = (expected_turns / actual_turns) * 100 if actual_turns > 0 else 0
        score = min(raw_score, 100.0)
        
        exceeded_expectations = actual_turns < expected_turns
        
        return EfficiencyMetrics(
            score=score,
            actual_turns=actual_turns,
            expected_turns=expected_turns,
            exceeded_expectations=exceeded_expectations,
            task_complexity=task_complexity
        )
    
    def calculate_accuracy(
        self,
        total_turns: int,
        corrections: int
    ) -> AccuracyMetrics:
        """
        Calculate accuracy score.
        
        Args:
            total_turns: Total conversation turns
            corrections: Number of corrections/fixes required
        
        Returns:
            AccuracyMetrics with correctness percentage
        """
        if total_turns == 0:
            return AccuracyMetrics(
                score=0,
                total_turns=0,
                corrections=0,
                correct_responses=0
            )
        
        correct_responses = max(0, total_turns - corrections)
        score = (correct_responses / total_turns) * 100
        
        return AccuracyMetrics(
            score=score,
            total_turns=total_turns,
            corrections=corrections,
            correct_responses=correct_responses
        )
    
    def calculate_accuracy_from_content(
        self,
        chat_content: str
    ) -> AccuracyMetrics:
        """
        Calculate accuracy by detecting correction keywords in chat.
        
        Args:
            chat_content: Full chat session content
        
        Returns:
            AccuracyMetrics with auto-detected corrections
        """
        # Count conversation turns
        user_turns = len(re.findall(r"(?:^|\n)User:", chat_content))
        
        # Detect correction keywords (case-insensitive)
        corrections = 0
        detected_keywords = []
        
        for keyword in self.CORRECTION_KEYWORDS:
            matches = re.findall(
                rf"\b{re.escape(keyword)}\b",
                chat_content,
                re.IGNORECASE
            )
            if matches:
                corrections += len(matches)
                detected_keywords.append(keyword)
        
        # Limit corrections to max turns (can't correct more than total)
        corrections = min(corrections, user_turns)
        
        return AccuracyMetrics(
            score=(max(0, user_turns - corrections) / user_turns * 100) if user_turns > 0 else 100,
            total_turns=user_turns,
            corrections=corrections,
            correct_responses=max(0, user_turns - corrections),
            correction_keywords=detected_keywords
        )
    
    def calculate_tool_success(
        self,
        successful_invocations: int,
        total_invocations: int
    ) -> ToolSuccessMetrics:
        """
        Calculate tool success rate.
        
        Args:
            successful_invocations: Successful tool invocations
            total_invocations: Total tool invocations
        
        Returns:
            ToolSuccessMetrics with success percentage
        """
        if total_invocations == 0:
            return ToolSuccessMetrics(
                success_rate=0,
                total_invocations=0,
                successful_invocations=0,
                failed_invocations=0
            )
        
        success_rate = (successful_invocations / total_invocations) * 100
        failed_invocations = total_invocations - successful_invocations
        
        return ToolSuccessMetrics(
            success_rate=success_rate,
            total_invocations=total_invocations,
            successful_invocations=successful_invocations,
            failed_invocations=failed_invocations
        )
    
    def calculate_tool_success_from_content(
        self,
        chat_content: str
    ) -> ToolSuccessMetrics:
        """
        Calculate tool success by parsing tool results from chat.
        
        Args:
            chat_content: Full chat session content
        
        Returns:
            ToolSuccessMetrics with parsed success/failure counts
        """
        # Find all tool calls and their results
        tool_pattern = r"\[Tool call: ([^\]]+)\]\s*(?:Result|Output)): ([^\n]+)"
        matches = re.findall(tool_pattern, chat_content)
        
        total_invocations = len(matches)
        successful_invocations = 0
        tool_breakdown: Dict[str, Dict[str, int]] = {}
        
        # Success indicators in results
        success_indicators = ["success", "created", "retrieved", "complete", "passed"]
        failure_indicators = ["error", "failed", "exception", "not found"]
        
        for tool_name, result in matches:
            result_lower = result.lower()
            
            # Check for success/failure
            is_success = any(ind in result_lower for ind in success_indicators)
            is_failure = any(ind in result_lower for ind in failure_indicators)
            
            # Assume success if no explicit failure
            if not is_failure:
                is_success = True
            
            if is_success:
                successful_invocations += 1
            
            # Track per-tool breakdown
            if tool_name not in tool_breakdown:
                tool_breakdown[tool_name] = {"success": 0, "failure": 0}
            
            if is_success:
                tool_breakdown[tool_name]["success"] += 1
            else:
                tool_breakdown[tool_name]["failure"] += 1
        
        return ToolSuccessMetrics(
            success_rate=(successful_invocations / total_invocations * 100) if total_invocations > 0 else 0,
            total_invocations=total_invocations,
            successful_invocations=successful_invocations,
            failed_invocations=total_invocations - successful_invocations,
            tool_breakdown=tool_breakdown
        )
    
    def calculate_learning_velocity(
        self,
        enhancements_extracted: int,
        sessions_analyzed: int,
        previous_velocity: Optional[float] = None
    ) -> LearningVelocityMetrics:
        """
        Calculate learning velocity.
        
        Args:
            enhancements_extracted: Total enhancements extracted
            sessions_analyzed: Total sessions analyzed
            previous_velocity: Previous period velocity (for improvement rate)
        
        Returns:
            LearningVelocityMetrics with velocity and improvement
        """
        if sessions_analyzed == 0:
            velocity = 0.0
        else:
            velocity = enhancements_extracted / sessions_analyzed
        
        high_value_session = velocity > 1.0
        
        # Calculate improvement rate if previous velocity provided
        improvement_rate = None
        if previous_velocity is not None and previous_velocity > 0:
            improvement_rate = ((velocity - previous_velocity) / previous_velocity) * 100
        
        return LearningVelocityMetrics(
            velocity=velocity,
            enhancements_extracted=enhancements_extracted,
            sessions_analyzed=sessions_analyzed,
            high_value_session=high_value_session,
            improvement_rate=improvement_rate
        )
    
    def calculate_context_efficiency(
        self,
        meaningful_tokens: int,
        total_tokens: int
    ) -> ContextEfficiencyMetrics:
        """
        Calculate context efficiency.
        
        Args:
            meaningful_tokens: Tokens contributing to task
            total_tokens: Total tokens used
        
        Returns:
            ContextEfficiencyMetrics with efficiency percentage
        """
        if total_tokens == 0:
            return ContextEfficiencyMetrics(
                efficiency=0,
                meaningful_tokens=0,
                total_tokens=0,
                wasted_tokens=0
            )
        
        efficiency = (meaningful_tokens / total_tokens) * 100
        wasted_tokens = total_tokens - meaningful_tokens
        needs_improvement = efficiency < 70
        
        # Generate recommendations if efficiency low
        recommendations = []
        if needs_improvement:
            recommendations.append("Reduce narration and filler phrases")
            recommendations.append("Eliminate repetitive explanations")
            recommendations.append("Use more concise responses")
        
        return ContextEfficiencyMetrics(
            efficiency=efficiency,
            meaningful_tokens=meaningful_tokens,
            total_tokens=total_tokens,
            wasted_tokens=wasted_tokens,
            needs_improvement=needs_improvement,
            recommendations=recommendations
        )
    
    def calculate_context_efficiency_from_content(
        self,
        chat_content: str
    ) -> ContextEfficiencyMetrics:
        """
        Calculate context efficiency by detecting waste patterns.
        
        Args:
            chat_content: Full chat session content
        
        Returns:
            ContextEfficiencyMetrics with detected waste patterns
        """
        # Approximate token count (4 chars ≈ 1 token)
        total_tokens = len(chat_content) // 4
        
        # Detect waste patterns
        wasted_tokens = 0
        detected_patterns = []
        
        for pattern_name, pattern_regex in self.WASTE_PATTERNS.items():
            matches = re.findall(pattern_regex, chat_content, re.IGNORECASE)
            if matches:
                # Count wasted tokens from matches
                for match in matches:
                    match_str = match if isinstance(match, str) else match[0]
                    wasted_tokens += len(match_str) // 4
                detected_patterns.append(pattern_name)
        
        # Cap wasted tokens at total
        wasted_tokens = min(wasted_tokens, total_tokens)
        meaningful_tokens = total_tokens - wasted_tokens
        
        efficiency = (meaningful_tokens / total_tokens * 100) if total_tokens > 0 else 0
        needs_improvement = efficiency < 80
        
        recommendations = []
        if "narration" in detected_patterns:
            recommendations.append("Reduce verbose narration before actions")
        if "repetition" in detected_patterns:
            recommendations.append("Eliminate repetitive phrases")
        if "filler" in detected_patterns:
            recommendations.append("Remove filler words (um, uh, basically)")
        
        return ContextEfficiencyMetrics(
            efficiency=efficiency,
            meaningful_tokens=meaningful_tokens,
            total_tokens=total_tokens,
            wasted_tokens=wasted_tokens,
            waste_patterns=detected_patterns,
            recommendations=recommendations,
            needs_improvement=needs_improvement
        )
    
    def calculate_all_metrics(
        self,
        chat_session_data: Dict[str, Any]
    ) -> DigestMetrics:
        """
        Calculate all 5 metrics from chat session data.
        
        Args:
            chat_session_data: Dict with keys:
                - user_turns: int
                - copilot_turns: int
                - tool_invocations: int
                - successful_tools: int
                - corrections: int
                - task_complexity: str
                - total_tokens: int
                - meaningful_tokens: int
                - enhancements_extracted: int
        
        Returns:
            DigestMetrics with all 5 metrics and overall score
        """
        # Extract data
        user_turns = chat_session_data.get("user_turns", 0)
        task_complexity = chat_session_data.get("task_complexity", "medium")
        total_turns = user_turns + chat_session_data.get("copilot_turns", 0)
        corrections = chat_session_data.get("corrections", 0)
        tool_invocations = chat_session_data.get("tool_invocations", 0)
        successful_tools = chat_session_data.get("successful_tools", 0)
        total_tokens = chat_session_data.get("total_tokens", 0)
        meaningful_tokens = chat_session_data.get("meaningful_tokens", 0)
        enhancements = chat_session_data.get("enhancements_extracted", 0)
        
        # Calculate each metric
        efficiency = self.calculate_efficiency(
            actual_turns=user_turns,
            task_complexity=task_complexity
        )
        
        accuracy = self.calculate_accuracy(
            total_turns=total_turns,
            corrections=corrections
        )
        
        tool_success = self.calculate_tool_success(
            successful_invocations=successful_tools,
            total_invocations=tool_invocations
        )
        
        learning_velocity = self.calculate_learning_velocity(
            enhancements_extracted=enhancements,
            sessions_analyzed=1  # This session
        )
        
        context_efficiency = self.calculate_context_efficiency(
            meaningful_tokens=meaningful_tokens,
            total_tokens=total_tokens
        )
        
        # Calculate overall quality score (weighted average)
        weights = {
            "efficiency": 0.25,
            "accuracy": 0.30,
            "tool_success": 0.20,
            "learning_velocity": 0.15,  # Normalized to 0-100 scale
            "context_efficiency": 0.10
        }
        
        # Normalize learning_velocity to 0-100 scale (assume 2.0 = 100%)
        normalized_velocity = min(learning_velocity.velocity / 2.0 * 100, 100)
        
        overall_quality_score = (
            efficiency.score * weights["efficiency"] +
            accuracy.score * weights["accuracy"] +
            tool_success.success_rate * weights["tool_success"] +
            normalized_velocity * weights["learning_velocity"] +
            context_efficiency.efficiency * weights["context_efficiency"]
        )
        
        return DigestMetrics(
            efficiency=efficiency,
            accuracy=accuracy,
            tool_success=tool_success,
            learning_velocity=learning_velocity,
            context_efficiency=context_efficiency,
            overall_quality_score=overall_quality_score,
            weights=weights,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "session_data": chat_session_data
            }
        )
    
    def compare_to_baseline(
        self,
        current_metrics: DigestMetrics,
        baseline_metrics: DigestMetrics
    ) -> Dict[str, Any]:
        """
        Compare current metrics to baseline.
        
        Args:
            current_metrics: Current session metrics
            baseline_metrics: Historical baseline metrics
        
        Returns:
            Dict with improvement percentages and verdict
        """
        def calc_improvement(current: float, baseline: float) -> float:
            if baseline == 0:
                return 0.0
            return ((current - baseline) / baseline) * 100
        
        return {
            "efficiency_improvement": calc_improvement(
                current_metrics.efficiency.score,
                baseline_metrics.efficiency.score
            ),
            "accuracy_improvement": calc_improvement(
                current_metrics.accuracy.score,
                baseline_metrics.accuracy.score
            ),
            "tool_success_improvement": calc_improvement(
                current_metrics.tool_success.success_rate,
                baseline_metrics.tool_success.success_rate
            ),
            "learning_velocity_improvement": calc_improvement(
                current_metrics.learning_velocity.velocity,
                baseline_metrics.learning_velocity.velocity
            ),
            "context_efficiency_improvement": calc_improvement(
                current_metrics.context_efficiency.efficiency,
                baseline_metrics.context_efficiency.efficiency
            ),
            "overall_improvement": current_metrics.overall_quality_score > baseline_metrics.overall_quality_score,
            "overall_improvement_pct": calc_improvement(
                current_metrics.overall_quality_score,
                baseline_metrics.overall_quality_score
            )
        }
