"""IngestKnowledgeExtractor — Phase 144-c.

Converts classified file content into CORTEX-aligned knowledge format.
Handles YAML normalisation and text-to-knowledge heading/list extraction.

Source: GitHub Issue #17 — FB-2026-03-09-074435-001
CORE: CORE-008, CORE-011, CORE-012
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .file_classifier import ClassifiedFile, IngestFileCategory
from .document_reader import DocumentContent, DocumentReader

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ExtractedKnowledge:
    """Normalised knowledge payload ready for cortex-registry/ persistence.

    Attributes:
        source_path: Original file path.
        domain: Target knowledge domain.
        title: Human-readable title.
        content_type: e.g. 'best_practices', 'architecture', 'rca'.
        best_practices: List of extracted practice strings.
        metadata: Arbitrary key-value metadata.
        raw_yaml: YAML dict payload for .yaml files; empty otherwise.
    """

    source_path: Path
    domain: str
    title: str
    content_type: str = "technical_doc"
    best_practices: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_yaml: Dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Extractor
# ─────────────────────────────────────────────────────────────────────────────

class IngestKnowledgeExtractor:
    """Extracts and normalises knowledge from classified documents.

    Supports three source types:
    - YAML files  → direct normalisation preserving structure
    - Text files  → heading/list extraction
    - Office docs → DocumentReader dispatch then text extraction

    Usage::

        extractor = IngestKnowledgeExtractor()
        knowledge = extractor.extract(classified_file)
    """

    def __init__(self) -> None:
        """Initialise extractor with a DocumentReader."""
        self._reader = DocumentReader()

    def extract(self, classified: ClassifiedFile) -> ExtractedKnowledge:
        """Extract knowledge from a classified file.

        Args:
            classified: ClassifiedFile with path, category, and domain_hint.

        Returns:
            ExtractedKnowledge with normalised content and CORTEX alignment metadata.
        """
        domain = classified.domain_hint or "general"

        if classified.category == IngestFileCategory.KNOWLEDGE_YAML:
            knowledge = self._extract_from_yaml(classified.path, domain)
        elif classified.path.suffix.lower() in {".md", ".txt", ".rst"}:
            knowledge = self._extract_from_text(classified.path, domain)
        else:
            knowledge = self._extract_from_office(classified.path, domain)

        # Inject CORTEX alignment metadata
        knowledge.metadata.update({
            "source": str(classified.path),
            "ingested_at": datetime.utcnow().isoformat() + "Z",
            "confidence": classified.confidence,
            "verified": False,
            "ingest_category": classified.category.value,
        })
        return knowledge

    # ── Source-specific handlers ──────────────────────────────────────────

    def _extract_from_yaml(self, path: Path, domain: str) -> ExtractedKnowledge:
        """Normalise a YAML knowledge file."""
        raw: Dict[str, Any] = {}
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            logger.warning("IngestKnowledgeExtractor: YAML parse error for %s: %s", path, exc)
            raw = {}
        title = raw.get("title") or raw.get("name") or path.stem
        practices = raw.get("best_practices") or raw.get("practices") or []
        if isinstance(practices, dict):
            # Flatten nested dicts
            practices = [f"{k}: {v}" for k, v in practices.items()]
        return ExtractedKnowledge(
            source_path=path,
            domain=domain,
            title=str(title),
            content_type="knowledge_yaml",
            best_practices=[str(p) for p in practices],
            raw_yaml=raw,
        )

    def _extract_from_text(self, path: Path, domain: str) -> ExtractedKnowledge:
        """Extract heading and list items from Markdown/plain text."""
        try:
            raw_text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.warning("IngestKnowledgeExtractor: cannot read %s: %s", path, exc)
            raw_text = ""

        title = path.stem
        practices: List[str] = []

        for line in raw_text.splitlines():
            stripped = line.strip()
            # Capture first heading as title
            if re.match(r"^#+\s+", stripped):
                candidate = re.sub(r"^#+\s+", "", stripped).strip()
                if candidate and title == path.stem:
                    title = candidate
            # Extract list items as best practices
            elif re.match(r"^[-*+]\s+", stripped):
                practice = re.sub(r"^[-*+]\s+", "", stripped).strip()
                if practice:
                    practices.append(practice)
            elif re.match(r"^\d+\.\s+", stripped):
                practice = re.sub(r"^\d+\.\s+", "", stripped).strip()
                if practice:
                    practices.append(practice)

        content_type = "rca_doc" if "rca" in path.stem.lower() else "technical_doc"
        return ExtractedKnowledge(
            source_path=path,
            domain=domain,
            title=title,
            content_type=content_type,
            best_practices=practices,
        )

    def _extract_from_office(self, path: Path, domain: str) -> ExtractedKnowledge:
        """Extract knowledge from an Office/PDF document."""
        doc_content: DocumentContent = self._reader.read(path)
        practices: List[str] = []
        for section in doc_content.sections:
            body = section.get("body", "")
            for line in body.splitlines():
                stripped = line.strip()
                if re.match(r"^[-*+]\s+", stripped):
                    practice = re.sub(r"^[-*+]\s+", "", stripped).strip()
                    if practice:
                        practices.append(practice)
        return ExtractedKnowledge(
            source_path=path,
            domain=domain,
            title=doc_content.title or path.stem,
            content_type="technical_doc",
            best_practices=practices,
        )
