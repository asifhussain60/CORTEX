"""
ENH-087 Track 5 Phase 2: LENS Physical File Handling Implementation (GREEN)

Implements physical file lifecycle for LENS orchestrators to prevent silent
production failures (YAML profile corruption, session state loss, etc.).

Authority: ENH-087 Track 5 + Integration-First Testing pattern
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

AC_START: AC-ENH087-T5-P2-GREEN-001
Description: Repository onboarding orchestrator with physical file validation
"""

from __future__ import annotations

import logging
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ProfileStatus(Enum):
    """Status of repository profile."""
    PENDING = "pending"
    CREATED = "created"
    VALIDATED = "validated"
    ARCHIVED = "archived"


@dataclass
class RepositoryMetadata:
    """Repository metadata extracted during onboarding."""
    name: str
    path: str
    repo_type: str = "local"
    detected_languages: list[str] = field(default_factory=list)
    framework_stack: list[str] = field(default_factory=list)
    analyzed_files: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class RepositoryProfile:
    """Complete repository profile with metadata and classification."""
    repository: RepositoryMetadata
    classification: Dict[str, Any]
    metadata: Dict[str, Any]
    status: ProfileStatus = ProfileStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for YAML serialization."""
        return {
            "repository": {
                "name": self.repository.name,
                "path": self.repository.path,
                "type": self.repository.repo_type,
                "detected_languages": self.repository.detected_languages,
                "framework_stack": self.repository.framework_stack,
                "analyzed_files": self.repository.analyzed_files,
            },
            "classification": self.classification,
            "metadata": {
                **self.metadata,
                "created_at": self.repository.created_at,
                "updated_at": self.repository.updated_at,
                "status": self.status.value,
            }
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> RepositoryProfile:
        """Create profile from dictionary (loaded from YAML)."""
        repo_data = data.get("repository", {})
        meta = RepositoryMetadata(
            name=repo_data.get("name", "unknown"),
            path=repo_data.get("path", ""),
            repo_type=repo_data.get("type", "local"),
            detected_languages=repo_data.get("detected_languages", []),
            framework_stack=repo_data.get("framework_stack", []),
            analyzed_files=repo_data.get("analyzed_files", 0),
        )
        
        meta_data = data.get("metadata", {})
        status_str = meta_data.get("status", "pending")
        
        return RepositoryProfile(
            repository=meta,
            classification=data.get("classification", {}),
            metadata={k: v for k, v in meta_data.items() if k not in ["status", "created_at", "updated_at"]},
            status=ProfileStatus(status_str),
        )


class RepositoryOnboardingOrchestrator:
    """
    Orchestrates repository onboarding with physical file validation.
    
    Responsibilities:
    - Analyze repository structure
    - Create physical profile YAML files
    - Validate profile integrity
    - Manage profile lifecycle (create, update, archive)
    
    Physical Artifacts:
    - cortex_brain/onboarded_repos/{repo_id}/profile.yaml
    - cortex_brain/onboarded_repos/{repo_id}/metadata.yaml
    """
    
    def __init__(self, cortex_brain_path: Optional[Path] = None) -> None:
        """
        Initialize orchestrator.
        
        Args:
            cortex_brain_path: Path to cortex_brain directory for artifact storage
        """
        self.cortex_brain_path = cortex_brain_path or Path("cortex_brain")
        self.profiles_dir = self.cortex_brain_path / "onboarded_repos"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized RepositoryOnboardingOrchestrator: {self.profiles_dir}")
    
    def onboard_repository(
        self,
        repo_path: str,
        repo_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Onboard a repository and create physical profile files.
        
        Args:
            repo_path: Path to repository
            repo_name: Optional repository name (defaults to directory name)
        
        Returns:
            Repository ID if successful, None otherwise
        
        Raises:
            ValueError: If repo_path doesn't exist
        """
        repo_path_obj = Path(repo_path)
        if not repo_path_obj.exists():
            raise ValueError(f"Repository path doesn't exist: {repo_path}")
        
        # Generate repo ID
        repo_id = repo_name or repo_path_obj.name
        repo_profile_dir = self.profiles_dir / repo_id
        repo_profile_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Analyze repository
            profile = self._analyze_repository(repo_path_obj, repo_id)
            
            # Write physical profile file
            profile_file = repo_profile_dir / "profile.yaml"
            with open(profile_file, 'w') as f:
                yaml.dump(profile.to_dict(), f, default_flow_style=False)
            logger.info(f"Created profile file: {profile_file}")
            
            # Write metadata file
            metadata_file = repo_profile_dir / "metadata.yaml"
            with open(metadata_file, 'w') as f:
                yaml.dump({
                    "profile_id": repo_id,
                    "repo_path": str(repo_path_obj),
                    "onboarded_at": datetime.utcnow().isoformat(),
                }, f, default_flow_style=False)
            logger.info(f"Created metadata file: {metadata_file}")
            
            # Validate created files
            if not self._validate_profile_files(repo_profile_dir):
                logger.error(f"Profile validation failed: {repo_profile_dir}")
                return None
            
            return repo_id
        
        except Exception as e:
            logger.exception(f"Onboarding failed for {repo_path}: {e}")
            return None
    
    def get_repository_profile(self, repo_id: str) -> Optional[RepositoryProfile]:
        """
        Retrieve repository profile by ID.
        
        Args:
            repo_id: Repository identifier
        
        Returns:
            RepositoryProfile if found and valid, None otherwise
        """
        profile_file = self.profiles_dir / repo_id / "profile.yaml"
        
        if not profile_file.exists():
            logger.warning(f"Profile not found: {profile_file}")
            return None
        
        try:
            with open(profile_file) as f:
                data = yaml.safe_load(f)
                return RepositoryProfile.from_dict(data)
        except Exception as e:
            logger.exception(f"Failed to load profile: {profile_file}: {e}")
            return None
    
    def update_repository_profile(
        self,
        repo_id: str,
        profile: RepositoryProfile,
    ) -> bool:
        """
        Update repository profile (overwrite existing file).
        
        Args:
            repo_id: Repository identifier
            profile: Updated profile
        
        Returns:
            True if successful, False otherwise
        """
        profile_file = self.profiles_dir / repo_id / "profile.yaml"
        profile_dir = profile_file.parent
        
        if not profile_dir.exists():
            profile_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(profile_file, 'w') as f:
                yaml.dump(profile.to_dict(), f, default_flow_style=False)
            
            # Validate update
            if not self._validate_profile_files(profile_dir):
                logger.error(f"Profile validation failed after update: {profile_dir}")
                return False
            
            logger.info(f"Updated profile: {profile_file}")
            return True
        except Exception as e:
            logger.exception(f"Failed to update profile: {profile_file}: {e}")
            return False
    
    def list_onboarded_repositories(self) -> list[str]:
        """
        List all onboarded repository IDs.
        
        Returns:
            List of repository IDs
        """
        if not self.profiles_dir.exists():
            return []
        
        repo_ids = [
            d.name for d in self.profiles_dir.iterdir()
            if d.is_dir() and (d / "profile.yaml").exists()
        ]
        return sorted(repo_ids)
    
    def archive_repository(self, repo_id: str) -> bool:
        """
        Archive repository profile (mark as archived).
        
        Args:
            repo_id: Repository identifier
        
        Returns:
            True if successful, False otherwise
        """
        profile = self.get_repository_profile(repo_id)
        if not profile:
            logger.warning(f"Repository not found for archiving: {repo_id}")
            return False
        
        profile.status = ProfileStatus.ARCHIVED
        return self.update_repository_profile(repo_id, profile)
    
    def delete_repository_profile(self, repo_id: str) -> bool:
        """
        Delete repository profile files.
        
        Args:
            repo_id: Repository identifier
        
        Returns:
            True if successful, False otherwise
        """
        repo_dir = self.profiles_dir / repo_id
        
        if not repo_dir.exists():
            logger.warning(f"Repository directory not found: {repo_dir}")
            return False
        
        try:
            import shutil
            shutil.rmtree(repo_dir)
            logger.info(f"Deleted repository directory: {repo_dir}")
            return True
        except Exception as e:
            logger.exception(f"Failed to delete repository: {repo_dir}: {e}")
            return False
    
    def _analyze_repository(
        self,
        repo_path: Path,
        repo_id: str,
    ) -> RepositoryProfile:
        """
        Analyze repository structure and create profile.
        
        Args:
            repo_path: Path to repository
            repo_id: Repository identifier
        
        Returns:
            RepositoryProfile with analysis results
        """
        # Detect languages
        languages = self._detect_languages(repo_path)
        
        # Detect framework stack
        frameworks = self._detect_frameworks(repo_path)
        
        # Count analyzed files
        file_count = len(list(repo_path.glob("**/*")))
        
        metadata = RepositoryMetadata(
            name=repo_id,
            path=str(repo_path),
            detected_languages=languages,
            framework_stack=frameworks,
            analyzed_files=file_count,
            created_at=datetime.utcnow().isoformat(),
        )
        
        return RepositoryProfile(
            repository=metadata,
            classification={
                "complexity": "medium",
                "test_coverage": "unknown",
                "documentation": "partial",
            },
            metadata={
                "analyzed_files": file_count,
                "analysis_status": "complete",
            }
        )
    
    def _detect_languages(self, repo_path: Path) -> list[str]:
        """
        Detect programming languages in repository.
        
        Args:
            repo_path: Path to repository
        
        Returns:
            List of detected languages
        """
        language_extensions = {
            ".py": "Python",
            ".ts": "TypeScript",
            ".js": "JavaScript",
            ".java": "Java",
            ".cs": "C#",
            ".go": "Go",
            ".rs": "Rust",
        }
        
        detected = set()
        for ext, lang in language_extensions.items():
            if list(repo_path.glob(f"**/*{ext}")):
                detected.add(lang)
        
        return sorted(list(detected))
    
    def _detect_frameworks(self, repo_path: Path) -> list[str]:
        """
        Detect frameworks in repository.
        
        Args:
            repo_path: Path to repository
        
        Returns:
            List of detected frameworks
        """
        framework_indicators = {
            "FastAPI": ["fastapi", "requirements.txt"],
            "Django": ["django", "requirements.txt"],
            "React": ["react", "package.json"],
            "Vue": ["vue", "package.json"],
            "Angular": ["@angular", "package.json"],
        }
        
        detected = set()
        for framework, files in framework_indicators.items():
            for file_pattern in files:
                if list(repo_path.glob(f"**/*{file_pattern}*")):
                    detected.add(framework)
                    break
        
        return sorted(list(detected))
    
    def _validate_profile_files(self, repo_dir: Path) -> bool:
        """
        Validate that profile files exist and are readable.
        
        Args:
            repo_dir: Repository profile directory
        
        Returns:
            True if all required files valid, False otherwise
        """
        profile_file = repo_dir / "profile.yaml"
        metadata_file = repo_dir / "metadata.yaml"
        
        # Check existence
        if not profile_file.exists() or not metadata_file.exists():
            logger.error(f"Missing required files in {repo_dir}")
            return False
        
        # Check readability and format
        try:
            with open(profile_file) as f:
                profile_data = yaml.safe_load(f)
                if not isinstance(profile_data, dict):
                    logger.error(f"Invalid profile format: {profile_file}")
                    return False
            
            with open(metadata_file) as f:
                metadata = yaml.safe_load(f)
                if not isinstance(metadata, dict):
                    logger.error(f"Invalid metadata format: {metadata_file}")
                    return False
            
            return True
        except Exception as e:
            logger.exception(f"Profile validation error: {e}")
            return False


# AC_COMPLETE: AC-ENH087-T5-P2-GREEN-001 ✅ Repository onboarding orchestrator implemented
