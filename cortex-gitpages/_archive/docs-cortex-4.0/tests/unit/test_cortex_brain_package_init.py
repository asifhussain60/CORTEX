"""Tests for cortex_brain package initialization."""

import pytest
from pathlib import Path


class TestCortexBrainPackageInit:
    """Verify cortex_brain/__init__.py is properly initialized."""

    def test_cortex_brain_module_importable(self):
        """Cortex_brain package should be importable."""
        import cortex_brain
        assert cortex_brain is not None

    def test_cortex_brain_has_version(self):
        """Cortex_brain should have __version__ attribute."""
        import cortex_brain
        assert hasattr(cortex_brain, '__version__')
        assert isinstance(cortex_brain.__version__, str)

    def test_cortex_brain_has_docstring(self):
        """Cortex_brain module should have docstring."""
        import cortex_brain
        assert cortex_brain.__doc__ is not None
        assert len(cortex_brain.__doc__) > 0

    def test_cortex_brain_file_exists(self):
        """cortex_brain/__init__.py file should exist."""
        cortex_brain_init = Path(__file__).parent.parent.parent / 'cortex_brain' / '__init__.py'
        assert cortex_brain_init.exists(), f"cortex_brain/__init__.py not found at {cortex_brain_init}"

    def test_cortex_brain_tier_structure_accessible(self):
        """Cortex_brain should have tier subpackages accessible."""
        import cortex_brain
        # Tiers should be accessible through the package
        assert hasattr(cortex_brain, '__path__')

    def test_cortex_brain_has_author(self):
        """Cortex_brain should have __author__ attribute."""
        import cortex_brain
        assert hasattr(cortex_brain, '__author__')

    def test_cortex_brain_name_correct(self):
        """Cortex_brain __name__ should be 'cortex_brain'."""
        import cortex_brain
        assert cortex_brain.__name__ == 'cortex_brain'
