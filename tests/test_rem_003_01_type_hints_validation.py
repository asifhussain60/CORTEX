"""
tests/test_rem_003_01_type_hints_validation.py

Tests for AC-FIX-TYPING-001: Type hints validation.

REMEDIATION-003-PHASE-A: Validates type hints across cortex modules.
"""

import ast
import unittest
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class TestTypeHintsPresence(unittest.TestCase):
    """Tests for type hints presence in critical modules."""
    
    def get_function_signatures(self, filepath: Path) -> List[Tuple[str, bool]]:
        """Extract function names and whether they have return type hints.
        
        Args:
            filepath: Path to Python file
            
        Returns:
            List of (function_name, has_return_hint) tuples
        """
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        results = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                has_return = node.returns is not None
                results.append((node.name, has_return))
        return results
    
    def test_exceptions_module_has_type_hints(self) -> None:
        """cortex/common/exceptions.py should have type hints."""
        filepath = Path("cortex/common/exceptions.py")
        if not filepath.exists():
            self.skipTest("exceptions.py not found")
        
        funcs = self.get_function_signatures(filepath)
        # Filter out dunder methods
        public_funcs = [(n, h) for n, h in funcs if not n.startswith("_")]
        
        for name, has_return in public_funcs:
            with self.subTest(function=name):
                self.assertTrue(
                    has_return,
                    f"Function '{name}' missing return type hint"
                )
    
    def test_connection_utils_has_type_hints(self) -> None:
        """cortex/common/connection_utils.py should have type hints."""
        filepath = Path("cortex/common/connection_utils.py")
        if not filepath.exists():
            self.skipTest("connection_utils.py not found")
        
        funcs = self.get_function_signatures(filepath)
        public_funcs = [(n, h) for n, h in funcs if not n.startswith("_")]
        
        for name, has_return in public_funcs:
            with self.subTest(function=name):
                self.assertTrue(
                    has_return,
                    f"Function '{name}' missing return type hint"
                )
    
    def test_health_check_has_type_hints(self) -> None:
        """cortex/common/health_check.py should have type hints."""
        filepath = Path("cortex/common/health_check.py")
        if not filepath.exists():
            self.skipTest("health_check.py not found")
        
        funcs = self.get_function_signatures(filepath)
        public_funcs = [(n, h) for n, h in funcs if not n.startswith("_")]
        
        for name, has_return in public_funcs:
            with self.subTest(function=name):
                self.assertTrue(
                    has_return,
                    f"Function '{name}' missing return type hint"
                )
    
    def test_file_utils_has_type_hints(self) -> None:
        """cortex/common/file_utils.py should have type hints."""
        filepath = Path("cortex/common/file_utils.py")
        if not filepath.exists():
            self.skipTest("file_utils.py not found")
        
        funcs = self.get_function_signatures(filepath)
        public_funcs = [(n, h) for n, h in funcs if not n.startswith("_")]
        
        for name, has_return in public_funcs:
            with self.subTest(function=name):
                self.assertTrue(
                    has_return,
                    f"Function '{name}' missing return type hint"
                )
    
    def test_validators_has_type_hints(self) -> None:
        """cortex/common/validators.py should have type hints."""
        filepath = Path("cortex/common/validators.py")
        if not filepath.exists():
            self.skipTest("validators.py not found")
        
        funcs = self.get_function_signatures(filepath)
        public_funcs = [(n, h) for n, h in funcs if not n.startswith("_")]
        
        for name, has_return in public_funcs:
            with self.subTest(function=name):
                self.assertTrue(
                    has_return,
                    f"Function '{name}' missing return type hint"
                )


class TestTypeHintsForParameters(unittest.TestCase):
    """Tests for parameter type hints."""
    
    def get_functions_with_params(self, filepath: Path) -> List[Dict[str, Any]]:
        """Extract functions with their parameter info.
        
        Returns list of dicts with function name and param hint info.
        """
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        results = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip dunder methods
                if node.name.startswith("__"):
                    continue
                
                params_with_hints = []
                params_without_hints = []
                
                for arg in node.args.args:
                    if arg.arg in ("self", "cls"):
                        continue
                    if arg.annotation is not None:
                        params_with_hints.append(arg.arg)
                    else:
                        params_without_hints.append(arg.arg)
                
                results.append({
                    "name": node.name,
                    "with_hints": params_with_hints,
                    "without_hints": params_without_hints,
                })
        return results
    
    def test_validators_params_have_hints(self) -> None:
        """cortex/common/validators.py params should have hints."""
        filepath = Path("cortex/common/validators.py")
        if not filepath.exists():
            self.skipTest("validators.py not found")
        
        funcs = self.get_functions_with_params(filepath)
        
        for func in funcs:
            with self.subTest(function=func["name"]):
                self.assertEqual(
                    func["without_hints"],
                    [],
                    f"Function '{func['name']}' has params without hints: {func['without_hints']}"
                )


if __name__ == "__main__":
    unittest.main()
