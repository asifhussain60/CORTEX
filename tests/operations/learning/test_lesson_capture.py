"""
Tests for Interactive Lesson Capture (Phase 3)
Validates structured prompts, user input handling, validation, and skip functionality.

RED Phase Test Creation - These tests should fail initially.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

from src.operations.modules.learning.lesson_capture import (
    LessonCapture,
    CapturedLesson,
    ValidationError
)
from src.operations.modules.learning.commit_filter import Candidate, CommitMetadata


@pytest.fixture
def sample_candidate():
    """Create sample candidate for testing."""
    commit = CommitMetadata(
        sha="abc123",
        timestamp=datetime(2024, 12, 7, 10, 30, 0),
        author="Test Author",
        message="Fix critical bug in payment processing",
        files_changed=["payment.py", "test_payment.py", "validators.py", "api.py", "models.py"],
        lines_added=50,
        lines_deleted=20,
        net_change=30
    )
    return Candidate(
        commit=commit,
        confidence_score=0.85,
        matched_heuristics={"error_keywords": True},
        explanation="Matched error keywords: fix, bug"
    )


@pytest.fixture
def lesson_capture():
    """Create LessonCapture instance."""
    return LessonCapture()


class TestLessonCaptureInitialization:
    """Test LessonCapture initialization and configuration."""
    
    def test_initialization_loads_prompts(self, lesson_capture):
        """Test that LessonCapture loads prompt templates on init."""
        assert lesson_capture is not None
        assert hasattr(lesson_capture, 'prompts')
        assert len(lesson_capture.prompts) == 5  # problem, root_cause, solution, prevention_rules, time_cost
        
    def test_prompt_fields_are_defined(self, lesson_capture):
        """Test that all required prompt fields are defined."""
        expected_fields = ['problem', 'root_cause', 'solution', 'prevention_rules', 'time_cost']
        for field in expected_fields:
            assert field in lesson_capture.prompts
            assert 'question' in lesson_capture.prompts[field]
            assert 'validation' in lesson_capture.prompts[field]


class TestInteractivePrompting:
    """Test interactive prompt display and user input handling."""
    
    @patch('builtins.input', side_effect=["Payment processing failed due to null checks", "Missing validation", "Added null checks", "Validate inputs before processing", "2h"])
    def test_capture_lesson_with_valid_inputs(self, mock_input, lesson_capture, sample_candidate):
        """Test capturing lesson with all valid inputs."""
        result = lesson_capture.capture_lesson(sample_candidate)
        
        assert result is not None
        assert isinstance(result, CapturedLesson)
        assert result.problem == "Payment processing failed due to null checks"
        assert result.root_cause == "Missing validation"
        assert result.solution == "Added null checks"
        assert result.prevention_rules == ["Validate inputs before processing"]
        assert result.time_cost == "2h"
        assert result.commit_hash == "abc123"
        
    @patch('builtins.input', return_value="skip")
    def test_skip_candidate(self, mock_input, lesson_capture, sample_candidate):
        """Test that user can skip a candidate by typing 'skip'."""
        result = lesson_capture.capture_lesson(sample_candidate)
        
        assert result is None  # Skipped candidates return None
        
    @patch('builtins.input', side_effect=["", "skip"])  # Empty input, then skip
    def test_empty_input_reprompts(self, mock_input, lesson_capture, sample_candidate):
        """Test that empty input triggers re-prompt."""
        result = lesson_capture.capture_lesson(sample_candidate)
        
        assert result is None  # Eventually skipped
        assert mock_input.call_count == 2  # Asked twice


class TestInputValidation:
    """Test validation rules for each prompt field."""
    
    @patch('builtins.input', side_effect=["ab", "Valid problem description"])
    def test_problem_minimum_length_validation(self, mock_input, lesson_capture, sample_candidate):
        """Test that problem field requires minimum 10 characters."""
        result = lesson_capture._prompt_for_field('problem', sample_candidate)
        
        assert result == "Valid problem description"
        assert mock_input.call_count == 2  # Re-prompted due to validation failure
            
    @patch('builtins.input', side_effect=["invalid-time", "3.5h"])
    def test_time_cost_format_validation(self, mock_input, lesson_capture, sample_candidate):
        """Test that time_cost field validates format (e.g., '2h', '30m', '1.5h')."""
        result = lesson_capture._prompt_for_field('time_cost', sample_candidate)
        
        assert result == "3.5h"
        assert mock_input.call_count == 2
            
    @patch('builtins.input', return_value="Rule 1; Rule 2; Rule 3")
    def test_prevention_rules_parsing(self, mock_input, lesson_capture, sample_candidate):
        """Test that prevention_rules field parses semicolon-separated rules."""
        result = lesson_capture._prompt_for_field('prevention_rules', sample_candidate)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == "Rule 1"
        assert result[1] == "Rule 2"
        assert result[2] == "Rule 3"


class TestCandidateDisplay:
    """Test commit candidate display formatting."""
    
    def test_display_candidate_shows_commit_info(self, lesson_capture, sample_candidate):
        """Test that candidate display includes commit hash, message, and confidence."""
        display = lesson_capture._format_candidate_display(sample_candidate)
        
        assert "abc123" in display  # Commit hash
        assert "Fix critical bug" in display  # Commit message
        assert "0.85" in display or "85%" in display  # Confidence score
        assert "error_keywords" in display  # Matched heuristics
        
    def test_display_candidate_shows_file_stats(self, lesson_capture, sample_candidate):
        """Test that candidate display shows files changed and line counts."""
        display = lesson_capture._format_candidate_display(sample_candidate)
        
        assert "5" in display  # len(files_changed) = 5
        assert "50" in display  # lines_added
        assert "20" in display  # lines_deleted


class TestCapturedLessonStructure:
    """Test CapturedLesson dataclass structure."""
    
    def test_captured_lesson_has_required_fields(self):
        """Test that CapturedLesson contains all required fields."""
        lesson = CapturedLesson(
            problem="Test problem",
            root_cause="Test cause",
            solution="Test solution",
            prevention_rules=["Rule 1"],
            time_cost="1h",
            commit_hash="abc123",
            confidence=0.85
        )
        
        assert lesson.problem == "Test problem"
        assert lesson.root_cause == "Test cause"
        assert lesson.solution == "Test solution"
        assert lesson.prevention_rules == ["Rule 1"]
        assert lesson.time_cost == "1h"
        assert lesson.commit_hash == "abc123"
        assert lesson.confidence == 0.85
        
    def test_captured_lesson_validates_on_creation(self):
        """Test that CapturedLesson validates fields on instantiation."""
        with pytest.raises(ValidationError):
            CapturedLesson(
                problem="",  # Empty problem should fail
                root_cause="Test cause",
                solution="Test solution",
                prevention_rules=[],
                time_cost="invalid",
                commit_hash="abc123",
                confidence=0.85
            )
