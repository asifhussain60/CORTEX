"""
Integration Test: Code Refinement Toolkit

Tests the batch path hardening functionality including:
- Pattern detection
- Dry-run mode
- QA orchestrator integration
- Report generation

Author: Asif Hussain
"""

import pytest
import sys
from pathlib import Path
from typing import List

# Add scripts to path for importing batch_path_hardening
root_path = Path(__file__).parent.parent.parent
scripts_path = root_path / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# Also add src to path for QA orchestrator
src_path = root_path / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from batch_path_hardening import (
    PathHardeningOrchestrator,
    PathReplacement,
    BatchResult
)


class TestPathHardeningOrchestrator:
    """Test PathHardeningOrchestrator functionality."""
    
    def test_initialization(self):
        """Test orchestrator initializes correctly."""
        orchestrator = PathHardeningOrchestrator()
        
        assert orchestrator.root_path.exists()
        assert orchestrator.src_path.exists()
        assert orchestrator.backup_dir.parent.exists()  # cortex-brain/backups should exist
    
    def test_scan_files_tier1(self):
        """Test scanning tier1 module for hardcoded paths."""
        orchestrator = PathHardeningOrchestrator()
        
        files = orchestrator.scan_files(module="tier1")
        
        # Should find files with hardcoded paths
        assert len(files) > 0
        assert all(f.suffix == ".py" for f in files)
        assert all("tier1" in str(f) for f in files)
    
    def test_analyze_file(self, tmp_path):
        """Test analyzing a file for path replacements."""
        # Create test file with hardcoded path
        test_file = tmp_path / "test_module.py"
        test_file.write_text("""
from pathlib import Path

def get_root():
    project_root = Path(__file__).parent.parent.parent
    return project_root
""")
        
        orchestrator = PathHardeningOrchestrator()
        replacements = orchestrator.analyze_file(test_file)
        
        # Should detect the hardcoded path
        assert len(replacements) == 1
        assert "Path(__file__).parent.parent.parent" in replacements[0].old_pattern
        assert "get_root_path()" in replacements[0].new_pattern
    
    def test_dry_run_mode(self):
        """Test dry-run mode doesn't modify files."""
        orchestrator = PathHardeningOrchestrator()
        
        # Execute in dry-run mode
        result = orchestrator.execute(module="tier1", dry_run=True)
        
        assert result.dry_run is True
        assert result.files_processed >= 0
        assert result.replacements_made >= 0
        # Dry run should not create errors
        assert len(result.errors) == 0
    
    def test_report_generation(self):
        """Test report generation."""
        orchestrator = PathHardeningOrchestrator()
        
        # Execute dry-run
        result = orchestrator.execute(module="tier1", dry_run=True)
        
        # Generate report
        report = orchestrator.generate_report(result)
        
        assert "CORTEX Batch Path Hardening Report" in report
        assert "DRY RUN" in report or "APPLIED" in report
        assert "Summary:" in report
        assert f"Total files scanned: {result.total_files}" in report


class TestQAOrchestratorIntegration:
    """Test QA orchestrator integration."""
    
    def test_qa_orchestrator_has_path_hardening(self):
        """Test QA orchestrator has path hardening methods."""
        from src.orchestration_3_0.orchestrators.qa.qa_orchestrator import create_qa_orchestrator
        
        qa = create_qa_orchestrator()
        
        # Check methods exist
        assert hasattr(qa, 'execute_path_hardening')
        assert hasattr(qa, 'generate_path_hardening_report')
        assert hasattr(qa, 'path_hardening_orchestrator')
    
    def test_qa_path_hardening_dry_run(self):
        """Test QA orchestrator path hardening in dry-run mode."""
        from src.orchestration_3_0.orchestrators.qa.qa_orchestrator import create_qa_orchestrator
        
        qa = create_qa_orchestrator()
        
        # Execute path hardening
        result = qa.execute_path_hardening(module="tier1", dry_run=True)
        
        assert isinstance(result, BatchResult)
        assert result.dry_run is True
        assert result.files_processed >= 0
    
    def test_qa_report_generation(self):
        """Test QA orchestrator report generation."""
        from src.orchestration_3_0.orchestrators.qa.qa_orchestrator import create_qa_orchestrator
        
        qa = create_qa_orchestrator()
        
        # Execute and generate report
        result = qa.execute_path_hardening(module="tier1", dry_run=True)
        report = qa.generate_path_hardening_report(result)
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "CORTEX Batch Path Hardening Report" in report


class TestPatternDetection:
    """Test path pattern detection."""
    
    def test_project_root_pattern(self, tmp_path):
        """Test detection of project root pattern."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
project_root = Path(__file__).parent.parent.parent
""")
        
        orchestrator = PathHardeningOrchestrator()
        replacements = orchestrator.analyze_file(test_file)
        
        assert len(replacements) == 1
        assert "get_root_path()" in replacements[0].new_pattern
    
    def test_brain_path_pattern(self, tmp_path):
        """Test detection of brain path pattern."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
brain_dir = Path(__file__).parent.parent.parent / "cortex-brain"
""")
        
        orchestrator = PathHardeningOrchestrator()
        replacements = orchestrator.analyze_file(test_file)
        
        # Should detect at least one replacement (may detect multiple patterns)
        assert len(replacements) >= 1
        # Should contain cortex-brain in old pattern
        assert any("cortex-brain" in r.old_pattern for r in replacements)
    
    def test_skip_patterns(self):
        """Test that skip patterns are respected."""
        orchestrator = PathHardeningOrchestrator()
        
        # These should be skipped
        skip_files = [
            "src/config.py",
            "src/utils/resource_resolver.py",
            "src/test_something.py",
            "src/__pycache__/module.py"
        ]
        
        for skip_file in skip_files:
            # Check if file matches skip patterns (use string match patterns)
            skip_file_path = Path(skip_file)
            should_skip = any(skip_file_path.match(pattern) for pattern in orchestrator.SKIP_PATTERNS)
            assert should_skip, f"File {skip_file} should be skipped but isn't"


class TestSafety:
    """Test safety features."""
    
    def test_dry_run_no_modifications(self, tmp_path):
        """Test dry-run doesn't modify original files."""
        # Create test file
        test_file = tmp_path / "test.py"
        original_content = """
project_root = Path(__file__).parent.parent.parent
"""
        test_file.write_text(original_content)
        
        orchestrator = PathHardeningOrchestrator()
        replacements = orchestrator.analyze_file(test_file)
        
        # Apply in dry-run mode
        result = orchestrator.apply_replacements(replacements, dry_run=True)
        
        # File should be unchanged
        assert test_file.read_text() == original_content
        assert result.dry_run is True


def test_cli_help():
    """Test CLI help command works."""
    import subprocess
    
    result = subprocess.run(
        ["python", "scripts/refine.py", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "CORTEX Code Refinement Tools" in result.stdout


def test_batch_script_help():
    """Test batch script help command works."""
    import subprocess
    
    result = subprocess.run(
        ["python", "scripts/batch_path_hardening.py", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "CORTEX Batch Path Hardening" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
