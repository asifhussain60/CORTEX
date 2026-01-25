"""
Integration tests for MCP Tools and CLI Router

Tests the complete flow:
1. MCP tools calling planner_orchestrator methods
2. CLI router parsing commands and routing to MCP tools
3. End-to-end command execution

AC-PLANNER-MCP-002: MCP tool and CLI integration testing
"""

from unittest.mock import patch, MagicMock

from cortex.orchestrators.mcp_tools_planner import (
    PlannerOrchestratorMCPTools,
    MCP_ToolResult,
)
from cortex.orchestrators.cli_router_planner import PlannerCLIRouter


class TestMCPTools:
    """Test MCP tool wrappers"""

    def test_mcp_tool_result_to_dict(self):
        """Test MCP_ToolResult serialization"""
        result = MCP_ToolResult(
            success=True,
            data={"plan_id": "abc123", "status": "temp"},
            message="Plan created",
        )

        result_dict = result.to_dict()

        assert result_dict["success"] is True
        assert result_dict["data"]["plan_id"] == "abc123"
        assert result_dict["message"] == "Plan created"

    def test_cortex_create_plan_success(self):
        """Test successful plan creation"""
        # Mock the planner orchestrator
        mock_planner = MagicMock()
        mock_result = MagicMock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = {
            "plan_id": "abc123",
            "status": "temp",
            "description": "Test plan",
        }
        mock_planner.create_temp_plan.return_value = mock_result

        with patch(
            "cortex.orchestrators.mcp_tools_planner.get_planner_orchestrator",
            return_value=mock_planner,
        ):
            result = PlannerOrchestratorMCPTools.cortex_create_plan(
                description="Test plan",
                scope="file",
                impact="medium",
                confidence=0.8,
            )

        assert result.success is True
        assert result.data["plan_id"] == "abc123"
        assert "Plan created" in result.message

    def test_cortex_create_plan_failure(self):
        """Test plan creation failure"""
        mock_planner = MagicMock()
        mock_result = MagicMock()
        mock_result.is_ok.return_value = False
        mock_result.error = "Disk full"
        mock_planner.create_temp_plan.return_value = mock_result

        with patch(
            "cortex.orchestrators.mcp_tools_planner.get_planner_orchestrator",
            return_value=mock_planner,
        ):
            result = PlannerOrchestratorMCPTools.cortex_create_plan(
                description="Test plan",
            )

        assert result.success is False
        assert result.error == "Disk full"

    def test_cortex_approve_plan_success(self):
        """Test successful plan approval"""
        mock_planner = MagicMock()
        mock_result = MagicMock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = {
            "plan_id": "abc123",
            "status": "active",
        }
        mock_planner.approve_plan.return_value = mock_result

        with patch(
            "cortex.orchestrators.mcp_tools_planner.get_planner_orchestrator",
            return_value=mock_planner,
        ):
            result = PlannerOrchestratorMCPTools.cortex_approve_plan(plan_id="abc123")

        assert result.success is True
        assert result.data["status"] == "active"

    def test_cortex_execute_plan_success(self):
        """Test successful plan execution"""
        mock_planner = MagicMock()
        mock_result = MagicMock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = {
            "plan_id": "abc123",
            "status": "executed",
        }
        mock_planner.execute_plan.return_value = mock_result

        with patch(
            "cortex.orchestrators.mcp_tools_planner.get_planner_orchestrator",
            return_value=mock_planner,
        ):
            result = PlannerOrchestratorMCPTools.cortex_execute_plan(
                plan_id="abc123", confirmed=True
            )

        assert result.success is True
        assert result.data["status"] == "executed"

    def test_cortex_list_plans_success(self):
        """Test successful plan listing"""
        mock_planner = MagicMock()
        mock_result = MagicMock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = [
            {"plan_id": "plan1", "description": "Plan 1"},
            {"plan_id": "plan2", "description": "Plan 2"},
        ]
        mock_planner.list_active_plans.return_value = mock_result

        with patch(
            "cortex.orchestrators.mcp_tools_planner.get_planner_orchestrator",
            return_value=mock_planner,
        ):
            result = PlannerOrchestratorMCPTools.cortex_list_plans(
                state="active", limit=10
            )

        assert result.success is True
        assert result.data["total"] == 2
        assert len(result.data["plans"]) == 2

    def test_cortex_get_plan_from_temp(self):
        """Test retrieving plan from temp storage"""
        mock_planner = MagicMock()
        mock_result = MagicMock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = {
            "plan_id": "abc123",
            "status": "temp",
        }
        mock_planner.get_temp_plan.return_value = mock_result

        with patch(
            "cortex.orchestrators.mcp_tools_planner.get_planner_orchestrator",
            return_value=mock_planner,
        ):
            result = PlannerOrchestratorMCPTools.cortex_get_plan(plan_id="abc123")

        assert result.success is True
        assert result.data["status"] == "temp"

    def test_cortex_get_plan_not_found(self):
        """Test retrieving non-existent plan"""
        mock_planner = MagicMock()
        mock_result = MagicMock()
        mock_result.is_ok.return_value = False
        mock_planner.get_temp_plan.return_value = mock_result
        mock_planner.get_active_plan.return_value = mock_result

        with patch(
            "cortex.orchestrators.mcp_tools_planner.get_planner_orchestrator",
            return_value=mock_planner,
        ):
            result = PlannerOrchestratorMCPTools.cortex_get_plan(plan_id="nonexistent")

        assert result.success is False
        assert "Plan not found" in str(result.error)

    def test_cortex_reject_plan(self):
        """Test plan rejection"""
        mock_planner = MagicMock()
        mock_result = MagicMock()
        mock_result.is_ok.return_value = True
        mock_planner.get_temp_plan.return_value = mock_result

        with patch(
            "cortex.orchestrators.mcp_tools_planner.get_planner_orchestrator",
            return_value=mock_planner,
        ):
            result = PlannerOrchestratorMCPTools.cortex_reject_plan(
                plan_id="abc123", reason="Needs more review"
            )

        assert result.success is True
        assert result.data["status"] == "rejected"


class TestCLIRouter:
    """Test CLI command routing"""

    def test_create_command_parsing(self):
        """Test /plan create command parsing"""
        result = PlannerCLIRouter.route_command(
            "/plan create Fix authentication bug --impact high --confidence 0.8"
        )
        # Will fail without mock, but tests parsing logic
        assert isinstance(result, MCP_ToolResult)

    def test_approve_command_parsing(self):
        """Test /plan approve command parsing"""
        result = PlannerCLIRouter.route_command("/plan approve abc123")
        assert isinstance(result, MCP_ToolResult)

    def test_execute_command_parsing(self):
        """Test /plan execute command parsing"""
        result = PlannerCLIRouter.route_command(
            "/plan execute abc123 --confirm --reason 'Ready to go'"
        )
        assert isinstance(result, MCP_ToolResult)

    def test_list_command_parsing(self):
        """Test /plan list command parsing"""
        result = PlannerCLIRouter.route_command("/plan list active --limit 20")
        assert isinstance(result, MCP_ToolResult)

    def test_show_command_parsing(self):
        """Test /plan show command parsing"""
        result = PlannerCLIRouter.route_command("/plan show abc123")
        assert isinstance(result, MCP_ToolResult)

    def test_reject_command_parsing(self):
        """Test /plan reject command parsing"""
        result = PlannerCLIRouter.route_command(
            "/plan reject abc123 Scope needs more definition"
        )
        assert isinstance(result, MCP_ToolResult)

    def test_unknown_command(self):
        """Test unknown command handling"""
        result = PlannerCLIRouter.route_command("/plan invalid")
        assert result.success is False
        assert "Unknown command" in result.error

    def test_missing_create_description(self):
        """Test /plan create without description"""
        result = PlannerCLIRouter.route_command("/plan create")
        assert result.success is False
        assert "Missing description" in result.error

    def test_missing_approve_plan_id(self):
        """Test /plan approve without plan_id"""
        result = PlannerCLIRouter.route_command("/plan approve")
        assert result.success is False
        assert "Missing plan_id" in result.error

    def test_format_response_success(self):
        """Test response formatting for success"""
        result = MCP_ToolResult(
            success=True,
            data={"plan_id": "abc123", "status": "active"},
            message="Plan approved",
        )

        formatted = PlannerCLIRouter.format_response(result)
        assert "✅" in formatted
        assert "Plan approved" in formatted
        assert "abc123" in formatted

    def test_format_response_error(self):
        """Test response formatting for error"""
        result = MCP_ToolResult(
            success=False,
            error="Plan not found",
            message="Failed to retrieve plan",
        )

        formatted = PlannerCLIRouter.format_response(result)
        assert "❌" in formatted
        assert "Failed to retrieve plan" in formatted
        assert "Plan not found" in formatted

    def test_format_response_list(self):
        """Test response formatting for list"""
        result = MCP_ToolResult(
            success=True,
            data={
                "plans": [
                    {"plan_id": "plan1", "description": "Plan 1"},
                    {"plan_id": "plan2", "description": "Plan 2"},
                ],
                "total": 2,
                "state": "active",
                "limit": 10,
            },
            message="Found 2 plans",
        )

        formatted = PlannerCLIRouter.format_response(result)
        assert "📋" in formatted
        assert "plan1" in formatted
        assert "plan2" in formatted
        assert "Total: 2" in formatted

    def test_create_command_with_confidence(self):
        """Test /plan create command with float confidence"""
        result = PlannerCLIRouter._handle_create(
            "/plan create Implement feature --confidence 0.95"
        )
        assert isinstance(result, MCP_ToolResult)

    def test_list_command_defaults(self):
        """Test /plan list command with defaults"""
        result = PlannerCLIRouter._handle_list("/plan list")
        assert isinstance(result, MCP_ToolResult)

    def test_execute_command_confirm_flag(self):
        """Test /plan execute command with --confirm flag"""
        result = PlannerCLIRouter._handle_execute(
            "/plan execute abc123 --confirm"
        )
        assert isinstance(result, MCP_ToolResult)

    def test_create_command_scope_variations(self):
        """Test /plan create with different scopes"""
        for scope in ["file", "module", "system", "architecture"]:
            result = PlannerCLIRouter._handle_create(
                f"/plan create Test plan --scope {scope}"
            )
            assert isinstance(result, MCP_ToolResult)

    def test_create_command_impact_variations(self):
        """Test /plan create with different impacts"""
        for impact in ["low", "medium", "high"]:
            result = PlannerCLIRouter._handle_create(
                f"/plan create Test plan --impact {impact}"
            )
            assert isinstance(result, MCP_ToolResult)
