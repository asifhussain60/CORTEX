"""
Integration Tests for MasterOrchestrator Knowledge Integration (AC-KN-002-01).

PHASE-REMEDIATION-06: Knowledge Repository Integration Tests
AC-ID: AC-KN-002-01 - Master Orchestrator Knowledge Awareness

Tests:
1. Knowledge repository initialization in MasterOrchestrator
2. Knowledge query methods (by domain, tags, keywords)
3. Knowledge evaluation during coordinate_operation
4. Knowledge context in composite request output
5. Graceful degradation when knowledge unavailable

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
# TEST: KNOWLEDGE REPOSITORY MODULE
# =============================================================================

class TestKnowledgeRepositoryModule:
    """Test KnowledgeRepository standalone functionality."""
    
    def test_knowledge_repository_class_exists(self):
        """Verify KnowledgeRepository class can be imported."""
        from src.core.knowledge.knowledge_repository import KnowledgeRepository
        assert KnowledgeRepository is not None
    
    def test_knowledge_entry_dataclass_exists(self):
        """Verify KnowledgeEntry dataclass can be imported."""
        from src.core.knowledge.knowledge_repository import KnowledgeEntry
        assert KnowledgeEntry is not None
    
    def test_knowledge_query_result_dataclass_exists(self):
        """Verify KnowledgeQueryResult dataclass can be imported."""
        from src.core.knowledge.knowledge_repository import KnowledgeQueryResult
        assert KnowledgeQueryResult is not None
    
    def test_get_knowledge_repository_singleton_exists(self):
        """Verify singleton accessor function exists."""
        from src.core.knowledge.knowledge_repository import get_knowledge_repository
        assert callable(get_knowledge_repository)


class TestKnowledgeRepositoryInitialization:
    """Test KnowledgeRepository initialization with actual files."""
    
    @pytest.fixture
    def knowledge_repo(self):
        """Create KnowledgeRepository instance."""
        from src.core.knowledge.knowledge_repository import KnowledgeRepository
        return KnowledgeRepository(project_root=str(project_root))
    
    def test_repository_initializes_successfully(self, knowledge_repo):
        """Verify repository initializes without error."""
        assert knowledge_repo.is_loaded is True
    
    def test_repository_loads_entries(self, knowledge_repo):
        """Verify repository loads knowledge entries."""
        assert knowledge_repo.entry_count > 0
        assert knowledge_repo.entry_count >= 35  # Known: 35 migrated files
    
    def test_repository_has_domains(self, knowledge_repo):
        """Verify repository has multiple domains."""
        domains = knowledge_repo.domains
        assert len(domains) > 0
        assert "ARCHITECTURE" in domains
        assert "SECURITY" in domains
    
    def test_repository_has_metadata(self, knowledge_repo):
        """Verify repository has metadata from index."""
        metadata = knowledge_repo.metadata
        assert "version" in metadata
        assert "entry_count" in metadata


class TestKnowledgeRepositoryQueries:
    """Test KnowledgeRepository query functionality."""
    
    @pytest.fixture
    def knowledge_repo(self):
        """Create KnowledgeRepository instance."""
        from src.core.knowledge.knowledge_repository import KnowledgeRepository
        return KnowledgeRepository(project_root=str(project_root))
    
    def test_get_by_domain_returns_entries(self, knowledge_repo):
        """Verify get_by_domain returns entries."""
        entries = knowledge_repo.get_by_domain("ARCHITECTURE")
        assert len(entries) > 0
    
    def test_get_by_domain_filters_correctly(self, knowledge_repo):
        """Verify all entries match requested domain."""
        entries = knowledge_repo.get_by_domain("SECURITY")
        for entry in entries:
            assert entry.domain == "SECURITY"
    
    def test_query_with_no_filters_returns_all(self, knowledge_repo):
        """Verify query with no filters returns all entries."""
        result = knowledge_repo.query()
        assert result.total_matches == knowledge_repo.entry_count
    
    def test_query_with_domain_filter(self, knowledge_repo):
        """Verify query filters by domain."""
        result = knowledge_repo.query(domains=["SECURITY"])
        assert result.total_matches > 0
        for entry in result.entries:
            assert entry.domain == "SECURITY"
    
    def test_query_with_multiple_domains(self, knowledge_repo):
        """Verify query handles multiple domains."""
        result = knowledge_repo.query(domains=["SECURITY", "ARCHITECTURE"])
        assert result.total_matches > 0
        domains_found = {e.domain for e in result.entries}
        assert domains_found.issubset({"SECURITY", "ARCHITECTURE"})
    
    def test_get_relevant_knowledge_returns_limited_results(self, knowledge_repo):
        """Verify get_relevant_knowledge respects max_entries."""
        entries = knowledge_repo.get_relevant_knowledge(max_entries=3)
        assert len(entries) <= 3


class TestKnowledgeRepositoryHelpers:
    """Test KnowledgeRepository helper methods."""
    
    @pytest.fixture
    def knowledge_repo(self):
        """Create KnowledgeRepository instance."""
        from src.core.knowledge.knowledge_repository import KnowledgeRepository
        return KnowledgeRepository(project_root=str(project_root))
    
    def test_get_security_knowledge(self, knowledge_repo):
        """Verify security knowledge helper."""
        entries = knowledge_repo.get_security_knowledge()
        for entry in entries:
            assert entry.domain == "SECURITY"
    
    def test_get_architecture_knowledge(self, knowledge_repo):
        """Verify architecture knowledge helper."""
        entries = knowledge_repo.get_architecture_knowledge()
        for entry in entries:
            assert entry.domain == "ARCHITECTURE"
    
    def test_get_knowledge_summary(self, knowledge_repo):
        """Verify knowledge summary method."""
        summary = knowledge_repo.get_knowledge_summary()
        assert "total_entries" in summary
        assert "domains" in summary
        assert "domain_counts" in summary
        assert summary["total_entries"] > 0


# =============================================================================
# TEST: MASTER ORCHESTRATOR KNOWLEDGE INTEGRATION
# =============================================================================

class TestMasterOrchestratorKnowledgeIntegration:
    """Test MasterOrchestrator knowledge repository integration."""
    
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
    
    def test_master_orchestrator_has_knowledge_repository_attribute(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify MasterOrchestrator has _knowledge_repository attribute."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        # Clear singleton
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, '_knowledge_repository')
    
    def test_master_orchestrator_has_knowledge_repository_property(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify has_knowledge_repository property exists."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, 'has_knowledge_repository')
        # Repository should be available if index exists
        assert isinstance(orchestrator.has_knowledge_repository, bool)
    
    def test_master_orchestrator_get_knowledge_summary_method_exists(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify get_knowledge_summary method exists."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, 'get_knowledge_summary')
        assert callable(orchestrator.get_knowledge_summary)
    
    def test_master_orchestrator_query_knowledge_method_exists(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify query_knowledge method exists."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, 'query_knowledge')
        assert callable(orchestrator.query_knowledge)
    
    def test_master_orchestrator_get_relevant_knowledge_method_exists(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify get_relevant_knowledge_for_operation method exists."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, 'get_relevant_knowledge_for_operation')
        assert callable(orchestrator.get_relevant_knowledge_for_operation)


class TestMasterOrchestratorKnowledgeQueries:
    """Test MasterOrchestrator knowledge query functionality."""
    
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
    
    @pytest.fixture
    def orchestrator(self, mock_logger, mock_db, mock_transaction_manager):
        """Create MasterOrchestrator instance."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        MasterOrchestrator._instance = None
        return MasterOrchestrator()
    
    def test_get_knowledge_summary_returns_result(self, orchestrator):
        """Verify get_knowledge_summary returns Result."""
        result = orchestrator.get_knowledge_summary()
        # Should return Ok or Err
        assert hasattr(result, 'is_ok') or hasattr(result, 'is_err')
    
    def test_query_knowledge_returns_result(self, orchestrator):
        """Verify query_knowledge returns Result."""
        result = orchestrator.query_knowledge(domains=["SECURITY"])
        assert hasattr(result, 'is_ok') or hasattr(result, 'is_err')
    
    def test_get_relevant_knowledge_for_operation_returns_result(self, orchestrator):
        """Verify get_relevant_knowledge_for_operation returns Result."""
        result = orchestrator.get_relevant_knowledge_for_operation(
            operation="validate_security",
            context={"intent": "security check"}
        )
        assert hasattr(result, 'is_ok') or hasattr(result, 'is_err')


class TestMasterOrchestratorKnowledgeEvaluation:
    """Test knowledge evaluation during coordinate_operation."""
    
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
            # Setup context manager
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
            from src.core.result import Ok
            registry.initialize.return_value = Ok("initialized")
            registry.should_proceed.return_value = Ok(True)
            mock.instance.return_value = registry
            yield registry
    
    def test_evaluate_knowledge_for_request_method_exists(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify _evaluate_knowledge_for_request method exists."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, '_evaluate_knowledge_for_request')
        assert callable(orchestrator._evaluate_knowledge_for_request)
    
    def test_evaluate_knowledge_returns_context_dict(
        self, mock_logger, mock_db, mock_transaction_manager
    ):
        """Verify _evaluate_knowledge_for_request returns dict with expected keys."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        context = orchestrator._evaluate_knowledge_for_request(
            operation="test_operation",
            context={"intent": "test"},
            target_domains=None
        )
        
        assert isinstance(context, dict)
        assert "knowledge_evaluated" in context
        assert "guidelines" in context
        assert "best_practices" in context
        assert "security_considerations" in context
        assert "architecture_patterns" in context


class TestMasterOrchestratorKnowledgeGracefulDegradation:
    """Test graceful degradation when knowledge repository is unavailable."""
    
    def test_orchestrator_works_without_knowledge_repository(self):
        """Verify orchestrator functions when repository fails to load."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        with patch('src.orchestrators.core.master_orchestrator.EnhancedAuditLogger') as mock_logger:
            with patch('src.orchestrators.core.master_orchestrator.DatabaseManager'):
                with patch('src.orchestrators.core.master_orchestrator.DatabaseTransactionManager'):
                    # Patch KnowledgeRepository to raise FileNotFoundError
                    with patch(
                        'src.orchestrators.core.master_orchestrator.KnowledgeRepository',
                        side_effect=FileNotFoundError("Index not found")
                    ):
                        mock_logger.instance.return_value = Mock()
                        MasterOrchestrator._instance = None
                        
                        # Should not raise exception
                        orchestrator = MasterOrchestrator()
                        
                        # Repository should be None
                        assert orchestrator._knowledge_repository is None
                        assert orchestrator.has_knowledge_repository is False
    
    def test_get_relevant_knowledge_returns_empty_when_unavailable(self):
        """Verify get_relevant_knowledge returns empty list gracefully."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        with patch('src.orchestrators.core.master_orchestrator.EnhancedAuditLogger') as mock_logger:
            with patch('src.orchestrators.core.master_orchestrator.DatabaseManager'):
                with patch('src.orchestrators.core.master_orchestrator.DatabaseTransactionManager'):
                    with patch(
                        'src.orchestrators.core.master_orchestrator.KnowledgeRepository',
                        side_effect=FileNotFoundError("Index not found")
                    ):
                        mock_logger.instance.return_value = Mock()
                        MasterOrchestrator._instance = None
                        orchestrator = MasterOrchestrator()
                        
                        # Should return Ok with empty list, not error
                        result = orchestrator.get_relevant_knowledge_for_operation(
                            operation="test",
                            context={}
                        )
                        
                        assert result.is_ok()
                        assert result.unwrap() == []


# =============================================================================
# TEST: INTEGRATION WITH COORDINATE_OPERATION
# =============================================================================

class TestCoordinateOperationKnowledgeIntegration:
    """Test knowledge integration in coordinate_operation flow."""
    
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
            from src.core.result import Ok
            registry.initialize.return_value = Ok("initialized")
            registry.should_proceed.return_value = Ok(True)
            mock.instance.return_value = registry
            yield registry
    
    def test_coordinate_operation_includes_knowledge_context(
        self, mock_logger, mock_db, mock_transaction_manager, mock_governance
    ):
        """Verify coordinate_operation result includes knowledge_context."""
        from src.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        MasterOrchestrator._instance = None
        orchestrator = MasterOrchestrator()
        
        # Register a mock orchestrator
        mock_domain_orchestrator = Mock()
        mock_domain_orchestrator.get_name.return_value = "MockDomain"
        mock_domain_orchestrator.get_version.return_value = "1.0"
        orchestrator.register_orchestrator("mock_domain", mock_domain_orchestrator)
        
        # Execute coordinate_operation
        result = orchestrator.coordinate_operation(
            operation="security_check",
            context={"intent": "validate security"},
            target_domains=["mock_domain"]
        )
        
        assert result.is_ok()
        output = result.unwrap()
        
        # Verify knowledge_context is present
        assert "knowledge_context" in output
        knowledge_ctx = output["knowledge_context"]
        
        # Verify expected keys
        assert "knowledge_evaluated" in knowledge_ctx
        assert "guidelines" in knowledge_ctx
        assert "best_practices" in knowledge_ctx
        assert "security_considerations" in knowledge_ctx


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
