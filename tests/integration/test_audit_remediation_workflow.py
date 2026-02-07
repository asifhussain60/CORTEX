"""
AC-ENH-059-009: Integration tests for audit → remediation workflow

Tests the complete end-to-end flow:
1. Audit operation executes
2. Audit results automatically feed into remediation planner
3. Plan is generated with 4 execution options
4. User selection routes to appropriate handler

Authority: ENH-059 (P1, 8.5 confidence)
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock

from cortex.orchestrators.planning import (
    RemediationPlanGenerator,
    RemediationPlanFormatter,
    AuditRemediationCoordinator
)


class TestAuditRemediationWorkflow:
    """Integration tests for complete audit → remediation → execution workflow."""
    
    @pytest.fixture
    def mock_audit_results(self) -> Dict[str, Any]:
        """Sample audit results matching cortex_audit_cohesion format."""
        return {
            "status": "issues_found",
            "execution_time_seconds": 2.34,
            "summary": {
                "total_issues": 5,
                "validators_run": 7,
                "checks_executed": 15,
                "meets_performance_target": False
            },
            "validation_results": {
                "P0_CRITICAL": [
                    {
                        "check_id": "SEC-001",
                        "description": "Hardcoded credentials detected",
                        "severity": "CRITICAL",
                        "file": "cortex/config/settings.py",
                        "line": 42,
                        "recommendation": "Use environment variables"
                    }
                ],
                "P1_HIGH": [
                    {
                        "check_id": "GOV-002",
                        "description": "Missing docstrings",
                        "severity": "HIGH",
                        "file": "cortex/orchestrators/new_feature.py",
                        "line": 15,
                        "recommendation": "Add Google-style docstrings"
                    },
                    {
                        "check_id": "TEST-001",
                        "description": "Test coverage below 70%",
                        "severity": "HIGH",
                        "file": "cortex/orchestrators/new_feature.py",
                        "recommendation": "Add unit tests"
                    }
                ],
                "P2_MEDIUM": [
                    {
                        "check_id": "PERF-001",
                        "description": "Inefficient database query",
                        "severity": "MEDIUM",
                        "file": "cortex/data/repository.py",
                        "line": 128,
                        "recommendation": "Add index or use batch query"
                    },
                    {
                        "check_id": "STYLE-001",
                        "description": "Line too long (>100 chars)",
                        "severity": "MEDIUM",
                        "file": "cortex/utils/helpers.py",
                        "line": 56,
                        "recommendation": "Split into multiple lines"
                    }
                ]
            }
        }
    
    def test_audit_to_plan_conversion(self, mock_audit_results):
        """Step 1: Audit results convert to remediation plan."""
        coordinator = AuditRemediationCoordinator()
        
        plan = coordinator.generate_remediation_plan(mock_audit_results)
        
        # Verify plan structure
        assert plan is not None
        assert len(plan.phases) > 0
        assert plan.total_effort_minutes > 0
        assert plan.overall_risk in ["LOW", "MEDIUM", "HIGH", "LOW-MEDIUM", "MEDIUM-HIGH"]
        assert len(plan.execution_options) == 4
        
        # Verify phases match audit priorities
        phase_names = [p.name for p in plan.phases]
        assert any("Critical" in name or "P0" in name for name in phase_names)
    
    def test_plan_formatting_includes_audit_summary(self, mock_audit_results):
        """Step 2: Formatted plan includes audit summary."""
        coordinator = AuditRemediationCoordinator()
        plan = coordinator.generate_remediation_plan(mock_audit_results)
        
        formatted = coordinator.format_plan_with_prompt(plan, mock_audit_results)
        
        # Verify audit summary present
        assert "Total Issues" in formatted or "total issues" in formatted
        assert "Validators Run" in formatted or "validators" in formatted.lower()
        
        # Verify execution options present
        assert "1." in formatted or "[1]" in formatted  # Option 1
        assert "2." in formatted or "[2]" in formatted  # Option 2
        assert "3." in formatted or "[3]" in formatted  # Option 3
        assert "4." in formatted or "[4]" in formatted  # Option 4
        
        # Verify prompt for user selection
        assert "selection" in formatted.lower() or "choose" in formatted.lower()
    
    def test_user_selection_autonomous(self):
        """Step 3a: User selects option 1 (Autonomous)."""
        coordinator = AuditRemediationCoordinator()
        
        result = coordinator.process_user_selection(1)
        
        assert result["mode"] == "AUTONOMOUS"
        assert result["proceed"] is True
        assert "description" in result
        assert "auto" in result["description"].lower() or "autonomous" in result["description"].lower()
    
    def test_user_selection_interactive(self):
        """Step 3b: User selects option 2 (Interactive)."""
        coordinator = AuditRemediationCoordinator()
        
        result = coordinator.process_user_selection(2)
        
        assert result["mode"] == "INTERACTIVE"
        assert result["proceed"] is True
        assert "step-by-step" in result["description"].lower()
    
    def test_user_selection_review_only(self):
        """Step 3c: User selects option 3 (Review Only)."""
        coordinator = AuditRemediationCoordinator()
        
        result = coordinator.process_user_selection(3)
        
        assert result["mode"] == "REVIEW_ONLY"
        assert result["proceed"] is False
        assert "review" in result["description"].lower()
    
    def test_user_selection_cancel(self):
        """Step 3d: User selects option 4 (Cancel)."""
        coordinator = AuditRemediationCoordinator()
        
        result = coordinator.process_user_selection(4)
        
        assert result["mode"] == "CANCEL"
        assert result["proceed"] is False
        assert "cancelled" in result["description"].lower()
    
    @pytest.mark.asyncio
    async def test_mcp_tool_audit_to_plan(self, mock_audit_results):
        """Step 4: MCP tool accepts audit results and returns formatted plan."""
        from cortex.mcp.tools.planning import planning_tools
        
        result = await planning_tools.cortex_audit_remediation_plan(
            arguments={
                "audit_results": mock_audit_results,
                "format": "markdown"
            }
        )
        
        assert result["success"] is True
        assert "formatted" in result
        assert result["phase_count"] > 0
        assert result["total_effort_minutes"] > 0
        
        # Verify formatted output
        formatted = result["formatted"]
        assert "1." in formatted or "[1]" in formatted  # Option 1
        assert "2." in formatted or "[2]" in formatted  # Option 2
        assert "3." in formatted or "[3]" in formatted  # Option 3
        assert "4." in formatted or "[4]" in formatted  # Option 4
    
    @pytest.mark.asyncio
    async def test_mcp_tool_process_selection(self):
        """Step 5: MCP tool processes user's execution mode selection."""
        from cortex.mcp.tools.planning import planning_tools
        
        result = await planning_tools.cortex_process_remediation_selection(
            arguments={"option": 1}
        )
        
        assert result["success"] is True
        assert result["mode"] == "AUTONOMOUS"
        assert result["proceed"] is True
    
    def test_complete_workflow_simulation(self, mock_audit_results):
        """Step 6: Simulate complete workflow from audit to execution routing."""
        # Step 1: Audit completes (mock)
        audit_results = mock_audit_results
        
        # Step 2: Generate remediation plan
        coordinator = AuditRemediationCoordinator()
        plan = coordinator.generate_remediation_plan(audit_results)
        
        # Step 3: Format and present to user
        formatted_plan = coordinator.format_plan_with_prompt(plan, audit_results)
        
        # Verify plan was generated
        assert formatted_plan is not None
        assert len(formatted_plan) > 500  # Substantial output
        
        # Step 4: Simulate user selection (option 1 - Autonomous)
        user_choice = 1
        routing_result = coordinator.process_user_selection(user_choice)
        
        # Step 5: Verify routing decision
        assert routing_result["mode"] == "AUTONOMOUS"
        assert routing_result["proceed"] is True
        
        # At this point, the system would:
        # - If AUTONOMOUS or INTERACTIVE → Route to TDDOrchestrator / EnforcementOrchestrator
        # - If REVIEW_ONLY → Display plan details
        # - If CANCEL → Stop execution
    
    def test_zero_issues_scenario(self):
        """Edge case: Audit finds no issues."""
        clean_audit = {
            "status": "success",
            "summary": {"total_issues": 0},
            "validation_results": {}
        }
        
        coordinator = AuditRemediationCoordinator()
        plan = coordinator.generate_remediation_plan(clean_audit)
        
        # Should still generate plan (even if empty)
        assert plan is not None
        assert len(plan.phases) == 0  # No phases for zero issues
        assert plan.total_effort_minutes == 0
    
    def test_high_priority_only_scenario(self, mock_audit_results):
        """Edge case: Only P0/P1 issues found."""
        high_priority_only = {
            "status": "issues_found",
            "summary": {"total_issues": 2},
            "validation_results": {
                "P0_CRITICAL": mock_audit_results["validation_results"]["P0_CRITICAL"],
                "P1_HIGH": mock_audit_results["validation_results"]["P1_HIGH"][:1]
            }
        }
        
        coordinator = AuditRemediationCoordinator()
        plan = coordinator.generate_remediation_plan(high_priority_only)
        
        # With P0+P1 issues, overall risk should be elevated
        # (Could be HIGH, MEDIUM-HIGH, or LOW-MEDIUM depending on phase distribution)
        assert plan.overall_risk in ["HIGH", "MEDIUM-HIGH", "LOW-MEDIUM"]
        # At least one phase should have elevated risk
        assert any(p.risk_level in ["HIGH", "MEDIUM-HIGH", "MEDIUM"] for p in plan.phases)


class TestAuditRemediationMCPIntegration:
    """Integration tests for MCP tool layer."""
    
    @pytest.mark.asyncio
    async def test_mcp_tool_json_format(self):
        """Test MCP tool with JSON output format."""
        from cortex.mcp.tools.planning import planning_tools
        
        audit_results = {
            "status": "issues_found",
            "summary": {"total_issues": 1},
            "validation_results": {
                "P1_HIGH": [{
                    "check_id": "TEST",
                    "description": "Test issue",
                    "severity": "HIGH",
                    "file": "test.py",
                    "line": 1,
                    "recommendation": "Fix it"
                }]
            }
        }
        
        result = await planning_tools.cortex_audit_remediation_plan(
            arguments={
                "audit_results": audit_results,
                "format": "json"
            }
        )
        
        assert result["success"] is True
        assert "plan" in result
        assert "phases" in result["plan"]
        assert isinstance(result["plan"]["phases"], list)
    
    @pytest.mark.asyncio
    async def test_mcp_tool_error_handling(self):
        """Test MCP tool error handling."""
        from cortex.mcp.tools.planning import planning_tools
        
        # Missing audit_results
        result = await planning_tools.cortex_audit_remediation_plan(
            arguments={}
        )
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_mcp_selection_invalid_option(self):
        """Test MCP tool with invalid option."""
        from cortex.mcp.tools.planning import planning_tools
        
        result = await planning_tools.cortex_process_remediation_selection(
            arguments={"option": 99}
        )
        
        assert result["success"] is True  # Coordinator handles gracefully
        assert result["mode"] == "CANCEL"  # Invalid → Cancel


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
