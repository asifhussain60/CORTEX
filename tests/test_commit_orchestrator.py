"""
Unit tests for CommitOrchestrator

Tests cover:
- Pre-flight validation
- Untracked file handling
- Pull/merge scenarios
- Push operations
- Checkpoint integration
- Error handling

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import tempfile
import shutil

from src.orchestrators.commit_orchestrator import CommitOrchestrator


class TestCommitOrchestrator(unittest.TestCase):
    """Test suite for CommitOrchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.brain_path = self.test_dir / "cortex-brain"
        self.brain_path.mkdir(parents=True)
        
        # Create orchestrator with mocked git checkpoint orchestrator
        with patch('src.orchestrators.commit_orchestrator.GitCheckpointOrchestrator'):
            self.orchestrator = CommitOrchestrator(self.test_dir, self.brain_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        self.assertEqual(self.orchestrator.project_root, self.test_dir)
        self.assertEqual(self.orchestrator.brain_path, self.brain_path)
        self.assertIsNotNone(self.orchestrator.checkpoint_orchestrator)
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_run_git_command_success(self, mock_run):
        """Test successful git command execution."""
        mock_run.return_value = Mock(returncode=0, stdout="success output", stderr="")
        
        success, output = self.orchestrator._run_git_command(["status"])
        
        self.assertTrue(success)
        self.assertEqual(output, "success output")
        mock_run.assert_called_once()
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_run_git_command_failure(self, mock_run):
        """Test failed git command execution."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error message")
        
        success, output = self.orchestrator._run_git_command(["status"])
        
        self.assertFalse(success)
        self.assertEqual(output, "error message")
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_get_current_branch(self, mock_run):
        """Test getting current branch name."""
        mock_run.return_value = Mock(returncode=0, stdout="main\n", stderr="")
        
        branch = self.orchestrator._get_current_branch()
        
        self.assertEqual(branch, "main")
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_get_untracked_files(self, mock_run):
        """Test getting list of untracked files."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="file1.txt\nfile2.py\ndir/file3.md\n",
            stderr=""
        )
        
        untracked = self.orchestrator._get_untracked_files()
        
        self.assertEqual(len(untracked), 3)
        self.assertIn("file1.txt", untracked)
        self.assertIn("file2.py", untracked)
        self.assertIn("dir/file3.md", untracked)
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_has_uncommitted_changes_true(self, mock_run):
        """Test detection of uncommitted changes."""
        mock_run.return_value = Mock(returncode=0, stdout="M file.py\n", stderr="")
        
        has_changes = self.orchestrator._has_uncommitted_changes()
        
        self.assertTrue(has_changes)
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_has_uncommitted_changes_false(self, mock_run):
        """Test detection when no uncommitted changes."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        has_changes = self.orchestrator._has_uncommitted_changes()
        
        self.assertFalse(has_changes)
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_has_merge_conflicts_true(self, mock_run):
        """Test detection of merge conflicts."""
        mock_run.return_value = Mock(returncode=0, stdout="conflict.py\n", stderr="")
        
        has_conflicts = self.orchestrator._has_merge_conflicts()
        
        self.assertTrue(has_conflicts)
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_has_merge_conflicts_false(self, mock_run):
        """Test detection when no merge conflicts."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        has_conflicts = self.orchestrator._has_merge_conflicts()
        
        self.assertFalse(has_conflicts)
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_get_remote_name(self, mock_run):
        """Test getting remote name."""
        mock_run.return_value = Mock(returncode=0, stdout="origin\n", stderr="")
        
        remote = self.orchestrator._get_remote_name()
        
        self.assertEqual(remote, "origin")
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_get_remote_name_default(self, mock_run):
        """Test getting default remote name when none configured."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        remote = self.orchestrator._get_remote_name()
        
        self.assertEqual(remote, "origin")
    
    @patch.object(CommitOrchestrator, '_get_current_branch')
    @patch.object(CommitOrchestrator, '_get_untracked_files')
    @patch.object(CommitOrchestrator, '_has_uncommitted_changes')
    def test_pre_flight_check_clean(self, mock_changes, mock_untracked, mock_branch):
        """Test pre-flight check with clean repository."""
        mock_branch.return_value = "main"
        mock_untracked.return_value = []
        mock_changes.return_value = False
        
        result = self.orchestrator.pre_flight_check()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["branch"], "main")
        self.assertEqual(result["untracked_files"], [])
        self.assertFalse(result["uncommitted_changes"])
        self.assertEqual(result["issues"], [])
    
    @patch.object(CommitOrchestrator, '_get_current_branch')
    @patch.object(CommitOrchestrator, '_get_untracked_files')
    @patch.object(CommitOrchestrator, '_has_uncommitted_changes')
    def test_pre_flight_check_with_issues(self, mock_changes, mock_untracked, mock_branch):
        """Test pre-flight check with untracked files and uncommitted changes."""
        mock_branch.return_value = "feature-branch"
        mock_untracked.return_value = ["file1.txt", "file2.py"]
        mock_changes.return_value = True
        
        result = self.orchestrator.pre_flight_check()
        
        self.assertFalse(result["success"])
        self.assertEqual(result["branch"], "feature-branch")
        self.assertEqual(len(result["untracked_files"]), 2)
        self.assertTrue(result["uncommitted_changes"])
        self.assertGreater(len(result["issues"]), 0)
    
    @patch.object(CommitOrchestrator, '_get_current_branch')
    def test_pre_flight_check_no_branch(self, mock_branch):
        """Test pre-flight check when unable to get branch."""
        mock_branch.return_value = None
        
        result = self.orchestrator.pre_flight_check()
        
        self.assertFalse(result["success"])
        self.assertIsNone(result["branch"])
        self.assertIn("Failed to get current branch", result["issues"])
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_handle_untracked_files_none(self, mock_run):
        """Test handling when no untracked files."""
        success, msg = self.orchestrator.handle_untracked_files([])
        
        self.assertTrue(success)
        self.assertEqual(msg, "No untracked files")
        mock_run.assert_not_called()
    
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_handle_untracked_files_auto_add(self, mock_run):
        """Test auto-adding untracked files."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        files = ["file1.txt", "file2.py"]
        success, msg = self.orchestrator.handle_untracked_files(files, auto_add=True)
        
        self.assertTrue(success)
        self.assertIn("Added 2 file(s)", msg)
        mock_run.assert_called_once()
    
    def test_handle_untracked_files_manual(self):
        """Test prompting for manual handling of untracked files."""
        files = ["file1.txt", "file2.py"]
        success, msg = self.orchestrator.handle_untracked_files(files, auto_add=False)
        
        self.assertFalse(success)
        self.assertIn("handle 2 untracked file(s) manually", msg)
    
    @patch.object(CommitOrchestrator, '_get_remote_name')
    @patch.object(CommitOrchestrator, '_get_current_branch')
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_pull_from_origin_success(self, mock_run, mock_branch, mock_remote):
        """Test successful pull from origin."""
        mock_remote.return_value = "origin"
        mock_branch.return_value = "main"
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # fetch
            Mock(returncode=0, stdout="Already up to date.", stderr="")  # pull
        ]
        
        with patch.object(self.orchestrator, '_has_merge_conflicts', return_value=False):
            success, msg = self.orchestrator.pull_from_origin()
        
        self.assertTrue(success)
        self.assertIn("Successfully pulled", msg)
    
    @patch.object(CommitOrchestrator, '_get_remote_name')
    @patch.object(CommitOrchestrator, '_get_current_branch')
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_pull_from_origin_conflict(self, mock_run, mock_branch, mock_remote):
        """Test pull with merge conflict."""
        mock_remote.return_value = "origin"
        mock_branch.return_value = "main"
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # fetch
            Mock(returncode=1, stdout="", stderr="CONFLICT: Merge conflict in file.py")  # pull
        ]
        
        success, msg = self.orchestrator.pull_from_origin()
        
        self.assertFalse(success)
        self.assertIn("conflict", msg.lower())
    
    @patch.object(CommitOrchestrator, '_get_remote_name')
    @patch.object(CommitOrchestrator, '_get_current_branch')
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_pull_from_origin_with_rebase(self, mock_run, mock_branch, mock_remote):
        """Test pull with rebase strategy."""
        mock_remote.return_value = "origin"
        mock_branch.return_value = "main"
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # fetch
            Mock(returncode=0, stdout="Successfully rebased", stderr="")  # pull --rebase
        ]
        
        with patch.object(self.orchestrator, '_has_merge_conflicts', return_value=False):
            success, msg = self.orchestrator.pull_from_origin(rebase=True)
        
        self.assertTrue(success)
        # Verify rebase flag was used
        pull_call = mock_run.call_args_list[1]
        self.assertIn("--rebase", pull_call[0][0])
    
    @patch.object(CommitOrchestrator, '_get_remote_name')
    @patch.object(CommitOrchestrator, '_get_current_branch')
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_push_to_origin_success(self, mock_run, mock_branch, mock_remote):
        """Test successful push to origin."""
        mock_remote.return_value = "origin"
        mock_branch.return_value = "main"
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        success, msg = self.orchestrator.push_to_origin()
        
        self.assertTrue(success)
        self.assertIn("Successfully pushed", msg)
    
    @patch.object(CommitOrchestrator, '_get_remote_name')
    @patch.object(CommitOrchestrator, '_get_current_branch')
    @patch('src.orchestrators.commit_orchestrator.subprocess.run')
    def test_push_to_origin_failure(self, mock_run, mock_branch, mock_remote):
        """Test failed push to origin."""
        mock_remote.return_value = "origin"
        mock_branch.return_value = "main"
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Permission denied")
        
        success, msg = self.orchestrator.push_to_origin()
        
        self.assertFalse(success)
        self.assertIn("Failed to push", msg)
    
    @patch.object(CommitOrchestrator, 'pre_flight_check')
    @patch.object(CommitOrchestrator, 'handle_untracked_files')
    @patch.object(CommitOrchestrator, '_run_git_command')
    @patch.object(CommitOrchestrator, 'pull_from_origin')
    @patch.object(CommitOrchestrator, 'push_to_origin')
    def test_execute_complete_workflow_clean(
        self, mock_push, mock_pull, mock_git, mock_handle, mock_preflight
    ):
        """Test complete workflow with clean repository."""
        # Mock pre-flight check (clean repo)
        mock_preflight.return_value = {
            "success": True,
            "branch": "main",
            "untracked_files": [],
            "uncommitted_changes": False,
            "issues": []
        }
        
        # Mock checkpoint creation
        self.orchestrator.checkpoint_orchestrator.create_checkpoint = Mock(return_value="abc123")
        
        # Mock pull and push success
        mock_pull.return_value = (True, "Successfully pulled")
        mock_push.return_value = (True, "Successfully pushed")
        
        result = self.orchestrator.execute()
        
        self.assertTrue(result["success"])
        self.assertTrue(result["checkpoint_created"])
        # Clean repo completes 5 steps (no untracked files step, no commit step)
        self.assertGreaterEqual(len(result["steps_completed"]), 4)
    
    @patch.object(CommitOrchestrator, 'pre_flight_check')
    @patch.object(CommitOrchestrator, 'handle_untracked_files')
    def test_execute_untracked_files_not_handled(self, mock_handle, mock_preflight):
        """Test workflow failure when untracked files not handled."""
        # Mock pre-flight check with untracked files
        mock_preflight.return_value = {
            "success": False,
            "branch": "main",
            "untracked_files": ["file1.txt"],
            "uncommitted_changes": False,
            "issues": ["Found 1 untracked file(s)"]
        }
        
        # Mock user declining to handle files
        mock_handle.return_value = (False, "Please handle untracked files manually")
        
        result = self.orchestrator.execute(auto_add_untracked=False)
        
        self.assertFalse(result["success"])
        self.assertIn("untracked", result["message"].lower())
    
    @patch.object(CommitOrchestrator, 'pre_flight_check')
    @patch.object(CommitOrchestrator, 'handle_untracked_files')
    @patch.object(CommitOrchestrator, '_run_git_command')
    @patch.object(CommitOrchestrator, 'pull_from_origin')
    def test_execute_pull_failure(self, mock_pull, mock_git, mock_handle, mock_preflight):
        """Test workflow failure on pull."""
        # Mock pre-flight check
        mock_preflight.return_value = {
            "success": True,
            "branch": "main",
            "untracked_files": [],
            "uncommitted_changes": False,
            "issues": []
        }
        
        # Mock checkpoint creation
        self.orchestrator.checkpoint_orchestrator.create_checkpoint = Mock(return_value="abc123")
        
        # Mock pull failure
        mock_pull.return_value = (False, "Merge conflict detected")
        
        result = self.orchestrator.execute()
        
        self.assertFalse(result["success"])
        self.assertIn("conflict", result["message"].lower())
        self.assertTrue(result["checkpoint_created"])
    
    @patch.object(CommitOrchestrator, 'pre_flight_check')
    @patch.object(CommitOrchestrator, 'handle_untracked_files')
    @patch.object(CommitOrchestrator, '_run_git_command')
    @patch.object(CommitOrchestrator, 'pull_from_origin')
    @patch.object(CommitOrchestrator, 'push_to_origin')
    def test_execute_with_auto_add(
        self, mock_push, mock_pull, mock_git, mock_handle, mock_preflight
    ):
        """Test workflow with auto-add untracked files."""
        # Mock pre-flight check with untracked files
        mock_preflight.return_value = {
            "success": False,
            "branch": "main",
            "untracked_files": ["file1.txt", "file2.py"],
            "uncommitted_changes": False,
            "issues": ["Found 2 untracked file(s)"]
        }
        
        # Mock auto-add success
        mock_handle.return_value = (True, "Added 2 file(s)")
        
        # Mock git commands for commit
        mock_git.side_effect = [
            (True, ""),  # add -A
            (True, "")   # commit
        ]
        
        # Mock checkpoint creation
        self.orchestrator.checkpoint_orchestrator.create_checkpoint = Mock(return_value="abc123")
        
        # Mock pull and push success
        mock_pull.return_value = (True, "Successfully pulled")
        mock_push.return_value = (True, "Successfully pushed")
        
        result = self.orchestrator.execute(auto_add_untracked=True)
        
        self.assertTrue(result["success"])
        mock_handle.assert_called_once()
        # Verify auto_add=True was passed
        self.assertTrue(mock_handle.call_args[0][1])
    
    @patch.object(CommitOrchestrator, 'pre_flight_check')
    @patch.object(CommitOrchestrator, 'handle_untracked_files')
    @patch.object(CommitOrchestrator, '_run_git_command')
    @patch.object(CommitOrchestrator, 'pull_from_origin')
    @patch.object(CommitOrchestrator, 'push_to_origin')
    def test_execute_with_custom_message(
        self, mock_push, mock_pull, mock_git, mock_handle, mock_preflight
    ):
        """Test workflow with custom commit message."""
        # Mock pre-flight check with uncommitted changes
        mock_preflight.return_value = {
            "success": False,
            "branch": "main",
            "untracked_files": [],
            "uncommitted_changes": True,
            "issues": ["Found uncommitted changes"]
        }
        
        # Mock git commands for commit
        mock_git.side_effect = [
            (True, ""),  # add -A
            (True, "")   # commit
        ]
        
        # Mock checkpoint creation
        self.orchestrator.checkpoint_orchestrator.create_checkpoint = Mock(return_value="abc123")
        
        # Mock pull and push success
        mock_pull.return_value = (True, "Successfully pulled")
        mock_push.return_value = (True, "Successfully pushed")
        
        custom_msg = "Custom commit message"
        result = self.orchestrator.execute(commit_message=custom_msg)
        
        self.assertTrue(result["success"])
        # Verify custom message was used
        commit_call = [c for c in mock_git.call_args_list if "commit" in str(c)][0]
        self.assertIn(custom_msg, str(commit_call))


if __name__ == "__main__":
    unittest.main()
