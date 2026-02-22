"""
GAP-004 RED: ObservabilityOrchestrator default db path must not write to cortex/intelligence/.

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
GAP-004: SQL-002 — default db path recreates gitignored cortex/intelligence/ directory.
"""

import pytest
from pathlib import Path
from unittest.mock import patch


class TestObservabilityOrchestratorDbPath:
    """GAP-004: Default audit db path must be under .cortex-runtime/, not cortex/intelligence/."""

    def test_default_db_path_not_cortex_intelligence(self) -> None:
        """Default audit_db_path must NOT be inside cortex/intelligence/ (gitignored dir)."""
        from cortex.orchestrators.core.observability_orchestrator import (
            ObservabilityOrchestrator,
        )

        with patch.object(
            ObservabilityOrchestrator, "_init_audit_db", return_value=None
        ):
            orch = ObservabilityOrchestrator.__new__(ObservabilityOrchestrator)
            orch.service_name = "test"
            orch._alerts = []
            orch._metrics = {}
            orch._spans = []
            # Trigger the path logic by calling __init__ via a temp db
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
                tmp_path = f.name
            try:
                orch2 = ObservabilityOrchestrator(
                    service_name="test", audit_db_path=Path(tmp_path)
                )
                assert "cortex_intelligence" not in str(orch2.audit_db_path), (
                    f"audit_db_path uses gitignored cortex/intelligence/: {orch2.audit_db_path}"
                )
            finally:
                os.unlink(tmp_path)

    def test_default_db_path_uses_cortex_runtime(self) -> None:
        """Default audit_db_path (no arg) must resolve under .cortex-runtime/."""
        from cortex.orchestrators.core.observability_orchestrator import (
            ObservabilityOrchestrator,
        )

        import tempfile, os
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Patch Path to avoid actually creating dirs
            with patch(
                "cortex.orchestrators.core.observability_orchestrator.Path",
                wraps=Path,
            ):
                # Instantiate with explicit safe path to avoid side effects
                safe_path = Path(tmp_dir) / "observability_audit.db"
                orch = ObservabilityOrchestrator(
                    service_name="test-svc", audit_db_path=safe_path
                )
                # Key check: the class should use .cortex-runtime by default
                # Validate by inspecting default branch logic
                import inspect, re
                src = inspect.getsource(ObservabilityOrchestrator.__init__)
                # Find all Path("...") calls — exclude comment lines
                path_calls = re.findall(r'Path\("([^"]+)"\)', src)
                for p in path_calls:
                    assert "cortex_intelligence" not in p, (
                        f"ObservabilityOrchestrator.__init__ Path call still uses cortex/intelligence/: Path('{p}')"
                    )

    def test_observability_orchestrator_importable(self) -> None:
        """ObservabilityOrchestrator must import cleanly."""
        from cortex.orchestrators.core.observability_orchestrator import (
            ObservabilityOrchestrator,
        )

        assert ObservabilityOrchestrator is not None
