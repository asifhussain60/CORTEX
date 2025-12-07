"""
Tests for Learning Librarian Agent Integration (Phase 6)
Validates agent routing, orchestration, and entry point integration.

RED Phase Test Creation - These tests should fail initially.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path

from src.cortex_agents.learning_librarian_agent import (
    LearningLibrarianAgent,
    LearningLibraryRequest,
    LearningLibraryResponse
)


@pytest.fixture
def learning_agent():
    """Create LearningLibrarianAgent instance."""
    return LearningLibrarianAgent()


@pytest.fixture
def mock_scanner():
    """Mock git history scanner."""
    with patch('src.cortex_agents.learning_librarian_agent.GitHistoryScanner') as mock:
        yield mock.return_value


@pytest.fixture
def mock_filter():
    """Mock commit filter."""
    with patch('src.cortex_agents.learning_librarian_agent.CommitFilter') as mock:
        yield mock.return_value


@pytest.fixture
def mock_capture():
    """Mock lesson capture."""
    with patch('src.cortex_agents.learning_librarian_agent.LessonCapture') as mock:
        yield mock.return_value


@pytest.fixture
def mock_detector():
    """Mock duplication detector."""
    with patch('src.cortex_agents.learning_librarian_agent.DuplicationDetector') as mock:
        yield mock.return_value


@pytest.fixture
def mock_writer():
    """Mock YAML writer."""
    with patch('src.cortex_agents.learning_librarian_agent.YAMLWriter') as mock:
        yield mock.return_value


class TestAgentRouting:
    """Test agent can_handle and intent detection."""
    
    def test_can_handle_update_learning_library(self, learning_agent):
        """Test agent handles 'update learning library' trigger."""
        request = LearningLibraryRequest(
            user_message="update learning library",
            since_hours=24
        )
        
        assert learning_agent.can_handle(request) is True
        
    def test_can_handle_capture_lessons(self, learning_agent):
        """Test agent handles 'capture lessons' trigger."""
        request = LearningLibraryRequest(
            user_message="capture lessons from last 48 hours",
            since_hours=48
        )
        
        assert learning_agent.can_handle(request) is True
        
    def test_can_handle_document_learnings(self, learning_agent):
        """Test agent handles 'document learnings' trigger."""
        request = LearningLibraryRequest(
            user_message="document learnings",
            since_hours=24
        )
        
        assert learning_agent.can_handle(request) is True
        
    def test_cannot_handle_unrelated_request(self, learning_agent):
        """Test agent rejects unrelated requests."""
        request = LearningLibraryRequest(
            user_message="run tests",
            since_hours=24
        )
        
        assert learning_agent.can_handle(request) is False


class TestOrchestration:
    """Test full workflow orchestration."""
    
    def test_orchestrate_full_workflow(
        self, 
        learning_agent, 
        mock_scanner, 
        mock_filter, 
        mock_capture, 
        mock_detector, 
        mock_writer
    ):
        """Test agent orchestrates scan → filter → capture → dedupe → write."""
        # Setup mocks
        mock_scanner.scan_commits.return_value = [MagicMock()]  # 1 commit
        mock_filter.filter_learning_candidates.return_value = [MagicMock()]  # 1 candidate
        mock_capture.capture_lesson.return_value = MagicMock()  # 1 lesson
        mock_detector.find_duplicates.return_value = []  # No duplicates
        mock_writer.append_lesson.return_value = 'git-learning-001'
        
        request = LearningLibraryRequest(
            user_message="update learning library",
            since_hours=24
        )
        
        response = learning_agent.execute(request)
        
        # Verify full workflow executed
        assert mock_scanner.scan_commits.called
        assert mock_filter.filter_learning_candidates.called
        assert mock_capture.capture_lesson.called
        assert mock_detector.find_duplicates.called
        assert mock_writer.append_lesson.called
        
        assert response.success is True
        assert response.lessons_captured == 1
        
    def test_handle_no_commits_found(self, learning_agent, mock_scanner):
        """Test graceful handling when no commits in timeframe."""
        mock_scanner.scan_commits.return_value = []
        
        request = LearningLibraryRequest(
            user_message="update learning library",
            since_hours=24
        )
        
        response = learning_agent.execute(request)
        
        assert response.success is True
        assert response.lessons_captured == 0
        assert "no commits" in response.message.lower()


class TestTimeframeParameter:
    """Test timeframe parameter extraction and handling."""
    
    def test_extract_timeframe_from_message(self, learning_agent):
        """Test timeframe extraction from natural language."""
        test_cases = [
            ("last 48 hours", 48),
            ("past 2 days", 48),
            ("last week", 168),
        ]
        
        for message, expected_hours in test_cases:
            hours = learning_agent._extract_timeframe(message)
            assert hours == expected_hours
            
    def test_default_timeframe(self, learning_agent):
        """Test default 24h timeframe when not specified."""
        request = LearningLibraryRequest(
            user_message="update learning library",
            since_hours=None
        )
        
        # Should default to 24 hours
        assert learning_agent._get_timeframe(request) == 24


class TestResponseFormatting:
    """Test response message formatting."""
    
    def test_format_success_response(self, learning_agent):
        """Test success response formatting."""
        response = learning_agent._format_response(
            success=True,
            lessons_captured=3,
            duplicates_skipped=1,
            commits_scanned=50
        )
        
        assert "3" in response.message
        assert "50" in response.message
        assert response.success is True
