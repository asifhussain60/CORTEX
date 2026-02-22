"""
OPJWriter — writes success and failure patterns to the Operational Pattern Journal.

Writes YAML to:
  cortex-registry/integration/patterns/success/{orchestrator_snake}.yaml
  cortex-registry/integration/patterns/failure/{orchestrator_snake}.yaml
  cortex-registry/integration/patterns/_registry.yaml  (index)

AC-ID: AC-OPJ-PHASE52-WRITER
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

_WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_REGISTRY = _WORKSPACE_ROOT / "cortex-registry"

_SIMILARITY_THRESHOLD = 0.3  # reuse PatternLibrary dedup threshold
_DEDUP_THRESHOLD = 0.95       # near-exact match required for deduplication


def _snake(name: str) -> str:
    """Convert CamelCase or arbitrary string to snake_case (handles consecutive caps e.g. TDDOrchestrator)."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _entry_id(orchestrator: str) -> str:
    """Generate a unique OPJ entry ID (microsecond precision for uniqueness in rapid calls)."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    slug = _snake(orchestrator).upper()[:20]
    return f"OPJ-{slug}-{ts}"


def _similarity(a: str, b: str) -> float:
    """Rough character-overlap similarity (0.0–1.0) between two strings."""
    if not a or not b:
        return 0.0
    set_a, set_b = set(a.lower()), set(b.lower())
    return len(set_a & set_b) / max(len(set_a | set_b), 1)


class OPJEntry:
    """Lightweight entry dataclass used by OPJWriter (internal use)."""

    def __init__(
        self,
        pattern_id: str,
        orchestrator: str,
        operation: str,
        outcome: "OPJOutcome",
        confidence: float,
        context: Dict[str, Any],
        resolution: Optional[str] = None,
        error: Optional[str] = None,
        attempted_fix: Optional[str] = None,
        root_cause: Optional[str] = None,
        avoid_in_future: Optional[str] = None,
        recorded_at: Optional[str] = None,
    ) -> None:
        self.pattern_id = pattern_id
        self.orchestrator = orchestrator
        self.operation = operation
        self.outcome = outcome
        self.confidence = confidence
        self.context = context
        self.resolution = resolution
        self.error = error
        self.attempted_fix = attempted_fix
        self.root_cause = root_cause
        self.avoid_in_future = avoid_in_future
        self.recorded_at = recorded_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a YAML-safe dict."""
        ctx_hash = hashlib.md5(str(sorted(self.context.items())).encode()).hexdigest()[:8]
        d: Dict[str, Any] = {
            "pattern_id": self.pattern_id,
            "orchestrator": self.orchestrator,
            "operation": self.operation,
            "outcome": self.outcome.value if hasattr(self.outcome, "value") else str(self.outcome),
            "confidence": self.confidence,
            "recorded_at": self.recorded_at,
            "context": self.context,
            "_context_hash": ctx_hash,
            "occurrence_count": 1,
        }
        if self.resolution is not None:
            d["resolution"] = self.resolution
        if self.error is not None:
            d["error"] = self.error
        if self.attempted_fix is not None:
            d["attempted_fix"] = self.attempted_fix
        if self.root_cause is not None:
            d["root_cause"] = self.root_cause
        if self.avoid_in_future is not None:
            d["avoid_in_future"] = self.avoid_in_future
        return d


class OPJOutcome:
    """Outcome constants (mirrors opj_models.OPJOutcome for zero import coupling)."""

    SUCCESS = type("_O", (), {"value": "success"})()
    FAILURE = type("_O", (), {"value": "failure"})()


class OPJWriter:
    """
    Writes success and failure patterns to the Operational Pattern Journal.

    Each call to record_success() / record_failure() appends an entry to:
      {registry_root}/success/{orchestrator_snake}.yaml
      {registry_root}/failure/{orchestrator_snake}.yaml

    Identical entries (same orchestrator + operation + resolution/error) are
    deduplicated and their occurrence_count is incremented instead of duplicated.

    The _registry.yaml index is updated after every write.
    """

    def __init__(self, registry_root: Optional[Path] = None) -> None:
        """
        Initialise OPJWriter.

        Args:
            registry_root: Path to the cortex-registry/ root (or any workspace root
                           from which integration/patterns/ is resolved). Defaults to
                           the canonical workspace cortex-registry/.
        """
        _base = Path(registry_root) if registry_root is not None else _DEFAULT_REGISTRY
        self._root = _base / "integration" / "patterns"
        self._success_dir = self._root / "success"
        self._failure_dir = self._root / "failure"
        self._registry_file = self._root / "_registry.yaml"
        self._success_dir.mkdir(parents=True, exist_ok=True)
        self._failure_dir.mkdir(parents=True, exist_ok=True)

    # ── Public API ──────────────────────────────────────────────────────────

    def record_success(
        self,
        orchestrator: str,
        operation: str,
        context: Dict[str, Any],
        resolution: str,
        confidence: float,
    ) -> None:
        """
        Record a successful operation pattern.

        Args:
            orchestrator: Class name of the orchestrator (e.g. 'DigestSessionOrchestrator').
            operation: Operation performed (e.g. 'process_markdown').
            context: Key input values that contributed to success.
            resolution: Human-readable description of what made it succeed.
            confidence: Confidence score 0.0–1.0.
        """
        entry = OPJEntry(
            pattern_id=_entry_id(orchestrator),
            orchestrator=orchestrator,
            operation=operation,
            outcome=OPJOutcome.SUCCESS,
            confidence=confidence,
            context=context,
            resolution=resolution,
        )
        self._write_entry(entry, self._success_dir)

    def record_failure(
        self,
        orchestrator: str,
        operation: str,
        error: str,
        attempted_fix: str,
        confidence: float,
        root_cause: Optional[str] = None,
        avoid_in_future: Optional[str] = None,
    ) -> None:
        """
        Record a failed operation pattern.

        Args:
            orchestrator: Class name of the orchestrator.
            operation: Operation that failed.
            error: What went wrong.
            attempted_fix: What was tried.
            confidence: Confidence in the failure pattern 0.0–1.0.
            root_cause: Why it failed (optional).
            avoid_in_future: Actionable avoidance rule (optional).
        """
        entry = OPJEntry(
            pattern_id=_entry_id(orchestrator),
            orchestrator=orchestrator,
            operation=operation,
            outcome=OPJOutcome.FAILURE,
            confidence=confidence,
            context={},
            error=error,
            attempted_fix=attempted_fix,
            root_cause=root_cause,
            avoid_in_future=avoid_in_future,
        )
        self._write_entry(entry, self._failure_dir)

    # ── Internal ────────────────────────────────────────────────────────────

    def _write_entry(self, entry: OPJEntry, shard_dir: Path) -> None:
        """Write an entry to the appropriate shard file, deduplicating if needed."""
        snake_name = _snake(entry.orchestrator)
        shard = shard_dir / f"{snake_name}.yaml"

        existing_data: Dict[str, Any] = {"entries": []}
        if shard.exists():
            loaded = yaml.safe_load(shard.read_text()) or {}
            existing_data = loaded if isinstance(loaded, dict) else {"entries": []}

        entries: list = existing_data.get("entries", [])

        # Deduplication: find similar existing entry
        dup_idx = self._find_duplicate(entry, entries)
        if dup_idx is not None:
            entries[dup_idx]["occurrence_count"] = entries[dup_idx].get("occurrence_count", 1) + 1
            entries[dup_idx]["confidence"] = max(
                entries[dup_idx].get("confidence", 0.0), entry.confidence
            )
        else:
            entries.append(entry.to_dict())

        existing_data["entries"] = entries
        shard.write_text(yaml.safe_dump(existing_data, sort_keys=False, allow_unicode=True))
        self._update_registry(entry, shard)

    def _find_duplicate(self, entry: OPJEntry, existing: list) -> Optional[int]:
        """Return index of a duplicate entry if one exists, else None.

        Deduplication requires:
        - Same orchestrator + operation
        - Near-identical resolution/error text (similarity >= 0.95)
        - Same context hash (prevents entries with different inputs from deduping)
        """
        compare_field = entry.resolution or entry.error or ""
        context_hash = hashlib.md5(str(sorted(entry.context.items())).encode()).hexdigest()[:8]
        for i, e in enumerate(existing):
            if e.get("orchestrator") != entry.orchestrator:
                continue
            if e.get("operation") != entry.operation:
                continue
            existing_text = e.get("resolution") or e.get("error") or ""
            existing_ctx_hash = e.get("_context_hash", "")
            if existing_ctx_hash and existing_ctx_hash != context_hash:
                continue
            if _similarity(compare_field, existing_text) >= _DEDUP_THRESHOLD:
                return i
        return None

    def _update_registry(self, entry: OPJEntry, shard: Path) -> None:
        """Update _registry.yaml with the new entry reference."""
        registry_data: Dict[str, Any] = {
            "schema_version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "entries": [],
        }
        if self._registry_file.exists():
            loaded = yaml.safe_load(self._registry_file.read_text()) or {}
            registry_data = loaded if isinstance(loaded, dict) else registry_data

        reg_entries: list = registry_data.get("entries", [])
        reg_entries.append({
            "pattern_id": entry.pattern_id,
            "orchestrator": entry.orchestrator,
            "operation": entry.operation,
            "outcome": entry.outcome.value if hasattr(entry.outcome, "value") else str(entry.outcome),
            "confidence": entry.confidence,
            "file_path": str(shard.relative_to(self._root)) if shard.is_relative_to(self._root) else str(shard),
            "recorded_at": entry.recorded_at,
        })
        registry_data["entries"] = reg_entries
        registry_data["total_entries"] = len(reg_entries)
        registry_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._registry_file.write_text(
            yaml.safe_dump(registry_data, sort_keys=False, allow_unicode=True)
        )
