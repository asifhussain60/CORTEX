"""
Test suite for meta-directive filtering in IntentRouter

This test verifies that the IntentRouter correctly filters out meta-directives
like "Follow instructions in X" before intent classification.

Bug Context:
- ISSUE: When users say "Follow instructions in CORTEX.prompt.md. [actual request]",
  Copilot treats the meta-directive as the user's request and responds with
  generic help instead of processing the actual request.
- FIX: Added _filter_meta_directives() method to strip meta-directives before
  intent classification
"""

import pytest
from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.base_agent import AgentRequest


class TestMetaDirectiveFiltering:
    """Test meta-directive filtering functionality."""
    
    def setup_method(self):
        """Initialize IntentRouter for testing."""
        self.router = IntentRouter(name="TestRouter")
    
    def test_filter_follow_instructions_semicolon(self):
        """Test filtering 'Follow instructions in X;' pattern."""
        message = "Follow instructions in CORTEX.prompt.md; Should we run align as first step of deploy?"
        filtered = self.router._filter_meta_directives(message)
        
        assert filtered == "Should we run align as first step of deploy?"
        assert "Follow instructions" not in filtered
    
    def test_filter_follow_instructions_period(self):
        """Test filtering 'Follow instructions in X.' pattern."""
        message = "Follow instructions in CORTEX.prompt.md. Should we run align as first step of deploy?"
        filtered = self.router._filter_meta_directives(message)
        
        assert filtered == "Should we run align as first step of deploy?"
        assert "Follow instructions" not in filtered
    
    def test_filter_use_prompt_file(self):
        """Test filtering 'Use X.prompt.md' pattern."""
        message = "Use CORTEX.prompt.md. I'm having an issue with X"
        filtered = self.router._filter_meta_directives(message)
        
        assert filtered == "I'm having an issue with X"
        assert "Use " not in filtered or filtered.startswith("I")
    
    def test_filter_reference_file_uri(self):
        """Test filtering 'Reference file:///' pattern."""
        message = "Reference file:///d:/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md. Help me debug this"
        filtered = self.router._filter_meta_directives(message)
        
        assert filtered == "Help me debug this"
        assert "Reference file" not in filtered
    
    def test_filter_load_hash_file(self):
        """Test filtering 'Load #file:' pattern."""
        message = "Load #file:CORTEX.prompt.md; What can you do?"
        filtered = self.router._filter_meta_directives(message)
        
        assert filtered == "What can you do?"
        assert "Load #file" not in filtered
    
    def test_filter_according_to(self):
        """Test filtering 'According to X' pattern."""
        message = "According to the instructions. Create a new feature"
        filtered = self.router._filter_meta_directives(message)
        
        assert filtered == "Create a new feature"
        assert "According to" not in filtered
    
    def test_filter_newline_separated(self):
        """Test filtering when meta-directive is on first line."""
        message = "Follow instructions in CORTEX.prompt.md\nShould we run align first?"
        filtered = self.router._filter_meta_directives(message)
        
        assert "Should we run align first?" in filtered
        assert "Follow instructions" not in filtered
    
    def test_no_filtering_needed(self):
        """Test that messages without meta-directives pass through unchanged."""
        message = "Should we run align as first step of deploy?"
        filtered = self.router._filter_meta_directives(message)
        
        assert filtered == message
    
    def test_empty_after_filtering(self):
        """Test handling when only meta-directive exists (no actual request)."""
        message = "Follow instructions in CORTEX.prompt.md."
        filtered = self.router._filter_meta_directives(message)
        
        assert filtered == ""
    
    def test_case_insensitive_filtering(self):
        """Test that filtering works regardless of case."""
        message = "FOLLOW INSTRUCTIONS IN CORTEX.PROMPT.MD. Help me"
        filtered = self.router._filter_meta_directives(message)
        
        assert filtered == "Help me"
        assert "FOLLOW" not in filtered
    
    def test_execute_with_meta_directive(self):
        """Test full execute() flow with meta-directive filtering."""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Follow instructions in CORTEX.prompt.md. Should we run align orchestrator as first step of deploy orchestrator?"
        )
        
        response = self.router.execute(request)
        
        # Verify the request message was modified
        assert "Follow instructions" not in request.user_message
        assert "Should we run align" in request.user_message
        
        # Verify routing succeeded
        assert response.success
    
    def test_execute_with_empty_after_filter(self):
        """Test execute() when filtering leaves empty message."""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Follow instructions in CORTEX.prompt.md."
        )
        
        response = self.router.execute(request)
        
        # Should return error prompting for actual request
        assert not response.success
        assert "what would you like me to do" in response.message.lower()
        assert response.metadata.get("filtered_meta_directive") is True
    
    def test_multiple_patterns_in_one_message(self):
        """Test filtering only the FIRST meta-directive (expected behavior)."""
        message = "Follow instructions in X. Use Y.prompt.md. Now do the thing."
        filtered = self.router._filter_meta_directives(message)
        
        # Only first meta-directive should be filtered
        assert "Follow instructions" not in filtered
        # The rest should remain (we only filter first match)
        assert "Use Y.prompt.md" in filtered or filtered == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
