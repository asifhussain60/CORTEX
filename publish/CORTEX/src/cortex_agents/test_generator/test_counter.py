"""Test counting utilities."""

import ast


class TestCounter:
    """Counts test functions in generated code."""
    
    def count(self, test_code: str) -> int:
        """
        Count number of test functions in generated code.
        
        Args:
            test_code: Generated test code
        
        Returns:
            Number of test functions
        """
        try:
            tree = ast.parse(test_code)
            count = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        count += 1
            
            return count
        except:
            # Fallback: count lines with "def test_"
            return test_code.count('def test_')
