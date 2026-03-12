"""Tests — Document Ingest Pipeline (Phase 144).

Covers: FileClassifier, DocumentReader, KnowledgeExtractor, ContentRouter,
DocumentIngestOrchestrator — full pipeline classify→extract→route→persist,
teardown, dry-run, graceful degradation without Office libraries.

Source: GitHub Issue #17 — FB-2026-03-09-074435-001
CORE: CORE-008 (TDD)
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from cortex.orchestrators.support.ingest import (
    IngestFileCategory,
    ClassifiedFile,
    IngestClassificationResult,
    IngestFileClassifier,
    DocumentContent,
    DocumentReader,
    ExtractedKnowledge,
    IngestKnowledgeExtractor,
    RoutingDecision,
    IngestContentRouter,
    IngestResult,
    DocumentIngestOrchestrator,
)


# ─────────────────────────────────────────────────────────────────────────────
# IngestFileClassifier
# ─────────────────────────────────────────────────────────────────────────────

class TestFileClassifier:
    def test_file_category_enum_has_9_categories(self):
        assert len(IngestFileCategory) == 9

    def test_classified_file_dataclass(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("title: test\n")
        classifier = IngestFileClassifier()
        cf = classifier.classify_file(f)
        assert isinstance(cf, ClassifiedFile)
        assert cf.path == f

    def test_binary_extension_rejected(self, tmp_path):
        f = tmp_path / "archive.zip"
        f.write_bytes(b"PK")
        classifier = IngestFileClassifier()
        cf = classifier.classify_file(f)
        assert cf.category == IngestFileCategory.REJECTED_BINARY

    def test_pii_filename_rejected(self, tmp_path):
        f = tmp_path / "employee_salary_2024.md"
        f.write_text("# Salary\n")
        classifier = IngestFileClassifier()
        cf = classifier.classify_file(f)
        assert cf.category == IngestFileCategory.REJECTED_PII

    def test_classify_directory_returns_result(self, tmp_path):
        (tmp_path / "doc.md").write_text("# Docs\n")
        (tmp_path / "data.zip").write_bytes(b"PK")
        classifier = IngestFileClassifier()
        result = classifier.classify_directory(tmp_path, recursive=False)
        assert isinstance(result, IngestClassificationResult)
        assert result.total_scanned == 2
        assert len(result.processable) == 1
        assert len(result.rejected) == 1

    def test_domain_hint_extraction_security(self, tmp_path):
        f = tmp_path / "owasp-security-checklist.md"
        f.write_text("# OWASP\n")
        classifier = IngestFileClassifier()
        cf = classifier.classify_file(f)
        assert cf.domain_hint == "security"

    def test_yaml_file_classified_as_knowledge_yaml(self, tmp_path):
        f = tmp_path / "patterns.yaml"
        f.write_text("title: patterns\n")
        classifier = IngestFileClassifier()
        cf = classifier.classify_file(f)
        assert cf.category == IngestFileCategory.KNOWLEDGE_YAML

    def test_docx_classified_as_technical_doc(self, tmp_path):
        f = tmp_path / "design.docx"
        f.write_bytes(b"PK")  # docx is a zip, but we test classification by ext
        # Remove the zip from binary blocklist test — .docx is NOT in _BINARY_EXTENSIONS
        classifier = IngestFileClassifier()
        cf = classifier.classify_file(f)
        assert cf.category == IngestFileCategory.TECHNICAL_DOC


# ─────────────────────────────────────────────────────────────────────────────
# DocumentReader
# ─────────────────────────────────────────────────────────────────────────────

class TestDocumentReader:
    def test_document_content_dataclass(self, tmp_path):
        f = tmp_path / "notes.txt"
        f.write_text("Hello world\n")
        reader = DocumentReader()
        dc = reader.read(f)
        assert isinstance(dc, DocumentContent)
        assert dc.path == f
        assert "Hello world" in dc.text

    def test_read_text_file_extracts_content(self, tmp_path):
        f = tmp_path / "notes.txt"
        f.write_text("# My Title\n\nSome content here.\n")
        reader = DocumentReader()
        dc = reader.read(f)
        assert dc.title == "My Title"
        assert "Some content here" in dc.text

    def test_read_md_headings_become_title(self, tmp_path):
        f = tmp_path / "design.md"
        f.write_text("# Architecture Decision\n\nContent.\n")
        reader = DocumentReader()
        dc = reader.read(f)
        assert dc.title == "Architecture Decision"

    def test_graceful_degradation_without_docx_library(self, tmp_path):
        """DocumentReader.read_docx() must not raise even without python-docx."""
        f = tmp_path / "test.docx"
        f.write_bytes(b"not a real docx")
        reader = DocumentReader()
        dc = reader.read(f)
        # Should have an error message but not raise
        assert isinstance(dc, DocumentContent)
        assert dc.format == "docx"

    def test_unified_read_dispatcher_yaml(self, tmp_path):
        f = tmp_path / "config.yaml"
        f.write_text("key: value\n")
        reader = DocumentReader()
        dc = reader.read(f)
        assert "key: value" in dc.text

    def test_unsupported_extension_returns_error(self, tmp_path):
        f = tmp_path / "file.xyz123"
        f.write_text("data")
        reader = DocumentReader()
        dc = reader.read(f)
        assert dc.error != ""


# ─────────────────────────────────────────────────────────────────────────────
# IngestKnowledgeExtractor
# ─────────────────────────────────────────────────────────────────────────────

class TestKnowledgeExtractor:
    def _make_classified(self, path: Path, category: IngestFileCategory = IngestFileCategory.TECHNICAL_DOC) -> ClassifiedFile:
        return ClassifiedFile(path=path, category=category, reason="test", domain_hint="security", confidence=0.9)

    def test_extracted_knowledge_dataclass(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# Test\n")
        classified = self._make_classified(f)
        extractor = IngestKnowledgeExtractor()
        knowledge = extractor.extract(classified)
        assert isinstance(knowledge, ExtractedKnowledge)

    def test_extract_from_yaml_file(self, tmp_path):
        f = tmp_path / "practices.yaml"
        f.write_text("title: OWASP\nbest_practices:\n  - Use HTTPS\n  - Validate input\n")
        classified = ClassifiedFile(path=f, category=IngestFileCategory.KNOWLEDGE_YAML, reason="yaml", domain_hint="security")
        extractor = IngestKnowledgeExtractor()
        knowledge = extractor.extract(classified)
        assert knowledge.title == "OWASP"
        assert "Use HTTPS" in knowledge.best_practices

    def test_extract_from_text_file(self, tmp_path):
        f = tmp_path / "security.md"
        f.write_text("# Security Practices\n- Use HTTPS\n- Validate input\n")
        classified = self._make_classified(f)
        extractor = IngestKnowledgeExtractor()
        knowledge = extractor.extract(classified)
        assert knowledge.title == "Security Practices"
        assert "Use HTTPS" in knowledge.best_practices

    def test_cortex_alignment_metadata(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# Test\n")
        classified = self._make_classified(f)
        extractor = IngestKnowledgeExtractor()
        knowledge = extractor.extract(classified)
        assert "source" in knowledge.metadata
        assert "ingested_at" in knowledge.metadata
        assert knowledge.metadata["verified"] is False


# ─────────────────────────────────────────────────────────────────────────────
# IngestContentRouter
# ─────────────────────────────────────────────────────────────────────────────

class TestContentRouter:
    def test_routing_decision_dataclass(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# Doc\n")
        classified = ClassifiedFile(path=f, category=IngestFileCategory.TECHNICAL_DOC, reason="test", domain_hint="security")
        router = IngestContentRouter()
        decision = router.route(classified)
        assert isinstance(decision, RoutingDecision)

    def test_14_domain_routing_table(self):
        from cortex.orchestrators.support.ingest.content_router import _DOMAIN_ROUTING
        assert len(_DOMAIN_ROUTING) == 14

    def test_category_fallback_routing(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# Doc\n")
        classified = ClassifiedFile(path=f, category=IngestFileCategory.ARCHITECTURE_DOC, reason="test", domain_hint=None)
        router = IngestContentRouter()
        decision = router.route(classified)
        assert "architecture" in decision.destination_dir

    def test_company_content_segregation(self, tmp_path):
        f = tmp_path / "business-rules.yaml"
        f.write_text("title: rules\n")
        classified = ClassifiedFile(path=f, category=IngestFileCategory.KNOWLEDGE_YAML, reason="test", domain_hint="business-rules")
        router = IngestContentRouter()
        decision = router.route(classified)
        assert decision.is_company_content is True
        assert "company" in decision.destination_dir

    def test_route_returns_decision(self, tmp_path):
        f = tmp_path / "security-checklist.yaml"
        f.write_text("title: security\n")
        classified = ClassifiedFile(path=f, category=IngestFileCategory.KNOWLEDGE_YAML, reason="test", domain_hint="security")
        router = IngestContentRouter()
        decision = router.route(classified)
        assert decision.output_filename.endswith(".yaml")


# ─────────────────────────────────────────────────────────────────────────────
# DocumentIngestOrchestrator
# ─────────────────────────────────────────────────────────────────────────────

class TestDocumentIngestOrchestrator:
    def test_inherits_required_mixins(self):
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        orch = DocumentIngestOrchestrator()
        assert isinstance(orch, OrchestratorProtocolMixin)
        assert isinstance(orch, WorkflowEnforcementMixin)

    def test_phase90_gateway_exempt(self):
        assert DocumentIngestOrchestrator.PHASE90_GATEWAY_EXEMPT is True

    def test_ingest_directory_classify_extract_route_persist(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        (source / "security.md").write_text("# Security\n- Use HTTPS\n- Validate input\n")
        registry = tmp_path / "cortex-registry"
        registry.mkdir()
        orch = DocumentIngestOrchestrator(registry_root=registry)
        result = orch.ingest_directory(source)
        assert result.ingested >= 1
        assert result.errors == 0

    def test_dry_run_mode(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        (source / "design.md").write_text("# Design\n- Pattern A\n")
        registry = tmp_path / "cortex-registry"
        registry.mkdir()
        orch = DocumentIngestOrchestrator(registry_root=registry)
        result = orch.ingest_directory(source, dry_run=True)
        # Nothing written in dry run
        assert result.dry_run is True
        assert len(result.created_paths) == 0

    def test_teardown_removes_created_files(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        (source / "practices.md").write_text("# Practices\n- Do TDD\n")
        registry = tmp_path / "cortex-registry"
        registry.mkdir()
        orch = DocumentIngestOrchestrator(registry_root=registry)
        result = orch.ingest_directory(source)
        created = list(result.created_paths)
        assert all(p.exists() for p in created), "Files should exist before teardown"
        orch.teardown(result)
        assert all(not p.exists() for p in created), "Files should be removed after teardown"

    def test_ac_marker_emission(self, tmp_path, caplog):
        import logging
        source = tmp_path / "source"
        source.mkdir()
        (source / "doc.md").write_text("# Doc\n")
        registry = tmp_path / "cortex-registry"
        registry.mkdir()
        orch = DocumentIngestOrchestrator(registry_root=registry)
        with caplog.at_level(logging.INFO):
            orch.ingest_directory(source)
        assert any("AC_START" in r.message for r in caplog.records)
        assert any("AC_COMPLETE" in r.message for r in caplog.records)

    def test_auto_detect_registry_root(self):
        orch = DocumentIngestOrchestrator()
        assert orch._registry_root is not None
        assert isinstance(orch._registry_root, Path)
