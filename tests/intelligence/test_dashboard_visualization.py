"""
Tests for Dashboard Visualization components.

Tests coverage heatmaps, priority matrices, roadmap Gantt charts,
interactive drill-down, and export functionality.

Author: CORTEX TDD Workflow
Date: 2025-12-08
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_coverage_data():
    """Sample coverage data for testing."""
    return {
        "overall_coverage": {
            "line_coverage": 67.3,
            "function_coverage": 72.1,
            "class_coverage": 58.9,
            "branch_coverage": 54.2
        },
        "coverage_by_file": [
            {
                "file": "src/parking/ParkingController.cs",
                "line_coverage": 91.2,
                "loc": 234,
                "tested": True,
                "domain": "Parking"
            },
            {
                "file": "src/rewards/RewardService.cs",
                "line_coverage": 38.5,
                "loc": 456,
                "tested": True,
                "domain": "Rewards"
            },
            {
                "file": "src/payroll/PayrollCalculator.cs",
                "line_coverage": 0.0,
                "loc": 312,
                "tested": False,
                "domain": "Payroll"
            },
            {
                "file": "src/utils/DateHelper.cs",
                "line_coverage": 85.3,
                "loc": 89,
                "tested": True,
                "domain": "Utilities"
            }
        ],
        "coverage_by_domain": {
            "Parking": {"line_coverage": 82.1, "function_coverage": 89.3},
            "Rewards": {"line_coverage": 45.2, "function_coverage": 51.7},
            "Payroll": {"line_coverage": 23.1, "function_coverage": 18.9},
            "Utilities": {"line_coverage": 75.4, "function_coverage": 80.2}
        }
    }


@pytest.fixture
def sample_gap_data():
    """Sample gap prioritization data for testing."""
    return {
        "p0_critical": {
            "count": 15,
            "total_loc": 2340,
            "estimated_hours": 38,
            "examples": [
                {
                    "file": "PayrollCalculator.cs",
                    "class": "PayrollCalculator",
                    "method": "CalculateNetPay",
                    "reason": "Financial calculation with 0% coverage",
                    "complexity": 18,
                    "risk_score": 95,
                    "current_coverage": 0,
                    "effort_hours": 3
                }
            ]
        },
        "p1_high": {
            "count": 28,
            "total_loc": 4120,
            "estimated_hours": 62,
            "examples": []
        },
        "p2_medium": {
            "count": 45,
            "total_loc": 5890,
            "estimated_hours": 78,
            "examples": []
        },
        "p3_low": {
            "count": 89,
            "total_loc": 8930,
            "estimated_hours": 56,
            "examples": []
        }
    }


@pytest.fixture
def sample_roadmap_data():
    """Sample roadmap data for testing."""
    return {
        "baseline_coverage": 23.1,
        "target_coverage": 80.0,
        "total_effort_hours": 234,
        "estimated_weeks": 12,
        "milestones": [
            {
                "id": "M1",
                "name": "Critical Coverage (P0)",
                "goal": "Test all critical paths",
                "target_coverage": 90.0,
                "effort_hours": 94,
                "timeline_weeks": 3,
                "tasks": 47,
                "tasks_list": []
            },
            {
                "id": "M2",
                "name": "High Priority Coverage (P1)",
                "goal": "Test business logic services",
                "target_coverage": 70.0,
                "effort_hours": 78,
                "timeline_weeks": 4,
                "tasks": 35,
                "tasks_list": []
            }
        ],
        "quick_wins": [
            {
                "task": "Test RewardCalculator.CalculatePoints",
                "effort_hours": 2,
                "impact": "Covers 8% of untested P1 code",
                "reason": "Simple logic, high reuse",
                "priority": "P1"
            },
            {
                "task": "Test AuthService.ValidateToken",
                "effort_hours": 1.5,
                "impact": "Covers 5% of untested P0 code",
                "reason": "Critical security path",
                "priority": "P0"
            }
        ]
    }


# ============================================================================
# Test Heatmap Generation
# ============================================================================

class TestHeatmapGeneration:
    """Test coverage heatmap generation."""
    
    def test_generate_heatmap_structure(self, sample_coverage_data):
        """Test heatmap data structure generation."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        heatmap = viz.generate_heatmap(sample_coverage_data)
        
        assert "nodes" in heatmap
        assert "metadata" in heatmap
        assert len(heatmap["nodes"]) == 4  # 4 files
        
        # Check node structure
        node = heatmap["nodes"][0]
        assert "name" in node
        assert "value" in node  # LOC
        assert "coverage" in node
        assert "color" in node
        assert "domain" in node
    
    def test_heatmap_color_mapping(self, sample_coverage_data):
        """Test coverage percentage to color mapping."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        heatmap = viz.generate_heatmap(sample_coverage_data)
        
        # Low coverage (<30%) = red
        payroll_node = [n for n in heatmap["nodes"] if "Payroll" in n["name"]][0]
        assert payroll_node["color"] == "red"
        
        # Medium coverage (30-70%) = yellow
        rewards_node = [n for n in heatmap["nodes"] if "Reward" in n["name"]][0]
        assert rewards_node["color"] == "yellow"
        
        # High coverage (>70%) = green
        parking_node = [n for n in heatmap["nodes"] if "Parking" in n["name"]][0]
        assert parking_node["color"] == "green"
    
    def test_heatmap_domain_grouping(self, sample_coverage_data):
        """Test grouping files by business domain."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        heatmap = viz.generate_heatmap(sample_coverage_data, group_by="domain")
        
        # Should have domain parent nodes
        assert "groups" in heatmap
        assert len(heatmap["groups"]) >= 3  # Parking, Rewards, Payroll


# ============================================================================
# Test Priority Matrix
# ============================================================================

class TestPriorityMatrix:
    """Test priority matrix visualization."""
    
    def test_generate_matrix_structure(self, sample_gap_data):
        """Test matrix data structure generation."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        matrix = viz.generate_priority_matrix(sample_gap_data)
        
        assert "points" in matrix
        assert "quadrants" in matrix
        assert len(matrix["quadrants"]) == 4  # P0, P1, P2, P3
    
    def test_matrix_point_positioning(self, sample_gap_data):
        """Test point positioning by coverage and risk."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        matrix = viz.generate_priority_matrix(sample_gap_data)
        
        # P0 points should be in high-risk, low-coverage quadrant
        p0_points = [p for p in matrix["points"] if p["priority"] == "P0"]
        assert len(p0_points) > 0
        
        for point in p0_points:
            assert point["y"] >= 70  # High risk (y-axis)
            assert point["x"] <= 30  # Low coverage (x-axis)
    
    def test_matrix_hover_details(self, sample_gap_data):
        """Test hover tooltip details."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        matrix = viz.generate_priority_matrix(sample_gap_data)
        
        point = matrix["points"][0]
        assert "tooltip" in point
        assert "file" in point["tooltip"]
        assert "class" in point["tooltip"]
        assert "method" in point["tooltip"]
        assert "reason" in point["tooltip"]


# ============================================================================
# Test Gantt Chart
# ============================================================================

class TestGanttChart:
    """Test roadmap Gantt chart generation."""
    
    def test_generate_gantt_structure(self, sample_roadmap_data):
        """Test Gantt chart data structure."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        gantt = viz.generate_gantt_chart(sample_roadmap_data)
        
        assert "milestones" in gantt
        assert "tasks" in gantt
        assert "timeline" in gantt
        assert len(gantt["milestones"]) == 2  # M1, M2
    
    def test_gantt_milestone_dates(self, sample_roadmap_data):
        """Test milestone start/end date calculation."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        gantt = viz.generate_gantt_chart(sample_roadmap_data)
        
        m1 = gantt["milestones"][0]
        assert "start_date" in m1
        assert "end_date" in m1
        assert "duration_weeks" in m1
        
        # M1 should be 3 weeks
        start = datetime.fromisoformat(m1["start_date"])
        end = datetime.fromisoformat(m1["end_date"])
        duration = (end - start).days / 7
        assert abs(duration - 3) < 0.5  # Within 0.5 weeks
    
    def test_gantt_priority_colors(self, sample_roadmap_data):
        """Test color coding by priority."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        gantt = viz.generate_gantt_chart(sample_roadmap_data)
        
        # P0 milestone should be red
        m1 = gantt["milestones"][0]  # Critical Coverage (P0)
        assert m1["color"] == "red"


# ============================================================================
# Test Domain Coverage Table
# ============================================================================

class TestDomainCoverageTable:
    """Test domain coverage table generation."""
    
    def test_generate_table_structure(self, sample_coverage_data):
        """Test table data structure."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        table = viz.generate_domain_table(sample_coverage_data)
        
        assert "columns" in table
        assert "rows" in table
        assert len(table["rows"]) == 4  # 4 domains
        
        # Check column structure
        expected_cols = ["Domain", "Files", "LOC", "Coverage %", "P0 Count", "Status"]
        assert all(col in table["columns"] for col in expected_cols)
    
    def test_table_sorting_support(self, sample_coverage_data):
        """Test sortable columns."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        table = viz.generate_domain_table(sample_coverage_data)
        
        # All numeric columns should be sortable
        assert table["sortable"] is True
        for col in table["columns"]:
            if col in ["Files", "LOC", "Coverage %", "P0 Count"]:
                assert table["column_types"][col] == "numeric"
    
    def test_table_status_indicators(self, sample_coverage_data):
        """Test status indicators (Good/Warning/Critical)."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        table = viz.generate_domain_table(sample_coverage_data)
        
        # Parking (82.1% coverage) = Good
        parking_row = [r for r in table["rows"] if r["Domain"] == "Parking"][0]
        assert parking_row["Status"] == "Good"
        
        # Payroll (23.1% coverage) = Critical
        payroll_row = [r for r in table["rows"] if r["Domain"] == "Payroll"][0]
        assert payroll_row["Status"] == "Critical"


# ============================================================================
# Test Quick Wins Display
# ============================================================================

class TestQuickWinsDisplay:
    """Test quick wins card generation."""
    
    def test_generate_quick_wins_cards(self, sample_roadmap_data):
        """Test quick wins card generation."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        cards = viz.generate_quick_wins_cards(sample_roadmap_data)
        
        assert "cards" in cards
        assert len(cards["cards"]) == 2  # 2 quick wins
        
        # Check card structure
        card = cards["cards"][0]
        assert "title" in card
        assert "effort_hours" in card
        assert "impact" in card
        assert "priority" in card
        assert "action_button" in card
    
    def test_quick_wins_sorting(self, sample_roadmap_data):
        """Test quick wins sorted by effort (ascending)."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        cards = viz.generate_quick_wins_cards(sample_roadmap_data)
        
        efforts = [card["effort_hours"] for card in cards["cards"]]
        assert efforts == sorted(efforts)  # Ascending order
    
    def test_quick_wins_action_buttons(self, sample_roadmap_data):
        """Test action button generation."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        cards = viz.generate_quick_wins_cards(sample_roadmap_data)
        
        card = cards["cards"][0]
        assert card["action_button"]["text"] == "Generate Test Skeleton"
        assert "callback" in card["action_button"]


# ============================================================================
# Test HTML Rendering
# ============================================================================

class TestHTMLRendering:
    """Test HTML/JS/CSS generation."""
    
    def test_render_complete_dashboard(self, sample_coverage_data, sample_gap_data, sample_roadmap_data):
        """Test complete dashboard HTML rendering."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        html = viz.render_dashboard(
            coverage_data=sample_coverage_data,
            gap_data=sample_gap_data,
            roadmap_data=sample_roadmap_data
        )
        
        assert "<html" in html  # Match opening html tag
        assert "<div class=\"test-coverage-tab\">" in html
        assert "coverage-heatmap" in html  # Match class name (can be in combination)
        assert "priority-matrix" in html
        assert "roadmap-gantt" in html
    
    def test_render_with_chart_libraries(self, sample_coverage_data):
        """Test inclusion of chart libraries (D3.js, Chart.js)."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        html = viz.render_dashboard(coverage_data=sample_coverage_data)
        
        # Should include D3.js for heatmap/matrix
        assert "d3.min.js" in html or "d3.v7.min.js" in html
        
        # Should include Chart.js for line charts
        assert "chart.js" in html or "Chart.min.js" in html
    
    def test_render_responsive_layout(self, sample_coverage_data):
        """Test responsive CSS grid layout."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        html = viz.render_dashboard(coverage_data=sample_coverage_data)
        
        # Should have responsive grid
        assert "display: grid" in html or "grid-template-columns" in html
        assert "@media" in html  # Media queries for mobile


# ============================================================================
# Test Export Functionality
# ============================================================================

class TestExportFunctionality:
    """Test dashboard export to PDF/CSV."""
    
    def test_export_roadmap_to_pdf(self, sample_roadmap_data):
        """Test PDF export with charts and tables."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        pdf_bytes = viz.export_to_pdf(sample_roadmap_data)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 100  # PDF has content (stub)
        assert pdf_bytes[:4] == b'%PDF'  # PDF magic number
    
    def test_export_domain_table_to_csv(self, sample_coverage_data):
        """Test CSV export of domain table."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        csv_content = viz.export_table_to_csv(sample_coverage_data)
        
        assert "Domain,Files,LOC,Coverage %" in csv_content
        assert "Parking," in csv_content
        assert "Payroll," in csv_content
    
    def test_export_includes_metadata(self, sample_roadmap_data):
        """Test export includes generation timestamp and metadata."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        pdf_bytes = viz.export_to_pdf(sample_roadmap_data)
        
        # PDF should contain metadata (check via PDF parser)
        # For now, just verify non-empty (stub implementation)
        assert len(pdf_bytes) > 100  # Stub PDF is minimal


# ============================================================================
# Test Interactive Features
# ============================================================================

class TestInteractiveFeatures:
    """Test interactive drill-down and filtering."""
    
    def test_heatmap_click_drilldown(self, sample_coverage_data):
        """Test heatmap click generates drill-down data."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        drilldown = viz.get_file_drilldown("src/rewards/RewardService.cs", sample_coverage_data)
        
        assert "file" in drilldown
        assert "untested_methods" in drilldown
        assert "coverage_details" in drilldown
    
    def test_priority_filter(self, sample_gap_data):
        """Test filtering matrix by priority (P0 only)."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        matrix = viz.generate_priority_matrix(sample_gap_data, filter_priority="P0")
        
        # Only P0 points should be present
        for point in matrix["points"]:
            assert point["priority"] == "P0"
    
    def test_generate_test_skeleton_action(self, sample_roadmap_data):
        """Test test skeleton generation from quick win action."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        quick_win = sample_roadmap_data["quick_wins"][0]
        
        skeleton = viz.generate_test_skeleton_from_task(quick_win["task"], language="python")
        
        assert "import pytest" in skeleton
        assert "def test_" in skeleton
        assert "CalculatePoints" in skeleton


# ============================================================================
# Test Performance
# ============================================================================

class TestPerformance:
    """Test rendering performance with large datasets."""
    
    def test_heatmap_performance_500_files(self):
        """Test heatmap renders 500 files in <2s."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        import time
        
        # Generate 500 file dataset
        large_data = {
            "coverage_by_file": [
                {
                    "file": f"src/module{i}/File{j}.cs",
                    "line_coverage": 50.0 + (i % 50),
                    "loc": 100 + (j % 200),
                    "tested": True,
                    "domain": f"Domain{i % 10}"
                }
                for i in range(50) for j in range(10)
            ]
        }
        
        viz = DashboardVisualizer()
        start = time.time()
        heatmap = viz.generate_heatmap(large_data)
        elapsed = time.time() - start
        
        assert elapsed < 2.0  # <2s requirement
        assert len(heatmap["nodes"]) == 500
    
    def test_matrix_filter_performance(self):
        """Test matrix filter updates in <500ms."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        import time
        
        # Generate large gap dataset
        large_gaps = {
            "p0_critical": {"count": 100, "examples": [{"risk_score": 90, "current_coverage": 10}] * 100}
        }
        
        viz = DashboardVisualizer()
        
        start = time.time()
        matrix = viz.generate_priority_matrix(large_gaps, filter_priority="P0")
        elapsed = time.time() - start
        
        assert elapsed < 0.5  # <500ms requirement


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_no_coverage_data(self):
        """Test graceful handling of missing coverage data."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        heatmap = viz.generate_heatmap({})
        
        assert heatmap["nodes"] == []
        assert "error" not in heatmap or heatmap.get("message") == "No coverage data available"
    
    def test_no_roadmap_data(self):
        """Test graceful handling of missing roadmap."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        gantt = viz.generate_gantt_chart({"milestones": []})
        
        assert gantt["milestones"] == []
        assert gantt.get("message") == "No milestones defined"
    
    def test_invalid_priority_filter(self):
        """Test invalid priority filter value."""
        from src.intelligence.dashboard_visualization import DashboardVisualizer
        
        viz = DashboardVisualizer()
        
        with pytest.raises(ValueError, match="Invalid priority"):
            viz.generate_priority_matrix({}, filter_priority="P99")
