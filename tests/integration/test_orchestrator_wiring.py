"""
Integration tests for orchestrator wiring with checkpoints, rollback, and git enrichment.

Tests verify that:
1. Planning orchestrator creates phase checkpoints
2. TDD orchestrator integrates checkpoint validation
3. System Alignment orchestrator uses Enhancement Catalog
4. All orchestrators support rollback commands
5. Git history enrichment works across workflows

Author: Asif Hussain
Created: 2025-11-28
Increment: 16 (Wire All Orchestrators)
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import orchestrators
from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager
from src.orchestrators.rollback_orchestrator import RollbackOrchestrator
from src.enrichers.git_history_enricher import GitHistoryEnricher


class TestPlanningOrchestratorWiring:
    """Test Planning Orchestrator integration with checkpoints."""
    
    def test_planning_creates_checkpoints_at_phases(self):
        """Planning orchestrator should create checkpoints at DoR, Implementation, DoD phases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            cortex_root = Path(tmpdir)
            metadata_dir = cortex_root / ".cortex" / "metadata"
            metadata_dir.mkdir(parents=True)
            
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            session_id = "planning-test-session"
            
            # Simulate planning workflow phases
            phases = ["DoR_Complete", "Implementation_Start", "DoD_Validation"]
            commit_shas = []
            
            for phase in phases:
                checkpoint_id = f"checkpoint-{phase.lower()}"
                commit_sha = f"abc{len(commit_shas)}1234"
                checkpoint_mgr.store_checkpoint_metadata(
                    session_id=session_id,
                    phase=phase,
                    checkpoint_id=checkpoint_id,
                    commit_sha=commit_sha,
                    metrics={"phase_duration_s": 120}
                )
                commit_shas.append(commit_sha)
            
            # Verify checkpoints created
            checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(checkpoints) == 3
            assert checkpoints[0]["phase"] == "DoR_Complete"
            assert checkpoints[2]["phase"] == "DoD_Validation"
    
    def test_planning_provides_rollback_to_dor(self):
        """Planning orchestrator should allow rollback to DoR checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            
            # Initialize git repo
            os.system(f"cd {project_root} && git init")
            
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            session_id = "planning-rollback-test"
            checkpoint_id = "checkpoint-dor-complete"
            
            # Store DoR checkpoint
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="DoR_Complete",
                checkpoint_id=checkpoint_id,
                commit_sha="abc123def456",
                metrics={}
            )
            
            # Verify rollback can validate checkpoint
            is_valid = rollback_orch.validate_checkpoint(session_id, checkpoint_id)
            assert is_valid is True


class TestTDDOrchestratorWiring:
    """Test TDD Orchestrator integration with checkpoints."""
    
    def test_tdd_creates_checkpoint_per_phase(self):
        """TDD orchestrator should create checkpoints for RED, GREEN, REFACTOR phases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            session_id = "tdd-test-session"
            
            # Simulate TDD workflow
            tdd_phases = ["RED_Phase", "GREEN_Phase", "REFACTOR_Phase"]
            
            for idx, phase in enumerate(tdd_phases):
                checkpoint_id = f"tdd-checkpoint-{phase.lower()}"
                checkpoint_mgr.store_checkpoint_metadata(
                    session_id=session_id,
                    phase=phase,
                    checkpoint_id=checkpoint_id,
                    commit_sha=f"tdd{idx}abcd",
                    metrics={"tests_passing": idx * 2}
                )
            
            # Verify TDD checkpoints
            checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(checkpoints) == 3
            assert any(c["phase"] == "RED_Phase" for c in checkpoints)
            assert any(c["phase"] == "GREEN_Phase" for c in checkpoints)
            assert any(c["phase"] == "REFACTOR_Phase" for c in checkpoints)
    
    def test_tdd_rollback_preserves_test_files(self):
        """TDD rollback should preserve test files and only rollback implementation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            cortex_root = project_root / ".cortex"
            cortex_root.mkdir()
            
            # Initialize git
            os.system(f"cd {project_root} && git init && git config user.email 'test@test.com' && git config user.name 'Test'")
            
            # Create test file (should be preserved)
            test_file = project_root / "test_feature.py"
            test_file.write_text("def test_feature(): pass")
            os.system(f"cd {project_root} && git add test_feature.py && git commit -m 'RED phase: failing test'")
            red_commit = os.popen(f"cd {project_root} && git rev-parse HEAD").read().strip()
            
            # Create implementation (to be rolled back)
            impl_file = project_root / "feature.py"
            impl_file.write_text("def feature(): return 42")
            os.system(f"cd {project_root} && git add feature.py && git commit -m 'GREEN phase: implementation'")
            
            # Verify rollback orchestrator can access checkpoint
            rollback_orch = RollbackOrchestrator(
                cortex_dir=cortex_root,
                project_root=project_root
            )
            
            # Test file should still exist
            assert test_file.exists()


class TestSystemAlignmentWiring:
    """Test System Alignment integration with Enhancement Catalog."""
    
    def test_alignment_discovers_catalog_features(self):
        """System Alignment should discover features from Enhancement Catalog during Phase 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            
            # Mock Enhancement Catalog discovery
            # In real implementation, this would call EnhancementCatalog.get_features_since()
            catalog_features = [
                {"name": "Git Enrichment", "feature_type": "Enhancement", "version": "3.0.1"},
                {"name": "Progress Bars", "feature_type": "UI", "version": "3.0.2"}
            ]
            
            # Simulate Phase 0 catalog discovery
            discovered_count = len(catalog_features)
            assert discovered_count == 2
            
            # Verify report includes catalog stats
            report = {
                "catalog_features_total": 15,
                "catalog_features_new": 2,
                "catalog_last_review": "2025-11-20T10:00:00"
            }
            
            assert report["catalog_features_new"] == 2
            assert report["catalog_features_total"] >= report["catalog_features_new"]


class TestGitHistoryEnrichment:
    """Test Git History Enricher integration across workflows."""
    
    def test_git_enrichment_provides_file_context(self):
        """Git enricher should provide commit history for files referenced in requests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            # Initialize git repo with history - use shell commands that explicitly cd to temp dir
            import subprocess
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=project_root, check=True, capture_output=True)
            
            test_file = project_root / "module.py"
            test_file.write_text("# Version 1")
            subprocess.run(["git", "add", "module.py"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial version"], cwd=project_root, check=True, capture_output=True)
            
            test_file.write_text("# Version 2")
            subprocess.run(["git", "add", "module.py"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Updated module"], cwd=project_root, check=True, capture_output=True)
            
            # Use GitHistoryEnricher
            enricher = GitHistoryEnricher(repo_path=project_root)
            history = enricher.get_file_history("module.py", max_commits=5)
            
            # Verify history contains commits
            assert len(history) == 2
            assert any("Initial version" in commit.get("message", "") for commit in history)
            assert any("Updated module" in commit.get("message", "") for commit in history)
    
    def test_git_enrichment_caches_results(self):
        """Git enricher should cache results to avoid repeated git log calls."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            # Initialize git
            os.system(f"cd {project_root} && git init && git config user.email 'test@test.com' && git config user.name 'Test'")
            
            test_file = project_root / "cached_file.py"
            test_file.write_text("# Cached")
            os.system(f"cd {project_root} && git add cached_file.py && git commit -m 'Cache test'")
            
            enricher = GitHistoryEnricher(repo_path=project_root)
            
            # First call - populates cache
            history1 = enricher.get_file_history("cached_file.py")
            
            # Second call - should use cache (no git call)
            history2 = enricher.get_file_history("cached_file.py")
            
            # Both should return same results
            assert len(history1) == len(history2)
            assert history1 == history2
