"""
Add data-cortex-* semantic selectors to HTML files.

Phase 99 Stage 2 implementation:
- CortexIDValidator  — validates data-cortex-id format, uniqueness, type
- CortexIDMigrator   — adds / migrates data-cortex-* attributes in HTML
- ValidationResult   — value object returned by all validation methods

AC-MEGA-PHASE99-S2-001: Pre-commit hook validates unique IDs
AC-MEGA-PHASE99-S2-002: Migration script operational
AC-MEGA-PHASE99-S2-003: data-cortex-* attributes added to HTML

Author: Asif Hussain
Phase: 99
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Value object
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    valid: bool = True
    errors: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Record an error and mark the result as invalid."""
        self.errors.append(message)
        self.valid = False


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

_VALID_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$")
_MAX_ID_LENGTH = 50
_VALID_TYPES = {"nav", "cta", "content", "viz", "form"}


class CortexIDValidator:
    """Validate data-cortex-* semantic selector attributes in HTML.

    Rules enforced:
    - IDs must be lowercase alphanumeric + hyphens only
    - IDs must not exceed 50 characters
    - IDs must be unique within a document
    - data-cortex-type must be one of the canonical set
    """

    # -- ID format -----------------------------------------------------------

    def validate_id(self, cortex_id: str) -> ValidationResult:
        """Validate a single data-cortex-id value.

        Args:
            cortex_id: The candidate ID string.

        Returns:
            ValidationResult with .valid and .errors populated.
        """
        result = ValidationResult()

        if len(cortex_id) > _MAX_ID_LENGTH:
            result.add_error(
                f"ID exceeds maximum length of 50 characters: '{cortex_id}' ({len(cortex_id)} chars)"
            )

        if cortex_id != cortex_id.lower():
            result.add_error(
                f"ID must be lowercase: '{cortex_id}' — convert to lowercase"
            )

        if not re.match(r"^[a-z0-9][a-z0-9-]*$|^[a-z0-9]$", cortex_id):
            result.add_error(
                f"ID must contain only alphanumeric characters and hyphens: '{cortex_id}'"
            )

        return result

    # -- Duplicate detection -------------------------------------------------

    def check_duplicates(self, html_content: str) -> ValidationResult:
        """Detect duplicate data-cortex-id values in HTML content.

        Args:
            html_content: Raw HTML string to inspect.

        Returns:
            ValidationResult; errors contain the duplicate ID value.
        """
        result = ValidationResult()
        ids_found: Dict[str, int] = {}

        for match in re.finditer(r'data-cortex-id="([^"]+)"', html_content):
            cid = match.group(1)
            ids_found[cid] = ids_found.get(cid, 0) + 1

        for cid, count in ids_found.items():
            if count > 1:
                result.add_error(
                    f"duplicate cortex-id detected: '{cid}' appears {count} times"
                )

        return result

    # -- Type validation -----------------------------------------------------

    def validate_type(self, type_value: str) -> ValidationResult:
        """Validate a data-cortex-type attribute value.

        Args:
            type_value: The candidate type string.

        Returns:
            ValidationResult.
        """
        result = ValidationResult()
        if type_value not in _VALID_TYPES:
            result.add_error(
                f"invalid cortex type '{type_value}' — must be one of: {sorted(_VALID_TYPES)}"
            )
        return result


# ---------------------------------------------------------------------------
# Migrator
# ---------------------------------------------------------------------------

# Tags that receive automatic cortex-id assignment
_MIGRATABLE_TAGS = {"button", "nav", "a", "header", "section", "article", "main"}


class CortexIDMigrator:
    """Add data-cortex-* attributes to HTML elements that lack them.

    Usage::

        migrator = CortexIDMigrator()
        output_html = migrator.add_cortex_ids(input_html)

        output_html, summary = migrator.migrate_with_summary(input_html)
    """

    # -- ID generation -------------------------------------------------------

    def generate_id(
        self,
        tag: str,
        class_name: Optional[str] = None,
        index: int = 0,
    ) -> str:
        """Generate a semantic cortex-id for an HTML element.

        Args:
            tag: HTML tag name (e.g. 'button').
            class_name: Primary CSS class (used as prefix when present).
            index: Zero-based occurrence index.

        Returns:
            A valid cortex-id string, e.g. 'cta-primary-001'.
        """
        prefix = class_name if class_name else tag
        # Normalise: lowercase, replace underscores/spaces with hyphens
        prefix = re.sub(r"[^a-z0-9-]", "-", prefix.lower()).strip("-")
        return f"{prefix}-{index:03d}"

    # -- Type inference -------------------------------------------------------

    def _infer_type(self, tag: str, class_name: str) -> str:
        """Infer data-cortex-type from tag and class."""
        if tag == "nav" or "nav" in class_name:
            return "nav"
        if "cta" in class_name or tag == "button" or tag == "a":
            return "cta"
        if tag in {"section", "article", "main"}:
            return "content"
        return "content"

    # -- Migration -----------------------------------------------------------

    def add_cortex_ids(self, html_content: str) -> str:
        """Add data-cortex-id and data-cortex-type to elements that lack them.

        Existing data-cortex-id values are preserved unchanged.

        Args:
            html_content: Raw HTML input.

        Returns:
            HTML with data-cortex-* attributes injected.
        """
        output, _ = self._process(html_content)
        return output

    def migrate_with_summary(self, html_content: str) -> Tuple[str, Dict]:
        """Migrate HTML and return a summary report.

        Args:
            html_content: Raw HTML input.

        Returns:
            Tuple of (migrated HTML, summary dict).
        """
        return self._process(html_content)

    # -- Internal ------------------------------------------------------------

    def _process(self, html_content: str) -> Tuple[str, Dict]:
        """Core migration logic."""
        counters: Dict[str, int] = {}
        ids_added = 0
        ids_preserved = 0
        elements_modified = 0

        def _replace(m: re.Match) -> str:
            nonlocal ids_added, ids_preserved, elements_modified

            full_tag = m.group(0)
            tag = m.group(1).lower()

            # Already has a cortex-id → preserve
            if "data-cortex-id=" in full_tag:
                ids_preserved += 1
                return full_tag

            # Infer class name from class="..." if present
            class_match = re.search(r'class="([^"]*)"', full_tag)
            primary_class = class_match.group(1).split()[0] if class_match else ""

            # Build a counter key
            counter_key = f"{tag}:{primary_class}"
            idx = counters.get(counter_key, 0)
            counters[counter_key] = idx + 1

            cortex_id = self.generate_id(tag, primary_class or None, idx)
            cortex_type = self._infer_type(tag, primary_class)

            # Inject attributes before the closing >
            injected = full_tag[:-1] if full_tag.endswith(">") else full_tag
            injected = f'{injected} data-cortex-id="{cortex_id}" data-cortex-type="{cortex_type}">'

            ids_added += 1
            elements_modified += 1
            return injected

        # Match opening tags for migratable elements
        pattern = r"<(" + "|".join(_MIGRATABLE_TAGS) + r")\b([^>]*)>"
        result = re.sub(pattern, _replace, html_content, flags=re.IGNORECASE)

        summary = {
            "elements_modified": elements_modified,
            "ids_added": ids_added,
            "ids_preserved": ids_preserved,
        }
        return result, summary
