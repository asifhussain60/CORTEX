"""
RegistryIndexer — full YAML→Model→JSON pipeline.

Orchestrates the complete registry documentation build:

1. **discover()** — find all YAML/YML files under ``root_dir``
2. **parse_all()** — parse each file using the typed parser registry
3. **resolve()** — cross-link references via ``ReferenceResolver``
4. **emit()** — produce the final JSON payload (artifacts + graph + integrity)
5. **run()** — convenience one-shot for the full pipeline

Output JSON structure::

    {
        "artifacts": [...],    # list of model dicts
        "graph": {...},        # D3.js-compatible dependency graph
        "integrity": {...},    # integrity report
        "stats": {...}         # summary statistics
    }
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import yaml

from cortex.intelligence.registry.dependency_graph import DependencyGraphBuilder
from cortex.intelligence.registry.integrity_checker import IntegrityChecker
from cortex.intelligence.registry.models.base import BaseRegistryModel
from cortex.intelligence.registry.parsers import get_parser_for_type
from cortex.intelligence.registry.reference_resolver import ReferenceResolver


class RegistryIndexer:
    """End-to-end registry documentation indexer.

    Args:
        root_dir: The root directory to scan for YAML files.
    """

    def __init__(self, root_dir: str) -> None:
        self._root_dir = root_dir
        self._files: List[str] = []
        self._models: List[BaseRegistryModel] = []
        self._resolver = ReferenceResolver()
        self._graph_builder = DependencyGraphBuilder()
        self._integrity_checker = IntegrityChecker()

    # ── Stage 1: Discover ───────────────────────────────────────────────

    def discover(self) -> List[str]:
        """Find all YAML/YML files under ``root_dir`` recursively.

        Returns:
            Sorted list of absolute file paths.
        """
        found: List[str] = []
        for dirpath, _dirnames, filenames in os.walk(self._root_dir):
            for fn in filenames:
                if fn.endswith((".yaml", ".yml")):
                    found.append(os.path.join(dirpath, fn))
        found.sort()
        self._files = found
        return found

    # ── Stage 2: Parse ──────────────────────────────────────────────────

    def parse_all(self) -> List[BaseRegistryModel]:
        """Parse every discovered YAML file into a typed model.

        Falls back to ``GenericParser`` for unknown ``schema_type`` values.

        Returns:
            List of parsed models.
        """
        self._models = []
        for filepath in self._files:
            model = self._parse_file(filepath)
            if model is not None:
                self._models.append(model)
        return self._models

    def _parse_file(self, filepath: str) -> Optional[BaseRegistryModel]:
        """Parse a single YAML file into a model."""
        try:
            with open(filepath) as f:
                data = yaml.safe_load(f)
        except Exception:
            return None

        if not isinstance(data, dict):
            return None

        schema_type = data.get("schema_type", "generic")
        relative = os.path.relpath(filepath, self._root_dir)

        parser_cls = get_parser_for_type(schema_type)
        parser = parser_cls()
        return parser.parse(data, source_file=relative)

    # ── Stage 3: Resolve ────────────────────────────────────────────────

    def resolve(self) -> None:
        """Cross-link references across all parsed models."""
        self._resolver.resolve(self._models)

    # ── Stage 4: Emit ───────────────────────────────────────────────────

    def emit(self) -> Dict[str, Any]:
        """Produce the complete output payload.

        Returns:
            Dict with ``artifacts``, ``graph``, ``integrity``, and ``stats``.
        """
        artifacts = [m.to_dict() for m in self._models]
        graph = self._graph_builder.build(self._models)
        integrity = self._integrity_checker.check(self._models)
        stats = self._graph_builder.stats(graph)

        return {
            "artifacts": artifacts,
            "graph": graph,
            "integrity": integrity,
            "stats": stats,
        }

    def to_json(self) -> str:
        """Emit the payload as deterministic JSON.

        Returns:
            JSON string with sorted keys and 2-space indent.
        """
        output = self.emit()
        return json.dumps(output, sort_keys=True, indent=2, ensure_ascii=False)

    def write_to(self, output_path: str) -> None:
        """Write the JSON payload to a file.

        Creates parent directories as needed.

        Args:
            output_path: Destination file path.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(self.to_json())

    # ── Convenience: Full pipeline ──────────────────────────────────────

    def run(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Execute the full discover→parse→resolve→emit pipeline.

        Args:
            output_path: If provided, also write JSON to this path.

        Returns:
            The complete output dict.
        """
        self.discover()
        self.parse_all()
        self.resolve()
        output = self.emit()

        if output_path:
            self.write_to(output_path)

        return output
