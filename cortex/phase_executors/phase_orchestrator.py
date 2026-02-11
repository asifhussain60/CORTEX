"""
Phase Orchestrator

Coordinates execution of multiple phases with proper governance.

Implements:
- CORE-038: File placement in proper module
- CORE-049: Silent autonomous execution
- Challenge Gate validation
- Registry state management
- Git commit coordination

AC-PHASE80-EXE-003: Phase Orchestrator
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PhaseOrchestrator:
    """
    Orchestrates execution of one or more phases.

    Responsibilities:
    - Validate phase dependencies
    - Execute phases sequentially
    - Manage registry state
    - Generate git commits
    - Report progress
    """

    def __init__(self, cortex_root: Path):
        """
        Initialize orchestrator.

        Args:
            cortex_root: Root path of CORTEX repository.
        """
        self.cortex_root = cortex_root
        self.registry_root = cortex_root / "cortex-registry" / "_cortex-master"
        self.execution_results: List[Dict[str, Any]] = []

    def execute_phase_sequence(self, phase_ids: List[str]) -> bool:
        """
        Execute a sequence of phases.

        Args:
            phase_ids: List of phase identifiers to execute.

        Returns:
            True if all phases succeeded, False otherwise.
        """
        logger.info(f"Starting phase sequence: {', '.join(phase_ids)}")

        for idx, phase_id in enumerate(phase_ids, 1):
            print(f"\n{'━'*70}")
            print(f"📋 Phase {phase_id}")
            print(f"{'━'*70}\n")

            # Import here to avoid circular imports
            from cortex.phase_executors.phase_executor_factory import (
                PhaseExecutorFactory,
            )

            factory = PhaseExecutorFactory(self.cortex_root)
            executor = factory.create_executor(phase_id)
            result = executor.execute()

            self.execution_results.append(result.__dict__)

            if result.status == "FAILED":
                logger.error(f"Phase {phase_id} FAILED: {result.error_message}")
                return False

            logger.info(f"Phase {phase_id} completed successfully")

        return True

    def report_summary(self) -> None:
        """Print execution summary."""
        if not self.execution_results:
            return

        print(f"\n{'━'*70}")
        print("✅ Execution Summary")
        print(f"{'━'*70}\n")

        total_tests = sum(r.get("tests_total", 0) for r in self.execution_results)
        total_passed = sum(r.get("tests_passed", 0) for r in self.execution_results)
        avg_coverage = (
            sum(r.get("coverage_percent", 0) for r in self.execution_results)
            / len(self.execution_results)
            if self.execution_results
            else 0.0
        )

        print(f"Phases executed: {len(self.execution_results)}")
        print(f"Total tests: {total_passed}/{total_tests} passing")
        print(f"Average coverage: {avg_coverage:.1f}%")
        print(f"Status: {'✅ ALL PASSED' if total_passed == total_tests else '⚠️ PARTIAL'}")
        print(f"\nTimestamp: {datetime.now().isoformat()}")
        print(f"{'━'*70}\n")

    def commit_results(self, message: str) -> Optional[str]:
        """
        Create git commit with execution results.

        Args:
            message: Commit message.

        Returns:
            Commit hash if successful, None otherwise.
        """
        try:
            # Stage changes
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.cortex_root,
                check=True,
                capture_output=True,
            )

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.cortex_root,
                check=True,
                capture_output=True,
                text=True,
            )

            # Extract commit hash
            output = result.stdout
            for line in output.split("\n"):
                if "[" in line and "]" in line:
                    start = line.find("[") + 1
                    end = line.find("]")
                    commit_hash = line[start:end].strip()
                    logger.info(f"Created commit: {commit_hash}")
                    return commit_hash

            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e.stderr}")
            return None

    def push_to_remote(self) -> bool:
        """
        Push changes to remote.

        Returns:
            True if successful, False otherwise.
        """
        try:
            subprocess.run(
                ["git", "push"],
                cwd=self.cortex_root,
                check=True,
                capture_output=True,
            )
            logger.info("Pushed changes to remote")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Git push failed: {e.stderr}")
            return False
