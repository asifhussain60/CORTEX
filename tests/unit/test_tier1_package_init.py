"""Tests for cortex_intelligence.memory.tier1_learned package initialization."""

import pytest
from pathlib import Path


class TestTier1PackageInit:
    """Verify cortex_intelligence.memory.tier1_learned/__init__.py is properly initialized."""

    def test_tier1_module_importable(self):
        """Tier1 package should be importable."""
        import cortex_intelligence.tier1
        assert cortex_intelligence.memory.tier1_learned is not None

    def test_tier1_has_docstring(self):
        """Tier1 module should have docstring."""
        import cortex_intelligence.tier1
        assert cortex_intelligence.memory.tier1_learned.__doc__ is not None
        assert len(cortex_intelligence.memory.tier1_learned.__doc__) > 0

    def test_tier1_file_exists(self):
        """cortex_brain/tier1/__init__.py file should exist."""
        tier1_init = Path(__file__).parent.parent.parent / 'cortex_brain' / 'tier1' / '__init__.py'
        assert tier1_init.exists(), f"cortex_brain/tier1/__init__.py not found at {tier1_init}"

    def test_tier1_name_correct(self):
        """Tier1 __name__ should be 'cortex_intelligence.memory.tier1_learned'."""
        import cortex_intelligence.tier1
        assert cortex_intelligence.memory.tier1_learned.__name__ == 'cortex_intelligence.memory.tier1_learned'

    def test_tier1_has_path_package(self):
        """Tier1 should be a proper package with __path__."""
        import cortex_intelligence.tier1
        assert hasattr(cortex_intelligence.memory.tier1_learned, '__path__')

    def test_tier1_core_logic_imports(self):
        """Tier1 should support importing core logic components."""
        import cortex_intelligence.tier1
        # Verify it's properly set up as a package
        assert hasattr(cortex_intelligence.memory.tier1_learned, '__file__')

    def test_tier1_isolation(self):
        """Tier1 should be isolated tier with core logic focus."""
        import cortex_intelligence.tier1
        # Verify module is in correct package hierarchy
        assert 'cortex_brain' in cortex_intelligence.memory.tier1_learned.__name__
        assert 'tier1' in cortex_intelligence.memory.tier1_learned.__name__
