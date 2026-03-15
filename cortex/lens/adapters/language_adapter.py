"""
LanguageAdapter abstract base class for multi-language AST parsing.

Defines the contract that all language-specific adapters must implement
(CSharpAdapter, JavaAdapter, TypeScriptAdapter, JavaScriptAdapter, PythonAdapter).

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from cortex.lens.adapters.i_lens_adapter import ILensAdapter


class LanguageAdapter(ABC, ILensAdapter):  # CORE-035-scoped — domain-specific variant
    """
    Abstract base class for language-specific AST parsers.

    All language adapters (CSharpAdapter, JavaAdapter, etc.) must implement:
    - parse_file(): Parse source code and return PolyglotASTResult
    - get_supported_extensions(): Return list of file extensions (e.g., [".py", ".pyi"])
    - get_language_name(): Return human-readable language name (e.g., "Python")

    Usage:
        class PythonAdapter(LanguageAdapter):
            def parse_file(self, file_path: Path) -> PolyglotASTResult:
                # Parse Python file using tree-sitter or ast module
                ...

            def get_supported_extensions(self) -> List[str]:
                return [".py", ".pyi"]

            def get_language_name(self) -> str:
                return "Python"

    Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
    """

    @abstractmethod
    def parse_file(self, file_path: Path) -> None:
        """
        Parse a source file and return unified AST result.

        Args:
            file_path: Path to source file to parse

        Returns:
            PolyglotASTResult containing classes, functions, imports

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file has syntax errors
            ValueError: If file extension not supported
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Return list of file extensions this adapter supports.

        Returns:
            List of extensions with leading dot (e.g., [".py", ".pyi"])

        Example:
            Python: [".py", ".pyi"]
            C#: [".cs"]
            Java: [".java"]
            TypeScript: [".ts", ".tsx"]
            JavaScript: [".js", ".jsx"]
        """
        pass

    @abstractmethod
    def get_language_name(self) -> str:
        """
        Return human-readable language name.

        Returns:
            Language name (e.g., "Python", "C#", "Java")

        Example:
            "Python", "C#", "Java", "TypeScript", "JavaScript"
        """
        pass

    def supports_file(self, file_path: Path) -> bool:
        """
        Check if this adapter supports the given file.

        Args:
            file_path: Path to file to check

        Returns:
            True if file extension is supported, False otherwise

        Example:
            >>> adapter = PythonAdapter()
            >>> adapter.supports_file(Path("test.py"))
            True
            >>> adapter.supports_file(Path("test.java"))
            False
        """
        file_ext = file_path.suffix.lower()
        supported = [ext.lower() for ext in self.get_supported_extensions()]
        return file_ext in supported

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze source file through adapter parse path and normalize payload."""
        result = self.parse_file(file_path)
        payload: Dict[str, Any]
        if hasattr(result, "to_dict"):
            payload = result.to_dict()  # type: ignore[assignment]
        elif isinstance(result, dict):
            payload = result
        else:
            payload = {"result": result}

        payload.setdefault("language", self.get_language_name())
        payload.setdefault("file_path", str(file_path))
        return payload

    def get_context(self, file_path: Path) -> Dict[str, Any]:
        """Return context envelope for orchestration-level routing."""
        return {
            "language": self.get_language_name(),
            "supports": self.supports(file_path),
            "file_path": str(file_path),
        }

    def supports(self, file_path: Path) -> bool:
        """Canonical support predicate required by ILensAdapter."""
        return self.supports_file(file_path)
