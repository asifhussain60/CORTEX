"""Phase M4-a RED tests for LENS streamline adapter retirement and preservation."""

from __future__ import annotations

import importlib

import pytest


def test_python_ast_analyzer_module_removed() -> None:
    """Python-specific AST analyzer module should be retired in M4-a."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("cortex.lens.analyzers.ast_analyzer")


def test_python_analyzer_module_removed() -> None:
    """Python-specific analyzer module should be retired in M4-a."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("cortex.lens.analyzers.python_analyzer")


def test_polyglot_adapters_preserved() -> None:
    """Polyglot adapters for enterprise stacks should remain importable."""
    module = importlib.import_module("cortex.lens.adapters")

    csharp_adapter = getattr(module, "CSharpAdapter")
    java_adapter = getattr(module, "JavaAdapter")
    typescript_adapter = getattr(module, "TypeScriptAdapter")
    javascript_adapter = getattr(module, "JavaScriptAdapter")

    assert csharp_adapter is not None
    assert java_adapter is not None
    assert typescript_adapter is not None
    assert javascript_adapter is not None
