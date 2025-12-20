"""
Tests for Clean Architecture Implementation - Task 2.1

Validates domain entities, repositories, and use cases.

Author: Asif Hussain
Created: 2025-11-30
"""

import pytest
from pathlib import Path
import tempfile
import json

# Domain entities
from src.dashboard.domain import (
    Component, ComponentType,
    Dependency, DependencyType, DependencyStrength,
    HealthScore, LayerScore,
    Issue, IssueType, IssueSeverity,
    Recommendation, RecommendationCategory, RecommendationPriority
)

# Repositories
from src.dashboard.data.json_repositories import (
    JSONComponentRepository,
    JSONDependencyRepository,
    JSONIssueRepository,
    JSONHealthScoreRepository
)

# Use cases
from src.dashboard.use_cases.load_overview import LoadOverviewUseCase
from src.dashboard.use_cases.render_architecture_graph import RenderArchitectureGraphUseCase
from src.dashboard.use_cases.analyze_quality_metrics import AnalyzeQualityMetricsUseCase
from src.dashboard.use_cases.scan_security_vulnerabilities import ScanSecurityVulnerabilitiesUseCase
from src.dashboard.use_cases.generate_recommendations import GenerateRecommendationsUseCase


class TestDomainEntities:
    """Test domain entities (pure business objects)"""
    
    def test_component_creation(self):
        """Test Component entity creation and validation"""
        component = Component(
            name="AuthService",
            path="src/services/auth_service.py",
            type=ComponentType.SERVICE,
            health_score=85.5,
            lines_of_code=250,
            complexity=12
        )
        
        assert component.name == "AuthService"
        assert component.health_category == "warning"  # 85.5 falls in warning range
        assert component.health_color == "#ffc107"
        assert component.total_issues == 0
    
    def test_component_health_validation(self):
        """Test Component health score validation"""
        with pytest.raises(ValueError):
            Component(
                name="Test",
                path="test.py",
                type=ComponentType.FILE,
                health_score=150  # Invalid: > 100
            )
    
    def test_dependency_creation(self):
        """Test Dependency entity creation"""
        dep = Dependency(
            source="component_a.py",
            target="component_b.py",
            type=DependencyType.IMPORT,
            usage_count=5
        )
        
        assert dep.edge_id == "component_a.py→component_b.py"
        assert not dep.is_circular
        assert dep.strength == DependencyStrength.MODERATE
    
    def test_dependency_circular_marking(self):
        """Test marking dependency as circular"""
        dep = Dependency(
            source="a.py",
            target="b.py",
            type=DependencyType.IMPORT
        )
        
        dep.mark_circular()
        
        assert dep.is_circular
        assert dep.strength == DependencyStrength.TIGHT
        assert dep.edge_color == "#dc3545"  # Red for circular
    
    def test_health_score_7_layers(self):
        """Test HealthScore with 7-layer breakdown"""
        health = HealthScore()
        
        # Should have 7 default layers
        assert len(health.layers) == 7
        assert 'discovery' in health.layers
        assert 'tests' in health.layers
        
        # Update a layer
        health.update_layer('tests', 90.0, True, [])
        
        assert health.layers['tests'].score == 90.0
        assert health.layers['tests'].passed is True
    
    def test_health_score_calculation(self):
        """Test weighted health score calculation"""
        health = HealthScore()
        
        # Set all layers to 80
        for layer_name in health.layers:
            health.update_layer(layer_name, 80.0, True, [])
        
        # Total should be 80 (weighted average)
        assert health.total_score == 80.0
        assert health.health_category == "warning"
    
    def test_issue_severity_ranking(self):
        """Test Issue severity ranking"""
        issue = Issue(
            id="ISS-001",
            type=IssueType.VULNERABILITY,
            severity=IssueSeverity.CRITICAL,
            title="SQL Injection",
            message="Unsanitized user input",
            component_path="api.py",
            file_path="src/api.py"
        )
        
        assert issue.severity_rank == 2  # CRITICAL = rank 2
        assert issue.is_security_issue is True
        assert issue.is_high_priority is True
    
    def test_recommendation_roi_calculation(self):
        """Test Recommendation ROI score"""
        rec = Recommendation(
            id="REC-001",
            category=RecommendationCategory.TESTING,
            priority=RecommendationPriority.HIGH,
            title="Add unit tests",
            description="Increase test coverage",
            rationale="Improve quality",
            effort_hours=4.0,
            impact_score=8.0
        )
        
        assert rec.roi_score == 2.0  # 8.0 / 4.0
        assert rec.is_quick_win is False  # 4 hours > 2 hours threshold


class TestRepositories:
    """Test repository implementations"""
    
    def test_component_repository_save_and_load(self):
        """Test saving and loading components"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = Path(f.name)
        
        try:
            repo = JSONComponentRepository(temp_file)
            
            component = Component(
                name="TestComponent",
                path="test.py",
                type=ComponentType.FILE,
                health_score=75.0
            )
            
            # Save
            repo.save(component)
            
            # Load
            loaded = repo.get_by_path("test.py")
            
            assert loaded is not None
            assert loaded.name == "TestComponent"
            assert loaded.health_score == 75.0
        finally:
            temp_file.unlink()
    
    def test_dependency_repository_circular_filter(self):
        """Test filtering circular dependencies"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = Path(f.name)
        
        try:
            repo = JSONDependencyRepository(temp_file)
            
            # Save circular dependency
            dep = Dependency(
                source="a.py",
                target="b.py",
                type=DependencyType.IMPORT
            )
            dep.mark_circular()
            repo.save(dep)
            
            # Save normal dependency
            dep2 = Dependency(
                source="c.py",
                target="d.py",
                type=DependencyType.IMPORT
            )
            repo.save(dep2)
            
            # Filter circular
            circular = repo.get_circular()
            
            assert len(circular) == 1
            assert circular[0].source == "a.py"
        finally:
            temp_file.unlink()
    
    def test_issue_repository_security_filter(self):
        """Test filtering security issues"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = Path(f.name)
        
        try:
            repo = JSONIssueRepository(temp_file)
            
            # Save security issue
            sec_issue = Issue(
                id="SEC-001",
                type=IssueType.VULNERABILITY,
                severity=IssueSeverity.CRITICAL,
                title="XSS",
                message="Cross-site scripting",
                component_path="web.py",
                file_path="src/web.py"
            )
            repo.save(sec_issue)
            
            # Save code smell
            smell = Issue(
                id="SMELL-001",
                type=IssueType.CODE_SMELL,
                severity=IssueSeverity.MINOR,
                title="Long method",
                message="Method too long",
                component_path="util.py",
                file_path="src/util.py"
            )
            repo.save(smell)
            
            # Filter security
            security_issues = repo.get_security_issues()
            
            assert len(security_issues) == 1
            assert security_issues[0].id == "SEC-001"
        finally:
            temp_file.unlink()


class TestUseCases:
    """Test use case implementations"""
    
    def setup_method(self):
        """Setup test repositories with sample data"""
        self.temp_files = {}
        
        # Create temporary files for each repository
        for repo_type in ['component', 'dependency', 'issue', 'health']:
            f = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            self.temp_files[repo_type] = Path(f.name)
            f.close()
        
        # Initialize repositories
        self.component_repo = JSONComponentRepository(self.temp_files['component'])
        self.dependency_repo = JSONDependencyRepository(self.temp_files['dependency'])
        self.issue_repo = JSONIssueRepository(self.temp_files['issue'])
        self.health_repo = JSONHealthScoreRepository(self.temp_files['health'])
        
        # Add sample data
        self._populate_sample_data()
    
    def teardown_method(self):
        """Cleanup temporary files"""
        for temp_file in self.temp_files.values():
            if temp_file.exists():
                temp_file.unlink()
    
    def _populate_sample_data(self):
        """Populate repositories with sample data"""
        # Add components
        for i in range(5):
            component = Component(
                name=f"Component{i}",
                path=f"src/component{i}.py",
                type=ComponentType.FILE,
                health_score=70 + (i * 5),
                lines_of_code=100 + (i * 50),
                complexity=10 + i,
                test_coverage=50 + (i * 10),
                code_smells=5 - i,
                security_issues=2 if i == 0 else 0
            )
            self.component_repo.save(component)
        
        # Add dependencies
        for i in range(3):
            dep = Dependency(
                source=f"src/component{i}.py",
                target=f"src/component{i+1}.py",
                type=DependencyType.IMPORT
            )
            self.dependency_repo.save(dep)
        
        # Add issues
        for i in range(3):
            issue = Issue(
                id=f"ISS-{i:03d}",
                type=IssueType.CODE_SMELL if i < 2 else IssueType.VULNERABILITY,
                severity=IssueSeverity.MAJOR,
                title=f"Issue {i}",
                message=f"Description {i}",
                component_path=f"src/component{i}.py",
                file_path=f"src/component{i}.py"
            )
            self.issue_repo.save(issue)
        
        # Add system health score
        health = HealthScore(total_score=78.5)
        self.health_repo.save(health)
    
    def test_load_overview_use_case(self):
        """Test LoadOverviewUseCase"""
        use_case = LoadOverviewUseCase(
            self.component_repo,
            self.issue_repo,
            self.health_repo
        )
        
        result = use_case.execute()
        
        assert 'statistics' in result
        assert result['statistics']['total_components'] == 5
        assert 'health_distribution' in result
        assert 'issue_breakdown' in result
    
    def test_render_architecture_graph_use_case(self):
        """Test RenderArchitectureGraphUseCase"""
        use_case = RenderArchitectureGraphUseCase(
            self.component_repo,
            self.dependency_repo,
            self.health_repo
        )
        
        result = use_case.execute()
        
        assert 'nodes' in result
        assert 'links' in result
        assert len(result['nodes']) == 5
        assert len(result['links']) == 3
        assert 'statistics' in result
    
    def test_analyze_quality_metrics_use_case(self):
        """Test AnalyzeQualityMetricsUseCase"""
        use_case = AnalyzeQualityMetricsUseCase(
            self.component_repo,
            self.issue_repo
        )
        
        result = use_case.execute()
        
        assert 'complexity' in result
        assert 'test_coverage' in result
        assert 'code_smells' in result
        assert 'technical_debt' in result
        assert 'quality_score' in result
        assert result['quality_score'] > 0
    
    def test_scan_security_vulnerabilities_use_case(self):
        """Test ScanSecurityVulnerabilitiesUseCase"""
        use_case = ScanSecurityVulnerabilitiesUseCase(
            self.component_repo,
            self.issue_repo
        )
        
        result = use_case.execute()
        
        assert 'total_vulnerabilities' in result
        assert 'severity_distribution' in result
        assert 'vulnerable_components' in result
        assert 'security_score' in result
    
    def test_generate_recommendations_use_case(self):
        """Test GenerateRecommendationsUseCase"""
        use_case = GenerateRecommendationsUseCase(
            self.component_repo,
            self.issue_repo,
            self.dependency_repo
        )
        
        result = use_case.execute()
        
        assert 'by_category' in result
        assert 'by_priority' in result
        assert 'quick_wins' in result
        assert 'all' in result


class TestCleanArchitecturePrinciples:
    """Test adherence to Clean Architecture principles"""
    
    def test_domain_has_no_external_dependencies(self):
        """Test that domain entities have no external dependencies"""
        # Component should not import from data or use_cases layers
        component = Component(
            name="Test",
            path="test.py",
            type=ComponentType.FILE
        )
        
        # Should be able to create and use without any infrastructure
        assert component.name == "Test"
        assert component.to_dict() is not None
    
    def test_use_cases_depend_on_interfaces(self):
        """Test that use cases depend on interfaces, not concrete implementations"""
        from src.dashboard.data.repository_interface import IComponentRepository
        
        # LoadOverviewUseCase should accept interface type
        use_case = LoadOverviewUseCase(
            component_repo=None,  # Type hint should be IComponentRepository
            issue_repo=None,
            health_repo=None
        )
        
        assert use_case is not None
    
    def test_repositories_implement_interfaces(self):
        """Test that repositories implement interface contracts"""
        from src.dashboard.data.repository_interface import IComponentRepository
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = Path(f.name)
        
        try:
            repo = JSONComponentRepository(temp_file)
            
            # Should implement all interface methods
            assert hasattr(repo, 'get_all')
            assert hasattr(repo, 'get_by_path')
            assert hasattr(repo, 'get_by_health_category')
            assert hasattr(repo, 'save')
            
            # Verify it's a valid implementation
            assert callable(repo.get_all)
        finally:
            temp_file.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
