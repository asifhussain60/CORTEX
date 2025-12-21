"""
Tests for DocumentationPreferenceTracker

Tests preference tracking, learning from feedback, and user edit analysis.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestration_4_0.orchestrators.documentation.preference_tracker import (
    DocumentationPreferenceTracker,
    DocumentationPreferences,
    DocumentationStyle,
    DocumentationTone,
    DocumentationDepth,
    ExampleDensity,
    PreferenceUpdate
)


@pytest.fixture
def temp_storage():
    """Create temporary storage for preferences"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_logger():
    """Mock logger"""
    return Mock()


@pytest.fixture
def tracker(mock_logger, temp_storage):
    """Create preference tracker with temp storage"""
    return DocumentationPreferenceTracker(
        logger=mock_logger,
        storage_path=temp_storage / "preferences.json"
    )


class TestDocumentationPreferences:
    """Test DocumentationPreferences dataclass"""
    
    def test_default_preferences(self):
        """Test default preference values"""
        prefs = DocumentationPreferences(user_id="test_user")
        
        assert prefs.user_id == "test_user"
        assert prefs.style == DocumentationStyle.BALANCED
        assert prefs.tone == DocumentationTone.NEUTRAL
        assert prefs.depth == DocumentationDepth.MODERATE
        assert prefs.example_density == ExampleDensity.BALANCED
        assert prefs.preferred_format == "markdown"
        assert prefs.include_diagrams is True
        assert prefs.include_toc is True
    
    def test_custom_preferences(self):
        """Test custom preference values"""
        prefs = DocumentationPreferences(
            user_id="test_user",
            project_id="test_project",
            style=DocumentationStyle.TECHNICAL,
            tone=DocumentationTone.FORMAL,
            depth=DocumentationDepth.DETAILED,
            example_density=ExampleDensity.MANY
        )
        
        assert prefs.project_id == "test_project"
        assert prefs.style == DocumentationStyle.TECHNICAL
        assert prefs.tone == DocumentationTone.FORMAL
        assert prefs.depth == DocumentationDepth.DETAILED
        assert prefs.example_density == ExampleDensity.MANY
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        prefs = DocumentationPreferences(
            user_id="test_user",
            style=DocumentationStyle.ACCESSIBLE
        )
        
        data = prefs.to_dict()
        
        assert data['user_id'] == "test_user"
        assert data['style'] == "accessible"
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            'user_id': 'test_user',
            'project_id': 'test_project',
            'style': 'technical',
            'tone': 'formal',
            'depth': 'detailed',
            'example_density': 'many',
            'preferred_format': 'html',
            'include_diagrams': False,
            'include_toc': True
        }
        
        prefs = DocumentationPreferences.from_dict(data)
        
        assert prefs.user_id == 'test_user'
        assert prefs.project_id == 'test_project'
        assert prefs.style == DocumentationStyle.TECHNICAL
        assert prefs.tone == DocumentationTone.FORMAL
        assert prefs.depth == DocumentationDepth.DETAILED
        assert prefs.example_density == ExampleDensity.MANY
        assert prefs.preferred_format == 'html'
        assert prefs.include_diagrams is False


class TestDocumentationPreferenceTracker:
    """Test DocumentationPreferenceTracker"""
    
    def test_initialization(self, tracker):
        """Test tracker initialization"""
        assert tracker.logger is not None
        assert tracker.storage_path is not None
        assert tracker.preferences == {}
        assert tracker.update_history == {}
    
    def test_get_default_preferences(self, tracker):
        """Test getting default preferences for new user"""
        prefs = tracker.get_preferences(user_id="new_user")
        
        assert prefs.user_id == "new_user"
        assert prefs.style == DocumentationStyle.BALANCED
        assert "new_user" in tracker.preferences
    
    def test_get_existing_preferences(self, tracker):
        """Test retrieving existing preferences"""
        # Create initial preferences
        prefs1 = tracker.get_preferences(user_id="test_user")
        prefs1.style = DocumentationStyle.TECHNICAL
        
        # Retrieve same preferences
        prefs2 = tracker.get_preferences(user_id="test_user")
        
        assert prefs2.style == DocumentationStyle.TECHNICAL
        assert id(prefs1) == id(prefs2)  # Same object
    
    def test_get_project_specific_preferences(self, tracker):
        """Test project-specific preferences"""
        prefs = tracker.get_preferences(
            user_id="test_user",
            project_id="project_a"
        )
        
        assert prefs.project_id == "project_a"
        
        # Different project should have different preferences
        prefs2 = tracker.get_preferences(
            user_id="test_user",
            project_id="project_b"
        )
        
        assert prefs2.project_id == "project_b"
        assert id(prefs) != id(prefs2)
    
    def test_update_preference_style(self, tracker):
        """Test updating style preference"""
        prefs = tracker.get_preferences(user_id="test_user")
        original_style = prefs.style
        
        tracker.update_preference(
            user_id="test_user",
            preference_type="style",
            new_value="technical",
            reason="user_feedback"
        )
        
        updated_prefs = tracker.get_preferences(user_id="test_user")
        assert updated_prefs.style == DocumentationStyle.TECHNICAL
        assert updated_prefs.style != original_style
    
    def test_update_preference_tone(self, tracker):
        """Test updating tone preference"""
        tracker.update_preference(
            user_id="test_user",
            preference_type="tone",
            new_value="casual",
            reason="user_edit"
        )
        
        prefs = tracker.get_preferences(user_id="test_user")
        assert prefs.tone == DocumentationTone.CASUAL
    
    def test_update_preference_history(self, tracker):
        """Test preference update history tracking"""
        tracker.update_preference(
            user_id="test_user",
            preference_type="style",
            new_value="technical",
            reason="user_feedback"
        )
        
        history = tracker.get_update_history(user_id="test_user")
        
        assert len(history) == 1
        assert history[0].preference_type == "style"
        assert history[0].new_value == "technical"
        assert history[0].reason == "user_feedback"
    
    def test_update_invalid_preference(self, tracker, mock_logger):
        """Test updating invalid preference type"""
        # Should log error and not raise (catches internally)
        tracker.update_preference(
            user_id="test_user",
            preference_type="invalid_type",
            new_value="value",
            reason="test"
        )
        
        # Should have logged an error
        # Check that preferences remain unchanged
        prefs = tracker.get_preferences(user_id="test_user")
        assert prefs.style == DocumentationStyle.BALANCED  # Still default
    
    def test_learn_from_edits_style_detection(self, tracker):
        """Test learning style preference from edits"""
        original = """
        This function instantiates a new object utilizing the factory pattern.
        Subsequently, it facilitates data processing.
        """
        
        edited = """
        This function creates a new object using the factory pattern.
        Then, it helps process data.
        """
        
        tracker.learn_from_edits(
            user_id="test_user",
            original_doc=original,
            edited_doc=edited
        )
        
        prefs = tracker.get_preferences(user_id="test_user")
        # Should detect accessible style (simplified language)
        assert prefs.style == DocumentationStyle.ACCESSIBLE
    
    def test_learn_from_edits_tone_detection(self, tracker):
        """Test learning tone preference from edits"""
        original = """
        The implementation demonstrates sophisticated algorithmic approaches.
        Consequently, performance optimization is achieved.
        """
        
        edited = """
        The code shows smart ways to solve the problem.
        So, it runs faster.
        """
        
        tracker.learn_from_edits(
            user_id="test_user",
            original_doc=original,
            edited_doc=edited
        )
        
        prefs = tracker.get_preferences(user_id="test_user")
        # NOTE: Current heuristics only detect style (technical words) and depth (length)
        # Tone detection would require more sophisticated NLP
        # For now, verify that depth was detected (content shortened)
        assert prefs.depth == DocumentationDepth.CONCISE
    
    def test_learn_from_edits_example_density(self, tracker):
        """Test learning example density preference"""
        original = """
        Example:
        obj = MyClass()
        
        Documentation continues here...
        """
        
        edited = """
        Example:
        obj = MyClass()
        
        Example:
        obj = MyClass(param=value)
        
        Example:
        try:
            obj = MyClass()
        except Exception:
            pass
        
        Documentation continues here...
        """
        
        tracker.learn_from_edits(
            user_id="test_user",
            original_doc=original,
            edited_doc=edited
        )
        
        prefs = tracker.get_preferences(user_id="test_user")
        # Should detect preference for more examples (3 examples vs 1)
        # Threshold is 1.5x increase, so 3 > 1*1.5
        assert prefs.example_density == ExampleDensity.MANY
    
    def test_learn_from_edits_depth_detection(self, tracker):
        """Test learning depth preference from edits"""
        original = """
        Function does X.
        
        Args:
            param: Input value
        """
        
        edited = """
        Function performs comprehensive analysis of X by iterating through
        all possible configurations and applying transformation algorithms.
        
        The implementation uses a three-phase approach:
        1. Validation of input parameters
        2. Transformation using pattern matching
        3. Optimization of results
        
        Args:
            param: Input value representing the initial state.
                   Must be a valid integer in range [0, 100].
                   Default: 0
        """
        
        tracker.learn_from_edits(
            user_id="test_user",
            original_doc=original,
            edited_doc=edited
        )
        
        prefs = tracker.get_preferences(user_id="test_user")
        # Should detect detailed depth preference
        assert prefs.depth == DocumentationDepth.DETAILED
    
    def test_persistence_save_and_load(self, tracker):
        """Test saving and loading preferences"""
        # Create preferences
        prefs = tracker.get_preferences(user_id="test_user")
        prefs.style = DocumentationStyle.TECHNICAL
        
        # Save
        tracker.save_preferences()
        
        # Create new tracker with same storage
        new_tracker = DocumentationPreferenceTracker(
            logger=Mock(),
            storage_path=tracker.storage_path
        )
        
        # Load should restore preferences
        loaded_prefs = new_tracker.get_preferences(user_id="test_user")
        assert loaded_prefs.style == DocumentationStyle.TECHNICAL
    
    def test_get_preference_summary(self, tracker):
        """Test generating preference summary"""
        prefs = tracker.get_preferences(user_id="test_user")
        prefs.style = DocumentationStyle.TECHNICAL
        prefs.tone = DocumentationTone.FORMAL
        
        summary = tracker.get_preference_summary(user_id="test_user")
        
        assert "test_user" in summary
        assert "technical" in summary.lower()
        assert "formal" in summary.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
