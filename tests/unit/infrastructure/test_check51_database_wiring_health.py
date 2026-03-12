"""
Preflight test for drift lock check-51 — Database Wiring Health.

Verifies DatabaseHealthVerifier covers all DB_REGISTRY entries.
"""
from __future__ import annotations

from cortex.infrastructure.database_health_verifier import (
    DatabaseHealthReport,
    DatabaseHealthVerifier,
)
from cortex.infrastructure.env_initializer import DB_REGISTRY


class TestCheck51DatabaseWiringHealth:
    """Preflight guard: DatabaseHealthVerifier must cover all DB_REGISTRY entries."""

    def test_database_health_verifier_module_importable(self) -> None:
        # The module must exist and be importable
        assert DatabaseHealthVerifier is not None

    def test_verify_all_returns_report_type(self, tmp_path):
        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        report = v.verify_all()
        assert isinstance(report, DatabaseHealthReport)

    def test_verify_all_covers_all_db_registry_entries(self, tmp_path):
        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        report = v.verify_all()
        assert len(report.results) == len(DB_REGISTRY), (
            f"DatabaseHealthVerifier checked {len(report.results)} databases "
            f"but DB_REGISTRY declares {len(DB_REGISTRY)}"
        )

    def test_verify_all_result_names_match_registry_keys(self, tmp_path):
        v = DatabaseHealthVerifier(runtime_root=tmp_path)
        report = v.verify_all()
        covered = {r.db_name for r in report.results}
        expected = set(DB_REGISTRY.keys())
        assert covered == expected, (
            f"Missing from verification: {expected - covered}; "
            f"Extra: {covered - expected}"
        )

    def test_drift_lock_yaml_valid(self) -> None:
        import yaml
        from pathlib import Path

        lock_path = Path(
            "cortex-registry/governance/drift-locks/"
            "check-51-database-wiring-health-lock.yaml"
        )
        assert lock_path.exists(), f"Drift lock file not found: {lock_path}"
        data = yaml.safe_load(lock_path.read_text())
        assert data["check_number"] == 51
        assert data["status"] == "ACTIVE"
        assert data["enforcement_tier"] == "P0"
