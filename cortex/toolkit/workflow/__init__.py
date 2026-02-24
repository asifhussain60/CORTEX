"""Workflow orchestration — generic pipeline with step definitions.

Components:
    StepDefinition:         Step protocol (execute, rollback, validate)
    PipelineBuilder:        Fluent API for step composition
    ConditionalBranching:   if/then/else logic in pipelines
    ParallelExecution:      Fan-out/fan-in for independent steps

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
"""

__all__ = [
    "StepDefinition",
    "PipelineBuilder",
    "ConditionalBranching",
    "ParallelExecution",
]
