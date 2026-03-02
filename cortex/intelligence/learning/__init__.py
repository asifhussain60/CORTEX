"""
Learning module for CORTEX - Universal Learning Loop.

Phase 71: Universal Learning Infrastructure
Provides automatic pattern extraction and knowledge integration for all orchestrators.

Components:
- S1: UniversalLearningLoop - Core learning coordinator
- S2: OrchestratorBaseProtocol Phase 6 - Protocol-level learning
- S3: MCPLearningInterceptor - MCP gateway learning capture
- S4: TestValueScorer - Test quality measurement
- S5: OrchestratorLearningMixin - Orchestrator integration
- S6: IntelligenceValidator - E2E validation
- S7: LearningDashboard - Metrics and visualization
"""

from cortex.intelligence.learning.reinforcement_signal import (
    ReinforcementEngine,
    ReinforcementSignal,
    SignalType,
)
from cortex.orchestrators.validation.confidence_scorer import (
    ConfidenceScorer,
)
from cortex.lens.schemas.ldv1_schema import (
    ConfidenceLevel,
)
from cortex.intelligence.learning.intelligence_validator import (
    IntelligenceValidator,
    ValidationReport,
    get_intelligence_validator,
)
from cortex.intelligence.learning.knowledge_merger import (
    KnowledgeMerger,
    MergeStrategy,
)
from cortex.intelligence.learning.learning_dashboard import (
    LearningDashboard,
    MetricsSnapshot,
    get_learning_dashboard,
)
from cortex.intelligence.learning.orchestrator_learning_mixin import (
    OrchestratorLearningMixin,
    LearningContext,
)
from cortex.intelligence.learning.orchestrator_integration_mixin import (
    OrchestratorIntegrationMixin,
)
from cortex.intelligence.learning.pattern_extractor import (
    ExtractedPattern,
    PatternExtractor,
)
from cortex.intelligence.learning.universal_learning_loop import (
    LearningCapture,
    PatternType,
    UniversalLearningLoop,
    get_learning_loop,
)

__all__ = [
    # Universal Learning Loop
    "UniversalLearningLoop",
    "get_learning_loop",
    "LearningCapture",
    "PatternType",
    # Reinforcement Signal (Phase 83)
    "ReinforcementSignal",
    "ReinforcementEngine",
    "SignalType",
    # Pattern Extraction
    "PatternExtractor",
    "ExtractedPattern",
    # Knowledge Merging
    "KnowledgeMerger",
    "MergeStrategy",
    # Confidence Scoring
    "ConfidenceScorer",
    "ConfidenceLevel",
    # Orchestrator Integration (Phase 71 S5)
    "OrchestratorIntegrationMixin",
    "OrchestratorLearningMixin",  # canonical (orchestrator_learning_mixin.py)
    "LearningContext",
    # Validation
    "IntelligenceValidator",
    "ValidationReport",
    "get_intelligence_validator",
    # Dashboard
    "LearningDashboard",
    "MetricsSnapshot",
    "get_learning_dashboard",
]
