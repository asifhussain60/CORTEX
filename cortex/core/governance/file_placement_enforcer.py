"""CORE-038 File Placement Enforcer — validates file organization compliance.

Enforces CORTEX file placement policy:
- All files must be in appropriate subfolders
- Kebab-case naming convention required
- Root directories must be clean
- HTML generation validates content pipeline compliance

Gap ref: GAP-M21-05
Phase: phase-m21
"""
from __future__ import annotations

import pathlib
import re
from typing import Any


class FilePlacementEnforcer:
    """Validator for CORE-038 file placement policy compliance."""

    # Allowed root files
    ALLOWED_ROOT_FILES = {
        # Documentation
        "README.md",
        "ARCHITECTURE-RECOMMENDATION.md",
        "SECURITY.md",
        # Configuration
        "requirements.txt",
        "pytest.ini",
        "pyproject.toml",
        "Makefile",
        "CLAUDE.md",
        "conftest.py",
        # Build configuration
        ".gitignore",
        ".gitattributes",
        "mkdocs.yml",
        "pyrightconfig.json",
        "setup.py",
        # Cortex config
        "cortex-config.yaml",
        "cortex-impl-map.yaml",
    }

    # Root path categories that require subdirectories
    CATEGORIES_REQUIRING_SUBDIRS = {
        "docs": "All documentation must be in subdirectories (docs/{topic}/*.md)",
        "cortex-registry": "All registry content must be in subdirectories",
        "cortex": "All cortex modules must be organized (cortex/{module}/*.py)",
        "tests": "All tests must be organized (tests/{category}/*.py)",
        "scripts": "Scripts organization varies but prefer subdirs",
        "deployment": "Deployment files must be in subdirectories",
    }

    @staticmethod
    def _is_kebab_case(filename: str) -> bool:
        """Validate kebab-case naming convention.

        Format: lowercase letters/digits with hyphens, no spaces or underscores.
        Examples: valid-file.md, my-script.py, check-54-lock.yaml
        """
        # Split filename and extension
        if "." not in filename:
            name = filename
        else:
            name = ".".join(filename.split(".")[:-1])

        if not name:
            return False

        # Pattern: start with lowercase|digit, can contain hyphens, end with lowercase|digit
        pattern = r"^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$"
        return bool(re.match(pattern, name))

    @staticmethod
    def validate_root_files(root_path: pathlib.Path) -> dict[str, list[str]]:
        """Validate that root-level files are in allowed list.

        Args:
            root_path: Repository root directory

        Returns:
            Dict with violations and warning lists
        """
        violations = []
        warnings = []

        if not root_path.exists():
            return {"violations": [], "warnings": ["Root path does not exist"]}

        for item in root_path.glob("*"):
            if not item.is_file():
                continue

            filename = item.name

            # Skip hidden files
            if filename.startswith("."):
                continue

            # Check if allowed
            if filename not in FilePlacementEnforcer.ALLOWED_ROOT_FILES:
                violations.append(
                    f"File at root violates CORE-038: {filename} (must be in subdirectory)"
                )

            # Check kebab-case
            if not FilePlacementEnforcer._is_kebab_case(filename):
                warnings.append(f"Filename not kebab-case: {filename}")

        return {"violations": violations, "warnings": warnings}

    @staticmethod
    def validate_directory_structure(
        root_path: pathlib.Path, category: str
    ) -> dict[str, list[str]]:
        """Validate organization within a category directory.

        Args:
            root_path: Repository root
            category: Category name (e.g., 'docs', 'cortex')

        Returns:
            Dict with violations and warning lists
        """
        violations = []
        category_path = root_path / category

        if not category_path.exists():
            return {"violations": [], "warnings": []}

        # Check for files at category root
        root_files = list(category_path.glob("*.py")) + list(category_path.glob("*.md"))

        # Some categories allow root files
        if category in ("docs", "cortex-registry"):
            for f in root_files:
                if f.name not in {"README.md", "SECURITY.md"}:
                    violations.append(
                        f"File at {category}/ root violates CORE-038: {f.name}"
                    )

        # Check all filenames for kebab-case
        for item in category_path.rglob("*"):
            if item.is_file():
                if not FilePlacementEnforcer._is_kebab_case(item.name):
                    rel = item.relative_to(root_path)
                    violations.append(f"Non-kebab-case filename: {rel}")

        return {"violations": violations, "warnings": []}

    @staticmethod
    def validate_html_output(
        root_path: pathlib.Path,
    ) -> dict[str, list[str]]:
        """Validate HTML files follow placement rules.

        Args:
            root_path: Repository root

        Returns:
            Dict with violations
        """
        violations = []
        dashboard_dir = root_path / "cortex-registry" / "company" / "dashboards"

        if not dashboard_dir.exists():
            return {"violations": [], "warnings": ["Dashboard directory not found"]}

        # Check for HTML files at root
        root_html = list(dashboard_dir.glob("*.html"))
        for f in root_html:
            violations.append(
                f"HTML file at dashboards/ root violates CORE-038: {f.name}"
            )

        # Check all HTML files use kebab-case
        for html_file in dashboard_dir.rglob("*.html"):
            if not FilePlacementEnforcer._is_kebab_case(html_file.name):
                rel = html_file.relative_to(root_path)
                violations.append(f"HTML filename not kebab-case: {rel}")

        return {"violations": violations, "warnings": []}

    @staticmethod
    def validate_all(root_path: pathlib.Path | None = None) -> dict[str, Any]:
        """Run comprehensive file placement validation.

        Args:
            root_path: Repository root (defaults to cwd)

        Returns:
            Consolidated validation result
        """
        if root_path is None:
            root_path = pathlib.Path.cwd()

        root_path = root_path.resolve()

        results = {
            "timestamp": None,
            "compliance": True,
            "categories": {},
            "html_output": {},
            "summary": None,
        }

        # Validate root files
        root_result = FilePlacementEnforcer.validate_root_files(root_path)
        if root_result["violations"]:
            results["compliance"] = False
        results["categories"]["root"] = root_result

        # Validate category directories
        for category in ["docs", "cortex", "cortex-registry", "tests", "deployment"]:
            cat_result = FilePlacementEnforcer.validate_directory_structure(
                root_path, category
            )
            if cat_result["violations"]:
                results["compliance"] = False
            results["categories"][category] = cat_result

        # Validate HTML output
        html_result = FilePlacementEnforcer.validate_html_output(root_path)
        if html_result["violations"]:
            results["compliance"] = False
        results["html_output"] = html_result

        # Summary
        total_violations = sum(
            len(cat.get("violations", []))
            for cat in results["categories"].values()
        ) + len(html_result.get("violations", []))

        results["summary"] = (
            f"CORE-038 Compliance: {'✅ PASS' if results['compliance'] else '❌ FAIL'} "
            f"({total_violations} violations)"
        )

        return results
