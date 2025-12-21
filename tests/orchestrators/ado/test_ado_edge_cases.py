"""
Test Suite: ADO Orchestrator Edge Cases & Exception Paths

Targets uncovered code paths to achieve 90%+ test coverage:
- Exception handling in discovery phase (lines 360-377)
- High assumption count warnings (line 421)
- General exception catching (lines 500-503)
- Epic/feature/story hierarchy variations (lines 1033-1070)
- DoD validation edge cases (lines 1124, 1129)
- Additional validation and approval gate paths

Coverage Enhancement: 87.23% → 90%+
Author: Asif Hussain
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.ado.ado_orchestrator import (
    ADOOrchestrator, 
    ADOPhase, 
    ADOResult
)


class TestADOEdgeCases(unittest.TestCase):
    """Test suite for ADO Orchestrator edge cases and exception paths."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "name": "ADOOrchestrator",
            "version": "1.0.0",
            "workspace_root": "/test/workspace"
        }
    
    def test_discovery_phase_review_orchestrator_exception(self):
        """
        Test: Discovery phase handles review orchestrator exception gracefully.
        
        Covers: Lines 360-361, 371-377 (exception paths in discovery)
        
        Expected behavior:
        - Review orchestrator raises exception
        - Warning added to warnings list
        - Execution continues with review_context = None
        - Overall execution still succeeds
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Mock review orchestrator to raise exception
        with patch.object(orchestrator, '_run_review_orchestrator') as mock_review:
            mock_review.side_effect = Exception("Review service unavailable")
            
            result = orchestrator.execute(
                feature="Test Feature",
                test_mode=True,
                auto_approve=True
            )
        
        # Verify graceful degradation
        self.assertTrue(result.success)
        self.assertIn("discovery", result.data)
        self.assertIsNone(result.data["discovery"]["review_context"])
        
        # Check for warning about review orchestrator
        has_warning = any("review orchestrator unavailable" in w.lower() for w in result.warnings)
        self.assertTrue(has_warning, "Should log warning about review orchestrator exception")
    
    def test_discovery_phase_duplicate_detection_exception(self):
        """
        Test: Discovery phase handles duplicate detection exception gracefully.
        
        Covers: Lines 371-377 (duplicate detection exception path)
        
        Expected behavior:
        - Duplicate detection raises exception
        - Warning added to warnings list
        - Execution continues with empty duplicates list
        - Overall execution still succeeds
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Mock duplicate detection to raise exception
        with patch.object(orchestrator, '_detect_duplicates') as mock_detect:
            mock_detect.side_effect = Exception("ADO API unavailable")
            
            result = orchestrator.execute(
                feature="Test Feature",
                test_mode=True,
                auto_approve=True
            )
        
        # Verify graceful degradation
        self.assertTrue(result.success)
        self.assertIn("discovery", result.data)
        
        # Check for warning about duplicate detection
        has_warning = any("duplicate detection unavailable" in w.lower() for w in result.warnings)
        self.assertTrue(has_warning, "Should log warning about duplicate detection exception")
    
    def test_high_assumption_count_triggers_warning(self):
        """
        Test: High number of assumptions triggers warning.
        
        Covers: Line 421 (high assumption count warning)
        
        Expected behavior:
        - When assumptions > 5, warning is added
        - Warning mentions high number of assumptions
        - Suggests uncertainty in requirements
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Provide many assumptions (> 5)
        many_assumptions = [
            "Database will be SQL Server",
            "Authentication via Azure AD",
            "Legacy system APIs available",
            "User roles predefined",
            "Network latency < 100ms",
            "Third-party service uptime 99.9%",
            "Data migration completed"
        ]
        
        result = orchestrator.execute(
            feature="Complex Integration",
            assumptions=many_assumptions,
            test_mode=True,
            auto_approve=True
        )
        
        # Check for high assumption count warning
        has_warning = any(
            "high number of assumptions" in w.lower() and "uncertainty" in w.lower() 
            for w in result.warnings
        )
        self.assertTrue(has_warning, "Should warn about high assumption count")
        self.assertGreaterEqual(len(many_assumptions), 5)
    
    def test_no_constraints_provided_handled_gracefully(self):
        """
        Test: No constraints provided is handled without error.
        
        Covers: Lines around 430-436 (empty constraints handling)
        
        Expected behavior:
        - Empty constraints list does not cause error
        - Info log added about optional constraints
        - Execution proceeds normally
        """
        orchestrator = ADOOrchestrator(self.config)
        
        result = orchestrator.execute(
            feature="Simple Feature",
            constraints=[],  # Explicitly empty
            test_mode=True,
            auto_approve=True
        )
        
        # Should complete successfully
        self.assertTrue(result.success)
        self.assertIn("dor", result.data)
        self.assertEqual(result.data["dor"]["constraints"], [])
    
    def test_general_exception_during_execution(self):
        """
        Test: General exception during execution is caught and handled.
        
        Covers: Lines 500-503 (general exception handling)
        
        Expected behavior:
        - Unexpected exception caught
        - Error result returned with proper structure
        - Phase information preserved
        - Error message includes phase context
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Mock execute method's internal flow to raise unexpected exception
        with patch.object(orchestrator, '_classify_complexity') as mock_classify:
            mock_classify.side_effect = RuntimeError("Unexpected system error")
            
            result = orchestrator.execute(
                feature="Test Feature",
                test_mode=True
            )
        
        # Verify error handling
        self.assertFalse(result.success)
        self.assertEqual(result.status, "error")
        self.assertGreater(len(result.errors), 0)
        self.assertIn("Unexpected system error", str(result.errors))
    
    def test_epic_hierarchy_with_features_and_stories(self):
        """
        Test: Epic → Features → Stories → Tasks hierarchy generation.
        
        Covers: Lines 1033-1070 (epic/feature branch in hierarchy processing)
        
        Expected behavior:
        - Epic at top level
        - Features under epic
        - Stories under features
        - Tasks under stories
        - All items properly formatted
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Create hierarchy with epic (with required work_item_type field)
        hierarchy = {
            "epic": {
                "title": "E-Commerce Platform",
                "description": "Build e-commerce platform",
                "work_item_type": "Epic"
            },
            "features": [
                {
                    "title": "User Management",
                    "description": "User management feature",
                    "work_item_type": "Feature",
                    "stories": [
                        {
                            "title": "User Registration",
                            "description": "User registration story",
                            "work_item_type": "User Story",
                            "tasks": [
                                {
                                    "title": "Create registration form",
                                    "description": "Create form",
                                    "work_item_type": "Task"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        batch_payload = orchestrator._format_batch_work_items(hierarchy)
        
        # Verify all levels present
        self.assertGreater(len(batch_payload), 0)
        
        # Check for epic
        epic_items = [item for item in batch_payload if item.get("fields", {}).get("System.WorkItemType") == "Epic"]
        self.assertGreater(len(epic_items), 0, "Should have epic in payload")
        
        # Check for features
        feature_items = [item for item in batch_payload if item.get("fields", {}).get("System.WorkItemType") == "Feature"]
        self.assertGreater(len(feature_items), 0, "Should have features in payload")
        
        # Check for stories
        story_items = [item for item in batch_payload if "Story" in item.get("fields", {}).get("System.WorkItemType", "")]
        self.assertGreater(len(story_items), 0, "Should have stories in payload")
        
        # Check for tasks
        task_items = [item for item in batch_payload if item.get("fields", {}).get("System.WorkItemType") == "Task"]
        self.assertGreater(len(task_items), 0, "Should have tasks in payload")
    
    def test_low_complexity_stories_without_features(self):
        """
        Test: LOW complexity case with stories directly (no features).
        
        Covers: Lines 1061-1070 (elif stories branch)
        
        Expected behavior:
        - No epic or features
        - Stories at top level
        - Tasks under stories
        - Simpler hierarchy for low complexity
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Create LOW complexity hierarchy (stories only) with required fields
        hierarchy = {
            "stories": [
                {
                    "title": "Simple User Story",
                    "description": "Simple story",
                    "work_item_type": "User Story",
                    "tasks": [
                        {
                            "title": "Implement feature",
                            "description": "Implementation",
                            "work_item_type": "Task"
                        },
                        {
                            "title": "Write tests",
                            "description": "Testing",
                            "work_item_type": "Task"
                        }
                    ]
                }
            ]
        }
        
        batch_payload = orchestrator._format_batch_work_items(hierarchy)
        
        # Verify stories and tasks present
        self.assertGreater(len(batch_payload), 0)
        
        # Should NOT have epic or features
        epic_items = [item for item in batch_payload if item.get("fields", {}).get("System.WorkItemType") == "Epic"]
        feature_items = [item for item in batch_payload if item.get("fields", {}).get("System.WorkItemType") == "Feature"]
        self.assertEqual(len(epic_items), 0, "LOW complexity should not have epic")
        self.assertEqual(len(feature_items), 0, "LOW complexity should not have features")
        
        # Should have stories and tasks
        story_items = [item for item in batch_payload if "Story" in item.get("fields", {}).get("System.WorkItemType", "")]
        task_items = [item for item in batch_payload if item.get("fields", {}).get("System.WorkItemType") == "Task"]
        self.assertGreater(len(story_items), 0, "Should have stories")
        self.assertGreater(len(task_items), 0, "Should have tasks")
    
    def test_dod_validation_with_missing_criteria(self):
        """
        Test: DoD validation identifies missing completion criteria.
        
        Covers: Lines 1124, 1129 (missing criteria tracking)
        
        Expected behavior:
        - Missing criteria identified
        - Percentage calculated correctly
        - is_complete = False when criteria missing
        - missing_criteria list populated
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Test DoD validation with partially met criteria
        dod_data = {
            "test_coverage": 85,  # Met (≥80%)
            "documentation_updated": True,
            "code_review_completed": False,  # Missing
            "acceptance_criteria_verified": True
        }
        
        dod_result = orchestrator._validate_dod_completeness(dod_data)
        
        # Verify validation results
        self.assertFalse(dod_result["is_complete"], "Should not be complete with missing criteria")
        self.assertIn("code_review_completed", dod_result["missing_criteria"])
        self.assertLess(dod_result["percentage"], 100)
        self.assertEqual(dod_result["test_coverage_percentage"], 85)
    
    def test_dod_validation_all_criteria_met(self):
        """
        Test: DoD validation passes when all criteria met.
        
        Covers: Lines 1124, 1129 (all criteria met path)
        
        Expected behavior:
        - All criteria met
        - Percentage = 100
        - is_complete = True
        - missing_criteria list empty
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Test DoD validation with all criteria met
        dod_data = {
            "test_coverage": 90,  # Met (≥80%)
            "documentation_updated": True,
            "code_review_completed": True,
            "acceptance_criteria_verified": True
        }
        
        dod_result = orchestrator._validate_dod_completeness(dod_data)
        
        # Verify validation results
        self.assertTrue(dod_result["is_complete"], "Should be complete with all criteria met")
        self.assertEqual(len(dod_result["missing_criteria"]), 0)
        self.assertEqual(dod_result["percentage"], 100)
        self.assertEqual(dod_result["test_coverage_percentage"], 90)
    
    def test_work_item_missing_description_uses_title(self):
        """
        Test: Work item without description uses title as fallback.
        
        Covers: Lines 1033-1035 (ensure_required_fields helper)
        
        Expected behavior:
        - Work item missing description
        - Description auto-populated from title
        - No error occurs
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Create hierarchy with item missing description
        hierarchy = {
            "stories": [
                {
                    "title": "Story Without Description",
                    "work_item_type": "User Story"
                    # No description field - should auto-populate
                }
            ]
        }
        
        batch_payload = orchestrator._format_batch_work_items(hierarchy)
        
        # Verify description was populated
        self.assertGreater(len(batch_payload), 0)
        story_item = batch_payload[0]
        self.assertIn("fields", story_item)
        self.assertIn("System.Description", story_item["fields"])
        self.assertEqual(story_item["fields"]["System.Description"], "Story Without Description")
    
    def test_empty_hierarchy_returns_empty_payload(self):
        """
        Test: Empty hierarchy returns empty batch payload.
        
        Covers: Edge case for empty input
        
        Expected behavior:
        - Empty hierarchy dict
        - Returns empty list
        - No errors
        """
        orchestrator = ADOOrchestrator(self.config)
        
        # Empty hierarchy
        hierarchy = {}
        
        batch_payload = orchestrator._format_batch_work_items(hierarchy)
        
        # Should return empty list
        self.assertEqual(len(batch_payload), 0)
        self.assertIsInstance(batch_payload, list)


if __name__ == '__main__':
    unittest.main()
