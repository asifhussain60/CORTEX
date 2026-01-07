"""
CORTEX 6.0 Enterprise Audit Logger

Structured trace logging for Phase 3 Infrastructure Implementation.
Provides searchable, organized audit trail for all orchestrator operations.

Enhanced with:
- Correlation ID propagation
- Audit log analysis methods
- Phase/Feature gate integration

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
import uuid
import functools
import statistics
from contextlib import contextmanager
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Generator
import threading


class AuditLevel(str, Enum):
    """Audit log levels."""
    TRACE = "trace"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(str, Enum):
    """Categories for audit events."""
    STATE_MANAGEMENT = "state_management"
    EXECUTION = "execution"
    MIDDLEWARE = "middleware"
    RESPONSE = "response"
    PERFORMANCE = "performance"
    SECURITY = "security"
    VALIDATION = "validation"


@dataclass
class AuditEntry:
    """Structured audit log entry."""
    timestamp: str
    level: AuditLevel
    category: AuditCategory
    component: str
    operation: str
    message: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    correlation_id: Optional[str] = None
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class CorrelationSearchResult:
    """Result of correlation ID search."""
    correlation_id: str
    total_entries: int
    entries: List[AuditEntry]
    time_span_ms: float
    components: List[str]
    first_timestamp: Optional[str] = None
    last_timestamp: Optional[str] = None


@dataclass
class TraceResult:
    """Result of trace retrieval."""
    correlation_id: str
    status: str
    start_time: Optional[str]
    end_time: Optional[str]
    duration_ms: float
    steps: List[AuditEntry]
    input_context: Dict[str, Any]
    output_result: Dict[str, Any]


@dataclass
class ErrorSummary:
    """Summary of errors for a correlation ID or time range."""
    total_entries: int
    error_count: int
    error_rate: float
    errors: List[AuditEntry]
    error_types: List[str]


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""
    operation: str
    sample_count: int
    min_ms: float
    max_ms: float
    avg_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float


@dataclass
class TimelineEvent:
    """Single event in a timeline."""
    timestamp: str
    component: str
    operation: str
    message: str
    level: AuditLevel


@dataclass
class TimelineView:
    """Timeline view of operations."""
    events: List[TimelineEvent]
    total_duration_ms: float


@dataclass
class GateResult:
    """Result of a gate check."""
    passed: bool
    gate_name: str
    feature_id: str
    phase_id: Optional[int] = None
    required_features: Optional[List[str]] = None
    message: Optional[str] = None


# Thread-local storage for correlation context
_correlation_context = threading.local()


class EnterpriseAuditLogger:
    """
    Enterprise-grade audit logging system.
    
    Features:
    - Structured JSON logging
    - Category-based organization
    - Correlation ID tracking and propagation
    - Performance metrics
    - Thread-safe operations
    - Searchable output
    - Phase/Feature gate integration
    """
    
    def __init__(
        self,
        log_dir: Optional[str] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        auto_generate_correlation: bool = True
    ):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory for audit logs
            enable_console: Enable console output
            enable_file: Enable file output
            auto_generate_correlation: Auto-generate correlation IDs when not provided
        """
        self.log_dir = Path(log_dir) if log_dir else Path("cortex-brain/audit-logs")
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.auto_generate_correlation = auto_generate_correlation
        self._lock = threading.Lock()
        self._setup_logging()
        
        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.entry_count = 0
        
        # Category-specific files
        self.category_files: Dict[AuditCategory, Path] = {}
        
        # Correlation chain tracking
        self._correlation_chains: Dict[str, List[str]] = {}
        
        # Trace storage for active traces
        self._active_traces: Dict[str, Dict[str, Any]] = {}
        
        if enable_file:
            self._setup_category_files()
    
    # =========================================================================
    # CORRELATION ID MANAGEMENT (Task 1.3.2)
    # =========================================================================
    
    def _generate_correlation_id(self) -> str:
        """Generate a new correlation ID."""
        return f"CORTEX-{uuid.uuid4().hex[:12].upper()}"
    
    def get_current_correlation_id(self) -> Optional[str]:
        """Get the current correlation ID from thread-local context."""
        return getattr(_correlation_context, 'correlation_id', None)
    
    def _set_correlation_context(self, correlation_id: str):
        """Set the correlation ID in thread-local context."""
        _correlation_context.correlation_id = correlation_id
    
    def _clear_correlation_context(self):
        """Clear the correlation ID from thread-local context."""
        if hasattr(_correlation_context, 'correlation_id'):
            delattr(_correlation_context, 'correlation_id')
    
    @contextmanager
    def correlation_context(self, correlation_id: str) -> Generator[str, None, None]:
        """
        Context manager for correlation ID propagation.
        
        All log entries within this context will automatically use
        the specified correlation ID.
        
        Args:
            correlation_id: The correlation ID to use
            
        Yields:
            The correlation ID
        """
        previous = self.get_current_correlation_id()
        self._set_correlation_context(correlation_id)
        try:
            yield correlation_id
        finally:
            if previous:
                self._set_correlation_context(previous)
            else:
                self._clear_correlation_context()
    
    def start_correlation_chain(self, parent_id: str):
        """
        Start a correlation chain for tracking parent-child relationships.
        
        Args:
            parent_id: The parent correlation ID
        """
        self._set_correlation_context(parent_id)
        with self._lock:
            self._correlation_chains[parent_id] = [parent_id]
    
    def create_child_correlation(self) -> str:
        """
        Create a child correlation ID linked to the current parent.
        
        Returns:
            The new child correlation ID
        """
        parent_id = self.get_current_correlation_id()
        child_id = f"{parent_id}-CHILD-{uuid.uuid4().hex[:8].upper()}"
        
        with self._lock:
            if parent_id and parent_id in self._correlation_chains:
                self._correlation_chains[parent_id].append(child_id)
                # Store parent reference for later retrieval
                self._correlation_chains[f"_parent_{child_id}"] = parent_id
        
        return child_id
    
    def end_correlation_chain(self):
        """End the current correlation chain."""
        self._clear_correlation_context()
    
    def get_correlation_chain(self, parent_id: str) -> Optional[List[AuditEntry]]:
        """
        Get all entries in a correlation chain.
        
        Args:
            parent_id: The parent correlation ID
            
        Returns:
            List of audit entries in the chain, or None if not found
        """
        with self._lock:
            chain_ids = self._correlation_chains.get(parent_id, [])
        
        if not chain_ids:
            return None
        
        entries = []
        for corr_id in chain_ids:
            entries.extend(self.search(correlation_id=corr_id))
        
        # Sort by timestamp
        entries.sort(key=lambda e: e.timestamp)
        return entries
    
    def _setup_logging(self):
        """Setup Python logging."""
        self.logger = logging.getLogger("cortex.audit")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(component)s.%(operation)s: %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _setup_category_files(self):
        """Setup category-specific log files."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        for category in AuditCategory:
            category_file = self.log_dir / f"{self.session_id}_{category.value}.jsonl"
            self.category_files[category] = category_file
    
    def log(
        self,
        level: AuditLevel,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        duration_ms: Optional[float] = None
    ):
        """
        Log audit entry.
        
        Args:
            level: Audit level
            category: Event category
            component: Component name
            operation: Operation name
            message: Log message
            context: Operation context
            metadata: Additional metadata
            correlation_id: Correlation ID for tracking (auto-propagates from context)
            duration_ms: Operation duration in milliseconds
        """
        with self._lock:
            self.entry_count += 1
            
            # Determine correlation ID
            effective_correlation_id = correlation_id
            if not effective_correlation_id:
                # Check thread-local context first
                effective_correlation_id = self.get_current_correlation_id()
            if not effective_correlation_id and self.auto_generate_correlation:
                # Auto-generate if enabled
                effective_correlation_id = self._generate_correlation_id()
            
            # Build metadata with parent correlation if applicable
            effective_metadata = dict(metadata or {})
            if effective_correlation_id and "-CHILD-" in effective_correlation_id:
                parent_key = f"_parent_{effective_correlation_id}"
                parent_id = self._correlation_chains.get(parent_key)
                if parent_id:
                    effective_metadata["parent_correlation_id"] = parent_id
            
            entry = AuditEntry(
                timestamp=datetime.now().isoformat(),
                level=level,
                category=category,
                component=component,
                operation=operation,
                message=message,
                context=context or {},
                metadata=effective_metadata,
                correlation_id=effective_correlation_id,
                duration_ms=duration_ms
            )
            
            # Log to console via Python logging
            if self.enable_console:
                log_level = {
                    AuditLevel.TRACE: logging.DEBUG,
                    AuditLevel.INFO: logging.INFO,
                    AuditLevel.WARNING: logging.WARNING,
                    AuditLevel.ERROR: logging.ERROR,
                    AuditLevel.CRITICAL: logging.CRITICAL
                }[level]
                
                extra = {
                    'component': component,
                    'operation': operation
                }
                
                self.logger.log(log_level, message, extra=extra)
            
            # Write to category file
            if self.enable_file:
                self._write_to_file(entry)
    
    def _safe_json_serialize(self, obj: Any) -> Any:
        """
        Safely serialize object to JSON, handling circular references.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON-safe representation
        """
        seen = set()
        
        def _serialize(o: Any, depth: int = 0) -> Any:
            if depth > 50:  # Max recursion depth
                return "<max_depth_exceeded>"
            
            if id(o) in seen:
                return "<circular_reference>"
            
            if isinstance(o, dict):
                seen.add(id(o))
                return {k: _serialize(v, depth + 1) for k, v in o.items()}
            elif isinstance(o, (list, tuple)):
                seen.add(id(o))
                return [_serialize(i, depth + 1) for i in o]
            elif isinstance(o, (str, int, float, bool, type(None))):
                return o
            else:
                try:
                    return str(o)
                except Exception:
                    return "<unserializable>"
        
        return _serialize(obj)
    
    def _write_to_file(self, entry: AuditEntry):
        """Write entry to category-specific file."""
        category_file = self.category_files.get(entry.category)
        if not category_file:
            return
        
        try:
            # Handle circular references in context and metadata
            safe_entry = AuditEntry(
                timestamp=entry.timestamp,
                level=entry.level,
                category=entry.category,
                component=entry.component,
                operation=entry.operation,
                message=entry.message,
                context=self._safe_json_serialize(entry.context),
                metadata=self._safe_json_serialize(entry.metadata),
                correlation_id=entry.correlation_id,
                duration_ms=entry.duration_ms
            )
            with open(category_file, 'a') as f:
                f.write(safe_entry.to_json() + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write audit entry: {e}")
    
    def trace(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log trace-level entry."""
        self.log(AuditLevel.TRACE, category, component, operation, message, **kwargs)
    
    def info(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log info-level entry."""
        self.log(AuditLevel.INFO, category, component, operation, message, **kwargs)
    
    def warning(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log warning-level entry."""
        self.log(AuditLevel.WARNING, category, component, operation, message, **kwargs)
    
    def error(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log error-level entry."""
        self.log(AuditLevel.ERROR, category, component, operation, message, **kwargs)
    
    def critical(
        self,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """Log critical-level entry."""
        self.log(AuditLevel.CRITICAL, category, component, operation, message, **kwargs)
    
    def search(
        self,
        category: Optional[AuditCategory] = None,
        component: Optional[str] = None,
        operation: Optional[str] = None,
        level: Optional[AuditLevel] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditEntry]:
        """
        Search audit logs.
        
        Args:
            category: Filter by category
            component: Filter by component
            operation: Filter by operation
            level: Filter by level
            correlation_id: Filter by correlation ID
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of matching audit entries
        """
        results = []
        
        # Determine which files to search
        if category:
            files = [self.category_files[category]]
        else:
            files = list(self.category_files.values())
        
        for file_path in files:
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        entry_dict = json.loads(line.strip())
                        entry = AuditEntry(**entry_dict)
                        
                        # Apply filters
                        if component and entry.component != component:
                            continue
                        if operation and entry.operation != operation:
                            continue
                        if level and entry.level != level:
                            continue
                        if correlation_id and entry.correlation_id != correlation_id:
                            continue
                        
                        # Time range filter
                        entry_time = datetime.fromisoformat(entry.timestamp)
                        if start_time and entry_time < start_time:
                            continue
                        if end_time and entry_time > end_time:
                            continue
                        
                        results.append(entry)
            
            except Exception as e:
                self.logger.error(f"Failed to search {file_path}: {e}")
        
        return results
    
    # =========================================================================
    # AUDIT LOG ANALYSIS METHODS (Task 1.3.3)
    # =========================================================================
    
    def search_by_correlation(self, correlation_id: str) -> CorrelationSearchResult:
        """
        Search logs by correlation ID with enhanced metadata.
        
        Args:
            correlation_id: The correlation ID to search for
            
        Returns:
            CorrelationSearchResult with entries and metadata
        """
        entries = self.search(correlation_id=correlation_id)
        entries.sort(key=lambda e: e.timestamp)
        
        components = list(dict.fromkeys(e.component for e in entries))
        
        time_span_ms = 0.0
        first_ts = None
        last_ts = None
        
        if len(entries) >= 2:
            first_ts = entries[0].timestamp
            last_ts = entries[-1].timestamp
            first_time = datetime.fromisoformat(first_ts)
            last_time = datetime.fromisoformat(last_ts)
            time_span_ms = (last_time - first_time).total_seconds() * 1000
        elif len(entries) == 1:
            first_ts = last_ts = entries[0].timestamp
        
        return CorrelationSearchResult(
            correlation_id=correlation_id,
            total_entries=len(entries),
            entries=entries,
            time_span_ms=time_span_ms,
            components=components,
            first_timestamp=first_ts,
            last_timestamp=last_ts
        )
    
    def trace_start(
        self,
        correlation_id: str,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Start a trace for an operation.
        
        Args:
            correlation_id: The correlation ID for this trace
            operation: The operation being traced
            context: Input context for the operation
        """
        with self._lock:
            self._active_traces[correlation_id] = {
                "operation": operation,
                "start_time": datetime.now().isoformat(),
                "input_context": context or {}
            }
        
        self.info(
            category=AuditCategory.EXECUTION,
            component="trace",
            operation="trace_start",
            message=f"Started trace for {operation}",
            correlation_id=correlation_id,
            context=context
        )
    
    def trace_end(
        self,
        correlation_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ):
        """
        End a trace for an operation.
        
        Args:
            correlation_id: The correlation ID for this trace
            status: The final status (success, failure, etc.)
            result: Output result from the operation
        """
        with self._lock:
            if correlation_id in self._active_traces:
                self._active_traces[correlation_id]["end_time"] = datetime.now().isoformat()
                self._active_traces[correlation_id]["status"] = status
                self._active_traces[correlation_id]["output_result"] = result or {}
        
        self.info(
            category=AuditCategory.EXECUTION,
            component="trace",
            operation="trace_end",
            message=f"Ended trace with status: {status}",
            correlation_id=correlation_id,
            context=result,
            metadata={"status": status}
        )
    
    def get_trace(self, correlation_id: str) -> Optional[TraceResult]:
        """
        Get a complete trace for a correlation ID.
        
        Args:
            correlation_id: The correlation ID to get trace for
            
        Returns:
            TraceResult with full trace data, or None if not found
        """
        with self._lock:
            trace_data = self._active_traces.get(correlation_id)
        
        entries = self.search(correlation_id=correlation_id)
        entries.sort(key=lambda e: e.timestamp)
        
        if not entries:
            return None
        
        # Calculate duration
        start_time = trace_data.get("start_time") if trace_data else entries[0].timestamp
        end_time = trace_data.get("end_time") if trace_data else entries[-1].timestamp
        status = trace_data.get("status", "unknown") if trace_data else "unknown"
        input_context = trace_data.get("input_context", {}) if trace_data else {}
        output_result = trace_data.get("output_result", {}) if trace_data else {}
        
        duration_ms = 0.0
        if start_time and end_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration_ms = (end_dt - start_dt).total_seconds() * 1000
        
        return TraceResult(
            correlation_id=correlation_id,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            steps=entries,
            input_context=input_context,
            output_result=output_result
        )
    
    def get_error_summary(
        self,
        correlation_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> ErrorSummary:
        """
        Get error summary for a correlation ID or time range.
        
        Args:
            correlation_id: Filter by correlation ID
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            ErrorSummary with error statistics
        """
        entries = self.search(
            correlation_id=correlation_id,
            start_time=start_time,
            end_time=end_time
        )
        
        errors = [e for e in entries if e.level in (AuditLevel.ERROR, AuditLevel.CRITICAL)]
        error_types = list(set(
            e.context.get("error_type", "Unknown") 
            for e in errors 
            if e.context.get("error_type")
        ))
        
        error_rate = len(errors) / len(entries) if entries else 0.0
        
        return ErrorSummary(
            total_entries=len(entries),
            error_count=len(errors),
            error_rate=error_rate,
            errors=errors,
            error_types=error_types
        )
    
    def get_performance_metrics(
        self,
        correlation_id: Optional[str] = None,
        operation: Optional[str] = None,
        component: Optional[str] = None
    ) -> Optional[PerformanceMetrics]:
        """
        Get performance metrics for operations.
        
        Args:
            correlation_id: Filter by correlation ID
            operation: Filter by operation name
            component: Filter by component name
            
        Returns:
            PerformanceMetrics with statistics, or None if no data
        """
        entries = self.search(
            correlation_id=correlation_id,
            operation=operation,
            component=component,
            category=AuditCategory.PERFORMANCE
        )
        
        durations = [e.duration_ms for e in entries if e.duration_ms is not None]
        
        if not durations:
            return None
        
        durations.sort()
        
        def percentile(data: List[float], p: float) -> float:
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f + 1 < len(data) else f
            return data[f] + (k - f) * (data[c] - data[f]) if c != f else data[f]
        
        return PerformanceMetrics(
            operation=operation or "all",
            sample_count=len(durations),
            min_ms=min(durations),
            max_ms=max(durations),
            avg_ms=statistics.mean(durations),
            p50_ms=percentile(durations, 50),
            p95_ms=percentile(durations, 95),
            p99_ms=percentile(durations, 99)
        )
    
    def get_timeline(self, correlation_id: str) -> Optional[TimelineView]:
        """
        Get timeline view of operations for a correlation ID.
        
        Args:
            correlation_id: The correlation ID to get timeline for
            
        Returns:
            TimelineView with ordered events, or None if no data
        """
        entries = self.search(correlation_id=correlation_id)
        entries.sort(key=lambda e: e.timestamp)
        
        if not entries:
            return None
        
        events = [
            TimelineEvent(
                timestamp=e.timestamp,
                component=e.component,
                operation=e.operation,
                message=e.message,
                level=e.level
            )
            for e in entries
        ]
        
        # Calculate total duration
        total_duration_ms = 0.0
        if len(entries) >= 2:
            first_time = datetime.fromisoformat(entries[0].timestamp)
            last_time = datetime.fromisoformat(entries[-1].timestamp)
            total_duration_ms = (last_time - first_time).total_seconds() * 1000
        
        return TimelineView(
            events=events,
            total_duration_ms=total_duration_ms
        )
    
    # =========================================================================
    # PHASE/FEATURE GATE INTEGRATION (Task 1.3.4)
    # =========================================================================
    
    def phase_gate_check(
        self,
        feature_id: str,
        phase_id: int,
        gate_name: str,
        condition: Callable[[], bool],
        correlation_id: Optional[str] = None
    ) -> GateResult:
        """
        Check a phase gate and log the result.
        
        Args:
            feature_id: The feature being gated
            phase_id: The phase number
            gate_name: Name of the gate
            condition: Callable that returns True if gate passes
            correlation_id: Optional correlation ID
            
        Returns:
            GateResult with pass/fail status
        """
        try:
            passed = condition()
        except Exception as e:
            passed = False
            self.error(
                category=AuditCategory.VALIDATION,
                component="gate",
                operation="phase_gate_check",
                message=f"Gate condition failed with error: {e}",
                correlation_id=correlation_id,
                metadata={
                    "gate_name": gate_name,
                    "feature_id": feature_id,
                    "phase_id": phase_id,
                    "gate_passed": False,
                    "error": str(e)
                }
            )
            return GateResult(
                passed=False,
                gate_name=gate_name,
                feature_id=feature_id,
                phase_id=phase_id,
                message=f"Gate condition error: {e}"
            )
        
        level = AuditLevel.INFO if passed else AuditLevel.ERROR
        self.log(
            level=level,
            category=AuditCategory.VALIDATION,
            component="gate",
            operation="phase_gate_check",
            message=f"Phase gate '{gate_name}' {'passed' if passed else 'failed'}",
            correlation_id=correlation_id,
            metadata={
                "gate_name": gate_name,
                "feature_id": feature_id,
                "phase_id": phase_id,
                "gate_passed": passed
            }
        )
        
        return GateResult(
            passed=passed,
            gate_name=gate_name,
            feature_id=feature_id,
            phase_id=phase_id,
            message=f"Gate {'passed' if passed else 'failed'}"
        )
    
    def feature_gate_check(
        self,
        feature_id: str,
        gate_name: str,
        required_features: List[str],
        correlation_id: Optional[str] = None
    ) -> GateResult:
        """
        Check a feature gate and log the result.
        
        Args:
            feature_id: The feature being gated
            gate_name: Name of the gate
            required_features: List of features that must be complete
            correlation_id: Optional correlation ID
            
        Returns:
            GateResult with pass/fail status
        """
        # For now, just log that the gate was checked
        # In a full implementation, this would check actual feature completion status
        self.info(
            category=AuditCategory.VALIDATION,
            component="gate",
            operation="feature_gate_check",
            message=f"Feature gate '{gate_name}' checked for {feature_id}",
            correlation_id=correlation_id,
            metadata={
                "gate_name": gate_name,
                "feature_id": feature_id,
                "required_features": required_features
            }
        )
        
        return GateResult(
            passed=True,  # Placeholder - would check actual completion
            gate_name=gate_name,
            feature_id=feature_id,
            required_features=required_features
        )
    
    def audit_gate(
        self,
        gate_type: str,
        feature_id: str,
        phase_id: Optional[int] = None,
        gate_name: str = "default"
    ) -> Callable:
        """
        Decorator for automatic gate logging.
        
        Args:
            gate_type: Type of gate (phase, feature)
            feature_id: The feature being gated
            phase_id: Optional phase number
            gate_name: Name of the gate
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self.info(
                    category=AuditCategory.VALIDATION,
                    component=func.__name__,
                    operation=func.__name__,
                    message=f"Executing gated operation: {func.__name__}",
                    metadata={
                        "gate_type": gate_type,
                        "feature_id": feature_id,
                        "phase_id": phase_id,
                        "gate_name": gate_name
                    }
                )
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def audit_gate_condition(
        self,
        condition: Callable[[], bool],
        gate_name: str,
        on_fail: str = "skip"
    ) -> Callable:
        """
        Decorator that checks condition before execution.
        
        Args:
            condition: Callable that returns True if operation should proceed
            gate_name: Name of the gate
            on_fail: Action on failure ("skip", "raise", "warn")
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if condition():
                    return func(*args, **kwargs)
                else:
                    self.warning(
                        category=AuditCategory.VALIDATION,
                        component=func.__name__,
                        operation=func.__name__,
                        message=f"Operation skipped due to gate condition: {gate_name}",
                        metadata={
                            "gate_name": gate_name,
                            "on_fail": on_fail
                        }
                    )
                    if on_fail == "raise":
                        raise RuntimeError(f"Gate condition failed: {gate_name}")
                    return None
            return wrapper
        return decorator
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit log statistics."""
        stats = {
            "session_id": self.session_id,
            "total_entries": self.entry_count,
            "by_category": {},
            "by_level": {},
            "log_directory": str(self.log_dir)
        }
        
        # Count entries by category
        for category, file_path in self.category_files.items():
            if file_path.exists():
                with open(file_path, 'r') as f:
                    count = sum(1 for _ in f)
                stats["by_category"][category.value] = count
        
        return stats
    
    def export_session(self, output_file: str):
        """
        Export entire session to single file.
        
        Args:
            output_file: Output file path
        """
        all_entries = []
        
        for file_path in self.category_files.values():
            if not file_path.exists():
                continue
            
            with open(file_path, 'r') as f:
                for line in f:
                    all_entries.append(json.loads(line.strip()))
        
        # Sort by timestamp
        all_entries.sort(key=lambda e: e['timestamp'])
        
        # Write to output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "exported_at": datetime.now().isoformat(),
                "total_entries": len(all_entries),
                "entries": all_entries
            }, f, indent=2)
        
        self.logger.info(f"Exported {len(all_entries)} entries to {output_file}")


# Global audit logger instance
_audit_logger: Optional[EnterpriseAuditLogger] = None


def get_audit_logger() -> EnterpriseAuditLogger:
    """Get or create global audit logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = EnterpriseAuditLogger()
    return _audit_logger


def set_audit_logger(logger: EnterpriseAuditLogger):
    """Set global audit logger."""
    global _audit_logger
    _audit_logger = logger
