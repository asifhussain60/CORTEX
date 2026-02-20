"""InfrastructureDetector — automated infrastructure detection from repository code.

Scans repository files for infrastructure hints:
- API framework declarations (FastAPI, Express, gRPC)
- Container definitions (Dockerfile, docker-compose)
- Kubernetes manifests (k8s/, helm/)
- Cloud provider configs (azure-pipelines, GitHub Actions, serverless)
- API client imports (consumed APIs)

All detection is non-blocking: failures emit warnings, never break onboarding.

Authority: Phase 08 — Registry & Docs Alignment (R8)
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class InfrastructureHint:
    """A detected infrastructure hint from repository code."""

    category: str  # 'api', 'platform', 'application', 'cloud'
    source_file: str  # File that triggered detection
    inferred_type: str  # e.g. 'REST API exposed', 'containerized'
    confidence: float  # 0.0 - 1.0
    details: Dict[str, Any] = field(default_factory=dict)


class InfrastructureDetector:
    """Detects infrastructure patterns from repository source code.

    All detection methods are non-blocking. If detection fails for any
    reason, the detector logs a warning and continues.

    Usage:
        detector = InfrastructureDetector(repo_path="/path/to/repo")
        hints = detector.detect_all()
        draft_yamls = detector.generate_drafts(hints)
    """

    # API framework patterns
    API_PATTERNS: Dict[str, re.Pattern] = {
        "fastapi": re.compile(
            r"@app\.(get|post|put|delete|patch|route)\(|from\s+fastapi\s+import",
            re.IGNORECASE,
        ),
        "flask": re.compile(
            r"@app\.route\(|from\s+flask\s+import",
            re.IGNORECASE,
        ),
        "express": re.compile(
            r"app\.(get|post|put|delete|patch)\(|require\(['\"]express['\"]\)",
            re.IGNORECASE,
        ),
        "grpc": re.compile(
            r"\.proto$|grpc\.|from\s+grpc\s+import",
            re.IGNORECASE,
        ),
    }

    # Container patterns
    CONTAINER_FILES = ["Dockerfile", "docker-compose.yaml", "docker-compose.yml"]

    # Kubernetes patterns
    K8S_PATTERNS = ["k8s/", "kubernetes/", "helm/", "Chart.yaml"]

    # Cloud config patterns
    CLOUD_PATTERNS: Dict[str, List[str]] = {
        "azure": ["azure-pipelines.yml", "azure-pipelines.yaml"],
        "github": [".github/workflows/"],
        "aws": ["serverless.yaml", "serverless.yml", "template.yaml", "sam.yaml"],
        "gcp": ["app.yaml", "cloudbuild.yaml"],
    }

    def __init__(self, repo_path: str) -> None:
        """Initialize detector with repository path.

        Args:
            repo_path: Absolute path to the repository root.
        """
        self.repo_path = Path(repo_path)
        self._hints: List[InfrastructureHint] = []

    def detect_all(self) -> List[InfrastructureHint]:
        """Run all detection methods and return aggregated hints.

        Returns:
            List of InfrastructureHint objects. Empty list on total failure.
        """
        self._hints = []
        detectors = [
            self.detect_api_frameworks,
            self.detect_containers,
            self.detect_kubernetes,
            self.detect_cloud_config,
        ]
        for detector_fn in detectors:
            try:
                detector_fn()
            except Exception as e:
                logger.warning(
                    "Infrastructure detection failed in %s: %s",
                    detector_fn.__name__,
                    str(e),
                )
        return self._hints

    def detect_api_frameworks(self) -> None:
        """Detect API framework usage (FastAPI, Flask, Express, gRPC).

        Scans Python and JavaScript files for framework-specific patterns.
        """
        if not self.repo_path.exists():
            return
        extensions = {".py", ".js", ".ts", ".proto"}
        for source_file in self._walk_files(extensions):
            try:
                content = source_file.read_text(errors="ignore")
                for framework, pattern in self.API_PATTERNS.items():
                    if pattern.search(content):
                        self._hints.append(
                            InfrastructureHint(
                                category="api",
                                source_file=str(source_file.relative_to(self.repo_path)),
                                inferred_type=f"REST API exposed ({framework})",
                                confidence=0.85,
                                details={"framework": framework},
                            )
                        )
            except Exception as e:
                logger.warning("Failed to scan %s: %s", source_file, e)

    def detect_containers(self) -> None:
        """Detect containerized deployment (Dockerfile, docker-compose)."""
        for container_file in self.CONTAINER_FILES:
            candidate = self.repo_path / container_file
            if candidate.exists():
                self._hints.append(
                    InfrastructureHint(
                        category="platform",
                        source_file=container_file,
                        inferred_type="containerized platform requirement",
                        confidence=0.95,
                        details={"file": container_file},
                    )
                )

    def detect_kubernetes(self) -> None:
        """Detect Kubernetes manifests (k8s/, helm/, Chart.yaml)."""
        for k8s_pattern in self.K8S_PATTERNS:
            candidate = self.repo_path / k8s_pattern
            if candidate.exists():
                self._hints.append(
                    InfrastructureHint(
                        category="platform",
                        source_file=k8s_pattern,
                        inferred_type="Kubernetes platform",
                        confidence=0.90,
                        details={"pattern": k8s_pattern},
                    )
                )

    def detect_cloud_config(self) -> None:
        """Detect cloud provider configurations (Azure, GitHub, AWS, GCP)."""
        for provider, patterns in self.CLOUD_PATTERNS.items():
            for pattern in patterns:
                candidate = self.repo_path / pattern
                if candidate.exists():
                    self._hints.append(
                        InfrastructureHint(
                            category="cloud",
                            source_file=pattern,
                            inferred_type=f"cloud platform usage ({provider})",
                            confidence=0.80,
                            details={"provider": provider, "config_file": pattern},
                        )
                    )

    def generate_drafts(
        self,
        hints: List[InfrastructureHint],
        repo_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Generate draft infrastructure YAML content from detected hints.

        Args:
            hints: List of detected infrastructure hints.
            repo_name: Optional repository name for draft file naming.

        Returns:
            Dict mapping draft filenames to their YAML content as dicts.
        """
        if not repo_name:
            repo_name = self.repo_path.name

        drafts: Dict[str, Dict[str, Any]] = {}

        # Always create app draft
        drafts[f"draft-app-{repo_name}.yaml"] = {
            "name": repo_name,
            "type": "api-service",
            "repository": repo_name,
            "status": "draft",
            "source": "auto-detected",
            "tech_stack": self._infer_tech_stack(hints),
            "apis_exposed": [
                h.details.get("framework", "unknown")
                for h in hints
                if h.category == "api"
            ],
        }

        # Create API draft if API hints found
        api_hints = [h for h in hints if h.category == "api"]
        if api_hints:
            drafts[f"draft-api-{repo_name}.yaml"] = {
                "name": f"{repo_name}-api",
                "type": "rest",
                "version": "1.0.0",
                "owner_repo": repo_name,
                "status": "draft",
                "source": "auto-detected",
                "frameworks_detected": list(
                    {h.details.get("framework", "unknown") for h in api_hints}
                ),
            }

        return drafts

    def _walk_files(self, extensions: set) -> List[Path]:
        """Walk repository files with given extensions, skipping hidden dirs.

        Args:
            extensions: Set of file extensions to include (e.g., {'.py', '.js'}).

        Returns:
            List of matching file paths.
        """
        results = []
        if not self.repo_path.exists():
            return results
        try:
            for path in self.repo_path.rglob("*"):
                if any(part.startswith(".") for part in path.parts):
                    continue
                if path.is_file() and path.suffix in extensions:
                    results.append(path)
        except Exception as e:
            logger.warning("File walk failed: %s", e)
        return results

    def _infer_tech_stack(self, hints: List[InfrastructureHint]) -> List[str]:
        """Infer technology stack from detected hints.

        Args:
            hints: List of detected infrastructure hints.

        Returns:
            List of technology strings.
        """
        stack = set()
        for hint in hints:
            if hint.category == "api":
                framework = hint.details.get("framework", "")
                if framework in ("fastapi", "flask"):
                    stack.add("python")
                elif framework in ("express",):
                    stack.add("node.js")
                elif framework == "grpc":
                    stack.add("grpc")
            elif hint.category == "platform":
                if "container" in hint.inferred_type:
                    stack.add("docker")
                if "Kubernetes" in hint.inferred_type:
                    stack.add("kubernetes")
            elif hint.category == "cloud":
                provider = hint.details.get("provider", "")
                if provider:
                    stack.add(provider)
        return sorted(stack)
