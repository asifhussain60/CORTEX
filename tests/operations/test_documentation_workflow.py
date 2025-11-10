"""
Test documentation operation workflow - scan → build → publish pipeline.

Tests the complete documentation generation system end-to-end.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from src.operations.modules.scan_docstrings_module import ScanDocstringsModule
from src.operations.modules.build_documentation_module import BuildDocumentationModule
from src.operations.modules.publish_documentation_module import PublishDocumentationModule
from src.operations.base_operation_module import OperationStatus


@pytest.fixture
def temp_project():
    """Create temporary project with Python files."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create project structure
    src_dir = temp_dir / "src"
    src_dir.mkdir()
    
    # Create sample Python files with docstrings
    
    # Module 1: utils.py
    utils_file = src_dir / "utils.py"
    utils_file.write_text('''"""
Utility module for CORTEX.

This module provides utility functions for common tasks.
"""

def format_message(text: str) -> str:
    """
    Format a message for display.
    
    Args:
        text: Message text
        
    Returns:
        Formatted message string
    """
    return f"[CORTEX] {text}"


class MessageFormatter:
    """
    Advanced message formatting class.
    
    Provides multiple formatting options for messages.
    """
    
    def format(self, text: str) -> str:
        """
        Format a message.
        
        Args:
            text: Message text
            
        Returns:
            Formatted message
        """
        return f">>> {text}"
    
    def format_error(self, text: str) -> str:
        """
        Format an error message.
        
        Args:
            text: Error text
            
        Returns:
            Formatted error message
        """
        return f"[ERROR] {text}"
''', encoding='utf-8')
    
    # Module 2: operations/base.py
    operations_dir = src_dir / "operations"
    operations_dir.mkdir()
    
    base_file = operations_dir / "base.py"
    base_file.write_text('''"""
Base operation module.

Provides abstract base class for all operations.
"""

from abc import ABC, abstractmethod


class BaseOperation(ABC):
    """
    Abstract base class for operations.
    
    All CORTEX operations inherit from this class.
    """
    
    @abstractmethod
    def execute(self, context: dict) -> dict:
        """
        Execute the operation.
        
        Args:
            context: Operation context
            
        Returns:
            Operation result dict
        """
        pass
''', encoding='utf-8')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestDocumentationWorkflow:
    """Test complete documentation generation workflow."""
    
    def test_scan_module(self, temp_project):
        """Test docstring scanning module."""
        scanner = ScanDocstringsModule()
        
        context = {
            "project_root": str(temp_project)
        }
        
        result = scanner.execute(context)
        
        # Verify success
        assert result.success is True
        assert result.status == OperationStatus.SUCCESS
        
        # Verify data structure
        assert "docstring_index" in result.data
        assert "total_docstrings" in result.data
        assert "files_scanned" in result.data
        
        # Verify docstrings extracted
        index = result.data["docstring_index"]
        assert len(index["modules"]) >= 2  # utils, operations.base
        assert len(index["classes"]) >= 2  # MessageFormatter, BaseOperation
        assert len(index["functions"]) >= 1  # format_message
        
        # Verify stats
        stats = index["stats"]
        assert stats["modules"] >= 2
        assert stats["classes"] >= 2
        assert stats["functions"] >= 1
        
        # Store index in context for next module
        context["docstring_index"] = index
        
        return context
    
    def test_build_module(self, temp_project):
        """Test documentation building module."""
        # First scan
        scanner = ScanDocstringsModule()
        context = {
            "project_root": str(temp_project)
        }
        scan_result = scanner.execute(context)
        assert scan_result.success is True
        
        # Add scan results to context
        context["docstring_index"] = scan_result.data["docstring_index"]
        
        # Build documentation
        builder = BuildDocumentationModule()
        result = builder.execute(context)
        
        # Verify success
        assert result.success is True
        assert result.status == OperationStatus.SUCCESS
        
        # Verify data structure
        assert "output_dir" in result.data
        assert "files_created" in result.data
        assert "total_files" in result.data
        
        # Verify files created
        output_dir = Path(result.data["output_dir"])
        assert output_dir.exists()
        
        # Check for index
        index_file = output_dir / "index.md"
        assert index_file.exists()
        
        # Check for directories
        assert (output_dir / "modules").exists()
        assert (output_dir / "classes").exists()
        assert (output_dir / "functions").exists()
        
        # Verify markdown files created
        module_files = list((output_dir / "modules").glob("*.md"))
        assert len(module_files) >= 2
        
        return context
    
    def test_publish_module(self, temp_project):
        """Test documentation publishing module."""
        # First scan
        scanner = ScanDocstringsModule()
        context = {
            "project_root": str(temp_project)
        }
        scan_result = scanner.execute(context)
        assert scan_result.success is True
        
        # Add scan results to context
        context["docstring_index"] = scan_result.data["docstring_index"]
        
        # Build documentation
        builder = BuildDocumentationModule()
        build_result = builder.execute(context)
        assert build_result.success is True
        
        # Publish documentation (without building site)
        publisher = PublishDocumentationModule()
        context["build_site"] = False
        context["deploy"] = False
        
        result = publisher.execute(context)
        
        # Verify success
        assert result.success is True
        assert result.status == OperationStatus.SUCCESS
        
        # Verify data structure
        assert "files_published" in result.data
        assert "actions_performed" in result.data
        assert "docs_location" in result.data
        
        # Verify actions performed
        actions = result.data["actions_performed"]
        assert "Verified documentation structure" in actions
    
    def test_complete_workflow(self, temp_project):
        """Test complete scan → build → publish workflow."""
        context = {
            "project_root": str(temp_project),
            "build_site": False,
            "deploy": False
        }
        
        # Step 1: Scan
        scanner = ScanDocstringsModule()
        scan_result = scanner.execute(context)
        
        assert scan_result.success is True
        assert scan_result.data["total_docstrings"] > 0
        
        # Pass data to next module
        context["docstring_index"] = scan_result.data["docstring_index"]
        
        # Step 2: Build
        builder = BuildDocumentationModule()
        build_result = builder.execute(context)
        
        assert build_result.success is True
        assert build_result.data["total_files"] > 0
        
        # Step 3: Publish
        publisher = PublishDocumentationModule()
        publish_result = publisher.execute(context)
        
        assert publish_result.success is True
        assert publish_result.data["files_published"] > 0
        
        # Verify complete pipeline
        output_dir = Path(build_result.data["output_dir"])
        
        # Check all expected files exist
        assert (output_dir / "index.md").exists()
        assert (output_dir / "modules").exists()
        assert (output_dir / "classes").exists()
        assert (output_dir / "functions").exists()
        
        # Verify content quality
        index_content = (output_dir / "index.md").read_text()
        assert "API Reference" in index_content
        assert "Statistics" in index_content
        assert "Modules:" in index_content
        
        # Verify module docs
        module_files = list((output_dir / "modules").glob("*.md"))
        assert len(module_files) > 0
        
        # Check one module file content
        module_content = module_files[0].read_text()
        assert "Module:" in module_content
        assert "Module Path:" in module_content
    
    def test_scan_missing_src_dir(self, temp_project):
        """Test scanner handles missing src directory."""
        # Remove src directory
        src_dir = temp_project / "src"
        if src_dir.exists():
            shutil.rmtree(src_dir)
        
        scanner = ScanDocstringsModule()
        context = {"project_root": str(temp_project)}
        
        result = scanner.execute(context)
        
        assert result.success is False
        assert result.status == OperationStatus.FAILED
        assert "not found" in result.message.lower()
    
    def test_build_missing_docstring_index(self, temp_project):
        """Test builder handles missing docstring index."""
        builder = BuildDocumentationModule()
        context = {"project_root": str(temp_project)}
        
        result = builder.execute(context)
        
        assert result.success is False
        assert result.status == OperationStatus.FAILED
        assert "docstring" in result.message.lower() or "index" in result.message.lower()
    
    def test_publish_missing_api_docs(self, temp_project):
        """Test publisher handles missing API docs."""
        publisher = PublishDocumentationModule()
        context = {
            "project_root": str(temp_project),
            "build_site": False,
            "deploy": False
        }
        
        result = publisher.execute(context)
        
        assert result.success is False
        assert result.status == OperationStatus.FAILED
        assert "not found" in result.message.lower()
    
    def test_module_dependencies(self):
        """Test module dependency declarations."""
        scanner = ScanDocstringsModule()
        builder = BuildDocumentationModule()
        publisher = PublishDocumentationModule()
        
        # Verify metadata
        scan_meta = scanner.get_metadata()
        build_meta = builder.get_metadata()
        publish_meta = publisher.get_metadata()
        
        # Verify IDs
        assert scan_meta.module_id == "scan_docstrings"
        assert build_meta.module_id == "build_documentation"
        assert publish_meta.module_id == "publish_documentation"
        
        # Verify dependencies
        assert build_meta.dependencies == ["scan_docstrings"]
        assert publish_meta.dependencies == ["build_documentation"]
        
        # Verify phases are in order
        assert scan_meta.phase.order < build_meta.phase.order
        assert build_meta.phase.order < publish_meta.phase.order
    
    def test_docstring_extraction_quality(self, temp_project):
        """Test quality of extracted docstrings."""
        scanner = ScanDocstringsModule()
        context = {"project_root": str(temp_project)}
        
        result = scanner.execute(context)
        assert result.success is True
        
        index = result.data["docstring_index"]
        
        # Check modules have docstrings
        modules = index["modules"]
        assert len(modules) > 0
        
        for module in modules:
            assert "module_path" in module
            assert "docstring" in module
            assert module["docstring"]  # Not empty
            assert len(module["docstring"]) > 10  # Substantial content
        
        # Check classes have docstrings
        classes = index["classes"]
        for cls in classes:
            assert "name" in cls
            assert "docstring" in cls
            assert cls["docstring"]
        
        # Check functions have signatures
        functions = index["functions"]
        for func in functions:
            assert "signature" in func
            assert func["signature"]
            assert "(" in func["signature"]  # Has arguments
    
    def test_markdown_formatting(self, temp_project):
        """Test generated Markdown is well-formatted."""
        # Run complete workflow
        context = {
            "project_root": str(temp_project),
            "build_site": False,
            "deploy": False
        }
        
        scanner = ScanDocstringsModule()
        scan_result = scanner.execute(context)
        context["docstring_index"] = scan_result.data["docstring_index"]
        
        builder = BuildDocumentationModule()
        build_result = builder.execute(context)
        
        output_dir = Path(build_result.data["output_dir"])
        
        # Check index formatting
        index_content = (output_dir / "index.md").read_text()
        
        # Should have proper headings
        assert index_content.count("#") >= 3  # Multiple heading levels
        
        # Should have links
        assert "[" in index_content and "]" in index_content
        assert "(" in index_content and ")" in index_content
        
        # Should have lists
        assert "- " in index_content or "* " in index_content
        
        # Check module file formatting
        module_files = list((output_dir / "modules").glob("*.md"))
        if module_files:
            module_content = module_files[0].read_text()
            
            # Should have code formatting
            assert "`" in module_content
            
            # Should have horizontal rules
            assert "---" in module_content
            
            # Should have metadata
            assert "Module Path:" in module_content
            assert "Source Line:" in module_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
