"""Plan registry with index.yaml SSOT pattern and CRUD operations."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel

from cortex.models.plan_models import PlanSpec


class PlanSummary(BaseModel):
    """Summary of a plan for listing/search."""

    plan_id: str
    title: str
    status: str
    priority: str
    roi_score: float
    created: Optional[str] = None
    completed: Optional[str] = None


class PlanRegistry:
    """Plan registry with index.yaml SSOT management."""

    def __init__(self, registry_path: str = "cortex-registry/planning") -> None:
        """Initialize plan registry."""
        self.registry_path = Path(registry_path)
        self.index_path = self.registry_path / "index.yaml"
        self.active_path = self.registry_path / "active"
        self.completed_path = self.registry_path / "completed"
        self.templates_path = self.registry_path / "templates"

        # Ensure directories exist
        self.active_path.mkdir(parents=True, exist_ok=True)
        self.completed_path.mkdir(parents=True, exist_ok=True)
        self.templates_path.mkdir(parents=True, exist_ok=True)

        self._index: Dict[str, Any] = {}

    def _load_index(self) -> Dict[str, Any]:
        """Load index.yaml into memory."""
        if self._index:
            return self._index

        if not self.index_path.exists():
            self._init_index()

        with open(self.index_path, "r") as f:
            loaded = yaml.safe_load(f)
            if loaded:
                self._index = loaded
            else:
                self._index = {}

        return self._index

    def _init_index(self) -> None:
        """Initialize empty index.yaml."""
        index: Dict[str, Any] = {
            "version": "1.0",
            "registry_name": "planning",
            "description": "Planning registry with index.yaml SSOT pattern",
            "last_updated": datetime.utcnow().isoformat(),
            "active_plans": [],
            "completed_plans": {},
        }
        with open(self.index_path, "w") as f:
            yaml.dump(index, f, default_flow_style=False)
        self._index = index

    def _save_index(self) -> None:
        """Save index to index.yaml."""
        self._index["last_updated"] = datetime.utcnow().isoformat()
        with open(self.index_path, "w") as f:
            yaml.dump(self._index, f, default_flow_style=False)

    def create_plan(
        self,
        plan_spec: PlanSpec,
        plan_id: Optional[str] = None,
    ) -> str:
        """Create a new plan."""
        plan_id = plan_id or plan_spec.metadata.phase_id
        plan_path = self.active_path / plan_id / "plan.yaml"

        if plan_path.exists():
            raise ValueError(f"Plan {plan_id} already exists")

        # Create plan directory and file
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        spec_dict = plan_spec.model_dump(mode="json")
        with open(plan_path, "w") as f:
            yaml.dump(spec_dict, f, default_flow_style=False)

        # Update index
        index = self._load_index()
        index["active_plans"].append(
            {
                "id": plan_id,
                "name": plan_spec.metadata.title,
                "file": f"active/{plan_id}/plan.yaml",
                "created": datetime.utcnow().isoformat(),
                "status": plan_spec.metadata.status.value,
                "priority": "P0",
                "roi_score": plan_spec.metadata.roi_score,
            }
        )
        self._save_index()

        return plan_id

    def get_plan(self, plan_id: str) -> PlanSpec:
        """Get plan specification by ID."""
        plan_path = self.active_path / plan_id / "plan.yaml"

        if not plan_path.exists():
            # Try completed
            for year_dir in self.completed_path.iterdir():
                if year_dir.is_dir():
                    cand = year_dir / plan_id / "plan.yaml"
                    if cand.exists():
                        plan_path = cand
                        break

        if not plan_path.exists():
            raise FileNotFoundError(f"Plan {plan_id} not found")

        with open(plan_path, "r") as f:
            data = yaml.safe_load(f)

        return PlanSpec(**data)

    def list_plans(
        self,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[PlanSummary]:
        """List plans with optional filters."""
        index = self._load_index()
        results: List[PlanSummary] = []

        for plan_entry in index.get("active_plans", []):
            plan_id = plan_entry["id"]

            # Apply filters
            if status_filter and plan_entry.get("status") != status_filter:
                continue
            if priority_filter and plan_entry.get("priority") != priority_filter:
                continue
            if search_query:
                name = plan_entry.get("name", "").lower()
                if search_query.lower() not in name:
                    continue

            results.append(
                PlanSummary(
                    plan_id=plan_id,
                    title=plan_entry.get("name", "Untitled"),
                    status=plan_entry.get("status", "pending"),
                    priority=plan_entry.get("priority", "P3"),
                    roi_score=plan_entry.get("roi_score", 0.0),
                    created=plan_entry.get("created"),
                )
            )

        return results

    def update_plan_status(self, plan_id: str, new_status: str) -> None:
        """Update plan status."""
        index = self._load_index()

        for plan_entry in index.get("active_plans", []):
            if plan_entry["id"] == plan_id:
                plan_entry["status"] = new_status
                break

        self._save_index()

    def archive_plan(self, plan_id: str, completion_notes: Optional[str] = None) -> str:
        """Archive a completed plan."""
        plan_path = self.active_path / plan_id
        if not plan_path.exists():
            raise FileNotFoundError(f"Plan {plan_id} not found")

        # Determine archive year
        year = datetime.utcnow().year
        archive_path = self.completed_path / str(year) / plan_id

        # Create archive directory and move files
        archive_path.mkdir(parents=True, exist_ok=True)
        for file in plan_path.iterdir():
            dest = archive_path / file.name
            if file.is_file():
                file.rename(dest)

        # Clean up empty directory
        try:
            if not any(plan_path.iterdir()):
                plan_path.rmdir()
        except (FileNotFoundError, OSError):
            pass

        # Update index
        index = self._load_index()
        index["active_plans"] = [p for p in index["active_plans"] if p["id"] != plan_id]
        if str(year) not in index.get("completed_plans", {}):
            if "completed_plans" not in index:
                index["completed_plans"] = {}
            index["completed_plans"][str(year)] = []
        index["completed_plans"][str(year)].append(
            {
                "id": plan_id,
                "archived": datetime.utcnow().isoformat(),
            }
        )
        self._save_index()

        return str(archive_path)

    def search_plans(self, query: str) -> List[PlanSummary]:
        """Search plans by keyword."""
        return self.list_plans(search_query=query)

    def generate_plans_json(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate plans.json for viewer frontend."""
        plans = self.list_plans()

        data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_plans": len(plans),
            "plans": [p.model_dump() for p in plans],
        }

        if output_path:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w") as f:
                json.dump(data, f, indent=2)

        return data
