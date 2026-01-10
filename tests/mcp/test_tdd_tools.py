"""
CORTEX 6.0 - TDD MCP Tools Tests

Tests for TDD MCP tool wrappers.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp.tdd_tools import (
    tdd_execute,
    tdd_red_phase,
    tdd_green_phase,
    tdd_refactor_phase,
    tdd_check_code
)


@pytest.mark.ac_id("AC-TDD-001")
class TestTDDExecute:
    """Test tdd_execute MCP tool."""
    
    def test_execute_dry_run(self):
        """Test dry run TDD execution."""
        result = tdd_execute(
            feature_description="Test feature",
            dry_run=True
        )
        
        assert result["success"] is True
        assert result["dry_run"] is True
        assert "RED" in result["phases"]
        assert "GREEN" in result["phases"]
        assert "REFACTOR" in result["phases"]
    
    def test_execute_real(self):
        """Test real TDD execution."""
        temp_dir = tempfile.mkdtemp()
        try:
            result = tdd_execute(
                feature_description="Email validation",
                workspace_root=temp_dir
            )
            
            assert result["success"] is True
            assert result["tests_generated"] > 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.ac_id("AC-TDD-002")
class TestTDDRedPhase:
    """Test tdd_red_phase MCP tool."""
    
    def test_red_phase_generates_tests(self):
        """Test RED phase generates failing tests."""
        result = tdd_red_phase(
            feature_description="User authentication"
        )
        
        assert result["success"] is True
        assert result["phase"] == "RED"
        assert result["tests_generated"] > 0
        assert len(result["tests"]) > 0
        # All tests should be FAILING
        assert all(t["status"] == "FAILING" for t in result["tests"])


@pytest.mark.ac_id("AC-TDD-003")
class TestTDDGreenPhase:
    """Test tdd_green_phase MCP tool."""
    
    def test_green_phase_implementation(self):
        """Test GREEN phase creates implementation."""
        result = tdd_green_phase(
            tests_file="tests/test_feature.py"
        )
        
        assert result["success"] is True
        assert result["phase"] == "GREEN"
        assert result["implementation_created"] is True


@pytest.mark.ac_id("AC-TDD-004")
class TestTDDRefactorPhase:
    """Test tdd_refactor_phase MCP tool."""
    
    def test_refactor_phase(self):
        """Test REFACTOR phase applies clean code."""
        result = tdd_refactor_phase(
            implementation_path="src/feature.py"
        )
        
        assert result["success"] is True
        assert result["phase"] == "REFACTOR"
        assert "clean_code_score" in result


@pytest.mark.ac_id("AC-TDD-005")
class TestTDDCheckCode:
    """Test tdd_check_code MCP tool."""
    
    def test_check_clean_code(self):
        """Test checking clean code."""
        code = """
def simple_function():
    return "hello"
"""
        result = tdd_check_code(code=code)
        
        assert result["success"] is True
        assert result["clean"] is True
        assert result["violations_count"] == 0
    
    def test_check_violations(self):
        """Test detecting code violations."""
        # Very long function
        code = "\n".join([f"    line_{i} = {i}" for i in range(100)])
        code = f"def long_function():\n{code}"
        
        result = tdd_check_code(code=code)
        
        assert result["success"] is True
        assert result["violations_count"] > 0
        assert result["clean"] is False
