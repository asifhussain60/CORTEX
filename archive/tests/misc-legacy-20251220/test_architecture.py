"""
Architecture Enforcement Tests (RED Phase)

Tests to verify Clean Architecture dependency rule is maintained.
Domain → Application → Infrastructure → Presentation
No layer should import from layers above it.

Author: Asif Hussain
"""
import pytest
import ast
from pathlib import Path


def get_python_files(directory: Path):
    """Get all Python files in directory"""
    return list(directory.rglob("*.py"))


def get_imports_from_file(file_path: Path):
    """Extract all imports from Python file"""
    with open(file_path, 'r') as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return []
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    return imports


def test_domain_layer_no_framework_dependencies():
    """Test domain layer has zero framework dependencies"""
    domain_path = Path("src/dashboard/domain")
    
    forbidden_imports = ["flask", "django", "fastapi", "sqlite3", "json"]
    
    for py_file in get_python_files(domain_path):
        imports = get_imports_from_file(py_file)
        
        for imp in imports:
            for forbidden in forbidden_imports:
                assert not imp.startswith(forbidden), \
                    f"Domain layer file {py_file} imports {imp} (framework dependency)"


def test_domain_layer_no_infrastructure_imports():
    """Test domain layer doesn't import from infrastructure"""
    domain_path = Path("src/dashboard/domain")
    
    for py_file in get_python_files(domain_path):
        imports = get_imports_from_file(py_file)
        
        for imp in imports:
            assert not imp.startswith("src.dashboard.infrastructure"), \
                f"Domain layer file {py_file} imports from infrastructure: {imp}"


def test_domain_layer_no_application_imports():
    """Test domain layer doesn't import from application"""
    domain_path = Path("src/dashboard/domain")
    
    for py_file in get_python_files(domain_path):
        imports = get_imports_from_file(py_file)
        
        for imp in imports:
            assert not imp.startswith("src.dashboard.application"), \
                f"Domain layer file {py_file} imports from application: {imp}"


def test_domain_layer_no_presentation_imports():
    """Test domain layer doesn't import from presentation"""
    domain_path = Path("src/dashboard/domain")
    
    for py_file in get_python_files(domain_path):
        imports = get_imports_from_file(py_file)
        
        for imp in imports:
            assert not imp.startswith("src.dashboard.presentation"), \
                f"Domain layer file {py_file} imports from presentation: {imp}"


def test_application_layer_no_infrastructure_imports():
    """Test application layer doesn't import from infrastructure"""
    app_path = Path("src/dashboard/application")
    
    for py_file in get_python_files(app_path):
        imports = get_imports_from_file(py_file)
        
        for imp in imports:
            assert not imp.startswith("src.dashboard.infrastructure"), \
                f"Application layer file {py_file} imports from infrastructure: {imp}"


def test_application_layer_no_presentation_imports():
    """Test application layer doesn't import from presentation"""
    app_path = Path("src/dashboard/application")
    
    for py_file in get_python_files(app_path):
        imports = get_imports_from_file(py_file)
        
        for imp in imports:
            assert not imp.startswith("src.dashboard.presentation"), \
                f"Application layer file {py_file} imports from presentation: {imp}"


def test_infrastructure_layer_no_presentation_imports():
    """Test infrastructure layer doesn't import from presentation"""
    infra_path = Path("src/dashboard/infrastructure")
    
    for py_file in get_python_files(infra_path):
        imports = get_imports_from_file(py_file)
        
        for imp in imports:
            assert not imp.startswith("src.dashboard.presentation"), \
                f"Infrastructure layer file {py_file} imports from presentation: {imp}"


def test_presentation_layer_can_import_all_layers():
    """Test presentation layer CAN import from all other layers (this is allowed)"""
    # This test just documents that presentation is the outermost layer
    # and can depend on everything below it
    assert True  # No restrictions on presentation layer imports
