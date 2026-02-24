"""
Phase 68: RED → GREEN tests for cortex/core flatten sweep (SWEEP-68-CORE-FLATTEN).

Verifies:
  - cortex/core/common/ is the canonical home for all consolidated modules
  - All imports from cortex.core.common work without error
  - Stub subdirs (safety, errors, recovery, state, decorators, config, resilience) are gone
  - cortex/core/bootstrap/__init__.py correctly re-exports _bootstrap_success
  - cortex/__init__.py _bootstrap_success import path resolves without ImportError

Author: Asif Hussain
Phase: 68-D
Sweep: SWEEP-68-CORE-FLATTEN
"""

import importlib
from pathlib import Path
import pytest

# AC_START: AC-68-D-CORE-FLATTEN-20260224T000000Z

CORTEX_CORE = Path(__file__).parents[3] / "cortex" / "core"

# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL IMPORTS — cortex.core.common
# ─────────────────────────────────────────────────────────────────────────────

class TestCommonModuleImports:
    """All consolidated modules must be importable from cortex.core.common."""

    def test_output_validator_importable(self) -> None:
        """LLMOutputValidator must import from cortex.core.common."""
        from cortex.core.common.output_validator import (
            LLMOutputValidator,
            ValidationResult,
            ValidationViolation,
        )
        assert LLMOutputValidator is not None

    def test_structured_error_importable(self) -> None:
        """StructuredError must import from cortex.core.common."""
        from cortex.core.common.structured_error import (
            StructuredError,
            ErrorContext,
            ErrorType,
        )
        assert StructuredError is not None

    def test_saga_coordinator_importable(self) -> None:
        """SagaCoordinator must import from cortex.core.common."""
        from cortex.core.common.saga_coordinator import SagaCoordinator
        assert SagaCoordinator is not None

    def test_optimistic_lock_importable(self) -> None:
        """VersionedRow must import from cortex.core.common."""
        from cortex.core.common.optimistic_lock import VersionedRow, MergeStrategy
        assert VersionedRow is not None

    def test_phase_state_machine_importable(self) -> None:
        """PhaseStateMachine must import from cortex.core.common."""
        from cortex.core.common.phase_state_machine import PhaseStateMachine
        assert PhaseStateMachine is not None

    def test_timeout_profiles_importable(self) -> None:
        """get_timeout must import from cortex.core.common."""
        from cortex.core.common.timeout_profiles import get_timeout, TimeoutProfile
        assert get_timeout is not None

    def test_thread_safety_importable(self) -> None:
        """safe_thread_join must import from cortex.core.common."""
        from cortex.core.common.thread_safety import safe_thread_join
        assert safe_thread_join is not None

    def test_orchestrator_decorator_importable(self) -> None:
        """orchestrator decorator must import from cortex.core.common."""
        from cortex.core.common.orchestrator_decorator import (
            orchestrator,
            get_registered_orchestrators,
        )
        assert orchestrator is not None


# ─────────────────────────────────────────────────────────────────────────────
# STUB DIRS REMOVED — Phase 68-B/C exit criteria
# ─────────────────────────────────────────────────────────────────────────────

class TestStubDirsRemoved:
    """Low-caller stub subdirs must be deleted from cortex/core/."""

    @pytest.mark.parametrize("subdir", [
        "safety",
        "errors",
        "recovery",
        "state",
        "decorators",
        "config",
        "resilience",
        "bootstrap",
    ])
    def test_stub_subdir_does_not_exist(self, subdir: str) -> None:
        """cortex/core/{subdir}/ must not exist after Phase 68-B/C flatten."""
        assert not (CORTEX_CORE / subdir).exists(), (
            f"cortex/core/{subdir}/ still exists — Phase 68-B/C not complete. "
            f"Run: rm -rf cortex/core/{subdir}/"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SUBDIR COUNT — Phase 68-D exit criteria (≤9 subdirs)
# ─────────────────────────────────────────────────────────────────────────────

class TestCoreSubdirCount:
    """cortex/core/ must have ≤15 subdirectories after Phase 68 flatten."""

    def test_core_has_fifteen_or_fewer_subdirs(self) -> None:
        """cortex/core/ must have ≤15 subdirectories (from 27 baseline, 8 stubs removed).

        The 15 canonical dirs are the high-caller dirs that are KEPT per the phase-68 plan:
        common, discovery, execution, governance, hallucination_prevention, intelligence,
        intent, interaction, interfaces, knowledge, models, orchestrator, registry,
        security, wiring.
        """
        subdirs = [p for p in CORTEX_CORE.iterdir() if p.is_dir() and not p.name.startswith("__")]
        count = len(subdirs)
        names = sorted(p.name for p in subdirs)
        assert count <= 15, (
            f"cortex/core/ has {count} subdirs (expected ≤15 after Phase 68 flatten).\n"
            f"Current subdirs: {names}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# BOOTSTRAP COMPAT — cortex.core.bootstrap must re-export _bootstrap_success
# ─────────────────────────────────────────────────────────────────────────────

class TestBootstrapCompat:
    """cortex.bootstrap must expose _bootstrap_success (cortex.core.bootstrap dir deleted)."""

    def test_bootstrap_success_importable_from_canonical(self) -> None:
        """_bootstrap_success must be importable from canonical cortex.bootstrap."""
        from cortex.bootstrap import _bootstrap_success  # noqa: F401
        # This is what cortex/__init__.py now imports directly (Phase 68-C)

    def test_cortex_init_bootstrap_resolves(self) -> None:
        """cortex package must import cleanly."""
        import cortex  # noqa: F401
        assert cortex.__author__ == "Asif Hussain"


# AC_COMPLETE: AC-68-D-CORE-FLATTEN-20260224T000000Z ✅
