"""
Test Suite: ADO Work Item Generation Phase

RED Phase Tests - Task 4: Work Item Generation Phase
These tests define expected behavior for work item hierarchy, story points, TDD injection.

Task 4 Scope:
- Work item hierarchy (Epic → Feature → User Story → Task)
- Story point conversion from effort estimates
- TDD test injection requirements
- ADO-formatted output validation

Expected: All tests FAIL initially (RED phase)
Then: Implement code to make tests pass (GREEN phase)
Finally: Refactor while keeping tests green (REFACTOR phase)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from src.orchestrators.ado.ado_orchestrator import ADOOrchestrator, ADOPhase


class TestWorkItemHierarchy:
    """
    RED Phase Tests for Work Item Hierarchy Generation
    
    Requirements:
    - REQ-ADO-002: Work item type mapping
    - REQ-ADO-004: Parent-child linking
    - Planning System 2.0 parity: Feature decomposition
    """
    
    def test_generate_hierarchy_from_high_complexity(self):
        """
        Test: HIGH complexity features generate full hierarchy
        
        Expected Structure:
        Epic (1)
          ├── Feature (1-3)
          │   ├── User Story (3-5 per feature)
          │   │   ├── Task (2-4 per story)
        
        Expected (RED): Method not implemented
        Expected (GREEN): Full hierarchy returned
        """
        orchestrator = ADOOrchestrator()
        
        # HIGH complexity input
        feature = "Implement distributed blockchain payment system"
        complexity = "HIGH"
        acceptance_criteria = [
            "Given a user initiates payment, When transaction completes, Then blockchain confirms",
            "Given network failure, When retry triggered, Then payment resumes from checkpoint"
        ]
        
        # Generate hierarchy
        hierarchy = orchestrator._generate_work_item_hierarchy(
            feature_name=feature,
            complexity=complexity,
            acceptance_criteria=acceptance_criteria
        )
        
        # Validate structure
        assert "epic" in hierarchy, "HIGH complexity must include Epic"
        assert "features" in hierarchy, "HIGH complexity must include Features"
        assert len(hierarchy["features"]) >= 1, "Must have at least 1 feature"
        
        # Check first feature has stories
        first_feature = hierarchy["features"][0]
        assert "stories" in first_feature, "Features must have User Stories"
        assert len(first_feature["stories"]) >= 3, "Features must have 3-5 stories"
        
        # Check first story has tasks
        first_story = first_feature["stories"][0]
        assert "tasks" in first_story, "Stories must have Tasks"
        assert len(first_story["tasks"]) >= 2, "Stories must have 2-4 tasks"
    
    def test_generate_hierarchy_from_medium_complexity(self):
        """
        Test: MEDIUM complexity features skip Epic level
        
        Expected Structure:
        Feature (1)
          ├── User Story (2-4)
          │   ├── Task (2-3 per story)
        
        Expected (RED): Method not implemented
        Expected (GREEN): Feature-level hierarchy returned
        """
        orchestrator = ADOOrchestrator()
        
        # MEDIUM complexity input
        feature = "Add user authentication API"
        complexity = "MEDIUM"
        acceptance_criteria = [
            "Given valid credentials, When user logs in, Then JWT token returned"
        ]
        
        # Generate hierarchy
        hierarchy = orchestrator._generate_work_item_hierarchy(
            feature_name=feature,
            complexity=complexity,
            acceptance_criteria=acceptance_criteria
        )
        
        # Validate structure
        assert "epic" not in hierarchy, "MEDIUM complexity should skip Epic"
        assert "features" in hierarchy, "MEDIUM complexity starts at Feature level"
        assert len(hierarchy["features"]) == 1, "MEDIUM has single feature"
        
        # Check feature has stories
        feature_item = hierarchy["features"][0]
        assert "stories" in feature_item, "Feature must have User Stories"
        assert 2 <= len(feature_item["stories"]) <= 4, "MEDIUM has 2-4 stories"
    
    def test_generate_hierarchy_from_low_complexity(self):
        """
        Test: LOW complexity features generate single story with tasks
        
        Expected Structure:
        User Story (1)
          ├── Task (1-2)
        
        Expected (RED): Method not implemented
        Expected (GREEN): Story-level hierarchy returned
        """
        orchestrator = ADOOrchestrator()
        
        # LOW complexity input
        feature = "Fix login button color"
        complexity = "LOW"
        acceptance_criteria = [
            "Given login page loads, When button displays, Then color is #007bff"
        ]
        
        # Generate hierarchy
        hierarchy = orchestrator._generate_work_item_hierarchy(
            feature_name=feature,
            complexity=complexity,
            acceptance_criteria=acceptance_criteria
        )
        
        # Validate structure
        assert "epic" not in hierarchy, "LOW complexity should skip Epic"
        assert "features" not in hierarchy, "LOW complexity should skip Feature"
        assert "stories" in hierarchy, "LOW complexity starts at Story level"
        assert len(hierarchy["stories"]) == 1, "LOW has single story"
        
        # Check story has tasks
        story = hierarchy["stories"][0]
        assert "tasks" in story, "Story must have Tasks"
        assert 1 <= len(story["tasks"]) <= 2, "LOW has 1-2 tasks"


class TestStoryPointConversion:
    """
    RED Phase Tests for Story Point Conversion
    
    Requirements:
    - REQ-ADO-003: Story point conversion from effort
    - Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21
    - Conversion formula: hours → story points
    """
    
    def test_convert_effort_to_story_points_small(self):
        """
        Test: Convert small effort (1-3h) to story points
        
        Mapping:
        - 1h → 1 point
        - 2h → 2 points
        - 3h → 3 points
        
        Expected (RED): Method not implemented
        Expected (GREEN): Correct story points returned
        """
        orchestrator = ADOOrchestrator()
        
        # Test small effort values
        assert orchestrator._convert_effort_to_story_points(1) == 1
        assert orchestrator._convert_effort_to_story_points(2) == 2
        assert orchestrator._convert_effort_to_story_points(3) == 3
    
    def test_convert_effort_to_story_points_medium(self):
        """
        Test: Convert medium effort (4-8h) to story points
        
        Mapping:
        - 4h → 5 points
        - 5-6h → 5 points
        - 7-8h → 8 points
        
        Expected (RED): Method not implemented
        Expected (GREEN): Correct story points returned
        """
        orchestrator = ADOOrchestrator()
        
        # Test medium effort values
        assert orchestrator._convert_effort_to_story_points(4) == 5
        assert orchestrator._convert_effort_to_story_points(5) == 5
        assert orchestrator._convert_effort_to_story_points(6) == 5
        assert orchestrator._convert_effort_to_story_points(7) == 8
        assert orchestrator._convert_effort_to_story_points(8) == 8
    
    def test_convert_effort_to_story_points_large(self):
        """
        Test: Convert large effort (9-20h) to story points
        
        Mapping:
        - 9-12h → 13 points
        - 13-20h → 21 points
        - 20+h → 21 points (max)
        
        Expected (RED): Method not implemented
        Expected (GREEN): Correct story points returned
        """
        orchestrator = ADOOrchestrator()
        
        # Test large effort values
        assert orchestrator._convert_effort_to_story_points(9) == 13
        assert orchestrator._convert_effort_to_story_points(12) == 13
        assert orchestrator._convert_effort_to_story_points(15) == 21
        assert orchestrator._convert_effort_to_story_points(20) == 21
        assert orchestrator._convert_effort_to_story_points(30) == 21  # Max cap


class TestTDDInjection:
    """
    RED Phase Tests for TDD Test Injection
    
    Requirements:
    - All work items must include TDD requirements
    - RED → GREEN → REFACTOR phases defined
    - Test-first approach enforced
    - SKULL rule compliance (TDD_ENFORCEMENT)
    """
    
    def test_inject_tdd_requirements_in_tasks(self):
        """
        Test: Every task must have TDD requirements injected
        
        Expected TDD Fields:
        - test_strategy: "RED → GREEN → REFACTOR"
        - red_phase: "Write failing test first"
        - green_phase: "Implement minimal code to pass"
        - refactor_phase: "Improve code quality"
        
        Expected (RED): Method not implemented
        Expected (GREEN): TDD fields present in tasks
        """
        orchestrator = ADOOrchestrator()
        
        # Sample task without TDD
        task = {
            "title": "Implement user login validation",
            "description": "Add validation logic for user credentials",
            "effort_hours": 3
        }
        
        # Inject TDD requirements
        enhanced_task = orchestrator._inject_tdd_requirements(task)
        
        # Verify TDD fields added
        assert "test_strategy" in enhanced_task, "Task must have test_strategy"
        assert enhanced_task["test_strategy"] == "RED → GREEN → REFACTOR"
        
        assert "red_phase" in enhanced_task, "Task must have red_phase"
        assert "write failing test" in enhanced_task["red_phase"].lower()
        
        assert "green_phase" in enhanced_task, "Task must have green_phase"
        assert "implement" in enhanced_task["green_phase"].lower()
        
        assert "refactor_phase" in enhanced_task, "Task must have refactor_phase"
        assert "refactor" in enhanced_task["refactor_phase"].lower()
    
    def test_inject_tdd_requirements_with_acceptance_criteria(self):
        """
        Test: TDD injection must reference acceptance criteria
        
        Expected: RED phase test references AC
        
        Expected (RED): Method not implemented
        Expected (GREEN): AC referenced in TDD fields
        """
        orchestrator = ADOOrchestrator()
        
        # Task with acceptance criteria
        task = {
            "title": "Validate email format",
            "description": "Ensure email follows RFC 5322",
            "effort_hours": 2,
            "acceptance_criteria": [
                "Given email input, When format invalid, Then error shown"
            ]
        }
        
        # Inject TDD
        enhanced_task = orchestrator._inject_tdd_requirements(task)
        
        # Verify AC referenced
        assert "acceptance_criteria" in enhanced_task["red_phase"].lower() or \
               "given" in enhanced_task["red_phase"].lower(), \
               "RED phase must reference acceptance criteria"


class TestADOFormattedOutput:
    """
    RED Phase Tests for ADO-Formatted Output
    
    Requirements:
    - REQ-ADO-005: ADO work item JSON format
    - Must match Azure DevOps REST API schema
    - Include all required fields
    """
    
    def test_format_work_item_for_ado_api(self):
        """
        Test: Format internal work item to ADO API JSON
        
        Required ADO Fields:
        - fields[System.Title]
        - fields[System.Description]
        - fields[Microsoft.VSTS.Scheduling.StoryPoints]
        - fields[System.WorkItemType]
        - relations[] (for parent links)
        
        Expected (RED): Method not implemented
        Expected (GREEN): Valid ADO JSON returned
        """
        orchestrator = ADOOrchestrator()
        
        # Internal work item
        work_item = {
            "title": "User Story: Login Flow",
            "description": "Implement user authentication workflow",
            "story_points": 5,
            "work_item_type": "User Story",
            "parent_id": 12345
        }
        
        # Format for ADO
        ado_payload = orchestrator._format_work_item_for_ado(work_item)
        
        # Validate ADO schema
        assert "fields" in ado_payload, "Must have fields object"
        assert "System.Title" in ado_payload["fields"]
        assert "System.Description" in ado_payload["fields"]
        assert "Microsoft.VSTS.Scheduling.StoryPoints" in ado_payload["fields"]
        assert "System.WorkItemType" in ado_payload["fields"]
        
        # Validate parent link
        if work_item.get("parent_id"):
            assert "relations" in ado_payload, "Must have relations for parent link"
            assert len(ado_payload["relations"]) > 0
            assert ado_payload["relations"][0]["rel"] == "System.LinkTypes.Hierarchy-Reverse"
    
    def test_format_batch_work_items(self):
        """
        Test: Format multiple work items for batch creation
        
        ADO Batch API Format:
        - Array of work item payloads
        - Order matters (parents before children)
        
        Expected (RED): Method not implemented
        Expected (GREEN): Ordered batch payload returned
        """
        orchestrator = ADOOrchestrator()
        
        # Hierarchy with parent-child relationships
        hierarchy = {
            "features": [
                {
                    "title": "Feature: User Management",
                    "work_item_type": "Feature",
                    "stories": [
                        {
                            "title": "Story: User Login",
                            "work_item_type": "User Story",
                            "tasks": [
                                {"title": "Task: Login Form", "work_item_type": "Task"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Format for batch
        batch_payload = orchestrator._format_batch_work_items(hierarchy)
        
        # Validate ordering (parents before children)
        assert len(batch_payload) == 3, "Must have 3 work items (Feature, Story, Task)"
        assert batch_payload[0]["fields"]["System.WorkItemType"] == "Feature"
        assert batch_payload[1]["fields"]["System.WorkItemType"] == "User Story"
        assert batch_payload[2]["fields"]["System.WorkItemType"] == "Task"


# ===== TEST EXECUTION SUMMARY =====
# Expected Initial State (RED Phase):
# - 12 tests defined
# - All tests should FAIL (methods not implemented)
#
# After GREEN Phase Implementation:
# - All tests should PASS
#
# After REFACTOR Phase:
# - Tests remain PASSING
# - Code quality improved
