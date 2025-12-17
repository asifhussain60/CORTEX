"""
Edge Case Validator for CORTEX 3.0 Unified Planning System

Implements comprehensive safety checks and edge case handling for:
- Security (input sanitization, code injection prevention)
- Stability (rollback safety, timeout handling)
- Robustness (concurrent sessions, disk space, resource limits)
- Quality of Life (progress callbacks, session expiry, complexity analysis)

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0
"""

import re
import os
import psutil
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "CRITICAL"  # Must fix - blocks execution
    WARNING = "WARNING"    # Should fix - may cause issues
    INFO = "INFO"          # Optional - quality of life


@dataclass
class ValidationIssue:
    """Represents a validation issue found."""
    severity: ValidationSeverity
    category: str
    message: str
    mitigation: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class ValidationReport:
    """Complete validation report."""
    passed: bool
    critical_issues: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    
    def has_blocking_issues(self) -> bool:
        """Check if there are blocking issues."""
        return len(self.critical_issues) > 0
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        parts = []
        if self.critical_issues:
            parts.append(f"❌ {len(self.critical_issues)} critical issue(s)")
        if self.warnings:
            parts.append(f"⚠️  {len(self.warnings)} warning(s)")
        if self.info:
            parts.append(f"ℹ️  {len(self.info)} info item(s)")
        
        if not parts:
            return "✅ All validation checks passed"
        return " | ".join(parts)


class EdgeCaseValidator:
    """
    Comprehensive edge case validation for CORTEX 3.0 planning system.
    
    Implements all edge case checks organized by priority:
    - Immediate (Security): #2, #5, #6
    - Short-term (Stability): #9, #11, #12, #17
    - Medium-term (Robustness): #1, #8, #14, #15
    - Long-term (Quality of Life): #19, #20, #22
    """
    
    # Security patterns
    INJECTION_PATTERNS = [
        r'__import__',
        r'eval\s*\(',
        r'exec\s*\(',
        r'compile\s*\(',
        r'subprocess\.',
        r'os\.system',
        r'os\.popen',
        r'\bimport\s+os\b',
        r'\bimport\s+sys\b',
        r'\.\./',  # Path traversal
        r'\.\.[/\\]',  # Path traversal (Windows/Unix)
    ]
    
    # Filesystem-safe name pattern (alphanumeric, hyphen, underscore)
    SAFE_NAME_PATTERN = r'^[a-zA-Z0-9_-]+$'
    
    # Defaults
    DEFAULT_MAX_SESSIONS = 10
    DEFAULT_MIN_DISK_SPACE_GB = 1.0
    DEFAULT_ANALYSIS_TIMEOUT_SECONDS = 300  # 5 minutes
    DEFAULT_SESSION_EXPIRY_HOURS = 24
    DEFAULT_MAX_ITERATIONS = 50
    
    def __init__(
        self,
        sessions_dir: Path,
        max_sessions: int = DEFAULT_MAX_SESSIONS,
        min_disk_space_gb: float = DEFAULT_MIN_DISK_SPACE_GB,
        analysis_timeout: int = DEFAULT_ANALYSIS_TIMEOUT_SECONDS,
        session_expiry_hours: int = DEFAULT_SESSION_EXPIRY_HOURS,
        max_iterations: int = DEFAULT_MAX_ITERATIONS
    ):
        """
        Initialize edge case validator.
        
        Args:
            sessions_dir: Directory where sessions are stored
            max_sessions: Maximum concurrent sessions allowed
            min_disk_space_gb: Minimum required disk space (GB)
            analysis_timeout: Timeout for AST/Lens analysis (seconds)
            session_expiry_hours: Hours until session expires
            max_iterations: Maximum planning iterations
        """
        self.sessions_dir = Path(sessions_dir)
        self.max_sessions = max_sessions
        self.min_disk_space_gb = min_disk_space_gb
        self.analysis_timeout = analysis_timeout
        self.session_expiry_hours = session_expiry_hours
        self.max_iterations = max_iterations
        
        # Compile injection patterns once
        self.injection_regexes = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.INJECTION_PATTERNS
        ]
        self.safe_name_regex = re.compile(self.SAFE_NAME_PATTERN)
        
        # Active session locks
        self._session_locks: Dict[str, threading.Lock] = {}
        self._session_lock = threading.Lock()
        
        logger.info(f"✅ EdgeCaseValidator initialized")
        logger.info(f"   Max sessions: {max_sessions}")
        logger.info(f"   Min disk space: {min_disk_space_gb}GB")
        logger.info(f"   Analysis timeout: {analysis_timeout}s")
        logger.info(f"   Session expiry: {session_expiry_hours}h")
    
    # ===================================================================
    # IMMEDIATE (Security) - Issues #2, #5, #6
    # ===================================================================
    
    def validate_input_sanitization(self, user_input: str, field_name: str) -> ValidationIssue:
        """
        Validate input for code injection attempts (#6).
        
        Checks for:
        - Eval/exec attempts
        - Import statements
        - Subprocess calls
        - Path traversal
        
        Args:
            user_input: User-provided input
            field_name: Name of the field being validated
            
        Returns:
            ValidationIssue if suspicious patterns found, None otherwise
        """
        for regex in self.injection_regexes:
            if regex.search(user_input):
                return ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="security",
                    message=f"Potential code injection detected in '{field_name}': {regex.pattern}",
                    mitigation="Remove suspicious code patterns from input",
                    auto_fixable=False
                )
        return None
    
    def validate_filesystem_safe_name(self, name: str, field_name: str) -> ValidationIssue:
        """
        Validate name is filesystem-safe (#5).
        
        Requirements:
        - Only alphanumeric, hyphen, underscore
        - No spaces, special chars, path separators
        - Not empty
        - Length between 1-100 chars
        
        Args:
            name: Name to validate
            field_name: Name of the field being validated
            
        Returns:
            ValidationIssue if name is unsafe, None otherwise
        """
        if not name:
            return ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="security",
                message=f"'{field_name}' cannot be empty",
                mitigation="Provide a non-empty name",
                auto_fixable=False
            )
        
        if len(name) > 100:
            return ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="security",
                message=f"'{field_name}' too long (max 100 chars): {len(name)} chars",
                mitigation="Shorten the name",
                auto_fixable=False
            )
        
        if not self.safe_name_regex.match(name):
            return ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="security",
                message=f"'{field_name}' contains invalid characters: '{name}'. Only alphanumeric, hyphen, underscore allowed",
                mitigation="Remove special characters and spaces",
                auto_fixable=True  # Could auto-fix by replacing chars
            )
        
        return None
    
    def acquire_session_file_lock(self, session_id: str, timeout: float = 5.0) -> bool:
        """
        Acquire file lock for session (#2).
        
        Prevents concurrent modifications to same session.
        
        Args:
            session_id: Session identifier
            timeout: Maximum seconds to wait for lock
            
        Returns:
            True if lock acquired, False if timeout
        """
        with self._session_lock:
            if session_id not in self._session_locks:
                self._session_locks[session_id] = threading.Lock()
        
        lock = self._session_locks[session_id]
        acquired = lock.acquire(timeout=timeout)
        
        if not acquired:
            logger.warning(f"⚠️  Failed to acquire lock for session {session_id} within {timeout}s")
        
        return acquired
    
    def release_session_file_lock(self, session_id: str):
        """
        Release file lock for session (#2).
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._session_locks:
            self._session_locks[session_id].release()
    
    # ===================================================================
    # SHORT-TERM (Stability) - Issues #9, #11, #12, #17
    # ===================================================================
    
    def validate_rollback_safety(
        self,
        plan_id: str,
        temp_plan_path: Path,
        permanent_plan_path: Path
    ) -> ValidationIssue:
        """
        Validate rollback safety for plan promotion (#9).
        
        Checks:
        - Temp plan exists
        - Permanent location doesn't already exist
        - Backup of existing permanent plan created
        
        Args:
            plan_id: Plan identifier
            temp_plan_path: Path to temporary plan
            permanent_plan_path: Target permanent plan path
            
        Returns:
            ValidationIssue if rollback not safe, None otherwise
        """
        if not temp_plan_path.exists():
            return ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="stability",
                message=f"Temp plan not found for promotion: {temp_plan_path}",
                mitigation="Ensure temp plan exists before promotion",
                auto_fixable=False
            )
        
        if permanent_plan_path.exists():
            # Should backup existing permanent plan
            backup_path = permanent_plan_path.parent / f"{permanent_plan_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            return ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="stability",
                message=f"Permanent plan already exists: {permanent_plan_path}",
                mitigation=f"Will create backup at: {backup_path}",
                auto_fixable=True
            )
        
        return None
    
    def validate_analysis_timeout(self, analysis_type: str, elapsed_seconds: float) -> ValidationIssue:
        """
        Validate analysis hasn't exceeded timeout (#11, #12).
        
        Args:
            analysis_type: Type of analysis (AST, Lens, etc.)
            elapsed_seconds: Elapsed time in seconds
            
        Returns:
            ValidationIssue if timeout exceeded, None otherwise
        """
        if elapsed_seconds > self.analysis_timeout:
            return ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="stability",
                message=f"{analysis_type} analysis exceeded timeout: {elapsed_seconds:.1f}s > {self.analysis_timeout}s",
                mitigation="Analysis will be terminated and stub data used",
                auto_fixable=True  # Can fallback to stub data
            )
        elif elapsed_seconds >= self.analysis_timeout * 0.8:
            # Warning at 80% of timeout
            return ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="stability",
                message=f"{analysis_type} analysis approaching timeout: {elapsed_seconds:.1f}s / {self.analysis_timeout}s",
                mitigation="Consider optimizing analysis scope",
                auto_fixable=False
            )
        
        return None
    
    def validate_idempotency(
        self,
        operation: str,
        plan_id: str,
        expected_state: str,
        current_state: str
    ) -> ValidationIssue:
        """
        Validate operation is idempotent (#17).
        
        Prevents duplicate operations (e.g., approving already approved plan).
        
        Args:
            operation: Operation being performed
            plan_id: Plan identifier
            expected_state: Expected current state
            current_state: Actual current state
            
        Returns:
            ValidationIssue if operation not idempotent, None otherwise
        """
        if current_state != expected_state:
            return ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="stability",
                message=f"Cannot {operation} plan {plan_id}: expected state '{expected_state}', found '{current_state}'",
                mitigation="Check plan state before operation",
                auto_fixable=False
            )
        
        return None
    
    def validate_max_iterations(self, current_iteration: int) -> ValidationIssue:
        """
        Validate iteration count within limits (#10).
        
        Args:
            current_iteration: Current iteration number
            
        Returns:
            ValidationIssue if max iterations exceeded, None otherwise
        """
        if current_iteration > self.max_iterations:
            return ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="stability",
                message=f"Max iterations exceeded: {current_iteration} > {self.max_iterations}",
                mitigation="Plan may be stuck in refinement loop - consider manual intervention",
                auto_fixable=False
            )
        elif current_iteration >= self.max_iterations * 0.8:
            return ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="stability",
                message=f"Approaching max iterations: {current_iteration} / {self.max_iterations}",
                mitigation="Consider finalizing plan soon",
                auto_fixable=False
            )
        
        return None
    
    # ===================================================================
    # MEDIUM-TERM (Robustness) - Issues #1, #8, #14, #15
    # ===================================================================
    
    def validate_concurrent_sessions(self, active_session_ids: List[str]) -> ValidationIssue:
        """
        Validate no concurrent sessions for same user/plan (#1).
        
        Args:
            active_session_ids: List of currently active session IDs
            
        Returns:
            ValidationIssue if concurrent sessions detected, None otherwise
        """
        if len(active_session_ids) > 1:
            return ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="robustness",
                message=f"Multiple concurrent sessions detected: {len(active_session_ids)} active",
                mitigation="Close or complete existing sessions before starting new ones",
                auto_fixable=False
            )
        
        return None
    
    def cleanup_stale_sessions(self) -> List[str]:
        """
        Cleanup stale sessions on startup (#8).
        
        Returns:
            List of cleaned up session IDs
        """
        cleaned = []
        sessions_file = self.sessions_dir / "active-sessions.json"
        
        if not sessions_file.exists():
            return cleaned
        
        try:
            import json
            data = json.loads(sessions_file.read_text(encoding='utf-8'))
            
            expiry_threshold = datetime.now() - timedelta(hours=self.session_expiry_hours)
            
            for session_id, session_data in list(data.items()):
                last_updated = datetime.fromisoformat(session_data.get('last_updated', ''))
                
                if last_updated < expiry_threshold:
                    del data[session_id]
                    cleaned.append(session_id)
                    logger.info(f"🧹 Cleaned stale session: {session_id}")
            
            # Write back cleaned data
            sessions_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
            
        except Exception as e:
            logger.error(f"Failed to cleanup stale sessions: {e}")
        
        return cleaned
    
    def validate_disk_space(self) -> ValidationIssue:
        """
        Validate sufficient disk space (#14).
        
        Returns:
            ValidationIssue if disk space insufficient, None otherwise
        """
        try:
            usage = psutil.disk_usage(str(self.sessions_dir))
            free_gb = usage.free / (1024 ** 3)
            
            if free_gb < self.min_disk_space_gb:
                return ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="robustness",
                    message=f"Insufficient disk space: {free_gb:.2f}GB free < {self.min_disk_space_gb}GB required",
                    mitigation="Free up disk space before continuing",
                    auto_fixable=False
                )
            elif free_gb < self.min_disk_space_gb * 2:
                return ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="robustness",
                    message=f"Low disk space: {free_gb:.2f}GB free",
                    mitigation="Consider freeing up disk space soon",
                    auto_fixable=False
                )
            
        except Exception as e:
            logger.warning(f"Failed to check disk space: {e}")
        
        return None
    
    def validate_max_sessions_limit(self, current_session_count: int) -> ValidationIssue:
        """
        Validate max sessions limit not exceeded (#15).
        
        Args:
            current_session_count: Number of currently active sessions
            
        Returns:
            ValidationIssue if max sessions exceeded, None otherwise
        """
        if current_session_count >= self.max_sessions:
            return ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="robustness",
                message=f"Max sessions limit reached: {current_session_count} / {self.max_sessions}",
                mitigation="Close or complete existing sessions before starting new ones",
                auto_fixable=False
            )
        elif current_session_count >= self.max_sessions * 0.8:
            return ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="robustness",
                message=f"Approaching max sessions: {current_session_count} / {self.max_sessions}",
                mitigation="Consider closing unused sessions",
                auto_fixable=False
            )
        
        return None
    
    # ===================================================================
    # LONG-TERM (Quality of Life) - Issues #19, #20, #22
    # ===================================================================
    
    def validate_session_expiry(self, session_created_at: datetime) -> ValidationIssue:
        """
        Validate session hasn't expired (#19).
        
        Args:
            session_created_at: When session was created
            
        Returns:
            ValidationIssue if session expired, None otherwise
        """
        age = datetime.now() - session_created_at
        expiry_threshold = timedelta(hours=self.session_expiry_hours)
        
        if age > expiry_threshold:
            return ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="quality_of_life",
                message=f"Session expired: {age.total_seconds() / 3600:.1f}h > {self.session_expiry_hours}h",
                mitigation="Session will be archived and closed",
                auto_fixable=True
            )
        elif age > expiry_threshold * 0.8:
            remaining_hours = (expiry_threshold - age).total_seconds() / 3600
            return ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="quality_of_life",
                message=f"Session expiring soon: {remaining_hours:.1f}h remaining",
                mitigation="Consider completing or extending session",
                auto_fixable=False
            )
        
        return None
    
    def validate_complexity_analysis(
        self,
        feature_description: str,
        acceptance_criteria_count: int,
        estimated_tier: int
    ) -> ValidationIssue:
        """
        Validate complexity analysis quality (#20).
        
        Checks if complexity tier matches heuristics:
        - HIGH (Tier 4): >10 acceptance criteria or >500 char description
        - MEDIUM (Tier 3): 5-10 criteria or 200-500 chars
        - LOW (Tier 1-2): <5 criteria or <200 chars
        
        Args:
            feature_description: Feature description
            acceptance_criteria_count: Number of acceptance criteria
            estimated_tier: Estimated complexity tier
            
        Returns:
            ValidationIssue if complexity seems mismatched, None otherwise
        """
        desc_length = len(feature_description)
        
        # Heuristic tier estimation
        heuristic_tier = 2  # Default to MEDIUM
        if acceptance_criteria_count > 10 or desc_length > 500:
            heuristic_tier = 4  # HIGH
        elif acceptance_criteria_count >= 5 or desc_length >= 200:
            heuristic_tier = 3  # MEDIUM
        elif acceptance_criteria_count < 3 or desc_length < 100:
            heuristic_tier = 1  # LOW
        
        # Allow 1 tier variance
        if abs(estimated_tier - heuristic_tier) > 1:
            return ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="quality_of_life",
                message=f"Complexity tier {estimated_tier} may not match feature scope (heuristic suggests tier {heuristic_tier})",
                mitigation="Review complexity analysis and adjust if needed",
                auto_fixable=False
            )
        
        return None
    
    def create_progress_callback(
        self,
        operation: str,
        total_steps: int
    ) -> Callable[[int, str], None]:
        """
        Create progress callback for long operations (#22).
        
        Args:
            operation: Operation name
            total_steps: Total number of steps
            
        Returns:
            Callback function that accepts (current_step, status_message)
        """
        def callback(current_step: int, status_message: str):
            """Progress callback."""
            percentage = (current_step / total_steps) * 100
            logger.info(f"📊 {operation}: [{current_step}/{total_steps}] ({percentage:.0f}%) - {status_message}")
        
        return callback
    
    # ===================================================================
    # COMPREHENSIVE VALIDATION
    # ===================================================================
    
    def validate_planning_request(
        self,
        feature_name: str,
        feature_description: str,
        acceptance_criteria: List[str],
        active_sessions: List[str],
        current_session_count: int
    ) -> ValidationReport:
        """
        Comprehensive validation for new planning request.
        
        Runs all applicable validation checks.
        
        Args:
            feature_name: Feature name
            feature_description: Feature description
            acceptance_criteria: List of acceptance criteria
            active_sessions: Active session IDs for this user/plan
            current_session_count: Total active sessions
            
        Returns:
            ValidationReport with all issues found
        """
        critical_issues = []
        warnings = []
        info = []
        
        # Security checks
        issue = self.validate_input_sanitization(feature_name, "feature_name")
        if issue:
            critical_issues.append(issue)
        
        issue = self.validate_input_sanitization(feature_description, "feature_description")
        if issue:
            critical_issues.append(issue)
        
        issue = self.validate_filesystem_safe_name(feature_name, "feature_name")
        if issue:
            if issue.severity == ValidationSeverity.CRITICAL:
                critical_issues.append(issue)
            else:
                warnings.append(issue)
        
        # Robustness checks
        issue = self.validate_concurrent_sessions(active_sessions)
        if issue:
            warnings.append(issue)
        
        issue = self.validate_max_sessions_limit(current_session_count)
        if issue:
            if issue.severity == ValidationSeverity.CRITICAL:
                critical_issues.append(issue)
            else:
                warnings.append(issue)
        
        issue = self.validate_disk_space()
        if issue:
            if issue.severity == ValidationSeverity.CRITICAL:
                critical_issues.append(issue)
            else:
                warnings.append(issue)
        
        # Create report
        passed = len(critical_issues) == 0
        return ValidationReport(
            passed=passed,
            critical_issues=critical_issues,
            warnings=warnings,
            info=info
        )
    
    def validate_session_operation(
        self,
        operation: str,
        session_id: str,
        session_created_at: datetime,
        current_iteration: int,
        expected_state: str,
        current_state: str
    ) -> ValidationReport:
        """
        Comprehensive validation for session operation.
        
        Args:
            operation: Operation being performed
            session_id: Session identifier
            session_created_at: When session was created
            current_iteration: Current iteration count
            expected_state: Expected session state
            current_state: Actual session state
            
        Returns:
            ValidationReport with all issues found
        """
        critical_issues = []
        warnings = []
        info = []
        
        # Stability checks
        issue = self.validate_idempotency(operation, session_id, expected_state, current_state)
        if issue:
            critical_issues.append(issue)
        
        issue = self.validate_max_iterations(current_iteration)
        if issue:
            if issue.severity == ValidationSeverity.CRITICAL:
                critical_issues.append(issue)
            else:
                warnings.append(issue)
        
        # Quality of life checks
        issue = self.validate_session_expiry(session_created_at)
        if issue:
            if issue.severity == ValidationSeverity.WARNING:
                warnings.append(issue)
            else:
                info.append(issue)
        
        # Create report
        passed = len(critical_issues) == 0
        return ValidationReport(
            passed=passed,
            critical_issues=critical_issues,
            warnings=warnings,
            info=info
        )
