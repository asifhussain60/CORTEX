"""
CORTEX Release Builder

Creates release tags and validates semantic versioning.

AC_START: AC-CORTEX-ALIGN-003
Description: Release tag builder with version validation
Authority: PHASE-DEPLOYMENT-001
"""

from typing import Dict, Any
import re
import subprocess
from pathlib import Path


class ReleaseBuilder:
    """Build release tags and validate versions."""
    
    SEMVER_PATTERN = re.compile(
        r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
        r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
        r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
        r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )
    
    def __init__(self, repo_path: str = "."):
        """Initialize release builder.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)
    
    def create_release(self, version: str) -> Dict[str, Any]:
        """Create release tag.
        
        Args:
            version: Semantic version (e.g., "1.0.0")
        
        Returns:
            Dictionary with tag and SHA
        """
        if not self.validate_version(version):
            return {
                "error": f"Invalid semantic version: {version}",
                "tag": None,
                "sha": None
            }
        
        return self._create_tag(version)
    
    def validate_version(self, version: str) -> bool:
        """Validate semantic version format.
        
        Args:
            version: Version string to validate
        
        Returns:
            True if valid semantic version
        """
        return bool(self.SEMVER_PATTERN.match(version))
    
    def _create_tag(self, version: str) -> Dict[str, Any]:
        """Create git tag for release.
        
        Args:
            version: Version to tag
        
        Returns:
            Tag creation results
        """
        tag_name = f"v{version}"
        
        try:
            # Get current commit SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=True
            )
            sha = result.stdout.strip()
            
            # Create annotated tag
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Release {version}"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "tag": tag_name,
                "sha": sha,
                "version": version
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "error": f"Git command failed: {e.stderr}",
                "tag": None,
                "sha": None
            }
        except Exception as e:
            return {
                "error": str(e),
                "tag": None,
                "sha": None
            }
