"""
Challenge Engine Plugin Base Classes.

AC-FIX-SOLID-IMPORT-001: Created to unblock solid_analyzers import chain.

Provides the base plugin interface for SOLID analyzers and other
disagreement detection plugins used by the ChallengeEngine.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from cortex.models.canonical_enums import DisagreementType


@dataclass
class DisagreementContext:
    """Context for disagreement detection.

    Provides all necessary information for a plugin to detect
    potential issues or disagreements in code.

    Attributes:
        file_path: Path to the file being analyzed.
        source_code: Source code content.
        metadata: Additional metadata about the context.
        intent: The user's intent (IMPLEMENT, FIX, etc.).
        scope: Analysis scope.
    """

    file_path: str = ""
    source_code: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    intent: str = ""
    scope: str = "module"


class DisagreementPlugin(ABC):
    """Base class for disagreement detection plugins.

    All SOLID analyzers and challenge plugins inherit from this
    to provide a consistent interface for the ChallengeEngine.

    Subclasses must implement:
        - detect(): Check for potential disagreements
        - generate_recommendation(): Suggest improvements
    """

    @abstractmethod
    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect potential disagreements in the given context.

        Args:
            context: Analysis context with source code and metadata.

        Returns:
            Description of disagreement if found, None otherwise.
        """
        ...

    @abstractmethod
    def generate_recommendation(self, context: DisagreementContext) -> str:
        """Generate a recommendation for the detected disagreement.

        Args:
            context: Analysis context with source code and metadata.

        Returns:
            Recommendation string.
        """
        ...


__all__ = [
    "DisagreementContext",
    "DisagreementPlugin",
    "DisagreementType",
]
