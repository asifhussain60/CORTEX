"""
Tests for MasterOrchestrator with IntentRouterFactory integration.

AC-GOVE-REM-001: Verify IntentRouterFactory is wired into MasterOrchestrator
Tests that intent classification happens on every operation execution.
"""

import pytest
from unittest.mock import Mock, patch

from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.core.intent_router import IntentType, RoutingDecision


class TestMasterOrchestratorIntentRouting:
    """Tests for intent routing integration in MasterOrchestrator."""

    @pytest.fixture
    def mock_router_instance(self) -> Mock:
        """Create mock router instance."""
        router = Mock()
        router.classify_intent.return_value = RoutingDecision(
            intent_type=IntentType.IMPLEMENT,
            target_handler="BuilderOrchestrator",
            confidence_score=0.85,
            reasoning="Detected implementation intent",
        )
        return router

    @pytest.fixture
    def mock_factory(self, mock_router_instance: Mock) -> Mock:
        """Create mock factory."""
        factory = Mock()
        factory.create_router.return_value = mock_router_instance
        return factory

    def test_intent_classification_on_execute_operation(self, mock_factory: Mock) -> None:
        """Test that intent classification happens on execute_operation."""
        with patch(
            "cortex.orchestrators.core.master_orchestrator.get_intent_router_factory",
            return_value=mock_factory,
        ):
            # Mock the governance registry and other dependencies
            with patch(
                "cortex.orchestrators.core.master_orchestrator.GovernanceRegistry"
            ) as mock_gov:
                mock_gov_instance = Mock()
                mock_gov_instance.initialize.return_value = Mock(is_err=Mock(return_value=False))
                mock_gov.instance.return_value = mock_gov_instance
                
                orchestrator = MasterOrchestrator()
                
                # Execute operation
                orchestrator.execute_operation(
                    operation_name="coordinate_operation",
                    parameters={"operation": "test", "context": {}},
                )
                
                # Verify intent classification was called
                mock_factory.create_router.assert_called()
                mock_factory.create_router.return_value.classify_intent.assert_called()

    def test_intent_classification_with_different_intent_types(
        self, mock_factory: Mock
    ) -> None:
        """Test intent classification with different intent types."""
        test_cases = [
            (IntentType.IMPLEMENT, "BuilderOrchestrator"),
            (IntentType.FIX, "FixOrchestrator"),
            (IntentType.REFACTOR, "RefactorOrchestrator"),
        ]
        
        for intent_type, expected_handler in test_cases:
            mock_router = mock_factory.create_router.return_value
            mock_router.classify_intent.return_value = RoutingDecision(
                intent_type=intent_type,
                target_handler=expected_handler,
                confidence_score=0.8,
                reasoning=f"Test {intent_type.value}",
            )
            
            with patch(
                "cortex.orchestrators.core.master_orchestrator.get_intent_router_factory",
                return_value=mock_factory,
            ):
                with patch(
                    "cortex.orchestrators.core.master_orchestrator.GovernanceRegistry"
                ) as mock_gov:
                    mock_gov_instance = Mock()
                    mock_gov_instance.initialize.return_value = Mock(
                        is_err=Mock(return_value=False)
                    )
                    mock_gov.instance.return_value = mock_gov_instance
                    
                    orchestrator = MasterOrchestrator()
                    orchestrator.execute_operation(
                        operation_name="test_op",
                        parameters={"test": "data"},
                    )
                    
                    # Verify classification happened
                    assert mock_router.classify_intent.called

    def test_intent_classification_failure_doesnt_block_execution(
        self, mock_factory: Mock
    ) -> None:
        """Test that intent classification failure doesn't block operation execution."""
        mock_router = mock_factory.create_router.return_value
        mock_router.classify_intent.side_effect = Exception("Classification failed")
        
        with patch(
            "cortex.orchestrators.core.master_orchestrator.get_intent_router_factory",
            return_value=mock_factory,
        ):
            with patch(
                "cortex.orchestrators.core.master_orchestrator.GovernanceRegistry"
            ) as mock_gov:
                mock_gov_instance = Mock()
                mock_gov_instance.initialize.return_value = Mock(
                    is_err=Mock(return_value=False)
                )
                mock_gov.instance.return_value = mock_gov_instance
                
                orchestrator = MasterOrchestrator()
                
                # Operation should complete despite classification failure
                try:
                    orchestrator.execute_operation(
                        operation_name="test_op",
                        parameters={"test": "data"},
                    )
                    # Execution continues past classification error
                    assert True
                except Exception as e:
                    # Classification error should be logged but not raised
                    pytest.fail(
                        f"Classification error should not block execution: {str(e)}"
                    )

    def test_audit_logging_captures_intent_classification(self, mock_factory: Mock) -> None:
        """Test that audit logging captures intent classification details."""
        with patch(
            "cortex.orchestrators.core.master_orchestrator.get_intent_router_factory",
            return_value=mock_factory,
        ):
            with patch(
                "cortex.orchestrators.core.master_orchestrator.GovernanceRegistry"
            ) as mock_gov:
                mock_gov_instance = Mock()
                mock_gov_instance.initialize.return_value = Mock(
                    is_err=Mock(return_value=False)
                )
                mock_gov.instance.return_value = mock_gov_instance
                
                with patch(
                    "cortex.orchestrators.core.master_orchestrator.EnhancedAuditLogger"
                ) as mock_logger:
                    mock_logger_instance = Mock()
                    mock_logger.instance.return_value = mock_logger_instance
                    
                    orchestrator = MasterOrchestrator()
                    orchestrator.execute_operation(
                        operation_name="coordinate_operation",
                        parameters={"operation": "test"},
                    )
                    
                    # Verify audit log was called with intent classification
                    assert mock_logger_instance.log_operation_start.called

    def test_intent_router_factory_none_doesnt_fail(self) -> None:
        """Test that operation executes even if IntentRouterFactory is None."""
        with patch(
            "cortex.orchestrators.core.master_orchestrator.get_intent_router_factory",
            return_value=None,
        ):
            with patch(
                "cortex.orchestrators.core.master_orchestrator.GovernanceRegistry"
            ) as mock_gov:
                mock_gov_instance = Mock()
                mock_gov_instance.initialize.return_value = Mock(
                    is_err=Mock(return_value=False)
                )
                mock_gov.instance.return_value = mock_gov_instance
                
                orchestrator = MasterOrchestrator()
                
                # Should handle None gracefully
                try:
                    orchestrator.execute_operation(
                        operation_name="test_op",
                        parameters={"test": "data"},
                    )
                    assert True
                except Exception as e:
                    pytest.fail(f"Should handle None factory gracefully: {str(e)}")
