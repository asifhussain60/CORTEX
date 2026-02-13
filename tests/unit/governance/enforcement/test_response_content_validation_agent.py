"""
Tests for ResponseContentValidationAgent (CORE-002-RESPONSE enforcement)

Authority: CORTEX Inline-First Architecture (Response-Level Gate)
Phase: CORTEX Architecture Enhancement
"""

import pytest
from cortex.orchestrators.core.enforcement_orchestrator import (
    ResponseContentValidationAgent,
    EnforcementLevel,
)


class TestResponseContentValidationAgent:
    """Test suite for ResponseContentValidationAgent."""

    def setup_method(self):
        """Setup test agent."""
        self.agent = ResponseContentValidationAgent()

    def test_validate_empty_response(self):
        """Test validation of empty response."""
        result = self.agent.validate({"response_text": ""})
        assert result.level == EnforcementLevel.PASS
        assert len(result.violations) == 0

    def test_validate_response_no_violations(self):
        """Test validation of clean response."""
        response = "Here's the analysis:\n\n- Point 1\n- Point 2\n\nAll inline!"
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.PASS
        assert len(result.violations) == 0

    def test_detect_cat_redirection_pattern(self):
        """Test detection of 'cat > file.md' pattern."""
        response = "Run: cat > analysis.md << 'EOF'\nContent here\nEOF"
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0
        assert "cat >" in result.violations[0].lower()

    def test_detect_create_file_pattern(self):
        """Test detection of create_file pattern."""
        response = 'Please run: create_file("report.md", content_var)'
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0

    def test_detect_save_as_pattern(self):
        """Test detection of 'save as' pattern."""
        response = "Save this as project-report.md for future reference"
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0

    def test_detect_generate_report_pattern(self):
        """Test detection of 'generate markdown report' pattern."""
        response = "I'll generate a detailed markdown report now"
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0

    def test_detect_echo_redirection_pattern(self):
        """Test detection of 'echo > file.md' pattern."""
        response = "echo 'Test content' > test-output.md"
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0

    def test_detect_write_to_pattern(self):
        """Test detection of 'write to' pattern."""
        response = "Write the output to metrics-report.md"
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0

    def test_allowed_exception_github_prompts(self):
        """Test that .github/prompts/ is allowed."""
        response = "Update the prompt in .github/prompts/my-prompt.md"
        result = self.agent.validate({"response_text": response})
        # Should not block since it's in allowed context
        assert result.level == EnforcementLevel.PASS or len(result.violations) == 0

    def test_allowed_exception_github_agents(self):
        """Test that .github/agents/ is allowed."""
        response = "Create agent spec in .github/agents/custom-agent.md"
        result = self.agent.validate({"response_text": response})
        # Should not block since it's in allowed context
        assert result.level == EnforcementLevel.PASS or len(result.violations) == 0

    def test_allowed_exception_readme(self):
        """Test that README.md is allowed."""
        response = "Update README.md with the new feature documentation"
        result = self.agent.validate({"response_text": response})
        # Should not block since it's in allowed context
        assert result.level == EnforcementLevel.PASS or len(result.violations) == 0

    def test_explicit_markdown_override(self):
        """Test that explicit override allows markdown."""
        response = "cat > report.md << 'EOF'\nContent\nEOF"
        result = self.agent.validate({
            "response_text": response,
            "allow_markdown_suggestions": True
        })
        assert result.level == EnforcementLevel.PASS
        assert len(result.violations) == 0
        assert result.metadata.get("explicit_override") is True

    def test_multiple_violations(self):
        """Test detection of multiple violations in one response."""
        response = """
        First, create the file: create_file("analysis.md", data)
        Then save it as output-report.md
        Finally generate a markdown report
        """
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED
        # Should detect multiple violations
        assert len(result.violations) >= 2

    def test_metadata_populated(self):
        """Test that metadata is properly populated."""
        response = "Display results inline"
        result = self.agent.validate({"response_text": response})
        
        assert "agent" in result.metadata
        assert result.metadata["agent"] == "ResponseContentValidationAgent"
        assert "rules_checked" in result.metadata
        assert "CORE-002-RESPONSE" in result.metadata["rules_checked"]
        assert "response_length" in result.metadata
        assert "patterns_checked" in result.metadata
        assert result.metadata["patterns_checked"] > 0

    def test_transform_response_cat_pattern(self):
        """Test transformation of cat redirection."""
        response = "Run: cat > analysis.md << 'EOF'\nContent\nEOF"
        transformed = ResponseContentValidationAgent.transform_response_to_inline(response)
        
        assert "cat >" not in transformed.lower() or "chat" in transformed.lower()
        assert "inline" in transformed.lower()

    def test_transform_response_create_file_pattern(self):
        """Test transformation of create_file pattern."""
        response = 'Run: create_file("output.md", data)'
        transformed = ResponseContentValidationAgent.transform_response_to_inline(response)
        
        assert "display" in transformed.lower() or "inline" in transformed.lower()

    def test_transform_response_save_as_pattern(self):
        """Test transformation of save as pattern."""
        response = "Save this analysis as report.md"
        transformed = ResponseContentValidationAgent.transform_response_to_inline(response)
        
        assert "save" not in transformed.lower() or "transcript" in transformed.lower()
        assert "inline" in transformed.lower()

    def test_transform_response_generate_report(self):
        """Test transformation of generate report pattern."""
        response = "I'll generate a markdown report for you"
        transformed = ResponseContentValidationAgent.transform_response_to_inline(response)
        
        assert "generate" not in transformed.lower() or "markdown table" in transformed.lower()
        assert "inline" in transformed.lower()

    def test_case_insensitivity(self):
        """Test that pattern matching is case-insensitive."""
        response_upper = "CAT > FILE.MD"
        response_lower = "cat > file.md"
        response_mixed = "Cat > File.Md"
        
        result_upper = self.agent.validate({"response_text": response_upper})
        result_lower = self.agent.validate({"response_text": response_lower})
        result_mixed = self.agent.validate({"response_text": response_mixed})
        
        # All should detect violations
        assert result_upper.level == EnforcementLevel.BLOCKED
        assert result_lower.level == EnforcementLevel.BLOCKED
        assert result_mixed.level == EnforcementLevel.BLOCKED

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        response = "cat  >  file.md"  # Extra spaces
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED

    def test_real_world_example_1(self):
        """Test real-world example: code analysis response."""
        response = """
        Let me analyze your code:
        
        I'll create a comprehensive analysis report:
        
        ```bash
        create_file('code-analysis-report.md', report_content)
        ```
        
        Save this as code-review-2026-02-13.md
        """
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) >= 2

    def test_real_world_example_2(self):
        """Test real-world example: security audit response."""
        response = """
        Security audit findings:
        
        - Issue 1: SQL injection vulnerability
        - Issue 2: Missing authentication
        - Issue 3: Unencrypted credentials
        
        | Severity | Component | Fix |
        |----------|-----------|-----|
        | HIGH | API | Validate inputs |
        | MEDIUM | Auth | Add MFA | 
        """
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.PASS
        # Tables are OK - it's inline content

    def test_multiple_patterns_in_same_line(self):
        """Test detection when multiple patterns appear close together."""
        response = 'Then create_file("file.md") and save as output.md'
        result = self.agent.validate({"response_text": response})
        assert result.level == EnforcementLevel.BLOCKED
        # Should detect at least the create_file or save patterns


class TestEnforcementOrchestratorIntegration:
    """Integration tests for EnforcementOrchestrator response validation."""

    def test_orchestrator_has_response_validation_method(self):
        """Test that EnforcementOrchestrator has validate_response_content method."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            EnforcementOrchestrator,
        )
        
        orchestrator = EnforcementOrchestrator()
        assert hasattr(orchestrator, "validate_response_content")
        assert callable(getattr(orchestrator, "validate_response_content"))

    def test_orchestrator_has_transform_method(self):
        """Test that EnforcementOrchestrator has transform_response_to_inline method."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            EnforcementOrchestrator,
        )
        
        orchestrator = EnforcementOrchestrator()
        assert hasattr(orchestrator, "transform_response_to_inline")
        assert callable(getattr(orchestrator, "transform_response_to_inline"))

    def test_response_validation_integration(self):
        """Test orchestrator's validate_response_content method."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            EnforcementOrchestrator,
        )
        
        orchestrator = EnforcementOrchestrator()
        response = "Display the analysis inline"
        
        result = orchestrator.validate_response_content(response)
        assert result.is_ok()
        
        # Violation case
        bad_response = "Run: create_file('report.md', data)"
        result = orchestrator.validate_response_content(bad_response)
        assert result.is_err()

    def test_response_agent_in_agents_list(self):
        """Test that ResponseContentValidationAgent is in the agents list."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            EnforcementOrchestrator,
            ResponseContentValidationAgent,
        )
        
        orchestrator = EnforcementOrchestrator()
        agent_classes = [agent.__class__ for agent in orchestrator.agents]
        
        assert ResponseContentValidationAgent in agent_classes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
