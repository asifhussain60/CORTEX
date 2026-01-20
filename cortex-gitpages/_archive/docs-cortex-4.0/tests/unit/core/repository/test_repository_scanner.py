"""
Unit tests for Repository Scanner (AC-PROD-004-01).

Tests the system-wide code analysis capabilities including:
- File discovery and classification
- Code structure analysis (classes, functions, imports)
- Pattern detection
- Relationship mapping
- Various repository structures

Tests: 20+
Status: RED (TDD - tests before implementation)
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from src.orchestrators.core.repository_scanner import (
    RepositoryScanner,
    ScanContext,
    ScanOutput,
    FileEntity,
    ClassEntity,
    FunctionEntity,
    ImportStatement,
    CodePattern,
)


# ============================================================================
# Test Data Structures
# ============================================================================

class EntityType(Enum):
    """Types of code entities."""
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    IMPORT = "import"
    PATTERN = "pattern"


@dataclass
class MockFileStructure:
    """Represents a mock file structure for testing."""
    path: str
    content: str
    is_python: bool = True


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_python_file():
    """Sample Python file with various code structures."""
    return MockFileStructure(
        path="src/example.py",
        content="""
import os
import sys
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Config:
    name: str
    version: str
    
    def validate(self) -> bool:
        return len(self.name) > 0

def process_data(items: List[str]) -> Dict[str, int]:
    result = {}
    for item in items:
        result[item] = len(item)
    return result

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add_item(self, item: str):
        self.data.append(item)
    
    def process(self) -> List[str]:
        return [item.upper() for item in self.data]
""",
        is_python=True
    )


@pytest.fixture
def scan_context():
    """Create a basic scan context."""
    return ScanContext(
        workspace_root=Path("/workspace"),
        target_paths=[Path("/workspace/src")],
        exclude_patterns=["*.pyc", "__pycache__", ".git"],
    )


@pytest.fixture
def scanner(tmp_path):
    """Create a scanner instance with temp directory."""
    return RepositoryScanner(workspace_root=tmp_path)


# ============================================================================
# Test Suite 1: Initialization and Configuration
# ============================================================================

class TestRepositoryScannerInitialization:
    """Test scanner initialization and configuration."""
    
    def test_scanner_initialization(self, scanner):
        """Test scanner can be initialized."""
        assert scanner is not None
        assert isinstance(scanner, RepositoryScanner)
    
    def test_scanner_workspace_root_set(self, tmp_path):
        """Test workspace root is properly set."""
        scanner = RepositoryScanner(workspace_root=tmp_path)
        assert scanner.workspace_root == tmp_path
    
    def test_scan_context_initialization(self, scan_context):
        """Test scan context is properly structured."""
        assert scan_context.workspace_root is not None
        assert isinstance(scan_context.target_paths, list)
        assert isinstance(scan_context.exclude_patterns, list)


# ============================================================================
# Test Suite 2: File Discovery
# ============================================================================

class TestFileDiscovery:
    """Test file discovery and classification."""
    
    def test_discover_python_files(self, scanner, tmp_path):
        """Test scanner discovers Python files."""
        # Create test Python files
        (tmp_path / "file1.py").touch()
        (tmp_path / "file2.py").touch()
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        files = scanner.discover_files(context)
        assert len(files) >= 2
        assert any(f.path.name == "file1.py" for f in files)
        assert any(f.path.name == "file2.py" for f in files)
    
    def test_exclude_patterns_respected(self, scanner, tmp_path):
        """Test that exclude patterns are respected."""
        (tmp_path / "include.py").touch()
        (tmp_path / "exclude.pyc").touch()
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=["*.pyc"],
        )
        
        files = scanner.discover_files(context)
        names = [f.path.name for f in files]
        assert "include.py" in names
        assert "exclude.pyc" not in names
    
    def test_recursive_directory_discovery(self, scanner, tmp_path):
        """Test recursive discovery in nested directories."""
        nested = tmp_path / "src" / "nested"
        nested.mkdir(parents=True)
        (nested / "deep.py").touch()
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        files = scanner.discover_files(context)
        paths = [str(f.path) for f in files]
        assert any("deep.py" in p for p in paths)
    
    def test_file_count_accuracy(self, scanner, tmp_path):
        """Test accurate file counting."""
        for i in range(5):
            (tmp_path / f"file{i}.py").touch()
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        files = scanner.discover_files(context)
        assert len(files) == 5


# ============================================================================
# Test Suite 3: Code Structure Analysis
# ============================================================================

class TestCodeStructureAnalysis:
    """Test analysis of code structures."""
    
    def test_extract_imports(self, scanner, sample_python_file):
        """Test extraction of import statements."""
        imports = scanner.extract_imports(sample_python_file.content)
        
        assert len(imports) >= 3
        assert any("os" in imp.module for imp in imports)
        assert any("typing" in imp.module for imp in imports)
    
    def test_identify_classes(self, scanner, sample_python_file):
        """Test identification of class definitions."""
        classes = scanner.identify_classes(sample_python_file.content)
        
        assert len(classes) >= 2
        assert any("Config" in cls.name for cls in classes)
        assert any("DataProcessor" in cls.name for cls in classes)
    
    def test_identify_functions(self, scanner, sample_python_file):
        """Test identification of function definitions."""
        functions = scanner.identify_functions(sample_python_file.content)
        
        assert len(functions) >= 1
        assert any("process_data" in func.name for func in functions)
    
    def test_extract_class_methods(self, scanner, sample_python_file):
        """Test extraction of methods from classes."""
        classes = scanner.identify_classes(sample_python_file.content)
        
        # Find DataProcessor class
        data_proc = next((c for c in classes if "DataProcessor" in c.name), None)
        assert data_proc is not None
        assert len(data_proc.methods) >= 3


# ============================================================================
# Test Suite 4: Pattern Detection
# ============================================================================

class TestPatternDetection:
    """Test pattern detection in code."""
    
    def test_detect_dataclass_pattern(self, scanner, sample_python_file):
        """Test detection of dataclass pattern."""
        patterns = scanner.detect_patterns(sample_python_file.content)
        
        assert any(p.name == "dataclass" for p in patterns)
    
    def test_detect_decorator_patterns(self, scanner, sample_python_file):
        """Test detection of decorator usage."""
        patterns = scanner.detect_patterns(sample_python_file.content)
        
        decorator_patterns = [p for p in patterns if "decorator" in p.category.value.lower()]
        assert len(decorator_patterns) > 0
    
    def test_detect_type_hints(self, scanner, sample_python_file):
        """Test detection of type hints in code."""
        patterns = scanner.detect_patterns(sample_python_file.content)
        
        type_patterns = [p for p in patterns if "type_hint" in p.category.value.lower()]
        assert len(type_patterns) > 0


# ============================================================================
# Test Suite 5: Relationship Mapping
# ============================================================================

class TestRelationshipMapping:
    """Test detection of relationships between entities."""
    
    def test_class_dependency_detection(self, scanner, sample_python_file):
        """Test detection of class dependencies."""
        # Analyze the file to get structure
        result = scanner.analyze_file(sample_python_file.path, sample_python_file.content)
        
        assert result is not None
        assert hasattr(result, 'imports') or hasattr(result, 'classes')
    
    def test_import_dependency_graph(self, scanner, tmp_path):
        """Test generation of import dependency graph."""
        # Create two interdependent files
        file1 = tmp_path / "module1.py"
        file1.write_text("def func1(): pass")
        
        file2 = tmp_path / "module2.py"
        file2.write_text("from module1 import func1\ndef func2(): pass")
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        # First discover and analyze files
        files = scanner.discover_files(context)
        result = scanner.build_dependency_graph(context, files)
        
        assert result is not None
        assert len(result.files) >= 1  # At least one file discovered


# ============================================================================
# Test Suite 6: Repository Structure Analysis
# ============================================================================

class TestRepositoryStructureAnalysis:
    """Test analysis of overall repository structure."""
    
    def test_analyze_simple_structure(self, scanner, tmp_path):
        """Test analysis of simple repository structure."""
        # Create simple structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("def main(): pass")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_main.py").write_text("def test_main(): pass")
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        result = scanner.scan(context)
        
        assert result is not None
        assert hasattr(result, 'file_count')
        assert hasattr(result, 'class_count')
        assert hasattr(result, 'function_count')
    
    def test_analyze_complex_structure(self, scanner, tmp_path):
        """Test analysis of complex repository structure."""
        # Create complex structure with multiple layers
        for layer in ["src", "tests", "docs"]:
            (tmp_path / layer).mkdir()
            for i in range(3):
                (tmp_path / layer / f"file{i}.py").write_text(
                    f"def func{i}(): pass\nclass Class{i}: pass"
                )
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        result = scanner.scan(context)
        
        assert result is not None
        assert result.file_count >= 9
        assert result.class_count >= 9
        assert result.function_count >= 9


# ============================================================================
# Test Suite 7: Scan Output and Reporting
# ============================================================================

class TestScanOutputAndReporting:
    """Test scan output generation and reporting."""
    
    def test_scan_output_structure(self, scanner, tmp_path):
        """Test scan output has correct structure."""
        (tmp_path / "test.py").write_text("def func(): pass")
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        output = scanner.scan(context)
        
        assert isinstance(output, ScanOutput)
        assert output.workspace_root == tmp_path
        assert output.file_count >= 1
        assert output.scan_duration >= 0
    
    def test_scan_summary_generation(self, scanner, tmp_path):
        """Test generation of scan summary."""
        (tmp_path / "test.py").write_text("class TestClass: pass")
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        output = scanner.scan(context)
        summary = scanner.generate_summary(output)
        
        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_output_to_dict(self, scanner, tmp_path):
        """Test conversion of output to dictionary."""
        (tmp_path / "test.py").write_text("def func(): pass")
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        output = scanner.scan(context)
        output_dict = output.to_dict()
        
        assert isinstance(output_dict, dict)
        assert "file_count" in output_dict
        assert "class_count" in output_dict


# ============================================================================
# Test Suite 8: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling in repository scanner."""
    
    def test_handle_nonexistent_path(self, scanner):
        """Test handling of nonexistent path."""
        context = ScanContext(
            workspace_root=Path("/nonexistent"),
            target_paths=[Path("/nonexistent")],
            exclude_patterns=[],
        )
        
        # Should not raise, should handle gracefully
        result = scanner.scan(context)
        assert result is not None
    
    def test_handle_permission_denied(self, scanner, tmp_path):
        """Test handling of permission denied errors."""
        restricted = tmp_path / "restricted"
        restricted.mkdir()
        (restricted / "test.py").write_text("pass")
        restricted.chmod(0o000)
        
        try:
            context = ScanContext(
                workspace_root=tmp_path,
                target_paths=[tmp_path],
                exclude_patterns=[],
            )
            
            # Should handle gracefully
            result = scanner.scan(context)
            assert result is not None
        finally:
            restricted.chmod(0o755)
    
    def test_handle_binary_files(self, scanner, tmp_path):
        """Test handling of binary files in repository."""
        (tmp_path / "binary.bin").write_bytes(b"\x00\x01\x02")
        (tmp_path / "text.py").write_text("def func(): pass")
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        result = scanner.scan(context)
        
        # Should process Python file and skip binary
        assert any(f.path.name == "text.py" for f in result.files)


# ============================================================================
# Test Suite 9: Governance and Audit
# ============================================================================

class TestGovernanceAndAudit:
    """Test governance compliance and audit logging."""
    
    def test_scan_result_includes_timestamp(self, scanner, tmp_path):
        """Test that scan result includes timestamp."""
        (tmp_path / "test.py").write_text("pass")
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        result = scanner.scan(context)
        
        assert result.timestamp is not None
    
    def test_scan_result_includes_version(self, scanner, tmp_path):
        """Test that scan result includes scanner version."""
        (tmp_path / "test.py").write_text("pass")
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        result = scanner.scan(context)
        
        assert hasattr(result, 'scanner_version')


# ============================================================================
# Test Suite 10: Integration with Stage 2
# ============================================================================

class TestIntegrationWithStage2:
    """Test integration with master orchestrator Stage 2."""
    
    def test_scan_context_creation(self, tmp_path):
        """Test creation of scan context for Stage 2."""
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path / "src"],
            exclude_patterns=["*.pyc", "__pycache__"],
        )
        
        assert context is not None
        assert isinstance(context.target_paths, list)
    
    def test_scan_output_passable_to_stage2(self, scanner, tmp_path):
        """Test that scan output can be passed to Stage 2."""
        (tmp_path / "test.py").write_text("class TestClass: pass")
        
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        output = scanner.scan(context)
        
        # Verify it has required fields for Stage 2
        assert output.file_count > 0
        assert output.files is not None
        assert output.entities is not None
