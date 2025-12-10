"""
Implementation Engine for TDD Orchestrator (GREEN Phase)
Generates minimal implementation to pass tests (YAGNI principle)

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any, List
import logging
import ast
import inspect

logger = logging.getLogger(__name__)


class ImplementationEngine:
    """
    Generates minimal implementation for GREEN phase.
    
    Features:
    - Minimal code generation (YAGNI)
    - Over-engineering detection
    - AST-based code insertion
    - Test-to-implementation mapping
    """
    
    def __init__(self):
        """Initialize implementation engine."""
        self.logger = logging.getLogger(f"{__name__}.ImplementationEngine")
    
    def generate_minimal_implementation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate minimal implementation to pass tests.
        
        Args:
            context: Tests and configuration
        
        Returns:
            Dict with success, complexity, implementation_content
        """
        try:
            tests = context.get('tests', [])
            config = context.get('config', {})
            
            self.logger.info(f"Generating implementation for {len(tests)} tests")
            
            # Analyze tests to determine minimal requirements
            requirements = self._analyze_test_requirements(tests)
            
            # Generate minimal code
            implementation = self._generate_code(requirements, config)
            
            # Check complexity
            complexity = self._calculate_complexity(implementation)
            
            return {
                'success': True,
                'complexity': complexity,
                'implementation_content': implementation,
                'lines_of_code': len(implementation.split('\n'))
            }
        
        except Exception as e:
            self.logger.error(f"Implementation generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def detect_over_engineering(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect over-engineering violations (YAGNI).
        
        Args:
            context: Code and test count
        
        Returns:
            Dict with over_engineering flag and violations
        """
        code = context.get('code', '')
        test_count = context.get('test_count', 0)
        
        violations = []
        
        # Check lines of code vs test count ratio
        loc = len(code.split('\n'))
        if loc > test_count * 10:
            violations.append(f"Too much code for {test_count} tests ({loc} LOC)")
        
        # Check for premature abstractions
        if 'class Factory' in code or 'class Builder' in code:
            violations.append("Premature abstraction patterns detected")
        
        # Check for unused code
        tree = ast.parse(code)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if len(functions) > test_count:
            violations.append(f"More functions ({len(functions)}) than tests ({test_count})")
        
        over_engineering = len(violations) > 0
        
        return {
            'over_engineering': over_engineering,
            'violations': violations,
            'loc': loc,
            'test_count': test_count
        }
    
    def insert_code_via_ast(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert code using AST manipulation.
        
        Args:
            context: Target file, code, position
        
        Returns:
            Dict with inserted flag
        """
        target_file = context.get('target_file', '')
        code = context.get('code', '')
        position = context.get('position', 'end')
        
        try:
            # Mock AST insertion (real implementation would modify file)
            self.logger.info(f"Inserting code at {position} in {target_file}")
            
            return {
                'inserted': True,
                'target_file': target_file,
                'position': position
            }
        
        except Exception as e:
            self.logger.error(f"AST insertion failed: {e}")
            return {'inserted': False, 'error': str(e)}
    
    def map_tests_to_implementation(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Map test functions to implementation functions.
        
        Args:
            context: Tests and implementation file
        
        Returns:
            Dict mapping test names to function names
        """
        tests = context.get('tests', [])
        implementation = context.get('implementation', '')
        
        mapping = {}
        
        for test in tests:
            # Extract function name from test name (test_login -> login)
            if test.startswith('test_'):
                func_name = test[5:]  # Remove 'test_' prefix
                mapping[test] = func_name
        
        return mapping
    
    def _analyze_test_requirements(self, tests: List[str]) -> Dict[str, Any]:
        """Analyze what tests require from implementation."""
        requirements = {
            'functions': set(),
            'return_types': {},
            'parameters': {}
        }
        
        # Simple heuristic: test_X requires function X
        for test in tests:
            if test.startswith('test_'):
                func_name = test[5:]
                requirements['functions'].add(func_name)
        
        return requirements
    
    def _generate_code(self, requirements: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate minimal implementation code."""
        lines = ['"""', 'Generated implementation', '"""', '']
        
        complexity = config.get('complexity', 'low')
        
        for func in requirements['functions']:
            if complexity == 'low':
                lines.append(f'def {func}():')
                lines.append('    """Minimal implementation."""')
                lines.append('    pass')
            elif complexity == 'medium':
                lines.append(f'def {func}(data):')
                lines.append('    """Minimal implementation with parameter."""')
                lines.append('    return data')
            else:
                lines.append(f'class {func.capitalize()}:')
                lines.append('    """Minimal implementation as class."""')
                lines.append('    def execute(self):')
                lines.append('        pass')
            
            lines.append('')
        
        return '\n'.join(lines)
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity."""
        try:
            tree = ast.parse(code)
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                    complexity += 1
            
            return complexity
        
        except:
            return 0
