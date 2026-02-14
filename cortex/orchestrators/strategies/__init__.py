"""
__init__.py for orchestrator strategies package.

ENH-087 Track 1.1: Stage Execution Strategy Pattern.
ENH-087 Track 1.2: Stage 2/3/4 Strategies.
ENH-087 Track 1.3: MasterOrchestrator Refactoring.

Imports use try/except for graceful degradation — strategy pattern
modules are created incrementally via TDD.
"""

# Core pipeline strategies (always available)
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

# ENH-090 Track 2: Refactoring Strategy Pattern (created via TDD when needed)
try:
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
except ImportError:
    RefactoringOperationType = None  # type: ignore[misc, assignment]
    RefactoringLanguage = None  # type: ignore[misc, assignment]
    StrategyExecutionMode = None  # type: ignore[misc, assignment]
    RefactoringRequest = None  # type: ignore[misc, assignment]
    RefactoringMetrics = None  # type: ignore[misc, assignment]
    RefactoringResult = None  # type: ignore[misc, assignment]
    RefactoringStrategy = None  # type: ignore[misc, assignment]
    BasicRefactoringStrategy = None  # type: ignore[misc, assignment]
    SOLIDRefactoringStrategy = None  # type: ignore[misc, assignment]
    ReviewRefactoringStrategy = None  # type: ignore[misc, assignment]
    UnifiedRefactoringOrchestrator = None  # type: ignore[misc, assignment]

# ENH-090 Track 2: Planning Strategy Pattern (created via TDD when needed)
try:
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
except ImportError:
    PlanningLevel = None  # type: ignore[misc, assignment]
    PlanningOperationType = None  # type: ignore[misc, assignment]
    RiskLevel = None  # type: ignore[misc, assignment]
    PlanningStep = None  # type: ignore[misc, assignment]
    PlanningRequest = None  # type: ignore[misc, assignment]
    PlanningMetrics = None  # type: ignore[misc, assignment]
    PlanningResult = None  # type: ignore[misc, assignment]
    PlanningStrategy = None  # type: ignore[misc, assignment]
    MacroPlanningStrategy = None  # type: ignore[misc, assignment]
    MicroPlanningStrategy = None  # type: ignore[misc, assignment]
    UnifiedPlanningOrchestrator = None  # type: ignore[misc, assignment]

# ENH-090 Track 2: Support Layer Consolidation (created via TDD when needed)
try:
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
except ImportError:
    SupportOperationType = None  # type: ignore[misc, assignment]
    SupportRequest = None  # type: ignore[misc, assignment]
    SupportMetrics = None  # type: ignore[misc, assignment]
    SupportResult = None  # type: ignore[misc, assignment]
    SupportStrategy = None  # type: ignore[misc, assignment]
    ValidationStrategy = None  # type: ignore[misc, assignment]
    ErrorHandlingStrategy = None  # type: ignore[misc, assignment]
    CachingStrategy = None  # type: ignore[misc, assignment]
    UnifiedSupportOrchestrator = None  # type: ignore[misc, assignment]

# ENH-091 Track 3: Infrastructure Layer Consolidation (created via TDD when needed)
try:
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
except ImportError:
    InfrastructureOperationType = None  # type: ignore[misc, assignment]
    InfrastructureRequest = None  # type: ignore[misc, assignment]
    InfrastructureMetrics = None  # type: ignore[misc, assignment]
    InfrastructureResult = None  # type: ignore[misc, assignment]
    InfrastructureStrategy = None  # type: ignore[misc, assignment]
    SessionManagementStrategy = None  # type: ignore[misc, assignment]
    ConfigurationManagementStrategy = None  # type: ignore[misc, assignment]
    DeploymentStrategy = None  # type: ignore[misc, assignment]
    MonitoringStrategy = None  # type: ignore[misc, assignment]
    UnifiedInfrastructureOrchestrator = None  # type: ignore[misc, assignment]

__all__ = [
    # Core pipeline (always available)
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
    # ENH-090 Track 2: Planning Strategy Pattern
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
    # ENH-090 Track 2: Support Layer Consolidation
    "SupportOperationType",
    "SupportRequest",
    "SupportMetrics",
    "SupportResult",
    "SupportStrategy",
    "ValidationStrategy",
    "ErrorHandlingStrategy",
    "CachingStrategy",
    "UnifiedSupportOrchestrator",
    # ENH-091 Track 3: Infrastructure Layer Consolidation
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
