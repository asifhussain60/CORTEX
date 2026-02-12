"""Cleaner Plugin Interface - Abstract Base for VacuumOrchestrator Cleaners

This module defines the abstract interface that all VacuumOrchestrator cleaners
must implement. Follows SOLID principles for extensibility.

SOLID Compliance:
- Single Responsibility: Each cleaner handles one domain
- Open/Closed: New cleaners without modifying orchestrator
- Liskov Substitution: All cleaners interchangeable via interface
- Interface Segregation: Minimal required methods
- Dependency Inversion: Orchestrator depends on abstraction

Author: CORTEX Builder
Phase: PHASE-VAC-001-01
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Analysis:
    """Result of analyze() phase - non-destructive intelligence gathering.

    Attributes:
        cleaner_id: Identifier of the cleaner that performed analysis
        timestamp: ISO-8601 timestamp when analysis ran
        files_scanned: Total number of files examined
        issues_found: Number of issues detected
        plan: Execution plan describing what will change
        logs: Detailed analysis logs
    """

    cleaner_id: str
    timestamp: str
    files_scanned: int
    issues_found: int
    plan: Dict[str, Any]
    logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of analysis
        """
        return {
            'cleaner_id': self.cleaner_id,
            'timestamp': self.timestamp,
            'files_scanned': self.files_scanned,
            'issues_found': self.issues_found,
            'plan': self.plan,
            'logs': self.logs,
        }


@dataclass
class Report:
    """Result of execute() phase - execution outcome with changes.

    Attributes:
        cleaner_id: Identifier of the cleaner that executed
        timestamp: ISO-8601 timestamp when execution ran
        status: Execution status ('SUCCESS', 'FAILED', 'PARTIAL', 'DRY_RUN')
        actions_taken: Number of changes made
        changes: Dictionary describing what actually changed
        errors: List of any errors encountered
        logs: Detailed execution logs
    """

    cleaner_id: str
    timestamp: str
    status: str  # 'SUCCESS', 'FAILED', 'PARTIAL', 'DRY_RUN'
    actions_taken: int
    changes: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of report
        """
        return {
            'cleaner_id': self.cleaner_id,
            'timestamp': self.timestamp,
            'status': self.status,
            'actions_taken': self.actions_taken,
            'changes': self.changes,
            'errors': self.errors,
            'logs': self.logs,
        }

    @property
    def is_success(self) -> bool:
        """Check if execution was successful.

        Returns:
            True if status is SUCCESS
        """
        return self.status == 'SUCCESS'

    @property
    def is_failed(self) -> bool:
        """Check if execution failed.

        Returns:
            True if status is FAILED
        """
        return self.status == 'FAILED'


@dataclass
class RollbackResult:
    """Result of rollback() phase - restoration outcome.

    Attributes:
        cleaner_id: Identifier of the cleaner that performed rollback
        timestamp: ISO-8601 timestamp when rollback ran
        status: Rollback status ('SUCCESS', 'FAILED')
        files_restored: Number of files restored from snapshot
        errors: List of any errors during rollback
    """

    cleaner_id: str
    timestamp: str
    status: str  # 'SUCCESS', 'FAILED'
    files_restored: int
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of rollback result
        """
        return {
            'cleaner_id': self.cleaner_id,
            'timestamp': self.timestamp,
            'status': self.status,
            'files_restored': self.files_restored,
            'errors': self.errors,
        }

    @property
    def is_success(self) -> bool:
        """Check if rollback was successful.

        Returns:
            True if status is SUCCESS
        """
        return self.status == 'SUCCESS'


class CleanerInterface(ABC):
    """Abstract base for all VacuumOrchestrator cleaners.

    All cleaner plugins MUST implement this interface to be registered with
    VacuumOrchestrator. This ensures SOLID compliance and consistent behavior.

    SOLID Principles Enforced:
    - Single Responsibility: Each cleaner handles one specific domain
    - Open/Closed: New cleaners added WITHOUT modifying orchestrator code
    - Liskov Substitution: All cleaners interchangeable via this interface
    - Interface Segregation: Minimal required methods (analyze, execute, rollback)
    - Dependency Inversion: VacuumOrchestrator depends on this abstraction

    Plugin Lifecycle:
    1. analyze() - Scan and gather intelligence (NON-DESTRUCTIVE)
    2. execute(plan) - Apply changes with snapshot support
    3. rollback() - Restore from snapshot if needed

    Example:
        ```python
        cleaner = MDOrganizerCleaner(config)
        analysis = cleaner.analyze()
        print(f"Found {analysis.issues_found} issues")

        report = cleaner.execute(analysis.plan)
        if report.is_failed:
            result = cleaner.rollback()
        ```

    Type Hints: All parameters and return types are fully typed (CORE-011)
    Docstrings: All public methods have Google-style docstrings (CORE-012)
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize cleaner with configuration.

        Args:
            config: Cleaner-specific configuration dictionary

        Raises:
            ValueError: If required configuration keys are missing
        """
        self.config: Dict[str, Any] = config
        self.cleaner_id: str = self.__class__.__name__
        self.logger: logging.Logger = self._setup_logger()
        self._log(f"Initialized {self.name} (v{self.version})")

    @abstractmethod
    def analyze(self) -> Analysis:
        """Non-destructive analysis phase.

        Scan repository to:
        1. Identify items to clean
        2. Detect dependencies/cross-references
        3. Plan execution strategy
        4. Estimate impact

        Returns:
            Analysis: Detailed analysis result with execution plan

        Guarantees:
            - MUST NOT modify any files (read-only)
            - MUST be deterministic (same input → same output)
            - MUST complete in reasonable time (<60 seconds)
            - MUST log all findings

        Raises:
            Exception: Subclasses may raise domain-specific exceptions
        """
        pass

    @abstractmethod
    def execute(self, plan: Dict[str, Any]) -> Report:
        """Controlled execution phase.

        Apply changes per provided plan:
        1. Create pre-execution snapshot
        2. Apply changes with detailed logging
        3. Verify final state
        4. Enable rollback capability

        Args:
            plan: Execution plan from analyze() phase

        Returns:
            Report: Detailed execution result

        Guarantees:
            - MUST create snapshot before modifications
            - MUST log all changes with timestamp
            - MUST verify final state after changes
            - MUST support rollback() to restore pre-execution state

        Raises:
            Exception: Subclasses may raise domain-specific exceptions
        """
        pass

    @abstractmethod
    def rollback(self) -> RollbackResult:
        """Rollback to pre-execution state.

        Restore repository from snapshot:
        1. Verify snapshot exists and is valid
        2. Restore all files from snapshot
        3. Verify restoration completed correctly
        4. Clean up snapshot resources

        Returns:
            RollbackResult: Rollback operation result

        Guarantees:
            - MUST verify snapshot integrity before restore
            - MUST handle partial failures gracefully
            - MUST log all restore operations
            - MUST clean up after restoration

        Raises:
            Exception: Subclasses may raise domain-specific exceptions
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable cleaner name.

        Returns:
            str: Display name (e.g., "MD Organizer", "Python Cache Cleaner")
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Cleaner version string.

        Returns:
            str: Version in semver format (e.g., "1.0.0")
        """
        pass

    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain this cleaner operates on.

        Used for:
        - Configuration resolution (cortex_brain/tier1/orchestrators/cleaners/<domain>/config.yaml)
        - Logging and identification
        - Dependency management

        Returns:
            str: Domain identifier (e.g., "md_docs", "python_cache", "backups")
        """
        pass

    def _setup_logger(self) -> logging.Logger:
        """Setup cleaner-specific logger.

        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger(self.cleaner_id)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{self.cleaner_id}] %(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _log(self, message: str, level: str = 'INFO') -> None:
        """Log message with consistent formatting.

        Args:
            message: Message to log
            level: Log level ('INFO', 'WARNING', 'ERROR', 'DEBUG')
        """
        if level == 'DEBUG':
            self.logger.debug(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        else:
            self.logger.info(message)

    def __repr__(self) -> str:
        """String representation of cleaner.

        Returns:
            String describing cleaner identity
        """
        return f"{self.cleaner_id}(name={self.name}, version={self.version}, domain={self.domain})"
