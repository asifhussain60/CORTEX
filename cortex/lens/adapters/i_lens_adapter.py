"""Unified LENS adapter protocol.

Authority: SWEEP-M4-LENS-STREAMLINE (phase-m4-b)
"""

from pathlib import Path
from typing import Any, Dict, Protocol


class ILensAdapter(Protocol):
    """Canonical protocol for LENS language adapters."""

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a source file and return normalized metadata."""

    def get_context(self, file_path: Path) -> Dict[str, Any]:
        """Return lightweight context payload for orchestrator use."""

    def supports(self, file_path: Path) -> bool:
        """Return True when adapter supports the input file."""
