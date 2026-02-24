# COMPAT shim — cortex.core.resilience.thread_safety → cortex.core.common.thread_safety
# Retained: 2026-02-24 (Phase 68-B) | Expires: 2026-05-24
from cortex.core.common.thread_safety import *  # noqa: F401, F403
from cortex.core.common.thread_safety import safe_thread_join, spawn_with_timeout_join, scan_file_for_bare_joins  # noqa: F401
