"""Health-Vacuum Unified Pipeline

Canonical health scanning and vacuum remediation for CORTEX.

Architecture:
- HealthOrchestrator: Holistic scanner (filesystem + agents)
- VacuumOrchestrator: Standalone + companion remediation engine
- HealthVacuumPipeline: 5-stage coordinator
- Agents: Pluggable health detectors (BaseHealthAgent ABC)
- Models: Shared value objects (ScanResult, VacuumReport, etc.)
- FileContext: Single-walk filesystem snapshot

Author: CORTEX Framework
Phase: PHASE-51  (supersedes PHASE-92)
CORE Rules: CORE-008, CORE-011, CORE-012, CORE-028, CORE-035
"""

# Foundation (Stage 1)
from .constants import (
    EXCLUDED_DIRS,
    PROTECTED_FILES,
    PROTECTED_ROOT_EXTENSIONS,
    ALLOWED_MARKDOWN_PREFIXES,
    KEBAB_MAX_LEN,
    ARCHIVE_DIR,
    HANDOFF_FILENAME,
    ROLLBACK_FILENAME,
)
from .models import (
    IssueSeverity,
    IssueFile,
    NamingViolation,
    ScanResult,
    OperationResult,
    VacuumReport,
    PipelineReport,
)
from .file_context import FileContext
from .naming import (
    to_kebab_case,
    to_snake_case,
    is_screaming,
    is_valid_python_name,
    classify_naming_violation,
)

# Orchestrators (Stage 2-4)
from .health_orchestrator import HealthOrchestrator
from .vacuum_orchestrator import VacuumOrchestrator
from .pipeline import HealthVacuumPipeline

# Existing agent infrastructure
from .agents.base_agent import BaseHealthAgent, HealthIssue, HealthCheckResult
from .reports.health_report import HealthReport, HealthMetrics

__all__ = [
    # Foundation
    "EXCLUDED_DIRS",
    "PROTECTED_FILES",
    "PROTECTED_ROOT_EXTENSIONS",
    "ALLOWED_MARKDOWN_PREFIXES",
    "KEBAB_MAX_LEN",
    "ARCHIVE_DIR",
    "HANDOFF_FILENAME",
    "ROLLBACK_FILENAME",
    "IssueSeverity",
    "IssueFile",
    "NamingViolation",
    "ScanResult",
    "OperationResult",
    "VacuumReport",
    "PipelineReport",
    "FileContext",
    "to_kebab_case",
    "to_snake_case",
    "is_screaming",
    "is_valid_python_name",
    "classify_naming_violation",
    # Orchestrators
    "HealthOrchestrator",
    "VacuumOrchestrator",
    "HealthVacuumPipeline",
    # Agents
    "BaseHealthAgent",
    "HealthIssue",
    "HealthCheckResult",
    "HealthReport",
    "HealthMetrics",
]

__version__ = "2.0.0"
