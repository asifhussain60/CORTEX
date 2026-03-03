"""
OPJReader — queries the Operational Pattern Journal for prior success/failure patterns.

Reads YAML from:
  cortex-registry/patterns/success/{orchestrator_snake}.yaml
  cortex-registry/patterns/failure/{orchestrator_snake}.yaml

AC-ID: AC-OPJ-PHASE52-READER
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

_WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_REGISTRY = _WORKSPACE_ROOT / "cortex-registry"


def _snake(name: str) -> str:
    """Convert CamelCase or arbitrary string to snake_case (handles consecutive caps e.g. TDDOrchestrator)."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


class OPJReader:
    """
    Queries the Operational Pattern Journal for prior operation patterns.

    Usage::

        reader = OPJReader()
        failures = reader.query_failures("DigestSessionOrchestrator", "process")
        # Returns list of dicts sorted by confidence desc

    Used by OPJMixin._opj_consult() and cortex_query_opj MCP tool.
    """

    def __init__(self, registry_root: Optional[Path] = None) -> None:
        """
        Initialise OPJReader.

        Args:
            registry_root: Path to the cortex-registry/ root (or any root from which
                           patterns/ is resolved). Defaults to canonical location.
        """
        _base = Path(registry_root) if registry_root is not None else _DEFAULT_REGISTRY
        self._root = _base / "patterns"

    # ── Public API ──────────────────────────────────────────────────────────

    def query_patterns(
        self,
        orchestrator: Optional[str],
        operation: Optional[str],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Query all patterns (success + failure) for the given orchestrator/operation.

        Args:
            orchestrator: Orchestrator class name. Pass None to query all orchestrators.
            operation: Operation name. Pass None to query all operations.
            limit: Maximum number of results (default 5). Sorted by confidence desc.

        Returns:
            List of entry dicts, sorted by confidence descending.
        """
        results = self._load_all(orchestrator=orchestrator, operation=operation, outcome=None)
        return self._top_n(results, limit)

    def query_failures(
        self,
        orchestrator: Optional[str],
        operation: Optional[str],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Query failure patterns for the given orchestrator/operation.

        Args:
            orchestrator: Orchestrator class name. None = all.
            operation: Operation name. None = all.
            limit: Maximum number of results.

        Returns:
            List of failure entry dicts, sorted by confidence descending.
        """
        results = self._load_all(orchestrator=orchestrator, operation=operation, outcome="failure")
        return self._top_n(results, limit)

    def query_successes(
        self,
        orchestrator: Optional[str],
        operation: Optional[str],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Query success patterns for the given orchestrator/operation.

        Args:
            orchestrator: Orchestrator class name. None = all.
            operation: Operation name. None = all.
            limit: Maximum number of results.

        Returns:
            List of success entry dicts, sorted by confidence descending.
        """
        results = self._load_all(orchestrator=orchestrator, operation=operation, outcome="success")
        return self._top_n(results, limit)

    # ── Internal ────────────────────────────────────────────────────────────

    def _load_all(
        self,
        orchestrator: Optional[str],
        operation: Optional[str],
        outcome: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Load and filter all matching entries from the shard files."""
        outcomes_to_scan = [outcome] if outcome else ["success", "failure"]
        results: List[Dict[str, Any]] = []

        for out in outcomes_to_scan:
            shard_dir = self._root / out
            if not shard_dir.exists():
                continue

            if orchestrator:
                shard_files = [shard_dir / f"{_snake(orchestrator)}.yaml"]
            else:
                shard_files = list(shard_dir.glob("*.yaml"))

            for shard in shard_files:
                if not shard.exists():
                    continue
                try:
                    data = yaml.safe_load(shard.read_text()) or {}
                    entries = data.get("entries", [])
                    for entry in entries:
                        if operation and entry.get("operation") != operation:
                            continue
                        results.append(entry)
                except Exception as exc:
                    logger.warning("OPJReader: failed to read %s — %s", shard, exc)

        return results

    @staticmethod
    def _top_n(entries: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Sort by confidence descending and cap to limit."""
        sorted_entries = sorted(
            entries,
            key=lambda e: float(e.get("confidence", 0.0)),
            reverse=True,
        )
        return sorted_entries[:limit]
