"""
Domain Orchestrator - Domain-specific request routing and handling.

Routes requests to appropriate domain handlers with fallback and retry support.
"""

from typing import Dict, Any
from datetime import datetime


class DomainOrchestrator:
    """
    Routes requests to domain-specific handlers with resilience.
    """

    def __init__(self, max_retries: int = 3) -> None:
        """Initialize the domain orchestrator."""
        self.domain_registry: Dict[str, str] = {
            "api": "api_handler",
            "workflow": "workflow_handler",
            "diagnostic": "diagnostic_handler",
            "config": "config_handler",
        }
        self.max_retries = max_retries
        self.request_metrics: Dict[str, int] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
        }

    def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a request to the appropriate domain handler.
        
        Args:
            request: Request with domain, intent, parameters.
            
        Returns:
            Response from domain handler.
        """
        self.request_metrics["total_requests"] += 1
        
        domain = request.get("domain")
        fallback_domains = request.get("fallback_domains", [])
        retry_count = 0

        # Try primary domain
        if domain in self.domain_registry:
            try:
                response = self._handle_domain_request(domain, request)
                self.request_metrics["successful_requests"] += 1
                return response
            except Exception:
                retry_count += 1

        # Try fallback domains
        for fallback in fallback_domains:
            if fallback in self.domain_registry:
                try:
                    response = self._handle_domain_request(fallback, request)
                    response["used_fallback"] = True
                    self.request_metrics["successful_requests"] += 1
                    return response
                except Exception:
                    retry_count += 1

        # Fallback response
        self.request_metrics["failed_requests"] += 1
        return {
            "handled": False,
            "retry_count": retry_count,
            "error": "No suitable domain handler found",
        }

    def _handle_domain_request(self, domain: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request for a specific domain."""
        intent = request.get("intent", "unknown")
        return {
            "domain_handled": True,
            "domain": domain,
            "intent": intent,
            "handler": self.domain_registry[domain],
            "timestamp": datetime.now().isoformat(),
        }

    def get_metrics(self) -> Dict[str, int]:
        """Get request metrics."""
        return dict(self.request_metrics)
