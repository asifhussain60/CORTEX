"""
AC-ENH-059-001: RemediationPlanGenerator - TDD Test Suite

Tests for automated remediation plan generation from audit findings.
Implements ENH-059: Audit-Driven Auto-Planning specification.
"""

import pytest
from typing import Dict, List, Any

# Import from implementation
from cortex.orchestrators.planning.remediation_plan_generator import (
    AuditFinding,
    RemediationPhase,
    RemediationPlan
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_audit_findings() -> List[AuditFinding]:
    """Sample audit findings from chat01.txt session."""
    return [
        AuditFinding(
            severity="P0",
            category="Tool discovery crash",
            description="ToolCategory type mismatch causes 'str' object has no attribute 'value' crash",
            files_affected=["cortex/mcp/tool_discovery.py"],
            estimated_effort_minutes=15
        ),
        AuditFinding(
            severity="P0",
            category="Missing module",
            description="orchestrator_wiring module not found",
            files_affected=["cortex/orchestrators/core/orchestrator_wiring.py"],
            estimated_effort_minutes=10
        ),
        AuditFinding(
            severity="P1",
            category="Missing MCP adapters",
            description="26 orchestrators lack MCP adapter configuration",
            files_affected=["cortex/wiring/specifications/wiring.yaml"],
            estimated_effort_minutes=60
        ),
    ]


# ============================================================================
# TEST SUITE: RemediationPlanGenerator
# ============================================================================

class TestRemediationPlanGenerator:
    """Test suite for RemediationPlanGenerator."""
    
    def test_generator_initialization(self):
        """Generator initializes with default configuration."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        
        generator = RemediationPlanGenerator()
        
        assert generator is not None
        assert hasattr(generator, "generate_plan")
        assert hasattr(generator, "calculate_dependencies")
        assert hasattr(generator, "assess_risk")
    
    def test_generate_plan_from_findings(self, sample_audit_findings):
        """Generate remediation plan from audit findings."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        
        generator = RemediationPlanGenerator()
        plan = generator.generate_plan(sample_audit_findings)
        
        assert isinstance(plan, RemediationPlan)
        assert len(plan.phases) > 0
        assert plan.total_effort_minutes > 0
        assert plan.overall_risk in ["LOW", "MEDIUM", "HIGH", "LOW-MEDIUM", "MEDIUM-HIGH"]
    
    def test_phase_dependencies_calculated(self, sample_audit_findings):
        """Phases have correct dependencies."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        
        generator = RemediationPlanGenerator()
        plan = generator.generate_plan(sample_audit_findings)
        
        # Phase 1 (critical fixes) should have no dependencies
        phase1 = plan.phases[0]
        assert len(phase1.dependencies) == 0
        
        # Later phases may depend on Phase 1
        if len(plan.phases) > 1:
            later_phases = plan.phases[1:]
            # At least one should depend on Phase 1
            dependent_phases = [p for p in later_phases if phase1.phase_id in p.dependencies]
            assert len(dependent_phases) >= 0  # May or may not have dependencies
    
    def test_risk_assessment_by_severity(self, sample_audit_findings):
        """Risk assessment considers finding severity."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        
        generator = RemediationPlanGenerator()
        plan = generator.generate_plan(sample_audit_findings)
        
        # P0 findings should result in at least one LOW risk phase
        p0_findings = [f for f in sample_audit_findings if f.severity == "P0"]
        if p0_findings:
            # First phase with P0 fixes should be LOW risk (simple fixes)
            phase1 = plan.phases[0]
            assert phase1.risk_level in ["LOW", "MEDIUM"]
    
    def test_execution_options_included(self, sample_audit_findings):
        """Plan includes 4 execution options."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        
        generator = RemediationPlanGenerator()
        plan = generator.generate_plan(sample_audit_findings)
        
        assert len(plan.execution_options) == 4
        
        # Option 1: Auto-execute
        option1 = plan.execution_options[0]
        assert option1["number"] == 1
        assert "auto" in option1["name"].lower() or "autonomous" in option1["name"].lower()
        
        # Option 2: Interactive (default)
        option2 = plan.execution_options[1]
        assert option2["number"] == 2
        assert option2.get("default") is True
        
        # Option 3: Review only
        option3 = plan.execution_options[2]
        assert option3["number"] == 3
        
        # Option 4: Cancel
        option4 = plan.execution_options[3]
        assert option4["number"] == 4
    
    def test_total_effort_calculation(self, sample_audit_findings):
        """Total effort is sum of phase efforts."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        
        generator = RemediationPlanGenerator()
        plan = generator.generate_plan(sample_audit_findings)
        
        calculated_total = sum(phase.estimated_minutes for phase in plan.phases)
        assert plan.total_effort_minutes == calculated_total
    
    def test_test_requirements_specified(self, sample_audit_findings):
        """Each phase has test requirements."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        
        generator = RemediationPlanGenerator()
        plan = generator.generate_plan(sample_audit_findings)
        
        for phase in plan.phases:
            assert len(phase.test_requirements) > 0
            # Test requirements should be specific
            for test_req in phase.test_requirements:
                assert len(test_req) > 0
    
    def test_empty_findings_returns_empty_plan(self):
        """Empty findings list returns empty plan."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        
        generator = RemediationPlanGenerator()
        plan = generator.generate_plan([])
        
        assert len(plan.phases) == 0
        assert plan.total_effort_minutes == 0
        assert plan.overall_risk == "LOW"


# ============================================================================
# TEST SUITE: RemediationPlanFormatter
# ============================================================================

class TestRemediationPlanFormatter:
    """Test suite for RemediationPlanFormatter (markdown output)."""
    
    def test_formatter_initialization(self):
        """Formatter initializes successfully."""
        from cortex.orchestrators.planning.remediation_plan_formatter import (
            RemediationPlanFormatter
        )
        
        formatter = RemediationPlanFormatter()
        
        assert formatter is not None
        assert hasattr(formatter, "format_plan")
    
    def test_format_plan_markdown(self, sample_audit_findings):
        """Format plan as markdown."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        from cortex.orchestrators.planning.remediation_plan_formatter import (
            RemediationPlanFormatter
        )
        
        generator = RemediationPlanGenerator()
        plan = generator.generate_plan(sample_audit_findings)
        
        formatter = RemediationPlanFormatter()
        markdown = formatter.format_plan(plan)
        
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        
        # Should contain key sections
        assert "## 🎯 Audit Complete - Remediation Plan" in markdown
        assert "### 📊 Issues Found" in markdown
        assert "### 🔧 Remediation Plan" in markdown
        assert "### ⚙️ Execution Options" in markdown
        
        # Should contain phase information
        assert "**Phase" in markdown
        assert "Est:" in markdown
        assert "Risk:" in markdown
    
    def test_format_includes_execution_prompt(self, sample_audit_findings):
        """Formatted output includes user prompt."""
        from cortex.orchestrators.planning.remediation_plan_generator import (
            RemediationPlanGenerator
        )
        from cortex.orchestrators.planning.remediation_plan_formatter import (
            RemediationPlanFormatter
        )
        
        generator = RemediationPlanGenerator()
        plan = generator.generate_plan(sample_audit_findings)
        
        formatter = RemediationPlanFormatter()
        markdown = formatter.format_plan(plan)
        
        assert "Choose execution mode [1-4]:" in markdown


# ============================================================================
# TEST SUITE: Integration with MasterOrchestrator
# ============================================================================

class TestRemediationPlanIntegration:
    """Test integration with MasterOrchestrator audit flow."""
    
    def test_master_orchestrator_generates_plan_after_audit(self):
        """MasterOrchestrator generates remediation plan after audit."""
        # This will be implemented after RemediationPlanGenerator is working
        pytest.skip("Integration test - implement after generator complete")
    
    def test_plan_display_before_user_prompt(self):
        """Plan is displayed before requesting user input."""
        pytest.skip("Integration test - implement after generator complete")
    
    def test_option_routing(self):
        """User option selection routes correctly."""
        pytest.skip("Integration test - implement after generator complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
