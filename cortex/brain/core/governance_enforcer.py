"""
Governance Enforcer - Runtime Lock and Validation

Provides runtime enforcement of:
- Phase locks (prevent reimplementation)
- AC-ID validation (existence check)
- Intent canonicalization (hallucination prevention)
- Phase dependency gating

This is the core business logic layer. MCP tools wrap these functions.

Author: Asif Hussain
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional

from cortex.models.canonical_enums import IntentType




@dataclass
class CanonicalIntent:
    """Result of intent canonicalization."""
    intent_type: IntentType
    ac_id: Optional[str] = None
    phase: Optional[str] = None
    raw_intent: str = ""
    confidence: float = 1.0


@dataclass
class EnforcementResult:
    """Result of governance enforcement check."""
    allowed: bool
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Phase dependency map
PHASE_DEPENDENCIES = {
    "PHASE-01": None,  # No predecessor
    "PHASE-02": "PHASE-01",
    "PHASE-03": "PHASE-02",
    "PHASE-04": "PHASE-03",
    "PHASE-05": "PHASE-04",
    "PHASE-PARALLEL": "PHASE-01",  # Can run after PHASE-01
}


# Intent patterns for canonicalization
INTENT_PATTERNS = {
    IntentType.IMPLEMENT: [
        r"\b(implement|create|build|develop|code|write|add)\b",
    ],
    IntentType.ANALYZE: [
        r"\b(review|check|verify|validate|audit|inspect|analyze|examine)\b",
    ],
    IntentType.ANALYZE: [
        r"\b(status|show|get|what|list|display|query)\b",
    ],
    IntentType.REFACTOR: [
        r"\b(modify|change|update|edit|alter|refactor)\b",
    ],
    IntentType.DOCUMENT: [
        r"\b(document|lock|complete|finish|close|finalize)\b",
    ],
}

# AC-ID pattern: AC-XXX-NNN-NN or AC-WORD-NNN
AC_ID_PATTERN = re.compile(
    r"\bAC-[A-Z]+-\d{3}-\d{2}\b|"  # AC-AR-001-01 format
    r"\bAC-[A-Z]+-\d{3}\b"          # AC-VALIDATE-001 format
)


class GovernanceEnforcer:
    """
    Runtime governance enforcement.
    
    Provides core validation logic that MCP tools wrap.
    All enforcement decisions are audit-logged.
    """
    
    def __init__(self):
        """
        Initialize enforcer.
        """
        pass  # No database needed
    
    # =========================================================================
    # Phase Lock Enforcement
    # =========================================================================
    
    def check_phase_lock(self, phase_id: str) -> EnforcementResult:
        """
        Check if a phase is locked.
        
        Args:
            phase_id: Phase identifier (e.g., "PHASE-01")
        
        Returns:
            EnforcementResult with allowed=False if locked
        """
        result = self._db.is_phase_locked(phase_id)
        
        if result.is_err():
            return EnforcementResult(
                allowed=False,
                reason=f"Database error: {result.error}"
            )
        
        is_locked = result.unwrap()
        
        if is_locked:
            # Get lock details
            lock_info = self._db.get_phase_lock_info(phase_id)
            metadata = lock_info.unwrap() if lock_info.is_ok() else None
            
            return EnforcementResult(
                allowed=False,
                reason=f"Phase {phase_id} is locked and cannot be modified",
                metadata=metadata
            )
        
        return EnforcementResult(allowed=True)
    
    def can_start_phase(self, phase_id: str) -> EnforcementResult:
        """
        Check if a phase can be started (predecessor locked).
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            EnforcementResult with allowed=False if predecessor not locked
        """
        predecessor = PHASE_DEPENDENCIES.get(phase_id)
        
        # No predecessor required
        if predecessor is None:
            return EnforcementResult(allowed=True)
        
        # Check if predecessor is locked
        pred_locked = self._db.is_phase_locked(predecessor)
        
        if pred_locked.is_err():
            return EnforcementResult(
                allowed=False,
                reason=f"Database error checking predecessor: {pred_locked.error}"
            )
        
        if not pred_locked.unwrap():
            return EnforcementResult(
                allowed=False,
                reason=f"Cannot start {phase_id}: predecessor {predecessor} must be completed and locked first"
            )
        
        return EnforcementResult(allowed=True)
    
    # =========================================================================
    # AC-ID Validation
    # =========================================================================
    
    def is_valid_ac_format(self, ac_id: str) -> bool:
        """
        Check if AC-ID matches valid format.
        
        Args:
            ac_id: AC-ID string
        
        Returns:
            True if format is valid
        """
        return AC_ID_PATTERN.fullmatch(ac_id) is not None
    
    def validate_ac_id(self, ac_id: str) -> EnforcementResult:
        """
        Validate that an AC-ID exists and is properly formatted.
        
        Args:
            ac_id: Acceptance criteria ID
        
        Returns:
            EnforcementResult with validation status
        """
        # Check format first
        if not self.is_valid_ac_format(ac_id):
            return EnforcementResult(
                allowed=False,
                reason=f"Invalid format for AC-ID: {ac_id}. Expected AC-XXX-NNN-NN or AC-WORD-NNN"
            )
        
        # Check existence
        exists = self._db.ac_exists(ac_id)
        
        if exists.is_err():
            return EnforcementResult(
                allowed=False,
                reason=f"Database error: {exists.error}"
            )
        
        if not exists.unwrap():
            return EnforcementResult(
                allowed=False,
                reason=f"AC-ID not found: {ac_id}. Verify it exists in governance.db"
            )
        
        return EnforcementResult(allowed=True)
    
    # =========================================================================
    # Intent Canonicalization (Hallucination Prevention)
    # =========================================================================
    
    def canonicalize_intent(self, raw_intent: str) -> CanonicalIntent:
        """
        Canonicalize a raw intent string to structured form.
        
        Prevents hallucination by mapping varied phrasings to standard intents.
        
        Args:
            raw_intent: Raw user/agent intent string
        
        Returns:
            CanonicalIntent with type, AC-ID, and confidence
        """
        intent_lower = raw_intent.lower()
        
        # Extract AC-ID if present
        ac_match = AC_ID_PATTERN.search(raw_intent.upper())
        ac_id = ac_match.group(0) if ac_match else None
        
        # Determine intent type
        intent_type = IntentType.UNKNOWN
        confidence = 0.0
        
        for itype, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, intent_lower):
                    intent_type = itype
                    confidence = 1.0
                    break
            if intent_type != IntentType.UNKNOWN:
                break
        
        # Extract phase if mentioned
        phase_match = re.search(r"PHASE-(\d{2}|PARALLEL)", raw_intent.upper())
        phase = phase_match.group(0) if phase_match else None
        
        return CanonicalIntent(
            intent_type=intent_type,
            ac_id=ac_id,
            phase=phase,
            raw_intent=raw_intent,
            confidence=confidence
        )
    
    # =========================================================================
    # Full Operation Enforcement
    # =========================================================================
    
    def enforce_operation(
        self,
        operation: str,
        ac_id: str,
        phase: str
    ) -> EnforcementResult:
        """
        Enforce governance for a complete operation.
        
        Checks:
        1. Phase is not locked
        2. AC-ID exists and is valid
        3. Phase can be worked on (predecessor locked)
        
        Args:
            operation: Operation type (implement, review, etc.)
            ac_id: Target AC-ID
            phase: Target phase
        
        Returns:
            EnforcementResult with combined validation result
        """
        # Check phase lock
        lock_result = self.check_phase_lock(phase)
        if not lock_result.allowed:
            self._log_enforcement("BLOCKED_PHASE_LOCKED", ac_id, lock_result.reason)
            return lock_result
        
        # Check AC-ID validity
        ac_result = self.validate_ac_id(ac_id)
        if not ac_result.allowed:
            self._log_enforcement("BLOCKED_INVALID_AC", ac_id, ac_result.reason)
            return ac_result
        
        # Check phase dependencies
        phase_result = self.can_start_phase(phase)
        if not phase_result.allowed:
            self._log_enforcement("BLOCKED_PHASE_DEPENDENCY", ac_id, phase_result.reason)
            return phase_result
        
        # All checks passed
        self._log_enforcement("ALLOWED", ac_id, f"Operation {operation} permitted")
        return EnforcementResult(allowed=True)
    
    def _log_enforcement(
        self,
        decision: str,
        ac_id: Optional[str],
        reason: str
    ) -> None:
        """Log enforcement decision to audit trail."""
        self._db.insert_audit(
            operation=f"ENFORCE_{decision}",
            component="governance_enforcer",
            level="INFO" if decision == "ALLOWED" else "WARNING",
            message=reason,
            ac_id=ac_id
        )
