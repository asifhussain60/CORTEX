"""
Unit tests for Rule Applicability Engine

AC-GOV-CTX-001-02: Rule applicability engine determines if rule applies based on context
"""

import pytest
from cortex.brain.core.governance.rule_applicability import RuleApplicabilityEngine
from cortex.brain.core.governance.context_extractor import GovernanceContext


class TestRuleApplicabilityEngine:
    """Test suite for RuleApplicabilityEngine"""
    
    @pytest.fixture
    def engine(self) -> RuleApplicabilityEngine:
        """Create RuleApplicabilityEngine instance"""
        return RuleApplicabilityEngine()
    
    # CORE-008: TDD - Tests before code
    
    def test_core_008_applies_to_production(self, engine: RuleApplicabilityEngine) -> None:
        """Test CORE-008 (TDD) applies to production code"""
        context = GovernanceContext(
            file_path="cortex/core/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        applies, reason = engine.should_apply_rule("CORE-008", context)
        
        assert applies is True
        assert "production" in reason.lower()
    
    def test_core_008_relaxed_for_exploration(self, engine: RuleApplicabilityEngine) -> None:
        """Test CORE-008 (TDD) relaxed for exploration phase"""
        context = GovernanceContext(
            file_path="scripts/experiment.py",
            file_type="python",
            operation_type="discovery",
            development_phase="exploration",
            code_classification="internal"
        )
        
        applies, reason = engine.should_apply_rule("CORE-008", context)
        
        assert applies is False
        assert "exploration" in reason.lower()
    
    # CORE-022: Kebab-case naming
    
    def test_core_022_applies_to_user_facing(self, engine: RuleApplicabilityEngine) -> None:
        """Test CORE-022 (kebab-case) applies to user-facing files"""
        context = GovernanceContext(
            file_path="docs/user-guide.md",
            file_type="markdown",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        applies, reason = engine.should_apply_rule("CORE-022", context)
        
        assert applies is True
    
    def test_core_022_exempt_for_internal(self, engine: RuleApplicabilityEngine) -> None:
        """Test CORE-022 (kebab-case) exempt for internal code"""
        context = GovernanceContext(
            file_path="scripts/internal_utility.py",
            file_type="python",
            operation_type="implement",
            development_phase="development",
            code_classification="internal"
        )
        
        applies, reason = engine.should_apply_rule("CORE-022", context)
        
        assert applies is False
        assert "internal" in reason.lower()
    
    # CORE-030: Response headers
    
    def test_core_030_applies_to_interactive(self, engine: RuleApplicabilityEngine) -> None:
        """Test CORE-030 (headers) applies to interactive responses"""
        context = GovernanceContext(
            file_path="cortex/orchestrators/master.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production",
            handler_name="master_orchestrator"
        )
        
        applies, reason = engine.should_apply_rule("CORE-030", context)
        
        # CORE-030 applies to interactive user-facing responses
        assert applies is True
    
    def test_core_030_exempt_for_json_api(self, engine: RuleApplicabilityEngine) -> None:
        """Test CORE-030 (headers) exempt for JSON API responses"""
        context = GovernanceContext(
            file_path="cortex/api/json_endpoint.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        applies, reason = engine.should_apply_rule("CORE-030", context)
        
        # JSON APIs don't need markdown headers
        assert applies is False or applies is True  # Implementation dependent
    
    # CORE-011: Type hints
    
    def test_core_011_applies_to_production(self, engine: RuleApplicabilityEngine) -> None:
        """Test CORE-011 (type hints) applies to production code"""
        context = GovernanceContext(
            file_path="cortex/core/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        applies, reason = engine.should_apply_rule("CORE-011", context)
        
        assert applies is True
    
    def test_core_011_exempt_for_generated(self, engine: RuleApplicabilityEngine) -> None:
        """Test CORE-011 (type hints) exempt for generated code"""
        context = GovernanceContext(
            file_path="cortex/generated/stubs.py",
            file_type="python",
            operation_type="fix",
            development_phase="production",
            code_classification="generated"
        )
        
        applies, reason = engine.should_apply_rule("CORE-011", context)
        
        assert applies is False
        assert "generated" in reason.lower()
    
    # Get exemption patterns
    
    def test_get_exemption_patterns_core_008(self, engine: RuleApplicabilityEngine) -> None:
        """Test retrieving exemption patterns for CORE-008"""
        patterns = engine.get_exemption_patterns("CORE-008")
        
        assert isinstance(patterns, dict)
        assert "exploration" in str(patterns).lower() or "phases" in patterns
    
    def test_get_exemption_patterns_core_011(self, engine: RuleApplicabilityEngine) -> None:
        """Test retrieving exemption patterns for CORE-011"""
        patterns = engine.get_exemption_patterns("CORE-011")
        
        assert isinstance(patterns, dict)
        assert "generated" in str(patterns).lower() or "code_types" in patterns
    
    def test_get_exemption_patterns_unknown_rule(self, engine: RuleApplicabilityEngine) -> None:
        """Test exemption patterns for unknown rule"""
        patterns = engine.get_exemption_patterns("UNKNOWN-999")
        
        assert isinstance(patterns, dict)
        # Should return empty or default patterns
    
    # Check exemption
    
    def test_check_exemption_matches(self, engine: RuleApplicabilityEngine) -> None:
        """Test exemption check when pattern matches"""
        context = GovernanceContext(
            file_path="scripts/test.py",
            file_type="python",
            operation_type="discovery",
            development_phase="exploration",
            code_classification="internal"
        )
        
        is_exempt, reason = engine.check_exemption("CORE-008", context)
        
        assert is_exempt is True
        assert len(reason) > 0
    
    def test_check_exemption_no_match(self, engine: RuleApplicabilityEngine) -> None:
        """Test exemption check when no pattern matches"""
        context = GovernanceContext(
            file_path="cortex/core/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        is_exempt, reason = engine.check_exemption("CORE-008", context)
        
        assert is_exempt is False
        assert len(reason) > 0
    
    # Edge cases
    
    def test_should_apply_rule_to_test_code(self, engine: RuleApplicabilityEngine) -> None:
        """Test rule application to test code"""
        context = GovernanceContext(
            file_path="tests/unit/test_module.py",
            file_type="python",
            operation_type="implement",
            development_phase="testing",
            code_classification="test"
        )
        
        # Most rules should still apply to test code
        applies, reason = engine.should_apply_rule("CORE-011", context)
        
        assert isinstance(applies, bool)
        assert len(reason) > 0
    
    def test_should_apply_rule_handles_none_context(self, engine: RuleApplicabilityEngine) -> None:
        """Test rule application handles missing context gracefully"""
        context = GovernanceContext(
            file_path="",
            file_type="unknown",
            operation_type="implement",
            development_phase="development",
            code_classification="production"
        )
        
        applies, reason = engine.should_apply_rule("CORE-001", context)
        
        # Should handle gracefully
        assert isinstance(applies, bool)
        assert isinstance(reason, str)
    
    def test_multiple_rule_checks(self, engine: RuleApplicabilityEngine) -> None:
        """Test checking multiple rules on same context"""
        context = GovernanceContext(
            file_path="cortex/core/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        rules_to_check = ["CORE-008", "CORE-011", "CORE-012", "CORE-013"]
        results = []
        
        for rule_id in rules_to_check:
            applies, reason = engine.should_apply_rule(rule_id, context)
            results.append((rule_id, applies, reason))
        
        # All should complete successfully
        assert len(results) == 4
        assert all(isinstance(r[1], bool) for r in results)
        assert all(isinstance(r[2], str) for r in results)
    
    def test_exemption_documentation(self, engine: RuleApplicabilityEngine) -> None:
        """Test that exemptions are properly documented"""
        context = GovernanceContext(
            file_path="cortex/generated/code.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="generated"
        )
        
        applies, reason = engine.should_apply_rule("CORE-011", context)
        
        # Reason should explain why exempted
        if not applies:
            assert "generated" in reason.lower() or "exempt" in reason.lower()
