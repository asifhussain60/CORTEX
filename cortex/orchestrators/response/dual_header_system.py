"""
Dual header system implementation for CORTEX vs CORTEX Architect prompts.
Provides differentiated headers based on execution context.

Module: cortex.orchestrators.response.dual_header_system
Author: Asif Hussain
Created: 2026-02-07
Version: 1.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

# ============================================================================
# ENUMERATIONS
# ============================================================================


class HeaderType(str, Enum):
    """Header type enumeration for response differentiation."""

    CORTEX_OPERATIONS = "cortex_operations"
    """CORTEX.prompt.md - Operational orchestrator headers"""

    CORTEX_ARCHITECT = "cortex_architect"
    """cortex-architect.prompt.md - Self-development planning headers"""


class ResponseMode(str, Enum):
    """Response mode enumeration."""

    OPERATIONS = "Operations"
    AUDIT = "Audit"
    TDD = "TDD"
    DESIGN = "Design"
    PLAN = "Plan"
    QUERY = "Query"
    DIGEST = "Digest"
    META_AUDIT = "Meta-Audit"


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class HeaderSpec:
    """Specification for a header type."""

    type: HeaderType
    icon: str
    title: str
    mode_descriptions: List[str]
    keywords: List[str]
    usage_context: str


@dataclass
class HeaderContext:
    """Context information for header rendering."""

    mode: ResponseMode
    author: str = "Asif Hussain"
    scope: str = "Implementation"
    orchestrator: Optional[str] = None
    phase: Optional[str] = None


# ============================================================================
# HEADER SPECIFICATIONS
# ============================================================================


CORTEX_OPERATIONS_SPEC = HeaderSpec(
    type=HeaderType.CORTEX_OPERATIONS,
    icon="🧠",
    title="CORTEX",
    mode_descriptions=[
        "Brain orchestrator for operational execution",
        "Handles code synthesis, testing, deployment",
        "Active orchestrator with full capability access"
    ],
    keywords=["operations", "execution", "orchestrator", "TDD", "synthesis"],
    usage_context="Used in CORTEX.prompt.md for operational responses"
)

CORTEX_ARCHITECT_SPEC = HeaderSpec(
    type=HeaderType.CORTEX_ARCHITECT,
    icon="🏛️",
    title="CORTEX Architect",
    mode_descriptions=[
        "HEPTA-MODE capabilities: /audit /plan /query /design /digest /meta-audit",
        "Dedicated to CORTEX self-development and architectural planning",
        "Strategic planning and intelligence system"
    ],
    keywords=["architect", "planning", "design", "audit", "strategy", "self-development"],
    usage_context="Used in cortex-architect.prompt.md for strategic responses"
)


# ============================================================================
# ABSTRACT BASE CLASSES
# ============================================================================


class HeaderRenderer(ABC):
    """Abstract base class for header rendering."""

    @abstractmethod
    def render(self, context: HeaderContext) -> str:
        """Render header with given context."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate header specification."""
        pass


# ============================================================================
# HEADER RENDERERS
# ============================================================================


class CORTEXOperationsHeaderRenderer(HeaderRenderer):
    """Renderer for CORTEX operations headers."""

    def __init__(self):
        self.spec = CORTEX_OPERATIONS_SPEC

    def render(self, context: HeaderContext) -> str:
        """
        Render CORTEX operations header.

        Format:
            ## 🧠 CORTEX {mode}
            **Author:** {author} | **Orchestrator:** {orchestrator} ✅

            ---

        Args:
            context: Header context with mode, author, etc.

        Returns:
            Rendered header string
        """
        lines = [
            f"## {self.spec.icon} {self.spec.title} {context.mode.value}",
            f"**Author:** {context.author}",
        ]

        if context.orchestrator:
            lines[-1] += f" | **Orchestrator:** {context.orchestrator}"

        lines[-1] += " ✅"
        lines.append("")
        lines.append("---")

        return "\n".join(lines)

    def validate(self) -> bool:
        """Validate header specification."""
        return (
            self.spec.icon == "🧠"
            and self.spec.title == "CORTEX"
            and HeaderType.CORTEX_OPERATIONS in [HeaderType.CORTEX_OPERATIONS]
        )


class CORTEXArchitectHeaderRenderer(HeaderRenderer):
    """Renderer for CORTEX Architect headers."""

    def __init__(self):
        self.spec = CORTEX_ARCHITECT_SPEC

    def render(self, context: HeaderContext) -> str:
        """
        Render CORTEX Architect header with mode hints.

        Format:
            ## 🏛️ CORTEX Architect {mode}
            **Author:** {author} | **Modes:** /audit /plan /query /design /digest /meta-audit ✅

            **Dedicated to CORTEX self-development**

            ---

        Args:
            context: Header context with mode, author, etc.

        Returns:
            Rendered header string
        """
        lines = [
            f"## {self.spec.icon} {self.spec.title} {context.mode.value}",
            f"**Author:** {context.author} | **Modes:** /audit /plan /query /design /digest /meta-audit ✅",
            "",
            "**Dedicated to CORTEX self-development and architectural planning**",
            "",
            "---",
        ]

        return "\n".join(lines)

    def validate(self) -> bool:
        """Validate header specification."""
        return (
            self.spec.icon == "🏛️"
            and "Architect" in self.spec.title
            and HeaderType.CORTEX_ARCHITECT in [HeaderType.CORTEX_ARCHITECT]
        )


# ============================================================================
# HEADER FACTORY
# ============================================================================


class HeaderRendererFactory:
    """Factory for creating header renderers."""

    _renderers: Dict[HeaderType, HeaderRenderer] = {}

    @classmethod
    def create(cls, header_type: HeaderType) -> HeaderRenderer:
        """
        Create header renderer by type.

        Args:
            header_type: Type of header to create (CORTEX_OPERATIONS or CORTEX_ARCHITECT)

        Returns:
            HeaderRenderer instance

        Raises:
            ValueError: If header_type is not supported
        """
        if header_type not in cls._renderers:
            if header_type == HeaderType.CORTEX_OPERATIONS:
                cls._renderers[header_type] = CORTEXOperationsHeaderRenderer()
            elif header_type == HeaderType.CORTEX_ARCHITECT:
                cls._renderers[header_type] = CORTEXArchitectHeaderRenderer()
            else:
                raise ValueError(f"Unsupported header type: {header_type}")

        return cls._renderers[header_type]

    @classmethod
    def get_renderer_for_prompt(cls, prompt_name: str) -> HeaderRenderer:
        """
        Get appropriate header renderer for prompt name.

        Args:
            prompt_name: Name of prompt (e.g., "CORTEX.prompt.md")

        Returns:
            Appropriate HeaderRenderer
        """
        if "architect" in prompt_name.lower():
            return cls.create(HeaderType.CORTEX_ARCHITECT)
        else:
            return cls.create(HeaderType.CORTEX_OPERATIONS)


# ============================================================================
# HEADER MANAGER
# ============================================================================


class DualHeaderManager:
    """Manager for dual header system."""

    def __init__(self):
        self.factory = HeaderRendererFactory()

    def get_header(
        self,
        header_type: HeaderType,
        context: HeaderContext
    ) -> str:
        """
        Get rendered header for given type and context.

        Args:
            header_type: Type of header
            context: Header context

        Returns:
            Rendered header string
        """
        renderer = self.factory.create(header_type)
        if not renderer.validate():
            raise RuntimeError(f"Header validation failed for type: {header_type}")
        return renderer.render(context)

    def validate_all_headers(self) -> Dict[HeaderType, bool]:
        """
        Validate all header types.

        Returns:
            Dictionary mapping HeaderType to validation result
        """
        return {
            HeaderType.CORTEX_OPERATIONS: self.factory.create(
                HeaderType.CORTEX_OPERATIONS
            ).validate(),
            HeaderType.CORTEX_ARCHITECT: self.factory.create(
                HeaderType.CORTEX_ARCHITECT
            ).validate(),
        }


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "HeaderType",
    "ResponseMode",
    "HeaderSpec",
    "HeaderContext",
    "HeaderRenderer",
    "CORTEXOperationsHeaderRenderer",
    "CORTEXArchitectHeaderRenderer",
    "HeaderRendererFactory",
    "DualHeaderManager",
    "CORTEX_OPERATIONS_SPEC",
    "CORTEX_ARCHITECT_SPEC",
]
