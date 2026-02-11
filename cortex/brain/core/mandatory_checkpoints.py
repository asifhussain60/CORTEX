"""
Mandatory Checkpoints.

Pre-execution governance gates, post-execution audit trails,
git checkpoint enforcement, and violation detection.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 33 Stage 4 specification
"""

import logging
import re
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CheckpointError(Exception):
    """Base exception for checkpoint errors."""
    pass


class ViolationType(Enum):
    """Types of violations detected by checkpoints."""
    TDD_VIOLATION = "TDD_VIOLATION"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    NAMING_VIOLATION = "NAMING_VIOLATION"
    STANDARDS_VIOLATION = "STANDARDS_VIOLATION"
    GIT_VIOLATION = "GIT_VIOLATION"


@dataclass
class ViolationReport:
    """
    Violation report container.

    Attributes:
        violation_type: Type of violation
        severity: Severity level (CRITICAL, ERROR, WARNING)
        message: Violation description
        file_path: File where violation occurred
        line_number: Line number (if applicable)
        rule_id: CORE rule ID
    """
    violation_type: ViolationType
    severity: str
    message: str
    file_path: str
    line_number: Optional[int]
    rule_id: str


@dataclass
class CheckpointResult:
    """
    Checkpoint execution result.

    Attributes:
        passed: Whether checkpoint passed
        checkpoint_name: Name of checkpoint
        violations: List of violations found
        warnings: List of warnings
        execution_time: Time taken (seconds)
    """
    passed: bool
    checkpoint_name: str
    violations: List[ViolationReport]
    warnings: List[str]
    execution_time: float


@dataclass
class AuditTrail:
    """
    Audit trail for operation.

    Attributes:
        operation_id: Unique operation identifier
        operation_type: Type of operation (IMPLEMENT, FIX, etc.)
        timestamp: Operation timestamp
        user: User who initiated operation
        checkpoint_results: List of checkpoint results
        git_checkpoint_created: Whether git checkpoint was created
        status: Overall status (PASSED, FAILED, WARNING)
    """
    operation_id: str
    operation_type: str
    timestamp: datetime
    user: str
    checkpoint_results: List[CheckpointResult]
    git_checkpoint_created: bool
    status: str


class MandatoryCheckpoints:
    """
    Mandatory Checkpoints System.

    Enforces pre-execution governance gates, creates audit trails,
    and manages git checkpoints.
    """

    # Intents requiring git checkpoint
    GIT_CHECKPOINT_INTENTS = {"IMPLEMENT", "FIX", "REFACTOR"}

    # Intents requiring TDD
    TDD_REQUIRED_INTENTS = {"IMPLEMENT", "FIX", "REFACTOR"}

    # Severity thresholds
    MAX_VIOLATIONS = 3  # Block execution if >= 3 violations

    def __init__(self):
        """Initialize checkpoints system."""
        self._audit_trails: List[AuditTrail] = []
        logger.info("Mandatory Checkpoints initialized")

    def pre_execution_gate(self, request: Dict[str, Any]) -> CheckpointResult:
        """
        Pre-execution governance gate.

        Args:
            request: Request to validate

        Returns:
            CheckpointResult: Validation result
        """
        import time
        start_time = time.time()

        violations = []
        warnings = []

        try:
            # Validate request structure
            if not request or not isinstance(request, dict):
                raise CheckpointError("Invalid request structure")

            intent = request.get("intent", "")
            user_input = request.get("user_input", "")
            context = request.get("context", {})

            # Check TDD compliance (CORE-008)
            if intent in self.TDD_REQUIRED_INTENTS:
                if not self._check_tdd_mention(user_input):
                    violations.append(ViolationReport(
                        violation_type=ViolationType.TDD_VIOLATION,
                        severity="WARNING",
                        message="No mention of tests in request (TDD recommended)",
                        file_path="",
                        line_number=None,
                        rule_id="CORE-008",
                    ))

            # Check file naming (CORE-028)
            file_path = context.get("file", "") or self._extract_filename(user_input)
            if file_path and self._is_screaming_case(file_path):
                violations.append(ViolationReport(
                    violation_type=ViolationType.NAMING_VIOLATION,
                    severity="ERROR",
                    message=f"SCREAMING_CASE filename detected: {file_path}",
                    file_path=file_path,
                    line_number=None,
                    rule_id="CORE-028",
                ))

            # Check for security issues in user input
            security_violations = self._check_security_patterns(user_input)
            violations.extend(security_violations)

            # Determine if passed
            critical_violations = [v for v in violations if v.severity == "CRITICAL"]
            error_violations = [v for v in violations if v.severity == "ERROR"]

            passed = (
                len(critical_violations) == 0 and
                len(violations) < self.MAX_VIOLATIONS
            )

            execution_time = time.time() - start_time

            return CheckpointResult(
                passed=passed,
                checkpoint_name="PRE_EXECUTION",
                violations=violations,
                warnings=warnings,
                execution_time=execution_time,
            )

        except Exception as e:
            logger.error(f"Pre-execution gate error: {e}")
            raise CheckpointError(f"Pre-execution gate failed: {e}")

    def post_execution_audit(self, execution_result: Dict[str, Any]) -> AuditTrail:
        """
        Post-execution audit trail creation.

        Args:
            execution_result: Execution result data

        Returns:
            AuditTrail: Generated audit trail
        """
        operation_id = str(uuid.uuid4())[:8].upper()
        operation_type = execution_result.get("operation", "UNKNOWN")

        # Collect checkpoint results
        checkpoint_results = []
        if "pre_execution_result" in execution_result:
            checkpoint_results.append(execution_result["pre_execution_result"])

        # Determine status
        success = execution_result.get("success", False)
        has_violations = any(
            len(cr.violations) > 0
            for cr in checkpoint_results
        )

        if success and not has_violations:
            status = "PASSED"
        elif success and has_violations:
            status = "WARNING"
        else:
            status = "FAILED"

        # Check if git checkpoint was created
        git_checkpoint_created = execution_result.get("git_checkpoint_created", False)

        trail = AuditTrail(
            operation_id=operation_id,
            operation_type=operation_type,
            timestamp=datetime.now(),
            user="cortex",
            checkpoint_results=checkpoint_results,
            git_checkpoint_created=git_checkpoint_created,
            status=status,
        )

        # Persist trail
        self._audit_trails.append(trail)
        logger.info(f"Audit trail created: {operation_id} - {status}")

        return trail

    def requires_git_checkpoint(self, request: Dict[str, Any]) -> bool:
        """
        Check if request requires git checkpoint.

        Args:
            request: Request to evaluate

        Returns:
            bool: True if git checkpoint required
        """
        intent = request.get("intent", "")
        user_input = request.get("user_input", "").lower()
        context = request.get("context", {})

        # Major change indicators
        if intent in self.GIT_CHECKPOINT_INTENTS:
            # Check for major change keywords
            major_keywords = ["major", "refactor", "restructure", "migrate"]
            if any(kw in user_input for kw in major_keywords):
                return True

            # Check number of files
            files = context.get("files", [])
            if len(files) > 2:
                return True

        return False

    def create_git_checkpoint(self, message: str) -> bool:
        """
        Create git checkpoint (stash or commit).

        Args:
            message: Checkpoint message

        Returns:
            bool: True if checkpoint created successfully
        """
        try:
            # Create git stash as checkpoint
            result = subprocess.run(
                ["git", "stash", "push", "-u", "-m", message],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                logger.info(f"Git checkpoint created: {message}")
                return True
            else:
                logger.warning(f"Git checkpoint failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Git checkpoint error: {e}")
            return False

    def detect_violations(self, code: str, file_path: str) -> List[ViolationReport]:
        """
        Detect violations in code snippet.

        Args:
            code: Code to analyze
            file_path: File path

        Returns:
            List[ViolationReport]: Detected violations
        """
        violations = []

        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][\w]+["\']', "Hardcoded password detected"),
            (r'api[_-]?key\s*=\s*["\'][\w-]+["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'][\w]+["\']', "Hardcoded secret detected"),
        ]

        for pattern, message in secret_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                violations.append(ViolationReport(
                    violation_type=ViolationType.SECURITY_VIOLATION,
                    severity="CRITICAL",
                    message=message,
                    file_path=file_path,
                    line_number=line_num,
                    rule_id="SEC-001",
                ))

        return violations

    def _check_tdd_mention(self, text: str) -> bool:
        """Check if text mentions tests/TDD."""
        tdd_keywords = ["test", "tdd", "pytest", "unittest"]
        return any(kw in text.lower() for kw in tdd_keywords)

    def _is_screaming_case(self, filename: str) -> bool:
        """Check if filename is SCREAMING_CASE."""
        # Extract just the filename without extension
        name = filename.split('/')[-1].split('.')[0]
        # SCREAMING_CASE: all uppercase with underscores
        return name.isupper() and '_' in name and len(name) > 2

    def _extract_filename(self, text: str) -> str:
        """Extract filename from text."""
        # Simple extraction - look for .py files
        match = re.search(r'(\w+\.py)', text)
        return match.group(1) if match else ""

    def _check_security_patterns(self, text: str) -> List[ViolationReport]:
        """Check for security-related patterns in text."""
        violations = []

        # Check for dangerous operations in text
        dangerous_keywords = ["rm -rf", "DROP TABLE", "eval(", "exec("]
        for keyword in dangerous_keywords:
            if keyword in text:
                violations.append(ViolationReport(
                    violation_type=ViolationType.SECURITY_VIOLATION,
                    severity="WARNING",
                    message=f"Potentially dangerous operation mentioned: {keyword}",
                    file_path="",
                    line_number=None,
                    rule_id="SEC-002",
                ))

        return violations
