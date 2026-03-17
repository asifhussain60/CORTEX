"""PlanAnalysisGateRunner — CAPE sub-phase 136-c.

Implements 5 pre-approval analysis gates for CAPE-generated plans:

  Blocking (halt plan on P0 conditions):
    1. ThreatModelGate      — P0 threats in scope
    2. QualityAnalysisGate  — quality score < 7.0
    3. SecurityAssessmentGate — P0 CVEs / vulnerabilities

  Informational (adjust CDR score, never block):
    4. RCAHistoryGate       — adjusts CDR by up to -0.3 on repeat failures
    5. OPJConsultationGate  — adjusts CDR by up to ±0.3 on OPJ history

Author: CORTEX Framework
Compliance: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064
AC-ID: AC-136-CAPE-003
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# PlanGateVerdict — result produced by every gate
# ---------------------------------------------------------------------------

_BLOCKING_SEVERITIES = frozenset({"P0", "p0"})
_QUALITY_THRESHOLD: float = 7.0
_RCA_MAX_FAILURES: int = 10
_OPJ_MAX_ADJUSTMENT: float = 0.3
_RCA_MAX_ADJUSTMENT: float = 0.3


@dataclass
class PlanGateVerdict:
    """Result returned by a single analysis gate.

    Attributes:
        gate:           Gate name (e.g. ``"ThreatModel"``).
        blocking:       True if the gate halts plan execution.
        reason:         Human-readable explanation.
        cdr_adjustment: CDR score delta (informational gates only).
    """

    gate: str
    blocking: bool
    reason: str
    cdr_adjustment: float = 0.0


# ---------------------------------------------------------------------------
# Individual gates
# ---------------------------------------------------------------------------

class ThreatModelGate:
    """Blocking gate — halts plan if any P0 threat is present."""

    name: str = "ThreatModel"

    def evaluate(self, *, threats: List[Dict[str, Any]]) -> PlanGateVerdict:
        """Evaluate the threat model gate.

        Args:
            threats: List of threat dicts with a ``"severity"`` key.

        Returns:
            :class:`PlanGateVerdict` with ``blocking=True`` if any P0 threat found.
        """
        p0_threats = [t for t in threats if t.get("severity") in _BLOCKING_SEVERITIES]
        if p0_threats:
            names = ", ".join(t.get("name", "unnamed") for t in p0_threats)
            return PlanGateVerdict(
                gate=self.name,
                blocking=True,
                reason=f"P0 threats detected: {names}",
            )
        return PlanGateVerdict(gate=self.name, blocking=False, reason="No P0 threats")


class QualityAnalysisGate:
    """Blocking gate — halts plan if quality score < 7.0."""

    name: str = "Quality"

    def evaluate(self, *, quality_score: float) -> PlanGateVerdict:
        """Evaluate the quality analysis gate.

        Args:
            quality_score: Numeric quality score (0–10 scale).

        Returns:
            :class:`PlanGateVerdict` with ``blocking=True`` if score below threshold.
        """
        if quality_score < _QUALITY_THRESHOLD:
            return PlanGateVerdict(
                gate=self.name,
                blocking=True,
                reason=f"Quality score {quality_score} below threshold {_QUALITY_THRESHOLD}",
            )
        return PlanGateVerdict(
            gate=self.name,
            blocking=False,
            reason=f"Quality score {quality_score} ≥ {_QUALITY_THRESHOLD}",
        )


class SecurityAssessmentGate:
    """Blocking gate — halts plan if any P0 vulnerability is present."""

    name: str = "Security"

    def evaluate(self, *, vulnerabilities: List[Dict[str, Any]]) -> PlanGateVerdict:
        """Evaluate the security assessment gate.

        Args:
            vulnerabilities: List of vulnerability dicts with a ``"severity"`` key.

        Returns:
            :class:`PlanGateVerdict` with ``blocking=True`` if any P0 vuln found.
        """
        p0_vulns = [v for v in vulnerabilities if v.get("severity") in _BLOCKING_SEVERITIES]
        if p0_vulns:
            cves = ", ".join(v.get("cve", "unknown") for v in p0_vulns)
            return PlanGateVerdict(
                gate=self.name,
                blocking=True,
                reason=f"P0 vulnerabilities: {cves}",
            )
        return PlanGateVerdict(gate=self.name, blocking=False, reason="No P0 vulnerabilities")


class RCAHistoryGate:
    """Informational gate — adjusts CDR score downward based on failure history.

    CDR adjustment: ``−min(failures / max_failures, 1.0) × 0.3``,
    clamped to ``[−0.3, 0.0]``.  Never blocks.
    """

    name: str = "RCAHistory"

    def evaluate(self, *, rca_failures: int, cdr_score: float) -> PlanGateVerdict:
        """Evaluate the RCA history gate.

        Args:
            rca_failures: Number of historical RCA failure events.
            cdr_score:    Current CDR composite score (unused in adjustment
                          calculation but provided for context).

        Returns:
            :class:`PlanGateVerdict` with ``blocking=False`` and a negative
            ``cdr_adjustment`` proportional to failure count.
        """
        ratio = min(1.0, rca_failures / max(1, _RCA_MAX_FAILURES))
        adjustment = -round(ratio * _RCA_MAX_ADJUSTMENT, 4)
        adjustment = max(-_RCA_MAX_ADJUSTMENT, min(0.0, adjustment))
        return PlanGateVerdict(
            gate=self.name,
            blocking=False,
            reason=f"RCA failures: {rca_failures} → CDR adjustment {adjustment:+.4f}",
            cdr_adjustment=adjustment,
        )


class OPJConsultationGate:
    """Informational gate — adjusts CDR score based on OPJ history signal.

    ``opj_score`` is expected in ``[−1.0, 1.0]``.  The CDR adjustment is
    ``opj_score × 0.3``, clamped to ``[−0.3, +0.3]``.  Never blocks.
    """

    name: str = "OPJConsultation"

    def evaluate(self, *, opj_score: float) -> PlanGateVerdict:
        """Evaluate the OPJ consultation gate.

        Args:
            opj_score: OPJ history signal in ``[−1.0, 1.0]``.

        Returns:
            :class:`PlanGateVerdict` with ``blocking=False`` and a
            ``cdr_adjustment`` in ``[−0.3, +0.3]``.
        """
        raw = opj_score * _OPJ_MAX_ADJUSTMENT
        adjustment = max(-_OPJ_MAX_ADJUSTMENT, min(_OPJ_MAX_ADJUSTMENT, raw))
        adjustment = round(adjustment, 4)
        return PlanGateVerdict(
            gate=self.name,
            blocking=False,
            reason=f"OPJ score {opj_score} → CDR adjustment {adjustment:+.4f}",
            cdr_adjustment=adjustment,
        )


# ---------------------------------------------------------------------------
# PlanAnalysisGateRunner
# ---------------------------------------------------------------------------

class PlanAnalysisGateRunner:
    """Run all 5 CAPE analysis gates and aggregate verdicts.

    Gates are always executed in the canonical order:
    Threat → Quality → Security → RCAHistory → OPJConsultation.

    Usage::

        runner = PlanAnalysisGateRunner()
        verdicts = runner.run_all_gates(
            threats=[],
            quality_score=8.5,
            vulnerabilities=[],
            rca_failures=2,
            cdr_score=0.4,
            opj_score=0.3,
        )
        approved = runner.overall_approved(verdicts)
    """

    def __init__(self) -> None:
        self._threat = ThreatModelGate()
        self._quality = QualityAnalysisGate()
        self._security = SecurityAssessmentGate()
        self._rca = RCAHistoryGate()
        self._opj = OPJConsultationGate()

    def run_all_gates(
        self,
        *,
        threats: List[Dict[str, Any]],
        quality_score: float,
        vulnerabilities: List[Dict[str, Any]],
        rca_failures: int,
        cdr_score: float,
        opj_score: float,
    ) -> Dict[str, PlanGateVerdict]:
        """Execute all 5 gates and return an ordered dict of verdicts.

        Args:
            threats:         Threat list for :class:`ThreatModelGate`.
            quality_score:   Quality score (0–10) for :class:`QualityAnalysisGate`.
            vulnerabilities: Vulnerability list for :class:`SecurityAssessmentGate`.
            rca_failures:    Failure count for :class:`RCAHistoryGate`.
            cdr_score:       Current CDR score for :class:`RCAHistoryGate`.
            opj_score:       OPJ signal [−1,1] for :class:`OPJConsultationGate`.

        Returns:
            Ordered dict keyed by gate name in canonical execution order.
        """
        return {
            self._threat.name:   self._threat.evaluate(threats=threats),
            self._quality.name:  self._quality.evaluate(quality_score=quality_score),
            self._security.name: self._security.evaluate(vulnerabilities=vulnerabilities),
            self._rca.name:      self._rca.evaluate(rca_failures=rca_failures, cdr_score=cdr_score),
            self._opj.name:      self._opj.evaluate(opj_score=opj_score),
        }

    @staticmethod
    def overall_approved(verdicts: Dict[str, PlanGateVerdict]) -> bool:
        """Return True only if no blocking gate fired.

        Args:
            verdicts: Dict returned by :meth:`run_all_gates`.

        Returns:
            True when all blocking gates passed.
        """
        return all(not v.blocking for v in verdicts.values())


# Backwards-compatibility alias — tests and downstream code may import GateVerdict
GateVerdict = PlanGateVerdict
