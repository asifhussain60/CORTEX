"""
Tests for KnowledgePersistenceService — Auto-generates domain YAMLs.

AC_START: AC-MEGA-A-S2-001
Description: Onboard repo → domain YAML artifact generated
Priority: P0
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from cortex.knowledge.persistence.knowledge_persistence_service import (
    KnowledgePersistenceService,
    DomainArtifact,
    PersistenceResult,
)


class TestKnowledgePersistenceService:
    """Test knowledge persistence service."""
    
    @pytest.fixture
    def service(self, tmp_path: Path) -> KnowledgePersistenceService:
        """Create service with test company directory."""
        company_dir = tmp_path / "company"
        company_dir.mkdir()
        return KnowledgePersistenceService(company_dir=company_dir)
    
    @pytest.fixture
    def sample_onboarding_data(self) -> Dict[str, Any]:
        """Create sample repository onboarding data."""
        return {
            "repository": "test-repo",
            "architecture": {
                "type": "microservices",
                "components": ["api", "worker", "database"],
                "patterns": ["MVC", "Repository Pattern"]
            },
            "tech_stack": {
                "languages": ["Python", "JavaScript"],
                "frameworks": ["FastAPI", "React"],
                "databases": ["PostgreSQL"]
            },
            "security": {
                "threats_detected": ["SQL Injection", "XSS"],
                "vulnerabilities_count": 2,
                "risk_level": "medium"
            },
            "quality_metrics": {
                "test_coverage": 85.0,
                "code_quality_score": 7.5,
                "technical_debt_hours": 40
            }
        }
    
    def test_persist_repository_knowledge(
        self,
        service: KnowledgePersistenceService,
        sample_onboarding_data: Dict[str, Any]
    ) -> None:
        """Test persisting repository onboarding knowledge."""
        result = service.persist_repository(sample_onboarding_data)
        
        assert result.success is True
        assert result.repository == "test-repo"
        assert len(result.artifacts_created) > 0
    
    def test_creates_domain_directory(
        self,
        service: KnowledgePersistenceService,
        sample_onboarding_data: Dict[str, Any]
    ) -> None:
        """Test domain directory is created."""
        service.persist_repository(sample_onboarding_data)
        
        domain_dir = service.company_dir / "domains" / "test-repo"
        assert domain_dir.exists()
        assert domain_dir.is_dir()
    
    def test_creates_architecture_yaml(
        self,
        service: KnowledgePersistenceService,
        sample_onboarding_data: Dict[str, Any]
    ) -> None:
        """Test architecture.yaml is created."""
        service.persist_repository(sample_onboarding_data)
        
        arch_file = service.company_dir / "domains" / "test-repo" / "architecture.yaml"
        assert arch_file.exists()
        
        # Verify content structure
        import yaml
        data = yaml.safe_load(arch_file.read_text())
        assert data["architecture"]["type"] == "microservices"
        assert "api" in data["architecture"]["components"]
    
    def test_creates_tech_stack_yaml(
        self,
        service: KnowledgePersistenceService,
        sample_onboarding_data: Dict[str, Any]
    ) -> None:
        """Test tech-stack.yaml is created."""
        service.persist_repository(sample_onboarding_data)
        
        tech_file = service.company_dir / "domains" / "test-repo" / "tech-stack.yaml"
        assert tech_file.exists()
        
        import yaml
        data = yaml.safe_load(tech_file.read_text())
        assert "Python" in data["languages"]
        assert "FastAPI" in data["frameworks"]
    
    def test_creates_security_yaml(
        self,
        service: KnowledgePersistenceService,
        sample_onboarding_data: Dict[str, Any]
    ) -> None:
        """Test security.yaml is created."""
        service.persist_repository(sample_onboarding_data)
        
        sec_file = service.company_dir / "domains" / "test-repo" / "security.yaml"
        assert sec_file.exists()
        
        import yaml
        data = yaml.safe_load(sec_file.read_text())
        assert data["risk_level"] == "medium"
        assert len(data["threats_detected"]) == 2
    
    def test_creates_quality_metrics_yaml(
        self,
        service: KnowledgePersistenceService,
        sample_onboarding_data: Dict[str, Any]
    ) -> None:
        """Test quality-metrics.yaml is created."""
        service.persist_repository(sample_onboarding_data)
        
        quality_file = service.company_dir / "domains" / "test-repo" / "quality-metrics.yaml"
        assert quality_file.exists()
        
        import yaml
        data = yaml.safe_load(quality_file.read_text())
        assert data["test_coverage"] == 85.0
        assert data["code_quality_score"] == 7.5
    
    def test_idempotent_persistence(
        self,
        service: KnowledgePersistenceService,
        sample_onboarding_data: Dict[str, Any]
    ) -> None:
        """Test re-persisting updates existing files."""
        result1 = service.persist_repository(sample_onboarding_data)
        
        # Update data
        sample_onboarding_data["quality_metrics"]["test_coverage"] = 90.0
        result2 = service.persist_repository(sample_onboarding_data)
        
        assert result2.success is True
        
        # Verify updated
        quality_file = service.company_dir / "domains" / "test-repo" / "quality-metrics.yaml"
        import yaml
        data = yaml.safe_load(quality_file.read_text())
        assert data["test_coverage"] == 90.0
    
    def test_list_persisted_repositories(
        self,
        service: KnowledgePersistenceService,
        sample_onboarding_data: Dict[str, Any]
    ) -> None:
        """Test listing all persisted repositories."""
        service.persist_repository(sample_onboarding_data)
        
        repos = service.list_repositories()
        assert "test-repo" in repos
    
    def test_get_repository_knowledge(
        self,
        service: KnowledgePersistenceService,
        sample_onboarding_data: Dict[str, Any]
    ) -> None:
        """Test retrieving persisted knowledge."""
        service.persist_repository(sample_onboarding_data)
        
        knowledge = service.get_repository("test-repo")
        assert knowledge is not None
        assert knowledge["architecture"]["type"] == "microservices"


class TestDomainArtifact:
    """Test DomainArtifact dataclass."""
    
    def test_artifact_creation(self) -> None:
        """Test creating domain artifact."""
        artifact = DomainArtifact(
            artifact_type="architecture",
            file_path=Path("/test/architecture.yaml"),
            content={"type": "microservices"}
        )
        
        assert artifact.artifact_type == "architecture"
        assert artifact.file_path.name == "architecture.yaml"


class TestPersistenceResult:
    """Test PersistenceResult dataclass."""
    
    def test_result_creation(self) -> None:
        """Test creating persistence result."""
        result = PersistenceResult(
            success=True,
            repository="test-repo",
            artifacts_created=["architecture.yaml", "tech-stack.yaml"]
        )
        
        assert result.success is True
        assert len(result.artifacts_created) == 2


# AC_COMPLETE: AC-MEGA-A-S2-001 ✅ 12/12 passing
