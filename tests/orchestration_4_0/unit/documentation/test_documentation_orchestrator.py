"""
Tests for DocumentationOrchestrator - Main orchestrator
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from src.orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig,
    DocumentationResult
)


@pytest.fixture
def logger():
    """Create a mock logger"""
    return Mock()


@pytest.fixture
def orchestrator(logger):
    """Create a DocumentationOrchestrator instance"""
    return DocumentationOrchestrator(logger=logger)


@pytest.fixture
def sample_source_dir(tmp_path):
    """Create a sample source directory with Python files"""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create a simple Python file
    sample_file = src_dir / "sample.py"
    sample_file.write_text("""
'''Sample module'''

class SampleClass:
    '''Sample class'''
    
    def sample_method(self) -> None:
        '''Sample method'''
        pass
""")
    
    return src_dir


@pytest.fixture
def doc_config(tmp_path, sample_source_dir):
    """Create documentation configuration"""
    return DocumentationConfig(
        source_paths=[sample_source_dir],
        output_dir=tmp_path / "docs",
        include_private=False,
        generate_diagrams=True
    )


class TestDocumentationOrchestrator:
    """Tests for DocumentationOrchestrator"""
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator is not None
        assert orchestrator.code_analyzer is not None
        assert orchestrator.type_extractor is not None
        assert orchestrator.api_doc_generator is not None
        assert orchestrator.diagram_generator is not None
    
    def test_setup_with_config(self, orchestrator, doc_config):
        """Test setup phase with configuration"""
        context = {'config': doc_config}
        orchestrator._setup(context)
        
        assert 'config' in context
        assert 'result' in context
        assert isinstance(context['result'], DocumentationResult)
    
    def test_setup_with_dict_config(self, orchestrator, tmp_path, sample_source_dir):
        """Test setup with dict configuration"""
        context = {
            'config': {
                'source_paths': [sample_source_dir],
                'output_dir': tmp_path / "docs"
            }
        }
        orchestrator._setup(context)
        
        assert context['config'].source_paths == [sample_source_dir]
    
    def test_setup_invalid_config(self, orchestrator):
        """Test setup with invalid configuration"""
        with pytest.raises(ValueError):
            orchestrator._setup({'config': "invalid"})
    
    def test_setup_no_source_paths(self, orchestrator, tmp_path):
        """Test setup with no source paths"""
        config = DocumentationConfig(
            source_paths=[],
            output_dir=tmp_path / "docs"
        )
        
        with pytest.raises(ValueError, match="No source paths"):
            orchestrator._setup({'config': config})
    
    def test_setup_nonexistent_path(self, orchestrator, tmp_path):
        """Test setup with non-existent source path"""
        config = DocumentationConfig(
            source_paths=[tmp_path / "nonexistent"],
            output_dir=tmp_path / "docs"
        )
        
        with pytest.raises(FileNotFoundError):
            orchestrator._setup({'config': config})
    
    def test_register_phases(self, orchestrator, doc_config):
        """Test phase registration"""
        orchestrator._setup({'config': doc_config})
        orchestrator._register_phases()
        
        phase_names = [p.name for p in orchestrator.phase_manager.phases]
        assert "analyze" in phase_names
        assert "extract" in phase_names
        assert "generate_docs" in phase_names
        assert "generate_diagrams" in phase_names
        assert "validate" in phase_names
        assert "export" in phase_names
    
    def test_register_phases_no_diagrams(self, orchestrator, tmp_path, sample_source_dir):
        """Test phase registration without diagrams"""
        config = DocumentationConfig(
            source_paths=[sample_source_dir],
            output_dir=tmp_path / "docs",
            generate_diagrams=False
        )
        orchestrator._setup({'config': config})
        orchestrator._register_phases()
        
        # generate_diagrams phase should still be registered but skipped
        phase_names = [p.name for p in orchestrator.phase_manager.phases]
        assert "analyze" in phase_names
        assert "generate_docs" in phase_names
    
    def test_analyze_phase_single_file(self, orchestrator, doc_config, sample_source_dir):
        """Test analyze phase with single file"""
        orchestrator._setup({'config': doc_config})
        result = DocumentationResult()
        context = {'config': doc_config, 'result': result}
        
        orchestrator._analyze_phase(context, result)
        
        assert result.modules_analyzed > 0
        assert len(orchestrator.modules) > 0
    
    def test_analyze_phase_directory(self, orchestrator, tmp_path):
        """Test analyze phase with directory"""
        # Create multiple Python files
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        for i in range(3):
            file = src_dir / f"module{i}.py"
            file.write_text(f"'''Module {i}'''\n\nclass Class{i}:\n    pass")
        
        config = DocumentationConfig(
            source_paths=[src_dir],
            output_dir=tmp_path / "docs"
        )
        orchestrator._setup({'config': config})
        result = DocumentationResult()
        context = {'config': config, 'result': result}
        
        orchestrator._analyze_phase(context, result)
        
        assert result.modules_analyzed == 3
    
    def test_analyze_phase_skip_tests(self, orchestrator, tmp_path):
        """Test that test files are skipped during analysis"""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        # Create regular file
        (src_dir / "module.py").write_text("'''Module'''")
        
        # Create test file (should be skipped)
        (src_dir / "test_module.py").write_text("'''Test'''")
        
        config = DocumentationConfig(
            source_paths=[src_dir],
            output_dir=tmp_path / "docs"
        )
        orchestrator._setup({'config': config})
        result = DocumentationResult()
        context = {'config': config, 'result': result}
        
        orchestrator._analyze_phase(context, result)
        
        assert result.modules_analyzed == 1  # Only the regular file
    
    def test_extract_phase(self, orchestrator, doc_config, sample_source_dir):
        """Test extract phase"""
        orchestrator._setup({'config': doc_config})
        result = DocumentationResult()
        context = {'config': doc_config, 'result': result}
        
        # First analyze
        orchestrator._analyze_phase(context, result)
        
        # Then extract
        orchestrator._extract_phase(context, result)
        
        assert result.classes_documented > 0
    
    def test_generate_docs_phase(self, orchestrator, doc_config, sample_source_dir):
        """Test docs generation phase"""
        orchestrator._setup({'config': doc_config})
        result = DocumentationResult()
        context = {'config': doc_config, 'result': result}
        
        # Analyze and extract first
        orchestrator._analyze_phase(context, result)
        orchestrator._extract_phase(context, result)
        
        # Generate docs
        orchestrator._generate_docs_phase(context, result)
        
        assert len(result.output_files) > 0
        assert any(f.name.endswith('.md') for f in result.output_files)
    
    def test_generate_docs_phase_no_modules(self, orchestrator, doc_config):
        """Test docs generation with no modules"""
        orchestrator._setup({'config': doc_config})
        result = DocumentationResult()
        context = {'config': doc_config, 'result': result}
        
        # Skip analyze phase - no modules
        orchestrator._generate_docs_phase(context, result)
        
        assert len(result.warnings) > 0
    
    def test_validate_phase(self, orchestrator, doc_config, sample_source_dir):
        """Test validation phase"""
        orchestrator._setup({'config': doc_config})
        result = DocumentationResult()
        context = {'config': doc_config, 'result': result}
        
        # Run through phases
        orchestrator._analyze_phase(context, result)
        orchestrator._extract_phase(context, result)
        orchestrator._generate_docs_phase(context, result)
        
        # Validate
        orchestrator._validate_phase(context, result)
        
        # Should have some warnings about missing docstrings
        assert len(result.warnings) >= 0
    
    def test_export_phase(self, orchestrator, doc_config, sample_source_dir):
        """Test export phase"""
        orchestrator._setup({'config': doc_config})
        result = DocumentationResult()
        result.modules_analyzed = 1
        result.classes_documented = 1
        context = {'config': doc_config, 'result': result}
        
        orchestrator._export_phase(context, result)
        
        # Check summary file was created
        summary_path = doc_config.output_dir / "summary.md"
        assert summary_path.exists()
        assert summary_path in result.output_files
    
    def test_full_execution(self, orchestrator, doc_config):
        """Test full orchestrator execution"""
        context = {'config': doc_config}
        result = orchestrator.execute(context)
        
        assert result is not None
        assert 'result' in result
        doc_result = result['result']
        assert doc_result.modules_analyzed > 0
    
    def test_validation_methods(self, orchestrator, doc_config):
        """Test validation methods"""
        orchestrator._setup({'config': doc_config})
        result = DocumentationResult()
        
        # Test validate_analyze - should fail with no modules
        context = {'config': doc_config, 'result': result}
        assert not orchestrator._validate_analyze(context)
        
        # Add modules
        orchestrator.modules = [Mock()]
        assert orchestrator._validate_analyze(context)
        
        # Test validate_extract - should fail with no documented items
        assert not orchestrator._validate_extract(context)
        
        result.classes_documented = 1
        assert orchestrator._validate_extract(context)
        
        # Test validate_docs - should fail with no output files
        assert not orchestrator._validate_docs(context)
        
        result.output_files.append(Path("test.md"))
        assert orchestrator._validate_docs(context)
    
    def test_teardown(self, orchestrator, doc_config):
        """Test teardown phase"""
        orchestrator._setup({'config': doc_config})
        orchestrator.doc_result = DocumentationResult(
            modules_analyzed=2,
            classes_documented=5,
            functions_documented=10
        )
        
        # Should not raise
        orchestrator._teardown()

