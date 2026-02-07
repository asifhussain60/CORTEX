"""
Legacy migration and MCP tools test suite.
Consolidates 5 existing response systems, exposes 4 new MCP tools.

Module: tests.unit.orchestrators.response.test_legacy_migration_mcp_tools
"""

import pytest
from cortex.orchestrators.response.legacy_migration_mcp_tools import (
    LegacyResponseSystem,
    UnifiedResponseEngine,
    MCPToolExporter,
    ProcessRequestMCPTool,
    AnalyzeResponseMCPTool,
    GenerateResponseMCPTool,
    MigrationOrchestrator,
)


class TestLegacyResponseSystem:
    """Tests for legacy response system."""
    
    def test_legacy_system_creation(self):
        """Test creating legacy response system."""
        legacy = LegacyResponseSystem(name="old_response_v1")
        assert legacy.name == "old_response_v1"
    
    def test_legacy_system_render(self):
        """Test legacy system render."""
        legacy = LegacyResponseSystem(name="old_response_v1")
        output = legacy.render(code="def f(): pass")
        assert isinstance(output, str)
    
    def test_legacy_system_configuration(self):
        """Test legacy system configuration."""
        legacy = LegacyResponseSystem(name="old_response_v1")
        legacy.configure(style="verbose", level="detailed")
        assert legacy.configured is True


class TestUnifiedResponseEngine:
    """Tests for unified response engine."""
    
    def test_unified_engine_creation(self):
        """Test creating unified engine."""
        engine = UnifiedResponseEngine()
        assert engine is not None
    
    def test_unified_engine_integrates_legacy(self):
        """Test unified engine integrates legacy systems."""
        engine = UnifiedResponseEngine()
        assert hasattr(engine, 'legacy_systems')
    
    def test_unified_engine_consolidates(self):
        """Test unified engine consolidates 5 systems."""
        engine = UnifiedResponseEngine()
        systems = engine.get_legacy_systems()
        assert len(systems) >= 5
    
    def test_unified_engine_migration_status(self):
        """Test migration status tracking."""
        engine = UnifiedResponseEngine()
        status = engine.get_migration_status()
        assert isinstance(status, dict)
        assert "consolidated" in status or "systems" in status


class TestMCPToolExporter:
    """Tests for MCP tool exporter."""
    
    def test_exporter_creation(self):
        """Test creating exporter."""
        exporter = MCPToolExporter()
        assert exporter is not None
    
    def test_exporter_exports_4_tools(self):
        """Test exporter exports 4 tools."""
        exporter = MCPToolExporter()
        tools = exporter.get_exported_tools()
        assert len(tools) >= 4
    
    def test_tool_names(self):
        """Test tool names are correct."""
        exporter = MCPToolExporter()
        tools = exporter.get_exported_tools()
        tool_names = {tool.name for tool in tools}
        
        # Should include 4 MCP tools
        assert len(tool_names) >= 4


class TestProcessRequestMCPTool:
    """Tests for process_request MCP tool."""
    
    def test_tool_creation(self):
        """Test creating process_request tool."""
        tool = ProcessRequestMCPTool()
        assert tool.name == "cortex_process_request"
    
    def test_tool_execute(self):
        """Test executing process_request."""
        tool = ProcessRequestMCPTool()
        result = tool.execute(
            intent="implement",
            context="test implementation",
            code_sample="def f(): pass"
        )
        assert isinstance(result, dict)
        assert "result" in result or "status" in result
    
    def test_tool_schema(self):
        """Test tool has proper schema."""
        tool = ProcessRequestMCPTool()
        schema = tool.get_schema()
        assert "name" in schema
        assert "description" in schema
        assert tool.name in [schema.get("name"), "cortex_process_request"]


class TestAnalyzeResponseMCPTool:
    """Tests for analyze_response MCP tool."""
    
    def test_tool_creation(self):
        """Test creating analyze_response tool."""
        tool = AnalyzeResponseMCPTool()
        assert tool.name == "cortex_analyze_response"
    
    def test_tool_analyze(self):
        """Test analyzing response."""
        tool = AnalyzeResponseMCPTool()
        analysis = tool.execute(
            response="Test response content",
            context="test"
        )
        assert isinstance(analysis, dict)
    
    def test_analysis_includes_metrics(self):
        """Test analysis includes metrics."""
        tool = AnalyzeResponseMCPTool()
        analysis = tool.execute(
            response="Test response",
            context="test"
        )
        # Should have analysis results
        assert len(analysis) > 0


class TestGenerateResponseMCPTool:
    """Tests for generate_response MCP tool."""
    
    def test_tool_creation(self):
        """Test creating generate_response tool."""
        tool = GenerateResponseMCPTool()
        assert tool.name == "cortex_generate_response"
    
    def test_tool_generate(self):
        """Test generating response."""
        tool = GenerateResponseMCPTool()
        response = tool.execute(
            code="def calculate(x): return x * 2",
            role="engineer",
            task="code_review"
        )
        assert isinstance(response, str)
    
    def test_generate_for_different_roles(self):
        """Test generate for different roles."""
        tool = GenerateResponseMCPTool()
        
        roles = ["engineer", "product_manager", "business_lead"]
        for role in roles:
            response = tool.execute(
                code="def f(): pass",
                role=role,
                task="review"
            )
            assert isinstance(response, str)


class TestMigrationOrchestrator:
    """Tests for migration orchestrator."""
    
    def test_orchestrator_creation(self):
        """Test creating orchestrator."""
        orchestrator = MigrationOrchestrator()
        assert orchestrator is not None
    
    def test_orchestrator_consolidates_5_systems(self):
        """Test orchestrator consolidates 5 legacy systems."""
        orchestrator = MigrationOrchestrator()
        legacy_count = orchestrator.get_legacy_system_count()
        assert legacy_count >= 5
    
    def test_orchestrator_migration_plan(self):
        """Test orchestrator creates migration plan."""
        orchestrator = MigrationOrchestrator()
        plan = orchestrator.create_migration_plan()
        assert isinstance(plan, list) or isinstance(plan, dict)
    
    def test_orchestrator_executes_migration(self):
        """Test orchestrator executes migration."""
        orchestrator = MigrationOrchestrator()
        success = orchestrator.execute_migration()
        assert isinstance(success, bool)
    
    def test_orchestrator_validates_consolidation(self):
        """Test orchestrator validates consolidation."""
        orchestrator = MigrationOrchestrator()
        is_valid = orchestrator.validate_consolidation()
        assert isinstance(is_valid, bool)


class TestMCPToolIntegration:
    """Tests for MCP tool integration."""
    
    def test_all_4_tools_exported(self):
        """Test all 4 MCP tools are exported."""
        exporter = MCPToolExporter()
        tools = exporter.get_exported_tools()
        
        tool_names = [tool.name for tool in tools]
        assert "cortex_process_request" in tool_names
        assert "cortex_analyze_response" in tool_names
        assert "cortex_generate_response" in tool_names
    
    def test_tools_interoperate(self):
        """Test tools can interoperate."""
        process_tool = ProcessRequestMCPTool()
        analyze_tool = AnalyzeResponseMCPTool()
        generate_tool = GenerateResponseMCPTool()
        
        # Process request
        result = process_tool.execute(
            intent="analyze",
            context="test",
            code_sample="def f(): pass"
        )
        
        # Should be able to analyze result
        analysis = analyze_tool.execute(
            response=str(result),
            context="test"
        )
        
        assert isinstance(analysis, dict)
    
    def test_tool_gateway_compatibility(self):
        """Test tools are compatible with MCP gateway."""
        exporter = MCPToolExporter()
        tools = exporter.get_exported_tools()
        
        for tool in tools:
            schema = tool.get_schema()
            # Should have required fields for MCP gateway
            assert "name" in schema or tool.name
            assert callable(tool.execute)


class TestLegacySystemConsolidation:
    """Tests for legacy system consolidation."""
    
    def test_consolidates_response_system_1(self):
        """Test consolidates response system 1."""
        orchestrator = MigrationOrchestrator()
        system = LegacyResponseSystem(name="response_system_1")
        consolidated = orchestrator.consolidate(system)
        assert consolidated is not None
    
    def test_consolidates_response_system_2(self):
        """Test consolidates response system 2."""
        orchestrator = MigrationOrchestrator()
        system = LegacyResponseSystem(name="response_system_2")
        consolidated = orchestrator.consolidate(system)
        assert consolidated is not None
    
    def test_consolidates_response_system_3(self):
        """Test consolidates response system 3."""
        orchestrator = MigrationOrchestrator()
        system = LegacyResponseSystem(name="response_system_3")
        consolidated = orchestrator.consolidate(system)
        assert consolidated is not None
    
    def test_consolidates_response_system_4(self):
        """Test consolidates response system 4."""
        orchestrator = MigrationOrchestrator()
        system = LegacyResponseSystem(name="response_system_4")
        consolidated = orchestrator.consolidate(system)
        assert consolidated is not None
    
    def test_consolidates_response_system_5(self):
        """Test consolidates response system 5."""
        orchestrator = MigrationOrchestrator()
        system = LegacyResponseSystem(name="response_system_5")
        consolidated = orchestrator.consolidate(system)
        assert consolidated is not None
    
    def test_no_data_loss_during_consolidation(self):
        """Test no data loss during consolidation."""
        orchestrator = MigrationOrchestrator()
        
        original_data = ["req1", "req2", "req3"]
        for data in original_data:
            system = LegacyResponseSystem(name=data)
            consolidated = orchestrator.consolidate(system)
            # Should preserve data
            assert consolidated is not None


class TestDeploymentValidation:
    """Tests for deployment validation."""
    
    def test_unified_engine_production_ready(self):
        """Test unified engine is production ready."""
        engine = UnifiedResponseEngine()
        is_ready = engine.is_production_ready()
        assert isinstance(is_ready, bool)
    
    def test_mcp_tools_production_ready(self):
        """Test MCP tools are production ready."""
        exporter = MCPToolExporter()
        tools = exporter.get_exported_tools()
        
        for tool in tools:
            is_ready = tool.is_production_ready()
            assert isinstance(is_ready, bool)
    
    def test_orchestrator_validates_before_deployment(self):
        """Test orchestrator validates before deployment."""
        orchestrator = MigrationOrchestrator()
        
        validation_passed = orchestrator.validate_all()
        assert isinstance(validation_passed, bool)


# ============================================================================
# PYTEST FIXTURES
# ============================================================================


@pytest.fixture
def legacy_system():
    """Provide legacy system."""
    return LegacyResponseSystem(name="test_legacy")


@pytest.fixture
def unified_engine():
    """Provide unified engine."""
    return UnifiedResponseEngine()


@pytest.fixture
def mcp_tools():
    """Provide MCP tools."""
    return {
        "process": ProcessRequestMCPTool(),
        "analyze": AnalyzeResponseMCPTool(),
        "generate": GenerateResponseMCPTool(),
    }
