"""
cortex.orchestrators.strategies.stage_execution_strategy

Re-exports StageContext and StageExecutionStrategy from the canonical
location in cortex.orchestrators.core.

Authority: ENH-087, CORE-035 (Single Canonical Implementation)
"""

from cortex.orchestrators.core.pipeline_stage_strategy import (
    StageContext,
    StageExecutionStrategy,
)

__all__ = [
    "StageContext",
    "StageExecutionStrategy",
]
