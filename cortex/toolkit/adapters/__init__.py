"""Domain adapters — pluggable extensions for specific use cases.

Base Protocol:
    DomainAdapter:      Interface for domain-specific rules and enrichment

Concrete Adapters:
    MediaAdapter:       Studios, artists, external metadata (IAFD, TMDB)
    CodeAdapter:        Packages, modules, imports, dependencies
    DocumentAdapter:    Authors, citations, references

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
"""

__all__ = [
    "DomainAdapter",
    "MediaAdapter",
    "CodeAdapter",
    "DocumentAdapter",
]
