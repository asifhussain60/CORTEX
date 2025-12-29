"""
Tests for Documentation Preference Tracker and Style Adaptation Engine

Tests preference tracking, learning from edits, and style adaptation.
"""

import pytest
from pathlib import Path
import tempfile
import time
from unittest.mock import Mock

from src.orchestration_4_0.orchestrators.documentation.preference_tracker import (
    DocumentationPreferenceTracker,
    DocumentationPreferences,
    DocumentationStyle,
    DocumentationTone,
    DocumentationDepth,
    ExampleDensity,
    PreferenceUpdate
)

from src.orchestration_4_0.orchestrators.documentation.style_adaptation import (
    StyleAdaptationEngine,
    FeedbackLoopIntegrator
)


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    return Mock()


@pytest.fixture
def temp_storage(tmp_path):
    """Temporary storage path for preferences"""
    return tmp_path / "preferences.json"


@pytest.fixture
def preference_tracker(mock_logger, temp_storage):
    """Preference tracker instance"""
    return DocumentationPreferenceTracker(mock_logger, temp_storage)


@pytest.fixture
def style_engine(mock_logger):
    """Style adaptation engine instance"""
    return StyleAdaptationEngine(mock_logger)


class TestDocumentationPreferences:
    """Tests for DocumentationPreferences dataclass"""
    
    def test_to_dict(self):
        """Test converting preferences to dictionary"""
        prefs = DocumentationPreferences(
            user_id="test_user",
            project_id="test_project",
            style=DocumentationStyle.TECHNICAL
        )
        
        data = prefs.to_dict()
        
        assert data['user_id'] == "test_user"
        assert data['project_id'] == "test_project"
        assert data['style'] == "technical"
    
    def test_from_dict(self):
        """Test creating preferences from dictionary"""
        data = {
            'user_id': 'test_user',
            'project_id': 'test_project',
            'style': 'accessible',
            'tone': 'casual',
            'depth': 'detailed'
        }
        
        prefs = DocumentationPreferences.from_dict(data)
        
        assert prefs.user_id == "test_user"
        assert prefs.style == DocumentationStyle.ACCESSIBLE
        assert prefs.tone == DocumentationTone.CASUAL
        assert prefs.depth == DocumentationDepth.DETAILED


class TestDocumentationPreferenceTracker:
    """Tests for DocumentationPreferenceTracker"""
    
    def test_get_preferences_creates_default(self, preference_tracker):
        """Test getting preferences creates default if not exists"""
        prefs = preference_tracker.get_preferences("new_user")
        
        assert prefs.user_id == "new_user"
        assert prefs.style == DocumentationStyle.BALANCED
        assert prefs.tone == DocumentationTone.NEUTRAL
    
    def test_get_preferences_with_project_id(self, preference_tracker):
        """Test getting project-specific preferences"""
        prefs = preference_tracker.get_preferences("user1", "project_a")
        
        assert prefs.user_id == "user1"
        assert prefs.project_id == "project_a"
    
    def test_update_preference_style(self, preference_tracker):
        """Test updating style preference"""
        preference_tracker.get_preferences("user1")
        
        preference_tracker.update_preference(
            user_id="user1",
            preference_type="style",
            new_value="technical",
            reason="user_feedback"
        )
        
        prefs = preference_tracker.get_preferences("user1")
        assert prefs.style == DocumentationStyle.TECHNICAL
    
    def test_update_preference_tone(self, preference_tracker):
        """Test updating tone preference"""
        preference_tracker.update_preference(
            user_id="user1",
            preference_type="tone",
            new_value="casual"
        )
        
        prefs = preference_tracker.get_preferences("user1")
        assert prefs.tone == DocumentationTone.CASUAL
    
    def test_update_preference_depth(self, preference_tracker):
        """Test updating depth preference"""
        preference_tracker.update_preference(
            user_id="user1",
            preference_type="depth",
            new_value="concise"
        )
        
        prefs = preference_tracker.get_preferences("user1")
        assert prefs.depth == DocumentationDepth.CONCISE
    
    def test_update_preference_example_density(self, preference_tracker):
        """Test updating example density preference"""
        preference_tracker.update_preference(
            user_id="user1",
            preference_type="example_density",
            new_value="many"
        )
        
        prefs = preference_tracker.get_preferences("user1")
        assert prefs.example_density == ExampleDensity.MANY
    
    def test_update_preference_records_history(self, preference_tracker):
        """Test that preference updates are recorded in history"""
        preference_tracker.update_preference(
            user_id="user1",
            preference_type="style",
            new_value="technical"
        )
        
        history = preference_tracker.get_update_history("user1")
        
        assert len(history) == 1
        assert history[0].preference_type == "style"
        assert history[0].new_value == "technical"
    
    def test_learn_from_edits_more_examples(self, preference_tracker):
        """Test learning when user adds more examples"""
        original = "Brief documentation without examples."
        edited = """
        Detailed documentation with examples:
        
        ```python
        example1()
        ```
        
        ```python
        example2()
        ```
        
        ```python
        example3()
        ```
        """
        
        preference_tracker.learn_from_edits("user1", original, edited)
        
        prefs = preference_tracker.get_preferences("user1")
        assert prefs.example_density == ExampleDensity.MANY
    
    def test_learn_from_edits_simplifies_language(self, preference_tracker):
        """Test learning when user simplifies technical language"""
        original = "This demonstrates polymorphism and encapsulation with abstraction."
        edited = "This shows how objects work differently and hide data."
        
        preference_tracker.learn_from_edits("user1", original, edited)
        
        prefs = preference_tracker.get_preferences("user1")
        assert prefs.style == DocumentationStyle.ACCESSIBLE
    
    def test_learn_from_edits_wants_detail(self, preference_tracker):
        """Test learning when user expands content"""
        original = "Brief description."
        edited = "Brief description expanded with much more detailed information and explanations that go into depth about the topic."
        
        preference_tracker.learn_from_edits("user1", original, edited)
        
        prefs = preference_tracker.get_preferences("user1")
        assert prefs.depth == DocumentationDepth.DETAILED
    
    def test_learn_from_edits_wants_conciseness(self, preference_tracker):
        """Test learning when user condenses content"""
        original = "Very long and detailed description with lots of explanation and redundant information."
        edited = "Short description."
        
        preference_tracker.learn_from_edits("user1", original, edited)
        
        prefs = preference_tracker.get_preferences("user1")
        assert prefs.depth == DocumentationDepth.CONCISE
    
    def test_persistence_across_instances(self, temp_storage, mock_logger):
        """Test that preferences persist across tracker instances"""
        # Create first tracker and set preference
        tracker1 = DocumentationPreferenceTracker(mock_logger, temp_storage)
        tracker1.update_preference("user1", "style", "technical")
        
        # Create second tracker and check preference persisted
        tracker2 = DocumentationPreferenceTracker(mock_logger, temp_storage)
        prefs = tracker2.get_preferences("user1")
        
        assert prefs.style == DocumentationStyle.TECHNICAL


class TestStyleAdaptationEngine:
    """Tests for StyleAdaptationEngine"""
    
    def test_adapt_style_to_accessible(self, style_engine):
        """Test adapting style to accessible"""
        prefs = DocumentationPreferences(
            user_id="user1",
            style=DocumentationStyle.ACCESSIBLE
        )
        
        original = "This class demonstrates polymorphism and encapsulation."
        adapted = style_engine.adapt_documentation(original, prefs)
        
        assert "polymorphism" not in adapted.lower() or "using objects" in adapted.lower()
    
    def test_adapt_tone_to_casual(self, style_engine):
        """Test adapting tone to casual"""
        prefs = DocumentationPreferences(
            user_id="user1",
            tone=DocumentationTone.CASUAL
        )
        
        original = "Utilize this method to implement the feature."
        adapted = style_engine.adapt_documentation(original, prefs)
        
        assert "use" in adapted.lower() or "build" in adapted.lower()
    
    def test_adapt_tone_to_formal(self, style_engine):
        """Test adapting tone to formal"""
        prefs = DocumentationPreferences(
            user_id="user1",
            tone=DocumentationTone.FORMAL
        )
        
        original = "Let's use this method to build the feature."
        adapted = style_engine.adapt_documentation(original, prefs)
        
        # Conversational markers should be removed
        assert "Let's" not in adapted
    
    def test_adapt_multiple_preferences(self, style_engine):
        """Test adapting with multiple preference changes"""
        prefs = DocumentationPreferences(
            user_id="user1",
            style=DocumentationStyle.ACCESSIBLE,
            tone=DocumentationTone.CASUAL,
            depth=DocumentationDepth.DETAILED
        )
        
        original = "Utilize polymorphism to implement this feature."
        adapted = style_engine.adapt_documentation(original, prefs)
        
        # Should apply multiple transformations
        assert adapted != original
    
    def test_get_adaptation_summary(self, style_engine):
        """Test getting adaptation summary"""
        prefs = DocumentationPreferences(
            user_id="user1",
            style=DocumentationStyle.ACCESSIBLE
        )
        
        original = "Technical documentation with polymorphism."
        adapted = style_engine.adapt_documentation(original, prefs)
        
        summary = style_engine.get_adaptation_summary(original, adapted, prefs)
        
        assert 'style' in summary
        assert 'original_length' in summary
        assert 'adapted_length' in summary
        assert summary['style'] == 'accessible'


class TestFeedbackLoopIntegrator:
    """Tests for FeedbackLoopIntegrator"""
    
    def test_process_user_edit(self, preference_tracker, mock_logger):
        """Test processing user edit feedback"""
        integrator = FeedbackLoopIntegrator(preference_tracker, mock_logger)
        
        original = "Brief doc."
        edited = "Brief doc with lots more detail and examples."
        
        integrator.process_user_edit(
            user_id="user1",
            original_doc=original,
            edited_doc=edited
        )
        
        # Should update preferences through tracker
        prefs = preference_tracker.get_preferences("user1")
        assert prefs.depth == DocumentationDepth.DETAILED
    
    def test_get_preference_confidence_new_user(self, preference_tracker, mock_logger):
        """Test confidence score for new user with no history"""
        integrator = FeedbackLoopIntegrator(preference_tracker, mock_logger)
        
        confidence = integrator.get_preference_confidence("new_user")
        
        assert confidence == 0.0
    
    def test_get_preference_confidence_with_history(self, preference_tracker, mock_logger):
        """Test confidence score increases with more updates"""
        integrator = FeedbackLoopIntegrator(preference_tracker, mock_logger)
        
        # Add several preference updates
        for i in range(5):
            preference_tracker.update_preference(
                user_id="user1",
                preference_type="style",
                new_value="technical"
            )
        
        confidence = integrator.get_preference_confidence("user1")
        
        assert confidence > 0.0
        assert confidence <= 1.0


class TestIntegration:
    """Integration tests for preference tracking and style adaptation"""
    
    def test_end_to_end_learning_and_adaptation(
        self,
        preference_tracker,
        style_engine,
        mock_logger
    ):
        """Test complete workflow: learn → adapt"""
        # Step 1: User edits documentation (adds examples)
        original = "Brief API documentation."
        edited = """
        API documentation with examples:
        
        Example:
        ```python
        api.method()
        ```
        
        Example:
        ```python
        api.another_method()
        ```
        """
        
        # Learn from edit
        preference_tracker.learn_from_edits("user1", original, edited)
        
        # Step 2: Generate new documentation and adapt it
        prefs = preference_tracker.get_preferences("user1")
        new_doc = "New API method documentation."
        adapted_doc = style_engine.adapt_documentation(new_doc, prefs)
        
        # Verify preferences were learned and applied
        assert prefs.example_density == ExampleDensity.MANY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
