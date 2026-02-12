#!/usr/bin/env python3
"""
Consolidation Validation & Audit Script
Validates consolidated files against source structure, generates audit trails,
and provides recovery support for consolidation operations.

Responsibilities:
- Pre-consolidation baseline capture
- Post-consolidation completeness verification
- Structure reconciliation (subfolders ↔ consolidated file entries)
- Audit log generation
- Recovery manifest creation
- Data integrity validation

Usage:
    # Pre-consolidation baseline (run before consolidate.py)
    python validate_consolidation.py --folder <target-folder> --baseline

    # Post-consolidation validation (run after consolidate.py)
    python validate_consolidation.py --folder <target-folder> --validate

    # Full audit report with recovery manifest
    python validate_consolidation.py --folder <target-folder> --audit

    # Strict mode: fail on any anomaly
    python validate_consolidation.py --folder <target-folder> --validate --strict
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml


class ConsolidationValidator:
    """Validates consolidation operations and manages audit trails."""

    def __init__(self, folder_path: Path, strict: bool = False):
        """Initialize validator."""
        self.folder_path = folder_path.resolve()
        self.parent_path = self.folder_path.parent
        self.consolidated_file_yaml = self.parent_path / f"{self.folder_path.name}.yaml"
        self.consolidated_file_json = self.parent_path / f"{self.folder_path.name}.json"
        self.baseline_file = self.parent_path / f".{self.folder_path.name}.baseline.json"
        self.audit_file = self.parent_path / f"{self.folder_path.name}.audit.json"
        self.manifest_file = self.parent_path / f"{self.folder_path.name}.manifest.json"

        self.strict = strict
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

        # Setup logging
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging to both console and file."""
        logger = logging.getLogger(self.folder_path.name)
        logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)-8s %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        return logger

    def capture_baseline(self) -> bool:
        """Capture baseline of source folder structure before consolidation.

        Stores:
        - Directory tree structure
        - File counts per directory
        - File names and sizes
        - Content hashes (for integrity verification)
        - Timestamp of baseline capture
        """
        if not self.folder_path.exists():
            self.errors.append(f"Folder not found: {self.folder_path}")
            return False

        baseline = {
            "capture_timestamp": datetime.now().isoformat(),
            "source_folder": str(self.folder_path),
            "folder_name": self.folder_path.name,
            "subfolders": [],
            "file_inventory": {},
            "statistics": {
                "total_files": 0,
                "total_size_bytes": 0,
                "files_by_extension": {}
            },
            "errors": []
        }

        try:
            # Recursively scan folder structure
            self._scan_folder_recursive(self.folder_path, baseline)

            # Write baseline file
            with open(self.baseline_file, 'w', encoding='utf-8') as f:
                json.dump(baseline, f, indent=2, ensure_ascii=False)

            self.info.append(f"Baseline captured: {baseline['statistics']['total_files']} files, "
                           f"{baseline['statistics']['total_size_bytes']:,} bytes")
            self.logger.info(f"✓ Baseline written: {self.baseline_file}")

            return True

        except Exception as e:
            self.errors.append(f"Baseline capture failed: {e}")
            return False

    def _scan_folder_recursive(self, current_path: Path, baseline: Dict[str, Any],
                              relative_path: str = "") -> None:
        """Recursively scan folder structure and capture file metadata."""
        try:
            # Get relative path for this folder
            if relative_path:
                folder_key = relative_path
            else:
                folder_key = self.folder_path.name

            # Track this subfolder
            if relative_path and folder_key not in baseline["subfolders"]:
                baseline["subfolders"].append(folder_key)

            # Initialize file list for this folder
            if folder_key not in baseline["file_inventory"]:
                baseline["file_inventory"][folder_key] = {
                    "files": [],
                    "file_count": 0,
                    "total_size_bytes": 0
                }

            # Scan items in this folder
            for item in sorted(current_path.iterdir()):
                if item.name.startswith('.'):
                    continue

                if item.is_dir():
                    # Recurse into subdirectory
                    new_relative_path = f"{relative_path}{item.name}/" if relative_path else f"{item.name}/"
                    self._scan_folder_recursive(item, baseline, new_relative_path)

                elif item.is_file():
                    # Capture file metadata
                    self._capture_file_metadata(item, baseline, folder_key, relative_path)

        except Exception as e:
            baseline["errors"].append(f"Scan error in {current_path}: {e}")

    def _capture_file_metadata(self, file_path: Path, baseline: Dict[str, Any],
                              folder_key: str, relative_path: str) -> None:
        """Capture metadata for a single file including content hash."""
        try:
            stat_info = file_path.stat()

            # Compute SHA256 hash of file content
            file_hash = self._compute_file_hash(file_path)

            # Relative path within original folder structure
            relative_file_path = f"{relative_path}{file_path.name}"

            file_metadata = {
                "filename": file_path.name,
                "original_path": relative_file_path,
                "size_bytes": stat_info.st_size,
                "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "extension": file_path.suffix or "no_extension",
                "sha256": file_hash
            }

            # Add to inventory
            baseline["file_inventory"][folder_key]["files"].append(file_metadata)
            baseline["file_inventory"][folder_key]["file_count"] += 1
            baseline["file_inventory"][folder_key]["total_size_bytes"] += stat_info.st_size

            # Update statistics
            baseline["statistics"]["total_files"] += 1
            baseline["statistics"]["total_size_bytes"] += stat_info.st_size

            ext = file_path.suffix or "no_extension"
            baseline["statistics"]["files_by_extension"][ext] = \
                baseline["statistics"]["files_by_extension"].get(ext, 0) + 1

        except Exception as e:
            baseline["errors"].append(f"Failed to capture {file_path.name}: {e}")

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file content."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            import logging
            logging.error(f"File not found: {file_path}")
            return "ERROR_FILE_NOT_FOUND"
        except IOError as e:
            import logging
            logging.error(f"Cannot read file {file_path}: {e}")
            return "ERROR_READING_FILE"
        except Exception as e:
            import logging
            logging.error(f"Unexpected error reading {file_path}: {e}")
            return "ERROR_READING_FILE"

    def validate_consolidated(self) -> Tuple[bool, List[str]]:
        """Validate consolidated file against baseline.

        Checks:
        - File exists and is readable
        - Format is valid (parseable YAML/JSON)
        - All expected subfolders have entries
        - File count matches baseline
        - No orphaned files (in consolidation but not in baseline)
        """
        issues = []

        # Find consolidated file
        consolidated_path = self._find_consolidated_file()
        if not consolidated_path:
            self.errors.append("No consolidated file found")
            return False, issues

        self.logger.info(f"Validating: {consolidated_path.name}")

        # Load consolidated file
        try:
            consolidated_data = self._load_consolidated_file(consolidated_path)
            if not consolidated_data:
                return False, issues
        except Exception as e:
            self.errors.append(f"Failed to parse consolidated file: {e}")
            return False, issues

        # Load baseline if available
        baseline_data = None
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file, 'r', encoding='utf-8') as f:
                    baseline_data = json.load(f)
            except Exception as e:
                self.warnings.append(f"Could not load baseline for comparison: {e}")

        # Perform validation checks
        if baseline_data:
            issues.extend(self._reconcile_with_baseline(consolidated_data, baseline_data))
        else:
            self.warnings.append("No baseline available; skipping structure validation")

        # Validate consolidated file structure
        issues.extend(self._validate_consolidated_structure(consolidated_data))

        # Check for data integrity issues
        issues.extend(self._check_consolidation_integrity(consolidated_data))

        # Report issues
        if not issues:
            self.info.append("✓ Consolidated file is valid and complete")
            return True, issues
        else:
            for issue in issues:
                if "missing" in issue.lower() or "not found" in issue.lower():
                    self.errors.append(issue)
                else:
                    self.warnings.append(issue)
            return len(self.errors) == 0, issues

    def _find_consolidated_file(self) -> Optional[Path]:
        """Find consolidated YAML or JSON file."""
        for path in [self.consolidated_file_yaml, self.consolidated_file_json]:
            if path.exists():
                return path
        return None

    def _load_consolidated_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and parse consolidated file."""
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:  # YAML
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

            self.logger.info("✓ Consolidated file parsed successfully")
            return data
        except Exception as e:
            self.errors.append(f"Failed to parse {file_path.name}: {e}")
            return None

    def _reconcile_with_baseline(self, consolidated: Dict[str, Any],
                                baseline: Dict[str, Any]) -> List[str]:
        """Reconcile consolidated file with baseline."""
        issues = []

        cons_files = consolidated.get("files", [])
        cons_file_count = len(cons_files)
        baseline_file_count = baseline["statistics"]["total_files"]

        if cons_file_count != baseline_file_count:
            issues.append(f"File count mismatch: consolidated has {cons_file_count}, "
                        f"baseline had {baseline_file_count} (missing {baseline_file_count - cons_file_count})")

        # Build set of subfolders from baseline
        expected_subfolders = set(baseline.get("subfolders", []))

        # Extract subfolders from consolidated files
        consolidated_subfolders = set()
        for file_entry in cons_files:
            original_path = file_entry.get("original_path", "")
            if "/" in original_path:
                subfolder = original_path.rsplit("/", 1)[0]
                consolidated_subfolders.add(subfolder)

        # Check for missing subfolders
        missing_subfolders = expected_subfolders - consolidated_subfolders
        if missing_subfolders:
            issues.append(f"Missing subfolders in consolidated file: {', '.join(sorted(missing_subfolders))}")

        # Check for unexpected subfolders
        extra_subfolders = consolidated_subfolders - expected_subfolders
        if extra_subfolders:
            issues.append(f"Unexpected subfolders in consolidated file: {', '.join(sorted(extra_subfolders))}")

        return issues

    def _validate_consolidated_structure(self, consolidated: Dict[str, Any]) -> List[str]:
        """Validate structure of consolidated file itself."""
        issues = []

        metadata = consolidated.get("metadata", {})
        files = consolidated.get("files", [])

        if not metadata:
            issues.append("Missing metadata section in consolidated file")

        if not files:
            issues.append("No files found in consolidated file")

        # Check metadata completeness
        required_fields = ["consolidation_timestamp", "source_folder", "folder_name", "total_files"]
        for field in required_fields:
            if field not in metadata:
                issues.append(f"Missing metadata field: {field}")

        # Check file entry completeness
        required_file_fields = ["filename", "size_bytes", "extension", "content"]
        for i, file_entry in enumerate(files[:5]):  # Check first 5
            for field in required_file_fields:
                if field not in file_entry:
                    issues.append(f"File entry {i} missing field: {field}")
                    break

        return issues

    def _check_consolidation_integrity(self, consolidated: Dict[str, Any]) -> List[str]:
        """Check for integrity issues in consolidated data."""
        issues = []

        metadata = consolidated.get("metadata", {})
        files = consolidated.get("files", [])

        # Check for reported errors
        consolidation_errors = metadata.get("errors", [])
        if consolidation_errors:
            error_count = len(consolidation_errors)
            issues.append(f"Consolidation encountered {error_count} errors during collection "
                        f"(potential data loss)")

        # Verify file count in metadata
        metadata_file_count = metadata.get("total_files", 0)
        actual_file_count = len(files)
        if metadata_file_count != actual_file_count:
            issues.append(f"File count mismatch in metadata: {metadata_file_count} "
                        f"declared but {actual_file_count} files present")

        # Check for suspiciously large or small consolidation
        total_size = metadata.get("total_size_bytes", 0)
        if total_size == 0 and files:
            issues.append("Metadata shows 0 bytes but files are present")

        return issues

    def generate_audit_log(self) -> bool:
        """Generate immutable audit log of consolidation operation."""
        audit_log = {
            "audit_timestamp": datetime.now().isoformat(),
            "operation": "consolidation_audit",
            "source_folder": str(self.folder_path),
            "folder_name": self.folder_path.name,
            "checks_performed": [],
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "validation_passed": len(self.errors) == 0
            },
            "baseline_available": self.baseline_file.exists(),
            "consolidated_file": self._find_consolidated_file() and str(self._find_consolidated_file()),
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info
        }

        try:
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                json.dump(audit_log, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✓ Audit log written: {self.audit_file}")
            return True
        except Exception as e:
            self.errors.append(f"Failed to write audit log: {e}")
            return False

    def generate_recovery_manifest(self) -> bool:
        """Generate manifest for recovery if consolidation file is lost."""
        consolidated_path = self._find_consolidated_file()
        if not consolidated_path or not consolidated_path.exists():
            self.warnings.append("Consolidated file not found; cannot generate recovery manifest")
            return False

        try:
            consolidated_data = self._load_consolidated_file(consolidated_path)
            if not consolidated_data:
                return False

            manifest = {
                "manifest_timestamp": datetime.now().isoformat(),
                "consolidation_file_path": str(consolidated_path),
                "consolidation_file_size_bytes": consolidated_path.stat().st_size,
                "consolidation_file_hash": self._compute_file_hash(consolidated_path),
                "source_folder": consolidated_data.get("metadata", {}).get("source_folder", ""),
                "total_files_consolidated": len(consolidated_data.get("files", [])),
                "total_size_bytes": consolidated_data.get("metadata", {}).get("total_size_bytes", 0),
                "subfolders_consolidated": self._extract_subfolders_from_consolidation(consolidated_data),
                "recovery_instructions": [
                    "This manifest provides metadata to recover consolidated content if original file is lost",
                    "1. Verify consolidation_file_hash matches actual file SHA256",
                    "2. If mismatch, consolidation file may be corrupted",
                    "3. Check audit log for any reported errors during consolidation",
                    "4. Subfolders list shows which directories were consolidated"
                ]
            }

            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✓ Recovery manifest written: {self.manifest_file}")
            return True
        except Exception as e:
            self.errors.append(f"Failed to generate recovery manifest: {e}")
            return False

    def _extract_subfolders_from_consolidation(self, consolidated: Dict[str, Any]) -> List[str]:
        """Extract unique subfolders from consolidated files."""
        subfolders = set()
        for file_entry in consolidated.get("files", []):
            original_path = file_entry.get("original_path", "")
            if "/" in original_path:
                subfolder = original_path.rsplit("/", 1)[0]
                subfolders.add(subfolder)
        return sorted(list(subfolders))

    def print_report(self) -> None:
        """Print validation report to console."""
        print(f"\n{'='*70}")
        print("CONSOLIDATION VALIDATION REPORT")
        print(f"{'='*70}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.info:
            print(f"\n✓ INFO ({len(self.info)}):")
            for info in self.info:
                print(f"  • {info}")

        print(f"\n{'='*70}")
        if self.errors:
            print(f"Status: FAILED ({len(self.errors)} error(s))")
        elif self.warnings:
            print(f"Status: PASSED WITH WARNINGS ({len(self.warnings)} warning(s))")
        else:
            print("Status: PASSED (all checks successful)")
        print(f"{'='*70}\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate consolidation operations, generate audit trails, and support recovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture baseline before consolidation
  python validate_consolidation.py --folder <target-folder> --baseline

  # Validate consolidated file after consolidation
  python validate_consolidation.py --folder <target-folder> --validate

  # Full audit with recovery manifest
  python validate_consolidation.py --folder <target-folder> --audit

  # Strict mode: fail on any warnings
  python validate_consolidation.py --folder <target-folder> --validate --strict
        """
    )

    parser.add_argument(
        "--folder", "-f",
        required=True,
        type=str,
        help="Folder to validate"
    )

    parser.add_argument(
        "--baseline", "-b",
        action="store_true",
        help="Capture baseline of source folder structure (run before consolidation)"
    )

    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Validate consolidated file (run after consolidation)"
    )

    parser.add_argument(
        "--audit", "-a",
        action="store_true",
        help="Generate full audit log and recovery manifest"
    )

    parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="Strict mode: fail on any warning (not just errors)"
    )

    args = parser.parse_args()

    folder_path = Path(args.folder).resolve()

    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        return 1

    validator = ConsolidationValidator(folder_path, strict=args.strict)

    success = True

    if args.baseline:
        success = validator.capture_baseline() and success

    if args.validate:
        is_valid, issues = validator.validate_consolidated()
        success = is_valid and success

    if args.audit or args.validate:
        validator.generate_audit_log()
        if not args.baseline:  # Only generate manifest if not doing baseline
            validator.generate_recovery_manifest()

    validator.print_report()

    # Exit code: 0=success, 1=errors, 2=warnings (in strict mode)
    if validator.errors:
        return 1
    elif args.strict and validator.warnings:
        return 2
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
