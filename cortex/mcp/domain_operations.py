"""
Domain Operations MCP Tools

Exposes DomainOrchestrator capabilities via MCP for SaaS deployment.
Provides domain-specific operation execution, validation, and registration.

AC-ID: ARCH-007-DOMAIN-MCP
Author: Asif Hussain
"""

import logging
from typing import Dict, Any, Optional, List

from cortex.mcp.decorator import mcp_tool

logger = logging.getLogger(__name__)


@mcp_tool(
    name="cortex_domain_execute",
    description="Execute domain-specific operation through DomainOrchestrator",
    category="domain"
)
def cortex_domain_execute(
    domain_id: str,
    operation: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute domain-specific operation.
    
    Args:
        domain_id: Target domain identifier (business, technical, governance, etc.)
        operation: Operation type (create, modify, fix, analyze, optimize, integrate)
        params: Operation parameters as dictionary
        
    Returns:
        Operation result with status and data
        
    Examples:
        cortex_domain_execute("business", "create", {"entity": "Customer"})
        cortex_domain_execute("technical", "analyze", {"scope": "codebase"})
        cortex_domain_execute("governance", "fix", {"rule": "CORE-035"})
    """
    try:
        from cortex.domain_orchestrators.domain_orchestrator import DomainOrchestrator
        
        orchestrator = DomainOrchestrator()
        result = orchestrator.execute(domain_id, operation, params)
        
        return {
            "status": "success",
            "domain_id": domain_id,
            "operation": operation,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Domain operation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "domain_id": domain_id,
            "operation": operation,
            "error": str(e)
        }


@mcp_tool(
    name="cortex_domain_list",
    description="List all registered domains and their capabilities",
    category="domain"
)
def cortex_domain_list() -> Dict[str, Any]:
    """
    List all registered domains and available operations.
    
    Returns:
        Dictionary with registered domains and their handlers
    """
    try:
        from cortex.domain_orchestrators.domain_orchestrator import DomainOrchestrator
        
        orchestrator = DomainOrchestrator()
        domains = list(orchestrator.registry.domains.keys())
        
        # Available operations from DomainRegistry
        operations = ["create", "modify", "fix", "analyze", "optimize", "integrate"]
        
        return {
            "status": "success",
            "domains": domains,
            "operations": operations,
            "count": len(domains)
        }
        
    except Exception as e:
        logger.error(f"Failed to list domains: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "domains": [],
            "operations": []
        }


@mcp_tool(
    name="cortex_domain_register",
    description="Register new domain handler for domain-specific operations",
    category="domain"
)
def cortex_domain_register(
    domain_id: str,
    domain_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Register new domain with DomainOrchestrator.
    
    Args:
        domain_id: Unique domain identifier
        domain_path: Path to domain handler or configuration
        metadata: Optional domain metadata
        
    Returns:
        Registration result
    """
    try:
        from cortex.domain_orchestrators.domain_orchestrator import DomainOrchestrator
        
        orchestrator = DomainOrchestrator()
        orchestrator.registry.domains[domain_id] = domain_path
        
        return {
            "status": "success",
            "domain_id": domain_id,
            "domain_path": domain_path,
            "metadata": metadata or {},
            "message": f"Domain '{domain_id}' registered successfully"
        }
        
    except Exception as e:
        logger.error(f"Domain registration failed: {e}", exc_info=True)
        return {
            "status": "error",
            "domain_id": domain_id,
            "error": str(e)
        }


@mcp_tool(
    name="cortex_domain_validate",
    description="Validate parameters for domain operation before execution",
    category="domain"
)
def cortex_domain_validate(
    domain_id: str,
    operation: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate parameters for domain operation.
    
    Args:
        domain_id: Target domain
        operation: Operation type
        params: Parameters to validate
        
    Returns:
        Validation result with errors if invalid
    """
    try:
        from cortex.domain_orchestrators.domain_orchestrator import DomainOrchestrator
        
        orchestrator = DomainOrchestrator()
        handler = orchestrator.registry.get_handler(operation)
        
        if not handler:
            return {
                "status": "error",
                "valid": False,
                "error": f"Unknown operation: {operation}",
                "domain_id": domain_id
            }
        
        is_valid = handler.validate(params)
        
        return {
            "status": "success",
            "valid": is_valid,
            "domain_id": domain_id,
            "operation": operation,
            "message": "Parameters valid" if is_valid else "Invalid parameters"
        }
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "valid": False,
            "domain_id": domain_id,
            "error": str(e)
        }


# Export all domain tools
__all__ = [
    "cortex_domain_execute",
    "cortex_domain_list",
    "cortex_domain_register",
    "cortex_domain_validate",
]

