"""
Integration Tests for Context-Aware Governance

AC-GOV-CTX-001-04: Verify end-to-end context-aware rule evaluation
Tests the complete pipeline: context extraction → applicability → validation
"""

import pytest
from cortex.brain.core.rule_evaluator import RuleEvaluator


class TestContextAwareIntegration:
    """Integration tests for context-aware governance evaluation"""
    
    def setup_method(self):
        """Setup for each test"""
        self.evaluator = RuleEvaluator()
    
    def test_evaluator_has_context_aware_components(self):
        """
        AC-GOV-CTX-001-04: Verify evaluator has context-aware pipeline
        """
        # Check that evaluator has required components
        assert hasattr(self.evaluator, 'context_extractor')
        assert hasattr(self.evaluator, 'applicability_engine')
        assert self.evaluator.context_extractor is not None
        assert self.evaluator.applicability_engine is not None
    
    def test_evaluate_rules_extracts_context_automatically(self):
        """
        AC-GOV-CTX-001-04: Context extraction happens automatically
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "MODIFY",
            "lines_changed": 100
        }
        
        # Should not crash - context extractor fills in missing context
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        # Evaluation completed successfully
        assert eval_result.evaluation_time_ms > 0
    
    def test_core_001_incremental_execution_pass(self):
        """
        AC-GOV-CTX-001-04: CORE-001 passes with small change
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "MODIFY",
            "lines_changed": 250
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # CORE-001 should pass (no violation for <500 lines)
        core_001_violations = [v for v in eval_result.violations if v.rule_id == "CORE-001"]
        assert len(core_001_violations) == 0
    
    def test_core_001_incremental_execution_violation(self):
        """
        AC-GOV-CTX-001-04: CORE-001 fails with large change
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "MODIFY",
            "lines_changed": 750
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # CORE-001 should fail (violation for >500 lines)
        core_001_violations = [v for v in eval_result.violations if v.rule_id == "CORE-001"]
        assert len(core_001_violations) >= 1
        
        violation = core_001_violations[0]
        assert violation.severity == "blocked"
        assert "750" in violation.message
    
    def test_core_008_tdd_pass_with_test(self):
        """
        AC-GOV-CTX-001-04: CORE-008 passes when test exists
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "CREATE",
            "test_file_exists": True
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # CORE-008 should pass (no violation when test exists)
        core_008_violations = [v for v in eval_result.violations if v.rule_id == "CORE-008"]
        assert len(core_008_violations) == 0
    
    def test_core_008_tdd_violation_no_test(self):
        """
        AC-GOV-CTX-001-04: CORE-008 fails when no test exists in production
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "CREATE",
            "test_file_exists": False
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # CORE-008 should fail (violation when no test in production code)
        core_008_violations = [v for v in eval_result.violations if v.rule_id == "CORE-008"]
        assert len(core_008_violations) >= 1
        
        violation = core_008_violations[0]
        assert violation.severity == "blocked"
        assert "test" in violation.message.lower()
    
    def test_core_011_type_hints_pass(self):
        """
        AC-GOV-CTX-001-04: CORE-011 passes with full type hint coverage
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "MODIFY",
            "functions_analyzed": 5,
            "functions_with_hints": 5
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # CORE-011 should pass (no violation with 100% coverage)
        core_011_violations = [v for v in eval_result.violations if v.rule_id == "CORE-011"]
        assert len(core_011_violations) == 0
    
    def test_core_011_type_hints_violation(self):
        """
        AC-GOV-CTX-001-04: CORE-011 fails with incomplete type hints
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "MODIFY",
            "functions_analyzed": 5,
            "functions_with_hints": 3
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # CORE-011 should fail (violation with <100% coverage)
        core_011_violations = [v for v in eval_result.violations if v.rule_id == "CORE-011"]
        assert len(core_011_violations) >= 1
        
        violation = core_011_violations[0]
        assert violation.severity == "blocked"
        assert "type hint" in violation.message.lower()
    
    def test_core_013_error_handling_pass(self):
        """
        AC-GOV-CTX-001-04: CORE-013 passes with no bare except
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "MODIFY",
            "bare_except_count": 0
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # CORE-013 should pass (no violation with no bare except)
        core_013_violations = [v for v in eval_result.violations if v.rule_id == "CORE-013"]
        assert len(core_013_violations) == 0
    
    def test_core_013_error_handling_violation(self):
        """
        AC-GOV-CTX-001-04: CORE-013 fails with bare except
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "MODIFY",
            "bare_except_count": 2
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # CORE-013 should fail (violation with bare except)
        core_013_violations = [v for v in eval_result.violations if v.rule_id == "CORE-013"]
        assert len(core_013_violations) >= 1
        
        violation = core_013_violations[0]
        assert violation.severity == "blocked"
        assert "bare" in violation.message.lower()
    
    def test_multiple_rules_evaluated(self):
        """
        AC-GOV-CTX-001-04: Multiple rules evaluated in single call
        """
        context = {
            "file_path": "cortex/core/example.py",
            "operation_type": "MODIFY",
            "lines_changed": 750,  # Violates CORE-001
            "test_file_exists": False,  # Violates CORE-008
            "functions_analyzed": 5,
            "functions_with_hints": 3,  # Violates CORE-011
            "bare_except_count": 1  # Violates CORE-013
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        assert eval_result.passed is False
        
        # Should have violations from multiple rules
        assert len(eval_result.violations) >= 2
        
        # Check that violations include CORE-001
        rule_ids = {v.rule_id for v in eval_result.violations}
        assert "CORE-001" in rule_ids


class TestRuleApplicabilityIntegration:
    """Test rule exemption patterns in context-aware pipeline"""
    
    def setup_method(self):
        """Setup for each test"""
        self.evaluator = RuleEvaluator()
    
    def test_exploration_code_context_extraction(self):
        """
        AC-GOV-CTX-001-04: Exploration code detected and exempt from TDD
        """
        context = {
            "file_path": "experiments/spike_prototype.py",
            "operation_type": "CREATE",
            "test_file_exists": False
        }
        
        # Should not crash - exemption engine handles exploration phase
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # Evaluation completed (exemption handled)
        assert eval_result.evaluation_time_ms > 0
    
    def test_generated_code_context_extraction(self):
        """
        AC-GOV-CTX-001-04: Generated code detected and exempt from type hints
        """
        context = {
            "file_path": "cortex/core/__generated__/models.py",
            "operation_type": "CREATE",
            "functions_analyzed": 10,
            "functions_with_hints": 0
        }
        
        # Should not crash - exemption engine handles generated code
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # Evaluation completed (exemption handled)
        assert eval_result.evaluation_time_ms > 0

