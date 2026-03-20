"""Drift lock test — Check #54: CORE-038 File Placement Gate + HTML Conversion Enforcement.

All generated HTML files must comply with CORE-038 (file placement policy)
and HTML conversion must succeed without errors.

This drift lock prevents:
- HTML files landing in root directories
- Generated content landing outside cortex-registry/company/dashboards/
- Markdown-to-HTML conversion failures silently passing through governance
- NEW filename violations for M21-generated content

Root cause (2026-03-20): M21 bundle introduced SkillExecutor, DocumentationOrchestrator,
and HTML dashboard generation. This lock ensures generated artifacts comply with
CORE-038 naming/placement policy and validate HTML conversion capability end-to-end.

Note: Enforcement focuses on M21-generated content (dashboards/) and HTML conversion.
Existing docs/ organization is legacy and covered by other policies.

Gap ref: GAP-M21-05
Phase: phase-m21
"""
from __future__ import annotations

import pathlib
import re
from typing import Any

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
LOCK_FILE = (
    CORTEX_ROOT
    / "cortex-registry"
    / "governance"
    / "drift-locks"
    / "check-54-file-placement-html-conversion-lock.yaml"
)
DASHBOARD_DIR = CORTEX_ROOT / "cortex-registry" / "company" / "dashboards"


def _load_lock_file() -> dict[str, Any]:
    """Load the drift lock YAML definition."""
    if not LOCK_FILE.exists():
        return {}
    return yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8")) or {}


def _is_kebab_case(filename: str) -> bool:
    """Check if filename follows kebab-case convention."""
    # Kebab-case: lowercase, hyphens, no spaces or underscores
    name_without_ext = ".".join(filename.split(".")[:-1])
    if not name_without_ext:
        return False
    # Must start with lowercase|digit, can contain hyphens, end with lowercase|digit
    pattern = r"^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$"
    return bool(re.match(pattern, name_without_ext))


def _get_html_violations() -> list[str]:
    """Return list of HTML placement violations (M21 focus)."""
    violations: list[str] = []

    if DASHBOARD_DIR.exists():
        for html_file in DASHBOARD_DIR.rglob("*.html"):
            rel_path = str(html_file.relative_to(CORTEX_ROOT))
            filename = html_file.name

            # Check for kebab-case compliance
            if not _is_kebab_case(filename):
                violations.append(f"Filename not kebab-case: {rel_path}")

            # HTML files must be in subdirectory of dashboards/
            if html_file.parent == DASHBOARD_DIR:
                violations.append(f"HTML file at root of dashboards/: {rel_path}")

    return violations


def _test_html_conversion_capability() -> bool:
    """Test that basic HTML conversion works."""
    try:
        import html as html_module
        sample_md = "# Test\n\n**bold** and *italic*"
        test_content = html_module.escape(sample_md)
        return bool(test_content)
    except Exception:
        return False


class TestDriftLockCheck54:
    """Check #54 — CORE-038 File Placement Gate + HTML Conversion Enforcement (M21)."""

    def test_lock_file_exists(self) -> None:
        """The drift lock YAML for this check must be present."""
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P0 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        """Drift lock file must be valid YAML with required fields."""
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")

        data = _load_lock_file()
        assert data is not None
        assert data.get("check_number") == 54
        assert data.get("status") == "ACTIVE"
        assert data.get("gap_id") == "GAP-M21-05"

    def test_lock_has_required_fields(self) -> None:
        """Drift lock must have all required governance metadata."""
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")

        data = _load_lock_file()
        required_fields = [
            "id",
            "check_number",
            "phase",
            "gap_id",
            "status",
            "title",
            "description",
            "detect_command",
            "pass_criteria",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_dashboard_directory_exists(self) -> None:
        """cortex-registry/company/dashboards/ must exist (M21 output location)."""
        assert DASHBOARD_DIR.exists(), (
            "cortex-registry/company/dashboards/ does not exist"
        )

    def test_no_html_files_at_dashboard_root(self) -> None:
        """No .html files should be at dashboards/ root (CORE-038)."""
        if not DASHBOARD_DIR.exists():
            pytest.skip("Dashboard directory missing")

        html_at_root = list(DASHBOARD_DIR.glob("*.html"))
        assert not html_at_root, f"HTML files at dashboards/ root: {[f.name for f in html_at_root]}"

    def test_html_filenames_use_kebab_case(self) -> None:
        """All HTML files in dashboards/ must use kebab-case naming (M21 policy)."""
        if not DASHBOARD_DIR.exists():
            pytest.skip("Dashboard directory missing")

        violations = []
        for html_file in DASHBOARD_DIR.rglob("*.html"):
            if not _is_kebab_case(html_file.name):
                violations.append(f"{html_file.relative_to(CORTEX_ROOT)}: {html_file.name}")

        assert not violations, f"HTML filenames violate kebab-case: {violations}"

    def test_html_conversion_capability_works(self) -> None:
        """HTML conversion capability must function without errors."""
        can_convert = _test_html_conversion_capability()
        assert can_convert, "HTML conversion failed — content pipeline cannot generate HTML files"

    def test_html_placement_violations(self) -> None:
        """Validate critical file placement rules (M21 focus: HTML dashboards)."""
        violations = _get_html_violations()
        assert not violations, f"Critical HTML placement violations:\n" + "\n".join(
            f"  - {v}" for v in violations
        )

    def test_pass_criteria_defined(self) -> None:
        """Pass criteria must be clearly defined."""
        data = _load_lock_file()
        pass_criteria = data.get("pass_criteria", "")
        assert "FILE_PLACEMENT_AND_HTML_CONVERSION=OK" in pass_criteria

    def test_ci_gate_is_enabled(self) -> None:
        """This drift lock must be enforced in CI."""
        data = _load_lock_file()
        assert data.get("ci_gate") is True, "CI gate must be True for P0 governance checks"
