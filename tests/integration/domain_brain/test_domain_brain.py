"""
Integration tests for domain brain - registry, introspection, implementations.
"""

import pytest
from typing import Dict, Any, List


class TestDomainRegistry:
    """Tests for domain registry and discovery."""

    def test_registry_initializes(self) -> None:
        """Test domain registry initialization."""
        from cortex_brain.domain.domain_registry import DomainRegistry
        
        registry = DomainRegistry()
        assert registry is not None

    def test_registry_registers_domain(self) -> None:
        """Test registering a domain type."""
        from cortex_brain.domain.domain_registry import DomainRegistry
        
        registry = DomainRegistry()
        registry.register("sales", {"name": "Sales"})
        assert registry.is_registered("sales") is True

    def test_registry_discovers_domains(self) -> None:
        """Test discovering registered domains."""
        from cortex_brain.domain.domain_registry import DomainRegistry
        
        registry = DomainRegistry()
        registry.register("sales", {"name": "Sales"})
        registry.register("support", {"name": "Support"})
        
        domains = registry.list_domains()
        assert len(domains) >= 2
        assert "sales" in domains
        assert "support" in domains

    def test_registry_retrieves_domain_metadata(self) -> None:
        """Test retrieving domain metadata."""
        from cortex_brain.domain.domain_registry import DomainRegistry
        
        registry = DomainRegistry()
        metadata = {"name": "Sales", "priority": "P1"}
        registry.register("sales", metadata)
        
        retrieved = registry.get_domain("sales")
        assert retrieved is not None
        assert retrieved["name"] == "Sales"

    def test_registry_unregisters_domain(self) -> None:
        """Test unregistering a domain."""
        from cortex_brain.domain.domain_registry import DomainRegistry
        
        registry = DomainRegistry()
        registry.register("sales", {"name": "Sales"})
        assert registry.is_registered("sales") is True
        
        registry.unregister("sales")
        assert registry.is_registered("sales") is False


class TestDomainIntrospection:
    """Tests for domain introspection and capabilities."""

    def test_introspection_initializes(self) -> None:
        """Test domain introspection initialization."""
        from cortex_brain.domain.domain_introspection import DomainIntrospection
        
        introspection = DomainIntrospection()
        assert introspection is not None

    def test_introspection_returns_capabilities(self) -> None:
        """Test retrieving domain capabilities."""
        from cortex_brain.domain.domain_introspection import DomainIntrospection
        
        introspection = DomainIntrospection()
        capabilities = introspection.get_capabilities("sales")
        
        assert capabilities is not None
        assert isinstance(capabilities, list)

    def test_introspection_returns_constraints(self) -> None:
        """Test retrieving domain constraints."""
        from cortex_brain.domain.domain_introspection import DomainIntrospection
        
        introspection = DomainIntrospection()
        constraints = introspection.get_constraints("sales")
        
        assert constraints is not None
        assert isinstance(constraints, list)

    def test_introspection_returns_requirements(self) -> None:
        """Test retrieving domain requirements."""
        from cortex_brain.domain.domain_introspection import DomainIntrospection
        
        introspection = DomainIntrospection()
        requirements = introspection.get_requirements("sales")
        
        assert requirements is not None
        assert isinstance(requirements, list)

    def test_introspection_validates_domain(self) -> None:
        """Test domain validation through introspection."""
        from cortex_brain.domain.domain_introspection import DomainIntrospection
        
        introspection = DomainIntrospection()
        is_valid = introspection.validate_domain("sales")
        
        assert is_valid is True


class TestDomainImplementations:
    """Tests for domain-specific implementations."""

    def test_sales_domain_implementation(self) -> None:
        """Test sales domain implementation."""
        from cortex_brain.domain.implementations.sales_domain import SalesDomain
        
        sales = SalesDomain()
        assert sales is not None
        assert sales.domain_type == "sales"

    def test_support_domain_implementation(self) -> None:
        """Test support domain implementation."""
        from cortex_brain.domain.implementations.support_domain import SupportDomain
        
        support = SupportDomain()
        assert support is not None
        assert support.domain_type == "support"

    def test_finance_domain_implementation(self) -> None:
        """Test finance domain implementation."""
        from cortex_brain.domain.implementations.finance_domain import FinanceDomain
        
        finance = FinanceDomain()
        assert finance is not None
        assert finance.domain_type == "finance"

    def test_operations_domain_implementation(self) -> None:
        """Test operations domain implementation."""
        from cortex_brain.domain.implementations.operations_domain import OperationsDomain
        
        operations = OperationsDomain()
        assert operations is not None
        assert operations.domain_type == "operations"

    def test_hr_domain_implementation(self) -> None:
        """Test HR domain implementation."""
        from cortex_brain.domain.implementations.hr_domain import HRDomain
        
        hr = HRDomain()
        assert hr is not None
        assert hr.domain_type == "hr"


class TestDomainModels:
    """Tests for domain models and data structures."""

    def test_domain_capability_model(self) -> None:
        """Test domain capability model."""
        from cortex_brain.domain.domain_models import DomainCapability
        
        capability = DomainCapability(
            name="request_processing",
            description="Process customer requests",
            complexity="medium"
        )
        
        assert capability.name == "request_processing"
        assert capability.description == "Process customer requests"

    def test_domain_constraint_model(self) -> None:
        """Test domain constraint model."""
        from cortex_brain.domain.domain_models import DomainConstraint
        
        constraint = DomainConstraint(
            name="response_time",
            value="<5s",
            severity="high"
        )
        
        assert constraint.name == "response_time"
        assert constraint.value == "<5s"

    def test_domain_metadata_model(self) -> None:
        """Test domain metadata model."""
        from cortex_brain.domain.domain_models import DomainMetadata
        
        metadata = DomainMetadata(
            domain_id="sales",
            name="Sales Domain",
            version="1.0"
        )
        
        assert metadata.domain_id == "sales"
        assert metadata.name == "Sales Domain"


class TestDomainIntegration:
    """Integration tests for domain brain components."""

    def test_registry_and_introspection_integration(self) -> None:
        """Test registry and introspection working together."""
        from cortex_brain.domain.domain_registry import DomainRegistry
        from cortex_brain.domain.domain_introspection import DomainIntrospection
        
        registry = DomainRegistry()
        introspection = DomainIntrospection()
        
        # Register domain
        registry.register("sales", {"name": "Sales"})
        
        # Introspect capabilities
        capabilities = introspection.get_capabilities("sales")
        assert capabilities is not None

    def test_domain_factory_creates_domains(self) -> None:
        """Test domain brain factory creates domain instances."""
        from cortex_brain.domain.domain_factory import DomainFactory
        
        factory = DomainFactory()
        sales = factory.create_domain("sales")
        
        assert sales is not None
        assert sales.domain_type == "sales"

    def test_all_domains_discoverable(self) -> None:
        """Test all domains are discoverable through registry."""
        from cortex_brain.domain.domain_registry import DomainRegistry
        
        registry = DomainRegistry()
        domains = registry.list_all_available_domains()
        
        assert len(domains) >= 5
        assert "sales" in domains
        assert "support" in domains
        assert "finance" in domains

    def test_domain_registration_performance(self) -> None:
        """Test domain registration performance."""
        from cortex_brain.domain.domain_registry import DomainRegistry
        import time
        
        registry = DomainRegistry()
        
        start = time.time()
        for i in range(100):
            registry.register(f"domain-{i}", {"name": f"Domain {i}"})
        elapsed = time.time() - start
        
        # Should complete in reasonable time (<1 second)
        assert elapsed < 1.0

    def test_domain_discovery_performance(self) -> None:
        """Test domain discovery performance."""
        from cortex_brain.domain.domain_registry import DomainRegistry
        import time
        
        registry = DomainRegistry()
        for i in range(50):
            registry.register(f"domain-{i}", {"name": f"Domain {i}"})
        
        start = time.time()
        for _ in range(1000):
            domains = registry.list_domains()
        elapsed = time.time() - start
        
        # Should complete in reasonable time (<100ms)
        assert elapsed < 0.1
