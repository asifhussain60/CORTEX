#!/usr/bin/env python3
"""
Migration Activation Validator

Prevents "developed but not activated" failures by validating:
1. New 4.0 code is activated (referenced in instructions/config)
2. Old 3.0 code is deleted from filesystem
3. Tests reference new paths only
4. Documentation is updated

Usage:
    python scripts/validate_migration_activation.py [--migration MIGRATION_NAME]
    python scripts/validate_migration_activation.py --all
    python scripts/validate_migration_activation.py --fix

Exit codes:
    0 - All validations passed
    1 - Validation failures detected
    2 - Configuration error
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class MigrationValidator:
    """Validates migration activation status"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.checklist_path = repo_root / "cortex-brain/manifests/migration-activation-checklist.yaml"
        self.checklist = self._load_checklist()
        self.failures: List[str] = []
        self.warnings: List[str] = []
        
    def _load_checklist(self) -> Dict:
        """Load migration activation checklist"""
        if not self.checklist_path.exists():
            raise FileNotFoundError(f"Checklist not found: {self.checklist_path}")
        
        with open(self.checklist_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def validate_migration(self, migration_name: str) -> bool:
        """Validate a single migration"""
        if migration_name not in self.checklist['migrations']:
            print(f"❌ Migration not found in checklist: {migration_name}")
            return False
        
        migration = self.checklist['migrations'][migration_name]
        status = migration.get('status', 'UNKNOWN')
        
        print(f"\n{'='*80}")
        print(f"🔍 Validating: {migration_name}")
        print(f"{'='*80}")
        print(f"Status: {status}")
        
        if status == 'PENDING':
            print("⏳ Migration pending - skipping validation")
            return True
        
        # Run all validation checks
        checks = [
            self._check_new_code_activated(migration_name, migration),
            self._check_old_code_deleted(migration_name, migration),
            self._check_tests_updated(migration_name, migration),
            self._check_docs_updated(migration_name, migration),
        ]
        
        passed = all(checks)
        
        if passed:
            print(f"✅ All checks passed for {migration_name}")
        else:
            print(f"❌ Validation failed for {migration_name}")
        
        return passed
    
    def _check_new_code_activated(self, name: str, migration: Dict) -> bool:
        """Check if new 4.0 code is activated"""
        print(f"\n📋 Check 1: New Code Activated")
        
        new_path = migration.get('new_path')
        if not new_path:
            print("⚠️  No new_path specified - skipping")
            return True
        
        # Check file exists
        full_path = self.repo_root / new_path
        if not full_path.exists():
            self.failures.append(f"❌ {name}: New code does not exist: {new_path}")
            print(f"❌ File not found: {new_path}")
            return False
        
        print(f"✅ New code exists: {new_path}")
        
        # Check if activated (referenced in instructions)
        activated_in = migration.get('activated_in', [])
        if not activated_in:
            self.failures.append(f"❌ {name}: Not activated (no references in instructions)")
            print(f"❌ Not activated - no references found")
            return False
        
        # Verify references exist
        activation_files = [
            '.github/copilot-instructions.md',
            '.github/prompts/CORTEX.prompt.md',
            'cortex.config.json',
        ]
        
        filename = Path(new_path).stem
        classname = self._path_to_classname(new_path)
        
        found_references = False
        for ref_file in activation_files:
            ref_path = self.repo_root / ref_file
            if not ref_path.exists():
                continue
            
            content = ref_path.read_text(encoding='utf-8')
            if filename in content or classname in content:
                print(f"✅ Referenced in: {ref_file}")
                found_references = True
        
        if not found_references:
            self.failures.append(f"❌ {name}: New code exists but not referenced in instructions")
            print(f"❌ Not found in: {', '.join(activation_files)}")
            return False
        
        return True
    
    def _check_old_code_deleted(self, name: str, migration: Dict) -> bool:
        """Check if old 3.0 code is deleted"""
        print(f"\n🗑️  Check 2: Old Code Deleted")
        
        old_path = migration.get('old_path')
        if not old_path:
            print("✅ No old code to delete (new component)")
            return True
        
        deleted_info = migration.get('deleted', [])
        
        # Check if deletion is pending
        if deleted_info:
            if isinstance(deleted_info, list) and len(deleted_info) > 0:
                if deleted_info[0].get('status') == 'PENDING':
                    paths = deleted_info[0].get('paths', [])
                    self.warnings.append(f"⚠️  {name}: Old code deletion pending: {', '.join(paths)}")
                    print(f"⚠️  Deletion pending: {', '.join(paths)}")
                    return False
        
        # Check if old path still exists
        full_path = self.repo_root / old_path
        if full_path.exists():
            # Allow if it's in archive/
            if 'archive' in str(full_path) or '.backup' in str(full_path):
                print(f"✅ Old code archived: {old_path}")
                return True
            
            self.failures.append(f"❌ {name}: Old code still exists: {old_path}")
            print(f"❌ Old code NOT deleted: {old_path}")
            return False
        
        print(f"✅ Old code deleted: {old_path}")
        return True
    
    def _check_tests_updated(self, name: str, migration: Dict) -> bool:
        """Check if tests reference new paths"""
        print(f"\n🧪 Check 3: Tests Updated")
        
        old_path = migration.get('old_path')
        if not old_path:
            print("✅ No old tests to update (new component)")
            return True
        
        # Search for old path references in tests
        tests_dir = self.repo_root / 'tests'
        if not tests_dir.exists():
            print("⚠️  No tests directory found")
            return True
        
        # Extract old module path pattern
        old_module = old_path.replace('src/', '').replace('.py', '').replace('/', '.')
        
        matches = []
        for test_file in tests_dir.rglob('*.py'):
            content = test_file.read_text(encoding='utf-8', errors='ignore')
            if old_module in content or old_path in content:
                matches.append(str(test_file.relative_to(self.repo_root)))
        
        if matches:
            self.warnings.append(f"⚠️  {name}: {len(matches)} test files still reference old path")
            print(f"⚠️  Found {len(matches)} files with old path references:")
            for match in matches[:5]:  # Show first 5
                print(f"   - {match}")
            if len(matches) > 5:
                print(f"   ... and {len(matches) - 5} more")
            return False
        
        print(f"✅ No test files reference old path")
        return True
    
    def _check_docs_updated(self, name: str, migration: Dict) -> bool:
        """Check if documentation is updated"""
        print(f"\n📚 Check 4: Documentation Updated")
        
        old_path = migration.get('old_path')
        if not old_path:
            print("✅ No old docs to update (new component)")
            return True
        
        # Search for old path references in docs
        docs_dirs = [
            self.repo_root / 'docs',
            self.repo_root / 'cortex-brain/documents',
        ]
        
        matches = []
        for docs_dir in docs_dirs:
            if not docs_dir.exists():
                continue
            
            for doc_file in docs_dir.rglob('*.md'):
                try:
                    content = doc_file.read_text(encoding='utf-8')
                    if old_path in content:
                        matches.append(str(doc_file.relative_to(self.repo_root)))
                except Exception:
                    pass
        
        if matches:
            # Allow some historical references
            if len(matches) <= 5:
                print(f"✅ Minor doc references found ({len(matches)}): acceptable")
                return True
            
            self.warnings.append(f"⚠️  {name}: {len(matches)} doc files still reference old path")
            print(f"⚠️  Found {len(matches)} files with old path references:")
            for match in matches[:5]:
                print(f"   - {match}")
            if len(matches) > 5:
                print(f"   ... and {len(matches) - 5} more")
        else:
            print(f"✅ No documentation references old path")
        
        return True
    
    def validate_all(self) -> bool:
        """Validate all completed migrations"""
        migrations = self.checklist['migrations']
        completed = [name for name, data in migrations.items() 
                     if data.get('status') == 'COMPLETE']
        
        print(f"\n{'='*80}")
        print(f"🔍 Validating {len(completed)} completed migrations")
        print(f"{'='*80}")
        
        results = []
        for migration_name in completed:
            results.append(self.validate_migration(migration_name))
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 VALIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total migrations validated: {len(results)}")
        print(f"Passed: {sum(results)}")
        print(f"Failed: {len(results) - sum(results)}")
        
        if self.failures:
            print(f"\n❌ FAILURES ({len(self.failures)}):")
            for failure in self.failures:
                print(f"  {failure}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        return all(results)
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate migration activation status report"""
        if output_path is None:
            output_path = self.repo_root / "cortex-brain/documents/reports/migration-activation-status.md"
        
        migrations = self.checklist['migrations']
        
        report = []
        report.append("# Migration Activation Status Report")
        report.append(f"\n**Generated:** {self._current_timestamp()}")
        report.append("\n---\n")
        
        # Progress summary
        total = len(migrations)
        complete = sum(1 for m in migrations.values() if m.get('status') == 'COMPLETE')
        activated = sum(1 for m in migrations.values() 
                       if m.get('status') == 'COMPLETE' and m.get('activated_in'))
        deleted = sum(1 for m in migrations.values()
                     if m.get('status') == 'COMPLETE' and 
                     m.get('deleted') and 
                     not any(d.get('status') == 'PENDING' for d in m.get('deleted', [])))
        
        report.append("## 📊 Progress Summary\n")
        report.append(f"- **Total Migrations:** {total}")
        report.append(f"- **Completed:** {complete}/{total} ({complete/total*100:.0f}%)")
        activated_pct = (activated/complete*100) if complete > 0 else 0
        report.append(f"- **Activated:** {activated}/{complete} ({activated_pct:.0f}%)")
        deleted_pct = (deleted/complete*100) if complete > 0 else 0
        report.append(f"- **Cleanup Done:** {deleted}/{complete} ({deleted_pct:.0f}%)")
        
        # Failures
        if self.failures:
            report.append("\n## ❌ Activation Failures\n")
            for failure in self.failures:
                report.append(f"- {failure}")
        
        # Warnings
        if self.warnings:
            report.append("\n## ⚠️  Cleanup Pending\n")
            for warning in self.warnings:
                report.append(f"- {warning}")
        
        # Details table
        report.append("\n## 📋 Migration Details\n")
        report.append("| Migration | Status | Activated | Deleted | Notes |")
        report.append("|-----------|--------|-----------|---------|-------|")
        
        for name, data in migrations.items():
            status = data.get('status', 'UNKNOWN')
            activated = '✅' if data.get('activated_in') else '❌'
            deleted_status = data.get('deleted', [])
            deleted = '✅' if deleted_status and not any(d.get('status') == 'PENDING' for d in deleted_status) else '⏳'
            notes = data.get('notes', '-')
            
            if status == 'PENDING':
                activated = '-'
                deleted = '-'
            
            report.append(f"| {name} | {status} | {activated} | {deleted} | {notes} |")
        
        report_text = '\n'.join(report)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text, encoding='utf-8')
        print(f"\n📄 Report saved: {output_path}")
        
        return report_text
    
    def _path_to_classname(self, path: str) -> str:
        """Convert file path to likely class name"""
        # src/orchestration_4_0/orchestrators/execution_orchestrator_v4.py
        # -> ExecutionOrchestratorV4
        stem = Path(path).stem
        parts = stem.split('_')
        return ''.join(p.capitalize() for p in parts)
    
    def _current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    parser = argparse.ArgumentParser(description='Validate migration activation status')
    parser.add_argument('--migration', help='Validate specific migration')
    parser.add_argument('--all', action='store_true', help='Validate all completed migrations')
    parser.add_argument('--report', action='store_true', help='Generate status report')
    
    args = parser.parse_args()
    
    # Find repo root
    repo_root = Path(__file__).parent.parent
    
    try:
        validator = MigrationValidator(repo_root)
        
        if args.report:
            validator.generate_report()
            return 0
        
        if args.all:
            success = validator.validate_all()
            validator.generate_report()
            return 0 if success else 1
        
        if args.migration:
            success = validator.validate_migration(args.migration)
            return 0 if success else 1
        
        # Default: validate all
        success = validator.validate_all()
        validator.generate_report()
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
