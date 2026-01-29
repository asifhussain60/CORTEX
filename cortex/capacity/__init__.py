"""CORTEX Capacity Planning Module.

Phase 12 Implementation: Multi-model estimation with transparent assumptions.

Components:
- MultiModelEstimationEngine: PERT, Story Points, CPM consensus
- SkillAllocator: Task classification and team allocation
- OutputFormatter: Sprint breakdowns and Gantt visualization
- LearningOrchestrator: Accuracy tracking and model tuning
- TeamAssumptions: Configuration-driven estimation basis with legend
"""

from cortex.capacity.multi_model_estimation_engine import (
    MultiModelEstimationEngine,
    EstimationResult,
    SkillLevel,
    PERTEstimator,
    StoryPointEstimator,
    CriticalPathEstimator,
)

from cortex.capacity.team_assumptions import (
    TeamAssumptions,
    TeamAssumptionsLoader,
    SkillLevelConfig,
    get_team_assumptions,
)

from cortex.capacity.capacity_planning_orchestrators import (
    SkillAllocator,
    OutputFormatter,
    LearningOrchestrator,
    TaskClassification,
    AllocationPlan,
)

__all__ = [
    # Estimation Engine
    "MultiModelEstimationEngine",
    "EstimationResult",
    "SkillLevel",
    "PERTEstimator",
    "StoryPointEstimator",
    "CriticalPathEstimator",
    # Team Assumptions
    "TeamAssumptions",
    "TeamAssumptionsLoader",
    "SkillLevelConfig",
    "get_team_assumptions",
    # Planning Orchestrators
    "SkillAllocator",
    "OutputFormatter",
    "LearningOrchestrator",
    "TaskClassification",
    "AllocationPlan",
]
