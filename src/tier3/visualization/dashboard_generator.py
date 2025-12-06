"""
Dashboard Generator

Generates interactive HTML dashboards for adoption analytics visualization.
Creates responsive charts and visualizations using Chart.js and modern CSS.

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import sqlite3


@dataclass
class DashboardConfig:
    """Configuration for dashboard generation"""
    title: str = "CORTEX Adoption Analytics"
    theme: str = "light"  # "light" or "dark"
    include_roi: bool = True
    include_trends: bool = True
    include_correlations: bool = True
    include_team_comparison: bool = True
    refresh_interval_seconds: int = 300  # Auto-refresh every 5 minutes


@dataclass
class DashboardResult:
    """Result of dashboard generation"""
    success: bool
    output_path: Optional[str] = None
    dashboard_url: Optional[str] = None
    error_message: Optional[str] = None


class DashboardGenerator:
    """
    Generate interactive HTML dashboards for adoption analytics.
    
    Features:
    - Responsive HTML/CSS design
    - Interactive Chart.js visualizations
    - ROI metrics display
    - Trend charts (time series)
    - Correlation heatmaps
    - Team comparison charts
    - Auto-refresh capability
    - Light/dark theme support
    
    Usage:
        config = DashboardConfig(
            title="Team Adoption Dashboard",
            theme="dark",
            include_roi=True,
            include_trends=True
        )
        
        generator = DashboardGenerator(
            db_path="/path/to/db",
            config=config
        )
        
        result = generator.generate_dashboard(
            output_path="/path/to/dashboard.html",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 30)
        )
    """
    
    def __init__(self, db_path: str, config: Optional[DashboardConfig] = None):
        """
        Initialize dashboard generator.
        
        Args:
            db_path: Path to Tier 3 development_context.db
            config: DashboardConfig with display parameters
        """
        self.db_path = Path(db_path)
        self.config = config or DashboardConfig()
    
    def generate_dashboard(
        self,
        output_path: str,
        start_date: date,
        end_date: date
    ) -> DashboardResult:
        """
        Generate HTML dashboard with analytics visualizations.
        
        Args:
            output_path: Path for output HTML file
            start_date: Start of data period
            end_date: End of data period
            
        Returns:
            DashboardResult with generation status
        """
        try:
            # Collect dashboard data
            data = self._collect_dashboard_data(start_date, end_date)
            
            # Generate HTML
            html = self._generate_html(data, start_date, end_date)
            
            # Write to file
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path_obj, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return DashboardResult(
                success=True,
                output_path=str(output_path_obj),
                dashboard_url=f"file:///{output_path_obj.absolute().as_posix()}"
            )
            
        except Exception as e:
            return DashboardResult(
                success=False,
                error_message=str(e)
            )
    
    def _collect_dashboard_data(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Collect all data needed for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = {}
        
        # ROI summary
        if self.config.include_roi:
            cursor.execute("""
                SELECT 
                    SUM(acceptances) as total_acceptances,
                    COUNT(DISTINCT engineer_hash) as total_engineers
                FROM copilot_metrics
                WHERE metric_date BETWEEN ? AND ?
            """, (start_date.isoformat(), end_date.isoformat()))
            
            row = cursor.fetchone()
            data['roi_summary'] = {
                'total_acceptances': row[0] or 0,
                'total_engineers': row[1] or 0,
                'estimated_hours_saved': round((row[0] or 0) * 0.5 / 60.0, 1),
                'estimated_cost_savings': round((row[0] or 0) * 0.5 / 60.0 * 50, 2)
            }
        
        # Trend data
        if self.config.include_trends:
            cursor.execute("""
                SELECT 
                    metric_date,
                    SUM(total_suggestions) as suggestions,
                    SUM(acceptances) as acceptances
                FROM copilot_metrics
                WHERE metric_date BETWEEN ? AND ?
                GROUP BY metric_date
                ORDER BY metric_date
            """, (start_date.isoformat(), end_date.isoformat()))
            
            trend_data = []
            for row in cursor.fetchall():
                acceptance_rate = (row[2] / row[1] * 100) if row[1] > 0 else 0
                trend_data.append({
                    'date': row[0],
                    'suggestions': row[1],
                    'acceptances': row[2],
                    'acceptance_rate': round(acceptance_rate, 2)
                })
            data['trends'] = trend_data
        
        # Team comparison
        if self.config.include_team_comparison:
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
                LIMIT 10
            """, (start_date.isoformat(), end_date.isoformat()))
            
            team_data = []
            for row in cursor.fetchall():
                team_data.append({
                    'team_id': row[0][:8] + '...',  # Truncate for display
                    'copilot_rate': round(row[1] * 100, 1) if row[1] else 0,
                    'cortex_rate': round(row[2] * 100, 1) if row[2] else 0,
                    'team_size': int(row[3]) if row[3] else 0
                })
            data['teams'] = team_data
        
        conn.close()
        return data
    
    def _generate_html(
        self,
        data: Dict[str, Any],
        start_date: date,
        end_date: date
    ) -> str:
        """Generate complete HTML dashboard"""
        
        # Prepare chart data as JSON
        trends_json = json.dumps(data.get('trends', []))
        teams_json = json.dumps(data.get('teams', []))
        roi_json = json.dumps(data.get('roi_summary', {}))
        
        # Theme colors
        if self.config.theme == "dark":
            bg_color = "#1e1e1e"
            text_color = "#e0e0e0"
            card_bg = "#2d2d2d"
            border_color = "#404040"
        else:
            bg_color = "#f5f5f5"
            text_color = "#333333"
            card_bg = "#ffffff"
            border_color = "#e0e0e0"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: {bg_color};
            color: {text_color};
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
            border-bottom: 2px solid {border_color};
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        header .period {{
            color: #888;
            font-size: 1.1em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        
        .metric-card .label {{
            font-size: 0.9em;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}
        
        .metric-card .value {{
            font-size: 2.5em;
            font-weight: 700;
            color: #0066cc;
            line-height: 1;
        }}
        
        .metric-card .unit {{
            font-size: 0.5em;
            color: #888;
            margin-left: 5px;
        }}
        
        .chart-container {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .chart-container h2 {{
            margin-bottom: 25px;
            font-size: 1.5em;
            font-weight: 600;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }}
        
        footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 2px solid {border_color};
            color: #888;
            font-size: 0.9em;
        }}
        
        .refresh-indicator {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 0.9em;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .chart-wrapper {{
                height: 300px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{self.config.title}</h1>
            <div class="period">
                {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}
            </div>
        </header>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="label">Total Engineers</div>
                <div class="value">{data.get('roi_summary', {}).get('total_engineers', 0)}</div>
            </div>
            <div class="metric-card">
                <div class="label">Copilot Acceptances</div>
                <div class="value">{data.get('roi_summary', {}).get('total_acceptances', 0):,}</div>
            </div>
            <div class="metric-card">
                <div class="label">Hours Saved</div>
                <div class="value">{data.get('roi_summary', {}).get('estimated_hours_saved', 0)}<span class="unit">hrs</span></div>
            </div>
            <div class="metric-card">
                <div class="label">Cost Savings</div>
                <div class="value">${data.get('roi_summary', {}).get('estimated_cost_savings', 0):,.0f}</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>Acceptance Trend Over Time</h2>
            <div class="chart-wrapper">
                <canvas id="trendChart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>Top Teams by Adoption Rate</h2>
            <div class="chart-wrapper">
                <canvas id="teamChart"></canvas>
            </div>
        </div>
        
        <footer>
            <p>Generated by CORTEX Adoption Analytics System</p>
            <p>Author: Asif Hussain | CORTEX v3.7+</p>
        </footer>
    </div>
    
    <div class="refresh-indicator" id="refreshIndicator">
        Last updated: <span id="lastUpdate"></span>
    </div>
    
    <script>
        // Data from Python
        const trendsData = {trends_json};
        const teamsData = {teams_json};
        const roiData = {roi_json};
        
        // Update timestamp
        function updateTimestamp() {{
            const now = new Date();
            document.getElementById('lastUpdate').textContent = now.toLocaleTimeString();
        }}
        updateTimestamp();
        
        // Trend Chart
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {{
            type: 'line',
            data: {{
                labels: trendsData.map(d => d.date),
                datasets: [{{
                    label: 'Acceptance Rate (%)',
                    data: trendsData.map(d => d.acceptance_rate),
                    borderColor: '#0066cc',
                    backgroundColor: 'rgba(0, 102, 204, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Team Chart
        const teamCtx = document.getElementById('teamChart').getContext('2d');
        new Chart(teamCtx, {{
            type: 'bar',
            data: {{
                labels: teamsData.map(t => t.team_id),
                datasets: [
                    {{
                        label: 'Copilot Rate (%)',
                        data: teamsData.map(t => t.copilot_rate),
                        backgroundColor: '#0066cc',
                        borderRadius: 6
                    }},
                    {{
                        label: 'CORTEX Rate (%)',
                        data: teamsData.map(t => t.cortex_rate),
                        backgroundColor: '#00cc66',
                        borderRadius: 6
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Auto-refresh
        {f"setInterval(() => {{ location.reload(); }}, {self.config.refresh_interval_seconds * 1000});" if self.config.refresh_interval_seconds > 0 else "// Auto-refresh disabled"}
    </script>
</body>
</html>"""
        
        return html
