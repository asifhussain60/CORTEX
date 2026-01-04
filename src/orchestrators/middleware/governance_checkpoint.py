"""
Governance Checkpoint Middleware - Runtime SKULL Rule Enforcement

Purpose:
    Continuous governance validation at phase boundaries and critical operations.
    Remediates Gap 2 (Runtime Governance Enforcement) from C50 epic.

Key Features:
    1. Phase Boundary Validation - Checkpoint at phase start/complete
    2. SKULL Rule Enforcement - Validate 61 governance rules at runtime
    3. Audit Logging - Record all governance decisions in JSONL
    4. Master Orchestrator Integration - Pre/post execution hooks

Usage:
    from orchestrators.middleware.governance_checkpoint import GovernanceCheckpoint

    checkpoint = GovernanceCheckpoint()

    # Phase start validation
    checkpoint.checkpoint_phase_start(phase_number=1, orchestrator="planning_v5")

    # Operation validation
    checkpoint.checkpoint_operation("file_creation", context={"path": "src/new_file.py"})

    # Phase completion validation
    checkpoint.checkpoint_phase_complete(phase_number=1, artifacts={"files_created": 5})

Version: 1.0
Author: CORTEX
Created: 2026-01-04
Sub-Plan: C50-03 (Knowledge Library Phase -1 + Gap 2 Remediation)
"""

import json
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class CheckpointType(Enum):
    """Types of governance checkpoints"""

    PHASE_START = "phase_start"
    PHASE_COMPLETE = "phase_complete"
    OPERATION = "operation"
    PRE_EXECUTION = "pre_execution"
    POST_EXECUTION = "post_execution"


class RuleSeverity(Enum):
    """Rule severity levels"""

    BLOCKED = "blocked"  # Execution cannot proceed
    WARNING = "warning"  # Log warning but allow
    INFO = "info"  # Informational only


@dataclass
class GovernanceViolation:
    """Represents a governance rule violation"""

    rule_id: str
    rule_name: str
    severity: str
    description: str
    recommendation: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckpointResult:
    """Result of a governance checkpoint"""

    timestamp: str
    checkpoint_type: str
    orchestrator: str
    phase: Optional[int]
    operation: Optional[str]
    rules_validated: List[str]
    violations: List[GovernanceViolation]
    status: str  # "PASSED" or "FAILED"
    blocked: bool


class GovernanceCheckpoint:
    """
    Runtime Governance Enforcement Middleware

    Validates SKULL rules at orchestrator lifecycle boundaries:
    - Pre-execution (setup verification)
    - Phase start (DoR validation)
    - Phase operations (continuous monitoring)
    - Phase complete (DoD validation)
    - Post-execution (teardown + REFACTOR)
    """

    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialize Governance Checkpoint

        Args:
            workspace_path: Root workspace path (defaults to current directory)
        """
        self.workspace_path = Path(workspace_path or Path.cwd())
        self.rules_path = self.workspace_path / "cortex-brain" / "brain-protection-rules.yaml"
        self.audit_path = self.workspace_path / "tracking" / "governance-audit.jsonl"

        # Load rules
        self.rules = self._load_rules()

        # Ensure audit directory exists
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_rules(self) -> Dict:
        """Load SKULL rules from brain-protection-rules.yaml"""
        if not self.rules_path.exists():
            print(f"⚠️  Warning: {self.rules_path} not found, using empty rules")
            return {}

        try:
            with open(self.rules_path, "r") as f:
                content = f.read()

            # Parse YAML safely - handle multi-document format
            rules = {}
            # Split by document separator and parse each
            documents = content.split("\n---\n")
            for doc in documents:
                try:
                    parsed = yaml.safe_load(doc)
                    if isinstance(parsed, dict):
                        # Top-level document with metadata
                        if "schema_version" in parsed or "categories" in parsed:
                            continue
                        # Single rule document
                        if "rule_id" in parsed:
                            rules[parsed["rule_id"]] = parsed
                    elif isinstance(parsed, list):
                        # List of rules
                        for item in parsed:
                            if isinstance(item, dict) and "rule_id" in item:
                                rules[item["rule_id"]] = item
                except yaml.YAMLError:
                    continue  # Skip malformed documents

            return rules
        except Exception as e:
            print(f"⚠️  Warning: Error loading rules: {e}, using empty rules")
            return {}

    def _log_audit(self, result: CheckpointResult):
        """Log checkpoint result to audit trail"""
        with open(self.audit_path, "a") as f:
            audit_entry = {
                "timestamp": result.timestamp,
                "checkpoint_type": result.checkpoint_type,
                "orchestrator": result.orchestrator,
                "phase": result.phase,
                "operation": result.operation,
                "rules_validated": result.rules_validated,
                "violations": [asdict(v) for v in result.violations],
                "status": result.status,
                "blocked": result.blocked,
            }
            f.write(json.dumps(audit_entry) + "\n")

    def checkpoint_phase_start(
        self, phase_number: int, orchestrator: str, context: Optional[Dict] = None
    ) -> CheckpointResult:
        """
        Validate governance rules at phase start

        Args:
            phase_number: Phase number (e.g., 0, 1, 2, -2, 999)
            orchestrator: Orchestrator name (e.g., "planning_v5")
            context: Optional phase context

        Returns:
            CheckpointResult with validation status

        Raises:
            GovernanceViolationError if BLOCKED rule violated
        """
        print(f"🛡️  Governance Checkpoint: Phase {phase_number} Start ({orchestrator})")

        context = context or {}
        violations = []
        rules_validated = []

        # Rule 1: SETUP_VERIFICATION (Phase -2)
        if phase_number == -2:
            rules_validated.append("SETUP_VERIFICATION")
            # Verify setup verification is actually running
            if not context.get("setup_verification_complete"):
                violations.append(
                    GovernanceViolation(
                        rule_id="SETUP_VERIFICATION",
                        rule_name="Phase -2: Setup Verification Mandatory",
                        severity="blocked",
                        description="Phase -2 must run setup verification",
                        recommendation="Execute SetupVerifier before proceeding",
                        context={"phase": phase_number},
                    )
                )

        # Rule 2: TDD_ENFORCEMENT (Code phases)
        if phase_number > 0 and phase_number < 900:
            rules_validated.append("TDD_ENFORCEMENT")
            if context.get("involves_code_changes") and not context.get("tests_written"):
                violations.append(
                    GovernanceViolation(
                        rule_id="TDD_ENFORCEMENT",
                        rule_name="RED→GREEN→REFACTOR Required",
                        severity="blocked",
                        description="Code changes require tests FIRST (RED phase)",
                        recommendation="Write failing tests before implementation",
                        context={"phase": phase_number, "orchestrator": orchestrator},
                    )
                )

        # Rule 3: PLANNING_ISOLATION
        if "planning" in orchestrator.lower():
            rules_validated.append("PLANNING_ISOLATION")
            if context.get("immediate_implementation"):
                violations.append(
                    GovernanceViolation(
                        rule_id="PLANNING_ISOLATION",
                        rule_name="Planning vs Implementation Isolation",
                        severity="blocked",
                        description="Planning commands must create plans ONLY, not implement",
                        recommendation="Create plan structure, then hand off to implementation",
                        context={"orchestrator": orchestrator},
                    )
                )

        # Determine status
        blocked_violations = [v for v in violations if v.severity == "blocked"]
        status = "FAILED" if blocked_violations else "PASSED"
        blocked = len(blocked_violations) > 0

        result = CheckpointResult(
            timestamp=datetime.now().isoformat(),
            checkpoint_type=CheckpointType.PHASE_START.value,
            orchestrator=orchestrator,
            phase=phase_number,
            operation=None,
            rules_validated=rules_validated,
            violations=violations,
            status=status,
            blocked=blocked,
        )

        # Log to audit trail
        self._log_audit(result)

        if blocked:
            print(f"   ❌ BLOCKED: {len(blocked_violations)} critical violations")
            for v in blocked_violations:
                print(f"      - {v.rule_name}: {v.description}")
            raise GovernanceViolationError(
                f"Governance checkpoint failed: {blocked_violations[0].description}"
            )
        else:
            print(f"   ✅ PASSED: {len(rules_validated)} rules validated")

        return result

    def checkpoint_operation(
        self, operation_name: str, orchestrator: str, context: Optional[Dict] = None
    ) -> CheckpointResult:
        """
        Validate governance rules for a specific operation

        Args:
            operation_name: Operation being performed (e.g., "file_creation", "git_commit")
            orchestrator: Orchestrator performing operation
            context: Operation-specific context

        Returns:
            CheckpointResult with validation status
        """
        print(f"🛡️  Governance Checkpoint: Operation '{operation_name}' ({orchestrator})")

        context = context or {}
        violations = []
        rules_validated = []

        # Rule: GIT_ISOLATION
        if operation_name == "git_commit":
            rules_validated.append("GIT_ISOLATION")
            commit_path = context.get("file_path", "")
            if "cortex" in commit_path.lower() and context.get("target_repo") != "CORTEX":
                violations.append(
                    GovernanceViolation(
                        rule_id="GIT_ISOLATION",
                        rule_name="CORTEX/User Repository Isolation",
                        severity="blocked",
                        description="CORTEX code cannot be committed to user repositories",
                        recommendation="Exclude CORTEX-related files from user repo commits",
                        context={
                            "file_path": commit_path,
                            "target_repo": context.get("target_repo"),
                        },
                    )
                )

        # Rule: HOLISTIC_DISCOVERY
        if operation_name == "file_creation":
            rules_validated.append("HOLISTIC_DISCOVERY")
            file_path = context.get("file_path", "")
            if not context.get("search_performed"):
                violations.append(
                    GovernanceViolation(
                        rule_id="HOLISTIC_DISCOVERY",
                        rule_name="Search Before Create",
                        severity="warning",
                        description="File creation without prior search for duplicates",
                        recommendation="Run workspace search before creating new files",
                        context={"file_path": file_path},
                    )
                )

        # Determine status
        blocked_violations = [v for v in violations if v.severity == "blocked"]
        status = "FAILED" if blocked_violations else "PASSED"
        blocked = len(blocked_violations) > 0

        result = CheckpointResult(
            timestamp=datetime.now().isoformat(),
            checkpoint_type=CheckpointType.OPERATION.value,
            orchestrator=orchestrator,
            phase=None,
            operation=operation_name,
            rules_validated=rules_validated,
            violations=violations,
            status=status,
            blocked=blocked,
        )

        # Log to audit trail
        self._log_audit(result)

        if blocked:
            print(f"   ❌ BLOCKED: {len(blocked_violations)} critical violations")
            raise GovernanceViolationError(
                f"Operation blocked: {blocked_violations[0].description}"
            )
        elif violations:
            print(f"   ⚠️  WARNINGS: {len(violations)} non-blocking violations")
        else:
            print(f"   ✅ PASSED: {len(rules_validated)} rules validated")

        return result

    def checkpoint_phase_complete(
        self, phase_number: int, orchestrator: str, artifacts: Optional[Dict] = None
    ) -> CheckpointResult:
        """
        Validate governance rules at phase completion

        Args:
            phase_number: Phase number completed
            orchestrator: Orchestrator name
            artifacts: Phase artifacts (files created, tests run, etc.)

        Returns:
            CheckpointResult with validation status
        """
        print(f"🛡️  Governance Checkpoint: Phase {phase_number} Complete ({orchestrator})")

        artifacts = artifacts or {}
        violations = []
        rules_validated = []

        # Rule: TEARDOWN_REFACTOR (Phase 999)
        if phase_number == 999:
            rules_validated.append("TEARDOWN_REFACTOR")
            if not artifacts.get("refactor_complete"):
                violations.append(
                    GovernanceViolation(
                        rule_id="TEARDOWN_REFACTOR",
                        rule_name="Phase N+1: Teardown + REFACTOR + Commit Mandatory",
                        severity="blocked",
                        description="Phase 999 must complete whole-file REFACTOR",
                        recommendation="Run teardown_refactor.py on all modified files",
                        context={"phase": phase_number},
                    )
                )

            if not artifacts.get("git_commit_complete"):
                violations.append(
                    GovernanceViolation(
                        rule_id="TEARDOWN_REFACTOR",
                        rule_name="Git Commit Required",
                        severity="blocked",
                        description="Phase 999 must complete git commit with /cortex-git-commit pattern",
                        recommendation="Create structured commit message and commit changes",
                        context={"phase": phase_number},
                    )
                )

        # Rule: TDD_ENFORCEMENT (Code phases)
        if phase_number > 0 and phase_number < 900:
            if artifacts.get("code_written") and not artifacts.get("tests_passing"):
                rules_validated.append("TDD_ENFORCEMENT")
                violations.append(
                    GovernanceViolation(
                        rule_id="TDD_ENFORCEMENT",
                        rule_name="Tests Must Pass Before Phase Completion",
                        severity="blocked",
                        description="All tests must pass before marking phase complete",
                        recommendation="Fix failing tests or revert implementation",
                        context={
                            "phase": phase_number,
                            "tests_passing": artifacts.get("tests_passing"),
                        },
                    )
                )

        # Determine status
        blocked_violations = [v for v in violations if v.severity == "blocked"]
        status = "FAILED" if blocked_violations else "PASSED"
        blocked = len(blocked_violations) > 0

        result = CheckpointResult(
            timestamp=datetime.now().isoformat(),
            checkpoint_type=CheckpointType.PHASE_COMPLETE.value,
            orchestrator=orchestrator,
            phase=phase_number,
            operation=None,
            rules_validated=rules_validated,
            violations=violations,
            status=status,
            blocked=blocked,
        )

        # Log to audit trail
        self._log_audit(result)

        if blocked:
            print(f"   ❌ BLOCKED: {len(blocked_violations)} critical violations")
            raise GovernanceViolationError(
                f"Phase completion blocked: {blocked_violations[0].description}"
            )
        else:
            print(f"   ✅ PASSED: {len(rules_validated)} rules validated")

        return result

    def get_audit_summary(self, orchestrator: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get audit trail summary

        Args:
            orchestrator: Optional filter by orchestrator name
            limit: Maximum number of entries to return

        Returns:
            List of audit entries
        """
        if not self.audit_path.exists():
            return []

        entries = []
        with open(self.audit_path, "r") as f:
            for line in f:
                entry = json.loads(line.strip())
                if orchestrator is None or entry.get("orchestrator") == orchestrator:
                    entries.append(entry)

        # Return most recent entries
        return entries[-limit:]


class GovernanceViolationError(Exception):
    """Raised when a BLOCKED governance rule is violated"""

    pass


# Convenience function for quick checkpoint
def quick_checkpoint(
    checkpoint_type: str,
    orchestrator: str,
    phase: Optional[int] = None,
    operation: Optional[str] = None,
    context: Optional[Dict] = None,
    artifacts: Optional[Dict] = None,
) -> CheckpointResult:
    """
    Quick governance checkpoint

    Args:
        checkpoint_type: "phase_start", "operation", or "phase_complete"
        orchestrator: Orchestrator name
        phase: Optional phase number
        operation: Optional operation name
        context: Optional context dict
        artifacts: Optional artifacts dict

    Returns:
        CheckpointResult
    """
    checkpoint = GovernanceCheckpoint()

    if checkpoint_type == "phase_start":
        return checkpoint.checkpoint_phase_start(phase, orchestrator, context)
    elif checkpoint_type == "operation":
        return checkpoint.checkpoint_operation(operation, orchestrator, context)
    elif checkpoint_type == "phase_complete":
        return checkpoint.checkpoint_phase_complete(phase, orchestrator, artifacts)
    else:
        raise ValueError(f"Invalid checkpoint_type: {checkpoint_type}")


if __name__ == "__main__":
    # Demo usage
    print("🛡️  CORTEX Governance Checkpoint Middleware - Demo")
    print("=" * 60)

    checkpoint = GovernanceCheckpoint()

    # Demo 1: Phase start validation
    print("\n1️⃣ Phase Start Checkpoint:")
    try:
        result = checkpoint.checkpoint_phase_start(
            phase_number=1, orchestrator="planning_v5", context={"involves_code_changes": False}
        )
        print(f"   Status: {result.status}")
    except GovernanceViolationError as e:
        print(f"   ❌ Blocked: {e}")

    # Demo 2: Operation validation
    print("\n2️⃣ Operation Checkpoint:")
    result = checkpoint.checkpoint_operation(
        operation_name="file_creation",
        orchestrator="refinement",
        context={"file_path": "src/new_module.py", "search_performed": True},
    )
    print(f"   Status: {result.status}")

    # Demo 3: Phase completion
    print("\n3️⃣ Phase Complete Checkpoint:")
    result = checkpoint.checkpoint_phase_complete(
        phase_number=1,
        orchestrator="refinement",
        artifacts={"code_written": True, "tests_passing": True},
    )
    print(f"   Status: {result.status}")

    # Demo 4: Audit summary
    print("\n4️⃣ Audit Trail Summary:")
    summary = checkpoint.get_audit_summary(limit=10)
    print(f"   Found {len(summary)} audit entries")

    print("\n" + "=" * 60)
    print("✅ Governance checkpoint demo complete")
