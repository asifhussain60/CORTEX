"""
CORTEX Bootstrap Module - Mandatory Startup Validation Hook

This module is imported by cortex/__init__.py to ensure all startup
validations run before any orchestrator code is executed.

AC-PERMANENT-FIX-015: Prevent repeated discovery of same critical issues
by running mandatory startup validation on first import.
"""

import logging
import sys

logger = logging.getLogger(__name__)


def bootstrap_cortex() -> bool:
    """
    Bootstrap CORTEX with mandatory startup validation.

    Called automatically on first import of cortex module.

    Returns:
        True if bootstrap successful, False if critical issues detected.
    """
    try:
        # Import validator (this also triggers auto-validation)
        from cortex.infrastructure.startup_validator import (
            run_startup_validation,
            get_startup_validator,
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

    except Exception as e:
        logger.exception("CORTEX bootstrap failed with exception")
        return False

    return True


# Run bootstrap on import
_bootstrap_success = bootstrap_cortex()
