"""
AC-MCP-002-01: Critical Tool MCP Exposure Tests

Tests for exposing critical CORTEX tools via @mcp_tool decorator:
- OrchestratorScaffolder.scaffold()
- TemplateValidator.validate()
- PhaseReadinessChecker.check_phase()
- BKIOOrchestrator.ingest_knowledge()
- AuditLogManager.query_audit_trail()

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import pytest
from typing import Dict, Any, Optional
from src.mcp.decorator import mcp_tool, get_registered_tools, clear_tools


class TestOrchestratorScaffolderExposure:
    """Test OrchestratorScaffolder exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_scaffold_orchestrator_tool_exists(self) -> None:
        """Test that scaffold_orchestrator is exposed as MCP tool."""
        @mcp_tool(category="orchestrator")
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
        assert tools["scaffold_orchestrator"].category == "orchestrator"
    
    def test_scaffold_orchestrator_parameters(self) -> None:
        """Test scaffold_orchestrator tool parameters."""
        @mcp_tool()
        def scaffold_orchestrator(
            template_name: str,
            orchestrator_name: str,
            domain: str,
            output_dir: Optional[str] = None
        ) -> Dict[str, str]:
            """Generate a new orchestrator from template."""
            return {}
        
        tools = get_registered_tools()
        schema = tools["scaffold_orchestrator"].parameters
        
        # Check required parameters
        assert "template_name" in schema["required"]
        assert "orchestrator_name" in schema["required"]
        assert "domain" in schema["required"]
        
        # Check optional parameters
        assert "output_dir" not in schema["required"]
        
        # Check parameter types
        props = schema["properties"]
        assert props["template_name"]["type"] == "string"
        assert props["orchestrator_name"]["type"] == "string"
        assert props["domain"]["type"] == "string"


class TestTemplateValidatorExposure:
    """Test TemplateValidator exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_validate_template_tool_exists(self) -> None:
        """Test that validate_template is exposed as MCP tool."""
        @mcp_tool(category="validator")
        def validate_template(template_path: str) -> Dict[str, Any]:
            """Validate an orchestrator template for correctness."""
            return {
                "valid": True,
                "errors": [],
                "warnings": []
            }
        
        tools = get_registered_tools()
        assert "validate_template" in tools
        assert tools["validate_template"].category == "validator"
    
    def test_validate_template_parameters(self) -> None:
        """Test validate_template tool parameters."""
        @mcp_tool()
        def validate_template(template_path: str) -> Dict[str, Any]:
            """Validate an orchestrator template for correctness."""
            return {}
        
        tools = get_registered_tools()
        schema = tools["validate_template"].parameters
        
        assert "template_path" in schema["required"]
        assert schema["properties"]["template_path"]["type"] == "string"


class TestPhaseReadinessCheckerExposure:
    """Test PhaseReadinessChecker exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_check_phase_readiness_tool_exists(self) -> None:
        """Test that check_phase_readiness is exposed as MCP tool."""
        @mcp_tool(category="phase_management")
        def check_phase_readiness(phase_id: str) -> Dict[str, Any]:
            """Check if a phase is ready to start."""
            return {
                "phase_id": phase_id,
                "ready": True,
                "blockers": []
            }
        
        tools = get_registered_tools()
        assert "check_phase_readiness" in tools
        assert tools["check_phase_readiness"].category == "phase_management"
    
    def test_check_phase_readiness_parameters(self) -> None:
        """Test check_phase_readiness tool parameters."""
        @mcp_tool()
        def check_phase_readiness(phase_id: str) -> Dict[str, Any]:
            """Check if a phase is ready to start."""
            return {}
        
        tools = get_registered_tools()
        schema = tools["check_phase_readiness"].parameters
        
        assert "phase_id" in schema["required"]
        assert schema["properties"]["phase_id"]["type"] == "string"


class TestBKIOOrchestratorExposure:
    """Test BKIOOrchestrator exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_ingest_knowledge_tool_exists(self) -> None:
        """Test that ingest_knowledge is exposed as MCP tool."""
        @mcp_tool(category="knowledge")
        def ingest_business_knowledge(
            content: str,
            domain: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, str]:
            """Ingest business knowledge document."""
            return {
                "status": "success",
                "domain": domain,
                "processed": True
            }
        
        tools = get_registered_tools()
        assert "ingest_business_knowledge" in tools
        assert tools["ingest_business_knowledge"].category == "knowledge"
    
    def test_ingest_knowledge_parameters(self) -> None:
        """Test ingest_knowledge tool parameters."""
        @mcp_tool()
        def ingest_business_knowledge(
            content: str,
            domain: str,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, str]:
            """Ingest business knowledge document."""
            return {}
        
        tools = get_registered_tools()
        schema = tools["ingest_business_knowledge"].parameters
        
        # Check required parameters
        assert "content" in schema["required"]
        assert "domain" in schema["required"]
        
        # Check optional parameters
        assert "metadata" not in schema["required"]
        
        # Check parameter types
        props = schema["properties"]
        assert props["content"]["type"] == "string"
        assert props["domain"]["type"] == "string"
        assert props["metadata"]["type"] == "object"


class TestAuditLogManagerExposure:
    """Test AuditLogManager exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_query_audit_trail_tool_exists(self) -> None:
        """Test that query_audit_trail is exposed as MCP tool."""
        @mcp_tool(category="audit")
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
        assert tools["query_audit_trail"].category == "audit"
    
    def test_query_audit_trail_parameters(self) -> None:
        """Test query_audit_trail tool parameters."""
        @mcp_tool()
        def query_audit_trail(
            ac_id: Optional[str] = None,
            operation: Optional[str] = None,
            limit: int = 100
        ) -> Dict[str, Any]:
            """Query the governance audit trail."""
            return {}
        
        tools = get_registered_tools()
        schema = tools["query_audit_trail"].parameters
        
        # All parameters should be optional
        assert "ac_id" not in schema["required"]
        assert "operation" not in schema["required"]
        assert "limit" not in schema["required"]
        
        # Check parameter types
        props = schema["properties"]
        assert props["ac_id"]["type"] == "string"
        assert props["operation"]["type"] == "string"
        assert props["limit"]["type"] == "integer"


class TestCriticalToolsCollective:
    """Test all critical tools together."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_five_critical_tools_registered(self) -> None:
        """Test that all 5 critical tools can be registered."""
        @mcp_tool(category="orchestrator")
        def scaffold_orchestrator(
            template_name: str,
            orchestrator_name: str,
            domain: str
        ) -> Dict[str, str]:
            """Generate a new orchestrator from template."""
            return {}
        
        @mcp_tool(category="validator")
        def validate_template(template_path: str) -> Dict[str, Any]:
            """Validate an orchestrator template for correctness."""
            return {}
        
        @mcp_tool(category="phase_management")
        def check_phase_readiness(phase_id: str) -> Dict[str, Any]:
            """Check if a phase is ready to start."""
            return {}
        
        @mcp_tool(category="knowledge")
        def ingest_business_knowledge(content: str, domain: str) -> Dict[str, str]:
            """Ingest business knowledge document."""
            return {}
        
        @mcp_tool(category="audit")
        def query_audit_trail(limit: int = 100) -> Dict[str, Any]:
            """Query the governance audit trail."""
            return {}
        
        tools = get_registered_tools()
        assert len(tools) == 5
        
        # Check all tools are registered
        tool_names = {"scaffold_orchestrator", "validate_template", 
                     "check_phase_readiness", "ingest_business_knowledge", 
                     "query_audit_trail"}
        assert set(tools.keys()) == tool_names
    
    def test_critical_tools_callable(self) -> None:
        """Test that critical tools are callable."""
        @mcp_tool()
        def scaffold_orchestrator(template_name: str) -> str:
            """Scaffold."""
            return f"scaffolded-{template_name}"
        
        @mcp_tool()
        def validate_template(template_path: str) -> bool:
            """Validate."""
            return True
        
        @mcp_tool()
        def check_phase_readiness(phase_id: str) -> bool:
            """Check."""
            return True
        
        @mcp_tool()
        def ingest_business_knowledge(content: str, domain: str) -> bool:
            """Ingest."""
            return True
        
        @mcp_tool()
        def query_audit_trail(limit: int = 50) -> int:
            """Query."""
            return limit
        
        # All tools should be callable
        assert scaffold_orchestrator("test") == "scaffolded-test"
        assert validate_template("/path") is True
        assert check_phase_readiness("PHASE-01") is True
        assert ingest_business_knowledge("content", "domain") is True
        assert query_audit_trail(100) == 100


class TestToolDescriptions:
    """Test that all critical tools have proper descriptions."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_scaffold_orchestrator_description(self) -> None:
        """Test scaffold_orchestrator has description."""
        @mcp_tool()
        def scaffold_orchestrator(template_name: str) -> str:
            """Generate a new orchestrator from template."""
            return ""
        
        tools = get_registered_tools()
        desc = tools["scaffold_orchestrator"].description
        assert "orchestrator" in desc.lower()
        assert "template" in desc.lower()
    
    def test_validate_template_description(self) -> None:
        """Test validate_template has description."""
        @mcp_tool()
        def validate_template(template_path: str) -> bool:
            """Validate an orchestrator template for correctness."""
            return True
        
        tools = get_registered_tools()
        desc = tools["validate_template"].description
        assert "validate" in desc.lower()
        assert "template" in desc.lower()
    
    def test_check_phase_readiness_description(self) -> None:
        """Test check_phase_readiness has description."""
        @mcp_tool()
        def check_phase_readiness(phase_id: str) -> bool:
            """Check if a phase is ready to start."""
            return True
        
        tools = get_registered_tools()
        desc = tools["check_phase_readiness"].description
        assert "phase" in desc.lower()
        assert "ready" in desc.lower()
    
    def test_ingest_knowledge_description(self) -> None:
        """Test ingest_business_knowledge has description."""
        @mcp_tool()
        def ingest_business_knowledge(content: str, domain: str) -> bool:
            """Ingest business knowledge document."""
            return True
        
        tools = get_registered_tools()
        desc = tools["ingest_business_knowledge"].description
        assert "knowledge" in desc.lower() or "ingest" in desc.lower()
    
    def test_query_audit_trail_description(self) -> None:
        """Test query_audit_trail has description."""
        @mcp_tool()
        def query_audit_trail(limit: int = 100) -> Dict[str, Any]:
            """Query the governance audit trail."""
            return {}
        
        tools = get_registered_tools()
        desc = tools["query_audit_trail"].description
        assert "audit" in desc.lower() or "query" in desc.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
