"""
Tests for CORTEX Documentation Generator

Comprehensive test suite for update_documentation operation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0 (CORTEX 3.0 Phase 1.1 Week 2)
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.operations.update_documentation import (
    DocumentationGenerator,
    DocGenerationResult
)


@pytest.fixture
def temp_cortex_root(tmp_path):
    """Create temporary CORTEX structure for testing."""
    # Create directory structure
    (tmp_path / "src" / "operations").mkdir(parents=True)
    (tmp_path / "src" / "cortex_agents").mkdir(parents=True)
    (tmp_path / "cortex-brain").mkdir(parents=True)
    (tmp_path / "docs" / "api").mkdir(parents=True)
    (tmp_path / "docs" / "operations").mkdir(parents=True)
    (tmp_path / "tests").mkdir(parents=True)
    
    # Create sample Python file with docstrings
    sample_py = tmp_path / "src" / "operations" / "sample_operation.py"
    sample_py.write_text('''"""
Sample Operation Module

This is a sample operation for testing documentation generation.

Author: Test Author
Copyright: © 2024-2025 Test. All rights reserved.
"""


class SampleOperation:
    """
    Sample operation class.
    
    This class demonstrates documentation generation.
    """
    
    def __init__(self):
        """Initialize the sample operation."""
        self.name = "sample"
    
    def execute(self, param1: str, param2: int = 10) -> bool:
        """
        Execute the sample operation.
        
        Args:
            param1: First parameter (required)
            param2: Second parameter (optional, default=10)
            
        Returns:
            True if successful, False otherwise
        """
        return True
    
    def _private_method(self):
        """Private method (should be excluded)."""
        pass


def sample_function(arg1: str) -> str:
    """
    Sample top-level function.
    
    Args:
        arg1: Input argument
        
    Returns:
        Processed string
    """
    return arg1.upper()
''')
    
    # Create sample markdown file
    sample_md = tmp_path / "docs" / "sample.md"
    sample_md.write_text('''# Sample Documentation

This is a [valid link](sample.md) and this is a [broken link](nonexistent.md).

[External link](https://github.com/example/repo)
''')
    
    # Create mkdocs.yml
    mkdocs_yml = tmp_path / "mkdocs.yml"
    mkdocs_yml.write_text('''site_name: Test Site
nav:
  - Home: index.md
  - About: about.md
''')
    
    return tmp_path


class TestDocGenerationResult:
    """Test DocGenerationResult dataclass."""
    
    def test_result_initialization(self):
        """Test result object initialization."""
        result = DocGenerationResult(success=True)
        
        assert result.success is True
        assert isinstance(result.docs_generated, list)
        assert isinstance(result.docs_updated, list)
        assert result.links_validated == 0
        assert isinstance(result.timestamp, datetime)
    
    def test_result_to_dict(self):
        """Test conversion to dictionary."""
        result = DocGenerationResult(
            success=True,
            docs_generated=['api/reference.md'],
            links_validated=10
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['success'] is True
        assert result_dict['docs_generated'] == ['api/reference.md']
        assert result_dict['links_validated'] == 10
        assert 'timestamp' in result_dict


class TestDocumentationGenerator:
    """Test DocumentationGenerator class."""
    
    def test_initialization(self, temp_cortex_root):
        """Test generator initialization."""
        generator = DocumentationGenerator(temp_cortex_root)
        
        assert generator.cortex_root == temp_cortex_root
        assert generator.docs_dir == temp_cortex_root / "docs"
        assert generator.src_dir == temp_cortex_root / "src"
        assert generator.brain_dir == temp_cortex_root / "cortex-brain"
    
    def test_load_config_creates_default(self, temp_cortex_root):
        """Test config loading creates default if not exists."""
        generator = DocumentationGenerator(temp_cortex_root)
        success = generator.load_config()
        
        assert success is True
        assert generator.config is not None
        assert 'version' in generator.config
        assert 'sources' in generator.config
        assert generator.config_file.exists()
    
    def test_load_config_reads_existing(self, temp_cortex_root):
        """Test config loading reads existing file."""
        # Create config file first
        config_file = temp_cortex_root / "cortex-brain" / "doc-generation-rules.yaml"
        config_file.write_text('''version: 2.0.0
author: Custom Author
''')
        
        generator = DocumentationGenerator(temp_cortex_root)
        success = generator.load_config()
        
        assert success is True
        assert generator.config['version'] == '2.0.0'
        assert generator.config['author'] == 'Custom Author'
    
    def test_discover_files(self, temp_cortex_root):
        """Test file discovery."""
        generator = DocumentationGenerator(temp_cortex_root)
        generator.load_config()
        success = generator.discover_files()
        
        assert success is True
        assert len(generator.python_files) > 0
        
        # Check that sample_operation.py was found
        py_files = [f.name for f in generator.python_files]
        assert 'sample_operation.py' in py_files
    
    def test_discover_files_excludes_patterns(self, temp_cortex_root):
        """Test file discovery excludes specified patterns."""
        # Create a file that should be excluded
        pycache_dir = temp_cortex_root / "src" / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "test.py").write_text("# Should be excluded")
        
        generator = DocumentationGenerator(temp_cortex_root)
        generator.load_config()
        generator.discover_files()
        
        # Check that __pycache__ files are excluded
        py_files = [str(f) for f in generator.python_files]
        assert not any('__pycache__' in f for f in py_files)
    
    def test_extract_python_docstrings(self, temp_cortex_root):
        """Test docstring extraction from Python files."""
        generator = DocumentationGenerator(temp_cortex_root)
        sample_file = temp_cortex_root / "src" / "operations" / "sample_operation.py"
        
        docstrings = generator.extract_python_docstrings(sample_file)
        
        assert docstrings is not None
        assert 'module_doc' in docstrings
        assert 'Sample Operation Module' in docstrings['module_doc']
        
        # Check class extraction
        assert len(docstrings['classes']) == 1
        assert docstrings['classes'][0]['name'] == 'SampleOperation'
        assert 'Sample operation class' in docstrings['classes'][0]['docstring']
        
        # Check method extraction
        methods = docstrings['classes'][0]['methods']
        method_names = [m['name'] for m in methods]
        assert 'execute' in method_names
        assert '_private_method' in method_names  # Still extracted, filtered later
        
        # Check function extraction
        assert len(docstrings['functions']) == 1
        assert docstrings['functions'][0]['name'] == 'sample_function'
    
    def test_extract_function_args(self, temp_cortex_root):
        """Test function argument extraction."""
        generator = DocumentationGenerator(temp_cortex_root)
        sample_file = temp_cortex_root / "src" / "operations" / "sample_operation.py"
        
        docstrings = generator.extract_python_docstrings(sample_file)
        execute_method = None
        
        for method in docstrings['classes'][0]['methods']:
            if method['name'] == 'execute':
                execute_method = method
                break
        
        assert execute_method is not None
        assert 'self' in execute_method['args']
        assert 'param1' in execute_method['args']
        assert 'param2' in execute_method['args']
    
    def test_generate_api_reference(self, temp_cortex_root):
        """Test API reference generation."""
        generator = DocumentationGenerator(temp_cortex_root)
        sample_file = temp_cortex_root / "src" / "operations" / "sample_operation.py"
        
        docstrings = [generator.extract_python_docstrings(sample_file)]
        api_content = generator.generate_api_reference(docstrings)
        
        assert '# CORTEX API Reference' in api_content
        assert 'SampleOperation' in api_content
        assert 'execute' in api_content
        assert 'sample_function' in api_content
        
        # Private methods should be excluded
        assert '_private_method' not in api_content
    
    def test_generate_operations_docs(self, temp_cortex_root):
        """Test operations documentation generation."""
        generator = DocumentationGenerator(temp_cortex_root)
        generator.load_config()
        
        operations_docs = generator.generate_operations_docs()
        
        assert len(operations_docs) > 0
        
        # Check that sample_operation.md was generated
        doc_names = [name for name, _ in operations_docs]
        assert 'sample-operation.md' in doc_names
        
        # Check content
        for name, content in operations_docs:
            if name == 'sample-operation.md':
                assert '# Sample Operation Operation' in content
                assert 'Overview' in content
                assert 'Usage' in content
    
    def test_validate_links(self, temp_cortex_root):
        """Test link validation."""
        generator = DocumentationGenerator(temp_cortex_root)
        generator.load_config()
        
        md_files = [temp_cortex_root / "docs" / "sample.md"]
        total_links, broken_links = generator.validate_links(md_files)
        
        assert total_links > 0
        assert len(broken_links) > 0
        
        # Should detect broken link to nonexistent.md
        assert any('nonexistent.md' in link for link in broken_links)
    
    def test_validate_links_disabled(self, temp_cortex_root):
        """Test link validation when disabled."""
        generator = DocumentationGenerator(temp_cortex_root)
        generator.load_config()
        generator.config['link_validation']['enabled'] = False
        
        md_files = [temp_cortex_root / "docs" / "sample.md"]
        total_links, broken_links = generator.validate_links(md_files)
        
        assert total_links == 0
        assert len(broken_links) == 0
    
    def test_update_mkdocs_nav(self, temp_cortex_root):
        """Test MkDocs navigation update."""
        generator = DocumentationGenerator(temp_cortex_root)
        generator.load_config()
        
        generated_docs = ['sample-operation.md']
        success = generator.update_mkdocs_nav(generated_docs)
        
        assert success is True
        
        # Check that mkdocs.yml was updated
        import yaml
        with open(generator.mkdocs_file, 'r') as f:
            mkdocs_config = yaml.safe_load(f)
        
        assert 'nav' in mkdocs_config
        # Should have added API Reference section
        nav_sections = [list(item.keys())[0] if isinstance(item, dict) else item 
                       for item in mkdocs_config['nav']]
        assert 'API Reference' in nav_sections
    
    def test_update_mkdocs_nav_disabled(self, temp_cortex_root):
        """Test MkDocs navigation update when disabled."""
        generator = DocumentationGenerator(temp_cortex_root)
        generator.load_config()
        generator.config['mkdocs']['auto_update_nav'] = False
        
        success = generator.update_mkdocs_nav(['test.md'])
        
        assert success is True
        # mkdocs.yml should remain unchanged
    
    def test_execute_full_workflow(self, temp_cortex_root):
        """Test full documentation generation workflow."""
        generator = DocumentationGenerator(temp_cortex_root)
        result = generator.execute()
        
        assert isinstance(result, DocGenerationResult)
        assert result.success is True
        assert len(result.docs_generated) > 0
        assert result.duration_seconds > 0
        
        # Check that files were created
        api_file = temp_cortex_root / "docs" / "api" / "reference.md"
        assert api_file.exists()
        
        # Check that operations docs were created
        operations_dir = temp_cortex_root / "docs" / "operations"
        assert operations_dir.exists()
        assert len(list(operations_dir.glob("*.md"))) > 0
    
    def test_execute_handles_errors_gracefully(self, temp_cortex_root):
        """Test error handling during execution."""
        # Remove a required directory to trigger an error
        shutil.rmtree(temp_cortex_root / "src")
        
        generator = DocumentationGenerator(temp_cortex_root)
        result = generator.execute()
        
        # Should complete without crashing
        assert isinstance(result, DocGenerationResult)
        assert result.duration_seconds >= 0


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_directory(self, tmp_path):
        """Test with empty directory."""
        generator = DocumentationGenerator(tmp_path)
        result = generator.execute()
        
        # Should handle gracefully
        assert isinstance(result, DocGenerationResult)
    
    def test_file_without_docstrings(self, temp_cortex_root):
        """Test Python file without docstrings."""
        no_doc_file = temp_cortex_root / "src" / "no_doc.py"
        no_doc_file.write_text('''
class NoDoc:
    def method(self):
        pass
''')
        
        generator = DocumentationGenerator(temp_cortex_root)
        docstrings = generator.extract_python_docstrings(no_doc_file)
        
        assert docstrings is not None
        assert docstrings['module_doc'] is None
    
    def test_malformed_python_file(self, temp_cortex_root):
        """Test handling of malformed Python file."""
        bad_file = temp_cortex_root / "src" / "bad.py"
        bad_file.write_text('def incomplete(')
        
        generator = DocumentationGenerator(temp_cortex_root)
        docstrings = generator.extract_python_docstrings(bad_file)
        
        # Should return empty dict on parse error
        assert docstrings == {}
    
    def test_markdown_with_no_links(self, temp_cortex_root):
        """Test markdown file with no links."""
        no_links = temp_cortex_root / "docs" / "no_links.md"
        no_links.write_text('# Just a heading\n\nSome text without links.')
        
        generator = DocumentationGenerator(temp_cortex_root)
        generator.load_config()
        
        total_links, broken_links = generator.validate_links([no_links])
        
        assert total_links == 0
        assert len(broken_links) == 0


class TestIntegration:
    """Integration tests with real CORTEX files."""
    
    @pytest.mark.skipif(
        not Path.cwd().name == "CORTEX",
        reason="Must run from CORTEX root directory"
    )
    def test_real_cortex_documentation(self):
        """Test documentation generation on real CORTEX codebase."""
        generator = DocumentationGenerator(Path.cwd())
        result = generator.execute()
        
        assert result.success is True
        assert len(result.docs_generated) > 0
        
        # Cleanup generated docs in test mode
        # (In real usage, these would be committed)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
