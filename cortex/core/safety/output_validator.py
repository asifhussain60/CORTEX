# COMPAT shim — cortex.core.safety.output_validator → cortex.core.common.output_validator
# Retained: 2026-02-24 (Phase 68-B) | Expires: 2026-05-24
from cortex.core.common.output_validator import *  # noqa: F401, F403
from cortex.core.common.output_validator import ValidationViolation, ValidationResult, LLMOutputValidator  # noqa: F401
