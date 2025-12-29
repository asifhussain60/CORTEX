"""
Integration tests for adaptive documentation generation with preference tracking

Tests the full workflow:
1. User-specific documentation generation
2. Style adaptation based on preferences
3. Learning from user feedback
4. Progressive improvement over multiple iterations
"""

import pytest
from pathlib import Path
import logging
from unittest.mock import Mock

from src.orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig,
    DocumentationResult
)
from src.orchestration_4_0.orchestrators.documentation.preference_tracker import (
    DocumentationPreferences,
    DocumentationStyle,
    DocumentationTone,
    DocumentationDepth,
    ExampleDensity
)


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    logger = logging.getLogger('test_adaptive_docs')
    logger.setLevel(logging.INFO)
    return logger


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary Python project for testing"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create a sample Python file
    sample_file = project_dir / "sample.py"
    sample_file.write_text('''
"""Sample module for testing documentation generation"""

class Calculator:
    """A simple calculator class demonstrating polymorphism and encapsulation"""
    
    def __init__(self):
        """Initialize the calculator"""
        self.result = 0
    
    def add(self, a: int, b: int) -> int:
        """
        Add two numbers
        
        Utilizes arithmetic operations to implement addition.
        
        Args:
            a: First operand
            b: Second operand
            
        Returns:
            Sum of a and b
        """
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers"""
        return a * b


def demonstrate_usage():
    """
    Demonstrate calculator usage
    
    This function instantiates a Calculator and demonstrates
    its polymorphic behavior with various operations.
    """
    calc = Calculator()
    result = calc.add(5, 3)
    print(f"Result: {result}")
''')
    
    return project_dir


@pytest.fixture
def temp_storage(tmp_path):
    """Temporary storage for preferences"""
    return tmp_path / "preferences.json"


class TestAdaptiveDocumentationGeneration:
    """Test adaptive documentation generation with user preferences"""
    
    def test_generation_without_user_preferences(self, mock_logger, temp_project, tmp_path):
        """Test baseline generation without user-specific preferences"""
        output_dir = tmp_path / "docs"
        
        config = DocumentationConfig(
            source_paths=[temp_project],
            output_dir=output_dir,
            include_private=False,
            generate_diagrams=False,
            enable_adaptive_style=False  # Disabled
        )
        
        orchestrator = DocumentationOrchestrator(logger=mock_logger)
        context = {"config": config}
        
        result = orchestrator.execute(context)
        
        assert result.get("is_complete")
        doc_result = result.get("result")
        assert doc_result.modules_analyzed > 0
        assert doc_result.classes_documented > 0
        
        # Check that documentation was generated
        assert len(doc_result.output_files) > 0
    
    def test_generation_with_default_preferences(self, mock_logger, temp_project, tmp_path, temp_storage):
        """Test generation with default user preferences"""
        output_dir = tmp_path / "docs_default"
        
        config = DocumentationConfig(
            source_paths=[temp_project],
            output_dir=output_dir,
            include_private=False,
            generate_diagrams=False,
            enable_adaptive_style=True,
            user_id="test_user_default",
            learn_from_feedback=True
        )
        
        orchestrator = DocumentationOrchestrator(logger=mock_logger)
        # Override storage path for testing
        orchestrator.preference_tracker.storage_path = temp_storage
        
        context = {"config": config}
        result = orchestrator.execute(context)
        
        assert result.get("is_complete")
        doc_result = result.get("result")
        assert doc_result.modules_analyzed > 0
        
        # Check that preferences were loaded (default values)
        prefs = orchestrator.get_user_preferences()
        assert prefs is not None
        assert prefs.user_id == "test_user_default"
        assert prefs.style == DocumentationStyle.BALANCED
    
    def test_generation_with_technical_style(self, mock_logger, temp_project, tmp_path, temp_storage):
        """Test generation with technical style preference"""
        output_dir = tmp_path / "docs_technical"
        
        config = DocumentationConfig(
            source_paths=[temp_project],
            output_dir=output_dir,
            include_private=False,
            generate_diagrams=False,
            enable_adaptive_style=True,
            user_id="test_user_technical",
            learn_from_feedback=True
        )
        
        orchestrator = DocumentationOrchestrator(logger=mock_logger)
        orchestrator.preference_tracker.storage_path = temp_storage
        
        # Set technical preferences before generation
        orchestrator.update_user_preference(
            preference_type="style",
            new_value="technical",
            reason="test_setup",
            user_id="test_user_technical"
        )
        
        context = {"config": config}
        result = orchestrator.execute(context)
        
        assert result.get("is_complete")
        
        # Verify preferences were applied
        prefs = orchestrator.get_user_preferences()
        assert prefs.style == DocumentationStyle.TECHNICAL
        
        # Read generated documentation
        docs_dir = output_dir / "modules"
        if docs_dir.exists():
            doc_files = list(docs_dir.glob("*.md"))
            assert len(doc_files) > 0
            
            # Technical style should preserve technical terms
            sample_doc = doc_files[0].read_text()
            # Check for technical language (this is simplified)
            assert len(sample_doc) > 0
    
    def test_generation_with_accessible_style(self, mock_logger, temp_project, tmp_path, temp_storage):
        """Test generation with accessible style preference"""
        output_dir = tmp_path / "docs_accessible"
        
        config = DocumentationConfig(
            source_paths=[temp_project],
            output_dir=output_dir,
            include_private=False,
            generate_diagrams=False,
            enable_adaptive_style=True,
            user_id="test_user_accessible",
            learn_from_feedback=True
        )
        
        orchestrator = DocumentationOrchestrator(logger=mock_logger)
        orchestrator.preference_tracker.storage_path = temp_storage
        
        # Set accessible preferences
        orchestrator.update_user_preference(
            preference_type="style",
            new_value="accessible",
            reason="test_setup",
            user_id="test_user_accessible"
        )
        
        context = {"config": config}
        result = orchestrator.execute(context)
        
        assert result.get("is_complete")
        
        # Verify preferences
        prefs = orchestrator.get_user_preferences()
        assert prefs.style == DocumentationStyle.ACCESSIBLE
        
        # Check adaptation occurred
        doc_result = result.get("result")
        assert len(doc_result.output_files) > 0


class TestPreferenceLearning:
    """Test preference learning from user feedback"""
    
    def test_learn_from_user_simplification(self, mock_logger, temp_project, tmp_path, temp_storage):
        """Test learning when user simplifies technical language"""
        output_dir = tmp_path / "docs_learning"
        
        config = DocumentationConfig(
            source_paths=[temp_project],
            output_dir=output_dir,
            include_private=False,
            generate_diagrams=False,
            enable_adaptive_style=True,
            user_id="test_learner",
            learn_from_feedback=True
        )
        
        orchestrator = DocumentationOrchestrator(logger=mock_logger)
        orchestrator.preference_tracker.storage_path = temp_storage
        
        # Initial generation with default preferences
        context = {"config": config}
        result = orchestrator.execute(context)
        assert result.get("is_complete")
        
        # Simulate user editing documentation to simplify it
        original = "This class demonstrates polymorphism and encapsulation with abstraction."
        edited = "This class shows how objects work differently and hide their data."
        
        orchestrator.learn_from_user_edit(
            original_doc=original,
            edited_doc=edited
        )
        
        # Check that preferences were updated
        prefs = orchestrator.get_user_preferences()
        assert prefs.style == DocumentationStyle.ACCESSIBLE
        
        # Confidence should be low (only 1 edit)
        confidence = orchestrator.get_preference_confidence()
        assert confidence > 0.0
        assert confidence < 1.0
    
    def test_learn_from_multiple_edits(self, mock_logger, temp_project, tmp_path, temp_storage):
        """Test that confidence increases with multiple consistent edits"""
        config = DocumentationConfig(
            source_paths=[temp_project],
            output_dir=tmp_path / "docs_multi",
            include_private=False,
            generate_diagrams=False,
            enable_adaptive_style=True,
            user_id="test_multi_learner",
            learn_from_feedback=True
        )
        
        orchestrator = DocumentationOrchestrator(logger=mock_logger)
        orchestrator.preference_tracker.storage_path = temp_storage
        
        # Multiple edits showing preference for detail
        edits = [
            ("Brief description.", "Brief description with extensive detail and examples."),
            ("Simple method.", "Simple method with comprehensive explanation and usage patterns."),
            ("Quick reference.", "Quick reference expanded with detailed information and context.")
        ]
        
        for original, edited in edits:
            orchestrator.learn_from_user_edit(original, edited, user_id="test_multi_learner")
        
        # Should have learned preference for detailed documentation
        prefs = orchestrator.get_user_preferences(user_id="test_multi_learner")
        assert prefs.depth == DocumentationDepth.DETAILED
        
        # Confidence should be higher with multiple edits
        confidence = orchestrator.get_preference_confidence(user_id="test_multi_learner")
        assert confidence > 0.3  # Should increase with more data


class TestProgressiveImprovement:
    """Test that documentation improves over multiple iterations"""
    
    def test_iterative_improvement_cycle(self, mock_logger, temp_project, tmp_path, temp_storage):
        """Test complete cycle: generate → feedback → regenerate → improved"""
        output_dir_v1 = tmp_path / "docs_v1"
        output_dir_v2 = tmp_path / "docs_v2"
        
        user_id = "test_improver"
        
        # Iteration 1: Generate with default preferences
        config_v1 = DocumentationConfig(
            source_paths=[temp_project],
            output_dir=output_dir_v1,
            include_private=False,
            generate_diagrams=False,
            enable_adaptive_style=True,
            user_id=user_id,
            learn_from_feedback=True
        )
        
        orchestrator_v1 = DocumentationOrchestrator(logger=mock_logger)
        orchestrator_v1.preference_tracker.storage_path = temp_storage
        
        result_v1 = orchestrator_v1.execute({"config": config_v1})
        assert result_v1.get("is_complete")
        
        # User provides feedback (wants concise, casual style)
        orchestrator_v1.update_user_preference("depth", "concise", "user_feedback", user_id=user_id)
        orchestrator_v1.update_user_preference("tone", "casual", "user_feedback", user_id=user_id)
        
        # Iteration 2: Regenerate with learned preferences
        config_v2 = DocumentationConfig(
            source_paths=[temp_project],
            output_dir=output_dir_v2,
            include_private=False,
            generate_diagrams=False,
            enable_adaptive_style=True,
            user_id=user_id,  # Same user
            learn_from_feedback=True
        )
        
        orchestrator_v2 = DocumentationOrchestrator(logger=mock_logger)
        orchestrator_v2.preference_tracker.storage_path = temp_storage
        orchestrator_v2.preference_tracker._load_preferences()  # Reload from new path
        
        result_v2 = orchestrator_v2.execute({"config": config_v2})
        assert result_v2.get("is_complete")
        
        # Verify preferences persisted and were applied
        prefs_v2 = orchestrator_v2.get_user_preferences()
        assert prefs_v2.depth == DocumentationDepth.CONCISE
        assert prefs_v2.tone == DocumentationTone.CASUAL
        
        # Both iterations should succeed
        assert result_v1.get("is_complete")
        assert result_v2.get("is_complete")


class TestPreferenceAPI:
    """Test the preference management API"""
    
    def test_get_user_preferences(self, mock_logger, temp_storage):
        """Test getting user preferences"""
        config = DocumentationConfig(
            source_paths=[Path(".")],
            user_id="test_api_user",
            enable_adaptive_style=True
        )
        
        orchestrator = DocumentationOrchestrator(logger=mock_logger)
        orchestrator.preference_tracker.storage_path = temp_storage
        orchestrator.doc_config = config
        
        prefs = orchestrator.get_user_preferences()
        
        assert prefs is not None
        assert prefs.user_id == "test_api_user"
    
    def test_update_user_preference(self, mock_logger, temp_storage):
        """Test updating a specific preference"""
        config = DocumentationConfig(
            source_paths=[Path(".")],
            user_id="test_update_user",
            enable_adaptive_style=True
        )
        
        orchestrator = DocumentationOrchestrator(logger=mock_logger)
        orchestrator.preference_tracker.storage_path = temp_storage
        orchestrator.doc_config = config
        
        # Update style preference
        orchestrator.update_user_preference(
            preference_type="style",
            new_value="technical",
            reason="unit_test"
        )
        
        prefs = orchestrator.get_user_preferences()
        assert prefs.style == DocumentationStyle.TECHNICAL
    
    def test_get_preference_confidence(self, mock_logger, temp_storage):
        """Test getting confidence score"""
        config = DocumentationConfig(
            source_paths=[Path(".")],
            user_id="test_confidence_user",
            enable_adaptive_style=True
        )
        
        orchestrator = DocumentationOrchestrator(logger=mock_logger)
        orchestrator.preference_tracker.storage_path = temp_storage
        orchestrator.doc_config = config
        
        # New user should have 0 confidence
        confidence = orchestrator.get_preference_confidence()
        assert confidence == 0.0
        
        # After updates, confidence should increase
        orchestrator.update_user_preference("style", "technical", "test")
        orchestrator.update_user_preference("tone", "formal", "test")
        
        confidence = orchestrator.get_preference_confidence()
        assert confidence > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
