"""
Governance Checkpoint Middleware

Enforces CORTEX SKULL rules and governance policies during execution.
Part of Phase 3 Infrastructure Implementation.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..audit_logger import get_audit_logger, AuditCategory, AuditLevel


class GovernanceLevel(str, Enum):
    """Governance severity levels."""
    BLOCKING = "blocking"     # Must pass or abort
    WARNING = "warning"       # Log warning, continue
    ADVISORY = "advisory"     # Informational only


@dataclass
class GovernanceCheckpoint:
    """Result of governance check."""
    rule_name: str
    passed: bool
    level: GovernanceLevel
    message: str
    violations: List[str] = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []


class GovernanceError(Exception):
    """Raised when blocking governance rule fails."""
    pass


class GovernanceCheckpointMiddleware:
    """
    Middleware for governance policy enforcement.
    
    Enforces:
    - SKULL rules (TDD, holistic discovery, git isolation)
    - Brain protection policies
    - Code quality standards
    - Security policies
    """
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize governance checkpoint middleware.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        self.logger = logging.getLogger("cortex.middleware.governance")
        self.audit = get_audit_logger()
        self.brain_path = brain_path or Path("cortex-brain")
        
        self.logger.info("GovernanceCheckpointMiddleware initialized")
        self.audit.info(
            AuditCategory.MIDDLEWARE,
            "GovernanceCheckpointMiddleware",
            "initialize",
            "Governance middleware initialized"
        )
    
    def check_tdd_enforcement(
        self,
        context: Dict[str, Any]
    ) -> GovernanceCheckpoint:
        """
        Check TDD enforcement (RED-GREEN-REFACTOR).
        
        Args:
            context: Execution context
            
        Returns:
            Governance checkpoint result
        """
        # Check if tests exist
        has_tests = context.get("has_tests", False)
        tests_passed = context.get("tests_passed", False)
        
        if not has_tests:
            return GovernanceCheckpoint(
                rule_name="TDD_ENFORCEMENT",
                passed=False,
                level=GovernanceLevel.WARNING,
                message="No tests found - TDD not followed",
                violations=["Missing test files"]
            )
        
        if not tests_passed:
            return GovernanceCheckpoint(
                rule_name="TDD_ENFORCEMENT",
                passed=False,
                level=GovernanceLevel.WARNING,
                message="Tests not passing",
                violations=["Failing tests"]
            )
        
        return GovernanceCheckpoint(
            rule_name="TDD_ENFORCEMENT",
            passed=True,
            level=GovernanceLevel.ADVISORY,
            message="TDD properly followed"
        )
    
    def check_brain_protection(
        self,
        affected_files: List[str]
    ) -> GovernanceCheckpoint:
        """
        Check brain protection rules.
        
        Args:
            affected_files: List of files being modified
            
        Returns:
            Governance checkpoint result
        """
        violations = []
        
        # Check if tier0 files are being modified
        for file_path in affected_files:
            if "tier0" in file_path or "governance" in file_path:
                violations.append(f"Attempting to modify protected file: {file_path}")
        
        if violations:
            return GovernanceCheckpoint(
                rule_name="BRAIN_PROTECTION",
                passed=False,
                level=GovernanceLevel.BLOCKING,
                message="Brain protection violation",
                violations=violations
            )
        
        return GovernanceCheckpoint(
            rule_name="BRAIN_PROTECTION",
            passed=True,
            level=GovernanceLevel.ADVISORY,
            message="No brain protection violations"
        )
    
    def check_git_isolation(
        self,
        repository_path: str,
        context: Dict[str, Any]
    ) -> GovernanceCheckpoint:
        """
        Check git isolation (CORTEX code never commits to user repos).
        
        Args:
            repository_path: Repository path
            context: Execution context
            
        Returns:
            Governance checkpoint result
        """
        repo_path = Path(repository_path)
        
        # Check if this is CORTEX repo
        is_cortex_repo = (repo_path / "cortex-brain").exists()
        
        if not is_cortex_repo:
            # User repo - check if CORTEX code is being committed
            cortex_files = context.get("cortex_files_modified", [])
            if cortex_files:
                return GovernanceCheckpoint(
                    rule_name="GIT_ISOLATION",
                    passed=False,
                    level=GovernanceLevel.BLOCKING,
                    message="CORTEX code cannot be committed to user repos",
                    violations=cortex_files
                )
        
        return GovernanceCheckpoint(
            rule_name="GIT_ISOLATION",
            passed=True,
            level=GovernanceLevel.ADVISORY,
            message="Git isolation maintained"
        )
    
    def check_holistic_discovery(
        self,
        context: Dict[str, Any]
    ) -> GovernanceCheckpoint:
        """
        Check holistic discovery (search before create).
        
        Args:
            context: Execution context
            
        Returns:
            Governance checkpoint result
        """
        search_performed = context.get("search_performed", False)
        creating_new_files = context.get("creating_new_files", False)
        
        if creating_new_files and not search_performed:
            return GovernanceCheckpoint(
                rule_name="HOLISTIC_DISCOVERY",
                passed=False,
                level=GovernanceLevel.WARNING,
                message="Creating files without searching for duplicates",
                violations=["Missing holistic discovery"]
            )
        
        return GovernanceCheckpoint(
            rule_name="HOLISTIC_DISCOVERY",
            passed=True,
            level=GovernanceLevel.ADVISORY,
            message="Holistic discovery performed"
        )
    
    def run_all_checks(
        self,
        context: Dict[str, Any]
    ) -> List[GovernanceCheckpoint]:
        """
        Run all governance checks.
        
        Args:
            context: Execution context
            
        Returns:
            List of governance checkpoints
        """
        checkpoints = []
        
        self.audit.info(
            AuditCategory.MIDDLEWARE,
            "GovernanceCheckpointMiddleware",
            "run_all_checks",
            "Running governance checks"
        )
        
        # Run each check
        checkpoints.append(self.check_tdd_enforcement(context))
        
        if "affected_files" in context:
            checkpoints.append(self.check_brain_protection(
                context["affected_files"]
            ))
        
        if "repository_path" in context:
            checkpoints.append(self.check_git_isolation(
                context["repository_path"],
                context
            ))
        
        checkpoints.append(self.check_holistic_discovery(context))
        
        # Log results
        for checkpoint in checkpoints:
            if not checkpoint.passed:
                self.audit.warning(
                    AuditCategory.MIDDLEWARE,
                    "GovernanceCheckpointMiddleware",
                    "governance_violation",
                    f"{checkpoint.rule_name}: {checkpoint.message}",
                    context={"violations": checkpoint.violations}
                )
        
        return checkpoints
    
    def enforce_blocking(self, checkpoints: List[GovernanceCheckpoint]):
        """
        Enforce blocking governance rules.
        
        Args:
            checkpoints: List of governance checkpoints
            
        Raises:
            GovernanceError: If blocking rule failed
        """
        blocking_failures = [
            c for c in checkpoints
            if c.level == GovernanceLevel.BLOCKING and not c.passed
        ]
        
        if blocking_failures:
            violations = []
            for failure in blocking_failures:
                violations.extend(failure.violations)
            
            error_msg = f"Blocking governance violations: {'; '.join(violations)}"
            
            self.audit.critical(
                AuditCategory.MIDDLEWARE,
                "GovernanceCheckpointMiddleware",
                "enforce_blocking",
                error_msg
            )
            
            raise GovernanceError(error_msg)
    
    def get_summary(
        self,
        checkpoints: List[GovernanceCheckpoint]
    ) -> Dict[str, Any]:
        """
        Get summary of governance checkpoints.
        
        Args:
            checkpoints: List of checkpoints
            
        Returns:
            Summary dictionary
        """
        return {
            "total": len(checkpoints),
            "passed": sum(1 for c in checkpoints if c.passed),
            "failed": sum(1 for c in checkpoints if not c.passed),
            "blocking_failures": sum(
                1 for c in checkpoints
                if c.level == GovernanceLevel.BLOCKING and not c.passed
            ),
            "warnings": sum(
                1 for c in checkpoints
                if c.level == GovernanceLevel.WARNING and not c.passed
            )
        }
