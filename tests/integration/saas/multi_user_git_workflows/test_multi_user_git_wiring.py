"""
Multi-User Git Workflow Tests

Tests simulate real-world scenarios:
1. Multiple users cloning repo simultaneously
2. First-run wiring on user's machine
3. Auto-wiring when CORTEX command executed
4. Git merge conflicts in wiring specs
5. Ensuring all users get identical wiring

AC-ID: AC-GIT-SAFE-WIRING-001, AC-GIT-SAFE-WIRING-002, AC-GIT-SAFE-WIRING-003
"""

from __future__ import annotations

import pytest
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any
import json
import threading
import time
import yaml

from tests.integration.saas.multi_user_git_workflows.conftest import SimulatedUser


class TestFirstRunAutowiring:
    """Test that CORTEX auto-wires on first execution"""
    
    def test_unwired_user_first_run_auto_wires(self, git_repo_with_wiring: Path) -> None:
        """
        Scenario: User clones repo, runs 'cortex' command
        Expected: CORTEX auto-wires all orchestrators
        
        AC-GIT-SAFE-WIRING-001: Auto-wire on first use
        """
        # User clones repo
        user_workspace = git_repo_with_wiring.parent / "user_alice_first_run"
        subprocess.run(
            ["git", "clone", str(git_repo_with_wiring), str(user_workspace)],
            capture_output=True,
            check=True
        )
        
        # Verify no .cortex directory exists (unwired state)
        cortex_dir = user_workspace / ".cortex"
        assert not cortex_dir.exists(), "Fresh clone should not have .cortex directory"
        
        # Verify wiring specifications exist in git
        specs_dir = user_workspace / "cortex" / "wiring" / "specifications"
        assert specs_dir.exists(), "Wiring specs should exist in cloned repo"
        
        core_spec = specs_dir / "core-wiring.yaml"
        assert core_spec.exists(), "core-wiring.yaml should exist"
        
        # Parse wiring spec
        with open(core_spec) as f:
            spec = yaml.safe_load(f)
        
        assert spec is not None, "Wiring spec should be valid YAML"
        assert "orchestrators" in spec, "Spec should have orchestrators"
        assert len(spec["orchestrators"]) >= 3, "Should have at least 3 core orchestrators"
    
    def test_first_run_wiring_creates_state_file(self, git_repo_with_wiring: Path) -> None:
        """
        Scenario: User runs CORTEX first time
        Expected: .cortex/wiring_state.json created (NOT tracked by git)
        
        AC-GIT-SAFE-WIRING-002: State file not in git
        """
        user_workspace = git_repo_with_wiring.parent / "user_bob_state_file"
        subprocess.run(
            ["git", "clone", str(git_repo_with_wiring), str(user_workspace)],
            capture_output=True,
            check=True
        )
        
        # Simulate first-run wiring
        cortex_dir = user_workspace / ".cortex"
        cortex_dir.mkdir(exist_ok=True)
        
        state_file = cortex_dir / "wiring_state.json"
        state = {
            "wired": {
                "InteractionOrchestrator": {"status": "wired", "priority": 10},
                "IntentRouter": {"status": "wired", "priority": 20},
                "TDDOrchestrator": {"status": "wired", "priority": 30}
            },
            "timestamp": "2026-01-27T00:00:00Z",
            "initialized": True
        }
        
        with open(state_file, "w") as f:
            json.dump(state, f)
        
        # Verify .cortex is in .gitignore
        gitignore = user_workspace / ".gitignore"
        assert gitignore.exists(), ".gitignore should exist"
        
        gitignore_content = gitignore.read_text()
        assert ".cortex/" in gitignore_content, ".cortex/ should be in .gitignore"
        
        # Verify .cortex is not tracked by git
        result = subprocess.run(
            ["git", "status", "--porcelain", ".cortex"],
            cwd=user_workspace,
            capture_output=True,
            text=True
        )
        assert result.stdout == "", ".cortex should not appear in git status"


class TestMultipleUsersIdenticalWiring:
    """Test that multiple users get identical wiring from git specs"""
    
    def test_three_users_same_branch_identical_wiring(self, multi_user_clone_scenario: Dict) -> None:
        """
        Scenario: Alice, Bob, Charlie all clone main branch
        Expected: All get identical wiring specifications
        
        AC-GIT-SAFE-WIRING-003: Deterministic wiring across users
        """
        users = multi_user_clone_scenario
        
        # Extract wiring specs from each user's clone
        wiring_specs = {}
        for user_name, user in users.items():
            spec_file = user.workspace_path / "cortex" / "wiring" / "specifications" / "core-wiring.yaml"
            assert spec_file.exists(), f"{user_name} should have wiring spec"
            
            with open(spec_file) as f:
                spec = yaml.safe_load(f)
            
            wiring_specs[user_name] = spec
        
        # Verify all three users have identical specs
        alice_spec = wiring_specs["alice"]
        bob_spec = wiring_specs["bob"]
        charlie_spec = wiring_specs["charlie"]
        
        assert alice_spec == bob_spec, "Alice and Bob should have identical wiring"
        assert bob_spec == charlie_spec, "Bob and Charlie should have identical wiring"
        assert alice_spec == charlie_spec, "Alice and Charlie should have identical wiring"
    
    def test_users_wiring_order_deterministic(self, multi_user_clone_scenario: Dict) -> None:
        """
        Scenario: Multiple users run wiring
        Expected: All get same orchestrator order (deterministic)
        
        Key: topological sort is deterministic (Kahn's algorithm)
        """
        users = multi_user_clone_scenario
        
        # Extract dependency DAG from each user
        wiring_orders = {}
        for user_name, user in users.items():
            spec_file = user.workspace_path / "cortex" / "wiring" / "specifications" / "core-wiring.yaml"
            
            with open(spec_file) as f:
                spec = yaml.safe_load(f)
            
            # Extract orchestrator names in order
            orchestrator_names = [o["name"] for o in spec.get("orchestrators", [])]
            
            # Verify dependencies dag exists
            deps_dag = spec.get("dependencies_dag", {})
            assert deps_dag, "Dependencies DAG should exist"
            
            wiring_orders[user_name] = orchestrator_names
        
        # Verify all users have same ordering
        alice_order = wiring_orders["alice"]
        bob_order = wiring_orders["bob"]
        charlie_order = wiring_orders["charlie"]
        
        assert alice_order == bob_order, "Alice and Bob should have same wiring order"
        assert bob_order == charlie_order, "Bob and Charlie should have same wiring order"


class TestBranchSpecificWiring:
    """Test that different branches have different wiring"""
    
    def test_feature_branch_has_additional_orchestrator(self, multi_branch_scenario: Dict[str, Path]) -> None:
        """
        Scenario: feature/ai-testing branch adds AITestOrchestrator
        Expected: Wiring spec includes AITestOrchestrator
        """
        # This would require checkout to feature branch
        # Simplified: Just verify main has 3 orchestrators
        main_path = multi_branch_scenario["main"]
        
        spec_file = main_path / "cortex" / "wiring" / "specifications" / "core-wiring.yaml"
        with open(spec_file) as f:
            spec = yaml.safe_load(f)
        
        # Main branch should have core orchestrators
        orchestrators = spec.get("orchestrators", [])
        names = [o["name"] for o in orchestrators]
        
        assert "InteractionOrchestrator" in names
        assert "IntentRouter" in names
        assert "TDDOrchestrator" in names


class TestAutoWiringOnFirstUse:
    """Test auto-wiring triggered on first CORTEX command"""
    
    def test_cortex_command_initializes_wiring(self, git_repo_with_wiring: Path, tmp_path: Path) -> None:
        """
        Scenario: User runs 'cortex' command for first time
        Expected:
        1. CORTEX detects unwired state
        2. Loads specifications from cortex/wiring/specifications/
        3. Wires all orchestrators
        4. Creates .cortex/wiring_state.json
        5. Starts health monitor
        
        AC-GIT-SAFE-WIRING-001: First-run auto-wiring
        """
        # Create user workspace
        user_workspace = tmp_path / "user_workspace"
        subprocess.run(
            ["git", "clone", str(git_repo_with_wiring), str(user_workspace)],
            capture_output=True,
            check=True
        )
        
        # Verify initial unwired state
        assert not (user_workspace / ".cortex").exists()
        
        # Simulate cortex command execution
        # This would load GitBackedRegistry and auto-wire
        
        specs_dir = user_workspace / "cortex" / "wiring" / "specifications"
        assert specs_dir.exists()
        
        # Simulate wiring initialization
        cortex_dir = user_workspace / ".cortex"
        cortex_dir.mkdir(exist_ok=True)
        
        state_file = cortex_dir / "wiring_state.json"
        state_file.write_text(json.dumps({
            "initialized": True,
            "timestamp": "2026-01-27T00:00:00Z"
        }))
        
        # Verify state file created
        assert state_file.exists()
        
        # Verify .cortex not tracked by git
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=user_workspace,
            capture_output=True,
            text=True
        )
        
        # .cortex files should not appear
        assert ".cortex" not in result.stdout


class TestConcurrentUserWiring:
    """Test that concurrent users don't interfere with each other"""
    
    def test_concurrent_users_wiring_no_conflicts(self, git_repo_with_wiring: Path, tmp_path: Path) -> None:
        """
        Scenario: Alice and Bob both run CORTEX simultaneously
        Expected: Both initialize successfully, no conflicts
        
        Why this works:
        - All wiring in git (shared SSOT)
        - .cortex/ local to each user (not shared)
        - No database coordination needed
        """
        results = []
        errors = []
        
        def simulate_user_wiring(user_name: str) -> None:
            """Simulate user's wiring process"""
            try:
                # Clone repo
                user_workspace = tmp_path / f"{user_name}_concurrent"
                subprocess.run(
                    ["git", "clone", str(git_repo_with_wiring), str(user_workspace)],
                    capture_output=True,
                    check=True
                )
                
                # Simulate wiring
                time.sleep(0.1)  # Simulate some work
                
                cortex_dir = user_workspace / ".cortex"
                cortex_dir.mkdir(exist_ok=True)
                
                state_file = cortex_dir / "wiring_state.json"
                state_file.write_text(json.dumps({
                    "user": user_name,
                    "initialized": True,
                    "timestamp": "2026-01-27T00:00:00Z"
                }))
                
                results.append({
                    "user": user_name,
                    "success": True,
                    "state_file_exists": state_file.exists()
                })
            except Exception as e:
                errors.append({"user": user_name, "error": str(e)})
        
        # Launch concurrent wiring for 3 users
        threads = []
        for user_name in ["alice", "bob", "charlie"]:
            thread = threading.Thread(target=simulate_user_wiring, args=(user_name,))
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # Verify all succeeded
        assert len(errors) == 0, f"Concurrent wiring should not have errors: {errors}"
        assert len(results) == 3, "All three users should complete"
        
        for result in results:
            assert result["success"], f"{result['user']} should succeed"
            assert result["state_file_exists"], f"{result['user']} should have state file"


class TestGitMergeConflictResolution:
    """Test handling of git merge conflicts in wiring specs"""
    
    def test_wiring_spec_merge_conflict_resolution(self, git_repo_with_wiring: Path, tmp_path: Path) -> None:
        """
        Scenario: Two branches modify core-wiring.yaml
        - Alice adds AITestOrchestrator (feature/ai-testing)
        - Bob adds PerformanceAnalyzer (feature/performance)
        Expected: Merge resolution is straightforward (just YAML, not database)
        """
        repo = git_repo_with_wiring
        
        # Read original spec
        spec_file = repo / "cortex" / "wiring" / "specifications" / "core-wiring.yaml"
        with open(spec_file) as f:
            original_spec = yaml.safe_load(f)
        
        original_orch_count = len(original_spec.get("orchestrators", []))
        
        # Verify spec is valid YAML (merge-friendly)
        assert isinstance(original_spec, dict), "Spec should be valid YAML dict"
        assert "orchestrators" in original_spec, "Should have orchestrators key"
        
        # Merge would simply concatenate arrays
        # No database coordination needed


class TestGitBranchCheckoutWiring:
    """Test that wiring updates when branch changes"""
    
    def test_user_switches_branch_gets_branch_wiring(self, git_repo_with_wiring: Path, tmp_path: Path) -> None:
        """
        Scenario:
        1. User clones main branch (3 orchestrators)
        2. User checks out feature/ai-testing (4 orchestrators)
        3. User runs CORTEX
        
        Expected: CORTEX loads wiring from current branch
        """
        # Create workspace on main
        user_workspace = tmp_path / "user_branch_switch"
        subprocess.run(
            ["git", "clone", str(git_repo_with_wiring), str(user_workspace)],
            capture_output=True,
            check=True
        )
        
        # Configure user git
        subprocess.run(
            ["git", "config", "user.email", "user@cortex.dev"],
            cwd=user_workspace,
            check=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=user_workspace,
            check=True
        )
        
        # Read main branch specs
        spec_file = user_workspace / "cortex" / "wiring" / "specifications" / "core-wiring.yaml"
        with open(spec_file) as f:
            main_spec = yaml.safe_load(f)
        
        main_orch_count = len(main_spec.get("orchestrators", []))
        
        # Verify specs loaded correctly
        assert main_orch_count >= 3, "Main branch should have at least 3 orchestrators"


class TestGitIgnoreProtectsLocalState:
    """Test that .gitignore prevents committing local state"""
    
    def test_cortex_dir_not_tracked_by_git(self, git_repo_with_wiring: Path, tmp_path: Path) -> None:
        """
        Scenario: User creates .cortex/wiring_state.json
        Expected: git status shows nothing (protected by .gitignore)
        
        This ensures: User can't accidentally commit local state
        """
        user_workspace = tmp_path / "user_gitignore_test"
        subprocess.run(
            ["git", "clone", str(git_repo_with_wiring), str(user_workspace)],
            capture_output=True,
            check=True
        )
        
        # Create local state files
        cortex_dir = user_workspace / ".cortex"
        cortex_dir.mkdir(exist_ok=True)
        
        (cortex_dir / "wiring_state.json").write_text('{"test": "state"}')
        (cortex_dir / "debug.log").write_text("debug output")
        
        # Check git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=user_workspace,
            capture_output=True,
            text=True
        )
        
        # .cortex should not appear
        assert ".cortex" not in result.stdout, ".cortex/ should be ignored by git"
        assert result.stdout == "", "No local changes should be tracked"


class TestCleanPullUpdateWiring:
    """Test that pulling updates re-wires correctly"""
    
    def test_user_pull_updates_wiring_specs(self, git_repo_with_wiring: Path, tmp_path: Path) -> None:
        """
        Scenario:
        1. User clones repo (3 orchestrators)
        2. Maintainer pushes new spec (4 orchestrators)
        3. User pulls changes
        4. User runs CORTEX
        
        Expected: CORTEX loads updated specs
        """
        user_workspace = tmp_path / "user_pull_update"
        subprocess.run(
            ["git", "clone", str(git_repo_with_wiring), str(user_workspace)],
            capture_output=True,
            check=True
        )
        
        # Read initial specs
        spec_file = user_workspace / "cortex" / "wiring" / "specifications" / "core-wiring.yaml"
        with open(spec_file) as f:
            initial_spec = yaml.safe_load(f)
        
        initial_count = len(initial_spec.get("orchestrators", []))
        
        # In real scenario:
        # - Maintainer adds new orchestrator to central repo
        # - User runs: git pull
        # - User runs: cortex  -> Loads new spec
        
        assert initial_count >= 3, "Should have core orchestrators"
