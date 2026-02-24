# COMPAT shim — cortex.core.errors.structured_error → cortex.core.common.structured_error
# Retained: 2026-02-24 (Phase 68-B) | Expires: 2026-05-24
from cortex.core.common.structured_error import *  # noqa: F401, F403
from cortex.core.common.structured_error import ErrorType, RecoveryHint, CausalityNode, CausalityChain, ErrorContext, StructuredError  # noqa: F401
