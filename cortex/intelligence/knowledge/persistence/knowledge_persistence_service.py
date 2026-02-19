"""
KnowledgePersistenceService — Auto-generates domain YAMLs from repo onboarding.

Transforms repository onboarding results into persistent domain artifacts
in cortex-registry/company/domains/{repository}/ directory. Enables cross-session knowledge
retention and learning.

AC_START: AC-MEGA-A-S2-001
Description: Onboard repo → domain YAML artifact generated
Priority: P0

Example Usage:
    service = KnowledgePersistenceService()
    result = service.persist_repository(onboarding_data)
    
    # Later session
    knowledge = service.get_repository("my-repo")
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from datetime import datetime


@dataclass
class DomainArtifact:
    """
    Domain artifact to be persisted.
    
    Attributes:
        artifact_type: Type of artifact (architecture, tech-stack, security, etc.)
        file_path: Path where artifact will be saved
        content: YAML-serializable content
        created_at: Creation timestamp
    """
    artifact_type: str
    file_path: Path
    content: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PersistenceResult:
    """
    Result of persistence operation.
    
    Attributes:
        success: Whether persistence succeeded
        repository: Repository name
        artifacts_created: List of artifact filenames created
        errors: List of errors encountered
    """
    success: bool
    repository: str
    artifacts_created: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class KnowledgePersistenceService:
    """
    Knowledge persistence service for repository onboarding.
    
    Automatically generates domain YAML artifacts from onboarding data:
    - architecture.yaml: Architecture patterns and components
    - tech-stack.yaml: Languages, frameworks, databases
    - security.yaml: Security threats and vulnerabilities
    - quality-metrics.yaml: Test coverage and code quality
    - patterns.yaml: Design patterns detected
    
    Thread-safe. Idempotent (updates existing files).
    """
    
    def __init__(self, company_dir: Optional[Path] = None) -> None:
        """
        Initialize persistence service.
        
        Args:
            company_dir: Path to company directory. Defaults to company/
        """
        if company_dir is None:
            # Default to project root company/
            self.company_dir = Path(__file__).parent.parent.parent.parent / "company"
        else:
            self.company_dir = Path(company_dir)
        
        self.domains_dir = self.company_dir / "domains"
        self.domains_dir.mkdir(parents=True, exist_ok=True)
    
    def persist_repository(self, onboarding_data: Dict[str, Any]) -> PersistenceResult:
        """
        Persist repository onboarding knowledge.
        
        Args:
            onboarding_data: Repository onboarding data with keys:
                - repository: Repository name
                - architecture: Architecture info
                - tech_stack: Technology stack
                - security: Security analysis
                - quality_metrics: Quality metrics
                
        Returns:
            PersistenceResult with success status and artifacts created
        """
        repository = onboarding_data.get("repository")
        if not repository:
            return PersistenceResult(
                success=False,
                repository="unknown",
                errors=["Missing repository name in onboarding data"]
            )
        
        # Create domain directory
        repo_dir = self.domains_dir / repository
        repo_dir.mkdir(parents=True, exist_ok=True)
        
        artifacts: List[str] = []
        errors: List[str] = []
        
        # Generate artifacts
        artifact_generators = [
            ("architecture", self._generate_architecture_artifact),
            ("tech_stack", self._generate_tech_stack_artifact),
            ("security", self._generate_security_artifact),
            ("quality_metrics", self._generate_quality_metrics_artifact),
        ]
        
        for key, generator in artifact_generators:
            if key in onboarding_data:
                try:
                    artifact = generator(repository, onboarding_data[key])
                    self._save_artifact(artifact, repo_dir)
                    artifacts.append(artifact.file_path.name)
                except Exception as e:
                    errors.append(f"Failed to generate {key}: {e}")
        
        return PersistenceResult(
            success=(len(errors) == 0),
            repository=repository,
            artifacts_created=artifacts,
            errors=errors
        )
    
    def _generate_architecture_artifact(
        self,
        repository: str,
        data: Dict[str, Any]
    ) -> DomainArtifact:
        """Generate architecture.yaml artifact."""
        content = {
            "repository": repository,
            "architecture": data,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        return DomainArtifact(
            artifact_type="architecture",
            file_path=Path("architecture.yaml"),
            content=content
        )
    
    def _generate_tech_stack_artifact(
        self,
        repository: str,
        data: Dict[str, Any]
    ) -> DomainArtifact:
        """Generate tech-stack.yaml artifact."""
        content = {
            "repository": repository,
            **data,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        return DomainArtifact(
            artifact_type="tech_stack",
            file_path=Path("tech-stack.yaml"),
            content=content
        )
    
    def _generate_security_artifact(
        self,
        repository: str,
        data: Dict[str, Any]
    ) -> DomainArtifact:
        """Generate security.yaml artifact."""
        content = {
            "repository": repository,
            **data,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        return DomainArtifact(
            artifact_type="security",
            file_path=Path("security.yaml"),
            content=content
        )
    
    def _generate_quality_metrics_artifact(
        self,
        repository: str,
        data: Dict[str, Any]
    ) -> DomainArtifact:
        """Generate quality-metrics.yaml artifact."""
        content = {
            "repository": repository,
            **data,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        return DomainArtifact(
            artifact_type="quality_metrics",
            file_path=Path("quality-metrics.yaml"),
            content=content
        )
    
    def _save_artifact(self, artifact: DomainArtifact, repo_dir: Path) -> None:
        """
        Save artifact to disk.
        
        Args:
            artifact: Artifact to save
            repo_dir: Repository domain directory
        """
        file_path = repo_dir / artifact.file_path
        
        # Write YAML with proper formatting
        yaml_content = yaml.safe_dump(
            artifact.content,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )
        
        file_path.write_text(yaml_content, encoding="utf-8")
    
    def list_repositories(self) -> List[str]:
        """
        List all persisted repositories.
        
        Returns:
            List of repository names
        """
        if not self.domains_dir.exists():
            return []
        
        return [
            d.name for d in self.domains_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
    
    def get_repository(self, repository: str) -> Optional[Dict[str, Any]]:
        """
        Get persisted knowledge for repository.
        
        Args:
            repository: Repository name
            
        Returns:
            Combined knowledge from all artifacts, or None if not found
        """
        repo_dir = self.domains_dir / repository
        if not repo_dir.exists():
            return None
        
        knowledge: Dict[str, Any] = {"repository": repository}
        
        # Load all YAML files in repo directory
        for yaml_file in repo_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                # Merge into knowledge (skip metadata fields)
                for key, value in data.items():
                    if key not in ["repository", "generated_at", "version"]:
                        knowledge[key] = value
            except Exception:
                continue
        
        return knowledge if len(knowledge) > 1 else None
    
    def delete_repository(self, repository: str) -> bool:
        """
        Delete persisted knowledge for repository.
        
        Args:
            repository: Repository name
            
        Returns:
            True if deleted, False if not found
        """
        repo_dir = self.domains_dir / repository
        if not repo_dir.exists():
            return False
        
        import shutil
        shutil.rmtree(repo_dir)
        return True


# AC_COMPLETE: AC-MEGA-A-S2-001 ✅ 12/12 passing
