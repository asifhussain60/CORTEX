"""
Migration script for adding data-cortex-* semantic selectors to HTML.

Provides:
- CortexIDValidator: Validates cortex-id format, uniqueness, type values
- CortexIDMigrator: Adds data-cortex-* attributes to HTML elements
- Pre-commit hook integration for ID validation

Usage:
    # Validate HTML file
    python scripts/add_cortex_semantic_ids.py --validate cortex-docs/index.html

    # Migrate HTML file (add cortex-ids)
    python scripts/add_cortex_semantic_ids.py --migrate cortex-docs/index.html

    # Dry-run (preview changes)
    python scripts/add_cortex_semantic_ids.py --migrate cortex-docs/index.html --dry-run

Phase: 99 Stage 2
Author: Asif Hussain
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ValidationResult:
    """Result of cortex-id validation."""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class CortexIDValidator:
    """
    Validator for data-cortex-* semantic selectors.

    Validates:
    - ID format: lowercase alphanumeric + dash only
    - ID length: max 50 characters
    - ID uniqueness: no duplicates across HTML
    - Type values: nav, cta, content, viz, form

    Example:
        ```python
        validator = CortexIDValidator()
        result = validator.validate_id("hero-cta-001")
        if result.valid:
            print("Valid cortex-id")
        else:
            print(f"Errors: {result.errors}")
        ```
    """

    VALID_TYPES = {"nav", "cta", "content", "viz", "form"}
    VALID_TRACKS = {"conversion", "navigation", "engagement"}
    MAX_ID_LENGTH = 50

    def validate_id(self, cortex_id: str) -> ValidationResult:
        """
        Validate cortex-id format.

        Args:
            cortex_id: ID to validate.

        Returns:
            ValidationResult with errors if invalid.
        """
        errors = []

        # Check length
        if len(cortex_id) > self.MAX_ID_LENGTH:
            errors.append(f"ID exceeds max length of {self.MAX_ID_LENGTH} characters")

        # Check format (lowercase alphanumeric + dash)
        if not re.match(r"^[a-z0-9-]+$", cortex_id):
            errors.append(
                "ID must contain only lowercase alphanumeric characters and dashes"
            )

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def validate_type(self, type_value: str) -> ValidationResult:
        """
        Validate data-cortex-type value.

        Args:
            type_value: Type to validate.

        Returns:
            ValidationResult with errors if invalid.
        """
        if type_value not in self.VALID_TYPES:
            valid_str = ", ".join(sorted(self.VALID_TYPES))
            return ValidationResult(
                valid=False,
                errors=[f"Invalid type '{type_value}'. Valid types: {valid_str}"],
            )

        return ValidationResult(valid=True)

    def validate_track(self, track_value: str) -> ValidationResult:
        """
        Validate data-cortex-track value.

        Args:
            track_value: Track to validate.

        Returns:
            ValidationResult with errors if invalid.
        """
        if track_value not in self.VALID_TRACKS:
            valid_str = ", ".join(sorted(self.VALID_TRACKS))
            return ValidationResult(
                valid=False,
                errors=[f"Invalid track '{track_value}'. Valid tracks: {valid_str}"],
            )

        return ValidationResult(valid=True)

    def check_duplicates(self, html_content: str) -> ValidationResult:
        """
        Check for duplicate cortex-ids in HTML content.

        Args:
            html_content: HTML content to check.

        Returns:
            ValidationResult with errors for each duplicate ID.
        """
        # Extract all cortex-ids
        pattern = r'data-cortex-id="([^"]+)"'
        matches = re.findall(pattern, html_content)

        # Find duplicates
        seen: Set[str] = set()
        duplicates: Set[str] = set()

        for cortex_id in matches:
            if cortex_id in seen:
                duplicates.add(cortex_id)
            seen.add(cortex_id)

        if duplicates:
            errors = [f"Duplicate cortex-id found: {cid}" for cid in sorted(duplicates)]
            return ValidationResult(valid=False, errors=errors)

        return ValidationResult(valid=True)

    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Validate all cortex-ids in HTML file.

        Args:
            file_path: Path to HTML file.

        Returns:
            ValidationResult with all validation errors.
        """
        if not file_path.exists():
            return ValidationResult(valid=False, errors=[f"File not found: {file_path}"])

        html_content = file_path.read_text(encoding="utf-8")

        # Check duplicates
        dup_result = self.check_duplicates(html_content)
        if not dup_result.valid:
            return dup_result

        # Validate each ID format
        pattern = r'data-cortex-id="([^"]+)"'
        matches = re.findall(pattern, html_content)

        errors = []
        for cortex_id in matches:
            id_result = self.validate_id(cortex_id)
            if not id_result.valid:
                errors.extend([f"ID '{cortex_id}': {err}" for err in id_result.errors])

        return ValidationResult(valid=len(errors) == 0, errors=errors)


class CortexIDMigrator:
    """
    Migrator for adding data-cortex-* attributes to HTML elements.

    Adds semantic selectors to HTML elements for Vision API integration.
    Preserves existing cortex-ids if present.

    Example:
        ```python
        migrator = CortexIDMigrator()
        html_input = '<button class="cta-primary">Get Started</button>'
        html_output = migrator.add_cortex_ids(html_input)
        print(html_output)  # Contains data-cortex-id
        ```
    """

    def __init__(self) -> None:
        """Initialize migrator."""
        self.id_counter: Dict[str, int] = {}

    def generate_id(
        self, tag: str, class_name: Optional[str] = None, index: int = 0
    ) -> str:
        """
        Generate semantic cortex-id from element.

        Args:
            tag: HTML tag name.
            class_name: Element class name (if present).
            index: Index for uniqueness.

        Returns:
            Generated cortex-id.
        """
        if class_name:
            # Use class name as base
            base = class_name.lower().replace(" ", "-").replace("_", "-")
        else:
            # Use tag name as base
            base = tag.lower()

        # Add index suffix for uniqueness
        return f"{base}-{index:03d}"

    def add_cortex_ids(self, html_content: str) -> str:
        """
        Add data-cortex-* attributes to HTML elements.

        Args:
            html_content: Original HTML content.

        Returns:
            Modified HTML with cortex-id attributes.
        """
        # Find all elements that should have cortex-ids
        # Target: buttons, nav elements, CTAs, forms, major content sections

        # Pattern: <tag [attributes]>
        # Look for tags without existing data-cortex-id

        lines = []
        for line in html_content.split("\n"):
            # Skip if already has cortex-id
            if "data-cortex-id=" in line:
                lines.append(line)
                continue

            # Add cortex-id to interactive elements
            # This is a simplified implementation for testing
            # Real implementation would use HTML parser

            # Example: <button class="cta-primary">
            if "<button" in line and "data-cortex-id=" not in line:
                # Extract class name
                class_match = re.search(r'class="([^"]+)"', line)
                class_name = class_match.group(1) if class_match else None

                # Generate ID
                cortex_id = self.generate_id("button", class_name, self.id_counter.get("button", 0))
                self.id_counter["button"] = self.id_counter.get("button", 0) + 1

                # Add attributes
                line = line.replace(
                    "<button",
                    f'<button data-cortex-id="{cortex_id}" data-cortex-type="cta"',
                )

            # Example: <nav>
            elif "<nav" in line and "data-cortex-id=" not in line:
                class_match = re.search(r'class="([^"]+)"', line)
                class_name = class_match.group(1) if class_match else None

                cortex_id = self.generate_id("nav", class_name, self.id_counter.get("nav", 0))
                self.id_counter["nav"] = self.id_counter.get("nav", 0) + 1

                line = line.replace(
                    "<nav",
                    f'<nav data-cortex-id="{cortex_id}" data-cortex-type="nav"',
                )

            lines.append(line)

        return "\n".join(lines)

    def migrate_with_summary(self, html_content: str) -> Tuple[str, Dict[str, int]]:
        """
        Migrate HTML and return summary statistics.

        Args:
            html_content: Original HTML content.

        Returns:
            Tuple of (modified HTML, summary dict).
        """
        # Count existing cortex-ids
        existing_ids = len(re.findall(r'data-cortex-id="[^"]+"', html_content))

        # Perform migration
        migrated_html = self.add_cortex_ids(html_content)

        # Count new cortex-ids
        new_ids = len(re.findall(r'data-cortex-id="[^"]+"', migrated_html))

        summary = {
            "elements_modified": new_ids,
            "ids_added": new_ids - existing_ids,
            "ids_preserved": existing_ids,
        }

        return migrated_html, summary

    def migrate_file(self, file_path: Path, dry_run: bool = False) -> Dict[str, int]:
        """
        Migrate HTML file by adding cortex-ids.

        Args:
            file_path: Path to HTML file.
            dry_run: If True, don't write changes.

        Returns:
            Summary statistics dict.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        html_content = file_path.read_text(encoding="utf-8")
        migrated_html, summary = self.migrate_with_summary(html_content)

        if not dry_run:
            file_path.write_text(migrated_html, encoding="utf-8")

        return summary


def main() -> int:
    """
    CLI entry point for cortex-id migration.

    Returns:
        Exit code (0 = success, 1 = validation failed).
    """
    parser = argparse.ArgumentParser(
        description="Add data-cortex-* semantic selectors to HTML"
    )
    parser.add_argument("file", type=Path, help="HTML file to process")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate cortex-ids only (no modification)",
    )
    parser.add_argument(
        "--migrate", action="store_true", help="Add cortex-ids to HTML elements"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to file",
    )

    args = parser.parse_args()

    if args.validate:
        # Validation mode
        validator = CortexIDValidator()
        result = validator.validate_file(args.file)

        if result.valid:
            print(f"✅ All cortex-ids valid in {args.file}")
            return 0
        else:
            print(f"❌ Validation failed for {args.file}:")
            for error in result.errors:
                print(f"  - {error}")
            return 1

    elif args.migrate:
        # Migration mode
        migrator = CortexIDMigrator()

        try:
            summary = migrator.migrate_file(args.file, dry_run=args.dry_run)

            if args.dry_run:
                print(f"🔍 Dry-run migration for {args.file}:")
            else:
                print(f"✅ Migrated {args.file}:")

            print(f"  - Elements modified: {summary['elements_modified']}")
            print(f"  - IDs added: {summary['ids_added']}")
            print(f"  - IDs preserved: {summary['ids_preserved']}")

            return 0

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
