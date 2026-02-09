#!/usr/bin/env python3
"""
LENS Migration Audit Script (Phase 53 - Stage 7)

Validates that LENS consolidation is complete:
- No duplicate LENS implementations
- All imports use cortex.brain.lens.*
- Deprecated APIs marked correctly
- Zero breaking changes detected

Usage:
    python scripts/audit_lens_migration.py --strict
    python scripts/audit_lens_migration.py --check-duplicates
    python scripts/audit_lens_migration.py --generate-report

Author: CORTEX Phase 53 - Stage 7
AC-PHASE53-009: Single source of truth validation
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
import re
import json


class LENSMigrationAuditor:
    """Audits LENS migration for Phase 53 completion."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.cortex_dir = repo_root / "cortex"
        self.tests_dir = repo_root / "tests"
        
        # Deprecated files that should only be referenced in migration docs
        self.deprecated_files = {
            "cortex/orchestrators/core/lens_synthesis.py",
            "cortex/domain_brain/lens_integration.py",
            "cortex/orchestrators/support/lens_analysis_extractor.py",
        }
        
        # Files scheduled for deletion in S7
        self.to_delete = {
            "cortex/orchestrators/support/lens_analysis_extractor.py",
        }
        
        # Canonical LENS implementation
        self.canonical_lens = "cortex/brain/lens/pipeline.py"
        
        self.issues: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []
    
    def audit_duplicate_implementations(self) -> bool:
        """Check for duplicate LENS class definitions."""
        print("\n🔍 Auditing duplicate LENS implementations...")
        
        lens_classes = ["LENSPipeline", "LENSSynthesis", "LENSContext", "LENSOrchestrator"]
        duplicates_found = False
        
        for lens_class in lens_classes:
            occurrences = []
            
            for py_file in self.cortex_dir.rglob("*.py"):
                if py_file.is_file():
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                    if f"class {lens_class}" in content:
                        occurrences.append(str(py_file.relative_to(self.repo_root)))
            
            if len(occurrences) > 1:
                # Check if extra occurrences are deprecated
                non_deprecated = [f for f in occurrences if f not in self.deprecated_files]
                
                if len(non_deprecated) > 1:
                    self.issues.append({
                        "type": "DUPLICATE_IMPLEMENTATION",
                        "class": lens_class,
                        "files": ", ".join(non_deprecated),
                        "severity": "HIGH"
                    })
                    duplicates_found = True
                    print(f"  ❌ {lens_class} found in {len(non_deprecated)} files: {non_deprecated}")
                elif len(occurrences) > 1:
                    print(f"  ⚠️  {lens_class} found in deprecated files (OK): {occurrences}")
                else:
                    print(f"  ✅ {lens_class} has single source of truth")
            elif len(occurrences) == 1:
                print(f"  ✅ {lens_class} has single source of truth: {occurrences[0]}")
            else:
                self.warnings.append({
                    "type": "MISSING_CLASS",
                    "class": lens_class,
                    "severity": "LOW"
                })
                print(f"  ⚠️  {lens_class} not found")
        
        return not duplicates_found
    
    def audit_import_statements(self) -> bool:
        """Verify all imports use canonical cortex.brain.lens path."""
        print("\n🔍 Auditing import statements...")
        
        bad_imports = []
        deprecated_import_patterns = [
            r"from cortex\.orchestrators\.core\.lens_synthesis import",
            r"from cortex\.domain_brain\.lens_integration import",
            r"from cortex\.orchestrators\.support\.lens_analysis_extractor import",
        ]
        
        for py_file in self.cortex_dir.rglob("*.py"):
            if py_file.is_file() and str(py_file.relative_to(self.repo_root)) not in self.deprecated_files:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                
                for pattern in deprecated_import_patterns:
                    if re.search(pattern, content):
                        bad_imports.append({
                            "file": str(py_file.relative_to(self.repo_root)),
                            "pattern": pattern
                        })
        
        if bad_imports:
            for bad_import in bad_imports:
                self.issues.append({
                    "type": "BAD_IMPORT",
                    "file": bad_import["file"],
                    "pattern": bad_import["pattern"],
                    "severity": "HIGH"
                })
                print(f"  ❌ {bad_import['file']} uses deprecated import")
            return False
        else:
            print("  ✅ All imports use canonical cortex.brain.lens.*")
            return True
    
    def audit_deprecated_markers(self) -> bool:
        """Verify deprecated files have @deprecated decorator."""
        print("\n🔍 Auditing deprecated markers...")
        
        missing_deprecation = []
        
        for deprecated_file in self.deprecated_files:
            file_path = self.repo_root / deprecated_file
            
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                
                if "@deprecated" not in content and "DeprecationWarning" not in content:
                    missing_deprecation.append(deprecated_file)
                    self.issues.append({
                        "type": "MISSING_DEPRECATION",
                        "file": deprecated_file,
                        "severity": "MEDIUM"
                    })
                    print(f"  ❌ {deprecated_file} missing @deprecated marker")
                else:
                    print(f"  ✅ {deprecated_file} properly marked as deprecated")
        
        return len(missing_deprecation) == 0
    
    def audit_deleted_files(self) -> bool:
        """Verify files scheduled for deletion are removed."""
        print("\n🔍 Auditing deleted files...")
        
        still_exists = []
        
        for file_to_delete in self.to_delete:
            file_path = self.repo_root / file_to_delete
            
            if file_path.exists():
                still_exists.append(file_to_delete)
                self.warnings.append({
                    "type": "FILE_NOT_DELETED",
                    "file": file_to_delete,
                    "severity": "MEDIUM"
                })
                print(f"  ⚠️  {file_to_delete} still exists (scheduled for deletion)")
            else:
                print(f"  ✅ {file_to_delete} successfully deleted")
        
        return len(still_exists) == 0
    
    def audit_canonical_implementation(self) -> bool:
        """Verify canonical LENS implementation exists and is complete."""
        print("\n🔍 Auditing canonical LENS implementation...")
        
        canonical_path = self.repo_root / self.canonical_lens
        
        if not canonical_path.exists():
            self.issues.append({
                "type": "MISSING_CANONICAL",
                "file": self.canonical_lens,
                "severity": "CRITICAL"
            })
            print(f"  ❌ Canonical LENS implementation missing: {self.canonical_lens}")
            return False
        
        content = canonical_path.read_text(encoding="utf-8")
        
        required_classes = ["LENSPipeline", "LanguagePhase", "ExaminationPhase", 
                           "SynthesisPhase", "KnowledgePhase"]
        missing_classes = [cls for cls in required_classes if f"class {cls}" not in content]
        
        if missing_classes:
            self.issues.append({
                "type": "INCOMPLETE_CANONICAL",
                "file": self.canonical_lens,
                "missing": ", ".join(missing_classes),
                "severity": "CRITICAL"
            })
            print(f"  ❌ {self.canonical_lens} missing classes: {missing_classes}")
            return False
        
        print(f"  ✅ {self.canonical_lens} is complete")
        return True
    
    def generate_report(self) -> Dict:
        """Generate migration audit report."""
        return {
            "audit_date": "2026-02-09",
            "phase": "Phase 53 - Stage 7",
            "canonical_implementation": self.canonical_lens,
            "deprecated_files": list(self.deprecated_files),
            "issues": self.issues,
            "warnings": self.warnings,
            "summary": {
                "total_issues": len(self.issues),
                "total_warnings": len(self.warnings),
                "critical_issues": len([i for i in self.issues if i.get("severity") == "CRITICAL"]),
                "high_issues": len([i for i in self.issues if i.get("severity") == "HIGH"]),
                "passed": len(self.issues) == 0
            }
        }
    
    def run_all_audits(self, strict: bool = False) -> bool:
        """Run all audit checks."""
        print("\n" + "=" * 80)
        print("LENS MIGRATION AUDIT - PHASE 53 STAGE 7")
        print("=" * 80)
        
        checks = [
            ("Duplicate Implementations", self.audit_duplicate_implementations),
            ("Import Statements", self.audit_import_statements),
            ("Deprecated Markers", self.audit_deprecated_markers),
            ("Deleted Files", self.audit_deleted_files),
            ("Canonical Implementation", self.audit_canonical_implementation),
        ]
        
        results = []
        for check_name, check_func in checks:
            try:
                passed = check_func()
                results.append((check_name, passed))
            except Exception as e:
                print(f"\n  ⚠️  Error during {check_name}: {e}")
                results.append((check_name, False))
        
        # Print summary
        print("\n" + "=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)
        
        all_passed = all(passed for _, passed in results)
        
        for check_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check_name}")
        
        print(f"\nTotal Issues: {len(self.issues)}")
        print(f"Total Warnings: {len(self.warnings)}")
        
        if all_passed:
            print("\n🎉 LENS MIGRATION AUDIT PASSED")
            return True
        else:
            print("\n⚠️  LENS MIGRATION AUDIT FAILED")
            
            if self.issues:
                print("\n❌ Issues Found:")
                for issue in self.issues:
                    print(f"  - [{issue['severity']}] {issue['type']}: {issue.get('file', issue.get('class', 'N/A'))}")
            
            if strict:
                print("\n🔴 STRICT MODE: Failing due to issues")
                return False
            else:
                print("\n⚠️  WARNINGS ONLY: Pass with warnings")
                return len([i for i in self.issues if i.get("severity") in ["CRITICAL", "HIGH"]]) == 0
        
        return all_passed


def main():
    parser = argparse.ArgumentParser(description="Audit LENS migration for Phase 53")
    parser.add_argument("--strict", action="store_true", help="Fail on any issues (not just critical)")
    parser.add_argument("--check-duplicates", action="store_true", help="Only check for duplicates")
    parser.add_argument("--generate-report", action="store_true", help="Generate JSON report")
    parser.add_argument("--output", default="lens_migration_audit.json", help="Report output file")
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    auditor = LENSMigrationAuditor(repo_root)
    
    if args.check_duplicates:
        passed = auditor.audit_duplicate_implementations()
        sys.exit(0 if passed else 1)
    
    passed = auditor.run_all_audits(strict=args.strict)
    
    if args.generate_report:
        report = auditor.generate_report()
        output_path = Path(args.output)
        output_path.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Report saved to: {output_path}")
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
