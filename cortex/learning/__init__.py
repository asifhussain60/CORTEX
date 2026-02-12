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

from cortex.learning.confidence_scorer import (
    ConfidenceLevel,
    ConfidenceScorer,
)
from cortex.learning.intelligence_validator import (
    IntelligenceValidator,
    ValidationReport,
    get_intelligence_validator,
)
from cortex.learning.knowledge_merger import (
    KnowledgeMerger,
    MergeStrategy,
)
from cortex.learning.learning_dashboard import (
    LearningDashboard,
    MetricsSnapshot,
    get_learning_dashboard,
)
from cortex.learning.orchestrator_integration_mixin import (
    OrchestratorLearningMixin,
)
from cortex.learning.pattern_extractor import (
    ExtractedPattern,
    PatternExtractor,
)
from cortex.learning.universal_learning_loop import (
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
    # Pattern Extraction
    "PatternExtractor",
    "ExtractedPattern",
    # Knowledge Merging
    "KnowledgeMerger",
    "MergeStrategy",
    # Confidence Scoring
    "ConfidenceScorer",
    "ConfidenceLevel",
    # Orchestrator Integration
    "OrchestratorLearningMixin",
    # Validation
    "IntelligenceValidator",
    "ValidationReport",
    "get_intelligence_validator",
    # Dashboard
    "LearningDashboard",
    "MetricsSnapshot",
    "get_learning_dashboard",
]
