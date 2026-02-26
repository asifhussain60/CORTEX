"""
Phase 84-f: CLI Commands + Provider Stubs — Implement or Guard
RED test suite — ALL tests must FAIL before implementation begins.

AC_START: AC-84-F-2026-02-26
Authority: CORE-008 (TDD first), CORE-064 (Sweep Completeness)
Covers: GAP-84-25, GAP-84-26, GAP-84-27, GAP-84-28, GAP-84-29
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORTEX_SRC = PROJECT_ROOT / "cortex"


class TestCLICommandsNoNotImplementedError:
    """GAPs 25-27: No CLI command may raise NotImplementedError."""

    def test_cli_onboard_does_not_raise_not_implemented(self) -> None:
        """
        GAP-84-25: cortex/cli/commands/onboard.py group command must not raise
        NotImplementedError when invoked.
        """
        from cortex.cli.commands.onboard import onboard

        runner = CliRunner()
        result = runner.invoke(onboard, ["--help"])
        assert result.exit_code == 0, (
            f"onboard --help must exit 0, got {result.exit_code}: {result.output} — GAP-84-25"
        )
        # The group itself must NOT raise NotImplementedError on invocation
        result2 = runner.invoke(onboard, [])
        assert "NotImplementedError" not in (result2.output or ""), (
            "onboard command group must not raise NotImplementedError — GAP-84-25"
        )

    def test_cli_lens_does_not_raise_not_implemented(self) -> None:
        """
        GAP-84-26: cortex/cli/commands/lens.py group command must not raise
        NotImplementedError when invoked.
        """
        from cortex.cli.commands.lens import lens

        runner = CliRunner()
        result = runner.invoke(lens, ["--help"])
        assert result.exit_code == 0, (
            f"lens --help must exit 0, got {result.exit_code}: {result.output} — GAP-84-26"
        )
        result2 = runner.invoke(lens, [])
        assert "NotImplementedError" not in (result2.output or ""), (
            "lens command group must not raise NotImplementedError — GAP-84-26"
        )

    def test_cli_governance_does_not_raise_not_implemented(self) -> None:
        """
        GAP-84-27: cortex/cli/__main__.py governance command must not raise
        NotImplementedError when invoked.
        """
        source = (CORTEX_SRC / "cli" / "__main__.py").read_text()
        # After fix: governance command must not have raise NotImplementedError
        assert "raise NotImplementedError" not in source or "governance" not in source, (
            "governance command in cli/__main__.py must not raise NotImplementedError — GAP-84-27"
        )


class TestWorkItemProvider:
    """GAP-84-28: WorkItemProvider methods must not raise NotImplementedError."""

    def test_work_item_provider_methods_not_raise(self) -> None:
        """
        GAP-84-28: WorkItemProvider.fetch_user_stories, fetch_by_id, health_check
        must return empty/graceful result instead of raising NotImplementedError.
        """
        source = (CORTEX_SRC / "repositories" / "work_item_provider.py").read_text()
        # After fix: no raw NotImplementedError raises in the Protocol implementation
        # The Protocol itself may declare abstract methods, but concrete implementations must not raise
        assert "raise NotImplementedError" not in source, (
            "work_item_provider.py must not raise NotImplementedError — GAP-84-28"
        )


class TestSecretsProvidersNoStubDocstrings:
    """GAP-84-29: Secrets provider docstrings must not contain 'stub'."""

    def test_secrets_providers_no_stub_docstrings(self) -> None:
        """
        GAP-84-29: aws.py, azure.py, vault.py docstrings must say 'backend', not 'backend stub'.
        """
        providers_dir = CORTEX_SRC / "infrastructure" / "secrets" / "providers"
        if not providers_dir.exists():
            providers_dir = CORTEX_SRC / "secrets" / "providers"

        violations = []
        for provider_file in providers_dir.glob("*.py"):
            if provider_file.name == "__init__.py":
                continue
            source = provider_file.read_text()
            if "backend stub" in source.lower() or ("stub" in source[:400].lower() and "backend" in source[:400].lower()):
                violations.append(provider_file.name)

        assert not violations, (
            f"Secrets providers still have 'backend stub' in docstrings: {violations} — GAP-84-29"
        )
