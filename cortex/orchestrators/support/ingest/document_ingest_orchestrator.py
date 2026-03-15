"""DocumentIngestOrchestrator — Phase 144-e.

Pipeline coordinator for document ingestion. Runs the full
classify → extract → route → persist sequence per file,
with teardown support and OPJ success recording.

Source: GitHub Issue #17 — FB-2026-03-09-074435-001
CORE: CORE-008, CORE-011, CORE-012, CORE-064, CORE-068
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from cortex.core.file_factory import get_file_factory
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin

try:
    from cortex.intelligence.learning.opj_mixin import OPJMixin
    _OPJBase = OPJMixin
except ImportError:  # graceful degradation when OPJ not wired
    class _OPJBase:  # type: ignore[no-redef]
        """No-op OPJ placeholder."""

from .file_classifier import ClassifiedFile, IngestClassificationResult, IngestFileClassifier
from .document_reader import DocumentReader
from .knowledge_extractor import ExtractedKnowledge, IngestKnowledgeExtractor
from .content_router import RoutingDecision, IngestContentRouter

logger = logging.getLogger(__name__)

# PHASE90_GATEWAY_EXEMPT — DocumentIngestOrchestrator processes external documents,
# not CORTEX source code, so it is exempt from the Phase-90 code-touching gate.
PHASE90_GATEWAY_EXEMPT: bool = True


# ─────────────────────────────────────────────────────────────────────────────
# Data class
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class IngestResult:
    """Summary of a completed ingestion run.

    Attributes:
        ingested: Files successfully persisted.
        skipped: Files skipped (rejected by classifier).
        errors: Files that caused errors during extraction/persist.
        dry_run: Whether this was a dry-run pass.
        created_paths: Absolute paths of files written (for teardown).
    """

    ingested: int = 0
    skipped: int = 0
    errors: int = 0
    dry_run: bool = False
    created_paths: List[Path] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class DocumentIngestOrchestrator(_OPJBase, OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Coordinates the full document ingestion pipeline.

    Pipeline per file: classify → extract → route → persist.
    Supports dry-run mode and full teardown.

    Attributes:
        PHASE90_GATEWAY_EXEMPT: True — external document processing is exempt
            from the Phase-90 code-touching gate.

    Usage::

        orch = DocumentIngestOrchestrator()
        result = orch.ingest_directory(Path("/incoming/docs"))
        print(f"Ingested: {result.ingested}, Skipped: {result.skipped}")
    """

    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self, registry_root: Optional[Path] = None) -> None:
        """Initialise orchestrator with an optional registry root override.

        Args:
            registry_root: Root of cortex-registry/. Auto-detected when None.
        """
        self._registry_root = registry_root or self._auto_detect_registry_root()
        self._classifier = IngestFileClassifier()
        self._reader = DocumentReader()
        self._extractor = IngestKnowledgeExtractor()
        self._router = IngestContentRouter()

    def ingest_directory(
        self,
        source_dir: Path,
        recursive: bool = True,
        dry_run: bool = False,
    ) -> IngestResult:
        """Ingest all processable documents from a directory.

        Runs classify → extract → route → persist for each file.
        Records OPJ success on completion.

        Args:
            source_dir: Directory containing documents to ingest.
            recursive: Descend into subdirectories when True.
            dry_run: Plan operations without writing files.

        Returns:
            IngestResult with counts and created path list.
        """
        _ac_id = f"AC-INGEST-{int(time.time() * 1000)}"
        logger.info("AC_START: %s — ingest_directory(%s)", _ac_id, source_dir)
        self._activate_cross_cutting_hooks(operation="ingest_directory")

        result = IngestResult(dry_run=dry_run)

        classification: IngestClassificationResult = self._classifier.classify_directory(
            source_dir, recursive=recursive
        )
        result.skipped += len(classification.rejected)

        for classified in classification.processable:
            try:
                knowledge = self._extractor.extract(classified)
                decision = self._router.route(classified, knowledge)
                if not dry_run:
                    created = self._persist(knowledge, decision)
                    if created:
                        result.created_paths.append(created)
                result.ingested += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "DocumentIngestOrchestrator: failed to ingest %s: %s",
                    classified.path,
                    exc,
                )
                result.errors += 1

        # OPJ success recording (best-effort)
        self._record_opj_success(result)

        logger.info(
            "AC_COMPLETE: %s ✅ ingested=%d skipped=%d errors=%d",
            _ac_id, result.ingested, result.skipped, result.errors,
        )
        return result

    def teardown(self, result: IngestResult) -> None:
        """Remove all files created during a previous ingest run.

        Deletes files in reverse creation order, then removes any
        empty directories that were created as a side-effect.

        Args:
            result: IngestResult returned by a previous ingest_directory() call.
        """
        for path in reversed(result.created_paths):
            try:
                if path.exists():
                    path.unlink()
                    logger.debug("DocumentIngestOrchestrator.teardown: removed %s", path)
            except OSError as exc:
                logger.warning("teardown: failed to remove %s: %s", path, exc)
            # Remove empty parent directories
            parent = path.parent
            try:
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
            except OSError:
                pass

    # ── Helpers ───────────────────────────────────────────────────────────

    def _persist(self, knowledge: ExtractedKnowledge, decision: RoutingDecision) -> Optional[Path]:
        """Write extracted knowledge to the registry.

        Args:
            knowledge: Extracted knowledge payload.
            decision: Routing decision with destination directory and filename.

        Returns:
            Path of the written file, or None if write failed.
        """
        dest_dir = self._registry_root / decision.destination_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / decision.output_filename

        try:
            if decision.output_format == "yaml":
                payload: Dict = {
                    "title": knowledge.title,
                    "domain": knowledge.domain,
                    "content_type": knowledge.content_type,
                    "best_practices": knowledge.best_practices,
                    "metadata": knowledge.metadata,
                }
                if knowledge.raw_yaml:
                    payload.update(knowledge.raw_yaml)
                dest_file.write_text(yaml.dump(payload, allow_unicode=True), encoding="utf-8")
            else:
                lines = [f"# {knowledge.title}\n"]
                if knowledge.best_practices:
                    lines.append("\n## Best Practices\n")
                    for practice in knowledge.best_practices:
                        lines.append(f"- {practice}\n")
                lines.append(f"\n---\n*Source: {knowledge.source_path}*\n")
                dest_file.write_text("".join(lines), encoding="utf-8")
            return dest_file
        except OSError as exc:
            logger.warning("DocumentIngestOrchestrator._persist: %s", exc)
            return None

    def _auto_detect_registry_root(self) -> Path:
        """Auto-detect cortex-registry/ root from module file location."""
        here = Path(__file__).resolve()
        # Walk up to workspace root (contains cortex-registry/)
        for parent in here.parents:
            candidate = parent / "cortex-registry"
            if candidate.is_dir():
                return candidate
        return Path.cwd() / "cortex-registry"

    def _record_opj_success(self, result: IngestResult) -> None:
        """Record OPJ success event (best-effort, no-op if OPJ unavailable)."""
        try:
            record = getattr(self, "record_success", None)
            if record is not None:
                record(
                    operation="document_ingest",
                    context={
                        "ingested": result.ingested,
                        "skipped": result.skipped,
                        "errors": result.errors,
                    },
                )
        except Exception:  # noqa: BLE001
            pass  # OPJ is best-effort
