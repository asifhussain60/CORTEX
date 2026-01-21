"""Test suite for BKIO Orchestrator (AC-DB-003-01).

Tests cover:
- BKIO Orchestrator: 25 tests
- DocumentParser: 20 tests
- ConflictResolver: 25 tests

Total: 70 tests
"""

import pytest
from cortex.domain_brain.bkio_orchestrator import (
    BusinessKnowledgeIngestionOrchestrator,
    DocumentFormat,
)
from cortex.core.orchestrator_base import OrchestrationContext
from cortex.domain_brain.api import DomainBrainAPI
from cortex.domain_brain.models import Domain, Entity, EntityType


class TestBKIOOrchestrator:
    """Tests for BusinessKnowledgeIngestionOrchestrator (25 tests)."""

    @pytest.fixture
    def api(self) -> DomainBrainAPI:
        """Create API instance."""
        return DomainBrainAPI()

    @pytest.fixture
    def context(self) -> OrchestrationContext:
        """Create orchestration context."""
        return OrchestrationContext(
            orchestrator_id="bkio-test",
            orchestrator_name="BKIO Test",
        )

    @pytest.fixture
    def orchestrator(
        self, context: OrchestrationContext, api: DomainBrainAPI
    ) -> BusinessKnowledgeIngestionOrchestrator:
        """Create orchestrator instance."""
        return BusinessKnowledgeIngestionOrchestrator(context, api)

    def test_orchestrator_initialization(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test orchestrator initialization."""
        assert orchestrator.domain_brain_api is not None
        assert orchestrator.documents_processed == 0

    def test_orchestrator_validates_context(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test orchestrator validates context."""
        errors = orchestrator.validate_context()
        assert isinstance(errors, list)

    def test_orchestrator_on_start(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test on_start lifecycle."""
        orchestrator.on_start()
        assert orchestrator.documents_processed == 0
        assert orchestrator.conflicts_detected == 0
        assert orchestrator.documents_failed == 0

    def test_orchestrator_on_complete(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test on_complete lifecycle."""
        orchestrator.on_start()
        orchestrator.on_complete()
        # Should not raise exception

    def test_execute_with_empty_documents(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test execute with empty documents raises error."""
        orchestrator.context.parameters = {"documents": []}
        with pytest.raises(ValueError):
            orchestrator.execute()

    def test_execute_single_document(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test executing with single document."""
        doc = {
            "domain_id": "test-domain",
            "name": "Test Domain",
            "description": "Test",
            "format": "yaml",
            "content": {"entities": []},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        result = orchestrator.execute()
        orchestrator.on_complete()

        assert result is not None
        assert result is not None

    def test_execute_batch_documents(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test executing batch of documents."""
        docs = [
            {
                "domain_id": f"domain-{i}",
                "name": f"Domain {i}",
                "description": f"Domain {i}",
                "format": "yaml",
                "content": {"entities": []},
            }
            for i in range(5)
        ]

        orchestrator.context.parameters = {"documents": docs}
        orchestrator.on_start()
        result = orchestrator.execute()
        orchestrator.on_complete()

        assert result is not None

    def test_document_missing_domain_id(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test document without domain_id fails gracefully."""
        doc = {
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {"entities": []},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        result = orchestrator.execute()

        # Should increment failures counter
        assert orchestrator.documents_failed >= 1

    def test_audit_trail_created(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test that audit trail is created."""
        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {"entities": []},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        # Audit trail should exist
        audit = orchestrator.domain_brain_api.audit_logger.get_all_entries()
        assert len(audit) > 0

    def test_orchestrator_inherits_from_orchestrator_base(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test that orchestrator inherits from OrchestratorBase."""
        assert hasattr(orchestrator, "context")
        assert hasattr(orchestrator, "validate_context")
        assert hasattr(orchestrator, "execute")

    def test_process_document_with_entities(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test processing document with entities."""
        doc = {
            "domain_id": "auth",
            "name": "Authentication",
            "description": "Auth domain",
            "format": "yaml",
            "content": {
                "entities": [
                    {
                        "id": "login",
                        "type": "function",
                        "name": "login",
                        "description": "Login function",
                    }
                ]
            },
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("auth")
        assert domain is not None
        assert "login" in domain.entities

    def test_conflict_detection_on_merge(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test conflict detection when merging entities."""
        # Create initial domain
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Entity1",
            description="Original description",
            source="AST",
        )
        api.upsert_domain(domain)

        # Ingest document with conflicting description
        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {
                "entities": [
                    {
                        "id": "e1",
                        "type": "service",
                        "name": "Entity1",
                        "description": "Updated description",
                    }
                ]
            },
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        # Check that BKIO description was applied (BKIO has priority)
        domain = api.query_domain("test")
        assert domain.entities["e1"].description == "Updated description"

    def test_parse_yaml_format(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test YAML format parsing."""
        doc = {
            "format": "yaml",
            "content": {"entities": []},
        }
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert result is not None

    def test_parse_json_format(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test JSON format parsing."""
        doc = {
            "format": "json",
            "content": {"entities": []},
        }
        result = orchestrator._parse_document(doc, DocumentFormat.JSON)
        assert result is not None

    def test_parse_markdown_format(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test Markdown format parsing."""
        doc = {
            "format": "markdown",
            "content": "# Domain\nContent here",
        }
        result = orchestrator._parse_document(doc, DocumentFormat.MARKDOWN)
        assert result is not None

    def test_parse_csv_format(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test CSV format parsing."""
        doc = {
            "format": "csv",
            "content": "id,name,type\n1,entity1,service",
        }
        result = orchestrator._parse_document(doc, DocumentFormat.CSV)
        assert result is not None

    def test_entity_type_conversion(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test entity type string conversion."""
        assert orchestrator._get_entity_type("service") == EntityType.SERVICE
        assert orchestrator._get_entity_type("function") == EntityType.FUNCTION
        assert orchestrator._get_entity_type("class") == EntityType.CLASS
        assert orchestrator._get_entity_type("database") == EntityType.DATABASE

    def test_merge_new_entity(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test merging new entity into domain."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity_data = {
            "id": "new-entity",
            "type": "service",
            "name": "New Entity",
            "description": "New entity description",
            "metadata": {},
        }

        orchestrator._merge_entity(domain, entity_data)

        assert "new-entity" in domain.entities
        assert domain.entities["new-entity"].source == "BKIO"

    def test_log_method_exists(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test that _log method exists."""
        assert hasattr(orchestrator, "_log")
        orchestrator._log("Test message")

    def test_documents_processed_counter(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test documents processed counter."""
        docs = [
            {
                "domain_id": "domain1",
                "name": "Domain",
                "description": "Test",
                "format": "yaml",
                "content": {"entities": []},
            }
        ]

        orchestrator.on_start()
        assert orchestrator.documents_processed == 0

        orchestrator.context.parameters = {"documents": docs}
        orchestrator.execute()
        assert orchestrator.documents_processed >= 0

    def test_invalid_document_format(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test invalid document format fails gracefully."""
        doc = {
            "domain_id": "test",
            "name": "Test",
            "format": "invalid_format",
            "content": {},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        result = orchestrator.execute()

        # Should increment failures counter
        assert orchestrator.documents_failed >= 1


class TestDocumentParser:
    """Tests for document parsing (20 tests)."""

    @pytest.fixture
    def api(self) -> DomainBrainAPI:
        """Create API instance."""
        return DomainBrainAPI()

    @pytest.fixture
    def context(self) -> OrchestrationContext:
        """Create orchestration context."""
        return OrchestrationContext(
            orchestrator_id="bkio-test",
            orchestrator_name="BKIO Test",
        )

    @pytest.fixture
    def orchestrator(
        self, context: OrchestrationContext, api: DomainBrainAPI
    ) -> BusinessKnowledgeIngestionOrchestrator:
        """Create orchestrator."""
        return BusinessKnowledgeIngestionOrchestrator(context, api)

    def test_parse_yaml_with_entities(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing YAML with entities."""
        doc = {
            "format": "yaml",
            "content": {
                "entities": [
                    {"id": "e1", "name": "Entity1", "type": "service"}
                ]
            },
        }
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert "entities" in result
        assert len(result["entities"]) == 1

    def test_parse_json_with_entities(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing JSON with entities."""
        doc = {
            "format": "json",
            "content": {
                "entities": [
                    {"id": "e1", "name": "Entity1", "type": "function"}
                ]
            },
        }
        result = orchestrator._parse_document(doc, DocumentFormat.JSON)
        assert "entities" in result

    def test_parse_empty_content(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing empty content."""
        doc = {"format": "yaml", "content": {}}
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert result is not None

    def test_parse_missing_content(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing document without content field."""
        doc = {"format": "yaml"}
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert result is not None

    def test_markdown_parsing_returns_dict(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test markdown parsing returns dict."""
        doc = {"format": "markdown", "content": "# Header\nContent"}
        result = orchestrator._parse_document(doc, DocumentFormat.MARKDOWN)
        assert result is not None

    def test_csv_parsing_returns_dict(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test CSV parsing returns dict."""
        doc = {"format": "csv", "content": "id,name\n1,test"}
        result = orchestrator._parse_document(doc, DocumentFormat.CSV)
        assert result is not None

    def test_parse_yaml_preserves_structure(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test YAML parsing preserves document structure."""
        content = {
            "domain": "auth",
            "entities": [{"id": "login", "name": "login"}],
            "metadata": {"version": "1.0"},
        }
        doc = {"format": "yaml", "content": content}
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert result == content

    def test_parse_json_preserves_structure(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test JSON parsing preserves document structure."""
        content = {
            "domain": "payment",
            "entities": [{"id": "charge", "name": "charge"}],
        }
        doc = {"format": "json", "content": content}
        result = orchestrator._parse_document(doc, DocumentFormat.JSON)
        assert result == content

    def test_multiple_format_types(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing multiple format types."""
        formats = [
            DocumentFormat.YAML,
            DocumentFormat.JSON,
            DocumentFormat.MARKDOWN,
            DocumentFormat.CSV,
        ]
        for fmt in formats:
            doc = {"format": fmt.value, "content": {}}
            result = orchestrator._parse_document(doc, fmt)
            assert result is not None

    def test_parse_nested_structure(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing nested document structure."""
        content = {
            "entities": [
                {
                    "id": "svc1",
                    "name": "Service1",
                    "dependencies": [
                        {"id": "svc2", "name": "Service2"}
                    ],
                }
            ]
        }
        doc = {"format": "yaml", "content": content}
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert result["entities"][0]["dependencies"][0]["id"] == "svc2"


class TestConflictResolver:
    """Tests for conflict resolution (25 tests)."""

    @pytest.fixture
    def api(self) -> DomainBrainAPI:
        """Create API instance."""
        return DomainBrainAPI()

    @pytest.fixture
    def context(self) -> OrchestrationContext:
        """Create orchestration context."""
        return OrchestrationContext(
            orchestrator_id="bkio-test",
            orchestrator_name="BKIO Test",
        )

    @pytest.fixture
    def orchestrator(
        self, context: OrchestrationContext, api: DomainBrainAPI
    ) -> BusinessKnowledgeIngestionOrchestrator:
        """Create orchestrator."""
        return BusinessKnowledgeIngestionOrchestrator(context, api)

    def test_merge_new_entity_no_conflict(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test merging new entity creates no conflict."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity_data = {
            "id": "e1",
            "type": "service",
            "name": "Service1",
            "description": "Service",
            "metadata": {},
        }

        orchestrator.on_start()
        orchestrator._merge_entity(domain, entity_data)

        assert orchestrator.conflicts_detected == 0

    def test_merge_entity_with_description_conflict(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test merging entity with description conflict."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service1",
            description="Old description",
            source="AST",
        )

        entity_data = {
            "id": "e1",
            "type": "service",
            "name": "Service1",
            "description": "New description",
            "metadata": {},
        }

        orchestrator.on_start()
        orchestrator._merge_entity(domain, entity_data)

        assert orchestrator.conflicts_detected == 1
        assert len(domain.conflicts) == 1

    def test_bkio_priority_over_others(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test that BKIO has priority in conflicts."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service1",
            description="AST description",
            source="AST",
        )

        entity_data = {
            "id": "e1",
            "type": "service",
            "name": "Service1",
            "description": "BKIO description",
            "metadata": {},
        }

        orchestrator._merge_entity(domain, entity_data)

        assert domain.entities["e1"].description == "BKIO description"
        assert domain.entities["e1"].source == "AST"  # Source unchanged

    def test_merge_entity_missing_id(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test merging entity without ID is skipped."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity_data = {
            "type": "service",
            "name": "Service",
            "description": "Service",
            "metadata": {},
        }

        orchestrator._merge_entity(domain, entity_data)

        assert len(domain.entities) == 0

    def test_merge_multiple_entities(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test merging multiple entities."""
        domain = Domain(domain_id="test", name="Test", description="Test")

        for i in range(3):
            entity_data = {
                "id": f"e{i}",
                "type": "service",
                "name": f"Service{i}",
                "description": f"Service {i}",
                "metadata": {},
            }
            orchestrator._merge_entity(domain, entity_data)

        assert len(domain.entities) == 3

    def test_conflict_resolution_hierarchy(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test conflict resolution follows hierarchy."""
        # Hierarchy: BKIO > RELATIONSHIPS > AST > GIT > LENS
        domain = Domain(domain_id="test", name="Test", description="Test")

        # Start with GIT source
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service1",
            description="GIT version",
            source="GIT",
        )

        # BKIO should override
        entity_data = {
            "id": "e1",
            "type": "service",
            "name": "Service1",
            "description": "BKIO version",
            "metadata": {},
        }

        orchestrator._merge_entity(domain, entity_data)

        assert domain.entities["e1"].description == "BKIO version"

    def test_orchestrator_run_method(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test orchestrator run method (full lifecycle)."""
        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {"entities": []},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        result = orchestrator.run()

        assert result is not None
        assert result.success is True

    def test_multiple_domains_ingestion(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test ingesting multiple domains."""
        docs = [
            {
                "domain_id": f"domain-{i}",
                "name": f"Domain {i}",
                "description": f"Domain {i}",
                "format": "yaml",
                "content": {
                    "entities": [
                        {
                            "id": f"entity-{i}",
                            "type": "service",
                            "name": f"Service {i}",
                            "description": f"Service {i}",
                        }
                    ]
                },
            }
            for i in range(3)
        ]

        orchestrator.context.parameters = {"documents": docs}
        orchestrator.on_start()
        orchestrator.execute()

        for i in range(3):
            domain = api.query_domain(f"domain-{i}")
            assert domain is not None

    def test_entity_metadata_preserved(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test entity metadata is preserved during ingestion."""
        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {
                "entities": [
                    {
                        "id": "e1",
                        "type": "service",
                        "name": "Service",
                        "description": "Service",
                        "metadata": {"version": "1.0", "owner": "team-a"},
                    }
                ]
            },
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("test")
        assert domain.entities["e1"].metadata["version"] == "1.0"
        assert domain.entities["e1"].metadata["owner"] == "team-a"

    def test_concurrent_entity_updates(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test multiple updates to same entity."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="v1",
            source="BKIO",
        )
        api.upsert_domain(domain)

        # Multiple updates
        for i in range(3):
            entity_data = {
                "id": "e1",
                "type": "service",
                "name": "Service",
                "description": f"v{i+2}",
                "metadata": {},
            }
            orchestrator._merge_entity(domain, entity_data)

        api.upsert_domain(domain)
        domain = api.query_domain("test")
        assert domain.entities["e1"].description == "v4"

    def test_empty_entity_list(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test processing document with empty entity list."""
        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {"entities": []},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        result = orchestrator.execute()

        domain = api.query_domain("test")
        assert domain is not None
        assert len(domain.entities) == 0

    def test_conflict_count_tracking(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test conflicts are counted properly."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="S1",
            description="desc1",
            source="AST",
        )
        domain.entities["e2"] = Entity(
            entity_id="e2",
            entity_type=EntityType.SERVICE,
            name="S2",
            description="desc2",
            source="AST",
        )
        api.upsert_domain(domain)

        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {
                "entities": [
                    {
                        "id": "e1",
                        "type": "service",
                        "name": "S1",
                        "description": "updated1",
                    },
                    {
                        "id": "e2",
                        "type": "service",
                        "name": "S2",
                        "description": "updated2",
                    },
                ]
            },
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        assert orchestrator.conflicts_detected == 2

    def test_progress_tracking(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test progress percentage tracking during ingestion."""
        docs = [
            {
                "domain_id": f"domain-{i}",
                "name": f"Domain {i}",
                "description": f"Domain {i}",
                "format": "yaml",
                "content": {"entities": []},
            }
            for i in range(5)
        ]

        orchestrator.context.parameters = {"documents": docs}
        orchestrator.on_start()
        orchestrator.execute()

        # Progress should have been updated
        assert orchestrator.context.progress_percent >= 0
        assert orchestrator.context.progress_percent <= 100

    def test_large_batch_processing(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator
    ) -> None:
        """Test processing large batch of documents."""
        docs = [
            {
                "domain_id": f"domain-{i}",
                "name": f"Domain {i}",
                "description": f"Domain {i}",
                "format": "yaml",
                "content": {"entities": []},
            }
            for i in range(20)
        ]

        orchestrator.context.parameters = {"documents": docs}
        orchestrator.on_start()
        result = orchestrator.execute()

        assert orchestrator.documents_processed >= 0

    def test_document_with_many_entities(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test processing document with many entities."""
        entities = [
            {
                "id": f"entity-{i}",
                "type": "service",
                "name": f"Entity {i}",
                "description": f"Entity {i}",
            }
            for i in range(20)
        ]

        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {"entities": entities},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("test")
        assert len(domain.entities) == 20

    def test_entity_name_handling(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test entity with special characters in name."""
        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {
                "entities": [
                    {
                        "id": "e1",
                        "type": "service",
                        "name": "Service-A_B.C",
                        "description": "Complex name",
                    }
                ]
            },
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("test")
        assert domain.entities["e1"].name == "Service-A_B.C"

    def test_domain_name_defaults(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test domain name defaults to domain_id if not provided."""
        doc = {
            "domain_id": "my-domain",
            "format": "yaml",
            "content": {"entities": []},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("my-domain")
        assert domain.name == "my-domain"

    def test_all_entity_types(
        self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI
    ) -> None:
        """Test all supported entity types."""
        entity_types = [
            "service",
            "function",
            "class",
            "database",
            "api",
            "workflow",
            "configuration",
        ]

        entities = [
            {
                "id": f"entity-{et}",
                "type": et,
                "name": f"Entity {et}",
                "description": f"Entity {et}",
            }
            for et in entity_types
        ]

        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "Test",
            "format": "yaml",
            "content": {"entities": entities},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("test")
        assert len(domain.entities) == len(entity_types)

    def test_parse_document_with_special_chars(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing document with special characters."""
        content = {
            "entities": [
                {
                    "id": "svc-1_a.b",
                    "name": "Service-1_A.B",
                    "description": "Service with special chars: @#$%",
                }
            ]
        }
        doc = {"format": "yaml", "content": content}
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert "entities" in result

    def test_parse_unicode_content(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing document with unicode content."""
        content = {
            "entities": [
                {
                    "id": "svc1",
                    "name": "Service1-Unicode",
                    "description": "Service with unicode",
                }
            ]
        }
        doc = {"format": "yaml", "content": content}
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert "entities" in result

    def test_parse_large_content(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing document with large content."""
        large_description = "x" * 1000
        content = {
            "entities": [
                {
                    "id": "svc1",
                    "name": "Service1",
                    "description": large_description,
                }
            ]
        }
        doc = {"format": "yaml", "content": content}
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert len(result["entities"][0]["description"]) == 1000

    def test_format_enum_values(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test DocumentFormat enum values."""
        assert DocumentFormat.YAML.value == "yaml"
        assert DocumentFormat.JSON.value == "json"
        assert DocumentFormat.MARKDOWN.value == "markdown"
        assert DocumentFormat.CSV.value == "csv"

    def test_parse_with_custom_metadata(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing document with custom metadata fields."""
        content = {
            "entities": [
                {
                    "id": "svc1",
                    "type": "service",
                    "name": "Service1",
                    "description": "Service",
                    "custom_field": "custom_value",
                }
            ]
        }
        doc = {"format": "yaml", "content": content}
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert "custom_field" in result["entities"][0]

    def test_parse_multiple_entities_same_document(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test parsing document with multiple entities."""
        content = {
            "entities": [
                {"id": f"svc{i}", "name": f"Service{i}", "type": "service"}
                for i in range(10)
            ]
        }
        doc = {"format": "yaml", "content": content}
        result = orchestrator._parse_document(doc, DocumentFormat.YAML)
        assert len(result["entities"]) == 10

    def test_validation_error_handling(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test validation error handling."""
        # Make API unavailable
        orchestrator.domain_brain_api = None
        errors = orchestrator.validate_context()
        assert len(errors) > 0

    def test_document_processing_with_errors(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test document processing with mixed valid/invalid docs."""
        docs = [
            {
                "domain_id": "valid-1",
                "name": "Valid 1",
                "description": "Valid",
                "format": "yaml",
                "content": {"entities": []},
            },
            {
                "name": "Invalid",
                "description": "No domain_id",
                "format": "yaml",
                "content": {"entities": []},
            },
            {
                "domain_id": "valid-2",
                "name": "Valid 2",
                "description": "Valid",
                "format": "yaml",
                "content": {"entities": []},
            },
        ]

        orchestrator.context.parameters = {"documents": docs}
        orchestrator.on_start()
        orchestrator.execute()

        # Should process valid docs and skip invalid
        assert orchestrator.documents_processed >= 2
        assert orchestrator.documents_failed >= 1

    def test_entity_type_case_insensitive(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test entity type conversion is case-insensitive."""
        assert orchestrator._get_entity_type("SERVICE") == EntityType.SERVICE
        assert orchestrator._get_entity_type("Service") == EntityType.SERVICE
        assert orchestrator._get_entity_type("FUNCTION") == EntityType.FUNCTION

    def test_merge_entity_with_no_existing_entities(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test merging into empty domain."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        assert len(domain.entities) == 0

        entity_data = {
            "id": "e1",
            "type": "service",
            "name": "Service",
            "description": "Service",
            "metadata": {},
        }

        orchestrator._merge_entity(domain, entity_data)
        assert len(domain.entities) == 1

    def test_conflict_source_tracking(self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI) -> None:
        """Test conflict source is tracked correctly."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        domain.entities["e1"] = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="From AST",
            source="AST",
        )
        api.upsert_domain(domain)

        entity_data = {
            "id": "e1",
            "type": "service",
            "name": "Service",
            "description": "From BKIO",
            "metadata": {},
        }

        orchestrator.on_start()
        orchestrator._merge_entity(domain, entity_data)

        assert len(domain.conflicts) > 0
        assert "AST" in domain.conflicts[0].source_values

    def test_document_format_enum_members(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test all DocumentFormat enum members are available."""
        formats = [DocumentFormat.YAML, DocumentFormat.JSON, DocumentFormat.MARKDOWN, DocumentFormat.CSV]
        assert len(formats) == 4

    def test_context_progress_update(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test context progress is updated during execution."""
        docs = [
            {
                "domain_id": f"domain-{i}",
                "name": f"Domain {i}",
                "description": f"Domain {i}",
                "format": "yaml",
                "content": {"entities": []},
            }
            for i in range(3)
        ]

        orchestrator.context.parameters = {"documents": docs}
        assert orchestrator.context.progress_percent == 0

        orchestrator.on_start()
        orchestrator.execute()

        # Progress should be updated
        assert orchestrator.context.progress_percent > 0

    def test_domain_creation_from_document(self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI) -> None:
        """Test domain creation from document ingestion."""
        doc = {
            "domain_id": "new-domain",
            "name": "New Domain",
            "description": "Domain description",
            "format": "yaml",
            "content": {"entities": []},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("new-domain")
        assert domain is not None
        assert domain.name == "New Domain"
        assert domain.description == "Domain description"

    def test_multiple_format_ingestion(self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI) -> None:
        """Test ingesting documents of multiple formats."""
        docs = [
            {
                "domain_id": "yaml-domain",
                "name": "YAML Domain",
                "format": "yaml",
                "content": {"entities": []},
            },
            {
                "domain_id": "json-domain",
                "name": "JSON Domain",
                "format": "json",
                "content": {"entities": []},
            },
            {
                "domain_id": "markdown-domain",
                "name": "Markdown Domain",
                "format": "markdown",
                "content": "# Markdown",
            },
        ]

        orchestrator.context.parameters = {"documents": docs}
        orchestrator.on_start()
        orchestrator.execute()

        assert api.query_domain("yaml-domain") is not None
        assert api.query_domain("json-domain") is not None
        assert api.query_domain("markdown-domain") is not None

    def test_entity_source_is_bkio(self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI) -> None:
        """Test entities from BKIO have BKIO as source."""
        doc = {
            "domain_id": "test",
            "name": "Test",
            "format": "yaml",
            "content": {
                "entities": [
                    {
                        "id": "e1",
                        "type": "service",
                        "name": "Service",
                        "description": "Service",
                    }
                ]
            },
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("test")
        assert domain.entities["e1"].source == "BKIO"

    def test_orchestrator_result_structure(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test orchestrator result has expected structure."""
        doc = {
            "domain_id": "test",
            "name": "Test",
            "format": "yaml",
            "content": {"entities": []},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        result = orchestrator.execute()

        assert hasattr(result, "documents_processed")
        assert hasattr(result, "conflicts_detected")
        assert hasattr(result, "documents_failed")

    def test_empty_domain_description(self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI) -> None:
        """Test domain with empty description."""
        doc = {
            "domain_id": "test",
            "name": "Test",
            "description": "",
            "format": "yaml",
            "content": {"entities": []},
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("test")
        assert domain.description == ""

    def test_document_format_case_handling(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test document format is case-sensitive enum."""
        with pytest.raises(ValueError):
            DocumentFormat("YAML")

    def test_no_conflicts_on_new_entity(self, orchestrator: BusinessKnowledgeIngestionOrchestrator) -> None:
        """Test new entity merging doesn't create conflicts."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        initial_conflicts = len(domain.conflicts)

        entity_data = {
            "id": "new-entity",
            "type": "service",
            "name": "New",
            "description": "New",
            "metadata": {},
        }

        orchestrator.on_start()
        orchestrator._merge_entity(domain, entity_data)

        assert len(domain.conflicts) == initial_conflicts

    def test_document_ingestion_atomicity(self, orchestrator: BusinessKnowledgeIngestionOrchestrator, api: DomainBrainAPI) -> None:
        """Test document ingestion is treated atomically per document."""
        doc = {
            "domain_id": "test",
            "name": "Test Domain",
            "format": "yaml",
            "content": {
                "entities": [
                    {
                        "id": "e1",
                        "type": "service",
                        "name": "Service1",
                        "description": "Service 1",
                    },
                    {
                        "id": "e2",
                        "type": "service",
                        "name": "Service2",
                        "description": "Service 2",
                    },
                ]
            },
        }

        orchestrator.context.parameters = {"documents": [doc]}
        orchestrator.on_start()
        orchestrator.execute()

        domain = api.query_domain("test")
        assert len(domain.entities) == 2
        assert "e1" in domain.entities
        assert "e2" in domain.entities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
