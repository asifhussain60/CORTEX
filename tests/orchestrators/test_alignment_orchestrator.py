"""
Tests for alignment orchestrator integration
Integrates validation, diagnostics, repair, and health monitoring

TDD Phase: RED - Tests written first, expected to fail
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json

from src.orchestrators.alignment_orchestrator import (
    AlignmentOrchestrator,
    AlignmentResult,
    AlignmentStatus
)


class TestAlignmentOrchestrator:
    """Test alignment orchestrator integration"""
    
    @pytest.fixture
    def temp_cortex_dir(self):
        """Create temporary CORTEX directory with valid structure"""
        temp_dir = tempfile.mkdtemp()
        cortex_dir = Path(temp_dir) / "CORTEX"
        cortex_dir.mkdir()
        
        # Create brain structure
        brain_dir = cortex_dir / "cortex-brain"
        brain_dir.mkdir()
        for tier in ["tier0", "tier1", "tier2", "tier3", "documents", "admin", "agents"]:
            (brain_dir / tier).mkdir()
        
        # Create valid config
        config = {
            "machines": {"test": {"rootPath": str(cortex_dir), "brainPath": str(brain_dir)}},
            "version": "3.2.0"
        }
        (cortex_dir / "cortex.config.json").write_text(json.dumps(config))
        
        yield cortex_dir
        
        shutil.rmtree(temp_dir)
    
    def test_orchestrator_initialization(self, temp_cortex_dir):
        """Test AlignmentOrchestrator can be initialized"""
        orchestrator = AlignmentOrchestrator(root_path=temp_cortex_dir)
        
        assert orchestrator is not None
        assert orchestrator.root_path == temp_cortex_dir
    
    def test_run_alignment_complete_flow(self, temp_cortex_dir):
        """Test complete alignment flow"""
        orchestrator = AlignmentOrchestrator(root_path=temp_cortex_dir)
        result = orchestrator.run_alignment()
        
        assert isinstance(result, AlignmentResult)
        assert result.status in [AlignmentStatus.ALIGNED, AlignmentStatus.REPAIRED, AlignmentStatus.FAILED]
    
    def test_alignment_includes_validation(self, temp_cortex_dir):
        """Test alignment runs validation"""
        orchestrator = AlignmentOrchestrator(root_path=temp_cortex_dir)
        result = orchestrator.run_alignment()
        
        assert hasattr(result, 'validation_result')
        assert result.validation_result is not None
    
    def test_alignment_includes_diagnostics(self, temp_cortex_dir):
        """Test alignment runs diagnostics"""
        orchestrator = AlignmentOrchestrator(root_path=temp_cortex_dir)
        result = orchestrator.run_alignment()
        
        assert hasattr(result, 'diagnostic_results')
        assert result.diagnostic_results is not None
    
    def test_alignment_includes_health_score(self, temp_cortex_dir):
        """Test alignment calculates health score"""
        orchestrator = AlignmentOrchestrator(root_path=temp_cortex_dir)
        result = orchestrator.run_alignment()
        
        assert hasattr(result, 'health_score')
        assert result.health_score is not None
    
    def test_alignment_auto_repair_on_issues(self, temp_cortex_dir):
        """Test alignment auto-repairs when issues found"""
        # Remove a required directory
        (temp_cortex_dir / "cortex-brain" / "tier1").rmdir()
        
        orchestrator = AlignmentOrchestrator(root_path=temp_cortex_dir, auto_repair=True)
        result = orchestrator.run_alignment()
        
        # Should attempt repair
        assert result.repair_attempted is True
        
        # Directory should be restored
        assert (temp_cortex_dir / "cortex-brain" / "tier1").exists()
    
    def test_alignment_status_enum(self):
        """Test AlignmentStatus enum values"""
        assert AlignmentStatus.ALIGNED.value == "aligned"
        assert AlignmentStatus.REPAIRED.value == "repaired"
        assert AlignmentStatus.FAILED.value == "failed"
    
    def test_generate_alignment_report(self, temp_cortex_dir):
        """Test alignment report generation"""
        orchestrator = AlignmentOrchestrator(root_path=temp_cortex_dir)
        result = orchestrator.run_alignment()
        report = orchestrator.generate_report(result)
        
        assert isinstance(report, str)
        assert "ALIGNMENT" in report.upper()
