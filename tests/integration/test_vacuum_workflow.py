"""Integration tests for vacuum workflow.

Tests the complete vacuum orchestration pipeline from script to cleaners.

Authority: PHASE-VACUUM-REFACTOR S6
"""

import subprocess
import sys
from pathlib import Path
import tempfile
import shutil

import pytest


# Locate CORTEX root
CORTEX_ROOT = Path(__file__).parent.parent.parent
VACUUM_SCRIPT = CORTEX_ROOT / "scripts" / "vacuum-runner.py"


class TestVacuumWorkflow:
    """Integration tests for vacuum orchestrator workflow."""
    
    def test_vacuum_script_exists(self):
        """Verify vacuum script exists in expected location."""
        assert VACUUM_SCRIPT.exists(), f"Vacuum script not found at {VACUUM_SCRIPT}"
        assert VACUUM_SCRIPT.stat().st_size > 0, "Vacuum script is empty"
    
    def test_vacuum_dry_run_succeeds(self):
        """Test vacuum dry-run completes without errors."""
        result = subprocess.run(
            [sys.executable, str(VACUUM_SCRIPT), "--dry-run"],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        # Should complete (exit code 0 or 1 if partial success)
        assert result.returncode in (0, 1), (
            f"Vacuum failed with code {result.returncode}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        
        # Should show status in output
        assert "Status:" in result.stdout, "No status in vacuum output"
        
        # Should not have critical failures
        assert "Traceback" not in result.stderr, f"Python error:\n{result.stderr}"
    
    def test_vacuum_script_under_100_lines(self):
        """Verify vacuum script is under 100 LOC (S4 acceptance criteria)."""
        with open(VACUUM_SCRIPT) as f:
            lines = f.readlines()
        
        # Count non-blank, non-comment lines
        loc = sum(
            1 for line in lines
            if line.strip() and not line.strip().startswith("#")
        )
        
        assert loc < 100, f"Vacuum script has {loc} LOC (target: <100)"
    
    def test_vacuum_orchestrator_integration(self):
        """Test VacuumOrchestrator can be instantiated and has cleaners."""
        # Add CORTEX to path
        sys.path.insert(0, str(CORTEX_ROOT))
        
        from cortex_brain.tier1.orchestrators.vacuum.orchestrator import VacuumOrchestrator
        from cortex_brain.tier1.orchestrators.cleaners import RootDatabaseCleaner
        
        # Create orchestrator
        config = {"repo_root": CORTEX_ROOT, "dry_run": True}
        orchestrator = VacuumOrchestrator(config)
        
        # Register a cleaner
        orchestrator.register_cleaner(RootDatabaseCleaner)
        
        # Verify registration
        domains = orchestrator.list_cleaners()
        assert "root_database" in domains, "RootDatabaseCleaner not registered"
    
    def test_vacuum_no_root_pollution(self):
        """Verify no .db files exist in repository root."""
        root_dbs = list(CORTEX_ROOT.glob("*.db"))
        assert len(root_dbs) == 0, f"Found {len(root_dbs)} .db files in root: {root_dbs}"
    
    def test_vacuum_gitignore_includes_db(self):
        """Verify .gitignore includes *.db pattern."""
        gitignore = CORTEX_ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore not found"
        
        content = gitignore.read_text()
        assert "*.db" in content, ".gitignore missing *.db pattern"
    
    @pytest.mark.slow
    def test_vacuum_full_cycle_isolated_repo(self):
        """Test vacuum full cycle in isolated temporary repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "test-repo"
            repo.mkdir()
            
            # Create test files
            (repo / "test.db").write_text("test database")
            (repo / "temp-report.json").write_text("{}")
            
            # Create minimal config
            config = {"repo_root": repo, "dry_run": False}
            
            # Import and run
            sys.path.insert(0, str(CORTEX_ROOT))
            from cortex_brain.tier1.orchestrators.vacuum.orchestrator import VacuumOrchestrator
            from cortex_brain.tier1.orchestrators.cleaners import RootDatabaseCleaner
            
            orchestrator = VacuumOrchestrator(config)
            orchestrator.register_cleaner(RootDatabaseCleaner)
            
            # Run vacuum
            report = orchestrator.run(dry_run=False)
            
            # Verify execution
            assert report.status in ("SUCCESS", "PARTIAL"), f"Vacuum failed: {report.status}"
            assert report.total_actions >= 0, "No actions recorded"
            
            # Verify cleanup (test.db should be deleted)
            assert not (repo / "test.db").exists(), "test.db not deleted"


class TestCleanerPluginArchitecture:
    """Test the cleaner plugin architecture."""
    
    def test_cleaner_interface_imported(self):
        """Verify CleanerInterface can be imported."""
        sys.path.insert(0, str(CORTEX_ROOT))
        from cortex_brain.tier1.orchestrators.cleaners import CleanerInterface
        
        assert hasattr(CleanerInterface, "analyze"), "Missing analyze method"
        assert hasattr(CleanerInterface, "execute"), "Missing execute method"
        assert hasattr(CleanerInterface, "rollback"), "Missing rollback method"
    
    def test_cleaner_registry_imported(self):
        """Verify CleanerRegistry can be imported."""
        sys.path.insert(0, str(CORTEX_ROOT))
        from cortex_brain.tier1.orchestrators.cleaners import CleanerRegistry
        
        registry = CleanerRegistry()
        assert hasattr(registry, "register"), "Missing register method"
        assert hasattr(registry, "get"), "Missing get method"
        assert hasattr(registry, "list_domains"), "Missing list_domains method"
    
    def test_root_database_cleaner_imported(self):
        """Verify RootDatabaseCleaner can be imported."""
        sys.path.insert(0, str(CORTEX_ROOT))
        from cortex_brain.tier1.orchestrators.cleaners import RootDatabaseCleaner
        
        assert RootDatabaseCleaner.__name__ == "RootDatabaseCleaner"
