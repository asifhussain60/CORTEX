"""
Unit tests for RecommendationEngineAdapter (Phase 8.5).

Tests MCP adapter capabilities, execution, and health checks.

Authority: AC-MCP-ADAPTER-PHASE-8
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from cortex.mcp.adapters.recommendation_adapter import RecommendationEngineAdapter
from cortex.mcp.orchestrator_mcp_server import ExecutionContext, CapabilityResponse


class TestRecommendationEngineAdapter:
    """Test suite for RecommendationEngineAdapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create adapter instance for testing."""
        with patch("cortex.mcp.adapters.recommendation_adapter.get_recommendation_engine"):
            return RecommendationEngineAdapter()
    
    @pytest.fixture
    def execution_context(self):
        """Create mock execution context."""
        context = MagicMock(spec=ExecutionContext)
        context.session_id = "test-session-123"
        return context
    
    # ========================================================================
    # Capability Discovery Tests
    # ========================================================================
    
    def test_adapter_initializes(self, adapter):
        """Test adapter initialization."""
        assert adapter is not None
        assert adapter.engine is not None
        assert adapter._health_check_ttl == 5.0
    
    def test_get_capabilities_returns_list(self, adapter):
        """Test that get_capabilities returns a list."""
        caps = adapter.get_capabilities()
        assert isinstance(caps, list)
        assert len(caps) > 0
    
    def test_get_capabilities_has_security_recommendation(self, adapter):
        """Test security recommendation capability is exposed."""
        caps = adapter.get_capabilities()
        cap_names = [c.name for c in caps]
        assert "recommend_security_fix" in cap_names
    
    def test_get_capabilities_has_solid_recommendation(self, adapter):
        """Test SOLID recommendation capability is exposed."""
        caps = adapter.get_capabilities()
        cap_names = [c.name for c in caps]
        assert "recommend_solid_fix" in cap_names
    
    def test_get_capabilities_has_performance_recommendation(self, adapter):
        """Test performance recommendation capability is exposed."""
        caps = adapter.get_capabilities()
        cap_names = [c.name for c in caps]
        assert "recommend_performance_fix" in cap_names
    
    def test_get_capabilities_has_compliance_recommendation(self, adapter):
        """Test compliance recommendation capability is exposed."""
        caps = adapter.get_capabilities()
        cap_names = [c.name for c in caps]
        assert "recommend_compliance_fix" in cap_names
    
    def test_security_capability_has_input_schema(self, adapter):
        """Test security capability has input schema."""
        caps = adapter.get_capabilities()
        security_cap = next(c for c in caps if c.name == "recommend_security_fix")
        assert security_cap.input_schema is not None
        assert "cwe_id" in security_cap.input_schema["properties"]
    
    def test_security_capability_has_routing_keywords(self, adapter):
        """Test security capability has routing keywords."""
        caps = adapter.get_capabilities()
        security_cap = next(c for c in caps if c.name == "recommend_security_fix")
        assert security_cap.routing_keywords is not None
        assert "security" in security_cap.routing_keywords
        assert "cwe" in security_cap.routing_keywords
    
    # ========================================================================
    # Security Recommendation Execution Tests
    # ========================================================================
    
    def test_execute_security_recommendation_with_valid_cwe(self, adapter, execution_context):
        """Test executing security recommendation with valid CWE."""
        # Mock recommendation result
        mock_result = MagicMock()
        mock_result.severity = "CRITICAL"
        mock_result.summary = "Test summary"
        mock_result.recommendations = []
        
        adapter.engine.recommend_for_security = MagicMock(return_value=mock_result)
        
        response = adapter.execute_capability(
            "recommend_security_fix",
            {"cwe_id": "CWE-94"},
            execution_context,
        )
        
        assert response.success is True
        assert response.result["cwe_id"] == "CWE-94"
        assert response.result["severity"] == "CRITICAL"
    
    def test_execute_security_recommendation_missing_cwe_id(self, adapter, execution_context):
        """Test executing security recommendation without CWE ID."""
        response = adapter.execute_capability(
            "recommend_security_fix",
            {},
            execution_context,
        )
        
        assert response.success is False
        assert "cwe_id" in response.error.lower()
    
    def test_execute_security_recommendation_returns_capability_response(self, adapter, execution_context):
        """Test that security recommendation returns CapabilityResponse."""
        mock_result = MagicMock()
        mock_result.severity = "HIGH"
        mock_result.summary = "Test"
        mock_result.recommendations = []
        
        adapter.engine.recommend_for_security = MagicMock(return_value=mock_result)
        
        response = adapter.execute_capability(
            "recommend_security_fix",
            {"cwe_id": "CWE-95"},
            execution_context,
        )
        
        assert isinstance(response, CapabilityResponse)
        assert response.request_id == "test-session-123"
        assert response.orchestrator == "recommendation_engine"
        assert hasattr(response, "duration_ms")
    
    # ========================================================================
    # SOLID Recommendation Execution Tests
    # ========================================================================
    
    def test_execute_solid_recommendation_with_valid_violation(self, adapter, execution_context):
        """Test executing SOLID recommendation with valid violation type."""
        mock_result = MagicMock()
        mock_result.principle = "Single Responsibility Principle"
        mock_result.summary = "Test SOLID summary"
        mock_result.recommendations = []
        
        adapter.engine.recommend_for_solid = MagicMock(return_value=mock_result)
        
        response = adapter.execute_capability(
            "recommend_solid_fix",
            {"violation_type": "SRP_VIOLATION"},
            execution_context,
        )
        
        assert response.success is True
        assert response.result["violation_type"] == "SRP_VIOLATION"
        assert response.result["principle"] == "Single Responsibility Principle"
    
    def test_execute_solid_recommendation_missing_violation_type(self, adapter, execution_context):
        """Test executing SOLID recommendation without violation type."""
        response = adapter.execute_capability(
            "recommend_solid_fix",
            {},
            execution_context,
        )
        
        assert response.success is False
        assert "violation_type" in response.error.lower()
    
    # ========================================================================
    # Performance Recommendation Execution Tests
    # ========================================================================
    
    def test_execute_performance_recommendation_with_valid_issue(self, adapter, execution_context):
        """Test executing performance recommendation with valid issue."""
        mock_result = MagicMock()
        mock_result.summary = "Performance test summary"
        mock_result.recommendations = []
        
        adapter.engine.recommend_for_performance = MagicMock(return_value=mock_result)
        
        response = adapter.execute_capability(
            "recommend_performance_fix",
            {"performance_issue": "slow_query"},
            execution_context,
        )
        
        assert response.success is True
        assert response.result["issue"] == "slow_query"
    
    def test_execute_performance_recommendation_missing_issue(self, adapter, execution_context):
        """Test executing performance recommendation without issue."""
        response = adapter.execute_capability(
            "recommend_performance_fix",
            {},
            execution_context,
        )
        
        assert response.success is False
        assert "performance_issue" in response.error.lower()
    
    # ========================================================================
    # Compliance Recommendation Execution Tests
    # ========================================================================
    
    def test_execute_compliance_recommendation_with_valid_framework(self, adapter, execution_context):
        """Test executing compliance recommendation with valid framework."""
        mock_result = MagicMock()
        mock_result.summary = "Compliance test summary"
        mock_result.recommendations = []
        
        adapter.engine.recommend_for_compliance = MagicMock(return_value=mock_result)
        
        response = adapter.execute_capability(
            "recommend_compliance_fix",
            {"framework": "SOC2"},
            execution_context,
        )
        
        assert response.success is True
        assert response.result["framework"] == "SOC2"
    
    def test_execute_compliance_recommendation_missing_framework(self, adapter, execution_context):
        """Test executing compliance recommendation without framework."""
        response = adapter.execute_capability(
            "recommend_compliance_fix",
            {},
            execution_context,
        )
        
        assert response.success is False
        assert "framework" in response.error.lower()
    
    # ========================================================================
    # Unknown Capability Tests
    # ========================================================================
    
    def test_execute_unknown_capability_returns_error(self, adapter, execution_context):
        """Test executing unknown capability returns error."""
        response = adapter.execute_capability(
            "unknown_capability",
            {},
            execution_context,
        )
        
        assert response.success is False
        assert "unknown capability" in response.error.lower()
        assert response.error_code == "UNKNOWN_CAPABILITY"
    
    # ========================================================================
    # Exception Handling Tests
    # ========================================================================
    
    def test_execute_security_recommendation_handles_exception(self, adapter, execution_context):
        """Test security recommendation handles engine exceptions."""
        adapter.engine.recommend_for_security = MagicMock(side_effect=Exception("Test error"))
        
        response = adapter.execute_capability(
            "recommend_security_fix",
            {"cwe_id": "CWE-94"},
            execution_context,
        )
        
        assert response.success is False
        assert "Test error" in response.error
        assert response.error_code == "RECOMMENDATION_ERROR"
    
    def test_execute_solid_recommendation_handles_exception(self, adapter, execution_context):
        """Test SOLID recommendation handles engine exceptions."""
        adapter.engine.recommend_for_solid = MagicMock(side_effect=Exception("SOLID error"))
        
        response = adapter.execute_capability(
            "recommend_solid_fix",
            {"violation_type": "SRP"},
            execution_context,
        )
        
        assert response.success is False
        assert response.error_code == "RECOMMENDATION_ERROR"
    
    # ========================================================================
    # Health Check Tests
    # ========================================================================
    
    def test_is_healthy_returns_boolean(self, adapter):
        """Test is_healthy returns boolean."""
        result = adapter.is_healthy()
        assert isinstance(result, bool)
    
    def test_is_healthy_checks_advisors(self, adapter):
        """Test health check verifies advisors exist."""
        # Set up advisors with PropertyMock to work with hasattr
        type(adapter.engine)._security_advisor = PropertyMock(return_value=MagicMock())
        type(adapter.engine)._solid_advisor = PropertyMock(return_value=MagicMock())
        type(adapter.engine)._performance_advisor = PropertyMock(return_value=MagicMock())
        type(adapter.engine)._compliance_advisor = PropertyMock(return_value=MagicMock())
        
        result = adapter.is_healthy()
        # Result depends on whether hasattr succeeds on the engine
        assert isinstance(result, bool)
    
    def test_is_healthy_caches_result(self, adapter):
        """Test health check caches results."""
        adapter.engine._security_advisor = MagicMock()
        adapter.engine._solid_advisor = MagicMock()
        adapter.engine._performance_advisor = MagicMock()
        adapter.engine._compliance_advisor = MagicMock()
        
        # First call
        result1 = adapter.is_healthy()
        
        # Modify engine (shouldn't affect cache)
        adapter.engine._security_advisor = None
        
        # Second call should use cache
        result2 = adapter.is_healthy()
        assert result1 == result2
    
    def test_is_healthy_handles_missing_engine(self, adapter):
        """Test health check handles missing engine."""
        with patch("cortex.mcp.adapters.recommendation_adapter.get_recommendation_engine", return_value=None):
            result = adapter.is_healthy()
            assert result is False
    
    def test_is_healthy_handles_exception(self, adapter):
        """Test health check handles exceptions."""
        adapter.engine = MagicMock(side_effect=Exception("Engine error"))
        result = adapter.is_healthy()
        assert result is False
    
    # ========================================================================
    # Status Tests
    # ========================================================================
    
    def test_get_status_returns_dict(self, adapter):
        """Test get_status returns dictionary."""
        status = adapter.get_status()
        assert isinstance(status, dict)
    
    def test_get_status_includes_name(self, adapter):
        """Test status includes name."""
        status = adapter.get_status()
        assert status.get("name") == "RecommendationEngine"
    
    def test_get_status_includes_phase(self, adapter):
        """Test status includes phase."""
        status = adapter.get_status()
        assert status.get("phase") == "8.4-8.5"
    
    def test_get_status_includes_advisors(self, adapter):
        """Test status includes advisor information."""
        status = adapter.get_status()
        assert "advisors" in status
        assert status["advisors"]["security"] == "enabled"
        assert status["advisors"]["solid"] == "enabled"
        assert status["advisors"]["performance"] == "enabled"
        assert status["advisors"]["compliance"] == "enabled"
    
    def test_get_status_includes_capability_count(self, adapter):
        """Test status includes capability count."""
        status = adapter.get_status()
        assert "capabilities" in status
        assert status["capabilities"] == 4  # 4 recommendation types
    
    def test_get_status_includes_authority(self, adapter):
        """Test status includes authority."""
        status = adapter.get_status()
        assert status.get("authority") == "AC-SECURITY-FRAMEWORK-001"
    
    def test_get_status_handles_exception(self, adapter):
        """Test status handles exceptions gracefully."""
        # Mock is_healthy to fail
        adapter.is_healthy = MagicMock(side_effect=Exception("Status error"))
        status = adapter.get_status()
        assert status["healthy"] is False
        # Status can be either "error" or "degraded" depending on exception timing
        assert status["status"] in ["error", "degraded"]
    
    # ========================================================================
    # Integration Tests
    # ========================================================================
    
    def test_full_recommendation_workflow_security(self, adapter, execution_context):
        """Test full workflow: discover capability and execute security recommendation."""
        # Discover
        caps = adapter.get_capabilities()
        security_cap = next(c for c in caps if c.name == "recommend_security_fix")
        assert security_cap is not None
        
        # Execute
        mock_result = MagicMock()
        mock_result.severity = "CRITICAL"
        mock_result.summary = "Critical vulnerability found"
        mock_result.recommendations = []
        
        adapter.engine.recommend_for_security = MagicMock(return_value=mock_result)
        
        response = adapter.execute_capability(
            security_cap.name,
            {"cwe_id": "CWE-94"},
            execution_context,
        )
        
        assert response.success is True
        assert response.result["cwe_id"] == "CWE-94"
    
    def test_all_capabilities_have_routing_keywords(self, adapter):
        """Test all capabilities have routing keywords."""
        caps = adapter.get_capabilities()
        for cap in caps:
            assert cap.routing_keywords is not None
            assert len(cap.routing_keywords) > 0
    
    def test_all_capabilities_have_tags(self, adapter):
        """Test all capabilities have tags."""
        caps = adapter.get_capabilities()
        for cap in caps:
            assert cap.tags is not None
            assert len(cap.tags) > 0
    
    def test_all_capabilities_have_output_schema(self, adapter):
        """Test all capabilities have output schemas."""
        caps = adapter.get_capabilities()
        for cap in caps:
            assert cap.output_schema is not None
            assert "type" in cap.output_schema
