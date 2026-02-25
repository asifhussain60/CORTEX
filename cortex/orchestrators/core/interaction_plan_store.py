"""
InteractionPlanStore — Persistent Plan Lifecycle Storage (Phase 00, D10).

Implements EA-011 Plan-First Execution with Persistent Memory.

All plan YAML files are written exclusively to cortex-registry/plans/:
  - pending/   → newly created plans (not yet approved)
  - approved/  → plans approved for execution
  - archive/{YYYY}/{MM}/  → completed/executed plans (never deleted)

Authority: Phase 00, D10 — EA-011
CORE-008: TDD — tests in tests/core/test_interaction_plan_store.py
CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-028: snake_case file naming
CORE-035: Single canonical implementation — no new Orchestrator classes

AC_START: AC-PLAN-STORE-D10-001
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class PlanState(Enum):
    """Lifecycle states for an interaction plan."""

    PENDING = "pending"
    APPROVED = "approved"
    ARCHIVED = "archived"


@dataclass
class StoredPlan:
    """A plan persisted to cortex-registry/plans/.

    Attributes:
        plan_id: Unique identifier for this plan.
        intent: Human-readable description of the planned operation.
        steps: Ordered list of execution steps.
        state: Current lifecycle state (PENDING → APPROVED → ARCHIVED).
        files_modified: Files expected to be modified by this plan.
        commit_sha: Git commit SHA recorded at archive time (None until then).
        ccl_snapshot: CCL/LENS context snapshot captured at plan creation.
        created_at: UTC timestamp of plan creation.
        executed_at: UTC timestamp of plan execution (None until archived).
    """

    plan_id: str
    intent: str
    steps: List[Dict[str, Any]]
    state: PlanState = PlanState.PENDING
    files_modified: List[str] = field(default_factory=list)
    commit_sha: Optional[str] = None
    ccl_snapshot: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime.datetime] = None
    executed_at: Optional[datetime.datetime] = None

    def __post_init__(self) -> None:
        """Set created_at to now if not supplied."""
        if self.created_at is None:
            self.created_at = datetime.datetime.utcnow()


class InteractionPlanStore:
    """Persistent store for interaction plans in cortex-registry/plans/.

    All plan YAML files are written to cortex-registry — never inside the
    cortex/ source package (CORE-035, CORE-002).

    Directory layout (relative to registry_root):
        plans/
          pending/      ← create_plan() writes here
          approved/     ← approve_plan() moves YAML here
          archive/
            {YYYY}/
              {MM}/     ← archive_plan() moves YAML here
            index.yaml  ← cumulative archive manifest

    Approval triggers (acceptable user phrases):
        ``approval_triggers`` class attribute — checked by orchestrators to
        detect when a user wants to approve a pending plan.

    Usage::

        store = InteractionPlanStore()          # default: cortex-registry/
        plan  = store.create_plan(
            intent="implement auth",
            steps=[{"id": 1, "action": "write test"}],
        )
        approved = store.approve_plan(plan.plan_id)
        archived = store.archive_plan(plan.plan_id, commit_sha="abc1234")
    """

    #: Phrases that signal a user wants to approve a pending plan.
    approval_triggers: List[str] = [
        "proceed",
        "approve",
        "yes, execute",
        "execute",
        "confirm",
        "go ahead",
    ]

    def __init__(self, registry_root: Optional[Path] = None) -> None:
        """Initialise store and ensure all subdirectories exist.

        Args:
            registry_root: Root directory for plan storage.  Defaults to
                ``cortex-registry/`` relative to the current working directory.
                Tests supply a ``tmp_path`` fixture here to isolate I/O.
        """
        if registry_root is None:
            registry_root = Path("cortex-registry")

        self._root = Path(registry_root)
        self._plans_dir = self._root / "plans"
        self._pending_dir = self._plans_dir / "pending"
        self._approved_dir = self._plans_dir / "approved"
        self._archive_dir = self._plans_dir / "archive"

        # Ensure all directories exist on initialisation
        for d in (self._pending_dir, self._approved_dir, self._archive_dir):
            d.mkdir(parents=True, exist_ok=True)

        # In-memory index keyed by plan_id for fast lookup
        self._index: Dict[str, StoredPlan] = {}

    # ------------------------------------------------------------------
    # Public API — Create
    # ------------------------------------------------------------------

    def create_plan(
        self,
        intent: str,
        steps: Optional[List[Dict[str, Any]]] = None,
        files_modified: Optional[List[str]] = None,
        commit_sha: Optional[str] = None,
        ccl_snapshot: Optional[Dict[str, Any]] = None,
    ) -> StoredPlan:
        """Create a new plan and persist it to ``plans/pending/``.

        Plans are created silently — no execution occurs (CORE-049).

        Args:
            intent: Human-readable description of the planned operation.
            steps: Ordered list of execution step dicts.
            files_modified: Files the plan expects to modify.
            commit_sha: Optional git SHA (recorded if known at creation).
            ccl_snapshot: CCL/LENS context snapshot at plan creation time.

        Returns:
            StoredPlan with ``state=PENDING`` and a unique ``plan_id``.
        """
        plan_id = self._generate_plan_id()
        plan = StoredPlan(
            plan_id=plan_id,
            intent=intent,
            steps=steps or [],
            files_modified=files_modified or [],
            commit_sha=commit_sha,
            ccl_snapshot=ccl_snapshot or {},
        )

        self._write_yaml(self._pending_dir / f"{plan_id}.yaml", plan)
        self._index[plan_id] = plan
        return plan

    # ------------------------------------------------------------------
    # Public API — Approve
    # ------------------------------------------------------------------

    def approve_plan(self, plan_id: str) -> StoredPlan:
        """Approve a pending plan, moving its YAML from ``pending/`` to ``approved/``.

        Args:
            plan_id: Identifier of the plan to approve.

        Returns:
            Updated StoredPlan with ``state=APPROVED``.

        Raises:
            FileNotFoundError: If the plan YAML is not in ``pending/``.
            ValueError: If the plan is not in PENDING state.
        """
        plan = self._load_plan_from_dir(self._pending_dir, plan_id)

        if plan.state != PlanState.PENDING:
            raise ValueError(
                f"Plan {plan_id} is not PENDING (current state: {plan.state.value})"
            )

        plan.state = PlanState.APPROVED

        src = self._pending_dir / f"{plan_id}.yaml"
        dst = self._approved_dir / f"{plan_id}.yaml"
        self._write_yaml(dst, plan)
        src.unlink(missing_ok=True)

        self._index[plan_id] = plan
        return plan

    # ------------------------------------------------------------------
    # Public API — Archive
    # ------------------------------------------------------------------

    def archive_plan(
        self,
        plan_id: str,
        commit_sha: Optional[str] = None,
    ) -> StoredPlan:
        """Archive an approved plan, moving its YAML to a dated subdirectory.

        Archived plans are **never deleted** — they are moved to
        ``archive/{YYYY}/{MM}/{plan_id}.yaml``.

        Args:
            plan_id: Identifier of the plan to archive.
            commit_sha: Git SHA of the commit that completed this plan.

        Returns:
            Updated StoredPlan with ``state=ARCHIVED``.

        Raises:
            FileNotFoundError: If the plan YAML is not in ``approved/``.
            ValueError: If the plan is not in APPROVED state.
        """
        # Check pending dir first to give a clear "not approved" error
        pending_path = self._pending_dir / f"{plan_id}.yaml"
        if pending_path.exists():
            raise ValueError(
                f"Plan {plan_id!r} is PENDING and has not been approved. "
                "Call approve_plan() before archive_plan()."
            )

        plan = self._load_plan_from_dir(self._approved_dir, plan_id)

        if plan.state != PlanState.APPROVED:
            raise ValueError(
                f"Plan {plan_id} must be APPROVED before archiving "
                f"(current state: {plan.state.value})"
            )

        now = datetime.datetime.utcnow()
        month_dir = self._archive_dir / str(now.year) / f"{now.month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)

        plan.state = PlanState.ARCHIVED
        plan.executed_at = now
        if commit_sha:
            plan.commit_sha = commit_sha

        src = self._approved_dir / f"{plan_id}.yaml"
        dst = month_dir / f"{plan_id}.yaml"
        self._write_yaml(dst, plan)
        src.unlink(missing_ok=True)

        self._update_archive_index(plan, dst)
        self._index[plan_id] = plan
        return plan

    # ------------------------------------------------------------------
    # Public API — Query
    # ------------------------------------------------------------------

    def list_pending(self) -> List[StoredPlan]:
        """Return all plans currently in ``pending/`` state.

        Returns:
            List of StoredPlan objects with state PENDING.
        """
        return [
            self._yaml_to_plan(f)
            for f in sorted(self._pending_dir.glob("*.yaml"))
        ]

    def list_archived(self) -> List[StoredPlan]:
        """Return all plans in the archive tree.

        Returns:
            List of StoredPlan objects with state ARCHIVED.
        """
        return [
            self._yaml_to_plan(f)
            for f in sorted(self._archive_dir.rglob("*.yaml"))
            if f.name != "index.yaml"
        ]

    def get_plan(self, plan_id: str) -> Optional[StoredPlan]:
        """Retrieve any stored plan by ID, regardless of its state.

        Searches ``pending/`` → ``approved/`` → ``archive/**`` in order.

        Args:
            plan_id: The plan identifier to look up.

        Returns:
            StoredPlan if found, or None.
        """
        if plan_id in self._index:
            return self._index[plan_id]

        for search_dir in (self._pending_dir, self._approved_dir):
            candidate = search_dir / f"{plan_id}.yaml"
            if candidate.exists():
                plan = self._yaml_to_plan(candidate)
                self._index[plan_id] = plan
                return plan

        for candidate in self._archive_dir.rglob(f"{plan_id}.yaml"):
            plan = self._yaml_to_plan(candidate)
            self._index[plan_id] = plan
            return plan

        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_plan_id() -> str:
        """Generate a unique plan identifier.

        Returns:
            Short UUID4-based string prefixed with ``plan-``.
        """
        return f"plan-{uuid.uuid4().hex[:12]}"

    def _write_yaml(self, path: Path, plan: StoredPlan) -> None:
        """Serialise a StoredPlan to YAML on disk.

        Args:
            path: Full destination file path.
            plan: The plan to serialise.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data: Dict[str, Any] = {
            "plan_id": plan.plan_id,
            "intent": plan.intent,
            "steps": plan.steps,
            "state": plan.state.value,
            "files_modified": plan.files_modified,
            "commit_sha": plan.commit_sha,
            "ccl_snapshot": plan.ccl_snapshot,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "executed_at": plan.executed_at.isoformat() if plan.executed_at else None,
        }
        with open(path, "w") as fh:
            yaml.dump(data, fh, default_flow_style=False, sort_keys=False)

    @staticmethod
    def _yaml_to_plan(path: Path) -> StoredPlan:
        """Deserialise a YAML file into a StoredPlan.

        Args:
            path: Path to the plan YAML file.

        Returns:
            StoredPlan populated from the YAML data.
        """
        with open(path, "r") as fh:
            data: Dict[str, Any] = yaml.safe_load(fh) or {}

        created_at = None
        raw_created = data.get("created_at")
        if raw_created:
            try:
                created_at = datetime.datetime.fromisoformat(raw_created)
            except (ValueError, TypeError):
                pass

        executed_at = None
        raw_executed = data.get("executed_at")
        if raw_executed:
            try:
                executed_at = datetime.datetime.fromisoformat(raw_executed)
            except (ValueError, TypeError):
                pass

        state_raw = data.get("state", "pending")
        try:
            state = PlanState(state_raw)
        except ValueError:
            state = PlanState.PENDING

        return StoredPlan(
            plan_id=data.get("plan_id", path.stem),
            intent=data.get("intent", ""),
            steps=data.get("steps", []),
            state=state,
            files_modified=data.get("files_modified", []),
            commit_sha=data.get("commit_sha"),
            ccl_snapshot=data.get("ccl_snapshot", {}),
            created_at=created_at,
            executed_at=executed_at,
        )

    def _load_plan_from_dir(self, directory: Path, plan_id: str) -> StoredPlan:
        """Load a plan from a specific directory.

        Args:
            directory: The directory to search.
            plan_id: The plan identifier.

        Returns:
            Loaded StoredPlan.

        Raises:
            FileNotFoundError: If the YAML does not exist in ``directory``.
        """
        path = directory / f"{plan_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(
                f"Plan {plan_id!r} not found in {directory}"
            )
        return self._yaml_to_plan(path)

    def _update_archive_index(self, plan: StoredPlan, yaml_path: Path) -> None:
        """Append an archived plan entry to ``archive/index.yaml``.

        Creates the index file if it does not yet exist.

        Args:
            plan: The archived StoredPlan.
            yaml_path: Filesystem path where the plan YAML was written.
        """
        index_path = self._archive_dir / "index.yaml"
        if index_path.exists():
            with open(index_path, "r") as fh:
                index: Dict[str, Any] = yaml.safe_load(fh) or {}
        else:
            index = {"archived_plans": []}

        index.setdefault("archived_plans", []).append(
            {
                "plan_id": plan.plan_id,
                "intent": plan.intent,
                "state": plan.state.value,
                "archived_at": plan.executed_at.isoformat() if plan.executed_at else None,
                "yaml_path": str(yaml_path.relative_to(self._root)),
            }
        )

        with open(index_path, "w") as fh:
            yaml.dump(index, fh, default_flow_style=False, sort_keys=False)


# AC_COMPLETE: AC-PLAN-STORE-D10-001 ✅
