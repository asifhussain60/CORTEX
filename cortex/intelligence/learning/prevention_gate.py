"""
Phase 87 — Prevention Gate
Compares an incoming operation context against stored prevention rules
and returns a PreventionGateResult indicating PASS / ADVISORY / WARNING / BLOCKING.

Matching strategy: keyword overlap (Jaccard similarity on tokenised text).
Threshold: 0.20 for ADVISORY, 0.40 for WARNING, 0.60 for BLOCKING.

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-028: snake_case filename
CORE-035: Single canonical implementation
"""

from __future__ import annotations

import re
from typing import List, Optional, Set

from cortex.intelligence.learning.rca_models import (
    GateLevel,
    PreventionGateResult,
    PreventionRule,
)
from cortex.intelligence.learning.rca_store import RCAStore

# Similarity thresholds by gate_level severity
_THRESHOLDS: dict[GateLevel, float] = {
    GateLevel.ADVISORY: 0.20,
    GateLevel.WARNING: 0.40,
    GateLevel.BLOCKING: 0.60,
}

# Evaluation order: highest severity first so a BLOCKING rule wins over ADVISORY
_SEVERITY_ORDER: list[GateLevel] = [
    GateLevel.BLOCKING,
    GateLevel.WARNING,
    GateLevel.ADVISORY,
]


def _tokenise(text: str) -> Set[str]:
    """Split text into lowercase word tokens (non-alpha stripped).

    Args:
        text: Raw text string.

    Returns:
        A set of lowercase word tokens.
    """
    return set(re.findall(r"[a-z]+", text.lower()))


def _jaccard(a: Set[str], b: Set[str]) -> float:
    """Compute Jaccard similarity between two token sets.

    Args:
        a: First token set.
        b: Second token set.

    Returns:
        Jaccard similarity in [0.0, 1.0]. Returns 0.0 for two empty sets.
    """
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


class PreventionGate:
    """Compare incoming operation context against stored prevention rules.

    For each active rule the gate computes keyword-overlap similarity between
    the operation context and the rule text.  The rule's configured gate_level
    acts as the *intended* severity; a minimum similarity threshold (per level)
    must be exceeded for the rule to trigger.

    Args:
        store: An initialised RCAStore to query for active prevention rules.
    """

    def __init__(self, store: RCAStore) -> None:
        """Initialise with a reference to the backing RCAStore.

        Args:
            store: The RCAStore containing prevention rules to evaluate against.
        """
        self._store = store

    def check(self, operation_context: str) -> PreventionGateResult:
        """Evaluate an operation context against all active prevention rules.

        Iterates stored rules in descending severity order.  Returns the
        **highest-severity** match found, or PASS when no rule triggers.

        Args:
            operation_context: Natural-language description of the incoming
                               operation to evaluate.

        Returns:
            A PreventionGateResult with gate_level, matched_rule,
            similarity_score, rca_summary, and message.
        """
        rules: List[PreventionRule] = self._store.list_rules()
        active_rules = [r for r in rules if r.active]

        if not active_rules:
            return PreventionGateResult(
                gate_level=GateLevel.PASS,
                matched_rule=None,
                similarity_score=0.0,
                rca_summary=None,
                message="No prevention rules active — operation permitted.",
            )

        context_tokens = _tokenise(operation_context)

        # Evaluate highest-severity first; return on first match
        for level in _SEVERITY_ORDER:
            level_rules = [r for r in active_rules if r.gate_level == level]
            threshold = _THRESHOLDS.get(level, 0.30)
            for rule in level_rules:
                rule_tokens = _tokenise(rule.rule_text)
                score = _jaccard(context_tokens, rule_tokens)
                if score >= threshold:
                    return PreventionGateResult(
                        gate_level=level,
                        matched_rule=rule,
                        similarity_score=score,
                        rca_summary=(
                            f"Rule '{rule.id}' matched (similarity={score:.2f}): {rule.rule_text}"
                        ),
                        message=(
                            f"[{level.value.upper()}] Prevention gate triggered. "
                            f"Similarity={score:.2f}. Review RCA rule '{rule.id}' before proceeding."
                        ),
                    )

        # No rule matched above its threshold
        return PreventionGateResult(
            gate_level=GateLevel.PASS,
            matched_rule=None,
            similarity_score=0.0,
            rca_summary=None,
            message="All prevention rules evaluated — no match above threshold. Operation permitted.",
        )
