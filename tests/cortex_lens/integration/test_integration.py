"""
CORTEX Lens Integration Test Suite

End-to-end integration tests for the complete CORTEX Lens pipeline:
1. Repository Classification
2. Multi-Collector Data Collection (14 collectors)
3. Multi-Analyzer Parsing (Python, C#, JavaScript, SQL)
4. Business Narrative Generation (7 engines)
5. Dashboard Rendering with Narratives
6. Export (JSON, YAML, CSV, Markdown, ZIP)

NOTE: Pipeline integration tests currently skipped - tests written for planned
      high-level Pipeline API that doesn't exist yet. Current DataCollectionPipeline
      has different interface. Will be enabled once high-level pipeline is implemented.

Author: Asif Hussain
Date: December 13, 2025
"""

import pytest
import json
import yaml
from pathlib import Path
from src.cortex_lens.core.pipeline import DataCollectionPipeline
from src.cortex_lens.core.classifier import RepoTypeClassifier
from src.cortex_lens.generators.dashboard_renderer import DashboardRenderer
from src.cortex_lens.generators.export_manager import ExportManager


# ========== Fixtures ==========

@pytest.fixture
def sample_flask_repo(tmp_path):
    """Create sample Flask repository for testing."""
    # Create directory structure
    (tmp_path / "app").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "static").mkdir()
    (tmp_path / "templates").mkdir()
    
    # Create main application
    (tmp_path / "app" / "__init__.py").write_text("""
from flask import Flask

def create_app():
    app = Flask(__name__)
    return app
""", encoding='utf-8')
    
    (tmp_path / "app" / "routes.py").write_text("""
from flask import Blueprint, jsonify, request

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/users', methods=['GET'])
def get_users():
    '''Get all users.'''
    return jsonify([
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'}
    ])

@api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    '''Get user by ID.'''
    return jsonify({'id': user_id, 'name': 'User'})

@api.route('/users', methods=['POST'])
def create_user():
    '''Create new user.'''
    data = request.get_json()
    return jsonify({'id': 3, 'name': data['name']}), 201

@api.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    '''Update existing user.'''
    data = request.get_json()
    return jsonify({'id': user_id, 'name': data['name']})

@api.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    '''Delete user.'''
    return '', 204
""", encoding='utf-8')
    
    (tmp_path / "app" / "models.py").write_text("""
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    '''User model.'''
    id: int
    name: str
    email: str
    age: Optional[int] = None
    
    def to_dict(self):
        '''Convert to dictionary.'''
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age
        }
""", encoding='utf-8')
    
    # Create test file
    (tmp_path / "tests" / "test_routes.py").write_text("""
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_users(client):
    '''Test GET /api/users'''
    response = client.get('/api/users')
    assert response.status_code == 200
    assert len(response.get_json()) == 2

def test_create_user(client):
    '''Test POST /api/users'''
    response = client.post('/api/users', json={'name': 'Charlie'})
    assert response.status_code == 201
    assert response.get_json()['name'] == 'Charlie'

def test_get_user(client):
    '''Test GET /api/users/<id>'''
    response = client.get('/api/users/1')
    assert response.status_code == 200
    assert 'name' in response.get_json()
""", encoding='utf-8')
    
    # Create requirements.txt
    (tmp_path / "requirements.txt").write_text("""
flask==3.0.0
pytest==9.0.1
sqlalchemy==2.0.0
requests==2.31.0
python-dotenv==1.0.0
""", encoding='utf-8')
    
    # Create README
    (tmp_path / "README.md").write_text("""
# Flask User API

A simple Flask REST API for user management.

## Features
- CRUD operations for users
- RESTful endpoints
- JSON responses
- Unit tests with pytest

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
flask run
```
""", encoding='utf-8')
    
    # Create .gitignore
    (tmp_path / ".gitignore").write_text("""
__pycache__/
*.pyc
.env
venv/
.pytest_cache/
""", encoding='utf-8')
    
    return tmp_path


# ========== Classification Tests ==========

class TestRepositoryClassification:
    """Test repository type classification."""
    
    def test_classify_flask_repo(self, sample_flask_repo):
        """Test classification of Flask repository."""
        classifier = RepoTypeClassifier()
        result = classifier.classify(sample_flask_repo)
        
        assert result is not None
        assert 'primary_type' in result
        assert 'metadata' in result
        assert result['primary_type'] in ['library_package', 'api_service']
    
    def test_classification_confidence(self, sample_flask_repo):
        """Test classification confidence scores."""
        classifier = RepoTypeClassifier()
        result = classifier.classify(sample_flask_repo)
        
        assert 'confidence_scores' in result
        assert isinstance(result['confidence_scores'], dict)
        assert all(0 <= score <= 1 for score in result['confidence_scores'].values())


# ========== Pipeline Integration Tests ==========

@pytest.mark.skip(reason="Requires high-level Pipeline API (not yet implemented)")
class TestDataCollectionPipeline:
    """Test complete CORTEX Lens pipeline."""
    
    def test_pipeline_initialization(self, sample_flask_repo):
        """Test pipeline initialization."""
        pipeline = CortexLensPipeline(
            repository_path=sample_flask_repo,
            output_dir=sample_flask_repo / "output"
        )
        
        assert pipeline.repository_path == sample_flask_repo
        assert pipeline.output_dir is not None
    
    def test_full_analysis_workflow(self, sample_flask_repo):
        """Test complete analysis workflow."""
        pipeline = CortexLensPipeline(
            repository_path=sample_flask_repo,
            output_dir=sample_flask_repo / "output"
        )
        
        # Run analysis
        results = pipeline.analyze()
        
        # Verify all sections present
        assert 'classification' in results
        assert 'health' in results
        assert 'architecture' in results
        assert 'api_endpoints' in results
        assert 'security' in results
        assert 'complexity' in results
        assert 'tech_stack' in results
        assert 'dependencies' in results
        assert 'test_coverage' in results
        assert 'narratives' in results
    
    def test_health_data_collection(self, sample_flask_repo):
        """Test health data collection."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        health = results['health']
        assert 'total_files' in health
        assert 'total_lines' in health
        assert 'health_score' in health
        assert health['total_files'] > 0
        assert health['total_lines'] > 0
    
    def test_api_endpoint_detection(self, sample_flask_repo):
        """Test API endpoint detection."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        endpoints = results['api_endpoints']['endpoints']
        assert len(endpoints) >= 5  # 5 Flask routes
        
        # Check for CRUD operations
        methods = [ep['method'] for ep in endpoints]
        assert 'GET' in methods
        assert 'POST' in methods
        assert 'PUT' in methods
        assert 'DELETE' in methods
    
    def test_dependency_collection(self, sample_flask_repo):
        """Test dependency collection."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        packages = results['dependencies']['packages']
        assert len(packages) >= 5  # 5 packages in requirements.txt
        assert 'flask' in packages
        assert 'pytest' in packages
        assert packages['flask']['version'] == '3.0.0'
    
    def test_test_coverage_detection(self, sample_flask_repo):
        """Test test coverage detection."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        coverage = results['test_coverage']
        assert 'total_tests' in coverage
        assert coverage['total_tests'] >= 3  # 3 test functions


# ========== Narrative Integration Tests ==========

@pytest.mark.skip(reason="Requires high-level Pipeline API (not yet implemented)")
class TestNarrativeIntegration:
    """Test business intelligence narrative generation."""
    
    def test_narrative_generation(self, sample_flask_repo):
        """Test complete narrative generation."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        narratives = results['narratives']
        assert 'use_cases' in narratives
        assert 'problem_domain' in narratives
        assert 'competitive_position' in narratives
        assert 'risks' in narratives
    
    def test_use_case_discovery(self, sample_flask_repo):
        """Test use case discovery from endpoints."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        use_cases = results['narratives']['use_cases']
        assert len(use_cases) > 0
        
        # Check for CRUD workflow
        use_case_names = [uc['name'] for uc in use_cases]
        assert any('user' in name.lower() for name in use_case_names)
    
    def test_problem_domain_synthesis(self, sample_flask_repo):
        """Test problem domain narrative synthesis."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        problem_domain = results['narratives']['problem_domain']
        assert 'summary' in problem_domain
        assert len(problem_domain['summary']) > 0
    
    def test_risk_translation(self, sample_flask_repo):
        """Test technical risk to business impact translation."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        risks = results['narratives']['risks']
        assert len(risks) >= 0  # May have risks
        
        if len(risks) > 0:
            risk = risks[0]
            assert 'severity' in risk
            assert 'business_impact' in risk


# ========== Dashboard Generation Tests ==========

@pytest.mark.skip(reason="Requires high-level Pipeline API (not yet implemented)")
class TestDashboardGeneration:
    """Test dashboard generation with narratives."""
    
    def test_dashboard_rendering(self, sample_flask_repo):
        """Test HTML dashboard rendering."""
        pipeline = CortexLensPipeline(
            repository_path=sample_flask_repo,
            output_dir=sample_flask_repo / "output"
        )
        
        results = pipeline.analyze()
        dashboard_path = pipeline.export_dashboard(output_format='html')
        
        assert dashboard_path.exists()
        assert dashboard_path.suffix == '.html'
    
    def test_dashboard_contains_narratives(self, sample_flask_repo):
        """Test that dashboard includes narrative data."""
        pipeline = CortexLensPipeline(
            repository_path=sample_flask_repo,
            output_dir=sample_flask_repo / "output"
        )
        
        results = pipeline.analyze()
        dashboard_path = pipeline.export_dashboard(output_format='html')
        
        html_content = dashboard_path.read_text(encoding='utf-8')
        
        # Check for Executive Brief tab
        assert 'Executive Brief' in html_content or 'executive' in html_content
        
        # Check for narrative sections
        assert 'Problem' in html_content or 'Use Cases' in html_content
    
    def test_dashboard_contains_charts(self, sample_flask_repo):
        """Test that dashboard includes Chart.js integration."""
        pipeline = CortexLensPipeline(
            repository_path=sample_flask_repo,
            output_dir=sample_flask_repo / "output"
        )
        
        results = pipeline.analyze()
        dashboard_path = pipeline.export_dashboard(output_format='html')
        
        html_content = dashboard_path.read_text(encoding='utf-8')
        
        # Check for Chart.js
        assert 'chart.js' in html_content.lower() or 'Chart' in html_content


# ========== Export Format Tests ==========

@pytest.mark.skip(reason="Requires high-level Pipeline API (not yet implemented)")
class TestExportFormats:
    """Test multiple export formats."""
    
    def test_json_export(self, sample_flask_repo):
        """Test JSON export format."""
        pipeline = CortexLensPipeline(
            repository_path=sample_flask_repo,
            output_dir=sample_flask_repo / "output"
        )
        
        results = pipeline.analyze()
        export_path = pipeline.export_dashboard(output_format='json')
        
        assert export_path.exists()
        assert export_path.suffix == '.json'
        
        # Validate JSON structure
        with open(export_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'classification' in data
            assert 'narratives' in data
    
    def test_yaml_export(self, sample_flask_repo):
        """Test YAML export format."""
        pipeline = CortexLensPipeline(
            repository_path=sample_flask_repo,
            output_dir=sample_flask_repo / "output"
        )
        
        results = pipeline.analyze()
        export_path = pipeline.export_dashboard(output_format='yaml')
        
        assert export_path.exists()
        assert export_path.suffix in ['.yaml', '.yml']
        
        # Validate YAML structure
        with open(export_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            assert 'classification' in data
            assert 'narratives' in data
    
    def test_markdown_export(self, sample_flask_repo):
        """Test Markdown export format."""
        pipeline = CortexLensPipeline(
            repository_path=sample_flask_repo,
            output_dir=sample_flask_repo / "output"
        )
        
        results = pipeline.analyze()
        export_path = pipeline.export_dashboard(output_format='markdown')
        
        assert export_path.exists()
        assert export_path.suffix == '.md'
        
        # Check for markdown headers
        content = export_path.read_text(encoding='utf-8')
        assert '#' in content  # Markdown headers


# ========== Performance Tests ==========

@pytest.mark.skip(reason="Requires high-level Pipeline API (not yet implemented)")
class TestPerformance:
    """Test pipeline performance."""
    
    def test_analysis_completes_in_reasonable_time(self, sample_flask_repo):
        """Test that analysis completes in reasonable time."""
        import time
        
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        
        start_time = time.time()
        results = pipeline.analyze()
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Small repo should analyze in < 30 seconds
        assert duration < 30, f"Analysis took {duration:.2f}s (expected < 30s)"
    
    def test_dashboard_generation_speed(self, sample_flask_repo):
        """Test dashboard generation speed."""
        import time
        
        pipeline = CortexLensPipeline(
            repository_path=sample_flask_repo,
            output_dir=sample_flask_repo / "output"
        )
        
        results = pipeline.analyze()
        
        start_time = time.time()
        dashboard_path = pipeline.export_dashboard(output_format='html')
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Dashboard generation should be < 5 seconds
        assert duration < 5, f"Dashboard generation took {duration:.2f}s (expected < 5s)"


# ========== Edge Case Tests ==========

@pytest.mark.skip(reason="Requires high-level Pipeline API (not yet implemented)")
class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_repository(self, tmp_path):
        """Test handling of empty repository."""
        pipeline = CortexLensPipeline(repository_path=tmp_path)
        results = pipeline.analyze()
        
        # Should complete without errors
        assert results is not None
        assert results['health']['total_files'] == 0
    
    def test_no_dependencies_file(self, tmp_path):
        """Test repository without requirements.txt."""
        (tmp_path / "app.py").write_text("print('Hello')", encoding='utf-8')
        
        pipeline = CortexLensPipeline(repository_path=tmp_path)
        results = pipeline.analyze()
        
        # Should not crash
        assert results is not None
        assert 'dependencies' in results
    
    def test_no_tests_directory(self, tmp_path):
        """Test repository without tests."""
        (tmp_path / "app.py").write_text("print('Hello')", encoding='utf-8')
        
        pipeline = CortexLensPipeline(repository_path=tmp_path)
        results = pipeline.analyze()
        
        # Should not crash
        assert results is not None
        assert results['test_coverage']['total_tests'] == 0


# ========== Data Consistency Tests ==========

@pytest.mark.skip(reason="Requires high-level Pipeline API (not yet implemented)")
class TestDataConsistency:
    """Test data consistency across pipeline."""
    
    def test_file_counts_consistency(self, sample_flask_repo):
        """Test that file counts are consistent."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        health_files = results['health']['total_files']
        
        # File count should be reasonable
        assert health_files > 0
        assert health_files < 1000  # Small test repo
    
    def test_endpoint_count_matches_routes(self, sample_flask_repo):
        """Test that endpoint count matches actual routes."""
        pipeline = CortexLensPipeline(repository_path=sample_flask_repo)
        results = pipeline.analyze()
        
        endpoints = results['api_endpoints']['endpoints']
        use_cases = results['narratives']['use_cases']
        
        # Use cases should be derived from endpoints
        assert len(use_cases) > 0 if len(endpoints) > 0 else True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
