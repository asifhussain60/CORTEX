"""Multi-Model Estimation Engine - Phase 12 CAP-2 Implementation.

Implements three estimation models for consensus:
1. PERT (Program Evaluation and Review Technique)
2. Story Points with skill-level conversion
3. Critical Path Method (CPM)

Enhanced with transparent estimation basis (legend) from team_assumptions.yaml.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from cortex.capacity.team_assumptions import get_team_assumptions, TeamAssumptions


logger = logging.getLogger(__name__)


class SkillLevel(Enum):
    """Team member skill levels."""
    JUNIOR = 1      # 6-8 hours per story point
    MIDLEVEL = 2    # 4-5 hours per story point
    SENIOR = 3      # 2-3 hours per story point
    ARCHITECT = 4   # 1-2 hours per story point


@dataclass
class EstimationResult:
    """Result of multi-model estimation.
    
    Attributes:
        task_id: Task identifier
        pert_hours: PERT model estimate (hours)
        story_points: Story point estimate
        cpm_hours: Critical path method estimate
        confidence_interval_low: 80% CI low bound
        confidence_interval_high: 80% CI high bound
        recommended_hours: Consensus recommendation
        risk_factors: Identified risk factors
        skill_level_used: Skill level used for estimation
        estimated_cost: Total estimated cost (with overhead)
        legend: Estimation basis explanation
    """
    task_id: str
    pert_hours: float = 0.0
    story_points: int = 0
    cpm_hours: float = 0.0
    confidence_interval_low: float = 0.0
    confidence_interval_high: float = 0.0
    recommended_hours: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    model_agreement: float = 0.0  # % of models in agreement
    skill_level_used: str = "mid_level"
    estimated_cost: float = 0.0
    legend: str = ""


class PERTEstimator:
    """PERT (Program Evaluation and Review Technique) estimator.
    
    Formula: Expected = (Optimistic + 4*MostLikely + Pessimistic) / 6
    Standard Deviation = (Pessimistic - Optimistic) / 6
    """
    
    @staticmethod
    def estimate(optimistic: float, likely: float, pessimistic: float) -> Tuple[float, float]:
        """Estimate using PERT formula.
        
        Phase 12 AC-CAP-2-01: PERT estimator calculates expected hours correctly
        
        Args:
            optimistic: Best-case hours
            likely: Most likely hours
            pessimistic: Worst-case hours
            
        Returns:
            (expected_hours, standard_deviation)
        """
        if optimistic > likely or likely > pessimistic:
            raise ValueError("Must have: optimistic <= likely <= pessimistic")
        
        expected = (optimistic + 4 * likely + pessimistic) / 6
        std_dev = (pessimistic - optimistic) / 6
        
        return (expected, std_dev)
    
    @staticmethod
    def get_confidence_interval(expected: float, std_dev: float, confidence: float = 0.80) -> Tuple[float, float]:
        """Get confidence interval for estimate.
        
        Args:
            expected: Expected value
            std_dev: Standard deviation
            confidence: Confidence level (0.80 for 80%)
            
        Returns:
            (low_bound, high_bound)
        """
        # For 80% confidence, z-score ≈ 1.28
        z_score = 1.28 if confidence == 0.80 else 1.96
        margin = z_score * std_dev
        
        return (expected - margin, expected + margin)


class StoryPointEstimator:
    """Story point estimator with skill-level conversion.
    
    Converts story points to hours based on team skill levels:
    - Junior (1): 6-8 hours/pt
    - MidLevel (2): 4-5 hours/pt
    - Senior (3): 2-3 hours/pt
    - Architect (4): 1-2 hours/pt
    """
    
    # Story point to hours conversion matrix
    CONVERSION_MATRIX = {
        SkillLevel.JUNIOR: {"min": 6, "max": 8, "avg": 7},
        SkillLevel.MIDLEVEL: {"min": 4, "max": 5, "avg": 4.5},
        SkillLevel.SENIOR: {"min": 2, "max": 3, "avg": 2.5},
        SkillLevel.ARCHITECT: {"min": 1, "max": 2, "avg": 1.5},
    }
    
    @staticmethod
    def estimate_hours(story_points: int, skill_level: SkillLevel) -> float:
        """Convert story points to hours based on skill level.
        
        Phase 12 AC-CAP-2-02: Story point converter calculates hours per skill
        
        Args:
            story_points: Number of story points
            skill_level: Team skill level
            
        Returns:
            Estimated hours
        """
        conversion = StoryPointEstimator.CONVERSION_MATRIX.get(skill_level)
        if not conversion:
            conversion = StoryPointEstimator.CONVERSION_MATRIX[SkillLevel.MIDLEVEL]
        
        return story_points * conversion["avg"]
    
    @staticmethod
    def estimate_range(story_points: int, skill_level: SkillLevel) -> Tuple[float, float]:
        """Get range of hours for story points.
        
        Args:
            story_points: Number of story points
            skill_level: Team skill level
            
        Returns:
            (min_hours, max_hours)
        """
        conversion = StoryPointEstimator.CONVERSION_MATRIX.get(skill_level)
        if not conversion:
            conversion = StoryPointEstimator.CONVERSION_MATRIX[SkillLevel.MIDLEVEL]
        
        return (
            story_points * conversion["min"],
            story_points * conversion["max"]
        )


class CriticalPathEstimator:
    """Critical Path Method (CPM) estimator.
    
    Analyzes task dependencies to calculate critical path.
    Accounts for parallelization opportunities.
    """
    
    @dataclass
    class Task:
        """Task for CPM analysis."""
        task_id: str
        duration_hours: float
        dependencies: List[str] = field(default_factory=list)
        earliest_start: float = 0.0
        earliest_finish: float = 0.0
    
    @staticmethod
    def calculate_critical_path(tasks: Dict[str, Dict[str, Any]]) -> float:
        """Calculate critical path through task network.
        
        Phase 12 AC-CAP-2-03: CPM calculates parallel path optimization
        
        Args:
            tasks: Dictionary of {task_id: {duration, dependencies}}
            
        Returns:
            Total project duration in hours
        """
        if not tasks:
            return 0.0
        
        # Initialize
        task_objects = {}
        for task_id, task_data in tasks.items():
            task_objects[task_id] = CriticalPathEstimator.Task(
                task_id=task_id,
                duration_hours=task_data.get("duration", 0),
                dependencies=task_data.get("dependencies", [])
            )
        
        # Forward pass - calculate earliest start/finish
        def calculate_earliest(task_id: str) -> float:
            """Calculate earliest finish time for task."""
            task = task_objects[task_id]
            
            if not task.dependencies:
                task.earliest_start = 0.0
            else:
                # Earliest start = max(earliest finish of dependencies)
                task.earliest_start = max(
                    calculate_earliest(dep) for dep in task.dependencies
                )
            
            task.earliest_finish = task.earliest_start + task.duration_hours
            return task.earliest_finish
        
        # Calculate for all tasks
        critical_path_length = 0.0
        for task_id in task_objects:
            finish_time = calculate_earliest(task_id)
            critical_path_length = max(critical_path_length, finish_time)
        
        return critical_path_length


class MultiModelEstimationEngine:
    """Phase 12 CAP-2: Multi-Model Estimation Engine.
    
    Combines three independent estimation models:
    1. PERT: Statistical model for uncertainty
    2. Story Points: Team velocity-based estimation
    3. CPM: Dependency-based project scheduling
    
    Produces consensus estimate with:
    - 80% confidence intervals
    - Risk factor identification
    - Model agreement metrics
    - Transparent estimation basis (legend)
    
    AC-CAP-2-01: PERT estimator produces expected value + std dev
    AC-CAP-2-02: Story point converter handles 4 skill levels
    AC-CAP-2-03: CPM calculates parallel path optimization
    AC-CAP-2-04: Consensus produce 80% CI recommendations
    AC-CAP-2-05: Include estimation basis legend for transparency
    """
    
    def __init__(self):
        """Initialize MultiModelEstimationEngine."""
        self.pert = PERTEstimator()
        self.story_points = StoryPointEstimator()
        self.cpm = CriticalPathEstimator()
        self.assumptions = get_team_assumptions()
    
    def _skill_level_to_key(self, skill_level: SkillLevel) -> str:
        """Convert SkillLevel enum to config key.
        
        Args:
            skill_level: SkillLevel enum
            
        Returns:
            Config key string
        """
        mapping = {
            SkillLevel.JUNIOR: "junior",
            SkillLevel.MIDLEVEL: "mid_level",
            SkillLevel.SENIOR: "senior",
            SkillLevel.ARCHITECT: "architect",
        }
        return mapping.get(skill_level, "mid_level")
    
    def estimate_task(
        self,
        task_id: str,
        optimistic: float,
        likely: float,
        pessimistic: float,
        story_points: int,
        skill_level: SkillLevel = SkillLevel.MIDLEVEL,
        dependencies: Optional[Dict[str, float]] = None,
        include_legend: bool = True
    ) -> EstimationResult:
        """Estimate task using all three models.
        
        Phase 12 AC-CAP-2-04: Produce consensus estimate
        Phase 12 AC-CAP-2-05: Include estimation basis legend
        
        Args:
            task_id: Task identifier
            optimistic: PERT optimistic estimate
            likely: PERT likely estimate
            pessimistic: PERT pessimistic estimate
            story_points: Story point estimate
            skill_level: Team skill level
            dependencies: Dict of {dep_task_id: duration}
            include_legend: Whether to include full legend in result
            
        Returns:
            EstimationResult with all models and transparent legend
        """
        skill_key = self._skill_level_to_key(skill_level)
        
        # PERT estimation
        pert_hours, pert_std = self.pert.estimate(optimistic, likely, pessimistic)
        pert_low, pert_high = self.pert.get_confidence_interval(pert_hours, pert_std)
        
        # Story points estimation (use config-driven rates)
        config_hours_per_pt = self.assumptions.get_hours_per_point(skill_key)
        if config_hours_per_pt > 0:
            sp_hours = story_points * config_hours_per_pt
        else:
            sp_hours = self.story_points.estimate_hours(story_points, skill_level)
        sp_low, sp_high = self.story_points.estimate_range(story_points, skill_level)
        
        # CPM estimation
        cpm_hours = 0.0
        if dependencies:
            task_graph = {
                task_id: {
                    "duration": likely,
                    "dependencies": list(dependencies.keys())
                }
            }
            for dep_id, dep_duration in dependencies.items():
                task_graph[dep_id] = {
                    "duration": dep_duration,
                    "dependencies": []
                }
            cpm_hours = self.cpm.calculate_critical_path(task_graph)
        else:
            cpm_hours = likely
        
        # Calculate consensus
        model_estimates = [pert_hours, sp_hours, cpm_hours]
        recommended = sum(model_estimates) / len(model_estimates)
        
        # Calculate agreement
        variance = sum((x - recommended) ** 2 for x in model_estimates) / len(model_estimates)
        std_dev_models = math.sqrt(variance)
        agreement = max(0, 100 - (std_dev_models / recommended * 100)) if recommended > 0 else 0
        
        # Confidence interval
        all_estimates = [pert_low, pert_high, sp_low, sp_high, cpm_hours]
        ci_low = min(all_estimates)
        ci_high = max(all_estimates)
        
        # Calculate cost using config
        estimated_cost = self.assumptions.calculate_cost(recommended, skill_key)
        
        # Generate legend
        if include_legend:
            legend = self.assumptions.generate_legend(skill_levels_used=[skill_key])
        else:
            legend = self.assumptions.generate_compact_legend(skill_key)
        
        return EstimationResult(
            task_id=task_id,
            pert_hours=pert_hours,
            story_points=story_points,
            cpm_hours=cpm_hours,
            confidence_interval_low=ci_low,
            confidence_interval_high=ci_high,
            recommended_hours=recommended,
            model_agreement=agreement,
            skill_level_used=skill_key,
            estimated_cost=estimated_cost,
            legend=legend,
        )
    
    def get_estimation_summary(self, result: EstimationResult) -> Dict[str, Any]:
        """Get summary of estimation with cost and legend.
        
        Args:
            result: Estimation result
            
        Returns:
            Summary dictionary with transparent basis
        """
        currency = self.assumptions.costs.get("currency", "USD")
        
        return {
            "task_id": result.task_id,
            "recommended_hours": f"{result.recommended_hours:.1f}",
            "confidence_interval": f"{result.confidence_interval_low:.1f} - {result.confidence_interval_high:.1f}",
            "pert_hours": f"{result.pert_hours:.1f}",
            "story_points": result.story_points,
            "cpm_hours": f"{result.cpm_hours:.1f}",
            "model_agreement": f"{result.model_agreement:.1f}%",
            "skill_level": result.skill_level_used,
            "estimated_cost": f"{currency} {result.estimated_cost:,.2f}",
            "estimation_basis": result.legend,
        }
    
    def get_assumptions_legend(self) -> str:
        """Get full assumptions legend.
        
        Returns:
            Complete legend showing all estimation basis
        """
        return self.assumptions.generate_legend()


if __name__ == "__main__":
    logger.info("MultiModelEstimationEngine - Phase 12 CAP-2")
