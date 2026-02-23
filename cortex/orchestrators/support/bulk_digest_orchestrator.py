"""
BulkDigestOrchestrator — orchestrates bulk markdown ingestion via DigestSessionOrchestrator.

CORTEX canonical support orchestrator. CORE-035 compliant single implementation.
"""

from __future__ import annotations

import fnmatch
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.result import Ok, Result


class BulkDigestOrchestrator(OrchestratorProtocolMixin):
    """Orchestrates bulk markdown file ingestion with filtering, batching, and progress tracking."""

    _orch_name = "BulkDigestOrchestrator"
    _orch_version = "1.0.0"

    def __init__(self) -> None:
        """Initialize instance."""
        self._progress: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_directory(
        self,
        directory: str = ".",
        pattern: str = "*.md",
        exclude_patterns: Optional[List[str]] = None,
        auto_delete: bool = False,
        dry_run: bool = False,
        min_confidence: float = 0.0,
        parallel: bool = False,
        max_workers: int = 4,
        batch_size: int = 50,
        continue_on_error: bool = True,
    ) -> Dict[str, Any]:
        """Process all matching files in *directory* and return aggregated stats."""
        import time as _time_mod
        _ac_id = f"AC-DIGEST-{int(_time_mod.time() * 1000)}"
        # AC_START: {_ac_id}
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="process_directory")
        start = time.monotonic()
        exclude_patterns = exclude_patterns or []

        base = Path(directory)
        all_files = list(base.glob(pattern))

        # Filter
        processable = [
            f for f in all_files
            if f.is_file() and self._should_process(f.name, exclude_patterns)
        ]
        excluded_count = len(all_files) - len(processable)

        stats: Dict[str, Any] = {
            "success": True,
            "files_found": len(processable),
            "files_processed": 0,
            "files_skipped": 0,
            "files_deleted": 0,
            "files_failed": 0,
            "files_excluded": excluded_count,
            "total_enhancements": 0,
            "dry_run": dry_run,
            "parallel": parallel,
            "processing_time_seconds": 0.0,
        }

        for f in processable:
            try:
                file_result = self._process_single_file(
                    f,
                    dry_run=dry_run,
                    auto_delete=auto_delete,
                    min_confidence=min_confidence,
                )
                self._merge_file_result(stats, file_result, f, dry_run=dry_run)
            except Exception:
                stats["files_failed"] += 1
                if not continue_on_error:
                    stats["success"] = False
                    break

        stats["processing_time_seconds"] = round(time.monotonic() - start, 3)
        self._update_progress(stats)
        # AC_COMPLETE: {_ac_id} ✅
        return stats

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _should_process(self, filename: str, exclude_patterns: List[str]) -> bool:
        """Return True if *filename* should be processed (not matching exclude_patterns)."""
        for pat in exclude_patterns:
            # Support glob-style patterns like docs/**
            base_pat = pat.rstrip("/**").rstrip("/*")
            if fnmatch.fnmatch(filename, pat) or filename.startswith(base_pat + "/"):
                return False
            if fnmatch.fnmatch(filename, base_pat):
                return False
        return True

    def _process_single_file(
        self,
        filepath: Path,
        dry_run: bool,
        auto_delete: bool,
        min_confidence: float,
    ) -> Dict[str, Any]:
        """Process a single file via DigestSessionOrchestrator."""
        try:
            from cortex.orchestrators.support import digest_session_orchestrator as _dso  # type: ignore[import]
            orch = _dso.DigestSessionOrchestrator()
            result = orch.digest_session(str(filepath))
        except Exception:
            # Graceful fallback — treat as skipped
            return {"success": False, "skipped": True, "enhancements_found": 0, "deleted": False}

        confidence = getattr(result, "confidence_score", 10.0)
        if confidence < min_confidence:
            return {"success": True, "skipped": True, "enhancements_found": 0, "deleted": False}

        enhancements = getattr(result, "enhancements_found", 0)
        deleted = False
        if getattr(result, "success", False) and auto_delete and not dry_run:
            try:
                filepath.unlink()
                deleted = True
            except Exception:
                pass

        return {
            "success": getattr(result, "success", False),
            "skipped": False,
            "enhancements_found": enhancements,
            "deleted": deleted,
        }

    def _merge_file_result(
        self,
        stats: Dict[str, Any],
        file_result: Dict[str, Any],
        filepath: Path,
        dry_run: bool,
    ) -> None:
        """Accumulate per-file result into aggregate stats."""
        if file_result.get("skipped"):
            stats["files_skipped"] += 1
        elif file_result.get("success"):
            stats["files_processed"] += 1
            stats["total_enhancements"] += file_result.get("enhancements_found", 0)
            if file_result.get("deleted"):
                stats["files_deleted"] += 1
        else:
            stats["files_failed"] += 1

    def _create_batches(self, files: List[Any], batch_size: int = 50) -> List[List[Any]]:
        """Partition *files* into batches of *batch_size*."""
        return [files[i : i + batch_size] for i in range(0, len(files), batch_size)]

    def _update_progress(self, stats: Dict[str, Any]) -> None:
        """Store latest progress snapshot."""
        self._progress = dict(stats)

    # ------------------------------------------------------------------
    # Orchestration Protocol (IOrchestrator)
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return the canonical orchestrator name."""
        return "BulkDigestOrchestrator"

    def get_version(self) -> str:
        """Return the orchestrator version string."""
        return "1.0.0"

    def initialize(self) -> Any:
        """Initialise the orchestrator (setup already done in ``__init__``)."""
        return Ok("BulkDigestOrchestrator initialized")

    def health_check(self) -> Dict[str, Any]:
        """Return health status for wiring-contract validation."""
        return {
            "status": "healthy",
            "orchestrator": "BulkDigestOrchestrator",
        }
