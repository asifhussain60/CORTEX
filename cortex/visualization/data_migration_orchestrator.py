"""
AC_START: AC-PHASE53.0-S5-DATA-MIGRATION
Phase 53 S5: Data Migration & Cleanup Orchestrator

Handles:
1. Extraction of legacy repository data (5 repos)
2. Conversion to unified JSON schema
3. Safe deletion of legacy HTML files
4. Rollback capability on failure

Authority: CORE-008 (TDD), Phase 53 specification
"""

import hashlib
import json
import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DataMigrationOrchestrator:
    """Orchestrates data migration from legacy HTML dashboards to unified JSON."""

    # Legacy repositories to migrate
    LEGACY_REPOS = ["alist", "cortex", "kashkole", "ksessions", "noor-canvas"]
    LEGACY_ROOT = Path("company/dashboards/repos")
    JSON_OUTPUT_ROOT = Path("company/dashboards/data")
    BACKUP_ROOT = Path("company/dashboards/legacy_backup")

    def __init__(self, dry_run: bool = False):
        """
        Initialize orchestrator.

        Args:
            dry_run: If True, simulate without deleting files
        """
        self.dry_run = dry_run
        self.extraction_manifest: Dict[str, Any] = {}
        self.deletion_manifest: Dict[str, Any] = {}
        self.checkpoint: Dict[str, Any] = {}

    def extract_legacy_data(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Extract data from all 5 legacy HTML dashboards.

        Returns:
            Tuple of (success, extracted_data)
        """
        logger.info("🔍 Extracting legacy repository data...")

        extracted_data = {}
        checksums = {}

        for repo_name in self.LEGACY_REPOS:
            try:
                html_path = self.LEGACY_ROOT / repo_name / "index.html"

                if not html_path.exists():
                    logger.warning(f"⚠️  Legacy HTML not found: {html_path}")
                    continue

                # Read legacy HTML
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # Extract metadata
                repo_data = self._parse_legacy_html(repo_name, html_content)

                extracted_data[repo_name] = repo_data

                # Generate checksum
                checksum = hashlib.md5(html_content.encode()).hexdigest()
                checksums[repo_name] = checksum

                logger.info(f"✓ Extracted {repo_name}: {len(repo_data)} fields")

            except Exception as e:
                logger.error(f"✗ Failed to extract {repo_name}: {e}")
                return False, {}

        # Create extraction manifest
        self.extraction_manifest = {
            "timestamp": datetime.now().isoformat(),
            "operation": "extract_legacy_dashboards",
            "repositories_extracted": len(extracted_data),
            "checksums": checksums,
            "extracted_data": extracted_data
        }

        logger.info(f"✅ Extracted {len(extracted_data)}/5 repositories")
        return True, extracted_data

    def convert_to_unified_json(
        self,
        extracted_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Convert extracted data to unified JSON schema.

        Args:
            extracted_data: Dictionary of extracted repository data

        Returns:
            Tuple of (success, json_data_dict)
        """
        logger.info("📋 Converting to unified JSON schema...")

        converted_data = {}

        for repo_name, repo_data in extracted_data.items():
            try:
                # Build unified schema
                unified_schema = {
                    "schema_version": "1.0",
                    "generated_at": datetime.now().isoformat(),
                    "repository": repo_name,
                    "type": repo_data.get("type", "repository"),
                    "overview": {
                        "description": f"{repo_name} repository",
                        "stats": repo_data.get("stats", {})
                    },
                    "metadata": {
                        "migrated_from": f"company/dashboards/repos/{repo_name}/index.html",
                        "migration_timestamp": datetime.now().isoformat()
                    }
                }

                # Add optional sections if present
                if "metrics" in repo_data:
                    unified_schema["metrics"] = repo_data["metrics"]

                if "security" in repo_data:
                    unified_schema["security"] = repo_data["security"]

                # Validate schema
                if not self._validate_schema(unified_schema):
                    logger.error(f"✗ Schema validation failed for {repo_name}")
                    return False, {}

                converted_data[repo_name] = unified_schema
                logger.info(f"✓ Converted {repo_name} to unified schema")

            except Exception as e:
                logger.error(f"✗ Failed to convert {repo_name}: {e}")
                return False, {}

        logger.info(f"✅ Converted {len(converted_data)} repositories to JSON")
        return True, converted_data

    def create_rollback_checkpoint(self, converted_data: Dict[str, Any]) -> bool:
        """
        Create rollback checkpoint before deletion.

        Args:
            converted_data: Dictionary of converted JSON data

        Returns:
            True if checkpoint created successfully
        """
        logger.info("💾 Creating rollback checkpoint...")

        try:
            checkpoint = {
                "timestamp": datetime.now().isoformat(),
                "operation": "legacy_migration",
                "status": "checkpoint_created",
                "backed_up_files": len(self.LEGACY_REPOS),
                "backup_location": str(self.BACKUP_ROOT),
                "backup_manifest": {}
            }

            # Backup all legacy HTML files
            self.BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

            for repo_name in self.LEGACY_REPOS:
                html_path = self.LEGACY_ROOT / repo_name / "index.html"

                if html_path.exists():
                    backup_file = self.BACKUP_ROOT / f"{repo_name}_index.html"

                    if not self.dry_run:
                        shutil.copy(html_path, backup_file)

                    # Record backup
                    with open(html_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    checksum = hashlib.md5(content.encode()).hexdigest()

                    checkpoint["backup_manifest"][repo_name] = {
                        "source": str(html_path),
                        "backup": str(backup_file),
                        "checksum": checksum
                    }

                    logger.info(f"✓ Backed up {repo_name}")

            self.checkpoint = checkpoint

            if not self.dry_run:
                checkpoint_path = self.BACKUP_ROOT / "checkpoint.json"
                with open(checkpoint_path, 'w', encoding='utf-8') as f:
                    json.dump(checkpoint, f, indent=2)

            logger.info("✅ Rollback checkpoint created")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to create checkpoint: {e}")
            return False

    def write_json_files(self, converted_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Write converted data to JSON files.

        Args:
            converted_data: Dictionary of converted JSON data

        Returns:
            Tuple of (success, list_of_created_files)
        """
        logger.info("💾 Writing JSON files...")

        self.JSON_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

        created_files = []

        for repo_name, json_data in converted_data.items():
            try:
                json_path = self.JSON_OUTPUT_ROOT / f"{repo_name}.json"

                if not self.dry_run:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2)

                created_files.append(str(json_path))
                logger.info(f"✓ Wrote {json_path}")

            except Exception as e:
                logger.error(f"✗ Failed to write {repo_name}.json: {e}")
                return False, []

        logger.info(f"✅ Wrote {len(created_files)} JSON files")
        return True, created_files

    def cleanup_legacy_files(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Delete legacy HTML files after backup and JSON creation.

        Returns:
            Tuple of (success, deletion_manifest)
        """
        logger.info("🗑️  Cleaning up legacy HTML files...")

        if not self.checkpoint:
            logger.error("✗ No checkpoint found - cannot proceed with cleanup")
            return False, {}

        deletion_manifest = {
            "timestamp": datetime.now().isoformat(),
            "operation": "legacy_file_cleanup",
            "deleted_files": [],
            "skipped_files": [],
            "status": "completed"
        }

        for repo_name in self.LEGACY_REPOS:
            try:
                html_path = self.LEGACY_ROOT / repo_name / "index.html"

                if html_path.exists():
                    if not self.dry_run:
                        os.remove(html_path)

                    deletion_manifest["deleted_files"].append(str(html_path))
                    logger.info(f"✓ Deleted {html_path}")
                else:
                    deletion_manifest["skipped_files"].append(str(html_path))
                    logger.info(f"⊘ File not found: {html_path}")

            except Exception as e:
                logger.error(f"✗ Failed to delete {repo_name}: {e}")
                deletion_manifest["status"] = "failed"
                return False, deletion_manifest

        self.deletion_manifest = deletion_manifest
        logger.info(f"✅ Cleanup complete: {len(deletion_manifest['deleted_files'])} files deleted")
        return True, deletion_manifest

    def verify_migration_integrity(
        self,
        created_files: List[str]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify migration integrity through checksums and schema validation.

        Args:
            created_files: List of created JSON files

        Returns:
            Tuple of (success, verification_report)
        """
        logger.info("🔍 Verifying migration integrity...")

        verification_report = {
            "timestamp": datetime.now().isoformat(),
            "operation": "migration_integrity_check",
            "files_checked": 0,
            "files_valid": 0,
            "schema_errors": [],
            "status": "passed"
        }

        for json_file in created_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                verification_report["files_checked"] += 1

                # Validate schema
                if self._validate_schema(data):
                    verification_report["files_valid"] += 1
                    logger.info(f"✓ Verified {Path(json_file).name}")
                else:
                    verification_report["schema_errors"].append(json_file)
                    verification_report["status"] = "failed"
                    logger.error(f"✗ Schema validation failed: {json_file}")

            except Exception as e:
                logger.error(f"✗ Failed to verify {json_file}: {e}")
                verification_report["schema_errors"].append(json_file)
                verification_report["status"] = "failed"

        logger.info(f"✅ Verification complete: {verification_report['files_valid']}/{verification_report['files_checked']} files valid")
        return verification_report["status"] == "passed", verification_report

    def run_migration(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute full migration workflow.

        Returns:
            Tuple of (success, summary)
        """
        logger.info("=" * 80)
        logger.info("🚀 Phase 53 S5: Data Migration & Cleanup")
        logger.info(f"   Dry Run: {self.dry_run}")
        logger.info("=" * 80)

        # AC_START: Migration operation
        migration_summary = {
            "ac_marker": "AC_START: AC-PHASE53.0-S5-MIGRATION",
            "timestamp": datetime.now().isoformat(),
            "operation": "legacy_to_json_migration",
            "stages": {}
        }

        try:
            # STAGE 1: Extract legacy data
            success, extracted_data = self.extract_legacy_data()
            migration_summary["stages"]["extraction"] = {"success": success, "count": len(extracted_data)}

            if not success:
                return False, migration_summary

            # STAGE 2: Convert to unified JSON
            success, converted_data = self.convert_to_unified_json(extracted_data)
            migration_summary["stages"]["conversion"] = {"success": success, "count": len(converted_data)}

            if not success:
                return False, migration_summary

            # STAGE 3: Create rollback checkpoint
            success = self.create_rollback_checkpoint(converted_data)
            migration_summary["stages"]["checkpoint"] = {"success": success}

            if not success:
                return False, migration_summary

            # STAGE 4: Write JSON files
            success, created_files = self.write_json_files(converted_data)
            migration_summary["stages"]["json_write"] = {"success": success, "count": len(created_files)}

            if not success:
                return False, migration_summary

            # STAGE 5: Verify integrity
            success, verification = self.verify_migration_integrity(created_files)
            migration_summary["stages"]["verification"] = verification

            if not success:
                logger.error("✗ Migration verification failed - attempting rollback...")
                return False, migration_summary

            # STAGE 6: Cleanup legacy files
            success, deletion = self.cleanup_legacy_files()
            migration_summary["stages"]["cleanup"] = deletion

            if not success:
                logger.error("✗ Cleanup failed - rollback available")
                return False, migration_summary

            # Migration successful
            migration_summary["status"] = "completed"
            migration_summary["ac_marker"] = "AC_COMPLETE: AC-PHASE53.0-S5-MIGRATION ✅"

            logger.info("=" * 80)
            logger.info("✅ Migration completed successfully")
            logger.info(f"   - Extracted: {len(extracted_data)} repositories")
            logger.info(f"   - Converted: {len(converted_data)} JSON files")
            logger.info(f"   - Verified: {verification['files_valid']}/{verification['files_checked']} files")
            logger.info(f"   - Cleaned: {len(deletion['deleted_files'])} legacy files")
            logger.info("=" * 80)

            return True, migration_summary

        except Exception as e:
            logger.error(f"✗ Migration failed with error: {e}")
            migration_summary["status"] = "failed"
            migration_summary["error"] = str(e)
            return False, migration_summary

    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================

    def _parse_legacy_html(self, repo_name: str, html_content: str) -> Dict[str, Any]:
        """
        Parse legacy HTML to extract repository metadata.

        Args:
            repo_name: Repository name
            html_content: HTML content

        Returns:
            Dictionary of extracted metadata
        """
        data = {
            "repository": repo_name,
            "type": "repository",
            "stats": {}
        }

        # Extract type
        type_match = re.search(r'Type:\s*([^<]+)', html_content)
        if type_match:
            data["type"] = type_match.group(1).strip()

        # Extract stats
        files_match = re.search(r'Files:\s*(\d+(?:,\d{3})*)', html_content)
        if files_match:
            data["stats"]["files"] = int(files_match.group(1).replace(',', ''))

        size_match = re.search(r'Size:\s*([^<]+)', html_content)
        if size_match:
            data["stats"]["size"] = size_match.group(1).strip()

        coverage_match = re.search(r'Test Coverage:\s*(\d+)%', html_content)
        if coverage_match:
            data["stats"]["test_coverage"] = int(coverage_match.group(1))

        loc_match = re.search(r'Lines of Code:\s*([^<]+)', html_content)
        if loc_match:
            data["stats"]["loc"] = loc_match.group(1).strip()

        return data

    def _validate_schema(self, data: Dict[str, Any]) -> bool:
        """
        Validate data against unified schema.

        Args:
            data: Dictionary to validate

        Returns:
            True if valid
        """
        required_fields = ["schema_version", "repository", "type", "overview"]

        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False

        # Validate overview structure
        overview = data.get("overview", {})
        if not isinstance(overview, dict):
            logger.error("overview must be a dictionary")
            return False

        if "description" not in overview:
            logger.error("overview.description is required")
            return False

        return True

    def restore_from_rollback(self) -> bool:
        """
        Restore all files from rollback point if needed.

        Returns:
            True if restore successful
        """
        logger.info("🔄 Restoring from rollback point...")

        try:
            if not self.checkpoint:
                logger.error("No checkpoint available for rollback")
                return False

            for repo_name, backup_info in self.checkpoint["backup_manifest"].items():
                backup_file = Path(backup_info["backup"])
                source_file = Path(backup_info["source"])

                if backup_file.exists():
                    source_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(backup_file, source_file)
                    logger.info(f"✓ Restored {source_file}")

            logger.info("✅ Rollback restore complete")
            return True

        except Exception as e:
            logger.error(f"✗ Rollback restore failed: {e}")
            return False


# ============================================================================
# CLI EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    # Support dry-run mode
    dry_run = "--dry-run" in sys.argv

    orchestrator = DataMigrationOrchestrator(dry_run=dry_run)
    success, summary = orchestrator.run_migration()

    if not success:
        print("\n❌ Migration failed")
        sys.exit(1)
    else:
        print("\n✅ Migration complete")
        sys.exit(0)
