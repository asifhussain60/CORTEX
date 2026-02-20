"""Tests for cortex_intelligence package initialization."""

import pytest
from pathlib import Path


class TestCortexBrainPackageInit:
    """Verify cortex_intelligence/__init__.py is properly initialized."""

    def test_cortex_intelligence_module_importable(self):
        """Cortex_intelligence package should be importable."""
        import cortex_intelligence
        assert cortex_intelligence is not None

    def test_cortex_intelligence_has_version(self):
        """Cortex_intelligence should have __version__ attribute."""
        import cortex_intelligence
        assert hasattr(cortex_intelligence, '__version__')
        assert isinstance(cortex_intelligence.__version__, str)

    def test_cortex_intelligence_has_docstring(self):
        """Cortex_intelligence module should have docstring."""
        import cortex_intelligence
        assert cortex_intelligence.__doc__ is not None
        assert len(cortex_intelligence.__doc__) > 0

    def test_cortex_intelligence_file_exists(self):
        """cortex_intelligence/__init__.py file should exist."""
        cortex_intelligence_init = Path(__file__).parent.parent.parent / 'cortex_intelligence' / '__init__.py'
        assert cortex_intelligence_init.exists(), f"cortex_intelligence/__init__.py not found at {cortex_intelligence_init}"

    def test_cortex_intelligence_tier_structure_accessible(self):
        """Cortex_intelligence should have tier subpackages accessible."""
        import cortex_intelligence
        # Tiers should be accessible through the package
        assert hasattr(cortex_intelligence, '__path__')

    def test_cortex_intelligence_has_author(self):
        """Cortex_intelligence should have __author__ attribute."""
        import cortex_intelligence
        assert hasattr(cortex_intelligence, '__author__')

    def test_cortex_intelligence_name_correct(self):
        """Cortex_intelligence __name__ should be 'cortex_intelligence'."""
        import cortex_intelligence
        assert cortex_intelligence.__name__ == 'cortex_intelligence'
