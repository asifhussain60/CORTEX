"""
Tests for OPJModels — shared dataclasses for the Operational Pattern Journal.

AC-ID: AC-OPJ-PHASE52-MODELS
TDD Phase: RED → GREEN → REFACTOR
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone


class TestOPJEntry:
    """Tests for OPJEntry dataclass."""

    def test_opj_entry_success_fields_present(self) -> None:
        """OPJEntry with outcome=success must carry resolution and context."""
        from cortex.intelligence.learning.opj_models import OPJEntry, OPJOutcome

        entry = OPJEntry(
            entry_id="OPJ-TEST-20260222120000",
            orchestrator="TestOrchestrator",
            operation="test_op",
            outcome=OPJOutcome.SUCCESS,
            confidence=0.9,
            resolution="it worked because X",
            context={"key": "value"},
        )
        assert entry.outcome == OPJOutcome.SUCCESS
        assert entry.resolution == "it worked because X"
        assert entry.context == {"key": "value"}
        assert entry.confidence == 0.9

    def test_opj_entry_failure_fields_present(self) -> None:
        """OPJEntry with outcome=failure must carry error, attempted_fix, root_cause, avoid_in_future."""
        from cortex.intelligence.learning.opj_models import OPJEntry, OPJOutcome

        entry = OPJEntry(
            entry_id="OPJ-TEST-20260222130000",
            orchestrator="TestOrchestrator",
            operation="test_op",
            outcome=OPJOutcome.FAILURE,
            confidence=0.85,
            error="something broke",
            attempted_fix="tried Y",
            root_cause="because Z",
            avoid_in_future="never do Z",
        )
        assert entry.outcome == OPJOutcome.FAILURE
        assert entry.error == "something broke"
        assert entry.attempted_fix == "tried Y"
        assert entry.root_cause == "because Z"
        assert entry.avoid_in_future == "never do Z"

    def test_opj_entry_timestamp_defaults_to_now(self) -> None:
        """OPJEntry.timestamp should default to current datetime."""
        from cortex.intelligence.learning.opj_models import OPJEntry, OPJOutcome

        before = datetime.now(timezone.utc)
        entry = OPJEntry(
            entry_id="OPJ-TEST-20260222140000",
            orchestrator="TestOrchestrator",
            operation="test_op",
            outcome=OPJOutcome.SUCCESS,
            confidence=0.7,
        )
        after = datetime.now(timezone.utc)
        assert before <= entry.timestamp <= after

    def test_opj_entry_to_dict_roundtrip(self) -> None:
        """OPJEntry.to_dict() must produce a dict with all required keys."""
        from cortex.intelligence.learning.opj_models import OPJEntry, OPJOutcome

        entry = OPJEntry(
            entry_id="OPJ-TEST-20260222150000",
            orchestrator="TestOrchestrator",
            operation="test_op",
            outcome=OPJOutcome.SUCCESS,
            confidence=0.9,
            resolution="worked",
        )
        d = entry.to_dict()
        assert d["entry_id"] == "OPJ-TEST-20260222150000"
        assert d["orchestrator"] == "TestOrchestrator"
        assert d["operation"] == "test_op"
        assert d["outcome"] == "success"
        assert d["confidence"] == 0.9

    def test_opj_entry_id_format_validated(self) -> None:
        """entry_id must match OPJ-{ORCHESTRATOR}-{TIMESTAMP} pattern."""
        from cortex.intelligence.learning.opj_models import OPJEntry, OPJOutcome, OPJValidationError

        with pytest.raises(OPJValidationError, match="entry_id"):
            OPJEntry(
                entry_id="INVALID-ID",
                orchestrator="TestOrchestrator",
                operation="test_op",
                outcome=OPJOutcome.SUCCESS,
                confidence=0.9,
            )

    def test_opj_entry_confidence_range_enforced(self) -> None:
        """confidence must be between 0.0 and 1.0 inclusive."""
        from cortex.intelligence.learning.opj_models import OPJEntry, OPJOutcome, OPJValidationError

        with pytest.raises(OPJValidationError, match="confidence"):
            OPJEntry(
                entry_id="OPJ-TEST-20260222160000",
                orchestrator="TestOrchestrator",
                operation="test_op",
                outcome=OPJOutcome.SUCCESS,
                confidence=1.5,
            )

    def test_opj_outcome_enum_values(self) -> None:
        """OPJOutcome must have SUCCESS and FAILURE values."""
        from cortex.intelligence.learning.opj_models import OPJOutcome

        assert OPJOutcome.SUCCESS.value == "success"
        assert OPJOutcome.FAILURE.value == "failure"
