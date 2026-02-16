"""VacuumOrchestrator — Coordinator for cleaner plugin lifecycle.

This module implements the orchestrator pattern for vacuum operations,
managing cleaner registration, analysis, execution, and reporting.

Architecture:
    1. Register cleaners (plugins)
    2. Analyze repository (all cleaners scan)
    3. Execute cleanup (apply changes)
    4. Generate report (consolidated results)

State Machine:
    IDLE → ANALYZING → EXECUTING → COMPLETED
           ↓           ↓           ↓
         ERROR       ERROR       ERROR

Governance:
- CORE-008: TDD (tests drive implementation)
- CORE-011: Type hints 100%
- CORE-012: Google-style docstrings
- CORE-013: Specific exceptions only
- AC-VACUUM-REFACTOR-001: Orchestration layer

Author: CORTEX Architect
Phase: PHASE-VAC-001-05
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Type, Optional
import logging

from ..cleaners import (
    CleanerInterface,
    CleanerRegistry,
    Analysis,
    Report,
)


# =============================================================================
# STATE MANAGEMENT
# =============================================================================


class VacuumStrategy(Enum):
    """Vacuum strategy for cleaner configuration.
    
    Attributes:
        AGGRESSIVE: Delete all eligible files without confirmation
        CONSERVATIVE: Prompt for confirmation on deletions
        BALANCED: Delete known safe files, warn on others
    """

    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"


class OrchestratorState(Enum):
    """Orchestrator execution state."""

    IDLE = "idle"
    ANALYZING = "analyzing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class VacuumStats:
    """Statistics from vacuum operation (backward compatibility).

    Attributes:
        start_time: ISO 8601 timestamp of operation start
        end_time: ISO 8601 timestamp of operation end
        duration_seconds: Total execution time
        files_processed: Total files processed
        cleaners_used: Number of cleaners executed
        issues_fixed: Total issues fixed
        errors_encountered: Number of errors encountered
    """

    start_time: str
    end_time: str
    duration_seconds: float
    files_processed: int
    cleaners_used: int
    issues_fixed: int
    errors_encountered: int


@dataclass
class OrchestrationReport:
    """Consolidated report from all cleaners.

    Attributes:
        timestamp: ISO 8601 timestamp of orchestration
        state: Final orchestrator state
        status: Overall status (SUCCESS, FAILED, PARTIAL)
        cleaners_run: Number of cleaners executed
        total_actions: Total actions taken across all cleaners
        changes: Aggregated changes by type
        cleaner_reports: Individual reports from each cleaner
        errors: List of errors encountered
        duration_seconds: Total execution time
    """

    timestamp: str
    state: OrchestratorState
    status: str
    cleaners_run: int
    total_actions: int
    changes: Dict[str, int]
    cleaner_reports: List[Report] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0


# =============================================================================
# ORCHESTRATOR
# =============================================================================


class VacuumOrchestrator:
    """Coordinator for cleaner plugin lifecycle.

    The VacuumOrchestrator manages the complete vacuum workflow:
    1. Cleaner registration and configuration
    2. Repository analysis (all cleaners scan)
    3. Plan validation and approval
    4. Execution coordination
    5. Report aggregation and logging

    This class follows the orchestrator pattern, delegating actual
    cleanup work to registered cleaner plugins while coordinating
    the overall process.

    Attributes:
        config: Configuration dictionary for orchestrator
        registry: CleanerRegistry for plugin management
        state: Current orchestrator state
        logger: Python logger for operation logging
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize VacuumOrchestrator.

        Args:
            config: Configuration dictionary with keys:
                - repository_root or repo_root: Path to repository root
                - dry_run: If True, simulate without actual changes
                - log_level: Logging level (default: INFO)
        """
        self.config = config
        self.registry = CleanerRegistry()
        self.state = OrchestratorState.IDLE
        self.logger = logging.getLogger("cortex.vacuum.orchestrator")
        self.logger.setLevel(config.get("log_level", logging.INFO))

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate orchestrator configuration.

        Raises:
            ValueError: If required configuration is missing or invalid
        """
        # Accept both repository_root and repo_root for backward compatibility
        repo_root = self.config.get("repository_root") or self.config.get("repo_root")
        if not repo_root:
            raise ValueError("Configuration missing 'repository_root' or 'repo_root'")

        repo_path = Path(repo_root)
        if not repo_path.exists():
            raise ValueError(f"Repository root does not exist: {repo_path}")
        if not repo_path.is_dir():
            raise ValueError(f"Repository root is not a directory: {repo_path}")

    @property
    def dry_run(self) -> bool:
        """Get dry_run setting from config.

        Returns:
            True if dry_run is enabled, False otherwise
        """
        return self.config.get("dry_run", False)

    def register_cleaner(
        self,
        cleaner_class: Type[CleanerInterface],
        cleaner_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a cleaner plugin.

        Args:
            cleaner_class: Cleaner class to instantiate
            cleaner_config: Optional configuration for the cleaner

        Raises:
            TypeError: If cleaner_class is not a CleanerInterface subclass
        """
        if not issubclass(cleaner_class, CleanerInterface):
            raise TypeError(
                f"Cleaner must inherit from CleanerInterface, got {cleaner_class}"
            )

        # Merge orchestrator config with cleaner-specific config
        config = {**self.config, **(cleaner_config or {})}

        # Instantiate and register
        cleaner = cleaner_class(config)
        self.registry.register(cleaner)

        self.logger.info(
            f"Registered cleaner: {cleaner.name} v{cleaner.version} "
            f"(domain: {cleaner.domain})"
        )

    def list_cleaners(self) -> List[str]:
        """List all registered cleaner domains.

        Returns:
            List of cleaner domain names
        """
        return self.registry.list_domains()

    def has_cleaner(self, domain: str) -> bool:
        """Check if cleaner is registered.

        Args:
            domain: Cleaner domain name

        Returns:
            True if cleaner is registered, False otherwise
        """
        return self.registry.has(domain)

    def get_cleaner(self, domain: str) -> CleanerInterface:
        """Get registered cleaner by domain.

        Args:
            domain: Cleaner domain name

        Returns:
            CleanerInterface instance

        Raises:
            KeyError: If cleaner not registered
        """
        return self.registry.get(domain)

    def analyze(self) -> Dict[str, Analysis]:
        """Run analysis phase across all registered cleaners.

        Returns:
            Dictionary mapping cleaner domain to Analysis result

        Raises:
            RuntimeError: If no cleaners are registered
        """
        if not self.registry.list_domains():
            raise RuntimeError("No cleaners registered")

        self.state = OrchestratorState.ANALYZING
        self.logger.info(
            f"Starting analysis with {len(self.registry.list_domains())} cleaners"
        )

        analyses = {}
        for domain in self.registry.list_domains():
            cleaner = self.registry.get(domain)
            self.logger.info(f"Analyzing with {cleaner.name}...")

            try:
                analysis = cleaner.analyze()
                analyses[domain] = analysis
                self.logger.info(
                    f"  {cleaner.name}: {analysis.files_scanned} files scanned, "
                    f"{analysis.issues_found} issues found"
                )
            except Exception as e:
                self.logger.error(f"Analysis failed for {cleaner.name}: {e}")
                self.state = OrchestratorState.ERROR
                raise

        self.logger.info(f"Analysis complete: {len(analyses)} cleaners")
        return analyses

    def execute(
        self, analyses: Dict[str, Analysis], dry_run: Optional[bool] = None
    ) -> OrchestrationReport:
        """Execute cleanup operations based on analyses.

        Args:
            analyses: Dictionary of analyses from analyze() phase
            dry_run: Override config dry_run setting (optional)

        Returns:
            OrchestrationReport with consolidated results

        Raises:
            RuntimeError: If orchestrator state is not valid for execution
        """
        if self.state not in (OrchestratorState.ANALYZING, OrchestratorState.IDLE):
            raise RuntimeError(
                f"Cannot execute from state {self.state.value}. "
                "Run analyze() first."
            )

        is_dry_run = dry_run if dry_run is not None else self.config.get("dry_run", False)
        self.state = OrchestratorState.EXECUTING

        start_time = datetime.now()
        self.logger.info(
            f"Starting execution (dry_run={is_dry_run}) "
            f"for {len(analyses)} cleaners"
        )

        reports: List[Report] = []
        errors: List[str] = []
        total_actions = 0
        changes: Dict[str, int] = {}

        # Execute each cleaner
        for domain, analysis in analyses.items():
            cleaner = self.registry.get(domain)
            self.logger.info(f"Executing {cleaner.name}...")

            try:
                # Execute with dry_run override
                report = cleaner.execute(analysis.plan)
                reports.append(report)

                # Aggregate metrics
                total_actions += report.actions_taken
                for change_type, count in report.changes.items():
                    changes[change_type] = changes.get(change_type, 0) + count

                self.logger.info(
                    f"  {cleaner.name}: {report.status}, "
                    f"{report.actions_taken} actions"
                )

                if report.errors:
                    errors.extend(report.errors)

            except Exception as e:
                error_msg = f"Execution failed for {cleaner.name}: {e}"
                self.logger.error(error_msg)
                errors.append(error_msg)

        # Determine overall status
        if not errors:
            status = "SUCCESS"
            self.state = OrchestratorState.COMPLETED
        elif len(errors) == len(analyses):
            status = "FAILED"
            self.state = OrchestratorState.ERROR
        else:
            status = "PARTIAL"
            self.state = OrchestratorState.COMPLETED

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.logger.info(
            f"Execution complete: {status}, {total_actions} total actions "
            f"in {duration:.2f}s"
        )

        return OrchestrationReport(
            timestamp=datetime.now().isoformat(),
            state=self.state,
            status=status,
            cleaners_run=len(reports),
            total_actions=total_actions,
            changes=changes,
            cleaner_reports=reports,
            errors=errors,
            duration_seconds=duration,
        )

    def run(self, dry_run: Optional[bool] = None) -> OrchestrationReport:
        """Run complete vacuum cycle: analyze → execute → report.

        This is the main entry point for vacuum operations. It coordinates
        the full lifecycle: analysis, execution, and reporting.

        Args:
            dry_run: If True, simulate without actual changes (optional)

        Returns:
            OrchestrationReport with consolidated results

        Raises:
            RuntimeError: If no cleaners are registered
        """
        self.logger.info("Starting vacuum orchestration cycle")

        try:
            # Phase 1: Analyze
            analyses = self.analyze()

            # Phase 2: Execute
            report = self.execute(analyses, dry_run=dry_run)

            # Phase 3: Log summary
            self._log_summary(report)

            return report

        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            self.state = OrchestratorState.ERROR
            raise

    def _log_summary(self, report: OrchestrationReport) -> None:
        """Log orchestration summary.

        Args:
            report: OrchestrationReport to summarize
        """
        self.logger.info("=" * 60)
        self.logger.info("VACUUM ORCHESTRATION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Status: {report.status}")
        self.logger.info(f"Cleaners Run: {report.cleaners_run}")
        self.logger.info(f"Total Actions: {report.total_actions}")
        self.logger.info(f"Duration: {report.duration_seconds:.2f}s")

        if report.changes:
            self.logger.info("Changes:")
            for change_type, count in sorted(report.changes.items()):
                self.logger.info(f"  {change_type}: {count}")

        if report.errors:
            self.logger.warning(f"Errors encountered: {len(report.errors)}")
            for error in report.errors:
                self.logger.warning(f"  - {error}")

        self.logger.info("=" * 60)
