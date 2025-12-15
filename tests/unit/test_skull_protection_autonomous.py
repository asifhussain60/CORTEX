"""
SKULL Protection Tests for Autonomous Execution (Phase 2)

Verifies Brain Protection Rules are enforced for critical autonomous functionality.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import pytest
import yaml
from pathlib import Path


class TestSKULLProtectionRules:
    """Test suite for SKULL brain protection rules."""

    @pytest.fixture
    def brain_rules(self):
        """Load brain protection rules."""
        rules_path = Path("d:/PROJECTS/CORTEX/cortex-brain/brain-protection-rules.yaml")
        with open(rules_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_autonomous_execution_protection_rule_exists(self, brain_rules):
        """Verifies AUTONOMOUS_EXECUTION_PROTECTION rule is defined."""
        tier0_instincts = brain_rules.get('tier0_instincts', [])
        assert 'AUTONOMOUS_EXECUTION_PROTECTION' in tier0_instincts, \
            "AUTONOMOUS_EXECUTION_PROTECTION must be in tier0_instincts"

    def test_interactive_mode_enforcement_rule_exists(self, brain_rules):
        """Verifies INTERACTIVE_MODE_ENFORCEMENT rule is defined."""
        tier0_instincts = brain_rules.get('tier0_instincts', [])
        assert 'INTERACTIVE_MODE_ENFORCEMENT' in tier0_instincts, \
            "INTERACTIVE_MODE_ENFORCEMENT must be in tier0_instincts"

    def test_token_optimization_enforcement_rule_exists(self, brain_rules):
        """Verifies TOKEN_OPTIMIZATION_ENFORCEMENT rule is defined."""
        tier0_instincts = brain_rules.get('tier0_instincts', [])
        assert 'TOKEN_OPTIMIZATION_ENFORCEMENT' in tier0_instincts, \
            "TOKEN_OPTIMIZATION_ENFORCEMENT must be in tier0_instincts"

    def test_git_checkpoint_phase_protection_rule_exists(self, brain_rules):
        """Verifies GIT_CHECKPOINT_PHASE_PROTECTION rule is defined."""
        tier0_instincts = brain_rules.get('tier0_instincts', [])
        assert 'GIT_CHECKPOINT_PHASE_PROTECTION' in tier0_instincts, \
            "GIT_CHECKPOINT_PHASE_PROTECTION must be in tier0_instincts"

    def test_total_rule_count_updated(self, brain_rules):
        """Verifies total rule count reflects new rules."""
        total_count = brain_rules['rules']['total_count']
        assert total_count >= 61, \
            f"Total count should be at least 61 (57 + 4 new rules), got {total_count}"

    def test_autonomous_execution_protection_detailed(self, brain_rules):
        """Validates detailed AUTONOMOUS_EXECUTION_PROTECTION rule definition."""
        # Find rule in protection_layers
        found_rule = False
        for layer in brain_rules.get('protection_layers', []):
            for rule in layer.get('rules', []):
                if rule.get('rule_id') == 'AUTONOMOUS_EXECUTION_PROTECTION':
                    found_rule = True
                    # Validate structure
                    assert rule['severity'] == 'blocked'
                    assert 'test_requirements' in rule
                    assert rule.get('minimum_coverage') == 100
                    assert 'autonomous execution' in rule['description'].lower()
                    break
            if found_rule:
                break
        
        assert found_rule, "AUTONOMOUS_EXECUTION_PROTECTION detailed rule not found in protection_layers"

    def test_interactive_mode_enforcement_detailed(self, brain_rules):
        """Validates detailed INTERACTIVE_MODE_ENFORCEMENT rule definition."""
        found_rule = False
        for layer in brain_rules.get('protection_layers', []):
            for rule in layer.get('rules', []):
                if rule.get('rule_id') == 'INTERACTIVE_MODE_ENFORCEMENT':
                    found_rule = True
                    assert rule['severity'] == 'blocked'
                    assert 'test_requirements' in rule
                    assert rule.get('minimum_coverage') == 100
                    assert 'interactive' in rule['description'].lower()
                    break
            if found_rule:
                break
        
        assert found_rule, "INTERACTIVE_MODE_ENFORCEMENT detailed rule not found in protection_layers"

    def test_git_checkpoint_protection_detailed(self, brain_rules):
        """Validates detailed GIT_CHECKPOINT_PHASE_PROTECTION rule definition."""
        found_rule = False
        for layer in brain_rules.get('protection_layers', []):
            for rule in layer.get('rules', []):
                if rule.get('rule_id') == 'GIT_CHECKPOINT_PHASE_PROTECTION':
                    found_rule = True
                    assert rule['severity'] == 'blocked'
                    assert 'test_requirements' in rule
                    assert rule.get('minimum_coverage') == 100
                    assert 'checkpoint' in rule['description'].lower()
                    break
            if found_rule:
                break
        
        assert found_rule, "GIT_CHECKPOINT_PHASE_PROTECTION detailed rule not found in protection_layers"


class TestAutonomousExecutionIntegrity:
    """Tests to verify autonomous execution logic remains intact."""

    def test_should_auto_progress_exists(self):
        """Verifies _should_auto_progress method exists."""
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        assert hasattr(PlanningOrchestrator, '_should_auto_progress')

    def test_execute_next_phase_exists(self):
        """Verifies _execute_next_phase method exists."""
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        assert hasattr(PlanningOrchestrator, '_execute_next_phase')

    def test_execution_mode_detector_exists(self):
        """Verifies ExecutionModeDetector class exists."""
        from src.operations.modules.context.execution_mode_detector import ExecutionModeDetector
        assert ExecutionModeDetector is not None

    def test_complete_phase_autonomous_exists(self):
        """Verifies _complete_phase_autonomous method exists."""
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        assert hasattr(PlanningOrchestrator, '_complete_phase_autonomous')

    def test_create_phase_checkpoint_exists(self):
        """Verifies _create_phase_checkpoint method exists."""
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        assert hasattr(PlanningOrchestrator, '_create_phase_checkpoint')


class TestTestCoverageRequirements:
    """Validates test coverage exists for protected functionality."""

    def test_auto_progression_tests_exist(self):
        """Verifies auto-progression logic has test file."""
        test_file = Path("d:/PROJECTS/CORTEX/tests/unit/test_auto_progression_logic.py")
        assert test_file.exists(), "test_auto_progression_logic.py must exist (SKULL requirement)"

    def test_git_checkpoint_tests_exist(self):
        """Verifies git checkpoint integration has test file."""
        test_file = Path("d:/PROJECTS/CORTEX/tests/unit/test_git_checkpoint_integration.py")
        assert test_file.exists(), "test_git_checkpoint_integration.py must exist (SKULL requirement)"

    def test_progress_summaries_tests_exist(self):
        """Verifies progress summaries have test file."""
        test_file = Path("d:/PROJECTS/CORTEX/tests/unit/test_incremental_progress_summaries.py")
        assert test_file.exists(), "test_incremental_progress_summaries.py must exist (SKULL requirement)"

    def test_autonomous_flow_integration_tests_exist(self):
        """Verifies autonomous flow integration tests exist."""
        test_file = Path("d:/PROJECTS/CORTEX/tests/integration/test_autonomous_execution_flow.py")
        assert test_file.exists(), "test_autonomous_execution_flow.py must exist (SKULL requirement)"

    def test_minimum_test_count(self):
        """Verifies minimum test count for autonomous execution."""
        import subprocess
        result = subprocess.run(
            [
                "python", "-m", "pytest",
                "tests/unit/test_auto_progression_logic.py",
                "tests/unit/test_incremental_progress_summaries.py",
                "tests/integration/test_autonomous_execution_flow.py",
                "tests/unit/test_git_checkpoint_integration.py",
                "--collect-only", "-q"
            ],
            capture_output=True,
            text=True,
            cwd="d:/PROJECTS/CORTEX"
        )
        
        # Extract test count from output
        output = result.stdout
        # Look for pattern like "50 tests collected"
        import re
        match = re.search(r'(\d+) tests? collected', output)
        if match:
            test_count = int(match.group(1))
            assert test_count >= 50, \
                f"Minimum 50 tests required for autonomous execution, found {test_count}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
