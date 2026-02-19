"""
Education subsystem for CORTEX brain.

Provides intelligent educational features including:
- Next step generation
- Knowledge level detection
- Fault detection reporting
- Progressive disclosure

Authority: AC-EDUCATIONAL-INTERACTION-001
"""

from cortex.brain.education.fault_detection_reporter import (
    Fault,
    FaultCategory,
    FaultDetectionReporter,
    FaultReport,
    FaultSeverity,
)
from cortex.brain.education.knowledge_level_detector import (
    DetectionSignals,
    KnowledgeLevelDetector,
)
from cortex.brain.education.next_step_generator import (
    KnowledgeLevel,
    NextStepContext,
    NextStepGenerator,
    NextStepOption,
    StepType,
)

__all__ = [
    "NextStepGenerator",
    "NextStepOption",
    "NextStepContext",
    "KnowledgeLevel",
    "StepType",
    "KnowledgeLevelDetector",
    "DetectionSignals",
    "FaultDetectionReporter",
    "FaultReport",
    "Fault",
    "FaultSeverity",
    "FaultCategory",
]
