"""
Domain Introspection - Inspect capabilities, constraints, and requirements.
"""

from typing import List, Dict


class DomainIntrospection:
    """Provides introspection for domain capabilities and constraints."""

    def __init__(self) -> None:
        """Initialize domain introspection."""
        self.capabilities_map: Dict[str, List[str]] = {
            "sales": ["opportunity_management", "pipeline_tracking", "forecasting"],
            "support": ["ticket_management", "routing", "resolution_tracking"],
            "finance": ["budgeting", "forecasting", "reporting"],
            "operations": ["planning", "scheduling", "optimization"],
            "hr": ["recruitment", "onboarding", "performance_management"],
        }
        
        self.constraints_map: Dict[str, List[str]] = {
            "sales": ["max_pipeline_size", "forecast_accuracy_limit"],
            "support": ["sla_compliance", "escalation_time"],
            "finance": ["budget_variance", "audit_frequency"],
            "operations": ["capacity_limit", "resource_availability"],
            "hr": ["headcount_approval", "budget_constraints"],
        }
        
        self.requirements_map: Dict[str, List[str]] = {
            "sales": ["crm_integration", "real_time_updates"],
            "support": ["ticket_system", "knowledge_base"],
            "finance": ["accounting_system", "compliance_tools"],
            "operations": ["resource_system", "scheduling_system"],
            "hr": ["employee_system", "compliance_system"],
        }

    def get_capabilities(self, domain_id: str) -> List[str]:
        """
        Get domain capabilities.
        
        Args:
            domain_id: Domain identifier.
            
        Returns:
            List of capabilities.
        """
        return self.capabilities_map.get(domain_id, [])

    def get_constraints(self, domain_id: str) -> List[str]:
        """
        Get domain constraints.
        
        Args:
            domain_id: Domain identifier.
            
        Returns:
            List of constraints.
        """
        return self.constraints_map.get(domain_id, [])

    def get_requirements(self, domain_id: str) -> List[str]:
        """
        Get domain requirements.
        
        Args:
            domain_id: Domain identifier.
            
        Returns:
            List of requirements.
        """
        return self.requirements_map.get(domain_id, [])

    def validate_domain(self, domain_id: str) -> bool:
        """
        Validate a domain exists and is properly configured.
        
        Args:
            domain_id: Domain identifier.
            
        Returns:
            True if valid.
        """
        return (
            domain_id in self.capabilities_map and
            domain_id in self.constraints_map and
            domain_id in self.requirements_map
        )

    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """Get all capabilities by domain."""
        return self.capabilities_map.copy()

    def get_all_constraints(self) -> Dict[str, List[str]]:
        """Get all constraints by domain."""
        return self.constraints_map.copy()

    def get_all_requirements(self) -> Dict[str, List[str]]:
        """Get all requirements by domain."""
        return self.requirements_map.copy()
