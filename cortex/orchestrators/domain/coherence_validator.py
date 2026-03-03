"""
Coherence Validator — Phase 4 SDLC orchestrator component.

CORE-035 Note: This file contains CrossLayerCoherenceValidator (Python↔JS validation),
distinct from validation/coherence_validator.py which contains CoherenceValidator
(post-edit structural validation). Same filename, different classes and scopes.

Validates cross-layer coherence between Python and JavaScript/TypeScript
boundaries — enum alignment, field naming conventions, API contract parity —
before implementation begins, catching Phase 21-style mismatches at design time.

Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC-ID: AC-SDLC-PHASE4-001
"""
# noqa: CORE-035 — domain-scoped; class name appropriate for this module

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Misalignment:
    """A detected cross-layer coherence violation."""

    type: str
    description: str
    severity: str  # "LOW" | "MEDIUM" | "HIGH" | "BLOCKING"
    python_side: Optional[str] = None
    javascript_side: Optional[str] = None
    impact: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to plain dict."""
        return {
            "type": self.type,
            "description": self.description,
            "severity": self.severity,
            "python": self.python_side,
            "javascript": self.javascript_side,
            "impact": self.impact,
        }


@dataclass
class CoherenceReport:
    """Full coherence validation report."""

    status: str  # "PASS" | "FAIL"
    misalignments: List[Misalignment]
    contract_tests: int
    ready_to_implement: bool
    details: List[Dict[str, Any]] = field(default_factory=list)
    skipped: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to plain dict."""
        return {
            "status": self.status,
            "misalignments": [m.to_dict() for m in self.misalignments],
            "contract_tests": self.contract_tests,
            "ready_to_implement": self.ready_to_implement,
            "details": self.details,
            "skipped": self.skipped,
        }


def _to_camel(snake: str) -> str:
    """Convert snake_case to camelCase."""
    parts = snake.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class CrossLayerCoherenceValidator:
    """
    Validates cross-layer coherence between Python and JavaScript boundaries.

    Renamed from CoherenceValidator → CrossLayerCoherenceValidator (Phase 101)
    to resolve CORE-035 duplicate with cortex.orchestrators.validation.coherence_validator.

    Checks:
        - Enum value alignment (Python Enum ↔ JS const/enum)
        - Field naming convention parity (snake_case → camelCase)
        - API contract completeness
        - Schema version alignment

    Usage:
        validator = CrossLayerCoherenceValidator()
        # Simple skip for SIMPLE tasks
        result = validator.validate()

        # Full check for COMPLEX/CRITICAL tasks
        result = validator.validate(
            py_enums={"Status": ["ACTIVE", "INACTIVE"]},
            js_enums={"Status": ["ACTIVE", "INACTIVE"]},
            py_fields=["user_id", "created_at"],
            js_fields=["userId", "createdAt"],
        )
    """

    def validate(
        self,
        py_enums: Optional[Dict[str, List[str]]] = None,
        js_enums: Optional[Dict[str, List[str]]] = None,
        py_fields: Optional[List[str]] = None,
        js_fields: Optional[List[str]] = None,
        skip_for_simple: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute coherence validation.

        Args:
            py_enums:         Python enum definitions {EnumName: [values]}.
            js_enums:         JavaScript enum definitions {EnumName: [values]}.
            py_fields:        Python snake_case field names.
            js_fields:        JavaScript camelCase field names.
            skip_for_simple:  If True, skip validation (SIMPLE task optimisation).

        Returns:
            Dict with status, misalignments, contract_tests, ready_to_implement.
        """
        if skip_for_simple:
            return CoherenceReport(
                status="PASS",
                misalignments=[],
                contract_tests=0,
                ready_to_implement=True,
                skipped=True,
            ).to_dict()

        misalignments: List[Misalignment] = []
        details: List[Dict[str, Any]] = []
        contract_tests = 0

        # --- Enum alignment ---
        if py_enums and js_enums:
            for enum_name, py_values in py_enums.items():
                js_values = js_enums.get(enum_name, [])
                contract_tests += 1
                missing_in_js = [v for v in py_values if v not in js_values]
                extra_in_js = [v for v in js_values if v not in py_values]

                if missing_in_js or extra_in_js:
                    for val in missing_in_js:
                        misalignments.append(
                            Misalignment(
                                type="enum_value_mismatch",
                                description=f"{enum_name}.{val} defined in Python but missing in JS",
                                severity="HIGH",
                                python_side=f"{enum_name}.{val}",
                                javascript_side="Missing",
                                impact=f"Runtime error when {val} value encountered",
                            )
                        )
                    details.append(
                        {
                            "check": "enum_alignment",
                            "py_enum": enum_name,
                            "js_enum": enum_name,
                            "status": "MISMATCH" if missing_in_js else "MATCH",
                        }
                    )
                else:
                    details.append(
                        {
                            "check": "enum_alignment",
                            "py_enum": enum_name,
                            "js_enum": enum_name,
                            "status": "MATCH",
                        }
                    )

        # --- Field naming convention ---
        if py_fields and js_fields:
            contract_tests += 1
            expected_js = [_to_camel(f) for f in py_fields]
            naming_ok = set(expected_js) == set(js_fields)
            details.append(
                {
                    "check": "field_naming",
                    "py_fields": py_fields,
                    "js_fields": js_fields,
                    "status": "CAMELCASE_CONVERTED" if naming_ok else "MISMATCH",
                }
            )
            if not naming_ok:
                unexpected = [f for f in js_fields if f not in expected_js]
                for field_name in unexpected:
                    misalignments.append(
                        Misalignment(
                            type="field_naming_mismatch",
                            description=f"JS field '{field_name}' has no matching Python snake_case counterpart",
                            severity="MEDIUM",
                            javascript_side=field_name,
                            impact="Serialisation may fail at runtime",
                        )
                    )

        status = "FAIL" if misalignments else "PASS"
        ready = status == "PASS"

        return CoherenceReport(
            status=status,
            misalignments=misalignments,
            contract_tests=max(contract_tests, 1),
            ready_to_implement=ready,
            details=details,
        ).to_dict()


# ---------------------------------------------------------------------------
# Phase 101: Backward-compat alias (CORE-035 resolution)
# Canonical name is now CrossLayerCoherenceValidator to distinguish from
# cortex.orchestrators.validation.coherence_validator.CoherenceValidator.
# ---------------------------------------------------------------------------
CoherenceValidator = CrossLayerCoherenceValidator
"""Backward-compat alias. Use ``CrossLayerCoherenceValidator`` in new code.

AC: Phase 101 | CORE-035
"""

__all__ = ["CoherenceValidator", "CrossLayerCoherenceValidator"]
