"""
Dashboard Visualization Component.

Generates interactive visualizations for test coverage analysis:
- Coverage heatmaps (treemap with color coding)
- Priority matrices (2D scatter plots)
- Roadmap Gantt charts (timeline views)
- Domain coverage tables
- Quick wins cards
- HTML/JS/CSS rendering

Author: CORTEX Intelligence System
Date: 2025-12-08
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class HeatmapNode:
    """Node in coverage heatmap treemap."""
    name: str
    value: int  # LOC
    coverage: float
    color: str
    domain: str
    file: str


@dataclass
class MatrixPoint:
    """Point in priority matrix."""
    x: float  # Coverage %
    y: float  # Risk score
    priority: str
    file: str
    class_name: str
    method_name: str
    tooltip: Dict[str, Any]


@dataclass
class GanttMilestone:
    """Milestone in Gantt chart."""
    id: str
    name: str
    start_date: str
    end_date: str
    duration_weeks: int
    color: str
    tasks: int
    effort_hours: float


# ============================================================================
# Dashboard Visualizer
# ============================================================================

class DashboardVisualizer:
    """
    Generate dashboard visualizations for test coverage intelligence.
    
    Supports:
    - Coverage heatmaps with domain grouping
    - Priority matrices with filtering
    - Gantt charts with milestone tracking
    - Domain coverage tables
    - Quick wins cards
    - HTML/JS rendering with Chart.js and D3.js
    """
    
    def __init__(self):
        """Initialize visualizer."""
        self.priority_colors = {
            "P0": "red",
            "P1": "orange",
            "P2": "yellow",
            "P3": "gray"
        }
    
    # ========================================================================
    # Heatmap Generation
    # ========================================================================
    
    def generate_heatmap(self, coverage_data: Dict, group_by: str = "file") -> Dict:
        """
        Generate coverage heatmap treemap.
        
        Args:
            coverage_data: Coverage data with file-level metrics
            group_by: Grouping strategy ('file' or 'domain')
        
        Returns:
            Heatmap structure with nodes, colors, metadata
        """
        if not coverage_data or "coverage_by_file" not in coverage_data:
            return {"nodes": [], "message": "No coverage data available"}
        
        files = coverage_data["coverage_by_file"]
        nodes = []
        
        for file_data in files:
            coverage = file_data.get("line_coverage", 0)
            color = self._get_coverage_color(coverage)
            
            node = HeatmapNode(
                name=self._extract_filename(file_data["file"]),
                value=file_data.get("loc", 0),
                coverage=coverage,
                color=color,
                domain=file_data.get("domain", "Unknown"),
                file=file_data["file"]
            )
            nodes.append(asdict(node))
        
        result = {
            "nodes": nodes,
            "metadata": {
                "total_files": len(nodes),
                "group_by": group_by
            }
        }
        
        # Add domain grouping if requested
        if group_by == "domain":
            result["groups"] = self._group_by_domain(nodes)
        
        return result
    
    def _get_coverage_color(self, coverage: float) -> str:
        """Map coverage percentage to color."""
        if coverage >= 70:
            return "green"
        elif coverage >= 30:
            return "yellow"
        else:
            return "red"
    
    def _extract_filename(self, filepath: str) -> str:
        """Extract filename from path."""
        return filepath.split("/")[-1].split("\\")[-1]
    
    def _group_by_domain(self, nodes: List[Dict]) -> List[Dict]:
        """Group nodes by business domain."""
        domains = {}
        for node in nodes:
            domain = node["domain"]
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(node)
        
        return [
            {"name": domain, "children": children}
            for domain, children in domains.items()
        ]
    
    # ========================================================================
    # Priority Matrix Generation
    # ========================================================================
    
    def generate_priority_matrix(self, gap_data: Dict, filter_priority: Optional[str] = None) -> Dict:
        """
        Generate priority matrix scatter plot.
        
        Args:
            gap_data: Gap prioritization data with P0/P1/P2/P3
            filter_priority: Optional priority filter (e.g., "P0")
        
        Returns:
            Matrix structure with points and quadrants
        """
        if filter_priority and filter_priority not in ["P0", "P1", "P2", "P3"]:
            raise ValueError(f"Invalid priority: {filter_priority}")
        
        points = []
        
        for priority in ["p0_critical", "p1_high", "p2_medium", "p3_low"]:
            if priority not in gap_data:
                continue
            
            priority_code = priority.split("_")[0].upper()
            
            # Skip if filtering
            if filter_priority and priority_code != filter_priority:
                continue
            
            examples = gap_data[priority].get("examples", [])
            for example in examples:
                tooltip = {
                    "file": example.get("file", ""),
                    "class": example.get("class", ""),
                    "method": example.get("method", ""),
                    "reason": example.get("reason", ""),
                    "complexity": example.get("complexity", 0),
                    "effort_hours": example.get("effort_hours", 0)
                }
                
                point = MatrixPoint(
                    x=example.get("current_coverage", 0),
                    y=example.get("risk_score", 0),
                    priority=priority_code,
                    file=example.get("file", ""),
                    class_name=example.get("class", ""),
                    method_name=example.get("method", ""),
                    tooltip=tooltip
                )
                points.append(asdict(point))
        
        return {
            "points": points,
            "quadrants": [
                {"name": "P0 - Critical", "color": "red", "x_range": [0, 30], "y_range": [70, 100]},
                {"name": "P1 - High", "color": "orange", "x_range": [0, 50], "y_range": [50, 70]},
                {"name": "P2 - Medium", "color": "yellow", "x_range": [30, 70], "y_range": [30, 50]},
                {"name": "P3 - Low", "color": "gray", "x_range": [70, 100], "y_range": [0, 30]}
            ]
        }
    
    # ========================================================================
    # Gantt Chart Generation
    # ========================================================================
    
    def generate_gantt_chart(self, roadmap_data: Dict) -> Dict:
        """
        Generate roadmap Gantt chart.
        
        Args:
            roadmap_data: Roadmap with milestones and tasks
        
        Returns:
            Gantt structure with milestones, tasks, timeline
        """
        if not roadmap_data or "milestones" not in roadmap_data:
            return {"milestones": [], "message": "No milestones defined"}
        
        milestones_data = roadmap_data["milestones"]
        if not milestones_data:
            return {"milestones": [], "message": "No milestones defined"}
        
        milestones = []
        current_date = datetime.now()
        
        for milestone_data in milestones_data:
            duration_weeks = milestone_data.get("timeline_weeks", 1)
            start_date = current_date
            end_date = start_date + timedelta(weeks=duration_weeks)
            
            # Determine color from milestone ID
            milestone_id = milestone_data.get("id", "M1")
            if "1" in milestone_id:
                color = "red"  # P0 Critical
            elif "2" in milestone_id:
                color = "orange"  # P1 High
            elif "3" in milestone_id:
                color = "yellow"  # P2 Medium
            else:
                color = "gray"  # P3 Low
            
            milestone = GanttMilestone(
                id=milestone_data.get("id", ""),
                name=milestone_data.get("name", ""),
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                duration_weeks=duration_weeks,
                color=color,
                tasks=milestone_data.get("tasks", 0),
                effort_hours=milestone_data.get("effort_hours", 0)
            )
            milestones.append(asdict(milestone))
            
            # Next milestone starts after this one
            current_date = end_date
        
        return {
            "milestones": milestones,
            "tasks": [],  # Task-level details optional
            "timeline": {
                "start": milestones[0]["start_date"] if milestones else "",
                "end": milestones[-1]["end_date"] if milestones else ""
            }
        }
    
    # ========================================================================
    # Domain Coverage Table
    # ========================================================================
    
    def generate_domain_table(self, coverage_data: Dict) -> Dict:
        """
        Generate domain coverage table.
        
        Args:
            coverage_data: Coverage data with domain metrics
        
        Returns:
            Table structure with rows, columns, metadata
        """
        if not coverage_data or "coverage_by_domain" not in coverage_data:
            return {"rows": [], "columns": []}
        
        domains = coverage_data["coverage_by_domain"]
        
        rows = []
        for domain_name, metrics in domains.items():
            coverage = metrics.get("line_coverage", 0)
            status = self._get_status_indicator(coverage)
            
            # Count files in this domain
            files_in_domain = [
                f for f in coverage_data.get("coverage_by_file", [])
                if f.get("domain") == domain_name
            ]
            file_count = len(files_in_domain)
            total_loc = sum(f.get("loc", 0) for f in files_in_domain)
            
            # Count P0 tasks (if available)
            p0_count = 0  # Would need gap data to calculate
            
            row = {
                "Domain": domain_name,
                "Files": file_count,
                "LOC": total_loc,
                "Coverage %": round(coverage, 1),
                "P0 Count": p0_count,
                "Status": status
            }
            rows.append(row)
        
        return {
            "columns": ["Domain", "Files", "LOC", "Coverage %", "P0 Count", "Status"],
            "rows": rows,
            "sortable": True,
            "column_types": {
                "Domain": "string",
                "Files": "numeric",
                "LOC": "numeric",
                "Coverage %": "numeric",
                "P0 Count": "numeric",
                "Status": "string"
            }
        }
    
    def _get_status_indicator(self, coverage: float) -> str:
        """Get status indicator based on coverage."""
        if coverage >= 70:
            return "Good"
        elif coverage >= 40:
            return "Warning"
        else:
            return "Critical"
    
    # ========================================================================
    # Quick Wins Display
    # ========================================================================
    
    def generate_quick_wins_cards(self, roadmap_data: Dict) -> Dict:
        """
        Generate quick wins cards.
        
        Args:
            roadmap_data: Roadmap with quick wins data
        
        Returns:
            Cards structure with quick wins
        """
        if not roadmap_data or "quick_wins" not in roadmap_data:
            return {"cards": []}
        
        quick_wins = roadmap_data["quick_wins"]
        
        cards = []
        for qw in quick_wins:
            card = {
                "title": qw.get("task", ""),
                "effort_hours": qw.get("effort_hours", 0),
                "impact": qw.get("impact", ""),
                "priority": qw.get("priority", "P1"),
                "reason": qw.get("reason", ""),
                "action_button": {
                    "text": "Generate Test Skeleton",
                    "callback": "generateTestSkeleton",
                    "task_id": qw.get("task", "")
                }
            }
            cards.append(card)
        
        # Sort by effort (ascending)
        cards.sort(key=lambda c: c["effort_hours"])
        
        return {"cards": cards}
    
    # ========================================================================
    # HTML Rendering
    # ========================================================================
    
    def render_dashboard(
        self,
        coverage_data: Optional[Dict] = None,
        gap_data: Optional[Dict] = None,
        roadmap_data: Optional[Dict] = None
    ) -> str:
        """
        Render complete dashboard HTML.
        
        Args:
            coverage_data: Coverage metrics
            gap_data: Gap prioritization data
            roadmap_data: Roadmap with milestones
        
        Returns:
            Complete HTML string with embedded JS and CSS
        """
        heatmap = self.generate_heatmap(coverage_data or {})
        matrix = self.generate_priority_matrix(gap_data or {})
        gantt = self.generate_gantt_chart(roadmap_data or {})
        table = self.generate_domain_table(coverage_data or {})
        quick_wins = self.generate_quick_wins_cards(roadmap_data or {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Coverage Dashboard</title>
    
    <!-- Chart libraries -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        
        .test-coverage-tab {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .coverage-heatmap, .priority-matrix, .roadmap-gantt {{
            min-height: 400px;
        }}
        
        h2 {{
            margin-top: 0;
            color: #333;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="test-coverage-tab">
        <h1>Test Coverage Intelligence</h1>
        
        <div class="dashboard-grid">
            <div class="chart-container coverage-heatmap">
                <h2>Coverage Heatmap</h2>
                <div id="heatmap"></div>
            </div>
            
            <div class="chart-container priority-matrix">
                <h2>Priority Matrix</h2>
                <div id="matrix"></div>
            </div>
            
            <div class="chart-container roadmap-gantt">
                <h2>Roadmap Timeline</h2>
                <div id="gantt"></div>
            </div>
            
            <div class="chart-container domain-table">
                <h2>Domain Coverage</h2>
                <div id="table"></div>
            </div>
        </div>
        
        <div class="quick-wins">
            <h2>Quick Wins</h2>
            <div id="quick-wins-cards"></div>
        </div>
    </div>
    
    <script>
        // Data
        const heatmapData = {json.dumps(heatmap)};
        const matrixData = {json.dumps(matrix)};
        const ganttData = {json.dumps(gantt)};
        const tableData = {json.dumps(table)};
        const quickWinsData = {json.dumps(quick_wins)};
        
        // Render visualizations
        console.log('Dashboard data loaded', {{
            heatmap: heatmapData.nodes.length,
            matrix: matrixData.points.length,
            gantt: ganttData.milestones.length
        }});
    </script>
</body>
</html>
"""
        return html
    
    # ========================================================================
    # Export Functionality
    # ========================================================================
    
    def export_to_pdf(self, roadmap_data: Dict) -> bytes:
        """
        Export roadmap to PDF.
        
        Args:
            roadmap_data: Roadmap with milestones
        
        Returns:
            PDF bytes
        """
        # Simplified PDF generation (in production, use reportlab or weasyprint)
        pdf_content = b'%PDF-1.4\n'
        pdf_content += b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        pdf_content += b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
        pdf_content += b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n'
        pdf_content += b'xref\n0 4\n'
        pdf_content += b'trailer\n<< /Size 4 /Root 1 0 R >>\n'
        pdf_content += b'startxref\n%%EOF\n'
        
        return pdf_content
    
    def export_table_to_csv(self, coverage_data: Dict) -> str:
        """
        Export domain table to CSV.
        
        Args:
            coverage_data: Coverage data with domains
        
        Returns:
            CSV string
        """
        table = self.generate_domain_table(coverage_data)
        
        # CSV header
        csv_lines = [",".join(table["columns"])]
        
        # CSV rows
        for row in table["rows"]:
            values = [str(row[col]) for col in table["columns"]]
            csv_lines.append(",".join(values))
        
        return "\n".join(csv_lines)
    
    # ========================================================================
    # Interactive Features
    # ========================================================================
    
    def get_file_drilldown(self, filepath: str, coverage_data: Dict) -> Dict:
        """
        Get drill-down details for a file.
        
        Args:
            filepath: File path to drill down
            coverage_data: Coverage data
        
        Returns:
            Drill-down data with untested methods
        """
        file_info = next(
            (f for f in coverage_data.get("coverage_by_file", []) if f["file"] == filepath),
            None
        )
        
        if not file_info:
            return {"file": filepath, "error": "File not found"}
        
        return {
            "file": filepath,
            "coverage_details": {
                "line_coverage": file_info.get("line_coverage", 0),
                "loc": file_info.get("loc", 0),
                "tested": file_info.get("tested", False)
            },
            "untested_methods": []  # Would require more detailed analysis
        }
    
    def generate_test_skeleton_from_task(self, task_name: str, language: str) -> str:
        """
        Generate test skeleton from task name.
        
        Args:
            task_name: Task name (e.g., "Test ClassName.MethodName")
            language: Target language (python, csharp, javascript)
        
        Returns:
            Test skeleton code
        """
        # Extract class and method from task name
        if "." in task_name:
            parts = task_name.replace("Test ", "").split(".")
            class_name = parts[0] if len(parts) > 0 else "MyClass"
            method_name = parts[1] if len(parts) > 1 else "MyMethod"
        else:
            class_name = "MyClass"
            method_name = task_name.replace("Test ", "")
        
        if language.lower() == "python":
            return f'''import pytest

def test_{method_name.lower()}():
    """Test {class_name}.{method_name}."""
    # TODO: Implement test
    pass
'''
        elif language.lower() in ["csharp", "c#"]:
            return f'''using Xunit;

public class {class_name}Tests
{{
    [Fact]
    public void Test{method_name}()
    {{
        // TODO: Implement test
    }}
}}
'''
        else:
            return f"// Test skeleton for {language} not implemented"
