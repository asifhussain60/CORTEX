"""COMPAT shim — cortex.intelligence.hp_output_validator → cortex.intelligence.verification.hp_output_validator

The canonical implementation moved to cortex/intelligence/verification/hp_output_validator.py
as part of Phase 117-c (Intelligence Diamond flatten, GAP-117-08/09).
Retained for backward compatibility (CORE-035 compat exception).
Created: 2026-03-03  |  Review after: 2026-06-03
"""
from cortex.intelligence.verification.hp_output_validator import *  # noqa: F401, F403
