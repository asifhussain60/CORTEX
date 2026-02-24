"""Metadata enrichment — external APIs, local extraction, confidence scoring.

Components:
    ExternalEnricher:   Generic API accessor with rate limiting, caching, retry
    LocalEnricher:      File metadata extraction (ID3, EXIF, PDF, Office)
    TagWriter:          Cross-format metadata writing (MP4, MKV, PDF, etc.)
    ConfidenceScorer:   Match confidence calculation (0.0-1.0)

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
"""

__all__ = [
    "ExternalEnricher",
    "LocalEnricher",
    "TagWriter",
    "ConfidenceScorer",
]
