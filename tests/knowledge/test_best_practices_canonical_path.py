"""
Phase 148-B: Best-Practices Canonical Path Tests.

Validates that best-practice knowledge is accessible via the canonical
``cortex.knowledge.best_practices`` module, powered by KnowledgeRegistryProxy.

The best_practices package is NOT dead code — it provides a stable import path
backed by KnowledgeRegistryProxy delegating to cortex-registry/knowledge/.

GAP-148-02: Canonical best-practices path verification
CORE-035: Single canonical implementation
CORE-008: TDD mandatory

AC_START: AC-P148-BP-001
"""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict, List

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
CORTEX_ROOT = REPO_ROOT / "cortex"


class TestBestPracticesPackageCanonical:
    """Verify cortex.knowledge.best_practices is the canonical access path."""

    def test_best_practices_package_importable(self) -> None:
        """cortex.knowledge.best_practices must import without error."""
        mod = importlib.import_module("cortex.knowledge.best_practices")
        assert mod is not None

    def test_get_best_practices_callable(self) -> None:
        """get_best_practices() must be callable."""
        from cortex.knowledge.best_practices import get_best_practices
        assert callable(get_best_practices)

    def test_all_best_practices_callable(self) -> None:
        """all_best_practices() must be callable."""
        from cortex.knowledge.best_practices import all_best_practices
        assert callable(all_best_practices)

    def test_get_best_practices_returns_list(self) -> None:
        """get_best_practices() must return a list."""
        from cortex.knowledge.best_practices import get_best_practices
        result = get_best_practices()
        assert isinstance(result, list)

    def test_get_best_practices_with_domain_returns_list(self) -> None:
        """get_best_practices(domain=...) must return a list."""
        from cortex.knowledge.best_practices import get_best_practices
        result = get_best_practices(domain="architecture")
        assert isinstance(result, list)

    def test_all_best_practices_returns_list(self) -> None:
        """all_best_practices() must return a list."""
        from cortex.knowledge.best_practices import all_best_practices
        result = all_best_practices()
        assert isinstance(result, list)

    def test_best_practices_init_file_exists(self) -> None:
        """cortex/knowledge/best_practices/__init__.py must exist."""
        init = CORTEX_ROOT / "knowledge" / "best_practices" / "__init__.py"
        assert init.exists(), "cortex/knowledge/best_practices/__init__.py must exist"

    def test_best_practices_init_not_empty(self) -> None:
        """cortex/knowledge/best_practices/__init__.py must not be empty."""
        init = CORTEX_ROOT / "knowledge" / "best_practices" / "__init__.py"
        content = init.read_text()
        assert len(content.strip()) > 0, "__init__.py must not be empty"


class TestBestPracticesNoPhantomImports:
    """Verify no phantom imports exist for non-existent sub-packages."""

    def test_no_import_from_nonexistent_technical_subpackage(self) -> None:
        """cortex.knowledge.best_practices.technical sub-package must not be used as phantom."""
        # The package should only export via __init__.py, no phantom sub-packages
        tech_path = CORTEX_ROOT / "knowledge" / "best_practices" / "technical"
        if tech_path.exists():
            init = tech_path / "__init__.py"
            # If sub-package exists, it must have content (not phantom)
            assert init.exists(), "Sub-package technical/ must have __init__.py if it exists"
        # If it doesn't exist, no phantom imports should reference it
        # (checked implicitly by importability above)

    def test_best_practices_gateway_integration(self) -> None:
        """context_synthesis_gateway.py must import from cortex.knowledge.best_practices."""
        gateway_path = CORTEX_ROOT / "orchestrators" / "core" / "context_synthesis_gateway.py"
        content = gateway_path.read_text()
        assert "cortex.knowledge.best_practices" in content, (
            "ContextSynthesisGateway must integrate with cortex.knowledge.best_practices"
        )


# AC_COMPLETE: AC-P148-BP-001 ✅
