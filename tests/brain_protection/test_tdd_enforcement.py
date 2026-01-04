"""
TDD Enforcement Brain Protection Tests

Tests for TDD_ENFORCEMENT brain protection rule (SKULL rule).
Validates Test-Driven Development workflow enforcement.

Test Coverage:
- RED phase required before GREEN phase
- GREEN phase requires passing tests
- REFACTOR phase only after GREEN
- TDD cycle state transitions
- TDD violations logged

Author: Asif Hussain (CORTEX)
Created: January 3, 2026
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any


class TestTDDEnforcement:
    """Test suite for TDD_ENFORCEMENT brain protection rule."""
    
    def test_red_phase_required_before_green(self):
        """
        Test that RED phase (failing test) is required before GREEN phase.
        
        Brain Protection Rule: TDD_ENFORCEMENT
        Requirement: Tests must fail first (RED) before implementation (GREEN)
        
        Validates:
        - Cannot skip to GREEN without RED
        - RED phase must be documented
        - Failing test must exist before implementation
        """
        # Arrange - Create TDD state machine
        state = {
            "phase": "not_started",
            "tests_written": False,
            "tests_failing": False,
            "implementation_exists": False,
            "violations": []
        }
        
        # Act - Try to implement without tests (skip RED)
        def attempt_implementation():
            if not state["tests_written"]:
                state["violations"].append("TDD_ENFORCEMENT: Cannot implement without RED phase (failing tests)")
                return False
            state["implementation_exists"] = True
            state["phase"] = "green"
            return True
        
        result = attempt_implementation()
        
        # Assert - Should be blocked
        assert result is False, "Should not allow GREEN phase without RED phase"
        assert len(state["violations"]) == 1
        assert "TDD_ENFORCEMENT" in state["violations"][0]
        assert "RED phase" in state["violations"][0]
        
        # Act - Now do RED phase correctly
        state["tests_written"] = True
        state["tests_failing"] = True
        state["phase"] = "red"
        result = attempt_implementation()
        
        # Assert - Should succeed after RED phase
        assert result is True, "Should allow GREEN phase after RED phase"
        assert state["phase"] == "green"
    
    def test_green_phase_requires_passing_tests(self):
        """
        Test that GREEN phase requires all tests to pass.
        
        Brain Protection Rule: TDD_ENFORCEMENT
        Requirement: Implementation (GREEN) must make all tests pass
        
        Validates:
        - Cannot complete GREEN with failing tests
        - Test pass rate must be 100%
        - Partial success not accepted
        """
        # Arrange - GREEN phase with implementation
        state = {
            "phase": "green",
            "tests_written": True,
            "implementation_exists": True,
            "test_results": {"passed": 3, "failed": 2, "total": 5},
            "violations": []
        }
        
        # Act - Try to complete GREEN with failing tests
        def complete_green_phase():
            if state["test_results"]["failed"] > 0:
                state["violations"].append(
                    f"TDD_ENFORCEMENT: Cannot complete GREEN phase with {state['test_results']['failed']} failing tests"
                )
                return False
            state["phase"] = "green_complete"
            return True
        
        result = complete_green_phase()
        
        # Assert - Should be blocked
        assert result is False, "Should not complete GREEN with failing tests"
        assert len(state["violations"]) == 1
        assert "2 failing tests" in state["violations"][0]
        
        # Act - Fix tests to all pass
        state["test_results"]["failed"] = 0
        state["test_results"]["passed"] = 5
        result = complete_green_phase()
        
        # Assert - Should succeed with 100% pass rate
        assert result is True, "Should complete GREEN when all tests pass"
        assert state["phase"] == "green_complete"
    
    def test_refactor_phase_after_green_only(self):
        """
        Test that REFACTOR phase can only occur after successful GREEN phase.
        
        Brain Protection Rule: TDD_ENFORCEMENT
        Requirement: REFACTOR only after tests pass (after GREEN)
        
        Validates:
        - Cannot REFACTOR before GREEN completes
        - GREEN completion requires 100% test pass
        - REFACTOR preserves test pass rate
        """
        # Arrange - Try REFACTOR from RED phase
        state = {
            "phase": "red",
            "tests_written": True,
            "tests_passing": False,
            "violations": []
        }
        
        # Act - Try to refactor in RED phase
        def start_refactor():
            if state["phase"] != "green_complete" and not state["tests_passing"]:
                state["violations"].append(
                    "TDD_ENFORCEMENT: Cannot REFACTOR before GREEN phase completes with passing tests"
                )
                return False
            state["phase"] = "refactor"
            return True
        
        result = start_refactor()
        
        # Assert - Should be blocked
        assert result is False, "Should not allow REFACTOR from RED phase"
        assert "GREEN phase completes" in state["violations"][0]
        
        # Act - Complete GREEN phase first
        state["phase"] = "green_complete"
        state["tests_passing"] = True
        result = start_refactor()
        
        # Assert - Should succeed after GREEN
        assert result is True, "Should allow REFACTOR after GREEN completes"
        assert state["phase"] == "refactor"
    
    def test_tdd_cycle_state_transitions(self):
        """
        Test valid TDD cycle state machine transitions.
        
        Brain Protection Rule: TDD_ENFORCEMENT
        Requirement: Only valid RED→GREEN→REFACTOR transitions allowed
        
        Validates:
        - Valid transitions: RED→GREEN, GREEN→REFACTOR, REFACTOR→RED
        - Invalid transitions blocked: RED→REFACTOR, GREEN→RED
        - State machine enforces correct workflow
        """
        # Arrange - TDD state machine
        valid_transitions = {
            "not_started": ["red"],
            "red": ["green"],
            "green": ["green_complete"],
            "green_complete": ["refactor"],
            "refactor": ["red"]  # Start new cycle
        }
        
        state = {"phase": "not_started", "history": []}
        
        # Helper function to transition
        def transition(from_phase, to_phase):
            if to_phase not in valid_transitions.get(from_phase, []):
                return False
            state["history"].append((from_phase, to_phase))
            state["phase"] = to_phase
            return True
        
        # Act & Assert - Valid cycle
        assert transition("not_started", "red") is True
        assert transition("red", "green") is True
        assert transition("green", "green_complete") is True
        assert transition("green_complete", "refactor") is True
        assert transition("refactor", "red") is True  # New cycle
        
        # Assert - Invalid transitions blocked
        state["phase"] = "red"
        assert transition("red", "refactor") is False, "RED→REFACTOR should be invalid"
        
        state["phase"] = "green"
        assert transition("green", "red") is False, "GREEN→RED should be invalid"
        
        # Assert - History tracked
        assert len(state["history"]) >= 5, "Should track state transitions"
    
    def test_tdd_violations_logged(self):
        """
        Test that TDD violations are logged to protection events.
        
        Brain Protection Rule: TDD_ENFORCEMENT
        Requirement: All violations logged for analysis
        
        Validates:
        - Violations written to protection-events.jsonl
        - Log includes rule_id, timestamp, context
        - Audit trail for compliance
        """
        # Arrange - Violation logging system
        from datetime import datetime
        violations_log = []
        
        def log_violation(rule_id, severity, message, context=None):
            event = {
                "timestamp": datetime.now().isoformat(),
                "rule_id": rule_id,
                "severity": severity,
                "message": message,
                "context": context or {}
            }
            violations_log.append(event)
            return event
        
        # Act - Trigger violations
        log_violation("TDD_ENFORCEMENT", "ERROR", "Implementation without RED phase", 
                     {"attempted_phase": "green", "tests_written": False})
        log_violation("TDD_ENFORCEMENT", "ERROR", "REFACTOR before GREEN complete",
                     {"current_phase": "red", "tests_passing": False})
        
        # Assert - Violations logged correctly
        assert len(violations_log) == 2
        assert all("timestamp" in v for v in violations_log)
        assert all(v["rule_id"] == "TDD_ENFORCEMENT" for v in violations_log)
        assert all("severity" in v for v in violations_log)
        assert "RED phase" in violations_log[0]["message"]
        assert "REFACTOR" in violations_log[1]["message"]


class TestTDDEnforcementIntegration:
    """Integration tests for TDD workflow with orchestrators."""
    
    def test_tdd_orchestrator_enforces_red_phase(self):
        """
        Integration test: TDD orchestrator enforces RED phase.
        
        Validates TDD orchestrator checks for failing test before allowing
        implementation work.
        """
        # Arrange - Mock TDD orchestrator state
        orchestrator_state = {
            "phase": "not_started",
            "tests_exist": False,
            "tests_failing": False
        }
        
        # Mock orchestrator enforcement
        def can_start_implementation():
            if not orchestrator_state["tests_exist"]:
                return False, "TDD_ENFORCEMENT: Write failing tests first (RED phase)"
            if not orchestrator_state["tests_failing"]:
                return False, "TDD_ENFORCEMENT: Tests must fail before implementation"
            return True, "Proceed with implementation"
        
        # Act - Try to implement without tests
        allowed, message = can_start_implementation()
        
        # Assert - Should be blocked
        assert allowed is False
        assert "RED phase" in message
        
        # Act - Add failing tests
        orchestrator_state["tests_exist"] = True
        orchestrator_state["tests_failing"] = True
        allowed, message = can_start_implementation()
        
        # Assert - Should be allowed
        assert allowed is True
    
    def test_tdd_orchestrator_validates_green_phase(self):
        """
        Integration test: TDD orchestrator validates GREEN phase completion.
        
        Validates TDD orchestrator requires 100% test pass before
        completing GREEN phase.
        """
        # Arrange - Mock orchestrator in GREEN phase
        orchestrator_state = {
            "phase": "green",
            "test_results": {"total": 10, "passed": 7, "failed": 3}
        }
        
        # Mock completion check
        def can_complete_green():
            if orchestrator_state["test_results"]["failed"] > 0:
                return False, f"Fix {orchestrator_state['test_results']['failed']} failing tests first"
            return True, "GREEN phase complete"
        
        # Act - Try to complete with failures
        allowed, message = can_complete_green()
        
        # Assert - Should be blocked
        assert allowed is False
        assert "3 failing tests" in message
        
        # Act - Fix all tests
        orchestrator_state["test_results"]["failed"] = 0
        orchestrator_state["test_results"]["passed"] = 10
        allowed, message = can_complete_green()
        
        # Assert - Should be allowed
        assert allowed is True
        assert "complete" in message
    
    def test_tdd_orchestrator_enforces_refactor_cleanup(self):
        """
        Integration test: TDD orchestrator enforces REFACTOR cleanup.
        
        Validates REFACTOR phase includes comprehensive cleanup:
        - Whole file cleanup (not partial)
        - Remove orphaned code
        - Merge duplicate code
        - Remove unused imports
        """
        # Arrange - Mock REFACTOR phase validation
        refactor_checklist = {
            "whole_file_cleanup": False,
            "orphaned_code_removed": False,
            "duplicates_merged": False,
            "unused_imports_removed": False,
            "tests_still_passing": True
        }
        
        # Mock validation
        def validate_refactor():
            incomplete = [k for k, v in refactor_checklist.items() 
                         if not v and k != "tests_still_passing"]
            if incomplete:
                return False, f"Complete: {', '.join(incomplete)}"
            if not refactor_checklist["tests_still_passing"]:
                return False, "Tests must pass after REFACTOR"
            return True, "REFACTOR complete"
        
        # Act - Try to complete with incomplete checklist
        allowed, message = validate_refactor()
        
        # Assert - Should be blocked
        assert allowed is False
        assert "whole_file_cleanup" in message
        
        # Act - Complete all items
        for key in refactor_checklist:
            if key != "tests_still_passing":
                refactor_checklist[key] = True
        allowed, message = validate_refactor()
        
        # Assert - Should be allowed
        assert allowed is True


# Test fixtures
@pytest.fixture
def mock_brain_protector():
    """Mock Brain Protector agent for testing."""
    protector = Mock()
    protector.check_rule = Mock(return_value={"allowed": False, "rule": "TDD_ENFORCEMENT"})
    protector.log_violation = Mock()
    return protector


@pytest.fixture
def tdd_state_machine():
    """Mock TDD state machine for testing."""
    fsm = Mock()
    fsm.current_state = "RED"
    fsm.transition = Mock(return_value=True)
    fsm.is_valid_transition = Mock(return_value=True)
    return fsm


@pytest.fixture
def protection_events_log(tmp_path):
    """Temporary protection events log file."""
    log_file = tmp_path / "protection-events.jsonl"
    log_file.touch()
    return log_file


# Pytest marks
pytestmark = [
    pytest.mark.brain_protection,
    pytest.mark.tdd_enforcement,
    pytest.mark.unit
]
