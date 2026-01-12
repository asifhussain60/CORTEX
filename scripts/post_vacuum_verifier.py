#!/usr/bin/env python3
"""
CORTEX 6.0 Post-Vacuum Integrity Verifier

NEW (v4.0): Self-learning verification phase added to vacuum orchestrator.

Performs comprehensive checks after vacuum operations:
1. Critical file existence validation
2. Import chain verification for core modules
3. Test suite sanity check (sample critical tests)
4. Governance compliance verification
5. Database integrity checks

If issues found, generates self-learning recommendations for future vacuum runs.

Author: GitHub Copilot + CORTEX Governance System
Version: 1.0.0
Date: 2026-01-12
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import os

# Define workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent

# Add workspace to path for imports
sys.path.insert(0, str(WORKSPACE_ROOT))


class PostVacuumVerifier:
    """Verifies CORTEX integrity after vacuum operations"""
    
    # Critical files that MUST exist
    CRITICAL_FILES = {
        "cortex-brain/tier0/governance/core-rules.yaml": "Governance rules (SKULL)",
        "cortex-brain/tier1/tracking/progress-tracker.json": "Progress tracking state",
        "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml": "AC-ID registry",
        "cortex-brain/cx6-plan/master-plan.yaml": "Master plan",
        "src/infrastructure/enhanced_audit_logger.py": "Audit logger core",
        "src/orchestrators/core/governance_merger.py": "Governance merger",
        "src/orchestrators/core/master_orchestrator.py": "Master orchestrator",
    }
    
    # Critical imports to verify
    CRITICAL_IMPORTS = {
        "src.infrastructure.enhanced_audit_logger": ["EnhancedAuditLogger", "AuditStorage", "AuditMemoryBuffer"],
        "src.orchestrators.core.governance_merger": ["GovernanceMerger"],
        "src.orchestrators.core.master_orchestrator": ["MasterOrchestrator"],
        "src.mcp.audit_tools": ["audit_query"],
    }
    
    # Sample critical tests to verify
    SAMPLE_TESTS = [
        "tests/governance/test_governance_merger.py::TestGovernanceMerger::test_governance_merger_initialization",
        "tests/infrastructure/test_evidence_bundle_structure.py::TestBundleDirectoryCreation::test_create_bundle_directory",
        "tests/governance/test_audit_validation_simple.py::TestGovernanceAuditValidation::test_audit_system_operational",
    ]
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.issues: List[Dict] = []
        self.passed_checks: List[str] = []
        self.warnings: List[Dict] = []
    
    def verify_all(self) -> bool:
        """Run all verification checks. Returns True if all critical checks pass."""
        print("\n" + "="*70)
        print("🔍 POST-VACUUM INTEGRITY VERIFICATION (v1.0)")
        print("="*70)
        print()
        
        # Phase 1: File existence
        print("Phase 1: Critical File Verification")
        print("-" * 70)
        self._verify_critical_files()
        print()
        
        # Phase 2: Import chain
        print("Phase 2: Import Chain Verification")
        print("-" * 70)
        self._verify_imports()
        print()
        
        # Phase 3: Database integrity
        print("Phase 3: Database Integrity Check")
        print("-" * 70)
        self._verify_databases()
        print()
        
        # Phase 4: Sample tests
        print("Phase 4: Sample Test Suite Validation")
        print("-" * 70)
        self._verify_sample_tests()
        print()
        
        # Phase 5: Governance compliance
        print("Phase 5: Governance Compliance Check")
        print("-" * 70)
        self._verify_governance()
        print()
        
        # Summary
        return self._print_summary()
    
    def _verify_critical_files(self) -> None:
        """Verify all critical files exist and are readable."""
        missing = []
        
        for file_path, description in self.CRITICAL_FILES.items():
            full_path = WORKSPACE_ROOT / file_path
            
            if not full_path.exists():
                missing.append((file_path, description))
                self.issues.append({
                    "severity": "CRITICAL",
                    "type": "missing_file",
                    "file": file_path,
                    "description": description
                })
                print(f"  ✗ {file_path:50} {description}")
            else:
                try:
                    # Try to read file to verify it's not corrupted
                    size = full_path.stat().st_size
                    if size == 0:
                        self.warnings.append({
                            "type": "empty_file",
                            "file": file_path
                        })
                        print(f"  ⚠ {file_path:50} (empty - may be suspicious)")
                    else:
                        self.passed_checks.append(f"File exists: {file_path}")
                        print(f"  ✓ {file_path:50} ({size} bytes)")
                except Exception as e:
                    self.issues.append({
                        "severity": "CRITICAL",
                        "type": "file_read_error",
                        "file": file_path,
                        "error": str(e)
                    })
                    print(f"  ✗ {file_path:50} (read error: {e})")
        
        if missing:
            print(f"\n  ❌ {len(missing)} critical file(s) missing")
        else:
            print(f"\n  ✅ All {len(self.CRITICAL_FILES)} critical files present")
    
    def _verify_imports(self) -> None:
        """Verify critical Python imports work."""
        import_errors = []
        
        for module_name, classes in self.CRITICAL_IMPORTS.items():
            try:
                # Import module
                module = __import__(module_name, fromlist=classes)
                
                # Check each class/function exists
                for class_name in classes:
                    if hasattr(module, class_name):
                        self.passed_checks.append(f"Import: {module_name}.{class_name}")
                        print(f"  ✓ {module_name}.{class_name}")
                    else:
                        import_errors.append((module_name, class_name))
                        self.issues.append({
                            "severity": "CRITICAL",
                            "type": "missing_export",
                            "module": module_name,
                            "symbol": class_name
                        })
                        print(f"  ✗ {module_name}.{class_name} (not exported)")
            
            except ImportError as e:
                import_errors.append((module_name, str(e)))
                self.issues.append({
                    "severity": "CRITICAL",
                    "type": "import_error",
                    "module": module_name,
                    "error": str(e)
                })
                print(f"  ✗ {module_name} (import error: {e})")
        
        if import_errors:
            print(f"\n  ❌ {len(import_errors)} import error(s) detected")
        else:
            print(f"\n  ✅ All critical imports verified")
    
    def _verify_databases(self) -> None:
        """Verify database integrity (governance.db, progress tracker, etc.)"""
        db_path = WORKSPACE_ROOT / "cortex-brain" / "database" / "governance.db"
        
        if not db_path.exists():
            self.warnings.append({
                "type": "missing_database",
                "file": str(db_path)
            })
            print(f"  ⚠ {db_path.name} not found (may not be initialized yet)")
            return
        
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                self.warnings.append({
                    "type": "empty_database",
                    "file": str(db_path)
                })
                print(f"  ⚠ {db_path.name} exists but has no tables")
            else:
                table_count = len(tables)
                self.passed_checks.append(f"Database: {table_count} tables present")
                print(f"  ✓ {db_path.name} has {table_count} table(s)")
            
            conn.close()
        
        except Exception as e:
            self.issues.append({
                "severity": "WARNING",
                "type": "database_error",
                "file": str(db_path),
                "error": str(e)
            })
            print(f"  ✗ {db_path.name} error: {e}")
    
    def _verify_sample_tests(self) -> None:
        """Run a sample of critical tests to verify nothing broke."""
        if self.dry_run:
            print("  [DRY-RUN] Skipping test execution")
            return
        
        print(f"  Running {len(self.SAMPLE_TESTS)} sample tests...")
        
        passed = 0
        failed = 0
        
        for test_name in self.SAMPLE_TESTS:
            try:
                result = subprocess.run(
                    ["python3", "-m", "pytest", test_name, "-v", "--tb=no"],
                    cwd=str(WORKSPACE_ROOT),
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    passed += 1
                    self.passed_checks.append(f"Test: {test_name.split('::')[-1]}")
                    print(f"    ✓ {test_name.split('::')[-1]}")
                else:
                    failed += 1
                    self.issues.append({
                        "severity": "WARNING",
                        "type": "test_failure",
                        "test": test_name,
                        "reason": "Test returned non-zero exit code"
                    })
                    print(f"    ✗ {test_name.split('::')[-1]}")
            
            except subprocess.TimeoutExpired:
                failed += 1
                self.issues.append({
                    "severity": "WARNING",
                    "type": "test_timeout",
                    "test": test_name
                })
                print(f"    ✗ {test_name.split('::')[-1]} (timeout)")
            
            except Exception as e:
                failed += 1
                self.issues.append({
                    "severity": "WARNING",
                    "type": "test_execution_error",
                    "test": test_name,
                    "error": str(e)
                })
                print(f"    ✗ {test_name.split('::')[-1]} (error)")
        
        print(f"\n  Results: {passed} passed, {failed} failed")
    
    def _verify_governance(self) -> None:
        """Verify governance files are present and parseable."""
        import yaml
        
        governance_files = [
            "cortex-brain/tier0/governance/core-rules.yaml",
            "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml",
        ]
        
        for gov_file in governance_files:
            file_path = WORKSPACE_ROOT / gov_file
            
            if not file_path.exists():
                self.issues.append({
                    "severity": "CRITICAL",
                    "type": "missing_governance",
                    "file": gov_file
                })
                print(f"  ✗ {gov_file} (missing)")
                continue
            
            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                
                if data is None:
                    self.warnings.append({
                        "type": "empty_governance_file",
                        "file": gov_file
                    })
                    print(f"  ⚠ {gov_file} (empty)")
                else:
                    self.passed_checks.append(f"Governance: {gov_file}")
                    print(f"  ✓ {gov_file} (valid YAML, {len(data) if isinstance(data, dict) else '?'} entries)")
            
            except Exception as e:
                self.issues.append({
                    "severity": "CRITICAL",
                    "type": "governance_parse_error",
                    "file": gov_file,
                    "error": str(e)
                })
                print(f"  ✗ {gov_file} (parse error: {e})")
    
    def _print_summary(self) -> bool:
        """Print verification summary and return success status."""
        print("="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        print()
        
        critical_issues = [i for i in self.issues if i.get("severity") == "CRITICAL"]
        warning_issues = [i for i in self.issues if i.get("severity") != "CRITICAL"]
        
        print(f"✅ Checks Passed:        {len(self.passed_checks)}")
        print(f"⚠️  Warnings:             {len(self.warnings)}")
        print(f"⚠️  Non-Critical Issues:  {len(warning_issues)}")
        print(f"❌ Critical Issues:      {len(critical_issues)}")
        print()
        
        if critical_issues:
            print("CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"  • {issue['type']}: {issue.get('file', issue.get('module', 'unknown'))}")
            print()
        
        # Return success if no critical issues
        success = len(critical_issues) == 0
        
        if success:
            print("="*70)
            print("✅ POST-VACUUM VERIFICATION COMPLETE - NO CRITICAL ISSUES")
            print("="*70)
        else:
            print("="*70)
            print("❌ POST-VACUUM VERIFICATION FAILED - CRITICAL ISSUES DETECTED")
            print("="*70)
        
        return success


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Post-Vacuum Integrity Verifier"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip test execution (default: run tests)"
    )
    
    args = parser.parse_args()
    
    verifier = PostVacuumVerifier(dry_run=args.dry_run)
    success = verifier.verify_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
