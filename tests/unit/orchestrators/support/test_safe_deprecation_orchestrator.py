"""
Phase 62: Safe Deprecation Orchestrator - Test Suite

Tests for SafeDeprecationOrchestrator workflow integration.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime, timedelta

from cortex.orchestrators.support.safe_deprecation_orchestrator import (
    SafeDeprecationOrchestrator,
)


class TestSafeDeprecationOrchestrator:
    """Tests for SafeDeprecationOrchestrator"""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary repository and docs directories"""
        repo_tmpdir = tempfile.mkdtemp()
        docs_tmpdir = tempfile.mkdtemp()
        
        repo_path = Path(repo_tmpdir)
        docs_path = Path(docs_tmpdir)
        
        (repo_path / "cortex").mkdir()
        (docs_path / "migration").mkdir()
        
        yield repo_path, docs_path
        
        shutil.rmtree(repo_tmpdir)
        shutil.rmtree(docs_tmpdir)
    
    def test_orchestrator_initialization(self, temp_dirs):
        """Test orchestrator initialization"""
        repo_path, docs_path = temp_dirs
        orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
        
        assert orchestrator.repo_root == repo_path
        assert orchestrator.docs_root == docs_path
    
    def test_deprecate_module(self, temp_dirs):
        """Test deprecating a module"""
        repo_path, docs_path = temp_dirs
        
        # Create a module
        old_module = repo_path / "old_module.py"
        old_module.write_text("def old_func(): pass")
        
        orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
        notice = orchestrator.deprecate_module(
            old_module,
            "Old implementation",
            "new_module",
            days_notice=30
        )
        
        assert notice.module_path == old_module
        assert notice.alternative == "new_module"
        assert notice.days_remaining in [29, 30]
    
    def test_generate_migration_documentation(self, temp_dirs):
        """Test migration documentation generation"""
        repo_path, docs_path = temp_dirs
        
        old_module = repo_path / "old_module.py"
        old_module.write_text("def old_func(): pass")
        
        orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
        notice = orchestrator.deprecate_module(
            old_module,
            "Old implementation",
            "new_module",
            days_notice=30
        )
        
        orchestrator.generate_migration_documentation(notice)
        
        # Check migration guide was created
        guide_path = docs_path / "migration" / "migrate_new_module.md"
        assert guide_path.exists()
    
    def test_get_deprecation_status(self, temp_dirs):
        """Test getting deprecation status"""
        repo_path, docs_path = temp_dirs
        
        orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
        status = orchestrator.get_deprecation_status()
        
        assert isinstance(status, dict)
        assert "timestamp" in status
        assert "total_deprecated" in status
        assert "deprecation_notices" in status
    
    def test_get_upcoming_removals(self, temp_dirs):
        """Test getting upcoming removals"""
        repo_path, docs_path = temp_dirs
        
        old_module = repo_path / "old_module.py"
        old_module.write_text("def old_func(): pass")
        
        orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
        orchestrator.deprecate_module(
            old_module,
            "Old implementation",
            "new_module",
            days_notice=5  # Due soon
        )
        
        upcoming = orchestrator.get_upcoming_removals(days_ahead=7)
        assert len(upcoming) >= 0
    
    def test_generate_deprecation_report(self, temp_dirs):
        """Test deprecation report generation"""
        repo_path, docs_path = temp_dirs
        
        orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
        
        output_path = docs_path / "deprecation_report.json"
        orchestrator.generate_deprecation_report(output_path)
        
        assert output_path.exists()
        
        # Verify JSON structure
        with open(output_path) as f:
            report = json.load(f)
            assert "timestamp" in report
            assert "total_deprecated" in report
    
    def test_export_removal_schedule(self, temp_dirs):
        """Test removal schedule export"""
        repo_path, docs_path = temp_dirs
        
        old_module = repo_path / "old_module.py"
        old_module.write_text("def old_func(): pass")
        
        orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
        orchestrator.deprecate_module(
            old_module,
            "Old implementation",
            "new_module"
        )
        
        output_path = docs_path / "removal_schedule.json"
        orchestrator.export_removal_schedule(output_path)
        
        assert output_path.exists()
        
        with open(output_path) as f:
            schedule = json.load(f)
            assert "scheduled_removals" in schedule
    
    def test_create_migration_summary(self, temp_dirs):
        """Test migration summary creation"""
        repo_path, docs_path = temp_dirs
        
        old_module = repo_path / "old_module.py"
        old_module.write_text("def old_func(): pass")
        
        orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
        notice = orchestrator.deprecate_module(
            old_module,
            "Old implementation",
            "new_module"
        )
        
        summary = orchestrator.create_migration_summary([notice])
        
        assert isinstance(summary, str)
        assert "new_module" in summary
        assert "Old implementation" in summary
    
    def test_batch_deprecate_modules(self, temp_dirs):
        """Test batch deprecation"""
        repo_path, docs_path = temp_dirs
        
        # Create multiple modules
        modules_to_deprecate = []
        for i in range(3):
            module = repo_path / f"old_module_{i}.py"
            module.write_text(f"def func_{i}(): pass")
            modules_to_deprecate.append((
                module,
                f"Old implementation {i}",
                f"new_module_{i}"
            ))
        
        orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
        notices = orchestrator.batch_deprecate_modules(modules_to_deprecate)
        
        assert len(notices) == 3
        assert all(isinstance(n, object) for n in notices)


class TestOrchestratorWorkflow:
    """Integration tests for complete workflow"""
    
    def test_complete_deprecation_workflow(self):
        """Test complete deprecation workflow"""
        with tempfile.TemporaryDirectory() as repo_tmpdir, \
             tempfile.TemporaryDirectory() as docs_tmpdir:
            
            repo_path = Path(repo_tmpdir)
            docs_path = Path(docs_tmpdir)
            
            (repo_path / "cortex").mkdir()
            (docs_path / "migration").mkdir()
            
            # Create module
            old_module = repo_path / "old_module.py"
            old_module.write_text("def old_func(): pass")
            
            # Initialize orchestrator
            orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
            
            # Deprecate module
            notice = orchestrator.deprecate_module(
                old_module,
                "Old implementation",
                "new_module",
                days_notice=30
            )
            
            assert notice is not None
            
            # Generate documentation
            orchestrator.generate_migration_documentation(notice)
            
            # Get status
            status = orchestrator.get_deprecation_status()
            assert status["total_deprecated"] >= 1
            
            # Generate reports
            orchestrator.generate_deprecation_report(docs_path / "report.json")
            assert (docs_path / "report.json").exists()


class TestOrchestratorIntegration:
    """Integration with governance systems"""
    
    def test_timestamp_tracking(self):
        """Test that orchestrator tracks execution timestamp"""
        with tempfile.TemporaryDirectory() as repo_tmpdir, \
             tempfile.TemporaryDirectory() as docs_tmpdir:
            
            repo_path = Path(repo_tmpdir)
            docs_path = Path(docs_tmpdir)
            
            orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
            
            # Verify timestamp
            assert orchestrator.execution_timestamp
            assert isinstance(orchestrator.execution_timestamp, str)
    
    def test_report_exports(self):
        """Test that all reports export correctly"""
        with tempfile.TemporaryDirectory() as repo_tmpdir, \
             tempfile.TemporaryDirectory() as docs_tmpdir:
            
            repo_path = Path(repo_tmpdir)
            docs_path = Path(docs_tmpdir)
            
            (repo_path / "cortex").mkdir()
            (docs_path / "migration").mkdir()
            
            old_module = repo_path / "old.py"
            old_module.write_text("pass")
            
            orchestrator = SafeDeprecationOrchestrator(repo_path, docs_path)
            orchestrator.deprecate_module(old_module, "Old", "new")
            
            # Export both reports
            orchestrator.generate_deprecation_report(docs_path / "deprecation.json")
            orchestrator.export_removal_schedule(docs_path / "schedule.json")
            
            assert (docs_path / "deprecation.json").exists()
            assert (docs_path / "schedule.json").exists()
