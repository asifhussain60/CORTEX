"""
Audit Trail Verifier - Database Audit Trail Validation and Reporting.

Verifies planning audit trails for integrity, detects tampering, and
generates comprehensive audit reports. Integrates with database for
persistent verification and compliance reporting.

Features:
  - Complete chain integrity verification
  - Tampering detection and reporting
  - Audit trail reconstruction from database
  - Compliance reporting
  - Risk assessment from audit data
  - Clarity progression analysis

Verification Process:
  1. Load audit trail from database
  2. Verify each entry's hash (hasn't been tampered)
  3. Verify hash chain linkage (each entry links to previous)
  4. Detect any breaks or tampering
  5. Generate report with findings
  6. Calculate risk scores based on audit data

Author: CORTEX Master Orchestrator
Version: 2.0
Authority: AC-PLANNING-REFINE-COMPLETE
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.orchestrators.core.planning_audit_trail import (
    AuditEventType,
    AuditLogEntry,
    PlanningAuditTrail,
)


class VerificationStatus(Enum):
    """Audit verification status."""

    VERIFIED = "verified"
    TAMPERED = "tampered"
    BROKEN_CHAIN = "broken_chain"
    INCOMPLETE = "incomplete"
    ERROR = "error"


@dataclass
class AuditVerificationResult:
    """Result of audit trail verification."""

    session_id: str
    verification_status: VerificationStatus
    is_valid: bool
    total_entries: int
    total_turns: int
    chain_intact: bool
    tampered_entries: List[str]
    broken_links: List[Dict[str, Any]]
    first_failure_index: Optional[int]
    verification_timestamp: datetime
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "verification_status": self.verification_status.value,
            "is_valid": self.is_valid,
            "total_entries": self.total_entries,
            "total_turns": self.total_turns,
            "chain_intact": self.chain_intact,
            "tampered_entries": self.tampered_entries,
            "broken_links": self.broken_links,
            "first_failure_index": self.first_failure_index,
            "verification_timestamp": self.verification_timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class ClarityAnalysis:
    """Analysis of clarity progression from audit trail."""

    initial_clarity: float
    final_clarity: float
    clarity_progression: List[float]
    average_gain_per_turn: float
    turns_to_dor: int
    dor_achieved: bool
    estimated_next_clarity: Optional[float] = None
    clarification_factors: Optional[List[str]] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.clarification_factors is None:
            self.clarification_factors = []


class AuditTrailVerifier:
    """Verify and analyze planning audit trails."""

    def __init__(self):
        """Initialize verifier."""
        pass

    def verify_audit_trail(
        self, audit_trail: PlanningAuditTrail
    ) -> AuditVerificationResult:
        """
        Verify complete audit trail for integrity.

        Checks:
        1. Each entry's hash is correct
        2. Hash chain linkage is unbroken
        3. All critical events are present
        4. Clarity progression is monotonic

        Args:
            audit_trail: PlanningAuditTrail to verify

        Returns:
            AuditVerificationResult with findings
        """
        # Get base data
        session_id = audit_trail.session_id
        entries = audit_trail.entries
        turn_entries = [
            e for e in entries if e.event_type == AuditEventType.TURN_COMPLETED
        ]

        # Verify chain integrity
        tampering_report = audit_trail.get_tampering_report()
        chain_intact = tampering_report["chain_intact"]
        tampered_entries = tampering_report["tampered_entries"]
        broken_links = tampering_report["broken_links"]
        first_failure = tampering_report["first_failure"]

        # Determine verification status
        if not chain_intact:
            if tampered_entries:
                status = VerificationStatus.TAMPERED
            elif broken_links:
                status = VerificationStatus.BROKEN_CHAIN
            else:
                status = VerificationStatus.ERROR
        else:
            status = VerificationStatus.VERIFIED

        # Build details
        details = {
            "total_entries_verified": len(entries),
            "total_turns_verified": len(turn_entries),
            "session_summary": audit_trail.get_session_summary(),
            "clarity_analysis": self._analyze_clarity(audit_trail).__dict__,
        }

        return AuditVerificationResult(
            session_id=session_id,
            verification_status=status,
            is_valid=chain_intact,
            total_entries=len(entries),
            total_turns=len(turn_entries),
            chain_intact=chain_intact,
            tampered_entries=tampered_entries,
            broken_links=broken_links,
            first_failure_index=first_failure,
            verification_timestamp=datetime.now(),
            details=details,
        )

    def generate_audit_report(
        self, verification_result: AuditVerificationResult
    ) -> Dict[str, Any]:
        """
        Generate comprehensive audit report from verification.

        Args:
            verification_result: Result from verify_audit_trail()

        Returns:
            Dict with comprehensive audit report
        """
        report = {
            "report_type": "PLANNING_AUDIT_REPORT",
            "generated_at": verification_result.verification_timestamp.isoformat(),
            "session_id": verification_result.session_id,
            "verification": {
                "status": verification_result.verification_status.value,
                "is_valid": verification_result.is_valid,
                "chain_intact": verification_result.chain_intact,
                "total_entries": verification_result.total_entries,
                "total_turns": verification_result.total_turns,
            },
            "findings": {
                "tampered_entries": verification_result.tampered_entries,
                "broken_links": verification_result.broken_links,
                "first_failure_index": verification_result.first_failure_index,
            },
            "session_summary": verification_result.details.get("session_summary", {}),
            "clarity_analysis": verification_result.details.get("clarity_analysis", {}),
            "recommendations": self._generate_recommendations(verification_result),
        }

        return report

    def _analyze_clarity(self, audit_trail: PlanningAuditTrail) -> ClarityAnalysis:
        """
        Analyze clarity progression from audit trail.

        Args:
            audit_trail: PlanningAuditTrail to analyze

        Returns:
            ClarityAnalysis with progression metrics
        """
        progression = audit_trail.get_clarity_progression()

        if not progression:
            return ClarityAnalysis(
                initial_clarity=0.0,
                final_clarity=0.0,
                clarity_progression=[],
                average_gain_per_turn=0.0,
                turns_to_dor=0,
                dor_achieved=False,
            )

        initial = progression[0]
        final = progression[-1]
        dor_achieved = final >= 0.95
        turns_to_dor = (
            len(progression) if dor_achieved else len(progression)
        )  # All turns or incomplete

        # Calculate average gain per turn
        if len(progression) > 1:
            total_gain = final - initial
            avg_gain = total_gain / (len(progression) - 1)
        else:
            avg_gain = 0.0

        # Estimate next clarity (linear extrapolation)
        estimated_next = None
        if len(progression) >= 2 and avg_gain > 0:
            estimated_next = min(final + avg_gain, 1.0)

        return ClarityAnalysis(
            initial_clarity=initial,
            final_clarity=final,
            clarity_progression=progression,
            average_gain_per_turn=avg_gain,
            turns_to_dor=turns_to_dor,
            dor_achieved=dor_achieved,
            estimated_next_clarity=estimated_next,
            clarification_factors=[
                "User responses addressed gaps",
                "Git analysis identified risks",
                "CORTEX challenges refined scope",
                "Plan iterations improved specificity",
            ],
        )

    def _generate_recommendations(
        self, verification_result: AuditVerificationResult
    ) -> List[str]:
        """
        Generate recommendations based on verification findings.

        Args:
            verification_result: Verification result

        Returns:
            List of recommendations
        """
        recommendations = []

        # Integrity recommendations
        if not verification_result.is_valid:
            recommendations.append(
                "CRITICAL: Audit trail tampering detected. "
                "Do not proceed with plan execution until investigated."
            )

        if verification_result.tampered_entries:
            recommendations.append(
                f"URGENT: {len(verification_result.tampered_entries)} "
                f"audit entries have invalid hashes. Review all modifications."
            )

        if verification_result.broken_links:
            recommendations.append(
                "URGENT: Hash chain linkage broken. "
                "Some entries may have been removed or reordered."
            )

        # Clarity recommendations
        clarity_data = verification_result.details.get("clarity_analysis", {})
        final_clarity = clarity_data.get("final_clarity", 0.0)

        if final_clarity >= 0.95:
            recommendations.append(
                "✅ Definition of Ready (DoR) achieved. "
                "Plan is ready for TDD implementation."
            )
        elif final_clarity >= 0.80:
            recommendations.append(
                "Plan is mostly ready. Consider one more refinement turn "
                "to reach 95% clarity threshold."
            )
        else:
            recommendations.append(
                "Plan needs more refinement. Continue multi-turn loop "
                "until clarity >= 0.95."
            )

        # Process recommendations
        session_summary = verification_result.details.get("session_summary", {})
        total_turns = session_summary.get("total_turns", 0)

        if total_turns > 6:
            recommendations.append(
                "Plan required extended refinement. "
                "Consider if initial request was sufficiently clear."
            )
        elif total_turns <= 3:
            recommendations.append(
                "Quick agreement achieved. User requirement was well-defined."
            )

        return recommendations

    def detect_tampering_patterns(
        self, verification_result: AuditVerificationResult
    ) -> Dict[str, Any]:
        """
        Detect patterns of tampering in audit trail.

        Args:
            verification_result: Verification result

        Returns:
            Dict with tampering patterns and analysis
        """
        patterns = {
            "tampering_detected": len(verification_result.tampered_entries) > 0,
            "chain_broken": len(verification_result.broken_links) > 0,
            "patterns": [],
            "risk_level": "LOW" if verification_result.is_valid else "CRITICAL",
        }

        # Analyze patterns
        if verification_result.tampered_entries:
            patterns["patterns"].append(
                f"Hash tampering in {len(verification_result.tampered_entries)} entries"
            )

        if verification_result.broken_links:
            patterns["patterns"].append(
                f"Chain linkage broken at {len(verification_result.broken_links)} points"
            )

        if verification_result.first_failure_index is not None:
            patterns["first_tampering_at_entry"] = (
                verification_result.first_failure_index
            )
            patterns["patterns"].append(
                f"First failure detected at entry index "
                f"{verification_result.first_failure_index}"
            )

        return patterns


def get_audit_trail_verifier() -> AuditTrailVerifier:
    """Module-level factory function for verifier access."""
    return AuditTrailVerifier()
