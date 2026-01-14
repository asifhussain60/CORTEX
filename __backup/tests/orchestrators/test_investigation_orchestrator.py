"""
Tests for Investigation Orchestrator v2.

Validates root cause analysis capabilities:
- Log analysis
- Error pattern detection
- Dependency graph analysis
- Timeline reconstruction
- Solution recommendations

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path

from src.orchestrators.investigation.investigation_orchestrator import (
    InvestigationOrchestratorV2,
    InvestigationPhase,
    InvestigationResult
)
from src.orchestrators.base.base_orchestrator import (
    OrchestratorStatus,
    OrchestratorResult
)


class TestInvestigationOrchestratorV2:
    """Test suite for Investigation Orchestrator v2."""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace."""
        workspace = tmp_path / "test_workspace"
        workspace.mkdir()
        
        # Create sample log file
        logs_dir = workspace / "logs"
        logs_dir.mkdir()
        log_file = logs_dir / "app.log"
        log_file.write_text("""
2026-01-08 10:00:00 INFO Application started
2026-01-08 10:05:00 ERROR Connection failed: timeout
2026-01-08 10:05:01 ERROR Retry attempt 1 failed
2026-01-08 10:05:02 ERROR Retry attempt 2 failed
""")
        
        return str(workspace)
    
    @pytest.fixture
    def orchestrator(self, workspace_root):
        """Create InvestigationOrchestratorV2 instance."""
        return InvestigationOrchestratorV2(workspace_root=workspace_root)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test RED: Orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.workspace_root is not None
        assert hasattr(orchestrator, 'execute')
    
    def test_log_analysis(self, orchestrator):
        """Test RED: Analyze log files for errors."""
        result = orchestrator._analyze_logs()
        
        assert result is not None
        assert 'errors' in result or 'log_entries' in result
    
    def test_error_pattern_detection(self, orchestrator):
        """Test RED: Detect error patterns."""
        result = orchestrator._detect_error_patterns()
        
        assert result is not None
        assert 'patterns' in result or 'detected' in result
    
    def test_dependency_analysis(self, orchestrator):
        """Test RED: Analyze dependency relationships."""
        result = orchestrator._analyze_dependencies()
        
        assert result is not None
        assert 'dependencies' in result or 'graph' in result
    
    def test_timeline_reconstruction(self, orchestrator):
        """Test RED: Reconstruct event timeline."""
        result = orchestrator._reconstruct_timeline()
        
        assert result is not None
        assert 'timeline' in result or 'events' in result
    
    def test_solution_recommendations(self, orchestrator):
        """Test RED: Generate solution recommendations."""
        result = orchestrator._generate_recommendations(
            analysis_data={"errors": ["Connection timeout"], "patterns": ["retry_failure"]}
        )
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_full_investigation_execution(self, orchestrator):
        """Test RED: Full investigation workflow."""
        result = orchestrator.execute(
            context={"issue": "Application connection failures"}
        )
        
        assert result.status == OrchestratorStatus.SUCCESS
        assert 'investigation_complete' in result.data
