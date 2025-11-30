#!/usr/bin/env python3
"""
Publish Manifest Validator

Validates that only production files/folders are included in deployment manifest.
Blocks non-production content from being published to users.

Validation Categories:
    1. Temporary Folders - .temp-publish, test_merge, .venv, etc.
    2. Development Artifacts - __pycache__, .pytest_cache, coverage reports
    3. Test Fixtures - tests/, workflow_checkpoints/, examples/
    4. Admin Tools - scripts/admin/, cortex-brain/admin/
    5. Documentation Source - docs/ (MkDocs source, not needed by users)

Usage:
    # Validate before publish
    python scripts/validation/publish_manifest_validator.py
    
    # In deployment scripts (automatic)
    from scripts.validation.publish_manifest_validator import PublishManifestValidator
    validator = PublishManifestValidator(repo_root, manifest)
    success, report = validator.validate()

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PublishManifestValidator:
    """
    Validates deployment manifest to prevent non-production content from being published.
    
    Blocked Content:
        - Temporary folders (.temp-publish, test_merge, .venv)
        - Development artifacts (__pycache__, .pytest_cache, .coverage)
        - Test fixtures (tests/, workflow_checkpoints/, examples/)
        - Admin tools (scripts/admin/, cortex-brain/admin/)
        - Documentation source (docs/, site/)
        - Debug logs (logs/, *.log)
        - Build artifacts (dist/, build/)
    """
    
    # Folders that MUST NOT be included in deployment
    BLOCKED_FOLDERS = {
        # Temporary/Build Artifacts
        '.temp-publish',
        'test_merge',
        '.venv',
        'venv',
        '__pycache__',
        '.pytest_cache',
        'dist',
        'build',
        'publish',  # Don't recursively include publish folder
        
        # Development/Testing
        'tests',
        'workflow_checkpoints',
        'examples',
        'logs',
        '.coverage',
        'htmlcov',
        '.tox',
        
        # Documentation Source (users don't need MkDocs source)
        'docs',
        'site',
        
        # Version Control
        '.git',
        '.github/workflows',  # CI/CD not needed by users
        '.github/hooks',
        
        # Extensions/Demos
        'cortex-extension',
        '.backup-archive',
        
        # Admin-Only (SECURITY: Users must not modify CORTEX)
        'cortex-brain/admin',
        'src/operations/modules/admin',
        'scripts/admin',
        'tests/admin',
        'tests/operations/admin',
        'tests/operations/modules/admin',
        
        # Demo/Mock Data (PRODUCTION SAFETY)
        'cortex-brain/documents/analysis/INTELLIGENT-UX-DEMO',
    }
    
    # File patterns that MUST NOT be included
    BLOCKED_PATTERNS = {
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '*.log',
        '*.db-journal',
        '*.db-shm',
        '*.db-wal',
        '.DS_Store',
        'Thumbs.db',
        '.coverage',
        '*.egg-info',
        '*.orig',
        '*.swp',
        '*~',
    }
    
    # Admin-only files (SECURITY)
    BLOCKED_ADMIN_FILES = {
        'scripts/deploy_cortex.py',
        'scripts/deploy_cortex_OLD.py',
        'scripts/deploy_cortex_simple.py',
        'scripts/validate_deployment.py',
        'scripts/publish_to_branch.py',
    }
    
    def __init__(self, repo_root: Path, manifest: List[Path] = None):
        """
        Initialize validator.
        
        Args:
            repo_root: Path to CORTEX repository root
            manifest: List of paths to validate (if None, scans repo_root)
        """
        self.repo_root = Path(repo_root)
        self.manifest = manifest or self._scan_repository()
        self.violations: List[Dict] = []
        self.warnings: List[str] = []
        
    def _scan_repository(self) -> List[Path]:
        """
        Scan repository to build manifest.
        
        Returns:
            List of all files/folders in repository
        """
        manifest = []
        
        for item in self.repo_root.rglob('*'):
            if item.is_file() or item.is_dir():
                manifest.append(item.relative_to(self.repo_root))
        
        return manifest
    
    def validate(self) -> Tuple[bool, Dict]:
        """
        Run all validation checks.
        
        Returns:
            (success, report) where success is True if no violations found
            and report contains detailed validation results
        """
        logger.info("🔍 Validating publish manifest...")
        
        # Run checks
        self._check_blocked_folders()
        self._check_blocked_patterns()
        self._check_blocked_admin_files()
        self._check_database_files()
        
        # Generate report
        success = len(self.violations) == 0
        
        report = {
            'success': success,
            'violations': self.violations,
            'warnings': self.warnings,
            'stats': {
                'total_items': len(self.manifest),
                'violations': len(self.violations),
                'warnings': len(self.warnings),
                'blocked_folders': len([v for v in self.violations if v['type'] == 'blocked_folder']),
                'blocked_patterns': len([v for v in self.violations if v['type'] == 'blocked_pattern']),
                'blocked_admin': len([v for v in self.violations if v['type'] == 'blocked_admin']),
            }
        }
        
        # Print summary
        if success:
            logger.info("✅ Publish manifest validation PASSED")
            if self.warnings:
                logger.warning(f"⚠️  {len(self.warnings)} warning(s) found")
        else:
            logger.error(
                f"❌ Publish manifest validation FAILED - "
                f"{len(self.violations)} violation(s) found"
            )
        
        return success, report
    
    def _check_blocked_folders(self) -> None:
        """
        Check for blocked folders in manifest.
        
        Violations are added for each blocked folder found.
        """
        for item in self.manifest:
            # Check if any part of the path matches blocked folders
            parts = item.parts
            
            for blocked in self.BLOCKED_FOLDERS:
                blocked_parts = Path(blocked).parts
                
                # Check if blocked path is in item path
                if len(parts) >= len(blocked_parts):
                    if parts[:len(blocked_parts)] == blocked_parts:
                        self.violations.append({
                            'type': 'blocked_folder',
                            'path': str(item),
                            'reason': f"Blocked folder: {blocked}",
                            'severity': 'critical'
                        })
                        break
    
    def _check_blocked_patterns(self) -> None:
        """
        Check for blocked file patterns in manifest.
        
        Violations are added for each file matching blocked patterns.
        """
        import fnmatch
        
        for item in self.manifest:
            if not item.is_file():
                continue
            
            filename = item.name
            
            for pattern in self.BLOCKED_PATTERNS:
                if fnmatch.fnmatch(filename, pattern):
                    self.violations.append({
                        'type': 'blocked_pattern',
                        'path': str(item),
                        'reason': f"Matches blocked pattern: {pattern}",
                        'severity': 'warning'
                    })
                    break
    
    def _check_blocked_admin_files(self) -> None:
        """
        Check for admin-only files in manifest.
        
        SECURITY: Admin files give users ability to modify CORTEX deployment,
        which violates the source-available license.
        """
        for item in self.manifest:
            item_str = str(item).replace('\\', '/')
            
            for blocked_file in self.BLOCKED_ADMIN_FILES:
                if item_str == blocked_file or item_str.endswith(blocked_file):
                    self.violations.append({
                        'type': 'blocked_admin',
                        'path': str(item),
                        'reason': f"Admin-only file: {blocked_file}",
                        'severity': 'critical',
                        'security': True
                    })
                    break
    
    def _check_database_files(self) -> None:
        """
        Check for populated database files.
        
        Warning only - databases should be empty templates, not populated.
        """
        for item in self.manifest:
            if item.suffix == '.db':
                # Check file size (empty databases are small)
                try:
                    file_path = self.repo_root / item
                    if file_path.exists():
                        size = file_path.stat().st_size
                        
                        # If database > 100KB, it's probably populated
                        if size > 100_000:
                            self.warnings.append(
                                f"Large database file found: {item} ({size:,} bytes). "
                                "Consider excluding populated databases from deployment."
                            )
                except Exception:
                    pass


def main():
    """CLI entry point."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description="Validate CORTEX publish manifest",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--repo',
        type=Path,
        default=Path.cwd(),
        help='CORTEX repository root (default: current directory)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    parser.add_argument(
        '--manifest',
        type=Path,
        help='Path to manifest file (one path per line)'
    )
    
    args = parser.parse_args()
    
    # Load manifest if provided
    manifest = None
    if args.manifest:
        manifest_text = args.manifest.read_text(encoding='utf-8')
        manifest = [Path(line.strip()) for line in manifest_text.split('\n') if line.strip()]
    
    # Run validation
    validator = PublishManifestValidator(args.repo, manifest)
    success, report = validator.validate()
    
    # Output results
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("\n" + "=" * 60)
        print("PUBLISH MANIFEST VALIDATION REPORT")
        print("=" * 60)
        
        print(f"\nTotal items: {report['stats']['total_items']}")
        print(f"Violations: {report['stats']['violations']}")
        print(f"Warnings: {report['stats']['warnings']}")
        
        if report['violations']:
            print("\n❌ VIOLATIONS:")
            
            # Group by type
            by_type = {}
            for v in report['violations']:
                vtype = v['type']
                if vtype not in by_type:
                    by_type[vtype] = []
                by_type[vtype].append(v)
            
            for vtype, violations in by_type.items():
                print(f"\n  {vtype.upper().replace('_', ' ')} ({len(violations)}):")
                for v in violations[:10]:  # Show max 10 per type
                    security_flag = " [SECURITY]" if v.get('security') else ""
                    print(f"    • {v['path']}{security_flag}")
                    print(f"      {v['reason']}")
                
                if len(violations) > 10:
                    print(f"    ... and {len(violations) - 10} more")
        
        if report['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in report['warnings']:
                print(f"  • {warning}")
        
        if not report['violations'] and not report['warnings']:
            print("\n✅ All checks passed!")
        
        print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
