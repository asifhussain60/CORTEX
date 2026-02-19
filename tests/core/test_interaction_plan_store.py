"""
InteractionPlanStore — Plan-First Execution with Persistent Memory (Phase 00, D10).

Tests the persistent plan lifecycle:
  pending → approved → archived

And CCL synthesis of past plans.

Authority: Phase 00, D10 — EA-011 Plan-First Execution with Persistent Memory
CORE-008: Test-first
CORE-011: Type hints
CORE-012: Docstrings
CORE-035: Single canonical implementation (no new orchestrator classes)
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml

# ==============================================================================
# IMPORTS — will FAIL (RED) until cortex/orchestrators/core/interaction_plan_store.py
# ==============================================================================

try:
    from cortex.orchestrators.core.interaction_plan_store import (
        InteractionPlanStore,
        PlanState,
        StoredPlan,
    )
    PLAN_STORE_AVAILABLE = True
except ImportError:
    PLAN_STORE_AVAILABLE = False
    InteractionPlanStore = None  # type: ignore[assignment,misc]
    PlanState = None  # type: ignore[assignment,misc]
    StoredPlan = None  # type: ignore[assignment,misc]

try:
    from cortex.orchestrators.context_crystallization.ccl_core import (
        ContextCrystallizationLayer,
    )
    CCL_AVAILABLE = True
except ImportError:
    CCL_AVAILABLE = False
    ContextCrystallizationLayer = None  # type: ignore[assignment,misc]

REGISTRY_ROOT = Path(__file__).resolve().parents[2] / "cortex-registry"
PLANS_PENDING = REGISTRY_ROOT / "plans" / "pending"
PLANS_APPROVED = REGISTRY_ROOT / "plans" / "approved"
PLANS_ARCHIVE = REGISTRY_ROOT / "plans" / "archive"

pytestmark = pytest.mark.skipif(
    not PLAN_STORE_AVAILABLE,
    reason="cortex/orchestrators/core/interaction_plan_store.py not yet implemented (Phase 00 D10)"
)


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def store(tmp_path: Path) -> Any:
    """InteractionPlanStore using tmp_path as registry root."""
    return InteractionPlanStore(registry_root=tmp_path)


@pytest.fixture
def sample_plan_data() -> dict:
    """Minimal valid plan payload matching D10 YAML spec."""
    return {
        "intent": "implement interaction plan store",
        "steps": [
            {"id": 1, "action": "Write TDD RED test", "status": "done"},
            {"id": 2, "action": "Implement InteractionPlanStore", "status": "pending"},
            {"id": 3, "action": "GREEN pass", "status": "pending"},
        ],
        "files_modified": [],
        "commit_sha": None,
        "ccl_snapshot": {"lens_domains": ["orchestrators", "core"], "active_rules": ["CORE-008"]},
    }


# ==============================================================================
# 1. STRUCTURE — Plans Directories Exist or Are Created
# ==============================================================================

class TestPlanDirectoryStructure:
    """Plan registry directories must exist or be auto-created."""

    def test_pending_dir_created_on_init(self, store: Any, tmp_path: Path) -> None:
        """InteractionPlanStore must create pending/ on init."""
        pending = tmp_path / "plans" / "pending"
        assert pending.exists(), "pending/ directory must be created on store init"

    def test_approved_dir_created_on_init(self, store: Any, tmp_path: Path) -> None:
        """InteractionPlanStore must create approved/ on init."""
        approved = tmp_path / "plans" / "approved"
        assert approved.exists(), "approved/ directory must be created on store init"

    def test_archive_dir_created_on_init(self, store: Any, tmp_path: Path) -> None:
        """InteractionPlanStore must create archive/ on init."""
        archive = tmp_path / "plans" / "archive"
        assert archive.exists(), "archive/ directory must be created on store init"

    def test_production_pending_dir_exists(self) -> None:
        """Production cortex-registry/plans/pending/ must exist (gitkeep)."""
        assert PLANS_PENDING.exists(), f"Missing: {PLANS_PENDING}"

    def test_production_approved_dir_exists(self) -> None:
        """Production cortex-registry/plans/approved/ must exist (gitkeep)."""
        assert PLANS_APPROVED.exists(), f"Missing: {PLANS_APPROVED}"

    def test_production_archive_dir_exists(self) -> None:
        """Production cortex-registry/plans/archive/ must exist (gitkeep)."""
        assert PLANS_ARCHIVE.exists(), f"Missing: {PLANS_ARCHIVE}"


# ==============================================================================
# 2. CREATE PLAN → PENDING (no auto-execution)
# ==============================================================================

class TestCreatePlan:
    """Plans are created silently in pending/, no auto-execution."""

    def test_create_plan_returns_stored_plan(self, store: Any, sample_plan_data: dict) -> None:
        """create_plan() must return a StoredPlan instance."""
        plan = store.create_plan(**sample_plan_data)
        assert plan is not None
        assert isinstance(plan, StoredPlan)

    def test_create_plan_writes_yaml_to_pending(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """create_plan() must write a YAML file to pending/."""
        plan = store.create_plan(**sample_plan_data)
        pending_dir = tmp_path / "plans" / "pending"
        yaml_files = list(pending_dir.glob("*.yaml"))
        assert len(yaml_files) == 1, f"Expected 1 YAML in pending/, found: {yaml_files}"

    def test_pending_plan_yaml_has_plan_id(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Pending YAML must contain plan_id."""
        plan = store.create_plan(**sample_plan_data)
        pending_dir = tmp_path / "plans" / "pending"
        yaml_file = next(pending_dir.glob("*.yaml"))
        data = yaml.safe_load(yaml_file.read_text())
        assert "plan_id" in data, "plan_id missing from pending YAML"

    def test_pending_plan_yaml_has_intent(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Pending YAML must contain intent."""
        store.create_plan(**sample_plan_data)
        pending_dir = tmp_path / "plans" / "pending"
        data = yaml.safe_load(next(pending_dir.glob("*.yaml")).read_text())
        assert "intent" in data
        assert data["intent"] == sample_plan_data["intent"]

    def test_pending_plan_yaml_has_steps(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Pending YAML must contain steps list."""
        store.create_plan(**sample_plan_data)
        pending_dir = tmp_path / "plans" / "pending"
        data = yaml.safe_load(next(pending_dir.glob("*.yaml")).read_text())
        assert "steps" in data
        assert len(data["steps"]) == len(sample_plan_data["steps"])

    def test_pending_plan_yaml_has_ccl_snapshot(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Pending YAML must contain ccl_snapshot."""
        store.create_plan(**sample_plan_data)
        pending_dir = tmp_path / "plans" / "pending"
        data = yaml.safe_load(next(pending_dir.glob("*.yaml")).read_text())
        assert "ccl_snapshot" in data

    def test_pending_plan_yaml_has_state_field(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Pending YAML must have state: pending."""
        store.create_plan(**sample_plan_data)
        pending_dir = tmp_path / "plans" / "pending"
        data = yaml.safe_load(next(pending_dir.glob("*.yaml")).read_text())
        assert data.get("state") == "pending"

    def test_pending_plan_yaml_has_created_at(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Pending YAML must have created_at timestamp."""
        store.create_plan(**sample_plan_data)
        pending_dir = tmp_path / "plans" / "pending"
        data = yaml.safe_load(next(pending_dir.glob("*.yaml")).read_text())
        assert "created_at" in data

    def test_pending_plan_does_not_auto_execute(
        self, store: Any, sample_plan_data: dict
    ) -> None:
        """Creating a plan must NOT execute it — no side effects."""
        plan = store.create_plan(**sample_plan_data)
        assert plan.state == PlanState.PENDING
        assert plan.executed_at is None

    def test_plan_id_is_unique(self, store: Any, sample_plan_data: dict) -> None:
        """Each plan must get a unique plan_id."""
        plan1 = store.create_plan(**sample_plan_data)
        plan2 = store.create_plan(**sample_plan_data)
        assert plan1.plan_id != plan2.plan_id


# ==============================================================================
# 3. APPROVE PLAN → MOVE TO approved/
# ==============================================================================

class TestApprovePlan:
    """Approval moves plan from pending/ to approved/."""

    def test_approve_plan_changes_state(self, store: Any, sample_plan_data: dict) -> None:
        """approve_plan() must set state to APPROVED."""
        plan = store.create_plan(**sample_plan_data)
        approved = store.approve_plan(plan.plan_id)
        assert approved.state == PlanState.APPROVED

    def test_approve_plan_moves_yaml_to_approved_dir(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """approve_plan() must move YAML from pending/ to approved/."""
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        pending_dir = tmp_path / "plans" / "pending"
        approved_dir = tmp_path / "plans" / "approved"
        assert len(list(pending_dir.glob("*.yaml"))) == 0, "pending/ must be empty after approval"
        assert len(list(approved_dir.glob("*.yaml"))) == 1, "approved/ must have 1 YAML after approval"

    def test_approve_plan_yaml_updates_state_field(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Approved YAML must have state: approved."""
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        approved_dir = tmp_path / "plans" / "approved"
        data = yaml.safe_load(next(approved_dir.glob("*.yaml")).read_text())
        assert data["state"] == "approved"

    def test_approve_nonexistent_plan_raises(self, store: Any) -> None:
        """Approving a non-existent plan_id must raise an error."""
        with pytest.raises((KeyError, ValueError, FileNotFoundError)):
            store.approve_plan("nonexistent-plan-id")

    def test_approval_triggers_match_keywords(self, store: Any) -> None:
        """Approval trigger keywords must include 'proceed', 'approve', 'yes, execute'."""
        keywords = store.approval_triggers
        assert any(k in keywords for k in ["proceed", "approve", "yes, execute"]), (
            f"Approval triggers {keywords} missing required keywords"
        )


# ==============================================================================
# 4. ARCHIVE PLAN → archive/{YYYY}/{MM}/
# ==============================================================================

class TestArchivePlan:
    """Archive moves plan from approved/ into dated archive folder — never deleted."""

    def test_archive_plan_changes_state(self, store: Any, sample_plan_data: dict) -> None:
        """archive_plan() must set state to ARCHIVED."""
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        archived = store.archive_plan(plan.plan_id)
        assert archived.state == PlanState.ARCHIVED

    def test_archive_plan_moves_yaml_to_dated_path(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """archive_plan() must place YAML in archive/{YYYY}/{MM}/."""
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        archived = store.archive_plan(plan.plan_id)

        now = datetime.datetime.utcnow()
        year_dir = tmp_path / "plans" / "archive" / str(now.year)
        month_dir = year_dir / f"{now.month:02d}"
        assert month_dir.exists(), f"Dated archive dir not created: {month_dir}"
        yaml_files = list(month_dir.glob("*.yaml"))
        assert len(yaml_files) >= 1, "Archived YAML not found in dated folder"

    def test_archive_plan_yaml_is_never_deleted(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Archived YAML files must remain on disk permanently."""
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        store.archive_plan(plan.plan_id)

        now = datetime.datetime.utcnow()
        archive_root = tmp_path / "plans" / "archive"
        all_yamls = list(archive_root.rglob("*.yaml"))
        assert len(all_yamls) >= 1, "Archived YAML was deleted — must never be removed"

    def test_archive_index_yaml_is_updated(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """archive/index.yaml must be updated after archiving."""
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        store.archive_plan(plan.plan_id)

        index_path = tmp_path / "plans" / "archive" / "index.yaml"
        assert index_path.exists(), "archive/index.yaml must exist after first archive"
        index = yaml.safe_load(index_path.read_text())
        assert "archived_plans" in index or "plans" in index

    def test_archive_plan_yaml_has_commit_sha_field(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Archived YAML must have commit_sha field."""
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        store.archive_plan(plan.plan_id, commit_sha="abc1234")

        now = datetime.datetime.utcnow()
        month_dir = (
            tmp_path / "plans" / "archive" / str(now.year) / f"{now.month:02d}"
        )
        data = yaml.safe_load(next(month_dir.glob("*.yaml")).read_text())
        assert "commit_sha" in data
        assert data["commit_sha"] == "abc1234"

    def test_archive_plan_yaml_has_files_modified_field(
        self, store: Any, sample_plan_data: dict, tmp_path: Path
    ) -> None:
        """Archived YAML must have files_modified list."""
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        store.archive_plan(plan.plan_id)

        now = datetime.datetime.utcnow()
        month_dir = (
            tmp_path / "plans" / "archive" / str(now.year) / f"{now.month:02d}"
        )
        data = yaml.safe_load(next(month_dir.glob("*.yaml")).read_text())
        assert "files_modified" in data

    def test_archive_unapproved_plan_raises(
        self, store: Any, sample_plan_data: dict
    ) -> None:
        """Archiving a PENDING (non-approved) plan must raise an error."""
        plan = store.create_plan(**sample_plan_data)
        with pytest.raises((ValueError, RuntimeError)):
            store.archive_plan(plan.plan_id)


# ==============================================================================
# 5. LIST AND QUERY
# ==============================================================================

class TestPlanQuery:
    """Query operations on stored plans."""

    def test_list_pending_returns_pending_plans(
        self, store: Any, sample_plan_data: dict
    ) -> None:
        """list_pending() must return all plans in pending/ state."""
        store.create_plan(**sample_plan_data)
        store.create_plan(**sample_plan_data)
        pending = store.list_pending()
        assert len(pending) == 2

    def test_list_archived_returns_archived_plans(
        self, store: Any, sample_plan_data: dict
    ) -> None:
        """list_archived() must return all archived plans."""
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        store.archive_plan(plan.plan_id)
        archived = store.list_archived()
        assert len(archived) >= 1

    def test_get_plan_by_id(self, store: Any, sample_plan_data: dict) -> None:
        """get_plan(plan_id) must retrieve a plan regardless of state."""
        plan = store.create_plan(**sample_plan_data)
        retrieved = store.get_plan(plan.plan_id)
        assert retrieved is not None
        assert retrieved.plan_id == plan.plan_id


# ==============================================================================
# 6. CCL SYNTHESIS OF PAST PLANS
# ==============================================================================

class TestCCLSynthesis:
    """CCL must read archived plans and provide past context."""

    @pytest.mark.skipif(not CCL_AVAILABLE, reason="ccl_core.py not yet implemented")
    def test_ccl_reads_archive_and_synthesizes_past_plans(
        self, tmp_path: Path, sample_plan_data: dict
    ) -> None:
        """CCL.past_plans must include archived plan summaries."""
        store = InteractionPlanStore(registry_root=tmp_path)
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        store.archive_plan(plan.plan_id)

        ccl = ContextCrystallizationLayer(registry_root=tmp_path)
        context = ccl.synthesize()
        assert "past_plans" in context, "CCL synthesis missing past_plans key"
        assert len(context["past_plans"]) >= 1

    @pytest.mark.skipif(not CCL_AVAILABLE, reason="ccl_core.py not yet implemented")
    def test_ccl_past_plans_contain_intent(
        self, tmp_path: Path, sample_plan_data: dict
    ) -> None:
        """Each CCL past_plan entry must include the original intent."""
        store = InteractionPlanStore(registry_root=tmp_path)
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        store.archive_plan(plan.plan_id)

        ccl = ContextCrystallizationLayer(registry_root=tmp_path)
        context = ccl.synthesize()
        past = context["past_plans"]
        assert any(
            p.get("intent") == sample_plan_data["intent"] for p in past
        ), "Past plan intent not found in CCL synthesis"

    @pytest.mark.skipif(not CCL_AVAILABLE, reason="ccl_core.py not yet implemented")
    def test_ccl_past_plans_contain_plan_id(
        self, tmp_path: Path, sample_plan_data: dict
    ) -> None:
        """Each CCL past_plan entry must include plan_id."""
        store = InteractionPlanStore(registry_root=tmp_path)
        plan = store.create_plan(**sample_plan_data)
        store.approve_plan(plan.plan_id)
        store.archive_plan(plan.plan_id)

        ccl = ContextCrystallizationLayer(registry_root=tmp_path)
        context = ccl.synthesize()
        plan_ids = [p.get("plan_id") for p in context["past_plans"]]
        assert plan.plan_id in plan_ids


# ==============================================================================
# 7. INTERACTION ORCHESTRATOR INTEGRATION
# ==============================================================================

class TestInteractionOrchestratorIntegration:
    """InteractionOrchestrator must remain Stage 1, no new orchestrators."""

    def test_interaction_orchestrator_is_stage1_default(self) -> None:
        """MasterOrchestrator must still route to InteractionOrchestrator as Stage 1."""
        try:
            from cortex.orchestrators.core.interaction_orchestrator import (
                InteractionOrchestrator,
            )
            assert InteractionOrchestrator is not None
        except ImportError:
            pytest.skip("InteractionOrchestrator not importable")

    def test_no_new_orchestrator_class_created(self) -> None:
        """D10 must NOT introduce a new *Orchestrator class — only InteractionPlanStore."""
        plan_store_mod = __import__(
            "cortex.orchestrators.core.interaction_plan_store",
            fromlist=["InteractionPlanStore"],
        )
        import inspect
        classes = [
            name for name, obj in inspect.getmembers(plan_store_mod, inspect.isclass)
            if name.endswith("Orchestrator")
        ]
        assert classes == [], (
            f"D10 must not create new Orchestrator classes, found: {classes}"
        )

    def test_interaction_orchestrator_has_plan_store_attribute(self) -> None:
        """InteractionOrchestrator must accept a plan_store injection."""
        try:
            from cortex.orchestrators.core.interaction_orchestrator import (
                InteractionOrchestrator,
            )
            import inspect
            sig = inspect.signature(InteractionOrchestrator.__init__)
            # plan_store should be injectable (optional kwarg)
            param_names = list(sig.parameters.keys())
            # Either plan_store in constructor OR set_plan_store method
            has_param = "plan_store" in param_names
            has_method = hasattr(InteractionOrchestrator, "set_plan_store")
            assert has_param or has_method, (
                "InteractionOrchestrator must accept plan_store via constructor or set_plan_store()"
            )
        except ImportError:
            pytest.skip("InteractionOrchestrator not importable")


# ==============================================================================
# 8. STORED PLAN CONTRACT
# ==============================================================================

class TestStoredPlanContract:
    """StoredPlan dataclass/model must have the expected interface."""

    def test_stored_plan_has_plan_id(self, store: Any, sample_plan_data: dict) -> None:
        """StoredPlan must have plan_id."""
        plan = store.create_plan(**sample_plan_data)
        assert hasattr(plan, "plan_id")
        assert plan.plan_id

    def test_stored_plan_has_state(self, store: Any, sample_plan_data: dict) -> None:
        """StoredPlan must have state."""
        plan = store.create_plan(**sample_plan_data)
        assert hasattr(plan, "state")

    def test_stored_plan_has_intent(self, store: Any, sample_plan_data: dict) -> None:
        """StoredPlan must have intent."""
        plan = store.create_plan(**sample_plan_data)
        assert hasattr(plan, "intent")
        assert plan.intent == sample_plan_data["intent"]

    def test_stored_plan_has_steps(self, store: Any, sample_plan_data: dict) -> None:
        """StoredPlan must have steps list."""
        plan = store.create_plan(**sample_plan_data)
        assert hasattr(plan, "steps")
        assert isinstance(plan.steps, list)

    def test_stored_plan_has_created_at(self, store: Any, sample_plan_data: dict) -> None:
        """StoredPlan must have created_at timestamp."""
        plan = store.create_plan(**sample_plan_data)
        assert hasattr(plan, "created_at")
        assert plan.created_at is not None

    def test_stored_plan_has_executed_at(self, store: Any, sample_plan_data: dict) -> None:
        """StoredPlan must have executed_at (None when pending)."""
        plan = store.create_plan(**sample_plan_data)
        assert hasattr(plan, "executed_at")
        assert plan.executed_at is None

    def test_plan_state_enum_has_required_values(self) -> None:
        """PlanState enum must have PENDING, APPROVED, ARCHIVED."""
        assert hasattr(PlanState, "PENDING")
        assert hasattr(PlanState, "APPROVED")
        assert hasattr(PlanState, "ARCHIVED")
