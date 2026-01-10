"""
MasterOrchestrator Registration System

CRITICAL DESIGN PRINCIPLE:
MasterOrchestrator is IN CHARGE of all CORTEX operations.
This module provides decorators and utilities to enforce this.

All orchestrators MUST:
1. Register with MasterOrchestrator via @register_with_master
2. Use @require_master_routing on execute() method
3. Cannot execute independently without MasterOrchestrator context

AC-IDs: AC-SCAFFOLD-003, AC-ORCH-006

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import functools
import logging
from typing import Dict, Any, List, Callable, Optional, Type
from dataclasses import dataclass, field

logger = logging.getLogger("cortex.orchestrators.registration")


class MasterBypassError(Exception):
    """
    Raised when an orchestrator is invoked directly without MasterOrchestrator routing.
    
    This is a CRITICAL error - MasterOrchestrator is IN CHARGE and must not be bypassed.
    """
    pass


class RegistrationError(Exception):
    """Raised when orchestrator registration fails."""
    pass


@dataclass
class OrchestratorRegistration:
    """Registration metadata for an orchestrator."""
    name: str
    domain: str
    category: str
    routing_patterns: List[str]
    version: str
    class_ref: Optional[Type] = None
    registered_at: Optional[str] = None


class OrchestratorRegistry:
    """
    Central registry for all orchestrators.
    
    MasterOrchestrator uses this registry for routing decisions.
    Orchestrators register themselves via the @register_with_master decorator.
    """
    
    _instance = None
    _orchestrators: Dict[str, OrchestratorRegistration] = {}
    _pattern_map: Dict[str, str] = {}  # pattern -> orchestrator_name
    
    def __new__(cls):
        """Singleton pattern - one registry for entire application."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._orchestrators = {}
            cls._pattern_map = {}
        return cls._instance
    
    def register(self, registration: OrchestratorRegistration) -> None:
        """
        Register an orchestrator.
        
        Args:
            registration: OrchestratorRegistration with orchestrator metadata
            
        Raises:
            RegistrationError: If registration fails
        """
        if registration.name in self._orchestrators:
            logger.warning(f"Orchestrator {registration.name} already registered, updating...")
        
        self._orchestrators[registration.name] = registration
        
        # Map routing patterns
        for pattern in registration.routing_patterns:
            if pattern in self._pattern_map:
                existing = self._pattern_map[pattern]
                logger.warning(
                    f"Routing pattern '{pattern}' already mapped to {existing}, "
                    f"overwriting with {registration.name}"
                )
            self._pattern_map[pattern] = registration.name
        
        logger.info(
            f"Registered orchestrator: {registration.name} "
            f"(domain={registration.domain}, patterns={registration.routing_patterns})"
        )
    
    def get(self, name: str) -> Optional[OrchestratorRegistration]:
        """Get orchestrator registration by name."""
        return self._orchestrators.get(name)
    
    def get_by_pattern(self, pattern: str) -> Optional[OrchestratorRegistration]:
        """Get orchestrator registration by routing pattern."""
        orchestrator_name = self._pattern_map.get(pattern)
        if orchestrator_name:
            return self._orchestrators.get(orchestrator_name)
        return None
    
    def get_all(self) -> Dict[str, OrchestratorRegistration]:
        """Get all registered orchestrators."""
        return self._orchestrators.copy()
    
    def get_by_domain(self, domain: str) -> List[OrchestratorRegistration]:
        """Get all orchestrators for a domain."""
        return [
            reg for reg in self._orchestrators.values()
            if reg.domain.lower() == domain.lower()
        ]
    
    def is_registered(self, name: str) -> bool:
        """Check if orchestrator is registered."""
        return name in self._orchestrators


# Global registry instance
_registry = OrchestratorRegistry()


def get_registry() -> OrchestratorRegistry:
    """Get the global orchestrator registry."""
    return _registry


def register_with_master(
    name: str,
    domain: str,
    category: str,
    routing_patterns: List[str],
    version: str = "1.0.0"
) -> Callable:
    """
    Decorator to register an orchestrator with MasterOrchestrator.
    
    CRITICAL: All orchestrators MUST use this decorator.
    This ensures MasterOrchestrator knows about all orchestrators
    and can route requests appropriately.
    
    AC-SCAFFOLD-003: MasterOrchestrator Registration
    
    Args:
        name: Orchestrator name
        domain: Domain (e.g., 'finance', 'healthcare')
        category: Category (planning, execution, analysis, etc.)
        routing_patterns: List of patterns that route to this orchestrator
        version: Orchestrator version
        
    Returns:
        Decorated class with registration metadata
        
    Example:
        @register_with_master(
            name="Finance Report",
            domain="finance",
            category="execution",
            routing_patterns=["finance", "financial report"],
            version="1.0.0"
        )
        class FinanceReportOrchestrator(BaseOrchestratorV4):
            pass
    """
    def decorator(cls: Type) -> Type:
        # Create registration
        registration = OrchestratorRegistration(
            name=name,
            domain=domain,
            category=category,
            routing_patterns=routing_patterns,
            version=version,
            class_ref=cls
        )
        
        # Store registration metadata on class
        cls._master_registration = {
            "name": name,
            "domain": domain,
            "category": category,
            "routing_patterns": routing_patterns,
            "version": version
        }
        
        # Register with global registry
        _registry.register(registration)
        
        return cls
    
    return decorator


def require_master_routing(method: Callable) -> Callable:
    """
    Decorator to enforce MasterOrchestrator routing.
    
    CRITICAL: Apply this to the execute() method of all orchestrators.
    This prevents direct execution - all requests MUST come through
    MasterOrchestrator.
    
    The decorator checks for '_master_routed' flag in context.
    If missing, raises MasterBypassError.
    
    AC-SCAFFOLD-003: MasterOrchestrator Registration
    AC-ORCH-006: MasterOrchestrator as Central Controller
    
    Args:
        method: Method to decorate (typically execute())
        
    Returns:
        Wrapped method with master routing check
        
    Example:
        class MyOrchestrator(BaseOrchestratorV4):
            @require_master_routing
            def execute(self, context: Dict[str, Any]) -> OrchestratorResult:
                # This will only execute if routed through MasterOrchestrator
                pass
    """
    @functools.wraps(method)
    def wrapper(self, context: Dict[str, Any], *args, **kwargs):
        # Check for master routing flag
        if not context.get("_master_routed", False):
            class_name = self.__class__.__name__
            raise MasterBypassError(
                f"{class_name} must be invoked through MasterOrchestrator. "
                f"Direct execution is not permitted. "
                f"Ensure requests are routed through the MasterOrchestrator pipeline."
            )
        
        # Validate correlation_id for audit trail
        if "correlation_id" not in context:
            logger.warning(
                f"{self.__class__.__name__}.execute() called without correlation_id. "
                "Audit trail may be incomplete."
            )
        
        return method(self, context, *args, **kwargs)
    
    # Mark as requiring master routing (for inspection)
    wrapper._requires_master_routing = True
    
    return wrapper


def validate_orchestrator_registration(cls: Type) -> Dict[str, Any]:
    """
    Validate that an orchestrator class is properly registered.
    
    Checks:
    1. Has @register_with_master decorator
    2. Has @require_master_routing on execute()
    3. Registration metadata is complete
    
    Args:
        cls: Orchestrator class to validate
        
    Returns:
        Dict with validation results
    """
    issues = []
    warnings = []
    
    # Check for registration decorator
    if not hasattr(cls, "_master_registration"):
        issues.append("CRITICAL: Missing @register_with_master decorator")
    else:
        registration = cls._master_registration
        
        # Validate required fields
        required_fields = ["name", "domain", "category", "routing_patterns"]
        for field in required_fields:
            if field not in registration or not registration[field]:
                issues.append(f"Missing required registration field: {field}")
    
    # Check execute method for master routing requirement
    if hasattr(cls, "execute"):
        execute_method = getattr(cls, "execute")
        if not getattr(execute_method, "_requires_master_routing", False):
            issues.append(
                "CRITICAL: execute() method missing @require_master_routing decorator"
            )
    else:
        warnings.append("No execute() method found - may be inherited")
    
    # Check class inheritance
    base_classes = [base.__name__ for base in cls.__mro__]
    if "BaseOrchestratorV4" not in base_classes and "BaseOrchestrator" not in base_classes:
        warnings.append(
            "Orchestrator does not inherit from BaseOrchestratorV4 or BaseOrchestrator"
        )
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "class_name": cls.__name__
    }


def create_master_context(
    request: str,
    correlation_id: str,
    governance_rules: Dict[str, Any] = None,
    todo_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a valid MasterOrchestrator context for routing.
    
    This is the ONLY way to create a valid execution context.
    Use this in MasterOrchestrator when routing to child orchestrators.
    
    Args:
        request: Original user request
        correlation_id: Audit trail ID
        governance_rules: Merged 4-tier governance rules
        todo_id: Associated todo ID from TodoManager
        **kwargs: Additional context fields
        
    Returns:
        Dict with valid master routing context
    """
    return {
        "request": request,
        "correlation_id": correlation_id,
        "governance_rules": governance_rules or {},
        "todo_id": todo_id,
        "_master_routed": True,  # CRITICAL: This flag enables execution
        **kwargs
    }
