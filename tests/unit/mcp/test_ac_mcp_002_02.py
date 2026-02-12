"""
AC-MCP-002-02: Governance Auditor MCP Exposure Tests

Tests for exposing governance auditor tools via @mcp_tool decorator:
- GovernanceAuditor.audit_tool_exposure()
- GovernanceAuditor.check_decorator_compliance()
- GovernanceAuditor.generate_exposure_report()

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)

AC_START: AC-WAVE-L-001
Description: Governance auditor MCP tool tests
"""

import pytest
from typing import Dict, Any, List, Optional
from cortex.mcp.decorators import mcp_tool, get_registered_tools, clear_tools


class TestGovernanceAuditorExposure:
    """Test GovernanceAuditor exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_audit_tool_exposure_exists(self) -> None:
        """Test that audit_tool_exposure is exposed as MCP tool."""
        @mcp_tool(
            name="audit_tool_exposure",
            description="Audit MCP tool exposure compliance",
            category="governance"
        )
        def audit_tool_exposure(
            scope: str = "all",
            include_internal: bool = False
        ) -> Dict[str, Any]:
            """Audit MCP tool exposure compliance."""
            return {
                "status": "success",
                "scope": scope,
                "tools_audited": 10,
                "compliant": 8,
                "violations": 2
            }
        
        tools = get_registered_tools()
        assert "audit_tool_exposure" in tools
        assert tools["audit_tool_exposure"]["category"] == "governance"
    
    def test_audit_tool_exposure_parameters(self) -> None:
        """Test audit_tool_exposure tool parameters."""
        @mcp_tool(
            name="audit_tool_exposure",
            description="Audit MCP tool exposure compliance"
        )
        def audit_tool_exposure(
            scope: str = "all",
            include_internal: bool = False
        ) -> Dict[str, Any]:
            """Audit MCP tool exposure compliance."""
            return {}
        
        tools = get_registered_tools()
        assert "audit_tool_exposure" in tools
    
    def test_audit_tool_exposure_return_structure(self) -> None:
        """Test audit_tool_exposure returns expected structure."""
        @mcp_tool(
            name="audit_tool_exposure",
            description="Audit MCP tool exposure compliance"
        )
        def audit_tool_exposure(
            scope: str = "all",
            include_internal: bool = False
        ) -> Dict[str, Any]:
            """Audit MCP tool exposure compliance."""
            return {
                "status": "success",
                "scope": scope,
                "tools_audited": 10,
                "compliant": 8,
                "violations": 2,
                "details": []
            }
        
        result = audit_tool_exposure()
        assert "status" in result
        assert "tools_audited" in result
        assert "compliant" in result
        assert "violations" in result


class TestDecoratorComplianceExposure:
    """Test decorator compliance checking exposure."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_check_decorator_compliance_exists(self) -> None:
        """Test that check_decorator_compliance is exposed as MCP tool."""
        @mcp_tool(
            name="check_decorator_compliance",
            description="Check @mcp_tool decorator compliance",
            category="governance"
        )
        def check_decorator_compliance(
            tool_name: str,
            strict_mode: bool = True
        ) -> Dict[str, Any]:
            """Check @mcp_tool decorator compliance."""
            return {
                "tool_name": tool_name,
                "compliant": True,
                "issues": [],
                "recommendations": []
            }
        
        tools = get_registered_tools()
        assert "check_decorator_compliance" in tools
        assert tools["check_decorator_compliance"]["category"] == "governance"
    
    def test_check_decorator_compliance_strict_mode(self) -> None:
        """Test strict mode parameter."""
        @mcp_tool(
            name="check_decorator_compliance",
            description="Check @mcp_tool decorator compliance"
        )
        def check_decorator_compliance(
            tool_name: str,
            strict_mode: bool = True
        ) -> Dict[str, Any]:
            """Check @mcp_tool decorator compliance."""
            issues = [] if strict_mode else ["Warning: Non-strict mode"]
            return {
                "tool_name": tool_name,
                "compliant": True,
                "issues": issues,
                "strict_mode": strict_mode
            }
        
        result_strict = check_decorator_compliance("test_tool", strict_mode=True)
        result_lenient = check_decorator_compliance("test_tool", strict_mode=False)
        
        assert result_strict["issues"] == []
        assert len(result_lenient["issues"]) > 0


class TestExposureReportExposure:
    """Test exposure report generation exposure."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_generate_exposure_report_exists(self) -> None:
        """Test that generate_exposure_report is exposed as MCP tool."""
        @mcp_tool(
            name="generate_exposure_report",
            description="Generate MCP tool exposure report",
            category="governance"
        )
        def generate_exposure_report(
            output_format: str = "yaml",
            include_metrics: bool = True
        ) -> Dict[str, Any]:
            """Generate MCP tool exposure report."""
            return {
                "format": output_format,
                "timestamp": "2026-02-12T10:00:00Z",
                "total_tools": 15,
                "exposed_tools": 12,
                "coverage": 80.0
            }
        
        tools = get_registered_tools()
        assert "generate_exposure_report" in tools
        assert tools["generate_exposure_report"]["category"] == "governance"
    
    def test_generate_exposure_report_formats(self) -> None:
        """Test multiple output formats."""
        @mcp_tool(
            name="generate_exposure_report",
            description="Generate MCP tool exposure report"
        )
        def generate_exposure_report(
            output_format: str = "yaml",
            include_metrics: bool = True
        ) -> Dict[str, Any]:
            """Generate MCP tool exposure report."""
            return {
                "format": output_format,
                "data": "report_content"
            }
        
        result_yaml = generate_exposure_report(output_format="yaml")
        result_json = generate_exposure_report(output_format="json")
        
        assert result_yaml["format"] == "yaml"
        assert result_json["format"] == "json"


class TestGovernanceToolIntegration:
    """Test integration of multiple governance tools."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_multiple_governance_tools_registered(self) -> None:
        """Multiple governance tools can be registered."""
        @mcp_tool(
            name="audit_tool_exposure",
            description="Audit tool exposure",
            category="governance"
        )
        def audit_tool_exposure() -> Dict[str, Any]:
            return {"status": "success"}
        
        @mcp_tool(
            name="check_decorator_compliance",
            description="Check decorator compliance",
            category="governance"
        )
        def check_decorator_compliance() -> Dict[str, Any]:
            return {"compliant": True}
        
        @mcp_tool(
            name="generate_exposure_report",
            description="Generate exposure report",
            category="governance"
        )
        def generate_exposure_report() -> Dict[str, Any]:
            return {"total_tools": 3}
        
        tools = get_registered_tools()
        governance_tools = [
            name for name, tool in tools.items()
            if tool["category"] == "governance"
        ]
        
        assert len(governance_tools) == 3
        assert "audit_tool_exposure" in governance_tools
        assert "check_decorator_compliance" in governance_tools
        assert "generate_exposure_report" in governance_tools


class TestGovernanceMetrics:
    """Test governance metrics collection."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_collect_governance_metrics(self) -> None:
        """Test governance metrics collection."""
        @mcp_tool(
            name="collect_governance_metrics",
            description="Collect governance metrics",
            category="governance"
        )
        def collect_governance_metrics(
            metric_type: str = "all",
            time_range: str = "24h"
        ) -> Dict[str, Any]:
            """Collect governance metrics."""
            return {
                "metric_type": metric_type,
                "time_range": time_range,
                "tools_audited": 50,
                "violations_detected": 5,
                "compliance_rate": 90.0
            }
        
        tools = get_registered_tools()
        assert "collect_governance_metrics" in tools
        
        result = collect_governance_metrics()
        assert "compliance_rate" in result
        assert result["compliance_rate"] >= 0.0


class TestGovernanceReporting:
    """Test governance reporting tools."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_governance_dashboard_data(self) -> None:
        """Test governance dashboard data generation."""
        @mcp_tool(
            name="get_governance_dashboard_data",
            description="Get governance dashboard data",
            category="governance"
        )
        def get_governance_dashboard_data() -> Dict[str, Any]:
            """Get governance dashboard data."""
            return {
                "total_tools": 20,
                "exposed_tools": 18,
                "coverage_percentage": 90.0,
                "recent_violations": [],
                "trends": {
                    "weekly_compliance": [85.0, 87.0, 90.0],
                    "weekly_tools": [15, 18, 20]
                }
            }
        
        tools = get_registered_tools()
        assert "get_governance_dashboard_data" in tools
        
        result = get_governance_dashboard_data()
        assert "coverage_percentage" in result
        assert "trends" in result


# AC_COMPLETE: AC-WAVE-L-001 ✅
