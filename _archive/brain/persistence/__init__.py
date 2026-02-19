"""
CORTEX Brain Persistence Layer

Cross-session knowledge persistence with versioning and pattern tracking.

AC_START: AC-PHASE27-S1-003
Authority: Phase 27 Stage 1-3

Components:
- KnowledgeStore: Cross-session knowledge persistence (Stage 1)
- LearningLoopIntegration: Universal learning loop (Stage 2)
- AgentCapabilityRegistry: Agent capability storage (Stage 3)
- AgentDiscoveryService: Capability-based discovery (Stage 3)
- AgentHandoffProtocol: Systematic handoff (Stage 3)
"""

from cortex.brain.persistence.knowledge_store import (
    KnowledgeEntry,
    KnowledgeStore,
    SessionRecord,
)
from cortex.brain.persistence.learning_loop_integration import (
    LearningLoopIntegration,
    LearningLoopMixin,
)
from cortex.brain.persistence.agent_capability_registry import (
    AgentCapabilityRegistry,
)
from cortex.brain.persistence.agent_discovery_service import (
    AgentDiscoveryService,
)
from cortex.brain.persistence.agent_handoff_protocol import (
    AgentHandoffProtocol,
)

__all__ = [
    "KnowledgeStore",
    "KnowledgeEntry",
    "SessionRecord",
    "LearningLoopIntegration",
    "LearningLoopMixin",
    "AgentCapabilityRegistry",
    "AgentDiscoveryService",
    "AgentHandoffProtocol",
]

# AC_COMPLETE: AC-PHASE27-S1-003 ✅ Persistence module exports
