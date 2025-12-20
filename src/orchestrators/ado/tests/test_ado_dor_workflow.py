"""
Test Suite: ADO Orchestrator DoR (Definition of Ready) Workflow

Tests the VALIDATION phase implementation of ADO Orchestrator:
- DoR prompt generation for interactive refinement
- Field collection (acceptance criteria, assumptions, constraints)
- User feedback loop integration
- DoR completion validation
- Phase transition to GENERATION

Part of: Week 10 Day 2 AM - Task 3 (Interactive DoR Workflow)
TDD Phase: RED (Write failing tests first)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.ado.ado_orchestrator import ADOOrchestrator, ADOPhase, ADOResult


class TestADODoRWorkflow(unittest.TestCase):
    """Test suite for ADO Orchestrator VALIDATION phase (DoR workflow)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "name": "ADOOrchestrator",
            "version": "1.0.0",
            "workspace_root": "/test/workspace"
        }
    
    def test_validation_phase_generates_dor_prompts(self):
        """
        Test: VALIDATION phase should generate DoR prompts for user
        
        Validates that the orchestrator generates structured DoR prompts
        asking for acceptance criteria, assumptions, and constraints.
        
        Expected behavior:
        - DoR prompts include acceptance criteria request
        - DoR prompts include assumptions/constraints request
        - Prompts are clear and actionable
        - Prompts stored in result data for reference
        """
        orchestrator = ADOOrchestrator(self.config)
        result = orchestrator.execute(
            feature="User Authentication",
            test_mode=True,
            auto_approve=True
        )
        
        self.assertTrue(result.success)
        # DoR data should be present
        self.assertIn("dor", result.data)
        dor_data = result.data["dor"]
        
        # DoR prompts should be generated
        self.assertIn("prompts", dor_data)
        prompts = dor_data["prompts"]
        
        # Should have prompts for AC, assumptions, constraints
        self.assertIsInstance(prompts, dict)
        self.assertIn("acceptance_criteria", prompts)
        self.assertIn("assumptions", prompts)
        self.assertIn("constraints", prompts)
    
    def test_validation_phase_collects_acceptance_criteria(self):
        """
        Test: VALIDATION phase should collect acceptance criteria
        
        Validates that the orchestrator collects and stores acceptance
        criteria from user input during DoR refinement.
        
        Expected behavior:
        - Acceptance criteria can be provided as list of strings
        - Empty/missing AC triggers warning
        - AC stored in DoR data for work item generation
        - Given/When/Then format encouraged but not enforced
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Simulate with acceptance criteria
        result_with_ac = orchestrator.execute(
            feature="User Authentication",
            test_mode=True,
            auto_approve=True,
            acceptance_criteria=[
                "Given user enters valid credentials, When login submitted, Then user redirected to dashboard",
                "Given user enters invalid credentials, When login submitted, Then error message shown"
            ]
        )
        
        self.assertTrue(result_with_ac.success)
        dor_data = result_with_ac.data["dor"]
        
        # AC should be stored
        self.assertIn("acceptance_criteria", dor_data)
        self.assertIsInstance(dor_data["acceptance_criteria"], list)
        self.assertEqual(len(dor_data["acceptance_criteria"]), 2)
    
    def test_validation_phase_collects_assumptions(self):
        """
        Test: VALIDATION phase should collect assumptions
        
        Validates that assumptions (things taken for granted) are collected
        and stored for risk tracking.
        
        Expected behavior:
        - Assumptions provided as list of strings
        - Missing assumptions generates prompt reminder
        - Assumptions stored in DoR data
        - High number of assumptions (>5) triggers warning
        """
        orchestrator = ADOOrchestrator(self.config)
        
        result = orchestrator.execute(
            feature="User Authentication",
            test_mode=True,
            auto_approve=True,
            assumptions=[
                "OAuth provider (e.g., Azure AD) is available",
                "SSL certificates are configured",
                "User database schema exists"
            ]
        )
        
        self.assertTrue(result.success)
        dor_data = result.data["dor"]
        
        # Assumptions should be stored
        self.assertIn("assumptions", dor_data)
        self.assertIsInstance(dor_data["assumptions"], list)
        self.assertEqual(len(dor_data["assumptions"]), 3)
    
    def test_validation_phase_collects_constraints(self):
        """
        Test: VALIDATION phase should collect constraints
        
        Validates that constraints (limitations/boundaries) are collected
        and considered in planning.
        
        Expected behavior:
        - Constraints provided as list of strings
        - Missing constraints allowed (optional)
        - Constraints stored in DoR data
        - Examples: timeline, resources, technology, compliance
        """
        orchestrator = ADOOrchestrator(self.config)
        
        result = orchestrator.execute(
            feature="User Authentication",
            test_mode=True,
            auto_approve=True,
            constraints=[
                "Must complete within 2 sprints",
                "Cannot modify existing database schema",
                "Must comply with GDPR"
            ]
        )
        
        self.assertTrue(result.success)
        dor_data = result.data["dor"]
        
        # Constraints should be stored
        self.assertIn("constraints", dor_data)
        self.assertIsInstance(dor_data["constraints"], list)
        self.assertEqual(len(dor_data["constraints"]), 3)
    
    def test_validation_phase_validates_dor_completeness(self):
        """
        Test: VALIDATION phase should validate DoR completeness
        
        Validates that the orchestrator checks if DoR is complete enough
        to proceed to work item generation.
        
        Expected behavior:
        - Minimum requirement: at least 1 acceptance criterion
        - Warns if assumptions missing (not blocking)
        - Warns if constraints missing (not blocking)
        - DoR completeness percentage calculated
        - Complete DoR enables phase transition to GENERATION
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Complete DoR
        result_complete = orchestrator.execute(
            feature="User Authentication",
            test_mode=True,
            auto_approve=True,
            acceptance_criteria=["AC1", "AC2"],
            assumptions=["Assumption1"],
            constraints=["Constraint1"]
        )
        
        self.assertTrue(result_complete.success)
        dor_data = result_complete.data["dor"]
        
        # DoR validation should be present
        self.assertIn("is_complete", dor_data)
        self.assertTrue(dor_data["is_complete"])
        
        # Should have completeness percentage
        self.assertIn("completeness_percentage", dor_data)
        self.assertGreaterEqual(dor_data["completeness_percentage"], 75)
    
    def test_validation_phase_handles_incomplete_dor(self):
        """
        Test: VALIDATION phase should handle incomplete DoR gracefully
        
        Validates that missing DoR fields trigger warnings but don't block
        execution in test mode (allow iteration).
        
        Expected behavior:
        - Missing AC triggers warning
        - Missing assumptions triggers info message
        - Missing constraints triggers info message
        - Execution continues with warnings
        - DoR marked as incomplete
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Minimal DoR (no AC, assumptions, constraints)
        result_incomplete = orchestrator.execute(
            feature="User Authentication",
            test_mode=True,
            auto_approve=True
        )
        
        self.assertTrue(result_incomplete.success)
        
        # Should have warnings about incomplete DoR
        self.assertTrue(len(result_incomplete.warnings) > 0)
        
        # DoR should be marked incomplete
        dor_data = result_incomplete.data["dor"]
        self.assertFalse(dor_data["is_complete"])
        self.assertLess(dor_data["completeness_percentage"], 50)
    
    def test_validation_phase_transitions_to_generation(self):
        """
        Test: VALIDATION phase should transition to GENERATION
        
        Validates phase transition after DoR workflow completes.
        
        Expected behavior:
        - Phase transition logged with 🎭 engagement hint
        - Current phase moves from VALIDATION to GENERATION
        - DoR data carried forward to GENERATION phase
        - Transition happens regardless of DoR completeness (warnings added)
        """
        orchestrator = ADOOrchestrator(self.config)
        
        result = orchestrator.execute(
            feature="User Authentication",
            test_mode=True,
            auto_approve=True,
            acceptance_criteria=["AC1"]
        )
        
        self.assertTrue(result.success)
        
        # Should have transitioned through VALIDATION phase
        validation_transition = any(
            "VALIDATION" in log and "🎭" in log
            for log in result.logs
        )
        self.assertTrue(validation_transition, "VALIDATION phase transition should be logged")
        
        # Should eventually reach COMPLETION
        self.assertEqual(result.phase, ADOPhase.COMPLETION)


if __name__ == "__main__":
    unittest.main()
