"""
CORTEX Bootstrap Module - Mandatory Startup Validation Hook

This module is imported by cortex/__init__.py to ensure all startup
validations run before any orchestrator code is executed.

AC-PERMANENT-FIX-015: Prevent repeated discovery of same critical issues
by running mandatory startup validation on first import.

IMPORTANT (CORE-035): This module handles STARTUP VALIDATION only.
For ORCHESTRATOR WIRING, use cortex.core.wiring.bootstrap_cortex() which
returns the GitBackedRegistry with all 23 orchestrators.

Phase 109: env_initializer runs before startup_validator to guarantee the
.cortex-runtime/ directory tree and all 7 SQLite databases exist before any
orchestrator attempts to write traces or read governance state.
"""

import logging

logger = logging.getLogger(__name__)


def _ensure_runtime_environment() -> None:
    """
    Phase 109: Idempotent fast-init of .cortex-runtime/ and all 7 SQLite databases.

    Called once per process on first cortex import. Safe to call multiple times.
    Creates directories and databases if missing; migrates missing columns additively;
    rebuilds corrupt databases automatically. Target: < 300ms on warm runs.

    Skipped if CORTEX_SKIP_ENV_INIT=true (CI environments that pre-build the image).
    """
    import os
    if os.getenv("CORTEX_SKIP_ENV_INIT", "").lower() == "true":
        return
    try:
        from cortex.infrastructure.env_initializer import initialize_runtime_environment
        result = initialize_runtime_environment(verbose=False)
        if not result.ok:
            failed = [db.name for db in result.failed_dbs]
            logger.warning(
                f"⚠️  CORTEX env-init: {len(failed)} database(s) failed to initialize: "
                f"{failed}. Run 'python scripts/setup_env.py' to repair."
            )
        elif result.dirs_created or any(db.tables_created or db.was_rebuilt for db in result.databases):
            logger.info(
                f"✅ CORTEX env-init: runtime environment set up in "
                f"{result.total_duration_ms:.0f}ms "
                f"({result.dirs_created} dirs created)"
            )
        else:
            logger.debug("CORTEX env-init: runtime environment healthy (fast path)")
    except Exception as exc:
        logger.warning(f"CORTEX env-init skipped (non-fatal): {exc}")


def run_startup_validation_hook() -> bool:
    """
    Run CORTEX startup validation hook.

    Called automatically on first import of cortex module.
    This is NOT the orchestrator wiring bootstrap - for that use:
        from cortex.core.wiring import wiring_bootstrap_cortex

    Returns:
        True if validation successful, False if critical issues detected.
    """
    try:
        # Phase 109: Ensure runtime environment before any orchestrator code runs
        _ensure_runtime_environment()

        # AC-HYBRID-KNOWLEDGE-003: Rebuild knowledge cache from YAML on startup
        # try:
        #     from cortex.intelligence.knowledge.cache_builder import rebuild_knowledge_cache
        #     rebuild_knowledge_cache()
        # except Exception as e:
        #     logger.warning(f"Knowledge cache rebuild skipped during bootstrap: {e}")

        # Import validator (this also triggers auto-validation)
        from cortex.infrastructure.startup_validator import (
            run_startup_validation,
        )

        # Run validation
        result = run_startup_validation()

        if result.is_err():
            logger.error(f"CORTEX startup validation failed: {result.error}")
            # Optionally block import on critical issues
            # For now, we log but allow continuation
            return False

        # Get validation status for logging
        if result.is_ok():
            status = result.unwrap()
            if status.is_healthy:
                logger.debug(
                    f"✅ CORTEX bootstrap successful "
                    f"({len(status.auto_remediated_issues)} auto-remediated issues)"
                )
                return True
            else:
                logger.warning(
                    f"⚠️  CORTEX bootstrap completed with issues: "
                    f"{len(status.critical_issues)} critical, "
                    f"{len(status.warnings)} warnings"
                )
                return False

    except Exception:
        logger.exception("CORTEX startup validation failed with exception")
        return False

    return True


# Run startup validation on import
_bootstrap_success = run_startup_validation_hook()
