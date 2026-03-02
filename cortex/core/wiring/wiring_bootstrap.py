"""
CORTEX Bootstrap - Initialize Git-backed wiring system.

Authority: cortex-registry/planning/phases/completed/2025/ (Phase 3)
Rule: CORE-035 (Single Canonical Implementation)

Entry point for CORTEX system initialization.
"""

import logging

from cortex.core.wiring.registry import GitBackedRegistry, get_registry

logger = logging.getLogger(__name__)


def _ensure_trace_database_initialized() -> None:
    """Ensure trace database exists with current schema (idempotent).

    Authority: CORE-051 (Database Migration Safety)
    Pattern: Auto-repair missing databases on startup
    """
    try:
        from cortex.infrastructure.orchestrator_trace_logger import OrchestratorTraceLogger

        # Trigger singleton initialization (creates .db if missing)
        logger_instance = OrchestratorTraceLogger.get_instance()

        # Verify database exists
        db_path = logger_instance._db_path
        if not db_path.exists():
            logger.info(f"📦 Creating trace database: {db_path}")
            logger_instance._init_db()

        logger.debug(f"✅ Trace database ready: {db_path}")

    except Exception as e:
        # Non-fatal: tracing is observability, not core functionality
        logger.warning(f"⚠️ Trace database initialization skipped: {e}")


def bootstrap_cortex() -> GitBackedRegistry:
    """
    Bootstrap CORTEX orchestrator wiring system.

    This is the main entry point for initializing CORTEX. It:
    1. Loads wiring.yaml specification
    2. Registers all 23 orchestrators
    3. Validates wiring integrity
    4. Ensures trace database initialized
    5. Returns registry for orchestrator access

    Returns:
        GitBackedRegistry with all orchestrators loaded

    Raises:
        FileNotFoundError: If wiring.yaml not found
        ValueError: If wiring specification invalid

    Example:
        >>> from cortex.wiring import bootstrap_cortex
        >>> registry = bootstrap_cortex()
        >>> orch = registry.get_orchestrator("TDDOrchestrator")
        >>> result = orch.generate_tests(...)
    """
    logger.info("🚀 Bootstrapping CORTEX wiring system...")

    try:
        registry = get_registry()

        # Validate wiring
        errors = registry.validate()
        if errors:
            logger.error(f"❌ Wiring validation failed: {errors}")
            raise ValueError(f"Invalid wiring specification: {errors}")

        logger.info(f"✅ CORTEX wired successfully: {registry.orchestrator_count} orchestrators")

        # Initialize trace database (after orchestrator wiring)
        _ensure_trace_database_initialized()

        return registry

    except Exception as e:
        logger.error(f"❌ CORTEX bootstrap failed: {e}")
        raise


def get_cortex() -> GitBackedRegistry:
    """
    Get existing CORTEX registry (shorthand for get_registry).

    Returns:
        GitBackedRegistry instance

    Example:
        >>> from cortex.wiring import get_cortex
        >>> registry = get_cortex()
        >>> orch = registry.get_orchestrator("MasterOrchestrator")
    """
    return get_registry()


def is_wired() -> bool:
    """
    Check if CORTEX has been wired.

    Returns:
        True if wired, False otherwise

    Example:
        >>> from cortex.wiring import is_wired
        >>> if not is_wired():
        ...     bootstrap_cortex()
    """
    try:
        registry = get_registry()
        return registry.is_wired()
    except Exception:
        return False


def get_wiring_hash() -> str:
    """
    Get SHA256 hash of wiring.yaml for change detection.

    Returns:
        Hash string (16 chars) or error message

    Example:
        >>> from cortex.wiring import get_wiring_hash
        >>> hash1 = get_wiring_hash()
        >>> # ... modify wiring.yaml ...
        >>> hash2 = get_wiring_hash()
        >>> if hash1 != hash2:
        ...     print("Wiring changed!")
    """
    try:
        registry = get_registry()
        return registry.get_wiring_hash()
    except Exception as e:
        logger.error(f"Failed to get wiring hash: {e}")
        return "error"
