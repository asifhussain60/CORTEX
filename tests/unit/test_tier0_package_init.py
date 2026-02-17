"""Tests for cortex_intelligence.memory.core package initialization."""

import pytest
from pathlib import Path


class TestTier0PackageInit:
    """Verify cortex_intelligence.memory.core/__init__.py is properly initialized."""

    def test_tier0_module_importable(self):
        """Tier0 package should be importable."""
        import cortex_intelligence.tier0
        assert cortex_intelligence.memory.core is not None

    def test_tier0_has_docstring(self):
        """Tier0 module should have docstring."""
        import cortex_intelligence.tier0
        assert cortex_intelligence.memory.core.__doc__ is not None
        assert len(cortex_intelligence.memory.core.__doc__) > 0

    def test_tier0_file_exists(self):
        """cortex_intelligence/tier0/__init__.py file should exist."""
        tier0_init = Path(__file__).parent.parent.parent / 'cortex_intelligence' / 'tier0' / '__init__.py'
        assert tier0_init.exists(), f"cortex_intelligence/tier0/__init__.py not found at {tier0_init}"

    def test_tier0_name_correct(self):
        """Tier0 __name__ should be 'cortex_intelligence.memory.core'."""
        import cortex_intelligence.tier0
        assert cortex_intelligence.memory.core.__name__ == 'cortex_intelligence.memory.core'

    def test_tier0_has_path_package(self):
        """Tier0 should be a proper package with __path__."""
        import cortex_intelligence.tier0
        assert hasattr(cortex_intelligence.memory.core, '__path__')

    def test_tier0_governance_imports(self):
        """Tier0 should support importing governance components."""
        # This will be populated once __init__.py exports governance
        import cortex_intelligence.tier0
        # Verify it's properly set up as a package
        assert hasattr(cortex_intelligence.memory.core, '__file__')

    def test_tier0_isolation(self):
        """Tier0 should be isolated tier with governance focus."""
        import cortex_intelligence.tier0
        # Verify module is in correct package hierarchy
        assert 'cortex_intelligence' in cortex_intelligence.memory.core.__name__
        assert 'tier0' in cortex_intelligence.memory.core.__name__
