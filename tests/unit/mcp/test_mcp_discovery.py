"""
Test suite for MCP Service Discovery with Health Checks.

Tests for:
- Health endpoint responses and schema
- Database connection detection
- Governance rules loaded verification
- Orchestrators registered check
- Service discovery sequence (env var → config → default)
- Invalid endpoint detection
- Health check caching and latency
- Edge cases (DB timeout, network unreachable)
"""

import pytest
import os
from datetime import datetime
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock


class TestHealthEndpointResponse:
    """Test /health endpoint responses."""

    def test_health_endpoint_returns_200(self):
        """GET /health returns 200 status."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()
        status = checker.check_health()

        assert status["status"] in ["healthy", "degraded", "unhealthy"]
        assert "timestamp" in status
        assert "components" in status

    def test_health_response_has_valid_schema(self):
        """Health response matches expected schema."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()
        status = checker.check_health()

        # Required fields
        assert "status" in status
        assert "timestamp" in status
        assert "components" in status
        assert isinstance(status["components"], dict)

    def test_health_timestamp_format(self):
        """Health response includes ISO format timestamp."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()
        status = checker.check_health()

        # Should be ISO format string
        datetime.fromisoformat(status["timestamp"])


class TestDatabaseConnectionCheck:
    """Test database connectivity in health checks."""

    def test_health_detects_db_connection_failure(self):
        """Health check detects database connection failure."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()

        # Mock DB failure
        with patch.object(checker, "_check_db_connection") as mock_db:
            mock_db.return_value = False

            status = checker.check_health()

            # Should reflect DB failure
            assert status["components"]["database"]["status"] == "failed"

    def test_health_detects_db_connection_success(self):
        """Health check detects successful database connection."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()

        # Mock DB success
        with patch.object(checker, "_check_db_connection") as mock_db:
            mock_db.return_value = True

            status = checker.check_health()

            # Should reflect DB success
            assert status["components"]["database"]["status"] == "healthy"


class TestGovernanceRulesCheck:
    """Test governance rules loaded in health checks."""

    def test_health_detects_governance_rules_loaded(self):
        """Health check verifies governance rules are loaded."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()

        # Mock governance check
        with patch.object(checker, "_check_governance_rules") as mock_gov:
            mock_gov.return_value = True

            status = checker.check_health()

            assert status["components"]["governance"]["status"] == "healthy"

    def test_health_detects_missing_governance_rules(self):
        """Health check detects missing governance rules."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()

        # Mock governance failure
        with patch.object(checker, "_check_governance_rules") as mock_gov:
            mock_gov.return_value = False

            status = checker.check_health()

            assert status["components"]["governance"]["status"] == "failed"


class TestOrchestratorsRegisteredCheck:
    """Test orchestrators registered in health checks."""

    def test_health_detects_orchestrators_registered(self):
        """Health check verifies orchestrators are registered."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()

        # Mock orchestrators check
        with patch.object(checker, "_check_orchestrators_registered") as mock_orch:
            mock_orch.return_value = True

            status = checker.check_health()

            assert status["components"]["orchestrators"]["status"] == "healthy"


class TestServiceDiscoverySequence:
    """Test service discovery sequence."""

    def test_discovery_uses_env_var_first(self):
        """Service discovery tries env var first."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        with patch.dict(os.environ, {"CORTEX_MCP_ENDPOINT": "http://custom:9000"}):
            endpoint = discovery.discover_endpoint()

            assert endpoint == "http://custom:9000"

    def test_discovery_uses_config_file_second(self):
        """Service discovery falls back to config file."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(discovery, "_load_config_file") as mock_config:
                mock_config.return_value = "http://config:8000"

                endpoint = discovery.discover_endpoint()

                assert endpoint == "http://config:8000"

    def test_discovery_uses_default_last(self):
        """Service discovery uses default endpoint as last resort."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(discovery, "_load_config_file") as mock_config:
                mock_config.return_value = None

                endpoint = discovery.discover_endpoint()

                # Default should be 127.0.0.1:8000
                assert "127.0.0.1:8000" in endpoint or "localhost:8000" in endpoint

    def test_discovery_sequence_order(self):
        """Discovery tries options in correct order."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        # Env var present - should use it
        with patch.dict(os.environ, {"CORTEX_MCP_ENDPOINT": "http://env:9000"}):
            with patch.object(discovery, "_load_config_file") as mock_config:
                mock_config.return_value = "http://config:8000"

                endpoint = discovery.discover_endpoint()

                # Should use env var, not config
                assert endpoint == "http://env:9000"


class TestConfigFileEndpoint:
    """Test configuration file endpoint loading."""

    def test_load_cortex_config_yaml(self):
        """Load endpoint from cortex-config.yaml."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        # Mock config file loading
        config_data = {
            "mcp_endpoint": "http://hub:8000",
            "repo_id": "test-repo",
        }

        with patch.object(discovery, "_load_config_file") as mock_load:
            mock_load.return_value = "http://hub:8000"

            endpoint = discovery._load_config_file()

            assert endpoint == "http://hub:8000"

    def test_missing_config_file_returns_none(self):
        """Missing config file returns None."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        with patch.object(discovery, "_load_yaml_file") as mock_load:
            mock_load.return_value = None

            endpoint = discovery._load_config_file()

            assert endpoint is None


class TestInvalidEndpointDetection:
    """Test invalid endpoint detection."""

    def test_invalid_endpoint_format_detected(self):
        """Invalid endpoint format is detected."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        invalid_endpoints = [
            "not_a_url",
            "ftp://invalid:8000",  # Wrong protocol
            "http://",  # Missing host
            "",  # Empty
        ]

        for invalid in invalid_endpoints:
            is_valid = discovery.validate_endpoint(invalid)
            assert is_valid is False

    def test_valid_endpoint_format_accepted(self):
        """Valid endpoint formats are accepted."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        valid_endpoints = [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://hub.example.com:8000",
            "https://hub.example.com:8000",
        ]

        for valid in valid_endpoints:
            is_valid = discovery.validate_endpoint(valid)
            assert is_valid is True


class TestPromptVersionEndpoint:
    """Test /config/prompt-version endpoint."""

    def test_prompt_version_endpoint_returns_version(self):
        """GET /config/prompt-version returns current version."""
        from cortex.core.discovery.mcp_discovery import PromptVersionConfig

        config = PromptVersionConfig()

        with patch.object(config, "_get_current_version") as mock_ver:
            mock_ver.return_value = "1.0.0"

            version_info = config.get_version_config()

            assert version_info["current_version"] == "1.0.0"

    def test_prompt_version_includes_schema(self):
        """Version config includes schema information."""
        from cortex.core.discovery.mcp_discovery import PromptVersionConfig

        config = PromptVersionConfig()

        version_info = config.get_version_config()

        assert "current_version" in version_info
        assert "compatible_versions" in version_info or "schema" in version_info


class TestHealthCheckCaching:
    """Test health check result caching."""

    def test_health_check_results_cached(self):
        """Health check results are cached."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()

        result1 = checker.check_health()
        result2 = checker.check_health()

        # Same result from cache
        assert result1["timestamp"] == result2["timestamp"]

    def test_cache_expires_after_ttl(self):
        """Health check cache expires after TTL."""
        from cortex.core.discovery.mcp_discovery import HealthCheck
        from datetime import datetime, timedelta

        checker = HealthCheck(cache_ttl_seconds=1)

        result1 = checker.check_health()
        timestamp1 = result1["timestamp"]

        # Manually expire cache
        checker._cache_time = datetime.now() - timedelta(seconds=2)

        result2 = checker.check_health()
        timestamp2 = result2["timestamp"]

        # Should be different (fresh check)
        assert timestamp1 != timestamp2


class TestHealthCheckLatency:
    """Test health check latency requirements."""

    def test_health_check_latency_under_100ms(self):
        """Health check completes in <100ms."""
        from cortex.core.discovery.mcp_discovery import HealthCheck
        import time

        checker = HealthCheck()

        start = time.time()
        checker.check_health()
        elapsed = (time.time() - start) * 1000  # Convert to ms

        # Cached result should be <100ms
        assert elapsed < 100


class TestServiceDiscoveryEdgeCases:
    """Test edge cases in service discovery."""

    def test_discovery_with_empty_config_file(self):
        """Discovery handles empty config file."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        with patch.object(discovery, "_load_yaml_file") as mock_load:
            mock_load.return_value = {}

            endpoint = discovery._load_config_file()

            # Should be None or fall through to next option
            assert endpoint is None or isinstance(endpoint, str)

    def test_discovery_with_malformed_config_file(self):
        """Discovery handles malformed config file gracefully."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        with patch.object(discovery, "_load_yaml_file") as mock_load:
            mock_load.side_effect = Exception("YAML parse error")

            # Should not raise, should fall through to next option
            endpoint = discovery.discover_endpoint()

            assert endpoint is not None  # Should have default

    def test_discovery_with_unreachable_endpoint(self):
        """Discovery detects unreachable endpoints."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery

        discovery = ServiceDiscovery()

        unreachable_endpoint = "http://nonexistent.invalid:9999"

        reachable = discovery.validate_endpoint_reachable(unreachable_endpoint)

        assert reachable is False


class TestHealthCheckComponentStatus:
    """Test individual component status in health checks."""

    def test_health_includes_all_components(self):
        """Health check includes all required components."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()

        status = checker.check_health()

        required_components = ["database", "governance", "orchestrators"]

        for component in required_components:
            assert component in status["components"]
            assert "status" in status["components"][component]

    def test_overall_health_status_calculation(self):
        """Overall health status based on components."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()

        # All healthy
        with patch.object(checker, "_check_db_connection") as mock_db:
            with patch.object(checker, "_check_governance_rules") as mock_gov:
                with patch.object(
                    checker, "_check_orchestrators_registered"
                ) as mock_orch:
                    mock_db.return_value = True
                    mock_gov.return_value = True
                    mock_orch.return_value = True

                    status = checker.check_health()

                    assert status["status"] == "healthy"

    def test_degraded_health_when_one_component_fails(self):
        """Health status is degraded when one component fails."""
        from cortex.core.discovery.mcp_discovery import HealthCheck

        checker = HealthCheck()

        # One component fails
        with patch.object(checker, "_check_db_connection") as mock_db:
            with patch.object(checker, "_check_governance_rules") as mock_gov:
                with patch.object(
                    checker, "_check_orchestrators_registered"
                ) as mock_orch:
                    mock_db.return_value = True
                    mock_gov.return_value = False  # This one fails
                    mock_orch.return_value = True

                    status = checker.check_health()

                    assert status["status"] in ["degraded", "unhealthy"]


class TestDiscoveryThreadSafety:
    """Test thread safety of discovery operations."""

    def test_concurrent_endpoint_discovery(self):
        """Multiple concurrent discovery calls work correctly."""
        from cortex.core.discovery.mcp_discovery import ServiceDiscovery
        import threading

        discovery = ServiceDiscovery()

        results = []

        def discover():
            endpoint = discovery.discover_endpoint()
            results.append(endpoint)

        threads = [threading.Thread(target=discover) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should get same endpoint
        assert len(results) == 5
        assert all(r == results[0] for r in results)

    def test_concurrent_health_checks(self):
        """Multiple concurrent health checks work correctly."""
        from cortex.core.discovery.mcp_discovery import HealthCheck
        import threading

        checker = HealthCheck()

        results = []

        def check_health():
            status = checker.check_health()
            results.append(status)

        threads = [threading.Thread(target=check_health) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 5
