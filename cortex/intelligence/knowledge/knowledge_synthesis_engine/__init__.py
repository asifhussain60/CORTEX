"""
Knowledge Synthesis Engine package.

Phase 103-g: decomposed from knowledge_synthesis_engine.py (1,567L) god-object.

Public API (fully backwards-compatible with the flat module):
    KnowledgeSource, SynthesizedInstruction — data models
    KnowledgeSynthesisEngine                — main engine class
    get_synthesis_engine                     — singleton factory
"""
from cortex.intelligence.knowledge.knowledge_synthesis_engine.models import (
    KnowledgeSource,
    SynthesizedInstruction,
)
from cortex.intelligence.knowledge.knowledge_synthesis_engine.engine import (
    KnowledgeSynthesisEngine,
    get_synthesis_engine,
)

__all__ = [
    "KnowledgeSource",
    "SynthesizedInstruction",
    "KnowledgeSynthesisEngine",
    "get_synthesis_engine",
]
