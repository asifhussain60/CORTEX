"""Canonical AST intelligence adapter.

Phase M3 retires the Python-specific AST wrapper under
`cortex/intelligence/analysis/ast_intelligence.py`.
This module remains the stable import path and provides a compact
AST adapter used by legacy callers.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class ParameterInfo:
	"""Function parameter metadata."""

	name: str
	type_hint: Optional[str] = None
	default: Optional[str] = None

	def to_dict(self) -> Dict[str, Any]:
		"""Serialize parameter metadata."""
		return {
			"name": self.name,
			"type_hint": self.type_hint,
			"default": self.default,
		}


@dataclass
class FunctionInfo:
	"""Function/method metadata used by downstream analyzers."""

	name: str
	parameters: List[ParameterInfo] = field(default_factory=list)
	return_type: Optional[str] = None
	docstring: Optional[str] = None
	line_number: int = 0
	decorators: List[str] = field(default_factory=list)
	is_async: bool = False
	is_method: bool = False
	class_name: Optional[str] = None

	def to_dict(self) -> Dict[str, Any]:
		"""Serialize function metadata."""
		return {
			"name": self.name,
			"parameters": [p.to_dict() for p in self.parameters],
			"return_type": self.return_type,
			"docstring": self.docstring,
			"line_number": self.line_number,
			"decorators": self.decorators,
			"is_async": self.is_async,
			"is_method": self.is_method,
			"class_name": self.class_name,
		}


@dataclass
class ClassInfo:
	"""Class metadata used by pattern/call-graph components."""

	name: str
	bases: List[str] = field(default_factory=list)
	methods: List[FunctionInfo] = field(default_factory=list)
	class_variables: List[str] = field(default_factory=list)
	docstring: Optional[str] = None
	line_number: int = 0
	decorators: List[str] = field(default_factory=list)

	def to_dict(self) -> Dict[str, Any]:
		"""Serialize class metadata."""
		return {
			"name": self.name,
			"bases": self.bases,
			"methods": [m.to_dict() for m in self.methods],
			"class_variables": self.class_variables,
			"docstring": self.docstring,
			"line_number": self.line_number,
			"decorators": self.decorators,
		}


@dataclass
class ConstantInfo:
	"""Module-level constant metadata."""

	name: str
	value: str
	line_number: int = 0


@dataclass
class ParseResult:
	"""AST parse output contract for legacy consumers."""

	success: bool
	ast_tree: Optional[ast.Module] = None
	module_docstring: Optional[str] = None
	imports: Set[str] = field(default_factory=set)
	from_imports: Dict[str, List[str]] = field(default_factory=dict)
	functions: List[FunctionInfo] = field(default_factory=list)
	classes: List[ClassInfo] = field(default_factory=list)
	constants: List[ConstantInfo] = field(default_factory=list)
	error: Optional[str] = None
	error_line: Optional[int] = None
	error_column: Optional[int] = None
	source_path: Optional[Path] = None

	def to_dict(self) -> Dict[str, Any]:
		"""Serialize parse result for MCP/tool payloads."""
		return {
			"success": self.success,
			"module_docstring": self.module_docstring,
			"imports": sorted(self.imports),
			"from_imports": self.from_imports,
			"functions": [f.to_dict() for f in self.functions],
			"classes": [c.to_dict() for c in self.classes],
			"constants": [
				{
					"name": c.name,
					"value": c.value,
					"line_number": c.line_number,
				}
				for c in self.constants
			],
			"error": self.error,
			"error_line": self.error_line,
			"error_column": self.error_column,
		}


class ASTIntelligenceEngine:
	"""Lightweight AST parsing engine for compatibility consumers."""

	def __init__(self, enable_cache: bool = True) -> None:
		"""Initialize parser engine.

		Args:
			enable_cache: Enable in-memory content cache.
		"""
		self.enable_cache = enable_cache
		self._cache: Dict[str, ParseResult] = {}

	def parse_file(self, file_path: Path) -> ParseResult:
		"""Parse a Python file.

		Args:
			file_path: File to parse.

		Returns:
			Parse result payload.
		"""
		if not file_path.exists():
			return ParseResult(success=False, error=f"File not found: {file_path}")

		source = file_path.read_text(encoding="utf-8", errors="replace")
		if "\x00" in source:
			return ParseResult(success=False, error=f"Binary or non-text file: {file_path}")
		cache_key = f"{file_path}:{hash(source)}"
		if self.enable_cache and cache_key in self._cache:
			return self._cache[cache_key]

		result = self.parse_string(source)
		result.source_path = file_path
		if self.enable_cache:
			self._cache[cache_key] = result
		return result

	def parse_string(self, source_code: str) -> ParseResult:
		"""Parse raw Python source.

		Args:
			source_code: Python code string.

		Returns:
			Parse result payload.
		"""
		try:
			tree = ast.parse(source_code)
		except SyntaxError as exc:
			return ParseResult(
				success=False,
				error=str(exc),
				error_line=exc.lineno,
				error_column=exc.offset,
			)
		except ValueError as exc:
			return ParseResult(success=False, error=str(exc))

		result = ParseResult(success=True, ast_tree=tree, module_docstring=ast.get_docstring(tree))

		for node in tree.body:
			if isinstance(node, ast.Import):
				for alias in node.names:
					result.imports.add(alias.name)
			elif isinstance(node, ast.ImportFrom):
				if node.module:
					names = [alias.name for alias in node.names]
					result.from_imports[node.module] = names
					result.imports.add(node.module)
			elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
				result.functions.append(self._extract_function(node))
			elif isinstance(node, ast.ClassDef):
				result.classes.append(self._extract_class(node))
			elif isinstance(node, ast.Assign):
				for target in node.targets:
					if isinstance(target, ast.Name) and target.id.isupper():
						value_repr = ast.unparse(node.value) if hasattr(ast, "unparse") else str(node.value)
						result.constants.append(
							ConstantInfo(name=target.id, value=value_repr, line_number=node.lineno)
						)

		return result

	def _extract_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
		"""Extract function metadata from AST node."""
		parameters: List[ParameterInfo] = []
		defaults = list(node.args.defaults)
		default_start_index = len(node.args.args) - len(defaults)
		for index, arg in enumerate(node.args.args):
			type_hint = ast.unparse(arg.annotation) if arg.annotation is not None and hasattr(ast, "unparse") else None
			default_value: Optional[str] = None
			if index >= default_start_index and defaults and hasattr(ast, "unparse"):
				default_value = ast.unparse(defaults[index - default_start_index])
			parameters.append(ParameterInfo(name=arg.arg, type_hint=type_hint, default=default_value))

		decorators: List[str] = []
		for decorator in node.decorator_list:
			decorators.append(ast.unparse(decorator) if hasattr(ast, "unparse") else "decorator")

		return_type = ast.unparse(node.returns) if node.returns is not None and hasattr(ast, "unparse") else None

		return FunctionInfo(
			name=node.name,
			parameters=parameters,
			return_type=return_type,
			docstring=ast.get_docstring(node),
			line_number=node.lineno,
			decorators=decorators,
			is_async=isinstance(node, ast.AsyncFunctionDef),
		)

	def _extract_class(self, node: ast.ClassDef) -> ClassInfo:
		"""Extract class metadata from AST node."""
		bases: List[str] = []
		for base in node.bases:
			bases.append(ast.unparse(base) if hasattr(ast, "unparse") else "Base")

		methods: List[FunctionInfo] = []
		class_variables: List[str] = []
		for item in node.body:
			if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
				method = self._extract_function(item)
				method.is_method = True
				method.class_name = node.name
				methods.append(method)
			elif isinstance(item, ast.Assign):
				for target in item.targets:
					if isinstance(target, ast.Name):
						class_variables.append(target.id)

		decorators: List[str] = []
		for decorator in node.decorator_list:
			decorators.append(ast.unparse(decorator) if hasattr(ast, "unparse") else "decorator")

		return ClassInfo(
			name=node.name,
			bases=bases,
			methods=methods,
			class_variables=class_variables,
			docstring=ast.get_docstring(node),
			line_number=node.lineno,
			decorators=decorators,
		)


__all__ = [
	"ASTIntelligenceEngine",
	"ParseResult",
	"ParameterInfo",
	"FunctionInfo",
	"ClassInfo",
	"ConstantInfo",
]
