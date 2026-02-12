"""
__init__.py for orchestrator strategies package.

ENH-087 Track 1.1: Stage Execution Strategy Pattern.
ENH-087 Track 1.2: Stage 2/3/4 Strategies.
ENH-087 Track 1.3: MasterOrchestrator Refactoring.
"""

from cortex.orchestrators.strategies.stage_execution_strategy import (
    StageContext,
    StageExecutionStrategy,
)
from cortex.orchestrators.strategies.stage1_comprehension_strategy import (
    Stage1ComprehensionStrategy,
)
from cortex.orchestrators.strategies.stage234_strategies import (
    Stage2IntentClassificationStrategy,
    Stage3ComplianceValidationStrategy,
    Stage4DomainExecutionStrategy,
)
from cortex.orchestrators.strategies.refactoring_strategy_pattern import (
    RefactoringOperationType,
    RefactoringLanguage,
    StrategyExecutionMode,
    RefactoringRequest,
    RefactoringMetrics,
    RefactoringResult,
    RefactoringStrategy,
    BasicRefactoringStrategy,
    SOLIDRefactoringStrategy,
    ReviewRefactoringStrategy,
    UnifiedRefactoringOrchestrator,
)
from cortex.orchestrators.strategies.planning_strategy_pattern import (
    PlanningLevel,
    PlanningOperationType,
    RiskLevel,
    PlanningStep,
    PlanningRequest,
    PlanningMetrics,
    PlanningResult,
    PlanningStrategy,
    MacroPlanningStrategy,
    MicroPlanningStrategy,
    UnifiedPlanningOrchestrator,
)
from cortex.orchestrators.strategies.support_layer_pattern import (
    SupportOperationType,
    SupportRequest,
    SupportMetrics,
    SupportResult,
    SupportStrategy,
    ValidationStrategy,
    ErrorHandlingStrategy,
    CachingStrategy,
    UnifiedSupportOrchestrator,
)
from cortex.orchestrators.strategies.infrastructure_strategy_pattern import (
    InfrastructureOperationType,
    InfrastructureRequest,
    InfrastructureMetrics,
    InfrastructureResult,
    InfrastructureStrategy,
    SessionManagementStrategy,
    ConfigurationManagementStrategy,
    DeploymentStrategy,
    MonitoringStrategy,
    UnifiedInfrastructureOrchestrator,
)

__all__ = [
    "StageContext",
    "StageExecutionStrategy",
    "Stage1ComprehensionStrategy",
    "Stage2IntentClassificationStrategy",
    "Stage3ComplianceValidationStrategy",
    "Stage4DomainExecutionStrategy",
    # ENH-090 Track 2: Refactoring Strategy Pattern
    "RefactoringOperationType",
    "RefactoringLanguage",
    "StrategyExecutionMode",
    "RefactoringRequest",
    "RefactoringMetrics",
    "RefactoringResult",
    "RefactoringStrategy",
    "BasicRefactoringStrategy",
    "SOLIDRefactoringStrategy",
    "ReviewRefactoringStrategy",
    "UnifiedRefactoringOrchestrator",
    # ENH-090 Track 2: Planning Strategy Pattern (Stage 2)
    "PlanningLevel",
    "PlanningOperationType",
    "RiskLevel",
    "PlanningStep",
    "PlanningRequest",
    "PlanningMetrics",
    "PlanningResult",
    "PlanningStrategy",
    "MacroPlanningStrategy",
    "MicroPlanningStrategy",
    "UnifiedPlanningOrchestrator",
    # ENH-090 Track 2: Support Layer Consolidation (Stage 3)
    "SupportOperationType",
    "SupportRequest",
    "SupportMetrics",
    "SupportResult",
    "SupportStrategy",
    "ValidationStrategy",
    "ErrorHandlingStrategy",
    "CachingStrategy",
    "UnifiedSupportOrchestrator",
    # ENH-091 Track 3: Infrastructure Layer Consolidation (Stage 1)
    "InfrastructureOperationType",
    "InfrastructureRequest",
    "InfrastructureMetrics",
    "InfrastructureResult",
    "InfrastructureStrategy",
    "SessionManagementStrategy",
    "ConfigurationManagementStrategy",
    "DeploymentStrategy",
    "MonitoringStrategy",
    "UnifiedInfrastructureOrchestrator",
]
