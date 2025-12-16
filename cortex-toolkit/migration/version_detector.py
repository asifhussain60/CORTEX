"""
CORTEX Version Detection Module

Detects deployment type (setup vs upgrade) and manages version tracking.
Implements version comparison, .cortex-version file management, and upgrade eligibility checks.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
import re


class VersionDetector:
    """Detects CORTEX deployment type and manages version tracking."""
    
    VERSION_FILE = "VERSION"
    LEGACY_VERSION_FILE = ".cortex-version"  # For backward compatibility
    
    def __init__(self, cortex_path: Optional[Path] = None):
        """
        Initialize version detector.
        
        Args:
            cortex_path: Path to CORTEX directory. If None, auto-detects.
        """
        self.cortex_path = cortex_path or self._find_cortex_path()
        self.version_file_path = self.cortex_path / self.VERSION_FILE
        
    def _find_cortex_path(self) -> Path:
        """Auto-detect CORTEX installation path."""
        # Check current directory
        current = Path.cwd()
        if (current / ".github" / "prompts" / "CORTEX.prompt.md").exists():
            return current
            
        # Check parent directories
        for parent in current.parents:
            if (parent / ".github" / "prompts" / "CORTEX.prompt.md").exists():
                return parent
                
        # Check common locations
        common_paths = [
            Path.home() / "PROJECTS" / "CORTEX",
            Path(__file__).resolve().parent.parent.parent,
            Path("C:/PROJECTS/CORTEX"),
        ]
        
        for path in common_paths:
            if path.exists() and (path / ".github" / "prompts" / "CORTEX.prompt.md").exists():
                return path
                
        raise FileNotFoundError(
            "CORTEX installation not found. Please run from CORTEX directory or specify path."
        )
    
    def detect_deployment_type(self) -> str:
        """
        Detect if this is a fresh setup or existing installation.
        
        Returns:
            "setup" if no version file exists (fresh install)
            "upgrade" if version file exists (existing installation)
        """
        if self.version_file_path.exists():
            return "upgrade"
        return "setup"
    
    def get_current_version(self) -> Optional[str]:
        """
        Read current installed version from VERSION file.
        Handles both plain text format (v3.3.0) and legacy JSON format.
        
        Returns:
            Version string (e.g., "v3.3.0") for plain text format,
            or dict for legacy JSON format
        """
        if not self.version_file_path.exists():
            # Try legacy .cortex-version file
            legacy_file = self.cortex_path / self.LEGACY_VERSION_FILE
            if legacy_file.exists():
                try:
                    with open(legacy_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except (IOError, json.JSONDecodeError):
                    pass
            return None
            
        try:
            with open(self.version_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Try JSON format first (legacy)
                if content.startswith('{'):
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        pass
                
                # Plain text format (current)
                return content
        except IOError as e:
            print(f"⚠️  Warning: Could not read version file: {e}")
            return None
    
    def get_latest_version(self) -> str:
        """
        Get latest available CORTEX version from VERSION file.
        Always returns the version string, even if VERSION contains JSON.
        
        Returns:
            Version string (e.g., "v3.3.0") or "unknown"
        """
        version = self.get_current_version()
        
        if not version:
            return "unknown"
        
        # Extract string from dict format
        if isinstance(version, dict):
            return version.get("cortex_version", "unknown")
        
        # Already a string
        return version if isinstance(version, str) else "unknown"
    
    def create_version_file(
        self,
        version: str,
        deployment_type: str = "setup",
        workspace_id: Optional[str] = None,
        customizations: Optional[list] = None
    ) -> None:
        """
        Create .cortex-version file for tracking.
        
        Args:
            version: CORTEX version being installed
            deployment_type: "setup" or "upgrade"
            workspace_id: Optional unique workspace identifier
            customizations: Optional list of user customizations
        """
        version_data = {
            "cortex_version": version,
            "schema_version": self._get_schema_version(),
            "installed_date": datetime.now().isoformat(),
            "last_upgrade": datetime.now().isoformat() if deployment_type == "upgrade" else None,
            "upgrade_history": [],
            "workspace_id": workspace_id or self._generate_workspace_id(),
            "customizations": customizations or [],
            "deployment_type": deployment_type,
            "github_release_url": f"https://github.com/asifhussain60/CORTEX/releases/tag/v{version}"
        }
        
        # If upgrading, preserve history
        if deployment_type == "upgrade":
            existing = self.get_current_version()
            if existing:
                version_data["installed_date"] = existing.get("installed_date")
                version_data["upgrade_history"] = existing.get("upgrade_history", [])
                version_data["upgrade_history"].append({
                    "from_version": existing.get("cortex_version"),
                    "to_version": version,
                    "upgrade_date": datetime.now().isoformat(),
                    "success": True
                })
                version_data["workspace_id"] = existing.get("workspace_id")
                version_data["customizations"] = existing.get("customizations", [])
        
        with open(self.version_file_path, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2)
            
        print(f"✅ Version file created: {self.version_file_path}")
    
    def update_version_file(self, updates: Dict) -> None:
        """
        Update specific fields in version file.
        
        Args:
            updates: Dictionary of fields to update
        """
        current = self.get_current_version()
        if not current:
            raise FileNotFoundError("Version file does not exist")
            
        current.update(updates)
        
        with open(self.version_file_path, 'w', encoding='utf-8') as f:
            json.dump(current, f, indent=2)
    
    def validate_version_file(self) -> Tuple[bool, Optional[str]]:
        """
        Validate .cortex-version file structure and contents.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        version_data = self.get_current_version()
        if not version_data:
            return False, "Version file does not exist"
            
        required_fields = [
            "cortex_version",
            "schema_version",
            "installed_date",
            "workspace_id",
            "deployment_type"
        ]
        
        for field in required_fields:
            if field not in version_data:
                return False, f"Missing required field: {field}"
        
        # Validate version format (semver)
        if not self._is_valid_semver(version_data["cortex_version"]):
            return False, f"Invalid version format: {version_data['cortex_version']}"
            
        return True, None
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two semantic version strings.
        
        Args:
            version1: First version (e.g., "5.2.0")
            version2: Second version (e.g., "5.3.0")
            
        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2
        """
        v1_parts = self._parse_semver(version1)
        v2_parts = self._parse_semver(version2)
        
        for v1, v2 in zip(v1_parts, v2_parts):
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
                
        return 0
    
    def is_upgrade_available(self) -> bool:
        """
        Check if an upgrade is available.
        
        Returns:
            True if newer version available, False otherwise
        """
        current = self.get_current_version()
        if not current:
            return False  # Fresh install, not an upgrade
        
        # Handle both string and dict formats
        if isinstance(current, str):
            current_ver = current
        elif isinstance(current, dict):
            current_ver = current.get("cortex_version")
        else:
            return False
        
        if not current_ver or not isinstance(current_ver, str):
            return False
            
        latest_ver = self.get_latest_version()
        if not latest_ver:
            return False
        
        # Strip 'v' prefix for comparison
        current_clean = current_ver.lstrip('v') if isinstance(current_ver, str) else current_ver
        latest_clean = latest_ver.lstrip('v') if isinstance(latest_ver, str) else latest_ver
        
        return self.compare_versions(current_clean, latest_clean) < 0
    
    def get_upgrade_info(self) -> Dict:
        """
        Get comprehensive upgrade information.
        
        Returns:
            Dictionary with current version, latest version, upgrade status, etc.
        """
        current = self.get_current_version()
        latest = self.get_latest_version()
        deployment_type = self.detect_deployment_type()
        
        # Handle both string and dict formats for current version
        if isinstance(current, str):
            current_version = current
            installed_date = None
            last_upgrade = None
            upgrade_history_count = 0
            workspace_id = None
        elif isinstance(current, dict):
            current_version = current.get("cortex_version")
            installed_date = current.get("installed_date")
            last_upgrade = current.get("last_upgrade")
            upgrade_history_count = len(current.get("upgrade_history", []))
            workspace_id = current.get("workspace_id")
        else:
            current_version = None
            installed_date = None
            last_upgrade = None
            upgrade_history_count = 0
            workspace_id = None
        
        info = {
            "deployment_type": deployment_type,
            "current_version": current_version,
            "latest_version": latest,
            "upgrade_available": False,
            "installed_date": installed_date,
            "last_upgrade": last_upgrade,
            "upgrade_history_count": upgrade_history_count,
            "workspace_id": workspace_id
        }
        
        if deployment_type == "upgrade" and current:
            info["upgrade_available"] = self.is_upgrade_available()
            
        return info
    
    def _get_schema_version(self) -> int:
        """Get current database schema version from PRAGMA user_version."""
        # This will be implemented in Phase 5 (Schema Migrator)
        # For now, return a default value
        return 1
    
    def _generate_workspace_id(self) -> str:
        """Generate unique workspace identifier."""
        import uuid
        return str(uuid.uuid4())
    
    def _is_valid_semver(self, version: str) -> bool:
        """Check if version string is valid semantic version."""
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'
        return bool(re.match(pattern, version))
    
    def _parse_semver(self, version: str) -> Tuple[int, int, int]:
        """
        Parse semantic version string into tuple.
        
        Args:
            version: Version string (e.g., "5.3.0")
            
        Returns:
            Tuple of (major, minor, patch)
        """
        # Remove pre-release and build metadata
        version = version.split('-')[0].split('+')[0]
        parts = version.split('.')
        
        return (
            int(parts[0]) if len(parts) > 0 else 0,
            int(parts[1]) if len(parts) > 1 else 0,
            int(parts[2]) if len(parts) > 2 else 0
        )


def main():
    """CLI entry point for testing version detection."""
    import sys
    
    detector = VersionDetector()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "detect":
            print(f"Deployment Type: {detector.detect_deployment_type()}")
            
        elif command == "current":
            current = detector.get_current_version()
            if current:
                print(json.dumps(current, indent=2))
            else:
                print("No version file found")
                
        elif command == "info":
            info = detector.get_upgrade_info()
            print(json.dumps(info, indent=2))
            
        elif command == "validate":
            is_valid, error = detector.validate_version_file()
            if is_valid:
                print("✅ Version file is valid")
            else:
                print(f"❌ Version file invalid: {error}")
                
        elif command == "create":
            detector.create_version_file(
                version=detector.CURRENT_VERSION,
                deployment_type="setup"
            )
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    else:
        # Default: show upgrade info
        info = detector.get_upgrade_info()
        print("\n🧠 CORTEX Version Information\n")
        print(f"Deployment Type: {info['deployment_type']}")
        print(f"Current Version: {info['current_version'] or 'Not installed'}")
        print(f"Latest Version:  {info['latest_version']}")
        print(f"Upgrade Available: {'✅ Yes' if info['upgrade_available'] else '❌ No'}")
        
        if info['installed_date']:
            print(f"\nInstalled: {info['installed_date']}")
        if info['last_upgrade']:
            print(f"Last Upgrade: {info['last_upgrade']}")
        if info['upgrade_history_count'] > 0:
            print(f"Upgrade History: {info['upgrade_history_count']} upgrades")


if __name__ == "__main__":
    main()
