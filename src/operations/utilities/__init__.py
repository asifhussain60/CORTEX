"""
Operations Utilities - Shared components for CORTEX orchestration workflows.

**Modules:**
- progress_renderer: Real-time visual progress bars for autonomous execution
- vision_context_middleware: Automatic GPT-4V engagement for image analysis
- orchestration_metrics_collector: Silent background metrics collection
- task_injection_manager: Context-aware mid-execution task injection
- orchestration_checkpoint_manager: Save/restore/rollback workflow state
- parallel_orchestration_coordinator: Concurrent phase execution with dependency resolution
- orchestration_analytics_dashboard: Visualization and reporting for metrics
- resource_management_orchestrator: Resource monitoring and optimization
- error_recovery_orchestrator: Retry policies and circuit breakers
- performance_profiling_orchestrator: Execution profiling and bottleneck detection

**Author:** Asif Hussain
**Version:** 3.8.1
"""


from .progress_renderer import ProgressRenderer
from .vision_context_middleware import VisionContextMiddleware, with_vision_context_middleware
from .orchestration_metrics_collector import (
    OrchestrationMetricsCollector,
    with_orchestration_metrics
)
from .task_injection_manager import (
    TaskInjectionManager,
    TaskPriority,
    TaskStatus
)
from .orchestration_checkpoint_manager import (
    OrchestrationCheckpointManager,
    CheckpointNotFoundError,
    CheckpointCorruptedError
)
from .parallel_orchestration_coordinator import (
    ParallelOrchestrationCoordinator,
    PhaseDefinition,
    DependencyError,
    ResourceLockError
)
from .orchestration_analytics_dashboard import OrchestrationAnalyticsDashboard
from .resource_management_orchestrator import ResourceManagementOrchestrator
from .error_recovery_orchestrator import ErrorRecoveryOrchestrator
from .performance_profiling_orchestrator import (
    PerformanceProfilingOrchestrator,
    ProfileResult,
    BottleneckReport,
    RegressionReport
)
from .documentation_generation_orchestrator import (
    DocumentationGenerationOrchestrator,
    DocstringInfo,
    APIReference,
    UsageGuide
)
from .code_quality_orchestrator import (
    CodeQualityOrchestrator,
    CodeReviewReport,
    ComplexityReport,
    QualityScorecard
)
from .deployment_orchestrator import (
    DeploymentOrchestrator,
    DeploymentResult,
    EnvironmentConfig
)
from .integration_testing_orchestrator import (
    IntegrationTestingOrchestrator,
    TestEnvironment,
    TestResult
)
from .holistic_review_orchestrator import (
    HolisticReviewOrchestrator,
    ReviewResult,
    QualityGate
)
from .knowledge_graph_auto_updater import (
    KnowledgeGraphAutoUpdater,
    UpdateResult,
    PatternExtractor
)
from .vscode_cache_manager import (
    VSCodeCacheManager,
    optimize_pre_flight,
    run_full_cleanup,
    check_cache_health
)

__all__ = [
    "ProgressRenderer",
    "VisionContextMiddleware",
    "with_vision_context_middleware",
    "OrchestrationMetricsCollector",
    "with_orchestration_metrics",
    "TaskInjectionManager",
    "TaskPriority",
    "TaskStatus",
    "OrchestrationCheckpointManager",
    "CheckpointNotFoundError",
    "CheckpointCorruptedError",
    "ParallelOrchestrationCoordinator",
    "PhaseDefinition",
    "DependencyError",
    "ResourceLockError",
    "OrchestrationAnalyticsDashboard",
    "ResourceManagementOrchestrator",
    "ErrorRecoveryOrchestrator",
    "PerformanceProfilingOrchestrator",
    "ProfileResult",
    "BottleneckReport",
    "RegressionReport",
    "DocumentationGenerationOrchestrator",
    "DocstringInfo",
    "APIReference",
    "UsageGuide",
    "CodeQualityOrchestrator",
    "CodeReviewReport",
    "ComplexityReport",
    "QualityScorecard",
    "DeploymentOrchestrator",
    "DeploymentResult",
    "EnvironmentConfig",
    "IntegrationTestingOrchestrator",
    "TestEnvironment",
    "TestResult",
    "HolisticReviewOrchestrator",
    "ReviewResult",
    "QualityGate",
    "KnowledgeGraphAutoUpdater",
    "UpdateResult",
    "PatternExtractor",
    "VSCodeCacheManager",
    "optimize_pre_flight",
    "run_full_cleanup",
    "check_cache_health",
]
