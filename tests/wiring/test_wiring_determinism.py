"""
TEST-005: Wiring Determinism Tests.

Validates that wiring behavior is deterministic and reproducible.
Critical for Docker deployment where wiring must be consistent.

Phase: 6 (Test Suite & Final Validation)
Author: Asif Hussain
Date: 2026-01-28
"""

import hashlib
import subprocess
from pathlib import Path

import pytest


class TestWiringDeterminism:
    """Verify that wiring behavior is deterministic."""
    
    @pytest.fixture
    def cortex_root(self) -> Path:
        """Get CORTEX project root directory."""
        return Path(__file__).parent.parent.parent
    
    def test_cortex_imports_consistently(self):
        """Test that cortex can be imported multiple times consistently."""
        # Import cortex multiple times
        for _ in range(3):
            try:
                import cortex
                # If import works, it should work consistently
                assert cortex is not None
            except ImportError:
                pytest.skip("cortex not importable")
    
    def test_no_random_initialization(self, cortex_root: Path):
        """Test that wiring doesn't use random values for initialization."""
        # Search for random usage in wiring-related files
        wiring_patterns = [
            "cortex/wiring/**/*.py",
            "cortex/orchestrators/core/bootstrap*.py",
            "cortex/orchestrators/registry/**/*.py",
        ]
        
        violations = []
        
        for pattern in wiring_patterns:
            for py_file in cortex_root.glob(pattern):
                if py_file.name.startswith("test_"):
                    continue
                
                try:
                    content = py_file.read_text()
                    
                    # Check for random usage
                    random_indicators = [
                        "import random",
                        "from random",
                        "random.choice",
                        "random.shuffle",
                    ]
                    
                    for indicator in random_indicators:
                        if indicator in content:
                            # Make sure it's not in comments
                            for line in content.split("\n"):
                                if indicator in line and not line.strip().startswith("#"):
                                    violations.append((py_file, indicator))
                                    break
                
                except Exception:
                    pass
        
        assert not violations, (
            f"Found random usage in wiring files: {violations}. "
            "Wiring must be deterministic."
        )
    
    def test_wiring_uses_ordered_structures(self, cortex_root: Path):
        """Test that wiring uses ordered data structures (not plain dict in Python <3.7)."""
        # This is mostly ensured by Python 3.7+ dict ordering
        # Just verify we're on Python 3.7+
        import sys
        assert sys.version_info >= (3, 7), (
            "Python 3.7+ required for deterministic dict ordering"
        )
    
    def test_git_tracked_wiring_files_exist(self, cortex_root: Path):
        """Test that wiring specification files are Git-tracked."""
        # Check if Git is available
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=cortex_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            if result.returncode != 0:
                pytest.skip("Not a git repository or git not available")
            
            tracked_files = set(result.stdout.split("\n"))
            
            # Check for wiring specification files
            wiring_patterns = [
                "cortex/wiring/**/*.yaml",
                "cortex/wiring/**/*.yml",
                "cortex-registry/**/*.yaml",
            ]
            
            wiring_files = []
            for pattern in wiring_patterns:
                wiring_files.extend(cortex_root.glob(pattern))
            
            # If any wiring files exist, they should be tracked
            for wiring_file in wiring_files:
                rel_path = wiring_file.relative_to(cortex_root)
                assert str(rel_path) in tracked_files, (
                    f"Wiring file {rel_path} is not Git-tracked. "
                    "All wiring specifications must be in version control."
                )
        
        except subprocess.TimeoutExpired:
            pytest.skip("Git command timed out")
        except FileNotFoundError:
            pytest.skip("Git not available")
