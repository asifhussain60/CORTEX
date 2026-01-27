"""VacuumOrchestrator - Repository Maintenance Orchestrator

Coordinates cleaner plugins to manage repository maintenance tasks.
Provides a framework for discovering, registering, and executing cleaners
against a repository with support for analysis, execution, and rollback.

Architecture:
- Cleaner Registry: Plugin discovery and management
- State Tracking: Monitor analysis/execution progress
- Configuration: Load settings from vacuum/config.yaml
- Reporting: Aggregate results across cleaners

SOLID Principles:
- Single Responsibility: Only orchestrates cleaner execution
- Open/Closed: New cleaners added without modification
- Liskov Substitution: All cleaners implement CleanerInterface
- Interface Segregation: Minimal orchestrator interface
- Dependency Inversion: Depends on CleanerInterface abstraction

Author: CORTEX Builder
Phase: PHASE-VAC-001-04
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
import yaml

# Import cleaner interface and registry
from tier1.orchestrators.cleaners import (
    CleanerInterface,
    CleanerRegistry,
    Analysis,
    Report,
    RollbackResult,
)


# =============================================================================
# ORCHESTRATOR STATE & REPORTING
# =============================================================================


@dataclass
class OrchestratorState:
    """Track orchestrator state and execution history.

    Tracks which cleaners have analyzed/executed and their results.

    Attributes:
        timestamp: When state was created
        completed_analyses: Dict of cleaner_id → Analysis results
        completed_executions: Dict of cleaner_id → Report results
        pending_rollbacks: List of cleaner_ids with pending rollbacks
    """

    timestamp: str
    completed_analyses: Dict[str, Analysis]
    completed_executions: Dict[str, Report]
    pending_rollbacks: List[str]

    def __init__(self) -> None:
        """Initialize orchestrator state."""
        self.timestamp = datetime.now().isoformat()
        self.completed_analyses = {}
        self.completed_executions = {}
        self.pending_rollbacks = []


@dataclass
class OrchestrationReport:
    """Report of orchestration activities.

    Aggregates results from all cleaner invocations during orchestration.

    Attributes:
        timestamp: Report generation timestamp
        overall_status: SUCCESS, FAILED, or PARTIAL
        analyses_completed: Count of completed analyses
        executions_completed: Count of completed executions
        analyses: List of Analysis results
        reports: List of Report results
        errors: Aggregated error list
    """

    timestamp: str
    overall_status: str
    analyses_completed: int
    executions_completed: int
    analyses: List[Analysis]
    reports: List[Report]
    errors: List[str]


# =============================================================================
# VACUUM ORCHESTRATOR
# =============================================================================


class VacuumOrchestrator:
    """Main orchestrator for repository maintenance.

    Manages cleaner plugin lifecycle: discovery, configuration, execution,
    and rollback. Provides a unified interface for coordinating multiple
    cleaners on a repository.

    Attributes:
        config: Configuration dictionary
        registry: CleanerRegistry for plugin management
        state: OrchestratorState tracking execution progress
        dry_run: If True, don't actually modify files
        repo_root: Root path of repository being maintained
        logger: Logger for orchestration events

    Usage:
        ```python
        orchestrator = VacuumOrchestrator(config={
            "repo_root": "/path/to/repo",
            "dry_run": False
        })

        orchestrator.register_cleaner(MDOrganizerCleaner, {})
        analysis = orchestrator.analyze("md_organizer")
        report = orchestrator.execute("md_organizer", analysis.plan)
        ```
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize VacuumOrchestrator.

        Args:
            config: Configuration dictionary with keys:
                - repo_root: Repository root path
                - dry_run: If True, don't modify files (default: False)
                - config_file: Path to vacuum config (default: cortex_brain/vacuum/config.yaml)
                - verbose: If True, enable verbose logging (default: False)

        Raises:
            ValueError: If repo_root not provided or invalid
        """
        self.config = config
        self.registry = CleanerRegistry()
        self.state = OrchestratorState()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cleaner_configs: Dict[str, Dict[str, Any]] = {}

        # Configuration
        self.repo_root = Path(config.get("repo_root", "."))
        self.dry_run = config.get("dry_run", False)
        self.config_file = config.get("config_file", "cortex_brain/vacuum/config.yaml")
        self.verbose = config.get("verbose", False)

        # Load configuration if file exists
        self._load_vacuum_config()

        # Set logging level
        if self.verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.logger.info(f"Initialized VacuumOrchestrator (repo_root={self.repo_root})")

    def _load_vacuum_config(self) -> None:
        """Load vacuum configuration from YAML file.

        Loads cleaner configurations and file classification rules from
        the vacuum/config.yaml file if it exists.

        Raises:
            ValueError: If config file is invalid YAML
        """
        config_path = self.repo_root / self.config_file
        if not config_path.exists():
            self.logger.warning(f"Config file not found: {config_path}")
            return

        try:
            with open(config_path, "r") as f:
                vacuum_config = yaml.safe_load(f) or {}
            self.logger.debug(f"Loaded vacuum config from {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {config_path}: {str(e)}") from e

    def register_cleaner(
        self, cleaner_class: type, cleaner_config: Dict[str, Any]
    ) -> None:
        """Register a cleaner plugin.

        Registers a cleaner class with the registry and stores its
        configuration for later instantiation.

        Args:
            cleaner_class: Cleaner class (must implement CleanerInterface)
            cleaner_config: Configuration dictionary for this cleaner

        Raises:
            ValueError: If cleaner doesn't implement CleanerInterface
        """
        try:
            # Register with registry (this will determine domain)
            self.registry.register_cleaner(cleaner_class)
            
            # Get domain from the class
            temp_instance = cleaner_class({})
            domain = temp_instance.domain
            
            # Store config for later use
            self._cleaner_configs[domain] = cleaner_config
            
            self.logger.info(f"Registered cleaner: {cleaner_class.__name__}")
        except Exception as e:
            self.logger.error(f"Failed to register cleaner: {str(e)}")
            raise

    def has_cleaner(self, domain: str) -> bool:
        """Check if a cleaner is registered.

        Args:
            domain: Cleaner domain identifier

        Returns:
            True if cleaner is registered, False otherwise
        """
        return self.registry.has_cleaner(domain)

    def get_cleaner(self, domain: str) -> CleanerInterface:
        """Get a registered cleaner instance.

        Args:
            domain: Cleaner domain identifier

        Returns:
            CleanerInterface instance

        Raises:
            ValueError: If cleaner not registered
        """
        config = self._cleaner_configs.get(domain, {})
        return self.registry.get_cleaner(domain, config=config)

    def list_cleaners(self) -> List[str]:
        """List all registered cleaner domains.

        Returns:
            List of domain identifiers for registered cleaners
        """
        return self.registry.list_all()

    def analyze(self, domain: str) -> Analysis:
        """Execute analysis phase for a cleaner.

        Calls the cleaner's analyze() method to scan the repository
        and generate a migration/maintenance plan.

        Args:
            domain: Cleaner domain identifier

        Returns:
            Analysis dataclass with scan results and plan

        Raises:
            ValueError: If cleaner not registered
        """
        self.logger.info(f"Starting analysis phase for {domain}")

        try:
            cleaner = self.get_cleaner(domain)
            analysis = cleaner.analyze()

            # Track in state
            self.state.completed_analyses[domain] = analysis

            self.logger.info(
                f"Analysis complete: {analysis.files_scanned} files scanned, "
                f"{analysis.issues_found} issues found"
            )

            return analysis

        except Exception as e:
            self.logger.error(f"Analysis failed for {domain}: {str(e)}")
            raise

    def execute(self, domain: str, plan: Dict[str, Any]) -> Report:
        """Execute modification phase for a cleaner.

        Calls the cleaner's execute() method to apply the migration/maintenance
        plan. If dry_run is enabled, execution is simulated.

        Args:
            domain: Cleaner domain identifier
            plan: Execution plan from analysis phase

        Returns:
            Report dataclass with execution results

        Raises:
            ValueError: If cleaner not registered
        """
        self.logger.info(f"Starting execution phase for {domain}")

        try:
            cleaner = self.get_cleaner(domain)

            # Respect dry_run setting
            if self.dry_run:
                self.logger.info(f"DRY RUN: Not executing changes for {domain}")
                cleaner.dry_run = True

            report = cleaner.execute(plan)

            # Track in state
            self.state.completed_executions[domain] = report

            # Mark for potential rollback
            if report.status == "SUCCESS":
                self.state.pending_rollbacks.append(domain)

            self.logger.info(
                f"Execution complete: {report.actions_taken} actions, "
                f"status={report.status}"
            )

            return report

        except Exception as e:
            self.logger.error(f"Execution failed for {domain}: {str(e)}")
            raise

    def rollback(self, domain: str) -> RollbackResult:
        """Execute rollback phase for a cleaner.

        Calls the cleaner's rollback() method to restore the repository
        to its pre-execution state using the saved snapshot.

        Args:
            domain: Cleaner domain identifier

        Returns:
            RollbackResult dataclass with restoration info

        Raises:
            ValueError: If cleaner not registered
        """
        self.logger.info(f"Starting rollback phase for {domain}")

        try:
            cleaner = self.get_cleaner(domain)
            result = cleaner.rollback()

            # Remove from pending rollbacks
            if domain in self.state.pending_rollbacks:
                self.state.pending_rollbacks.remove(domain)

            self.logger.info(
                f"Rollback complete: {result.files_restored} files restored, "
                f"status={result.status}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Rollback failed for {domain}: {str(e)}")
            raise

    def generate_report(self) -> OrchestrationReport:
        """Generate comprehensive orchestration report.

        Aggregates results from all analysis and execution phases into
        a single report summarizing orchestrator activities.

        Returns:
            OrchestrationReport with aggregated results
        """
        self.logger.info("Generating orchestration report")

        # Determine overall status
        if not self.state.completed_executions:
            overall_status = "NO_EXECUTIONS"
        elif all(
            report.status == "SUCCESS"
            for report in self.state.completed_executions.values()
        ):
            overall_status = "SUCCESS"
        elif all(
            report.status in ["SUCCESS", "PARTIAL"]
            for report in self.state.completed_executions.values()
        ):
            overall_status = "PARTIAL"
        else:
            overall_status = "FAILED"

        # Aggregate errors
        errors: List[str] = []
        for report in self.state.completed_executions.values():
            errors.extend(report.errors)

        report = OrchestrationReport(
            timestamp=datetime.now().isoformat(),
            overall_status=overall_status,
            analyses_completed=len(self.state.completed_analyses),
            executions_completed=len(self.state.completed_executions),
            analyses=list(self.state.completed_analyses.values()),
            reports=list(self.state.completed_executions.values()),
            errors=errors,
        )

        self.logger.info(
            f"Report generated: {report.analyses_completed} analyses, "
            f"{report.executions_completed} executions, "
            f"overall_status={report.overall_status}"
        )

        return report


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "VacuumOrchestrator",
    "OrchestratorState",
    "OrchestrationReport",
]
