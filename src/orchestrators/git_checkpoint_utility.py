"""
Git Checkpoint Utility - Feature 2
Automates git checkpoints with rich metadata at phase boundaries

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class GitOperationError(Exception):
    """Raised when git operations fail"""
    pass


@dataclass
class CheckpointMetadata:
    """
    Metadata for a git checkpoint
    
    Captures all information needed for rich commit messages:
    - Feature and phase identification
    - Test coverage and quality metrics
    - DoR/DoD compliance status
    - Deliverables and duration
    """
    feature_number: int
    feature_name: str
    phase_number: int
    phase_name: str
    duration_hours: Optional[float] = None
    test_coverage: Optional[int] = None
    total_tests: Optional[int] = None
    files_changed: Optional[int] = None
    dor_complete: bool = False
    dod_complete: bool = False
    deliverables: List[str] = field(default_factory=list)
    evidence_file: Optional[str] = None
    
    def __post_init__(self):
        """Validate required fields"""
        if self.feature_number is None:
            raise ValueError("feature_number required")
        if self.feature_name is None:
            raise ValueError("feature_name required")
        if self.phase_number is None:
            raise ValueError("phase_number required")
        if self.phase_name is None:
            raise ValueError("phase_name required")
    
    @property
    def test_coverage_percent(self) -> float:
        """Calculate test coverage percentage"""
        if self.total_tests and self.test_coverage is not None:
            return (self.test_coverage / self.total_tests) * 100.0
        return 0.0
    
    @property
    def compliance_status(self) -> str:
        """Format DoR/DoD compliance status"""
        dor_icon = "✅" if self.dor_complete else "⏳"
        dod_icon = "✅" if self.dod_complete else "⏳"
        return f"{dor_icon} DoR {'Complete' if self.dor_complete else 'In Progress'}, {dod_icon} DoD {'Complete' if self.dod_complete else 'In Progress'}"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckpointMetadata':
        """Create metadata from Planning Orchestrator dict"""
        # Handle test_results nested structure
        test_results = data.get('test_results', {})
        test_coverage = test_results.get('passed', data.get('test_coverage'))
        total_tests = test_results.get('total', data.get('total_tests'))
        
        return cls(
            feature_number=data['feature_number'],
            feature_name=data['feature_name'],
            phase_number=data['phase_number'],
            phase_name=data['phase_name'],
            duration_hours=data.get('duration_hours'),
            test_coverage=test_coverage,
            total_tests=total_tests,
            files_changed=data.get('files_changed'),
            dor_complete=data.get('dor_complete', False),
            dod_complete=data.get('dod_complete', False),
            deliverables=data.get('deliverables', []),
            evidence_file=data.get('evidence_file')
        )


@dataclass
class CheckpointResult:
    """Result of a checkpoint operation"""
    success: bool
    commit_hash: Optional[str] = None
    tag_name: Optional[str] = None
    files_committed: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of pre-checkpoint validation"""
    ready: bool = True
    has_warnings: bool = False
    warning_message: Optional[str] = None
    error_message: Optional[str] = None


class CommitMessageBuilder:
    """
    Builds conventional commit messages with rich metadata
    
    Follows conventional commits specification:
    <type>(<scope>): <description>
    
    Includes:
    - Phase and feature information
    - Test coverage metrics
    - DoR/DoD compliance
    - Key deliverables
    - Duration and files changed
    """
    
    def build(self, metadata: CheckpointMetadata) -> str:
        """
        Build complete commit message
        
        Args:
            metadata: Checkpoint metadata
            
        Returns:
            Formatted commit message
        """
        lines = []
        
        # Conventional commit header
        lines.append(
            f"feat(phase-{metadata.phase_number}): "
            f"{metadata.feature_name} - {metadata.phase_name}"
        )
        lines.append("")
        
        # Phase identification
        lines.append(f"Phase: {metadata.phase_number}")
        
        # Duration if available
        if metadata.duration_hours:
            lines.append(f"Duration: {metadata.duration_hours} hours")
        
        # Test coverage
        if metadata.test_coverage is not None and metadata.total_tests:
            lines.append(f"Test Coverage: {metadata.test_coverage}/{metadata.total_tests} ({metadata.test_coverage_percent:.1f}%)")
        
        # Files changed
        if metadata.files_changed:
            lines.append(f"Files Changed: {metadata.files_changed} files")
        
        # Deliverables
        if metadata.deliverables:
            lines.append("")
            lines.append("Key Deliverables:")
            for deliverable in metadata.deliverables:
                lines.append(f"- {deliverable}")
        
        # Compliance section
        lines.append("")
        lines.append("Compliance:")
        dor_status = "✅ All criteria met" if metadata.dor_complete else "⏳ In progress"
        dod_status = "✅ All criteria met" if metadata.dod_complete else "⏳ In progress"
        lines.append(f"- DoR: {dor_status}")
        lines.append(f"- DoD: {dod_status}")
        
        if metadata.test_coverage is not None and metadata.total_tests:
            lines.append(f"- Tests: ✅ {metadata.test_coverage}/{metadata.total_tests} passing")
        
        # Evidence/Analysis link
        if metadata.evidence_file:
            lines.append("")
            lines.append(f"Evidence: {metadata.evidence_file}")
        
        return "\n".join(lines)


class GitTagManager:
    """
    Manages git tag creation for phase milestones
    
    Creates annotated tags with:
    - Semantic naming: feature-N-phase-M-TIMESTAMP
    - Descriptive messages
    - Timestamp for uniqueness
    """
    
    def __init__(self, repo_path: Path):
        """
        Initialize tag manager
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path
    
    def generate_tag_name(
        self,
        feature_number: int,
        phase_number: int,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate semantic tag name
        
        Args:
            feature_number: Feature number
            phase_number: Phase number
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            Tag name like "feature-2-phase-3-20251212-163000"
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%Y%m%d-%H%M%S")
        return f"feature-{feature_number}-phase-{phase_number}-{timestamp_str}"
    
    def create_tag(self, tag_name: str, message: str) -> None:
        """
        Create annotated git tag
        
        Args:
            tag_name: Name of the tag
            message: Tag annotation message
            
        Raises:
            GitOperationError: If tag creation fails
        """
        try:
            result = subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                raise GitOperationError(f"Failed to create tag: {result.stderr}")
                
        except Exception as e:
            raise GitOperationError(f"Tag creation error: {str(e)}")


class GitCheckpointUtility:
    """
    Main utility for creating git checkpoints with rich metadata
    
    Features:
    - Automatic staging of changes
    - Rich commit messages with metrics
    - Optional tag creation
    - Branch protection warnings
    - Rollback on failure
    
    Usage:
        utility = GitCheckpointUtility(repo_path=Path.cwd())
        metadata = CheckpointMetadata(
            feature_number=2,
            feature_name="Git Checkpoint Integration",
            phase_number=3,
            phase_name="GREEN phase"
        )
        result = utility.create_checkpoint(metadata, create_tag=True)
    """
    
    def __init__(self, repo_path: Path):
        """
        Initialize checkpoint utility
        
        Args:
            repo_path: Path to git repository
            
        Raises:
            GitOperationError: If not a git repository
        """
        self.repo_path = repo_path
        self.message_builder = CommitMessageBuilder()
        self.tag_manager = GitTagManager(repo_path)
        
        # Verify git repository
        if not self._is_git_repository():
            raise GitOperationError(f"{repo_path} is not a git repository")
    
    def _is_git_repository(self) -> bool:
        """Check if directory is a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @property
    def is_git_repo(self) -> bool:
        """Property to check if directory is git repo"""
        return self._is_git_repository()
    
    def get_current_branch(self) -> str:
        """
        Get current git branch name
        
        Returns:
            Branch name
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def is_protected_branch(self, branch_name: str) -> bool:
        """
        Check if branch is protected (main/master)
        
        Args:
            branch_name: Branch to check
            
        Returns:
            True if protected
        """
        return branch_name.lower() in ["main", "master"]
    
    def has_uncommitted_changes(self) -> bool:
        """
        Check for uncommitted changes
        
        Returns:
            True if uncommitted changes exist
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return len(result.stdout.strip()) > 0
        except subprocess.CalledProcessError:
            return False
    
    def validate_ready_for_checkpoint(self) -> ValidationResult:
        """
        Validate repository is ready for checkpoint
        
        Returns:
            ValidationResult with any warnings
        """
        result = ValidationResult()
        
        # Check for uncommitted changes (warning, not blocker)
        if self.has_uncommitted_changes():
            result.has_warnings = True
            result.warning_message = "Uncommitted changes detected - will be included in checkpoint"
        
        # Check protected branch
        current_branch = self.get_current_branch()
        if self.is_protected_branch(current_branch):
            result.has_warnings = True
            warning = f"Committing to protected branch: {current_branch}"
            if result.warning_message:
                result.warning_message += f"\n{warning}"
            else:
                result.warning_message = warning
        
        return result
    
    def create_checkpoint(
        self,
        metadata: CheckpointMetadata,
        create_tag: bool = False
    ) -> CheckpointResult:
        """
        Create a git checkpoint with rich metadata
        
        Steps:
        1. Validate ready for checkpoint
        2. Stage all changes (git add .)
        3. Generate commit message
        4. Commit with metadata
        5. Optionally create tag
        
        Args:
            metadata: Checkpoint metadata
            create_tag: Whether to create git tag
            
        Returns:
            CheckpointResult with commit hash and tag
            
        Raises:
            GitOperationError: If checkpoint fails
        """
        try:
            # Validate
            validation = self.validate_ready_for_checkpoint()
            
            # Stage all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path,
                check=True
            )
            
            # Build commit message
            commit_message = self.message_builder.build(metadata)
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                # Rollback staged changes
                subprocess.run(
                    ["git", "reset", "HEAD"],
                    cwd=self.repo_path,
                    check=False
                )
                raise GitOperationError(f"Commit failed: {result.stderr}")
            
            # Get commit hash
            commit_hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = commit_hash_result.stdout.strip()
            
            # Get files committed
            files_result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            files_committed = files_result.stdout.strip().split('\n')
            
            # Create tag if requested
            tag_name = None
            if create_tag:
                tag_name = self.tag_manager.generate_tag_name(
                    metadata.feature_number,
                    metadata.phase_number
                )
                self.tag_manager.create_tag(
                    tag_name,
                    f"Feature {metadata.feature_number} Phase {metadata.phase_number} Complete"
                )
            
            return CheckpointResult(
                success=True,
                commit_hash=commit_hash,
                tag_name=tag_name,
                files_committed=files_committed
            )
            
        except GitOperationError:
            raise
        except Exception as e:
            raise GitOperationError(f"Checkpoint creation failed: {str(e)}")


if __name__ == "__main__":
    # Example usage
    utility = GitCheckpointUtility(repo_path=Path.cwd())
    
    metadata = CheckpointMetadata(
        feature_number=2,
        feature_name="Git Checkpoint Integration",
        phase_number=1,
        phase_name="RED phase - Tests written",
        test_coverage=0,
        total_tests=21,
        deliverables=[
            "21 comprehensive tests",
            "CheckpointMetadata dataclass",
            "CommitMessageBuilder",
            "GitTagManager",
            "GitCheckpointUtility"
        ]
    )
    
    print("Example commit message:")
    print("=" * 60)
    print(CommitMessageBuilder().build(metadata))
