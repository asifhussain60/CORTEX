"""
CORTEX Bootstrap - Initialize Git-backed wiring system.

Authority: _workspaces/cortex-plan/migration-phases-plan.yaml (Phase 3)
Rule: CORE-035 (Single Canonical Implementation)

Entry point for CORTEX system initialization.
"""

from typing import Optional
import logging

from cortex.wiring.registry import GitBackedRegistry, get_registry

logger = logging.getLogger(__name__)


def bootstrap_cortex() -> GitBackedRegistry:
    """
    Bootstrap CORTEX orchestrator wiring system.
    
    This is the main entry point for initializing CORTEX. It:
    1. Loads wiring.yaml specification
    2. Registers all 23 orchestrators
    3. Validates wiring integrity
    4. Returns registry for orchestrator access
    
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
