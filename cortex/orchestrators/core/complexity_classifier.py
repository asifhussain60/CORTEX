"""
Complexity Classifier — Phase 2 SDLC orchestrator component.

Classifies user requests into SIMPLE / COMPLEX / CRITICAL complexity tiers
to route them through the appropriate validation pipeline.

Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC-ID: AC-SDLC-PHASE2-001
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ComplexityLevel(str, Enum):  # CORE-035-scoped — domain-specific complexity classification
    """Task complexity classification tiers."""

    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"
    CRITICAL = "CRITICAL"


@dataclass
class ComplexityResult:
    """Result of complexity classification."""

    level: ComplexityLevel
    loc_estimate: int
    layers_affected: int
    effort_estimate_minutes: int
    security_flag: bool
    governance_flag: bool
    reasoning: str
    raw_request: str = ""
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to plain dict for downstream orchestrators."""
        return {
            "level": self.level.value,
            "loc_estimate": self.loc_estimate,
            "layers_affected": self.layers_affected,
            "effort_estimate_minutes": self.effort_estimate_minutes,
            "security_flag": self.security_flag,
            "governance_flag": self.governance_flag,
            "reasoning": self.reasoning,
            "warnings": self.warnings,
        }


# Heuristic keyword sets
_SECURITY_KEYWORDS = frozenset(
    {"auth", "oauth", "jwt", "token", "password", "secret", "encrypt", "ssl", "tls"}
)
_GOVERNANCE_KEYWORDS = frozenset({"compliance", "gdpr", "audit", "governance", "policy"})
_COMPLEX_KEYWORDS = frozenset(
    {
        "database",
        "migration",
        "schema",
        "websocket",
        "real-time",
        "notification",
        "event",
        "stream",
        "frontend",
        "backend",
    }
)


class ComplexityClassifier:
    """
    Classifies incoming task requests into complexity tiers.

    Tiers:
        SIMPLE   — single file/function, <30 min, no cross-layer impact.
        COMPLEX  — multi-layer, >30 min, may have security aspects.
        CRITICAL — security-sensitive, governance-gated, requires full review chain.
    """

    def classify_complexity(self, request: str) -> Dict[str, Any]:
        """
        Classify the complexity of a natural-language task request.

        Args:
            request: Natural-language description of the task.

        Returns:
            Dict with keys: level, loc_estimate, layers_affected,
            effort_estimate_minutes, security_flag, governance_flag, reasoning.
        """
        lower = request.lower()
        words = set(lower.split())

        security_flag = bool(words & _SECURITY_KEYWORDS)
        governance_flag = bool(words & _GOVERNANCE_KEYWORDS)
        complex_signals = len(words & _COMPLEX_KEYWORDS)

        if security_flag or governance_flag:
            result = ComplexityResult(
                level=ComplexityLevel.CRITICAL,
                loc_estimate=400,
                layers_affected=4,
                effort_estimate_minutes=480,
                security_flag=security_flag,
                governance_flag=governance_flag,
                reasoning="Security/governance keywords detected — escalated to CRITICAL.",
                raw_request=request,
            )
        elif complex_signals >= 2:
            result = ComplexityResult(
                level=ComplexityLevel.COMPLEX,
                loc_estimate=300,
                layers_affected=3,
                effort_estimate_minutes=180,
                security_flag=False,
                governance_flag=False,
                reasoning=f"{complex_signals} cross-layer signals detected — classified COMPLEX.",
                raw_request=request,
            )
        else:
            result = ComplexityResult(
                level=ComplexityLevel.SIMPLE,
                loc_estimate=50,
                layers_affected=1,
                effort_estimate_minutes=20,
                security_flag=False,
                governance_flag=False,
                reasoning="Single-layer, low-signal request — classified SIMPLE.",
                raw_request=request,
            )

        return result.to_dict()
