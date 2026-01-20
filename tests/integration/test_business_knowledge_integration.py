"""
Integration Tests for Business Knowledge Repository and BKIO Wiring (AC-KN-003-01).

PHASE-REMEDIATION-06: Business Knowledge Repository Integration Tests
AC-ID: AC-KN-003-01 - Master Orchestrator Business Knowledge Awareness

Tests:
1. BusinessKnowledgeRepository standalone functionality
2. MasterOrchestrator business knowledge integration
3. Business knowledge evaluation during coordinate_operation
4. BKIO orchestrator registration and wiring
5. Graceful degradation when business knowledge unavailable
6. Unified knowledge evaluation (technical + business)

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
"""

import os
import sys
import pytest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# TEST: BUSINESS KNOWLEDGE REPOSITORY MODULE
# =============================================================================

class TestBusinessKnowledgeRepositoryModule:
    """Test BusinessKnowledgeRepository standalone functionality."""
    
    def test_business_knowledge_repository_class_exists(self):
        """Verify BusinessKnowledgeRepository class can be imported."""
        from cortex.domain_brain.business_knowledge_repository import BusinessKnowledgeRepository
        assert BusinessKnowledgeRepository is not None
    
    def test_business_knowledge_entry_dataclass_exists(self):
        """Verify BusinessKnowledgeEntry dataclass can be imported."""
        from cortex.domain_brain.business_knowledge_repository import BusinessKnowledgeEntry
        assert BusinessKnowledgeEntry is not None
    
    def test_business_knowledge_query_result_dataclass_exists(self):
        """Verify BusinessKnowledgeQueryResult dataclass can be imported."""
        from cortex.domain_brain.business_knowledge_repository import BusinessKnowledgeQueryResult
        assert BusinessKnowledgeQueryResult is not None
    
    def test_get_business_knowledge_repository_singleton_exists(self):
        """Verify singleton accessor function exists."""
        from cortex.domain_brain.business_knowledge_repository import get_business_knowledge_repository
        assert callable(get_business_knowledge_repository)


class TestBusinessKnowledgeRepositoryInitialization:
    """Test BusinessKnowledgeRepository initialization."""
    
    @pytest.fixture
    def mock_api(self):
        """Create mock DomainBrainAPI."""
        api = Mock()
        api.list_domains.return_value = []
        api.query_domain.return_value = None
        api.search_entities.return_value = []
        return api
    
    @pytest.fixture
    def business_repo(self, mock_api):
        """Create BusinessKnowledgeRepository instance with mock API."""
        from cortex.domain_brain.business_knowledge_repository import BusinessKnowledgeRepository
        return BusinessKnowledgeRepository(domain_brain_api=mock_api)
    
    def test_repository_initializes_successfully(self, business_repo):
        """Verify repository initializes without error."""
        assert business_repo.is_loaded is True
    
    def test_repository_has_domains_property(self, business_repo):
        """Verify repository has domains property."""
        domains = business_repo.domains
        assert isinstance(domains, list)
    
    def test_repository_has_entry_count_property(self, business_repo):
        """Verify repository has entry_count property."""
        count = business_repo.entry_count
        assert isinstance(count, int)
        assert count >= 0


class TestBusinessKnowledgeRepositoryQueries:
    """Test BusinessKnowledgeRepository query functionality."""
    
    @pytest.fixture
    def mock_domain(self):
        """Create mock domain with entities."""
        from cortex.domain_brain.models import Domain, Entity, EntityType
        
        domain = Domain(
            domain_id="test-domain",
            name="Test Domain",
            description="Test domain for unit tests"
        )
        
        # Add test entities
        entity1 = Entity(
            entity_id="entity-1",
            entity_type=EntityType.SERVICE,
            name="PaymentService",
            description="Handles payment processing",
            source="BKIO",
            metadata={}
        )
        entity2 = Entity(
            entity_id="entity-2",
            entity_type=EntityType.API,
            name="PaymentAPI",
            description="REST API for payments",
            source="BKIO",
            metadata={}
        )
        
        domain.entities["entity-1"] = entity1
        domain.entities["entity-2"] = entity2
        
        return domain
    
    @pytest.fixture
    def mock_api_with_data(self, mock_domain):
        """Create mock DomainBrainAPI with test data."""
        api = Mock()
        api.list_domains.return_value = [mock_domain]
        api.query_domain.return_value = mock_domain
        api.search_entities.return_value = list(mock_domain.entities.values())
        return api
    
    @pytest.fixture
    def business_repo_with_data(self, mock_api_with_data):
        """Create BusinessKnowledgeRepository with test data."""
        from cortex.domain_brain.business_knowledge_repository import BusinessKnowledgeRepository
        return BusinessKnowledgeRepository(domain_brain_api=mock_api_with_data)
    
    def test_get_by_domain_returns_entries(self, business_repo_with_data):
        """Verify get_by_domain returns entries."""
        entries = business_repo_with_data.get_by_domain("test-domain")
        assert len(entries) == 2
    
    def test_query_with_no_filters_returns_all(self, business_repo_with_data):
        """Verify query with no filters returns all entries."""
        result = business_repo_with_data.query()
        assert result.total_matches == 2
    
    def test_query_with_entity_type_filter(self, business_repo_with_data):
        """Verify query filters by entity type."""
        result = business_repo_with_data.query(entity_types=["service"])
        assert result.total_matches == 1
        assert result.entries[0].name == "PaymentService"
    
    def test_query_with_keyword_filter(self, business_repo_with_data):
        """Verify query filters by keyword."""
        result = business_repo_with_data.query(keywords=["payment"])
        assert result.total_matches == 2
    
    def test_get_relevant_knowledge_returns_limited_results(self, business_repo_with_data):
        """Verify get_relevant_knowledge respects max_entries."""
        entries = business_repo_with_data.get_relevant_knowledge(max_entries=1)
        assert len(entries) <= 1


class TestBusinessKnowledgeRepositoryHelpers:
    """Test BusinessKnowledgeRepository helper methods."""
    
    @pytest.fixture
    def mock_api(self):
        """Create mock DomainBrainAPI."""
        from cortex.domain_brain.models import Domain, Entity, EntityType
        
        domain = Domain(
            domain_id="payments",
            name="Payments Domain",
            description="Payment processing"
        )
        domain.entities["svc-1"] = Entity(
            entity_id="svc-1",
            entity_type=EntityType.SERVICE,
            name="PaymentService",
            description="Service",
            source="BKIO"
        )
        domain.entities["api-1"] = Entity(
            entity_id="api-1",
            entity_type=EntityType.API,
            name="PaymentAPI",
            description="API",
            source="BKIO"
        )
        
        api = Mock()
        api.list_domains.return_value = [domain]
        api.query_domain.return_value = domain
        return api
    
    @pytest.fixture
    def business_repo(self, mock_api):
        """Create BusinessKnowledgeRepository."""
        from cortex.domain_brain.business_knowledge_repository import BusinessKnowledgeRepository
        return BusinessKnowledgeRepository(domain_brain_api=mock_api)
    
    def test_get_services(self, business_repo):
        """Verify get_services helper."""
        services = business_repo.get_services()
        assert len(services) == 1
        assert services[0].name == "PaymentService"
    
    def test_get_apis(self, business_repo):
        """Verify get_apis helper."""
        apis = business_repo.get_apis()
        assert len(apis) == 1
        assert apis[0].name == "PaymentAPI"
    
    def test_get_knowledge_summary(self, business_repo):
        """Verify knowledge summary method."""
        summary = business_repo.get_knowledge_summary()
        assert "total_domains" in summary
        assert "total_entries" in summary
        assert "entity_type_counts" in summary


# =============================================================================
# TEST: MASTER ORCHESTRATOR BUSINESS KNOWLEDGE INTEGRATION
# =============================================================================

class TestMasterOrchestratorBusinessKnowledgeIntegration:
    """Test MasterOrchestrator business knowledge repository integration."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        with patch('src.orchestrators.core.master_orchestrator.EnhancedAuditLogger') as mock:
            logger_instance = Mock()
            mock.instance.return_value = logger_instance
            yield logger_instance
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        with patch('src.orchestrators.core.master_orchestrator.DatabaseManager') as mock:
            yield mock.return_value
    
    @pytest.fixture
    def mock_transaction_manager(self):
        """Create mock transaction manager."""
        with patch('src.orchestrators.core.master_orchestrator.DatabaseTransactionManager') as mock:
            manager = Mock()
            manager.atomic_operation.return_value.__enter__ = Mock(return_value=Mock(transaction_id="test-txn"))
            manager.atomic_operation.return_value.__exit__ = Mock(return_value=False)
            mock.return_value = manager
            yield manager
    
    def test_master_orchestrator_has_business_knowledge_repository_attribute(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify MasterOrchestrator has _business_knowledge_repository attribute."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, '_business_knowledge_repository')
    
    def test_master_orchestrator_has_business_knowledge_property(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify has_business_knowledge_repository property exists."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, 'has_business_knowledge_repository')
        assert isinstance(orchestrator.has_business_knowledge_repository, bool)
    
    def test_master_orchestrator_get_business_knowledge_summary_method_exists(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify get_business_knowledge_summary method exists."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, 'get_business_knowledge_summary')
        assert callable(orchestrator.get_business_knowledge_summary)
    
    def test_master_orchestrator_query_business_knowledge_method_exists(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify query_business_knowledge method exists."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, 'query_business_knowledge')
        assert callable(orchestrator.query_business_knowledge)
    
    def test_master_orchestrator_evaluate_business_knowledge_method_exists(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify _evaluate_business_knowledge_for_request method exists."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, '_evaluate_business_knowledge_for_request')
        assert callable(orchestrator._evaluate_business_knowledge_for_request)


class TestMasterOrchestratorBusinessKnowledgeEvaluation:
    """Test business knowledge evaluation during coordinate_operation."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        with patch('src.orchestrators.core.master_orchestrator.EnhancedAuditLogger') as mock:
            logger_instance = Mock()
            mock.instance.return_value = logger_instance
            yield logger_instance
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        with patch('src.orchestrators.core.master_orchestrator.DatabaseManager') as mock:
            yield mock.return_value
    
    @pytest.fixture
    def mock_transaction_manager(self):
        """Create mock transaction manager."""
        with patch('src.orchestrators.core.master_orchestrator.DatabaseTransactionManager') as mock:
            manager = Mock()
            txn = Mock(transaction_id="test-txn-123")
            manager.atomic_operation.return_value.__enter__ = Mock(return_value=txn)
            manager.atomic_operation.return_value.__exit__ = Mock(return_value=False)
            mock.return_value = manager
            yield manager
    
    @pytest.fixture
    def mock_governance_registry(self):
        """Create mock governance registry."""
        with patch('src.orchestrators.core.master_orchestrator.GovernanceRegistry') as mock:
            registry = Mock()
            from cortex.core.result import Ok
            registry.initialize.return_value = Ok("initialized")
            registry.should_proceed.return_value = Ok(True)
            mock.instance.return_value = registry
            yield registry
    
    def test_evaluate_business_knowledge_returns_context_dict(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify _evaluate_business_knowledge_for_request returns dict with expected keys."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        context = orchestrator._evaluate_business_knowledge_for_request(
            operation="test_operation",
            context={"intent": "test"},
            target_domains=None
        )
        
        assert isinstance(context, dict)
        assert "business_knowledge_evaluated" in context
        assert "business_domains" in context
        assert "services" in context
        assert "apis" in context
        assert "workflows" in context


# =============================================================================
# TEST: COORDINATE_OPERATION WITH BOTH KNOWLEDGE TYPES
# =============================================================================

class TestCoordinateOperationUnifiedKnowledge:
    """Test coordinate_operation includes both technical and business knowledge."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        with patch('src.orchestrators.core.master_orchestrator.EnhancedAuditLogger') as mock:
            logger_instance = Mock()
            mock.instance.return_value = logger_instance
            yield logger_instance
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        with patch('src.orchestrators.core.master_orchestrator.DatabaseManager') as mock:
            yield mock.return_value
    
    @pytest.fixture
    def mock_transaction_manager(self):
        """Create mock transaction manager."""
        with patch('src.orchestrators.core.master_orchestrator.DatabaseTransactionManager') as mock:
            manager = Mock()
            txn = Mock(transaction_id="test-txn-456")
            manager.atomic_operation.return_value.__enter__ = Mock(return_value=txn)
            manager.atomic_operation.return_value.__exit__ = Mock(return_value=False)
            mock.return_value = manager
            yield manager
    
    @pytest.fixture
    def mock_governance(self):
        """Create mock governance registry."""
        with patch('src.orchestrators.core.master_orchestrator.GovernanceRegistry') as mock:
            registry = Mock()
            from cortex.core.result import Ok
            registry.initialize.return_value = Ok("initialized")
            registry.should_proceed.return_value = Ok(True)
            mock.instance.return_value = registry
            yield registry
    
    def test_coordinate_operation_includes_both_knowledge_contexts(
        self, mock_logger, mock_db, mock_transaction_manager, mock_governance
    ):
        """Verify coordinate_operation result includes both knowledge contexts."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        # Register a mock orchestrator
        mock_domain_orchestrator = Mock()
        mock_domain_orchestrator.get_name.return_value = "MockDomain"
        mock_domain_orchestrator.get_version.return_value = "1.0"
        orchestrator.register_orchestrator("mock_domain", mock_domain_orchestrator)
        
        # Execute coordinate_operation
        result = orchestrator.coordinate_operation(
            operation="process_payment",
            context={"intent": "validate payment", "business_domain": "payments"},
            target_domains=["mock_domain"]
        )
        
        assert result.is_ok()
        output = result.unwrap()
        
        # Verify BOTH knowledge contexts are present
        assert "knowledge_context" in output
        assert "business_knowledge_context" in output
        
        # Verify technical knowledge context structure
        tech_ctx = output["knowledge_context"]
        assert "knowledge_evaluated" in tech_ctx
        assert "guidelines" in tech_ctx
        assert "best_practices" in tech_ctx
        assert "security_considerations" in tech_ctx
        
        # Verify business knowledge context structure
        biz_ctx = output["business_knowledge_context"]
        assert "business_knowledge_evaluated" in biz_ctx
        assert "business_domains" in biz_ctx
        assert "services" in biz_ctx
        assert "apis" in biz_ctx


# =============================================================================
# TEST: GRACEFUL DEGRADATION
# =============================================================================

class TestBusinessKnowledgeGracefulDegradation:
    """Test graceful degradation when business knowledge is unavailable."""
    
    def test_orchestrator_works_without_business_knowledge_repository(self):
        """Verify orchestrator functions when business repository fails."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        with patch('src.orchestrators.core.master_orchestrator.EnhancedAuditLogger') as mock_logger:
            with patch('src.orchestrators.core.master_orchestrator.DatabaseManager'):
                with patch('src.orchestrators.core.master_orchestrator.DatabaseTransactionManager'):
                    # Patch BusinessKnowledgeRepository to raise exception
                    with patch(
                        'src.orchestrators.core.master_orchestrator.BusinessKnowledgeRepository',
                        side_effect=Exception("Connection failed")
                    ):
                        mock_logger.instance.return_value = Mock()
                        MasterOrchestrator._instance = None
                        
                        # Should not raise exception
                        orchestrator = MasterOrchestrator()
                        
                        # Repository should be None
                        assert orchestrator._business_knowledge_repository is None
                        assert orchestrator.has_business_knowledge_repository is False
    
    def test_evaluate_business_knowledge_returns_empty_when_unavailable(self):
        """Verify _evaluate_business_knowledge_for_request returns empty gracefully."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        with patch('src.orchestrators.core.master_orchestrator.EnhancedAuditLogger') as mock_logger:
            with patch('src.orchestrators.core.master_orchestrator.DatabaseManager'):
                with patch('src.orchestrators.core.master_orchestrator.DatabaseTransactionManager'):
                    with patch(
                        'src.orchestrators.core.master_orchestrator.BusinessKnowledgeRepository',
                        side_effect=Exception("Connection failed")
                    ):
                        mock_logger.instance.return_value = Mock()
                        MasterOrchestrator._instance = None
                        orchestrator = MasterOrchestrator()
                        
                        # Should return empty context, not error
                        context = orchestrator._evaluate_business_knowledge_for_request(
                            operation="test",
                            context={}
                        )
                        
                        assert context["business_knowledge_evaluated"] is False
                        assert context["services"] == []
                        assert context["apis"] == []


# =============================================================================
# TEST: BKIO ORCHESTRATOR WIRING
# =============================================================================

class TestBKIOOrchestratorWiring:
    """Test BKIO orchestrator can be registered and used with MasterOrchestrator."""
    
    def test_bkio_orchestrator_can_be_imported(self):
        """Verify BKIO orchestrator can be imported."""
        from cortex.domain_brain.bkio_orchestrator import BusinessKnowledgeIngestionOrchestrator
        assert BusinessKnowledgeIngestionOrchestrator is not None
    
    def test_bkio_inherits_orchestrator_base(self):
        """Verify BKIO inherits from OrchestratorBase."""
        from cortex.domain_brain.bkio_orchestrator import BusinessKnowledgeIngestionOrchestrator
        from cortex.core.orchestrator_base import OrchestratorBase
        
        assert issubclass(BusinessKnowledgeIngestionOrchestrator, OrchestratorBase)
    
    def test_bkio_can_be_registered_with_master_orchestrator(self):
        """Verify BKIO can be registered in MasterOrchestrator's domain_orchestrators."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.domain_brain.bkio_orchestrator import BusinessKnowledgeIngestionOrchestrator
        from cortex.core.orchestrator_base import OrchestrationContext
        from cortex.domain_brain.api import DomainBrainAPI
        
        with patch('src.orchestrators.core.master_orchestrator.EnhancedAuditLogger') as mock_logger:
            with patch('src.orchestrators.core.master_orchestrator.DatabaseManager'):
                with patch('src.orchestrators.core.master_orchestrator.DatabaseTransactionManager'):
                    mock_logger.instance.return_value = Mock()
                    MasterOrchestrator._instance = None
                    orchestrator = MasterOrchestrator()
                    
                    # Create BKIO instance
                    context = OrchestrationContext(
                        orchestrator_id="bkio-test",
                        orchestrator_name="BKIO Integration Test"
                    )
                    api = DomainBrainAPI()
                    bkio = BusinessKnowledgeIngestionOrchestrator(context, api)
                    
                    # Register BKIO (no version parameter - uses OrchestratorMetadata default)
                    result = orchestrator.register_orchestrator(
                        domain="business_knowledge",
                        orchestrator=bkio,
                        capabilities=["document_parsing", "conflict_resolution"]
                    )
                    
                    assert result.is_ok()
                    assert "business_knowledge" in orchestrator.domain_orchestrators


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
