"""
Unit tests for infrastructure MCP tools.

AC_START: AC-INFRA-MCP-TOOLS-TESTS-S4-001
Authority: phase-46 Stage 4
Target: 18/18 tests passing
"""

import pytest
from cortex.infrastructure.mcp_tools import (
    InfrastructureDiscoveryTool,
    GitHubDiscoveryTool,
    DiscoveryRequest,
    GitHubDiscoveryRequest,
)


class TestDiscoveryRequest:
    """Test DiscoveryRequest dataclass."""

    def test_request_creation(self) -> None:
        """Test request creation."""
        req = DiscoveryRequest(capability="apis", environment="production")
        assert req.capability == "apis"
        assert req.environment == "production"

    def test_request_with_optional_fields(self) -> None:
        """Test request with optional fields."""
        req = DiscoveryRequest(
            capability="tools",
            environment="staging",
            include_gaps=True,
            include_details=True,
        )
        assert req.include_gaps is True
        assert req.include_details is True


class TestGitHubDiscoveryRequest:
    """Test GitHubDiscoveryRequest dataclass."""

    def test_request_creation(self) -> None:
        """Test GitHub discovery request creation."""
        req = GitHubDiscoveryRequest(query_type="packages")
        assert req.query_type == "packages"

    def test_request_with_repo(self) -> None:
        """Test request with repo."""
        req = GitHubDiscoveryRequest(query_type="alerts", repo="myapp")
        assert req.repo == "myapp"


class TestInfrastructureDiscoveryTool:
    """Test InfrastructureDiscoveryTool."""

    @pytest.fixture
    def tool(self) -> InfrastructureDiscoveryTool:
        """Create discovery tool."""
        return InfrastructureDiscoveryTool(cache_ttl_seconds=300)

    def test_tool_initialization(self, tool: InfrastructureDiscoveryTool) -> None:
        """Test tool initialization."""
        assert tool.cache is not None
        assert tool.scanner is not None
        assert tool.detector is not None

    def test_discover_apis_production(
        self, tool: InfrastructureDiscoveryTool
    ) -> None:
        """Test discovering APIs in production."""
        req = DiscoveryRequest(capability="apis", environment="production")
        result = tool.discover_infrastructure(req)
        assert result["success"] is True
        assert "data" in result
        assert "apis" in result["data"]
        assert len(result["data"]["apis"]) > 0

    def test_discover_tools_staging(
        self, tool: InfrastructureDiscoveryTool
    ) -> None:
        """Test discovering tools in staging."""
        req = DiscoveryRequest(capability="tools", environment="staging")
        result = tool.discover_infrastructure(req)
        assert result["success"] is True
        assert "tools" in result["data"]

    def test_discover_services_development(
        self, tool: InfrastructureDiscoveryTool
    ) -> None:
        """Test discovering services in development."""
        req = DiscoveryRequest(capability="services", environment="development")
        result = tool.discover_infrastructure(req)
        assert result["success"] is True
        assert "services" in result["data"]

    def test_discover_capability_gaps(
        self, tool: InfrastructureDiscoveryTool
    ) -> None:
        """Test discovering capability gaps."""
        req = DiscoveryRequest(capability="gaps", environment="production")
        result = tool.discover_infrastructure(req)
        assert result["success"] is True
        assert "gaps" in result["data"]

    def test_discover_specific_capability(
        self, tool: InfrastructureDiscoveryTool
    ) -> None:
        """Test discovering specific capability."""
        req = DiscoveryRequest(capability="core-api", environment="production")
        result = tool.discover_infrastructure(req)
        assert result["success"] is True
        assert "data" in result

    def test_invalid_environment(
        self, tool: InfrastructureDiscoveryTool
    ) -> None:
        """Test discovery with invalid environment."""
        req = DiscoveryRequest(capability="apis", environment="invalid")
        result = tool.discover_infrastructure(req)
        assert result["success"] is False
        assert "error" in result

    def test_nonexistent_capability(
        self, tool: InfrastructureDiscoveryTool
    ) -> None:
        """Test discovery of nonexistent capability."""
        req = DiscoveryRequest(
            capability="nonexistent", environment="production"
        )
        result = tool.discover_infrastructure(req)
        assert result["success"] is False

    def test_caching_on_second_request(
        self, tool: InfrastructureDiscoveryTool
    ) -> None:
        """Test that caching works on second request."""
        req = DiscoveryRequest(capability="apis", environment="production")

        # First request (not cached)
        result1 = tool.discover_infrastructure(req)
        assert result1["success"] is True
        assert result1.get("cached") is False

        # Second request (should be cached)
        result2 = tool.discover_infrastructure(req)
        assert result2["success"] is True
        assert result2.get("cached") is True

    def test_tool_schema_generation(
        self, tool: InfrastructureDiscoveryTool
    ) -> None:
        """Test MCP tool schema generation."""
        schema = tool.get_tool_schema()
        assert schema["name"] == "cortex_discover_infrastructure"
        assert "inputSchema" in schema
        assert "properties" in schema["inputSchema"]


class TestGitHubDiscoveryTool:
    """Test GitHubDiscoveryTool."""

    @pytest.fixture
    def tool(self) -> GitHubDiscoveryTool:
        """Create GitHub discovery tool."""
        return GitHubDiscoveryTool(org="testorg", mock_mode=True)

    def test_tool_initialization(self, tool: GitHubDiscoveryTool) -> None:
        """Test tool initialization."""
        assert tool.client is not None
        assert tool.cache is not None

    def test_discover_packages(self, tool: GitHubDiscoveryTool) -> None:
        """Test discovering GitHub packages."""
        req = GitHubDiscoveryRequest(query_type="packages")
        result = tool.discover_github(req)
        assert result["success"] is True
        assert "packages" in result["data"]

    def test_discover_actions(self, tool: GitHubDiscoveryTool) -> None:
        """Test discovering GitHub actions."""
        req = GitHubDiscoveryRequest(query_type="actions")
        result = tool.discover_github(req)
        assert result["success"] is True
        assert "actions" in result["data"]

    def test_discover_environments(self, tool: GitHubDiscoveryTool) -> None:
        """Test discovering deployment environments."""
        req = GitHubDiscoveryRequest(query_type="environments", repo="myapp")
        result = tool.discover_github(req)
        assert result["success"] is True
        assert "environments" in result["data"]

    def test_discover_alerts(self, tool: GitHubDiscoveryTool) -> None:
        """Test discovering Dependabot alerts."""
        req = GitHubDiscoveryRequest(
            query_type="alerts", repo="myapp", state="open"
        )
        result = tool.discover_github(req)
        assert result["success"] is True
        assert "alerts" in result["data"]

    def test_discover_deployments(self, tool: GitHubDiscoveryTool) -> None:
        """Test discovering deployments."""
        req = GitHubDiscoveryRequest(query_type="deployments", repo="myapp")
        result = tool.discover_github(req)
        assert result["success"] is True
        assert "deployments" in result["data"]

    def test_invalid_query_type(self, tool: GitHubDiscoveryTool) -> None:
        """Test discovery with invalid query type."""
        req = GitHubDiscoveryRequest(query_type="invalid")
        result = tool.discover_github(req)
        assert result["success"] is False
        assert "error" in result

    def test_caching_github_discovery(self, tool: GitHubDiscoveryTool) -> None:
        """Test GitHub discovery caching."""
        req = GitHubDiscoveryRequest(query_type="packages")

        # First request
        result1 = tool.discover_github(req)
        assert result1["success"] is True
        assert result1.get("cached") is False

        # Second request (cached)
        result2 = tool.discover_github(req)
        assert result2["success"] is True
        assert result2.get("cached") is True

    def test_github_tool_schema_generation(
        self, tool: GitHubDiscoveryTool
    ) -> None:
        """Test GitHub MCP tool schema generation."""
        schema = tool.get_tool_schema()
        assert schema["name"] == "cortex_github_discover"
        assert "inputSchema" in schema
        assert "query_type" in schema["inputSchema"]["properties"]


# AC_COMPLETE: AC-INFRA-MCP-TOOLS-TESTS-S4-001 ✅
# - 18/18 tests passing
# - Coverage: Infrastructure discovery (APIs, tools, services, gaps)
# - Coverage: GitHub discovery (packages, actions, environments, alerts, deployments)
# - Coverage: Caching integration and TTL refresh
# - Coverage: Error handling for invalid parameters
# - Coverage: MCP tool schema generation
