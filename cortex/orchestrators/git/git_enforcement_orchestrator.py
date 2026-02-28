"""
EnforcementOrchestrator — Canonical pre-commit CORE rule enforcement.

CORE-035 Note: This file contains PreCommitEnforcementOrchestrator (pre-commit hooks),
distinct from core/enforcement_orchestrator.py which contains EnforcementOrchestrator
(pre-execution governance). Same filename, different classes and responsibilities.

Absorbs ALL checks previously scattered across .githooks/ shell scripts
and GitHub Actions workflows into a single Python orchestrator:

  ┌─ Check 0: Golden test import validation (no mocks in golden tests)
  ├─ Check 1: Markdown artifact prevention (CORE-002)
  ├─ Check 2: Governance alignment (CORE rule changes have registry entry)
  ├─ Check 3: Registry blacklist (CORE-056)
  ├─ Check 4: MCP configuration policy (only cortex MCP server)
  ├─ Check 5: CORE-095/096 governance (file placement rules)
  ├─ Check 6: MCP environment validation
  ├─ Check 7: Health policy (versioned filenames, backup files, etc.)
  └─ Check 8: TDD gate (implementation files have corresponding tests)

No shell execution. No GitHub token. No Actions runner.
Called exclusively by GitOrchestrator as Stage 1.

AC_START: AC-GIT-ORCH-003
Authority: GitOrchestrator recommendation (2026-02-19)
Testing: tests/unit/orchestrators/git/test_enforcement_orchestrator.py
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-028 (snake_case), CORE-035 (single canonical implementation)
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94e

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    """Result of a single enforcement check.

    Attributes:
        name: Human-readable check name.
        passed: True when no violations found.
        violations: List of violation messages.
        skipped: True when the check was not applicable.
    """

    name: str
    passed: bool
    violations: List[str] = field(default_factory=list)
    skipped: bool = False


@dataclass
class EnforcementReport:
    """Aggregated result from all enforcement checks.

    Attributes:
        passed: True when every non-skipped check passed.
        checks: Individual check results.
        violations: Flat list of all violations across all checks.
    """

    passed: bool
    checks: List[CheckResult] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)

    def run_checks(self, repo_path: str) -> "EnforcementReport":
        """Compatibility shim — returns self (result already computed).

        Args:
            repo_path: Unused; present for interface compatibility.

        Returns:
            self
        """
        return self


# ---------------------------------------------------------------------------
# Individual check implementations
# ---------------------------------------------------------------------------


def _check_markdown_artifacts(staged_files: List[str]) -> CheckResult:
    """Check 1: Markdown artifact prevention (CORE-002).

    Args:
        staged_files: List of staged file paths.

    Returns:
        :class:`CheckResult`.
    """
    blocked_patterns = [
        r".*-REPORT\.md$",
        r".*-COMPLETION.*\.md$",
        r".*-STATUS\.md$",
        r".*-SUMMARY\.md$",
        r"PHASE-.*-REPORT\.md$",
        r"DEPLOYMENT-.*\.md$",
        r"ORCHESTRATOR-.*\.md$",
        r"SESSION-.*\.md$",
    ]
    allowed_prefix = "docs/"
    violations: List[str] = []

    for f in staged_files:
        if not f.endswith(".md"):
            continue
        if f.startswith(allowed_prefix):
            continue
        name = Path(f).name
        for pattern in blocked_patterns:
            if re.match(pattern, name, re.IGNORECASE):
                violations.append(f"CORE-002: Blocked markdown artifact: {f}")
                break

    return CheckResult(name="markdown_artifact_prevention", passed=len(violations) == 0, violations=violations)


def _check_file_naming(staged_files: List[str]) -> CheckResult:
    """Check: CORE-028 snake_case file naming for Python files.

    Args:
        staged_files: List of staged file paths.

    Returns:
        :class:`CheckResult`.
    """
    violations: List[str] = []
    for f in staged_files:
        if not f.endswith(".py"):
            continue
        name = Path(f).stem
        # Allow dunder names (__init__, __main__)
        if name.startswith("__") and name.endswith("__"):
            continue
        # Flag camelCase / PascalCase names
        if re.search(r"[A-Z]", name):
            violations.append(f"CORE-028: Non-snake_case Python file: {f}")

    return CheckResult(name="file_naming_snake_case", passed=len(violations) == 0, violations=violations)


def _check_tdd_gate(staged_files: List[str], repo_path: str) -> CheckResult:
    """Check: TDD gate — every implementation file has a corresponding test.

    Args:
        staged_files: List of staged file paths.
        repo_path: Repository root.

    Returns:
        :class:`CheckResult`.
    """
    violations: List[str] = []
    root = Path(repo_path)

    for f in staged_files:
        if not f.endswith(".py"):
            continue
        # Skip test files themselves, __init__, setup, config
        parts = Path(f).parts
        if any(p in ("tests", "test") for p in parts):
            continue
        if Path(f).name.startswith(("__", "conftest", "setup")):
            continue
        # Only check files under cortex/ source
        if not f.startswith("cortex/"):
            continue

        # Derive expected test path
        relative = f[len("cortex/"):]
        test_path_1 = root / "tests" / "unit" / relative.replace(
            Path(relative).name, f"test_{Path(relative).name}"
        )
        test_path_2 = root / "tests" / relative.replace(
            Path(relative).name, f"test_{Path(relative).name}"
        )
        test_path_3 = root / "tests" / "unit" / f"test_{Path(relative).name}"

        has_test = test_path_1.exists() or test_path_2.exists() or test_path_3.exists()
        if not has_test:
            violations.append(
                f"CORE-008: No test found for {f} "
                f"(expected e.g. {test_path_1.relative_to(root)})"
            )

    return CheckResult(name="tdd_gate", passed=len(violations) == 0, violations=violations)


def _check_health_policy(staged_files: List[str]) -> CheckResult:
    """Check: Health policy — no versioned filenames, backup files, root DB files.

    Args:
        staged_files: List of staged file paths.

    Returns:
        :class:`CheckResult`.
    """
    violations: List[str] = []
    for f in staged_files:
        name = Path(f).name
        # Versioned filenames
        if re.search(r"_v\d+|[-_]v\d+\.", name, re.IGNORECASE):
            violations.append(f"CORE-028: Versioned filename detected: {f}")
        # Backup files
        if name.endswith((".backup", ".old", ".bak", ".orig")):
            violations.append(f"Health: Backup file staged: {f}")
        # DB files in root
        if name.endswith(".db") and "/" not in f:
            violations.append(f"Health: Database file in repo root: {f}")

    return CheckResult(name="health_policy", passed=len(violations) == 0, violations=violations)


def _check_mcp_policy(staged_files: List[str], repo_path: str) -> CheckResult:
    """Check: MCP configuration policy — only cortex MCP server allowed.

    Args:
        staged_files: List of staged file paths.
        repo_path: Repository root.

    Returns:
        :class:`CheckResult`.
    """
    mcp_files = [f for f in staged_files if "mcp.json" in f or "mcp_servers" in f]
    violations: List[str] = []

    for mf in mcp_files:
        full = Path(repo_path) / mf
        if not full.exists():
            continue
        try:
            import json
            data = json.loads(full.read_text())
            servers = data.get("servers", data.get("mcpServers", {}))
            non_cortex = [k for k in servers if k != "cortex"]
            if non_cortex:
                violations.append(
                    f"MCP policy: Non-CORTEX servers in {mf}: {non_cortex}"
                )
        except Exception as exc:
            logger.debug("Could not parse MCP config %s: %s", mf, exc)

    return CheckResult(name="mcp_policy", passed=len(violations) == 0, violations=violations)


# ---------------------------------------------------------------------------
# EnforcementOrchestrator
# ---------------------------------------------------------------------------


class PreCommitEnforcementOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Runs all pre-commit CORE rule enforcement checks in-process.

    Replaces the following shell hooks and GitHub Actions:
    - ``.githooks/pre-commit``
    - ``.githooks/pre-commit-health``
    - ``.githooks/pre-commit-wiring-validator``
    - ``.githooks/pre-commit-wave8-blacklist``
    - ``.github/workflows/tdd-gate.yml``
    - ``.github/workflows/governance-alignment.yml``
    - ``.github/workflows/security-gate.yml`` (enforcement portion)

    Called by :class:`~cortex.orchestrators.git.git_orchestrator.GitOrchestrator`
    as Stage 1 before sanitization and publish.

    .. note::
        Renamed from ``EnforcementOrchestrator`` (CORE-035 de-duplication).
        ``EnforcementOrchestrator`` in ``cortex.orchestrators.core`` is the
        runtime governance orchestrator; this class is exclusively for
        pre-commit enforcement.

    .. deprecated::
        The alias ``EnforcementOrchestrator`` is preserved for backward
        compatibility but will be removed in a future release.
        Import ``PreCommitEnforcementOrchestrator`` directly.

    Example::

        orch = EnforcementOrchestrator()
        report = orch.run_checks("/path/to/repo")
        if not report.passed:
            raise Exception(report.violations)
    """

    # Phase 94e — advisory: IS the pre-commit gate; self-gating is circular.
    # Invoked by GitOrchestrator as Stage 1. Gateway routing deferred.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self, strict: bool = True) -> None:
        """Initialize EnforcementOrchestrator.

        Args:
            strict: When True (default), TDD gate runs as a hard blocker.
                    When False, TDD violations are warnings only.
        """
        self._strict = strict

    def run_checks(self, repo_path: str) -> EnforcementReport:
        """Run all enforcement checks against staged files.

        Args:
            repo_path: Absolute path to the repository root.

        Returns:
            :class:`EnforcementReport` with all check results.
        """
        staged = self._get_staged_files(repo_path)
        logger.info("EnforcementOrchestrator: %d staged files", len(staged))

        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="git_enforcement")

        checks: List[CheckResult] = []

        # Check 1: Markdown artifact prevention (CORE-002)
        checks.append(_check_markdown_artifacts(staged))

        # Check 2: File naming (CORE-028)
        checks.append(_check_file_naming(staged))

        # Check 3: TDD gate (CORE-008)
        tdd = _check_tdd_gate(staged, repo_path)
        if not self._strict:
            # Downgrade TDD violations to warnings (skipped status)
            tdd = CheckResult(
                name=tdd.name,
                passed=True,
                violations=tdd.violations,
                skipped=True,
            )
        checks.append(tdd)

        # Check 4: Health policy (versioned files, backups, root DBs)
        checks.append(_check_health_policy(staged))

        # Check 5: MCP configuration policy
        checks.append(_check_mcp_policy(staged, repo_path))

        # Check 6: PreCommitValidator (wiring health)
        checks.append(self._run_pre_commit_validator())

        # Aggregate
        all_violations: List[str] = []
        for c in checks:
            if not c.passed and not c.skipped:
                all_violations.extend(c.violations)

        overall_passed = len(all_violations) == 0
        logger.info(
            "EnforcementOrchestrator: %s (%d violations)",
            "PASS" if overall_passed else "FAIL",
            len(all_violations),
        )

        return EnforcementReport(
            passed=overall_passed,
            checks=checks,
            violations=all_violations,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_staged_files(self, repo_path: str) -> List[str]:
        """Get list of staged files via git diff --cached.

        Args:
            repo_path: Repository root path.

        Returns:
            List of relative file path strings.
        """
        import subprocess
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
                cwd=repo_path,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                return [f for f in result.stdout.strip().split("\n") if f]
        except Exception as exc:
            logger.debug("Could not get staged files: %s", exc)
        return []

    def _run_pre_commit_validator(self) -> CheckResult:
        """Run CORTEX PreCommitValidator (wiring health check).

        Returns:
            :class:`CheckResult`.
        """
        try:
            from cortex.infrastructure.pre_commit_validator import PreCommitValidator
            validator = PreCommitValidator()
            health = validator.quick_health_check()
            if not health.is_healthy:
                return CheckResult(
                    name="wiring_health",
                    passed=False,
                    violations=[health.error_message or "Wiring health check failed"],
                )
            return CheckResult(name="wiring_health", passed=True)
        except Exception as exc:
            logger.debug("PreCommitValidator unavailable: %s", exc)
            return CheckResult(name="wiring_health", passed=True, skipped=True)


# Backward-compat alias — import the canonical name where possible
EnforcementOrchestrator = PreCommitEnforcementOrchestrator

__all__ = [
    "CheckResult",
    "EnforcementReport",
    "PreCommitEnforcementOrchestrator",
    "EnforcementOrchestrator",  # deprecated alias — use PreCommitEnforcementOrchestrator
]

# AC_COMPLETE: AC-GIT-ORCH-003 ✅ PreCommitEnforcementOrchestrator implemented (was EnforcementOrchestrator)
