"""
Behavioral Boundary Rules for Hallucination Prevention

Enforces operational boundaries to prevent:
1. Locked phase modification
2. AC deletion without approval
3. Governance bypass attempts

AC-ID: HP-001-02
Phase: PHASE-11-HALLUCINATION-PREVENTION
Status: IMPLEMENTATION
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List
import json
import hashlib
import sqlite3
from pathlib import Path
import uuid


class ViolationType(Enum):
    """Types of boundary violations."""
    
    LOCKED_PHASE_MODIFICATION = "locked_phase_modification"
    AC_DELETION_WITHOUT_APPROVAL = "ac_deletion_without_approval"
    GOVERNANCE_BYPASS_ATTEMPT = "governance_bypass_attempt"
    UNKNOWN_BOUNDARY_VIOLATION = "unknown_boundary_violation"


@dataclass
class BoundaryViolation(Exception):
    """Represents a boundary rule violation."""
    
    violation_type: ViolationType
    message: str
    severity: str = "HIGH"  # LOW, MEDIUM, HIGH, CRITICAL
    context: Dict[str, Any] = field(default_factory=dict)
    violation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"[{self.severity}] {self.violation_type.value}: {self.message} "
            f"(ID: {self.violation_id})"
        )


class BehavioralBoundaryRules:
    """
    Enforces behavioral boundaries to prevent hallucinations and governance bypass.
    
    This class implements three core boundary checks:
    1. Phase Lock Protection: Prevent modification of locked phases
    2. AC Deletion Prevention: Require approval for AC deletion
    3. Governance Bypass Detection: Detect and log unauthorized modifications
    
    All violations are logged to audit trail for compliance tracking.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize behavioral boundary rules engine.
        
        Args:
            db_path: Path to governance database. If None, uses default.
        """
        self.db_path = db_path or "cortex-brain/state/governance.db"
        self._violation_cache: List[Dict[str, Any]] = []
        self._last_violation_id: Optional[str] = None
        self._correlation_id: str = str(uuid.uuid4())
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize database connection and create violation table if needed."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create violations table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS boundary_violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    violation_id TEXT UNIQUE NOT NULL,
                    violation_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    context TEXT NOT NULL,
                    correlation_id TEXT,
                    attempt_count INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            
            # Create index for correlation_id for violation chains
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_boundary_correlation 
                ON boundary_violations(correlation_id)
            """)
            
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            # Database might be locked or path invalid - continue anyway
            pass
    
    def check_phase_lock(self, context: Dict[str, Any]) -> None:
        """
        Check if phase modification respects lock status.
        
        Raises BoundaryViolation if:
        - Phase is locked and action is not QUERY
        
        Args:
            context: Operation context containing:
                - phase_id: Phase identifier
                - phase_locked: Boolean indicating lock status
                - action: Operation type (CREATE, MODIFY, DELETE, QUERY, etc.)
                - (optional) user_id: User performing action
                - (optional) timestamp: When action is performed
                
        Raises:
            BoundaryViolation: If locked phase modification is attempted
        """
        if not context:
            raise ValueError("Context required for phase lock check")
        
        phase_id = context.get("phase_id")
        phase_locked = context.get("phase_locked", False)
        action = context.get("action", "UNKNOWN").upper()
        
        # Read operations are always allowed on locked phases
        if action == "QUERY":
            return
        
        # If phase is locked, any other operation is forbidden
        if phase_locked:
            user_id = context.get("user_id", "unknown")
            violation = BoundaryViolation(
                violation_type=ViolationType.LOCKED_PHASE_MODIFICATION,
                message=(
                    f"Cannot perform {action} on locked phase {phase_id}. "
                    f"Locked phases are read-only. Contact governance administrator for unlock request."
                ),
                severity="CRITICAL",
                context=context,
            )
            
            # Log violation
            self._log_violation(violation)
            raise violation
    
    def check_ac_deletion(self, context: Dict[str, Any]) -> None:
        """
        Check if AC deletion has required approval.
        
        Raises BoundaryViolation if:
        - Action is DELETE but no approval provided
        - Approval is not current (expired)
        - Approval doesn't include required fields
        - Completed ACs require higher approval tier
        
        Args:
            context: Operation context containing:
                - ac_id: AC identifier
                - action: Operation type
                - approval: Optional approval dict with:
                    - approved: Boolean
                    - approved_by: User/role that approved
                    - approved_at: ISO timestamp of approval
                    - expires_at: Optional expiration time
                    - reason: Reason for approval (audit trail)
                - (optional) ac_status: AC status (PENDING, COMPLETED, etc.)
                
        Raises:
            BoundaryViolation: If AC deletion without approval is attempted
        """
        if not context:
            raise ValueError("Context required for AC deletion check")
        
        action = context.get("action", "UNKNOWN").upper()
        
        # Only DELETE actions require approval
        if action != "DELETE":
            return
        
        ac_id = context.get("ac_id")
        approval = context.get("approval")
        ac_status = context.get("ac_status", "UNKNOWN")
        
        # Check if approval exists
        if not approval:
            violation = BoundaryViolation(
                violation_type=ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                message=(
                    f"AC {ac_id} deletion requires approval. "
                    f"Submit approval request through governance API with reason."
                ),
                severity="CRITICAL",
                context=context,
            )
            self._log_violation(violation)
            raise violation
        
        # Validate approval structure
        if not approval.get("approved"):
            violation = BoundaryViolation(
                violation_type=ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                message=f"AC {ac_id} deletion not approved.",
                severity="CRITICAL",
                context=context,
            )
            self._log_violation(violation)
            raise violation
        
        # Require reason for audit trail
        if not approval.get("reason"):
            violation = BoundaryViolation(
                violation_type=ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                message=(
                    f"AC {ac_id} deletion approval must include reason for audit trail."
                ),
                severity="HIGH",
                context=context,
            )
            self._log_violation(violation)
            raise violation
        
        # Check approval expiration
        expires_at = approval.get("expires_at")
        if expires_at:
            try:
                expiration = datetime.fromisoformat(expires_at)
                if datetime.now() > expiration:
                    violation = BoundaryViolation(
                        violation_type=ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                        message=(
                            f"AC {ac_id} deletion approval expired at {expires_at}. "
                            f"Request new approval."
                        ),
                        severity="HIGH",
                        context=context,
                    )
                    self._log_violation(violation)
                    raise violation
            except (ValueError, TypeError):
                # Invalid timestamp format
                violation = BoundaryViolation(
                    violation_type=ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                    message=(
                        f"AC {ac_id} deletion approval has invalid timestamp."
                    ),
                    severity="HIGH",
                    context=context,
                )
                self._log_violation(violation)
                raise violation
        
        # For completed ACs, require higher approval tier
        if ac_status == "COMPLETED":
            approved_by = approval.get("approved_by", "")
            if approved_by not in ["governance_admin", "tier0_admin", "lead"]:
                violation = BoundaryViolation(
                    violation_type=ViolationType.AC_DELETION_WITHOUT_APPROVAL,
                    message=(
                        f"Deletion of completed AC {ac_id} requires approval from "
                        f"governance_admin or higher. Current approval: {approved_by}"
                    ),
                    severity="CRITICAL",
                    context=context,
                )
                self._log_violation(violation)
                raise violation
    
    def check_governance_compliance(self, context: Dict[str, Any]) -> None:
        """
        Check if operation bypasses governance controls.
        
        Detects and blocks:
        - Direct database modifications
        - SQL injection attempts
        - Unauthorized direct file edits
        - API calls with explicit bypass flags
        - Operations by unauthorized users
        
        Args:
            context: Operation context containing:
                - operation_type: Type of operation
                - target: What is being modified
                - (optional) query: SQL query being executed
                - (optional) bypass_lock: Explicit bypass flag
                - (optional) user_id: User performing action
                - (optional) tier: User authorization tier
                
        Raises:
            BoundaryViolation: If governance bypass is detected
        """
        if not context:
            raise ValueError("Context required for governance compliance check")
        
        operation_type = context.get("operation_type", "UNKNOWN")
        
        # Legitimate governance API calls are allowed
        if operation_type == "GOVERNANCE_API_CALL":
            return
        
        # Detect direct database writes (bypass API)
        if operation_type == "DIRECT_DB_WRITE":
            violation = BoundaryViolation(
                violation_type=ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                message=(
                    f"Direct database modification detected on {context.get('target')}. "
                    f"All modifications must go through governance API."
                ),
                severity="CRITICAL",
                context=context,
            )
            self._log_violation(violation)
            raise violation
        
        # Detect direct file modifications
        if operation_type == "DIRECT_FILE_EDIT":
            violation = BoundaryViolation(
                violation_type=ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                message=(
                    f"Direct file modification detected on {context.get('target_file')}. "
                    f"All governance modifications must go through API."
                ),
                severity="CRITICAL",
                context=context,
            )
            self._log_violation(violation)
            raise violation
        
        # Detect SQL injection patterns
        query = context.get("query", "")
        if query and self._contains_sql_injection_pattern(query):
            violation = BoundaryViolation(
                violation_type=ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                message="SQL injection pattern detected in query execution.",
                severity="CRITICAL",
                context=context,
            )
            self._log_violation(violation)
            raise violation
        
        # Detect explicit bypass flags in API calls
        if context.get("bypass_lock") or context.get("override_governance"):
            violation = BoundaryViolation(
                violation_type=ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                message=(
                    f"Explicit governance bypass attempted via API. "
                    f"Operation: {operation_type}"
                ),
                severity="CRITICAL",
                context=context,
            )
            self._log_violation(violation)
            raise violation
        
        # Check authorization tier for sensitive operations
        tier = context.get("tier", "UNKNOWN")
        if operation_type == "PHASE_MODIFICATION":
            required_tier = "TIER0"
            if tier not in [required_tier, "TIER0_ADMIN"]:
                violation = BoundaryViolation(
                    violation_type=ViolationType.GOVERNANCE_BYPASS_ATTEMPT,
                    message=(
                        f"Unauthorized phase modification attempt by {context.get('user_id')} "
                        f"with tier {tier}. Required: {required_tier}"
                    ),
                    severity="CRITICAL",
                    context=context,
                )
                self._log_violation(violation)
                raise violation
    
    def check_combined_boundaries(self, context: Dict[str, Any]) -> None:
        """
        Check multiple boundary rules in combination.
        
        Runs all applicable boundary checks and raises the most critical violation.
        
        Args:
            context: Operation context
            
        Raises:
            BoundaryViolation: Most critical violation found
        """
        violations: List[BoundaryViolation] = []
        
        try:
            self.check_phase_lock(context)
        except BoundaryViolation as e:
            violations.append(e)
        
        try:
            self.check_ac_deletion(context)
        except BoundaryViolation as e:
            violations.append(e)
        
        try:
            self.check_governance_compliance(context)
        except BoundaryViolation as e:
            violations.append(e)
        
        # If any violations found, raise the most critical one
        if violations:
            # Sort by severity
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            violations.sort(
                key=lambda v: severity_order.get(v.severity, 99)
            )
            raise violations[0]
    
    def get_recent_violations(
        self, 
        limit: int = 10,
        violation_type: Optional[ViolationType] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent violations from audit trail.
        
        Args:
            limit: Maximum number of violations to return
            violation_type: Filter by specific violation type
            
        Returns:
            List of violation records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM boundary_violations ORDER BY created_at DESC LIMIT ?"
            cursor.execute(query, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            violations = []
            for row in cursor.fetchall():
                violation_dict = dict(zip(columns, row))
                # Parse JSON context
                if violation_dict.get("context"):
                    violation_dict["context"] = json.loads(violation_dict["context"])
                violations.append(violation_dict)
            
            conn.close()
            return violations
        except sqlite3.OperationalError:
            return self._violation_cache[-limit:]
    
    def get_violation_chain(
        self, 
        correlation_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chain of related violations (e.g., repeated attempts).
        
        Args:
            correlation_id: Correlation ID for violation chain
            limit: Maximum violations to return
            
        Returns:
            List of violations in chain
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if correlation_id:
                query = """
                    SELECT * FROM boundary_violations 
                    WHERE correlation_id = ? 
                    ORDER BY created_at ASC LIMIT ?
                """
                cursor.execute(query, (correlation_id, limit))
            else:
                # Return last violation chain
                query = """
                    SELECT * FROM boundary_violations 
                    WHERE correlation_id = (
                        SELECT correlation_id FROM boundary_violations 
                        ORDER BY created_at DESC LIMIT 1
                    ) 
                    ORDER BY created_at ASC LIMIT ?
                """
                cursor.execute(query, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            violations = []
            for row in cursor.fetchall():
                violation_dict = dict(zip(columns, row))
                if violation_dict.get("context"):
                    violation_dict["context"] = json.loads(violation_dict["context"])
                violations.append(violation_dict)
            
            conn.close()
            return violations
        except sqlite3.OperationalError:
            return self._violation_cache
    
    def _log_violation(self, violation: BoundaryViolation) -> None:
        """
        Log boundary violation to audit trail.
        
        Args:
            violation: BoundaryViolation to log
        """
        # Cache in memory
        self._violation_cache.append({
            "violation_id": violation.violation_id,
            "violation_type": violation.violation_type.value,
            "severity": violation.severity,
            "message": violation.message,
            "context": violation.context,
            "correlation_id": violation.context.get("correlation_id"),
            "timestamp": violation.timestamp,
        })
        
        # Attempt to log to database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if this is part of a violation chain
            correlation_id = violation.context.get("correlation_id", str(uuid.uuid4()))
            
            cursor.execute("""
                INSERT INTO boundary_violations 
                (violation_id, violation_type, severity, message, context, correlation_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                violation.violation_id,
                violation.violation_type.value,
                violation.severity,
                violation.message,
                json.dumps(violation.context),
                correlation_id,
            ))
            
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            # Database operations failed - continue with in-memory cache
            pass
    
    @staticmethod
    def _contains_sql_injection_pattern(query: str) -> bool:
        """
        Detect common SQL injection patterns.
        
        Args:
            query: SQL query to check
            
        Returns:
            True if injection pattern detected
        """
        injection_patterns = [
            "DROP TABLE",
            "DELETE FROM",
            "TRUNCATE TABLE",
            "ALTER TABLE",
            "GRANT",
            "REVOKE",
            "exec(",
            "execute(",
            "; DROP",
            "; DELETE",
            "UNION SELECT",
            "OR 1=1",
            "'; DROP",
        ]
        
        query_upper = query.upper()
        return any(pattern in query_upper for pattern in injection_patterns)
