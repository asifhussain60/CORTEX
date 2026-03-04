# AC_START: AC-P125-D-001
"""
Test Suite: Phase 125-d — IntegrityChecker + HistoryTracker
Module: Registry integrity validation and hash-based change tracking.
Tests: 20 tests — integrity checks + history snapshots.
"""

import json
import os
import tempfile

import pytest

from cortex.intelligence.registry.integrity_checker import IntegrityChecker
from cortex.intelligence.registry.history_tracker import HistoryTracker
from cortex.intelligence.registry.models.governance import GovernanceRuleModel
from cortex.intelligence.registry.models.workflow import WorkflowTemplateModel
from cortex.intelligence.registry.models.base import BaseRegistryModel


# ═══════════════════════════════════════════════════════════════════════════════
# IntegrityChecker Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def checker() -> IntegrityChecker:
    return IntegrityChecker()


@pytest.fixture
def healthy_model() -> GovernanceRuleModel:
    return GovernanceRuleModel(
        id="gov-001",
        type="governance-rule",
        source_file="governance/dev.yaml",
        title="Dev Rules",
        source_hash="",
        integrity={"all_refs_resolved": True, "schema_valid": True, "warnings": []},
        rules=[{"id": "CORE-008"}],
    )


@pytest.fixture
def broken_model() -> WorkflowTemplateModel:
    return WorkflowTemplateModel(
        id="wf-001",
        type="workflow-template",
        source_file="workflows/broken.yaml",
        title="Broken Workflow",
        source_hash="",
        integrity={"all_refs_resolved": False, "schema_valid": True, "warnings": ["unresolved ref"]},
        steps=[],
    )


class TestIntegrityCheck:
    """IntegrityChecker.check() must produce a report."""

    def test_check_returns_dict(
        self, checker: IntegrityChecker, healthy_model: GovernanceRuleModel
    ) -> None:
        report = checker.check([healthy_model])
        assert isinstance(report, dict)

    def test_report_has_total_count(
        self, checker: IntegrityChecker, healthy_model: GovernanceRuleModel
    ) -> None:
        report = checker.check([healthy_model])
        assert "total_artifacts" in report

    def test_report_has_healthy_count(
        self, checker: IntegrityChecker, healthy_model: GovernanceRuleModel
    ) -> None:
        report = checker.check([healthy_model])
        assert report["healthy_count"] == 1

    def test_report_has_broken_count(
        self, checker: IntegrityChecker,
        healthy_model: GovernanceRuleModel,
        broken_model: WorkflowTemplateModel,
    ) -> None:
        report = checker.check([healthy_model, broken_model])
        assert report["broken_count"] == 1

    def test_report_lists_broken_artifacts(
        self, checker: IntegrityChecker, broken_model: WorkflowTemplateModel
    ) -> None:
        report = checker.check([broken_model])
        assert len(report["broken_artifacts"]) == 1
        assert report["broken_artifacts"][0]["id"] == "wf-001"

    def test_report_has_warnings(
        self, checker: IntegrityChecker, broken_model: WorkflowTemplateModel
    ) -> None:
        report = checker.check([broken_model])
        assert len(report["warnings"]) > 0

    def test_empty_list_produces_empty_report(
        self, checker: IntegrityChecker
    ) -> None:
        report = checker.check([])
        assert report["total_artifacts"] == 0
        assert report["healthy_count"] == 0

    def test_report_has_type_breakdown(
        self, checker: IntegrityChecker,
        healthy_model: GovernanceRuleModel,
        broken_model: WorkflowTemplateModel,
    ) -> None:
        report = checker.check([healthy_model, broken_model])
        assert "types" in report

    def test_to_json_valid(
        self, checker: IntegrityChecker, healthy_model: GovernanceRuleModel
    ) -> None:
        report = checker.check([healthy_model])
        json_str = checker.to_json(report)
        parsed = json.loads(json_str)
        assert "total_artifacts" in parsed

    def test_duplicate_id_detection(
        self, checker: IntegrityChecker
    ) -> None:
        m1 = GovernanceRuleModel(
            id="dup-001", type="governance-rule", source_file="a.yaml",
            title="A", source_hash="",
        )
        m2 = GovernanceRuleModel(
            id="dup-001", type="governance-rule", source_file="b.yaml",
            title="B", source_hash="",
        )
        report = checker.check([m1, m2])
        assert len(report["duplicate_ids"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# HistoryTracker Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHistoryTracker:
    """HistoryTracker stores snapshots and detects changes."""

    @pytest.fixture
    def tracker(self, tmp_path: object) -> HistoryTracker:
        return HistoryTracker(storage_dir=str(tmp_path))

    def test_snapshot_creates_file(self, tracker: HistoryTracker) -> None:
        models = [
            GovernanceRuleModel(
                id="gov-001", type="governance-rule", source_file="g.yaml",
                title="Gov", source_hash="",
            ),
        ]
        path = tracker.snapshot(models)
        assert os.path.exists(path)

    def test_snapshot_is_valid_json(self, tracker: HistoryTracker) -> None:
        models = [
            GovernanceRuleModel(
                id="gov-001", type="governance-rule", source_file="g.yaml",
                title="Gov", source_hash="",
            ),
        ]
        path = tracker.snapshot(models)
        with open(path) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_list_snapshots_empty(self, tracker: HistoryTracker) -> None:
        assert tracker.list_snapshots() == []

    def test_list_snapshots_after_snapshot(self, tracker: HistoryTracker) -> None:
        models = [
            GovernanceRuleModel(
                id="gov-001", type="governance-rule", source_file="g.yaml",
                title="Gov", source_hash="",
            ),
        ]
        tracker.snapshot(models)
        assert len(tracker.list_snapshots()) == 1

    def test_diff_detects_added(self, tracker: HistoryTracker) -> None:
        m1 = GovernanceRuleModel(
            id="gov-001", type="governance-rule", source_file="g.yaml",
            title="Gov", source_hash="",
        )
        tracker.snapshot([m1])
        m2 = WorkflowTemplateModel(
            id="wf-001", type="workflow-template", source_file="w.yaml",
            title="WF", source_hash="",
        )
        tracker.snapshot([m1, m2])
        diff = tracker.diff()
        assert len(diff["added"]) == 1

    def test_diff_detects_removed(self, tracker: HistoryTracker) -> None:
        m1 = GovernanceRuleModel(
            id="gov-001", type="governance-rule", source_file="g.yaml",
            title="Gov", source_hash="",
        )
        m2 = WorkflowTemplateModel(
            id="wf-001", type="workflow-template", source_file="w.yaml",
            title="WF", source_hash="",
        )
        tracker.snapshot([m1, m2])
        tracker.snapshot([m1])
        diff = tracker.diff()
        assert len(diff["removed"]) == 1

    def test_diff_detects_changed(self, tracker: HistoryTracker) -> None:
        m1 = GovernanceRuleModel(
            id="gov-001", type="governance-rule", source_file="g.yaml",
            title="Gov V1", source_hash="",
        )
        tracker.snapshot([m1])
        m1_v2 = GovernanceRuleModel(
            id="gov-001", type="governance-rule", source_file="g.yaml",
            title="Gov V2", source_hash="",
        )
        tracker.snapshot([m1_v2])
        diff = tracker.diff()
        assert len(diff["changed"]) == 1

    def test_diff_no_snapshots(self, tracker: HistoryTracker) -> None:
        diff = tracker.diff()
        assert diff["added"] == []
        assert diff["removed"] == []
        assert diff["changed"] == []

    def test_max_snapshots_enforced(self, tracker: HistoryTracker) -> None:
        """Tracker must keep at most max_snapshots (default 50)."""
        for i in range(55):
            m = GovernanceRuleModel(
                id=f"gov-{i}", type="governance-rule", source_file="g.yaml",
                title=f"Gov {i}", source_hash="",
            )
            tracker.snapshot([m])
        assert len(tracker.list_snapshots()) <= 50


# AC_COMPLETE: AC-P125-D-001 ✅
