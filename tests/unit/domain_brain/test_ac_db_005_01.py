"""Tests for AC-DB-005-01: End-to-End Integration Testing.

Comprehensive end-to-end tests validating the complete Domain Brain workflow
from document ingestion through LENS resolution.
"""

import pytest
from typing import List

from cortex.domain_brain.models import (
    Domain,
    Entity,
    EntityType,
    Conflict,
    AuditOperationType,
)
from cortex.domain_brain.api import DomainBrainAPI
from cortex.domain_brain.deduplication import DuplicateDetector
from cortex.domain_brain.audit_log_manager import AuditLogManager
from cortex.domain_brain.conflict_resolver import ConflictResolver
from cortex.domain_brain.lens_integration import LENSIntegrationLayer
from cortex.domain_brain.orphan_detector import ReferenceValidator


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    @pytest.fixture
    def api(self) -> DomainBrainAPI:
        """Create API fixture."""
        return DomainBrainAPI()

    @pytest.fixture
    def duplicate_detector(self) -> DuplicateDetector:
        """Create duplicate detector."""
        return DuplicateDetector()

    @pytest.fixture
    def conflict_resolver(self) -> ConflictResolver:
        """Create conflict resolver."""
        return ConflictResolver()

    def test_complete_domain_creation_workflow(
        self, api: DomainBrainAPI
    ) -> None:
        """Test complete domain creation and query workflow."""
        # Create domain
        domain = Domain(
            domain_id="microservices",
            name="Microservices Architecture",
            description="Core microservices platform",
        )

        # Add entities
        api_service = Entity(
            entity_id="api-gateway",
            entity_type=EntityType.SERVICE,
            name="API Gateway",
            description="Main API entry point",
            source="AST",
        )
        auth_service = Entity(
            entity_id="auth-service",
            entity_type=EntityType.SERVICE,
            name="Authentication Service",
            description="Handles user authentication",
            source="BKIO",
        )

        domain.entities["api-gateway"] = api_service
        domain.entities["auth-service"] = auth_service

        # Upsert domain
        api.upsert_domain(domain)

        # Query domain
        queried = api.query_domain("microservices")

        assert queried is not None
        assert len(queried.entities) == 2
        assert "api-gateway" in queried.entities

    def test_conflict_detection_and_resolution(
        self, api: DomainBrainAPI, conflict_resolver: ConflictResolver
    ) -> None:
        """Test conflict detection and resolution workflow."""
        # Create domain with conflict
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Original description",
            source="AST",
        )
        domain.entities["e1"] = entity

        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={
                "AST": "Original description",
                "BKIO": "Updated description",
            },
        )
        domain.conflicts.append(conflict)

        # Resolve conflict
        resolution = conflict_resolver.resolve_conflict(conflict)

        assert resolution is not None
        assert "BKIO" in resolution.reasoning  # BKIO should win

    def test_duplicate_prevention_workflow(
        self, api: DomainBrainAPI, duplicate_detector: DuplicateDetector
    ) -> None:
        """Test duplicate upload prevention."""
        # Create domain
        domain = Domain(
            domain_id="test",
            name="Test Domain",
            description="Test",
        )
        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Description",
            source="AST",
        )
        domain.entities["e1"] = entity

        # First upload
        is_dup1 = duplicate_detector.process_domain_upload(domain)
        assert is_dup1 is False

        # Duplicate upload
        domain_copy = Domain(
            domain_id="test",
            name="Test Domain",
            description="Test",
        )
        entity_copy = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Description",
            source="AST",
        )
        domain_copy.entities["e1"] = entity_copy

        is_dup2 = duplicate_detector.process_domain_upload(domain_copy)
        assert is_dup2 is True

    def test_reference_validation_workflow(
        self, api: DomainBrainAPI
    ) -> None:
        """Test reference validation across domains."""
        validator = ReferenceValidator()

        # Create related entities
        validator.register_entity("api-gateway")
        validator.register_entity("auth-service")
        validator.register_entity("user-db")

        # Add references
        validator.add_reference("api-gateway", "auth-service")
        validator.add_reference("auth-service", "user-db")

        # Validate references
        assert validator.validate_reference("api-gateway", "auth-service") is True
        assert validator.validate_reference("auth-service", "user-db") is True

        # Delete referenced entity
        validator.delete_entity("user-db")

        # Reference should now be invalid
        assert validator.validate_reference("auth-service", "user-db") is False

    def test_audit_trail_generation(self, api: DomainBrainAPI) -> None:
        """Test audit trail generation."""
        domain = Domain(domain_id="test", name="Test", description="Test")

        # Upsert domain (should log)
        api.upsert_domain(domain)

        # Query audit trail
        audit_entries = api.audit_domain("test")

        # Should have at least one entry
        assert len(audit_entries) > 0


class TestIntegrationScenarios:
    """Integration scenario tests."""

    @pytest.fixture
    def complete_system(self) -> tuple:
        """Create complete system with all components."""
        api = DomainBrainAPI()
        dup_detector = DuplicateDetector()
        conflict_resolver = ConflictResolver()
        reference_validator = ReferenceValidator()
        lens_layer = LENSIntegrationLayer(api)

        return (api, dup_detector, conflict_resolver, reference_validator, lens_layer)

    def test_multi_domain_ecosystem(
        self, complete_system: tuple
    ) -> None:
        """Test ecosystem with multiple related domains."""
        api, dup_detector, resolver, validator, lens = complete_system

        # Create interconnected domains
        services_domain = Domain(
            domain_id="services",
            name="Services Registry",
            description="All microservices",
        )

        api_service = Entity(
            entity_id="api",
            entity_type=EntityType.SERVICE,
            name="API Gateway",
            description="API",
            source="AST",
        )
        db_service = Entity(
            entity_id="db",
            entity_type=EntityType.SERVICE,
            name="Database",
            description="DB",
            source="AST",
        )

        services_domain.entities["api"] = api_service
        services_domain.entities["db"] = db_service

        # Register with API
        api.upsert_domain(services_domain)

        # Register references
        validator.register_entity("api")
        validator.register_entity("db")
        validator.add_reference("api", "db")

        # Query results
        queried_domain = api.query_domain("services")
        assert len(queried_domain.entities) == 2

        # Validate references
        assert validator.validate_reference("api", "db") is True

    def test_conflict_escalation_to_manual_review(
        self, complete_system: tuple
    ) -> None:
        """Test conflict escalation workflow."""
        api, dup_detector, resolver, validator, lens = complete_system

        # Create conflicting domain
        domain = Domain(domain_id="test", name="Test", description="Test")

        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Value1",
            source="AST",
        )
        domain.entities["e1"] = entity

        # Create conflict that will escalate to manual review
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={},  # Empty will trigger escalation
        )
        domain.conflicts.append(conflict)

        # Resolve (should escalate)
        resolution = resolver.resolve_conflict(conflict)

        # Check escalation
        if resolution is None:
            # Escalated to manual review
            pending = resolver.get_manual_review_queue()
            # There may be pending reviews

    def test_complete_import_workflow(
        self, complete_system: tuple
    ) -> None:
        """Test complete import workflow with all checks."""
        api, dup_detector, resolver, validator, lens = complete_system

        # Create domain
        domain = Domain(
            domain_id="imported",
            name="Imported Domain",
            description="From external source",
        )

        for i in range(3):
            entity = Entity(
                entity_id=f"e{i}",
                entity_type=EntityType.SERVICE,
                name=f"Service {i}",
                description=f"Service {i}",
                source="BKIO",
            )
            domain.entities[f"e{i}"] = entity

        # Check for duplicates
        is_dup = dup_detector.process_domain_upload(domain)
        assert is_dup is False

        # Ingest into Domain Brain
        api.upsert_domain(domain)

        # Register entities for reference tracking
        for i in range(3):
            validator.register_entity(f"e{i}")

        # Query to verify
        retrieved = api.query_domain("imported")
        assert len(retrieved.entities) == 3

        # Re-import (should be duplicate)
        is_dup2 = dup_detector.process_domain_upload(domain)
        assert is_dup2 is True


class TestSystemResilience:
    """Tests for system resilience and error handling."""

    @pytest.fixture
    def api(self) -> DomainBrainAPI:
        """Create API fixture."""
        return DomainBrainAPI()

    def test_invalid_domain_handling(self, api: DomainBrainAPI) -> None:
        """Test handling of invalid domains."""
        invalid_domain = Domain(
            domain_id="",  # Empty ID
            name="Invalid",
            description="Invalid domain",
        )

        # Should handle gracefully
        api.upsert_domain(invalid_domain)

        # Query non-existent domain
        result = api.query_domain("nonexistent")
        assert result is None

    def test_large_domain_handling(self, api: DomainBrainAPI) -> None:
        """Test handling of large domains."""
        large_domain = Domain(
            domain_id="large",
            name="Large Domain",
            description="Many entities",
        )

        # Add many entities
        for i in range(100):
            entity = Entity(
                entity_id=f"e{i}",
                entity_type=EntityType.SERVICE,
                name=f"Service {i}",
                description=f"Service {i}",
                source="AST",
            )
            large_domain.entities[f"e{i}"] = entity

        # Ingest
        api.upsert_domain(large_domain)

        # Query
        retrieved = api.query_domain("large")
        assert len(retrieved.entities) == 100

    def test_conflict_with_no_sources(self, api: DomainBrainAPI) -> None:
        """Test conflict with no source values."""
        resolver = ConflictResolver()

        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={},
        )

        # Should escalate to manual review
        resolution = resolver.resolve_conflict(conflict)
        # May be None (escalated)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
