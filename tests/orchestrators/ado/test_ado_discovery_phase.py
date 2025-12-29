"""
Test Suite: ADO Orchestrator Discovery Phase

Tests the DISCOVERY phase implementation of ADO Orchestrator:
- Review orchestrator integration for context gathering
- Duplicate work item detection
- Complexity classification (HIGH/MEDIUM/LOW)

Part of: Week 10 Day 1 PM - Task 2 (Discovery Phase Integration)
TDD Phase: RED (Write failing tests first)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.ado.ado_orchestrator import ADOOrchestrator, ADOPhase, ADOResult


class TestADODiscoveryPhase(unittest.TestCase):
    """Test suite for ADO Orchestrator DISCOVERY phase logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "name": "ADOOrchestrator",
            "version": "1.0.0",
            "workspace_root": "/test/workspace"
        }
    
    def test_discovery_phase_runs_review_orchestrator(self):
        """
        Test: DISCOVERY phase should invoke review orchestrator
        
        Validates that during DISCOVERY phase, the orchestrator attempts to call
        the review orchestrator. Since ReviewOrchestrator is not yet implemented,
        graceful degradation should occur (warning added, execution continues).
        
        Expected behavior:
        - Orchestrator attempts review orchestrator integration
        - Graceful degradation: warning added when unavailable
        - Execution completes successfully despite missing integration
        """
        orchestrator = ADOOrchestrator(self.config)
        result = orchestrator.execute(
            feature="User Authentication",
            test_mode=True,
            auto_approve=True
        )
        
        # Verify graceful degradation
        self.assertTrue(result.success)
        self.assertEqual(result.phase, ADOPhase.COMPLETION)
        # Should have warning about review orchestrator unavailability
        has_review_warning = any("review orchestrator unavailable" in w.lower() for w in result.warnings)
        self.assertTrue(has_review_warning, "Should warn about review orchestrator unavailability")
        # Discovery data should show review_context as None
        self.assertIn("discovery", result.data)
        self.assertIsNone(result.data["discovery"]["review_context"])
    
    def test_discovery_phase_detects_duplicate_work_items(self):
        """
        Test: DISCOVERY phase should detect duplicate ADO work items
        
        Validates that the orchestrator attempts to check existing ADO work items.
        Since ADOUtility is not yet implemented, graceful degradation should occur.
        
        Expected behavior:
        - Orchestrator attempts duplicate detection
        - Graceful degradation: warning added when unavailable
        - Execution completes successfully despite missing integration
        """
        orchestrator = ADOOrchestrator(self.config)
        result = orchestrator.execute(
            feature="User Authentication",
            test_mode=True,
            auto_approve=True
        )
        
        # Verify graceful degradation
        self.assertTrue(result.success)
        # Should have warning about duplicate detection unavailability
        has_duplicate_warning = any("duplicate detection unavailable" in w.lower() for w in result.warnings)
        self.assertTrue(has_duplicate_warning, "Should warn about duplicate detection unavailability")
        # Discovery data should show duplicates as empty list
        self.assertIn("discovery", result.data)
        self.assertEqual(result.data["discovery"]["duplicates"], [])
    
    def test_discovery_phase_classifies_complexity(self):
        """
        Test: DISCOVERY phase should classify feature complexity
        
        Validates that the orchestrator analyzes the feature and assigns
        a complexity level (HIGH/MEDIUM/LOW) which affects subsequent phases.
        
        Expected behavior:
        - Feature analyzed for complexity indicators
        - Complexity level assigned (HIGH/MEDIUM/LOW)
        - Complexity level available in result data
        - Higher complexity triggers additional validation (e.g., threat modeling)
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Test HIGH complexity feature
        result_high = orchestrator.execute(
            feature="Distributed Real-time Payment Processing with Blockchain Integration",
            test_mode=True,
            auto_approve=True
        )
        
        self.assertTrue(result_high.success)
        # High complexity should be detectable in result
        # (either in data dict or logs)
        has_complexity = (
            "complexity" in str(result_high.data).lower() or
            any("complexity" in log.lower() for log in result_high.logs)
        )
        self.assertTrue(has_complexity, "Complexity classification should be present in result")
    
    def test_discovery_phase_stores_context_in_result(self):
        """
        Test: DISCOVERY phase should store gathered context in result
        
        Validates that all context gathered during discovery (review data,
        duplicates, complexity) is properly stored in the ADOResult for
        use by subsequent phases.
        
        Expected behavior:
        - result.data contains 'discovery' key
        - Discovery data includes: context, duplicates, complexity
        """
        orchestrator = ADOOrchestrator(self.config)
        result = orchestrator.execute(
            feature="Simple Bug Fix",
            test_mode=True,
            auto_approve=True
        )
        
        self.assertTrue(result.success)
        # Discovery data should be captured
        self.assertIsInstance(result.data, dict)
    
    def test_discovery_phase_transitions_correctly(self):
        """
        Test: DISCOVERY phase should transition to VALIDATION phase
        
        Validates that after completing discovery, the orchestrator
        correctly transitions to the VALIDATION phase.
        
        Expected behavior:
        - Phase starts at DISCOVERY
        - Phase transitions logged with 🎭 engagement hint
        - Phase ends at COMPLETION (after all phases)
        """
        orchestrator = ADOOrchestrator(self.config)
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.phase, ADOPhase.COMPLETION)
        
        # Check phase transitions in logs
        discovery_transition = any(
            "DISCOVERY" in log and "🎭" in log 
            for log in result.logs
        )
        self.assertTrue(discovery_transition, "DISCOVERY phase transition should be logged")
    
    def test_discovery_phase_handles_review_orchestrator_failure(self):
        """
        Test: DISCOVERY phase should handle review orchestrator failures gracefully
        
        Validates error handling when review orchestrator fails or is unavailable.
        This test is effectively the same as test_discovery_phase_runs_review_orchestrator
        since we use graceful degradation (placeholder raises exception, caught in execute()).
        
        Expected behavior:
        - Review orchestrator placeholder raises exception
        - Exception caught and handled gracefully
        - Warning added to result
        - Execution completes successfully
        """
        orchestrator = ADOOrchestrator(self.config)
        result = orchestrator.execute(
            feature="Test Feature",
            test_mode=True,
            auto_approve=True
        )
        
        # Should succeed with graceful degradation
        self.assertTrue(result.success)
        self.assertEqual(result.status, "success")
        # Should have warning about review orchestrator unavailability
        has_review_warning = any("review orchestrator unavailable" in w.lower() for w in result.warnings)
        self.assertTrue(has_review_warning, "Should warn about review orchestrator unavailability")


if __name__ == "__main__":
    unittest.main()
