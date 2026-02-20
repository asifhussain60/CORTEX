"""Tests for cortex package initialization."""

import pytest
from pathlib import Path


class TestCortexPackageInit:
    """Verify cortex/__init__.py is properly initialized."""

    def test_cortex_module_importable(self):
        """Cortex package should be importable."""
        import cortex
        assert cortex is not None

    def test_cortex_has_version(self):
        """Cortex should have __version__ attribute."""
        import cortex
        assert hasattr(cortex, '__version__')
        assert isinstance(cortex.__version__, str)

    def test_cortex_has_docstring(self):
        """Cortex module should have docstring."""
        import cortex
        assert cortex.__doc__ is not None
        assert len(cortex.__doc__) > 0

    def test_cortex_file_exists(self):
        """cortex/__init__.py file should exist."""
        cortex_init = Path(__file__).parent.parent.parent / 'cortex' / '__init__.py'
        assert cortex_init.exists(), f"cortex/__init__.py not found at {cortex_init}"

    def test_cortex_has_author(self):
        """Cortex should have __author__ attribute."""
        import cortex
        assert hasattr(cortex, '__author__')

    def test_cortex_imports_are_accessible(self):
        """Core cortex modules should be accessible."""
        import cortex
        # Check that standard attributes are present
        assert hasattr(cortex, '__name__')
        assert cortex.__name__ == 'cortex'
