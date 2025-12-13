"""
Tests for dashboard_renderer.py - HTML dashboard generation.

Coverage target: 80%+ (12 tests for 328 LOC)
Focus areas:
- Template rendering
- Data transformation
- Static asset copying
- Jinja2 integration (simple MVP mode)
- Edge cases (missing data, empty datasets)

Author: Asif Hussain
Date: December 2025
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.cortex_lens.generators.dashboard_renderer import DashboardRenderer


# ========== Fixtures ==========

@pytest.fixture
def renderer(tmp_path):
    """Create renderer with mock template directory."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir(parents=True)
    
    # Create mock template files
    (template_dir / "dashboard.html").write_text("""
        <html>
            <head><title>{{ repository_name }}</title></head>
            <body>
                <h1>{{ repository_name }}</h1>
                <div class="health-score {{ health_score_class }}">{{ health_score }}</div>
                <div class="files">{{ total_files }}</div>
                <div class="lines">{{ total_lines }}</div>
                <div class="security">{{ security_issues }}</div>
                <div class="coverage">{{ test_coverage }}</div>
                <div class="repo-type">{{ repo_type_display }}</div>
                <div class="language">{{ primary_language }}</div>
                <script>var analysisData = {{ analysis_data_json }};</script>
            </body>
        </html>
    """, encoding='utf-8')
    
    (template_dir / "cortex-unified.css").write_text("body { margin: 0; }")
    (template_dir / "cortex-unified.js").write_text("console.log('loaded');")
    
    return DashboardRenderer(template_dir=template_dir)


@pytest.fixture
def sample_analysis_data():
    """Complete analysis data structure."""
    return {
        'classification': {
            'repo_type': 'fullstack_web',
            'primary_language': 'Python'
        },
        'health': {
            'total_files': 150,
            'total_lines': 12500,
            'health_score': 85,
            'language_map': {
                'Python': 100,
                'JavaScript': 30,
                'HTML': 20
            }
        },
        'security': {
            'vulnerabilities_found': 3,
            'findings': [
                {
                    'severity': 'HIGH',
                    'type': 'SQL Injection',
                    'file': '/src/db/queries.py',
                    'line': 42,
                    'description': 'Unsafe SQL concatenation'
                }
            ]
        },
        'test_coverage': {
            'coverage_summary': 78.5,
            'total_tests': 120,
            'test_quality_metrics': {
                'avg_assertions_per_test': 2.5
            },
            'tests_by_type': {
                'unit': 80,
                'integration': 40
            }
        },
        'architecture': {
            'patterns': {
                'MVC': 0.85,
                'REST API': 0.72
            },
            'layers': {
                'controller': ['api.py', 'views.py'],
                'model': ['user.py', 'product.py'],
                'service': ['auth.py']
            }
        },
        'complexity': {
            'complexity_summary': {
                'avg_cyclomatic': 4.2,
                'avg_cognitive': 6.1,
                'avg_maintainability': 72.3
            },
            'hotspots': [
                {
                    'name': 'process_order',
                    'file': '/src/orders.py',
                    'cyclomatic': 15,
                    'cognitive': 22,
                    'complexity_rating': 'high'
                }
            ]
        },
        'dependencies': {
            'packages': {
                'django': {'version': '4.2', 'type': 'direct', 'source': 'pypi'},
                'sqlparse': {'version': '0.4.3', 'type': 'transitive', 'source': 'pypi'}
            }
        },
        'tech_stack': {
            'frameworks': ['Django', 'React'],
            'databases': ['PostgreSQL'],
            'build_tools': ['webpack', 'pip']
        },
        'api_endpoints': {
            'endpoints': [
                {'method': 'GET', 'path': '/api/users'},
                {'method': 'POST', 'path': '/api/orders'}
            ]
        },
        'narratives': {
            'use_cases': ['User authentication', 'Order processing'],
            'problem_domain': {'domain': 'E-commerce'},
            'business_flows': ['Checkout flow'],
            'stakeholders': {'primary': 'Customers'},
            'competitive_position': {},
            'risks': ['Payment security'],
            'evolution': {}
        }
    }


# ========== Initialization Tests ==========

class TestInitialization:
    """Test renderer initialization."""
    
    def test_renderer_initialization_with_template_dir(self, tmp_path):
        """Test renderer initializes with custom template directory."""
        template_dir = tmp_path / "custom_templates"
        template_dir.mkdir()
        
        renderer = DashboardRenderer(template_dir=template_dir)
        
        assert renderer.template_dir == template_dir
        assert renderer.template_path == template_dir / 'dashboard.html'
        assert renderer.css_path == template_dir / 'cortex-unified.css'
        assert renderer.js_path == template_dir / 'cortex-unified.js'
        assert renderer.use_simple_rendering is True
    
    def test_renderer_initialization_default_template_dir(self):
        """Test renderer uses default template directory when none specified."""
        renderer = DashboardRenderer()
        
        expected_dir = Path(__file__).parent.parent.parent.parent / 'src' / 'cortex_lens' / 'templates' / 'base'
        assert renderer.template_dir.name == 'base'
        assert renderer.use_simple_rendering is True


# ========== Render Method Tests ==========

class TestRenderMethod:
    """Test main render() method."""
    
    def test_render_creates_dashboard_file(self, renderer, sample_analysis_data, tmp_path):
        """Test render creates dashboard.html file."""
        output_dir = tmp_path / "output"
        
        result = renderer.render(
            analysis_data=sample_analysis_data,
            output_dir=output_dir,
            repository_name="TestRepo"
        )
        
        assert result.exists()
        assert result.name == 'dashboard.html'
        assert result.parent == output_dir
    
    def test_render_creates_output_directory(self, renderer, sample_analysis_data, tmp_path):
        """Test render creates output directory if it doesn't exist."""
        output_dir = tmp_path / "nested" / "output" / "dir"
        
        result = renderer.render(
            analysis_data=sample_analysis_data,
            output_dir=output_dir,
            repository_name="TestRepo"
        )
        
        assert output_dir.exists()
        assert result.exists()
    
    def test_render_injects_repository_name(self, renderer, sample_analysis_data, tmp_path):
        """Test repository name is injected into template."""
        output_dir = tmp_path / "output"
        
        result = renderer.render(
            analysis_data=sample_analysis_data,
            output_dir=output_dir,
            repository_name="MyAwesomeRepo"
        )
        
        content = result.read_text(encoding='utf-8')
        assert 'MyAwesomeRepo' in content
    
    def test_render_injects_health_metrics(self, renderer, sample_analysis_data, tmp_path):
        """Test health metrics are injected correctly."""
        output_dir = tmp_path / "output"
        
        result = renderer.render(
            analysis_data=sample_analysis_data,
            output_dir=output_dir,
            repository_name="TestRepo"
        )
        
        content = result.read_text(encoding='utf-8')
        assert '85' in content  # health_score
        assert '150' in content  # total_files
        assert '12500' in content  # total_lines
        assert '3' in content  # security_issues
        assert '78.5' in content  # test_coverage
    
    def test_render_copies_static_assets(self, renderer, sample_analysis_data, tmp_path):
        """Test CSS and JS files are copied to output directory."""
        output_dir = tmp_path / "output"
        
        renderer.render(
            analysis_data=sample_analysis_data,
            output_dir=output_dir,
            repository_name="TestRepo"
        )
        
        assert (output_dir / 'cortex-unified.css').exists()
        assert (output_dir / 'cortex-unified.js').exists()


# ========== Data Preparation Tests ==========

class TestDataPreparation:
    """Test _prepare_template_data() method."""
    
    def test_prepare_template_data_structure(self, renderer, sample_analysis_data):
        """Test prepared data has all required fields."""
        result = renderer._prepare_template_data(sample_analysis_data, "TestRepo")
        
        # Verify core fields exist
        assert 'repository_name' in result
        assert 'repo_type' in result
        assert 'repo_type_display' in result
        assert 'primary_language' in result
        assert 'analysis_date' in result
        assert 'health_score' in result
        assert 'health_score_class' in result
        assert 'total_files' in result
        assert 'total_lines' in result
        assert 'security_issues' in result
        assert 'test_coverage' in result
    
    def test_health_score_classification(self, renderer, sample_analysis_data):
        """Test health score gets correct CSS class."""
        # Excellent (80+)
        sample_analysis_data['health']['health_score'] = 90
        result = renderer._prepare_template_data(sample_analysis_data, "TestRepo")
        assert result['health_score_class'] == 'excellent'
        
        # Good (60-79)
        sample_analysis_data['health']['health_score'] = 70
        result = renderer._prepare_template_data(sample_analysis_data, "TestRepo")
        assert result['health_score_class'] == 'good'
        
        # Fair (40-59)
        sample_analysis_data['health']['health_score'] = 50
        result = renderer._prepare_template_data(sample_analysis_data, "TestRepo")
        assert result['health_score_class'] == 'fair'
        
        # Poor (<40)
        sample_analysis_data['health']['health_score'] = 30
        result = renderer._prepare_template_data(sample_analysis_data, "TestRepo")
        assert result['health_score_class'] == 'poor'
    
    def test_language_distribution_calculation(self, renderer, sample_analysis_data):
        """Test language percentages are calculated correctly."""
        result = renderer._prepare_template_data(sample_analysis_data, "TestRepo")
        
        languages = result['languages']
        assert len(languages) == 3
        
        # Python should be first (100 files out of 150 = 66.7%)
        assert languages[0]['name'] == 'Python'
        assert languages[0]['percentage'] == pytest.approx(66.7, abs=0.1)
        
        # JavaScript should be second (30 files = 20%)
        assert languages[1]['name'] == 'JavaScript'
        assert languages[1]['percentage'] == 20.0
    
    def test_analysis_data_json_serialization(self, renderer, sample_analysis_data):
        """Test full analysis data is serialized to JSON."""
        result = renderer._prepare_template_data(sample_analysis_data, "TestRepo")
        
        assert 'analysis_data_json' in result
        # Should be valid JSON
        parsed = json.loads(result['analysis_data_json'])
        assert parsed['classification']['primary_language'] == 'Python'


# ========== Edge Cases Tests ==========

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_render_with_empty_analysis_data(self, renderer, tmp_path):
        """Test render handles empty analysis data gracefully."""
        output_dir = tmp_path / "output"
        empty_data = {
            'classification': {},
            'health': {},
            'security': {},
            'test_coverage': {},
            'architecture': {},
            'complexity': {},
            'dependencies': {},
            'tech_stack': {},
            'api_endpoints': {},
            'narratives': {}
        }
        
        result = renderer.render(
            analysis_data=empty_data,
            output_dir=output_dir,
            repository_name="EmptyRepo"
        )
        
        assert result.exists()
        content = result.read_text(encoding='utf-8')
        assert 'EmptyRepo' in content
    
    def test_render_with_missing_sections(self, renderer, tmp_path):
        """Test render handles missing data sections."""
        output_dir = tmp_path / "output"
        minimal_data = {
            'classification': {'repo_type': 'unknown', 'primary_language': 'unknown'}
        }
        
        result = renderer.render(
            analysis_data=minimal_data,
            output_dir=output_dir,
            repository_name="MinimalRepo"
        )
        
        assert result.exists()
    
    def test_static_assets_missing(self, renderer, sample_analysis_data, tmp_path):
        """Test render handles missing static assets gracefully."""
        output_dir = tmp_path / "output"
        
        # Delete static assets
        renderer.css_path.unlink()
        renderer.js_path.unlink()
        
        # Should still create dashboard
        result = renderer.render(
            analysis_data=sample_analysis_data,
            output_dir=output_dir,
            repository_name="TestRepo"
        )
        
        assert result.exists()
        # Assets not copied, but dashboard created
        assert not (output_dir / 'cortex-unified.css').exists()
        assert not (output_dir / 'cortex-unified.js').exists()


# ========== Helper Methods Tests ==========

class TestHelperMethods:
    """Test internal helper methods."""
    
    def test_get_health_score_class_ranges(self, renderer):
        """Test health score classification boundaries."""
        assert renderer._get_health_score_class(100) == 'excellent'
        assert renderer._get_health_score_class(80) == 'excellent'
        assert renderer._get_health_score_class(79) == 'good'
        assert renderer._get_health_score_class(60) == 'good'
        assert renderer._get_health_score_class(59) == 'fair'
        assert renderer._get_health_score_class(40) == 'fair'
        assert renderer._get_health_score_class(39) == 'poor'
        assert renderer._get_health_score_class(0) == 'poor'
    
    def test_format_number_formatting(self, renderer):
        """Test number formatting for display."""
        assert renderer._format_number(999) == '999'
        assert renderer._format_number(1000) == '1.0K'
        assert renderer._format_number(1500) == '1.5K'
        assert renderer._format_number(1_000_000) == '1.0M'
        assert renderer._format_number(2_500_000) == '2.5M'
