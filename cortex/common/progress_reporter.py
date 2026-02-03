"""
Progress Reporter - User Feedback and Time Estimation System.

Provides real-time progress feedback for long-running operations:
- Step-by-step progress reporting
- Time estimation (elapsed, remaining, ETA)
- Visual progress indicators
- Support for nested operations
- Callback-based progress updates

AC-ID: AC-PROGRESS-FEEDBACK-001
Authority: CORE-UX-001 (User Experience), CORTEX Standards

Author: Asif Hussain
Date: 2026-02-03
"""

from __future__ import annotations

import logging
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Protocol

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND TYPES
# =============================================================================


class ProgressStatus(Enum):
    """Status of a progress step."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


class ProgressStyle(Enum):
    """Output styles for progress reporting."""
    MINIMAL = "minimal"      # One-liner updates
    DETAILED = "detailed"    # Step-by-step with timing
    VERBOSE = "verbose"      # Full details with estimates
    SILENT = "silent"        # No output (logging only)


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class ProgressStep:
    """Represents a single step in a multi-step operation."""
    
    name: str
    description: str
    step_number: int = 0
    total_steps: int = 0
    status: ProgressStatus = ProgressStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration_seconds: float = 0.0
    actual_duration_seconds: float = 0.0
    sub_steps: List['ProgressStep'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        if self.started_at is None:
            return 0.0
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()
    
    @property
    def progress_percentage(self) -> float:
        """Get progress percentage (0-100)."""
        if self.total_steps == 0:
            return 0.0
        return (self.step_number / self.total_steps) * 100


@dataclass
class OperationProgress:
    """Tracks progress of an entire operation."""
    
    operation_name: str
    total_steps: int
    current_step: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    steps: List[ProgressStep] = field(default_factory=list)
    status: ProgressStatus = ProgressStatus.PENDING
    
    @property
    def elapsed_seconds(self) -> float:
        """Total elapsed time in seconds."""
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()
    
    @property
    def progress_percentage(self) -> float:
        """Get progress percentage (0-100)."""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100
    
    @property
    def estimated_remaining_seconds(self) -> float:
        """Estimate remaining time based on average step duration."""
        if self.current_step == 0:
            return 0.0
        avg_per_step = self.elapsed_seconds / self.current_step
        remaining_steps = self.total_steps - self.current_step
        return avg_per_step * remaining_steps
    
    @property
    def estimated_total_seconds(self) -> float:
        """Estimate total duration."""
        return self.elapsed_seconds + self.estimated_remaining_seconds
    
    @property
    def eta(self) -> Optional[datetime]:
        """Estimated time of arrival (completion)."""
        if self.current_step == 0:
            return None
        return datetime.now() + timedelta(seconds=self.estimated_remaining_seconds)


# =============================================================================
# TIME ESTIMATION ENGINE
# =============================================================================


class TimeEstimator:
    """
    Intelligent time estimation based on operation history.
    
    Tracks historical durations to provide more accurate estimates.
    """
    
    # Default estimates for common operations (seconds)
    DEFAULT_ESTIMATES: Dict[str, float] = {
        # Repository Onboarding Steps
        "ensure_assets": 2.0,
        "lens_analysis": 30.0,
        "business_narrative": 15.0,
        "security_modeling": 10.0,
        "domain_updates": 5.0,
        "recommendations": 5.0,
        "dashboard_generation": 10.0,
        "landing_page": 3.0,
        
        # Environment Setup Steps
        "environment_setup": 10.0,
        "dependency_check": 5.0,
        "package_installation": 60.0,  # Can be long
        "configuration": 5.0,
        "verification": 10.0,
        
        # MCP Onboarding V3 Steps
        "schema_check": 2.0,
        "lens_full_analysis": 45.0,
        "llm_generation": 30.0,
        "sqlite_aggregation": 15.0,
        "registry_update": 5.0,
        "validation": 10.0,
        
        # Generic defaults
        "file_scan_per_100": 1.0,  # Per 100 files
        "analysis_per_1000_loc": 0.5,  # Per 1000 lines of code
    }
    
    def __init__(self):
        """Initialize time estimator."""
        self._history: Dict[str, List[float]] = {}
        self._max_history = 10  # Keep last N measurements
    
    def get_estimate(self, operation: str, **context: Any) -> float:
        """
        Get time estimate for an operation.
        
        Args:
            operation: Operation identifier
            **context: Optional context (e.g., file_count, loc)
            
        Returns:
            Estimated duration in seconds
        """
        # Check history first
        if operation in self._history and self._history[operation]:
            return sum(self._history[operation]) / len(self._history[operation])
        
        # Use default estimate
        base_estimate = self.DEFAULT_ESTIMATES.get(operation, 10.0)
        
        # Adjust based on context
        if "file_count" in context:
            file_factor = context["file_count"] / 100
            base_estimate *= max(1.0, file_factor)
        
        if "loc" in context:
            loc_factor = context["loc"] / 10000
            base_estimate *= max(1.0, loc_factor)
        
        return base_estimate
    
    def record_duration(self, operation: str, duration: float) -> None:
        """
        Record actual duration for future estimates.
        
        Args:
            operation: Operation identifier
            duration: Actual duration in seconds
        """
        if operation not in self._history:
            self._history[operation] = []
        
        self._history[operation].append(duration)
        
        # Trim to max history
        if len(self._history[operation]) > self._max_history:
            self._history[operation] = self._history[operation][-self._max_history:]


# =============================================================================
# PROGRESS REPORTER
# =============================================================================


class ProgressCallback(Protocol):
    """Protocol for progress callbacks."""
    
    def __call__(
        self,
        step: int,
        total: int,
        message: str,
        elapsed: float,
        remaining: float,
    ) -> None:
        """Called on progress update."""
        ...


class ProgressReporter:
    """
    Main progress reporter for long-running operations.
    
    Features:
    - Step-by-step progress tracking
    - Time estimation (elapsed, remaining, ETA)
    - Multiple output styles
    - Callback support for UI integration
    - Nested operation support
    
    Example:
        >>> with ProgressReporter("Repository Onboarding", total_steps=7) as progress:
        ...     progress.start_step("LENS Analysis", estimated_seconds=30)
        ...     # ... do work ...
        ...     progress.complete_step()
        ...     progress.start_step("Security Modeling", estimated_seconds=10)
        ...     # ... do work ...
        ...     progress.complete_step()
    """
    
    def __init__(
        self,
        operation_name: str,
        total_steps: int,
        style: ProgressStyle = ProgressStyle.DETAILED,
        callback: Optional[ProgressCallback] = None,
        output_stream: Any = None,
        time_estimator: Optional[TimeEstimator] = None,
    ):
        """
        Initialize progress reporter.
        
        Args:
            operation_name: Name of the operation
            total_steps: Total number of steps
            style: Output style
            callback: Optional callback for progress updates
            output_stream: Output stream (defaults to sys.stdout)
            time_estimator: Optional time estimator for better estimates
        """
        self.operation_name = operation_name
        self.total_steps = total_steps
        self.style = style
        self.callback = callback
        self.output = output_stream or sys.stdout
        self.time_estimator = time_estimator or TimeEstimator()
        
        self._progress = OperationProgress(
            operation_name=operation_name,
            total_steps=total_steps,
        )
        self._current_step: Optional[ProgressStep] = None
        self._step_estimates: Dict[str, float] = {}
    
    def __enter__(self) -> 'ProgressReporter':
        """Context manager entry."""
        self._progress.status = ProgressStatus.RUNNING
        self._report_start()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if exc_type is None:
            self._progress.status = ProgressStatus.COMPLETED
        else:
            self._progress.status = ProgressStatus.FAILED
        self._progress.completed_at = datetime.now()
        self._report_complete()
    
    def set_step_estimates(self, estimates: Dict[str, float]) -> None:
        """
        Set estimated durations for steps.
        
        Args:
            estimates: Dict mapping step names to estimated seconds
        """
        self._step_estimates = estimates
    
    def start_step(
        self,
        name: str,
        description: str = "",
        estimated_seconds: Optional[float] = None,
    ) -> None:
        """
        Start a new step.
        
        Args:
            name: Step name
            description: Step description
            estimated_seconds: Estimated duration (auto-calculated if None)
        """
        # Complete previous step if needed
        if self._current_step and self._current_step.status == ProgressStatus.RUNNING:
            self.complete_step()
        
        self._progress.current_step += 1
        
        # Calculate estimate
        if estimated_seconds is None:
            estimated_seconds = self._step_estimates.get(
                name,
                self.time_estimator.get_estimate(name.lower().replace(" ", "_"))
            )
        
        step = ProgressStep(
            name=name,
            description=description or name,
            step_number=self._progress.current_step,
            total_steps=self.total_steps,
            status=ProgressStatus.RUNNING,
            started_at=datetime.now(),
            estimated_duration_seconds=estimated_seconds,
        )
        
        self._current_step = step
        self._progress.steps.append(step)
        self._report_step_start(step)
    
    def complete_step(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark current step as complete.
        
        Args:
            metadata: Optional metadata to attach
        """
        if self._current_step is None:
            return
        
        self._current_step.status = ProgressStatus.COMPLETED
        self._current_step.completed_at = datetime.now()
        self._current_step.actual_duration_seconds = self._current_step.elapsed_seconds
        
        if metadata:
            self._current_step.metadata.update(metadata)
        
        # Record for future estimates
        step_key = self._current_step.name.lower().replace(" ", "_")
        self.time_estimator.record_duration(step_key, self._current_step.actual_duration_seconds)
        
        self._report_step_complete(self._current_step)
    
    def fail_step(self, error: str) -> None:
        """
        Mark current step as failed.
        
        Args:
            error: Error message
        """
        if self._current_step is None:
            return
        
        self._current_step.status = ProgressStatus.FAILED
        self._current_step.completed_at = datetime.now()
        self._current_step.metadata["error"] = error
        self._report_step_failed(self._current_step, error)
    
    def skip_step(self, name: str, reason: str = "") -> None:
        """
        Skip a step.
        
        Args:
            name: Step name
            reason: Reason for skipping
        """
        self._progress.current_step += 1
        step = ProgressStep(
            name=name,
            description=reason or f"Skipped: {name}",
            step_number=self._progress.current_step,
            total_steps=self.total_steps,
            status=ProgressStatus.SKIPPED,
        )
        self._progress.steps.append(step)
        self._report_step_skipped(step, reason)
    
    def update_message(self, message: str) -> None:
        """
        Update progress message without changing step.
        
        Args:
            message: Status message
        """
        self._report_message(message)
    
    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed seconds."""
        return self._progress.elapsed_seconds
    
    @property
    def remaining_seconds(self) -> float:
        """Get estimated remaining seconds."""
        return self._progress.estimated_remaining_seconds
    
    @property
    def progress_percentage(self) -> float:
        """Get progress percentage."""
        return self._progress.progress_percentage
    
    # =========================================================================
    # REPORTING METHODS (style-dependent)
    # =========================================================================
    
    def _report_start(self) -> None:
        """Report operation start."""
        if self.style == ProgressStyle.SILENT:
            return
        
        total_estimate = sum(
            self._step_estimates.get(f"step_{i}", 10.0)
            for i in range(1, self.total_steps + 1)
        )
        if total_estimate == 0:
            total_estimate = self.total_steps * 10  # Default 10s per step
        
        header = f"\n{'='*70}"
        title = f"🚀 {self.operation_name}"
        info = f"   Steps: {self.total_steps} | Est. Time: {self._format_duration(total_estimate)}"
        
        if self.style == ProgressStyle.MINIMAL:
            self._write(f"\n⏳ {self.operation_name} ({self.total_steps} steps)...")
        else:
            self._write(header)
            self._write(title)
            self._write(info)
            self._write('='*70)
        
        logger.info(f"Started: {self.operation_name} ({self.total_steps} steps)")
    
    def _report_step_start(self, step: ProgressStep) -> None:
        """Report step start."""
        if self.style == ProgressStyle.SILENT:
            return
        
        progress_bar = self._create_progress_bar(step.step_number - 1, self.total_steps)
        step_info = f"[{step.step_number}/{self.total_steps}]"
        est_info = f"(~{self._format_duration(step.estimated_duration_seconds)})"
        
        if self.style == ProgressStyle.MINIMAL:
            self._write(f"\r⏳ {step_info} {step.name}...{' '*20}", end="")
        elif self.style == ProgressStyle.DETAILED:
            self._write(f"\n📌 Step {step_info}: {step.name} {est_info}")
            self._write(f"   {progress_bar}")
        else:  # VERBOSE
            remaining = self._progress.estimated_remaining_seconds
            eta = self._progress.eta
            eta_str = eta.strftime("%H:%M:%S") if eta else "calculating..."
            
            self._write(f"\n{'─'*70}")
            self._write(f"📌 Step {step_info}: {step.name}")
            self._write(f"   Description: {step.description}")
            self._write(f"   Estimated: {self._format_duration(step.estimated_duration_seconds)}")
            self._write(f"   Remaining: {self._format_duration(remaining)} | ETA: {eta_str}")
            self._write(f"   {progress_bar}")
        
        # Invoke callback
        if self.callback:
            self.callback(
                step=step.step_number,
                total=self.total_steps,
                message=f"Step {step.step_number}: {step.name}",
                elapsed=self._progress.elapsed_seconds,
                remaining=self._progress.estimated_remaining_seconds,
            )
    
    def _report_step_complete(self, step: ProgressStep) -> None:
        """Report step completion."""
        if self.style == ProgressStyle.SILENT:
            return
        
        duration = step.actual_duration_seconds
        
        if self.style == ProgressStyle.MINIMAL:
            self._write(f"\r✅ [{step.step_number}/{self.total_steps}] {step.name} ({self._format_duration(duration)})")
        elif self.style == ProgressStyle.DETAILED:
            self._write(f"   ✅ Completed in {self._format_duration(duration)}")
        else:  # VERBOSE
            diff = duration - step.estimated_duration_seconds
            diff_str = f"+{self._format_duration(abs(diff))}" if diff > 0 else f"-{self._format_duration(abs(diff))}"
            self._write(f"   ✅ Completed in {self._format_duration(duration)} ({diff_str} vs estimate)")
        
        logger.info(f"Completed step: {step.name} in {duration:.2f}s")
    
    def _report_step_failed(self, step: ProgressStep, error: str) -> None:
        """Report step failure."""
        if self.style == ProgressStyle.SILENT:
            return
        
        self._write(f"   ❌ FAILED: {error}")
        logger.error(f"Failed step: {step.name} - {error}")
    
    def _report_step_skipped(self, step: ProgressStep, reason: str) -> None:
        """Report step skipped."""
        if self.style == ProgressStyle.SILENT:
            return
        
        self._write(f"   ⏭️  Skipped: {step.name}" + (f" ({reason})" if reason else ""))
        logger.info(f"Skipped step: {step.name} - {reason}")
    
    def _report_message(self, message: str) -> None:
        """Report status message."""
        if self.style == ProgressStyle.SILENT:
            return
        
        if self.style == ProgressStyle.MINIMAL:
            self._write(f"\r   📝 {message}{' '*20}", end="")
        else:
            self._write(f"   📝 {message}")
    
    def _report_complete(self) -> None:
        """Report operation completion."""
        if self.style == ProgressStyle.SILENT:
            return
        
        total_duration = self._progress.elapsed_seconds
        status_emoji = "✅" if self._progress.status == ProgressStatus.COMPLETED else "❌"
        status_text = "COMPLETED" if self._progress.status == ProgressStatus.COMPLETED else "FAILED"
        
        if self.style == ProgressStyle.MINIMAL:
            self._write(f"\n{status_emoji} {self.operation_name} {status_text} in {self._format_duration(total_duration)}")
        else:
            self._write(f"\n{'='*70}")
            self._write(f"{status_emoji} {self.operation_name} {status_text}")
            self._write(f"   Total Time: {self._format_duration(total_duration)}")
            
            if self.style == ProgressStyle.VERBOSE:
                completed = sum(1 for s in self._progress.steps if s.status == ProgressStatus.COMPLETED)
                failed = sum(1 for s in self._progress.steps if s.status == ProgressStatus.FAILED)
                skipped = sum(1 for s in self._progress.steps if s.status == ProgressStatus.SKIPPED)
                self._write(f"   Steps: {completed} completed, {failed} failed, {skipped} skipped")
            
            self._write('='*70)
        
        logger.info(f"Finished: {self.operation_name} in {total_duration:.2f}s ({status_text})")
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _write(self, text: str, end: str = "\n") -> None:
        """Write to output stream."""
        self.output.write(text + end)
        self.output.flush()
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form."""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"
    
    def _create_progress_bar(
        self,
        current: int,
        total: int,
        width: int = 40,
    ) -> str:
        """Create ASCII progress bar."""
        if total == 0:
            percentage = 0
        else:
            percentage = (current / total) * 100
        
        filled = int(width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:5.1f}%"


# =============================================================================
# CONTEXT MANAGERS FOR COMMON OPERATIONS
# =============================================================================


@contextmanager
def track_repository_onboarding(
    repo_name: str,
    style: ProgressStyle = ProgressStyle.DETAILED,
    callback: Optional[ProgressCallback] = None,
):
    """
    Context manager for repository onboarding with progress tracking.
    
    Args:
        repo_name: Repository name
        style: Output style
        callback: Optional progress callback
        
    Yields:
        ProgressReporter instance
    """
    estimator = TimeEstimator()
    reporter = ProgressReporter(
        operation_name=f"Repository Onboarding: {repo_name}",
        total_steps=8,
        style=style,
        callback=callback,
        time_estimator=estimator,
    )
    
    reporter.set_step_estimates({
        "Ensure Assets": estimator.get_estimate("ensure_assets"),
        "LENS Analysis": estimator.get_estimate("lens_analysis"),
        "Business Narrative": estimator.get_estimate("business_narrative"),
        "Security Modeling": estimator.get_estimate("security_modeling"),
        "Domain Updates": estimator.get_estimate("domain_updates"),
        "Recommendations": estimator.get_estimate("recommendations"),
        "Dashboard Generation": estimator.get_estimate("dashboard_generation"),
        "Landing Page": estimator.get_estimate("landing_page"),
    })
    
    with reporter:
        yield reporter


@contextmanager
def track_environment_setup(
    environment_name: str = "Development",
    style: ProgressStyle = ProgressStyle.DETAILED,
    callback: Optional[ProgressCallback] = None,
):
    """
    Context manager for environment setup with progress tracking.
    
    Args:
        environment_name: Environment name
        style: Output style
        callback: Optional progress callback
        
    Yields:
        ProgressReporter instance
    """
    estimator = TimeEstimator()
    reporter = ProgressReporter(
        operation_name=f"Environment Setup: {environment_name}",
        total_steps=5,
        style=style,
        callback=callback,
        time_estimator=estimator,
    )
    
    reporter.set_step_estimates({
        "Pre-Validation": 2.0,
        "Environment Setup": estimator.get_estimate("environment_setup"),
        "Dependency Installation": estimator.get_estimate("package_installation"),
        "Configuration": estimator.get_estimate("configuration"),
        "Verification": estimator.get_estimate("verification"),
    })
    
    with reporter:
        yield reporter


@contextmanager
def track_mcp_onboarding_v3(
    repo_name: str,
    style: ProgressStyle = ProgressStyle.DETAILED,
    callback: Optional[ProgressCallback] = None,
):
    """
    Context manager for MCP V3 onboarding with progress tracking.
    
    Args:
        repo_name: Repository name
        style: Output style
        callback: Optional progress callback
        
    Yields:
        ProgressReporter instance
    """
    estimator = TimeEstimator()
    reporter = ProgressReporter(
        operation_name=f"MCP Onboarding V3: {repo_name}",
        total_steps=6,
        style=style,
        callback=callback,
        time_estimator=estimator,
    )
    
    reporter.set_step_estimates({
        "Schema Check": estimator.get_estimate("schema_check"),
        "LENS Analysis": estimator.get_estimate("lens_full_analysis"),
        "LLM Generation": estimator.get_estimate("llm_generation"),
        "SQLite Aggregation": estimator.get_estimate("sqlite_aggregation"),
        "Registry Update": estimator.get_estimate("registry_update"),
        "Validation": estimator.get_estimate("validation"),
    })
    
    with reporter:
        yield reporter


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_global_estimator: Optional[TimeEstimator] = None


def get_time_estimator() -> TimeEstimator:
    """Get global time estimator instance."""
    global _global_estimator
    if _global_estimator is None:
        _global_estimator = TimeEstimator()
    return _global_estimator


__all__ = [
    # Enums
    "ProgressStatus",
    "ProgressStyle",
    # Data models
    "ProgressStep",
    "OperationProgress",
    # Core classes
    "TimeEstimator",
    "ProgressReporter",
    "ProgressCallback",
    # Context managers
    "track_repository_onboarding",
    "track_environment_setup",
    "track_mcp_onboarding_v3",
    # Singleton
    "get_time_estimator",
]
