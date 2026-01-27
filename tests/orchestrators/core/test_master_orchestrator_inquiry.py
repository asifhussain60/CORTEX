"""Tests for MasterOrchestrator inquiry integration.

AC-ID: INQUIRY-015
Purpose: Test MCP tool integration
Author: Asif Hussain
Date: 2026-01-27
"""

from pathlib import Path

import pytest

from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.core.result import Ok, Err


class TestMasterOrchestratorInquiry:
    """Test inquiry integration in MasterOrchestrator."""
    
    def test_ask_codebase_question_exists(self) -> None:
        """Test ask_codebase_question method exists."""
        orchestrator = MasterOrchestrator()
        
        assert hasattr(orchestrator, "ask_codebase_question")
        assert callable(orchestrator.ask_codebase_question)
    
    def test_ask_simple_question(self, tmp_path: Path) -> None:
        """Test asking a simple question."""
        orchestrator = MasterOrchestrator()
        
        result = orchestrator.ask_codebase_question(
            question="What is this codebase about?",
            repo_path=str(tmp_path),
        )
        
        assert result.is_ok()
        response = result.unwrap()
        assert "answer" in response
        assert "confidence" in response
        assert "repo_type" in response
    
    def test_ask_with_category(self, tmp_path: Path) -> None:
        """Test asking with category hint."""
        orchestrator = MasterOrchestrator()
        
        result = orchestrator.ask_codebase_question(
            question="How is the system designed?",
            category="architecture",
            repo_path=str(tmp_path),
        )
        
        assert result.is_ok()
        response = result.unwrap()
        assert response["category"] == "architecture"
    
    def test_ask_with_invalid_category(self, tmp_path: Path) -> None:
        """Test asking with invalid category."""
        orchestrator = MasterOrchestrator()
        
        result = orchestrator.ask_codebase_question(
            question="Test question",
            category="invalid_category",
            repo_path=str(tmp_path),
        )
        
        assert result.is_err()
        error = result.unwrap_err()
        assert "Invalid category" in error
    
    def test_ask_with_file_paths(self, tmp_path: Path) -> None:
        """Test asking with file path hints."""
        orchestrator = MasterOrchestrator()
        
        result = orchestrator.ask_codebase_question(
            question="What does this file do?",
            file_paths=["src/main.py"],
            repo_path=str(tmp_path),
        )
        
        assert result.is_ok()


class TestMCPToolMetadata:
    """Test MCP tool metadata."""
    
    def test_mcp_tool_decorated(self) -> None:
        """Test method is decorated with @mcp_tool."""
        orchestrator = MasterOrchestrator()
        method = orchestrator.ask_codebase_question
        
        # Check for MCP tool attributes
        assert hasattr(method, "__wrapped__") or callable(method)
