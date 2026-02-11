"""
__init__.py for orchestrator strategies package.

ENH-087 Track 1.1: Stage Execution Strategy Pattern.
ENH-087 Track 1.2: Stage 2/3/4 Strategies.
ENH-087 Track 1.3: MasterOrchestrator Refactoring.
"""

from cortex.orchestrators.strategies.stage_execution_strategy import (
    StageContext,
    StageExecutionStrategy,
)
from cortex.orchestrators.strategies.stage1_comprehension_strategy import (
    Stage1ComprehensionStrategy,
)
from cortex.orchestrators.strategies.stage234_strategies import (
    Stage2IntentClassificationStrategy,
    Stage3ComplianceValidationStrategy,
    Stage4DomainExecutionStrategy,
)

__all__ = [
    "StageContext",
    "StageExecutionStrategy",
    "Stage1ComprehensionStrategy",
    "Stage2IntentClassificationStrategy",
    "Stage3ComplianceValidationStrategy",
    "Stage4DomainExecutionStrategy",
]
