"""
AC-ENH-059-004: AuditRemediationCoordinator - TDD Test Suite

Tests for audit-to-remediation coordination.
Integrates RemediationPlanGenerator with audit workflow.
"""

import pytest
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.planning import (
    RemediationPlanGenerator,
    AuditFinding,
    RemediationPlan
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_audit_results() -> Dict[str, Any]:
    """Mock audit results from an audit scan."""
    return {
        "status": "complete",
        "findings": [
            {
                "severity": "P0",
                "category": "Critical Error",
                "description": "System crash on startup",
                "files_affected": ["cortex/core/init.py"],
                "estimated_effort_minutes": 30
            },
            {
                "severity": "P1",
                "category": "Missing Tests",
                "description": "10 modules lack test coverage",
                "files_affected": ["cortex/module_a.py", "cortex/module_b.py"],
                "estimated_effort_minutes": 120
            }
        ],
        "summary": {
            "total_issues": 2,
            "p0_count": 1,
            "p1_count": 1
        }
    }


# ============================================================================
# TEST SUITE: AuditRemediationCoordinator
# ============================================================================

class TestAuditRemediationCoordinator:
    """Test suite for audit-to-remediation coordination."""
    
    def test_coordinator_initialization(self):
        """Coordinator initializes with generator and formatter."""
        from cortex.orchestrators.planning.audit_remediation_coordinator import (
            AuditRemediationCoordinator
        )
        
        coordinator = AuditRemediationCoordinator()
        
        assert coordinator is not None
        assert hasattr(coordinator, "generate_remediation_plan")
        assert hasattr(coordinator, "format_plan_with_prompt")
        assert hasattr(coordinator, "process_user_selection")
    
    def test_generate_plan_from_audit_results(self, mock_audit_results):
        """Generate remediation plan from audit results."""
        from cortex.orchestrators.planning.audit_remediation_coordinator import (
            AuditRemediationCoordinator
        )
        
        coordinator = AuditRemediationCoordinator()
        plan = coordinator.generate_remediation_plan(mock_audit_results)
        
        assert isinstance(plan, RemediationPlan)
        assert len(plan.phases) > 0
        assert plan.total_effort_minutes == 150  # 30 + 120
    
    def test_format_plan_includes_audit_summary(self, mock_audit_results):
        """Formatted plan includes audit summary section."""
        from cortex.orchestrators.planning.audit_remediation_coordinator import (
            AuditRemediationCoordinator
        )
        
        coordinator = AuditRemediationCoordinator()
        plan = coordinator.generate_remediation_plan(mock_audit_results)
        output = coordinator.format_plan_with_prompt(plan, mock_audit_results)
        
        assert "## 🎯 Audit Complete - Remediation Plan" in output
        assert "### 📊 Issues Found" in output
        assert "P0" in output
        assert "P1" in output
    
    def test_process_option_1_autonomous(self):
        """Option 1 triggers autonomous mode flag."""
        from cortex.orchestrators.planning.audit_remediation_coordinator import (
            AuditRemediationCoordinator
        )
        
        coordinator = AuditRemediationCoordinator()
        result = coordinator.process_user_selection(1)
        
        assert result["mode"] == "autonomous"
        assert result["autonomous"] is True
    
    def test_process_option_2_interactive(self):
        """Option 2 triggers interactive mode (current behavior)."""
        from cortex.orchestrators.planning.audit_remediation_coordinator import (
            AuditRemediationCoordinator
        )
        
        coordinator = AuditRemediationCoordinator()
        result = coordinator.process_user_selection(2)
        
        assert result["mode"] == "interactive"
        assert result["autonomous"] is False
    
    def test_process_option_3_review_only(self):
        """Option 3 returns review-only mode."""
        from cortex.orchestrators.planning.audit_remediation_coordinator import (
            AuditRemediationCoordinator
        )
        
        coordinator = AuditRemediationCoordinator()
        result = coordinator.process_user_selection(3)
        
        assert result["mode"] == "review"
        assert result["should_execute"] is False
    
    def test_process_option_4_cancel(self):
        """Option 4 returns cancel mode."""
        from cortex.orchestrators.planning.audit_remediation_coordinator import (
            AuditRemediationCoordinator
        )
        
        coordinator = AuditRemediationCoordinator()
        result = coordinator.process_user_selection(4)
        
        assert result["mode"] == "cancel"
        assert result["should_execute"] is False
    
    def test_invalid_option_returns_error(self):
        """Invalid option returns error result."""
        from cortex.orchestrators.planning.audit_remediation_coordinator import (
            AuditRemediationCoordinator
        )
        
        coordinator = AuditRemediationCoordinator()
        result = coordinator.process_user_selection(5)
        
        assert result["mode"] == "error"
        assert "error" in result or "invalid" in result.get("message", "").lower()
    
    def test_convert_audit_findings_format(self, mock_audit_results):
        """Converts audit results to AuditFinding objects."""
        from cortex.orchestrators.planning.audit_remediation_coordinator import (
            AuditRemediationCoordinator
        )
        
        coordinator = AuditRemediationCoordinator()
        findings = coordinator._convert_audit_findings(mock_audit_results)
        
        assert len(findings) == 2
        assert all(isinstance(f, AuditFinding) for f in findings)
        assert findings[0].severity == "P0"
        assert findings[1].severity == "P1"


# ============================================================================
# TEST SUITE: MCP Tool Integration
# ============================================================================

class TestAuditRemediationMCPTool:
    """Test MCP tool for audit remediation coordination."""
    
    def test_mcp_tool_exists(self):
        """MCP tool cortex_audit_remediation_plan exists."""
        from cortex.mcp.tools.planning import planning_tools
        
        # Check that the tool functions are defined and decorated
        assert hasattr(planning_tools, "cortex_audit_remediation_plan")
        assert hasattr(planning_tools, "cortex_process_remediation_selection")
        
        # Verify they are callable
        assert callable(planning_tools.cortex_audit_remediation_plan)
        assert callable(planning_tools.cortex_process_remediation_selection)
    
    def test_mcp_tool_accepts_audit_results(self, mock_audit_results):
        """MCP tool accepts audit results and returns formatted plan."""
        # This will be implemented when MCP tool is created
        pytest.skip("MCP tool integration - implement after coordinator complete")
    
    def test_mcp_tool_returns_user_prompt(self):
        """MCP tool returns plan with user selection prompt."""
        pytest.skip("MCP tool integration - implement after coordinator complete")



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
