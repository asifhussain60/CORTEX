"""
tests/test_rem_003_02_docstrings_validation.py

Tests for AC-FIX-DOCSTRINGS-001: Docstrings validation.

REMEDIATION-003-PHASE-B: Validates docstrings across cortex modules.
"""

import ast
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple


class TestDocstringsPresence(unittest.TestCase):
    """Tests for docstrings presence in critical modules."""
    
    def get_definitions_with_docstrings(
        self, filepath: Path
    ) -> List[Tuple[str, str, bool]]:
        """Extract class/function names and docstring status.
        
        Args:
            filepath: Path to Python file
            
        Returns:
            List of (type, name, has_docstring) tuples
        """
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        results = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                has_doc = ast.get_docstring(node) is not None
                results.append(("class", node.name, has_doc))
                # Check methods in class
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if child.name.startswith("_") and not child.name.startswith("__"):
                            continue
                        has_doc = ast.get_docstring(child) is not None
                        results.append(("method", child.name, has_doc))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private functions and nested wrappers
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue
                if node.name in ("wrapper", "decorator"):
                    continue
                has_doc = ast.get_docstring(node) is not None
                results.append(("function", node.name, has_doc))
        return results
    
    def test_exceptions_module_has_docstrings(self) -> None:
        """cortex/common/exceptions.py should have docstrings."""
        filepath = Path("cortex/common/exceptions.py")
        if not filepath.exists():
            self.skipTest("exceptions.py not found")
        
        defs = self.get_definitions_with_docstrings(filepath)
        
        for def_type, name, has_doc in defs:
            with self.subTest(type=def_type, name=name):
                self.assertTrue(
                    has_doc,
                    f"{def_type} '{name}' missing docstring"
                )
    
    def test_connection_utils_has_docstrings(self) -> None:
        """cortex/common/connection_utils.py should have docstrings."""
        filepath = Path("cortex/common/connection_utils.py")
        if not filepath.exists():
            self.skipTest("connection_utils.py not found")
        
        defs = self.get_definitions_with_docstrings(filepath)
        
        for def_type, name, has_doc in defs:
            with self.subTest(type=def_type, name=name):
                self.assertTrue(
                    has_doc,
                    f"{def_type} '{name}' missing docstring"
                )
    
    def test_health_check_has_docstrings(self) -> None:
        """cortex/common/health_check.py should have docstrings."""
        filepath = Path("cortex/common/health_check.py")
        if not filepath.exists():
            self.skipTest("health_check.py not found")
        
        defs = self.get_definitions_with_docstrings(filepath)
        
        for def_type, name, has_doc in defs:
            with self.subTest(type=def_type, name=name):
                self.assertTrue(
                    has_doc,
                    f"{def_type} '{name}' missing docstring"
                )
    
    def test_file_utils_has_docstrings(self) -> None:
        """cortex/common/file_utils.py should have docstrings."""
        filepath = Path("cortex/common/file_utils.py")
        if not filepath.exists():
            self.skipTest("file_utils.py not found")
        
        defs = self.get_definitions_with_docstrings(filepath)
        
        for def_type, name, has_doc in defs:
            with self.subTest(type=def_type, name=name):
                self.assertTrue(
                    has_doc,
                    f"{def_type} '{name}' missing docstring"
                )
    
    def test_validators_has_docstrings(self) -> None:
        """cortex/common/validators.py should have docstrings."""
        filepath = Path("cortex/common/validators.py")
        if not filepath.exists():
            self.skipTest("validators.py not found")
        
        defs = self.get_definitions_with_docstrings(filepath)
        
        for def_type, name, has_doc in defs:
            with self.subTest(type=def_type, name=name):
                self.assertTrue(
                    has_doc,
                    f"{def_type} '{name}' missing docstring"
                )


class TestDocstringsQuality(unittest.TestCase):
    """Tests for docstring quality (Args, Returns sections)."""
    
    def get_function_docstrings(self, filepath: Path) -> Dict[str, str]:
        """Extract function docstrings."""
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        results = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue
                doc = ast.get_docstring(node)
                if doc:
                    results[node.name] = doc
        return results
    
    def test_validators_docstrings_have_args(self) -> None:
        """Public functions with params should document Args."""
        filepath = Path("cortex/common/validators.py")
        if not filepath.exists():
            self.skipTest("validators.py not found")
        
        docs = self.get_function_docstrings(filepath)
        
        # Check that functions with args have Args section
        for name, doc in docs.items():
            if name in ("required", "type_check", "range_check", "regex_match", "validate_schema"):
                with self.subTest(function=name):
                    self.assertIn(
                        "Args:",
                        doc,
                        f"Function '{name}' missing Args section in docstring"
                    )
    
    def test_validators_docstrings_have_returns(self) -> None:
        """Functions with return values should document Returns."""
        filepath = Path("cortex/common/validators.py")
        if not filepath.exists():
            self.skipTest("validators.py not found")
        
        docs = self.get_function_docstrings(filepath)
        
        for name, doc in docs.items():
            if name in ("required", "type_check", "range_check", "regex_match", "validate_schema"):
                with self.subTest(function=name):
                    self.assertIn(
                        "Returns:",
                        doc,
                        f"Function '{name}' missing Returns section in docstring"
                    )


if __name__ == "__main__":
    unittest.main()
