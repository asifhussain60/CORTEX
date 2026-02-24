# COMPAT shim — cortex.core.state.phase_state_machine → cortex.core.common.phase_state_machine
# Retained: 2026-02-24 (Phase 68-B) | Expires: 2026-05-24
from cortex.core.common.phase_state_machine import (  # noqa: F401
    PhaseState,
    TransitionEntry,
    PhaseInfo,
    StateMachineMetrics,
    InvalidTransitionError,
    PhaseNotFoundError,
    PhaseStateMachine,
)
