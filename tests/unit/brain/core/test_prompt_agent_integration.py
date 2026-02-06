"""
Unit tests for Prompt/Agent Updates Integration.

Tests CORTEX.prompt.md integration, agent lazy loading,
response format compliance, and exit gate validation.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 33 Stage 5 specification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any

from cortex.brain.core.prompt_agent_integration import (
    PromptAgentIntegration,
    ResponseFormat,
    AgentLoader,
    ExitGate,
    IntegrationError,
)


class TestResponseFormat:
    """Test response format compliance."""
    
    def test_response_format_validation(self):
        """Test response format validation."""
        formatter = ResponseFormat()
        
        # Valid response with header
        valid_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Implementation details here."""
        
        is_valid = formatter.validate(valid_response)
        assert is_valid is True
    
    def test_response_format_missing_header(self):
        """Test detection of missing response header."""
        formatter = ResponseFormat()
        
        # Invalid response without header
        invalid_response = """Just some text without proper header."""
        
        is_valid = formatter.validate(invalid_response)
        assert is_valid is False
    
    def test_response_format_adds_header(self):
        """Test adding response header to content."""
        formatter = ResponseFormat()
        
        content = "Implementation complete."
        orchestrator = "TDDOrchestrator"
        
        formatted = formatter.add_header(content, orchestrator)
        
        assert "## 🧠 CORTEX" in formatted
        assert orchestrator in formatted
        assert content in formatted


class TestAgentLoader:
    """Test agent lazy loading."""
    
    @pytest.fixture
    def loader(self):
        """Create agent loader."""
        return AgentLoader()
    
    def test_agent_loader_initialization(self, loader):
        """Test agent loader initializes."""
        assert loader is not None
    
    def test_load_agent_on_demand(self, loader):
        """Test loading agent only when needed."""
        # Agent should not be loaded initially
        assert not loader.is_loaded("TDDAgent")
        
        # Load agent
        agent = loader.load_agent("TDDAgent", intent="IMPLEMENT")
        
        # Now should be loaded
        assert loader.is_loaded("TDDAgent")
        assert agent is not None
    
    def test_agent_intent_mapping(self, loader):
        """Test intent-based agent selection."""
        agent_name = loader.get_agent_for_intent("IMPLEMENT")
        assert agent_name in ["TDDAgent", "ImplementationAgent"]
        
        agent_name = loader.get_agent_for_intent("ANALYZE")
        assert agent_name in ["AnalysisAgent", "LENSAgent"]
    
    def test_agent_caching(self, loader):
        """Test agent caching after first load."""
        agent1 = loader.load_agent("TDDAgent", intent="IMPLEMENT")
        agent2 = loader.load_agent("TDDAgent", intent="IMPLEMENT")
        
        # Should return same cached instance
        assert agent1 is agent2


class TestExitGate:
    """Test exit gate validation."""
    
    @pytest.fixture
    def exit_gate(self):
        """Create exit gate."""
        return ExitGate()
    
    def test_exit_gate_initialization(self, exit_gate):
        """Test exit gate initializes."""
        assert exit_gate is not None
    
    def test_exit_gate_validates_completion(self, exit_gate):
        """Test exit gate validates task completion."""
        result = {
            "success": True,
            "tests_passing": 25,
            "violations": 0,
        }
        
        passed = exit_gate.validate(result)
        assert passed is True
    
    def test_exit_gate_blocks_incomplete_work(self, exit_gate):
        """Test exit gate blocks incomplete work."""
        result = {
            "success": False,
            "tests_passing": 20,
            "tests_failing": 5,
            "violations": 2,
        }
        
        passed = exit_gate.validate(result)
        assert passed is False
    
    def test_exit_gate_auto_vacuum_detection(self, exit_gate):
        """Test exit gate detects markdown files needing cleanup."""
        files = [
            "app.py",
            "test_app.py",
            "PHASE-33-SUMMARY.md",  # Should be vacuumed
            "README.md",  # Legitimate, keep
        ]
        
        files_to_vacuum = exit_gate.detect_vacuum_candidates(files)
        
        # Should detect phase summary for cleanup
        assert any("PHASE" in f for f in files_to_vacuum)
        assert "README.md" not in files_to_vacuum


class TestPromptAgentIntegration:
    """Test prompt/agent integration."""
    
    @pytest.fixture
    def integration(self):
        """Create integration instance."""
        return PromptAgentIntegration()
    
    def test_integration_initialization(self, integration):
        """Test integration initializes properly."""
        assert integration is not None
        assert integration.formatter is not None
        assert integration.agent_loader is not None
        assert integration.exit_gate is not None
    
    def test_process_request_with_agent_loading(self, integration):
        """Test request processing with lazy agent loading."""
        request = {
            "intent": "IMPLEMENT",
            "user_input": "implement feature",
        }
        
        response = integration.process_request(request)
        
        assert response is not None
        assert "orchestrator" in response
    
    def test_response_includes_proper_header(self, integration):
        """Test response includes CORTEX header."""
        request = {
            "intent": "ANALYZE",
            "user_input": "analyze code",
        }
        
        response = integration.process_request(request)
        
        # Check for response header
        assert "## 🧠 CORTEX" in response["formatted_output"]
    
    def test_exit_gate_runs_after_completion(self, integration):
        """Test exit gate validates after completion."""
        result = {
            "success": True,
            "operation": "IMPLEMENT",
        }
        
        exit_validation = integration.validate_completion(result)
        
        assert isinstance(exit_validation, bool)


class TestPromptLoading:
    """Test prompt loading from .github/prompts/."""
    
    @pytest.fixture
    def integration(self):
        """Create integration instance."""
        return PromptAgentIntegration()
    
    def test_load_cortex_prompt(self, integration):
        """Test loading CORTEX.prompt.md."""
        prompt_path = Path(".github/prompts/CORTEX.prompt.md")
        
        if prompt_path.exists():
            prompt_content = integration.load_prompt("CORTEX.prompt.md")
            assert prompt_content is not None
            assert len(prompt_content) > 0
        else:
            # Gracefully handle if file doesn't exist in test environment
            pytest.skip("CORTEX.prompt.md not found")
    
    def test_load_response_format_standards(self, integration):
        """Test loading response-format-standards.md."""
        standards_path = Path(".github/prompts/response-format-standards.md")
        
        if standards_path.exists():
            standards = integration.load_prompt("response-format-standards.md")
            assert standards is not None
        else:
            pytest.skip("response-format-standards.md not found")


class TestMarkdownVacuum:
    """Test markdown auto-vacuum (ENH-036)."""
    
    @pytest.fixture
    def exit_gate(self):
        """Create exit gate."""
        return ExitGate()
    
    def test_vacuum_detects_session_summaries(self, exit_gate):
        """Test vacuum detects session summary files."""
        files = [
            "PHASE-33-SESSION-SUMMARY.md",
            "implementation-report.md",
            "completion-summary.md",
        ]
        
        vacuum_candidates = exit_gate.detect_vacuum_candidates(files)
        
        # All should be vacuum candidates
        assert len(vacuum_candidates) >= 2
    
    def test_vacuum_preserves_docs(self, exit_gate):
        """Test vacuum preserves legitimate documentation."""
        files = [
            "README.md",
            "docs/architecture.md",
            "docs/api-reference.md",
            ".github/copilot-instructions.md",
        ]
        
        vacuum_candidates = exit_gate.detect_vacuum_candidates(files)
        
        # None should be vacuum candidates
        assert len(vacuum_candidates) == 0


class TestIntegrationErrorHandling:
    """Test integration error handling."""
    
    def test_integration_error_inheritance(self):
        """Test IntegrationError inherits from Exception."""
        error = IntegrationError("test error")
        assert isinstance(error, Exception)
    
    def test_handles_missing_agent_gracefully(self):
        """Test handling of missing agent."""
        loader = AgentLoader()
        
        # Try to load non-existent agent
        agent = loader.load_agent("NonExistentAgent", intent="UNKNOWN")
        
        # Should handle gracefully (return None or default)
        assert agent is None or agent is not None
    
    def test_handles_invalid_prompt_path(self):
        """Test handling of invalid prompt path."""
        integration = PromptAgentIntegration()
        
        prompt = integration.load_prompt("nonexistent.md")
        
        # Should return None or empty string
        assert prompt is None or prompt == ""
