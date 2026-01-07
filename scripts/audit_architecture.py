#!/usr/bin/env python3
"""
CORTEX 6.0 Architecture Audit Script

Validates architecture compliance before commits:
1. Audit logging is operational
2. Test infrastructure exists
3. Core components are present
4. No SKULL rule violations

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
AUDIT_LOG_DIR = PROJECT_ROOT / "cortex-brain" / "audit-logs"
TESTS_DIR = PROJECT_ROOT / "tests"
SRC_DIR = PROJECT_ROOT / "src"
SESSION_AUDIT = PROJECT_ROOT / ".asif" / "AI-Learning" / "cortex6" / "source-of-truth" / "session-audit.jsonl"


class ArchitectureAuditor:
    """Validates CORTEX architecture compliance."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []
        
    def audit_all(self) -> bool:
        """Run all architecture audits."""
        print("\n🔍 CORTEX 6.0 Architecture Audit")
        print("=" * 60)
        
        # Run audits
        self._audit_test_infrastructure()
        self._audit_core_components()
        self._audit_audit_logging()
        self._audit_skull_compliance()
        
        # Report results
        return self._report_results()
    
    def _audit_test_infrastructure(self):
        """Verify test infrastructure exists."""
        print("\n📁 Test Infrastructure Check...")
        
        required_paths = [
            TESTS_DIR / "__init__.py",
            TESTS_DIR / "conftest.py",
            TESTS_DIR / "unit" / "__init__.py",
            TESTS_DIR / "integration" / "__init__.py",
        ]
        
        for path in required_paths:
            if path.exists():
                self.passed.append(f"✓ {path.relative_to(PROJECT_ROOT)}")
            else:
                self.errors.append(f"Missing: {path.relative_to(PROJECT_ROOT)}")
        
        # Check for at least one test file
        test_files = list(TESTS_DIR.glob("**/test_*.py"))
        if test_files:
            self.passed.append(f"✓ Found {len(test_files)} test file(s)")
        else:
            self.warnings.append("No test files found in tests/")
    
    def _audit_core_components(self):
        """Verify core CORTEX components exist."""
        print("\n🧩 Core Components Check...")
        
        core_components = [
            SRC_DIR / "orchestrators" / "audit_logger.py",
            SRC_DIR / "orchestrators" / "state_manager.py",
            SRC_DIR / "orchestrators" / "pattern_router.py",
            SRC_DIR / "main.py",
        ]
        
        for path in core_components:
            if path.exists():
                self.passed.append(f"✓ {path.relative_to(PROJECT_ROOT)}")
            else:
                self.warnings.append(f"Optional: {path.relative_to(PROJECT_ROOT)}")
    
    def _audit_audit_logging(self):
        """Verify audit logging is operational."""
        print("\n📝 Audit Logging Check...")
        
        # Check audit log directory exists
        if not AUDIT_LOG_DIR.exists():
            self.errors.append("Audit log directory missing: cortex-brain/audit-logs/")
            return
        
        self.passed.append("✓ Audit log directory exists")
        
        # Check for recent audit logs (within last 24 hours)
        recent_logs = []
        cutoff = datetime.now() - timedelta(hours=24)
        
        for log_file in AUDIT_LOG_DIR.glob("*.jsonl"):
            if log_file.stat().st_mtime > cutoff.timestamp():
                recent_logs.append(log_file)
        
        if recent_logs:
            self.passed.append(f"✓ Found {len(recent_logs)} recent audit log(s)")
        else:
            self.warnings.append("No audit logs in last 24 hours (system may be idle)")
        
        # Check session audit log for CORTEX 6.0 build
        if SESSION_AUDIT.exists():
            with open(SESSION_AUDIT) as f:
                entries = [json.loads(line) for line in f if line.strip()]
            if entries:
                self.passed.append(f"✓ Session audit log has {len(entries)} entries")
            else:
                self.warnings.append("Session audit log is empty")
        else:
            self.warnings.append("No CORTEX 6.0 session audit log found")
    
    def _audit_skull_compliance(self):
        """Check SKULL (brain protection) rule compliance."""
        print("\n🛡️ SKULL Compliance Check...")
        
        # Check for forbidden patterns in staged files
        import subprocess
        
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            staged_files = [f for f in result.stdout.strip().split("\n") if f]
            
            if not staged_files:
                self.passed.append("✓ No staged files to check")
                return
            
            # SKULL Rule: No test files outside tests/
            for f in staged_files:
                if f.startswith("test_") and not f.startswith("tests/"):
                    self.errors.append(f"SKULL Violation: Test file outside tests/: {f}")
            
            # SKULL Rule: No root-level docs
            for f in staged_files:
                if f.endswith(".md") and "/" not in f and f not in ["README.md", "LICENSE", "DEPLOYMENT.md"]:
                    self.warnings.append(f"SKULL Warning: Root-level doc: {f}")
            
            self.passed.append(f"✓ Checked {len(staged_files)} staged file(s)")
            
        except Exception as e:
            self.warnings.append(f"Could not check staged files: {e}")
    
    def _report_results(self) -> bool:
        """Report audit results and return success status."""
        print("\n" + "=" * 60)
        print("📊 AUDIT RESULTS")
        print("=" * 60)
        
        # Print passed checks
        if self.passed:
            print(f"\n✅ PASSED ({len(self.passed)}):")
            for item in self.passed[:10]:  # Limit output
                print(f"   {item}")
            if len(self.passed) > 10:
                print(f"   ... and {len(self.passed) - 10} more")
        
        # Print warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for item in self.warnings:
                print(f"   {item}")
        
        # Print errors
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for item in self.errors:
                print(f"   {item}")
        
        # Summary
        print("\n" + "-" * 60)
        total = len(self.passed) + len(self.warnings) + len(self.errors)
        print(f"Total checks: {total}")
        print(f"Passed: {len(self.passed)} | Warnings: {len(self.warnings)} | Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ AUDIT FAILED - Fix errors before committing")
            return False
        elif self.warnings:
            print("\n⚠️  AUDIT PASSED WITH WARNINGS")
            return True
        else:
            print("\n✅ AUDIT PASSED")
            return True


def main():
    """Run architecture audit."""
    auditor = ArchitectureAuditor()
    success = auditor.audit_all()
    
    # Save audit report
    report_dir = PROJECT_ROOT / "cortex-brain" / "documents" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "passed": auditor.passed,
        "warnings": auditor.warnings,
        "errors": auditor.errors
    }
    
    report_file = report_dir / f"architecture-audit-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
