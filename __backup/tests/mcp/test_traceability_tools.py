"""
CORTEX 6.0 Traceability MCP Tools Tests

Tests for AC traceability MCP tools:
- traceability_scan: Scan tests for markers
- traceability_coverage: Generate coverage matrix
- traceability_gaps: Detect coverage gaps
- traceability_validate: Validate AC coverage

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from src.mcp.traceability_tools import (
    traceability_scan,
    traceability_coverage,
    traceability_gaps,
    traceability_validate,
    traceability_batch_validate,
)


@pytest.fixture
def workspace_root() -> str:
    """Return the CORTEX workspace root."""
    return str(Path(__file__).parent.parent.parent)


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace with test files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create tests directory
    tests_dir = Path(temp_dir) / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test file with AC markers
    test_file = tests_dir / "test_example.py"
    test_file.write_text("""
import pytest

@pytest.mark.ac_id("AC-TEST-001")
def test_first():
    pass

@pytest.mark.ac_id("AC-TEST-002")
def test_second():
    pass

@pytest.mark.ac_id("AC-TEST-001", "AC-TEST-003")
def test_multiple():
    pass

def test_no_marker():
    pass
""")
    
    # Create cortex-brain directory
    brain_dir = Path(temp_dir) / "cortex-brain" / "registry"
    brain_dir.mkdir(parents=True, exist_ok=True)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestTraceabilityScan:
    """Test traceability_scan MCP tool."""
    
    def test_scan_real_workspace(self, workspace_root):
        """Test: Scan actual CORTEX workspace returns results."""
        result = traceability_scan(workspace_root)
        
        assert result["success"] is True
        assert result["ac_count"] >= 0
        assert result["test_count"] >= 0
        assert "coverage_map" in result
    
    def test_scan_temp_workspace(self, temp_workspace):
        """Test: Scan temp workspace with known markers."""
        result = traceability_scan(temp_workspace)
        
        assert result["success"] is True
        assert result["ac_count"] == 3  # AC-TEST-001, AC-TEST-002, AC-TEST-003
        assert result["test_count"] == 4  # 4 test-AC links


class TestTraceabilityCoverage:
    """Test traceability_coverage MCP tool."""
    
    def test_coverage_real_workspace(self, workspace_root):
        """Test: Generate coverage for actual workspace."""
        result = traceability_coverage(workspace_root)
        
        assert result["success"] is True
        assert "covered_ac_count" in result
        assert "coverage_percentage" in result
    
    def test_coverage_temp_workspace(self, temp_workspace):
        """Test: Generate coverage for temp workspace."""
        result = traceability_coverage(temp_workspace)
        
        assert result["success"] is True
        assert result["covered_ac_count"] == 3


class TestTraceabilityGaps:
    """Test traceability_gaps MCP tool."""
    
    def test_gaps_real_workspace(self, workspace_root):
        """Test: Detect gaps in actual workspace."""
        result = traceability_gaps(workspace_root)
        
        assert result["success"] is True
        assert "uncovered_ac_count" in result
        assert "uncovered_ac" in result
    
    def test_gaps_include_orphans(self, temp_workspace):
        """Test: Include orphaned tests in gap report."""
        result = traceability_gaps(temp_workspace, include_orphans=True)
        
        assert result["success"] is True
        assert "orphaned_tests_count" in result


class TestTraceabilityValidate:
    """Test traceability_validate MCP tool."""
    
    def test_validate_temp_workspace_covered(self, temp_workspace):
        """Test: Validate AC with coverage."""
        result = traceability_validate(temp_workspace, "AC-TEST-001")
        
        assert result["success"] is True
        assert result["ac_id"] == "AC-TEST-001"
        assert result["has_coverage"] is True
        assert result["test_count"] == 2  # test_first and test_multiple
        assert result["validation_status"] == "COVERED"
    
    def test_validate_temp_workspace_not_covered(self, temp_workspace):
        """Test: Validate AC without coverage."""
        result = traceability_validate(temp_workspace, "AC-MISSING-999")
        
        assert result["success"] is True
        assert result["ac_id"] == "AC-MISSING-999"
        assert result["has_coverage"] is False
        assert result["test_count"] == 0
        assert result["validation_status"] == "NOT_COVERED"


class TestTraceabilityBatchValidate:
    """Test traceability_batch_validate MCP tool."""
    
    def test_batch_validate(self, temp_workspace):
        """Test: Batch validate multiple AC-IDs."""
        ac_ids = ["AC-TEST-001", "AC-TEST-002", "AC-MISSING-999"]
        result = traceability_batch_validate(temp_workspace, ac_ids)
        
        assert result["success"] is True
        assert result["total_validated"] == 3
        assert result["covered_count"] == 2
        assert result["uncovered_count"] == 1
        assert result["coverage_percentage"] == pytest.approx(66.67, rel=0.1)
    
    def test_batch_validate_empty(self, temp_workspace):
        """Test: Batch validate empty list."""
        result = traceability_batch_validate(temp_workspace, [])
        
        assert result["success"] is True
        assert result["total_validated"] == 0
        assert result["coverage_percentage"] == 0
