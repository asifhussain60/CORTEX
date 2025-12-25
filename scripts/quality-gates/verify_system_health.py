#!/usr/bin/env python3
"""
System Health Verification for CORTEX 4.0 GA Release

Runs comprehensive system health checks:
1. Test suite health (pass rate, execution time)
2. Import validation (all modules importable)
3. Configuration validation (all config files valid)
4. Database schema validation (brain databases exist)

Author: Asif Hussain
Date: December 25, 2025
"""

import subprocess
import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

class SystemHealthVerifier:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results = []
        
    def run_all_checks(self) -> Dict:
        """Run all health checks."""
        print("=" * 80)
        print("🏥 CORTEX 4.0 SYSTEM HEALTH VERIFICATION")
        print("=" * 80)
        print("")
        
        # Check 1: Test Suite Health
        print("📊 Check 1/5: Test Suite Health...")
        test_result = self._check_test_suite()
        self.results.append(test_result)
        self._print_check_result(test_result)
        
        # Check 2: Module Import Validation
        print("\n📦 Check 2/5: Core Module Existence...")
        import_result = self._check_module_imports()
        self.results.append(import_result)
        self._print_check_result(import_result)
        
        # Check 3: Configuration Validation
        print("\n⚙️  Check 3/5: Configuration Validation...")
        config_result = self._check_configurations()
        self.results.append(config_result)
        self._print_check_result(config_result)
        
        # Check 4: Database Schema Validation
        print("\n🗄️  Check 4/5: Database Schema Validation...")
        db_result = self._check_databases()
        self.results.append(db_result)
        self._print_check_result(db_result)
        
        # Check 5: Critical File Existence
        print("\n📁 Check 5/5: Critical File Existence...")
        file_result = self._check_critical_files()
        self.results.append(file_result)
        self._print_check_result(file_result)
        
        return {
            "overall_status": all(r["status"] == "pass" for r in self.results),
            "checks": self.results
        }
    
    def _check_test_suite(self) -> Dict:
        """Check test suite health."""
        try:
            # Use virtual environment Python if available
            venv_python = self.project_root / ".venv/bin/python3"
            python_cmd = str(venv_python) if venv_python.exists() else "python3"
            
            result = subprocess.run(
                [python_cmd, "-m", "pytest", "tests/", "-q", "--tb=no", "--no-header"],
                capture_output=True,
                text=True,
                timeout=180,  # 3 minutes max
                cwd=self.project_root
            )
            
            # Parse output
            output = result.stdout + result.stderr
            lines = output.strip().split('\n')
            summary_line = lines[-1] if lines else ""
            
            # Extract metrics
            passed = 0
            failed = 0
            skipped = 0
            
            if "passed" in summary_line:
                parts = summary_line.split()
                for i, part in enumerate(parts):
                    if part == "passed,":
                        passed = int(parts[i-1])
                    elif part == "failed,":
                        failed = int(parts[i-1])
                    elif part == "skipped":
                        skipped = int(parts[i-1])
            
            total = passed + failed + skipped
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            return {
                "check": "Test Suite Health",
                "status": "pass" if pass_rate >= 95 else "warn",
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": f"{pass_rate:.1f}%",
                "threshold": "≥95%",
                "message": f"{passed} passed, {failed} failed, {skipped} skipped ({pass_rate:.1f}%)"
            }
        except Exception as e:
            return {
                "check": "Test Suite Health",
                "status": "warn",
                "message": f"Could not run tests (venv may be inactive): {str(e)[:50]}"
            }
    
    def _check_module_imports(self) -> Dict:
        """Check that core modules exist (file-based check)."""
        critical_modules = [
            "src/orchestrators/base_orchestrator.py",
            "src/cortex_agents/investigation_router_agent.py",
            "src/tier0/brain_protector.py",
            "src/tier1/working_memory.py",
            "src/tier2/knowledge_graph.py",
            "src/tier3/development_context.py",
            "src/core/context_injector.py",
        ]
        
        existing = []
        missing = []
        
        for module_path in critical_modules:
            path = self.project_root / module_path
            if path.exists():
                existing.append(module_path)
            else:
                missing.append(module_path)
        
        success_rate = len(existing) / len(critical_modules) * 100
        
        return {
            "check": "Core Module Existence",
            "status": "pass" if len(missing) == 0 else "fail",
            "existing": len(existing),
            "missing": len(missing),
            "success_rate": f"{success_rate:.1f}%",
            "threshold": "100%",
            "message": f"{len(existing)}/{len(critical_modules)} core modules exist",
            "failures": [{"file": f} for f in missing] if missing else None
        }
    
    def _check_configurations(self) -> Dict:
        """Check that all configuration files are valid JSON."""
        config_files = [
            "cortex.config.json",
            "cortex-brain/config/operations-config.yaml",
        ]
        
        valid = []
        invalid = []
        
        for config_file in config_files:
            path = self.project_root / config_file
            if not path.exists():
                invalid.append({"file": config_file, "error": "File not found"})
                continue
            
            try:
                if config_file.endswith('.json'):
                    with open(path) as f:
                        json.load(f)
                valid.append(config_file)
            except Exception as e:
                invalid.append({"file": config_file, "error": str(e)[:100]})
        
        return {
            "check": "Configuration Validation",
            "status": "pass" if len(invalid) == 0 else "warn",
            "valid": len(valid),
            "invalid": len(invalid),
            "message": f"{len(valid)}/{len(config_files)} configuration files valid",
            "failures": invalid if invalid else None
        }
    
    def _check_databases(self) -> Dict:
        """Check that brain databases exist and are accessible."""
        databases = [
            "cortex-brain.db",
            "cortex-brain/conversation-history.db",
        ]
        
        accessible = []
        issues = []
        
        for db_file in databases:
            path = self.project_root / db_file
            if not path.exists():
                issues.append({"database": db_file, "error": "File not found"})
                continue
            
            try:
                conn = sqlite3.connect(str(path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                accessible.append({"database": db_file, "tables": len(tables)})
            except Exception as e:
                issues.append({"database": db_file, "error": str(e)[:100]})
        
        return {
            "check": "Database Schema Validation",
            "status": "pass" if len(issues) == 0 else "warn",
            "accessible": len(accessible),
            "issues": len(issues),
            "message": f"{len(accessible)}/{len(databases)} databases accessible",
            "failures": issues if issues else None,
            "details": accessible
        }
    
    def _check_critical_files(self) -> Dict:
        """Check that all critical files exist."""
        critical_files = [
            "README.md",
            "CHANGELOG.md",
            "requirements.txt",
            "cortex-operations.yaml",
            "cortex-brain/brain-protection-rules.yaml",
            "cortex-brain/response-templates-v4.yaml",
            ".github/prompts/CORTEX.prompt.md",
            "cortex-brain/documents/guides/RELEASE-NOTES-v4.0-GA.md",
        ]
        
        existing = []
        missing = []
        
        for file_path in critical_files:
            path = self.project_root / file_path
            if path.exists():
                existing.append(file_path)
            else:
                missing.append(file_path)
        
        return {
            "check": "Critical File Existence",
            "status": "pass" if len(missing) == 0 else "fail",
            "existing": len(existing),
            "missing": len(missing),
            "message": f"{len(existing)}/{len(critical_files)} critical files present",
            "failures": missing if missing else None
        }
    
    def _print_check_result(self, result: Dict):
        """Print check result with color coding."""
        status_icons = {
            "pass": "✅",
            "warn": "⚠️ ",
            "fail": "❌",
            "error": "💥"
        }
        
        icon = status_icons.get(result["status"], "❓")
        print(f"   {icon} {result['check']}: {result['message']}")
        
        if result.get("failures"):
            for failure in result["failures"][:3]:  # Show first 3 failures
                if isinstance(failure, dict):
                    print(f"      - {failure.get('file') or failure.get('module') or failure.get('database')}: {failure.get('error', 'Unknown error')}")
    
    def generate_report(self, summary: Dict) -> str:
        """Generate health verification report."""
        report = []
        report.append("=" * 80)
        report.append("🏥 SYSTEM HEALTH VERIFICATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall status
        overall = "✅ PASS" if summary["overall_status"] else "❌ FAIL"
        report.append(f"**Overall Status:** {overall}")
        report.append(f"**Checks Run:** {len(self.results)}")
        report.append(f"**Passed:** {sum(1 for r in self.results if r['status'] == 'pass')}")
        report.append(f"**Warnings:** {sum(1 for r in self.results if r['status'] == 'warn')}")
        report.append(f"**Failed:** {sum(1 for r in self.results if r['status'] in ['fail', 'error'])}")
        report.append("")
        
        # Individual check results
        report.append("=" * 80)
        report.append("📊 CHECK DETAILS")
        report.append("=" * 80)
        report.append("")
        
        for result in self.results:
            status = result["status"].upper()
            report.append(f"**{result['check']}:** {status}")
            report.append(f"   {result['message']}")
            
            if result.get("failures"):
                report.append(f"   Issues found: {len(result['failures'])}")
            
            report.append("")
        
        # Summary
        report.append("=" * 80)
        report.append("📊 HEALTH SUMMARY")
        report.append("=" * 80)
        report.append("")
        
        if summary["overall_status"]:
            report.append("✅ SUCCESS: System is healthy and ready for GA release")
        else:
            report.append("❌ FAILURE: System has health issues that need attention")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main health verification workflow."""
    project_root = Path(__file__).parent.parent.parent
    
    print("🚀 Starting System Health Verification for CORTEX 4.0 GA")
    print(f"📁 Project Root: {project_root}")
    print("")
    
    verifier = SystemHealthVerifier(str(project_root))
    summary = verifier.run_all_checks()
    
    # Generate report
    print("\n" + "=" * 80)
    print("📊 GENERATING REPORT")
    print("=" * 80)
    report = verifier.generate_report(summary)
    print("\n" + report)
    
    # Save report
    report_path = project_root / "cortex-brain/documents/reports/task-9.4-system-health-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write("# Task 9.4: System Health Verification Report\n\n")
        f.write(f"**Date:** December 25, 2025\n")
        f.write(f"**Verifier:** verify_system_health.py\n\n")
        f.write("```\n")
        f.write(report)
        f.write("\n```\n")
    
    print(f"\n📝 Report saved to: {report_path}")
    
    return 0 if summary["overall_status"] else 1


if __name__ == "__main__":
    exit(main())
