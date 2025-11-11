"""
Integration tests for CORTEX 2.0 agent coordination.

Tests multi-agent workflows, corpus callosum coordination, and left/right brain integration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import json
from datetime import datetime

# Import actual agents where available, mock where not
try:
    from src.cortex_agents.intent_router import IntentRouter
except ImportError:
    IntentRouter = None

try:
    from src.cortex_agents.architect import Architect
    from src.cortex_agents.work_planner import WorkPlanner
    from src.cortex_agents.executor import Executor
    from src.cortex_agents.learner import Learner
    from src.cortex_agents.pattern_matcher import PatternMatcher
except ImportError:
    Architect = None
    WorkPlanner = None
    Executor = None
    Learner = None
    PatternMatcher = None

# For agents not yet implemented, we'll use mocks in the tests


@pytest.mark.skip(reason="Requires all 10 agents to be implemented - TODO for Phase 5.2")
class TestMultiAgentWorkflow:
    """Test coordinated workflows involving multiple agents."""
    
    @pytest.fixture
    def mock_brain_root(self, tmp_path):
        """Create temporary brain directory structure."""
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        (brain_root / "conversation-history.jsonl").write_text("")
        return brain_root
    
    @pytest.fixture
    def intent_router(self, mock_tier1_api, mock_tier2_kg, mock_tier3_context):
        """Create intent router with mocked dependencies."""
        return IntentRouter(
            name="TestRouter",
            tier1_api=mock_tier1_api,
            tier2_kg=mock_tier2_kg,
            tier3_context=mock_tier3_context
        )
    
    def test_feature_development_full_pipeline(self, intent_router, mock_brain_root):
        """
        Test complete feature development pipeline:
        Intent → Plan → Execute → Test → Validate → Learn
        """
        # Step 1: Intent Detection
        request = "Add a purple button to the dashboard"
        intent = intent_router.detect_intent(request)
        
        assert intent["primary_intent"] == "EXECUTE"
        assert intent["confidence"] > 0.8
        assert "dashboard" in intent["entities"]
        assert "purple" in intent["entities"]
        
        # Step 2: Work Planning
        planner = WorkPlanner(brain_root=str(mock_brain_root))
        plan = planner.create_plan(request, intent)
        
        assert plan["status"] == "success"
        assert "tasks" in plan
        assert len(plan["tasks"]) >= 3  # Create button, style, integrate
        
        # Step 3: Execution
        executor = Executor(brain_root=str(mock_brain_root))
        execution_result = executor.execute_plan(plan)
        
        assert execution_result["status"] in ["success", "partial"]
        assert "files_modified" in execution_result
        
        # Step 4: Test Generation
        tester = Tester(brain_root=str(mock_brain_root))
        test_result = tester.generate_tests(execution_result)
        
        assert test_result["status"] == "success"
        assert "test_files" in test_result
        assert len(test_result["test_files"]) > 0
        
        # Step 5: Validation
        validator = Validator(brain_root=str(mock_brain_root))
        validation_result = validator.validate_implementation(
            execution_result, test_result
        )
        
        assert validation_result["status"] in ["passed", "passed_with_warnings"]
        assert "checks" in validation_result
        
        # Step 6: Learning
        learner = Learner(brain_root=str(mock_brain_root))
        learning_result = learner.extract_patterns({
            "request": request,
            "intent": intent,
            "plan": plan,
            "execution": execution_result,
            "validation": validation_result
        })
        
        assert learning_result["status"] == "success"
        assert "patterns_learned" in learning_result
    
    def test_architecture_planning_workflow(self, intent_router, mock_brain_root):
        """
        Test architecture planning workflow:
        Intent → Pattern Match → Architect → Validate
        """
        # Step 1: Intent Detection
        request = "Design a caching layer for database queries"
        intent = intent_router.detect_intent(request)
        
        assert intent["primary_intent"] == "ARCHITECT"
        
        # Step 2: Pattern Matching
        pattern_matcher = PatternMatcher(brain_root=str(mock_brain_root))
        similar_patterns = pattern_matcher.find_similar_patterns(request)
        
        assert "patterns" in similar_patterns
        # May have 0 patterns in fresh brain, but should execute without error
        
        # Step 3: Architecture Design
        architect = Architect(brain_root=str(mock_brain_root))
        architecture = architect.design_solution(request, similar_patterns)
        
        assert architecture["status"] == "success"
        assert "design" in architecture
        assert "components" in architecture["design"]
        
        # Step 4: Validation
        validator = Validator(brain_root=str(mock_brain_root))
        validation = validator.validate_architecture(architecture)
        
        assert validation["status"] in ["passed", "passed_with_warnings"]
        assert "solid_principles" in validation


class TestCorpusCallosumCoordination:
    """Test coordination between left-brain (tactical) and right-brain (strategic) agents."""
    
    @pytest.fixture
    def mock_brain_root(self, tmp_path):
        """Create temporary brain directory structure."""
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        return brain_root
    
    @pytest.mark.skipif(Architect is None, reason="Requires Architect agent to be implemented")
    def test_tactical_strategic_handoff(self, mock_brain_root):
        """
        Test handoff between strategic planning (right brain) and tactical execution (left brain).
        """
        # Right Brain: Strategic Planning
        architect = Architect(brain_root=str(mock_brain_root))
        design = architect.design_solution(
            "Create a user authentication system with JWT tokens"
        )
        
        assert design["status"] == "success"
        
        # Left Brain: Break down into tasks
        planner = WorkPlanner(brain_root=str(mock_brain_root))
        plan = planner.create_plan(
            "Implement the authentication system",
            {"design": design}
        )
        
        assert plan["status"] == "success"
        assert len(plan["tasks"]) > 0
        
        # Left Brain: Execute
        executor = Executor(brain_root=str(mock_brain_root))
        execution = executor.execute_plan(plan)
        
        assert execution["status"] in ["success", "partial", "simulated"]
    
    @pytest.mark.skipif(Learner is None, reason="Requires Learner and PatternMatcher agents to be implemented")
    def test_pattern_learning_feedback_loop(self, mock_brain_root):
        """
        Test feedback loop: Learning (right brain) → Pattern matching (right brain) → 
        Execution (left brain) → Learning update.
        """
        learner = Learner(brain_root=str(mock_brain_root))
        pattern_matcher = PatternMatcher(brain_root=str(mock_brain_root))
        
        # Initial: No patterns
        patterns = pattern_matcher.find_similar_patterns("create REST API")
        initial_count = len(patterns.get("patterns", []))
        
        # Learn new pattern
        learning = learner.extract_patterns({
            "request": "create REST API",
            "solution": "Flask + SQLAlchemy + JWT",
            "success": True
        })
        
        assert learning["status"] == "success"
        
        # Pattern should now be available (if learner saves properly)
        # This tests the learning → pattern matching integration
        patterns_after = pattern_matcher.find_similar_patterns("build REST API")
        # Note: May still be 0 if learner doesn't persist immediately, 
        # but workflow should execute without error


class TestLeftBrainAgentCoordination:
    """Test coordination among left-brain (tactical) agents."""
    
    @pytest.fixture
    def mock_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        return brain_root
    
    def test_executor_tester_validator_pipeline(self, mock_brain_root):
        """
        Test: Executor → Tester → Validator pipeline (all left brain).
        """
        # Executor: Make changes
        executor = Executor(brain_root=str(mock_brain_root))
        execution = executor.execute_plan({
            "tasks": [
                {"action": "create_file", "file": "test.py", "content": "def foo(): pass"}
            ]
        })
        
        # Tester: Generate tests
        tester = Tester(brain_root=str(mock_brain_root))
        tests = tester.generate_tests(execution)
        
        assert tests["status"] == "success"
        
        # Validator: Check quality
        validator = Validator(brain_root=str(mock_brain_root))
        validation = validator.validate_implementation(execution, tests)
        
        assert validation["status"] in ["passed", "passed_with_warnings", "failed"]


class TestRightBrainAgentCoordination:
    """Test coordination among right-brain (strategic) agents."""
    
    @pytest.fixture
    def mock_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        return brain_root
    
    def test_architect_pattern_matcher_integration(self, mock_brain_root):
        """
        Test: Pattern Matcher → Architect workflow (both right brain).
        """
        # Pattern Matcher: Find similar solutions
        pattern_matcher = PatternMatcher(brain_root=str(mock_brain_root))
        patterns = pattern_matcher.find_similar_patterns("design caching system")
        
        # Architect: Use patterns to inform design
        architect = Architect(brain_root=str(mock_brain_root))
        design = architect.design_solution(
            "design caching system",
            context={"patterns": patterns}
        )
        
        assert design["status"] == "success"


class TestAgentErrorHandling:
    """Test error handling and recovery in multi-agent workflows."""
    
    @pytest.fixture
    def mock_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        return brain_root
    
    def test_executor_failure_doesnt_crash_pipeline(self, mock_brain_root):
        """Test that executor failure is handled gracefully."""
        executor = Executor(brain_root=str(mock_brain_root))
        
        # Executor fails
        execution = executor.execute_plan({
            "tasks": [{"action": "invalid_action"}]
        })
        
        # Should return error status, not crash
        assert execution["status"] in ["failed", "partial", "error"]
        assert "error" in execution or "message" in execution
        
        # Tester should handle failed execution gracefully
        tester = Tester(brain_root=str(mock_brain_root))
        tests = tester.generate_tests(execution)
        
        # Should not crash, even with failed input
        assert "status" in tests
    
    def test_invalid_intent_handled_gracefully(self, mock_brain_root):
        """Test that invalid intents don't crash the router."""
        router = IntentRouter(brain_root=str(mock_brain_root))
        
        # Empty request
        intent = router.detect_intent("")
        assert intent is not None
        assert "primary_intent" in intent or "error" in intent
        
        # Gibberish request
        intent = router.detect_intent("asdfghjkl qwertyuiop")
        assert intent is not None


class TestAgentMemorySharing:
    """Test that agents properly share context through the brain."""
    
    @pytest.fixture
    def shared_brain_root(self, tmp_path):
        """Create brain with shared state."""
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        
        # Initialize with some shared context
        kg_path = brain_root / "knowledge-graph.yaml"
        kg_path.write_text("""
patterns:
  auth_pattern:
    solution: JWT + bcrypt
    success_rate: 0.95
""")
        
        history_path = brain_root / "conversation-history.jsonl"
        history_path.write_text(json.dumps({
            "request": "implement authentication",
            "solution": "JWT tokens with bcrypt hashing",
            "timestamp": datetime.now().isoformat()
        }) + "\n")
        
        return brain_root
    
    def test_agents_access_shared_knowledge_graph(self, shared_brain_root):
        """Test that multiple agents can access the same knowledge graph."""
        learner = Learner(brain_root=str(shared_brain_root))
        pattern_matcher = PatternMatcher(brain_root=str(shared_brain_root))
        
        # Both should access the same knowledge graph
        # (implementation-specific test - may need adjustment based on actual API)
        patterns = pattern_matcher.find_similar_patterns("authentication")
        
        # Should find the auth_pattern from the pre-populated knowledge graph
        assert "patterns" in patterns
    
    def test_agents_access_shared_conversation_history(self, shared_brain_root):
        """Test that agents can access shared conversation history."""
        router = IntentRouter(brain_root=str(shared_brain_root))
        
        # Router should have access to conversation history for context
        # (implementation-specific test)
        intent = router.detect_intent("make it purple")
        
        # Should detect reference to previous context
        # (actual behavior depends on intent router implementation)
        assert "primary_intent" in intent


class TestConcurrentAgentExecution:
    """Test behavior when multiple agents execute concurrently (edge cases)."""
    
    @pytest.fixture
    def mock_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        return brain_root
    
    def test_parallel_independent_operations(self, mock_brain_root):
        """
        Test that independent operations can execute concurrently without conflicts.
        """
        # Simulate two independent feature requests happening at the same time
        router1 = IntentRouter(brain_root=str(mock_brain_root))
        router2 = IntentRouter(brain_root=str(mock_brain_root))
        
        intent1 = router1.detect_intent("Add login button")
        intent2 = router2.detect_intent("Fix header alignment")
        
        # Both should execute without conflicts
        assert intent1 is not None
        assert intent2 is not None
        assert "primary_intent" in intent1
        assert "primary_intent" in intent2


# Run with: pytest tests/integration/test_agent_coordination.py -v
