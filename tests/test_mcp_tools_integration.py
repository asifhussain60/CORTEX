"""Tests for Phase 48 S6: MCP Tools Integration.

Integration and deployment of holistic validation as MCP tools.
"""

import pytest
from cortex.orchestrators.holistic.mcp_tools_integration import (
    MCPToolIntegrationOrchestrator,
    MCPToolDefinition,
    ToolCategory,
)


class TestToolCategory:
    """Tests for ToolCategory enum."""

    def test_all_categories(self):
        """Test all tool categories exist."""
        categories = [
            ToolCategory.VALIDATION,
            ToolCategory.ANALYSIS,
            ToolCategory.GOVERNANCE,
        ]
        assert len(categories) == 3

    def test_category_values(self):
        """Test category string values."""
        assert ToolCategory.VALIDATION.value == "validation"
        assert ToolCategory.ANALYSIS.value == "analysis"
        assert ToolCategory.GOVERNANCE.value == "governance"


class TestMCPToolDefinition:
    """Tests for MCPToolDefinition dataclass."""

    def test_create_tool_definition(self):
        """Test creating MCP tool definition."""
        tool = MCPToolDefinition(
            name="test_tool",
            description="Test tool description",
            category=ToolCategory.VALIDATION,
            inputs={"param1": "str"},
            outputs={"result": "dict"},
            entry_point="module.path:Class.method",
            requires_approval=False,
            blocking=True,
        )

        assert tool.name == "test_tool"
        assert tool.category == ToolCategory.VALIDATION
        assert tool.blocking is True

    def test_tool_definition_completeness(self):
        """Test tool definition has all required fields."""
        tool = MCPToolDefinition(
            name="tool",
            description="desc",
            category=ToolCategory.ANALYSIS,
            inputs={},
            outputs={},
            entry_point="entry",
            requires_approval=True,
            blocking=False,
        )

        assert tool.name is not None
        assert tool.description is not None
        assert tool.category is not None
        assert tool.entry_point is not None
        assert isinstance(tool.requires_approval, bool)
        assert isinstance(tool.blocking, bool)

    def test_tool_inputs_and_outputs(self):
        """Test tool inputs and outputs specification."""
        tool = MCPToolDefinition(
            name="tool",
            description="desc",
            category=ToolCategory.VALIDATION,
            inputs={
                "operation": "str",
                "target": "str",
                "registry_path": "str",
            },
            outputs={
                "verdict": "str",
                "risk_score": "float",
                "evidence": "List[Dict]",
            },
            entry_point="entry",
            requires_approval=False,
            blocking=True,
        )

        assert len(tool.inputs) == 3
        assert len(tool.outputs) == 3
        assert "operation" in tool.inputs
        assert "verdict" in tool.outputs


class TestMCPToolIntegrationOrchestrator:
    """Tests for MCPToolIntegrationOrchestrator."""

    def test_initialize(self):
        """Test initializing orchestrator."""
        orchestrator = MCPToolIntegrationOrchestrator()
        assert orchestrator is not None
        assert len(orchestrator.tools) == 0

    def test_define_mcp_tools(self):
        """Test defining MCP tools."""
        orchestrator = MCPToolIntegrationOrchestrator()
        tools = orchestrator.define_mcp_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert all(isinstance(t, MCPToolDefinition) for t in tools)

    def test_all_phase_48_tools_defined(self):
        """Test all Phase 48 orchestrators have tools."""
        orchestrator = MCPToolIntegrationOrchestrator()
        tools = orchestrator.define_mcp_tools()

        tool_names = [t.name for t in tools]

        # Should have tool for each stage
        assert any("validate_holistically" in n for n in tool_names)  # S1
        assert any("dependency_graph" in n for n in tool_names)  # S2
        assert any("challenge" in n for n in tool_names)  # S3
        assert any("analyze_self" in n for n in tool_names)  # S4
        assert any("enhance_prompts" in n for n in tool_names)  # S5

    def test_tool_definitions_have_entry_points(self):
        """Test all tools have valid entry points."""
        orchestrator = MCPToolIntegrationOrchestrator()
        tools = orchestrator.define_mcp_tools()

        for tool in tools:
            assert ":" in tool.entry_point
            assert "cortex.orchestrators" in tool.entry_point

    def test_validation_tools_blocking(self):
        """Test validation tools have blocking enabled."""
        orchestrator = MCPToolIntegrationOrchestrator()
        tools = orchestrator.define_mcp_tools()

        validation_tools = [t for t in tools if "validate" in t.name]
        assert len(validation_tools) > 0

        for tool in validation_tools:
            assert tool.blocking is True

    def test_challenge_tool_requires_approval(self):
        """Test challenge tool requires user approval."""
        orchestrator = MCPToolIntegrationOrchestrator()
        tools = orchestrator.define_mcp_tools()

        challenge_tool = [t for t in tools if "challenge" in t.name][0]
        assert challenge_tool.requires_approval is True

    def test_wire_tools_to_mcp_gateway(self):
        """Test generating MCP gateway wiring configuration."""
        orchestrator = MCPToolIntegrationOrchestrator()
        wiring = orchestrator.wire_tools_to_mcp_gateway()

        assert isinstance(wiring, dict)
        assert "version" in wiring
        assert "gateway" in wiring
        assert "tools" in wiring

    def test_mcp_gateway_wiring_structure(self):
        """Test MCP gateway wiring has correct structure."""
        orchestrator = MCPToolIntegrationOrchestrator()
        wiring = orchestrator.wire_tools_to_mcp_gateway()

        # Should have all required sections
        assert wiring["version"] == "1.0"
        assert wiring["namespace"] == "cortex.orchestrators.holistic"
        assert len(wiring["tools"]) >= 5
        assert "execution_order" in wiring
        assert "blocking_gates" in wiring
        assert "approval_gates" in wiring

    def test_execution_order_defined(self):
        """Test execution order is defined for tools."""
        orchestrator = MCPToolIntegrationOrchestrator()
        wiring = orchestrator.wire_tools_to_mcp_gateway()

        execution_order = wiring["execution_order"]
        assert len(execution_order) >= 4

        # Validate order makes sense
        validate_idx = next(
            (i for i, t in enumerate(execution_order) if "validate" in t),
            None,
        )
        challenge_idx = next(
            (i for i, t in enumerate(execution_order) if "challenge" in t),
            None,
        )
        assert validate_idx is not None
        assert challenge_idx is not None
        assert validate_idx < challenge_idx  # Validate before challenge

    def test_integrate_with_master_orchestrator(self):
        """Test generating MasterOrchestrator integration config."""
        orchestrator = MCPToolIntegrationOrchestrator()
        integration = orchestrator.integrate_with_master_orchestrator()

        assert isinstance(integration, dict)
        assert integration["orchestrator"] == "MasterOrchestrator"
        assert "new_components" in integration
        assert "workflow_integration" in integration

    def test_new_components_defined(self):
        """Test all new components are defined in integration."""
        orchestrator = MCPToolIntegrationOrchestrator()
        integration = orchestrator.integrate_with_master_orchestrator()

        components = integration["new_components"]
        component_names = [c["name"] for c in components]

        # Should have components for all stages
        assert any("Holistic" in n for n in component_names)  # S1
        assert any("Dependency" in n for n in component_names)  # S2
        assert any("Challenge" in n for n in component_names)  # S3
        assert any("CortexBrain" in n for n in component_names)  # S4
        assert any("Prompt" in n for n in component_names)  # S5

    def test_component_tier_classification(self):
        """Test components are properly tiered."""
        orchestrator = MCPToolIntegrationOrchestrator()
        integration = orchestrator.integrate_with_master_orchestrator()

        components = integration["new_components"]

        # Count by tier
        tiers = [c["tier"] for c in components]
        assert "core" in tiers
        assert "domain" in tiers
        assert "support" in tiers

    def test_workflow_integration_defined(self):
        """Test workflow integration specifies when to run tools."""
        orchestrator = MCPToolIntegrationOrchestrator()
        integration = orchestrator.integrate_with_master_orchestrator()

        workflows = integration["workflow_integration"]

        # Should have triggers for different operations
        assert "before_IMPLEMENT" in workflows
        assert "before_FIX" in workflows
        assert "before_REFACTOR" in workflows
        assert "periodic_analysis" in workflows

        # Each should have tools
        for workflow, tools in workflows.items():
            assert len(tools) > 0

    def test_generate_integration_report(self):
        """Test generating integration report."""
        orchestrator = MCPToolIntegrationOrchestrator()
        report = orchestrator.generate_integration_report()

        assert report is not None
        assert report.phase == "Phase 48 S6"
        assert report.tools_defined >= 5
        assert report.tools_registered == report.tools_defined
        assert report.orchestrators_wired == 5

    def test_integration_report_impact(self):
        """Test integration report impact is high."""
        orchestrator = MCPToolIntegrationOrchestrator()
        report = orchestrator.generate_integration_report()

        assert report.total_impact == "high"

    def test_integration_report_recommendations(self):
        """Test integration report includes recommendations."""
        orchestrator = MCPToolIntegrationOrchestrator()
        report = orchestrator.generate_integration_report()

        assert len(report.recommendations) > 0
        assert any("regression" in rec.lower() for rec in report.recommendations)
        assert any("gateway" in rec.lower() for rec in report.recommendations)

    def test_generate_deployment_checklist(self):
        """Test generating deployment checklist."""
        orchestrator = MCPToolIntegrationOrchestrator()
        checklist = orchestrator.generate_deployment_checklist()

        assert isinstance(checklist, list)
        assert len(checklist) > 10

    def test_checklist_covers_all_stages(self):
        """Test checklist covers all implementation stages."""
        orchestrator = MCPToolIntegrationOrchestrator()
        checklist = orchestrator.generate_deployment_checklist()

        checklist_str = str(checklist).lower()

        # Should mention each stage
        assert "s1" in checklist_str or "validation" in checklist_str
        assert "s2" in checklist_str or "dependency" in checklist_str
        assert "s3" in checklist_str or "challenge" in checklist_str
        assert "s4" in checklist_str or "cortex" in checklist_str
        assert "s5" in checklist_str or "prompt" in checklist_str

    def test_checklist_has_verification_steps(self):
        """Test checklist includes verification steps."""
        orchestrator = MCPToolIntegrationOrchestrator()
        checklist = orchestrator.generate_deployment_checklist()

        checklist_str = str(checklist).lower()

        assert "regression" in checklist_str
        assert "test" in checklist_str
        assert "deploy" in checklist_str or "register" in checklist_str

    def test_orchestrator_api_completeness(self):
        """Test orchestrator has all required methods."""
        orchestrator = MCPToolIntegrationOrchestrator()

        assert hasattr(orchestrator, "define_mcp_tools")
        assert callable(orchestrator.define_mcp_tools)
        assert hasattr(orchestrator, "wire_tools_to_mcp_gateway")
        assert callable(orchestrator.wire_tools_to_mcp_gateway)
        assert hasattr(orchestrator, "integrate_with_master_orchestrator")
        assert callable(orchestrator.integrate_with_master_orchestrator)
        assert hasattr(orchestrator, "generate_integration_report")
        assert callable(orchestrator.generate_integration_report)
        assert hasattr(orchestrator, "generate_deployment_checklist")
        assert callable(orchestrator.generate_deployment_checklist)

    def test_tool_definitions_complete(self):
        """Test each tool definition is complete and valid."""
        orchestrator = MCPToolIntegrationOrchestrator()
        tools = orchestrator.define_mcp_tools()

        for tool in tools:
            # Should have inputs and outputs
            assert isinstance(tool.inputs, dict)
            assert isinstance(tool.outputs, dict)

            # Should have valid category
            assert tool.category in [
                ToolCategory.VALIDATION,
                ToolCategory.ANALYSIS,
                ToolCategory.GOVERNANCE,
            ]

            # Should have valid entry point
            assert ":" in tool.entry_point
            assert "." in tool.entry_point
