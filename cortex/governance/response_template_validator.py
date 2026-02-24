"""
ResponseTemplateValidator — CORE-066 enforcement.

Validates that all user-visible output from CORTEX workflows is rendered
through the canonical Response Template format defined in:
  cortex-registry/workflows/templates/governance/copilot-chat-response-template.yaml
  .github/templates/cortex-response-templates.md (SSOT)

Any raw dict output, missing Author header, or non-canonical formatting is
flagged as a CORE-066 violation (P0 if it blocks AC_COMPLETE, P1 otherwise).

This validator is wired as a post-step hook in WorkflowEngine (CORE-066).

Authority: CORE-066 (Response Template Binding)
           CORE-002 (All output inline — no .md/.txt report files)
           CORE-049 (Silent autonomous execution)

AC_START: AC-64-G-IMPL-002
Phase: 64 | Stage: G | Priority: P0
"""

import logging
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)

# Required canonical header tokens (SSOT: cortex-response-templates.md)
_CANONICAL_AUTHOR = "Asif Hussain"
_ORCHESTRATOR_MARKER = "**Orchestrator:**"
_AUTHOR_MARKER = "**Author:**"


class ResponseTemplateValidator:
    """Validates CORTEX workflow output against canonical response template format.

    Used as a post-step hook in WorkflowEngine to enforce CORE-066.
    Each step's user-visible output is passed through validate_output() before
    rendering to the VS Code GitHub Copilot Chat Session.

    Example:
        >>> validator = ResponseTemplateValidator()
        >>> result = validator.validate_output({"raw": "dict"})
        >>> result["valid"]
        False
        >>> result["severity"]
        'P1'

        >>> result = validator.validate_output(
        ...     "## ⚡ CORTEX Architect IMPLEMENT\\n"
        ...     "**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅\\n"
        ... )
        >>> result["valid"]
        True
    """

    # ──────────────────────────────────────────────────────────────────────────
    # PUBLIC
    # ──────────────────────────────────────────────────────────────────────────

    def validate_output(self, output: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a workflow step's user-visible output against CORE-066.

        Args:
            output: The step output to validate. May be a formatted string or
                    a raw dict (raw dict is always a violation).

        Returns:
            Dict with:
              - valid: bool — True if output passes CORE-066
              - severity: str — 'P0', 'P1', or None (if valid)
              - rule: str — 'CORE-066' on violation
              - message: str — human-readable result
              - violations: List[str] — specific violation details
        """
        violations = []

        # ── Check 1: Raw dict is an immediate P1 violation ─────────────────
        if isinstance(output, dict):
            violations.append(
                "Raw dict output is a CORE-066 violation — all user-visible output "
                "must be rendered through the canonical Response Template."
            )
            return {
                "valid": False,
                "severity": "P1",
                "rule": "CORE-066",
                "message": (
                    "CORE-066 P1: Raw dict output detected. "
                    "Wrap output using canonical Response Template sections."
                ),
                "violations": violations,
            }

        # ── Check 2: Must be a string beyond this point ────────────────────
        if not isinstance(output, str):
            violations.append(
                f"Unexpected output type: {type(output).__name__}. Expected str."
            )
            return {
                "valid": False,
                "severity": "P1",
                "rule": "CORE-066",
                "message": "CORE-066 P1: Non-string, non-dict output type.",
                "violations": violations,
            }

        # ── Check 3: Author line must be present ───────────────────────────
        if _AUTHOR_MARKER not in output:
            violations.append(
                f"Missing '{_AUTHOR_MARKER}' canonical header line (CORE-066 / SSOT)."
            )

        # ── Check 4: Canonical author value must be Asif Hussain ──────────
        if _CANONICAL_AUTHOR not in output:
            violations.append(
                f"Canonical author '{_CANONICAL_AUTHOR}' not found in output."
            )

        # ── Check 5: Orchestrator marker must be present ───────────────────
        if _ORCHESTRATOR_MARKER not in output:
            violations.append(
                f"Missing '{_ORCHESTRATOR_MARKER}' orchestrator identifier (CORE-066)."
            )

        if violations:
            return {
                "valid": False,
                "severity": "P1",
                "rule": "CORE-066",
                "message": (
                    f"CORE-066 P1: Response template binding violations ({len(violations)}): "
                    + "; ".join(violations)
                ),
                "violations": violations,
            }

        logger.debug("ResponseTemplateValidator: output passes CORE-066 checks.")
        return {
            "valid": True,
            "severity": None,
            "rule": None,
            "message": "Output is CORE-066 compliant ✅",
            "violations": [],
        }


# AC_COMPLETE: AC-64-G-IMPL-002 ✅ ResponseTemplateValidator implemented (GREEN phase)
