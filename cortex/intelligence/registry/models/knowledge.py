"""
KnowledgeModel — typed model for knowledge-base YAML artifacts.

Represents YAML files in ``cortex-registry/knowledge/`` that define
best-practice guides, knowledge indexes, and domain-specific references.
"""

from __future__ import annotations

import dataclasses
import os
from typing import Any, Dict, List

from cortex.intelligence.registry.models.base import BaseRegistryModel


@dataclasses.dataclass
class KnowledgeModel(BaseRegistryModel):
    """Typed model for knowledge-base YAML artifacts.

    Extends :class:`BaseRegistryModel` with knowledge-specific fields for
    domains, guides, and keywords.
    """

    domains: List[str] = dataclasses.field(default_factory=list)
    guides: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    keywords: List[str] = dataclasses.field(default_factory=list)

    @classmethod
    def from_data(
        cls,
        data: Dict[str, Any],
        source_file: str,
    ) -> "KnowledgeModel":
        """Create a KnowledgeModel from parsed YAML data.

        Args:
            data: The parsed YAML dict (knowledge INDEX or guide).
            source_file: Path to the source YAML file.

        Returns:
            A fully populated ``KnowledgeModel`` instance.
        """
        if not isinstance(data, dict):
            data = {}

        # --- Extract domains and guides from INDEX-style data ---
        domains: List[str] = []
        guides: List[Dict[str, Any]] = []
        keywords: List[str] = []
        skip_keys = {"id", "title", "name", "created", "updated", "description"}

        for k, v in data.items():
            if k in skip_keys:
                continue
            if isinstance(v, dict) and "guides" in v:
                domains.append(k)
                domain_guides = v.get("guides", [])
                if isinstance(domain_guides, list):
                    for g in domain_guides:
                        if isinstance(g, dict):
                            guide_entry = dict(g)
                            guide_entry["domain"] = k
                            guides.append(guide_entry)
                            kws = g.get("keywords", [])
                            if isinstance(kws, list):
                                keywords.extend(kws)

        # Deduplicate keywords
        keywords = sorted(set(keywords))

        # --- ID ---
        knowledge_id = str(data.get("id", "") or data.get("name", "") or "")
        if not knowledge_id:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            knowledge_id = f"knowledge-{name_part}"

        # --- Title ---
        title = str(data.get("title", "") or data.get("name", "") or "")
        if not title:
            basename = os.path.basename(source_file)
            name_part = os.path.splitext(basename)[0]
            title = name_part.replace("-", " ").replace("_", " ").title()

        # --- Content (extra fields) ---
        content: Dict[str, Any] = {k: v for k, v in data.items()
                                    if k not in skip_keys and not (isinstance(v, dict) and "guides" in v)}

        meta: Dict[str, Any] = {}
        if data.get("created"):
            meta["created"] = str(data["created"])
        if data.get("updated"):
            meta["updated"] = str(data["updated"])

        return cls(
            id=knowledge_id,
            type="knowledge",
            source_file=source_file,
            title=title,
            source_hash="",
            metadata=meta,
            content=content,
            domains=domains,
            guides=guides,
            keywords=keywords,
        )
