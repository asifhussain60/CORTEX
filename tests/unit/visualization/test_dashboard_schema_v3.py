"""
PHASE-21 Phase-0: JSON Schema v3.0 Pydantic Models - Test Suite
Authority: phase-21-json-first-rewrite.yaml
Status: RED phase (test-driven development)
Note: Tests import from cortex.models.dashboard_schema_pydantic (canonical name, no versioning per CORE-035)
"""

import pytest
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ValidationError


# ============================================================================
# TEST SUITE: Repository Schema
# ============================================================================

class TestRepositorySchema:
    """RED: Define repository metadata structure"""

    def test_repository_slug_required(self):
        """Test: slug field is mandatory"""
        from cortex.models.dashboard_schema_pydantic import Repository
        with pytest.raises(ValidationError):
            Repository(display_name="Test")

    def test_repository_display_name_required(self):
        """Test: display_name field is mandatory"""
        from cortex.models.dashboard_schema_pydantic import Repository
        with pytest.raises(ValidationError):
            Repository(slug="test-repo")

    def test_repository_valid_minimal(self):
        """Test: Create repo with minimal required fields"""
        from cortex.models.dashboard_schema_pydantic import Repository
        repo = Repository(
            slug="cortex",
            display_name="CORTEX"
        )
        assert repo.slug == "cortex"
        assert repo.display_name == "CORTEX"

    def test_repository_full_structure(self):
        """Test: All optional fields accepted"""
        from cortex.models.dashboard_schema_pydantic import Repository
        repo = Repository(
            slug="cortex",
            display_name="CORTEX",
            description="Enterprise Code Intelligence Platform",
            primary_language="Python",
            tech_stack=["Python", "FastAPI", "Pydantic"],
            total_loc=125000,
            file_count=850,
            health_score=85,
            last_analyzed_at=datetime.now()
        )
        assert repo.primary_language == "Python"
        assert len(repo.tech_stack) == 3
        assert repo.health_score == 85

    def test_repository_health_score_bounds(self):
        """Test: health_score must be 0-100"""
        from cortex.models.dashboard_schema_pydantic import Repository
        with pytest.raises(ValidationError):
            Repository(slug="test", display_name="Test", health_score=101)
        with pytest.raises(ValidationError):
            Repository(slug="test", display_name="Test", health_score=-1)

    def test_repository_to_dict(self):
        """Test: Serialize repository to dict"""
        from cortex.models.dashboard_schema_pydantic import Repository
        repo = Repository(slug="cortex", display_name="CORTEX")
        data = repo.model_dump()
        assert isinstance(data, dict)
        assert "slug" in data
        assert "display_name" in data


# ============================================================================
# TEST SUITE: Metrics Schema
# ============================================================================

class TestMetricsSchema:
    """RED: Define metrics structure"""

    def test_code_metrics_valid(self):
        """Test: CodeMetrics with all fields"""
        from cortex.models.dashboard_schema_pydantic import CodeMetrics
        metrics = CodeMetrics(
            lines_of_code=125000,
            cyclomatic_complexity=3.2,
            maintainability_index=75,
            test_coverage_percent=85,
            duplication_percent=2.5
        )
        assert metrics.lines_of_code == 125000
        assert metrics.test_coverage_percent == 85

    def test_code_metrics_coverage_bounds(self):
        """Test: Coverage must be 0-100%"""
        from cortex.models.dashboard_schema_pydantic import CodeMetrics
        with pytest.raises(ValidationError):
            CodeMetrics(test_coverage_percent=101)

    def test_dependency_metrics_valid(self):
        """Test: DependencyMetrics structure"""
        from cortex.models.dashboard_schema_pydantic import DependencyMetrics
        metrics = DependencyMetrics(
            total_dependencies=42,
            up_to_date=35,
            outdated=5,
            vulnerable=2
        )
        assert metrics.total_dependencies == 42
        assert metrics.vulnerable == 2

    def test_security_metrics_valid(self):
        """Test: SecurityMetrics structure"""
        from cortex.models.dashboard_schema_pydantic import SecurityMetrics
        metrics = SecurityMetrics(
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=8,
            low_vulnerabilities=15,
            security_score=78
        )
        assert metrics.critical_vulnerabilities == 0
        assert metrics.security_score == 78

    def test_security_score_bounds(self):
        """Test: Security score 0-100"""
        from cortex.models.dashboard_schema_pydantic import SecurityMetrics
        with pytest.raises(ValidationError):
            SecurityMetrics(security_score=101)


# ============================================================================
# TEST SUITE: Overview Schema
# ============================================================================

class TestOverviewSchema:
    """RED: Define overview/summary structure"""

    def test_overview_summary_required(self):
        """Test: summary field mandatory"""
        from cortex.models.dashboard_schema_pydantic import Overview
        with pytest.raises(ValidationError):
            Overview()

    def test_overview_full_structure(self):
        """Test: Create overview with all fields"""
        from cortex.models.dashboard_schema_pydantic import Overview
        overview = Overview(
            summary="High-level repo summary",
            business_summary="LLM-generated business language",
            key_features=["Feature 1", "Feature 2", "Feature 3"],
            critical_issues=["Issue 1"],
            upcoming_maintenance=["Task 1"]
        )
        assert overview.summary == "High-level repo summary"
        assert len(overview.key_features) == 3
        assert overview.critical_issues is not None


# ============================================================================
# TEST SUITE: Dashboard Schema (Complete)
# ============================================================================

class TestDashboardSchema:
    """RED: Complete dashboard JSON schema"""

    def test_dashboard_schema_version(self):
        """Test: Dashboard has correct schema version"""
        from cortex.models.dashboard_schema_pydantic import Dashboard, Repository, Overview
        dashboard = Dashboard(
            schema_version="3.0",
            repo=Repository(slug="test", display_name="Test"),
            overview=Overview(summary="Test overview")
        )
        assert dashboard.schema_version == "3.0"

    def test_dashboard_complete_structure(self):
        """Test: Full dashboard with all sections"""
        from cortex.models.dashboard_schema_pydantic import (
            Dashboard, Repository, Overview, CodeMetrics
        )
        
        repo = Repository(slug="cortex", display_name="CORTEX")
        overview = Overview(summary="Test repo")
        
        dashboard = Dashboard(
            schema_version="3.0",
            repo=repo,
            overview=overview,
            metadata={
                "generated_at": "2026-02-06T10:00:00Z",
                "generator": "cortex-v3.0"
            }
        )
        assert dashboard.repo.slug == "cortex"
        assert dashboard.schema_version == "3.0"

    def test_dashboard_to_json(self):
        """Test: Serialize dashboard to JSON-compatible dict"""
        from cortex.models.dashboard_schema_pydantic import Dashboard, Repository, Overview
        
        repo = Repository(slug="test", display_name="Test")
        overview = Overview(summary="Test")
        dashboard = Dashboard(
            schema_version="3.0",
            repo=repo,
            overview=overview
        )
        
        data = dashboard.model_dump()
        assert isinstance(data, dict)
        assert data["schema_version"] == "3.0"

    def test_dashboard_json_serializable(self):
        """Test: Dashboard can be JSON serialized"""
        import json
        from cortex.models.dashboard_schema_pydantic import Dashboard, Repository, Overview
        
        repo = Repository(slug="test", display_name="Test")
        overview = Overview(summary="Test")
        dashboard = Dashboard(
            schema_version="3.0",
            repo=repo,
            overview=overview
        )
        
        json_str = dashboard.model_dump_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["schema_version"] == "3.0"


# ============================================================================
# TEST SUITE: Data Sections (Metrics, Security, Dependencies)
# ============================================================================

class TestDashboardDataSections:
    """RED: Individual dashboard sections"""

    def test_metrics_section_structure(self):
        """Test: Metrics section in dashboard"""
        from cortex.models.dashboard_schema_pydantic import Dashboard, Repository, Overview, CodeMetrics
        
        repo = Repository(slug="test", display_name="Test")
        overview = Overview(summary="Test")
        code_metrics = CodeMetrics(lines_of_code=10000)
        
        dashboard = Dashboard(
            schema_version="3.0",
            repo=repo,
            overview=overview,
            metrics={"code": code_metrics}
        )
        assert dashboard.metrics["code"].lines_of_code == 10000

    def test_security_section_structure(self):
        """Test: Security section in dashboard"""
        from cortex.models.dashboard_schema_pydantic import (
            Dashboard, Repository, Overview, SecurityMetrics
        )
        
        repo = Repository(slug="test", display_name="Test")
        overview = Overview(summary="Test")
        sec_metrics = SecurityMetrics(critical_vulnerabilities=0)
        
        dashboard = Dashboard(
            schema_version="3.0",
            repo=repo,
            overview=overview,
            security={"metrics": sec_metrics}
        )
        assert dashboard.security["metrics"].critical_vulnerabilities == 0


# ============================================================================
# TEST SUITE: Validation & Constraints
# ============================================================================

class TestSchemaValidation:
    """RED: Schema validation and constraints"""

    def test_health_score_validation(self):
        """Test: Health score range validation"""
        from cortex.models.dashboard_schema_pydantic import Repository
        valid = Repository(slug="test", display_name="Test", health_score=50)
        assert valid.health_score == 50

    def test_tech_stack_type(self):
        """Test: Tech stack is list of strings"""
        from cortex.models.dashboard_schema_pydantic import Repository
        repo = Repository(
            slug="test",
            display_name="Test",
            tech_stack=["Python", "FastAPI"]
        )
        assert isinstance(repo.tech_stack, list)
        assert all(isinstance(t, str) for t in repo.tech_stack)

    def test_optional_fields_can_be_none(self):
        """Test: Optional fields can be None"""
        from cortex.models.dashboard_schema_pydantic import Repository
        repo = Repository(
            slug="test",
            display_name="Test",
            description=None,
            primary_language=None
        )
        assert repo.description is None
        assert repo.primary_language is None


# ============================================================================
# TEST SUITE: Real-World Examples
# ============================================================================

class TestRealWorldExamples:
    """RED: Test with realistic data"""

    def test_cortex_repo_dashboard(self):
        """Test: Realistic CORTEX repository dashboard"""
        from cortex.models.dashboard_schema_pydantic import (
            Dashboard, Repository, Overview, CodeMetrics
        )
        
        dashboard = Dashboard(
            schema_version="3.0",
            repo=Repository(
                slug="cortex",
                display_name="CORTEX",
                description="Enterprise Code Intelligence Platform",
                primary_language="Python",
                tech_stack=["Python", "FastAPI", "Pydantic", "SQLite"],
                total_loc=125000,
                file_count=850,
                health_score=85
            ),
            overview=Overview(
                summary="High-performance code intelligence system",
                business_summary="AI-powered repository analysis for enterprises",
                key_features=["Code Analysis", "Metrics", "Security Scanning"],
                critical_issues=[],
                upcoming_maintenance=[]
            ),
            metrics={
                "code": CodeMetrics(
                    lines_of_code=125000,
                    cyclomatic_complexity=3.2,
                    maintainability_index=75,
                    test_coverage_percent=85,
                    duplication_percent=2.5
                )
            }
        )
        
        assert dashboard.repo.slug == "cortex"
        assert dashboard.repo.health_score == 85
        assert dashboard.metrics["code"].test_coverage_percent == 85


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
