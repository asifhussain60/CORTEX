"""
Domain Factory - Create domain instances.
"""

from typing import Any


class DomainFactory:
    """Factory for creating domain instances."""

    def create_domain(self, domain_id: str) -> Any:
        """
        Create a domain instance.
        
        Args:
            domain_id: Domain identifier.
            
        Returns:
            Domain instance.
        """
        if domain_id == "sales":
            from cortex_brain.domain.implementations.sales_domain import SalesDomain
            return SalesDomain()
        elif domain_id == "support":
            from cortex_brain.domain.implementations.support_domain import SupportDomain
            return SupportDomain()
        elif domain_id == "finance":
            from cortex_brain.domain.implementations.finance_domain import FinanceDomain
            return FinanceDomain()
        elif domain_id == "operations":
            from cortex_brain.domain.implementations.operations_domain import OperationsDomain
            return OperationsDomain()
        elif domain_id == "hr":
            from cortex_brain.domain.implementations.hr_domain import HRDomain
            return HRDomain()
        else:
            raise ValueError(f"Unknown domain: {domain_id}")
