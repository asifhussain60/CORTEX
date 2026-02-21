"""
DigestSessionOrchestrator — processes a single markdown/chat session file.

Classifies content, extracts enhancements, and returns a structured result.
CORTEX canonical support orchestrator (CORE-035).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class DigestResult:
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


class DigestSessionOrchestrator:
    """Orchestrates ingestion of a single markdown/chat session file."""

    def digest_session(self, file_path: str) -> DigestResult:
        """
        Analyse *file_path* and return a :class:`DigestResult`.

        Args:
            file_path: Absolute or relative path to the markdown file.

        Returns:
            :class:`DigestResult` with classification and enhancement counts.
        """
        path = Path(file_path)

        if not path.exists():
            return DigestResult(
                success=False,
                file_path=file_path,
                error_message=f"File not found: {file_path}",
            )

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return DigestResult(
                success=False,
                file_path=file_path,
                error_message=str(exc),
            )

        is_chat = self._classify_as_chat(content)
        confidence = self._compute_confidence(content, is_chat)
        enhancements = self._count_enhancements(content)

        return DigestResult(
            success=True,
            is_chat_file=is_chat,
            confidence_score=confidence,
            enhancements_found=enhancements,
            file_path=file_path,
        )

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
    # Health Check (IOrchestrator protocol)
    # ------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """Return health status for wiring-contract validation."""
        return {
            "status": "healthy",
            "orchestrator": "DigestSessionOrchestrator",
        }
