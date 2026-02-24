"""Domain adapters — pluggable extensions for specific use cases.

Base Protocol:
    DomainAdapter:      Interface for domain-specific rules and enrichment
    MorphRule:          Text transformation rule dataclass
    EnrichmentSource:   External API configuration dataclass

Concrete Adapters:
    MediaAdapter:       Studios, artists, external metadata (IAFD, TMDB)
    CodeAdapter:        Packages, modules, imports, dependencies (TODO)
    DocumentAdapter:    Authors, citations, references (TODO)

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
"""

from cortex.toolkit.adapters.domain_adapter import (
    DomainAdapter,
    MorphRule,
    EnrichmentSource,
)
from cortex.toolkit.adapters.media_adapter import MediaAdapter

__all__ = [
    "DomainAdapter",
    "MorphRule",
    "EnrichmentSource",
    "MediaAdapter",
]
