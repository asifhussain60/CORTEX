"""Tests for Copilot Chat Template Engine.

AC-ID: AC-REFACTOR-ARCHITECT-001
Governance: CORE-008 (TDD-first)
"""

import pytest
from cortex.orchestrators.response.copilot_chat_templates import (
    CopilotChatTemplateEngine,
    CopilotChatMode,
    SectionDefinition,
    get_copilot_chat_engine,
)


class TestCopilotChatTemplateEngine:
    """Test suite for Copilot chat template engine."""
    
    @pytest.fixture
    def engine(self):
        """Create template engine instance."""
        return CopilotChatTemplateEngine()
    
    def test_engine_initialization(self, engine):
        """Test engine initializes with all templates registered."""
        assert engine is not None
        assert engine.base_engine is not None
        assert engine.base_engine.registry is not None
        
        # Verify all 5 templates are registered
        templates = engine.base_engine.registry.list_templates()
        template_ids = {t.template_id for t in templates}
        
        assert "copilot-audit-summary" in template_ids
        assert "copilot-design-challenge" in template_ids
        assert "copilot-dor-gate" in template_ids
        assert "copilot-implementation-complete" in template_ids
        assert "copilot-next-steps" in template_ids
    
    def test_audit_summary_template(self, engine):
        """Test audit summary template rendering."""
        result = engine.render_audit_summary(
            orchestrator="MasterOrchestrator",
            p0_count=2,
            p1_count=5,
            p2_count=10,
            p3_count=3,
            audit_details="| Category | Status |\n|----------|--------|\n| Security | ✅ |",
            recommendations="1. Add caching\n2. Refactor module X",
            next_steps="1. Fix P0 issues\n2. Review P1 infrastructure"
        )
        
        # Verify header
        assert "## 🔍 CORTEX Audit" in result
        assert "**Author:** Asif Hussain" in result
        assert "**Orchestrator:** MasterOrchestrator ✅" in result
        
        # Verify sections
        assert "### 📋 Audit Summary" in result
        assert "### 💡 Out of the Box Recommendations" in result
        assert "### 🎯 Next Steps" in result
        
        # Verify content
        assert "Add caching" in result
        assert "Fix P0 issues" in result
        
        # Verify Next Steps is last major section
        assert engine.validate_section_order(result)
    
    def test_design_challenge_template(self, engine):
        """Test design challenge template rendering."""
        result = engine.render_design_challenge(
            orchestrator="MasterOrchestrator",
            user_request="Add user authentication",
            extensibility_analysis="| Dimension | Current | Gap |\n|-----------|---------|-----|",
            accuracy_efficiency_tradeoff="| Factor | Accuracy | Speed |\n|--------|----------|-------|",
            weaknesses="| # | Weakness | Category |\n|---|----------|----------|",
            fix_plans="**Fix #1:** Root cause analysis",
            best_practices="| Source | Standard | Status |\n|--------|----------|--------|",
            verdict="PROCEED",
            next_steps="1. Implement auth module\n2. Add tests"
        )
        
        # Verify header
        assert "## ⚠️ CHALLENGE + RECOMMENDATION" in result
        assert "**User's Request:** Add user authentication" in result
        
        # Verify all required sections
        assert "### 🎯 Extensibility & Scalability Analysis" in result
        assert "### ⚖️ Accuracy vs Efficiency Tradeoff" in result
        assert "### 🔴 Identified Weaknesses" in result
        assert "### 🟢 Evidence-Based Fix Plan" in result
        assert "### 🎓 Best Practices" in result
        assert "**Verdict:** PROCEED" in result
        assert "### 🎯 Next Steps" in result
        
        # Verify approval gate
        assert "⏳ Awaiting approval" in result
        assert 'Type **"proceed"**' in result
        
        # Verify Next Steps before approval gate
        assert engine.validate_section_order(result)
    
    def test_design_challenge_with_counter_proposal(self, engine):
        """Test design challenge template with optional counter-proposal."""
        result = engine.render_design_challenge(
            orchestrator="MasterOrchestrator",
            user_request="Use Redis for caching",
            extensibility_analysis="| Dimension | Current | Gap |\n|-----------|---------|-----|",
            accuracy_efficiency_tradeoff="| Factor | Accuracy | Speed |\n|--------|----------|-------|",
            weaknesses="| # | Weakness | Category |\n|---|----------|----------|",
            fix_plans="**Fix #1:** Consider alternatives",
            best_practices="| Source | Standard | Status |\n|--------|----------|--------|",
            verdict="PIVOT",
            next_steps="1. Evaluate in-memory cache\n2. Compare benchmarks",
            counter_proposal="Use Python's functools.lru_cache for simpler solution"
        )
        
        # Verify counter-proposal section appears
        assert "### 🧠 Counter-Proposal" in result
        assert "functools.lru_cache" in result
        assert "**Verdict:** PIVOT" in result
    
    def test_dor_gate_template(self, engine):
        """Test DoR approval gate template rendering."""
        result = engine.render_dor_gate(
            orchestrator="MasterOrchestrator",
            intent="IMPLEMENT",
            target="AuthenticationModule",
            dor_table="| Field | Value | Validated |\n|-------|-------|-----------|",
            next_steps="1. Execute TDD cycle\n2. Run integration tests"
        )
        
        # Verify header
        assert "## 📋 Definition of Ready" in result
        
        # Verify DoR table
        assert "| Field | Value | Validated |" in result
        
        # Verify architecture ready
        assert "**Architecture Evolution Ready:** YES ✅" in result
        
        # Verify Next Steps
        assert "### 🎯 Next Steps" in result
        assert "Execute TDD cycle" in result
        
        # Verify approval gate
        assert "⏳ Awaiting approval" in result
        assert '"implement"' in result
        
        # Verify Next Steps is last before approval
        assert engine.validate_section_order(result)
    
    def test_implementation_complete_template(self, engine):
        """Test implementation complete template rendering."""
        result = engine.render_implementation_complete(
            orchestrator="MasterOrchestrator",
            summary="- Feature X implemented\n- Tests passing\n- Documentation updated",
            files_modified=5,
            tests_passing=True,
            gap_analysis="| Gap | Priority | Effort |\n|-----|----------|--------|",
            architecture_evolution="| Metric | Before | After |\n|--------|--------|-------|",
            next_steps="1. Deploy to staging\n2. Monitor metrics"
        )
        
        # Verify header
        assert "## ✅ Implementation Complete" in result
        assert "**Author:** Asif Hussain" in result
        assert "**Orchestrator:** MasterOrchestrator ✅" in result
        
        # Verify summary section
        assert "### 📊 Summary" in result
        assert "Feature X implemented" in result
        
        # Verify metrics
        assert "**Files Modified:** 5" in result
        assert "**Tests Passing:** ✅ Passing" in result
        
        # Verify gap analysis
        assert "### 🔍 Gap Analysis" in result
        
        # Verify architecture evolution
        assert "### 🏗️ Architecture Evolution" in result
        
        # Verify Next Steps is last
        assert "### 🎯 Next Steps" in result
        assert "Deploy to staging" in result
        assert engine.validate_section_order(result)
    
    def test_implementation_complete_with_failing_tests(self, engine):
        """Test implementation complete template with failing tests."""
        result = engine.render_implementation_complete(
            orchestrator="MasterOrchestrator",
            summary="- Implementation in progress",
            files_modified=3,
            tests_passing=False,
            gap_analysis="| Gap | Priority |\n|-----|----------|",
            architecture_evolution="| Metric | Status |\n|--------|--------|",
            next_steps="1. Fix failing tests\n2. Complete implementation"
        )
        
        # Verify failing test indicator
        assert "**Tests Passing:** ❌ Failing" in result
        assert "Fix failing tests" in result
    
    def test_next_steps_standalone(self, engine):
        """Test standalone next steps section rendering."""
        result = engine.render_next_steps(
            steps="1. First action\n2. Second action\n3. Third action"
        )
        
        # Verify section
        assert "### 🎯 Next Steps" in result
        assert "1. First action" in result
        assert "2. Second action" in result
        assert "3. Third action" in result
    
    def test_section_order_validation_valid(self, engine):
        """Test section order validation with correct order."""
        valid_response = """
## Some Header

### Content Section

Some content here

### 🎯 Next Steps

1. Action 1
2. Action 2

---

**⏳ Awaiting approval...** Type "proceed" to continue.
"""
        assert engine.validate_section_order(valid_response) is True
    
    def test_section_order_validation_invalid(self, engine):
        """Test section order validation with incorrect order."""
        invalid_response = """
## Some Header

### 🎯 Next Steps

1. Action 1

### Another Section After Next Steps

This breaks the ordering rule.

---

**⏳ Awaiting approval...** Type "proceed" to continue.
"""
        # Should fail because content appears between Next Steps and approval
        assert engine.validate_section_order(invalid_response) is False
    
    def test_section_order_validation_no_approval_gate(self, engine):
        """Test section order validation without approval gate."""
        response_without_gate = """
## Some Header

### Content

Some content

### 🎯 Next Steps

1. Action 1
2. Action 2
"""
        # Should pass (no approval gate to validate against)
        assert engine.validate_section_order(response_without_gate) is True
    
    def test_template_variable_validation(self, engine):
        """Test template validates required variables."""
        # This test should verify that all required variables are present
        # Since we're passing all required variables, it should succeed
        result = engine.render_audit_summary(
            orchestrator="MasterOrchestrator",
            p0_count=1,
            p1_count=2,
            p2_count=3,
            p3_count=4,
            audit_details="Details",
            recommendations="Recommendations",
            next_steps=""  # Empty but present - should work
        )
        
        # Verify result contains expected sections
        assert "## 🔍 CORTEX Audit" in result
        assert "MasterOrchestrator" in result
    
    def test_get_singleton_engine(self):
        """Test singleton pattern for engine access."""
        engine1 = get_copilot_chat_engine()
        engine2 = get_copilot_chat_engine()
        
        # Should return same instance
        assert engine1 is engine2
        
        # Should have templates registered
        templates = engine1.base_engine.registry.list_templates()
        assert len(templates) >= 5


class TestSectionDefinition:
    """Test suite for SectionDefinition dataclass."""
    
    def test_section_definition_creation(self):
        """Test creating section definition."""
        section = SectionDefinition(
            name="Header",
            required=True,
            order=1,
            template="## {{ title }}"
        )
        
        assert section.name == "Header"
        assert section.required is True
        assert section.order == 1
        assert section.template == "## {{ title }}"


class TestCopilotChatMode:
    """Test suite for CopilotChatMode enum."""
    
    def test_mode_enum_values(self):
        """Test all mode enum values exist."""
        assert CopilotChatMode.AUDIT.value == "audit"
        assert CopilotChatMode.DESIGN.value == "design"
        assert CopilotChatMode.DOR_GATE.value == "dor_gate"
        assert CopilotChatMode.IMPLEMENTATION_COMPLETE.value == "implementation_complete"
        assert CopilotChatMode.NEXT_STEPS_ONLY.value == "next_steps_only"


class TestIntegrationScenarios:
    """Integration tests for full workflow scenarios."""
    
    @pytest.fixture
    def engine(self):
        """Create template engine instance."""
        return CopilotChatTemplateEngine()
    
    def test_full_audit_to_implementation_workflow(self, engine):
        """Test complete workflow from audit to implementation."""
        # Step 1: Audit
        audit_response = engine.render_audit_summary(
            orchestrator="MasterOrchestrator",
            p0_count=0,
            p1_count=2,
            p2_count=5,
            p3_count=1,
            audit_details="| Category | Issues |\n|----------|--------|\n| Security | 0 |\n| Infrastructure | 2 |",
            recommendations="1. Improve test coverage\n2. Add documentation",
            next_steps="1. Address P1 infrastructure gaps\n2. Review P2 quality issues"
        )
        
        assert "🔍 CORTEX Audit" in audit_response
        assert engine.validate_section_order(audit_response)
        
        # Step 2: Design Challenge
        challenge_response = engine.render_design_challenge(
            orchestrator="MasterOrchestrator",
            user_request="Fix infrastructure gaps",
            extensibility_analysis="| Dimension | Assessment |\n|-----------|------------|",
            accuracy_efficiency_tradeoff="| Factor | Choice |\n|--------|--------|",
            weaknesses="| # | Gap | Impact |\n|---|-----|--------|",
            fix_plans="**Fix #1:** Implement monitoring",
            best_practices="| Standard | Status |\n|----------|--------|",
            verdict="PROCEED",
            next_steps="1. Implement monitoring\n2. Add health checks"
        )
        
        assert "⚠️ CHALLENGE" in challenge_response
        assert engine.validate_section_order(challenge_response)
        
        # Step 3: DoR Gate
        dor_response = engine.render_dor_gate(
            orchestrator="MasterOrchestrator",
            intent="IMPLEMENT",
            target="MonitoringModule",
            dor_table="| Field | Status |\n|-------|--------|\n| Tests | ✅ |\n| Wiring | ✅ |",
            next_steps="1. RED: Write tests\n2. GREEN: Implement\n3. REFACTOR: Clean up"
        )
        
        assert "📋 Definition of Ready" in dor_response
        assert engine.validate_section_order(dor_response)
        
        # Step 4: Implementation Complete
        complete_response = engine.render_implementation_complete(
            orchestrator="MasterOrchestrator",
            summary="- Monitoring module implemented\n- Health checks added\n- Tests passing",
            files_modified=4,
            tests_passing=True,
            gap_analysis="| Enhancement | Priority |\n|-------------|----------|",
            architecture_evolution="| Metric | Improvement |\n|--------|-------------|",
            next_steps="1. Deploy to staging\n2. Monitor production"
        )
        
        assert "✅ Implementation Complete" in complete_response
        assert engine.validate_section_order(complete_response)
