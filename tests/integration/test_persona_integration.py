"""
Integration tests for Phase 37 persona system.

Tests end-to-end persona workflow: inference → styling → injection.

AC_START: AC-PHASE37.4-001
"""

import pytest
from typing import Dict, Any

# GREEN phase - implementation complete
from cortex.orchestrators.core.persona_orchestrator import PersonaOrchestrator


class TestPersonaIntegration:
    """Test complete persona workflow integration."""
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_end_to_end_persona_flow(self):
        """Should execute complete persona flow from inference to styling."""
        orchestrator = PersonaOrchestrator()
        
        # Simulate engineer context
        context = {
            "query": "How do I optimize this algorithm?",
            "file_path": "cortex/core/optimizer.py",
            "vocabulary_complexity": 0.85
        }
        
        # Execute inference
        result = orchestrator.process_request(
            query=context["query"],
            context=context
        )
        
        assert result["persona_id"] == "engineer"
        assert result["depth_id"] in ["standard", "detailed", "full"]
        
        # Test styling separately
        styled = orchestrator.style_response("Test response")
        assert len(styled) > 0
        
        # Test injection separately
        injected = orchestrator.inject_persona_context("{{PERSONA_INJECTION_POINT}}")
        assert "{{PERSONA_INJECTION_POINT}}" not in injected
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_persona_command_updates_state(self):
        """Should update persona state via /persona command."""
        orchestrator = PersonaOrchestrator()
        
        # Execute command
        result = orchestrator.execute_command("/persona set business_leader")
        
        assert result["success"] is True
        assert result["persona_id"] == "business_leader"
        
        # Verify state persists
        state = orchestrator.get_current_state()
        assert state["persona_id"] == "business_leader"
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_detail_command_with_ttl(self):
        """Should handle detail override with TTL correctly."""
        orchestrator = PersonaOrchestrator()
        
        # Set depth with 2 turns
        orchestrator.execute_command("/detail set executive 2")
        
        # First turn
        state1 = orchestrator.get_current_state()
        assert state1["depth_id"] == "executive"
        orchestrator.consume_turn()
        
        # Second turn (still active)
        state2 = orchestrator.get_current_state()
        assert state2["depth_id"] == "executive"
        orchestrator.consume_turn()
        
        # Third turn (expired, back to default)
        state3 = orchestrator.get_current_state()
        assert state3["depth_id"] != "executive"  # Should be persona default
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_persona_switching_mid_session(self):
        """Should handle persona switching correctly."""
        orchestrator = PersonaOrchestrator()
        
        # Start as engineer
        orchestrator.execute_command("/persona set engineer")
        state1 = orchestrator.get_current_state()
        assert state1["persona_id"] == "engineer"
        
        # Switch to business_leader
        orchestrator.execute_command("/persona set business_leader")
        state2 = orchestrator.get_current_state()
        assert state2["persona_id"] == "business_leader"
        
        # Depth should reset to new persona's default
        assert state2["depth_id"] == state2.get("persona_default_depth", "executive")
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_response_styling_applies_word_limits(self):
        """Should enforce persona word limits on responses."""
        orchestrator = PersonaOrchestrator()
        
        # Set business_leader (100 word limit)
        orchestrator.execute_command("/persona set business_leader")
        orchestrator.execute_command("/detail set executive")
        
        # Long response
        long_response = "This is a test response. " * 100  # ~500 words
        
        styled = orchestrator.style_response(long_response)
        word_count = len(styled.split())
        
        assert word_count <= 100  # Executive = 100 words
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_prompt_injection_with_active_persona(self):
        """Should inject persona context into prompts."""
        orchestrator = PersonaOrchestrator()
        
        orchestrator.execute_command("/persona set tech_lead")
        orchestrator.execute_command("/detail set detailed")
        
        prompt_template = """
You are CORTEX.

{{PERSONA_INJECTION_POINT}}

Follow these rules...
"""
        
        injected = orchestrator.inject_persona_context(prompt_template)
        
        assert "{{PERSONA_INJECTION_POINT}}" not in injected
        assert "tech_lead" in injected.lower() or "tech lead" in injected.lower()
        assert "detailed" in injected.lower()
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_unknown_persona_falls_back_to_default(self):
        """Should fall back to default persona when inference uncertain."""
        orchestrator = PersonaOrchestrator()
        
        # Ambiguous context - empty query
        context = {
            "query": ""
        }
        
        result = orchestrator.process_request(
            query=context["query"],
            context=context
        )
        
        # Should return unknown or default to engineer (low confidence)
        assert result["persona_id"] in ["unknown", "engineer", "product_owner", "scrum_master", "tech_lead"]
        assert result["confidence"] < 0.7  # Low confidence
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_metrics_filtering_by_persona(self):
        """Should filter metrics based on persona preferences."""
        orchestrator = PersonaOrchestrator()
        
        orchestrator.execute_command("/persona set business_leader")
        
        response = "Coverage: 85%, Complexity: 12, ROI: $150k"
        metrics = {
            "coverage": 85,
            "complexity": 12,
            "ROI": "150k"
        }
        
        styled = orchestrator.style_response(response, available_metrics=metrics)
        
        # Business leader only wants ROI
        assert "ROI" in styled
        assert "Coverage" not in styled or "coverage" not in styled.lower()
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_code_filtering_by_persona(self):
        """Should filter code blocks based on persona show_code setting."""
        orchestrator = PersonaOrchestrator()
        
        orchestrator.execute_command("/persona set business_leader")  # show_code: false
        
        response = "Here's the fix:\n```python\ncode here\n```\nDone."
        
        styled = orchestrator.style_response(response)
        
        assert "```python" not in styled
        assert "[Code block omitted]" in styled or "[code]" in styled
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_multi_turn_session_persistence(self):
        """Should maintain persona state across multiple turns."""
        orchestrator = PersonaOrchestrator()
        
        # Turn 1: Set persona
        orchestrator.execute_command("/persona set product_owner")
        state1 = orchestrator.get_current_state()
        
        # Turn 2: Process request (should use same persona)
        orchestrator.consume_turn()
        result2 = orchestrator.process_request(
            query="What features should we prioritize?",
            context={"vocabulary_complexity": 0.4}
        )
        
        # Should still be product_owner (not re-inferred)
        assert orchestrator.get_current_state()["persona_id"] == "product_owner"
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_inference_overrides_no_explicit_persona(self):
        """Should infer persona when no explicit persona set."""
        orchestrator = PersonaOrchestrator()
        
        # No persona set - should infer from context
        context = {
            "query": "What's the business impact of this feature?",
            "vocabulary_complexity": 0.2,
            "metric_focus": True
        }
        
        result = orchestrator.process_request(
            query=context["query"],
            context=context
        )
        
        # Should infer business_leader
        assert result["persona_id"] == "business_leader"
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_session_state_serialization(self):
        """Should serialize and restore session state."""
        orchestrator = PersonaOrchestrator()
        
        # Set state
        orchestrator.execute_command("/persona set engineer")
        orchestrator.execute_command("/detail set full")
        
        # Serialize
        serialized = orchestrator.serialize_state()
        
        # Create new orchestrator and restore
        new_orchestrator = PersonaOrchestrator()
        new_orchestrator.restore_state(serialized)
        
        # Verify state restored
        state = new_orchestrator.get_current_state()
        assert state["persona_id"] == "engineer"
        assert state["depth_id"] == "full"
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_bluf_format_for_business_leader(self):
        """Should apply BLUF format for business_leader persona."""
        orchestrator = PersonaOrchestrator()
        
        orchestrator.execute_command("/persona set business_leader")
        
        response = "Long explanation about the feature. The answer is yes, we should proceed."
        
        styled = orchestrator.style_response(response)
        
        assert styled.startswith("**BLUF:**") or "BLUF:" in styled[:50]
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_invalid_command_returns_error(self):
        """Should return error for invalid commands."""
        orchestrator = PersonaOrchestrator()
        
        result = orchestrator.execute_command("/persona invalid_subcommand")
        
        assert result["success"] is False
        assert "invalid" in result["message"].lower() or "unknown" in result["message"].lower()
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_concurrent_depth_and_persona_changes(self):
        """Should handle simultaneous persona and depth changes."""
        orchestrator = PersonaOrchestrator()
        
        # Set both
        orchestrator.execute_command("/persona set tech_lead")
        orchestrator.execute_command("/detail set detailed")
        
        state = orchestrator.get_current_state()
        
        assert state["persona_id"] == "tech_lead"
        assert state["depth_id"] == "detailed"
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_depth_reset_uses_persona_default(self):
        """Should use persona's default depth after reset."""
        orchestrator = PersonaOrchestrator()
        
        orchestrator.execute_command("/persona set business_leader")
        orchestrator.execute_command("/detail set full")
        
        # Reset
        orchestrator.execute_command("/detail reset")
        
        state = orchestrator.get_current_state()
        
        # Should use business_leader's default depth (executive)
        assert state["depth_id"] == "executive"
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_sticky_depth_persists_across_turns(self):
        """Should maintain sticky depth override across turns."""
        orchestrator = PersonaOrchestrator()
        
        # Set sticky depth (no turns specified)
        orchestrator.execute_command("/detail set detailed")
        
        # Consume many turns
        for _ in range(10):
            orchestrator.consume_turn()
            state = orchestrator.get_current_state()
            assert state["depth_id"] == "detailed"
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_alias_resolution_in_commands(self):
        """Should resolve persona aliases in commands."""
        orchestrator = PersonaOrchestrator()
        
        # Use alias
        result = orchestrator.execute_command("/persona set eng")
        
        assert result["success"] is True
        assert result["persona_id"] == "engineer"  # Alias resolved
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_full_workflow_with_real_context(self):
        """Should execute complete workflow with realistic context."""
        orchestrator = PersonaOrchestrator()
        
        # Realistic scenario: User editing Python file, asking technical question
        context = {
            "query": "How should I refactor this to improve performance?",
            "file_path": "cortex/orchestrators/core/optimizer.py",
            "vocabulary_complexity": 0.88,
            "session_history": [
                {"persona": "engineer", "confidence": 0.92}
            ]
        }
        
        # Step 1: Inference
        result = orchestrator.process_request(
            query=context["query"],
            context=context
        )
        
        # Should infer engineer
        assert result["persona_id"] == "engineer"
        assert result["confidence"] >= 0.7
        
        # Step 2: Style response
        raw_response = "Refactoring should focus on algorithmic efficiency and caching."
        styled = orchestrator.style_response(
            response=raw_response,
            available_metrics={"vocabulary_complexity": 0.88}
        )
        assert len(styled) > 0
        
        # Step 3: Inject persona context into prompt
        template = "{{PERSONA_INJECTION_POINT}}\n\n" + context["query"]
        injected = orchestrator.inject_persona_context(template)
        assert "engineer" in injected.lower()
        assert context["query"] in injected


# AC_COMPLETE: AC-PHASE37.4-001 ✅ 0/20 tests (skipped, RED phase)
