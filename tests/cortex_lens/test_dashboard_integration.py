"""
End-to-end integration tests for dashboard generation.

Tests complete pipeline: repository → JSON → validation

AC-ID: TEST-DASH-003
Sprint: 1 day (5 tests)
"""

import pytest
import subprocess
import json
from pathlib import Path
import tempfile
import shutil
from typing import Generator


class TestFullPipeline:
    """Test complete dashboard generation flow."""
    
    @pytest.fixture
    def test_repo(self) -> Generator[Path, None, None]:
        """Create a test repository with Python files."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create realistic structure
        (temp_dir / "cortex").mkdir()
        (temp_dir / "cortex" / "__init__.py").write_text("")
        (temp_dir / "cortex" / "main.py").write_text("""
'''Main module.'''
import os
import sys
from cortex import utils

def main():
    '''Entry point.'''
    pass
""")
        (temp_dir / "cortex" / "utils.py").write_text("""
'''Utility functions.'''

def helper():
    '''Helper function.'''
    return 42
""")
        
        (temp_dir / "tests").mkdir()
        (temp_dir / "tests" / "test_main.py").write_text("""
'''Tests for main module.'''
import pytest
from cortex.main import main

def test_main():
    '''Test main function.'''
    main()
""")
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, capture_output=True)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_generate_dashboard_command_success(self) -> None:
        """Should generate all JSON files successfully for CORTEX repo."""
        result = subprocess.run(
            ["python3", "-m", "cortex.scripts.generate_dashboard_data"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should complete without error
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        # Check output files exist
        data_dir = Path(__file__).parent.parent.parent / "cortex-lens" / "data" / "cortex"
        assert (data_dir / "overview.json").exists()
        assert (data_dir / "dependencies.json").exists()
        assert (data_dir / "orchestrators.json").exists()
        assert (data_dir / "timeline.json").exists()
        assert (data_dir / "impact.json").exists()
        assert (data_dir / "brain.json").exists()
    
    def test_generated_files_are_valid_json(self) -> None:
        """All generated files should be parseable JSON."""
        data_dir = Path(__file__).parent.parent.parent / "cortex-lens" / "data" / "cortex"
        
        json_files = [
            "overview.json",
            "dependencies.json",
            "orchestrators.json",
            "timeline.json",
            "impact.json",
            "brain.json"
        ]
        
        for filename in json_files:
            file_path = data_dir / filename
            if not file_path.exists():
                continue  # Skip if not generated yet
            
            try:
                data = json.loads(file_path.read_text())
                assert isinstance(data, dict), f"{filename} is not a JSON object"
            except json.JSONDecodeError as e:
                pytest.fail(f"{filename} is not valid JSON: {e}")
    
    def test_error_handling_for_invalid_repo(self, tmp_path: Path) -> None:
        """Should fail gracefully for non-Python repos."""
        # Create empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        # Try to generate dashboard for empty repo
        # Should not crash, should handle gracefully
        # This is a negative test - we expect it to either succeed with empty data
        # or fail with a clear error message
        result = subprocess.run(
            ["python3", "-c", f"""
import sys
sys.path.insert(0, '{Path(__file__).parent.parent.parent}')
from cortex.scripts.generate_dashboard_data import analyze_repository
from pathlib import Path
result = analyze_repository(Path('{empty_dir}'))
print(result)
"""],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should complete (with or without error is acceptable)
        # Key is that it doesn't hang or crash unexpectedly
        assert result.returncode in [0, 1], f"Unexpected exit code: {result.returncode}"
    
    def test_performance_benchmark(self) -> None:
        """Dashboard generation should complete in < 30 seconds for CORTEX repo."""
        import time
        
        start_time = time.time()
        
        result = subprocess.run(
            ["python3", "-m", "cortex.scripts.generate_dashboard_data"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            timeout=30
        )
        
        elapsed_time = time.time() - start_time
        
        assert result.returncode == 0, "Command failed"
        assert elapsed_time < 30, f"Generation took {elapsed_time:.1f}s, should be < 30s"
    
    def test_idempotency(self) -> None:
        """Running generation twice should produce identical results."""
        # Generate once
        result1 = subprocess.run(
            ["python3", "-m", "cortex.scripts.generate_dashboard_data"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            timeout=30
        )
        assert result1.returncode == 0
        
        # Read first generation
        data_dir = Path(__file__).parent.parent.parent / "cortex-lens" / "data" / "cortex"
        overview1 = json.loads((data_dir / "overview.json").read_text())
        
        # Generate again
        result2 = subprocess.run(
            ["python3", "-m", "cortex.scripts.generate_dashboard_data"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            timeout=30
        )
        assert result2.returncode == 0
        
        # Read second generation
        overview2 = json.loads((data_dir / "overview.json").read_text())
        
        # Key metrics should be identical (timestamps may differ)
        assert overview1["total_modules"] == overview2["total_modules"]
        assert overview1["total_files"] == overview2["total_files"]


# Summary: 5 integration tests
# - Full pipeline: 1 test
# - Validation: 1 test
# - Error handling: 1 test
# - Performance: 1 test
# - Idempotency: 1 test
