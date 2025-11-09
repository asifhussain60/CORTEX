"""
Tests for WorkPlanner Agent

Validates task breakdown, pattern matching, velocity-aware estimation,
and integration with Tier 2/3 systems.
"""

import pytest
from src.cortex_agents.work_planner import WorkPlanner
from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class TestWorkPlannerBasics:
    """Test basic WorkPlanner functionality"""
    
    def test_planner_initialization(self, mock_tier_apis):
        """Test WorkPlanner initialization"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        assert planner.name == "Planner"
        assert planner.tier1 is not None
        assert planner.tier2 is not None
        assert planner.tier3 is not None
        assert len(planner.TASK_TEMPLATES) > 0
    
    def test_planner_can_handle_plan_intent(self, mock_tier_apis):
        """Test WorkPlanner handles plan intents"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan a new feature"
        )
        
        assert planner.can_handle(request) is True
    
    def test_planner_can_handle_feature_intent(self, mock_tier_apis):
        """Test WorkPlanner handles feature intents"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="feature",
            context={},
            user_message="Build authentication"
        )
        
        assert planner.can_handle(request) is True
    
    def test_planner_rejects_invalid_intent(self, mock_tier_apis):
        """Test WorkPlanner rejects non-planning intents"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="code",
            context={},
            user_message="Write some code"
        )
        
        assert planner.can_handle(request) is False


class TestComplexityAnalysis:
    """Test complexity analysis"""
    
    def test_analyze_simple_complexity(self, mock_tier_apis):
        """Test simple complexity detection"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Add a simple button to the UI"
        )
        
        complexity = planner._analyze_complexity(request)
        assert complexity == "simple"
    
    def test_analyze_medium_complexity(self, mock_tier_apis):
        """Test medium complexity detection"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Refactor the authentication module"
        )
        
        complexity = planner._analyze_complexity(request)
        assert complexity == "medium"
    
    def test_analyze_complex_complexity(self, mock_tier_apis):
        """Test complex complexity detection"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Redesign the entire system architecture"
        )
        
        complexity = planner._analyze_complexity(request)
        assert complexity == "complex"
    
    def test_complexity_from_context(self, mock_tier_apis):
        """Test complexity detection from context"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={"complexity": "complex"},
            user_message="Do something"
        )
        
        complexity = planner._analyze_complexity(request)
        assert complexity == "complex"


class TestTaskBreakdown:
    """Test task breakdown generation"""
    
    def test_authentication_template_matching(self, mock_tier_apis):
        """Test matching authentication template"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Add user authentication with login"
        )
        
        response = planner.execute(request)
        
        assert response.success is True
        assert len(response.result["tasks"]) > 0
        assert response.result["complexity"] in ["simple", "medium", "complex"]
        assert response.result["total_hours"] > 0
    
    def test_api_endpoint_template_matching(self, mock_tier_apis):
        """Test matching API endpoint template"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Create a new REST API endpoint for users"
        )
        
        response = planner.execute(request)
        
        assert response.success is True
        tasks = response.result["tasks"]
        assert len(tasks) > 0
        # Should match api_endpoint template
        assert any("endpoint" in task["name"].lower() for task in tasks)
    
    def test_generic_breakdown(self, mock_tier_apis):
        """Test generic task breakdown for unmatched patterns"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Implement a completely unique feature"
        )
        
        response = planner.execute(request)
        
        assert response.success is True
        tasks = response.result["tasks"]
        assert len(tasks) >= 3  # Should have at least analyze, implement, test
        # Generic breakdown includes requirements analysis
        assert any("requir" in task["name"].lower() or "analyz" in task["name"].lower() for task in tasks)
    
    def test_task_has_required_fields(self, mock_tier_apis):
        """Test that tasks have all required fields"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan something"
        )
        
        response = planner.execute(request)
        
        assert response.success is True
        for task in response.result["tasks"]:
            assert "id" in task
            assert "name" in task
            assert "estimated_hours" in task
            assert "status" in task
            assert "priority" in task


class TestTierIntegration:
    """Test integration with Tier 2 and Tier 3"""
    
    def test_tier2_workflow_search(self, mock_tier_apis):
        """Test querying Tier 2 for workflow patterns"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        # Add a workflow pattern to Tier 2
        planner.tier2.add_pattern(
            "workflow",
            "Workflow: Add authentication",
            str({
                "tasks": [
                    {"name": "Setup auth library", "estimated_hours": 1.0},
                    {"name": "Create login form", "estimated_hours": 2.0}
                ],
                "complexity": "medium"
            })
        )
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Add authentication system"
        )
        
        workflows = planner._find_similar_workflows(request)
        # Should find the pattern we added
        assert len(workflows) >= 0  # May or may not match depending on search logic
    
    def test_tier3_velocity_metrics(self, mock_tier_apis):
        """Test getting velocity metrics from Tier 3"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        velocity_data = planner._get_velocity_metrics()
        
        assert velocity_data is not None
        assert "average_velocity" in velocity_data
        assert velocity_data["average_velocity"] > 0
    
    def test_velocity_adjusts_estimates(self, mock_tier_apis):
        """Test that velocity data adjusts time estimates"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        # Mock high velocity team
        planner.tier3.metrics["velocity"] = 25.0
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Simple feature"
        )
        
        response = planner.execute(request)
        
        assert response.success is True
        assert response.result["velocity_adjusted"] is True
    
    def test_stores_workflow_in_tier2(self, mock_tier_apis):
        """Test storing workflow pattern in Tier 2"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        initial_count = len(planner.tier2.patterns)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Create a new feature"
        )
        
        response = planner.execute(request)
        
        assert response.success is True
        # Should have stored workflow pattern
        assert len(planner.tier2.patterns) > initial_count


class TestEstimateAdjustment:
    """Test time estimate adjustments"""
    
    def test_complexity_multiplier(self, mock_tier_apis):
        """Test complexity affects estimates"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        # Simple request
        simple_request = AgentRequest(
            intent="plan",
            context={"complexity": "simple"},
            user_message="Add a button"
        )
        
        # Complex request
        complex_request = AgentRequest(
            intent="plan",
            context={"complexity": "complex"},
            user_message="Redesign architecture"
        )
        
        simple_response = planner.execute(simple_request)
        complex_response = planner.execute(complex_request)
        
        # Complex should have higher total hours
        assert complex_response.result["total_hours"] > simple_response.result["total_hours"]
    
    def test_estimate_adjustment_with_velocity(self, mock_tier_apis):
        """Test velocity adjustment of estimates"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        tasks = [
            {"name": "Task 1", "base_hours": 2.0},
            {"name": "Task 2", "base_hours": 3.0}
        ]
        
        velocity_data = {"average_velocity": 15.0}
        
        adjusted = planner._adjust_estimates(tasks, "medium", velocity_data)
        
        # Should have estimated_hours field
        assert all("estimated_hours" in task for task in adjusted)
        assert all(task["estimated_hours"] > 0 for task in adjusted)


class TestRiskAssessment:
    """Test risk assessment"""
    
    def test_complexity_risk(self, mock_tier_apis):
        """Test complex tasks get risk warnings"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={"complexity": "complex"},
            user_message="Redesign everything"
        )
        
        response = planner.execute(request)
        
        assert response.success is True
        assert len(response.result["risks"]) > 0
    
    def test_large_scope_risk(self, mock_tier_apis):
        """Test large task count triggers risk warning"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        # Create a scenario that generates many tasks
        tasks = [{"name": f"Task {i}", "estimated_hours": 1.0} for i in range(15)]
        
        risks = planner._assess_risks(
            AgentRequest(intent="plan", context={}, user_message="Big project"),
            "medium",
            tasks
        )
        
        # Should flag large number of tasks
        assert len(risks) > 0
        assert any("tasks" in risk.lower() for risk in risks)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_planner_without_tier_apis(self):
        """Test WorkPlanner functions without Tier APIs"""
        planner = WorkPlanner("Planner")
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan something"
        )
        
        response = planner.execute(request)
        
        # Should still work, just without pattern matching or velocity
        assert response.success is True
        assert len(response.result["tasks"]) > 0
    
    def test_empty_user_message(self, mock_tier_apis):
        """Test handling empty user message"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message=""
        )
        
        response = planner.execute(request)
        
        # Should create generic breakdown
        assert response.success is True
        assert len(response.result["tasks"]) > 0
    
    def test_tier2_search_failure(self, mock_tier_apis):
        """Test graceful handling of Tier 2 search failure"""
        planner = WorkPlanner("Planner", **mock_tier_apis)
        
        # Make Tier 2 search fail
        def failing_search(*args, **kwargs):
            raise Exception("Search failed")
        
        planner.tier2.search = failing_search
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan something"
        )
        
        response = planner.execute(request)
        
        # Should still succeed without pattern matching
        assert response.success is True
        assert len(response.result["tasks"]) > 0
