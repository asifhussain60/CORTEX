# COMPAT shim — cortex.core.config.timeout_profiles → cortex.core.common.timeout_profiles
# Retained: 2026-02-24 (Phase 68-C) | Expires: 2026-05-24
from cortex.core.common.timeout_profiles import (  # noqa: F401
    TimeoutProfile,
    PROFILES,
    get_environment,
    get_profile,
    get_timeout,
    get_timeout_seconds,
    get_thread_join_timeout,
    get_http_timeout,
    get_db_timeout,
    get_llm_timeout,
    get_fallback_timeout,
)
