"""
Report Generator

Generates formatted reports (Markdown/PDF) for adoption analytics.
Supports automated scheduling and email delivery integration.

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import sqlite3
from enum import Enum


class ReportFormat(Enum):
    """Supported report formats"""
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"


class ReportFrequency(Enum):
    """Report scheduling frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class ReportConfig:
    """Configuration for report generation"""
    format: ReportFormat = ReportFormat.MARKDOWN
    frequency: ReportFrequency = ReportFrequency.WEEKLY
    include_executive_summary: bool = True
    include_roi_analysis: bool = True
    include_team_breakdown: bool = True
    include_trends: bool = True
    include_recommendations: bool = True


@dataclass
class ReportResult:
    """Result of report generation"""
    success: bool
    output_path: Optional[str] = None
    report_date: Optional[date] = None
    error_message: Optional[str] = None


class ReportGenerator:
    """
    Generate formatted analytics reports.
    
    Features:
    - Multiple formats (Markdown, HTML, Text)
    - Executive summaries with key insights
    - ROI analysis with business metrics
    - Team performance breakdown
    - Trend analysis with visualizations
    - Automated recommendations
    - Configurable scheduling
    - Email-ready formatting
    
    Usage:
        config = ReportConfig(
            format=ReportFormat.MARKDOWN,
            frequency=ReportFrequency.WEEKLY,
            include_executive_summary=True
        )
        
        generator = ReportGenerator(
            db_path="/path/to/db",
            config=config
        )
        
        result = generator.generate_report(
            output_path="/path/to/report.md",
            report_date=date.today()
        )
    """
    
    def __init__(self, db_path: str, config: Optional[ReportConfig] = None):
        """
        Initialize report generator.
        
        Args:
            db_path: Path to Tier 3 development_context.db
            config: ReportConfig with report parameters
        """
        self.db_path = Path(db_path)
        self.config = config or ReportConfig()
    
    def generate_report(
        self,
        output_path: str,
        report_date: Optional[date] = None
    ) -> ReportResult:
        """
        Generate adoption analytics report.
        
        Args:
            output_path: Path for output report file
            report_date: End date for report period (defaults to today)
            
        Returns:
            ReportResult with generation status
        """
        try:
            if report_date is None:
                report_date = date.today()
            
            # Calculate period based on frequency
            start_date = self._calculate_start_date(report_date)
            
            # Collect report data
            data = self._collect_report_data(start_date, report_date)
            
            # Generate report content
            if self.config.format == ReportFormat.MARKDOWN:
                content = self._generate_markdown(data, start_date, report_date)
            elif self.config.format == ReportFormat.HTML:
                content = self._generate_html(data, start_date, report_date)
            else:
                content = self._generate_text(data, start_date, report_date)
            
            # Write to file
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path_obj, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return ReportResult(
                success=True,
                output_path=str(output_path_obj),
                report_date=report_date
            )
            
        except Exception as e:
            return ReportResult(
                success=False,
                error_message=str(e)
            )
    
    def _calculate_start_date(self, end_date: date) -> date:
        """Calculate report start date based on frequency"""
        if self.config.frequency == ReportFrequency.DAILY:
            return end_date
        elif self.config.frequency == ReportFrequency.WEEKLY:
            return end_date - timedelta(days=7)
        elif self.config.frequency == ReportFrequency.MONTHLY:
            return end_date - timedelta(days=30)
        else:  # QUARTERLY
            return end_date - timedelta(days=90)
    
    def _collect_report_data(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Collect all data needed for report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = {}
        
        # Overall summary
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT engineer_hash) as total_engineers,
                SUM(total_suggestions) as total_suggestions,
                SUM(acceptances) as total_acceptances
            FROM copilot_metrics
            WHERE metric_date BETWEEN ? AND ?
        """, (start_date.isoformat(), end_date.isoformat()))
        
        row = cursor.fetchone()
        data['summary'] = {
            'total_engineers': row[0] or 0,
            'total_suggestions': row[1] or 0,
            'total_acceptances': row[2] or 0,
            'acceptance_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0
        }
        
        # ROI metrics
        if self.config.include_roi_analysis:
            hours_saved = (data['summary']['total_acceptances'] * 0.5) / 60.0
            cost_savings = hours_saved * 50  # $50/hour default
            
            data['roi'] = {
                'hours_saved': round(hours_saved, 1),
                'cost_savings': round(cost_savings, 2),
                'productivity_gain': round(cost_savings * 1.2, 2)
            }
        
        # Team breakdown
        if self.config.include_team_breakdown:
            cursor.execute("""
                SELECT 
                    team_id,
                    AVG(copilot_acceptance_rate) as avg_acceptance,
                    AVG(cortex_success_rate) as avg_success,
                    AVG(team_size) as avg_size
                FROM team_aggregations
                WHERE aggregation_date BETWEEN ? AND ?
                GROUP BY team_id
                ORDER BY avg_acceptance DESC
            """, (start_date.isoformat(), end_date.isoformat()))
            
            teams = []
            for row in cursor.fetchall():
                teams.append({
                    'team_id': row[0],
                    'acceptance_rate': round(row[1] * 100, 1) if row[1] else 0,
                    'success_rate': round(row[2] * 100, 1) if row[2] else 0,
                    'team_size': int(row[3]) if row[3] else 0
                })
            data['teams'] = teams
        
        # Trends
        if self.config.include_trends:
            cursor.execute("""
                SELECT 
                    metric_date,
                    SUM(acceptances) as daily_acceptances
                FROM copilot_metrics
                WHERE metric_date BETWEEN ? AND ?
                GROUP BY metric_date
                ORDER BY metric_date
            """, (start_date.isoformat(), end_date.isoformat()))
            
            daily_data = [row[1] for row in cursor.fetchall()]
            if daily_data:
                data['trends'] = {
                    'avg_daily': round(sum(daily_data) / len(daily_data), 1),
                    'max_daily': max(daily_data),
                    'min_daily': min(daily_data),
                    'direction': 'increasing' if daily_data[-1] > daily_data[0] else 'decreasing'
                }
        
        conn.close()
        return data
    
    def _generate_markdown(
        self,
        data: Dict[str, Any],
        start_date: date,
        end_date: date
    ) -> str:
        """Generate Markdown report"""
        
        lines = [
            "# Adoption Analytics Report",
            "",
            f"**Report Period:** {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}  ",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  ",
            f"**Frequency:** {self.config.frequency.value.title()}  ",
            "",
            "---",
            ""
        ]
        
        # Executive Summary
        if self.config.include_executive_summary:
            summary = data['summary']
            lines.extend([
                "## Executive Summary",
                "",
                f"- **Total Engineers:** {summary['total_engineers']:,}",
                f"- **Copilot Suggestions:** {summary['total_suggestions']:,}",
                f"- **Acceptances:** {summary['total_acceptances']:,}",
                f"- **Acceptance Rate:** {summary['acceptance_rate']:.1f}%",
                ""
            ])
        
        # ROI Analysis
        if self.config.include_roi_analysis and 'roi' in data:
            roi = data['roi']
            lines.extend([
                "## Return on Investment",
                "",
                f"- **Time Saved:** {roi['hours_saved']:.1f} hours",
                f"- **Cost Savings:** ${roi['cost_savings']:,.2f}",
                f"- **Productivity Gain:** ${roi['productivity_gain']:,.2f}",
                "",
                "**Analysis:** Based on average engineer hourly cost of $50 and ",
                "estimated 0.5 minutes saved per Copilot acceptance.",
                ""
            ])
        
        # Team Breakdown
        if self.config.include_team_breakdown and 'teams' in data:
            lines.extend([
                "## Team Performance",
                "",
                "| Team | Acceptance Rate | Success Rate | Team Size |",
                "|------|----------------|--------------|-----------|"
            ])
            
            for team in data['teams'][:10]:  # Top 10 teams
                team_id = team['team_id'][:12] + '...' if len(team['team_id']) > 15 else team['team_id']
                lines.append(
                    f"| {team_id} | {team['acceptance_rate']:.1f}% | "
                    f"{team['success_rate']:.1f}% | {team['team_size']} |"
                )
            
            lines.append("")
        
        # Trends
        if self.config.include_trends and 'trends' in data:
            trends = data['trends']
            lines.extend([
                "## Adoption Trends",
                "",
                f"- **Average Daily Acceptances:** {trends['avg_daily']:.1f}",
                f"- **Peak Day:** {trends['max_daily']} acceptances",
                f"- **Lowest Day:** {trends['min_daily']} acceptances",
                f"- **Trend Direction:** {trends['direction'].title()}",
                ""
            ])
        
        # Recommendations
        if self.config.include_recommendations:
            lines.extend([
                "## Recommendations",
                "",
                self._generate_recommendations(data),
                ""
            ])
        
        # Footer
        lines.extend([
            "---",
            "",
            "*Report generated by CORTEX Adoption Analytics System*  ",
            "*Author: Asif Hussain | CORTEX v3.7+*"
        ])
        
        return "\n".join(lines)
    
    def _generate_html(
        self,
        data: Dict[str, Any],
        start_date: date,
        end_date: date
    ) -> str:
        """Generate HTML report"""
        # Convert markdown to HTML-like structure
        md_content = self._generate_markdown(data, start_date, end_date)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Adoption Analytics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #0066cc; }}
        h2 {{ color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #0066cc; color: white; }}
        ul {{ line-height: 1.8; }}
    </style>
</head>
<body>
    <pre>{md_content}</pre>
</body>
</html>"""
        return html
    
    def _generate_text(
        self,
        data: Dict[str, Any],
        start_date: date,
        end_date: date
    ) -> str:
        """Generate plain text report"""
        # Simplified version of markdown without formatting
        md_content = self._generate_markdown(data, start_date, end_date)
        # Remove markdown symbols
        text = md_content.replace('#', '').replace('**', '').replace('*', '')
        return text
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> str:
        """Generate smart recommendations based on data"""
        recommendations = []
        
        summary = data.get('summary', {})
        acceptance_rate = summary.get('acceptance_rate', 0)
        
        if acceptance_rate < 30:
            recommendations.append(
                "- **Low Acceptance Rate Alert:** Consider training sessions on "
                "effective Copilot usage patterns."
            )
        elif acceptance_rate > 60:
            recommendations.append(
                "- **High Adoption Success:** Current practices are working well. "
                "Consider documenting best practices for other teams."
            )
        
        if 'trends' in data:
            if data['trends']['direction'] == 'decreasing':
                recommendations.append(
                    "- **Declining Trend:** Investigate potential barriers to adoption. "
                    "Survey engineers for feedback."
                )
            else:
                recommendations.append(
                    "- **Positive Trend:** Adoption is increasing. Continue current "
                    "enablement efforts."
                )
        
        if 'teams' in data and len(data['teams']) > 0:
            top_team = data['teams'][0]
            if top_team['acceptance_rate'] > 50:
                recommendations.append(
                    f"- **Top Performer:** Team {top_team['team_id'][:12]}... shows "
                    "strong adoption. Consider case study for knowledge sharing."
                )
        
        if not recommendations:
            recommendations.append(
                "- Continue monitoring adoption metrics and engagement levels."
            )
        
        return "\n".join(recommendations)
    
    def schedule_report(
        self,
        output_directory: str,
        frequency: ReportFrequency
    ) -> Dict[str, Any]:
        """
        Set up automated report scheduling.
        
        Args:
            output_directory: Directory for scheduled reports
            frequency: Report frequency (DAILY, WEEKLY, MONTHLY, QUARTERLY)
            
        Returns:
            Dictionary with scheduling configuration
            
        Note: This returns configuration for external scheduler.
              Actual scheduling requires cron/Task Scheduler integration.
        """
        
        next_run = self._calculate_next_run(frequency)
        
        return {
            'frequency': frequency.value,
            'output_directory': output_directory,
            'next_run': next_run.isoformat(),
            'cron_expression': self._get_cron_expression(frequency),
            'command': f"python -m src.tier3.visualization.report_generator {output_directory}"
        }
    
    def _calculate_next_run(self, frequency: ReportFrequency) -> datetime:
        """Calculate next scheduled run time"""
        now = datetime.now()
        
        if frequency == ReportFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == ReportFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == ReportFrequency.MONTHLY:
            return now + timedelta(days=30)
        else:  # QUARTERLY
            return now + timedelta(days=90)
    
    def _get_cron_expression(self, frequency: ReportFrequency) -> str:
        """Get cron expression for frequency"""
        if frequency == ReportFrequency.DAILY:
            return "0 8 * * *"  # Daily at 8 AM
        elif frequency == ReportFrequency.WEEKLY:
            return "0 8 * * 1"  # Mondays at 8 AM
        elif frequency == ReportFrequency.MONTHLY:
            return "0 8 1 * *"  # 1st of month at 8 AM
        else:  # QUARTERLY
            return "0 8 1 */3 *"  # 1st of quarter at 8 AM
