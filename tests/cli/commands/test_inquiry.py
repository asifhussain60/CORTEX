"""Tests for inquiry CLI command.

AC-ID: INQUIRY-015
Purpose: Test /ask CLI command
Author: Asif Hussain
Date: 2026-01-27
"""

from pathlib import Path
from typing import Dict, Any

import pytest

from cortex.cli.commands.inquiry import (
    AskCommand,
    CommandResult,
)


class TestAskCommandInitialization:
    """Test command initialization."""
    
    def test_create_ask_command(self) -> None:
        """Test creating AskCommand."""
        command = AskCommand()
        
        assert command is not None
        assert hasattr(command, "execute")


class TestAskCommandExecution:
    """Test command execution."""
    
    def test_execute_with_question(self, tmp_path: Path) -> None:
        """Test executing with a question."""
        command = AskCommand(repo_path=tmp_path)
        
        result = command.execute(question="How does authentication work?")
        
        assert isinstance(result, CommandResult)
        assert result.success is True
        assert result.message
        assert result.data is not None
    
    def test_execute_returns_answer(self, tmp_path: Path) -> None:
        """Test response contains answer."""
        command = AskCommand(repo_path=tmp_path)
        
        result = command.execute(question="What is this codebase?")
        
        assert result.data is not None
        assert "answer" in result.data
        assert "confidence" in result.data
        assert "repo_type" in result.data
    
    def test_execute_with_category(self, tmp_path: Path) -> None:
        """Test execution with category hint."""
        command = AskCommand(repo_path=tmp_path)
        
        result = command.execute(
            question="How is the system designed?",
            category="architecture",
        )
        
        assert result.success is True
        assert result.data["category"] == "architecture"
    
    def test_execute_with_files(self, tmp_path: Path) -> None:
        """Test execution with file hints."""
        command = AskCommand(repo_path=tmp_path)
        
        result = command.execute(
            question="What does main.py do?",
            files=["src/main.py"],
        )
        
        assert result.success is True
        assert result.data is not None
    
    def test_execute_without_question_fails(self, tmp_path: Path) -> None:
        """Test execution fails without question."""
        command = AskCommand(repo_path=tmp_path)
        
        result = command.execute(question="")
        
        assert result.success is False
        assert "required" in result.message.lower()


class TestAskCommandFormatting:
    """Test response formatting."""
    
    def test_format_includes_metadata(self, tmp_path: Path) -> None:
        """Test formatted output includes metadata."""
        command = AskCommand(repo_path=tmp_path)
        
        result = command.execute(question="Test question")
        
        assert result.data is not None
        assert "repo_type" in result.data
        assert "confidence" in result.data
    
    def test_format_includes_evidence(self, tmp_path: Path) -> None:
        """Test formatted output includes evidence."""
        command = AskCommand(repo_path=tmp_path)
        
        result = command.execute(question="Test question")
        
        assert result.data is not None
        assert "evidence" in result.data


class TestCLIIntegration:
    """Test CLI integration scenarios."""
    
    def test_help_message(self) -> None:
        """Test help message generation."""
        command = AskCommand()
        
        help_text = command.get_help()
        
        assert "ask" in help_text.lower()
        assert "question" in help_text.lower()
    
    def test_examples(self) -> None:
        """Test example commands provided."""
        command = AskCommand()
        
        examples = command.get_examples()
        
        assert len(examples) > 0
        assert all("cortex ask" in ex for ex in examples)
