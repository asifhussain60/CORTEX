"""
Dashboard Generator - Real-time Plan Visualization

Generates plan-summary.json from index.yaml and updates dashboard HTML
with current statistics for Phase 25 PLAN MODE visualization.

AC-ID: PHASE-25-STAGE-2-001
Authority: phase-25-plan-mode-cortex-architect.yaml
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class PhaseSummary:
    """Summary of a single phase for dashboard display."""
    id: str
    name: str
    status: str
    priority: str
    progress: str = "0%"
    description: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "priority": self.priority,
            "progress": self.progress,
            "description": self.description,
        }


@dataclass
class DashboardData:
    """Complete dashboard data structure."""
    total_phases: int
    active_phases: int
    completed_phases: int
    completion_rate: float
    phases: List[PhaseSummary] = field(default_factory=list)
    in_progress_count: int = 0
    planned_count: int = 0
    last_updated: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_phases": self.total_phases,
            "active_phases": self.active_phases,
            "completed_phases": self.completed_phases,
            "completion_rate": self.completion_rate,
            "in_progress_count": self.in_progress_count,
            "planned_count": self.planned_count,
            "phases": [p.to_dict() for p in self.phases],
            "last_updated": self.last_updated or datetime.now().isoformat(),
        }


@dataclass
class DashboardSyncResult:
    """Result of dashboard sync operation."""
    success: bool
    error_message: str = ""
    json_updated: bool = False
    html_updated: bool = False


class DashboardGenerator:
    """
    Generates and updates dashboard data for CORTEX master plan.

    Responsibilities:
    - Generate plan-summary.json from index.yaml
    - Update dashboard HTML with current statistics
    - Verify sync between registry, implementation, and dashboard
    - Provide real-time plan visualization

    Usage:
        generator = DashboardGenerator(registry_root="cortex-registry/_cortex-master")
        result = generator.sync_dashboard()

        if result.success:
            print("Dashboard synced successfully")
    """

    # HTML template placeholders
    PLACEHOLDERS = {
        "TOTAL_PHASES": "{{TOTAL_PHASES}}",
        "ACTIVE_PHASES": "{{ACTIVE_PHASES}}",
        "COMPLETED_PHASES": "{{COMPLETED_PHASES}}",
        "COMPLETION_RATE": "{{COMPLETION_RATE}}",
        "IN_PROGRESS_COUNT": "{{IN_PROGRESS_COUNT}}",
        "PLANNED_COUNT": "{{PLANNED_COUNT}}",
        "LAST_UPDATED": "{{LAST_UPDATED}}",
    }

    def __init__(self, registry_root: str = "cortex-registry/_cortex-master"):
        """
        Initialize DashboardGenerator.

        Args:
            registry_root: Path to master registry root
        """
        self.registry_root = Path(registry_root)
        self.index_path = self.registry_root / "index.yaml"
        self.dashboard_dir = self.registry_root / "dashboard"
        self.dashboard_data_dir = self.dashboard_dir / "data"
        self.dashboard_data_path = self.dashboard_data_dir / "plan-summary.json"
        self.dashboard_html_path = self.dashboard_dir / "index.html"

    def generate_dashboard_data(self) -> DashboardData:
        """
        Generate dashboard data from index.yaml.

        Returns:
            DashboardData with statistics and phase summaries
        """
        # Load index.yaml
        index_data = self._load_index()

        # Extract statistics
        stats = index_data.get("statistics", {})
        total_phases = stats.get("total_phases", 0)
        active_phases = stats.get("active_phases", 0)
        completed_phases = stats.get("completed_phases", 0)

        # Calculate completion rate
        completion_rate = (completed_phases / total_phases * 100) if total_phases > 0 else 0.0

        # Process active phases
        phases = []
        in_progress_count = 0
        planned_count = 0

        for phase_data in index_data.get("active_phases", []):
            phase = PhaseSummary(
                id=phase_data.get("id", ""),
                name=phase_data.get("name", ""),
                status=phase_data.get("status", "planned"),
                priority=phase_data.get("priority", "P1"),
                progress=phase_data.get("progress", "0%"),
                description=phase_data.get("description", ""),
            )
            phases.append(phase)

            # Count by status
            if phase.status == "in-progress":
                in_progress_count += 1
            elif phase.status == "planned":
                planned_count += 1

        return DashboardData(
            total_phases=total_phases,
            active_phases=active_phases,
            completed_phases=completed_phases,
            completion_rate=round(completion_rate, 1),
            phases=phases,
            in_progress_count=in_progress_count,
            planned_count=planned_count,
            last_updated=datetime.now().isoformat(),
        )

    def save_dashboard_json(self, dashboard_data: DashboardData) -> None:
        """
        Save dashboard data to plan-summary.json.

        Args:
            dashboard_data: Dashboard data to save
        """
        # Ensure data directory exists
        self.dashboard_data_dir.mkdir(parents=True, exist_ok=True)

        # Write JSON
        with open(self.dashboard_data_path, 'w') as f:
            json.dump(dashboard_data.to_dict(), f, indent=2)

    def to_json(self, dashboard_data: DashboardData) -> str:
        """
        Convert dashboard data to JSON string.

        Args:
            dashboard_data: Dashboard data to convert

        Returns:
            JSON string
        """
        return json.dumps(dashboard_data.to_dict(), indent=2)

    def update_html_statistics(self, html_content: str, dashboard_data: DashboardData) -> str:
        """
        Update HTML template with current statistics.

        Args:
            html_content: Original HTML content with placeholders
            dashboard_data: Dashboard data with current values

        Returns:
            Updated HTML content
        """
        updated_html = html_content

        # Replace placeholders
        replacements = {
            self.PLACEHOLDERS["TOTAL_PHASES"]: str(dashboard_data.total_phases),
            self.PLACEHOLDERS["ACTIVE_PHASES"]: str(dashboard_data.active_phases),
            self.PLACEHOLDERS["COMPLETED_PHASES"]: str(dashboard_data.completed_phases),
            self.PLACEHOLDERS["COMPLETION_RATE"]: f"{dashboard_data.completion_rate}%",
            self.PLACEHOLDERS["IN_PROGRESS_COUNT"]: str(dashboard_data.in_progress_count),
            self.PLACEHOLDERS["PLANNED_COUNT"]: str(dashboard_data.planned_count),
            self.PLACEHOLDERS["LAST_UPDATED"]: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        for placeholder, value in replacements.items():
            updated_html = updated_html.replace(placeholder, value)

        return updated_html

    def save_updated_html(self, html_content: str) -> None:
        """
        Save updated HTML to dashboard file.

        Args:
            html_content: Updated HTML content
        """
        # Ensure dashboard directory exists
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)

        # Write HTML
        with open(self.dashboard_html_path, 'w') as f:
            f.write(html_content)

    def sync_dashboard(self) -> DashboardSyncResult:
        """
        Sync dashboard with current registry state.

        Performs full sync:
        1. Generate dashboard data from index.yaml
        2. Save plan-summary.json
        3. Update dashboard HTML with statistics

        Returns:
            DashboardSyncResult with success status
        """
        result = DashboardSyncResult(success=False)

        try:
            # Step 1: Generate dashboard data
            dashboard_data = self.generate_dashboard_data()

            # Step 2: Save JSON
            self.save_dashboard_json(dashboard_data)
            result.json_updated = True

            # Step 3: Update HTML
            html_template = self._load_html_template()
            updated_html = self.update_html_statistics(html_template, dashboard_data)
            self.save_updated_html(updated_html)
            result.html_updated = True

            result.success = True

        except Exception as e:
            result.success = False
            result.error_message = str(e)

        return result

    def verify_sync(self) -> bool:
        """
        Verify dashboard is in sync with registry.

        Checks:
        - plan-summary.json exists and is parseable
        - dashboard HTML exists
        - Statistics match between JSON and HTML

        Returns:
            True if synced, False otherwise
        """
        try:
            # Check JSON exists and is valid
            json_data = self._load_dashboard_json()
            if not json_data:
                return False

            # Check HTML exists
            html_content = self._load_dashboard_html()
            if not html_content:
                return False

            # Basic consistency check - total_phases should be in HTML
            total_phases = json_data.get("total_phases", 0)
            if str(total_phases) not in html_content:
                return False

            return True

        except Exception:
            return False

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _load_index(self) -> Dict:
        """Load index.yaml."""
        if not self.index_path.exists():
            return {
                "active_phases": [],
                "statistics": {
                    "total_phases": 0,
                    "active_phases": 0,
                    "completed_phases": 0,
                }
            }

        with open(self.index_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def _load_html_template(self) -> str:
        """Load dashboard HTML template."""
        if not self.dashboard_html_path.exists():
            # Return basic template if file doesn't exist
            return """
<!DOCTYPE html>
<html>
<head>
    <title>CORTEX Master Plan Dashboard</title>
</head>
<body>
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{{TOTAL_PHASES}}</div>
            <div class="stat-label">Total Phases</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ACTIVE_PHASES}}</div>
            <div class="stat-label">Active</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{COMPLETED_PHASES}}</div>
            <div class="stat-label">Completed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{COMPLETION_RATE}}</div>
            <div class="stat-label">Completion Rate</div>
        </div>
    </div>
    <p>Last Updated: {{LAST_UPDATED}}</p>
</body>
</html>
"""

        with open(self.dashboard_html_path, 'r') as f:
            return f.read()

    def _load_dashboard_json(self) -> Optional[Dict]:
        """Load dashboard JSON data."""
        if not self.dashboard_data_path.exists():
            return None

        with open(self.dashboard_data_path, 'r') as f:
            return json.load(f)

    def _load_dashboard_html(self) -> Optional[str]:
        """Load dashboard HTML."""
        if not self.dashboard_html_path.exists():
            return None

        with open(self.dashboard_html_path, 'r') as f:
            return f.read()
