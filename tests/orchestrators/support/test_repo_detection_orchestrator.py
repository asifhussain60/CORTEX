"""Tests for RepoDetectionOrchestrator.

AC-ID: INQUIRY-001-NEW
Purpose: Intelligent auto-detection of CORTEX vs user repositories
Author: Asif Hussain
Date: 2026-01-27
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.models.inquiry_models import RepoType, RepoContext
from cortex.orchestrators.support.repo_detection_orchestrator import (
    RepoDetectionOrchestrator,
    DetectionSignal,
)


class TestRepoDetectionOrchestrator:
    """Test RepoDetectionOrchestrator functionality."""
    
    @pytest.fixture
    def orchestrator(self) -> RepoDetectionOrchestrator:
        """Create orchestrator instance."""
        return RepoDetectionOrchestrator()
    
    # -------------------------------------------------------------------------
    # Step 1: Keyword Analysis Tests
    # -------------------------------------------------------------------------
    
    def test_detect_cortex_by_keyword_match(self, orchestrator: RepoDetectionOrchestrator) -> None:
        """Test detection via CORTEX keyword in question."""
        question = "How does CORTEX TDDOrchestrator work?"
        
        signal = orchestrator._check_keyword_match(question)
        
        assert signal.matched is True
        assert signal.confidence >= 0.85
        assert "CORTEX" in signal.evidence
    
    def test_detect_cortex_by_orchestrator_name(self, orchestrator: RepoDetectionOrchestrator) -> None:
        """Test detection via orchestrator name."""
        question = "How does MasterOrchestrator integrate with IntentRouter?"
        
        signal = orchestrator._check_keyword_match(question)
        
        assert signal.matched is True
        assert "orchestrator" in signal.evidence.lower()
    
    def test_detect_cortex_by_core_rule(self, orchestrator: RepoDetectionOrchestrator) -> None:
        """Test detection via CORE rule reference."""
        question = "What does CORE-008 require for TDD?"
        
        signal = orchestrator._check_keyword_match(question)
        
        assert signal.matched is True
        assert "CORE-" in signal.evidence
    
    def test_no_keyword_match_user_repo(self, orchestrator: RepoDetectionOrchestrator) -> None:
        """Test no keyword match for generic question."""
        question = "How does authentication work in my app?"
        
        signal = orchestrator._check_keyword_match(question)
        
        assert signal.matched is False
        assert signal.confidence == 0.0
    
    # -------------------------------------------------------------------------
    # Step 2: Working Directory Tests
    # -------------------------------------------------------------------------
    
    def test_detect_cortex_by_cwd(self, orchestrator: RepoDetectionOrchestrator) -> None:
        """Test detection via current working directory."""
        cwd = Path("/Users/asifhussain/PROJECTS/CORTEX")
        
        signal = orchestrator._check_working_directory(cwd)
        
        assert signal.matched is True
        assert signal.confidence >= 0.95
        assert "CORTEX" in str(signal.evidence)
    
    def test_detect_cortex_by_cwd_subdirectory(self, orchestrator: RepoDetectionOrchestrator) -> None:
        """Test detection in CORTEX subdirectory."""
        cwd = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators")
        
        signal = orchestrator._check_working_directory(cwd)
        
        assert signal.matched is True
        assert signal.confidence >= 0.95
    
    def test_no_cwd_match_user_repo(self, orchestrator: RepoDetectionOrchestrator) -> None:
        """Test no match for user repository path."""
        cwd = Path("/Users/john/projects/my-app")
        
        signal = orchestrator._check_working_directory(cwd)
        
        assert signal.matched is False
        assert signal.confidence == 0.0
    
    # -------------------------------------------------------------------------
    # Step 3: File Path Tests
    # -------------------------------------------------------------------------
    
    def test_detect_cortex_by_file_paths(self, orchestrator: RepoDetectionOrchestrator) -> None:
        """Test detection via file paths in evidence."""
        file_paths = [
            "cortex/orchestrators/core/tdd_orchestrator.py",
            "cortex_brain/tier0/governance/CORE-008.yaml",
        ]
        
        signal = orchestrator._check_file_paths(file_paths)
        
        assert signal.matched is True
        assert signal.confidence >= 0.70  # Base + 2 files = 0.80
        assert "cortex/" in signal.evidence.lower()
    
    def test_no_file_path_match_user_repo(self, orchestrator: RepoDetectionOrchestrator) -> None:
        """Test no match for user repository files."""
        file_paths = [
            "src/auth/jwt.py",
            "tests/unit/test_auth.py",
        ]
        
        signal = orchestrator._check_file_paths(file_paths)
        
        assert signal.matched is False
    
    # -------------------------------------------------------------------------
    # Step 4: Git Remote Tests
    # -------------------------------------------------------------------------
    
    @patch('subprocess.run')
    def test_detect_cortex_by_git_remote(
        self, 
        mock_run: Mock, 
        orchestrator: RepoDetectionOrchestrator
    ) -> None:
        """Test detection via git remote URL."""
        mock_run.return_value = MagicMock(
            stdout="git@github.com:asifhussain60/CORTEX.git\n",
            returncode=0
        )
        
        cwd = Path("/Users/asifhussain/PROJECTS/CORTEX")
        signal = orchestrator._check_git_remote(cwd)
        
        assert signal.matched is True
        assert signal.confidence >= 0.98
        assert "CORTEX" in signal.evidence
    
    @patch('subprocess.run')
    def test_no_git_remote_match_user_repo(
        self, 
        mock_run: Mock,
        orchestrator: RepoDetectionOrchestrator
    ) -> None:
        """Test no match for user repository git remote."""
        mock_run.return_value = MagicMock(
            stdout="git@github.com:john/my-app.git\n",
            returncode=0
        )
        
        cwd = Path("/Users/john/my-app")
        signal = orchestrator._check_git_remote(cwd)
        
        assert signal.matched is False
    
    @patch('subprocess.run')
    def test_git_remote_check_handles_no_git_repo(
        self,
        mock_run: Mock,
        orchestrator: RepoDetectionOrchestrator
    ) -> None:
        """Test graceful handling of non-git directories."""
        mock_run.side_effect = Exception("Not a git repository")
        
        cwd = Path("/tmp/not-a-repo")
        signal = orchestrator._check_git_remote(cwd)
        
        assert signal.matched is False
        assert signal.confidence == 0.0
    
    # -------------------------------------------------------------------------
    # Full Detection Tests
    # -------------------------------------------------------------------------
    
    @patch('subprocess.run')
    def test_detect_cortex_high_confidence(
        self,
        mock_run: Mock,
        orchestrator: RepoDetectionOrchestrator
    ) -> None:
        """Test CORTEX detection with high confidence."""
        mock_run.return_value = MagicMock(
            stdout="git@github.com:asifhussain60/CORTEX.git\n",
            returncode=0
        )
        
        question = "How does CORTEX TDDOrchestrator work?"
        cwd = Path("/Users/asifhussain/PROJECTS/CORTEX")
        file_paths = ["cortex/orchestrators/core/tdd_orchestrator.py"]
        
        repo_ctx = orchestrator.detect_repository(
            question=question,
            current_directory=cwd,
            file_paths=file_paths,
        )
        
        assert repo_ctx.repo_type == RepoType.CORTEX
        assert repo_ctx.detection_confidence >= 0.95
        assert repo_ctx.repo_name == "CORTEX"
        assert repo_ctx.detection_signals["keyword_match"] is True
        assert repo_ctx.detection_signals["cwd_match"] is True
    
    def test_detect_user_repo_no_cortex_signals(
        self,
        orchestrator: RepoDetectionOrchestrator
    ) -> None:
        """Test user repo detection when no CORTEX signals."""
        question = "How does authentication work in my app?"
        cwd = Path("/Users/john/projects/my-app")
        file_paths = ["src/auth/jwt.py"]
        
        repo_ctx = orchestrator.detect_repository(
            question=question,
            current_directory=cwd,
            file_paths=file_paths,
        )
        
        assert repo_ctx.repo_type == RepoType.USER_REPO
        assert repo_ctx.repo_name == "my-app"
        assert repo_ctx.detection_signals["keyword_match"] is False
        assert repo_ctx.detection_signals["cwd_match"] is False
    
    def test_detect_cortex_by_keyword_alone(
        self,
        orchestrator: RepoDetectionOrchestrator
    ) -> None:
        """Test CORTEX detection via keyword even outside CORTEX directory."""
        question = "What is CORTEX MasterOrchestrator?"
        cwd = Path("/Users/john/documents")
        
        repo_ctx = orchestrator.detect_repository(
            question=question,
            current_directory=cwd,
        )
        
        assert repo_ctx.repo_type == RepoType.CORTEX
        assert repo_ctx.detection_confidence >= 0.85
    
    def test_detect_cortex_by_cwd_alone(
        self,
        orchestrator: RepoDetectionOrchestrator
    ) -> None:
        """Test CORTEX detection via cwd even without keyword."""
        question = "How does the wiring work?"  # Generic question
        cwd = Path("/Users/asifhussain/PROJECTS/CORTEX")
        
        repo_ctx = orchestrator.detect_repository(
            question=question,
            current_directory=cwd,
        )
        
        assert repo_ctx.repo_type == RepoType.CORTEX
        assert repo_ctx.detection_confidence >= 0.95
    
    def test_confidence_accumulation(
        self,
        orchestrator: RepoDetectionOrchestrator
    ) -> None:
        """Test confidence scores accumulate from multiple signals."""
        question = "CORTEX orchestrator question"  # Keyword match
        cwd = Path("/Users/asifhussain/PROJECTS/CORTEX")  # CWD match
        file_paths = ["cortex/orchestrators/core/master.py"]  # File match
        
        repo_ctx = orchestrator.detect_repository(
            question=question,
            current_directory=cwd,
            file_paths=file_paths,
        )
        
        # Multiple signals = higher confidence
        assert repo_ctx.detection_confidence >= 0.95
        signal_count = sum(1 for v in repo_ctx.detection_signals.values() if v is True)
        assert signal_count >= 3


class TestDetectionSignal:
    """Test DetectionSignal data class."""
    
    def test_create_detection_signal(self) -> None:
        """Test creating detection signal."""
        signal = DetectionSignal(
            name="keyword_match",
            matched=True,
            confidence=0.90,
            evidence="Found 'CORTEX' in question",
        )
        
        assert signal.name == "keyword_match"
        assert signal.matched is True
        assert signal.confidence == 0.90
        assert "CORTEX" in signal.evidence
