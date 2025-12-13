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
]
