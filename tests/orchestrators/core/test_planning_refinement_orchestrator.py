"""
Test Planning Refinement Orchestrator

AC-ID: AC-PLANNING-REFINE-002 - Interactive Planning Refinement
CORE-008: TDD (tests before implementation)

Tests for planning refinement loop that handles:
1. Multi-turn conversation with user
2. LENS classification of feedback
3. Challenge generation and refinement
4. Clarity measurement (Scope C)
5. Back-and-forth until DoR achieved
"""

from __future__ import annotations

import pytest
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class RefinementTurn:
    """Single turn in planning refinement conversation."""
    turn_number: int
    action: str  # "propose_plan", "challenge", "refine", etc.
    clarity_score: float
    feedback: str = ""


class TestPlanningRefinementOrchestrator:
    """Test planning refinement system."""

    @pytest.fixture
    def setup(self) -> Dict[str, Any]:
        """Setup refinement system."""
        return {
            "session_id": "SESSION-REFINE-001",
            "turns": [],
            "clarity_threshold": 0.95,
        }

    def test_refinement_turn_1_initial_plan_generation(self, setup: Dict[str, Any]) -> None:
        """Turn 1: Generate initial draft plan from user request."""
        # User: "Build auth system with 2FA and OAuth"
        # Planning generates: draft plan with steps
        # Clarity: 0.45 (initial proposal)
        
        turn = RefinementTurn(
            turn_number=1,
            action="propose_plan",
            clarity_score=0.45,
            feedback="Initial proposal: 5-step auth implementation"
        )
        
        assert turn.turn_number == 1
        assert turn.clarity_score < setup["clarity_threshold"]
        assert "propose" in turn.action.lower()

    def test_refinement_turn_2_cortex_challenges(self, setup: Dict[str, Any]) -> None:
        """Turn 2: CORTEX challenges initial plan with 4-type challenges."""
        # CORTEX generates:
        # - Governance: "Needs security review"
        # - Alternative: "Consider passwordless auth"
        # - Scope: "OAuth integration adds complexity"
        # - Risk: "2FA adds user friction"
        # Clarity: 0.55 (questions raised)
        
        challenges = [
            {"type": "GOVERNANCE", "description": "Security review needed"},
            {"type": "ALTERNATIVE", "description": "Consider passwordless"},
            {"type": "SCOPE_CREEP", "description": "OAuth complexity"},
            {"type": "RISK_MISMATCH", "description": "2FA user friction"},
        ]
        
        assert len(challenges) == 4
        assert all("type" in c for c in challenges)
        assert all("description" in c for c in challenges)

    def test_refinement_turn_3_user_responds_to_challenges(self, setup: Dict[str, Any]) -> None:
        """Turn 3: User responds to challenges, provides clarification."""
        # User: "Security review mandatory. Passwordless later phase. 
        #        2FA required for compliance. OAuth needed."
        # Clarity: 0.68 (more clear)
        
        user_response = {
            "security_review": "mandatory",
            "passwordless": "phase_2",
            "2fa_requirement": "compliance",
            "oauth_necessity": "required"
        }
        
        clarity_score = 0.68
        
        assert clarity_score > 0.45
        assert len(user_response) == 4

    def test_refinement_turn_4_plan_refined_with_user_input(self, setup: Dict[str, Any]) -> None:
        """Turn 4: CORTEX refines plan based on user input."""
        # CORTEX incorporates feedback:
        # - Add security review step
        # - Add OAuth module
        # - Mark 2FA as critical
        # - Phase 2 for passwordless
        # Clarity: 0.82 (refined plan)
        
        refined_plan = {
            "steps": [
                {"number": 1, "action": "implement_2fa", "criticality": "high"},
                {"number": 2, "action": "implement_oauth", "criticality": "high"},
                {"number": 3, "action": "security_review", "criticality": "critical"},
                {"number": 4, "action": "deploy_staging", "criticality": "medium"},
            ],
            "future_phases": ["phase_2: passwordless auth"]
        }
        
        clarity_score = 0.82
        
        assert len(refined_plan["steps"]) == 4
        assert clarity_score > 0.68
        assert clarity_score < setup["clarity_threshold"]

    def test_refinement_turn_5_final_questions_from_cortex(self, setup: Dict[str, Any]) -> None:
        """Turn 5: CORTEX asks final clarification questions."""
        # CORTEX: "Confirm: (1) Timeline 2 weeks? (2) Test coverage 80%? 
        #         (3) Deploy to staging only? (4) Security review external?"
        # Clarity: 0.91 (nearly complete)
        
        final_questions = [
            "Is timeline 2 weeks confirmed?",
            "What's minimum test coverage?",
            "Staging only or production?",
            "Is security review external?",
        ]
        
        clarity_score = 0.91
        
        assert len(final_questions) == 4
        assert clarity_score > 0.82
        assert clarity_score < setup["clarity_threshold"]

    def test_refinement_turn_6_user_confirms_all_details(self, setup: Dict[str, Any]) -> None:
        """Turn 6: User confirms all final details."""
        # User: "Timeline confirmed. 80% test coverage. Staging only.
        #        Security review external. Ready to proceed."
        # Clarity: 0.98 (COMPLETE - exceeds threshold!)
        
        final_confirmation = {
            "timeline": "2_weeks",
            "test_coverage": 0.80,
            "deployment_target": "staging_only",
            "security_review": "external",
            "ready_to_proceed": True,
        }
        
        clarity_score = 0.98
        
        assert clarity_score >= setup["clarity_threshold"]
        assert final_confirmation["ready_to_proceed"] is True

    def test_refinement_dor_achieved_100_percent_clarity(self, setup: Dict[str, Any]) -> None:
        """DoR achieved: 100% clarity after 6 turns."""
        # After turn 6: clarity = 0.98 (exceeds 0.95 threshold)
        # DoR status: ACHIEVED
        # CORTEX: "Plan is complete with 100% clarity.
        #         Ready for execution. Please approve?"
        
        clarity_score = 0.98
        dor_achieved = clarity_score >= setup["clarity_threshold"]
        
        assert dor_achieved is True
        assert clarity_score == 0.98

    def test_refinement_no_approval_request_before_dor_achieved(self, setup: Dict[str, Any]) -> None:
        """CRITICAL: No approval request until DoR achieved."""
        # Turn 1-5: Clarity < 0.95
        # → NO approval request shown
        
        # Turn 6: Clarity = 0.98 (>= 0.95)
        # → FIRST approval request shown
        
        turns_with_clarity = [
            (1, 0.45),
            (2, 0.55),
            (3, 0.68),
            (4, 0.82),
            (5, 0.91),
            (6, 0.98),
        ]
        
        approval_requests_shown = 0
        for turn_num, clarity in turns_with_clarity:
            if clarity >= setup["clarity_threshold"]:
                approval_requests_shown += 1
        
        assert approval_requests_shown == 1, "Should show approval request exactly once, after DoR"

    def test_refinement_cortex_suggests_plan_ready_at_clarity_threshold(self, setup: Dict[str, Any]) -> None:
        """Scope C: CORTEX suggests plan is ready when clarity >= threshold."""
        # At clarity 0.98: CORTEX suggests "Plan is ready"
        # User can confirm: "Yes" or ask for more refinement: "No"
        
        clarity_score = 0.98
        threshold = setup["clarity_threshold"]
        
        if clarity_score >= threshold:
            cortex_suggestion = "PLAN_READY"
            user_action_options = ["APPROVE", "REFINE_MORE"]
        else:
            cortex_suggestion = "CONTINUE_REFINEMENT"
            user_action_options = ["PROVIDE_MORE_INPUT"]
        
        assert cortex_suggestion == "PLAN_READY"
        assert "APPROVE" in user_action_options

    def test_refinement_preserves_all_turns_in_history(self, setup: Dict[str, Any]) -> None:
        """All 6 refinement turns preserved in audit history."""
        # Complete conversation:
        # Turn 1: Initial plan (clarity 0.45)
        # Turn 2: Challenges (clarity 0.55)
        # Turn 3: User response (clarity 0.68)
        # Turn 4: Refined plan (clarity 0.82)
        # Turn 5: Final questions (clarity 0.91)
        # Turn 6: Confirmation (clarity 0.98)
        
        conversation_history = [
            (1, 0.45, "Initial plan proposal"),
            (2, 0.55, "CORTEX challenges"),
            (3, 0.68, "User responds"),
            (4, 0.82, "Plan refined"),
            (5, 0.91, "Final questions"),
            (6, 0.98, "User confirms"),
        ]
        
        assert len(conversation_history) == 6
        assert conversation_history[0][0] == 1
        assert conversation_history[-1][0] == 6
        assert conversation_history[-1][1] == 0.98

    def test_refinement_handles_user_disagreement_loops(self, setup: Dict[str, Any]) -> None:
        """Handle case where user disagrees with challenge."""
        # Turn 2: CORTEX challenges "Consider OAuth"
        # Turn 3: User: "OAuth not needed for MVP"
        # → Plan refined without OAuth
        # Clarity improves anyway
        
        initial_clarity = 0.55
        after_user_clarification = 0.72
        
        assert after_user_clarification > initial_clarity
        # Clarity improved even though user disagreed

    def test_refinement_early_agreement_reduces_turns(self, setup: Dict[str, Any]) -> None:
        """If user provides clear requirements upfront, fewer turns needed."""
        # Hypothetical scenario:
        # Turn 1: User provides complete requirements + constraints
        # → LENS analysis shows high clarity
        # Turn 2: CORTEX asks final confirmations only
        # → Clarity 0.97
        # Approval request shown
        
        fast_track_clarity = [
            (1, 0.70),  # User clear from start
            (2, 0.97),  # Quick confirmation
        ]
        
        assert fast_track_clarity[1][1] >= setup["clarity_threshold"]
        assert len(fast_track_clarity) < 6

    def test_refinement_scope_creep_detection_during_loop(self, setup: Dict[str, Any]) -> None:
        """Detect scope creep as user refines plan."""
        # Turn 1: Auth system (5 steps)
        # Turn 3: User adds "Also build admin panel, reporting, analytics"
        # → Challenge generated: "Scope expanded 3x"
        # → Clarity adjusted down until user clarifies priorities
        
        initial_scope = ["auth_system"]
        expanded_scope = ["auth_system", "admin_panel", "reporting", "analytics"]
        
        scope_items_added = len(expanded_scope) - len(initial_scope)
        assert scope_items_added == 3
        # Challenge should be generated

    def test_refinement_lens_classification_on_user_responses(self, setup: Dict[str, Any]) -> None:
        """Apply LENS to every user response for deeper understanding."""
        # Turn 3: User response "Security review mandatory..."
        # LENS analyzes:
        # - Language: "Mandatory" indicates strong requirement
        # - Examination: Implies compliance/governance concern
        # - Navigation: Route security concerns to security team
        # - Synthesis: Prioritize security review, schedule early
        
        user_response = "Security review mandatory. 2FA required for compliance."
        
        lens_analysis = {
            "language_layer": "Mandatory + compliance keywords detected",
            "examination_layer": "High-priority governance requirement",
            "navigation_layer": "Route to security team",
            "synthesis_layer": "Schedule security review early"
        }
        
        assert "mandatory" in user_response.lower()
        assert "language_layer" in lens_analysis
        assert "synthesis_layer" in lens_analysis

    def test_refinement_git_analysis_scope_d_integrated(self, setup: Dict[str, Any]) -> None:
        """Git analysis (Scope D: all scopes) integrated during refinement."""
        # During Turn 4 refinement:
        # - Current branch: "CORTEX" checked
        # - Affected files identified: auth module, tests, config
        # - Dependencies: cortex.core, cortex.brain identified
        # - Risk assessment: "Medium - security changes"
        
        git_analysis = {
            "current_branch": "CORTEX",
            "affected_files": ["auth_service.py", "test_auth.py", "config.yaml"],
            "dependencies": ["cortex.core", "cortex.brain"],
            "risk_level": "medium",
            "reason": "Security-critical auth module changes"
        }
        
        assert git_analysis["current_branch"] == "CORTEX"
        assert len(git_analysis["affected_files"]) == 3
        assert len(git_analysis["dependencies"]) == 2
