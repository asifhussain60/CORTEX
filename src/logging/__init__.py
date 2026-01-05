"""
Enterprise audit logging system for CORTEX.

Provides:
- Async audit logging with buffering
- Structured JSONL format
- Automatic rotation and compression
- Sensitive data redaction
- Context propagation
- Self-healing capabilities with pattern detection
- Health check and monitoring system
- Orchestrator integration layer
"""

from .audit_logger import AuditLogger, LogLevel
from .log_buffer import LogBuffer
from .log_writer import LogWriter
from .self_healing_engine import (
    SelfHealingEngine,
    PatternDetector,
    AnomalyDetector,
    ErrorCluster,
    RecoveryStrategy
)
from .pattern_detector import DetectedPattern, PerformanceDegradation
from .anomaly_detector import Anomaly, ThresholdViolation, RateAnomaly
from .health_check import HealthCheckSystem
from .integration import AuditedOrchestrator, OrchestratorHealthCheck

__all__ = [
    # Core logging
    "AuditLogger",
    "LogLevel",
    "LogBuffer",
    "LogWriter",
    # Self-healing
    "SelfHealingEngine",
    "PatternDetector",
    "AnomalyDetector",
    "ErrorCluster",
    "RecoveryStrategy",
    # Data classes
    "DetectedPattern",
    "PerformanceDegradation",
    "Anomaly",
    "ThresholdViolation",
    "RateAnomaly",
    # Health & Monitoring
    "HealthCheckSystem",
    # Integration
    "AuditedOrchestrator",
    "OrchestratorHealthCheck"
]
