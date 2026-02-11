"""
Response Assembly Orchestrator - Layer 2 Quality Enhancement.

Coordinates multi-template responses with:
- Semantic deduplication via fingerprinting
- Section reordering for narrative coherence
- Cross-template validation
- Unified response generation

Mirrors ContextAssemblyOrchestrator pattern for output symmetry.

Module: cortex.orchestrators.core.response_assembly_orchestrator
Author: Asif Hussain
Created: 2026-02-09
Version: 1.0
Authority: ENH-064 Phase 3 - Quality Enhancement
"""

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from cortex.orchestrators.core.base_response_template import ContentZone


class AssemblyStrategy(str, Enum):
    """Strategy for assembling multi-template responses."""

    SEQUENTIAL = "sequential"  # Preserve order
    NARRATIVE = "narrative"  # Reorder for coherence
    HIERARCHICAL = "hierarchical"  # Group by priority


@dataclass
class TemplateOutput:
    """Output from a single template."""

    orchestrator_name: str
    content: str
    zones: Set[ContentZone]
    priority: int = 5  # 1-10, higher = more important
    metadata: Dict = field(default_factory=dict)


@dataclass
class ResponseFragment:
    """Semantic fragment of response content."""

    content: str
    fingerprint: str
    zone: Optional[ContentZone] = None
    source_template: str = ""

    @staticmethod
    def create(content: str, zone: Optional[ContentZone], source: str) -> "ResponseFragment":
        """Create fragment with fingerprint."""
        # Normalize content for fingerprinting
        normalized = content.lower().strip()
        normalized = " ".join(normalized.split())  # Collapse whitespace

        # Create semantic fingerprint (first 100 chars)
        semantic_key = normalized[:100]
        fingerprint = hashlib.md5(semantic_key.encode()).hexdigest()[:8]

        return ResponseFragment(
            content=content,
            fingerprint=fingerprint,
            zone=zone,
            source_template=source
        )


class ResponseAssemblyOrchestrator:
    """
    Assembles multi-template responses with deduplication.

    Mirrors ContextAssemblyOrchestrator for input/output symmetry.
    Provides Layer 2 quality enhancement for ENH-064.
    """

    def __init__(self, strategy: AssemblyStrategy = AssemblyStrategy.SEQUENTIAL):
        """Initialize response assembly orchestrator.

        Args:
            strategy: Assembly strategy to use
        """
        self.strategy = strategy
        self._similarity_threshold = 0.85

    def assemble(
        self,
        outputs: List[TemplateOutput],
        strategy: Optional[AssemblyStrategy] = None
    ) -> str:
        """
        Assemble multiple template outputs into unified response.

        Args:
            outputs: List of template outputs to assemble
            strategy: Override default assembly strategy

        Returns:
            Unified response with deduplication applied
        """
        if not outputs:
            return ""

        # Fast path: single template
        if len(outputs) == 1:
            return outputs[0].content

        # Use specified strategy or default
        strategy = strategy or self.strategy

        # Step 1: Validate no zone conflicts
        self._validate_zones(outputs)

        # Step 2: Fragment responses by section
        fragments = self._fragment_responses(outputs)

        # Step 3: Deduplicate fragments
        unique_fragments = self._deduplicate(fragments)

        # Step 4: Apply assembly strategy
        if strategy == AssemblyStrategy.SEQUENTIAL:
            ordered = self._assemble_sequential(unique_fragments, outputs)
        elif strategy == AssemblyStrategy.NARRATIVE:
            ordered = self._assemble_narrative(unique_fragments)
        elif strategy == AssemblyStrategy.HIERARCHICAL:
            ordered = self._assemble_hierarchical(unique_fragments, outputs)
        else:
            ordered = unique_fragments

        # Step 5: Combine into single response
        return "\n".join(f.content for f in ordered)

    def _validate_zones(self, outputs: List[TemplateOutput]) -> None:
        """
        Validate no zone conflicts across templates.

        Args:
            outputs: Template outputs to validate

        Raises:
            RuntimeError: If zone conflicts detected
        """
        zone_sources: Dict[ContentZone, List[str]] = defaultdict(list)

        for output in outputs:
            for zone in output.zones:
                zone_sources[zone].append(output.orchestrator_name)

        # Check for conflicts
        conflicts = {
            zone: sources
            for zone, sources in zone_sources.items()
            if len(sources) > 1
        }

        if conflicts:
            conflict_desc = ", ".join([
                f"{zone.value} ({', '.join(sources)})"
                for zone, sources in conflicts.items()
            ])
            raise RuntimeError(
                f"Content zone conflicts detected: {conflict_desc}. "
                f"Multiple templates attempting to provide same semantic content."
            )

    def _fragment_responses(self, outputs: List[TemplateOutput]) -> List[ResponseFragment]:
        """
        Fragment responses by sections for analysis.

        Args:
            outputs: Template outputs to fragment

        Returns:
            List of response fragments
        """
        fragments = []

        for output in outputs:
            # Split by headers (## and ###)
            sections = self._split_sections(output.content)

            for section_content in sections:
                # Determine zone from content
                zone = self._infer_zone(section_content, output.zones)

                fragment = ResponseFragment.create(
                    content=section_content,
                    zone=zone,
                    source=output.orchestrator_name
                )
                fragments.append(fragment)

        return fragments

    def _split_sections(self, content: str) -> List[str]:
        """Split content by markdown headers."""
        lines = content.split("\n")
        sections = []
        current_section = []

        for line in lines:
            if line.startswith("## ") or line.startswith("### "):
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []
            current_section.append(line)

        if current_section:
            sections.append("\n".join(current_section))

        return sections

    def _infer_zone(self, content: str, declared_zones: Set[ContentZone]) -> Optional[ContentZone]:
        """Infer content zone from section content."""
        content_lower = content.lower()

        # Match keywords to zones
        zone_keywords = {
            ContentZone.TEST_RESULTS: ["test", "passing", "failing"],
            ContentZone.COVERAGE_METRICS: ["coverage", "line", "branch"],
            ContentZone.RECOMMENDATIONS: ["recommend", "suggest", "should"],
            ContentZone.ANALYSIS: ["analysis", "examine", "findings"],
            ContentZone.SECURITY: ["security", "vulnerability", "threat"],
        }

        for zone in declared_zones:
            if zone in zone_keywords:
                keywords = zone_keywords[zone]
                if any(kw in content_lower for kw in keywords):
                    return zone

        return None

    def _deduplicate(self, fragments: List[ResponseFragment]) -> List[ResponseFragment]:
        """
        Remove duplicate fragments based on fingerprints.

        Args:
            fragments: Fragments to deduplicate

        Returns:
            Unique fragments only
        """
        seen_fingerprints: Set[str] = set()
        unique = []

        for fragment in fragments:
            if fragment.fingerprint not in seen_fingerprints:
                unique.append(fragment)
                seen_fingerprints.add(fragment.fingerprint)

        return unique

    def _assemble_sequential(
        self,
        fragments: List[ResponseFragment],
        outputs: List[TemplateOutput]
    ) -> List[ResponseFragment]:
        """Assemble fragments in original template order."""
        # Sort by source template order
        template_order = {out.orchestrator_name: i for i, out in enumerate(outputs)}

        return sorted(
            fragments,
            key=lambda f: template_order.get(f.source_template, 999)
        )

    def _assemble_narrative(self, fragments: List[ResponseFragment]) -> List[ResponseFragment]:
        """Assemble fragments for narrative flow."""
        # Define narrative order for zones
        zone_order = {
            ContentZone.CONTEXT: 1,
            ContentZone.ANALYSIS: 2,
            ContentZone.TEST_RESULTS: 3,
            ContentZone.COVERAGE_METRICS: 4,
            ContentZone.SECURITY: 5,
            ContentZone.RECOMMENDATIONS: 6,
            ContentZone.PLAN: 7,
        }

        return sorted(
            fragments,
            key=lambda f: zone_order.get(f.zone, 99) if f.zone else 99
        )

    def _assemble_hierarchical(
        self,
        fragments: List[ResponseFragment],
        outputs: List[TemplateOutput]
    ) -> List[ResponseFragment]:
        """Assemble fragments by priority."""
        # Get priority for each source
        priority_map = {out.orchestrator_name: out.priority for out in outputs}

        return sorted(
            fragments,
            key=lambda f: priority_map.get(f.source_template, 5),
            reverse=True  # Higher priority first
        )


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "ResponseAssemblyOrchestrator",
    "AssemblyStrategy",
    "TemplateOutput",
    "ResponseFragment",
]
