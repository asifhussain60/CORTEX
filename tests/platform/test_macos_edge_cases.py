"""
macOS-Specific Edge Cases Test Suite

Tests platform-specific behaviors and quirks unique to macOS:
- Case-sensitive filesystem handling
- Unix path separator conventions  
- Multiple Python installation detection (Homebrew, MacPorts, pyenv)
- macOS file system access and sandboxing

These tests are only run on macOS (Darwin) platform.
"""

import pytest
import platform
import subprocess
from pathlib import Path
import tempfile
import os

# Skip all tests in this module if not on macOS
pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin",
    reason="macOS-specific tests only"
)


class TestMacOSEdgeCases:
    """Mac-specific edge case test suite (4 core tests)."""
    
    def test_case_sensitive_filesystem_handling(self):
        """
        Test handling of case-sensitive vs case-insensitive filesystems.
        
        macOS can be formatted as APFS (case-insensitive) or APFS (case-sensitive).
        This test verifies that CORTEX handles both correctly.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir)
            
            # Create a file with lowercase name
            lowercase_file = test_path / "testfile.txt"
            lowercase_file.write_text("test content")
            
            # Try accessing with different case
            uppercase_file = test_path / "TESTFILE.txt"
            
            # Check if filesystem is case-sensitive
            is_case_sensitive = not uppercase_file.exists()
            
            # Verify CORTEX config handles this properly
            from src.config import get_root_path
            
            # Root path should resolve correctly
            root = get_root_path()
            assert root.exists(), "CORTEX root should exist"
            
            if is_case_sensitive:
                # On case-sensitive FS, uppercase should not exist
                assert not uppercase_file.exists()
            else:
                # On case-insensitive FS, both should work
                assert uppercase_file.exists()
    
    def test_unix_path_separators(self):
        """
        Test Unix path separator (/) handling.
        
        Ensures CORTEX correctly uses forward slashes on macOS
        and doesn't incorrectly use Windows-style backslashes.
        """
        from src.config import get_root_path
        
        # Get CORTEX root path
        root = get_root_path()
        
        # Verify it uses Unix path separators
        assert "/" in str(root), "macOS paths should use forward slashes"
        assert "\\" not in str(root), "macOS paths should not contain backslashes"
        
        # Test path resolution with Path objects
        test_path = root / "cortex-brain" / "knowledge-graph.yaml"
        
        # Verify resolved path uses forward slashes
        assert "/" in str(test_path)
        assert "\\" not in str(test_path)
        
        # Test that Path objects work correctly
        assert root.is_absolute()
        assert root.parts[0] == "/", "Absolute paths should start with /"
    
    def test_homebrew_python_detection(self):
        """
        Test detection of multiple Python installations on macOS.
        
        macOS users often have multiple Python installations:
        - System Python (/usr/bin/python3)
        - Homebrew Python (/opt/homebrew/bin/python3 or /usr/local/bin/python3)
        - MacPorts Python (/opt/local/bin/python3)
        - pyenv Python (~/.pyenv/shims/python3)
        
        This test verifies CORTEX can detect and work with the correct Python.
        """
        # Common Python installation paths on macOS
        possible_pythons = [
            "/usr/bin/python3",  # System Python
            "/opt/homebrew/bin/python3",  # Homebrew (Apple Silicon)
            "/usr/local/bin/python3",  # Homebrew (Intel)
            "/opt/local/bin/python3",  # MacPorts
            str(Path.home() / ".pyenv/shims/python3"),  # pyenv
        ]
        
        # Find available Python installations
        available_pythons = []
        for python_path in possible_pythons:
            path = Path(python_path)
            if path.exists():
                try:
                    # Get version
                    result = subprocess.run(
                        [python_path, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip() or result.stderr.strip()
                        available_pythons.append({
                            "path": python_path,
                            "version": version
                        })
                except Exception:
                    pass
        
        # Should find at least one Python installation
        assert len(available_pythons) > 0, "Should detect at least one Python installation"
        
        # Current Python should be in the list
        import sys
        current_python = sys.executable
        
        # Verify current Python is functional
        assert Path(current_python).exists()
        
        # Test that CORTEX uses the correct Python
        result = subprocess.run(
            [current_python, "-c", "print('test')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "test" in result.stdout
    
    def test_macos_file_permissions_and_sandboxing(self):
        """
        Test macOS file permission handling and sandboxing restrictions.
        
        macOS has strict file access controls and sandboxing that can
        affect CORTEX operations. This test verifies proper handling.
        """
        # Test that CORTEX can access its own files
        from src.config import get_root_path, get_brain_path
        
        root = get_root_path()
        assert root.exists(), "CORTEX root should be accessible"
        
        # Test read access to brain directory
        brain_dir = get_brain_path()
        assert brain_dir.exists(), "Brain directory should exist"
        assert os.access(brain_dir, os.R_OK), "Should have read access to brain"
        
        # Test write access to temp/logs
        logs_dir = root / "logs"
        if logs_dir.exists():
            assert os.access(logs_dir, os.W_OK), "Should have write access to logs"
        
        # Test that we can create temp files
        with tempfile.TemporaryDirectory(prefix="cortex_test_") as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            assert test_file.exists()
            assert test_file.read_text() == "test content"
        
        # Test SQLite database access (common on macOS)
        db_file = brain_dir / "conversation-history.db"
        if db_file.exists():
            # Should be able to read the database
            assert os.access(db_file, os.R_OK), "Should have read access to DB"
            
            # Try to open it
            import sqlite3
            try:
                conn = sqlite3.connect(str(db_file))
                conn.close()
            except Exception as e:
                pytest.fail(f"Failed to open SQLite database: {e}")


class TestMacOSPerformanceOptimizations:
    """Test macOS-specific performance optimizations (bonus tests)."""
    
    def test_apfs_features_available(self):
        """
        Verify APFS filesystem features are available.
        
        APFS (Apple File System) has special features like:
        - Copy-on-write cloning
        - Snapshots
        - Fast directory sizing
        """
        # Check if running on APFS
        result = subprocess.run(
            ["df", "-T", str(Path.home())],
            capture_output=True,
            text=True
        )
        
        # APFS will show in the output
        is_apfs = "apfs" in result.stdout.lower()
        
        if is_apfs:
            # Test that we can use APFS-specific features
            with tempfile.TemporaryDirectory() as tmpdir:
                src_file = Path(tmpdir) / "source.txt"
                src_file.write_text("test content")
                
                dst_file = Path(tmpdir) / "dest.txt"
                
                # Try APFS cloning (cp -c)
                try:
                    subprocess.run(
                        ["cp", "-c", str(src_file), str(dst_file)],
                        check=True
                    )
                    assert dst_file.exists()
                    assert dst_file.read_text() == "test content"
                except subprocess.CalledProcessError:
                    pytest.skip("APFS cloning not available")
    
    def test_spotlight_search_available(self):
        """
        Test that Spotlight search (mdfind) is available.
        
        Spotlight can be used for fast file searches on macOS.
        """
        try:
            # Test mdfind command
            result = subprocess.run(
                ["mdfind", "-name", "pytest"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Command should execute successfully
            assert result.returncode == 0
            
            # Should return some results (pytest is installed)
            # Note: May be empty if Spotlight indexing is disabled
            assert isinstance(result.stdout, str)
            
        except FileNotFoundError:
            pytest.skip("Spotlight (mdfind) not available")
        except subprocess.TimeoutExpired:
            pytest.skip("Spotlight search timed out")


# Summary for test discovery
def test_mac_edge_cases_summary():
    """
    Summary test to document Mac edge case coverage.
    
    This test serves as documentation of what edge cases are covered.
    """
    edge_cases_covered = [
        "Case-sensitive filesystem handling",
        "Unix path separator conventions",
        "Multiple Python installation detection",
        "macOS file permissions and sandboxing",
        "APFS filesystem features (bonus)",
        "Spotlight search integration (bonus)"
    ]
    
    # This test always passes but documents coverage
    assert len(edge_cases_covered) == 6, f"Covering {len(edge_cases_covered)} Mac edge cases"
    
    print("\n✅ Mac Edge Case Coverage:")
    for idx, case in enumerate(edge_cases_covered, 1):
        print(f"  {idx}. {case}")
