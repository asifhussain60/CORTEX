"""
Tests for RepositoryDetector.

Tests repository type detection (CORTEX vs external repositories).

Authority: CORE-008 (TDD - Tests first)
AC-ID: LENS-DASH-001
"""

import pytest
from pathlib import Path
from cortex.visualization.repository_detector import (
    RepositoryDetector,
    CortexFeatures,
    is_cortex_repository,
)


class TestRepositoryDetector:
    """Test suite for RepositoryDetector class."""
    
    def test_detect_cortex_repository_all_markers(self, tmp_path: Path) -> None:
        """Test detection when all CORTEX markers are present."""
        # Arrange: Create all markers
        (tmp_path / "cortex_brain").mkdir()
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        (tmp_path / ".github" / "prompts").mkdir(parents=True)
        (tmp_path / ".github" / "prompts" / "CORTEX.prompt.md").touch()
        (tmp_path / "cortex" / "wiring" / "specifications").mkdir(parents=True)
        (tmp_path / "cortex" / "wiring" / "specifications" / "wiring.yaml").touch()
        
        # Act
        detector = RepositoryDetector(tmp_path)
        result = detector.is_cortex_repository()
        
        # Assert
        assert result is True
    
    def test_detect_cortex_repository_partial_markers(self, tmp_path: Path) -> None:
        """Test detection with only some CORTEX markers present."""
        # Arrange: Create only cortex_brain marker
        (tmp_path / "cortex_brain").mkdir()
        
        # Act
        detector = RepositoryDetector(tmp_path)
        result = detector.is_cortex_repository()
        
        # Assert
        assert result is True
    
    def test_detect_external_repository(self, tmp_path: Path) -> None:
        """Test detection of external repository (no CORTEX markers)."""
        # Arrange: Create typical project structure without CORTEX markers
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "README.md").touch()
        
        # Act
        detector = RepositoryDetector(tmp_path)
        result = detector.is_cortex_repository()
        
        # Assert
        assert result is False
    
    def test_detect_flask_project(self, tmp_path: Path) -> None:
        """Test detection of Flask project (external)."""
        # Arrange: Create Flask project structure
        (tmp_path / "app").mkdir()
        (tmp_path / "app" / "__init__.py").touch()
        (tmp_path / "requirements.txt").write_text("flask==2.0.0\n")
        
        # Act
        detector = RepositoryDetector(tmp_path)
        result = detector.is_cortex_repository()
        
        # Assert
        assert result is False
    
    def test_detect_django_project(self, tmp_path: Path) -> None:
        """Test detection of Django project (external)."""
        # Arrange: Create Django project structure
        (tmp_path / "manage.py").touch()
        (tmp_path / "myproject").mkdir()
        (tmp_path / "myproject" / "settings.py").touch()
        
        # Act
        detector = RepositoryDetector(tmp_path)
        result = detector.is_cortex_repository()
        
        # Assert
        assert result is False
    
    def test_detect_cortex_features(self, tmp_path: Path) -> None:
        """Test detection of specific CORTEX features."""
        # Arrange: Create selective markers
        (tmp_path / "cortex_brain").mkdir()
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        
        # Act
        detector = RepositoryDetector(tmp_path)
        features = detector.detect_cortex_features()
        
        # Assert
        assert features.has_cortex_brain is True
        assert features.has_orchestrators is True
        assert features.has_prompt_file is False
        assert features.has_wiring is False
    
    def test_get_cortex_markers(self, tmp_path: Path) -> None:
        """Test getting list of CORTEX markers to check."""
        # Act
        detector = RepositoryDetector(tmp_path)
        markers = detector.get_cortex_markers()
        
        # Assert
        assert len(markers) == 4
        assert all(isinstance(marker, Path) for marker in markers)
        assert any("cortex_brain" in str(marker) for marker in markers)
        assert any("orchestrators" in str(marker) for marker in markers)
    
    def test_is_cortex_repository_convenience_function(self, tmp_path: Path) -> None:
        """Test convenience function is_cortex_repository()."""
        # Arrange
        (tmp_path / "cortex_brain").mkdir()
        
        # Act
        result = is_cortex_repository(tmp_path)
        
        # Assert
        assert result is True
    
    def test_is_cortex_repository_with_wiring_only(self, tmp_path: Path) -> None:
        """Test detection with only wiring.yaml marker."""
        # Arrange
        (tmp_path / "cortex" / "wiring" / "specifications").mkdir(parents=True)
        (tmp_path / "cortex" / "wiring" / "specifications" / "wiring.yaml").touch()
        
        # Act
        result = is_cortex_repository(tmp_path)
        
        # Assert
        assert result is True
    
    def test_is_cortex_repository_with_prompt_only(self, tmp_path: Path) -> None:
        """Test detection with only CORTEX.prompt.md marker."""
        # Arrange
        (tmp_path / ".github" / "prompts").mkdir(parents=True)
        (tmp_path / ".github" / "prompts" / "CORTEX.prompt.md").touch()
        
        # Act
        result = is_cortex_repository(tmp_path)
        
        # Assert
        assert result is True
    
    def test_cortex_features_dataclass(self) -> None:
        """Test CortexFeatures dataclass creation."""
        # Act
        features = CortexFeatures(
            has_cortex_brain=True,
            has_orchestrators=True,
            has_prompt_file=False,
            has_wiring=False,
        )
        
        # Assert
        assert features.has_cortex_brain is True
        assert features.has_orchestrators is True
        assert features.has_prompt_file is False
        assert features.has_wiring is False
    
    def test_nonexistent_path(self) -> None:
        """Test handling of non-existent repository path."""
        # Arrange
        nonexistent_path = Path("/nonexistent/path/to/repo")
        
        # Act
        detector = RepositoryDetector(nonexistent_path)
        result = detector.is_cortex_repository()
        
        # Assert
        assert result is False
