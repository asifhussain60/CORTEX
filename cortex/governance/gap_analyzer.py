"""
GapAnalyzer for CORTEX Company Domain Integration.

Detects and reports missing company standards.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 27 specification
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class GapEntry:
    """
    Represents a missing company standard.

    Attributes:
        domain: Standards domain (e.g., "security")
        subdomain: Standards subdomain (e.g., "authentication")
        used_by: Component that requested the standard
        fallback_source: What source was used as fallback
    """
    domain: str
    subdomain: str
    used_by: str
    fallback_source: str


@dataclass
class GapReport:
    """
    Company domain gap report.

    Attributes:
        gap_count: Number of gaps detected
        markdown: Markdown-formatted report
        timestamp: Report generation timestamp
    """
    gap_count: int
    markdown: str
    timestamp: str


class GapAnalyzer:
    """
    Analyzes and reports missing company standards.

    Tracks when StandardsResolver falls back to cortex or defaults,
    generates gap reports for AUDIT mode.

    Example:
        >>> analyzer = GapAnalyzer()
        >>> analyzer.record_gap("security", "auth", "Agent", "cortex")
        >>> report = analyzer.generate_report()
        >>> print(report.markdown)
    """

    def __init__(self):
        """Initialize gap analyzer with empty gaps list."""
        self.gaps: List[GapEntry] = []

        # Deduplication tracking
        self._seen_gaps: set = set()

    def record_gap(
        self,
        domain: str,
        subdomain: str,
        used_by: str,
        fallback_source: str,
    ):
        """
        Record a gap when company standard missing.

        Args:
            domain: Standards domain
            subdomain: Standards subdomain
            used_by: Component that requested standard
            fallback_source: Fallback source used
        """
        # Deduplicate
        gap_key = (domain, subdomain, used_by)
        if gap_key in self._seen_gaps:
            return

        # Record gap
        entry = GapEntry(
            domain=domain,
            subdomain=subdomain,
            used_by=used_by,
            fallback_source=fallback_source,
        )

        self.gaps.append(entry)
        self._seen_gaps.add(gap_key)

    def generate_report(self) -> GapReport:
        """
        Generate markdown gap report.

        Returns:
            GapReport with gap count and markdown content
        """
        if not self.gaps:
            return GapReport(
                gap_count=0,
                markdown="# Company Domain Gap Report\n\n✅ **No gaps detected** — All company standards found.",
                timestamp=datetime.now().isoformat(),
            )

        # Build markdown report
        lines = [
            "# Company Domain Gap Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"**Total Gaps:** {len(self.gaps)}",
            "",
            "## Missing Standards",
            "",
        ]

        # Group by domain
        by_domain = {}
        for gap in self.gaps:
            if gap.domain not in by_domain:
                by_domain[gap.domain] = []
            by_domain[gap.domain].append(gap)

        # Generate entries
        for domain, domain_gaps in sorted(by_domain.items()):
            lines.append(f"### {domain.title()}")
            lines.append("")

            for gap in domain_gaps:
                lines.append(f"#### `{gap.domain}/{gap.subdomain}.yaml`")
                lines.append(f"- **Used by:** {gap.used_by}")
                lines.append(f"- **Fallback:** {gap.fallback_source}")
                lines.append(f"- **Recommendation:** Define company-specific {gap.subdomain} patterns in `company/domains/{gap.domain}/{gap.subdomain}.yaml`")
                lines.append("")

        markdown = "\n".join(lines)

        return GapReport(
            gap_count=len(self.gaps),
            markdown=markdown,
            timestamp=datetime.now().isoformat(),
        )

    def clear_gaps(self):
        """Clear all recorded gaps."""
        self.gaps.clear()
        self._seen_gaps.clear()
