"""
GitOrchestrator — Three-stage pipeline: Enforce → Sanitize → Publish.

Replaces GitHub Actions workflows and .githooks shell scripts with a
single Python orchestrator callable from MCP tools. Zero Arnica surface
area — no shell hooks, no YAML actions.

Pipeline stages:
  1. EnforcementOrchestrator — runs all CORE rule checks (CORE-002, CORE-008, CORE-028)
  2. SanitizationOrchestrator — deep-scans each file, morphs proprietary/PII/secrets
  3. GitPublishOrchestrator  — async git add → commit → push

AC_START: AC-GIT-ORCH-002
Authority: GitOrchestrator recommendation (2026-02-19)
Testing: tests/unit/orchestrators/git/test_git_orchestrator.py
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-028 (snake_case), CORE-035 (single canonical implementation)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cortex.orchestrators.git.git_publish_orchestrator import (
    GitPublishOrchestrator,
    PublishError,
)
from cortex.orchestrators.git.sanitization_orchestrator import (
    SanitizationError,
    SanitizationOrchestrator,
)
from cortex.orchestrators.git.enforcement_orchestrator import (
    EnforcementOrchestrator,
    EnforcementReport,
)
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class GitOrchestratorError(Exception):
    """Raised when any stage of the GitOrchestrator pipeline fails."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class GitOrchestratorResult:
    """Aggregated result of the full GitOrchestrator pipeline.

    Attributes:
        success: True when all three stages passed.
        enforcement_passed: True when no CORE violations found.
        sanitization_changes: Number of substitutions applied by sanitizer.
        commit_sha: SHA of the created commit.
        branch: Target branch pushed to.
        audit_summary: Dict from AuditTrail.summary().
    """

    success: bool
    enforcement_passed: bool
    sanitization_changes: int
    commit_sha: str = ""
    branch: str = ""
    audit_summary: Dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# GitOrchestrator
# ---------------------------------------------------------------------------


class GitOrchestrator(OrchestratorProtocolMixin):
    """Canonical orchestrator for git operations in CORTEX.

    Runs three sequential stages:
    1. **Enforcement** — full CORE rule validation via :class:`EnforcementOrchestrator`
    2. **Sanitization** — deep scan + morph via :class:`SanitizationOrchestrator`
    3. **Publish** — async git add/commit/push via :class:`GitPublishOrchestrator`

    Replaces ``.githooks/pre-commit``, ``.githooks/post-checkout``, and
    ``.github/workflows/security-gate.yml``, ``tdd-gate.yml``,
    ``governance-alignment.yml``.

    Example::

        orch = GitOrchestrator()
        result = await orch.execute(
            repo_path="/path/to/repo",
            branch="main",
            message="feat: sanitized push",
        )

    Args:
        proprietary_terms: Optional mapping of term → replacement registered
            with the SanitizationOrchestrator's PatternRegistry.
        remote: Git remote name (default: 'origin').
        sanitize_dry_run: When True, sanitization scans but does not write.
    """

    def __init__(
        self,
        proprietary_terms: Optional[Dict[str, str]] = None,
        remote: str = "origin",
        sanitize_dry_run: bool = False,
        auto_push: bool = False,
    ) -> None:
        """Initialize GitOrchestrator.

        Args:
            proprietary_terms: Extra proprietary term → replacement mappings.
            remote: Remote name for push.
            sanitize_dry_run: Skip file writes during sanitization when True.
            auto_push: When False (default), commit locally only.
                       Set True only with explicit user approval to push to remote.
        """
        self.enforcement = EnforcementOrchestrator(strict=True)
        self.sanitizer = SanitizationOrchestrator(proprietary_terms=proprietary_terms)
        self.publisher = GitPublishOrchestrator(remote=remote, auto_push=auto_push)
        self._sanitize_dry_run = sanitize_dry_run
        self._auto_push = auto_push

    async def execute(
        self,
        repo_path: str,
        branch: str,
        message: str,
        paths: Optional[List[str]] = None,
    ) -> GitOrchestratorResult:
        """Execute the full enforce → sanitize → publish pipeline.

        Args:
            repo_path: Absolute path to the git repository root.
            branch: Target branch on the remote.
            message: Commit message.
            paths: Specific paths to stage; defaults to all changes.

        Returns:
            :class:`GitOrchestratorResult` with all stage outcomes.

        Raises:
            GitOrchestratorError: When enforcement, sanitization, or publish fails.
        """
        logger.info("GitOrchestrator.execute → repo=%s branch=%s", repo_path, branch)
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation=f"git_commit_{branch}")

        # ── Stage 1: Enforcement ──────────────────────────────────────────
        logger.info("Stage 1/3: Enforcement checks")
        enforcement_result = self.enforcement.run_checks(repo_path)
        if not enforcement_result.passed:
            violations_str = "; ".join(enforcement_result.violations)
            raise GitOrchestratorError(
                f"Enforcement stage failed — CORE violations detected: {violations_str}"
            )
        logger.info("Stage 1/3: Enforcement ✅ passed")

        # ── Stage 2: Sanitization ─────────────────────────────────────────
        logger.info("Stage 2/3: Sanitization (dry_run=%s)", self._sanitize_dry_run)
        try:
            san_result = self.sanitizer.sanitize(
                repo_path, dry_run=self._sanitize_dry_run
            )
        except SanitizationError as exc:
            raise GitOrchestratorError(
                f"Sanitization stage failed — integrity check: {exc}"
            ) from exc
        logger.info(
            "Stage 2/3: Sanitization ✅ %d changes in %d files",
            san_result.total_changes,
            san_result.files_scanned,
        )

        # ── Stage 3: Publish ──────────────────────────────────────────────
        logger.info(
            "Stage 3/3: Git publish → commit locally (auto_push=%s)", self._auto_push
        )
        try:
            pub_result = await self.publisher.publish(
                repo_path=repo_path,
                branch=branch,
                message=message,
                paths=paths,
            )
        except PublishError as exc:
            raise GitOrchestratorError(
                f"Publish stage failed — git error: {exc}"
            ) from exc
        if pub_result.pushed:
            logger.info("Stage 3/3: Committed + pushed ✅ commit=%s", pub_result.commit_sha)
        else:
            logger.info(
                "Stage 3/3: Committed locally ✅ commit=%s — NOT pushed (requires explicit approval)",
                pub_result.commit_sha,
            )

        return GitOrchestratorResult(
            success=True,
            enforcement_passed=True,
            sanitization_changes=san_result.total_changes,
            commit_sha=pub_result.commit_sha,
            branch=branch,
            audit_summary=san_result.audit_trail.summary(),
        )


__all__ = [
    "GitOrchestratorError",
    "GitOrchestratorResult",
    "GitOrchestrator",
]

# AC_COMPLETE: AC-GIT-ORCH-002 ✅ GitOrchestrator implemented
