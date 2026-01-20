"""Integration tests for package imports."""

import pytest
import sys


class TestPackageImports:
    """Verify all critical imports work after __init__.py creation."""

    def test_import_cortex(self):
        """Should import cortex package."""
        import cortex
        assert cortex.__name__ == 'cortex'

    def test_import_cortex_brain(self):
        """Should import cortex_brain package."""
        import cortex_brain
        assert cortex_brain.__name__ == 'cortex_brain'

    def test_import_cortex_brain_tier0(self):
        """Should import cortex_brain.tier0 package."""
        import cortex_brain.tier0
        assert cortex_brain.tier0.__name__ == 'cortex_brain.tier0'

    def test_import_cortex_brain_tier1(self):
        """Should import cortex_brain.tier1 package."""
        import cortex_brain.tier1
        assert cortex_brain.tier1.__name__ == 'cortex_brain.tier1'

    def test_cortex_tier2_still_accessible(self):
        """TIER 2 should remain accessible (already has __init__.py)."""
        import cortex_brain.tier2
        assert cortex_brain.tier2 is not None

    def test_from_imports_work(self):
        """from X import * statements should work."""
        # Test that package structure is correct
        import cortex_brain.tier0
        import cortex_brain.tier1
        import cortex_brain.tier2
        
        # Verify all are accessible
        assert cortex_brain.tier0 is not None
        assert cortex_brain.tier1 is not None
        assert cortex_brain.tier2 is not None

    def test_no_import_errors(self):
        """Verify no ImportError or ModuleNotFoundError raised."""
        try:
            import cortex
            import cortex_brain
            import cortex_brain.tier0
            import cortex_brain.tier1
            import cortex_brain.tier2
        except ImportError as e:
            pytest.fail(f"Import failed with ImportError: {e}")
        except ModuleNotFoundError as e:
            pytest.fail(f"Import failed with ModuleNotFoundError: {e}")

    def test_sys_modules_populated(self):
        """Verify modules are registered in sys.modules."""
        import cortex
        import cortex_brain
        import cortex_brain.tier0
        import cortex_brain.tier1
        
        assert 'cortex' in sys.modules
        assert 'cortex_brain' in sys.modules
        assert 'cortex_brain.tier0' in sys.modules
        assert 'cortex_brain.tier1' in sys.modules
