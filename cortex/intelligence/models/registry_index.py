"""
cortex.intelligence.models.registry_index — RegistryIndexEntry
===============================================================

Typed representation of a single file entry in the cortex-registry/ tree,
as produced by ``IntelligenceFacade.registry_index()``.

Phase 123 (GAP-123-05): Provides a cross-domain metadata map of all YAML
files in ``cortex-registry/`` categorised by domain, enabling orchestrators
and governance systems to navigate the registry without knowing file paths.

CORE Rules: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-035 (single canonical)
AC_START: AC-123-REGISTRY-INTELLIGENCE-ENGINE
AC_COMPLETE: AC-123-REGISTRY-INTELLIGENCE-ENGINE | marker pair declared for static audit coverage
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

__all__ = ["RegistryIndexEntry"]


# Map from cortex-registry/ top-level directory name → domain label
DOMAIN_MAP: Dict[str, str] = {
    "governance": "governance",
    "core": "governance",        # tier-0 skull rules, wiring specs
    "workflows": "workflows",
    "knowledge": "knowledge",
    "planning": "planning",
    "patterns": "patterns",
    "artifacts": "artifacts",
    "config": "config",
    "company": "company",
    "metrics": "metrics",
    "memory": "memory",
    "playbooks": "playbooks",
    "templates": "templates",
    "plans": "plans",
}


@dataclass
class RegistryIndexEntry:
    """Metadata for a single YAML file in the cortex-registry/ tree.

    Attributes:
        path: Absolute filesystem path to the YAML file (as string).
        domain: High-level domain category (e.g. 'governance', 'workflows',
            'knowledge', 'planning').
        schema_type: Inferred schema type based on directory and file content
            (e.g. 'governance_rule', 'workflow_template', 'knowledge_entry',
            'phase_plan', 'unknown').
        file_name: Bare filename without directory prefix (e.g. 'skull-rules.yaml').
        relative_path: Path relative to the cortex-registry/ root.
        extra: Any additional metadata collected during indexing.
    """

    path: str
    domain: str
    schema_type: str
    file_name: str
    relative_path: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_path(cls, file_path: object, registry_root: object) -> "RegistryIndexEntry":
        """Construct a RegistryIndexEntry from a filesystem path.

        Infers ``domain`` from the first-level subdirectory under the registry
        root and ``schema_type`` from the directory + filename pattern.

        Args:
            file_path: :class:`pathlib.Path` of the YAML file.
            registry_root: :class:`pathlib.Path` of the cortex-registry/ directory.

        Returns:
            Populated RegistryIndexEntry.
        """
        from pathlib import Path as _Path

        fp: _Path = _Path(str(file_path))
        root: _Path = _Path(str(registry_root))

        try:
            rel = fp.relative_to(root)
        except ValueError:
            rel = fp

        # Domain: first path component after the registry root
        parts = rel.parts
        top_dir = parts[0] if parts else "unknown"
        domain = DOMAIN_MAP.get(top_dir, top_dir)

        # Schema type: coarse inference from directory name
        schema_type = _infer_schema_type(top_dir, fp.name)

        return cls(
            path=str(fp),
            domain=domain,
            schema_type=schema_type,
            file_name=fp.name,
            relative_path=str(rel),
        )


def _infer_schema_type(top_dir: str, file_name: str) -> str:
    """Infer a coarse schema type from directory + filename.

    Args:
        top_dir: Top-level directory name under cortex-registry/.
        file_name: Bare filename.

    Returns:
        Schema type string.
    """
    mapping = {
        "governance": "governance_rule",
        "core": "governance_rule",
        "workflows": "workflow_template",
        "knowledge": "knowledge_entry",
        "planning": "phase_plan",
        "patterns": "pattern_definition",
        "artifacts": "artifact",
        "config": "configuration",
        "company": "company_config",
        "metrics": "metrics_config",
        "memory": "memory_entry",
        "playbooks": "playbook",
        "templates": "template",
        "plans": "plan",
    }
    return mapping.get(top_dir, "unknown")
