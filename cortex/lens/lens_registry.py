"""Registry-based Analyzer Self-Wiring System

Enables LENS analyzers to declare capabilities via decorator,
eliminating manual wiring in YAML files.

Author: CORTEX Framework
Phase: PHASE-97 S3
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Set


class AnalyzerCapability(Enum):
    """Analyzer capability types."""

    AST_ANALYSIS = "ast_analysis"
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    DEPENDENCIES = "dependencies"
    API_DISCOVERY = "api_discovery"
    DATABASE = "database"
    CONFIG = "config"
    GIT_HISTORY = "git_history"
    TECH_STACK = "tech_stack"
    COMPLEXITY = "complexity"
    DUPLICATES = "duplicates"
    DOCUMENTATION = "documentation"


class LanguageSupport(Enum):
    """Supported programming languages."""

    PYTHON = "python"
    CSHARP = "csharp"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    AGNOSTIC = "agnostic"  # Language-agnostic analyzers


@dataclass
class AnalyzerMetadata:
    """Metadata for registered analyzer.

    Attributes:
        name: Analyzer class name
        capabilities: Set of analyzer capabilities
        languages: Supported languages
        priority: Execution priority (lower = higher priority)
        description: Human-readable description
        module_path: Python module path
    """

    name: str
    capabilities: Set[AnalyzerCapability]
    languages: Set[LanguageSupport]
    priority: int = 100
    description: str = ""
    module_path: str = ""


class AnalyzerRegistry:
    """Central registry for LENS analyzers.

    Maintains catalog of all analyzers with their capabilities
    and routing information.

    Attributes:
        _analyzers: Registered analyzer metadata
        _capability_index: Capability → analyzer names mapping
        _language_index: Language → analyzer names mapping
    """

    def __init__(self) -> None:
        """Initialize analyzer registry."""
        self._analyzers: Dict[str, AnalyzerMetadata] = {}
        self._capability_index: Dict[AnalyzerCapability, Set[str]] = {}
        self._language_index: Dict[LanguageSupport, Set[str]] = {}

    def register(self, metadata: AnalyzerMetadata) -> None:
        """Register analyzer with metadata.

        Args:
            metadata: Analyzer metadata
        """
        self._analyzers[metadata.name] = metadata

        # Update capability index
        for capability in metadata.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = set()
            self._capability_index[capability].add(metadata.name)

        # Update language index
        for language in metadata.languages:
            if language not in self._language_index:
                self._language_index[language] = set()
            self._language_index[language].add(metadata.name)

    def find_by_capability(
        self, capability: AnalyzerCapability
    ) -> List[AnalyzerMetadata]:
        """Find analyzers by capability.

        Args:
            capability: Capability to search for

        Returns:
            List of analyzer metadata sorted by priority
        """
        analyzer_names = self._capability_index.get(capability, set())
        analyzers = [self._analyzers[name] for name in analyzer_names]
        return sorted(analyzers, key=lambda a: a.priority)

    def find_by_language(
        self, language: LanguageSupport
    ) -> List[AnalyzerMetadata]:
        """Find analyzers by language support.

        Args:
            language: Language to search for

        Returns:
            List of analyzer metadata sorted by priority
        """
        analyzer_names = self._language_index.get(language, set())
        # Also include language-agnostic analyzers
        analyzer_names |= self._language_index.get(LanguageSupport.AGNOSTIC, set())
        analyzers = [self._analyzers[name] for name in analyzer_names]
        return sorted(analyzers, key=lambda a: a.priority)

    def get_all(self) -> List[AnalyzerMetadata]:
        """Get all registered analyzers.

        Returns:
            List of all analyzer metadata sorted by priority
        """
        return sorted(self._analyzers.values(), key=lambda a: a.priority)

    def get(self, name: str) -> Optional[AnalyzerMetadata]:
        """Get analyzer metadata by name.

        Args:
            name: Analyzer name

        Returns:
            Analyzer metadata or None if not found
        """
        return self._analyzers.get(name)


# Global registry instance
_global_registry = AnalyzerRegistry()


def analyzer_capabilities(
    capabilities: List[AnalyzerCapability],
    languages: List[LanguageSupport],
    priority: int = 100,
    description: str = "",
) -> Callable[[type], type]:
    """Decorator for declaring analyzer capabilities.

    Automatically registers analyzer with global registry.

    Args:
        capabilities: List of analyzer capabilities
        languages: List of supported languages
        priority: Execution priority (lower = higher priority)
        description: Human-readable description

    Returns:
        Class decorator

    Example:
        ```python
        @analyzer_capabilities(
            capabilities=[AnalyzerCapability.AST_ANALYSIS],
            languages=[LanguageSupport.PYTHON],
            priority=10,
            description="Python AST analyzer"
        )
        class PythonAnalyzer:
            pass
        ```
    """
    def decorator(cls: type) -> type:
        """Register class with metadata.

        Args:
            cls: Analyzer class

        Returns:
            Unmodified class
        """
        metadata = AnalyzerMetadata(
            name=cls.__name__,
            capabilities=set(capabilities),
            languages=set(languages),
            priority=priority,
            description=description or cls.__doc__ or "",
            module_path=f"{cls.__module__}.{cls.__name__}",
        )

        _global_registry.register(metadata)

        # Attach metadata to class for introspection
        cls.__analyzer_metadata__ = metadata

        return cls

    return decorator


def get_analyzer_registry() -> AnalyzerRegistry:
    """Get global analyzer registry.

    Returns:
        Global analyzer registry instance
    """
    return _global_registry
