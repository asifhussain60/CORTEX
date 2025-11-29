"""
TIMEFRAME Entry Point Module

Purpose: Time Investment Mapping & Effort Forecasting for Resource Allocation, Management & Execution
Author: Asif Hussain
Version: 1.0

Converts SWAGGER scope/complexity data into time estimates:
- Story point calculation (Fibonacci scale)
- Hours estimation (developer effort)
- Team capacity calculation (multi-developer)
- Sprint allocation (timeline generation)

Natural Language Triggers:
- "timeframe", "estimate", "time estimate", "how long", "duration"
- "story points", "sprint estimate", "team size", "velocity"
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TimeEstimate:
    """Time estimation result"""
    story_points: int
    hours_single: float
    hours_team: float
    days_single: float
    days_team: float
    sprints: float
    team_size: int
    confidence: str
    assumptions: List[str]
    breakdown: Dict[str, float]


class TimeframeEstimator:
    """
    TIMEFRAME Entry Point Module
    
    Converts SWAGGER complexity scores (0-100) into actionable time estimates.
    Uses industry-standard formulas with configurable multipliers.
    """
    
    # Story Point Mapping (Fibonacci scale)
    FIBONACCI_SCALE = [1, 2, 3, 5, 8, 13, 21, 34]
    
    # Default Configuration
    DEFAULT_HOURS_PER_POINT = 4.0      # Industry standard: 4-6 hours per story point
    DEFAULT_WORKING_HOURS_DAY = 6.0    # Effective working hours (8 hours - meetings/breaks)
    DEFAULT_SPRINT_DAYS = 10.0         # 2-week sprint (10 working days)
    DEFAULT_TEAM_SIZE = 1              # Single developer default
    
    # Complexity Score Breakpoints (0-100 scale from SWAGGER)
    COMPLEXITY_BREAKPOINTS = [
        (0, 10, 1),      # 0-10: Trivial (1 point)
        (11, 20, 2),     # 11-20: Simple (2 points)
        (21, 35, 3),     # 21-35: Small (3 points)
        (36, 50, 5),     # 36-50: Medium (5 points)
        (51, 65, 8),     # 51-65: Large (8 points)
        (66, 80, 13),    # 66-80: Very Large (13 points)
        (81, 90, 21),    # 81-90: Huge (21 points)
        (91, 100, 34),   # 91-100: Epic (34 points)
    ]
    
    def __init__(
        self,
        hours_per_point: float = DEFAULT_HOURS_PER_POINT,
        working_hours_day: float = DEFAULT_WORKING_HOURS_DAY,
        sprint_days: float = DEFAULT_SPRINT_DAYS
    ):
        """
        Initialize TIMEFRAME estimator
        
        Args:
            hours_per_point: Hours of work per story point (default: 4.0)
            working_hours_day: Effective working hours per day (default: 6.0)
            sprint_days: Working days per sprint (default: 10.0)
        """
        self.hours_per_point = hours_per_point
        self.working_hours_day = working_hours_day
        self.sprint_days = sprint_days
    
    def estimate_timeframe(
        self,
        complexity: float,
        scope: Optional[Dict] = None,
        team_size: int = DEFAULT_TEAM_SIZE,
        velocity: Optional[float] = None
    ) -> TimeEstimate:
        """
        Generate complete time estimate from SWAGGER complexity score
        
        Args:
            complexity: SWAGGER complexity score (0-100)
            scope: Optional SWAGGER scope dict (for detailed breakdown)
            team_size: Number of developers on team (default: 1)
            velocity: Optional team velocity (story points per sprint)
        
        Returns:
            TimeEstimate with story points, hours, days, sprints, breakdown
        """
        # Validate inputs
        complexity = max(0, min(100, complexity))
        team_size = max(1, team_size)
        
        # Step 1: Convert complexity to story points (Fibonacci)
        story_points = self._complexity_to_story_points(complexity)
        
        # Step 2: Calculate hours (single developer)
        hours_single = story_points * self.hours_per_point
        
        # Step 3: Calculate days (single developer)
        days_single = hours_single / self.working_hours_day
        
        # Step 4: Calculate team effort (parallel work with communication overhead)
        hours_team, days_team = self._calculate_team_effort(
            hours_single, team_size
        )
        
        # Step 5: Calculate sprint allocation
        sprints = self._calculate_sprints(
            story_points, team_size, velocity
        )
        
        # Step 6: Generate breakdown by entity type
        breakdown = self._generate_breakdown(scope, hours_single)
        
        # Step 7: Determine confidence level
        confidence = self._determine_confidence(complexity, scope)
        
        # Step 8: Generate assumptions
        assumptions = self._generate_assumptions(
            team_size, velocity, scope
        )
        
        return TimeEstimate(
            story_points=story_points,
            hours_single=round(hours_single, 1),
            hours_team=round(hours_team, 1),
            days_single=round(days_single, 1),
            days_team=round(days_team, 1),
            sprints=round(sprints, 1),
            team_size=team_size,
            confidence=confidence,
            assumptions=assumptions,
            breakdown=breakdown
        )
    
    def _complexity_to_story_points(self, complexity: float) -> int:
        """
        Convert SWAGGER complexity score (0-100) to Fibonacci story points
        
        Uses complexity breakpoints for mapping:
        - 0-10: 1 point (trivial)
        - 11-20: 2 points (simple)
        - 21-35: 3 points (small)
        - 36-50: 5 points (medium)
        - 51-65: 8 points (large)
        - 66-80: 13 points (very large)
        - 81-90: 21 points (huge)
        - 91-100: 34 points (epic)
        """
        for min_val, max_val, points in self.COMPLEXITY_BREAKPOINTS:
            if min_val <= complexity <= max_val:
                return points
        
        # Fallback for out-of-range values
        return self.FIBONACCI_SCALE[-1]
    
    def _calculate_team_effort(
        self,
        hours_single: float,
        team_size: int
    ) -> Tuple[float, float]:
        """
        Calculate team effort with communication overhead
        
        Brooks's Law: Adding people to a late project makes it later
        Communication overhead increases with team size
        
        Formula:
        - Ideal parallel: hours / team_size
        - Communication overhead: 1 + (team_size - 1) * 0.05
        - Actual: ideal * overhead
        
        Args:
            hours_single: Single developer hours
            team_size: Number of developers
        
        Returns:
            (team_hours, team_days) tuple
        """
        if team_size == 1:
            return hours_single, hours_single / self.working_hours_day
        
        # Ideal parallel work (assumes perfect parallelization)
        ideal_hours = hours_single / team_size
        
        # Communication overhead (5% per additional person)
        # 2 devs: 5% overhead, 3 devs: 10%, 4 devs: 15%, etc.
        overhead_multiplier = 1 + ((team_size - 1) * 0.05)
        
        # Actual team hours with overhead
        team_hours = ideal_hours * overhead_multiplier
        team_days = team_hours / self.working_hours_day
        
        return team_hours, team_days
    
    def _calculate_sprints(
        self,
        story_points: int,
        team_size: int,
        velocity: Optional[float]
    ) -> float:
        """
        Calculate sprint allocation
        
        Args:
            story_points: Total story points
            team_size: Number of developers
            velocity: Optional team velocity (points per sprint)
                     If not provided, assumes: team_size * 20 points per sprint
        
        Returns:
            Number of sprints (float)
        """
        if velocity is None:
            # Default velocity: 20 points per developer per sprint
            # (Assumes 2-week sprints, ~4 points per day per dev)
            velocity = team_size * 20
        
        sprints = story_points / velocity
        return max(0.5, sprints)  # Minimum 0.5 sprint
    
    def _generate_breakdown(
        self,
        scope: Optional[Dict],
        total_hours: float
    ) -> Dict[str, float]:
        """
        Generate effort breakdown by entity type
        
        Distribution based on typical development splits:
        - Tables: 20% (schema, migrations, CRUD)
        - Files: 40% (implementation, logic)
        - Services: 25% (integration, APIs)
        - Dependencies: 10% (setup, configuration)
        - Testing: 5% (if no explicit test files)
        
        Args:
            scope: SWAGGER scope dict (tables, files, services, dependencies)
            total_hours: Total estimated hours
        
        Returns:
            Dict mapping entity type to estimated hours
        """
        if not scope:
            # Default distribution when no scope provided
            return {
                'implementation': round(total_hours * 0.65, 1),
                'testing': round(total_hours * 0.25, 1),
                'deployment': round(total_hours * 0.10, 1)
            }
        
        breakdown = {}
        
        # Calculate proportions based on entity counts
        table_count = len(scope.get('tables', []))
        file_count = len(scope.get('files', []))
        service_count = len(scope.get('services', []))
        dependency_count = len(scope.get('dependencies', []))
        
        total_entities = table_count + file_count + service_count + dependency_count
        
        if total_entities == 0:
            return self._generate_breakdown(None, total_hours)
        
        # Weighted distribution
        if table_count > 0:
            breakdown['tables'] = round(total_hours * 0.20 * (table_count / total_entities), 1)
        
        if file_count > 0:
            breakdown['files'] = round(total_hours * 0.40 * (file_count / total_entities), 1)
        
        if service_count > 0:
            breakdown['services'] = round(total_hours * 0.25 * (service_count / total_entities), 1)
        
        if dependency_count > 0:
            breakdown['dependencies'] = round(total_hours * 0.10 * (dependency_count / total_entities), 1)
        
        # Add testing overhead (5%)
        breakdown['testing'] = round(total_hours * 0.05, 1)
        
        return breakdown
    
    def _determine_confidence(
        self,
        complexity: float,
        scope: Optional[Dict]
    ) -> str:
        """
        Determine estimate confidence level
        
        Factors:
        - SWAGGER confidence score (if available in scope)
        - Complexity level (high complexity = lower confidence)
        - Scope detail (detailed scope = higher confidence)
        
        Returns:
            "HIGH", "MEDIUM", or "LOW"
        """
        # Start with SWAGGER confidence if available
        if scope and 'confidence' in scope:
            swagger_confidence = scope['confidence']
            if swagger_confidence >= 0.80:
                base_confidence = "HIGH"
            elif swagger_confidence >= 0.60:
                base_confidence = "MEDIUM"
            else:
                base_confidence = "LOW"
        else:
            base_confidence = "MEDIUM"
        
        # Adjust based on complexity
        if complexity > 80:
            # Very high complexity reduces confidence
            if base_confidence == "HIGH":
                return "MEDIUM"
            else:
                return "LOW"
        
        return base_confidence
    
    def _generate_assumptions(
        self,
        team_size: int,
        velocity: Optional[float],
        scope: Optional[Dict]
    ) -> List[str]:
        """
        Generate list of estimation assumptions
        
        Args:
            team_size: Number of developers
            velocity: Team velocity (if provided)
            scope: SWAGGER scope (if provided)
        
        Returns:
            List of assumption strings
        """
        assumptions = [
            f"{self.hours_per_point} hours per story point (industry standard)",
            f"{self.working_hours_day} effective working hours per day",
            f"{self.sprint_days} working days per {int(self.sprint_days/5)}-week sprint"
        ]
        
        if team_size > 1:
            overhead_pct = (team_size - 1) * 5
            assumptions.append(
                f"{overhead_pct}% communication overhead for {team_size}-person team"
            )
        
        if velocity:
            assumptions.append(f"Team velocity: {velocity} story points per sprint")
        else:
            assumptions.append(f"Estimated velocity: {team_size * 20} points per sprint")
        
        if scope and 'confidence' in scope:
            assumptions.append(
                f"Based on SWAGGER scope confidence: {int(scope['confidence']*100)}%"
            )
        
        return assumptions
    
    def estimate_three_point(
        self,
        complexity: float,
        scope: Optional[Dict] = None,
        team_size: int = DEFAULT_TEAM_SIZE
    ) -> Dict[str, TimeEstimate]:
        """
        Generate PERT three-point estimate (Best/Likely/Worst)
        
        Formula:
        - Best case: complexity * 0.75
        - Most likely: complexity (as-is)
        - Worst case: complexity * 1.50
        
        Args:
            complexity: SWAGGER complexity score
            scope: Optional SWAGGER scope dict
            team_size: Number of developers
        
        Returns:
            Dict with 'best', 'likely', 'worst' TimeEstimate objects
        """
        best_complexity = complexity * 0.75
        worst_complexity = min(complexity * 1.50, 100)
        
        return {
            'best': self.estimate_timeframe(best_complexity, scope, team_size),
            'likely': self.estimate_timeframe(complexity, scope, team_size),
            'worst': self.estimate_timeframe(worst_complexity, scope, team_size)
        }
    
    def format_estimate_report(
        self,
        estimate: TimeEstimate,
        include_breakdown: bool = True
    ) -> str:
        """
        Format time estimate as human-readable report
        
        Args:
            estimate: TimeEstimate object
            include_breakdown: Include effort breakdown section
        
        Returns:
            Formatted markdown string
        """
        lines = []
        lines.append("## ⏱️ TIMEFRAME Estimate")
        lines.append("")
        lines.append(f"**Story Points:** {estimate.story_points} (Fibonacci scale)")
        lines.append(f"**Confidence:** {estimate.confidence}")
        lines.append("")
        
        lines.append("### 👤 Single Developer")
        lines.append(f"- **Hours:** {estimate.hours_single}h")
        lines.append(f"- **Days:** {estimate.days_single} days (~{int(estimate.days_single/5)} weeks)")
        lines.append("")
        
        if estimate.team_size > 1:
            lines.append(f"### 👥 Team ({estimate.team_size} developers)")
            lines.append(f"- **Hours per person:** {estimate.hours_team}h")
            lines.append(f"- **Calendar days:** {estimate.days_team} days")
            lines.append(f"- **Sprints:** {estimate.sprints} sprints")
            lines.append("")
        
        if include_breakdown and estimate.breakdown:
            lines.append("### 📊 Effort Breakdown")
            for category, hours in estimate.breakdown.items():
                pct = (hours / estimate.hours_single) * 100
                lines.append(f"- **{category.title()}:** {hours}h ({int(pct)}%)")
            lines.append("")
        
        lines.append("### 📋 Assumptions")
        for assumption in estimate.assumptions:
            lines.append(f"- {assumption}")
        
        return "\n".join(lines)


# Convenience function for quick estimates
def quick_estimate(
    complexity: float,
    team_size: int = 1
) -> str:
    """
    Quick one-line estimate for chat responses
    
    Args:
        complexity: SWAGGER complexity score (0-100)
        team_size: Number of developers
    
    Returns:
        One-line summary string
    """
    estimator = TimeframeEstimator()
    estimate = estimator.estimate_timeframe(complexity, team_size=team_size)
    
    if team_size == 1:
        return (
            f"{estimate.story_points} story points • "
            f"{estimate.hours_single}h • "
            f"{estimate.days_single} days • "
            f"{estimate.confidence} confidence"
        )
    else:
        return (
            f"{estimate.story_points} story points • "
            f"Team: {estimate.hours_team}h/person • "
            f"{estimate.days_team} calendar days • "
            f"{estimate.sprints} sprints • "
            f"{estimate.confidence} confidence"
        )
