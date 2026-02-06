"""Refactoring tool adapter plugin architecture.

This module provides the base adapter interface for integrating external
refactoring tools (Rope, Roslyn, TypeScript LSP, etc.) with CORTEX.

Classes:
    RefactoringToolAdapter: Abstract base class for refactoring tool adapters.
    RefactoringCapability: Dataclass describing a refactoring operation.
    RefactoringRequest: Dataclass for refactoring requests.
    RefactoringResult: Dataclass for refactoring results.
    RefactoringOperationType: Enum for supported refactoring operations.
"""

from .refactoring_tool_adapter import (
    RefactoringCapability,
    RefactoringOperationType,
    RefactoringRequest,
    RefactoringResult,
    RefactoringToolAdapter,
)

__all__ = [
    "RefactoringToolAdapter",
    "RefactoringCapability",
    "RefactoringRequest",
    "RefactoringResult",
    "RefactoringOperationType",
]
