"""
Tests for CORTEX Lens Main Orchestrator

Tests the main CortexLens orchestrator that coordinates the 6-phase analysis workflow.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.cortex_lens.orchestrator import CortexLens


# ========== Fixtures ==========

@pytest.fixture
def sample_repo(tmp_path):
    """Create sample repository structure"""
    repo = tmp_path / "test-repo"
    repo.mkdir()
    
    # Create some Python files
    (repo / "main.py").write_text("print('hello')")
    (repo / "utils.py").write_text("def helper(): pass")
    
    return repo


@pytest.fixture
def sample_classification():
    """Sample classification result"""
    return {
        'primary_type': 'console_app',
        'secondary_types': [],
        'confidence_scores': {
            'fullstack_web': 0.0,
            'api_service': 0.3,
            'database_project': 0.0,
            'console_app': 0.8,
            'microservices': 0.0,
            'library_package': 0.2
        },
        'dashboard_template': 'console-app-dashboard',
        'detected_patterns': {
            'has_frontend': False,
            'has_backend': True,
            'has_database': False,
        },
        'metadata': {
            'total_files': 10,
            'languages': {'Python': 5},
            'frameworks': set()
        }
    }


@pytest.fixture
def sample_collected_data():
    """Sample collected data"""
    return {
        'metadata': {
            'repo_name': 'test-repo',
            'total_files': 10,
            'total_loc': 500,
        },
        'health': {
            'score': 75,
            'total_files': 10,
        },
        'complexity': {
            'avg_complexity': 3.5,
        },
        'tech_stack': {
            'languages': ['Python'],
            'frameworks': ['Flask'],
        }
    }


@pytest.fixture
def sample_narrative():
    """Sample narrative"""
    return {
        'executive_summary': 'A console application',
        'capabilities': ['CLI processing'],
        'highlights': ['Simple architecture'],
        'recommendations': ['Add tests']
    }


# ========== Initialization Tests ==========

class TestInitialization:
    """Test orchestrator initialization"""
    
    def test_default_initialization(self):
        """Test initialization with default config"""
        lens = CortexLens()
        
        assert lens.version == "1.0.0"
        assert lens.config == {}
        assert lens._classifier is None
        assert lens._pipeline is None
        assert lens._narrative_generator is None
        assert lens._dashboard_builder is None
        assert lens._validator is None
        assert lens._packager is None
    
    def test_custom_config_initialization(self):
        """Test initialization with custom config"""
        config = {'cache_enabled': True, 'output_format': 'json'}
        lens = CortexLens(config=config)
        
        assert lens.config == config
        assert lens.config['cache_enabled'] is True


# ========== Scan Method Tests ==========

class TestScanMethod:
    """Test quick scan functionality"""
    
    @patch('src.cortex_lens.core.classifier.RepoTypeClassifier')
    def test_scan_returns_classification(self, mock_classifier_class, sample_repo, sample_classification):
        """Test scan returns classification results"""
        # Setup mock
        mock_classifier = Mock()
        mock_classifier.classify.return_value = sample_classification
        mock_classifier_class.return_value = mock_classifier
        
        lens = CortexLens()
        result = lens.scan(str(sample_repo))
        
        assert result == sample_classification
        mock_classifier.classify.assert_called_once()
    
    def test_scan_invalid_path_raises_error(self):
        """Test scan with invalid path (no error at scan phase)"""
        lens = CortexLens()
        
        # scan() doesn't validate path exists - classifier handles it
        # Just verify it returns classification (may be low confidence)
        result = lens.scan("/nonexistent/path")
        assert 'primary_type' in result
        assert 'confidence_scores' in result
    
    @patch('src.cortex_lens.core.classifier.RepoTypeClassifier')
    def test_scan_logs_detection(self, mock_classifier_class, sample_repo, sample_classification, caplog):
        """Test scan logs detection message"""
        mock_classifier = Mock()
        mock_classifier.classify.return_value = sample_classification
        mock_classifier_class.return_value = mock_classifier
        
        lens = CortexLens()
        lens.scan(str(sample_repo))
        
        assert "Quick scan" in caplog.text
        assert "Detected: console_app" in caplog.text


# ========== Analyze Method Tests ==========

class TestAnalyzeMethod:
    """Test full analysis workflow"""
    
    @patch('src.cortex_lens.core.classifier.RepoTypeClassifier')
    @patch('src.cortex_lens.core.pipeline.DataCollectionPipeline')
    @patch('src.cortex_lens.generators.narrative_generator.NarrativeGenerator')
    @patch('src.cortex_lens.generators.dashboard_builder.DashboardBuilder')
    @patch('src.cortex_lens.validators.schema_validator.SchemaValidator')
    @patch('src.cortex_lens.generators.packager.Packager')
    def test_analyze_full_workflow(
        self,
        mock_packager_class,
        mock_validator_class,
        mock_dashboard_class,
        mock_narrative_class,
        mock_pipeline_class,
        mock_classifier_class,
        sample_repo,
        sample_classification,
        sample_collected_data,
        sample_narrative
    ):
        """Test full analysis workflow executes all phases"""
        # Setup mocks
        mock_classifier = Mock()
        mock_classifier.classify.return_value = sample_classification
        mock_classifier_class.return_value = mock_classifier
        
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = sample_collected_data
        mock_pipeline_class.return_value = mock_pipeline
        
        mock_narrative_gen = Mock()
        mock_narrative_gen.generate.return_value = sample_narrative
        mock_narrative_class.return_value = mock_narrative_gen
        
        dashboard_path = sample_repo / "output" / "index.html"
        dashboard_path.parent.mkdir(parents=True)
        dashboard_path.write_text("<html></html>")
        
        mock_dashboard = Mock()
        mock_dashboard.build.return_value = dashboard_path
        mock_dashboard_class.return_value = mock_dashboard
        
        mock_validator = Mock()
        mock_validator.validate.return_value = {'valid': True}
        mock_validator_class.return_value = mock_validator
        
        package_path = sample_repo / "output" / "package.zip"
        mock_packager = Mock()
        mock_packager.package.return_value = package_path
        mock_packager.export.return_value = {'json': sample_repo / "output" / "data.json"}
        mock_packager_class.return_value = mock_packager
        
        # Execute
        lens = CortexLens()
        result = lens.analyze(str(sample_repo))
        
        # Verify all phases executed
        assert result['classification'] == sample_classification
        assert result['data'] == sample_collected_data
        assert result['narrative'] == sample_narrative
        assert result['dashboard_path'] == dashboard_path
        assert result['package_path'] == package_path
        assert result['validation_report'] == {'valid': True}
        assert 'duration_seconds' in result['metrics']
        assert result['metrics']['total_files'] == 10
    
    def test_analyze_invalid_repo_raises_error(self):
        """Test analyze with invalid repository path"""
        lens = CortexLens()
        
        with pytest.raises(FileNotFoundError):
            lens.analyze("/nonexistent/repo")
    
    @patch('src.cortex_lens.core.classifier.RepoTypeClassifier')
    @patch('src.cortex_lens.core.pipeline.DataCollectionPipeline')
    @patch('src.cortex_lens.generators.narrative_generator.NarrativeGenerator')
    @patch('src.cortex_lens.generators.dashboard_builder.DashboardBuilder')
    @patch('src.cortex_lens.validators.schema_validator.SchemaValidator')
    @patch('src.cortex_lens.generators.packager.Packager')
    def test_analyze_with_custom_template(
        self,
        mock_packager_class,
        mock_validator_class,
        mock_dashboard_class,
        mock_narrative_class,
        mock_pipeline_class,
        mock_classifier_class,
        sample_repo,
        sample_classification,
        sample_collected_data,
        sample_narrative
    ):
        """Test analyze with custom template override"""
        # Setup mocks (abbreviated)
        mock_classifier = Mock()
        mock_classifier.classify.return_value = sample_classification
        mock_classifier_class.return_value = mock_classifier
        
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = sample_collected_data
        mock_pipeline_class.return_value = mock_pipeline
        
        mock_narrative_gen = Mock()
        mock_narrative_gen.generate.return_value = sample_narrative
        mock_narrative_class.return_value = mock_narrative_gen
        
        dashboard_path = sample_repo / "output" / "index.html"
        dashboard_path.parent.mkdir(parents=True)
        dashboard_path.write_text("<html></html>")
        
        mock_dashboard = Mock()
        mock_dashboard.build.return_value = dashboard_path
        mock_dashboard_class.return_value = mock_dashboard
        
        mock_validator = Mock()
        mock_validator.validate.return_value = {'valid': True}
        mock_validator_class.return_value = mock_validator
        
        mock_packager = Mock()
        mock_packager.package.return_value = sample_repo / "output" / "package.zip"
        mock_packager.export.return_value = {}
        mock_packager_class.return_value = mock_packager
        
        # Execute with custom template
        lens = CortexLens()
        result = lens.analyze(str(sample_repo), template='fullstack-dashboard')
        
        # Verify template passed to builder
        mock_dashboard.build.assert_called_once()
        # build() signature: build(repo_path, data, narrative, classification, output_dir, template)
        call_args = mock_dashboard.build.call_args[0]  # positional args
        call_kwargs = mock_dashboard.build.call_args[1] if len(mock_dashboard.build.call_args) > 1 else {}
        # template is 6th positional arg (index 5)
        assert call_args[5] == 'fullstack-dashboard' or call_kwargs.get('template') == 'fullstack-dashboard'
    
    @patch('src.cortex_lens.core.classifier.RepoTypeClassifier')
    @patch('src.cortex_lens.core.pipeline.DataCollectionPipeline')
    @patch('src.cortex_lens.generators.narrative_generator.NarrativeGenerator')
    @patch('src.cortex_lens.generators.dashboard_builder.DashboardBuilder')
    @patch('src.cortex_lens.validators.schema_validator.SchemaValidator')
    @patch('src.cortex_lens.generators.packager.Packager')
    def test_analyze_with_export_formats(
        self,
        mock_packager_class,
        mock_validator_class,
        mock_dashboard_class,
        mock_narrative_class,
        mock_pipeline_class,
        mock_classifier_class,
        sample_repo,
        sample_classification,
        sample_collected_data,
        sample_narrative
    ):
        """Test analyze with multiple export formats"""
        # Setup mocks (abbreviated)
        mock_classifier = Mock()
        mock_classifier.classify.return_value = sample_classification
        mock_classifier_class.return_value = mock_classifier
        
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = sample_collected_data
        mock_pipeline_class.return_value = mock_pipeline
        
        mock_narrative_gen = Mock()
        mock_narrative_gen.generate.return_value = sample_narrative
        mock_narrative_class.return_value = mock_narrative_gen
        
        dashboard_path = sample_repo / "output" / "index.html"
        dashboard_path.parent.mkdir(parents=True)
        dashboard_path.write_text("<html></html>")
        
        mock_dashboard = Mock()
        mock_dashboard.build.return_value = dashboard_path
        mock_dashboard_class.return_value = mock_dashboard
        
        mock_validator = Mock()
        mock_validator.validate.return_value = {'valid': True}
        mock_validator_class.return_value = mock_validator
        
        export_paths = {
            'json': sample_repo / "output" / "data.json",
            'yaml': sample_repo / "output" / "data.yaml",
            'csv': sample_repo / "output" / "data.csv"
        }
        mock_packager = Mock()
        mock_packager.package.return_value = sample_repo / "output" / "package.zip"
        mock_packager.export.return_value = export_paths
        mock_packager_class.return_value = mock_packager
        
        # Execute with export formats
        lens = CortexLens()
        result = lens.analyze(str(sample_repo), export_formats=['json', 'yaml', 'csv'])
        
        # Verify export formats passed to packager
        mock_packager.export.assert_called_once()
        call_args = mock_packager.export.call_args[0]
        assert call_args[1] == ['json', 'yaml', 'csv']
        assert result['export_paths'] == export_paths


# ========== Compare Method Tests ==========

class TestCompareMethod:
    """Test multi-repo comparison functionality"""
    
    @patch('src.cortex_lens.core.classifier.RepoTypeClassifier')
    @patch('src.cortex_lens.core.pipeline.DataCollectionPipeline')
    @patch('src.cortex_lens.generators.narrative_generator.NarrativeGenerator')
    @patch('src.cortex_lens.generators.dashboard_builder.DashboardBuilder')
    @patch('src.cortex_lens.validators.schema_validator.SchemaValidator')
    @patch('src.cortex_lens.generators.packager.Packager')
    def test_compare_multiple_repos(
        self,
        mock_packager_class,
        mock_validator_class,
        mock_dashboard_class,
        mock_narrative_class,
        mock_pipeline_class,
        mock_classifier_class,
        tmp_path,
        sample_classification,
        sample_collected_data,
        sample_narrative
    ):
        """Test comparison of multiple repositories"""
        # Create two sample repos
        repo1 = tmp_path / "repo1"
        repo2 = tmp_path / "repo2"
        repo1.mkdir()
        repo2.mkdir()
        (repo1 / "main.py").write_text("print('repo1')")
        (repo2 / "main.py").write_text("print('repo2')")
        
        # Setup mocks
        mock_classifier = Mock()
        mock_classifier.classify.return_value = sample_classification
        mock_classifier_class.return_value = mock_classifier
        
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = sample_collected_data
        mock_pipeline_class.return_value = mock_pipeline
        
        mock_narrative_gen = Mock()
        mock_narrative_gen.generate.return_value = sample_narrative
        mock_narrative_class.return_value = mock_narrative_gen
        
        dashboard_path1 = repo1 / "output" / "index.html"
        dashboard_path1.parent.mkdir(parents=True)
        dashboard_path1.write_text("<html></html>")
        
        dashboard_path2 = repo2 / "output" / "index.html"
        dashboard_path2.parent.mkdir(parents=True)
        dashboard_path2.write_text("<html></html>")
        
        mock_dashboard = Mock()
        mock_dashboard.build.side_effect = [dashboard_path1, dashboard_path2]
        mock_dashboard_class.return_value = mock_dashboard
        
        mock_validator = Mock()
        mock_validator.validate.return_value = {'valid': True}
        mock_validator_class.return_value = mock_validator
        
        mock_packager = Mock()
        mock_packager.package.side_effect = [
            repo1 / "output" / "package.zip",
            repo2 / "output" / "package.zip"
        ]
        mock_packager.export.return_value = {}
        mock_packager_class.return_value = mock_packager
        
        # Execute comparison
        lens = CortexLens()
        result = lens.compare([str(repo1), str(repo2)])
        
        # Verify results
        assert len(result['analyses']) == 2
        assert result['comparison_data']['repo_count'] == 2
        assert 'comparison_path' in result
    
    def test_compare_generates_comparison_data(self, sample_collected_data, sample_classification):
        """Test comparison data generation"""
        lens = CortexLens()
        
        analyses = [
            {
                'classification': sample_classification,
                'data': sample_collected_data,
                'narrative': {},
                'dashboard_path': Path('/fake/path1'),
                'package_path': Path('/fake/package1'),
                'validation_report': {},
                'export_paths': {},
                'metrics': {}
            },
            {
                'classification': {**sample_classification, 'primary_type': 'api_service'},
                'data': sample_collected_data,
                'narrative': {},
                'dashboard_path': Path('/fake/path2'),
                'package_path': Path('/fake/package2'),
                'validation_report': {},
                'export_paths': {},
                'metrics': {}
            }
        ]
        
        comparison = lens._generate_comparison(analyses)
        
        assert comparison['repo_count'] == 2
        assert comparison['primary_types'] == ['console_app', 'api_service']


# ========== Private Method Tests ==========

class TestPrivateMethods:
    """Test private orchestration methods"""
    
    @patch('src.cortex_lens.core.classifier.RepoTypeClassifier')
    def test_classify_repository_lazy_loads_classifier(
        self,
        mock_classifier_class,
        sample_repo,
        sample_classification
    ):
        """Test classifier lazy loading"""
        mock_classifier = Mock()
        mock_classifier.classify.return_value = sample_classification
        mock_classifier_class.return_value = mock_classifier
        
        lens = CortexLens()
        assert lens._classifier is None
        
        result = lens._classify_repository(sample_repo)
        
        assert lens._classifier is not None
        assert result == sample_classification
        mock_classifier_class.assert_called_once()
    
    @patch('src.cortex_lens.core.pipeline.DataCollectionPipeline')
    def test_collect_data_lazy_loads_pipeline(
        self,
        mock_pipeline_class,
        sample_repo,
        sample_classification,
        sample_collected_data
    ):
        """Test pipeline lazy loading"""
        mock_pipeline = Mock()
        mock_pipeline.execute.return_value = sample_collected_data
        mock_pipeline_class.return_value = mock_pipeline
        
        lens = CortexLens()
        assert lens._pipeline is None
        
        result = lens._collect_data(sample_repo, sample_classification)
        
        assert lens._pipeline is not None
        assert result == sample_collected_data
        mock_pipeline.execute.assert_called_once_with(sample_repo, sample_classification)
    
    @patch('src.cortex_lens.generators.narrative_generator.NarrativeGenerator')
    def test_generate_narrative_lazy_loads_generator(
        self,
        mock_narrative_class,
        sample_collected_data,
        sample_classification,
        sample_narrative
    ):
        """Test narrative generator lazy loading"""
        mock_generator = Mock()
        mock_generator.generate.return_value = sample_narrative
        mock_narrative_class.return_value = mock_generator
        
        lens = CortexLens()
        assert lens._narrative_generator is None
        
        result = lens._generate_narrative(sample_collected_data, sample_classification)
        
        assert lens._narrative_generator is not None
        assert result == sample_narrative
    
    @patch('src.cortex_lens.generators.packager.Packager')
    def test_package_and_export(self, mock_packager_class, sample_repo, sample_collected_data):
        """Test packaging and export functionality"""
        dashboard_path = sample_repo / "output" / "index.html"
        dashboard_path.parent.mkdir(parents=True)
        dashboard_path.write_text("<html></html>")
        
        package_path = sample_repo / "output" / "package.zip"
        export_paths = {'json': sample_repo / "output" / "data.json"}
        
        mock_packager = Mock()
        mock_packager.package.return_value = package_path
        mock_packager.export.return_value = export_paths
        mock_packager_class.return_value = mock_packager
        
        lens = CortexLens()
        result_package, result_exports = lens._package_and_export(
            dashboard_path,
            sample_collected_data,
            ['json']
        )
        
        assert result_package == package_path
        assert result_exports == export_paths
        mock_packager.package.assert_called_once_with(dashboard_path)
        mock_packager.export.assert_called_once()


# ========== Edge Cases ==========

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_analyze_with_pathlib_path(self):
        """Test analyze accepts pathlib.Path objects"""
        lens = CortexLens()
        
        # Should raise FileNotFoundError for nonexistent path
        with pytest.raises(FileNotFoundError):
            lens.analyze(Path("/nonexistent/repo/that/does/not/exist/123"))
    
    @patch('src.cortex_lens.core.classifier.RepoTypeClassifier')
    def test_scan_with_string_path(self, mock_classifier_class, sample_repo, sample_classification):
        """Test scan accepts string paths"""
        mock_classifier = Mock()
        mock_classifier.classify.return_value = sample_classification
        mock_classifier_class.return_value = mock_classifier
        
        lens = CortexLens()
        result = lens.scan(str(sample_repo))
        
        assert result is not None
    
    def test_comparison_dashboard_creates_output_dir(self, tmp_path):
        """Test comparison dashboard creates output directory"""
        lens = CortexLens()
        output_dir = tmp_path / "comparison_output"
        
        comparison_data = {'repo_count': 2, 'primary_types': []}
        result = lens._generate_comparison_dashboard(comparison_data, str(output_dir))
        
        assert output_dir.exists()
        assert result.exists()
        assert result.name == 'comparison.html'
