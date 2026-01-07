"""
CORTEX Version Manager

Manages semantic versioning (MAJOR.MINOR.PATCH) for CORTEX deployments.
Automatically increments versions based on deployment type and validates consistency.

Semantic Versioning Rules:
- MAJOR: Breaking changes, API incompatible (user-initiated)
- MINOR: New features, backward compatible (default)
- PATCH: Bug fixes, backward compatible

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Version:
    """Semantic version representation."""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"
    
    def __repr__(self) -> str:
        return f"Version({self.major}, {self.minor}, {self.patch})"
    
    @classmethod
    def parse(cls, version_string: str) -> 'Version':
        """
        Parse version string into Version object.
        
        Args:
            version_string: Version in format "v3.2.0" or "3.2.0"
        
        Returns:
            Version object
        
        Raises:
            ValueError: If version string is invalid
        """
        # Remove 'v' prefix if present
        version_string = version_string.strip().lstrip('v')
        
        # Match MAJOR.MINOR.PATCH pattern
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_string)
        if not match:
            raise ValueError(
                f"Invalid version format: {version_string}. "
                f"Expected format: MAJOR.MINOR.PATCH (e.g., 3.2.0)"
            )
        
        major, minor, patch = map(int, match.groups())
        return cls(major, minor, patch)
    
    def bump_major(self) -> 'Version':
        """Increment MAJOR version, reset MINOR and PATCH to 0."""
        return Version(self.major + 1, 0, 0)
    
    def bump_minor(self) -> 'Version':
        """Increment MINOR version, reset PATCH to 0."""
        return Version(self.major, self.minor + 1, 0)
    
    def bump_patch(self) -> 'Version':
        """Increment PATCH version."""
        return Version(self.major, self.minor, self.patch + 1)
    
    def compare(self, other: 'Version') -> int:
        """
        Compare two versions.
        
        Returns:
            -1 if self < other
            0 if self == other
            1 if self > other
        """
        if self.major != other.major:
            return 1 if self.major > other.major else -1
        if self.minor != other.minor:
            return 1 if self.minor > other.minor else -1
        if self.patch != other.patch:
            return 1 if self.patch > other.patch else -1
        return 0
    
    def __eq__(self, other) -> bool:
        return self.compare(other) == 0
    
    def __lt__(self, other) -> bool:
        return self.compare(other) < 0
    
    def __gt__(self, other) -> bool:
        return self.compare(other) > 0


class VersionManager:
    """Manages CORTEX version across deployments."""
    
    def __init__(self, project_root: Path):
        """
        Initialize version manager.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.version_file = self.project_root / "VERSION"
    
    def get_current_version(self) -> Version:
        """
        Read current version from VERSION file.
        
        Returns:
            Current version
        
        Raises:
            FileNotFoundError: If VERSION file doesn't exist
            ValueError: If version format is invalid
        """
        if not self.version_file.exists():
            raise FileNotFoundError(f"VERSION file not found: {self.version_file}")
        
        content = self.version_file.read_text(encoding='utf-8').strip()
        return Version.parse(content)
    
    def set_version(self, version: Version, reason: str = "Manual version update") -> None:
        """
        Update VERSION file with new version.
        
        Args:
            version: New version to set
            reason: Reason for version change (for logging)
        """
        # Write to VERSION file
        self.version_file.write_text(str(version) + "\n", encoding='utf-8')
        
        # Log version change
        self._log_version_change(version, reason)
        
        print(f"✅ Version updated: {version}")
        print(f"   Reason: {reason}")
    
    def bump_version(
        self,
        bump_type: str = "minor",
        reason: Optional[str] = None
    ) -> Version:
        """
        Bump version based on type.
        
        Args:
            bump_type: "major", "minor", or "patch"
            reason: Optional reason for bump
        
        Returns:
            New version
        
        Raises:
            ValueError: If bump_type is invalid
        """
        current = self.get_current_version()
        
        if bump_type == "major":
            new_version = current.bump_major()
            default_reason = "Major release (breaking changes)"
        elif bump_type == "minor":
            new_version = current.bump_minor()
            default_reason = "Minor release (new features)"
        elif bump_type == "patch":
            new_version = current.bump_patch()
            default_reason = "Patch release (bug fixes)"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}. Must be 'major', 'minor', or 'patch'")
        
        reason = reason or default_reason
        self.set_version(new_version, reason)
        
        return new_version
    
    def validate_version_consistency(self) -> Tuple[bool, list[str]]:
        """
        Validate version consistency across CORTEX files.
        
        Checks:
        - VERSION file exists and is valid
        - CORTEX.prompt.md references correct version
        - No hardcoded version strings in critical files
        
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check 1: VERSION file
        try:
            current = self.get_current_version()
        except (FileNotFoundError, ValueError) as e:
            issues.append(f"VERSION file issue: {e}")
            return False, issues
        
        # Check 2: CORTEX.prompt.md version reference
        prompt_file = self.project_root / ".github/prompts/CORTEX.prompt.md"
        if prompt_file.exists():
            content = prompt_file.read_text(encoding='utf-8')
            
            # Look for version references
            version_pattern = r'v?\d+\.\d+\.\d+'
            matches = re.findall(version_pattern, content)
            
            for match in matches:
                found_version = Version.parse(match)
                if found_version != current:
                    issues.append(
                        f"Version mismatch in CORTEX.prompt.md: "
                        f"found {found_version}, expected {current}"
                    )
        
        # Check 3: Package metadata files
        package_files = [
            "cortex-operations.yaml",
            "README.md"
        ]
        
        for file_name in package_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                
                # Look for version references
                matches = re.findall(r'v?\d+\.\d+\.\d+', content)
                for match in matches:
                    try:
                        found_version = Version.parse(match)
                        if found_version != current:
                            issues.append(
                                f"Version mismatch in {file_name}: "
                                f"found {found_version}, expected {current}"
                            )
                    except ValueError:
                        # Skip invalid version strings
                        continue
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def _log_version_change(self, version: Version, reason: str) -> None:
        """Log version change to version history file."""
        history_file = self.project_root / "cortex-brain/documents/reports/VERSION-HISTORY.md"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create or append to history
        if not history_file.exists():
            history_file.write_text(
                "# CORTEX Version History\n\n"
                "Automated version tracking for CORTEX releases.\n\n"
                "---\n\n",
                encoding='utf-8'
            )
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"## {version} - {timestamp}\n**Reason:** {reason}\n\n"
        
        # Append to history
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(entry)
    
    def get_version_info(self) -> dict:
        """
        Get comprehensive version information.
        
        Returns:
            Dictionary with version details
        """
        current = self.get_current_version()
        is_valid, issues = self.validate_version_consistency()
        
        return {
            "current_version": str(current),
            "major": current.major,
            "minor": current.minor,
            "patch": current.patch,
            "is_valid": is_valid,
            "validation_issues": issues,
            "version_file": str(self.version_file)
        }


def main():
    """CLI interface for version management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Version Manager")
    parser.add_argument(
        "action",
        choices=["show", "bump", "set", "validate"],
        help="Action to perform"
    )
    parser.add_argument(
        "--type",
        choices=["major", "minor", "patch"],
        default="minor",
        help="Version bump type (for bump action)"
    )
    parser.add_argument(
        "--version",
        help="Version to set (for set action, e.g., '3.2.1')"
    )
    parser.add_argument(
        "--reason",
        help="Reason for version change"
    )
    
    args = parser.parse_args()
    
    # Find project root
    project_root = Path(__file__).parent.parent
    manager = VersionManager(project_root)
    
    if args.action == "show":
        info = manager.get_version_info()
        print(f"Current Version: {info['current_version']}")
        print(f"  Major: {info['major']}")
        print(f"  Minor: {info['minor']}")
        print(f"  Patch: {info['patch']}")
        print(f"  Valid: {'✅ Yes' if info['is_valid'] else '❌ No'}")
        if info['validation_issues']:
            print("\nValidation Issues:")
            for issue in info['validation_issues']:
                print(f"  - {issue}")
    
    elif args.action == "bump":
        current = manager.get_current_version()
        print(f"Current version: {current}")
        new_version = manager.bump_version(args.type, args.reason)
        print(f"New version: {new_version}")
    
    elif args.action == "set":
        if not args.version:
            print("❌ Error: --version required for 'set' action")
            return
        
        new_version = Version.parse(args.version)
        manager.set_version(new_version, args.reason or "Manual version update")
    
    elif args.action == "validate":
        is_valid, issues = manager.validate_version_consistency()
        if is_valid:
            print("✅ Version consistency validated")
        else:
            print("❌ Version validation failed:")
            for issue in issues:
                print(f"  - {issue}")


if __name__ == "__main__":
    main()
