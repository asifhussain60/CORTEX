"""
CORTEX Tier 0: Governance Engine Tests
Unit tests for governance rule enforcement.
"""

import pytest
from pathlib import Path
from datetime import datetime
from CORTEX.src.tier0.governance_engine import (
    GovernanceEngine,
    Severity,
    ViolationType
)


@pytest.fixture
def governance_engine():
    """Create a governance engine instance for testing."""
    # Use the actual governance.yaml file
    governance_file = Path(__file__).parent.parent.parent / "src" / "tier0" / "governance.yaml"
    return GovernanceEngine(governance_file)


class TestGovernanceEngineInitialization:
    """Test governance engine initialization and loading."""
    
    def test_loads_governance_file_successfully(self, governance_engine):
        """Test that governance.yaml loads without errors."""
        assert governance_engine.rules is not None
        assert len(governance_engine.rules) > 0
    
    def test_indexes_rules_by_id(self, governance_engine):
        """Test that rules are indexed by their ID."""
        assert 'TEST_FIRST_TDD' in governance_engine.rules
        assert 'DEFINITION_OF_DONE' in governance_engine.rules
        assert 'TIER_BOUNDARIES' in governance_engine.rules
    
    def test_loads_expected_rule_count(self, governance_engine):
        """Test that all 23 governance rules are loaded."""
        assert len(governance_engine.rules) == 23
    
    def test_raises_error_for_missing_file(self):
        """Test that FileNotFoundError is raised for missing governance file."""
        with pytest.raises(FileNotFoundError):
            GovernanceEngine(Path("/nonexistent/governance.yaml"))


class TestTDDEnforcement:
    """Test TDD (Test-First Development) rule enforcement."""
    
    def test_blocks_implementation_without_test(self, governance_engine):
        """Test that implementing code without a test is BLOCKED."""
        violation = governance_engine.check_tdd_violation(
            has_new_code=True,
            has_new_test=False,
            test_written_first=False
        )
        
        assert violation is not None
        assert violation['rule_id'] == 'TEST_FIRST_TDD'
        assert violation['action'] == 'BLOCKED'
        assert violation['violation_type'] == ViolationType.TDD_IMPLEMENTATION_WITHOUT_TEST.value
    
    def test_challenges_test_written_after_code(self, governance_engine):
        """Test that writing test after code is CHALLENGED."""
        violation = governance_engine.check_tdd_violation(
            has_new_code=True,
            has_new_test=True,
            test_written_first=False
        )
        
        assert violation is not None
        assert violation['rule_id'] == 'TEST_FIRST_TDD'
        assert violation['action'] == 'CHALLENGED'
        assert violation['violation_type'] == ViolationType.TDD_SKIPPING_RED_PHASE.value
    
    def test_allows_test_first_development(self, governance_engine):
        """Test that proper TDD (test-first) is allowed."""
        violation = governance_engine.check_tdd_violation(
            has_new_code=True,
            has_new_test=True,
            test_written_first=True
        )
        
        assert violation is None
    
    def test_logs_tdd_violations(self, governance_engine):
        """Test that TDD violations are logged."""
        governance_engine.clear_violations()
        
        governance_engine.check_tdd_violation(
            has_new_code=True,
            has_new_test=False,
            test_written_first=False
        )
        
        violations = governance_engine.get_violations()
        assert len(violations) == 1
        assert violations[0]['rule_id'] == 'TEST_FIRST_TDD'


class TestDefinitionOfDone:
    """Test Definition of Done validation."""
    
    def test_validates_all_criteria_met(self, governance_engine):
        """Test that DoD passes when all criteria are met."""
        result = governance_engine.validate_definition_of_done(
            compilation_clean=True,
            tests_pass=True,
            new_tests_created=True,
            tdd_cycle_complete=True,
            code_formatted=True,
            no_lint_violations=True,
            docs_updated=True,
            app_runs=True,
            no_exceptions=True,
            functionality_verified=True
        )
        
        assert result['valid'] is True
        assert len(result['failed_criteria']) == 0
        assert 'violation' not in result
    
    def test_blocks_when_criteria_not_met(self, governance_engine):
        """Test that DoD blocks when criteria fail."""
        result = governance_engine.validate_definition_of_done(
            compilation_clean=False,
            tests_pass=False,
            new_tests_created=True,
            tdd_cycle_complete=True,
            code_formatted=True,
            no_lint_violations=True,
            docs_updated=True,
            app_runs=True,
            no_exceptions=True,
            functionality_verified=True
        )
        
        assert result['valid'] is False
        assert 'compilation' in result['failed_criteria']
        assert 'tests_pass' in result['failed_criteria']
        assert 'violation' in result
        assert result['violation']['action'] == 'BLOCKED'
    
    def test_identifies_specific_failed_criteria(self, governance_engine):
        """Test that specific failed criteria are identified."""
        result = governance_engine.validate_definition_of_done(
            compilation_clean=True,
            tests_pass=True,
            new_tests_created=False,
            tdd_cycle_complete=False,
            code_formatted=False,
            no_lint_violations=True,
            docs_updated=True,
            app_runs=True,
            no_exceptions=True,
            functionality_verified=True
        )
        
        assert result['valid'] is False
        assert 'new_tests_created' in result['failed_criteria']
        assert 'tdd_cycle_complete' in result['failed_criteria']
        assert 'code_formatted' in result['failed_criteria']


class TestDefinitionOfReady:
    """Test Definition of Ready validation."""
    
    def test_validates_all_criteria_met(self, governance_engine):
        """Test that DoR passes when all criteria are met."""
        result = governance_engine.validate_definition_of_ready(
            user_story_clear=True,
            acceptance_criteria_defined=True,
            testable_outcomes=True,
            scope_bounded=True,
            dependencies_identified=True,
            estimate_possible=True,
            files_known=True,
            architecture_clear=True,
            no_blocking_dependencies=True
        )
        
        assert result['valid'] is True
        assert len(result['failed_criteria']) == 0
    
    def test_blocks_work_when_not_ready(self, governance_engine):
        """Test that DoR blocks work when criteria fail."""
        result = governance_engine.validate_definition_of_ready(
            user_story_clear=False,
            acceptance_criteria_defined=False,
            testable_outcomes=True,
            scope_bounded=True,
            dependencies_identified=True,
            estimate_possible=True,
            files_known=True,
            architecture_clear=True,
            no_blocking_dependencies=True
        )
        
        assert result['valid'] is False
        assert 'user_story_clear' in result['failed_criteria']
        assert 'acceptance_criteria_defined' in result['failed_criteria']


class TestTierBoundaryProtection:
    """Test tier boundary violation detection."""
    
    def test_detects_conversation_data_in_tier_0(self, governance_engine):
        """Test that conversations in Tier 0 are detected as violations."""
        violation = governance_engine.check_tier_boundary_violation(
            tier=0,
            data_type='conversations'
        )
        
        assert violation is not None
        assert violation['rule_id'] == 'TIER_BOUNDARIES'
        assert violation['action'] == 'CHALLENGED'
        assert violation['details']['tier'] == 0
        assert violation['details']['data_type'] == 'conversations'
    
    def test_detects_governance_in_tier_1(self, governance_engine):
        """Test that governance rules in Tier 1 are detected as violations."""
        violation = governance_engine.check_tier_boundary_violation(
            tier=1,
            data_type='governance'
        )
        
        assert violation is not None
        assert violation['rule_id'] == 'TIER_BOUNDARIES'
    
    def test_allows_correct_tier_data(self, governance_engine):
        """Test that data in correct tier is allowed."""
        violation = governance_engine.check_tier_boundary_violation(
            tier=0,
            data_type='governance'
        )
        
        assert violation is None
    
    def test_detects_patterns_in_tier_1(self, governance_engine):
        """Test that patterns in Tier 1 (should be Tier 2) are detected."""
        violation = governance_engine.check_tier_boundary_violation(
            tier=1,
            data_type='patterns'
        )
        
        assert violation is not None


class TestChallengeProtocol:
    """Test challenge creation for risky changes."""
    
    def test_creates_challenge_with_risks(self, governance_engine):
        """Test that challenges are created with identified risks."""
        challenge = governance_engine.create_challenge(
            proposed_change="Disable TDD for this feature",
            risks=[
                "May degrade code quality",
                "Violates CORTEX principles",
                "No safety net for changes"
            ],
            alternatives=[
                "Write tests incrementally",
                "Use temporary feature flag with tests"
            ]
        )
        
        assert challenge['rule_id'] == 'CHALLENGE_USER_CHANGES'
        assert challenge['proposed_change'] == "Disable TDD for this feature"
        assert len(challenge['risks_identified']) == 3
        assert len(challenge['alternatives']) == 2
        assert challenge['requires_explicit_override'] is True
    
    def test_challenge_includes_timestamp(self, governance_engine):
        """Test that challenges include timestamp."""
        challenge = governance_engine.create_challenge(
            proposed_change="Merge Tier 0 and Tier 1",
            risks=["Violates tier boundaries"]
        )
        
        assert 'challenge_timestamp' in challenge
        # Verify timestamp is recent (within last minute)
        timestamp = datetime.fromisoformat(challenge['challenge_timestamp'])
        assert (datetime.now() - timestamp).total_seconds() < 60


class TestRuleRetrieval:
    """Test rule retrieval and querying."""
    
    def test_gets_rule_by_id(self, governance_engine):
        """Test retrieving specific rule by ID."""
        rule = governance_engine.get_rule('TEST_FIRST_TDD')
        
        assert rule is not None
        assert rule['id'] == 'TEST_FIRST_TDD'
        assert rule['severity'] == 'CRITICAL'
        assert rule['category'] == 'quality'
    
    def test_returns_none_for_unknown_rule(self, governance_engine):
        """Test that unknown rule ID returns None."""
        rule = governance_engine.get_rule('NONEXISTENT_RULE')
        assert rule is None
    
    def test_gets_all_rules(self, governance_engine):
        """Test retrieving all rules."""
        rules = governance_engine.get_all_rules()
        assert len(rules) == 23
    
    def test_filters_rules_by_severity(self, governance_engine):
        """Test filtering rules by severity level."""
        critical_rules = governance_engine.get_rules_by_severity(Severity.CRITICAL)
        
        assert len(critical_rules) > 0
        for rule in critical_rules:
            assert rule['severity'] == 'CRITICAL'


class TestViolationLogging:
    """Test violation logging and retrieval."""
    
    def test_logs_violations(self, governance_engine):
        """Test that violations are logged."""
        governance_engine.clear_violations()
        
        governance_engine.check_tdd_violation(
            has_new_code=True,
            has_new_test=False,
            test_written_first=False
        )
        
        governance_engine.validate_definition_of_done(
            compilation_clean=False,
            tests_pass=False
        )
        
        violations = governance_engine.get_violations()
        assert len(violations) == 2
    
    def test_filters_violations_by_severity(self, governance_engine):
        """Test filtering violations by severity."""
        governance_engine.clear_violations()
        
        # Create CRITICAL violation
        governance_engine.check_tdd_violation(
            has_new_code=True,
            has_new_test=False,
            test_written_first=False
        )
        
        critical_violations = governance_engine.get_violations(
            severity=Severity.CRITICAL
        )
        
        assert len(critical_violations) >= 1
        for violation in critical_violations:
            assert violation['severity'] == 'CRITICAL'
    
    def test_limits_violation_results(self, governance_engine):
        """Test limiting number of violations returned."""
        governance_engine.clear_violations()
        
        # Create multiple violations
        for _ in range(5):
            governance_engine.check_tdd_violation(
                has_new_code=True,
                has_new_test=False,
                test_written_first=False
            )
        
        violations = governance_engine.get_violations(limit=3)
        assert len(violations) == 3
    
    def test_clears_violations(self, governance_engine):
        """Test clearing violation log."""
        governance_engine.check_tdd_violation(
            has_new_code=True,
            has_new_test=False,
            test_written_first=False
        )
        
        governance_engine.clear_violations()
        violations = governance_engine.get_violations()
        
        assert len(violations) == 0
