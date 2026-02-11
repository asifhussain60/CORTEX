"""
Capability Documentation System - CR-001-02

Auto-generates capability documentation from orchestrator metadata.
Provides search and indexing functionality.

Author: Asif Hussain
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class DocumentationMetadata:
    """Documentation metadata"""

    orchestrator_id: str
    version: str
    schema_version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary

        Returns:
            Metadata as dictionary
        """
        return {
            "orchestrator_id": self.orchestrator_id,
            "version": self.version,
            "schema_version": self.schema_version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class CapabilityDocumentation:
    """Capability documentation for an orchestrator"""

    orchestrator_id: str
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    domain: str = ""
    examples: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    changelog: List[Dict[str, Any]] = field(default_factory=list)

    def on_created(self) -> Dict[str, Any]:
        """Lifecycle hook: on creation

        Returns:
            Creation event data
        """
        return {
            "event": "created",
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_id": self.orchestrator_id,
        }

    def on_updated(self) -> Dict[str, Any]:
        """Lifecycle hook: on update

        Returns:
            Update event data
        """
        return {
            "event": "updated",
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_id": self.orchestrator_id,
        }

    def get_changelog(self) -> List[Dict[str, Any]]:
        """Get change log

        Returns:
            List of changes
        """
        return self.changelog.copy()


class CapabilityDocGenerator:
    """Generates capability documentation"""

    def generate_from_metadata(
        self,
        metadata: Dict[str, Any]
    ) -> CapabilityDocumentation:
        """Generate documentation from metadata

        Args:
            metadata: Orchestrator metadata dictionary

        Returns:
            Generated documentation
        """
        return CapabilityDocumentation(
            orchestrator_id=metadata.get("id", "unknown"),
            name=metadata.get("name", ""),
            description=metadata.get("description", ""),
            capabilities=metadata.get("capabilities", []),
            domain=metadata.get("domain", ""),
        )

    def to_markdown(self, doc: CapabilityDocumentation) -> str:
        """Convert documentation to markdown

        Args:
            doc: Capability documentation

        Returns:
            Markdown string
        """
        lines = [
            f"# {doc.name}",
            "",
            f"**ID:** `{doc.orchestrator_id}`",
            f"**Domain:** `{doc.domain}`",
            "",
            "## Description",
            f"{doc.description}",
            "",
        ]

        if doc.capabilities:
            lines.extend([
                "## Capabilities",
                "",
            ])
            for cap in doc.capabilities:
                lines.append(f"- `{cap}`")
            lines.append("")

        if doc.examples:
            lines.extend([
                "## Examples",
                "",
            ])
            for example in doc.examples:
                lines.append(f"- {example}")
            lines.append("")

        if doc.constraints:
            lines.extend([
                "## Constraints",
                "",
            ])
            for constraint in doc.constraints:
                lines.append(f"- {constraint}")
            lines.append("")

        return "\n".join(lines)

    def to_json(self, doc: CapabilityDocumentation) -> Dict[str, Any]:
        """Convert documentation to JSON

        Args:
            doc: Capability documentation

        Returns:
            JSON-serializable dictionary
        """
        return {
            "orchestrator_id": doc.orchestrator_id,
            "name": doc.name,
            "description": doc.description,
            "domain": doc.domain,
            "capabilities": doc.capabilities,
            "examples": doc.examples,
            "constraints": doc.constraints,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat(),
        }


@dataclass
class SearchResult:
    """Search result with relevance score"""

    orchestrator_id: str
    name: str
    domain: str
    relevance_score: float = 1.0
    doc: Optional[CapabilityDocumentation] = None


class CapabilityIndex:
    """Index for searching capability documentation"""

    def __init__(self) -> None:
        """Initialize capability index"""
        self._docs: Dict[str, CapabilityDocumentation] = {}

    def add(self, doc: CapabilityDocumentation) -> None:
        """Add documentation to index

        Args:
            doc: Documentation to add
        """
        self._docs[doc.orchestrator_id] = doc

    def get_all(self) -> List[CapabilityDocumentation]:
        """Get all indexed documentation

        Returns:
            List of all documentation
        """
        return list(self._docs.values())

    def search_by_capability(
        self,
        capability: str
    ) -> List[CapabilityDocumentation]:
        """Search by capability

        Args:
            capability: Capability name to search for

        Returns:
            List of matching documentation
        """
        results = []
        for doc in self._docs.values():
            if capability.lower() in [c.lower() for c in doc.capabilities]:
                results.append(doc)
        return results

    def search_by_domain(self, domain: str) -> List[CapabilityDocumentation]:
        """Search by domain

        Args:
            domain: Domain to search for

        Returns:
            List of matching documentation
        """
        results = []
        for doc in self._docs.values():
            if doc.domain.lower() == domain.lower():
                results.append(doc)
        return results

    def search_by_keyword(self, keyword: str) -> List[SearchResult]:
        """Search by keyword

        Args:
            keyword: Keyword to search for

        Returns:
            List of search results with relevance scores
        """
        results = []
        keyword_lower = keyword.lower()

        for doc in self._docs.values():
            relevance = 0.0

            # Check name
            if keyword_lower in doc.name.lower():
                relevance += 2.0

            # Check description
            if keyword_lower in doc.description.lower():
                relevance += 1.0

            # Check capabilities
            if any(keyword_lower in c.lower() for c in doc.capabilities):
                relevance += 1.5

            if relevance > 0:
                results.append(
                    SearchResult(
                        orchestrator_id=doc.orchestrator_id,
                        name=doc.name,
                        domain=doc.domain,
                        relevance_score=relevance,
                        doc=doc,
                    )
                )

        # Sort by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results

    def search_full_text(
        self,
        query: str,
        limit: int = 50
    ) -> List[SearchResult]:
        """Full-text search across documentation

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of search results
        """
        results = self.search_by_keyword(query)
        return results[:limit]

    def export_to_html(self) -> str:
        """Export index to HTML

        Returns:
            HTML representation of index
        """
        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Capability Documentation</title>",
            "</head>",
            "<body>",
            "<h1>Capability Documentation</h1>",
        ]

        for doc in self._docs.values():
            html_lines.extend([
                "<div class='orchestrator'>",
                f"<h2>{doc.name}</h2>",
                f"<p><strong>ID:</strong> {doc.orchestrator_id}</p>",
                f"<p><strong>Domain:</strong> {doc.domain}</p>",
                f"<p>{doc.description}</p>",
                "<h3>Capabilities</h3>",
                "<ul>",
            ])

            for cap in doc.capabilities:
                html_lines.append(f"<li>{cap}</li>")

            html_lines.extend([
                "</ul>",
                "</div>",
            ])

        html_lines.extend([
            "</body>",
            "</html>",
        ])

        return "\n".join(html_lines)
