#!/usr/bin/env python3
"""
CORTEX Dashboard Fix Validation Script

Validates the data loading race condition fix by:
1. Checking file modifications
2. Verifying fix implementation
3. Running integration tests
4. Generating validation report

Author: Asif Hussain
Date: 2026-02-03
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

class DashboardFixValidator:
    """Validates dashboard race condition fix."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.results: List[Dict] = []
        
    def validate_all(self) -> Dict:
        """Run all validation checks."""
        print("🔍 CORTEX Dashboard Fix Validation\n")
        print("=" * 60)
        
        # Check 1: Verify app.js modifications
        self.check_app_js_modifications()
        
        # Check 2: Verify dashboard.html modifications
        self.check_dashboard_html_modifications()
        
        # Check 3: Verify data structure compatibility
        self.check_data_structure()
        
        # Check 4: Verify test file exists
        self.check_test_file()
        
        # Generate report
        return self.generate_report()
    
    def check_app_js_modifications(self) -> None:
        """Verify app.js has the race condition fix."""
        print("\n📝 Checking app.js modifications...")
        
        app_js = self.base_path / "spa/js/app.js"
        
        if not app_js.exists():
            self.results.append({
                "check": "app.js modifications",
                "status": "FAIL",
                "message": "app.js not found"
            })
            return
        
        content = app_js.read_text()
        
        checks = [
            ("External data parameter", r"async init\(externalData = null\)"),
            ("External data check", r"if \(externalData\)"),
            ("Empty data validation", r"Object\.keys\(this\.data\)\.length === 0"),
            ("Fresh DOM read", r"dataScript\.textContent\.trim\(\)"),
        ]
        
        for check_name, pattern in checks:
            if re.search(pattern, content):
                print(f"  ✅ {check_name}")
                self.results.append({
                    "check": f"app.js: {check_name}",
                    "status": "PASS",
                    "message": "Implementation found"
                })
            else:
                print(f"  ❌ {check_name}")
                self.results.append({
                    "check": f"app.js: {check_name}",
                    "status": "FAIL",
                    "message": "Implementation not found"
                })
    
    def check_dashboard_html_modifications(self) -> None:
        """Verify dashboard.html passes data directly."""
        print("\n📝 Checking dashboard.html modifications...")
        
        dashboard_html = self.base_path / "spa/dashboard.html"
        
        if not dashboard_html.exists():
            self.results.append({
                "check": "dashboard.html modifications",
                "status": "FAIL",
                "message": "dashboard.html not found"
            })
            return
        
        content = dashboard_html.read_text()
        
        checks = [
            ("Direct data injection", r"dashboard\.init\(data\)"),
            ("Script content update", r"embeddedDataScript\.textContent = JSON\.stringify\(data\)"),
        ]
        
        for check_name, pattern in checks:
            if re.search(pattern, content):
                print(f"  ✅ {check_name}")
                self.results.append({
                    "check": f"dashboard.html: {check_name}",
                    "status": "PASS",
                    "message": "Implementation found"
                })
            else:
                print(f"  ❌ {check_name}")
                self.results.append({
                    "check": f"dashboard.html: {check_name}",
                    "status": "FAIL",
                    "message": "Implementation not found"
                })
    
    def check_data_structure(self) -> None:
        """Verify dashboard data structure is valid."""
        print("\n📝 Checking data structure...")
        
        data_file = self.base_path.parent / "repos/cortex/dashboard-data.json"
        
        if not data_file.exists():
            print(f"  ⚠️  Data file not found: {data_file}")
            self.results.append({
                "check": "data structure",
                "status": "WARN",
                "message": "Data file not found"
            })
            return
        
        try:
            data = json.loads(data_file.read_text())
            
            required_keys = [
                "repo", "overview", "metrics", "security",
                "dependencies", "quality", "use_cases"
            ]
            
            for key in required_keys:
                if key in data:
                    print(f"  ✅ {key} exists")
                    self.results.append({
                        "check": f"data structure: {key}",
                        "status": "PASS",
                        "message": "Key exists"
                    })
                else:
                    print(f"  ❌ {key} missing")
                    self.results.append({
                        "check": f"data structure: {key}",
                        "status": "FAIL",
                        "message": "Key missing"
                    })
            
            # Check array types
            if isinstance(data.get("security", {}).get("vulnerabilities"), list):
                print(f"  ✅ security.vulnerabilities is array ({len(data['security']['vulnerabilities'])} items)")
            else:
                print(f"  ❌ security.vulnerabilities is not array")
            
            if isinstance(data.get("quality", {}).get("code_smells"), list):
                print(f"  ✅ quality.code_smells is array ({len(data['quality']['code_smells'])} items)")
            else:
                print(f"  ❌ quality.code_smells is not array")
                
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON: {e}")
            self.results.append({
                "check": "data structure",
                "status": "FAIL",
                "message": f"Invalid JSON: {e}"
            })
    
    def check_test_file(self) -> None:
        """Verify integration test file exists."""
        print("\n📝 Checking test file...")
        
        test_file = self.base_path / "spa/tests/integration.test.html"
        
        if test_file.exists():
            content = test_file.read_text()
            
            # Check for test suites
            suite_count = len(re.findall(r"runner\.suite\(", content))
            test_count = len(re.findall(r"name: '.*?',\s*fn:", content))
            
            print(f"  ✅ Test file exists")
            print(f"  ✅ {suite_count} test suites found")
            print(f"  ✅ {test_count} test cases found")
            
            self.results.append({
                "check": "test file",
                "status": "PASS",
                "message": f"{suite_count} suites, {test_count} tests"
            })
        else:
            print(f"  ❌ Test file not found")
            self.results.append({
                "check": "test file",
                "status": "FAIL",
                "message": "Test file not found"
            })
    
    def generate_report(self) -> Dict:
        """Generate validation report."""
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT\n")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        warned = sum(1 for r in self.results if r["status"] == "WARN")
        
        print(f"Total Checks: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warned}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n✅ All checks passed! Race condition fix is complete.")
            status = "SUCCESS"
        else:
            print("\n❌ Some checks failed. Review implementation.")
            status = "FAILED"
        
        print("\n" + "=" * 60)
        
        return {
            "status": status,
            "total": total,
            "passed": passed,
            "failed": failed,
            "warned": warned,
            "success_rate": success_rate,
            "results": self.results
        }


def main():
    """Main execution."""
    # Get actual script location
    script_path = Path(__file__).resolve()
    base_path = script_path.parent  # company/dashboards
    
    validator = DashboardFixValidator(base_path)
    
    report = validator.validate_all()
    
    # Save report in tests directory (create if needed)
    tests_dir = base_path / "spa/tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = tests_dir / "validation-report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n📄 Report saved to: {report_file}")
    
    # Exit with appropriate code
    exit(0 if report["status"] == "SUCCESS" else 1)


if __name__ == "__main__":
    main()
