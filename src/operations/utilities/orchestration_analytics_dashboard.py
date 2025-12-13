"""
Orchestration Analytics Dashboard - Visualization and reporting for orchestrator metrics.

**Purpose:** Provide real-time and static visualizations of orchestrator engagement patterns
**Features:**
- 7-day and 30-day metrics aggregation
- Side-by-side orchestrator comparison
- Performance trends (line charts)
- Success rate visualization (pie charts)
- HTML report generation with embedded charts
- Flask server on port 5000 for live dashboard

**CLI Command:** cortex dashboard launch
**Reports Output:** cortex-brain/documents/reports/
**Data Source:** logs/orchestration-metrics/{YYYY-MM-DD}/*.json

**Author:** Asif Hussain
**Feature:** Orchestrator Enhancement Plan v2.0 - Feature 15
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class OrchestrationAnalyticsDashboard:
    """
    Analytics dashboard for orchestrator engagement metrics.
    
    **Responsibilities:**
    1. Aggregate metrics from OrchestrationMetricsCollector logs
    2. Generate performance trends (line charts)
    3. Calculate success rates (pie charts)
    4. Create HTML reports with embedded visualizations
    5. Serve live dashboard via Flask on port 5000
    6. Support 7-day and 30-day reporting windows
    """
    
    def __init__(
        self,
        metrics_base_path: Optional[Path] = None,
        report_output_path: Optional[Path] = None,
        port: int = 5000
    ):
        """
        Initialize analytics dashboard.
        
        Args:
            metrics_base_path: Path to metrics logs (default: logs/orchestration-metrics)
            report_output_path: Path for HTML reports (default: cortex-brain/documents/reports)
            port: Flask server port (default: 5000)
        """
        if metrics_base_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            metrics_base_path = project_root / "logs" / "orchestration-metrics"
        
        if report_output_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            report_output_path = project_root / "cortex-brain" / "documents" / "reports"
        
        self.metrics_base_path = Path(metrics_base_path)
        self.report_output_path = Path(report_output_path)
        self.port = port
        self.default_port = 5000
        
        # Ensure report output directory exists
        self.report_output_path.mkdir(parents=True, exist_ok=True)
    
    def _load_metrics_for_date_range(self, days: int) -> List[Dict[str, Any]]:
        """
        Load all metrics files from last N days.
        
        Args:
            days: Number of days to load (e.g., 7 or 30)
        
        Returns:
            List of all event dictionaries
        """
        events = []
        end_date = datetime.now()
        
        for days_ago in range(days):
            date = end_date - timedelta(days=days_ago)
            date_str = date.strftime("%Y-%m-%d")
            daily_folder = self.metrics_base_path / date_str
            
            if not daily_folder.exists():
                continue
            
            # Load all JSON files in daily folder
            for event_file in daily_folder.glob("*.json"):
                try:
                    with event_file.open("r") as f:
                        event = json.load(f)
                        events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to load event file {event_file}: {e}")
        
        return events
    
    def aggregate_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Aggregate metrics from last N days.
        
        Args:
            days: Number of days to aggregate (default: 7)
        
        Returns:
            Dictionary with:
            - total_engagements: Total count
            - by_orchestrator: {orchestrator_name: {count, avg_duration_ms, success_rate}}
            - by_day: {YYYY-MM-DD: count}
            - avg_duration_ms: Overall average
            - success_rate: Overall success percentage
        """
        events = self._load_metrics_for_date_range(days)
        
        # Filter to complete events only
        complete_events = [e for e in events if e.get("event_type") == "complete"]
        
        if not complete_events:
            return {
                "total_engagements": 0,
                "by_orchestrator": {},
                "by_day": {},
                "avg_duration_ms": 0.0,
                "success_rate": 0.0
            }
        
        # Aggregate by orchestrator
        by_orchestrator = defaultdict(lambda: {
            "count": 0,
            "total_duration_ms": 0.0,
            "success_count": 0,
            "error_count": 0
        })
        
        # Aggregate by day
        by_day = defaultdict(int)
        
        total_duration = 0.0
        total_success = 0
        
        for event in complete_events:
            orch_name = event.get("orchestrator_name", "unknown")
            status = event.get("status", "unknown")
            duration_ms = event.get("duration_ms", 0.0)
            timestamp = event.get("timestamp", "")
            
            # Update orchestrator stats
            by_orchestrator[orch_name]["count"] += 1
            by_orchestrator[orch_name]["total_duration_ms"] += duration_ms
            
            if status == "success":
                by_orchestrator[orch_name]["success_count"] += 1
                total_success += 1
            else:
                by_orchestrator[orch_name]["error_count"] += 1
            
            # Update daily stats
            if timestamp:
                try:
                    date_str = timestamp.split("T")[0]  # Extract YYYY-MM-DD
                    by_day[date_str] += 1
                except Exception:
                    pass
            
            total_duration += duration_ms
        
        # Calculate aggregated stats
        total_count = len(complete_events)
        avg_duration_ms = total_duration / total_count if total_count > 0 else 0.0
        success_rate = (total_success / total_count * 100) if total_count > 0 else 0.0
        
        # Calculate per-orchestrator stats
        orchestrator_stats = {}
        for orch_name, stats in by_orchestrator.items():
            count = stats["count"]
            avg_duration = stats["total_duration_ms"] / count if count > 0 else 0.0
            success_rate_orch = (stats["success_count"] / count * 100) if count > 0 else 0.0
            
            orchestrator_stats[orch_name] = {
                "count": count,
                "avg_duration_ms": avg_duration,
                "success_rate": success_rate_orch,
                "error_count": stats["error_count"]
            }
        
        return {
            "total_engagements": total_count,
            "by_orchestrator": orchestrator_stats,
            "by_day": dict(by_day),
            "avg_duration_ms": avg_duration_ms,
            "success_rate": success_rate
        }
    
    def compare_orchestrators(
        self,
        days: int = 7,
        sort_by: str = "engagement_count"
    ) -> List[Dict[str, Any]]:
        """
        Compare statistics across multiple orchestrators.
        
        Args:
            days: Number of days to analyze (default: 7)
            sort_by: Sort key ("engagement_count", "avg_duration", "success_rate")
        
        Returns:
            List of orchestrator statistics sorted by specified key
        """
        aggregated = self.aggregate_metrics(days)
        
        comparison = []
        for orch_name, stats in aggregated["by_orchestrator"].items():
            comparison.append({
                "orchestrator_name": orch_name,
                "total_engagements": stats["count"],
                "avg_duration_ms": stats["avg_duration_ms"],
                "success_rate": stats["success_rate"],
                "error_count": stats["error_count"]
            })
        
        # Sort by specified key
        if sort_by == "engagement_count":
            comparison.sort(key=lambda x: x["total_engagements"], reverse=True)
        elif sort_by == "avg_duration":
            comparison.sort(key=lambda x: x["avg_duration_ms"], reverse=True)
        elif sort_by == "success_rate":
            comparison.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return comparison
    
    def generate_performance_trend(
        self,
        days: int = 7,
        orchestrator_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate performance trend data for line charts.
        
        Args:
            days: Number of days to analyze
            orchestrator_filter: Optional orchestrator name to filter by
        
        Returns:
            Dictionary with dates and durations for charting:
            - dates: List of datetime objects
            - durations: List of average durations per day
            - by_orchestrator: {orch_name: {dates: [...], durations: [...]}}
        """
        events = self._load_metrics_for_date_range(days)
        complete_events = [e for e in events if e.get("event_type") == "complete"]
        
        # Aggregate by date
        by_date = defaultdict(lambda: {"total_duration": 0.0, "count": 0})
        by_orchestrator_date = defaultdict(lambda: defaultdict(lambda: {"total_duration": 0.0, "count": 0}))
        
        for event in complete_events:
            timestamp = event.get("timestamp", "")
            duration_ms = event.get("duration_ms", 0.0)
            orch_name = event.get("orchestrator_name", "unknown")
            
            if orchestrator_filter and orch_name != orchestrator_filter:
                continue
            
            if timestamp:
                try:
                    date_str = timestamp.split("T")[0]
                    date_obj = datetime.fromisoformat(date_str)
                    
                    by_date[date_obj]["total_duration"] += duration_ms
                    by_date[date_obj]["count"] += 1
                    
                    by_orchestrator_date[orch_name][date_obj]["total_duration"] += duration_ms
                    by_orchestrator_date[orch_name][date_obj]["count"] += 1
                except Exception:
                    pass
        
        # Convert to sorted lists
        sorted_dates = sorted(by_date.keys())
        durations = []
        
        for date in sorted_dates:
            stats = by_date[date]
            avg_duration = stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0.0
            durations.append(avg_duration)
        
        # Generate by-orchestrator trends
        by_orchestrator_trends = {}
        for orch_name, date_stats in by_orchestrator_date.items():
            sorted_dates_orch = sorted(date_stats.keys())
            durations_orch = []
            
            for date in sorted_dates_orch:
                stats = date_stats[date]
                avg_duration = stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0.0
                durations_orch.append(avg_duration)
            
            by_orchestrator_trends[orch_name] = {
                "dates": sorted_dates_orch,
                "durations": durations_orch
            }
        
        return {
            "dates": sorted_dates,
            "durations": durations,
            "by_orchestrator": by_orchestrator_trends
        }
    
    def generate_duration_chart(self, trend_data: Dict[str, Any]) -> Optional[Path]:
        """
        Generate duration line chart visualization.
        
        Args:
            trend_data: Trend data from generate_performance_trend()
        
        Returns:
            Path to generated chart image (PNG)
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            dates = trend_data.get("dates", [])
            durations = trend_data.get("durations", [])
            
            if dates and durations:
                ax.plot(dates, durations, marker='o', linewidth=2, markersize=6)
                ax.set_xlabel("Date")
                ax.set_ylabel("Average Duration (ms)")
                ax.set_title("Orchestrator Performance Trend")
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
            
            # Save chart
            chart_path = self.report_output_path / f"duration_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            return chart_path
        except ImportError:
            logger.warning("matplotlib not installed - chart generation skipped")
            return None
        except Exception as e:
            logger.error(f"Failed to generate duration chart: {e}")
            return None
    
    def calculate_success_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Calculate success/failure/skip metrics for pie charts.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with success_count, error_count, skip_count, success_rate
        """
        events = self._load_metrics_for_date_range(days)
        complete_events = [e for e in events if e.get("event_type") == "complete"]
        
        success_count = 0
        error_count = 0
        skip_count = 0
        
        for event in complete_events:
            status = event.get("status", "unknown")
            
            if status == "success":
                success_count += 1
            elif status == "error":
                error_count += 1
            elif status == "skip":
                skip_count += 1
        
        total = success_count + error_count + skip_count
        success_rate = (success_count / total * 100) if total > 0 else 0.0
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "skip_count": skip_count,
            "success_rate": success_rate
        }
    
    def generate_success_pie_chart(self, success_metrics: Dict[str, Any]) -> Optional[Path]:
        """
        Generate success rate pie chart.
        
        Args:
            success_metrics: Metrics from calculate_success_metrics()
        
        Returns:
            Path to generated chart image (PNG)
        """
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            labels = []
            sizes = []
            colors = ['#4CAF50', '#F44336', '#FFC107']
            
            if success_metrics["success_count"] > 0:
                labels.append(f"Success ({success_metrics['success_count']})")
                sizes.append(success_metrics["success_count"])
            
            if success_metrics["error_count"] > 0:
                labels.append(f"Error ({success_metrics['error_count']})")
                sizes.append(success_metrics["error_count"])
            
            if success_metrics["skip_count"] > 0:
                labels.append(f"Skip ({success_metrics['skip_count']})")
                sizes.append(success_metrics["skip_count"])
            
            if sizes:
                ax.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%',
                       startangle=90, textprops={'fontsize': 12})
                ax.set_title(f"Success Rate: {success_metrics['success_rate']:.1f}%", fontsize=14)
            
            # Save chart
            chart_path = self.report_output_path / f"success_rate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            return chart_path
        except ImportError:
            logger.warning("matplotlib not installed - pie chart generation skipped")
            return None
        except Exception as e:
            logger.error(f"Failed to generate success pie chart: {e}")
            return None
    
    def calculate_success_metrics_by_orchestrator(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Calculate success rate for each orchestrator separately.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            List of {orchestrator_name, success_count, error_count, success_rate}
        """
        events = self._load_metrics_for_date_range(days)
        complete_events = [e for e in events if e.get("event_type") == "complete"]
        
        by_orchestrator = defaultdict(lambda: {"success": 0, "error": 0, "skip": 0})
        
        for event in complete_events:
            orch_name = event.get("orchestrator_name", "unknown")
            status = event.get("status", "unknown")
            
            if status == "success":
                by_orchestrator[orch_name]["success"] += 1
            elif status == "error":
                by_orchestrator[orch_name]["error"] += 1
            elif status == "skip":
                by_orchestrator[orch_name]["skip"] += 1
        
        results = []
        for orch_name, stats in by_orchestrator.items():
            total = stats["success"] + stats["error"] + stats["skip"]
            success_rate = (stats["success"] / total * 100) if total > 0 else 0.0
            
            results.append({
                "orchestrator_name": orch_name,
                "success_count": stats["success"],
                "error_count": stats["error"],
                "skip_count": stats["skip"],
                "success_rate": success_rate
            })
        
        return results
    
    def generate_html_report(self, days: int = 7) -> Path:
        """
        Generate static HTML report with embedded charts.
        
        Args:
            days: Number of days to include in report
        
        Returns:
            Path to generated HTML report
        """
        # Aggregate data
        aggregated = self.aggregate_metrics(days)
        comparison = self.compare_orchestrators(days)
        trend_data = self.generate_performance_trend(days)
        success_metrics = self.calculate_success_metrics(days)
        
        # Generate charts
        duration_chart = self.generate_duration_chart(trend_data)
        success_chart = self.generate_success_pie_chart(success_metrics)
        
        # Build HTML content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Orchestration Analytics Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 8px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #2196F3; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #2196F3; color: white; }}
        .chart {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ margin-top: 40px; color: #666; font-size: 12px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Orchestration Analytics Dashboard</h1>
        <p>Generated: {timestamp} | Data Range: Last {days} days</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{aggregated['total_engagements']}</div>
            <div class="stat-label">Total Engagements</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{aggregated['avg_duration_ms']:.0f}ms</div>
            <div class="stat-label">Average Duration</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{aggregated['success_rate']:.1f}%</div>
            <div class="stat-label">Success Rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(aggregated['by_orchestrator'])}</div>
            <div class="stat-label">Active Orchestrators</div>
        </div>
    </div>
    
    <h2>Orchestrator Comparison</h2>
    <table>
        <thead>
            <tr>
                <th>Orchestrator</th>
                <th>Engagements</th>
                <th>Avg Duration (ms)</th>
                <th>Success Rate</th>
                <th>Errors</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for orch in comparison:
            html_content += f"""            <tr>
                <td>{orch['orchestrator_name']}</td>
                <td>{orch['total_engagements']}</td>
                <td>{orch['avg_duration_ms']:.0f}</td>
                <td>{orch['success_rate']:.1f}%</td>
                <td>{orch['error_count']}</td>
            </tr>
"""
        
        html_content += """        </tbody>
    </table>
"""
        
        # Add charts if available
        if duration_chart or success_chart:
            html_content += """    <h2>Visualizations</h2>
"""
            
            if duration_chart and duration_chart.exists():
                html_content += f"""    <div class="chart">
        <h3>Performance Trend</h3>
        <img src="{duration_chart.name}" alt="Duration Trend" style="max-width: 100%;">
    </div>
"""
            
            if success_chart and success_chart.exists():
                html_content += f"""    <div class="chart">
        <h3>Success Rate Distribution</h3>
        <img src="{success_chart.name}" alt="Success Rate" style="max-width: 100%;">
    </div>
"""
        
        html_content += f"""    
    <div class="footer">
        <p>© 2024-2025 Asif Hussain | CORTEX Orchestrator Enhancement Plan v2.0 - Feature 15</p>
    </div>
</body>
</html>
"""
        
        # Save HTML report
        report_filename = f"orchestration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path = self.report_output_path / report_filename
        
        report_path.write_text(html_content)
        logger.info(f"HTML report generated: {report_path}")
        
        return report_path
    
    def create_flask_app(self):
        """
        Create Flask application for live dashboard.
        
        Returns:
            Flask app instance with configured routes
        """
        try:
            from flask import Flask, jsonify, render_template_string
        except ImportError:
            logger.error("Flask not installed - cannot create dashboard server")
            return None
        
        app = Flask(__name__)
        
        @app.route("/dashboard")
        def dashboard():
            """Render HTML dashboard page"""
            report_path = self.generate_html_report(days=7)
            content = report_path.read_text()
            return content
        
        @app.route("/metrics/7days")
        def metrics_7days():
            """Return 7-day metrics as JSON"""
            aggregated = self.aggregate_metrics(days=7)
            return jsonify(aggregated)
        
        @app.route("/metrics/30days")
        def metrics_30days():
            """Return 30-day metrics as JSON"""
            aggregated = self.aggregate_metrics(days=30)
            return jsonify(aggregated)
        
        @app.route("/health")
        def health():
            """Server health check"""
            return jsonify({"status": "healthy", "service": "orchestration-analytics-dashboard"})
        
        return app
    
    def start_server(self, host: str = "127.0.0.1", port: Optional[int] = None):
        """
        Start Flask server for live dashboard.
        
        Args:
            host: Server host (default: localhost)
            port: Server port (default: self.port or 5000)
        """
        if port is None:
            port = self.port
        
        app = self.create_flask_app()
        
        if app is None:
            logger.error("Failed to create Flask app - server not started")
            return
        
        logger.info(f"Starting Orchestration Analytics Dashboard on http://{host}:{port}")
        logger.info(f"Dashboard: http://{host}:{port}/dashboard")
        logger.info(f"7-day metrics: http://{host}:{port}/metrics/7days")
        logger.info(f"30-day metrics: http://{host}:{port}/metrics/30days")
        
        app.run(host=host, port=port, debug=False)
