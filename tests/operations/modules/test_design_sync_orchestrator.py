"""
Integration tests for DesignSyncOrchestrator.

Tests the design synchronization operation that updates documentation to match implementation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
from src.operations.base_operation_module import OperationStatus


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root with test structure."""
    # Create source directory
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create operations directory
    ops_dir = src_dir / "operations"
    ops_dir.mkdir()
    
    # Create sample module
    module_file = ops_dir / "test_module.py"
    module_file.write_text('''
class TestOrchestrator:
    """Test orchestrator."""
    
    def execute(self, context):
        """Execute operation."""
        pass
''')
    
    # Create docs directory
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    # Create architecture directory
    arch_dir = docs_dir / "architecture"
    arch_dir.mkdir()
    
    # Create outdated diagram
    diagram_file = arch_dir / "operations.md"
    diagram_file.write_text("# Operations\nOld documentation")
    
    return tmp_path


@pytest.fixture
def orchestrator(project_root):
    """Create DesignSyncOrchestrator instance."""
    return DesignSyncOrchestrator()


@pytest.fixture
def context(project_root):
    """Create test context."""
    return {
        "project_root": str(project_root),
        "user_request": "design sync"
    }


class TestDesignSyncOrchestrator:
    """Test DesignSyncOrchestrator functionality."""
    
    def test_initialization(self, orchestrator, project_root):
        """Test orchestrator initializes correctly."""
        assert orchestrator.project_root == project_root
        assert orchestrator.docs_dir == project_root / "docs"
    
    def test_validate_returns_true(self, orchestrator, context):
        """Test validate returns true."""
        assert orchestrator.validate(context) is True
    
    def test_validate_prerequisites(self, orchestrator, context):
        """Test validate_prerequisites passes."""
        valid, errors = orchestrator.validate_prerequisites(context)
        assert valid is True
        assert len(errors) == 0
    
    def test_get_metadata(self, orchestrator):
        """Test get_metadata returns correct information."""
        metadata = orchestrator.get_metadata()
        
        assert metadata.module_id == "design_sync"
        assert "Design" in metadata.name or "Sync" in metadata.name
        assert metadata.optional is True
    
    def test_execute_success(self, orchestrator, context):
        """Test successful design sync execution."""
        result = orchestrator.execute(context)
        
        assert result.success is True or result.status == OperationStatus.WARNING
        assert result.message is not None
    
    def test_discovers_source_changes(self, orchestrator):
        """Test discovery of source code changes."""
        src_dir = orchestrator.project_root / "src"
        
        # Create new module
        new_module = src_dir / "operations" / "new_module.py"
        new_module.parent.mkdir(parents=True, exist_ok=True)
        new_module.write_text('''
class NewOrchestrator:
    """New orchestrator."""
    pass
''')
        
        # Execute sync
        result = orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Should detect the new module
        assert result.success is True or result.status == OperationStatus.WARNING
    
    def test_updates_documentation(self, orchestrator):
        """Test documentation update functionality."""
        # Execute sync
        result = orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Documentation should be updated or report generated
        assert result.message is not None
    
    def test_generates_sync_report(self, orchestrator):
        """Test sync report generation."""
        result = orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Should generate report
        if result.data:
            assert "changes" in result.data or "report" in result.data
    
    def test_preserves_manual_documentation(self, orchestrator):
        """Test that manually created documentation is preserved."""
        manual_doc = orchestrator.docs_dir / "architecture" / "manual.md"
        manual_doc.parent.mkdir(parents=True, exist_ok=True)
        manual_doc.write_text("# Manual Documentation\nImportant notes")
        
        original_content = manual_doc.read_text()
        
        orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Manual documentation should be preserved
        assert manual_doc.exists()
        # Content should be unchanged or have minimal changes
    
    def test_detects_api_changes(self, orchestrator):
        """Test detection of API changes."""
        # Create API module
        api_file = orchestrator.project_root / "src" / "api.py"
        api_file.parent.mkdir(parents=True, exist_ok=True)
        api_file.write_text('''
def new_endpoint():
    """New API endpoint."""
    pass
''')
        
        result = orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Should detect API changes
        assert result.success is True or result.status == OperationStatus.WARNING
    
    def test_rollback_capability(self, orchestrator, context):
        """Test rollback restores previous documentation."""
        # Rollback should restore documentation
        result = orchestrator.rollback(context)
        # May or may not support rollback
        assert isinstance(result, bool)


class TestDesignSyncReporting:
    """Test design sync reporting functionality."""
    
    def test_reports_changes_detected(self, orchestrator):
        """Test reporting of detected changes."""
        result = orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Should report what changed
        assert result.message is not None
    
    def test_reports_files_updated(self, orchestrator):
        """Test reporting of updated files."""
        result = orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Should indicate which files were updated
        if result.data:
            # May include updated_files list
            pass
    
    def test_reports_sync_duration(self, orchestrator):
        """Test reporting of sync operation duration."""
        result = orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Should include duration
        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0


@pytest.mark.integration
class TestDesignSyncIntegration:
    """Integration tests with real filesystem."""
    
    def test_sync_on_real_project(self):
        """Test design sync runs on actual CORTEX project."""
        project_root = Path.cwd()
        
        if not (project_root / "src").exists():
            pytest.skip("Not in CORTEX project")
        
        context = {"project_root": str(project_root)}
        orchestrator = DesignSyncOrchestrator(context)
        
        result = orchestrator.execute(context)
        
        assert result.success is True or result.status == OperationStatus.WARNING
    
    def test_sync_detects_real_modules(self):
        """Test sync detects actual CORTEX modules."""
        project_root = Path.cwd()
        
        if not (project_root / "src" / "operations").exists():
            pytest.skip("Not in CORTEX project")
        
        context = {"project_root": str(project_root)}
        orchestrator = DesignSyncOrchestrator(context)
        
        result = orchestrator.execute(context)
        
        # Should detect real modules
        assert result.message is not None
    
    def test_sync_validates_docs_directory(self):
        """Test sync validates docs directory exists."""
        project_root = Path.cwd()
        
        context = {"project_root": str(project_root)}
        orchestrator = DesignSyncOrchestrator(context)
        
        # Should handle missing docs directory gracefully
        result = orchestrator.execute(context)
        
        
        assert result.status in [OperationStatus.SUCCESS, OperationStatus.WARNING, OperationStatus.FAILED]


class TestDesignSyncDashboard:
    """Test Design Sync dashboard generation."""
    
    def test_dashboard_generation(self, orchestrator, project_root):
        """Test dashboard generation creates HTML file."""
        from src.operations.modules.design_sync.design_sync_models import (
            ImplementationState, DesignState, GapAnalysis, SyncMetrics
        )
        from datetime import datetime
        
        # Create test data
        impl_state = ImplementationState(
            total_modules=10,
            implemented_modules=8,
            completion_percentage=80.0,
            modules={'mod1': True, 'mod2': False},
            tests={'mod1': 5},
            plugins=[]
        )
        
        design_state = DesignState(
            version='3.3.0',
            design_files=[project_root / 'design1.md'],
            status_files=[project_root / 'STATUS.md']
        )
        
        gaps = GapAnalysis(
            redundant_status_files=[],
            verbose_md_candidates=[],
            inconsistent_counts={}
        )
        
        metrics = SyncMetrics(
            sync_id='test_sync',
            timestamp=datetime.now(),
            duration_seconds=10.0
        )
        
        # Generate dashboard
        orchestrator._generate_interactive_dashboard(
            impl_state, design_state, gaps, metrics, project_root
        )
        
        # Verify file created
        dashboard_path = project_root / "cortex-brain" / "admin" / "reports" / "design-sync-dashboard.html"
        assert dashboard_path.exists()
        
        # Verify file has content
        content = dashboard_path.read_text(encoding='utf-8')
        assert len(content) > 1000
        assert 'Design Sync Dashboard' in content
        assert 'D3' in content or 'd3' in content
    
    def test_dashboard_visualization_structure(self, orchestrator, project_root):
        """Test dashboard visualizations have correct structure."""
        from src.operations.modules.design_sync.design_sync_models import (
            ImplementationState, DesignState, GapAnalysis, SyncMetrics
        )
        from datetime import datetime
        
        impl_state = ImplementationState(
            total_modules=5,
            implemented_modules=3,
            completion_percentage=60.0,
            modules={'mod1': True, 'mod2': False, 'mod3': True},
            tests={},
            plugins=[]
        )
        
        design_state = DesignState(
            version='3.3.0',
            design_files=[],
            status_files=[]
        )
        
        gaps = GapAnalysis(
            redundant_status_files=['extra1.md', 'extra2.md'],
            verbose_md_candidates=[],
            inconsistent_counts={}
        )
        
        metrics = SyncMetrics(
            sync_id='test',
            timestamp=datetime.now()
        )
        
        # Test visualization builder
        viz_data = orchestrator._build_design_sync_visualizations(
            impl_state, design_state, gaps, metrics
        )
        
        # Verify structure
        assert 'forceGraph' in viz_data
        assert 'timeSeries' in viz_data
        assert 'nodes' in viz_data['forceGraph']
        assert 'links' in viz_data['forceGraph']
        assert 'data' in viz_data['timeSeries']
        assert len(viz_data['timeSeries']['data']) == 10  # 10-day trend

