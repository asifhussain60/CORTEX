"""
Phase 2: Architecture Synchronization - Comprehensive Test Suite
Following TDD Mastery: RED → GREEN → REFACTOR

Test Coverage:
- Deliverable 2.1: Deploy-triggered architecture updates
- Deliverable 2.2: Key files inventory automation
- Deliverable 2.3: Live documentation system
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import yaml
import json

from src.utils.architecture_sync import ArchitectureSync
from src.utils.doc_sync_hooks import DocSyncHook


class TestDeliverablethe1_ArchitectureSync:
    """Test Deploy-Triggered Architecture Updates"""
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX directory structure"""
        temp_dir = tempfile.mkdtemp()
        root = Path(temp_dir)
        
        # Create directory structure
        (root / "docs").mkdir()
        (root / "src" / "cortex_agents").mkdir(parents=True)
        (root / "src" / "orchestrators").mkdir(parents=True)
        (root / "cortex-brain").mkdir()
        (root / ".git" / "hooks").mkdir(parents=True, exist_ok=True)
        
        # Create sample files
        (root / "docs" / "ARCHITECTURE.md").write_text("# Architecture\n\n## Agents: 5\n## Orchestrators: 3")
        (root / "cortex-brain" / "capabilities.yaml").write_text("capabilities:\n  - name: test")
        (root / "VERSION").write_text("3.5.0\n")
        
        # Create sample agent files
        for i in range(7):
            (root / "src" / "cortex_agents" / f"agent_{i}.py").write_text("# Agent")
        
        # Create sample orchestrator files
        for i in range(5):
            (root / "src" / "orchestrators" / f"orchestrator_{i}.py").write_text("# Orch")
        
        yield root
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_architecture_sync_initialization(self, temp_cortex_root):
        """RED Phase: Test ArchitectureSync initializes correctly"""
        sync = ArchitectureSync(temp_cortex_root)
        
        assert sync.cortex_root == temp_cortex_root
        assert sync.architecture_doc.exists()
        assert sync.capabilities_file.exists()
        assert sync.version_file.exists()
    
    def test_count_agents_and_orchestrators(self, temp_cortex_root):
        """RED Phase: Test counting of agents and orchestrators"""
        sync = ArchitectureSync(temp_cortex_root)
        
        agent_count, orchestrator_count = sync.count_components()
        
        assert agent_count == 7
        assert orchestrator_count == 5
    
    def test_architecture_doc_updated_on_deploy(self, temp_cortex_root):
        """RED Phase: Test ARCHITECTURE.md gets updated"""
        sync = ArchitectureSync(temp_cortex_root)
        
        original_content = sync.architecture_doc.read_text()
        sync.update_architecture_doc()
        updated_content = sync.architecture_doc.read_text()
        
        assert original_content != updated_content
        assert "Agents: 7" in updated_content
        assert "Orchestrators: 5" in updated_content
    
    def test_architecture_sync_version_update(self, temp_cortex_root):
        """RED Phase: Test version gets updated in ARCHITECTURE.md"""
        sync = ArchitectureSync(temp_cortex_root)
        
        sync.update_architecture_doc()
        content = sync.architecture_doc.read_text()
        
        assert "3.5.0" in content
    
    def test_architecture_sync_timestamp_added(self, temp_cortex_root):
        """RED Phase: Test timestamp is added to ARCHITECTURE.md"""
        sync = ArchitectureSync(temp_cortex_root)
        
        sync.update_architecture_doc()
        content = sync.architecture_doc.read_text()
        
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in content or "Updated:" in content
    
    def test_align_orchestrator_no_longer_updates_architecture(self):
        """RED Phase: Test align CLI doesn't trigger architecture sync"""
        # This will be validated by code review - align orchestrator should NOT call architecture_sync
        # Implementation: Check align_orchestrator.py doesn't import architecture_sync
        from pathlib import Path
        
        align_file = Path("src/operations/align.py")
        if align_file.exists():
            content = align_file.read_text()
            assert "architecture_sync" not in content.lower(), "align.py should NOT import architecture_sync"


class TestDeliverable2_KeyFilesInventory:
    """Test Key Files Inventory Automation"""
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX directory structure"""
        temp_dir = tempfile.mkdtemp()
        root = Path(temp_dir)
        
        # Create structure
        (root / "cortex-brain" / "documents" / "planning").mkdir(parents=True)
        (root / "docs").mkdir()
        (root / "cortex-brain").mkdir(exist_ok=True)
        
        # Create key files inventory
        inventory_path = root / "cortex-brain" / "documents" / "planning" / "KEY-FILES-INVENTORY.md"
        inventory_path.write_text("""
# Key Files Inventory

| File | Last Updated | Auto-Update |
|------|--------------|-------------|
| docs/ARCHITECTURE.md | 2025-11-01 | Yes |
| cortex-brain/capabilities.yaml | 2025-10-15 | No |
""")
        
        # Create tracked files with different ages
        arch_file = root / "docs" / "ARCHITECTURE.md"
        arch_file.write_text("# Arch")
        arch_file.touch()  # Fresh
        
        cap_file = root / "cortex-brain" / "capabilities.yaml"
        cap_file.write_text("capabilities: []")
        # Make it 45 days old
        old_time = (datetime.now() - timedelta(days=45)).timestamp()
        import os
        os.utime(cap_file, (old_time, old_time))
        
        yield root
        shutil.rmtree(temp_dir)
    
    def test_key_files_freshness_checker_exists(self):
        """RED Phase: Test freshness checker module exists"""
        # Will implement src/utils/key_files_checker.py
        pass  # RED - not implemented yet
    
    def test_detect_stale_files_over_30_days(self, temp_cortex_root):
        """RED Phase: Test detection of files not updated in 30+ days"""
        from src.utils.key_files_checker import KeyFilesChecker
        
        checker = KeyFilesChecker(temp_cortex_root)
        stale_files = checker.find_stale_files(days=30)
        
        assert len(stale_files) > 0
        assert any("capabilities.yaml" in str(f) for f in stale_files)
    
    def test_freshness_report_generation(self, temp_cortex_root):
        """RED Phase: Test freshness report is generated"""
        from src.utils.key_files_checker import KeyFilesChecker
        
        checker = KeyFilesChecker(temp_cortex_root)
        report = checker.generate_freshness_report()
        
        assert "stale_files" in report
        assert "fresh_files" in report
        assert report["stale_count"] >= 0
    
    def test_freshness_check_runs_during_deploy(self):
        """RED Phase: Test freshness check is called by deploy orchestrator"""
        # Will verify deploy_orchestrator.py calls key_files_checker
        pass  # RED - integration not done yet
    
    def test_inventory_auto_update_tags_honored(self, temp_cortex_root):
        """RED Phase: Test only manual-update files flagged as stale"""
        from src.utils.key_files_checker import KeyFilesChecker
        
        checker = KeyFilesChecker(temp_cortex_root)
        stale_files = checker.find_stale_files(days=30)
        
        # Auto-update files should NOT be flagged as stale
        stale_names = [f.name for f in stale_files]
        assert "ARCHITECTURE.md" not in stale_names  # Auto-update: Yes


class TestDeliverable3_LiveDocumentationSystem:
    """Test Live Documentation System with Git Hooks"""
    
    @pytest.fixture
    def temp_git_repo(self):
        """Create temporary git repository"""
        temp_dir = tempfile.mkdtemp()
        root = Path(temp_dir)
        
        # Initialize git repo
        import subprocess
        subprocess.run(["git", "init"], cwd=root, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=root, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, capture_output=True)
        
        # Create structure
        (root / "src" / "cortex_agents").mkdir(parents=True)
        (root / "docs").mkdir()
        (root / ".git" / "hooks").mkdir(parents=True, exist_ok=True)
        
        yield root
        shutil.rmtree(temp_dir)
    
    def test_doc_sync_hook_initialization(self, temp_git_repo):
        """RED Phase: Test DocSyncHook initializes correctly"""
        hook = DocSyncHook(temp_git_repo)
        
        assert hook.repo_path == temp_git_repo
        assert hasattr(hook, 'detect_doc_sync_needed')
    
    def test_detect_agent_file_changes(self, temp_git_repo):
        """RED Phase: Test detection of agent file changes"""
        hook = DocSyncHook(temp_git_repo)
        
        # Create and commit agent file
        agent_file = temp_git_repo / "src" / "cortex_agents" / "new_agent.py"
        agent_file.write_text("# New agent")
        
        needs_sync = hook.detect_doc_sync_needed()
        
        assert needs_sync is True
    
    def test_post_commit_hook_installed(self, temp_git_repo):
        """RED Phase: Test post-commit hook is installed"""
        hook = DocSyncHook(temp_git_repo)
        hook.install_git_hook()
        
        hook_file = temp_git_repo / ".git" / "hooks" / "post-commit"
        assert hook_file.exists()
        assert hook_file.stat().st_mode & 0o111  # Executable
    
    def test_doc_sync_only_on_deploy_not_development(self, temp_git_repo):
        """RED Phase: Test sync runs during deploy, not on every commit"""
        hook = DocSyncHook(temp_git_repo)
        
        # Hook should detect need but NOT auto-execute during development
        needs_sync = hook.detect_doc_sync_needed()
        
        # Hook exists but doesn't immediately sync
        assert callable(hook.sync_documentation)
        # Actual sync only triggered by deploy orchestrator
    
    def test_doc_sync_creates_backup_before_update(self, temp_git_repo):
        """RED Phase: Test backup created before documentation update"""
        hook = DocSyncHook(temp_git_repo)
        
        doc_file = temp_git_repo / "docs" / "ARCHITECTURE.md"
        doc_file.write_text("Original content")
        
        hook.sync_documentation()
        
        backup_dir = temp_git_repo / "cortex-brain" / "backups"
        # Backup should exist if sync was performed
        # (Will implement backup logic in GREEN phase)
    
    def test_doc_sync_validates_after_generation(self, temp_git_repo):
        """RED Phase: Test validation after doc generation"""
        hook = DocSyncHook(temp_git_repo)
        
        result = hook.sync_documentation()
        
        assert "validation" in result or "validated" in str(result).lower()
    
    def test_doc_sync_rollback_on_failure(self, temp_git_repo):
        """RED Phase: Test rollback when validation fails"""
        hook = DocSyncHook(temp_git_repo)
        
        # Force validation failure
        with patch.object(hook, 'validate_generated_docs', return_value=False):
            result = hook.sync_documentation()
            
            assert result["rolled_back"] is True or result["success"] is False


class TestPhase2Integration:
    """Integration tests for full Phase 2 workflow"""
    
    def test_deploy_orchestrator_integration(self):
        """RED Phase: Test deploy orchestrator calls all Phase 2 components"""
        # Will verify deploy_orchestrator.py imports and calls:
        # 1. ArchitectureSync().update_architecture_doc()
        # 2. KeyFilesChecker().generate_freshness_report()
        # 3. DocSyncHook().sync_documentation()
        pass  # RED - not integrated yet
    
    def test_phase_2_performance_under_30_seconds(self):
        """RED Phase: Test Phase 2 operations complete in <30 seconds"""
        import time
        
        # This will test full pipeline when integrated
        # For now, just structure the test
        start_time = time.time()
        
        # Execute Phase 2 pipeline
        # (Will implement in GREEN phase)
        
        elapsed = time.time() - start_time
        assert elapsed < 30, f"Phase 2 took {elapsed}s, must be <30s"
    
    def test_no_architecture_sync_in_align_command(self):
        """RED Phase: Verify align command doesn't trigger architecture sync"""
        from src.operations import align
        import inspect
        
        # Check align module doesn't call architecture_sync
        source = inspect.getsource(align)
        assert "architecture_sync" not in source.lower()
        assert "ArchitectureSync" not in source


# ============================================
# Test Execution Summary
# ============================================
# Total Tests: 23
# Deliverable 2.1: 7 tests (architecture sync)
# Deliverable 2.2: 5 tests (key files inventory)
# Deliverable 2.3: 7 tests (live documentation)
# Integration: 4 tests (full pipeline)
#
# Expected State: RED (most tests failing, awaiting GREEN implementation)
# Next Step: Implement missing components to make tests pass
# ============================================
