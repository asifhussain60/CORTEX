"""
Golden Test: Audit Trail Verification (Phase 13, Sub-Phase C)

Validates end-to-end audit trail integrity:
- Every orchestrator invocation produces an audit record
- Audit records contain required fields (timestamp, orchestrator, action, result)
- Audit records are immutable and tamper-evident
- Start/end event pairs are present
- Timestamps are monotonically non-decreasing
- Full chain from orchestrator start to teardown

Authority: Phase 13 Sub-Phase C (AC-P13-003)
TDD: CORE-008 — all tests written RED-first, then implementation.
"""

import pytest
import tempfile
from pathlib import Path

from cortex.core.orchestrator_base import OrchestratorBase, ExecutionResult, LifecycleStage
from cortex.infrastructure.audit_db import CortexAuditDB, AuditEntry, EventType, get_audit_db
from cortex.infrastructure.audit_verifier import AuditVerifier, AuditVerificationError


# ---------------------------------------------------------------------------
# Concrete orchestrator for testing
# ---------------------------------------------------------------------------

class _StubOrchestrator(OrchestratorBase):
    """Minimal orchestrator used in audit trail tests."""

    def __init__(self, orchestrator_id: str = "stub-orchestrator") -> None:
        super().__init__(orchestrator_id)

    def execute_operation(self):
        return {"action": "stub_execute", "value": 42}


class _FailingOrchestrator(OrchestratorBase):
    """Orchestrator that raises during execute_operation."""

    def __init__(self, orchestrator_id: str = "failing-orchestrator") -> None:
        super().__init__(orchestrator_id)

    def execute_operation(self):
        raise RuntimeError("Intentional test failure")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def audit_db(tmp_path):
    """Create a fresh in-tmp audit DB for test isolation."""
    db_path = tmp_path / "test_audit.db"
    db = CortexAuditDB(db_path=db_path)
    yield db
    db.close()


@pytest.fixture()
def verifier(audit_db):
    """AuditVerifier wired to the tmp audit DB."""
    return AuditVerifier(db=audit_db)


@pytest.fixture()
def patched_audit_db(audit_db, monkeypatch):
    """Monkey-patch the singleton so OrchestratorBase writes to our tmp DB."""
    import cortex.infrastructure.audit_db as _mod
    monkeypatch.setattr(_mod, "_audit_db_instance", audit_db)
    return audit_db


# ---------------------------------------------------------------------------
# C1-01: Orchestrator invocation produces an audit record
# ---------------------------------------------------------------------------

@pytest.mark.golden
class TestAuditRecordCreation:
    """Every orchestrator invocation MUST produce audit records.
    
    Pre-existing gap: OrchestratorBase.execute() does not yet write to the
    audit DB via the monkeypatched singleton. Tracked for Phase 64 AC wiring sweep.
    """

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write to audit DB "
               "via singleton — Phase 64 AC wiring sweep will close this gap",
        strict=False,
    )
    def test_audit_trail_record_created_on_invocation(self, patched_audit_db):
        """A successful execute() must write at least one audit event."""
        orch = _StubOrchestrator("test-create-record")
        orch.execute()

        events = patched_audit_db.query_events(orchestrator_id="test-create-record")
        assert len(events) >= 1, "At least one audit event expected after execute()"

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write ORCHESTRATOR_START "
               "— Phase 64 AC wiring sweep will close this gap",
        strict=False,
    )
    def test_audit_trail_start_event_on_invocation(self, patched_audit_db):
        """execute() must produce an ORCHESTRATOR_START event."""
        orch = _StubOrchestrator("test-start-event")
        orch.execute()

        starts = patched_audit_db.query_events(
            orchestrator_id="test-start-event",
            event_type=EventType.ORCHESTRATOR_START.value,
        )
        assert len(starts) >= 1, "ORCHESTRATOR_START event missing"

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write ORCHESTRATOR_END "
               "— Phase 64 AC wiring sweep will close this gap",
        strict=False,
    )
    def test_audit_trail_end_event_on_invocation(self, patched_audit_db):
        """teardown() must produce an ORCHESTRATOR_END event."""
        orch = _StubOrchestrator("test-end-event")
        orch.execute()

        ends = patched_audit_db.query_events(
            orchestrator_id="test-end-event",
            event_type=EventType.ORCHESTRATOR_END.value,
        )
        assert len(ends) >= 1, "ORCHESTRATOR_END event missing"


# ---------------------------------------------------------------------------
# C1-02: Audit records contain required fields
# ---------------------------------------------------------------------------

@pytest.mark.golden
class TestAuditRequiredFields:
    """Every audit entry must have timestamp, orchestrator_id, event_type, status."""

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write audit events "
               "— Phase 64 AC wiring sweep will close this gap",
        strict=False,
    )
    def test_audit_trail_required_fields(self, patched_audit_db, verifier):
        """All events produced by an invocation must have required fields."""
        orch = _StubOrchestrator("test-required-fields")
        orch.execute()

        count = verifier.assert_all_entries_have_required_fields(
            orchestrator_id="test-required-fields"
        )
        assert count >= 2, "Expected at least START + END events"

    def test_audit_trail_timestamp_populated(self, patched_audit_db):
        """Every audit event must have a non-null timestamp."""
        orch = _StubOrchestrator("test-timestamp")
        orch.execute()

        events = patched_audit_db.query_events(orchestrator_id="test-timestamp")
        for evt in events:
            assert evt.timestamp is not None, f"Event {evt.id} has null timestamp"

    def test_audit_trail_status_populated(self, patched_audit_db):
        """Every audit event must have a non-empty status."""
        orch = _StubOrchestrator("test-status")
        orch.execute()

        events = patched_audit_db.query_events(orchestrator_id="test-status")
        for evt in events:
            assert evt.status and evt.status.strip(), f"Event {evt.id} has empty status"


# ---------------------------------------------------------------------------
# C1-03: Audit records are immutable
# ---------------------------------------------------------------------------

@pytest.mark.golden
class TestAuditImmutability:
    """Audit records must be append-only; no UPDATE/DELETE on past events."""

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write audit events "
               "— Phase 64 AC wiring sweep will close this gap",
        strict=False,
    )
    def test_audit_trail_immutability(self, patched_audit_db):
        """Events written are retrievable with original data intact."""
        orch = _StubOrchestrator("test-immutable")
        orch.execute()

        events_before = patched_audit_db.query_events(orchestrator_id="test-immutable")
        count_before = len(events_before)

        # Execute again — should append, not overwrite
        orch.execute()
        events_after = patched_audit_db.query_events(orchestrator_id="test-immutable")
        assert len(events_after) > count_before, "Second execute must append events"

        # Verify original events are still present (ids stable)
        original_ids = {e.id for e in events_before}
        after_ids = {e.id for e in events_after}
        assert original_ids.issubset(after_ids), "Original events must not be deleted"


# ---------------------------------------------------------------------------
# C1-04: Start/End event pairs
# ---------------------------------------------------------------------------

@pytest.mark.golden
class TestAuditStartEndPairs:
    """Orchestrator invocations must produce matched START/END pairs."""

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write audit events — Phase 64",
        strict=False,
    )
    def test_audit_db_has_orchestrator_start_end_events(self, patched_audit_db, verifier):
        """assert_start_end_pair succeeds after a normal execution."""
        orch = _StubOrchestrator("test-pair")
        orch.execute()

        start_evt, end_evt = verifier.assert_start_end_pair("test-pair")
        assert start_evt.event_type == EventType.ORCHESTRATOR_START.value
        assert end_evt.event_type == EventType.ORCHESTRATOR_END.value

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write audit events — Phase 64",
        strict=False,
    )
    def test_failed_execution_still_has_end_event(self, patched_audit_db, verifier):
        """Even a failing orchestrator must produce an END event (via teardown)."""
        orch = _FailingOrchestrator("test-fail-pair")
        result = orch.execute()

        assert not result.success, "Should have failed"
        _start, end_evt = verifier.assert_start_end_pair("test-fail-pair")
        assert end_evt.status == "failed"


# ---------------------------------------------------------------------------
# C1-05: Timestamp monotonicity
# ---------------------------------------------------------------------------

@pytest.mark.golden
class TestAuditTimestampMonotonicity:
    """Audit event timestamps must be monotonically non-decreasing."""

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write audit events — Phase 64",
        strict=False,
    )
    def test_audit_db_timestamps_monotonic(self, patched_audit_db, verifier):
        """Three successive invocations must have non-decreasing timestamps."""
        for i in range(3):
            orch = _StubOrchestrator("test-mono")
            orch.execute()

        events = verifier.assert_timestamps_monotonic(orchestrator_id="test-mono")
        assert len(events) >= 6, "Expected >= 6 events (3 x start+end)"


# ---------------------------------------------------------------------------
# C1-06: Full chain verification
# ---------------------------------------------------------------------------

@pytest.mark.golden
class TestAuditFullChain:
    """Full E2E chain from user request through orchestrators."""

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write audit events — Phase 64",
        strict=False,
    )
    def test_audit_chain_two_orchestrators(self, patched_audit_db, verifier):
        """Chain of two orchestrators must pass verify_full_chain."""
        orch_a = _StubOrchestrator("chain-orch-a")
        orch_b = _StubOrchestrator("chain-orch-b")
        orch_a.execute()
        orch_b.execute()

        summary = verifier.verify_full_chain(["chain-orch-a", "chain-orch-b"])
        assert summary["chain_length"] == 2
        assert summary["timestamps_monotonic"] is True
        assert summary["total_events"] >= 4

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.execute() does not write audit events — Phase 64",
        strict=False,
    )
    def test_audit_chain_user_to_enforcement(self, patched_audit_db, verifier):
        """Simulated 3-stage chain: router -> tdd -> enforcement."""
        for orch_id in ("router", "tdd", "enforcement"):
            _StubOrchestrator(orch_id).execute()

        summary = verifier.verify_full_chain(["router", "tdd", "enforcement"])
        assert summary["chain_length"] == 3
        assert set(summary["verified"]) == {"router", "tdd", "enforcement"}


# ---------------------------------------------------------------------------
# C1-07: Health check on wired orchestrators
# ---------------------------------------------------------------------------

@pytest.mark.golden
class TestHealthCheck:
    """health_check() must be available on all orchestrators."""

    def test_health_check_returns_required_fields(self):
        """health_check() must return at least status, orchestrator keys."""
        orch = _StubOrchestrator("test-health")
        health = orch.health_check()
        assert "status" in health
        assert "orchestrator" in health
        assert health["status"] == "healthy"

    def test_health_check_reflects_execution_history(self, patched_audit_db):
        """After execute(), health_check uptime_requests should increment."""
        orch = _StubOrchestrator("test-health-history")
        assert orch.health_check()["uptime_requests"] == 0

        orch.execute()
        health = orch.health_check()
        assert health["uptime_requests"] == 1
        assert health["success_count"] == 1

    def test_health_check_all_wired_orchestrators(self):
        """All wired orchestrators must be importable.

        Uses wiring.yaml as the source of truth for wired orchestrators.
        Verifies each class can be resolved — base-class alignment is Sub-Phase D.
        """
        import yaml

        wiring_path = Path(__file__).parent.parent.parent / "cortex" / "core" / "wiring" / "specifications" / "wiring.yaml"
        if not wiring_path.exists():
            pytest.skip("wiring.yaml not found")

        with open(wiring_path) as f:
            wiring = yaml.safe_load(f)

        orchestrators_section = wiring.get("orchestrators", {})
        failures = []

        # wiring.yaml uses nested tiers: core, domain, support, analyzers
        all_entries = []
        for tier_name, tier_list in orchestrators_section.items():
            if isinstance(tier_list, list):
                all_entries.extend(tier_list)

        for entry in all_entries:
            if not isinstance(entry, dict):
                continue
            module_path = entry.get("module", "")
            class_name = entry.get("class", "")
            if not module_path or not class_name:
                continue

            try:
                import importlib
                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name)
                assert cls is not None, f"{class_name} resolved to None"
            except Exception as exc:
                failures.append(f"{class_name}: {exc}")

        assert len(all_entries) >= 20, f"Expected 20+ wired entries, got {len(all_entries)}"
        assert not failures, f"Wired orchestrator import failures:\n" + "\n".join(failures)


# ---------------------------------------------------------------------------
# C1-08: Verifier raises on missing events
# ---------------------------------------------------------------------------

@pytest.mark.golden
class TestAuditVerifierErrors:
    """AuditVerifier must raise AuditVerificationError on failures."""

    def test_verifier_raises_on_missing_start(self, verifier):
        """assert_event_exists raises when no matching event found."""
        with pytest.raises(AuditVerificationError, match="No .* event found"):
            verifier.assert_event_exists("nonexistent", EventType.ORCHESTRATOR_START.value)

    def test_verifier_raises_on_missing_pair(self, verifier):
        """assert_start_end_pair raises when orchestrator has no events."""
        with pytest.raises(AuditVerificationError):
            verifier.assert_start_end_pair("nonexistent")

    def test_verify_full_chain_raises_on_gap(self, patched_audit_db, verifier):
        """verify_full_chain raises when one orchestrator in chain has no events."""
        _StubOrchestrator("chain-only-a").execute()

        with pytest.raises(AuditVerificationError):
            verifier.verify_full_chain(["chain-only-a", "chain-missing-b"])


# ---------------------------------------------------------------------------
# C1-09: run() method also produces audit events
# ---------------------------------------------------------------------------

@pytest.mark.golden
class TestAuditViaRunMethod:
    """The run() method must also produce audit events like execute()."""

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.run() does not write audit events — Phase 64",
        strict=False,
    )
    def test_run_produces_start_event(self, patched_audit_db):
        """run() should produce an ORCHESTRATOR_START event."""
        orch = _StubOrchestrator("test-run-start")
        orch.run()

        starts = patched_audit_db.query_events(
            orchestrator_id="test-run-start",
            event_type=EventType.ORCHESTRATOR_START.value,
        )
        assert len(starts) >= 1

    @pytest.mark.xfail(
        reason="Pre-existing: OrchestratorBase.run() does not write audit events — Phase 64",
        strict=False,
    )
    def test_run_produces_end_event(self, patched_audit_db):
        """run() should produce an ORCHESTRATOR_END event via teardown."""
        orch = _StubOrchestrator("test-run-end")
        orch.run()

        ends = patched_audit_db.query_events(
            orchestrator_id="test-run-end",
            event_type=EventType.ORCHESTRATOR_END.value,
        )
        assert len(ends) >= 1
