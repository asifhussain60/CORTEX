"""
Dashboard Data Collection Validator

Validates collected data files against configured benchmarks to ensure
comprehensive analysis was performed.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

from src.dashboard_config import get_config

logger = logging.getLogger(__name__)


class CollectionValidator:
    """
    Validates data collection against file size benchmarks.

    Ensures that "deep analysis" collectors actually produce comprehensive data
    by checking file sizes against configured minimums and targets.
    """

    def __init__(self):
        """Initialize validator with config"""
        self.config = get_config()
        self.collector_config = self.config.get_collector_config()
        self.benchmarks = self.collector_config.benchmarks if hasattr(
            self.collector_config, 'benchmarks') else {}

    def validate_collection(self, repo_path: Path) -> Dict[str, Any]:
        """
        Validate all collected data files against benchmarks.

        Args:
            repo_path: Path to repository data directory

        Returns:
            {
                "success": bool,
                "files_checked": int,
                "passed": int,
                "failed": int,
                "warnings": List[str],
                "details": {...}
            }
        """
        results = {
            "success": True,
            "files_checked": 0,
            "passed": 0,
            "failed": 0,
            "warnings": [],
            "details": {}
        }

        if not self.benchmarks:
            logger.warning("No benchmarks configured, skipping validation")
            results["warnings"].append("No benchmarks configured")
            return results

        for file_type, benchmark in self.benchmarks.items():
            file_path = repo_path / f"{file_type}.json"

            if not file_path.exists():
                results["failed"] += 1
                results["warnings"].append(f"Missing: {file_type}.json")
                results["success"] = False
                continue

            file_size = file_path.stat().st_size
            results["files_checked"] += 1

            # Check against benchmark
            status, message = self._check_file_size(
                file_size,
                benchmark["min_size"],
                benchmark["target_size"],
                benchmark["max_variance"]
            )

            results["details"][file_type] = {
                "size": file_size,
                "min_expected": benchmark["min_size"],
                "target": benchmark["target_size"],
                "status": status,
                "percentage_of_target": round((file_size / benchmark["target_size"]) * 100, 1),
                "message": message
            }

            if status == "passed":
                results["passed"] += 1
            elif status == "warning":
                results["warnings"].append(message)
                results["passed"] += 1  # Warning, not failure
            else:  # failed
                results["failed"] += 1
                results["warnings"].append(message)
                results["success"] = False

        return results

    def _check_file_size(
        self,
        actual: int,
        min_size: int,
        target: int,
        variance: float
    ) -> tuple[str, str]:
        """
        Check file size against benchmarks.

        Args:
            actual: Actual file size in bytes
            min_size: Minimum acceptable size
            target: Target size
            variance: Acceptable variance as percentage (0.3 = 30%)

        Returns:
            (status, message) tuple where status is 'passed', 'warning', or 'failed'
        """
        file_kb = actual / 1024
        target_kb = target / 1024
        min_kb = min_size / 1024

        if actual < min_size:
            return (
                "failed",
                f"Size {file_kb:.1f}KB below minimum {min_kb:.1f}KB (shallow analysis detected)"
            )
        elif actual < target:
            pct = (actual / target) * 100
            return (
                "warning",
                f"Size {file_kb:.1f}KB below target {target_kb:.1f}KB ({pct:.0f}% of target)"
            )
        elif actual > target * (1 + variance):
            pct = ((actual - target) / target) * 100
            return (
                "warning",
                f"Size {file_kb:.1f}KB exceeds target by {pct:.0f}% (unexpectedly large)"
            )
        else:
            return (
                "passed",
                f"Size {file_kb:.1f}KB within target range"
            )

    def format_validation_summary(self, validation: Dict[str, Any]) -> str:
        """
        Format validation results as human-readable summary.

        Args:
            validation: Validation results dictionary

        Returns:
            Formatted summary string
        """
        if not validation["files_checked"]:
            return "⚠️  No files validated (no benchmarks configured)"

        if validation["success"]:
            return (
                f"✅ Validation PASSED: {
                    validation['passed']}/{
                    validation['files_checked']} files meet standards"
            )
        else:
            summary = f"❌ Validation FAILED: {validation['failed']} files below minimum\n"
            for warning in validation["warnings"]:
                summary += f"  • {warning}\n"
            return summary.rstrip()

    def get_detailed_report(self, validation: Dict[str, Any]) -> str:
        """
        Get detailed validation report with per-file breakdown.

        Args:
            validation: Validation results dictionary

        Returns:
            Detailed report string
        """
        if not validation["details"]:
            return "No validation details available"

        report = "File Size Validation Report\n"
        report += "=" * 70 + "\n\n"

        for file_type, details in validation["details"].items():
            status_icon = {
                "passed": "✅",
                "warning": "⚠️ ",
                "failed": "❌"
            }.get(details["status"], "❓")

            report += f"{status_icon} {file_type}.json\n"
            report += f"   Size: {details['size']:,} bytes ({details['size'] / 1024:.1f} KB)\n"
            report += f"   Target: {
                details['target']:,} bytes ({
                details['target'] / 1024:.1f} KB)\n"
            report += f"   Progress: {details['percentage_of_target']}% of target\n"
            report += f"   Status: {details['message']}\n\n"

        report += "=" * 70 + "\n"
        report += f"Summary: {validation['passed']} passed, {validation['failed']} failed\n"

        return report


__all__ = ['CollectionValidator']
