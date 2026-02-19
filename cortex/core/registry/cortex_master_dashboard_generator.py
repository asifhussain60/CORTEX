"""
CORTEX Master Dashboard Generator - Auto-Sync System

Automatically regenerates cortex-master plan-summary.json when:
1. Phase completions occur
2. Variance exceeds threshold (>10%)
3. Manual refresh requested

Integrates with cortex-architect.prompt.md autonomous continuation flow.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class CortexMasterDashboardGenerator:
    """
    Generator for cortex-master dashboard data with variance tracking.

    Reads cortex-registry/_cortex-master/index.yaml and generates
    dashboard/data/plan-summary.json with automatic variance detection.
    """

    VERSION = "1.0.0"

    def __init__(self, registry_path: Path):
        """
        Initialize generator with registry path.

        Args:
            registry_path: Path to cortex-registry/_cortex-master/
        """
        self.registry_path = Path(registry_path)
        self.index_path = self.registry_path / "index.yaml"
        self.dashboard_data_path = self.registry_path / "dashboard" / "data" / "plan-summary.json"
        self.variance_threshold = 10.0  # Default, overridden by config
        self.silent_sync_threshold = 20.0

    def load_registry_data(self) -> Dict[str, Any]:
        """
        Load registry data from index.yaml.

        Returns:
            Dictionary containing registry data

        Raises:
            FileNotFoundError: If index.yaml doesn't exist
        """
        if not self.index_path.exists():
            raise FileNotFoundError(f"Registry index not found: {self.index_path}")

        with open(self.index_path) as f:
            data = yaml.safe_load(f)

        # Load variance threshold from config if present
        if "dashboard" in data and "variance_threshold" in data["dashboard"]:
            self.variance_threshold = data["dashboard"]["variance_threshold"]

        return data

    def load_previous_dashboard_data(self) -> Optional[Dict[str, Any]]:
        """
        Load previous dashboard data for variance calculation.

        Returns:
            Previous dashboard data or None if doesn't exist
        """
        if not self.dashboard_data_path.exists():
            return None

        try:
            with open(self.dashboard_data_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def calculate_variance(self, previous_data: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate variance score between current and previous dashboard data.

        Variance factors:
        - Phase progress changes
        - Phase status changes (active → completed)
        - New phases added
        - Enhancement status changes

        Args:
            previous_data: Previous dashboard data (optional, loaded if None)

        Returns:
            Variance score (0-100 percentage)
        """
        if previous_data is None:
            previous_data = self.load_previous_dashboard_data()

        if previous_data is None:
            return 0.0  # No previous data = no variance

        current_registry = self.load_registry_data()
        variance_score = 0.0

        # Compare active phases progress
        # Previous data has "number" field (from dashboard)
        prev_active = {p.get("number", p.get("id", "")): p.get("progress", 0)
                      for p in previous_data.get("active_phases", [])}

        # Current registry has "id" field (from index.yaml)
        # Extract phase number from id like "phase-23" -> 23
        curr_active = {}
        for p in current_registry.get("active_phases", []):
            phase_id = p.get("id", "")
            if phase_id.startswith("phase-"):
                try:
                    phase_num = int(phase_id.split("-")[1])
                    curr_active[phase_num] = p.get("progress", 0)
                except (ValueError, IndexError):
                    pass

        # Calculate progress changes
        for phase_num, curr_progress in curr_active.items():
            prev_progress = prev_active.get(phase_num, 0)
            progress_delta = abs(curr_progress - prev_progress)
            variance_score += progress_delta / 10  # Weight progress changes

        # Detect phase completions (active → completed)
        prev_active_nums = set(prev_active.keys())
        curr_active_nums = set(curr_active.keys())
        completed_phases = prev_active_nums - curr_active_nums

        if completed_phases:
            variance_score += len(completed_phases) * 15  # High weight for completions

        # Detect new phases
        new_phases = curr_active_nums - prev_active_nums
        if new_phases:
            variance_score += len(new_phases) * 10

        # Cap at 100%
        return min(variance_score, 100.0)

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate complete dashboard data structure.

        Returns:
            Dashboard data dictionary ready for JSON serialization
        """
        registry = self.load_registry_data()
        previous_data = self.load_previous_dashboard_data()
        variance_score = self.calculate_variance(previous_data)

        # Count phases
        active_phases = registry.get("active_phases", [])
        completed_2026 = registry.get("completed_phases_2026", {}).get("phases", [])
        completed_2025 = registry.get("completed_phases_2025", {}).get("phases", [])

        # Extract phase numbers from completed files
        completed_phases_count = len(completed_2026) + len(completed_2025)

        # Calculate completion rate
        total_phases = len(active_phases) + completed_phases_count
        completion_rate = int((completed_phases_count / total_phases * 100)
                             if total_phases > 0 else 0)

        # Transform active phases to dashboard format
        dashboard_active_phases = []
        for p in active_phases:
            phase_id = p.get("id", "")
            # Extract number from "phase-23" -> 23
            phase_num = 0
            if phase_id.startswith("phase-"):
                try:
                    phase_num = int(phase_id.split("-")[1])
                except (ValueError, IndexError):
                    pass

            dashboard_active_phases.append({
                "number": phase_num,
                "name": p.get("name", ""),
                "status": p.get("status", "in-progress"),
                "progress": p.get("progress", 0),
                "start_date": p.get("started", ""),
                "estimated_completion": p.get("estimated_completion", "")
            })

        # Build dashboard data
        dashboard_data = {
            "metadata": {
                "version": self.VERSION,
                "last_updated": datetime.now().isoformat() + "Z",
                "variance_score": round(variance_score, 1),
                "variance_threshold": self.variance_threshold,
                "silent_sync": variance_score >= self.silent_sync_threshold
            },
            "statistics": {
                "total_phases": total_phases,
                "active_phases": len(active_phases),
                "completed_2026": len(completed_2026),
                "completed_2025": len(completed_2025),
                "completion_rate": completion_rate,
                "overall_status": "ON_TRACK" if completion_rate >= 80 else "ATTENTION_NEEDED"
            },
            "active_phases": dashboard_active_phases,
            "completed_phases_2026": [
                {"name": f.replace(".yaml", "").replace("-", " ").title(), "completion_date": ""}
                for f in completed_2026
            ],
            "active_enhancements": registry.get("active_enhancements", []),
            "roadmap": registry.get("roadmap", {}),
            "registry_config": {
                "auto_sync_enabled": registry.get("dashboard", {}).get("auto_sync", False),
                "variance_check_interval": registry.get("dashboard", {}).get("sync_interval_seconds", 300),
                "variance_threshold": self.variance_threshold
            }
        }

        return dashboard_data

    def save_dashboard_data(self, dashboard_data: Dict[str, Any]) -> Path:
        """
        Save dashboard data to plan-summary.json.

        Args:
            dashboard_data: Dashboard data dictionary

        Returns:
            Path to saved file
        """
        # Ensure directory exists
        self.dashboard_data_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON with pretty formatting
        with open(self.dashboard_data_path, "w") as f:
            json.dump(dashboard_data, f, indent=2)

        return self.dashboard_data_path

    def should_notify_user(self, variance: float) -> bool:
        """
        Determine if user should be notified of dashboard update.

        Notification logic:
        - variance < 10%: No notification (below threshold)
        - 10% <= variance < 20%: Notify user
        - variance >= 20%: Silent sync (no notification)

        Args:
            variance: Variance score

        Returns:
            True if user notification needed
        """
        return self.variance_threshold <= variance < self.silent_sync_threshold

    def generate(self) -> Dict[str, Any]:
        """
        Complete generation workflow: load → calculate → generate → save.

        Returns:
            Result dictionary with output_path, variance_score, timestamp
        """
        dashboard_data = self.generate_dashboard_data()
        output_path = self.save_dashboard_data(dashboard_data)

        result = {
            "output_path": str(output_path),
            "variance_score": dashboard_data["metadata"]["variance_score"],
            "timestamp": dashboard_data["metadata"]["last_updated"],
            "silent_sync": dashboard_data["metadata"]["silent_sync"],
            "notify_user": self.should_notify_user(dashboard_data["metadata"]["variance_score"])
        }

        return result


def regenerate_dashboard(registry_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Convenience function to regenerate dashboard from registry path.

    Args:
        registry_path: Path to cortex-registry/_cortex-master/
                      (defaults to standard location)

    Returns:
        Generation result dictionary
    """
    if registry_path is None:
        # Default to standard location
        registry_path = Path(__file__).parent.parent.parent / "cortex-registry" / "_cortex-master"

    generator = CortexMasterDashboardGenerator(registry_path)
    return generator.generate()


if __name__ == "__main__":
    # CLI execution
    import sys

    if len(sys.argv) > 1:
        registry_path = Path(sys.argv[1])
    else:
        registry_path = None

    result = regenerate_dashboard(registry_path)

    print(f"✅ Dashboard regenerated: {result['output_path']}")
    print(f"   Variance: {result['variance_score']}%")
    print(f"   Timestamp: {result['timestamp']}")

    if result["notify_user"]:
        print("   ⚠️  User notification: Variance above threshold")
    elif result["silent_sync"]:
        print("   🔕 Silent sync: High variance (>20%)")
