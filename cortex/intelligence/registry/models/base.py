"""
BaseRegistryModel — abstract base for all registry artifact models.

Every YAML artifact in cortex-registry/ is parsed into a subclass of this model.
The model provides deterministic JSON serialization with sorted keys for stable
hashing and diff detection.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from typing import Any, Dict, List, Optional


@dataclasses.dataclass
class BaseRegistryModel:
    """Base model for all registry artifacts.

    Provides deterministic JSON serialization, stable hashing, and a
    consistent field contract that every viewer renderer can rely on.
    """

    id: str
    type: str
    source_file: str
    title: str
    source_hash: str
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)
    content: Dict[str, Any] = dataclasses.field(default_factory=dict)
    references: Dict[str, List[Dict[str, str]]] = dataclasses.field(
        default_factory=lambda: {"outgoing": [], "incoming": []}
    )
    integrity: Dict[str, Any] = dataclasses.field(
        default_factory=lambda: {
            "all_refs_resolved": True,
            "schema_valid": True,
            "warnings": [],
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """Return a dict with keys sorted alphabetically for deterministic output."""
        raw = dataclasses.asdict(self)
        return self._sort_dict(raw)

    def to_json(self) -> str:
        """Return deterministic JSON string (sorted keys, 2-space indent)."""
        return json.dumps(self.to_dict(), sort_keys=True, indent=2, ensure_ascii=False)

    def stable_hash(self) -> str:
        """Return a stable sha256 hash of the model's JSON representation."""
        json_bytes = self.to_json().encode("utf-8")
        digest = hashlib.sha256(json_bytes).hexdigest()
        return f"sha256:{digest}"

    @staticmethod
    def _sort_dict(d: Any) -> Any:
        """Recursively sort dict keys for deterministic serialization."""
        if isinstance(d, dict):
            return {k: BaseRegistryModel._sort_dict(v) for k, v in sorted(d.items(), key=lambda x: str(x[0]))}
        if isinstance(d, list):
            return [BaseRegistryModel._sort_dict(item) for item in d]
        return d
