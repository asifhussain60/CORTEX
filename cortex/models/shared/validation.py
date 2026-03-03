"""
cortex/models/shared/validation.py — Canonical ValidationResult.

Phase 114-a GAP-114-01: Re-exports from the existing canonical definition
at cortex.models.validation_result (already consolidated in Phase 80).

All new code should import from here:
  from cortex.models.shared.validation import ValidationResult

Governance: CORE-035 (single canonical), CORE-011 (type hints), CORE-012 (docstrings)
Authority: phase-114-a, SWEEP-114-LAYERING-RESET
"""
from __future__ import annotations

# Re-export the canonical definition — single source of truth
from cortex.models.validation_result import ValidationResult

__all__ = ["ValidationResult"]
