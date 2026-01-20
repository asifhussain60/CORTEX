"""
CORTEX LENS Module: Language-Examination-Synthesis-Knowledge Pipeline.

This module provides the 4-phase LENS pipeline for analyzing user intents,
examining codebase context, synthesizing routing decisions, and retrieving
domain knowledge.

Exports:
    LENSPipeline: Main pipeline orchestration class
    LanguagePhaseOutput: Output from Language phase
    ExaminationPhaseOutput: Output from Examination phase
    SynthesisPhaseOutput: Output from Synthesis phase
    KnowledgePhaseOutput: Output from Knowledge phase
    LENSPipelineOutput: Complete pipeline output
"""

from cortex.brain.lens.pipeline import (
    LENSPipeline,
    LanguagePhaseOutput,
    ExaminationPhaseOutput,
    SynthesisPhaseOutput,
    KnowledgePhaseOutput,
    LENSPipelineOutput,
    LanguagePhase,
    ExaminationPhase,
    SynthesisPhase,
    KnowledgePhase,
)

__all__ = [
    "LENSPipeline",
    "LanguagePhaseOutput",
    "ExaminationPhaseOutput",
    "SynthesisPhaseOutput",
    "KnowledgePhaseOutput",
    "LENSPipelineOutput",
    "LanguagePhase",
    "ExaminationPhase",
    "SynthesisPhase",
    "KnowledgePhase",
]
