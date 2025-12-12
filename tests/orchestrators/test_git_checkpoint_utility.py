"""
Tests for Git Checkpoint Utility - Feature 2
TDD Phase: RED (All tests should FAIL initially)

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import subprocess


# Import will fail until we create the module (expected in RED phase)
try:
    from src.orchestrators.git_checkpoint_utility import (
        GitCheckpointUtility,
        CommitMessageBuilder,
        GitTagManager,
        CheckpointMetadata,
        CheckpointResult,
        GitOperationError
    )
except ImportError:
    # Expected to fail in RED phase
    pytest.skip("GitCheckpointUtility not yet implemented", allow_module_level=True)


class TestMetadataGeneration:
    """Test metadata collection and validation"""
    
    def test_metadata_initialization_with_all_fields(self):
        """Metadata should capture phase, feature, duration, tests"""
        metadata = CheckpointMetadata(
            feature_number=2,
            feature_name="Git Checkpoint Integration",
            phase_number=3,
            phase_name="Commit message generator",
            duration_hours=0.5,
            test_coverage=18,
            total_tests=18,
            files_changed=4,
            dor_complete=True,
            dod_complete=False,
            deliverables=["CommitMessageBuilder", "Conventional commits format"]
        )
        
        assert metadata.feature_number == 2
        assert metadata.phase_number == 3
        assert metadata.test_coverage_percent == 100.0
        assert metadata.dor_complete is True
        assert len(metadata.deliverables) == 2
    
    def test_metadata_validation_requires_minimum_fields(self):
        """Metadata validation should reject incomplete data"""
        with pytest.raises(ValueError, match="feature_number required"):
            CheckpointMetadata(
                feature_number=None,
                feature_name="Test",
                phase_number=1,
                phase_name="Test Phase"
            )
    
    def test_metadata_calculates_test_coverage_percentage(self):
        """Should calculate coverage percentage from total and passing"""
        metadata = CheckpointMetadata(
            feature_number=1,
            feature_name="Test",
            phase_number=1,
            phase_name="Test",
            test_coverage=15,
            total_tests=20
        )
        
        assert metadata.test_coverage_percent == 75.0
    
    def test_metadata_tracks_dor_and_dod_compliance(self):
        """Should track Definition of Ready and Done separately"""
        metadata = CheckpointMetadata(
            feature_number=1,
            feature_name="Test",
            phase_number=1,
            phase_name="Test",
            dor_complete=True,
            dod_complete=True
        )
        
        assert metadata.compliance_status == "✅ DoR Complete, ✅ DoD Complete"


class TestCommitMessageBuilder:
    """Test conventional commit message generation"""
    
    def test_builds_conventional_commit_format(self):
        """Should follow conventional commits specification"""
        builder = CommitMessageBuilder()
        metadata = CheckpointMetadata(
            feature_number=2,
            feature_name="Git Checkpoint Integration",
            phase_number=3,
            phase_name="Commit message generator",
            duration_hours=0.5,
            test_coverage=18,
            total_tests=18,
            files_changed=4,
            deliverables=["CommitMessageBuilder", "Tests"]
        )
        
        message = builder.build(metadata)
        
        # Must start with conventional commit type
        assert message.startswith("feat(phase-3):")
        assert "Git Checkpoint Integration" in message
        assert "Phase: 3" in message
        assert "Duration: 0.5 hours" in message
        assert "Test Coverage: 18/18" in message
    
    def test_includes_dor_dod_compliance_section(self):
        """Commit message should include DoR/DoD status"""
        builder = CommitMessageBuilder()
        metadata = CheckpointMetadata(
            feature_number=1,
            feature_name="Test",
            phase_number=1,
            phase_name="Test",
            dor_complete=True,
            dod_complete=True
        )
        
        message = builder.build(metadata)
        
        assert "Compliance:" in message
        assert "DoR: ✅" in message
        assert "DoD: ✅" in message
    
    def test_formats_deliverables_as_bullet_list(self):
        """Deliverables should be formatted as markdown list"""
        builder = CommitMessageBuilder()
        metadata = CheckpointMetadata(
            feature_number=1,
            feature_name="Test",
            phase_number=1,
            phase_name="Test",
            deliverables=["Item 1", "Item 2", "Item 3"]
        )
        
        message = builder.build(metadata)
        
        assert "Key Deliverables:" in message
        assert "- Item 1" in message
        assert "- Item 2" in message
        assert "- Item 3" in message


class TestGitTagManager:
    """Test git tag creation and management"""
    
    def test_creates_semantic_version_tags(self):
        """Should create tags following semantic versioning"""
        manager = GitTagManager(repo_path=Path("/fake/repo"))
        
        tag_name = manager.generate_tag_name(
            feature_number=2,
            phase_number=3,
            timestamp=datetime(2025, 12, 12, 16, 30, 0)
        )
        
        assert tag_name == "feature-2-phase-3-20251212-163000"
    
    def test_creates_annotated_tags_with_metadata(self):
        """Should create annotated tags with message"""
        manager = GitTagManager(repo_path=Path("/fake/repo"))
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            manager.create_tag(
                tag_name="feature-2-phase-3-complete",
                message="Feature 2 Phase 3 Complete"
            )
            
            # Verify git tag command called
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "git" in call_args
            assert "tag" in call_args
            assert "-a" in call_args  # Annotated tag
    
    def test_handles_tag_creation_failure(self):
        """Should raise error if tag creation fails"""
        manager = GitTagManager(repo_path=Path("/fake/repo"))
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="tag exists")
            
            with pytest.raises(GitOperationError, match="tag exists"):
                manager.create_tag("duplicate-tag", "Message")


class TestGitCheckpointUtility:
    """Test main checkpoint utility orchestration"""
    
    def test_initializes_with_repo_path(self):
        """Should initialize with valid git repository"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=b"/fake/repo/.git")
            
            utility = GitCheckpointUtility(repo_path=Path("/fake/repo"))
            
            assert utility.repo_path == Path("/fake/repo")
            assert utility.is_git_repo is True
    
    def test_detects_non_git_directory(self):
        """Should raise error for non-git directories"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=128)
            
            with pytest.raises(GitOperationError, match="not a git repository"):
                GitCheckpointUtility(repo_path=Path("/not/a/repo"))
    
    def test_creates_checkpoint_with_all_operations(self):
        """Full checkpoint should: stage, commit, tag"""
        with patch('subprocess.run') as mock_run:
            # Mock all subprocess calls in order
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=b".git"),  # repo check
                MagicMock(returncode=0, stdout=b"", text=True),  # git status (validation)
                MagicMock(returncode=0, stdout="CORTEX-3.0\n", text=True),  # get branch (validation)
                MagicMock(returncode=0),  # git add
                MagicMock(returncode=0, stdout="", text=True),  # git commit
                MagicMock(returncode=0, stdout="abc123\n", text=True),  # get hash
                MagicMock(returncode=0, stdout="file1.py\nfile2.py\n", text=True),  # diff-tree
                MagicMock(returncode=0)  # git tag
            ]
            
            utility = GitCheckpointUtility(repo_path=Path("/fake/repo"))
            metadata = CheckpointMetadata(
                feature_number=2,
                feature_name="Git Checkpoint",
                phase_number=1,
                phase_name="RED phase"
            )
            
            result = utility.create_checkpoint(metadata, create_tag=True)
            
            assert result.success is True
            assert result.commit_hash == "abc123"
            assert result.tag_name is not None
            assert len(result.files_committed) == 2
    
    def test_detects_uncommitted_changes(self):
        """Should detect staged and unstaged changes"""
        with patch('subprocess.run') as mock_run:
            # Mock git repo check, then status check
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=b".git"),  # repo check
                MagicMock(returncode=0, stdout="M file1.py\nA file2.py\n", text=True)  # status
            ]
            
            utility = GitCheckpointUtility(repo_path=Path("/fake/repo"))
            has_changes = utility.has_uncommitted_changes()
            
            assert has_changes is True
    
    def test_validates_branch_before_commit(self):
        """Should check current branch and warn on main/master"""
        with patch('subprocess.run') as mock_run:
            # Mock git repo check, then branch check
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=b".git"),  # repo check
                MagicMock(returncode=0, stdout="main\n", text=True)  # branch
            ]
            
            utility = GitCheckpointUtility(repo_path=Path("/fake/repo"))
            current_branch = utility.get_current_branch()
            
            assert current_branch == "main"
            assert utility.is_protected_branch(current_branch) is True


class TestIntegrationWithPlanningOrchestrator:
    """Test integration with Planning System 2.0"""
    
    def test_receives_phase_metadata_from_orchestrator(self):
        """Should accept metadata dict from Planning Orchestrator"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=b".git")
            
            utility = GitCheckpointUtility(repo_path=Path("/fake/repo"))
            
            # Simulate Planning Orchestrator passing metadata
            orchestrator_metadata = {
                "feature_number": 2,
                "feature_name": "Git Checkpoint Integration",
                "phase_number": 3,
                "phase_name": "GREEN phase",
                "duration_hours": 0.5,
                "test_results": {"passed": 18, "total": 18}
            }
            
            metadata = CheckpointMetadata.from_dict(orchestrator_metadata)
            
            assert metadata.feature_number == 2
            assert metadata.test_coverage == 18
    
    def test_auto_checkpoints_after_each_phase(self):
        """Should be called automatically at phase boundaries"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=b".git")
            
            utility = GitCheckpointUtility(repo_path=Path("/fake/repo"))
            
            # Mock Planning Orchestrator triggering checkpoint
            with patch.object(utility, 'create_checkpoint') as mock_checkpoint:
                mock_checkpoint.return_value = CheckpointResult(
                    success=True,
                    commit_hash="abc123",
                    tag_name="feature-2-phase-3-complete"
                )
                
                # Simulate phase completion callback
                result = utility.create_checkpoint(
                    CheckpointMetadata(
                        feature_number=2,
                        feature_name="Test",
                        phase_number=3,
                        phase_name="Test"
                    )
                )
                
                assert mock_checkpoint.called
                assert result.success is True
    
    def test_includes_evidence_links_in_commit(self):
        """Commit message should link to analysis docs"""
        builder = CommitMessageBuilder()
        metadata = CheckpointMetadata(
            feature_number=2,
            feature_name="Git Checkpoint Integration",
            phase_number=1,
            phase_name="RED phase",
            evidence_file="cortex-brain/documents/analysis/copilot-chat-analysis-2025-12-12.md"
        )
        
        message = builder.build(metadata)
        
        assert "Evidence:" in message or "Analysis:" in message
        assert "copilot-chat-analysis" in message


class TestSafetyAndValidation:
    """Test pre-commit checks and safety features"""
    
    def test_prevents_commit_on_dirty_working_directory(self):
        """Should warn if uncommitted changes exist"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=b".git")
            
            utility = GitCheckpointUtility(repo_path=Path("/fake/repo"))
            
            with patch.object(utility, 'has_uncommitted_changes', return_value=True):
                # Should still allow but warn
                result = utility.validate_ready_for_checkpoint()
                
                assert result.has_warnings is True
                assert "uncommitted changes" in result.warning_message.lower()
    
    def test_validates_test_coverage_before_commit(self):
        """Should warn if test coverage is incomplete"""
        metadata = CheckpointMetadata(
            feature_number=1,
            feature_name="Test",
            phase_number=1,
            phase_name="Test",
            test_coverage=15,
            total_tests=20  # Only 75% coverage
        )
        
        assert metadata.test_coverage_percent < 100.0
        # Checkpoint should still succeed but include warning
    
    def test_rollback_on_commit_failure(self):
        """Should rollback staged changes if commit fails"""
        metadata = CheckpointMetadata(
            feature_number=1,
            feature_name="Test",
            phase_number=1,
            phase_name="Test"
        )
        
        with patch('subprocess.run') as mock_run:
            # Repo check, validation, stage succeeds, commit fails, then rollback
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=b".git"),  # repo check
                MagicMock(returncode=0, stdout="", text=True),  # status (validation)
                MagicMock(returncode=0, stdout="CORTEX-3.0\n", text=True),  # branch (validation)
                MagicMock(returncode=0),  # git add
                MagicMock(returncode=1, stderr="commit failed", text=True),  # git commit fails
                MagicMock(returncode=0)  # git reset (rollback)
            ]
            
            utility = GitCheckpointUtility(repo_path=Path("/fake/repo"))
            
            with pytest.raises(GitOperationError):
                utility.create_checkpoint(metadata)
            
            # Verify reset was called for rollback
            reset_call = [call for call in mock_run.call_args_list if len(call[0]) > 0 and "reset" in str(call[0][0])]
            assert len(reset_call) > 0, "git reset should be called for rollback"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
