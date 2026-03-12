"""IngestContentRouter — Phase 144-d.

Routes extracted knowledge to the correct cortex-registry/ destination
using a 14-domain routing table.  Business-rules content is segregated
to the company/ folder.

Source: GitHub Issue #17 — FB-2026-03-09-074435-001
CORE: CORE-008, CORE-011, CORE-012
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .file_classifier import ClassifiedFile, IngestFileCategory
from .knowledge_extractor import ExtractedKnowledge


# ─────────────────────────────────────────────────────────────────────────────
# 14-domain routing table
# ─────────────────────────────────────────────────────────────────────────────

_DOMAIN_ROUTING: dict[str, str] = {
    "architecture":             "knowledge/best-practices/content/architecture",
    "backend-python":           "knowledge/best-practices/content/backend-python",
    "backend-dotnet":           "knowledge/best-practices/content/backend-dotnet",
    "backend-java":             "knowledge/best-practices/content/backend-java",
    "frontend":                 "knowledge/best-practices/content/frontend",
    "security":                 "knowledge/best-practices/content/security",
    "testing-validation":       "knowledge/best-practices/content/testing-validation",
    "devops-infrastructure":    "knowledge/best-practices/content/devops-infrastructure",
    "performance-optimization": "knowledge/best-practices/content/performance-optimization",
    "sdlc":                     "knowledge/best-practices/content/sdlc",
    "business-rules":           "company/knowledge/business-rules",
    "migration":                "knowledge/best-practices/content/migration",
    "ai":                       "knowledge/best-practices/content/ai",
    "general":                  "knowledge/best-practices/content/general",
}

# Domains that route to company/ folder
_COMPANY_DOMAINS = frozenset({"business-rules"})

# Category-based fallback routing when no domain hint is available
_CATEGORY_FALLBACK: dict[IngestFileCategory, str] = {
    IngestFileCategory.ARCHITECTURE_DOC: "architecture",
    IngestFileCategory.PROCESS_DOC:      "sdlc",
    IngestFileCategory.RCA_DOC:          "general",
    IngestFileCategory.RELEASE_DOC:      "migration",
    IngestFileCategory.TECHNICAL_DOC:    "general",
    IngestFileCategory.KNOWLEDGE_YAML:   "general",
}


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RoutingDecision:
    """Result of routing a single file.

    Attributes:
        source: Original ClassifiedFile.
        destination_dir: Target directory path (relative to registry root).
        output_filename: Suggested filename for the persisted file.
        output_format: Target format ('yaml' or 'md').
        is_company_content: True when routed to company/ folder.
    """

    source: ClassifiedFile
    destination_dir: str
    output_filename: str
    output_format: str
    is_company_content: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────────────────────

class IngestContentRouter:
    """Routes classified files to their cortex-registry/ destination.

    Routing priority:
    1. Domain hint from classifier
    2. Category-based fallback
    3. 'general' catch-all

    Usage::

        router = IngestContentRouter()
        decision = router.route(classified_file)
    """

    def route(
        self,
        classified: ClassifiedFile,
        knowledge: Optional[ExtractedKnowledge] = None,
    ) -> RoutingDecision:
        """Route a classified file to its target cortex-registry/ location.

        Args:
            classified: ClassifiedFile from IngestFileClassifier.
            knowledge: Optional ExtractedKnowledge — used for domain override.

        Returns:
            RoutingDecision with destination directory and filename.
        """
        # Determine domain: ExtractedKnowledge takes precedence over classifier hint
        domain = (
            (knowledge.domain if knowledge else None)
            or classified.domain_hint
            or _CATEGORY_FALLBACK.get(classified.category, "general")
        )
        if domain not in _DOMAIN_ROUTING:
            domain = "general"

        destination_dir = _DOMAIN_ROUTING[domain]
        is_company = domain in _COMPANY_DOMAINS

        output_format = self._determine_output_format(classified)
        output_filename = self._build_output_filename(classified, output_format)

        return RoutingDecision(
            source=classified,
            destination_dir=destination_dir,
            output_filename=output_filename,
            output_format=output_format,
            is_company_content=is_company,
        )

    # ── Helpers ───────────────────────────────────────────────────────────

    def _determine_output_format(self, classified: ClassifiedFile) -> str:
        """Return 'yaml' for KNOWLEDGE_YAML category, else 'md'."""
        if classified.category == IngestFileCategory.KNOWLEDGE_YAML:
            return "yaml"
        return "md"

    def _build_output_filename(self, classified: ClassifiedFile, fmt: str) -> str:
        """Derive a safe output filename from origin path and format."""
        stem = classified.path.stem.lower().replace(" ", "-").replace("_", "-")
        # Remove any leading dots
        stem = stem.lstrip(".")
        return f"{stem}.{fmt}"
