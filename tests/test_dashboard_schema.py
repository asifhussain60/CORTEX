"""
Unit tests for Repository Dashboard Schema Validation
TDD-based tests for Pydantic models and validation rules
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from cortex.orchestrators.onboarding.dashboard_schema_models import (
    RepositoryMetadata, OverviewTab, ArchitectureTab, QualityTab,
    VulnerabilitiesTab, SecurityTab, DependenciesTab, TestingTab,
    PatternsTab, UseCasesTab, RepositoryDashboardSchema,
    validate_dashboard_data, ProgrammingLanguage, Priority, Severity,
    Persona, Complexity, Maturity, ComplianceStatus, SecurityStatus,
    IntegrationType
)


# ============================================================================
# METADATA TESTS
# ============================================================================

class TestRepositoryMetadata:
    """Test RepositoryMetadata validation"""
    
    def test_valid_metadata(self):
        """Test creating valid metadata"""
        meta = RepositoryMetadata(
            name="KSESSIONS",
            path="D:\\PROJECTS\\KSESSIONS",
            description="Enterprise session management",
            primary_language=ProgrammingLanguage.C_SHARP,
            total_files=26434,
            total_lines=3658465,
            contributors=30,
            last_updated=datetime.now(),
            repo_age_days=635
        )
        assert meta.name == "KSESSIONS"
        assert meta.contributors == 30
    
    def test_metadata_missing_required_field(self):
        """Test metadata with missing required field"""
        with pytest.raises(ValidationError):
            RepositoryMetadata(
                name="KSESSIONS",
                path="D:\\PROJECTS\\KSESSIONS",
                primary_language=ProgrammingLanguage.C_SHARP,
                total_files=26434,
                # missing total_lines
                contributors=30,
                last_updated=datetime.now(),
                repo_age_days=635
            )
    
    def test_metadata_invalid_contributors(self):
        """Test metadata with invalid contributors count"""
        with pytest.raises(ValidationError):
            RepositoryMetadata(
                name="KSESSIONS",
                path="D:\\PROJECTS\\KSESSIONS",
                primary_language=ProgrammingLanguage.C_SHARP,
                total_files=26434,
                total_lines=3658465,
                contributors=0,  # Invalid: minimum is 1
                last_updated=datetime.now(),
                repo_age_days=635
            )
    
    def test_metadata_invalid_lines_negative(self):
        """Test metadata with negative lines count"""
        with pytest.raises(ValidationError):
            RepositoryMetadata(
                name="KSESSIONS",
                path="D:\\PROJECTS\\KSESSIONS",
                primary_language=ProgrammingLanguage.C_SHARP,
                total_files=26434,
                total_lines=-100,  # Invalid: cannot be negative
                contributors=30,
                last_updated=datetime.now(),
                repo_age_days=635
            )
    
    def test_metadata_name_too_long(self):
        """Test metadata with name exceeding max length"""
        long_name = "x" * 256
        with pytest.raises(ValidationError):
            RepositoryMetadata(
                name=long_name,
                path="D:\\PROJECTS\\KSESSIONS",
                primary_language=ProgrammingLanguage.C_SHARP,
                total_files=26434,
                total_lines=3658465,
                contributors=30,
                last_updated=datetime.now(),
                repo_age_days=635
            )
    
    def test_metadata_datetime_parsing(self):
        """Test ISO8601 datetime parsing"""
        meta = RepositoryMetadata(
            name="KSESSIONS",
            path="D:\\PROJECTS\\KSESSIONS",
            primary_language=ProgrammingLanguage.C_SHARP,
            total_files=26434,
            total_lines=3658465,
            contributors=30,
            last_updated="2026-02-08T15:30:00Z",
            repo_age_days=635
        )
        assert isinstance(meta.last_updated, datetime)


# ============================================================================
# OVERVIEW TAB TESTS
# ============================================================================

class TestOverviewTab:
    """Test OverviewTab validation"""
    
    def test_valid_overview(self):
        """Test creating valid overview"""
        overview = OverviewTab(
            health_score=87.5,
            code_quality=8.2,
            test_coverage=92.0,
            maintainability_index=85.0,
            technical_debt_hours=120,
            languages={"C#": 2500000, "JavaScript": 450000}
        )
        assert overview.health_score == 87.5
        assert overview.test_coverage == 92.0
    
    def test_overview_invalid_health_score_range(self):
        """Test overview with health score out of range"""
        with pytest.raises(ValidationError):
            OverviewTab(
                health_score=101.0,  # Invalid: max is 100
                code_quality=8.2,
                test_coverage=92.0,
                maintainability_index=85.0,
                technical_debt_hours=120,
                languages={}
            )
    
    def test_overview_negative_health_score(self):
        """Test overview with negative health score"""
        with pytest.raises(ValidationError):
            OverviewTab(
                health_score=-5.0,  # Invalid: minimum is 0
                code_quality=8.2,
                test_coverage=92.0,
                maintainability_index=85.0,
                technical_debt_hours=120,
                languages={}
            )
    
    def test_overview_code_quality_bounds(self):
        """Test code quality score constraints"""
        with pytest.raises(ValidationError):
            OverviewTab(
                health_score=87.5,
                code_quality=10.5,  # Invalid: max is 10
                test_coverage=92.0,
                maintainability_index=85.0,
                technical_debt_hours=120,
                languages={}
            )


# ============================================================================
# QUALITY TAB TESTS
# ============================================================================

class TestQualityTab:
    """Test QualityTab validation"""
    
    def test_valid_quality_tab(self):
        """Test creating valid quality tab"""
        quality = QualityTab(
            code_quality_score=8.2,
            maintainability_index=85.0,
            code_smells=15,
            duplication_percentage=3.5,
            technical_debt_hours=120,
            test_coverage=92.0
        )
        assert quality.code_quality_score == 8.2
        assert quality.test_coverage == 92.0
    
    def test_quality_coverage_percentage_bounds(self):
        """Test test coverage percentage constraints"""
        with pytest.raises(ValidationError):
            QualityTab(
                code_quality_score=8.2,
                maintainability_index=85.0,
                code_smells=15,
                duplication_percentage=3.5,
                technical_debt_hours=120,
                test_coverage=101.0  # Invalid: max is 100
            )
    
    def test_quality_negative_code_smells(self):
        """Test negative code smells count"""
        with pytest.raises(ValidationError):
            QualityTab(
                code_quality_score=8.2,
                maintainability_index=85.0,
                code_smells=-5,  # Invalid: cannot be negative
                duplication_percentage=3.5,
                technical_debt_hours=120,
                test_coverage=92.0
            )
    
    def test_quality_with_hotspots(self):
        """Test quality with hotspots"""
        quality = QualityTab(
            code_quality_score=8.2,
            maintainability_index=85.0,
            code_smells=15,
            duplication_percentage=3.5,
            technical_debt_hours=120,
            test_coverage=92.0,
            hotspots=[
                {
                    "file": "Services/AuthService.cs",
                    "complexity": 12.5,
                    "issues": 3,
                    "priority": Priority.HIGH
                }
            ]
        )
        assert len(quality.hotspots) == 1
        assert quality.hotspots[0].file == "Services/AuthService.cs"


# ============================================================================
# VULNERABILITIES TAB TESTS
# ============================================================================

class TestVulnerabilitiesTab:
    """Test VulnerabilitiesTab validation"""
    
    def test_valid_vulnerabilities(self):
        """Test creating valid vulnerabilities tab"""
        vuln = VulnerabilitiesTab(
            critical=2,
            high=5,
            medium=12,
            low=8
        )
        assert vuln.critical == 2
        assert vuln.high == 5
    
    def test_vulnerabilities_with_cves(self):
        """Test vulnerabilities with CVEs"""
        vuln = VulnerabilitiesTab(
            critical=2,
            high=5,
            medium=12,
            low=8,
            cves=[
                {
                    "id": "CVE-2025-1234",
                    "severity": "high",
                    "affected_package": "lodash",
                    "fix_available": True
                }
            ]
        )
        assert len(vuln.cves) == 1
        assert vuln.cves[0].id == "CVE-2025-1234"
    
    def test_vulnerabilities_negative_count(self):
        """Test vulnerabilities with negative count"""
        with pytest.raises(ValidationError):
            VulnerabilitiesTab(
                critical=-1,  # Invalid: cannot be negative
                high=5,
                medium=12,
                low=8
            )


# ============================================================================
# SECURITY TAB TESTS
# ============================================================================

class TestSecurityTab:
    """Test SecurityTab validation"""
    
    def test_valid_security_tab(self):
        """Test creating valid security tab"""
        security = SecurityTab(
            security_score=8.5,
            security_posture="Strong"
        )
        assert security.security_score == 8.5
        assert security.security_posture == "Strong"
    
    def test_security_with_frameworks(self):
        """Test security with compliance frameworks"""
        security = SecurityTab(
            security_score=8.5,
            security_posture="Strong",
            frameworks=[
                {
                    "name": "OWASP Top 10",
                    "status": ComplianceStatus.COMPLIANT,
                    "score": 95.0,
                    "issues": 1
                }
            ]
        )
        assert len(security.frameworks) == 1
        assert security.frameworks[0].name == "OWASP Top 10"


# ============================================================================
# DEPENDENCIES TAB TESTS
# ============================================================================

class TestDependenciesTab:
    """Test DependenciesTab validation"""
    
    def test_valid_dependencies(self):
        """Test creating valid dependencies tab"""
        deps = DependenciesTab(
            direct_count=45,
            transitive_count=320,
            outdated_count=8,
            vulnerable_count=2
        )
        assert deps.direct_count == 45
        assert deps.vulnerable_count == 2
    
    def test_dependencies_with_packages(self):
        """Test dependencies with package list"""
        deps = DependenciesTab(
            direct_count=45,
            transitive_count=320,
            outdated_count=8,
            vulnerable_count=2,
            packages=[
                {
                    "name": "lodash",
                    "version": "4.17.19",
                    "latest": "4.17.21",
                    "type": "direct",
                    "license": "MIT",
                    "security_status": SecurityStatus.VULNERABLE,
                    "update_recommended": True
                }
            ]
        )
        assert len(deps.packages) == 1
        assert deps.packages[0].security_status == SecurityStatus.VULNERABLE


# ============================================================================
# TESTING TAB TESTS
# ============================================================================

class TestTestingTab:
    """Test TestingTab validation"""
    
    def test_valid_testing_tab(self):
        """Test creating valid testing tab"""
        testing = TestingTab(
            coverage_percentage=92.0,
            test_counts={
                "total": 1250,
                "passing": 1245,
                "failing": 3,
                "skipped": 2
            },
            test_types={
                "unit": 950,
                "integration": 200,
                "e2e": 100
            }
        )
        assert testing.coverage_percentage == 92.0
        assert testing.test_counts.total == 1250
    
    def test_testing_invalid_coverage(self):
        """Test testing tab with invalid coverage"""
        with pytest.raises(ValidationError):
            TestingTab(
                coverage_percentage=101.0,  # Invalid: max is 100
                test_counts={
                    "total": 1250,
                    "passing": 1245,
                    "failing": 3,
                    "skipped": 2
                },
                test_types={
                    "unit": 950,
                    "integration": 200,
                    "e2e": 100
                }
            )


# ============================================================================
# PATTERNS TAB TESTS
# ============================================================================

class TestPatternsTab:
    """Test PatternsTab validation"""
    
    def test_valid_patterns_tab(self):
        """Test creating valid patterns tab"""
        patterns = PatternsTab(
            design_patterns=[],
            anti_patterns=[
                {
                    "name": "God Object",
                    "severity": Severity.HIGH,
                    "count": 3,
                    "remediation": "Split into smaller classes"
                }
            ]
        )
        assert len(patterns.anti_patterns) == 1
        assert patterns.anti_patterns[0].severity == Severity.HIGH


# ============================================================================
# USE CASES TAB TESTS
# ============================================================================

class TestUseCasesTab:
    """Test UseCasesTab validation"""
    
    def test_valid_use_cases_tab(self):
        """Test creating valid use cases tab"""
        use_cases = UseCasesTab(
            detected_capabilities=[
                {
                    "id": "uc-001",
                    "business_capability": "User Authentication",
                    "technical_name": "AuthService",
                    "description": "Authenticate users",
                    "business_value": "Secures user access",
                    "complexity": Complexity.MEDIUM,
                    "maturity": Maturity.STABLE,
                    "modernization_score": 85.0
                }
            ]
        )
        assert len(use_cases.detected_capabilities) == 1
        assert use_cases.detected_capabilities[0].id == "uc-001"


# ============================================================================
# COMPLETE DASHBOARD SCHEMA TESTS
# ============================================================================

class TestRepositoryDashboardSchema:
    """Test complete RepositoryDashboardSchema validation"""
    
    def get_minimal_valid_data(self):
        """Get minimal valid dashboard data"""
        return {
            "metadata": {
                "name": "KSESSIONS",
                "path": "D:\\PROJECTS\\KSESSIONS",
                "primary_language": "C#",
                "total_files": 26434,
                "total_lines": 3658465,
                "contributors": 30,
                "last_updated": "2026-02-08T15:30:00Z",
                "repo_age_days": 635
            },
            "overview": {
                "health_score": 87.5,
                "code_quality": 8.2,
                "test_coverage": 92.0,
                "maintainability_index": 85.0,
                "technical_debt_hours": 120,
                "languages": {"C#": 2500000}
            },
            "architecture": {
                "layers": [],
                "modules": {},
                "design_patterns": []
            },
            "quality": {
                "code_quality_score": 8.2,
                "maintainability_index": 85.0,
                "code_smells": 15,
                "duplication_percentage": 3.5,
                "technical_debt_hours": 120,
                "test_coverage": 92.0
            },
            "vulnerabilities": {
                "critical": 2,
                "high": 5,
                "medium": 12,
                "low": 8
            },
            "security": {
                "security_score": 8.5,
                "security_posture": "Strong"
            },
            "dependencies": {
                "direct_count": 45,
                "transitive_count": 320,
                "outdated_count": 8,
                "vulnerable_count": 2
            },
            "testing": {
                "coverage_percentage": 92.0,
                "test_counts": {
                    "total": 1250,
                    "passing": 1245,
                    "failing": 3,
                    "skipped": 2
                },
                "test_types": {
                    "unit": 950,
                    "integration": 200,
                    "e2e": 100
                }
            },
            "patterns": {},
            "use_cases": {}
        }
    
    def test_valid_complete_dashboard(self):
        """Test creating valid complete dashboard schema"""
        data = self.get_minimal_valid_data()
        schema = validate_dashboard_data(data)
        assert schema.metadata.name == "KSESSIONS"
        assert schema.overview.health_score == 87.5
        assert schema.quality.test_coverage == 92.0
    
    def test_missing_required_tab(self):
        """Test dashboard with missing required tab"""
        data = self.get_minimal_valid_data()
        del data['quality']  # Remove required tab
        
        with pytest.raises(ValidationError):
            validate_dashboard_data(data)
    
    def test_all_tabs_present(self):
        """Test dashboard has all 10 required tabs"""
        data = self.get_minimal_valid_data()
        schema = RepositoryDashboardSchema(**data)
        
        required_fields = [
            'metadata', 'overview', 'architecture', 'quality',
            'vulnerabilities', 'security', 'dependencies', 'testing',
            'patterns', 'use_cases'
        ]
        
        for field in required_fields:
            assert hasattr(schema, field), f"Missing required field: {field}"
            assert getattr(schema, field) is not None, f"Field is None: {field}"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestDataValidation:
    """Integration tests for data validation"""
    
    def test_validate_real_world_data(self):
        """Test validating real-world-like data"""
        data = {
            "metadata": {
                "name": "KSESSIONS",
                "path": "D:\\PROJECTS\\KSESSIONS",
                "primary_language": "C#",
                "total_files": 26434,
                "total_lines": 3658465,
                "contributors": 30,
                "last_updated": "2026-02-08T15:30:00Z",
                "repo_age_days": 635
            },
            "overview": {
                "health_score": 87.5,
                "code_quality": 8.2,
                "test_coverage": 92.0,
                "maintainability_index": 85.0,
                "technical_debt_hours": 120,
                "languages": {
                    "C#": 2500000,
                    "JavaScript": 450000,
                    "SQL": 708465
                },
                "audiences": [
                    {
                        "persona": "Executive",
                        "icon": "👔",
                        "description": "C-level stakeholders"
                    }
                ]
            },
            "architecture": {
                "layers": [
                    {
                        "name": "Presentation",
                        "description": "Web UI and APIs",
                        "modules": ["WebUI", "API"],
                        "technologies": ["React", "ASP.NET Core"]
                    }
                ],
                "modules": {
                    "AuthService": {
                        "lines_of_code": 5000,
                        "files": 25,
                        "complexity": 8.5,
                        "sub_modules": ["OAuth", "JWT"],
                        "dependencies": ["Cryptography", "Database"]
                    }
                },
                "design_patterns": [
                    {
                        "name": "Repository Pattern",
                        "description": "Data access abstraction",
                        "location": "Data layer",
                        "usage_count": 45
                    }
                ]
            },
            "quality": {
                "code_quality_score": 8.2,
                "maintainability_index": 85.0,
                "code_smells": 15,
                "duplication_percentage": 3.5,
                "technical_debt_hours": 120,
                "test_coverage": 92.0,
                "coverage_trend": [
                    {"date": "2026-02-01", "value": 88.5},
                    {"date": "2026-02-08", "value": 92.0}
                ],
                "hotspots": [
                    {
                        "file": "Services/AuthService.cs",
                        "complexity": 12.5,
                        "issues": 3,
                        "priority": "high"
                    }
                ]
            },
            "vulnerabilities": {
                "critical": 2,
                "high": 5,
                "medium": 12,
                "low": 8,
                "cves": [
                    {
                        "id": "CVE-2025-1234",
                        "severity": "high",
                        "affected_package": "lodash",
                        "fix_available": True
                    }
                ]
            },
            "security": {
                "security_score": 8.5,
                "security_posture": "Strong",
                "frameworks": [
                    {
                        "name": "OWASP Top 10",
                        "status": "compliant",
                        "score": 95.0,
                        "issues": 1
                    }
                ]
            },
            "dependencies": {
                "direct_count": 45,
                "transitive_count": 320,
                "outdated_count": 8,
                "vulnerable_count": 2,
                "packages": [
                    {
                        "name": "lodash",
                        "version": "4.17.19",
                        "latest": "4.17.21",
                        "type": "direct",
                        "license": "MIT",
                        "security_status": "vulnerable",
                        "update_recommended": True
                    }
                ]
            },
            "testing": {
                "coverage_percentage": 92.0,
                "test_counts": {
                    "total": 1250,
                    "passing": 1245,
                    "failing": 3,
                    "skipped": 2
                },
                "test_types": {
                    "unit": 950,
                    "integration": 200,
                    "e2e": 100
                },
                "failing_tests": [
                    {
                        "name": "TestAuthTokenExpiry",
                        "file": "Tests/AuthServiceTests.cs",
                        "error": "Timeout after 5000ms",
                        "priority": "high"
                    }
                ]
            },
            "patterns": {
                "design_patterns": [],
                "anti_patterns": [
                    {
                        "name": "God Object",
                        "severity": "high",
                        "count": 3,
                        "remediation": "Split into smaller classes"
                    }
                ]
            },
            "use_cases": {
                "detected_capabilities": [
                    {
                        "id": "uc-001",
                        "business_capability": "User Authentication",
                        "technical_name": "AuthService",
                        "description": "Authenticate users",
                        "business_value": "Secures user access",
                        "complexity": "medium",
                        "maturity": "stable",
                        "modernization_score": 85.0
                    }
                ]
            }
        }
        
        schema = validate_dashboard_data(data)
        assert schema is not None
        assert schema.metadata.total_lines == 3658465
        assert schema.overview.health_score == 87.5
        assert len(schema.architecture.layers) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
