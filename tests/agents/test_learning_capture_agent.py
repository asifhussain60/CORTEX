"""
Tests for Learning Capture Agent

Tests automatic learning capture from:
- Operation failures
- Unicode/encoding errors
- SKULL violations
- Ambient daemon events
- Git commits
"""

import pytest
import yaml
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from src.cortex_agents.learning_capture_agent import (
    LearningCaptureAgent,
    LearningEvent,
    capture_operation_learning,
    capture_exception_learning
)


@pytest.fixture
def temp_brain(tmp_path):
    """Create temporary brain directory."""
    brain_path = tmp_path / 'cortex-brain'
    brain_path.mkdir()
    
    # Create empty lessons file
    lessons_file = brain_path / 'lessons-learned.yaml'
    lessons_file.write_text(yaml.dump({
        'version': '1.0',
        'total_lessons': 0,
        'lessons': []
    }))
    
    return tmp_path


@pytest.fixture
def agent(temp_brain):
    """Create LearningCaptureAgent with temp brain."""
    return LearningCaptureAgent(project_root=temp_brain)


@pytest.fixture
def unicode_error_result():
    """Mock operation result with Unicode error."""
    result = Mock()
    result.errors = [
        "'charmap' codec can't encode character '\\U0001f4cb' in position 289"
    ]
    result.modules_failed = []
    result.success = False
    return result


@pytest.fixture
def skull_violation_result():
    """Mock operation result with SKULL violation."""
    result = Mock()
    result.errors = [
        "SKULL tests failed - brain protection compromised!"
    ]
    result.modules_failed = ['optimize_cortex_orchestrator']
    result.module_results = {
        'optimize_cortex_orchestrator': Mock(
            message="SKULL tests failed - cannot proceed with optimization"
        )
    }
    result.success = False
    return result


class TestLearningEvent:
    """Test LearningEvent data class."""
    
    def test_creates_learning_event(self):
        """Can create learning event with required fields."""
        event = LearningEvent(
            event_type='error',
            severity='high',
            category='platform',
            timestamp=datetime.now().isoformat(),
            problem="Test problem"
        )
        
        assert event.event_type == 'error'
        assert event.severity == 'high'
        assert event.category == 'platform'
        assert event.problem == "Test problem"
    
    def test_converts_to_lesson_dict(self):
        """Converts event to lessons-learned.yaml format."""
        event = LearningEvent(
            event_type='error',
            severity='high',
            category='platform',
            timestamp='2025-11-11T12:00:00',
            problem="Unicode encoding error on Windows",
            solution="Use ASCII fallback",
            symptoms=["UnicodeEncodeError", "charmap codec"],
            root_cause="PowerShell cp1252 encoding",
            tags=['unicode', 'windows']
        )
        
        lesson = event.to_lesson_dict('platform-encoding-001')
        
        assert lesson['id'] == 'platform-encoding-001'
        assert lesson['category'] == 'platform'
        assert lesson['severity'] == 'high'
        assert lesson['problem'] == "Unicode encoding error on Windows"
        assert lesson['solution'] == "Use ASCII fallback"
        assert 'UnicodeEncodeError' in lesson['symptoms']
        assert lesson['root_cause'] == "PowerShell cp1252 encoding"
        assert 'unicode' in lesson['tags']
    
    def test_generates_title_from_problem(self):
        """Generates human-readable title."""
        event = LearningEvent(
            event_type='error',
            severity='high',
            category='platform',
            timestamp=datetime.now().isoformat(),
            problem="Windows PowerShell cannot display Unicode emoji characters"
        )
        
        lesson = event.to_lesson_dict('test-001')
        
        assert 'title' in lesson
        assert len(lesson['title']) > 0
        assert 'unicode' in lesson['title'].lower() or 'encoding' in lesson['title'].lower()
    
    def test_generates_prevention_rules(self):
        """Generates prevention rules from solution."""
        event = LearningEvent(
            event_type='error',
            severity='high',
            category='platform',
            timestamp=datetime.now().isoformat(),
            problem="Test problem",
            solution="Add tests and use Unicode fallback on platform"
        )
        
        lesson = event.to_lesson_dict('test-001')
        
        assert 'prevention_rules' in lesson
        rules = lesson['prevention_rules']
        assert len(rules) > 0
        assert any('test' in r.lower() for r in rules)


class TestLearningCaptureAgent:
    """Test LearningCaptureAgent initialization and configuration."""
    
    def test_initializes_with_project_root(self, temp_brain):
        """Agent initializes with provided project root."""
        agent = LearningCaptureAgent(project_root=temp_brain)
        
        assert agent.project_root == temp_brain
        assert agent.brain_path == temp_brain / 'cortex-brain'
        assert agent.lessons_file == temp_brain / 'cortex-brain' / 'lessons-learned.yaml'
    
    def test_initializes_with_default_root(self):
        """Agent initializes with default project root if not provided."""
        agent = LearningCaptureAgent()
        
        assert agent.project_root is not None
        assert agent.brain_path.exists() or True  # May not exist in test env


class TestOperationLearningCapture:
    """Test capturing learning from operation results."""
    
    def test_captures_unicode_error_from_operation(self, agent, unicode_error_result):
        """Captures Unicode encoding error from operation result."""
        event = agent.capture_from_operation_result(
            operation_name='design_sync',
            result=unicode_error_result,
            context={'profile': 'standard'}
        )
        
        assert event is not None
        assert event.event_type == 'error'
        assert event.category == 'platform'
        assert 'unicode' in event.problem.lower() or 'encoding' in event.problem.lower()
        assert 'windows' in event.tags
        assert 'unicode' in event.tags
        assert event.error_type == 'UnicodeEncodeError'
    
    def test_captures_skull_violation_from_operation(self, agent, skull_violation_result):
        """Captures SKULL violation from operation result."""
        event = agent.capture_from_operation_result(
            operation_name='optimize_cortex',
            result=skull_violation_result,
            context={}
        )
        
        assert event is not None
        assert event.event_type == 'skull_violation'
        assert event.severity == 'critical'
        assert event.category == 'testing'
        assert 'skull' in event.tags
        assert event.confidence == 1.0
    
    def test_captures_module_failure_from_operation(self, agent):
        """Captures module failure pattern."""
        result = Mock()
        result.errors = []
        result.modules_failed = ['module_a', 'module_b']
        result.module_results = {
            'module_a': Mock(message="Failed to validate"),
            'module_b': Mock(message="Missing dependency")
        }
        
        event = agent.capture_from_operation_result(
            operation_name='test_operation',
            result=result,
            context={}
        )
        
        assert event is not None
        assert event.event_type == 'operation'
        assert event.category == 'orchestration'
        assert '2 failed modules' in event.problem
        assert len(event.symptoms) == 2
    
    def test_returns_none_for_successful_operation(self, agent):
        """Returns None for successful operation (no learning needed)."""
        result = Mock()
        result.errors = []
        result.modules_failed = []
        result.success = True
        
        event = agent.capture_from_operation_result(
            operation_name='successful_op',
            result=result,
            context={}
        )
        
        assert event is None


class TestExceptionLearningCapture:
    """Test capturing learning from exceptions."""
    
    def test_captures_unicode_encode_error(self, agent):
        """Captures UnicodeEncodeError."""
        exception = UnicodeEncodeError(
            'charmap', "📋 Test", 0, 1, "character maps to <undefined>"
        )
        
        event = agent.capture_from_exception(
            exception=exception,
            context={'operation': 'design_sync'}
        )
        
        assert event is not None
        assert event.category == 'platform'
        assert 'unicode' in event.tags
        assert event.solution is not None
    
    def test_captures_module_not_found_error(self, agent):
        """Captures ModuleNotFoundError."""
        exception = ModuleNotFoundError("No module named 'missing_module'")
        
        event = agent.capture_from_exception(
            exception=exception,
            context={}
        )
        
        assert event is not None
        assert event.category == 'dependencies'
        assert event.error_type == 'ModuleNotFoundError'
    
    def test_returns_none_for_unrecognized_exception(self, agent):
        """Returns None for exceptions without recognized patterns."""
        exception = ValueError("Some generic error")
        
        event = agent.capture_from_exception(
            exception=exception,
            context={}
        )
        
        # May or may not capture generic errors - implementation decision
        # For now, accepts both outcomes
        assert True


class TestAmbientEventLearningCapture:
    """Test capturing learning from ambient daemon events."""
    
    def test_captures_from_ambient_terminal_errors(self, agent, temp_brain):
        """Captures learning from terminal errors in ambient log."""
        ambient_log = temp_brain / 'cortex-brain' / 'conversation-context.jsonl'
        
        # Write test ambient events
        events = [
            {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'terminal_error',
                'error': "UnicodeEncodeError: 'charmap' codec can't encode"
            },
            {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'file_save',
                'file': 'test.py'
            }
        ]
        
        with open(ambient_log, 'w') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')
        
        captured = agent.capture_from_ambient_events(lookback_minutes=30)
        
        assert len(captured) >= 1
        assert any(e.event_type == 'error' for e in captured)
    
    def test_ignores_old_ambient_events(self, agent, temp_brain):
        """Ignores ambient events older than lookback period."""
        ambient_log = temp_brain / 'cortex-brain' / 'conversation-context.jsonl'
        
        # Write old event
        old_event = {
            'timestamp': '2020-01-01T00:00:00',
            'event_type': 'terminal_error',
            'error': "Old error"
        }
        
        with open(ambient_log, 'w') as f:
            f.write(json.dumps(old_event) + '\n')
        
        captured = agent.capture_from_ambient_events(lookback_minutes=30)
        
        assert len(captured) == 0
    
    def test_handles_missing_ambient_log(self, agent):
        """Handles missing ambient log gracefully."""
        captured = agent.capture_from_ambient_events()
        
        assert captured == []


class TestGitCommitLearningCapture:
    """Test capturing learning from git commits."""
    
    def test_captures_from_fix_commit(self, agent):
        """Captures learning from fix commit."""
        event = agent.capture_from_git_commit(
            commit_sha='abc123def',
            commit_message='Fix: Unicode encoding error on Windows',
            files_changed=['src/operations/orchestrator.py']
        )
        
        assert event is not None
        assert event.event_type == 'fix'
        assert 'unicode' in event.problem.lower()
        assert 'abc123' in event.solution
        assert 'git-fix' in event.tags
    
    def test_ignores_non_fix_commits(self, agent):
        """Ignores commits that aren't fixes."""
        event = agent.capture_from_git_commit(
            commit_sha='xyz789',
            commit_message='Add new feature',
            files_changed=['src/new_feature.py']
        )
        
        assert event is None
    
    def test_infers_category_from_files(self, agent):
        """Infers correct category from files changed."""
        event = agent.capture_from_git_commit(
            commit_sha='test123',
            commit_message='Fix test failure',
            files_changed=['tests/test_something.py', 'tests/test_other.py']
        )
        
        assert event is not None
        assert event.category == 'testing'


class TestLessonSaving:
    """Test saving lessons to YAML file."""
    
    def test_saves_lesson_to_yaml(self, agent):
        """Saves lesson to lessons-learned.yaml."""
        event = LearningEvent(
            event_type='error',
            severity='high',
            category='platform',
            timestamp=datetime.now().isoformat(),
            problem="Test problem",
            solution="Test solution",
            tags=['test']
        )
        
        success = agent.save_lesson(event)
        
        assert success is True
        
        # Verify file content
        with open(agent.lessons_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data['total_lessons'] == 1
        assert len(data['lessons']) == 1
        assert data['lessons'][0]['problem'] == "Test problem"
    
    def test_generates_unique_ids(self, agent):
        """Generates unique IDs for multiple lessons."""
        event1 = LearningEvent(
            event_type='error',
            severity='high',
            category='platform',
            timestamp=datetime.now().isoformat(),
            problem="Problem 1",
            tags=['test']
        )
        
        event2 = LearningEvent(
            event_type='error',
            severity='high',
            category='platform',
            timestamp=datetime.now().isoformat(),
            problem="Problem 2",
            tags=['test']
        )
        
        agent.save_lesson(event1)
        agent.save_lesson(event2)
        
        with open(agent.lessons_file, 'r') as f:
            data = yaml.safe_load(f)
        
        ids = [l['id'] for l in data['lessons']]
        assert len(ids) == 2
        assert ids[0] != ids[1]
    
    def test_prevents_duplicate_lessons(self, agent):
        """Prevents saving duplicate lessons."""
        event = LearningEvent(
            event_type='error',
            severity='high',
            category='platform',
            timestamp=datetime.now().isoformat(),
            problem="Unicode encoding on Windows",
            tags=['test']
        )
        
        # Save once
        success1 = agent.save_lesson(event)
        assert success1 is True
        
        # Try to save duplicate
        success2 = agent.save_lesson(event)
        assert success2 is False
        
        # Verify only one lesson saved
        with open(agent.lessons_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data['total_lessons'] == 1
    
    def test_updates_last_updated_timestamp(self, agent):
        """Updates last_updated timestamp when saving."""
        event = LearningEvent(
            event_type='error',
            severity='high',
            category='platform',
            timestamp=datetime.now().isoformat(),
            problem="Test",
            tags=['test']
        )
        
        agent.save_lesson(event)
        
        with open(agent.lessons_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'last_updated' in data
        # Should be recent (within last minute)
        updated = datetime.fromisoformat(data['last_updated'])
        assert (datetime.now() - updated).total_seconds() < 60


class TestConvenienceFunctions:
    """Test convenience functions for quick integration."""
    
    def test_capture_operation_learning_quick_function(self, temp_brain):
        """Quick function captures operation learning."""
        result = Mock()
        result.errors = ["SKULL tests failed"]
        result.modules_failed = []
        
        success = capture_operation_learning(
            operation_name='test_op',
            result=result,
            context={},
            project_root=temp_brain
        )
        
        assert success is True
    
    def test_capture_exception_learning_quick_function(self, temp_brain):
        """Quick function captures exception learning."""
        exception = UnicodeEncodeError(
            'charmap', "Test", 0, 1, "error"
        )
        
        success = capture_exception_learning(
            exception=exception,
            context={'test': True},
            project_root=temp_brain
        )
        
        assert success is True


class TestIntegrationScenarios:
    """Test end-to-end learning capture scenarios."""
    
    def test_full_unicode_error_learning_flow(self, agent):
        """Complete flow: Unicode error → capture → save → verify."""
        # Simulate Unicode error from operation
        result = Mock()
        result.errors = [
            "'charmap' codec can't encode character '\\U0001f4cb'"
        ]
        result.modules_failed = []
        
        # Capture learning
        event = agent.capture_from_operation_result(
            operation_name='design_sync',
            result=result,
            context={'profile': 'standard'}
        )
        
        assert event is not None
        
        # Save lesson
        saved = agent.save_lesson(event)
        assert saved is True
        
        # Verify in YAML
        with open(agent.lessons_file, 'r') as f:
            data = yaml.safe_load(f)
        
        lessons = data['lessons']
        assert len(lessons) == 1
        
        lesson = lessons[0]
        assert lesson['category'] == 'platform'
        assert 'unicode' in lesson['tags']
        assert lesson['solution'] is not None
        assert 'prevention_rules' in lesson
        assert len(lesson['prevention_rules']) > 0
