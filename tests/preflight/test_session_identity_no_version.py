# AC_START: AC-HARDENING-SESSION-IDENTITY-001
"""Preflight: Session Identity template must not render version numbers.

Validates that ``block-session-identity.yaml`` does not expose a version
number, semver string, or ``{version}`` template variable in user-facing
rendered output. CORTEX uses date-stamped governance — never semantic versioning.

Gap ref: GAP-126-05 (no-versioning-anywhere)
Drift lock: cortex-registry/governance/drift-locks/check-34-no-versioning-lock.yaml
Tier: T0 (preflight) — YAML parse only, no server startup, < 1 s
CORE rules: CORE-002 (no version artefacts), CORE-008 (TDD)
"""
from __future__ import annotations

import pathlib
import re

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
SESSION_IDENTITY_PATH = (
    CORTEX_ROOT
    / "cortex-registry"
    / "templates"
    / "response"
    / "blocks"
    / "block-session-identity.yaml"
)


class TestSessionIdentityNoVersion:
    """block-session-identity.yaml must not render version numbers to users."""

    def test_session_identity_file_exists(self) -> None:
        """The session identity template YAML must exist."""
        assert SESSION_IDENTITY_PATH.exists(), (
            f"block-session-identity.yaml not found at {SESSION_IDENTITY_PATH}"
        )

    def test_template_has_no_version_placeholder(self) -> None:
        """Template must not contain {version} placeholder variable."""
        content = SESSION_IDENTITY_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        template = data.get("template", "")
        assert "{version}" not in template, (
            "Session identity template renders {version} — violates no-versioning rule. "
            "Use date-stamped governance instead."
        )

    def test_template_renders_no_semver(self) -> None:
        """Template must not contain hardcoded semver strings (vX.Y.Z)."""
        content = SESSION_IDENTITY_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        template = data.get("template", "")
        semver_pattern = re.compile(r"v\d+\.\d+\.\d+")
        match = semver_pattern.search(template)
        assert match is None, (
            f"Session identity template contains semver '{match.group()}' — "
            "violates no-versioning rule."
        )

    def test_template_renders_no_v_prefix_version(self) -> None:
        """Template must not contain v{version} or similar version rendering."""
        content = SESSION_IDENTITY_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        template = data.get("template", "")
        assert "v{" not in template.lower(), (
            "Session identity template renders 'v{...}' — violates no-versioning rule."
        )

    def test_comments_do_not_reference_version_variable(self) -> None:
        """YAML comments should not reference {version} as an active template variable."""
        content = SESSION_IDENTITY_PATH.read_text(encoding="utf-8")
        # Check that {version} is not listed as a template variable in comments
        # (old comment format: "# {version} = CORTEX framework version")
        active_var_pattern = re.compile(
            r"^#\s*\{version\}\s*=", re.MULTILINE
        )
        match = active_var_pattern.search(content)
        assert match is None, (
            "Session identity YAML still documents {version} as an active template "
            "variable in comments. Remove it to prevent drift."
        )


# AC_COMPLETE: AC-HARDENING-SESSION-IDENTITY-001 ✅
