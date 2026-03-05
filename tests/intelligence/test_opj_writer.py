"""
Tests for OPJWriter — Operational Pattern Journal writer.

TDD RED phase: tests defined before implementation.
AC_START: AC-OPJ-WRITER-001

Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import yaml
from pathlib import Path
from datetime import datetime, timezone

import pytest

from cortex.intelligence.learning.opj_writer import OPJWriter, OPJEntry, OPJOutcome


class TestOPJWriter:
    """Unit tests for OPJWriter."""

    @pytest.fixture()
    def tmp_registry(self, tmp_path: Path) -> Path:
        """Provide a temporary cortex-registry root."""
        registry = tmp_path / "cortex-registry"
        (registry / "patterns" / "success").mkdir(parents=True)
        (registry / "patterns" / "failure").mkdir(parents=True)
        return registry

    @pytest.fixture()
    def writer(self, tmp_registry: Path) -> OPJWriter:
        """OPJWriter pointed at temporary registry."""
        return OPJWriter(registry_root=tmp_registry)

    # ------------------------------------------------------------------
    # record_success
    # ------------------------------------------------------------------

    def test_record_success_creates_yaml_file(self, writer: OPJWriter, tmp_registry: Path) -> None:
        """record_success must create a YAML file under success/."""
        writer.record_success(
            orchestrator="DigestSessionOrchestrator",
            operation="process_markdown",
            context={"file": "README.md"},
            resolution="chunked into 3 sections, confidence 0.92",
            confidence=0.92,
        )
        target = tmp_registry / "patterns" / "success" / "digest_session_orchestrator.yaml"
        assert target.exists(), "YAML file must be created for orchestrator"

    def test_record_success_entry_has_required_fields(self, writer: OPJWriter, tmp_registry: Path) -> None:
        """Every success entry must contain mandatory OPJ fields."""
        writer.record_success(
            orchestrator="TDDOrchestrator",
            operation="run_red_phase",
            context={"module": "opj_writer"},
            resolution="test written, implementation pending",
            confidence=0.88,
        )
        target = tmp_registry / "patterns" / "success" / "tdd_orchestrator.yaml"
        data = yaml.safe_load(target.read_text())
        entries = data["entries"]
        assert len(entries) == 1
        entry = entries[0]
        assert entry["outcome"] == "success"
        assert entry["orchestrator"] == "TDDOrchestrator"
        assert entry["operation"] == "run_red_phase"
        assert "resolution" in entry
        assert "confidence" in entry
        assert "recorded_at" in entry
        assert "pattern_id" in entry

    def test_record_success_appends_not_overwrites(self, writer: OPJWriter, tmp_registry: Path) -> None:
        """Multiple calls must append entries, not overwrite."""
        for i in range(3):
            writer.record_success(
                orchestrator="EnforcementOrchestrator",
                operation="validate_rule",
                context={"rule": f"CORE-{i:03d}"},
                resolution=f"rule CORE-{i:03d} passed",
                confidence=0.9,
            )
        target = tmp_registry / "patterns" / "success" / "enforcement_orchestrator.yaml"
        data = yaml.safe_load(target.read_text())
        assert len(data["entries"]) == 3

    # ------------------------------------------------------------------
    # record_failure
    # ------------------------------------------------------------------

    def test_record_failure_creates_yaml_file(self, writer: OPJWriter, tmp_registry: Path) -> None:
        """record_failure must create a YAML file under failure/."""
        writer.record_failure(
            orchestrator="DigestSessionOrchestrator",
            operation="process_markdown",
            error="UnicodeDecodeError on binary file",
            attempted_fix="skip binary, retry with encoding='latin-1'",
            confidence=0.75,
        )
        target = tmp_registry / "patterns" / "failure" / "digest_session_orchestrator.yaml"
        assert target.exists()

    def test_record_failure_entry_has_required_fields(self, writer: OPJWriter, tmp_registry: Path) -> None:
        """Every failure entry must contain mandatory OPJ fields."""
        writer.record_failure(
            orchestrator="BulkDigestOrchestrator",
            operation="process_directory",
            error="PermissionError accessing /restricted",
            attempted_fix="skipped restricted paths, logged warning",
            confidence=0.6,
        )
        target = tmp_registry / "patterns" / "failure" / "bulk_digest_orchestrator.yaml"
        data = yaml.safe_load(target.read_text())
        entry = data["entries"][0]
        assert entry["outcome"] == "failure"
        assert entry["error"] == "PermissionError accessing /restricted"
        assert "attempted_fix" in entry
        assert "pattern_id" in entry
        assert "recorded_at" in entry

    # ------------------------------------------------------------------
    # _registry.yaml index
    # ------------------------------------------------------------------

    def test_registry_index_updated_on_write(self, writer: OPJWriter, tmp_registry: Path) -> None:
        """_registry.yaml must be updated after every write."""
        writer.record_success(
            orchestrator="TDDOrchestrator",
            operation="run_green_phase",
            context={},
            resolution="all tests green",
            confidence=0.95,
        )
        registry_index = tmp_registry / "patterns" / "_registry.yaml"
        assert registry_index.exists(), "_registry.yaml must exist after first write"
        data = yaml.safe_load(registry_index.read_text())
        assert "entries" in data
        assert len(data["entries"]) >= 1

    def test_registry_index_contains_pattern_id_and_outcome(self, writer: OPJWriter, tmp_registry: Path) -> None:
        """Registry index entries must reference pattern_id and outcome."""
        writer.record_failure(
            orchestrator="VacuumOrchestrator",
            operation="cleanup_markdown",
            error="file locked by another process",
            attempted_fix="deferred to next cycle",
            confidence=0.5,
        )
        registry_index = tmp_registry / "patterns" / "_registry.yaml"
        data = yaml.safe_load(registry_index.read_text())
        entry = data["entries"][0]
        assert "pattern_id" in entry
        assert "outcome" in entry
        assert "orchestrator" in entry
        assert "operation" in entry
        assert "file_path" in entry

    # ------------------------------------------------------------------
    # OPJEntry dataclass
    # ------------------------------------------------------------------

    def test_opj_entry_serialises_to_dict(self) -> None:
        """OPJEntry.to_dict() must include all mandatory fields."""
        entry = OPJEntry(
            pattern_id="OPJ-TEST-001",
            orchestrator="TestOrchestrator",
            operation="test_op",
            outcome=OPJOutcome.SUCCESS,
            confidence=0.8,
            context={},
            resolution="worked",
            recorded_at=datetime.now(timezone.utc).isoformat(),
        )
        d = entry.to_dict()
        assert d["pattern_id"] == "OPJ-TEST-001"
        assert d["outcome"] == "success"
        assert d["confidence"] == 0.8

    def test_pattern_id_is_unique_per_entry(self, writer: OPJWriter, tmp_registry: Path) -> None:
        """Each call to record_* must produce a unique pattern_id."""
        ids = set()
        for i in range(5):
            writer.record_success(
                orchestrator="TestOrchestrator",
                operation="op",
                context={"i": i},
                resolution="ok",
                confidence=0.9,
            )
        target = tmp_registry / "patterns" / "success" / "test_orchestrator.yaml"
        data = yaml.safe_load(target.read_text())
        for entry in data["entries"]:
            ids.add(entry["pattern_id"])
        assert len(ids) == 5, "All pattern_ids must be unique"
