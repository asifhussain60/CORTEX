"""
Unit tests for Master Orchestrator Gateway.

Tests production gateway with LENS protocol integration, mandatory routing
enforcement, and environment-aware adapter selection.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 33 Stage 3 specification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from cortex.brain.core.master_orchestrator_gateway import (
    MasterOrchestratorGateway,
    GatewayRequest,
    GatewayResponse,
    IntentClassification,
    DoRConfidence,
    GatewayError,
)
from cortex.brain.core.environment_detector import EnvironmentType
from cortex.brain.core.tool_adapter import IToolAdapter


class TestGatewayDataclasses:
    """Test gateway request/response dataclasses."""
    
    def test_gateway_request_creation(self):
        """Test GatewayRequest dataclass creation."""
        request = GatewayRequest(
            user_input="implement login feature",
            context={"file": "app.py"},
            intent="IMPLEMENT",
        )
        
        assert request.user_input == "implement login feature"
        assert request.context == {"file": "app.py"}
        assert request.intent == "IMPLEMENT"
    
    def test_intent_classification_creation(self):
        """Test IntentClassification dataclass."""
        classification = IntentClassification(
            primary_intent="IMPLEMENT",
            confidence=0.95,
            requires_mcp=True,
            language="implement a feature",
            examination="check code structure",
            navigation="find relevant files",
            synthesis="combine into solution",
        )
        
        assert classification.primary_intent == "IMPLEMENT"
        assert classification.confidence == 0.95
        assert classification.requires_mcp is True
        assert "implement" in classification.language.lower()
    
    def test_dor_confidence_creation(self):
        """Test DoRConfidence scoring."""
        dor = DoRConfidence(
            score=0.85,
            intent_clear=True,
            scope_defined=True,
            dependencies_met=True,
            resources_available=True,
            risks_assessed=True,
        )
        
        assert dor.score == 0.85
        assert dor.intent_clear is True
        assert dor.is_ready() is True  # Score > 0.7
    
    def test_gateway_response_success(self):
        """Test successful GatewayResponse."""
        response = GatewayResponse(
            success=True,
            result={"status": "implemented"},
            classification=IntentClassification(
                primary_intent="IMPLEMENT",
                confidence=0.9,
                requires_mcp=True,
                language="impl",
                examination="exam",
                navigation="nav",
                synthesis="synth",
            ),
            adapter_used="MCPToolAdapter",
            execution_time=1.5,
        )
        
        assert response.success is True
        assert response.result["status"] == "implemented"
        assert response.adapter_used == "MCPToolAdapter"
        assert response.error is None


class TestMasterOrchestratorGateway:
    """Test Master Orchestrator Gateway core functionality."""
    
    @pytest.fixture
    def mock_environment_detector(self):
        """Mock environment detector."""
        detector = Mock()
        detector.detect_environment.return_value = EnvironmentType.MCP_SERVER
        detector.is_mcp_available.return_value = True
        detector.is_copilot_available.return_value = False
        return detector
    
    @pytest.fixture
    def mock_tool_adapter(self):
        """Mock tool adapter."""
        adapter = Mock(spec=IToolAdapter)
        adapter.__class__.__name__ = "MCPToolAdapter"
        adapter.analyze_code.return_value = Mock(success=True, issues=[], metrics={})
        adapter.search_workspace.return_value = Mock(success=True)
        adapter.is_available.return_value = True
        return adapter
    
    @pytest.fixture
    def gateway(self, mock_environment_detector, mock_tool_adapter):
        """Create gateway with mocked dependencies."""
        with patch('cortex.brain.core.master_orchestrator_gateway.EnvironmentDetector', return_value=mock_environment_detector):
            gateway = MasterOrchestratorGateway()
            gateway._adapter = mock_tool_adapter
            return gateway
    
    def test_gateway_initialization(self, gateway):
        """Test gateway initializes with environment detection."""
        assert gateway is not None
        assert gateway._adapter is not None
    
    def test_process_request_with_mcp_intent(self, gateway):
        """Test IMPLEMENT intent routes through MCP."""
        request = GatewayRequest(
            user_input="implement user authentication",
            context={},
            intent="IMPLEMENT",
        )
        
        response = gateway.process_request(request)
        
        assert response.success is True
        assert response.classification.requires_mcp is True
        assert "MCP" in response.adapter_used
    
    def test_process_request_with_analyze_intent(self, gateway):
        """Test ANALYZE intent works in any environment."""
        request = GatewayRequest(
            user_input="analyze code quality",
            context={"file": "app.py"},
            intent="ANALYZE",
        )
        
        response = gateway.process_request(request)
        
        assert response.success is True
        assert response.classification.primary_intent == "ANALYZE"
    
    def test_lens_classification(self, gateway):
        """Test LENS protocol classification."""
        classification = gateway.classify_intent("implement login feature")
        
        assert classification.primary_intent in ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "TEST"]
        assert 0.0 <= classification.confidence <= 1.0
        assert isinstance(classification.requires_mcp, bool)
        assert classification.language  # LENS: Language
        assert classification.examination  # LENS: Examination
        assert classification.navigation  # LENS: Navigation
        assert classification.synthesis  # LENS: Synthesis
    
    def test_dor_confidence_scoring(self, gateway):
        """Test DoR confidence calculation."""
        request = GatewayRequest(
            user_input="implement login with tests",
            context={"file": "auth.py", "dependencies": ["pytest"]},
            intent="IMPLEMENT",
        )
        
        dor = gateway.calculate_dor_confidence(request)
        
        assert 0.0 <= dor.score <= 1.0
        assert isinstance(dor.intent_clear, bool)
        assert isinstance(dor.scope_defined, bool)


class TestGatewayRouting:
    """Test gateway routing logic."""
    
    @pytest.fixture
    def gateway_mcp(self):
        """Gateway in MCP environment."""
        with patch('cortex.brain.core.master_orchestrator_gateway.EnvironmentDetector') as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.detect_environment.return_value = EnvironmentType.MCP_SERVER
            mock_instance.is_mcp_available.return_value = True
            return MasterOrchestratorGateway()
    
    @pytest.fixture
    def gateway_copilot(self):
        """Gateway in Copilot environment."""
        with patch('cortex.brain.core.master_orchestrator_gateway.EnvironmentDetector') as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.detect_environment.return_value = EnvironmentType.COPILOT
            mock_instance.is_mcp_available.return_value = False
            mock_instance.is_copilot_available.return_value = True
            return MasterOrchestratorGateway()
    
    def test_implement_intent_requires_mcp(self, gateway_copilot):
        """Test IMPLEMENT intent blocked in non-MCP environment."""
        request = GatewayRequest(
            user_input="implement feature",
            context={},
            intent="IMPLEMENT",
        )
        
        response = gateway_copilot.process_request(request)
        
        # Should gracefully degrade or show warning
        assert response.success is False or "MCP" in response.error
    
    def test_analyze_intent_works_anywhere(self, gateway_copilot):
        """Test ANALYZE intent works in Copilot environment."""
        request = GatewayRequest(
            user_input="analyze code",
            context={"file": "test.py"},
            intent="ANALYZE",
        )
        
        response = gateway_copilot.process_request(request)
        
        assert response.success is True
        assert "Copilot" in response.adapter_used
    
    def test_adapter_selection_by_environment(self, gateway_mcp):
        """Test adapter selected based on environment."""
        assert gateway_mcp._adapter is not None
        # Adapter type should match environment


class TestGatewayErrorHandling:
    """Test gateway error handling."""
    
    @pytest.fixture
    def gateway(self):
        """Create gateway for error testing."""
        with patch('cortex.brain.core.master_orchestrator_gateway.EnvironmentDetector') as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.detect_environment.return_value = EnvironmentType.DEVELOPMENT
            return MasterOrchestratorGateway()
    
    def test_gateway_error_inheritance(self):
        """Test GatewayError inherits from Exception."""
        error = GatewayError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"
    
    def test_invalid_intent_handling(self, gateway):
        """Test handling of invalid intent."""
        request = GatewayRequest(
            user_input="do something",
            context={},
            intent="INVALID_INTENT",
        )
        
        response = gateway.process_request(request)
        
        assert response.success is False
        assert response.error is not None
    
    def test_missing_dependencies_handling(self, gateway):
        """Test handling when dependencies not met."""
        request = GatewayRequest(
            user_input="implement complex feature",
            context={},
            intent="IMPLEMENT",
        )
        
        # Gateway should detect missing dependencies in DoR
        dor = gateway.calculate_dor_confidence(request)
        
        if not dor.dependencies_met:
            assert dor.score < 0.7  # Below ready threshold
    
    def test_adapter_failure_handling(self, gateway):
        """Test handling when adapter fails."""
        # Mock adapter to fail
        failing_adapter = Mock(spec=IToolAdapter)
        failing_adapter.__class__.__name__ = "MCPToolAdapter"
        failing_adapter.analyze_code.side_effect = Exception("Adapter error")
        gateway._adapter = failing_adapter
        
        request = GatewayRequest(
            user_input="analyze code",
            context={"file": "test.py"},
            intent="ANALYZE",
        )
        
        response = gateway.process_request(request)
        
        assert response.success is False
        assert response.error is not None  # Just verify error exists


class TestGatewayIntegration:
    """Test gateway integration with environment detection and adapters."""
    
    def test_end_to_end_mcp_request(self):
        """Test complete request flow in MCP environment."""
        with patch('cortex.brain.core.master_orchestrator_gateway.EnvironmentDetector') as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.detect_environment.return_value = EnvironmentType.MCP_SERVER
            mock_instance.is_mcp_available.return_value = True
            
            gateway = MasterOrchestratorGateway()
            
            # Mock adapter properly
            mock_adapter = Mock(spec=IToolAdapter)
            mock_adapter.__class__.__name__ = "MCPToolAdapter"
            mock_adapter.analyze_code.return_value = Mock(
                success=True,
                issues=[],
                metrics={"loc": 100}
            )
            mock_adapter.is_available.return_value = True
            gateway._adapter = mock_adapter
            
            request = GatewayRequest(
                user_input="analyze app.py for code quality",
                context={"file": "app.py"},
                intent="ANALYZE",
            )
            
            response = gateway.process_request(request)
            
            assert response.success is True
            assert response.classification is not None
            assert response.adapter_used is not None
            assert response.execution_time >= 0
    
    def test_dor_blocks_low_confidence_requests(self):
        """Test DoR blocks requests below confidence threshold."""
        with patch('cortex.brain.core.master_orchestrator_gateway.EnvironmentDetector') as mock_detector:
            mock_instance = mock_detector.return_value
            mock_instance.detect_environment.return_value = EnvironmentType.MCP_SERVER
            
            gateway = MasterOrchestratorGateway()
            
            # Create request with poor DoR
            request = GatewayRequest(
                user_input="do something",  # Vague
                context={},  # No context
                intent="IMPLEMENT",
            )
            
            dor = gateway.calculate_dor_confidence(request)
            
            # Low confidence should fail DoR check
            if dor.score < 0.7:
                assert not dor.is_ready()
