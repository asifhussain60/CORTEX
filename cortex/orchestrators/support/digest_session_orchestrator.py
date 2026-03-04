"""
DigestSessionOrchestrator — processes a single markdown/chat session file.

Classifies content, extracts enhancements, and returns a structured result.
CORTEX canonical support orchestrator (CORE-035).

OPJ Integration (Phase 52): consults OPJ before processing, records outcome after.
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.intelligence.learning.opj_mixin import OPJMixin
from cortex.core.result import Ok
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin  # Phase 62-B
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94e


@dataclass
class DigestResult:  # CORE-035-scoped — domain-specific variant
    """Result of digesting a single session file."""

    success: bool = False
    is_chat_file: bool = False
    confidence_score: float = 0.0
    enhancements_found: int = 0
    error_message: Optional[str] = None
    file_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the digest result to a serializable dictionary."""
        return {
            "success": self.success,
            "is_chat_file": self.is_chat_file,
            "confidence_score": self.confidence_score,
            "enhancements_found": self.enhancements_found,
            "error_message": self.error_message,
            "file_path": self.file_path,
        }


class DigestSessionOrchestrator(OPJMixin, OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Orchestrates ingestion of a single markdown/chat session file."""

    # Phase 94e — advisory: digest processing, invoked by audit pipeline.
    # Gateway routing deferred until MasterOrchestrator milestone.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def digest_session(self, file_path: str) -> DigestResult:
        """
        Analyse *file_path* and return a :class:`DigestResult`.

        Args:
            file_path: Absolute or relative path to the markdown file.

        Returns:
            :class:`DigestResult` with classification and enhancement counts.
        """
        path = Path(file_path)
        import time as _time_mod
        _ac_id = f"AC-DSESSION-{int(_time_mod.time() * 1000)}"
        # AC_START: {_ac_id}
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="digest_session")

        if not path.exists():
            # AC_COMPLETE: {_ac_id} ❌ file not found
            return DigestResult(
                success=False,
                file_path=file_path,
                error_message=f"File not found: {file_path}",
            )

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            self._opj_record_failure(
                operation="digest_session",
                error=str(exc),
                attempted_fix="read with errors='replace' — failed",
                root_cause="File unreadable",
            )
            return DigestResult(
                success=False,
                file_path=file_path,
                error_message=str(exc),
            )

        is_chat = self._classify_as_chat(content)
        confidence = self._compute_confidence(content, is_chat)
        enhancements = self._count_enhancements(content)

        result = DigestResult(
            success=True,
            is_chat_file=is_chat,
            confidence_score=confidence,
            enhancements_found=enhancements,
            file_path=file_path,
        )
        self._opj_record_success(
            operation="digest_session",
            context={"file": file_path, "is_chat": is_chat},
            resolution=f"classified {'chat' if is_chat else 'doc'} confidence={confidence:.2f} enhancements={enhancements}",
            confidence=min(confidence / 10.0, 1.0),
        )
        # AC_COMPLETE: {_ac_id} ✅
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _classify_as_chat(self, content: str) -> bool:
        """Heuristic: file is a chat session if it contains known markers."""
        markers = ["## User", "## Assistant", "**User:**", "**Assistant:**", "# Chat"]
        return any(m in content for m in markers)

    def _compute_confidence(self, content: str, is_chat: bool) -> float:
        """Return a 0–10 confidence score based on content quality."""
        if not content.strip():
            return 0.0
        score = 5.0
        if is_chat:
            score += 2.0
        if len(content) > 500:
            score += 1.0
        if "## Summary" in content or "## Conclusion" in content:
            score += 1.0
        return min(score, 10.0)

    def _count_enhancements(self, content: str) -> int:
        """Count actionable enhancement markers in content."""
        markers = ["TODO:", "FIXME:", "ENHANCE:", "ENH-", "AC-"]
        return sum(content.count(m) for m in markers)


    # ------------------------------------------------------------------
    # Orchestration Protocol (IOrchestrator)
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return the canonical orchestrator name."""
        return "DigestSessionOrchestrator"

    def get_version(self) -> str:
        """Return the orchestrator version string."""
        return "1.0.0"

    def initialize(self) -> Any:
        """Initialise the orchestrator (setup already done in ``__init__``)."""
        return Ok("DigestSessionOrchestrator initialized")

    def health_check(self) -> Dict[str, Any]:
        """Return health status for wiring-contract validation."""
        return {
            "status": "healthy",
            "orchestrator": "DigestSessionOrchestrator",
        }

