"""
Infrastructure Detector — Analyzes repositories for infrastructure elements.

Discovers FastAPI routes, Dockerfiles, Kubernetes manifests, cloud configs,
and infers platform requirements from repository contents.

Authority: Phase 08 — Registry & Docs Alignment
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum


class PlatformType(str, Enum):
    """Inferred platform types from infrastructure detection."""
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    EC2 = "ec2"
    LAMBDA = "lambda"
    CLOUD_RUN = "cloud-run"
    AKS = "aks"
    GKE = "gke"
    UNKNOWN = "unknown"


class CloudProvider(str, Enum):
    """Detected cloud providers."""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREM = "on-prem"
    HYBRID = "hybrid"


class ApplicationType(str, Enum):
    """Detected application types."""
    REST_API = "rest-api"
    GRAPHQL_API = "graphql-api"
    GRPC_SERVICE = "grpc-service"
    FRONTEND_APP = "frontend-app"
    WORKER = "worker"
    SCHEDULER = "scheduler"
    ML_MODEL = "ml-model"
    DATA_PIPELINE = "data-pipeline"
    UNKNOWN = "unknown"


@dataclass
class InfrastructureDetection:
    """Results from infrastructure detection scan."""
    repository_name: str
    application_type: ApplicationType = ApplicationType.UNKNOWN
    platforms: Set[PlatformType] = field(default_factory=set)
    cloud_providers: Set[CloudProvider] = field(default_factory=set)
    tech_stack: Set[str] = field(default_factory=set)
    exposed_apis: List[Dict[str, str]] = field(default_factory=list)
    consumed_apis: List[Dict[str, str]] = field(default_factory=list)
    internal_services: Set[str] = field(default_factory=set)
    databases: Set[str] = field(default_factory=set)
    caches: Set[str] = field(default_factory=set)
    queues: Set[str] = field(default_factory=set)
    deployment_method: Optional[str] = None
    health_check_url: Optional[str] = None
    has_dockerfile: bool = False
    has_kubernetes_manifests: bool = False
    has_helm_charts: bool = False
    has_terraform: bool = False
    has_cicd_workflow: bool = False
    ci_platforms: Set[str] = field(default_factory=set)
    errors: List[str] = field(default_factory=list)


class InfrastructureDetector:
    """
    Analyzes repository for infrastructure elements.
    Non-blocking detection — failures don't prevent onboarding.
    """

    def __init__(self, repo_path: Path):
        """Initialize detector with repository path."""
        self.repo_path = Path(repo_path)
        self.repo_name = self.repo_path.name

    def detect(self, repo_name: str) -> InfrastructureDetection:
        """
        Run full infrastructure detection.
        
        Args:
            repo_name: Repository name or path
            
        Returns:
            InfrastructureDetection object with all detected elements
        """
        detection = InfrastructureDetection(repository_name=repo_name)

        try:
            # Non-blocking detection pipeline
            self._detect_api_types(detection)
        except Exception as e:
            detection.errors.append(f"API detection failed: {str(e)}")

        try:
            self._detect_containerization(detection)
        except Exception as e:
            detection.errors.append(f"Containerization detection failed: {str(e)}")

        try:
            self._detect_kubernetes(detection)
        except Exception as e:
            detection.errors.append(f"Kubernetes detection failed: {str(e)}")

        try:
            self._detect_cloud_platform(detection)
        except Exception as e:
            detection.errors.append(f"Cloud platform detection failed: {str(e)}")

        try:
            self._detect_tech_stack(detection)
        except Exception as e:
            detection.errors.append(f"Tech stack detection failed: {str(e)}")

        try:
            self._detect_cicd(detection)
        except Exception as e:
            detection.errors.append(f"CI/CD detection failed: {str(e)}")

        try:
            self._detect_deployment_method(detection)
        except Exception as e:
            detection.errors.append(f"Deployment method detection failed: {str(e)}")

        return detection

    def _detect_api_types(self, detection: InfrastructureDetection) -> None:
        """Detect REST, GraphQL, gRPC APIs."""
        if not self.repo_path.exists():
            return

        # REST API patterns (FastAPI, Flask, Django, Express)
        rest_patterns = [
            r"@app\.(get|post|put|patch|delete|route)",  # FastAPI/Flask
            r"@router\.(get|post|put|patch|delete)",  # FastAPI routers
            r"path\(['\"]\/",  # FastAPI path()
            r"Query\(|Body\(|Header\(",  # FastAPI parameters
            r"def (get|post|put|delete|patch)_",  # Django view naming
            r"urlpatterns\s*=",  # Django URL routing
            r"app\.route\(|app\.get\(|app\.post\(",  # Generic routing
        ]

        # GraphQL patterns
        graphql_patterns = [
            r"@graphene\.ObjectType",
            r"graphene\.Schema",
            r"Query\(graphene\.",
            r"@strawberry\.type",
            r"schema\s*=\s*strawberry\.Schema",
            r"apollo|graphql-request|urql",
        ]

        # gRPC patterns
        grpc_patterns = [
            r"\.proto",  # Protocol buffers
            r"from.*grpc",
            r"grpc\.servicer_to_handler",
            r"grpc\.aio",
        ]

        has_rest = False
        has_graphql = False
        has_grpc = False

        for py_file in self.repo_path.rglob("*.py"):
            try:
                content = py_file.read_text(errors="ignore")
                if any(re.search(p, content) for p in rest_patterns):
                    has_rest = True
                if any(re.search(p, content) for p in graphql_patterns):
                    has_graphql = True
                if any(re.search(p, content) for p in grpc_patterns):
                    has_grpc = True
            except Exception:
                pass

        # Infer application type
        if has_rest:
            detection.application_type = ApplicationType.REST_API
            detection.exposed_apis.append({
                "type": "rest",
                "framework": "fastapi/flask",
                "inferred": True,
            })
        elif has_graphql:
            detection.application_type = ApplicationType.GRAPHQL_API
            detection.exposed_apis.append({
                "type": "graphql",
                "inferred": True,
            })
        elif has_grpc:
            detection.application_type = ApplicationType.GRPC_SERVICE
            detection.exposed_apis.append({
                "type": "grpc",
                "inferred": True,
            })

    def _detect_containerization(self, detection: InfrastructureDetection) -> None:
        """Detect Docker/containerization."""
        dockerfile = self.repo_path / "Dockerfile"
        if dockerfile.exists():
            detection.has_dockerfile = True
            detection.platforms.add(PlatformType.DOCKER)

        docker_compose = self.repo_path / "docker-compose.yaml"
        if docker_compose.exists():
            detection.platforms.add(PlatformType.DOCKER)

    def _detect_kubernetes(self, detection: InfrastructureDetection) -> None:
        """Detect Kubernetes manifests and Helm."""
        k8s_dir = self.repo_path / "k8s"
        if k8s_dir.exists() and k8s_dir.is_dir():
            detection.has_kubernetes_manifests = True
            detection.platforms.add(PlatformType.KUBERNETES)

        helm_dir = self.repo_path / "helm"
        if helm_dir.exists() and helm_dir.is_dir():
            detection.has_helm_charts = True
            detection.platforms.add(PlatformType.KUBERNETES)

        # K8s manifest files
        for yaml_file in self.repo_path.rglob("*.yaml"):
            try:
                content = yaml_file.read_text()
                if any(k in content for k in ["kind:", "apiVersion:", "metadata:"]):
                    if any(kind in content for kind in ["Deployment", "Service", "ConfigMap", "Pod"]):
                        detection.has_kubernetes_manifests = True
                        detection.platforms.add(PlatformType.KUBERNETES)
            except Exception:
                pass

    def _detect_cloud_platform(self, detection: InfrastructureDetection) -> None:
        """Detect cloud provider usage."""
        # AWS patterns
        if (self.repo_path / "serverless.yaml").exists():
            detection.cloud_providers.add(CloudProvider.AWS)
            detection.platforms.add(PlatformType.LAMBDA)

        if (self.repo_path / "terraform").exists():
            for tf_file in self.repo_path.rglob("*.tf"):
                try:
                    content = tf_file.read_text()
                    if "aws_" in content:
                        detection.cloud_providers.add(CloudProvider.AWS)
                    if "google_" in content or "gcp" in content:
                        detection.cloud_providers.add(CloudProvider.GCP)
                    if "azurerm_" in content:
                        detection.cloud_providers.add(CloudProvider.AZURE)
                except Exception:
                    pass
            detection.has_terraform = True

        # GCP patterns
        if (self.repo_path / "app.yaml").exists():  # App Engine
            detection.cloud_providers.add(CloudProvider.GCP)
            detection.platforms.add(PlatformType.CLOUD_RUN)

        # Azure patterns
        if (self.repo_path / "azure-pipelines.yml").exists():
            detection.cloud_providers.add(CloudProvider.AZURE)
            detection.has_cicd_workflow = True
            detection.ci_platforms.add("azure-pipelines")

    def _detect_tech_stack(self, detection: InfrastructureDetection) -> None:
        """Detect programming languages and frameworks."""
        # Python
        if list(self.repo_path.rglob("*.py")):
            detection.tech_stack.add("python")
            for py_file in self.repo_path.rglob("requirements*.txt"):
                try:
                    content = py_file.read_text()
                    if "fastapi" in content:
                        detection.tech_stack.add("fastapi")
                    if "django" in content:
                        detection.tech_stack.add("django")
                    if "flask" in content:
                        detection.tech_stack.add("flask")
                    if "sqlalchemy" in content:
                        detection.databases.add("postgresql")
                    if "redis" in content:
                        detection.caches.add("redis")
                except Exception:
                    pass

        # Node.js
        if (self.repo_path / "package.json").exists():
            detection.tech_stack.add("nodejs")
            try:
                content = (self.repo_path / "package.json").read_text()
                if "express" in content:
                    detection.tech_stack.add("express")
                if "next" in content:
                    detection.tech_stack.add("nextjs")
                if "react" in content:
                    detection.tech_stack.add("react")
            except Exception:
                pass

        # Go
        if (self.repo_path / "go.mod").exists():
            detection.tech_stack.add("go")

        # Java
        if (self.repo_path / "pom.xml").exists() or (self.repo_path / "build.gradle").exists():
            detection.tech_stack.add("java")

    def _detect_cicd(self, detection: InfrastructureDetection) -> None:
        """Detect CI/CD workflows."""
        github_workflows = self.repo_path / ".github" / "workflows"
        if github_workflows.exists():
            detection.has_cicd_workflow = True
            detection.ci_platforms.add("github-actions")

        gitlab_ci = self.repo_path / ".gitlab-ci.yml"
        if gitlab_ci.exists():
            detection.has_cicd_workflow = True
            detection.ci_platforms.add("gitlab-ci")

        circle_ci = self.repo_path / ".circleci" / "config.yml"
        if circle_ci.exists():
            detection.has_cicd_workflow = True
            detection.ci_platforms.add("circleci")

    def _detect_deployment_method(self, detection: InfrastructureDetection) -> None:
        """Infer deployment method."""
        if detection.has_dockerfile:
            detection.deployment_method = "docker"
        elif detection.has_helm_charts:
            detection.deployment_method = "helm"
        elif detection.has_terraform:
            detection.deployment_method = "terraform"
        elif detection.has_cicd_workflow:
            detection.deployment_method = "cicd-pipeline"
        else:
            detection.deployment_method = "manual"
