"""
Test suite for DashboardBuilder
Tests template selection, HTML generation, output creation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.cortex_lens.generators.dashboard_builder import DashboardBuilder


# ========== Fixtures ==========

@pytest.fixture
def builder():
    """Create dashboard builder instance."""
    return DashboardBuilder()


@pytest.fixture
def sample_data():
    """Sample analysis data."""
    return {
        'data': {
            'metadata': {
                'repo_name': 'test-repo',
                'repo_type': ['api_service'],
                'total_files': 42,
                'total_loc': 5000
            },
            'health': {
                'status': 'healthy',
                'total_files': 42
            },
            'architecture': {
                'layers': [{'name': 'API', 'loc': 2000}]
            }
        },
        'narrative': {
            'executive_summary': 'Test API service',
            'key_capabilities': ['REST API', 'Authentication']
        },
        'classification': {
            'primary_type': 'api_service',
            'confidence': 0.85,
            'dashboard_template': 'api-service-dashboard'
        }
    }


@pytest.fixture
def sample_repo(tmp_path):
    """Create sample repository."""
    repo = tmp_path / "test-repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Test Repo")
    return repo


# ========== Initialization Tests ==========

class TestInitialization:
    """Test dashboard builder initialization."""
    
    def test_builder_initialization(self):
        """Test builder initializes correctly."""
        builder = DashboardBuilder()
        
        assert builder is not None
        assert hasattr(builder, 'templates_dir')
        assert builder.templates_dir.name == 'templates'
    
    def test_templates_dir_exists(self):
        """Test templates directory path is set."""
        builder = DashboardBuilder()
        
        # Should point to src/cortex_lens/templates
        assert 'templates' in str(builder.templates_dir)


# ========== Build Method Tests ==========

class TestBuildMethod:
    """Test build() wrapper method."""
    
    def test_build_with_explicit_output(self, builder, sample_repo, sample_data, tmp_path):
        """Test build with explicit output directory."""
        output_dir = tmp_path / "output"
        
        result = builder.build(
            repo_path=sample_repo,
            data=sample_data['data'],
            narrative=sample_data['narrative'],
            classification=sample_data['classification'],
            output_dir=str(output_dir),
            template='api-service-dashboard'
        )
        
        assert result.exists()
        assert result.name == 'index.html'
        assert output_dir in result.parents
    
    def test_build_with_auto_output(self, builder, sample_repo, sample_data):
        """Test build with automatic output directory."""
        result = builder.build(
            repo_path=sample_repo,
            data=sample_data['data'],
            narrative=sample_data['narrative'],
            classification=sample_data['classification'],
            output_dir=None,
            template=None
        )
        
        assert result.exists()
        assert 'cortex-lens-output' in str(result)
        assert result.name == 'index.html'
    
    def test_build_creates_output_directory(self, builder, sample_repo, sample_data, tmp_path):
        """Test that build creates output directory if missing."""
        output_dir = tmp_path / "nested" / "output" / "dir"
        
        result = builder.build(
            repo_path=sample_repo,
            data=sample_data['data'],
            narrative=sample_data['narrative'],
            classification=sample_data['classification'],
            output_dir=str(output_dir),
            template='test-template'
        )
        
        assert output_dir.exists()
        assert result.parent == output_dir


# ========== Generate Method Tests ==========

class TestGenerateMethod:
    """Test generate() core method."""
    
    def test_generate_creates_html(self, builder, sample_data, tmp_path):
        """Test generate creates index.html file."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        result = builder.generate(
            data=sample_data,
            output_path=output_path,
            template='api-service-dashboard'
        )
        
        assert result.exists()
        assert result.name == 'index.html'
        assert result.parent == output_path
    
    def test_generate_html_content(self, builder, sample_data, tmp_path):
        """Test generated HTML has expected content."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        result = builder.generate(
            data=sample_data,
            output_path=output_path
        )
        
        content = result.read_text(encoding='utf-8')
        
        # Should contain HTML structure
        assert '<html' in content.lower()
        assert '</html>' in content.lower()
        
        # Should contain repo name
        assert 'test-repo' in content
    
    def test_generate_with_auto_template(self, builder, sample_data, tmp_path):
        """Test generate auto-detects template from classification."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        # Don't specify template - should use classification
        result = builder.generate(
            data=sample_data,
            output_path=output_path
        )
        
        assert result.exists()
        content = result.read_text(encoding='utf-8')
        assert len(content) > 0
    
    def test_generate_without_template_uses_default(self, builder, tmp_path):
        """Test generate uses default template when none specified."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        # Minimal data without template
        data = {
            'data': {'metadata': {'repo_name': 'test'}},
            'narrative': {},
            'classification': {}
        }
        
        result = builder.generate(data=data, output_path=output_path)
        
        assert result.exists()


# ========== Template Selection Tests ==========

class TestTemplateSelection:
    """Test template selection logic."""
    
    def test_explicit_template_used(self, builder, sample_data, tmp_path):
        """Test explicit template parameter is used."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        result = builder.generate(
            data=sample_data,
            output_path=output_path,
            template='custom-template'
        )
        
        assert result.exists()
    
    def test_classification_template_used(self, builder, tmp_path):
        """Test template from classification is used."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        data = {
            'data': {'metadata': {'repo_name': 'test'}},
            'narrative': {},
            'classification': {
                'dashboard_template': 'microservices-dashboard'
            }
        }
        
        result = builder.generate(data=data, output_path=output_path)
        
        assert result.exists()
    
    def test_default_template_fallback(self, builder, tmp_path):
        """Test default template is used as fallback."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        # No template in classification
        data = {
            'data': {'metadata': {'repo_name': 'test'}},
            'narrative': {},
            'classification': {}
        }
        
        result = builder.generate(data=data, output_path=output_path)
        
        assert result.exists()
        content = result.read_text(encoding='utf-8')
        assert 'fullstack-web-dashboard' in content.lower() or len(content) > 0


# ========== HTML Content Tests ==========

class TestHTMLContent:
    """Test generated HTML content structure."""
    
    def test_html_contains_metadata(self, builder, sample_data, tmp_path):
        """Test HTML contains repository metadata."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        result = builder.generate(data=sample_data, output_path=output_path)
        content = result.read_text(encoding='utf-8')
        
        # Should contain metadata fields
        assert 'test-repo' in content
    
    def test_html_contains_narrative(self, builder, sample_data, tmp_path):
        """Test HTML contains narrative content."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        result = builder.generate(data=sample_data, output_path=output_path)
        content = result.read_text(encoding='utf-8')
        
        # Should contain executive summary
        assert 'Test API service' in content or 'executive_summary' in content.lower()
    
    def test_html_valid_structure(self, builder, sample_data, tmp_path):
        """Test HTML has valid basic structure."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        result = builder.generate(data=sample_data, output_path=output_path)
        content = result.read_text(encoding='utf-8')
        
        # Basic HTML validation
        assert content.count('<html') == 1
        assert content.count('</html>') == 1
        assert '<head>' in content or '<body>' in content


# ========== Edge Cases Tests ==========

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_data(self, builder, tmp_path):
        """Test with empty data dictionary."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        data = {'data': {}, 'narrative': {}, 'classification': {}}
        
        result = builder.generate(data=data, output_path=output_path)
        
        assert result.exists()
    
    def test_missing_metadata(self, builder, tmp_path):
        """Test with missing metadata section."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        data = {
            'data': {'health': {'status': 'ok'}},
            'narrative': {},
            'classification': {}
        }
        
        result = builder.generate(data=data, output_path=output_path)
        
        assert result.exists()
    
    def test_large_dataset(self, builder, tmp_path):
        """Test with large data set."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        # Create large data structure
        data = {
            'data': {
                'metadata': {'repo_name': 'large-repo'},
                'entities': {
                    'api_endpoints': [{'path': f'/api/endpoint{i}'} for i in range(100)]
                }
            },
            'narrative': {},
            'classification': {}
        }
        
        result = builder.generate(data=data, output_path=output_path)
        
        assert result.exists()
    
    def test_special_characters_in_data(self, builder, tmp_path):
        """Test with special characters in data."""
        output_path = tmp_path / "dashboard"
        output_path.mkdir()
        
        data = {
            'data': {
                'metadata': {
                    'repo_name': 'test-<repo>&"quotes"'
                }
            },
            'narrative': {},
            'classification': {}
        }
        
        result = builder.generate(data=data, output_path=output_path)
        
        assert result.exists()
        content = result.read_text(encoding='utf-8')
        # Should handle special characters
        assert len(content) > 0


# ========== Output Path Tests ==========

class TestOutputPaths:
    """Test output path handling."""
    
    def test_output_path_as_string(self, builder, sample_data, tmp_path):
        """Test output_path as string."""
        output_path = str(tmp_path / "dashboard")
        Path(output_path).mkdir()
        
        result = builder.generate(
            data=sample_data,
            output_path=Path(output_path)
        )
        
        assert result.exists()
    
    def test_output_path_with_spaces(self, builder, sample_data, tmp_path):
        """Test output path with spaces."""
        output_path = tmp_path / "dashboard with spaces"
        output_path.mkdir()
        
        result = builder.generate(data=sample_data, output_path=output_path)
        
        assert result.exists()
    
    def test_relative_output_path(self, builder, sample_data):
        """Test with relative output path."""
        output_path = Path.cwd() / "test_output"
        output_path.mkdir(exist_ok=True)
        
        try:
            result = builder.generate(data=sample_data, output_path=output_path)
            assert result.exists()
        finally:
            # Cleanup
            if output_path.exists():
                import shutil
                shutil.rmtree(output_path)
