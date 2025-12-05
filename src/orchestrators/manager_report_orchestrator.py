"""
Manager Report Orchestrator

Generates comprehensive manager-level reports for CORTEX development metrics.
Provides velocity, coverage, productivity, and quality insights for team oversight.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tier3.context_intelligence import ContextIntelligence
from tier3.coverage_tracker import CoverageTracker


class ManagerReportOrchestrator:
    """
    Orchestrates generation of manager-level performance reports.
    
    Combines velocity metrics, test coverage, code quality, and productivity
    insights into executive-friendly markdown reports.
    """
    
    def __init__(self, cortex_root: Path):
        """
        Initialize manager report orchestrator.
        
        Args:
            cortex_root: Root directory of CORTEX installation
        """
        self.cortex_root = Path(cortex_root)
        self.brain_path = self.cortex_root / "cortex-brain"
        self.tier3_db = self.brain_path / "tier3" / "development_context.db"
        
        self.context_intelligence = ContextIntelligence(db_path=self.tier3_db)
        self.coverage_tracker = CoverageTracker(db_path=self.tier3_db)
    
    def generate_report(
        self,
        period: str = "weekly",
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive manager report.
        
        Args:
            period: Report period ("weekly", "monthly", "quarterly")
            output_path: Optional custom output path
            
        Returns:
            Dict with success, report_path, metrics summary
        """
        # Determine report timeframe
        days = self._get_days_for_period(period)
        
        # Collect metrics
        velocity_data = self.context_intelligence.calculate_task_velocity(days=days, group_by="week")
        git_metrics = self.context_intelligence.collect_git_metrics(days=days)
        coverage_trends = self.coverage_tracker.get_coverage_trends(days=days)
        file_hotspots = self.context_intelligence.analyze_file_hotspots(days=days)
        insights = self.context_intelligence.generate_insights()
        
        # Calculate summary statistics
        summary = self._calculate_summary(
            velocity_data=velocity_data,
            git_metrics=git_metrics,
            coverage_trends=coverage_trends,
            file_hotspots=file_hotspots,
            insights=insights
        )
        
        # Generate markdown report
        report_content = self._format_report(
            period=period,
            days=days,
            summary=summary,
            velocity_data=velocity_data,
            git_metrics=git_metrics,
            coverage_trends=coverage_trends,
            file_hotspots=file_hotspots,
            insights=insights
        )
        
        # Write report to file
        if output_path is None:
            reports_dir = self.brain_path / "documents" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_path = reports_dir / f"manager-report-{period}-{timestamp}.md"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content, encoding='utf-8')
        
        return {
            "success": True,
            "report_path": str(output_path),
            "period": period,
            "days_covered": days,
            "summary": summary
        }
    
    def _get_days_for_period(self, period: str) -> int:
        """Get number of days for report period."""
        period_map = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "quarterly": 90
        }
        return period_map.get(period.lower(), 7)
    
    def _calculate_summary(
        self,
        velocity_data: List[Dict[str, Any]],
        git_metrics: List,
        coverage_trends: List[Dict[str, Any]],
        file_hotspots: List,
        insights: List
    ) -> Dict[str, Any]:
        """Calculate summary statistics for report."""
        summary = {
            "tasks_completed": 0,
            "avg_task_duration_hours": 0.0,
            "total_commits": 0,
            "total_lines_changed": 0,
            "current_coverage": 0.0,
            "coverage_trend": "stable",
            "critical_hotspots": 0,
            "critical_insights": 0
        }
        
        # Task velocity
        if velocity_data:
            summary["tasks_completed"] = sum(v["tasks_completed"] for v in velocity_data)
            total_duration = sum(v["total_duration"] for v in velocity_data)
            if summary["tasks_completed"] > 0:
                summary["avg_task_duration_hours"] = (total_duration / summary["tasks_completed"]) / 3600
        
        # Git activity
        if git_metrics:
            summary["total_commits"] = sum(m.commits_count for m in git_metrics)
            summary["total_lines_changed"] = sum(m.lines_added + m.lines_deleted for m in git_metrics)
        
        # Coverage
        if coverage_trends:
            summary["current_coverage"] = coverage_trends[0]["coverage_percentage"]
            
            # Determine coverage trend
            if len(coverage_trends) >= 2:
                recent = coverage_trends[0]["coverage_percentage"]
                previous = coverage_trends[-1]["coverage_percentage"]
                diff = recent - previous
                
                if diff > 2:
                    summary["coverage_trend"] = "improving"
                elif diff < -2:
                    summary["coverage_trend"] = "declining"
                else:
                    summary["coverage_trend"] = "stable"
        
        # Hotspots
        if file_hotspots:
            from tier3.context_intelligence import Stability
            summary["critical_hotspots"] = sum(
                1 for h in file_hotspots if h.stability == Stability.UNSTABLE
            )
        
        # Insights
        if insights:
            from tier3.context_intelligence import Severity
            summary["critical_insights"] = sum(
                1 for i in insights if i.severity in [Severity.CRITICAL, Severity.ERROR]
            )
        
        return summary
    
    def _format_report(
        self,
        period: str,
        days: int,
        summary: Dict[str, Any],
        velocity_data: List[Dict[str, Any]],
        git_metrics: List,
        coverage_trends: List[Dict[str, Any]],
        file_hotspots: List,
        insights: List
    ) -> str:
        """Format report as markdown."""
        report = []
        
        # Header
        report.append("# 📊 CORTEX Manager Report")
        report.append(f"\n**Report Period:** {period.capitalize()}")
        report.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        report.append(f"**Coverage:** Last {days} days")
        report.append("\n---\n")
        
        # Executive Summary
        report.append("## 🎯 Executive Summary\n")
        report.append(f"- **Tasks Completed:** {summary['tasks_completed']}")
        report.append(f"- **Average Task Duration:** {summary['avg_task_duration_hours']:.1f} hours")
        report.append(f"- **Total Commits:** {summary['total_commits']}")
        report.append(f"- **Lines Changed:** {summary['total_lines_changed']:,}")
        report.append(f"- **Test Coverage:** {summary['current_coverage']:.1f}% ({summary['coverage_trend']})")
        report.append(f"- **Critical Hotspots:** {summary['critical_hotspots']}")
        report.append(f"- **Action Items:** {summary['critical_insights']}")
        report.append("\n")
        
        # Velocity Trends
        report.append("## 🚀 Task Velocity\n")
        if velocity_data:
            report.append("| Period | Tasks | Avg Duration | Cycles | RED → GREEN | GREEN → REFACTOR |")
            report.append("|--------|-------|--------------|--------|-------------|------------------|")
            
            for v in velocity_data:
                period_str = v["period"]
                tasks = v["tasks_completed"]
                avg_hrs = v["avg_duration"] / 3600 if v["avg_duration"] > 0 else 0
                cycles = v["total_cycles"]
                red_time = self._format_duration(v["avg_red_time"])
                green_time = self._format_duration(v["avg_green_time"])
                
                report.append(
                    f"| {period_str} | {tasks} | {avg_hrs:.1f}h | {cycles} | {red_time} | {green_time} |"
                )
            report.append("\n")
        else:
            report.append("*No task velocity data available for this period.*\n\n")
        
        # Test Coverage
        report.append("## 🧪 Test Coverage Trends\n")
        if coverage_trends:
            report.append("| Date | Coverage | Total Tests | Pass Rate |")
            report.append("|------|----------|-------------|-----------|")
            
            for c in coverage_trends[:10]:  # Show last 10 runs
                date_str = c["timestamp"][:10]
                coverage = c["coverage_percentage"]
                total = c["total_tests"]
                pass_rate = (c["passed_tests"] / total * 100) if total > 0 else 0
                
                report.append(
                    f"| {date_str} | {coverage:.1f}% | {total} | {pass_rate:.1f}% |"
                )
            report.append("\n")
        else:
            report.append("*No coverage data available for this period.*\n\n")
        
        # File Hotspots
        report.append("## 🔥 Code Hotspots\n")
        if file_hotspots:
            report.append("| File | Stability | Churn Rate | Edits |")
            report.append("|------|-----------|------------|-------|")
            
            for h in file_hotspots[:15]:  # Top 15 hotspots
                file_name = Path(h.file_path).name
                stability = h.stability.value
                churn = f"{h.churn_rate * 100:.1f}%"
                edits = h.file_edits
                
                stability_icon = "🔴" if stability == "UNSTABLE" else "🟡" if stability == "MODERATE" else "🟢"
                
                report.append(
                    f"| {file_name} | {stability_icon} {stability} | {churn} | {edits} |"
                )
            report.append("\n")
        else:
            report.append("*No file hotspots detected for this period.*\n\n")
        
        # Insights & Action Items
        report.append("## ⚠️ Insights & Recommendations\n")
        if insights:
            for i in insights:
                severity_icon = {
                    "CRITICAL": "🔴",
                    "ERROR": "🟠",
                    "WARNING": "🟡",
                    "INFO": "ℹ️"
                }.get(i.severity.value, "ℹ️")
                
                report.append(f"### {severity_icon} {i.insight_type.value.replace('_', ' ').title()}\n")
                report.append(f"**Message:** {i.message}\n")
                
                if i.recommendation:
                    report.append(f"**Recommendation:** {i.recommendation}\n")
                
                report.append("\n")
        else:
            report.append("*No critical insights at this time. System is healthy.*\n\n")
        
        # Footer
        report.append("---\n")
        report.append(f"\n*Generated by CORTEX Manager Report System*")
        report.append(f"\n*Report Path: `cortex-brain/documents/reports/`*")
        
        return "\n".join(report)
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds == 0:
            return "N/A"
        
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds / 60:.1f}m"
        else:
            return f"{seconds / 3600:.1f}h"


def main():
    """CLI entry point for manager reports."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate CORTEX manager reports")
    parser.add_argument(
        "--period",
        choices=["daily", "weekly", "monthly", "quarterly"],
        default="weekly",
        help="Report period"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Custom output path"
    )
    
    args = parser.parse_args()
    
    # Detect CORTEX root
    cortex_root = Path(__file__).parent.parent.parent
    
    orchestrator = ManagerReportOrchestrator(cortex_root=cortex_root)
    result = orchestrator.generate_report(
        period=args.period,
        output_path=Path(args.output) if args.output else None
    )
    
    if result["success"]:
        print(f"✅ Manager report generated successfully")
        print(f"📄 Report: {result['report_path']}")
        print(f"\n📊 Summary:")
        print(f"  - Tasks Completed: {result['summary']['tasks_completed']}")
        print(f"  - Coverage: {result['summary']['current_coverage']:.1f}%")
        print(f"  - Critical Items: {result['summary']['critical_insights']}")
    else:
        print(f"❌ Report generation failed")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
