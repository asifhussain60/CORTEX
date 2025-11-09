"""Integration tests for modular ErrorCorrector agent."""

import pytest
from src.cortex_agents.error_corrector import ErrorCorrector
from src.cortex_agents.base_agent import AgentRequest


class TestErrorCorrectorIntegration:
    """Integration tests for complete error correction workflow."""
    
    def test_agent_initialization(self):
        """Test agent initializes with all components."""
        agent = ErrorCorrector()
        assert len(agent.parsers) == 5
        assert len(agent.strategies) == 4
        assert agent.path_validator is not None
        assert agent.fix_validator is not None
    
    def test_can_handle_fix_intent(self):
        """Test agent recognizes fix intents."""
        agent = ErrorCorrector()
        request = AgentRequest(
            intent="FIX",
            user_message="Fix this error",
            context={"error_output": "SyntaxError"}
        )
        assert agent.can_handle(request) is True
    
    def test_reject_non_fix_intent(self):
        """Test agent rejects non-fix intents."""
        agent = ErrorCorrector()
        request = AgentRequest(
            intent="QUERY",
            user_message="What is the error?",
            context={}
        )
        assert agent.can_handle(request) is False
    
    def test_parse_and_fix_indentation_error(self):
        """Test complete workflow for indentation error."""
        agent = ErrorCorrector()
        error_output = '''
        File "test.py", line 10
            print("hello")
        IndentationError: unexpected indent
        '''
        request = AgentRequest(
            intent="FIX",
            user_message="Fix indentation",
            context={"error_output": error_output, "file_path": "test.py"}
        )
        response = agent.execute(request)
        assert response.success is True
        assert "indentation" in response.result.get("applied_pattern", "").lower()
    
    def test_parse_and_suggest_import(self):
        """Test complete workflow for undefined name."""
        agent = ErrorCorrector()
        error_output = '''
        Traceback (most recent call last):
          File "app.py", line 5
        NameError: name 'Path' is not defined
        '''
        request = AgentRequest(
            intent="FIX",
            user_message="Fix undefined name",
            context={"error_output": error_output}
        )
        response = agent.execute(request)
        assert response.success is True or "import" in response.message.lower()
    
    def test_parse_and_suggest_package_install(self):
        """Test complete workflow for missing module."""
        agent = ErrorCorrector()
        error_output = '''
        File "script.py", line 1
        ModuleNotFoundError: No module named 'requests'
        '''
        request = AgentRequest(
            intent="FIX",
            user_message="Fix missing module",
            context={"error_output": error_output}
        )
        response = agent.execute(request)
        assert response.success is True
        assert "requests" in response.message or "install" in response.message.lower()
    
    def test_protect_cortex_tests(self):
        """Test agent refuses to fix protected paths."""
        agent = ErrorCorrector()
        error_output = "SyntaxError: invalid syntax"
        request = AgentRequest(
            intent="FIX",
            user_message="Fix error",
            context={
                "error_output": error_output,
                "file_path": "CORTEX/tests/test_agent.py"
            }
        )
        response = agent.execute(request)
        assert response.success is False
        assert "protected" in response.message.lower()
    
    def test_handle_unparseable_error(self):
        """Test agent handles unknown error formats gracefully."""
        agent = ErrorCorrector()
        error_output = "Something went wrong but no standard format"
        request = AgentRequest(
            intent="FIX",
            user_message="Fix error",
            context={"error_output": error_output}
        )
        response = agent.execute(request)
        # Should not crash, but may not find a fix
        assert response is not None
    
    def test_handle_missing_error_output(self):
        """Test agent handles missing error output."""
        agent = ErrorCorrector()
        request = AgentRequest(
            intent="FIX",
            user_message="Fix error",
            context={}
        )
        response = agent.execute(request)
        assert response.success is False
        assert "No error output" in response.message
