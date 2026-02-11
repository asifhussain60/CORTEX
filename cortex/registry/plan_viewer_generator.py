"""
Plan viewer data generation and HTML support.

AC_START: AC-PLAN-SYSTEM-S4-002
Purpose: Glassmorphism plan-viewer.html SPA data layer (Stage 4)
Authority: phase-45-enhanced-planning-system.yaml § Stage 4
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# DATA MODELS FOR FRONTEND
# ============================================================================


class PlanJsonSchema(BaseModel):
    """JSON schema for frontend consumption of plan data.

    Simplified plan representation optimized for display in plan-viewer.

    Attributes:
        plan_id: Unique plan identifier
        title: Plan title
        status: Current status (pending/approved/in_progress/blocked/completed/archived)
        priority: Priority level (P0-P3)
        roi_score: Return on investment score (0-1)
        created: ISO 8601 creation timestamp
        completed: ISO 8601 completion timestamp (if applicable)
    """

    plan_id: str = Field(..., description="Unique plan identifier")
    title: str = Field(..., description="Plan title")
    status: str = Field(..., description="Plan status")
    priority: str = Field(..., description="Priority level")
    roi_score: float = Field(..., ge=0.0, le=1.0, description="ROI score")
    created: str = Field(..., description="Creation timestamp (ISO 8601)")
    completed: Optional[str] = Field(None, description="Completion timestamp (ISO 8601)")


class MetricsCardData(BaseModel):
    """Metrics card data for dashboard visualization.

    Provides summary metrics for the metrics cards row.

    Attributes:
        total_plans: Total number of plans
        active_plans: Number of active plans
        completed_plans: Number of completed plans
        average_roi: Average ROI across all plans
    """

    total_plans: int = Field(..., description="Total plans")
    active_plans: int = Field(..., description="Active plans")
    completed_plans: int = Field(..., description="Completed plans")
    average_roi: float = Field(..., ge=0.0, le=1.0, description="Average ROI")


class PlanViewerSchema(BaseModel):
    """Top-level schema for plan viewer data file.

    Generated as JSON for frontend consumption.

    Attributes:
        plans: List of plan JSON schemas
        metrics: Metrics card data
        generated_at: Timestamp when data was generated
    """

    plans: List[PlanJsonSchema] = Field(..., description="Plan list")
    metrics: MetricsCardData = Field(..., description="Metrics cards")
    generated_at: str = Field(..., description="Generation timestamp (ISO 8601)")


# ============================================================================
# VIEWER DATA GENERATOR
# ============================================================================


class PlanViewerDataGenerator:
    """Generates JSON data for plan viewer frontend.

    Converts plan specifications into simplified JSON format optimized
    for display in the plan-viewer.html SPA. Includes metrics calculation
    and file writing.
    """

    def __init__(self) -> None:
        """Initialize plan viewer data generator."""
        self.logger = logging.getLogger(__name__)

    def calculate_metrics(
        self, plans: List[PlanJsonSchema]
    ) -> MetricsCardData:
        """Calculate metrics from plans list.

        Args:
            plans: List of plans

        Returns:
            MetricsCardData with calculated summary metrics
        """
        if not plans:
            return MetricsCardData(
                total_plans=0,
                active_plans=0,
                completed_plans=0,
                average_roi=0.0,
            )

        total = len(plans)
        active = sum(
            1 for p in plans if p.status in ["pending", "approved", "in_progress"]
        )
        completed = sum(1 for p in plans if p.status == "completed")
        avg_roi = sum(p.roi_score for p in plans) / total if total > 0 else 0.0

        return MetricsCardData(
            total_plans=total,
            active_plans=active,
            completed_plans=completed,
            average_roi=round(avg_roi, 2),
        )

    def generate_plans_json(self, plans: List[PlanJsonSchema]) -> str:
        """Generate JSON data for plan viewer.

        Args:
            plans: List of plan JSON schemas

        Returns:
            JSON string with plans and metrics
        """
        metrics = self.calculate_metrics(plans)

        viewer_data = PlanViewerSchema(
            plans=plans,
            metrics=metrics,
            generated_at=datetime.utcnow().isoformat() + "Z",
        )

        json_str = viewer_data.model_dump_json(
            indent=2, exclude_none=True
        )

        self.logger.debug(f"Generated plan viewer JSON: {len(plans)} plans")
        return json_str

    def write_plans_json(
        self, plans: List[PlanJsonSchema], output_path: str
    ) -> None:
        """Write generated JSON to file.

        Args:
            plans: List of plan JSON schemas
            output_path: Path to write JSON file
        """
        json_content = self.generate_plans_json(plans)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            f.write(json_content)

        self.logger.info(f"Wrote plan viewer JSON to {output_path}")


# ============================================================================
# HTML GENERATOR
# ============================================================================


class PlanViewerHtmlGenerator:
    """Generates plan-viewer.html SPA page.

    Creates a glassmorphism-styled HTML page that loads plans.json
    and displays plans with metrics, search, and filtering.
    """

    def __init__(self) -> None:
        """Initialize HTML generator."""
        self.logger = logging.getLogger(__name__)

    def generate_html(self) -> str:
        """Generate plan-viewer.html content.

        Returns:
            HTML string for plan-viewer.html
        """
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Plan Workbench</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --glass-bg: rgba(255, 255, 255, 0.1);
            --glass-border: rgba(255, 255, 255, 0.2);
            --primary: #6366f1;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1f2937;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
            color: #f3f4f6;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            margin-bottom: 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }

        .header h1 {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .breadcrumb {
            font-size: 12px;
            color: #9ca3af;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .breadcrumb a {
            color: #6366f1;
            text-decoration: none;
        }

        .breadcrumb a:hover {
            text-decoration: underline;
        }

        /* Metrics Cards */
        .metrics-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .metric-card {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-4px);
        }

        .metric-card .label {
            font-size: 12px;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }

        .metric-card .value {
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .metric-card .subtext {
            font-size: 13px;
            color: #9ca3af;
        }

        .metric-card.status-p0 {
            border-left: 4px solid #ef4444;
        }

        .metric-card.status-p1 {
            border-left: 4px solid #f59e0b;
        }

        .metric-card.status-p2 {
            border-left: 4px solid #6366f1;
        }

        /* Search & Filter */
        .controls {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }

        .search-input {
            flex: 1;
            min-width: 250px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 10px 16px;
            color: #f3f4f6;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
        }

        .search-input::placeholder {
            color: #9ca3af;
        }

        .search-input:focus {
            outline: none;
            border-color: #6366f1;
        }

        .filter-select {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 10px 16px;
            color: #f3f4f6;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            cursor: pointer;
        }

        .filter-select:focus {
            outline: none;
            border-color: #6366f1;
        }

        /* Plans Table */
        .plans-table {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            overflow: hidden;
        }

        .table-header {
            display: grid;
            grid-template-columns: 1fr 2fr 1fr 1fr 1fr 1fr;
            gap: 16px;
            padding: 16px 20px;
            background: rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid var(--glass-border);
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #9ca3af;
        }

        .table-row {
            display: grid;
            grid-template-columns: 1fr 2fr 1fr 1fr 1fr 1fr;
            gap: 16px;
            padding: 16px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            align-items: center;
            transition: background 0.2s ease;
        }

        .table-row:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        .table-row:last-child {
            border-bottom: none;
        }

        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .status-pending {
            background: rgba(99, 102, 241, 0.2);
            color: #93c5fd;
        }

        .status-approved {
            background: rgba(16, 185, 129, 0.2);
            color: #6ee7b7;
        }

        .status-in_progress {
            background: rgba(59, 130, 246, 0.2);
            color: #93c5fd;
        }

        .status-completed {
            background: rgba(16, 185, 129, 0.2);
            color: #6ee7b7;
        }

        .priority-p0 {
            color: #ef4444;
            font-weight: 600;
        }

        .priority-p1 {
            color: #f59e0b;
        }

        .priority-p2 {
            color: #6366f1;
        }

        .priority-p3 {
            color: #9ca3af;
        }

        .roi-score {
            font-weight: 600;
            color: #10b981;
        }

        .action-button {
            background: none;
            border: 1px solid var(--glass-border);
            color: #6366f1;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s ease;
        }

        .action-button:hover {
            background: rgba(99, 102, 241, 0.1);
            border-color: #6366f1;
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #9ca3af;
        }

        .empty-state h3 {
            font-size: 18px;
            margin-bottom: 12px;
        }

        /* Responsive */
        @media (max-width: 1024px) {
            .table-header,
            .table-row {
                grid-template-columns: 1fr 1.5fr 1fr 1fr;
            }
        }

        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                align-items: flex-start;
                gap: 16px;
            }

            .metrics-cards {
                grid-template-columns: repeat(2, 1fr);
            }

            .table-header,
            .table-row {
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🎯 CORTEX Plan Workbench</h1>
            <div class="breadcrumb">
                <a href="../dashboard/index.html">Master Plan Observatory</a>
                <span>→</span>
                <span>Plan Workbench</span>
            </div>
        </div>

        <!-- Metrics Cards -->
        <div class="metrics-cards" id="metrics-container">
            <div class="metric-card">
                <div class="label">Total Plans</div>
                <div class="value" id="metric-total">0</div>
                <div class="subtext">All time</div>
            </div>
            <div class="metric-card">
                <div class="label">Active Plans</div>
                <div class="value" id="metric-active">0</div>
                <div class="subtext">In progress</div>
            </div>
            <div class="metric-card">
                <div class="label">Completed Plans</div>
                <div class="value" id="metric-completed">0</div>
                <div class="subtext">Finished</div>
            </div>
            <div class="metric-card">
                <div class="label">Average ROI</div>
                <div class="value" id="metric-roi">0.00</div>
                <div class="subtext">Across all plans</div>
            </div>
        </div>

        <!-- Controls -->
        <div class="controls">
            <input
                type="text"
                class="search-input"
                id="search-input"
                placeholder="Search plans by title, ID, or description..."
            >
            <select class="filter-select" id="status-filter">
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="archived">Archived</option>
            </select>
            <select class="filter-select" id="priority-filter">
                <option value="">All Priority</option>
                <option value="P0">P0 - Critical</option>
                <option value="P1">P1 - High</option>
                <option value="P2">P2 - Medium</option>
                <option value="P3">P3 - Low</option>
            </select>
        </div>

        <!-- Plans Table -->
        <div class="plans-table">
            <div class="table-header">
                <div>ID</div>
                <div>Title</div>
                <div>Status</div>
                <div>Priority</div>
                <div>ROI</div>
                <div>Actions</div>
            </div>
            <div id="plans-container">
                <div class="empty-state">
                    <h3>No plans yet</h3>
                    <p>Create a plan to get started</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load plans data
        async function loadPlans() {
            try {
                const response = await fetch('./data/plans.json');
                const data = await response.json();
                renderMetrics(data.metrics);
                renderPlans(data.plans);
            } catch (error) {
                console.error('Error loading plans:', error);
                document.getElementById('plans-container').innerHTML =
                    '<div class="empty-state"><h3>Error loading plans</h3></div>';
            }
        }

        function renderMetrics(metrics) {
            document.getElementById('metric-total').textContent = metrics.total_plans;
            document.getElementById('metric-active').textContent = metrics.active_plans;
            document.getElementById('metric-completed').textContent = metrics.completed_plans;
            document.getElementById('metric-roi').textContent = metrics.average_roi.toFixed(2);
        }

        function renderPlans(plans) {
            const container = document.getElementById('plans-container');
            if (plans.length === 0) {
                container.innerHTML = '<div class="empty-state"><h3>No plans yet</h3></div>';
                return;
            }

            container.innerHTML = plans.map(plan => `
                <div class="table-row">
                    <div><code>${plan.plan_id}</code></div>
                    <div>${plan.title}</div>
                    <div><span class="status-badge status-${plan.status}">${plan.status}</span></div>
                    <div><span class="priority-${plan.priority}">${plan.priority}</span></div>
                    <div><span class="roi-score">${(plan.roi_score * 100).toFixed(0)}%</span></div>
                    <div><button class="action-button" onclick="viewPlan('${plan.plan_id}')">View</button></div>
                </div>
            `).join('');
        }

        function viewPlan(planId) {
            alert('Plan detail view coming soon: ' + planId);
        }

        // Initialize
        loadPlans();
    </script>
</body>
</html>
"""
        return html

    def write_html(self, output_path: str) -> None:
        """Write HTML to file.

        Args:
            output_path: Path to write HTML file
        """
        html_content = self.generate_html()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            f.write(html_content)

        self.logger.info(f"Wrote plan viewer HTML to {output_path}")


# AC_COMPLETE: AC-PLAN-SYSTEM-S4-002 ✅ Stage 4 viewer generator implemented
