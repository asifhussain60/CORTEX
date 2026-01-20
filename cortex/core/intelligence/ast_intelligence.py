"""AST Intelligence - Abstract Syntax Tree analysis for code comprehension.

Analyzes Python code structures using AST parsing to extract semantic information,
identify patterns, and provide code intelligence.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import ast
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class ASTNode:
    """Analyzed AST node with semantic information.

    Attributes:
        type: Node type (function, class, import, etc).
        name: Node name.
        line_number: Source line number.
        docstring: Node docstring if present.
        metadata: Additional metadata dictionary.
    """

    type: str
    name: str
    line_number: int
    docstring: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}


class ASTIntelligence:
    """Abstract Syntax Tree analyzer for code intelligence."""

    def __init__(self, source_code: str) -> None:
        """Initialize AST analyzer.

        Args:
            source_code: Python source code to analyze.
        """
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        self.nodes: List[ASTNode] = []
        self._analyze()

    def _analyze(self) -> None:
        """Analyze the AST and extract nodes."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self.nodes.append(
                    ASTNode(
                        type="function",
                        name=node.name,
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node),
                    )
                )
            elif isinstance(node, ast.ClassDef):
                self.nodes.append(
                    ASTNode(
                        type="class",
                        name=node.name,
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node),
                    )
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.nodes.append(
                        ASTNode(
                            type="import",
                            name=alias.name,
                            line_number=node.lineno,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    self.nodes.append(
                        ASTNode(
                            type="from_import",
                            name=f"{module}.{alias.name}",
                            line_number=node.lineno,
                        )
                    )

    def get_functions(self) -> List[ASTNode]:
        """Get all functions in the code.

        Returns:
            List of function nodes.
        """
        return [n for n in self.nodes if n.type == "function"]

    def get_classes(self) -> List[ASTNode]:
        """Get all classes in the code.

        Returns:
            List of class nodes.
        """
        return [n for n in self.nodes if n.type == "class"]

    def get_imports(self) -> List[ASTNode]:
        """Get all imports in the code.

        Returns:
            List of import nodes.
        """
        return [n for n in self.nodes if n.type in ("import", "from_import")]

    def extract_dependencies(self) -> Set[str]:
        """Extract external dependencies.

        Returns:
            Set of imported module names.
        """
        dependencies = set()
        for node in self.get_imports():
            # Extract base module name
            parts = node.name.split(".")
            dependencies.add(parts[0])
        return dependencies

    def get_node_by_name(self, name: str) -> Optional[ASTNode]:
        """Get a node by name.

        Args:
            name: Node name.

        Returns:
            ASTNode or None if not found.
        """
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def get_complexity_score(self) -> float:
        """Calculate cyclomatic complexity score.

        Returns:
            Complexity score (0-100).
        """
        complexity = 1
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
        # Normalize to 0-100
        return min(100, complexity * 5)


__all__ = [
    "ASTIntelligence",
    "ASTNode",
]
