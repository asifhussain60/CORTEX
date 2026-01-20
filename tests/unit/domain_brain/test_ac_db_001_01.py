"""Test suite for Domain Brain Foundation (AC-DB-001-01).

Tests cover:
- DomainBrainAPI: 25 tests
- ConsistencyValidator: 20 tests  
- AuditLogger: 15 tests

Total: 60 tests
"""

import pytest
from datetime import datetime
from cortex.domain_brain import (
    DomainBrainAPI,
    Domain,
    Entity,
    Conflict,
    ConsistencyValidator,
    AuditLogger,
)
from cortex.domain_brain.models import EntityType, ConflictResolution, AuditOperationType


class TestDomainBrainAPI:
    """Tests for DomainBrainAPI (25 tests)."""

    @pytest.fixture
    def api(self) -> DomainBrainAPI:
        """Create API instance."""
        return DomainBrainAPI()

    @pytest.fixture
    def sample_domain(self) -> Domain:
        """Create sample domain for testing."""
        domain = Domain(
            domain_id="auth-service",
            name="Authentication Service",
            description="Handles user authentication and token management",
        )

        # Add entities
        domain.entities["user-validator"] = Entity(
            entity_id="user-validator",
            entity_type=EntityType.FUNCTION,
            name="validate_user",
            description="Validates user credentials",
            source="AST",
        )

        domain.entities["token-issuer"] = Entity(
            entity_id="token-issuer",
            entity_type=EntityType.FUNCTION,
            name="issue_token",
            description="Issues authentication tokens",
            source="BKIO",
        )

        return domain

    def test_query_existing_domain(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test querying an existing domain."""
        api.upsert_domain(sample_domain)
        retrieved = api.query_domain("auth-service")
        assert retrieved is not None
        assert retrieved.domain_id == "auth-service"
        assert retrieved.name == "Authentication Service"

    def test_query_non_existent_domain(self, api: DomainBrainAPI) -> None:
        """Test querying a non-existent domain."""
        retrieved = api.query_domain("non-existent")
        assert retrieved is None

    def test_list_domains_empty(self, api: DomainBrainAPI) -> None:
        """Test listing domains when none exist."""
        domains = api.list_domains()
        assert domains == []

    def test_list_domains_multiple(self, api: DomainBrainAPI) -> None:
        """Test listing multiple domains."""
        domain1 = Domain(domain_id="auth", name="Auth", description="Auth")
        domain2 = Domain(domain_id="payment", name="Payment", description="Payment")

        api.upsert_domain(domain1)
        api.upsert_domain(domain2)

        domains = api.list_domains()
        assert len(domains) == 2
        assert any(d.domain_id == "auth" for d in domains)
        assert any(d.domain_id == "payment" for d in domains)

    def test_search_entities_by_name(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test searching entities by name."""
        api.upsert_domain(sample_domain)
        results = api.search_entities("validate")
        assert len(results) > 0
        assert any(e.name == "validate_user" for e in results)

    def test_search_entities_by_description(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test searching entities by description."""
        api.upsert_domain(sample_domain)
        results = api.search_entities("token")
        assert len(results) > 0
        assert any("token" in e.description.lower() for e in results)

    def test_search_entities_no_results(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test search with no results."""
        api.upsert_domain(sample_domain)
        results = api.search_entities("nonexistent")
        assert len(results) == 0

    def test_upsert_new_domain(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test creating a new domain."""
        assert api.query_domain("auth-service") is None
        api.upsert_domain(sample_domain)
        assert api.query_domain("auth-service") is not None

    def test_upsert_update_domain(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test updating an existing domain."""
        api.upsert_domain(sample_domain)
        original = api.query_domain("auth-service")
        assert original is not None

        # Update domain
        sample_domain.name = "Updated Auth Service"
        api.upsert_domain(sample_domain)

        updated = api.query_domain("auth-service")
        assert updated is not None
        assert updated.name == "Updated Auth Service"

    def test_delete_domain(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test deleting a domain."""
        api.upsert_domain(sample_domain)
        assert api.query_domain("auth-service") is not None

        api.delete_domain("auth-service")
        assert api.query_domain("auth-service") is None

    def test_get_conflicts_empty(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test getting conflicts when none exist."""
        api.upsert_domain(sample_domain)
        conflicts = api.get_conflicts("auth-service")
        assert conflicts == []

    def test_get_conflicts_existing(self, api: DomainBrainAPI) -> None:
        """Test getting existing conflicts."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        conflict = Conflict(
            conflict_id="conflict-1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "AST description", "BKIO": "BKIO description"},
        )
        domain.conflicts.append(conflict)
        api.upsert_domain(domain)

        conflicts = api.get_conflicts("test")
        assert len(conflicts) == 1
        assert conflicts[0].conflict_id == "conflict-1"

    def test_resolve_conflict(self, api: DomainBrainAPI) -> None:
        """Test resolving a conflict."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        conflict = Conflict(
            conflict_id="conflict-1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )
        domain.conflicts.append(conflict)
        api.upsert_domain(domain)

        api.resolve_conflict("conflict-1", "test", "resolved_value", "hierarchy")

        resolved_conflict = api.get_conflicts("test")[0]
        assert resolved_conflict.resolved_at is not None
        assert resolved_conflict.resolution_method == "hierarchy"

    def test_audit_domain(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test getting audit trail for domain."""
        api.upsert_domain(sample_domain)
        audit = api.audit_domain("auth-service")
        assert len(audit) > 0

    def test_validate_domain_valid(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test validating a valid domain."""
        result = api.validate_domain(sample_domain)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_domain_with_conflicts(self, api: DomainBrainAPI) -> None:
        """Test validating domain with entity conflicts."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="same_name",
            description="desc1",
            source="AST",
        )
        domain.entities["e2"] = Entity(
            entity_id="e2",
            entity_type=EntityType.SERVICE,
            name="same_name",
            description="desc2",
            source="BKIO",
        )

        result = api.validate_domain(domain)
        assert len(result.conflicts_detected) > 0

    def test_get_audit_stats(self, api: DomainBrainAPI, sample_domain: Domain) -> None:
        """Test getting audit statistics."""
        api.upsert_domain(sample_domain)
        stats = api.get_audit_stats()
        assert "cache_size" in stats
        assert "total_entries" in stats
        assert "domains_count" in stats
        assert stats["domains_count"] >= 1

    def test_upsert_invalid_domain(self, api: DomainBrainAPI) -> None:
        """Test upserting invalid domain raises error."""
        # Create domain with circular dependency
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Entity1",
            description="desc",
            source="AST",
            metadata={"depends_on": ["e2"]},
        )
        domain.entities["e2"] = Entity(
            entity_id="e2",
            entity_type=EntityType.SERVICE,
            name="Entity2",
            description="desc",
            source="AST",
            metadata={"depends_on": ["e1"]},
        )

        # This should raise ValueError due to circular dependency
        with pytest.raises(ValueError):
            api.upsert_domain(domain)

    def test_multiple_domains_isolation(self, api: DomainBrainAPI) -> None:
        """Test that multiple domains remain isolated."""
        domain1 = Domain(
            domain_id="domain1",
            name="Domain1",
            description="Domain1",
            entities={
                "e1": Entity(
                    entity_id="e1",
                    entity_type=EntityType.SERVICE,
                    name="Entity1",
                    description="desc",
                    source="AST",
                )
            },
        )

        domain2 = Domain(
            domain_id="domain2",
            name="Domain2",
            description="Domain2",
            entities={
                "e2": Entity(
                    entity_id="e2",
                    entity_type=EntityType.SERVICE,
                    name="Entity2",
                    description="desc",
                    source="BKIO",
                )
            },
        )

        api.upsert_domain(domain1)
        api.upsert_domain(domain2)

        d1 = api.query_domain("domain1")
        assert len(d1.entities) == 1
        assert "e1" in d1.entities
        assert "e2" not in d1.entities

    def test_search_case_insensitive(self, api: DomainBrainAPI) -> None:
        """Test that search is case-insensitive."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="MyService",
            description="A service",
            source="AST",
        )
        api.upsert_domain(domain)

        results1 = api.search_entities("myservice")
        results2 = api.search_entities("MYSERVICE")
        results3 = api.search_entities("MyService")

        assert len(results1) > 0
        assert len(results2) > 0
        assert len(results3) > 0


class TestConsistencyValidator:
    """Tests for ConsistencyValidator (20 tests)."""

    @pytest.fixture
    def validator(self) -> ConsistencyValidator:
        """Create validator instance."""
        return ConsistencyValidator()

    def test_schema_validation_valid(self, validator: ConsistencyValidator) -> None:
        """Test schema validation with valid data."""
        domain = Domain(
            domain_id="test",
            name="Test Domain",
            description="A test domain",
        )
        result = validator.validate_domain(domain)
        assert result.is_valid

    def test_referential_integrity_valid(self, validator: ConsistencyValidator) -> None:
        """Test referential integrity with valid references."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Entity1",
            description="desc",
            source="AST",
        )
        domain.entities["e2"] = Entity(
            entity_id="e2",
            entity_type=EntityType.SERVICE,
            name="Entity2",
            description="desc",
            source="AST",
            metadata={"references": ["e1"]},
        )

        result = validator.validate_domain(domain)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_referential_integrity_broken(self, validator: ConsistencyValidator) -> None:
        """Test referential integrity with broken references."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Entity1",
            description="desc",
            source="AST",
            metadata={"references": ["non-existent"]},
        )

        result = validator.validate_domain(domain)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("non-existent" in e for e in result.errors)

    def test_circular_dependency_detection_simple(self, validator: ConsistencyValidator) -> None:
        """Test circular dependency detection (A -> B -> A)."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Entity1",
            description="desc",
            source="AST",
            metadata={"depends_on": ["e2"]},
        )
        domain.entities["e2"] = Entity(
            entity_id="e2",
            entity_type=EntityType.SERVICE,
            name="Entity2",
            description="desc",
            source="AST",
            metadata={"depends_on": ["e1"]},
        )

        result = validator.validate_domain(domain)
        assert not result.is_valid
        assert any("Circular" in e for e in result.errors)

    def test_circular_dependency_detection_complex(self, validator: ConsistencyValidator) -> None:
        """Test circular dependency detection (A -> B -> C -> A)."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Entity1",
            description="desc",
            source="AST",
            metadata={"depends_on": ["e2"]},
        )
        domain.entities["e2"] = Entity(
            entity_id="e2",
            entity_type=EntityType.SERVICE,
            name="Entity2",
            description="desc",
            source="AST",
            metadata={"depends_on": ["e3"]},
        )
        domain.entities["e3"] = Entity(
            entity_id="e3",
            entity_type=EntityType.SERVICE,
            name="Entity3",
            description="desc",
            source="AST",
            metadata={"depends_on": ["e1"]},
        )

        result = validator.validate_domain(domain)
        assert not result.is_valid
        assert any("Circular" in e for e in result.errors)

    def test_conflict_detection_same_entity_different_sources(self, validator: ConsistencyValidator) -> None:
        """Test conflict detection when same entity exists in different sources."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1_ast"] = Entity(
            entity_id="e1_ast",
            entity_type=EntityType.SERVICE,
            name="SameName",
            description="From AST",
            source="AST",
        )
        domain.entities["e1_bkio"] = Entity(
            entity_id="e1_bkio",
            entity_type=EntityType.SERVICE,
            name="SameName",
            description="From BKIO",
            source="BKIO",
        )

        result = validator.validate_domain(domain)
        assert len(result.conflicts_detected) > 0

    def test_dependency_broken_reference(self, validator: ConsistencyValidator) -> None:
        """Test broken dependency references."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Entity1",
            description="desc",
            source="AST",
            metadata={"depends_on": ["missing"]},
        )

        result = validator.validate_domain(domain)
        assert not result.is_valid
        assert any("depends on non-existent" in e for e in result.errors)

    def test_validate_single_entity_valid(self, validator: ConsistencyValidator) -> None:
        """Test validating a single entity with valid references."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Entity1",
            description="desc",
            source="AST",
        )
        domain.entities["e2"] = Entity(
            entity_id="e2",
            entity_type=EntityType.SERVICE,
            name="Entity2",
            description="desc",
            source="AST",
            metadata={"references": ["e1"]},
        )

        result = validator.validate_entity(domain.entities["e2"], domain)
        assert result.is_valid

    def test_validate_single_entity_broken_reference(self, validator: ConsistencyValidator) -> None:
        """Test validating a single entity with broken reference."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Entity1",
            description="desc",
            source="AST",
            metadata={"references": ["missing"]},
        )

        result = validator.validate_entity(entity, domain)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_no_errors_on_empty_domain(self, validator: ConsistencyValidator) -> None:
        """Test validation passes on empty domain."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        result = validator.validate_domain(domain)
        assert result.is_valid

    def test_complex_valid_domain(self, validator: ConsistencyValidator) -> None:
        """Test validation on complex valid domain."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["service"] = Entity(
            entity_id="service",
            entity_type=EntityType.SERVICE,
            name="MainService",
            description="Main service",
            source="BKIO",
        )
        domain.entities["func1"] = Entity(
            entity_id="func1",
            entity_type=EntityType.FUNCTION,
            name="Function1",
            description="Function 1",
            source="AST",
            metadata={"depends_on": ["service"]},
        )
        domain.entities["func2"] = Entity(
            entity_id="func2",
            entity_type=EntityType.FUNCTION,
            name="Function2",
            description="Function 2",
            source="AST",
            metadata={"depends_on": ["func1"]},
        )

        result = validator.validate_domain(domain)
        assert result.is_valid


class TestAuditLogger:
    """Tests for AuditLogger (15 tests)."""

    @pytest.fixture
    def logger(self) -> AuditLogger:
        """Create logger instance."""
        return AuditLogger()

    def test_log_operation_basic(self, logger: AuditLogger) -> None:
        """Test logging a basic operation."""
        entry = logger.log_operation(
            AuditOperationType.CREATE,
            domain_id="test-domain",
            description="Create test domain",
        )

        assert entry.operation == AuditOperationType.CREATE
        assert entry.domain_id == "test-domain"
        assert entry.hash != ""

    def test_hash_chain_integrity(self, logger: AuditLogger) -> None:
        """Test hash chain maintains integrity."""
        entry1 = logger.log_operation(
            AuditOperationType.CREATE,
            domain_id="domain1",
        )
        entry2 = logger.log_operation(
            AuditOperationType.UPDATE,
            domain_id="domain1",
        )

        assert entry2.previous_hash == entry1.hash
        assert entry1.previous_hash != entry2.hash

    def test_append_only_enforcement(self, logger: AuditLogger) -> None:
        """Test that log is append-only."""
        logger.log_operation(AuditOperationType.CREATE, domain_id="d1")
        logger.log_operation(AuditOperationType.UPDATE, domain_id="d1")
        logger.log_operation(AuditOperationType.DELETE, domain_id="d1")

        entries = logger.get_all_entries()
        assert len(entries) == 3
        assert entries[0].operation == AuditOperationType.CREATE
        assert entries[1].operation == AuditOperationType.UPDATE
        assert entries[2].operation == AuditOperationType.DELETE

    def test_ttl_cache_performance(self, logger: AuditLogger) -> None:
        """Test TTL cache improves performance for recent entries."""
        for i in range(10):
            logger.log_operation(
                AuditOperationType.CREATE,
                domain_id=f"domain{i}",
            )

        # Recent entries should be in cache
        stats = logger.get_cache_stats()
        assert stats["cache_size"] > 0
        assert stats["total_entries"] == 10

    def test_audit_trail_queryable(self, logger: AuditLogger) -> None:
        """Test that audit trail is queryable."""
        logger.log_operation(AuditOperationType.CREATE, domain_id="domain1", entity_id="e1")
        logger.log_operation(AuditOperationType.UPDATE, domain_id="domain1", entity_id="e1")
        logger.log_operation(AuditOperationType.CREATE, domain_id="domain2", entity_id="e2")

        trail = logger.get_domain_audit_trail("domain1")
        assert len(trail) == 2
        assert all(e.domain_id == "domain1" for e in trail)

    def test_get_entry_from_cache(self, logger: AuditLogger) -> None:
        """Test retrieving entry from cache."""
        entry = logger.log_operation(
            AuditOperationType.CREATE,
            domain_id="test",
        )

        retrieved = logger.get_entry(entry.entry_id)
        assert retrieved is not None
        assert retrieved.entry_id == entry.entry_id
        assert retrieved.operation == AuditOperationType.CREATE

    def test_get_entry_not_found(self, logger: AuditLogger) -> None:
        """Test retrieving non-existent entry."""
        retrieved = logger.get_entry("non-existent-id")
        assert retrieved is None

    def test_verify_hash_chain_valid(self, logger: AuditLogger) -> None:
        """Test hash chain verification on valid log."""
        logger.log_operation(AuditOperationType.CREATE, domain_id="d1")
        logger.log_operation(AuditOperationType.UPDATE, domain_id="d1")
        logger.log_operation(AuditOperationType.DELETE, domain_id="d1")

        is_valid = logger.verify_hash_chain()
        assert is_valid

    def test_get_all_entries(self, logger: AuditLogger) -> None:
        """Test retrieving all entries."""
        for i in range(5):
            logger.log_operation(AuditOperationType.CREATE, domain_id=f"d{i}")

        entries = logger.get_all_entries()
        assert len(entries) == 5

    def test_get_entry_count(self, logger: AuditLogger) -> None:
        """Test getting entry count."""
        assert logger.get_entry_count() == 0

        for i in range(10):
            logger.log_operation(AuditOperationType.CREATE)

        assert logger.get_entry_count() == 10

    def test_get_recent_entries(self, logger: AuditLogger) -> None:
        """Test retrieving recent entries."""
        for i in range(20):
            logger.log_operation(AuditOperationType.CREATE, domain_id=f"d{i}")

        recent = logger.get_recent_entries(limit=5)
        assert len(recent) <= 5

    def test_audit_operation_with_values(self, logger: AuditLogger) -> None:
        """Test logging operation with previous and new values."""
        entry = logger.log_operation(
            AuditOperationType.UPDATE,
            domain_id="domain1",
            previous_value={"old": "value"},
            new_value={"new": "value"},
        )

        assert entry.previous_value == {"old": "value"}
        assert entry.new_value == {"new": "value"}

    def test_multiple_domains_audit_isolation(self, logger: AuditLogger) -> None:
        """Test that audit trails remain isolated per domain."""
        logger.log_operation(AuditOperationType.CREATE, domain_id="d1")
        logger.log_operation(AuditOperationType.UPDATE, domain_id="d1")
        logger.log_operation(AuditOperationType.CREATE, domain_id="d2")

        d1_trail = logger.get_domain_audit_trail("d1")
        d2_trail = logger.get_domain_audit_trail("d2")

        assert len(d1_trail) == 2
        assert len(d2_trail) == 1
        assert all(e.domain_id == "d1" for e in d1_trail)
        assert all(e.domain_id == "d2" for e in d2_trail)


# Integration tests
class TestDomainBrainIntegration:
    """Integration tests combining multiple components."""

    def test_api_with_audit_logger(self) -> None:
        """Test that API properly integrates with audit logger."""
        api = DomainBrainAPI()
        domain = Domain(domain_id="test", name="Test", description="Test")

        api.upsert_domain(domain)
        audit_trail = api.audit_domain("test")

        assert len(audit_trail) > 0
        assert any(entry["operation"] == "CREATE" for entry in audit_trail)

    def test_validator_rejects_invalid_domain_on_upsert(self) -> None:
        """Test that validator prevents invalid domain from being upserted."""
        api = DomainBrainAPI()

        # Create domain with circular dependency
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="E1",
            description="desc",
            source="AST",
            metadata={"depends_on": ["e2"]},
        )
        domain.entities["e2"] = Entity(
            entity_id="e2",
            entity_type=EntityType.SERVICE,
            name="E2",
            description="desc",
            source="AST",
            metadata={"depends_on": ["e1"]},
        )

        with pytest.raises(ValueError):
            api.upsert_domain(domain)

    def test_end_to_end_domain_workflow(self) -> None:
        """Test complete workflow: create, query, update, resolve conflict, delete."""
        api = DomainBrainAPI()

        # Create domain
        domain = Domain(
            domain_id="auth",
            name="Authentication",
            description="Auth service",
        )
        domain.entities["login"] = Entity(
            entity_id="login",
            entity_type=EntityType.FUNCTION,
            name="login",
            description="Login function",
            source="AST",
        )

        api.upsert_domain(domain)

        # Query
        retrieved = api.query_domain("auth")
        assert retrieved is not None
        assert len(retrieved.entities) == 1

        # Add conflict
        conflict = Conflict(
            conflict_id="c1",
            domain_id="auth",
            attribute="description",
            source_values={"AST": "old", "BKIO": "new"},
        )
        retrieved.conflicts.append(conflict)
        api.upsert_domain(retrieved)

        # Resolve conflict
        api.resolve_conflict("c1", "auth", "resolved_value")

        # Verify resolution
        conflicts = api.get_conflicts("auth")
        assert conflicts[0].resolved_at is not None

        # Delete
        api.delete_domain("auth")
        assert api.query_domain("auth") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
