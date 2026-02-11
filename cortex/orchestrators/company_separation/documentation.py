"""Phase 47 S6: Documentation and Deprecation.

Final documentation, deprecation warnings, and cleanup.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class DeprecationNotice:
    """Deprecation notice for legacy code."""

    old_path: str
    new_path: str
    deprecated_date: str
    removal_date: str
    message: str
    severity: str  # "low", "medium", "high"


class DocumentationGenerator:
    """Generate migration documentation."""

    def __init__(self):
        """Initialize generator."""
        self.sections: List[Dict[str, str]] = []

    def add_section(self, title: str, content: str) -> None:
        """Add documentation section.

        Args:
            title: Section title
            content: Section content
        """
        self.sections.append({"title": title, "content": content})

    def generate_markdown(self) -> str:
        """Generate markdown documentation.

        Returns:
            Markdown formatted documentation.
        """
        lines = ["# CORTEX Company Registry Migration Guide\n"]

        for section in self.sections:
            lines.append(f"## {section['title']}\n")
            lines.append(f"{section['content']}\n")

        return "\n".join(lines)

    def generate_yaml(self) -> Dict[str, Any]:
        """Generate YAML documentation.

        Returns:
            YAML-compatible dictionary.
        """
        return {
            "title": "CORTEX Company Registry Migration",
            "sections": self.sections,
        }

    def get_sections_count(self) -> int:
        """Get number of sections.

        Returns:
            Count of documentation sections.
        """
        return len(self.sections)


class DeprecationManager:
    """Manage deprecation of legacy code."""

    def __init__(self):
        """Initialize manager."""
        self.notices: List[DeprecationNotice] = []

    def add_deprecation(
        self,
        old_path: str,
        new_path: str,
        removal_date: str,
        message: str,
        severity: str = "medium",
    ) -> None:
        """Add deprecation notice.

        Args:
            old_path: Path to deprecated code
            new_path: Path to replacement code
            removal_date: Expected removal date
            message: Deprecation message
            severity: Severity level
        """
        notice = DeprecationNotice(
            old_path=old_path,
            new_path=new_path,
            deprecated_date=datetime.now().isoformat(),
            removal_date=removal_date,
            message=message,
            severity=severity,
        )
        self.notices.append(notice)

    def get_deprecations(self) -> List[DeprecationNotice]:
        """Get all deprecation notices.

        Returns:
            List of DeprecationNotice objects.
        """
        return self.notices

    def get_high_priority_deprecations(self) -> List[DeprecationNotice]:
        """Get high priority deprecations.

        Returns:
            List of high priority DeprecationNotice objects.
        """
        return [n for n in self.notices if n.severity == "high"]

    def generate_deprecation_warnings(self) -> List[str]:
        """Generate deprecation warning messages.

        Returns:
            List of warning strings.
        """
        warnings = []

        for notice in self.notices:
            warning = (
                f"DEPRECATED: {notice.old_path} → {notice.new_path}\n"
                f"  {notice.message}\n"
                f"  Removal: {notice.removal_date}"
            )
            warnings.append(warning)

        return warnings

    def get_deprecation_summary(self) -> Dict[str, Any]:
        """Get deprecation summary.

        Returns:
            Dictionary with deprecation summary.
        """
        return {
            "total_deprecations": len(self.notices),
            "high_severity": len(self.get_high_priority_deprecations()),
            "by_severity": {
                "high": len([n for n in self.notices if n.severity == "high"]),
                "medium": len([n for n in self.notices if n.severity == "medium"]),
                "low": len([n for n in self.notices if n.severity == "low"]),
            },
        }


class MigrationCheckpoint:
    """Track migration checkpoint."""

    def __init__(self, name: str):
        """Initialize checkpoint.

        Args:
            name: Checkpoint name
        """
        self.name = name
        self.created_at = datetime.now().isoformat()
        self.status = "active"
        self.metrics: Dict[str, Any] = {}

    def record_metric(self, metric_name: str, value: Any) -> None:
        """Record metric.

        Args:
            metric_name: Name of metric
            value: Metric value
        """
        self.metrics[metric_name] = value

    def mark_complete(self) -> None:
        """Mark checkpoint as complete."""
        self.status = "complete"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "name": self.name,
            "created_at": self.created_at,
            "status": self.status,
            "metrics": self.metrics,
        }


class CleanupValidator:
    """Validate cleanup operations."""

    def __init__(self):
        """Initialize validator."""
        self.cleanup_items: List[Dict[str, str]] = []
        self.cleanup_count = 0

    def add_cleanup_item(self, item_type: str, item_path: str) -> None:
        """Add cleanup item.

        Args:
            item_type: Type of item (file/directory/reference)
            item_path: Path to item
        """
        self.cleanup_items.append(
            {
                "type": item_type,
                "path": item_path,
                "status": "pending",
            }
        )

    def mark_cleaned(self, index: int) -> bool:
        """Mark item as cleaned.

        Args:
            index: Index of item

        Returns:
            True if successfully marked.
        """
        if 0 <= index < len(self.cleanup_items):
            self.cleanup_items[index]["status"] = "cleaned"
            self.cleanup_count += 1
            return True
        return False

    def get_cleanup_status(self) -> Dict[str, Any]:
        """Get cleanup status.

        Returns:
            Dictionary with status.
        """
        return {
            "total_items": len(self.cleanup_items),
            "cleaned_items": self.cleanup_count,
            "remaining_items": len(self.cleanup_items) - self.cleanup_count,
        }

    def get_cleanup_summary(self) -> str:
        """Get cleanup summary.

        Returns:
            Formatted summary string.
        """
        status = self.get_cleanup_status()

        return (
            f"Cleanup Progress: {status['cleaned_items']}/{status['total_items']} items\n"
            f"Remaining: {status['remaining_items']} items"
        )
