"""Phase M4-b tests for unified ILensAdapter protocol adoption."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def test_ilens_adapter_protocol_contract() -> None:
    """ILensAdapter defines analyze/get_context/supports methods."""
    from cortex.lens.adapters.i_lens_adapter import ILensAdapter

    for method_name in ("analyze", "get_context", "supports"):
        assert hasattr(ILensAdapter, method_name)


def test_language_adapter_exposes_ilens_methods() -> None:
    """LanguageAdapter should expose default ILensAdapter behavior."""
    from cortex.lens.adapters.language_adapter import LanguageAdapter

    for method_name in ("analyze", "get_context", "supports"):
        assert callable(getattr(LanguageAdapter, method_name, None))


def test_polyglot_adapter_classes_inherit_language_adapter() -> None:
    """Surviving polyglot adapters should inherit LanguageAdapter."""
    from cortex.lens.adapters.language_adapter import LanguageAdapter
    from cortex.lens.adapters.csharp_adapter import CSharpAdapter
    from cortex.lens.adapters.java_adapter import JavaAdapter
    from cortex.lens.adapters.javascript_adapter import JavaScriptAdapter
    from cortex.lens.adapters.typescript_adapter import TypeScriptAdapter

    for adapter_cls in (CSharpAdapter, JavaAdapter, JavaScriptAdapter, TypeScriptAdapter):
        assert issubclass(adapter_cls, LanguageAdapter)


def test_supports_alias_matches_supports_file() -> None:
    """supports() should match supports_file() behavior on adapters."""
    from cortex.lens.adapters.java_adapter import JavaAdapter

    adapter = JavaAdapter()
    java_path = Path("Example.java")
    py_path = Path("Example.py")

    assert adapter.supports(java_path) is adapter.supports_file(java_path)
    assert adapter.supports(py_path) is adapter.supports_file(py_path)


def test_get_context_returns_required_keys() -> None:
    """get_context() should return a normalized context envelope."""
    from cortex.lens.adapters.java_adapter import JavaAdapter

    adapter = JavaAdapter()
    context: dict[str, Any] = adapter.get_context(Path("sample.java"))

    assert context["language"]
    assert "supports" in context
    assert context["file_path"].endswith("sample.java")
