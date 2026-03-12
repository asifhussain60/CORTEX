"""Document Ingest Pipeline — Phase 144.

Classifies, reads, extracts, routes, and persists external documents
(Word, Excel, PowerPoint, PDF, YAML, Markdown) into cortex-registry/.

Components:
    IngestFileClassifier  — PII/binary rejection, 9 categories
    DocumentReader        — Office/PDF text extraction (lazy imports)
    IngestKnowledgeExtractor — YAML normalisation + text-to-knowledge
    IngestContentRouter   — 14-domain routing + company segregation
    DocumentIngestOrchestrator — Pipeline coordinator with teardown

Source: GitHub Issue #17 — FB-2026-03-09-074435-001
CORE: CORE-008, CORE-011, CORE-012, CORE-064, CORE-068
"""

from .file_classifier import (
    IngestFileCategory,
    ClassifiedFile,
    IngestClassificationResult,
    IngestFileClassifier,
)
from .document_reader import DocumentContent, DocumentReader
from .knowledge_extractor import ExtractedKnowledge, IngestKnowledgeExtractor
from .content_router import RoutingDecision, IngestContentRouter
from .document_ingest_orchestrator import IngestResult, DocumentIngestOrchestrator

__all__ = [
    "IngestFileCategory",
    "ClassifiedFile",
    "IngestClassificationResult",
    "IngestFileClassifier",
    "DocumentContent",
    "DocumentReader",
    "ExtractedKnowledge",
    "IngestKnowledgeExtractor",
    "RoutingDecision",
    "IngestContentRouter",
    "IngestResult",
    "DocumentIngestOrchestrator",
]
