"""
CORTEX Test Coverage Reporter

Advanced coverage reporting with tier-specific analysis:
- Overall project coverage
- Tier-specific coverage (tier0, tier1, tier2, tier3)
- Plugin coverage
- HTML report generation
- Coverage threshold validation

Part of Test Execution Infrastructure
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import sys
import re
import json


class CoverageStatus(Enum):
    """Coverage status levels."""
    EXCELLENT = "excellent"  # >= 90%
    GOOD = "good"            # >= 80%
    ACCEPTABLE = "acceptable"  # >= 70%
    POOR = "poor"            # >= 60%
    CRITICAL = "critical"    # < 60%


@dataclass
class CoverageMetrics:
    """Coverage metrics for a component."""
    component: str
    statements: int
    covered: int
    missing: int
    excluded: int
    percentage: float
    status: CoverageStatus


@dataclass
class CoverageReport:
    """Complete coverage report."""
    overall: CoverageMetrics
    by_tier: Dict[str, CoverageMetrics]
    by_plugin: Dict[str, CoverageMetrics]
    by_file: Dict[str, CoverageMetrics]
    html_report_path: Optional[Path]
    json_data: Optional[Dict]
    threshold_passed: bool
    threshold_value: float


class CoverageReporter:
    """
    Generates and analyzes test coverage reports.
    
    Features:
    - Runs pytest with coverage
    - Generates HTML reports
    - Tier-specific analysis
    - Threshold validation
    - Trend tracking
    """
    
    def __init__(
        self,
        test_root: Optional[Path] = None,
        source_root: Optional[Path] = None,
        threshold: float = 80.0
    ):
        """
        Initialize Coverage Reporter.
        
        Args:
            test_root: Root directory for tests
            source_root: Root directory for source code
            threshold: Minimum acceptable coverage percentage
        """
        if test_root is None or source_root is None:
            project_root = Path(__file__).parent.parent.parent
            test_root = test_root or project_root / "tests"
            source_root = source_root or project_root / "src"
        
        self.test_root = Path(test_root)
        self.source_root = Path(source_root)
        self.threshold = threshold
        self.project_root = self.source_root.parent
        
        # Coverage output paths
        self.coverage_dir = self.project_root / ".coverage_reports"
        self.coverage_dir.mkdir(exist_ok=True)
        
        self.html_dir = self.coverage_dir / "html"
        self.json_path = self.coverage_dir / "coverage.json"
    
    def run_coverage(
        self,
        test_pattern: Optional[str] = None,
        show_missing: bool = True
    ) -> CoverageReport:
        """
        Run tests with coverage analysis.
        
        Args:
            test_pattern: Optional pytest pattern to filter tests
            show_missing: Whether to show missing lines
        
        Returns:
            CoverageReport with results
        """
        print("=" * 70)
        print("CORTEX COVERAGE ANALYSIS")
        print("=" * 70)
        print(f"Test Root: {self.test_root}")
        print(f"Source Root: {self.source_root}")
        print(f"Threshold: {self.threshold}%")
        print()
        
        # Build pytest command with coverage
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_root),
            f"--cov={self.source_root}",
            "--cov-report=html:" + str(self.html_dir),
            "--cov-report=json:" + str(self.json_path),
            "--cov-report=term-missing" if show_missing else "--cov-report=term",
            "-v"
        ]
        
        if test_pattern:
            cmd.extend(["-k", test_pattern])
        
        print("[*] Running tests with coverage...")
        print(f"    Command: {' '.join(cmd[:5])}...")
        print()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            
            # Parse coverage results
            coverage_report = self._parse_coverage_results()
            
            # Display summary
            print()
            print("=" * 70)
            print("COVERAGE SUMMARY")
            print("=" * 70)
            self._print_coverage_summary(coverage_report)
            
            return coverage_report
        
        except subprocess.TimeoutExpired:
            print("[X] Coverage analysis timed out after 10 minutes")
            raise
        except Exception as e:
            print(f"[X] Coverage analysis failed: {e}")
            raise
    
    def _parse_coverage_results(self) -> CoverageReport:
        """Parse coverage results from JSON file."""
        # Load JSON coverage data
        try:
            with open(self.json_path, 'r') as f:
                json_data = json.load(f)
        except Exception as e:
            print(f"[!] Failed to load coverage JSON: {e}")
            json_data = {}
        
        # Parse overall metrics
        totals = json_data.get('totals', {})
        overall = CoverageMetrics(
            component="overall",
            statements=totals.get('num_statements', 0),
            covered=totals.get('covered_lines', 0),
            missing=totals.get('missing_lines', 0),
            excluded=totals.get('excluded_lines', 0),
            percentage=totals.get('percent_covered', 0.0),
            status=self._determine_status(totals.get('percent_covered', 0.0))
        )
        
        # Parse by-file metrics
        files = json_data.get('files', {})
        by_file = {}
        for file_path, file_data in files.items():
            summary = file_data.get('summary', {})
            by_file[file_path] = CoverageMetrics(
                component=file_path,
                statements=summary.get('num_statements', 0),
                covered=summary.get('covered_lines', 0),
                missing=summary.get('missing_lines', 0),
                excluded=summary.get('excluded_lines', 0),
                percentage=summary.get('percent_covered', 0.0),
                status=self._determine_status(summary.get('percent_covered', 0.0))
            )
        
        # Aggregate by tier
        by_tier = self._aggregate_by_tier(by_file)
        
        # Aggregate by plugin
        by_plugin = self._aggregate_by_plugin(by_file)
        
        # Check threshold
        threshold_passed = overall.percentage >= self.threshold
        
        return CoverageReport(
            overall=overall,
            by_tier=by_tier,
            by_plugin=by_plugin,
            by_file=by_file,
            html_report_path=self.html_dir / "index.html",
            json_data=json_data,
            threshold_passed=threshold_passed,
            threshold_value=self.threshold
        )
    
    def _aggregate_by_tier(self, by_file: Dict[str, CoverageMetrics]) -> Dict[str, CoverageMetrics]:
        """Aggregate coverage by tier."""
        tier_data = {
            "tier0": {"statements": 0, "covered": 0, "missing": 0},
            "tier1": {"statements": 0, "covered": 0, "missing": 0},
            "tier2": {"statements": 0, "covered": 0, "missing": 0},
            "tier3": {"statements": 0, "covered": 0, "missing": 0},
            "other": {"statements": 0, "covered": 0, "missing": 0}
        }
        
        for file_path, metrics in by_file.items():
            # Normalize path
            file_path_normalized = file_path.replace('\\', '/')
            
            # Detect tier
            if '/tier0/' in file_path_normalized:
                tier = "tier0"
            elif '/tier1/' in file_path_normalized:
                tier = "tier1"
            elif '/tier2/' in file_path_normalized:
                tier = "tier2"
            elif '/tier3/' in file_path_normalized:
                tier = "tier3"
            else:
                tier = "other"
            
            # Accumulate
            tier_data[tier]["statements"] += metrics.statements
            tier_data[tier]["covered"] += metrics.covered
            tier_data[tier]["missing"] += metrics.missing
        
        # Convert to CoverageMetrics
        by_tier = {}
        for tier, data in tier_data.items():
            if data["statements"] > 0:
                percentage = (data["covered"] / data["statements"]) * 100
            else:
                percentage = 0.0
            
            by_tier[tier] = CoverageMetrics(
                component=tier,
                statements=data["statements"],
                covered=data["covered"],
                missing=data["missing"],
                excluded=0,
                percentage=percentage,
                status=self._determine_status(percentage)
            )
        
        return by_tier
    
    def _aggregate_by_plugin(self, by_file: Dict[str, CoverageMetrics]) -> Dict[str, CoverageMetrics]:
        """Aggregate coverage by plugin."""
        plugin_data = {}
        
        for file_path, metrics in by_file.items():
            file_path_normalized = file_path.replace('\\', '/')
            
            # Detect plugin
            if '/plugins/' in file_path_normalized:
                # Extract plugin name
                match = re.search(r'/plugins/([^/]+)', file_path_normalized)
                if match:
                    plugin_name = match.group(1)
                    if plugin_name not in plugin_data:
                        plugin_data[plugin_name] = {"statements": 0, "covered": 0, "missing": 0}
                    
                    plugin_data[plugin_name]["statements"] += metrics.statements
                    plugin_data[plugin_name]["covered"] += metrics.covered
                    plugin_data[plugin_name]["missing"] += metrics.missing
        
        # Convert to CoverageMetrics
        by_plugin = {}
        for plugin_name, data in plugin_data.items():
            if data["statements"] > 0:
                percentage = (data["covered"] / data["statements"]) * 100
            else:
                percentage = 0.0
            
            by_plugin[plugin_name] = CoverageMetrics(
                component=plugin_name,
                statements=data["statements"],
                covered=data["covered"],
                missing=data["missing"],
                excluded=0,
                percentage=percentage,
                status=self._determine_status(percentage)
            )
        
        return by_plugin
    
    def _determine_status(self, percentage: float) -> CoverageStatus:
        """Determine coverage status from percentage."""
        if percentage >= 90:
            return CoverageStatus.EXCELLENT
        elif percentage >= 80:
            return CoverageStatus.GOOD
        elif percentage >= 70:
            return CoverageStatus.ACCEPTABLE
        elif percentage >= 60:
            return CoverageStatus.POOR
        else:
            return CoverageStatus.CRITICAL
    
    def _print_coverage_summary(self, report: CoverageReport):
        """Print coverage summary to console."""
        # Overall
        status_icon = self._get_status_icon(report.overall.status)
        print(f"{status_icon} OVERALL: {report.overall.percentage:.1f}% coverage")
        print(f"   Statements: {report.overall.statements}")
        print(f"   Covered: {report.overall.covered}")
        print(f"   Missing: {report.overall.missing}")
        print()
        
        # Threshold check
        if report.threshold_passed:
            print(f"✅ Threshold PASSED: {report.overall.percentage:.1f}% >= {report.threshold_value}%")
        else:
            print(f"❌ Threshold FAILED: {report.overall.percentage:.1f}% < {report.threshold_value}%")
        print()
        
        # By tier
        if report.by_tier:
            print("COVERAGE BY TIER:")
            print("-" * 70)
            for tier in ["tier0", "tier1", "tier2", "tier3", "other"]:
                if tier in report.by_tier:
                    metrics = report.by_tier[tier]
                    icon = self._get_status_icon(metrics.status)
                    bar = "█" * int(metrics.percentage / 2)
                    print(f"  {icon} {tier:10s} {metrics.percentage:5.1f}% {bar}")
            print()
        
        # By plugin
        if report.by_plugin:
            print("COVERAGE BY PLUGIN:")
            print("-" * 70)
            for plugin_name, metrics in sorted(report.by_plugin.items(), key=lambda x: -x[1].percentage):
                icon = self._get_status_icon(metrics.status)
                bar = "█" * int(metrics.percentage / 2)
                print(f"  {icon} {plugin_name:20s} {metrics.percentage:5.1f}% {bar}")
            print()
        
        # HTML report
        if report.html_report_path and report.html_report_path.exists():
            print(f"📄 HTML Report: {report.html_report_path}")
            print()
    
    def _get_status_icon(self, status: CoverageStatus) -> str:
        """Get icon for coverage status."""
        icons = {
            CoverageStatus.EXCELLENT: "🟢",
            CoverageStatus.GOOD: "🟢",
            CoverageStatus.ACCEPTABLE: "🟡",
            CoverageStatus.POOR: "🟠",
            CoverageStatus.CRITICAL: "🔴"
        }
        return icons.get(status, "⚪")
    
    def generate_markdown_report(self, report: CoverageReport) -> str:
        """Generate markdown-formatted coverage report."""
        md = []
        md.append("# CORTEX Test Coverage Report")
        md.append("")
        md.append(f"**Overall Coverage:** {report.overall.percentage:.1f}%")
        md.append(f"**Threshold:** {report.threshold_value}%")
        md.append(f"**Status:** {'✅ PASSED' if report.threshold_passed else '❌ FAILED'}")
        md.append("")
        
        # Overall metrics
        md.append("## Overall Metrics")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Statements | {report.overall.statements} |")
        md.append(f"| Covered | {report.overall.covered} |")
        md.append(f"| Missing | {report.overall.missing} |")
        md.append(f"| Coverage | {report.overall.percentage:.1f}% |")
        md.append("")
        
        # By tier
        if report.by_tier:
            md.append("## Coverage by Tier")
            md.append("")
            md.append("| Tier | Statements | Covered | Coverage |")
            md.append("|------|------------|---------|----------|")
            for tier in ["tier0", "tier1", "tier2", "tier3", "other"]:
                if tier in report.by_tier:
                    m = report.by_tier[tier]
                    md.append(f"| {tier} | {m.statements} | {m.covered} | {m.percentage:.1f}% |")
            md.append("")
        
        # By plugin
        if report.by_plugin:
            md.append("## Coverage by Plugin")
            md.append("")
            md.append("| Plugin | Statements | Covered | Coverage |")
            md.append("|--------|------------|---------|----------|")
            for plugin_name, m in sorted(report.by_plugin.items(), key=lambda x: -x[1].percentage):
                md.append(f"| {plugin_name} | {m.statements} | {m.covered} | {m.percentage:.1f}% |")
            md.append("")
        
        return "\n".join(md)


def run_coverage_analysis(
    test_pattern: Optional[str] = None,
    threshold: float = 80.0
) -> bool:
    """
    Convenience function to run coverage analysis.
    
    Args:
        test_pattern: Optional pytest pattern to filter tests
        threshold: Minimum acceptable coverage percentage
    
    Returns:
        True if threshold passed
    """
    reporter = CoverageReporter(threshold=threshold)
    report = reporter.run_coverage(test_pattern=test_pattern)
    return report.threshold_passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CORTEX coverage analysis")
    parser.add_argument("-k", "--pattern", help="Test pattern to filter")
    parser.add_argument("--threshold", type=float, default=80.0, help="Coverage threshold")
    args = parser.parse_args()
    
    passed = run_coverage_analysis(test_pattern=args.pattern, threshold=args.threshold)
    sys.exit(0 if passed else 1)
