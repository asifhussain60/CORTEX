"""mode_controller.py — re-export from canonical cortex.core.core.mode_controller.

CORE-035: Single canonical implementation lives in cortex/core/core/mode_controller.py.
This module re-exports ModeController and RuntimeMode for the canonical
``cortex.core.mode_controller`` import path.
"""

from cortex.core.core.mode_controller import ModeController, RuntimeMode  # noqa: F401

__all__ = ["ModeController", "RuntimeMode"]

