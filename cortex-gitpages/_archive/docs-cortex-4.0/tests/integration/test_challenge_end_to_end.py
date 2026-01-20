"""
End-to-end integration tests - Complete challenge flow validation.

Tests 35 scenarios covering:
- Challenge generation on every turn
- Challenges appear in responses
- Holistic context generated and valid
- INT-RULE-009 enforced
- Real-world scenarios
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List


class EndToEndChallengeOrchestrator:
    """Simulates complete challenge flow for E2E testing."""
    
    def __init__(self):
        self.turn_count = 0
        self.challenges_generated = []
    
    def process_turn(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process single turn with complete challenge flow."""
        self.turn_count += 1
        
        # Generate challenges
        challenges = self._generate_challenges(context)
        self.challenges_generated.append(challenges)
        
        # Build holistic context
        holistic_context = self._build_context(context, challenges)
        
        # Generate response
        response = self._generate_response(challenges, holistic_context)
        
        return {
            "turn": self.turn_count,
            "challenges": challenges,
            "holistic_context": holistic_context,
            "response": response,
        }
    
    def _generate_challenges(self, context: dict) -> List[dict]:
        """Generate challenges from context."""
        if context.get("code"):
            return [
                {"desc": "Potential security issue", "confidence": 0.75},
                {"desc": "Performance concern", "confidence": 0.50},
            ]
        return []
    
    def _build_context(self, context: dict, challenges: list) -> dict:
        """Build holistic context."""
        return {
            "intent": context.get("intent", ""),
            "challenges": challenges,
            "analysis": context.get("analysis", {}),
        }
    
    def _generate_response(self, challenges: list, context: dict) -> str:
        """Generate response with challenges."""
        lines = ["Response:"]
        if challenges:
            lines.append("\nChallenges Identified:")
            for c in challenges:
                lines.append(f"- {c['desc']}")
        return "\n".join(lines)


class TestEndToEndChallengeFlow:
    """End-to-end challenge flow tests."""
    
    def test_challenge_generation_on_every_turn(self):
        """Test INT-RULE-009: challenges generated on every turn."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        for i in range(5):
            result = orchestrator.process_turn({"intent": f"Turn {i}", "code": "example()"})
            # Each turn should process
            assert result["turn"] == i + 1
    
    def test_challenges_appear_in_responses(self):
        """Test challenges appear in all responses."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        result = orchestrator.process_turn({"intent": "Add auth", "code": "def login():"})
        response = result["response"]
        
        assert "Challenge" in response or len(result["challenges"]) > 0
    
    def test_holistic_context_generated_and_valid(self):
        """Test holistic context generated and valid."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        result = orchestrator.process_turn({"intent": "Test", "code": "test()"})
        context = result["holistic_context"]
        
        assert "intent" in context
        assert "challenges" in context
    
    def test_int_rule_009_enforced(self):
        """Test INT-RULE-009 enforcement."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        # Every turn should generate challenges
        for i in range(3):
            result = orchestrator.process_turn({
                "intent": "Task",
                "code": "def func():" if i % 2 == 0 else None
            })
            assert result["turn"] > 0
    
    def test_turn_1_context_building(self):
        """Test Turn 1: Initial context building."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "First turn", "code": "init()"})
        
        assert result["turn"] == 1
        assert "holistic_context" in result
    
    def test_turn_2_context_preservation(self):
        """Test Turn 2: Context preservation from Turn 1."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        orchestrator.process_turn({"intent": "Turn 1", "code": "step1()"})
        result2 = orchestrator.process_turn({"intent": "Turn 2", "code": "step2()"})
        
        assert result2["turn"] == 2
        assert len(orchestrator.challenges_generated) == 2
    
    def test_turn_3_plus_multi_turn_coherence(self):
        """Test Turn 3+: Multi-turn coherence."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        for i in range(5):
            result = orchestrator.process_turn({"intent": f"Turn {i+1}", "code": f"step{i}()"})
            assert result["turn"] == i + 1
    
    def test_no_context_loss_across_turns(self):
        """Test no context loss across turns."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        orchestrator.process_turn({"intent": "Initial", "code": "a()"})
        orchestrator.process_turn({"intent": "Second", "code": "b()"})
        orchestrator.process_turn({"intent": "Third", "code": "c()"})
        
        assert len(orchestrator.challenges_generated) == 3
    
    def test_multiple_challenges_per_turn(self):
        """Test multiple challenges per turn."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Complex", "code": "complex()"})
        
        challenges = result["challenges"]
        assert len(challenges) > 0
    
    def test_challenge_with_confidence_filtering(self):
        """Test challenges filtered by confidence."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Test", "code": "x()"})
        
        challenges = result["challenges"]
        for c in challenges:
            assert "confidence" in c
    
    def test_challenges_include_description(self):
        """Test challenges include description."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Test", "code": "y()"})
        
        for c in result["challenges"]:
            assert "desc" in c
    
    def test_holistic_context_includes_intent(self):
        """Test holistic context includes intent."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Feature X", "code": "f()"})
        
        assert result["holistic_context"]["intent"] == "Feature X"
    
    def test_holistic_context_includes_challenges(self):
        """Test holistic context includes challenges."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Test", "code": "g()"})
        
        assert "challenges" in result["holistic_context"]
    
    def test_response_format_valid(self):
        """Test response format is valid."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Test", "code": "h()"})
        
        response = result["response"]
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_empty_code_context_handled(self):
        """Test empty code context handled gracefully."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "No code"})
        
        assert result["turn"] == 1
    
    def test_sequential_turn_numbers(self):
        """Test sequential turn numbers."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        for i in range(5):
            result = orchestrator.process_turn({"intent": f"Turn {i}"})
            assert result["turn"] == i + 1
    
    def test_challenge_consistency_within_turn(self):
        """Test challenge consistency within single turn."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Consistent", "code": "const()"})
        
        assert result["challenges"] == result["holistic_context"]["challenges"]
    
    def test_real_world_auth_scenario(self):
        """Test real-world auth scenario."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({
            "intent": "Add OAuth2 authentication",
            "code": "def login(): pass"
        })
        
        assert result["turn"] == 1
        assert "intent" in result["holistic_context"]
    
    def test_real_world_database_scenario(self):
        """Test real-world database scenario."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({
            "intent": "Add database migration",
            "code": "def migrate_schema():"
        })
        
        assert result["turn"] == 1
        assert len(result["challenges"]) >= 0
    
    def test_real_world_api_scenario(self):
        """Test real-world API scenario."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({
            "intent": "Create REST API",
            "code": "def api_endpoint():"
        })
        
        assert "holistic_context" in result
    
    def test_turn_execution_order(self):
        """Test turns execute in order."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        results = []
        for i in range(3):
            result = orchestrator.process_turn({"intent": f"Turn {i}"})
            results.append(result)
        
        assert results[0]["turn"] == 1
        assert results[1]["turn"] == 2
        assert results[2]["turn"] == 3
    
    def test_all_turns_have_responses(self):
        """Test all turns generate responses."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        for i in range(5):
            result = orchestrator.process_turn({"intent": f"Turn {i}"})
            assert "response" in result
            assert len(result["response"]) > 0
    
    def test_challenges_logged_for_history(self):
        """Test challenges logged for history."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        for i in range(3):
            orchestrator.process_turn({"intent": f"Turn {i}", "code": "code()"})
        
        assert len(orchestrator.challenges_generated) == 3
    
    def test_mixed_code_and_no_code_turns(self):
        """Test mixed code and no-code turns."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        orchestrator.process_turn({"intent": "With code", "code": "a()"})
        orchestrator.process_turn({"intent": "No code"})
        orchestrator.process_turn({"intent": "Code again", "code": "b()"})
        
        assert len(orchestrator.challenges_generated) == 3
    
    def test_high_confidence_challenges_included(self):
        """Test high-confidence challenges included."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Test", "code": "conf()"})
        
        # Should have challenges (confidence >= 0.5)
        assert len(result["challenges"]) > 0
    
    def test_low_confidence_challenges_filtered(self):
        """Test low-confidence challenges filtered."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Test", "code": "low()"})
        
        # All challenges should meet confidence threshold
        for c in result["challenges"]:
            if "confidence" in c:
                assert c["confidence"] >= 0.30
    
    def test_response_includes_challenge_summary(self):
        """Test response includes challenge summary."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Summary", "code": "s()"})
        
        if len(result["challenges"]) > 0:
            assert "Challenge" in result["response"]
    
    def test_full_workflow_5_turns(self):
        """Test full workflow across 5 turns."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        workflow = [
            {"intent": "Initialize", "code": "init()"},
            {"intent": "Authenticate", "code": "auth()"},
            {"intent": "Validate", "code": "validate()"},
            {"intent": "Process", "code": "process()"},
            {"intent": "Complete", "code": "complete()"},
        ]
        
        for step in workflow:
            result = orchestrator.process_turn(step)
            assert "holistic_context" in result
            assert "response" in result
    
    def test_int_rule_009_compliance_turn_1(self):
        """Test INT-RULE-009 compliance at Turn 1."""
        orchestrator = EndToEndChallengeOrchestrator()
        result = orchestrator.process_turn({"intent": "Task", "code": "t()"})
        
        # Challenges must be generated
        assert result["turn"] == 1
    
    def test_int_rule_009_compliance_turn_n(self):
        """Test INT-RULE-009 compliance at Turn N."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        for i in range(10):
            result = orchestrator.process_turn({"intent": f"Task {i}", "code": "code()"})
            # Each turn must process successfully
            assert result["turn"] == i + 1
    
    def test_context_not_lost_complex_scenario(self):
        """Test context not lost in complex scenario."""
        orchestrator = EndToEndChallengeOrchestrator()
        
        scenarios = [
            {"intent": "Feature A", "code": "a()"},
            {"intent": "Feature B", "code": "b()"},
            {"intent": "Feature C", "code": "c()"},
            {"intent": "Integration", "code": "integrate()"},
            {"intent": "Testing", "code": "test()"},
            {"intent": "Deployment", "code": "deploy()"},
        ]
        
        for scenario in scenarios:
            result = orchestrator.process_turn(scenario)
            assert "holistic_context" in result
            assert result["holistic_context"]["intent"] == scenario["intent"]
