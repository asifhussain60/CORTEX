"""
Tests for OPJMixin — zero-disruption drop-in for all orchestrators.

AC-ID: AC-OPJ-PHASE52-MIXIN
TDD Phase: RED → GREEN → REFACTOR
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import pytest
from pathlib import Path


class TestOPJMixin:
    """Tests for OPJMixin."""

    def test_mixin_provides_opj_consult(self, tmp_path: Path) -> None:
        """_opj_consult() must return a list (empty when journal is empty)."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin

        class MyOrchestrator(OPJMixin):
            name = "MyOrchestrator"

        orch = MyOrchestrator()
        orch._opj_init(registry_root=tmp_path)
        results = orch._opj_consult(operation="test_op")
        assert isinstance(results, list)

    def test_mixin_record_success_writes_entry(self, tmp_path: Path) -> None:
        """_opj_record_success() writes to the journal without raising."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin

        class MyOrchestrator(OPJMixin):
            name = "MyOrchestrator"

        orch = MyOrchestrator()
        orch._opj_init(registry_root=tmp_path)
        # Must not raise
        orch._opj_record_success(
            operation="test_op",
            context={"x": 1},
            resolution="worked",
            confidence=0.9,
        )
        shard = tmp_path / "patterns" / "success" / "my_orchestrator.yaml"
        assert shard.exists()

    def test_mixin_record_failure_writes_entry(self, tmp_path: Path) -> None:
        """_opj_record_failure() writes to the journal without raising."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin

        class MyOrchestrator(OPJMixin):
            name = "MyOrchestrator"

        orch = MyOrchestrator()
        orch._opj_init(registry_root=tmp_path)
        orch._opj_record_failure(
            operation="test_op",
            error="something broke",
            attempted_fix="tried Y",
            confidence=0.7,
        )
        shard = tmp_path / "patterns" / "failure" / "my_orchestrator.yaml"
        assert shard.exists()

    def test_mixin_does_not_change_base_class(self) -> None:
        """OPJMixin must not require or modify OrchestratorBase."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin

        # Pure standalone class — no OrchestratorBase required
        class StandaloneOrchestrator(OPJMixin):
            name = "StandaloneOrchestrator"

        orch = StandaloneOrchestrator()
        assert hasattr(orch, "_opj_consult")
        assert hasattr(orch, "_opj_record_success")
        assert hasattr(orch, "_opj_record_failure")

    def test_mixin_opj_init_is_lazy_safe(self, tmp_path: Path) -> None:
        """_opj_consult before _opj_init must return [] without crashing."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin

        class LazyOrchestrator(OPJMixin):
            name = "LazyOrchestrator"

        orch = LazyOrchestrator()
        # No _opj_init called — must not raise
        results = orch._opj_consult(operation="anything")
        assert results == []

    def test_mixin_uses_class_name_when_name_absent(self, tmp_path: Path) -> None:
        """If orchestrator has no `name` attr, uses class.__name__ as fallback."""
        from cortex.intelligence.learning.opj_mixin import OPJMixin
        import yaml

        class NamelessOrchestrator(OPJMixin):
            pass  # no `name` attr

        orch = NamelessOrchestrator()
        orch._opj_init(registry_root=tmp_path)
        orch._opj_record_success(
            operation="op",
            context={},
            resolution="ok",
            confidence=0.8,
        )
        shard = tmp_path / "patterns" / "success" / "nameless_orchestrator.yaml"
        assert shard.exists()
        data = yaml.safe_load(shard.read_text())
        assert data["entries"][0]["orchestrator"] == "NamelessOrchestrator"
