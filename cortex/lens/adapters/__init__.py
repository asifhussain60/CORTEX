"""
Language adapters for multi-language AST parsing.

This package contains the abstract LanguageAdapter base class and concrete
implementations for each supported language.

Phase 0: LanguageAdapter ABC
Phase 1: CSharpAdapter (COMPLETE ✅)
Phase 3: JavaAdapter (COMPLETE ✅)
Phase 4: TypeScriptAdapter, JavaScriptAdapter (PLANNED)

Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml
"""

from cortex.lens.adapters.language_adapter import LanguageAdapter

__all__ = ["LanguageAdapter", "CSharpAdapter", "JavaAdapter"]


def __getattr__(name: str):
    """Lazy import adapters to prevent circular dependencies."""
    if name == "CSharpAdapter":
        from cortex.lens.adapters.csharp_adapter import CSharpAdapter
        return CSharpAdapter
    elif name == "JavaAdapter":
        from cortex.lens.adapters.java_adapter import JavaAdapter
        return JavaAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
