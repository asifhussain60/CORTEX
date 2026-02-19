"""
Tests for Dashboard Schema Models.

Tests RepoDashboardModel and all sub-sections following TDD principles.

AC-ID: AC-TEST-DASHBOARD-SCHEMA-001
Authority: CORE-008 (TDD), CORE-011 (Type hints)
"""

import pytest
from datetime import datetime
from typing import Any, Dict, List
import json


class TestRepoMetadata:
    """Test RepoMetadata dataclass."""
    
    def test_repo_metadata_creation(self):
        """Test creating RepoMetadata with all required fields."""
        from cortex.models.dashboard_schema import RepoMetadata
        
        repo = RepoMetadata(
            slug="cortex",
            display_name="CORTEX",
            description="Test description",
            owner="Test Owner",
            primary_language="Python",
            version="1.0",
            last_analyzed_at="2026-02-03T10:00:00Z"
        )
        
        assert repo.slug == "cortex"
        assert repo.display_name == "CORTEX"
        assert repo.primary_language == "Python"
    
    def test_repo_metadata_to_dict(self):
        """Test RepoMetadata serialization."""
        from cortex.models.dashboard_schema import RepoMetadata
        
        repo = RepoMetadata(
            slug="test",
            display_name="Test",
            description="Test",
            owner="Owner",
            primary_language="Python",
            version="1.0",
            last_analyzed_at="2026-02-03T10:00:00Z"
        )
        
        data = repo.to_dict()
        assert isinstance(data, dict)
        assert data["slug"] == "test"
        assert data["display_name"] == "Test"
    
    def test_repo_metadata_from_dict(self):
        """Test RepoMetadata deserialization."""
        from cortex.models.dashboard_schema import RepoMetadata
        
        data = {
            "slug": "cortex",
            "display_name": "CORTEX",
            "description": "Test",
            "owner": "Owner",
            "primary_language": "Python",
            "version": "1.0",
            "last_analyzed_at": "2026-02-03T10:00:00Z"
        }
        
        repo = RepoMetadata.from_dict(data)
        assert repo.slug == "cortex"
        assert repo.display_name == "CORTEX"


class TestOverviewSection:
    """Test OverviewSection dataclass."""
    
    def test_overview_creation(self):
        """Test creating OverviewSection."""
        from cortex.models.dashboard_schema import OverviewSection
        
        overview = OverviewSection(
            summary="Test summary",
            business_summary="Business summary",
            key_findings=["Finding 1", "Finding 2"]
        )
        
        assert overview.summary == "Test summary"
        assert len(overview.key_findings) == 2
    
    def test_overview_to_dict(self):
        """Test OverviewSection serialization."""
        from cortex.models.dashboard_schema import OverviewSection
        
        overview = OverviewSection(
            summary="Test",
            business_summary="Business",
            key_findings=["F1"]
        )
        
        data = overview.to_dict()
        assert isinstance(data, dict)
        assert "summary" in data
        assert "key_findings" in data


class TestMetricsSection:
    """Test MetricsSection dataclass."""
    
    def test_metrics_creation(self):
        """Test creating MetricsSection with all fields."""
        from cortex.models.dashboard_schema import MetricsSection
        
        metrics = MetricsSection(
            health_score=85,
            risk_score=25,
            loc=125000,
            code_lines=95000,
            comment_lines=18000,
            blank_lines=12000,
            files=850,
            coverage_pct=78.5,
            languages={"Python": 85000, "TypeScript": 15000}
        )
        
        assert metrics.health_score == 85
        assert metrics.risk_score == 25
        assert metrics.loc == 125000
        assert metrics.coverage_pct == 78.5
        assert "Python" in metrics.languages
    
    def test_metrics_score_validation(self):
        """Test metrics score ranges (0-100)."""
        from cortex.models.dashboard_schema import MetricsSection
        
        # Valid scores
        metrics = MetricsSection(
            health_score=100,
            risk_score=0,
            loc=1000,
            code_lines=800,
            comment_lines=100,
            blank_lines=100,
            files=10,
            coverage_pct=50.0,
            languages={}
        )
        assert metrics.health_score == 100
        
        # Invalid scores should raise or be clamped
        with pytest.raises((ValueError, AssertionError)):
            MetricsSection(
                health_score=150,  # Invalid
                risk_score=0,
                loc=1000,
                code_lines=800,
                comment_lines=100,
                blank_lines=100,
                files=10,
                coverage_pct=50.0,
                languages={}
            )


class TestSecuritySection:
    """Test SecuritySection dataclass."""
    
    def test_security_section_creation(self):
        """Test creating SecuritySection with vulnerabilities."""
        from cortex.models.dashboard_schema import SecuritySection, SecurityVulnerability
        
        vuln = SecurityVulnerability(
            id="SEC-001",
            title="SQL Injection",
            severity="high",
            cwe_id="CWE-89",
            location="file.py:145",
            status="open",
            description="Test vuln"
        )
        
        security = SecuritySection(
            total_count=10,
            critical_count=1,
            high_count=3,
            medium_count=4,
            low_count=2,
            vulnerabilities=[vuln]
        )
        
        assert security.total_count == 10
        assert len(security.vulnerabilities) == 1
        assert security.vulnerabilities[0].severity == "high"
    
    def test_security_count_consistency(self):
        """Test security counts match vulnerability list."""
        from cortex.models.dashboard_schema import SecuritySection, SecurityVulnerability
        
        vulns = [
            SecurityVulnerability(
                id="SEC-001", title="Test", severity="critical",
                cwe_id="CWE-1", location="a.py:1", status="open",
                description="Test"
            ),
            SecurityVulnerability(
                id="SEC-002", title="Test", severity="high",
                cwe_id="CWE-2", location="b.py:1", status="open",
                description="Test"
            ),
        ]
        
        security = SecuritySection(
            total_count=2,
            critical_count=1,
            high_count=1,
            medium_count=0,
            low_count=0,
            vulnerabilities=vulns
        )
        
        # Validate counts
        calculated_total = (
            security.critical_count + security.high_count +
            security.medium_count + security.low_count
        )
        assert calculated_total == security.total_count


class TestDependenciesSection:
    """Test DependenciesSection dataclass."""
    
    def test_dependencies_creation(self):
        """Test creating DependenciesSection."""
        from cortex.models.dashboard_schema import DependenciesSection, PackageDependency
        
        pkg = PackageDependency(
            name="requests",
            version="2.31.0",
            license="Apache-2.0",
            is_direct=True
        )
        
        deps = DependenciesSection(
            total_count=50,
            direct_count=20,
            transitive_count=30,
            packages=[pkg],
            licenses={"Apache-2.0": 25, "MIT": 25}
        )
        
        assert deps.total_count == 50
        assert len(deps.packages) == 1
        assert deps.packages[0].name == "requests"


class TestQualitySection:
    """Test QualitySection dataclass."""
    
    def test_quality_section_creation(self):
        """Test creating QualitySection with code smells."""
        from cortex.models.dashboard_schema import QualitySection, CodeSmell
        
        smell = CodeSmell(
            id="CS-001",
            title="Long method",
            severity="medium",
            category="complexity",
            location="file.py:100-150",
            description="Method too long"
        )
        
        quality = QualitySection(
            maintainability=75,
            readability=80,
            documentation=70,
            complexity=65,
            code_smells=[smell],
            hotspots=[]
        )
        
        assert quality.maintainability == 75
        assert len(quality.code_smells) == 1


class TestUseCaseModel:
    """Test UseCase dataclass."""
    
    def test_use_case_creation(self):
        """Test creating UseCase with all fields."""
        from cortex.models.dashboard_schema import UseCase
        
        use_case = UseCase(
            id="UC-001",
            title="Monitor Code Quality",
            persona="Engineering Manager",
            category="Quality",
            summary="Track code quality metrics",
            signals=["health_score", "code_smells"],
            recommended_actions=["Review hotspots", "Refactor"],
            tags=["quality", "monitoring"],
            severity="medium"
        )
        
        assert use_case.id == "UC-001"
        assert use_case.persona == "Engineering Manager"
        assert len(use_case.signals) == 2
    
    def test_use_case_filtering(self):
        """Test use case can be filtered by persona/category."""
        from cortex.models.dashboard_schema import UseCase
        
        cases = [
            UseCase(
                id="UC-001", title="T1", persona="Engineer",
                category="Quality", summary="S1", signals=[],
                recommended_actions=[], tags=[], severity="low"
            ),
            UseCase(
                id="UC-002", title="T2", persona="Manager",
                category="Security", summary="S2", signals=[],
                recommended_actions=[], tags=[], severity="high"
            ),
        ]
        
        # Filter by persona
        engineer_cases = [c for c in cases if c.persona == "Engineer"]
        assert len(engineer_cases) == 1
        
        # Filter by category
        security_cases = [c for c in cases if c.category == "Security"]
        assert len(security_cases) == 1


class TestRepoDashboardModel:
    """Test RepoDashboardModel main dataclass."""
    
    def test_full_dashboard_model_creation(self):
        """Test creating complete RepoDashboardModel."""
        from cortex.models.dashboard_schema import (
            RepoDashboardModel, RepoMetadata, OverviewSection,
            MetricsSection, SecuritySection, DependenciesSection,
            QualitySection, LensSection, RefactoringSection
        )
        
        model = RepoDashboardModel(
            repo=RepoMetadata(
                slug="test", display_name="Test", description="Test",
                owner="Owner", primary_language="Python", version="1.0",
                last_analyzed_at="2026-02-03T10:00:00Z"
            ),
            overview=OverviewSection(
                summary="Summary", business_summary="Business",
                key_findings=["F1"]
            ),
            metrics=MetricsSection(
                health_score=80, risk_score=20, loc=10000,
                code_lines=8000, comment_lines=1000, blank_lines=1000,
                files=100, coverage_pct=75.0, languages={"Python": 10000}
            ),
            security=SecuritySection(
                total_count=0, critical_count=0, high_count=0,
                medium_count=0, low_count=0, vulnerabilities=[]
            ),
            dependencies=DependenciesSection(
                total_count=10, direct_count=5, transitive_count=5,
                packages=[], licenses={}
            ),
            quality=QualitySection(
                maintainability=80, readability=80, documentation=70,
                complexity=65, code_smells=[], hotspots=[]
            ),
            use_cases=[],
            lens=LensSection(analysis_summary="Test lens"),
            refactoring=RefactoringSection(recommendations=[])
        )
        
        assert model.repo.slug == "test"
        assert model.metrics.health_score == 80
        assert model.security.total_count == 0
    
    def test_dashboard_model_to_dict(self):
        """Test RepoDashboardModel serialization to dict."""
        from cortex.models.dashboard_schema import (
            RepoDashboardModel, RepoMetadata, OverviewSection,
            MetricsSection, SecuritySection, DependenciesSection,
            QualitySection, LensSection, RefactoringSection
        )
        
        model = RepoDashboardModel(
            repo=RepoMetadata(
                slug="test", display_name="Test", description="Test",
                owner="Owner", primary_language="Python", version="1.0",
                last_analyzed_at="2026-02-03T10:00:00Z"
            ),
            overview=OverviewSection(
                summary="S", business_summary="B", key_findings=[]
            ),
            metrics=MetricsSection(
                health_score=80, risk_score=20, loc=1000,
                code_lines=800, comment_lines=100, blank_lines=100,
                files=10, coverage_pct=75.0, languages={}
            ),
            security=SecuritySection(
                total_count=0, critical_count=0, high_count=0,
                medium_count=0, low_count=0, vulnerabilities=[]
            ),
            dependencies=DependenciesSection(
                total_count=0, direct_count=0, transitive_count=0,
                packages=[], licenses={}
            ),
            quality=QualitySection(
                maintainability=80, readability=80, documentation=70,
                complexity=65, code_smells=[], hotspots=[]
            ),
            use_cases=[],
            lens=LensSection(analysis_summary="Test"),
            refactoring=RefactoringSection(recommendations=[])
        )
        
        data = model.to_dict()
        
        # Validate structure
        assert isinstance(data, dict)
        assert "repo" in data
        assert "overview" in data
        assert "metrics" in data
        assert "security" in data
        assert "dependencies" in data
        assert "quality" in data
        assert "use_cases" in data
        assert "lens" in data
        assert "refactoring" in data
        
        # Validate nested data
        assert data["repo"]["slug"] == "test"
        assert data["metrics"]["health_score"] == 80
    
    def test_dashboard_model_to_json(self):
        """Test RepoDashboardModel can be serialized to JSON."""
        from cortex.models.dashboard_schema import (
            RepoDashboardModel, RepoMetadata, OverviewSection,
            MetricsSection, SecuritySection, DependenciesSection,
            QualitySection, LensSection, RefactoringSection
        )
        
        model = RepoDashboardModel(
            repo=RepoMetadata(
                slug="test", display_name="Test", description="Test",
                owner="Owner", primary_language="Python", version="1.0",
                last_analyzed_at="2026-02-03T10:00:00Z"
            ),
            overview=OverviewSection(
                summary="S", business_summary="B", key_findings=[]
            ),
            metrics=MetricsSection(
                health_score=80, risk_score=20, loc=1000,
                code_lines=800, comment_lines=100, blank_lines=100,
                files=10, coverage_pct=75.0, languages={}
            ),
            security=SecuritySection(
                total_count=0, critical_count=0, high_count=0,
                medium_count=0, low_count=0, vulnerabilities=[]
            ),
            dependencies=DependenciesSection(
                total_count=0, direct_count=0, transitive_count=0,
                packages=[], licenses={}
            ),
            quality=QualitySection(
                maintainability=80, readability=80, documentation=70,
                complexity=65, code_smells=[], hotspots=[]
            ),
            use_cases=[],
            lens=LensSection(analysis_summary="Test"),
            refactoring=RefactoringSection(recommendations=[])
        )
        
        json_str = model.to_json()
        
        # Validate JSON
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["repo"]["slug"] == "test"
    
    def test_dashboard_model_from_dict(self):
        """Test RepoDashboardModel deserialization."""
        from cortex.models.dashboard_schema import RepoDashboardModel
        
        data = {
            "repo": {
                "slug": "test", "display_name": "Test",
                "description": "Test", "owner": "Owner",
                "primary_language": "Python", "version": "1.0",
                "last_analyzed_at": "2026-02-03T10:00:00Z"
            },
            "overview": {
                "summary": "S", "business_summary": "B",
                "key_findings": []
            },
            "metrics": {
                "health_score": 80, "risk_score": 20, "loc": 1000,
                "code_lines": 800, "comment_lines": 100,
                "blank_lines": 100, "files": 10, "coverage_pct": 75.0,
                "languages": {}
            },
            "security": {
                "total_count": 0, "critical_count": 0,
                "high_count": 0, "medium_count": 0, "low_count": 0,
                "vulnerabilities": []
            },
            "dependencies": {
                "total_count": 0, "direct_count": 0,
                "transitive_count": 0, "packages": [], "licenses": {}
            },
            "quality": {
                "maintainability": 80, "readability": 80,
                "documentation": 70, "complexity": 65,
                "code_smells": [], "hotspots": []
            },
            "use_cases": [],
            "lens": {"analysis_summary": "Test"},
            "refactoring": {"recommendations": []}
        }
        
        model = RepoDashboardModel.from_dict(data)
        
        assert model.repo.slug == "test"
        assert model.metrics.health_score == 80
    
    def test_dashboard_model_extensibility(self):
        """Test adding new sections doesn't break existing code."""
        from cortex.models.dashboard_schema import RepoDashboardModel
        
        # Simulate old data without new field
        data = {
            "repo": {
                "slug": "test", "display_name": "Test",
                "description": "Test", "owner": "Owner",
                "primary_language": "Python", "version": "1.0",
                "last_analyzed_at": "2026-02-03T10:00:00Z"
            },
            "overview": {
                "summary": "S", "business_summary": "B",
                "key_findings": []
            },
            "metrics": {
                "health_score": 80, "risk_score": 20, "loc": 1000,
                "code_lines": 800, "comment_lines": 100,
                "blank_lines": 100, "files": 10, "coverage_pct": 75.0,
                "languages": {}
            },
            "security": {
                "total_count": 0, "critical_count": 0,
                "high_count": 0, "medium_count": 0, "low_count": 0,
                "vulnerabilities": []
            },
            "dependencies": {
                "total_count": 0, "direct_count": 0,
                "transitive_count": 0, "packages": [], "licenses": {}
            },
            "quality": {
                "maintainability": 80, "readability": 80,
                "documentation": 70, "complexity": 65,
                "code_smells": [], "hotspots": []
            },
            "use_cases": [],
            "lens": {"analysis_summary": "Test"},
            "refactoring": {"recommendations": []}
            # Missing future field: "performance": {...}
        }
        
        # Should not fail even if new fields added to schema
        model = RepoDashboardModel.from_dict(data)
        assert model.repo.slug == "test"


class TestSchemaValidation:
    """Test schema validation utilities."""
    
    def test_validate_required_fields(self):
        """Test validation catches missing required fields."""
        from cortex.models.dashboard_schema import validate_dashboard_model
        
        # Missing required fields
        invalid_data = {
            "repo": {"slug": "test"},  # Missing other required fields
            # Missing other sections
        }
        
        is_valid, errors = validate_dashboard_model(invalid_data)
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_complete_model(self):
        """Test validation passes for complete model."""
        from cortex.models.dashboard_schema import validate_dashboard_model
        
        valid_data = {
            "repo": {
                "slug": "test", "display_name": "Test",
                "description": "Test", "owner": "Owner",
                "primary_language": "Python", "version": "1.0",
                "last_analyzed_at": "2026-02-03T10:00:00Z"
            },
            "overview": {
                "summary": "S", "business_summary": "B",
                "key_findings": []
            },
            "metrics": {
                "health_score": 80, "risk_score": 20, "loc": 1000,
                "code_lines": 800, "comment_lines": 100,
                "blank_lines": 100, "files": 10, "coverage_pct": 75.0,
                "languages": {}
            },
            "security": {
                "total_count": 0, "critical_count": 0,
                "high_count": 0, "medium_count": 0, "low_count": 0,
                "vulnerabilities": []
            },
            "dependencies": {
                "total_count": 0, "direct_count": 0,
                "transitive_count": 0, "packages": [], "licenses": {}
            },
            "quality": {
                "maintainability": 80, "readability": 80,
                "documentation": 70, "complexity": 65,
                "code_smells": [], "hotspots": []
            },
            "use_cases": [],
            "lens": {"analysis_summary": "Test"},
            "refactoring": {"recommendations": []}
        }
        
        is_valid, errors = validate_dashboard_model(valid_data)
        assert is_valid
        assert len(errors) == 0
