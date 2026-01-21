#!/usr/bin/env python3
"""Test Analytics Dashboard - Comprehensive test suite analysis and reporting.

Tracks test performance, hanging patterns, and provides analytics for test suites.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import re


class TestAnalyticsDashboard:
    """Analytics dashboard for test suite performance."""
    
    def __init__(self, workspace_root: Path = None):
        """Initialize analytics dashboard.
        
        Args:
            workspace_root: Root path of workspace (default: current directory)
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.analytics_dir = self.workspace_root / "_workspaces" / "roadmap" / "analytics"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_test_suite(self, test_path: str) -> Dict[str, Any]:
        """Analyze a test suite for metrics and issues.
        
        Args:
            test_path: Path to test suite
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\n{'='*70}")
        print(f"ANALYZING TEST SUITE: {test_path}")
        print(f"{'='*70}\n")
        
        # Collection phase
        print("[1/4] Collecting tests...")
        collection_result = self._collect_tests(test_path)
        
        # Execution phase
        print("[2/4] Running tests with progress monitoring...")
        execution_result = self._execute_tests(test_path)
        
        # Analysis phase
        print("[3/4] Analyzing results...")
        analysis = self._analyze_results(collection_result, execution_result)
        
        # Reporting phase
        print("[4/4] Generating report...")
        report = self._generate_report(test_path, analysis)
        
        # Save analytics
        self._save_analytics(test_path, report)
        
        # Print summary
        self._print_summary(report)
        
        return report
        
    def _collect_tests(self, test_path: str) -> Dict[str, Any]:
        """Collect tests from path."""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", test_path, "--collect-only", "-q"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            
            # Parse collection info
            match = re.search(r'collected (\d+)', output)
            total = int(match.group(1)) if match else 0
            
            # Find errors
            errors = output.count("ERROR")
            
            return {
                "total_tests": total,
                "collection_errors": errors,
                "output": output,
            }
        except Exception as e:
            return {"total_tests": 0, "collection_errors": 1, "error": str(e)}
            
    def _execute_tests(self, test_path: str) -> Dict[str, Any]:
        """Execute tests with progress tracking."""
        try:
            # Run with progress tracking
            result = subprocess.run(
                ["python3", "-m", "pytest", test_path, "-q", "--tb=no"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = result.stdout + result.stderr
            
            # Parse results
            passed = failed = errors = skipped = 0
            
            for line in output.split('\n'):
                if 'passed' in line.lower():
                    match = re.search(r'(\d+)\s+passed', line)
                    if match:
                        passed = int(match.group(1))
                        
                if 'failed' in line.lower():
                    match = re.search(r'(\d+)\s+failed', line)
                    if match:
                        failed = int(match.group(1))
                        
                if 'error' in line.lower():
                    match = re.search(r'(\d+)\s+error', line)
                    if match:
                        errors = int(match.group(1))
                        
                if 'skipped' in line.lower():
                    match = re.search(r'(\d+)\s+skipped', line)
                    if match:
                        skipped = int(match.group(1))
            
            return {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "exit_code": result.returncode,
                "output": output,
            }
        except subprocess.TimeoutExpired:
            return {"error": "Test execution timeout (hanging detected)", "timeout": True}
        except Exception as e:
            return {"error": str(e)}
            
    def _analyze_results(self, collection: Dict[str, Any], execution: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results."""
        total_run = execution.get("passed", 0) + execution.get("failed", 0) + execution.get("errors", 0)
        total_collected = collection.get("total_tests", 0)
        
        pass_rate = (execution.get("passed", 0) / total_run * 100) if total_run > 0 else 0
        
        # Calculate health score
        health_score = 100
        if execution.get("timeout"):
            health_score -= 50
        if collection.get("collection_errors", 0) > 0:
            health_score -= 25
        if execution.get("failed", 0) > 0:
            health_score -= min(25, execution.get("failed", 0))
        if execution.get("errors", 0) > 0:
            health_score -= min(25, execution.get("errors", 0))
            
        health_score = max(0, health_score)
        
        return {
            "total_collected": total_collected,
            "total_run": total_run,
            "passed": execution.get("passed", 0),
            "failed": execution.get("failed", 0),
            "errors": execution.get("errors", 0),
            "skipped": execution.get("skipped", 0),
            "pass_rate": pass_rate,
            "collection_errors": collection.get("collection_errors", 0),
            "hanging_detected": execution.get("timeout", False),
            "health_score": health_score,
        }
        
    def _generate_report(self, test_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "test_path": test_path,
            "analysis": analysis,
            "metrics": {
                "collection": {
                    "total": analysis["total_collected"],
                    "errors": analysis["collection_errors"],
                },
                "execution": {
                    "total_run": analysis["total_run"],
                    "passed": analysis["passed"],
                    "failed": analysis["failed"],
                    "errors": analysis["errors"],
                    "skipped": analysis["skipped"],
                },
                "quality": {
                    "pass_rate": analysis["pass_rate"],
                    "health_score": analysis["health_score"],
                    "hanging_detected": analysis["hanging_detected"],
                },
            }
        }
        
    def _save_analytics(self, test_path: str, report: Dict[str, Any]) -> None:
        """Save analytics to file."""
        safe_path = test_path.replace("/", "_").replace(".", "_")
        report_file = self.analytics_dir / f"{safe_path}_report.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"✓ Saved analytics to: {report_file}")
        
    def _print_summary(self, report: Dict[str, Any]) -> None:
        """Print summary of results."""
        analysis = report["analysis"]
        metrics = report["metrics"]
        
        print(f"\n{'='*70}")
        print("TEST ANALYTICS SUMMARY")
        print(f"{'='*70}")
        
        print(f"\nCollection Phase:")
        print(f"  Total Collected:    {metrics['collection']['total']}")
        print(f"  Collection Errors:  {metrics['collection']['errors']}")
        
        print(f"\nExecution Phase:")
        print(f"  Total Run:          {metrics['execution']['total_run']}")
        print(f"  ✓ Passed:           {metrics['execution']['passed']}")
        print(f"  ✗ Failed:           {metrics['execution']['failed']}")
        print(f"  ⚠ Errors:           {metrics['execution']['errors']}")
        print(f"  - Skipped:          {metrics['execution']['skipped']}")
        
        print(f"\nQuality Metrics:")
        print(f"  Pass Rate:          {analysis['pass_rate']:.1f}%")
        print(f"  Health Score:       {analysis['health_score']}/100")
        if analysis["hanging_detected"]:
            print(f"  Hanging Detected:   ✓ YES (CRITICAL)")
        
        print(f"\n{'='*70}\n")


def main() -> int:
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: test-analytics.py <test_path> [test_path2] ...")
        print("Example: test-analytics.py tests/unit/core tests/unit/infrastructure")
        return 1
    
    dashboard = TestAnalyticsDashboard()
    
    for test_path in sys.argv[1:]:
        dashboard.analyze_test_suite(test_path)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
