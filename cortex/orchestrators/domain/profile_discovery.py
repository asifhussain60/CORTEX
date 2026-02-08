"""
CORTEX Phase-54 S1: Profile Discovery & Analysis

Discovers all repository profiles from cortex_brain/onboarded_repos/
and analyzes their metadata for dashboard generation.

AC_START: AC-PHASE54-S1-001
Description: Profile discovery service infrastructure
Author: CORTEX Implementation
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class RepositoryProfile:
    """Repository profile data model"""
    repo_name: str
    profile_path: Path
    profile_data: Dict[str, Any]
    
    def get_tech_stack(self) -> Dict[str, Any]:
        """Extract tech stack information"""
        return self.profile_data.get("tech_stack", {})
    
    def get_structure(self) -> Dict[str, Any]:
        """Extract structure information"""
        return self.profile_data.get("structure", {})
    
    def get_standards(self) -> Dict[str, Any]:
        """Extract standards information"""
        return self.profile_data.get("standards", {})
    
    def get_security(self) -> Dict[str, Any]:
        """Extract security information"""
        return self.profile_data.get("security", {})


@dataclass
class ProfileMetadata:
    """Extracted metadata from repository profile"""
    repo_name: str
    file_count: int
    primary_language: str
    has_tests: bool
    test_framework: Optional[str]
    test_coverage: Optional[str]
    has_docs: bool
    security_vulnerabilities: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for dashboard generation"""
        return {
            "repo_name": self.repo_name,
            "file_count": self.file_count,
            "primary_language": self.primary_language,
            "has_tests": self.has_tests,
            "test_framework": self.test_framework,
            "test_coverage": self.test_coverage,
            "has_docs": self.has_docs,
            "security_vulnerabilities": self.security_vulnerabilities
        }


class ProfileDiscoveryService:
    """
    Discover and analyze repository profiles.
    
    Provides:
    - Profile discovery from cortex_brain/onboarded_repos/
    - Profile loading and parsing
    - Metadata extraction
    - Validation of profile structure
    """
    
    PROFILE_DIR = Path("cortex_brain/onboarded_repos")
    PROFILE_PATTERN = "*.yaml"
    
    def __init__(self, profile_base_path: Optional[Path] = None):
        """
        Initialize discovery service.
        
        Args:
            profile_base_path: Base path for profile directory (default: cortex_brain/onboarded_repos)
        """
        self.profile_base_path = profile_base_path or self.PROFILE_DIR
        self._discovered_profiles: List[RepositoryProfile] = []
        self._discovery_timestamp = None
    
    def discover_all_profiles(self) -> List[RepositoryProfile]:
        """
        Discover all profiles in the profile directory.
        
        Returns:
            List of RepositoryProfile objects
        """
        self._discovered_profiles = []
        
        if not self.profile_base_path.exists():
            logger.warning(
                f"Profile directory not found: {self.profile_base_path}"
            )
            return []
        
        # Discover all YAML files
        profile_files = list(self.profile_base_path.glob(self.PROFILE_PATTERN))
        logger.info(f"Discovered {len(profile_files)} profile files")
        
        for profile_file in sorted(profile_files):
            try:
                profile = self._load_profile(profile_file)
                if profile:
                    self._discovered_profiles.append(profile)
                    logger.debug(f"Loaded profile: {profile.repo_name}")
            except Exception as e:
                logger.error(f"Error loading profile {profile_file}: {e}")
        
        logger.info(
            f"Successfully loaded {len(self._discovered_profiles)} profiles"
        )
        return self._discovered_profiles
    
    def _load_profile(self, profile_file: Path) -> Optional[RepositoryProfile]:
        """
        Load and parse a single profile file.
        
        Args:
            profile_file: Path to profile YAML file
            
        Returns:
            RepositoryProfile object or None if invalid
        """
        try:
            with open(profile_file, 'r') as f:
                profile_data = yaml.safe_load(f)
            
            if not profile_data:
                logger.warning(f"Profile file is empty: {profile_file}")
                return None
            
            # Extract repo name from filename or data
            repo_name = profile_data.get("repository", {}).get("name")
            if not repo_name:
                repo_name = profile_file.stem
            
            return RepositoryProfile(
                repo_name=repo_name,
                profile_path=profile_file,
                profile_data=profile_data
            )
        
        except yaml.YAMLError as e:
            logger.error(f"YAML parse error in {profile_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading profile {profile_file}: {e}")
            return None
    
    def get_profile_metadata(
        self,
        profile: RepositoryProfile
    ) -> ProfileMetadata:
        """
        Extract and validate metadata from profile.
        
        Args:
            profile: Repository profile
            
        Returns:
            ProfileMetadata object
        """
        repo_data = profile.profile_data.get("repository", {})
        tech_stack = profile.get_tech_stack()
        structure = profile.get_structure()
        security = profile.get_security()
        
        # Extract metadata
        file_count = repo_data.get("file_count", 0)
        primary_language = tech_stack.get("primary_language", "Unknown")
        has_tests = structure.get("has_tests", False)
        test_framework = structure.get("test_framework")
        test_coverage = structure.get("test_coverage")
        has_docs = structure.get("has_docs", False)
        security_vulnerabilities = security.get("vulnerabilities_detected", 0)
        
        return ProfileMetadata(
            repo_name=profile.repo_name,
            file_count=file_count,
            primary_language=primary_language,
            has_tests=has_tests,
            test_framework=test_framework,
            test_coverage=test_coverage,
            has_docs=has_docs,
            security_vulnerabilities=security_vulnerabilities
        )
    
    def get_profiles_by_language(self, language: str) -> List[RepositoryProfile]:
        """
        Get profiles filtered by primary language.
        
        Args:
            language: Programming language to filter by
            
        Returns:
            List of matching profiles
        """
        if not self._discovered_profiles:
            self.discover_all_profiles()
        
        return [
            p for p in self._discovered_profiles
            if p.get_tech_stack().get("primary_language") == language
        ]
    
    def get_profiles_by_size(
        self,
        min_files: int = 0,
        max_files: int = None
    ) -> List[RepositoryProfile]:
        """
        Get profiles filtered by repository size (file count).
        
        Args:
            min_files: Minimum file count
            max_files: Maximum file count (None for unlimited)
            
        Returns:
            List of matching profiles
        """
        if not self._discovered_profiles:
            self.discover_all_profiles()
        
        profiles = []
        for profile in self._discovered_profiles:
            file_count = profile.profile_data.get("repository", {}).get("file_count", 0)
            if file_count >= min_files:
                if max_files is None or file_count <= max_files:
                    profiles.append(profile)
        
        return profiles
    
    def validate_profile_for_dashboard(
        self,
        profile: RepositoryProfile
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if profile has required fields for dashboard generation.
        
        Args:
            profile: Repository profile to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = [
            "repository",
            "tech_stack",
            "structure",
            "standards"
        ]
        
        for field in required_fields:
            if field not in profile.profile_data:
                return False, f"Missing required field: {field}"
        
        # Validate specific nested fields
        repo_data = profile.profile_data.get("repository", {})
        if not repo_data.get("name"):
            return False, "Repository name is required"
        
        return True, None
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """
        Get summary of discovered profiles.
        
        Returns:
            Summary statistics
        """
        if not self._discovered_profiles:
            return {
                "total_profiles": 0,
                "profiles": []
            }
        
        total_files = sum(
            p.profile_data.get("repository", {}).get("file_count", 0)
            for p in self._discovered_profiles
        )
        
        languages = {}
        for profile in self._discovered_profiles:
            lang = profile.get_tech_stack().get("primary_language", "Unknown")
            languages[lang] = languages.get(lang, 0) + 1
        
        return {
            "total_profiles": len(self._discovered_profiles),
            "total_files_across_repos": total_files,
            "languages": languages,
            "profiles": [
                {
                    "repo_name": p.repo_name,
                    "file_count": p.profile_data.get("repository", {}).get("file_count", 0),
                    "primary_language": p.get_tech_stack().get("primary_language", "Unknown")
                }
                for p in self._discovered_profiles
            ]
        }


# AC_COMPLETE: AC-PHASE54-S1-001 ✅
# Profile discovery service complete
# - ProfileDiscoveryService class implemented
# - Profile loading and parsing
# - Metadata extraction
# - Filtering and validation
# Ready for integration into BatchDashboardSeeder
