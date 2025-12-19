"""
Test Skeleton Generator - Auto-generate pytest templates for untested features

Generates:
- pytest test class structure
- Basic test methods (initialization, execute/process)
- Fixture suggestions
- Mock templates

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional


class TestSkeletonGenerator:
    """Generates pytest test skeletons for untested features"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / "tests"
    
    def generate_test_skeleton(self, feature_name: str, feature_path: str, 
                               methods: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Generate pytest test skeleton for a feature
        
        Args:
            feature_name: Name of orchestrator/agent (e.g., "PaymentOrchestrator")
            feature_path: Path to feature file (e.g., "src/operations/modules/payment_orchestrator.py")
            methods: List of public methods to test (optional, will extract if not provided)
        
        Returns:
            Dictionary with keys: test_code, test_path, fixtures
        """
        # Extract methods from source file if not provided
        if methods is None:
            methods = self._extract_public_methods(feature_path)
        
        # Determine test file path
        test_path = self._determine_test_path(feature_path)
        
        # Generate import statements
        imports = self._generate_imports(feature_name, feature_path)
        
        # Generate test class
        test_class = self._generate_test_class(feature_name, methods)
        
        # Generate fixtures
        fixtures = self._generate_fixtures(feature_name)
        
        # Combine into full test file
        test_code = self._assemble_test_file(imports, fixtures, test_class)
        
        return {
            "test_code": test_code,
            "test_path": str(test_path),
            "fixtures": fixtures,
            "feature_name": feature_name,
            "methods_tested": methods
        }
    
    def _extract_public_methods(self, feature_path: str) -> List[str]:
        """Extract public method names from source file using AST"""
        try:
            file_path = self.project_root / feature_path
            if not file_path.exists():
                return ["execute"]  # Default method
            
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            methods = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Skip private methods (start with _)
                            if not item.name.startswith('_'):
                                methods.append(item.name)
            
            return methods if methods else ["execute"]
        
        except Exception:
            return ["execute"]  # Fallback to default
    
    def _determine_test_path(self, feature_path: str) -> Path:
        """Determine where test file should be created"""
        # Convert src/operations/modules/payment_orchestrator.py
        # to tests/operations/modules/test_payment_orchestrator.py
        
        # Handle empty or invalid paths
        if not feature_path:
            return self.project_root / "tests" / "test_unknown.py"
        
        path = Path(feature_path)
        
        # Replace 'src' with 'tests'
        parts = list(path.parts)
        
        # Handle empty parts list
        if not parts:
            return self.project_root / "tests" / "test_unknown.py"
        
        if parts[0] == 'src':
            parts[0] = 'tests'
        
        # Add 'test_' prefix to filename
        filename = path.stem
        if not filename.startswith('test_'):
            filename = f"test_{filename}"
        
        parts[-1] = f"{filename}.py"
        
        return self.project_root / Path(*parts)
    
    def _generate_imports(self, feature_name: str, feature_path: str) -> str:
        """Generate import statements"""
        # Convert file path to import path
        # src/operations/modules/payment_orchestrator.py
        # -> from src.operations.modules.payment_orchestrator import PaymentOrchestrator
        
        path = Path(feature_path)
        module_parts = list(path.parts[:-1]) + [path.stem]  # Remove .py extension
        module_path = '.'.join(module_parts)
        
        imports = f"""import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from {module_path} import {feature_name}
"""
        return imports
    
    def _generate_test_class(self, feature_name: str, methods: List[str]) -> str:
        """Generate test class with test methods"""
        class_name = f"Test{feature_name}"
        
        test_class = f'''
class {class_name}:
    """Test suite for {feature_name}"""
    
    def test_initialization(self, {self._to_snake_case(feature_name)}_instance):
        """Test that {feature_name} can be instantiated"""
        assert {self._to_snake_case(feature_name)}_instance is not None
        assert isinstance({self._to_snake_case(feature_name)}_instance, {feature_name})
'''
        
        # Generate test methods for each public method
        for method in methods:
            if method == '__init__':
                continue  # Already tested in test_initialization
            
            test_class += f'''
    def test_{method}(self, {self._to_snake_case(feature_name)}_instance):
        """Test {feature_name}.{method}() method"""
        # TODO: Implement test logic for {method}()
        # Arrange
        # expected_result = ...
        
        # Act
        # result = {self._to_snake_case(feature_name)}_instance.{method}()
        
        # Assert
        # assert result == expected_result
        pass
'''
        
        return test_class
    
    def _generate_fixtures(self, feature_name: str) -> str:
        """Generate pytest fixtures"""
        fixture_name = self._to_snake_case(feature_name)
        
        fixtures = f'''
@pytest.fixture
def {fixture_name}_instance():
    """Fixture providing a {feature_name} instance"""
    # TODO: Add any required initialization parameters
    return {feature_name}()


@pytest.fixture
def mock_dependencies():
    """Fixture providing mocked dependencies"""
    # TODO: Add mocks for external dependencies
    return {{
        # "dependency_name": Mock(),
    }}
'''
        return fixtures
    
    def _assemble_test_file(self, imports: str, fixtures: str, test_class: str) -> str:
        """Assemble complete test file"""
        header = '''"""
Tests for {feature_name}

Auto-generated test skeleton by CORTEX System Alignment.
TODO: Implement test logic for each method.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

'''
        return header + imports + fixtures + test_class
    
    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase/CamelCase to snake_case"""
        # Remove "Orchestrator" or "Agent" suffix
        name = re.sub(r'(Orchestrator|Agent)$', '', name)
        
        # Insert underscore before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def generate_batch_skeletons(self, untested_features: List[Dict[str, any]]) -> List[Dict[str, str]]:
        """
        Generate test skeletons for multiple untested features
        
        Args:
            untested_features: List of dicts with keys: name, path, methods
        
        Returns:
            List of test skeleton suggestions (one per feature)
        """
        skeletons = []
        
        for feature in untested_features:
            skeleton = self.generate_test_skeleton(
                feature_name=feature.get("name", "Unknown"),
                feature_path=feature.get("path", ""),
                methods=feature.get("methods")
            )
            skeletons.append(skeleton)
        
        return skeletons
