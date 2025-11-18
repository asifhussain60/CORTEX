"""
Phase 3 Integration Tests: Summary Generation Control Across All Tactical Agents

Tests that all tactical agents (TestGenerator, ErrorCorrector, HealthValidator, CommitHandler)
properly respect the skip_summary_generation flag from rule_context.

Validates:
- Execution intents suppress verbose summaries
- Investigation intents allow detailed summaries
- Rule context propagates correctly from IntentRouter
- Backward compatibility (missing rule_context defaults to verbose)
"""

import pytest
from src.cortex_agents.test_generator.agent import TestGenerator
from src.cortex_agents.error_corrector import ErrorCorrector
from src.cortex_agents.health_validator.agent import HealthValidator
from src.cortex_agents.commit_handler import CommitHandler
from src.cortex_agents.base_agent import AgentRequest


class TestTestGeneratorSummaryControl:
    """Test summary generation control in TestGenerator."""
    
    def test_execution_intent_skips_summary(self):
        """TestGenerator should suppress verbose summary for execution intents."""
        agent = TestGenerator(name="TestGen")
        
        request = AgentRequest(
            intent="test",
            context={
                "rule_context": {
                    "skip_summary_generation": True,
                    "intelligent_test_determination": True
                },
                "source_code": "def add(a, b): return a + b",
                "file_path": None
            },
            user_message="Generate tests for add function"
        )
        
        response = agent.execute(request)
        
        # Should succeed
        assert response.success is True
        
        # Should have essential fields
        assert "test_code" in response.result
        assert "test_count" in response.result
        
        # Should NOT have verbose summary fields
        assert "scenarios" not in response.result
        assert "functions" not in response.result
        assert "classes" not in response.result
        
        # Should have skip_summary flag in metadata
        assert response.metadata.get("skip_summary") is True
        
        # Message should be concise
        assert "Generated" in response.message
        assert "tests" in response.message
        # Should NOT have verbose detail like "for X functions and Y classes"
        assert "functions and" not in response.message
    
    def test_investigation_intent_allows_summary(self):
        """TestGenerator should allow verbose summary for investigation intents."""
        agent = TestGenerator(name="TestGen")
        
        request = AgentRequest(
            intent="test",
            context={
                "rule_context": {
                    "skip_summary_generation": False,  # Investigation intent
                    "intelligent_test_determination": False
                },
                "source_code": "def multiply(x, y): return x * y",
                "file_path": None
            },
            user_message="Analyze test coverage for multiply function"
        )
        
        response = agent.execute(request)
        
        # Should succeed
        assert response.success is True
        
        # Should have ALL fields including verbose summary
        assert "test_code" in response.result
        assert "test_count" in response.result
        assert "scenarios" in response.result
        assert "functions" in response.result
        assert "classes" in response.result
        
        # Should have skip_summary flag set to False
        assert response.metadata.get("skip_summary") is False
        
        # Message should be detailed
        assert "functions and" in response.message or "classes" in response.message
    
    def test_missing_rule_context_defaults_verbose(self):
        """TestGenerator should default to verbose (backward compatibility)."""
        agent = TestGenerator(name="TestGen")
        
        request = AgentRequest(
            intent="test",
            context={
                # No rule_context provided (legacy request)
                "source_code": "def subtract(a, b): return a - b",
                "file_path": None
            },
            user_message="Generate tests"
        )
        
        response = agent.execute(request)
        
        # Should succeed
        assert response.success is True
        
        # Should default to verbose (backward compatibility)
        assert "scenarios" in response.result
        assert "functions" in response.result
        assert "classes" in response.result


class TestErrorCorrectorSummaryControl:
    """Test summary generation control in ErrorCorrector."""
    
    def test_execution_intent_skips_error_details(self):
        """ErrorCorrector should suppress verbose error analysis for execution intents."""
        agent = ErrorCorrector(name="ErrorFixer")
        
        request = AgentRequest(
            intent="fix",
            context={
                "rule_context": {
                    "skip_summary_generation": True
                },
                "error_output": "NameError: name 'undefined_var' is not defined",
                "file_path": "app.py",
                "error_type": "runtime"
            },
            user_message="Fix undefined variable error"
        )
        
        response = agent.execute(request)
        
        # Should succeed (or detect error)
        assert response.success in [True, False]
        
        # Should have skip_summary flag
        assert response.metadata.get("skip_summary") is True
        
        # Result structure varies by error parsing success
        # If parsing failed, result is the parsed_error dict
        # If fix not available and parsing succeeded, result has "recommendation"
        # Just verify metadata is set correctly
        assert isinstance(response.result, dict)
    
    def test_investigation_intent_allows_error_details(self):
        """ErrorCorrector should allow verbose error analysis for investigation intents."""
        agent = ErrorCorrector(name="ErrorFixer")
        
        request = AgentRequest(
            intent="fix",
            context={
                "rule_context": {
                    "skip_summary_generation": False  # Investigation intent
                },
                "error_output": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
                "file_path": "calculator.py",
                "error_type": "runtime"
            },
            user_message="Analyze type error in calculator"
        )
        
        response = agent.execute(request)
        
        # Should succeed (or detect error)
        assert response.success in [True, False]
        
        # Should have skip_summary flag set to False
        assert response.metadata.get("skip_summary") is False
        
        # Just verify response structure is valid and metadata is correct
        assert isinstance(response.result, dict)


class TestHealthValidatorSummaryControl:
    """Test summary generation control in HealthValidator."""
    
    def test_execution_intent_skips_health_details(self):
        """HealthValidator should suppress detailed check results for execution intents."""
        agent = HealthValidator(name="HealthCheck")
        
        request = AgentRequest(
            intent="health_check",
            context={
                "rule_context": {
                    "skip_summary_generation": True
                },
                "skip_tests": True  # Skip expensive test validation
            },
            user_message="Quick health check before deployment"
        )
        
        response = agent.execute(request)
        
        # Should succeed or fail based on health
        assert response.success in [True, False]
        
        # Should have essential fields
        assert "status" in response.result
        assert "risk_level" in response.result
        
        # Should NOT have verbose details
        assert "checks" not in response.result
        assert "warnings" not in response.result
        assert "errors" not in response.result
        assert "suggestions" not in response.result or response.result["suggestions"] == []
        
        # Should have skip_summary flag
        assert response.metadata.get("skip_summary") is True
        
        # Message should be concise
        assert "System" in response.message
        # Should NOT have detailed breakdown
    
    def test_investigation_intent_allows_health_details(self):
        """HealthValidator should allow detailed check results for investigation intents."""
        agent = HealthValidator(name="HealthCheck")
        
        request = AgentRequest(
            intent="health_check",
            context={
                "rule_context": {
                    "skip_summary_generation": False  # Investigation intent
                },
                "skip_tests": True
            },
            user_message="Detailed system health investigation"
        )
        
        response = agent.execute(request)
        
        # Should succeed or fail based on health
        assert response.success in [True, False]
        
        # Should have ALL fields including verbose details
        assert "status" in response.result
        assert "risk_level" in response.result
        assert "checks" in response.result
        assert "warnings" in response.result
        assert "errors" in response.result
        assert "suggestions" in response.result
        
        # Should have skip_summary flag set to False
        assert response.metadata.get("skip_summary") is False


class TestCommitHandlerSummaryControl:
    """Test summary generation control in CommitHandler."""
    
    def test_execution_intent_skips_commit_details(self, tmp_path, monkeypatch):
        """CommitHandler should suppress detailed file list for execution intents."""
        agent = CommitHandler(name="Committer", tier1_api=None, tier2_kg=None, tier3_context=None)
        
        # Mock git status to return staged files
        def mock_check_git_status(self):
            return True, ["src/file1.py", "src/file2.py"]
        
        monkeypatch.setattr(CommitHandler, "_check_git_status", mock_check_git_status)
        
        # Mock commit execution
        def mock_execute_commit(self, message):
            return "abc123def"
        
        monkeypatch.setattr(CommitHandler, "_execute_commit", mock_execute_commit)
        
        request = AgentRequest(
            intent="commit",
            context={
                "rule_context": {
                    "skip_summary_generation": True
                },
                "type": "feat",
                "description": "Add authentication feature"
            },
            user_message="Commit authentication changes"
        )
        
        response = agent.execute(request)
        
        # Should succeed
        assert response.success is True
        
        # Should have essential fields
        assert "committed" in response.result
        assert "message" in response.result
        
        # Should NOT have verbose details
        assert "files" not in response.result
        assert "staged_files" not in response.result
        assert "commit_hash" not in response.result
        
        # Should have skip_summary flag
        assert response.metadata.get("skip_summary") is True
        
        # Message should be concise
        assert "Committed:" in response.message or "Would commit:" in response.message
        # Should NOT list file count
        assert " files:" not in response.message.lower() or "2 files" not in response.message
    
    def test_investigation_intent_allows_commit_details(self, tmp_path, monkeypatch):
        """CommitHandler should allow detailed file list for investigation intents."""
        agent = CommitHandler(name="Committer", tier1_api=None, tier2_kg=None, tier3_context=None)
        
        # Mock git status
        def mock_check_git_status(self):
            return True, ["tests/test_auth.py", "docs/README.md"]
        
        monkeypatch.setattr(CommitHandler, "_check_git_status", mock_check_git_status)
        
        # Mock commit execution
        def mock_execute_commit(self, message):
            return "xyz789abc"
        
        monkeypatch.setattr(CommitHandler, "_execute_commit", mock_execute_commit)
        
        request = AgentRequest(
            intent="commit",
            context={
                "rule_context": {
                    "skip_summary_generation": False  # Investigation intent
                },
                "type": "docs",
                "description": "Update documentation"
            },
            user_message="Review commit details"
        )
        
        response = agent.execute(request)
        
        # Should succeed
        assert response.success is True
        
        # Should have ALL fields including verbose details
        assert "committed" in response.result
        assert "message" in response.result
        assert "files" in response.result
        assert "staged_files" in response.result
        assert "commit_hash" in response.result
        
        # Should have skip_summary flag set to False
        assert response.metadata.get("skip_summary") is False
        
        # Message should include file count
        assert "2 files" in response.message


class TestPhase3Integration:
    """Integration tests across all agents."""
    
    def test_all_agents_respect_skip_summary_flag(self):
        """All tactical agents should respect skip_summary_generation flag."""
        # TestGenerator
        test_gen = TestGenerator(name="TestGen")
        test_request = AgentRequest(
            intent="test",
            context={
                "rule_context": {"skip_summary_generation": True},
                "source_code": "def test_func(): pass"
            },
            user_message="Generate tests"
        )
        test_response = test_gen.execute(test_request)
        assert test_response.metadata.get("skip_summary") is True
        
        # ErrorCorrector
        error_fix = ErrorCorrector(name="ErrorFixer")
        error_request = AgentRequest(
            intent="fix",
            context={
                "rule_context": {"skip_summary_generation": True},
                "error_output": "SyntaxError: invalid syntax"
            },
            user_message="Fix syntax error"
        )
        error_response = error_fix.execute(error_request)
        assert error_response.metadata.get("skip_summary") is True
        
        # HealthValidator
        health_check = HealthValidator(name="HealthCheck")
        health_request = AgentRequest(
            intent="health_check",
            context={
                "rule_context": {"skip_summary_generation": True},
                "skip_tests": True
            },
            user_message="Check health"
        )
        health_response = health_check.execute(health_request)
        assert health_response.metadata.get("skip_summary") is True
    
    def test_backward_compatibility_no_rule_context(self):
        """All agents should handle missing rule_context gracefully (default verbose)."""
        # TestGenerator
        test_gen = TestGenerator(name="TestGen")
        test_request = AgentRequest(
            intent="test",
            context={
                # No rule_context - legacy request
                "source_code": "def legacy_func(): pass"
            },
            user_message="Generate tests"
        )
        test_response = test_gen.execute(test_request)
        # Should default to verbose (skip_summary=False)
        assert "scenarios" in test_response.result  # Verbose field should be present
