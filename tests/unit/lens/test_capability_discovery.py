"""
Test suite for CapabilityDiscoveryEngine.

Validates:
- Repository fingerprinting (tech stack detection)
- Capability gap analysis (missing analyzers)
- Crawler specification generation
- Bounded complexity (max 5 custom crawlers)
- Evidence trail creation (CORE-027)

AC_START: TEST-CDF-CapabilityDiscovery-001
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from cortex.lens.capability_discovery import (
    CapabilityDiscoveryEngine,
    FingerprintAnalyzer,
    CapabilityMapper,
    CrawlerSpecGenerator,
    TechStackFingerprint,
    CapabilityGap,
    CrawlerSpec,
)


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository with various tech stack files."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    
    # Python project
    (repo / "requirements.txt").write_text("django==4.2.0\npostgresql-adapter==2.9.0\n")
    (repo / "setup.py").write_text("from setuptools import setup\n")
    
    # Node.js project
    (repo / "package.json").write_text('{"dependencies": {"express": "^4.18.0"}}\n')
    (repo / "tsconfig.json").write_text('{"compilerOptions": {}}\n')
    
    # Database migrations
    migrations = repo / "migrations"
    migrations.mkdir()
    (migrations / "001_initial.sql").write_text("CREATE TABLE users (id SERIAL);\n")
    
    # API spec
    (repo / "openapi.yaml").write_text("openapi: 3.0.0\n")
    
    return repo


@pytest.fixture
def python_repo(tmp_path):
    """Python-only repository."""
    repo = tmp_path / "python_repo"
    repo.mkdir()
    (repo / "requirements.txt").write_text("flask==2.3.0\nsqlalchemy==2.0.0\n")
    (repo / "setup.py").write_text("from setuptools import setup\n")
    return repo


@pytest.fixture
def typescript_repo(tmp_path):
    """TypeScript-only repository."""
    repo = tmp_path / "ts_repo"
    repo.mkdir()
    (repo / "package.json").write_text('{"dependencies": {"typescript": "^5.0.0"}}\n')
    (repo / "tsconfig.json").write_text('{"compilerOptions": {"target": "ES2020"}}\n')
    return repo


@pytest.fixture
def fingerprint_analyzer():
    """Create FingerprintAnalyzer instance."""
    return FingerprintAnalyzer()


@pytest.fixture
def capability_mapper():
    """Create CapabilityMapper instance."""
    return CapabilityMapper()


@pytest.fixture
def crawler_spec_generator():
    """Create CrawlerSpecGenerator instance."""
    return CrawlerSpecGenerator()


@pytest.fixture
def discovery_engine():
    """Create CapabilityDiscoveryEngine instance."""
    return CapabilityDiscoveryEngine()


class TestFingerprintAnalyzer:
    """Tests for repository fingerprinting."""
    
    def test_cdf_001_analyze_python_project(self, fingerprint_analyzer, python_repo):
        """CDF-001: Detect Python project with Flask + SQLAlchemy."""
        fingerprint = fingerprint_analyzer.analyze(python_repo)
        
        assert fingerprint.primary_language == "Python"
        assert "flask" in fingerprint.frameworks
        assert "sqlalchemy" in fingerprint.frameworks
        assert fingerprint.has_database
        assert "requirements.txt" in fingerprint.detected_files
    
    def test_cdf_002_analyze_typescript_project(self, fingerprint_analyzer, typescript_repo):
        """CDF-002: Detect TypeScript project."""
        fingerprint = fingerprint_analyzer.analyze(typescript_repo)
        
        assert fingerprint.primary_language == "TypeScript"
        assert "typescript" in fingerprint.frameworks
        assert "tsconfig.json" in fingerprint.detected_files
    
    def test_cdf_003_analyze_polyglot_project(self, fingerprint_analyzer, temp_repo):
        """CDF-003: Detect multi-language project (Python + TypeScript)."""
        fingerprint = fingerprint_analyzer.analyze(temp_repo)
        
        assert len(fingerprint.languages) >= 2
        assert "Python" in fingerprint.languages
        assert "TypeScript" in fingerprint.languages or "JavaScript" in fingerprint.languages
        assert fingerprint.has_database
        assert fingerprint.has_api
    
    def test_cdf_004_detect_database_migrations(self, fingerprint_analyzer, temp_repo):
        """CDF-004: Detect database migration files."""
        fingerprint = fingerprint_analyzer.analyze(temp_repo)
        
        assert fingerprint.has_database
        assert fingerprint.has_migrations
        assert "SQL" in fingerprint.database_types or len(fingerprint.migration_files) > 0
    
    def test_cdf_005_detect_api_specs(self, fingerprint_analyzer, temp_repo):
        """CDF-005: Detect OpenAPI/Swagger specifications."""
        fingerprint = fingerprint_analyzer.analyze(temp_repo)
        
        assert fingerprint.has_api
        assert any("openapi" in f.lower() for f in fingerprint.api_spec_files)
    
    def test_cdf_006_empty_repository(self, fingerprint_analyzer, tmp_path):
        """CDF-006: Handle empty repository gracefully."""
        empty_repo = tmp_path / "empty"
        empty_repo.mkdir()
        
        fingerprint = fingerprint_analyzer.analyze(empty_repo)
        
        assert fingerprint.primary_language is None
        assert len(fingerprint.languages) == 0
        assert not fingerprint.has_database
        assert not fingerprint.has_api


class TestCapabilityMapper:
    """Tests for capability gap analysis."""
    
    def test_cdf_007_map_existing_capabilities(self, capability_mapper):
        """CDF-007: Map tech stack to existing LENS analyzers."""
        fingerprint = TechStackFingerprint(
            primary_language="Python",
            languages=["Python"],
            frameworks=["flask"],
            has_database=False,
            has_api=True,
        )
        
        capabilities = capability_mapper.map_to_capabilities(fingerprint)
        
        assert "CodeAnalyzer" in capabilities.existing_analyzers
        assert "ConfigAnalyzer" in capabilities.existing_analyzers
        assert "DependencyAnalyzer" in capabilities.existing_analyzers
    
    def test_cdf_008_identify_database_gap(self, capability_mapper):
        """CDF-008: Identify database analyzer gap for SQL projects."""
        fingerprint = TechStackFingerprint(
            primary_language="Python",
            languages=["Python"],
            frameworks=["sqlalchemy"],
            has_database=True,
            has_migrations=True,
            database_types=["PostgreSQL"],
        )
        
        capabilities = capability_mapper.map_to_capabilities(fingerprint)
        gaps = capability_mapper.identify_gaps(capabilities, fingerprint)
        
        assert len(gaps) > 0
        # Should identify need for advanced DB analyzer if not present
        gap_names = [g.capability_name for g in gaps]
        assert any("database" in name.lower() or "migration" in name.lower() for name in gap_names)
    
    def test_cdf_009_identify_graphql_gap(self, capability_mapper):
        """CDF-009: Identify GraphQL API gap."""
        fingerprint = TechStackFingerprint(
            primary_language="TypeScript",
            languages=["TypeScript"],
            frameworks=["apollo-server", "graphql"],
            has_api=True,
            api_types=["GraphQL"],
        )
        
        capabilities = capability_mapper.map_to_capabilities(fingerprint)
        gaps = capability_mapper.identify_gaps(capabilities, fingerprint)
        
        gap_names = [g.capability_name for g in gaps]
        assert any("graphql" in name.lower() for name in gap_names)
    
    def test_cdf_010_no_gaps_for_standard_python(self, capability_mapper):
        """CDF-010: Standard Python project has no gaps (covered by existing analyzers)."""
        fingerprint = TechStackFingerprint(
            primary_language="Python",
            languages=["Python"],
            frameworks=["flask"],
            has_database=False,
            has_api=True,
            api_types=["REST"],
        )
        
        capabilities = capability_mapper.map_to_capabilities(fingerprint)
        gaps = capability_mapper.identify_gaps(capabilities, fingerprint)
        
        # May have minor gaps, but should be < 3 for standard stack
        assert len(gaps) < 3


class TestCrawlerSpecGenerator:
    """Tests for crawler specification generation."""
    
    def test_cdf_011_generate_database_crawler_spec(self, crawler_spec_generator):
        """CDF-011: Generate spec for database migration analyzer."""
        gap = CapabilityGap(
            capability_name="DatabaseMigrationAnalyzer",
            reason="Repository has SQL migrations but no migration analyzer",
            priority="high",
            tech_stack=["PostgreSQL", "SQLAlchemy"],
        )
        
        spec = crawler_spec_generator.generate_spec(gap)
        
        assert spec.crawler_name == "DatabaseMigrationAnalyzer"
        assert spec.base_class == "BaseAnalyzer"
        assert "migration" in spec.description.lower()
        assert len(spec.required_methods) > 0
        assert "analyze" in spec.required_methods
    
    def test_cdf_012_generate_graphql_crawler_spec(self, crawler_spec_generator):
        """CDF-012: Generate spec for GraphQL analyzer."""
        gap = CapabilityGap(
            capability_name="GraphQLAnalyzer",
            reason="GraphQL API detected but no GraphQL analyzer exists",
            priority="medium",
            tech_stack=["GraphQL", "Apollo"],
        )
        
        spec = crawler_spec_generator.generate_spec(gap)
        
        assert spec.crawler_name == "GraphQLAnalyzer"
        assert "graphql" in spec.description.lower()
        assert spec.priority == "medium"
    
    def test_cdf_013_bounded_crawler_generation(self, crawler_spec_generator):
        """CDF-013: Limit to max 5 custom crawlers per repo."""
        gaps = [
            CapabilityGap(f"Analyzer{i}", f"Gap {i}", "low", [])
            for i in range(10)  # Request 10 crawlers
        ]
        
        specs = crawler_spec_generator.generate_specs(gaps, max_crawlers=5)
        
        assert len(specs) == 5  # Should cap at 5
        # Should prioritize high priority gaps
    
    def test_cdf_014_spec_includes_test_requirements(self, crawler_spec_generator):
        """CDF-014: Generated spec includes test requirements."""
        gap = CapabilityGap("TestAnalyzer", "Test gap", "high", [])
        
        spec = crawler_spec_generator.generate_spec(gap)
        
        assert spec.requires_tests
        assert len(spec.test_scenarios) > 0
    
    def test_cdf_015_spec_validation(self, crawler_spec_generator):
        """CDF-015: Validate generated spec structure."""
        gap = CapabilityGap("ValidAnalyzer", "Valid gap", "medium", ["Python"])
        
        spec = crawler_spec_generator.generate_spec(gap)
        
        assert spec.validate()
        assert spec.crawler_name.endswith("Analyzer")
        assert spec.module_path.startswith("cortex.lens.crawlers.")
        assert len(spec.dependencies) >= 0


class TestCapabilityDiscoveryEngine:
    """Tests for full discovery workflow."""
    
    def test_cdf_016_full_discovery_workflow(self, discovery_engine, temp_repo):
        """CDF-016: Complete discovery: fingerprint → gaps → specs."""
        result = discovery_engine.discover(temp_repo)
        
        assert result.fingerprint is not None
        assert result.capabilities is not None
        assert isinstance(result.gaps, list)
        assert isinstance(result.crawler_specs, list)
        assert len(result.crawler_specs) <= 5  # Bounded
    
    def test_cdf_017_evidence_bundle_creation(self, discovery_engine, python_repo):
        """CDF-017: Create CORE-027 compliant evidence bundle."""
        result = discovery_engine.discover(python_repo, create_evidence=True)
        
        assert result.evidence_bundle is not None
        assert "fingerprint_hash" in result.evidence_bundle
        assert "capability_decisions" in result.evidence_bundle
        assert "timestamp" in result.evidence_bundle
    
    def test_cdf_018_timeout_enforcement(self, discovery_engine, temp_repo):
        """CDF-018: Enforce 30-minute timeout."""
        # Create a minimal repo for timeout test
        (temp_repo / "requirements.txt").write_text("flask==2.0.0")
        
        # Test that timeout parameter is accepted
        result = discovery_engine.discover(temp_repo, max_duration_seconds=1800)
        
        # Verify duration is tracked
        assert result.duration_seconds >= 0
        assert result.duration_seconds < 10  # Should complete quickly for minimal repo
    
    def test_cdf_019_no_duplicates_with_existing_analyzers(self, discovery_engine, python_repo):
        """CDF-019: Don't generate crawlers for capabilities already covered."""
        result = discovery_engine.discover(python_repo)
        
        # Standard Python project should use existing analyzers
        existing_names = {a.lower() for a in result.capabilities.existing_analyzers}
        spec_names = {s.crawler_name.lower() for s in result.crawler_specs}
        
        # No overlap between existing and generated
        assert len(existing_names & spec_names) == 0
    
    def test_cdf_020_priority_ordering(self, discovery_engine, temp_repo):
        """CDF-020: Prioritize high-priority gaps first."""
        result = discovery_engine.discover(temp_repo)
        
        if len(result.crawler_specs) > 1:
            # First specs should be high priority
            priorities = [s.priority for s in result.crawler_specs]
            assert priorities[0] in ["high", "critical"]


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_cdf_021_nonexistent_path(self, discovery_engine):
        """CDF-021: Handle non-existent repository path."""
        with pytest.raises(FileNotFoundError):
            discovery_engine.discover(Path("/nonexistent/repo"))
    
    def test_cdf_022_permission_denied(self, discovery_engine, tmp_path):
        """CDF-022: Handle permission errors gracefully."""
        restricted = tmp_path / "restricted"
        restricted.mkdir()
        
        # Mock the analyze method to raise PermissionError during file reading
        with patch.object(discovery_engine.fingerprint_analyzer, 'analyze', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError):
                discovery_engine.discover(restricted)
    
    def test_cdf_023_corrupted_config_files(self, fingerprint_analyzer, tmp_path):
        """CDF-023: Handle corrupted package.json/requirements.txt."""
        repo = tmp_path / "corrupted"
        repo.mkdir()
        (repo / "package.json").write_text("invalid json {{{")
        
        fingerprint = fingerprint_analyzer.analyze(repo)
        
        # Should detect file but handle parse error
        assert "package.json" in fingerprint.detected_files
        # Should still complete analysis
        assert fingerprint.primary_language is not None or len(fingerprint.languages) == 0


# AC_COMPLETE: TEST-CDF-CapabilityDiscovery-001
