"""
Tests for Interactive Planning Session

Purpose: TDD tests for collaborative planning with context discovery,
         user approval loops, and cleanup phase validation.

Author: CORTEX Development Team
Created: 2025-12-29
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
from enum import Enum


# Import session classes (to be created)
try:
    from src.orchestrators.planning.interactive_session import (
        PlanningSession,
        SessionState,
        DiscoveryEngine,
        ApprovalWorkflow,
        CleanupPhase
    )
except ImportError:
    # Create placeholder for initial RED phase
    class SessionState(Enum):
        INITIALIZING = "initializing"
        DISCOVERY = "discovery"
        CONTEXT_GATHERING = "context_gathering"
        DRAFTING = "drafting"
        USER_REVIEW = "user_review"
        REFINING = "refining"
        APPROVED = "approved"
        CLEANUP = "cleanup"
        FINALIZED = "finalized"
    
    class PlanningSession:
        pass
    
    class DiscoveryEngine:
        pass
    
    class ApprovalWorkflow:
        pass
    
    class CleanupPhase:
        pass


class TestPlanningSessionInitialization:
    """Test session creation and state management."""
    
    def test_session_creation_with_plan_name(self):
        """
        RED TEST: Create planning session with plan name and user context.
        """
        session = PlanningSession(
            plan_name="user-authentication",
            user_context={"target_audience": "developers", "duration": "60min"}
        )
        
        assert session.plan_name == "user-authentication"
        assert session.state == SessionState.INITIALIZING
        assert session.session_id is not None
        assert len(session.session_id) > 0
        assert session.created_at is not None
    
    def test_session_tracks_conversation_history(self):
        """
        RED TEST: Session must track all Q&A exchanges.
        """
        session = PlanningSession(plan_name="test-plan")
        
        session.add_exchange(
            question="What is the target audience?",
            answer="New developers"
        )
        
        assert len(session.conversation_history) == 1
        assert session.conversation_history[0]["question"] == "What is the target audience?"
        assert session.conversation_history[0]["answer"] == "New developers"
    
    def test_session_state_transitions(self):
        """
        RED TEST: Session must transition through defined states.
        """
        session = PlanningSession(plan_name="test-plan")
        
        # Valid transitions
        assert session.can_transition_to(SessionState.DISCOVERY)
        session.transition_to(SessionState.DISCOVERY)
        assert session.state == SessionState.DISCOVERY
        
        assert session.can_transition_to(SessionState.CONTEXT_GATHERING)
        session.transition_to(SessionState.CONTEXT_GATHERING)
        assert session.state == SessionState.CONTEXT_GATHERING
        
        # Invalid transition (can't skip states)
        assert not session.can_transition_to(SessionState.FINALIZED)


class TestDiscoveryQuestions:
    """Test discovery phase with DoR questions."""
    
    def test_generate_discovery_questions_for_plan_type(self):
        """
        RED TEST: Generate relevant questions based on plan type.
        """
        engine = DiscoveryEngine()
        
        questions = engine.generate_questions(
            plan_name="user-authentication",
            plan_type="feature"
        )
        
        assert len(questions) >= 5
        assert any("audience" in q.lower() for q in questions)
        assert any("learn" in q.lower() or "achieve" in q.lower() for q in questions)
        assert any("time" in q.lower() or "duration" in q.lower() for q in questions)
    
    def test_questions_adapt_to_plan_context(self):
        """
        RED TEST: Questions should be contextual to plan name.
        """
        engine = DiscoveryEngine()
        
        auth_questions = engine.generate_questions("user-authentication", "feature")
        onboard_questions = engine.generate_questions("onboarding-system", "guide")
        
        # Auth plan should ask about security
        assert any("security" in q.lower() or "auth" in q.lower() for q in auth_questions)
        
        # Onboarding plan should ask about learning
        assert any("learn" in q.lower() or "onboard" in q.lower() for q in onboard_questions)


class TestContextDiscoveryEngine:
    """Test AST analysis, code graph building, brain consultation."""
    
    def test_ast_analysis_discovers_related_code(self):
        """
        RED TEST: AST parser finds related classes/functions in codebase.
        """
        engine = DiscoveryEngine(cortex_root=Path("/fake/cortex"))
        
        # Simulate user wants to plan "add logging feature"
        context = engine.discover_context(
            plan_name="add-logging-feature",
            target_area="src/core/",
            user_answers={"scope": "application-wide logging"}
        )
        
        assert "ast_analysis" in context
        assert "discovered_files" in context["ast_analysis"]
        assert "dependencies" in context["ast_analysis"]
    
    def test_code_graph_identifies_impact_zones(self):
        """
        RED TEST: Code graph shows what files will be affected.
        """
        engine = DiscoveryEngine(cortex_root=Path("/fake/cortex"))
        
        context = engine.discover_context(
            plan_name="refactor-database-layer",
            target_area="src/database/",
            user_answers={"changes": "move to SQLAlchemy"}
        )
        
        assert "code_graph" in context
        assert "impacted_files" in context["code_graph"]
        assert "dependency_count" in context["code_graph"]
    
    def test_brain_consultation_finds_similar_plans(self):
        """
        RED TEST: Brain queries knowledge graph for similar past plans.
        """
        engine = DiscoveryEngine(cortex_root=Path("/fake/cortex"))
        
        context = engine.discover_context(
            plan_name="add-user-authentication",
            target_area="src/auth/",
            user_answers={}
        )
        
        assert "brain_insights" in context
        assert "similar_plans" in context["brain_insights"]
        assert "lessons_learned" in context["brain_insights"]
    
    def test_context_gathering_presents_findings_to_user(self):
        """
        RED TEST: Findings formatted for user review and approval.
        """
        engine = DiscoveryEngine(cortex_root=Path("/fake/cortex"))
        
        context = engine.discover_context(
            plan_name="test-plan",
            target_area="src/",
            user_answers={}
        )
        
        presentation = engine.format_findings_for_user(context)
        
        assert "summary" in presentation
        assert "discovered_files" in presentation
        assert "impact_analysis" in presentation
        assert "recommendations" in presentation


class TestUserApprovalWorkflow:
    """Test iterative refinement and user approval loop."""
    
    def test_present_findings_to_user(self):
        """
        RED TEST: Present discovered context and wait for approval.
        """
        workflow = ApprovalWorkflow()
        
        findings = {
            "discovered_files": ["src/auth/login.py", "src/auth/session.py"],
            "impact_analysis": "2 files will be modified, 5 tests need updates",
            "recommendations": ["Add rate limiting", "Implement JWT tokens"]
        }
        
        presentation = workflow.create_presentation(findings)
        
        assert "📋 Discovered Context" in presentation
        assert "src/auth/login.py" in presentation
        assert "Do you approve these findings?" in presentation
    
    def test_user_can_request_refinements(self):
        """
        RED TEST: User can provide feedback to refine discoveries.
        """
        workflow = ApprovalWorkflow()
        session = PlanningSession(plan_name="test")
        
        feedback = {
            "approved": False,
            "changes_requested": [
                "Don't modify session.py, only login.py",
                "Add OAuth2 support to recommendations"
            ]
        }
        
        refinement_needed = workflow.process_feedback(session, feedback)
        
        assert refinement_needed is True
        assert len(session.refinement_requests) == 2
    
    def test_approval_transitions_to_drafting(self):
        """
        RED TEST: User approval moves session to drafting state.
        """
        workflow = ApprovalWorkflow()
        session = PlanningSession(plan_name="test")
        session.state = SessionState.USER_REVIEW
        
        feedback = {"approved": True, "notes": "Looks good!"}
        
        workflow.process_feedback(session, feedback)
        
        assert session.state == SessionState.APPROVED
        assert session.approval_timestamp is not None
    
    def test_iterative_refinement_loop(self):
        """
        RED TEST: Multiple refinement iterations until approval.
        """
        workflow = ApprovalWorkflow()
        session = PlanningSession(plan_name="test")
        
        # Iteration 1: Not approved
        feedback1 = {"approved": False, "changes_requested": ["Add more files"]}
        assert workflow.process_feedback(session, feedback1) is True
        
        # Iteration 2: Still not approved
        feedback2 = {"approved": False, "changes_requested": ["Different approach"]}
        assert workflow.process_feedback(session, feedback2) is True
        
        # Iteration 3: Approved
        feedback3 = {"approved": True}
        assert workflow.process_feedback(session, feedback3) is False
        
        assert session.refinement_count == 2
        assert session.state == SessionState.APPROVED


class TestCleanupPhaseOrchestrator:
    """Test holistic code review and documentation generation."""
    
    def test_cleanup_phase_reviews_all_modified_files(self):
        """
        RED TEST: Cleanup reviews every file modified in plan.
        """
        cleanup = CleanupPhase(cortex_root=Path("/fake/cortex"))
        
        plan_data = {
            "modified_files": [
                "src/auth/login.py",
                "src/auth/session.py",
                "tests/test_auth.py"
            ]
        }
        
        review_result = cleanup.holistic_code_review(plan_data)
        
        assert "files_reviewed" in review_result
        assert len(review_result["files_reviewed"]) == 3
        assert "issues_found" in review_result
        assert "suggestions" in review_result
    
    def test_cleanup_validates_codebase_not_broken(self):
        """
        RED TEST: Cleanup ensures no broken imports or dependencies.
        """
        cleanup = CleanupPhase(cortex_root=Path("/fake/cortex"))
        
        plan_data = {
            "modified_files": ["src/core/database.py"],
            "new_dependencies": ["sqlalchemy"]
        }
        
        validation = cleanup.validate_codebase_integrity(plan_data)
        
        assert "import_check" in validation
        assert "dependency_check" in validation
        assert "syntax_check" in validation
        assert validation["is_valid"] in [True, False]
    
    def test_cleanup_generates_pdoc3_documentation(self):
        """
        RED TEST: Cleanup generates pdoc3 docs for learning library.
        """
        cleanup = CleanupPhase(cortex_root=Path("/fake/cortex"))
        
        plan_data = {
            "plan_name": "add-user-authentication",
            "modified_files": ["src/auth/login.py"],
            "learning_outcomes": [
                "Implemented JWT authentication",
                "Added rate limiting",
                "Created session management"
            ]
        }
        
        doc_result = cleanup.generate_learning_documentation(plan_data)
        
        assert "doc_path" in doc_result
        assert "pdoc3" in doc_result["doc_path"] or "learning-library" in doc_result["doc_path"]
        assert doc_result["format"] == "pdoc3"
        assert "generated_files" in doc_result
    
    def test_cleanup_adds_to_knowledge_graph(self):
        """
        RED TEST: Cleanup updates brain with lessons learned.
        """
        cleanup = CleanupPhase(cortex_root=Path("/fake/cortex"))
        
        plan_data = {
            "plan_name": "test-plan",
            "phases": [{"name": "Implementation", "duration": "2h"}],
            "outcomes": ["Feature completed", "Tests passing"],
            "challenges": ["Rate limiting was tricky"]
        }
        
        brain_update = cleanup.update_knowledge_graph(plan_data)
        
        assert "knowledge_entries_added" in brain_update
        assert "lessons_learned_count" in brain_update
        assert brain_update["success"] is True


class TestEndToEndInteractivePlanning:
    """Integration test for complete interactive planning flow."""
    
    def test_full_interactive_planning_workflow(self, tmp_path, monkeypatch):
        """
        RED TEST: Complete flow from initialization to finalization.
        
        Flow:
        1. Initialize session
        2. Discovery questions
        3. Context gathering (AST/graph/brain)
        4. User approval loop
        5. Draft plan generation
        6. Cleanup phase
        7. Finalization
        """
        # Create minimal cortex structure with required directories
        cortex_root = tmp_path / "cortex"
        cortex_brain = cortex_root / "cortex-brain"
        planning_root = cortex_brain / "documents" / "planning" / "active"
        planning_root.mkdir(parents=True)
        
        (cortex_root / "cortex-toolkit" / "core" / "utilities").mkdir(parents=True)
        
        # Create dummy plan_scaffold_generator.py
        scaffold_module = cortex_root / "cortex-toolkit" / "core" / "utilities" / "plan_scaffold_generator.py"
        scaffold_module.write_text("""
class PlanScaffoldGenerator:
    def __init__(self, cortex_root=None):
        self.cortex_root = cortex_root
        
    def create_scaffold(self, plan_name, plan_type="feature"):
        return {
            "status": "created",
            "plan_name": plan_name,
            "folder_name": f"{plan_type}s/active/{plan_name}"
        }
""")
        
        # Now import and test
        from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator
        
        config = {"cortex_root": str(cortex_root)}
        orchestrator = PlanningOrchestrator(config)
        
        # Should have interactive mode
        assert hasattr(orchestrator, 'interactive_plan_creation')
        
        # Start interactive session
        session = orchestrator.interactive_plan_creation(
            plan_name="test-feature",
            user_context={"target": "developers"}
        )
        
        # Session should be created
        assert session is not None
        assert session.state == SessionState.DISCOVERY
        
        # Mock user answers to discovery questions
        answers = {
            "target_audience": "developers",
            "duration": "60min",
            "scope": "authentication feature"
        }
        
        # Context gathering should happen
        session.add_answers(answers)
        context = session.discover_context()
        
        assert context is not None
        assert "ast_analysis" in context or "code_graph" in context
        
        # User approval
        session.approve_context()
        assert session.state == SessionState.APPROVED
        
        # Drafting phase
        session.transition_to(SessionState.DRAFTING)
        assert session.state == SessionState.DRAFTING
        
        # Cleanup phase
        session.transition_to(SessionState.CLEANUP)
        cleanup_result = session.execute_cleanup()
        
        assert cleanup_result["code_review_passed"]
        assert "documentation_generated" in cleanup_result
        
        # Finalization
        session.transition_to(SessionState.FINALIZED)
        assert session.state == SessionState.FINALIZED


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
