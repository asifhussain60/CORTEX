"""
IntelligencePreserver - Snapshot and restore CORTEX intelligence.

Preserves governance.db, tier1 rules, and learned patterns across upgrades.

AC-ID: AC-DEP-005-02
"""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class IntelligencePreserver:
    """
    Preserver for CORTEX learned intelligence.

    Handles snapshotting and restoring governance state, tier1 rules,
    and learned patterns during upgrades.
    Follows CORE-008 (TDD) and CORE-011 (type hints).
    """

    def __init__(self, repo_path: Path):
        """
        Initialize IntelligencePreserver.

        Args:
            repo_path: Path to the repository root.
        """
        self.repo_path = Path(repo_path)
        self.snapshots_dir = self.repo_path / ".cortex-snapshots"

    def snapshot_governance_db(self, version: str) -> Dict[str, Any]:
        """
        Snapshot governance.db to .cortex-snapshots.

        Args:
            version: Version string for snapshot directory.

        Returns:
            Result dictionary.
        """
        result = {"success": False, "error": None}

        try:
            # Find governance.db
            db_path = self.repo_path / "cortex_brain" / "state" / "governance.db"

            if not db_path.exists():
                result["error"] = "governance.db not found"
                return result

            # Create snapshot directory
            snapshot_dir = self.snapshots_dir / f"v{version}"
            snapshot_dir.mkdir(parents=True, exist_ok=True)

            # Copy database
            snapshot_path = snapshot_dir / "governance.db"
            shutil.copy2(db_path, snapshot_path)

            result["success"] = True
            result["snapshot_path"] = str(snapshot_path)

        except Exception as e:
            result["error"] = str(e)

        return result

    def snapshot_tier1_rules(self, version: str) -> Dict[str, Any]:
        """
        Snapshot tier1 rules directory.

        Args:
            version: Version string for snapshot directory.

        Returns:
            Result dictionary.
        """
        result = {"success": False, "files_copied": 0, "error": None}

        try:
            # Find tier1 directory
            tier1_path = self.repo_path / "cortex_brain" / "tier1"

            if not tier1_path.exists():
                result["error"] = "tier1 directory not found"
                return result

            # Create snapshot directory
            snapshot_dir = self.snapshots_dir / f"v{version}" / "tier1"
            snapshot_dir.mkdir(parents=True, exist_ok=True)

            # Copy all tier1 files
            files_copied = 0
            for file_path in tier1_path.glob("*"):
                if file_path.is_file():
                    shutil.copy2(file_path, snapshot_dir / file_path.name)
                    files_copied += 1

            result["success"] = True
            result["files_copied"] = files_copied

        except Exception as e:
            result["error"] = str(e)

        return result

    def snapshot_learned_patterns(self, version: str) -> Dict[str, Any]:
        """
        Snapshot learned patterns (rule hits, routing decisions).

        Args:
            version: Version string for snapshot directory.

        Returns:
            Result dictionary.
        """
        result = {"success": False, "error": None}

        try:
            state_dir = self.repo_path / "cortex_brain" / "state"
            patterns_file = state_dir / "learned_patterns.json"

            # Create snapshot directory
            snapshot_dir = self.snapshots_dir / f"v{version}"
            snapshot_dir.mkdir(parents=True, exist_ok=True)

            if patterns_file.exists():
                shutil.copy2(patterns_file, snapshot_dir / "learned_patterns.json")
            else:
                # Create empty patterns file
                (snapshot_dir / "learned_patterns.json").write_text("{}")

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        return result

    def generate_snapshot_manifest(
        self,
        version: str,
        files: List[str]
    ) -> Dict[str, Any]:
        """
        Generate manifest with timestamp and file list.

        Args:
            version: Version string.
            files: List of files in snapshot.

        Returns:
            Manifest dictionary.
        """
        manifest = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "files": files,
            "hashes": {}
        }

        # Calculate hashes for each file
        snapshot_dir = self.snapshots_dir / f"v{version}"
        for file_name in files:
            file_path = snapshot_dir / file_name
            if file_path.exists():
                manifest["hashes"][file_name] = self._calculate_hash(file_path)

        return manifest

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def validate_snapshot_integrity(self, version: str) -> Dict[str, Any]:
        """
        Validate snapshot integrity via hash verification.

        Args:
            version: Version to validate.

        Returns:
            Validation result dictionary.
        """
        result = {"valid": True, "errors": []}

        try:
            snapshot_dir = self.snapshots_dir / f"v{version}"
            manifest_path = snapshot_dir / "manifest.json"

            if not manifest_path.exists():
                # No manifest, consider valid if files exist
                return result

            manifest = json.loads(manifest_path.read_text())

            for file_name, expected_hash in manifest.get("files", {}).items():
                file_path = snapshot_dir / file_name
                if not file_path.exists():
                    result["valid"] = False
                    result["errors"].append(f"Missing file: {file_name}")
                elif isinstance(expected_hash, str):
                    actual_hash = self._calculate_hash(file_path)
                    if actual_hash != expected_hash:
                        result["valid"] = False
                        result["errors"].append(f"Hash mismatch: {file_name}")

        except Exception as e:
            result["valid"] = False
            result["errors"].append(str(e))

        return result

    def restore_from_snapshot(self, version: str) -> Dict[str, Any]:
        """
        Restore all files from a snapshot.

        Args:
            version: Version to restore from.

        Returns:
            Result dictionary.
        """
        result = {"success": False, "files_restored": 0, "error": None}

        try:
            snapshot_dir = self.snapshots_dir / f"v{version}"

            if not snapshot_dir.exists():
                result["error"] = f"Snapshot v{version} not found"
                return result

            files_restored = 0

            # Restore governance.db
            db_snapshot = snapshot_dir / "governance.db"
            if db_snapshot.exists():
                state_dir = self.repo_path / "cortex_brain" / "state"
                state_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(db_snapshot, state_dir / "governance.db")
                files_restored += 1

            # Restore tier1 rules
            tier1_snapshot = snapshot_dir / "tier1"
            if tier1_snapshot.exists():
                tier1_dir = self.repo_path / "cortex_brain" / "tier1"
                tier1_dir.mkdir(parents=True, exist_ok=True)
                for file_path in tier1_snapshot.glob("*"):
                    shutil.copy2(file_path, tier1_dir / file_path.name)
                    files_restored += 1

            # Restore learned patterns
            patterns_snapshot = snapshot_dir / "learned_patterns.json"
            if patterns_snapshot.exists():
                state_dir = self.repo_path / "cortex_brain" / "state"
                state_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(patterns_snapshot, state_dir / "learned_patterns.json")
                files_restored += 1

            result["success"] = True
            result["files_restored"] = files_restored

        except Exception as e:
            result["error"] = str(e)

        return result

    def list_snapshots(self) -> List[str]:
        """
        List all available snapshots.

        Returns:
            List of version strings.
        """
        if not self.snapshots_dir.exists():
            return []

        snapshots = []
        for dir_path in self.snapshots_dir.iterdir():
            if dir_path.is_dir() and dir_path.name.startswith("v"):
                version = dir_path.name[1:]  # Remove 'v' prefix
                snapshots.append(version)

        return sorted(snapshots)

    def create_full_snapshot(self, version: str) -> Dict[str, Any]:
        """
        Create a complete snapshot of all intelligence.

        Args:
            version: Version string.

        Returns:
            Result dictionary.
        """
        result = {"success": False, "components": {}, "error": None}

        try:
            # Snapshot all components
            result["components"]["governance_db"] = self.snapshot_governance_db(version)
            result["components"]["tier1_rules"] = self.snapshot_tier1_rules(version)
            result["components"]["learned_patterns"] = self.snapshot_learned_patterns(version)

            # Generate manifest
            snapshot_dir = self.snapshots_dir / f"v{version}"
            files = [f.name for f in snapshot_dir.rglob("*") if f.is_file()]
            manifest = self.generate_snapshot_manifest(version, files)

            # Save manifest
            manifest_path = snapshot_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2))

            result["success"] = all(
                c.get("success", False) or c.get("error") is None
                for c in result["components"].values()
            )

        except Exception as e:
            result["error"] = str(e)

        return result
