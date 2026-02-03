"""
Education subsystem for CORTEX brain.

Provides intelligent educational features including:
- Next step generation
- Knowledge level detection
- Fault detection reporting
- Progressive disclosure

Authority: AC-EDUCATIONAL-INTERACTION-001
"""

from cortex.brain.education.next_step_generator import (
    NextStepGenerator,
    NextStepOption,
    NextStepContext,
    KnowledgeLevel,
    StepType,
)

__all__ = [
    "NextStepGenerator",
    "NextStepOption",
    "NextStepContext",
    "KnowledgeLevel",
    "StepType",
]
