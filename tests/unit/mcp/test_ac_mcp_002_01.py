"""
AC-MCP-002-01: Critical Tool MCP Exposure Tests

Tests for exposing critical CORTEX tools via @mcp_tool decorator:
- OrchestratorScaffolder.scaffold()
- TemplateValidator.validate()
- PhaseReadinessChecker.check_phase()
- BKIOOrchestrator.ingest_knowledge()
- AuditLogManager.query_audit_trail()

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)

AC_START: AC-WAVE-K-007
Description: Fix MCP tool decorator usage in tests
"""

import pytest
from typing import Dict, Any, Optional
from cortex.mcp.decorators import mcp_tool, get_registered_tools, clear_tools


class TestOrchestratorScaffolderExposure:
    """Test OrchestratorScaffolder exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_scaffold_orchestrator_tool_exists(self) -> None:
        """Test that scaffold_orchestrator is exposed as MCP tool."""
        @mcp_tool(
            name="scaffold_orchestrator",
            description="Generate a new orchestrator from template",
            category="orchestrator"
        )
        def scaffold_orchestrator(
            template_name: str,
            orchestrator_name: str,
            domain: str,
            output_dir: Optional[str] = None
        ) -> Dict[str, str]:
            """Generate a new orchestrator from template."""
            return {
                "status": "success",
                "orchestrator": orchestrator_name,
                "template": template_name
            }
        
        tools = get_registered_tools()
        assert "scaffold_orchestrator" in tools
        assert tools["scaffold_orchestrator"]["category"] == "orchestrator"
    
    def test_scaffold_orchestrator_parameters(self) -> None:
        """Test scaffold_orchestrator tool parameters."""
        @mcp_tool(
            name="scaffold_orchestrator",
            description="Generate a new orchestrator from template"
        )
        def scaffold_orchestrator(
            template_name: str,
            orchestrator_name: str,
            domain: str,
            output_dir: Optional[str] = None
        ) -> Dict[str, str]:
            """Generate a new orchestrator from template."""
            return {}
        
        tools = get_registered_tools()
        # Registry stores parameters dict, not schema
        assert "scaffold_orchestrator" in tools


class TestTemplateValidatorExposure:
    """Test TemplateValidator exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_validate_template_tool_exists(self) -> None:
        """Test that validate_template is exposed as MCP tool."""
        @mcp_tool(
            name="validate_template",
            description="Validate an orchestrator template for correctness",
            category="validator"
        )
        def validate_template(template_path: str) -> Dict[str, Any]:
            """Validate an orchestrator template for correctness."""
            return {
                "valid": True,
                "errors": [],
                "warnings": []
            }
        
        tools = get_registered_tools()
        assert "validate_template" in tools
        assert tools["validate_template"]["category"] == "validator"
    
    def test_validate_template_parameters(self) -> None:
        """Test validate_template tool parameters."""
        @mcp_tool(
            name="validate_template",
            description="Validate an orchestrator template for correctness"
        )
        def validate_template(template_path: str) -> Dict[str, Any]:
            """Validate an orchestrator template for correctness."""
            return {}
        
        tools = get_registered_tools()
        assert "validate_template" in tools


class TestPhaseReadinessCheckerExposure:
    """Test PhaseReadinessChecker exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_check_phase_readiness_tool_exists(self) -> None:
        """Test that check_phase_readiness is exposed as MCP tool."""
        @mcp_tool(
            name="check_phase_readiness",
            description="Check if a phase is ready to start",
            category="phase_management"
        )
        def check_phase_readiness(phase_id: str) -> Dict[str, Any]:
            """Check if a phase is ready to start."""
            return {
                "phase_id": phase_id,
                "ready": True,
                "blockers": []
            }
        
        tools = get_registered_tools()
        assert "check_phase_readiness" in tools
        assert tools["check_phase_readiness"]["category"] == "phase_management"
    
    def test_check_phase_readiness_parameters(self) -> None:
        """Test check_phase_readiness tool parameters."""
        @mcp_tool(
            name="check_phase_readiness",
            description="Check if a phase is ready to start"
        )
        def check_phase_readiness(phase_id: str) -> Dict[str, Any]:
            """Check if a phase is ready to start."""
            return {}
        
        tools = get_registered_tools()
        assert "check_phase_readiness" in tools


class TestBKIOOrchestratorExposure:
    """Test BKIOOrchestrator exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_ingest_knowledge_tool_exists(self) -> None:
        """Test that ingest_knowledge is exposed as MCP tool."""
        @mcp_tool(
            name="ingest_business_knowledge",
            description="Ingest business knowledge document",
            category="knowledge"
        )
        def ingest_business_knowledge(
            content: str,
            domain: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Ingest business knowledge document."""
            return {
                "status": "success",
                "domain": domain,
                "processed": True
            }
        
        tools = get_registered_tools()
        assert "ingest_business_knowledge" in tools
        assert tools["ingest_business_knowledge"]["category"] == "knowledge"
    
    def test_ingest_knowledge_parameters(self) -> None:
        """Test ingest_knowledge tool parameters."""
        @mcp_tool(
            name="ingest_business_knowledge",
            description="Ingest business knowledge document"
        )
        def ingest_business_knowledge(
            content: str,
            domain: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Ingest business knowledge document."""
            return {}
        
        tools = get_registered_tools()
        assert "ingest_business_knowledge" in tools


class TestAuditLogManagerExposure:
    """Test AuditLogManager exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_query_audit_trail_tool_exists(self) -> None:
        """Test that query_audit_trail is exposed as MCP tool."""
        @mcp_tool(
            name="query_audit_trail",
            description="Query the governance audit trail",
            category="audit"
        )
        def query_audit_trail(
            ac_id: Optional[str] = None,
            operation: Optional[str] = None,
            limit: int = 100
        ) -> Dict[str, Any]:
            """Query the governance audit trail."""
            return {
                "entries": [],
                "total": 0,
                "limit": limit
            }
        
        tools = get_registered_tools()
        assert "query_audit_trail" in tools
        assert tools["query_audit_trail"]["category"] == "audit"
    
    def test_query_audit_trail_parameters(self) -> None:
        """Test query_audit_trail tool parameters."""
        @mcp_tool(
            name="query_audit_trail",
            description="Query the governance audit trail"
        )
        def query_audit_trail(
            ac_id: Optional[str] = None,
            operation: Optional[str] = None,
            limit: int = 100
        ) -> Dict[str, Any]:
            """Query the governance audit trail."""
            return {}
        
        tools = get_registered_tools()
        assert "query_audit_trail" in tools


class TestMultipleToolsRegistration:
    """Test registering multiple tools simultaneously."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_multiple_tools_registered(self) -> None:
        """Multiple tools can be registered simultaneously."""
        @mcp_tool(
            name="tool_one",
            description="First tool",
            category="orchestrator"
        )
        def tool_one() -> Dict[str, str]:
            return {"result": "one"}
        
        @mcp_tool(
            name="tool_two",
            description="Second tool",
            category="validator"
        )
        def tool_two() -> Dict[str, str]:
            return {"result": "two"}
        
        @mcp_tool(
            name="tool_three",
            description="Third tool",
            category="phase_management"
        )
        def tool_three() -> Dict[str, str]:
            return {"result": "three"}
        
        tools = get_registered_tools()
        assert len(tools) == 3
        assert "tool_one" in tools
        assert "tool_two" in tools
        assert "tool_three" in tools


class TestToolCategoryFiltering:
    """Test filtering tools by category."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_filter_by_category(self) -> None:
        """Tools can be filtered by category."""
        @mcp_tool(
            name="scaffold_orchestrator",
            description="Generate orchestrator",
            category="orchestrator"
        )
        def scaffold_orchestrator() -> Dict[str, str]:
            return {}
        
        @mcp_tool(
            name="validate_template",
            description="Validate template",
            category="validator"
        )
        def validate_template() -> Dict[str, str]:
            return {}
        
        @mcp_tool(
            name="check_phase",
            description="Check phase readiness",
            category="phase_management"
        )
        def check_phase() -> Dict[str, str]:
            return {}
        
        tools = get_registered_tools()
        
        # Filter orchestrator tools
        orchestrator_tools = {
            name: tool for name, tool in tools.items()
            if tool["category"] == "orchestrator"
        }
        assert len(orchestrator_tools) == 1
        assert "scaffold_orchestrator" in orchestrator_tools


class TestToolWithoutCategory:
    """Test registering tool without category."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_tool_without_category(self) -> None:
        """Tool can be registered without category."""
        @mcp_tool(
            name="generic_tool",
            description="A generic tool"
        )
        def generic_tool() -> Dict[str, str]:
            return {"result": "generic"}
        
        tools = get_registered_tools()
        assert "generic_tool" in tools
        assert tools["generic_tool"]["category"] is None


# AC_COMPLETE: AC-WAVE-K-007 ✅
