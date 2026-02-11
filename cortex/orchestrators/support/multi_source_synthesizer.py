"""
Multi-Source Synthesizer for Repository Onboarding.

Merges LENS analysis, Git history, and configuration files
into structured input for unified LLM synthesis.

AC_START: AC-MULTI-SOURCE-SYNTHESIZER-001
Authority: Phase 28.2.2 | CORE-008 (TDD) | CORE-035 (No Duplication)
"""

import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class GitHistory:
    """Repository Git history metadata."""

    first_commit_date: Optional[str] = None
    last_commit_date: Optional[str] = None
    total_commits: int = 0
    active_contributors: int = 0
    languages_used: List[str] = field(default_factory=list)
    primary_branch: str = "main"
    tags: List[str] = field(default_factory=list)
    recent_changes: List[str] = field(default_factory=list)

    def age_in_days(self) -> Optional[int]:
        """Calculate repository age in days."""
        if self.first_commit_date:
            try:
                first = datetime.fromisoformat(self.first_commit_date.replace("Z", "+00:00"))
                return (datetime.utcnow() - first).days
            except Exception:
                return None
        return None

    def is_active(self, days_threshold: int = 30) -> bool:
        """Check if repository is actively maintained."""
        if self.last_commit_date:
            try:
                last = datetime.fromisoformat(self.last_commit_date.replace("Z", "+00:00"))
                days_since = (datetime.utcnow() - last).days
                return days_since <= days_threshold
            except Exception:
                return False
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "first_commit": self.first_commit_date,
            "last_commit": self.last_commit_date,
            "total_commits": self.total_commits,
            "contributors": self.active_contributors,
            "languages": self.languages_used,
            "primary_branch": self.primary_branch,
            "tags": self.tags,
            "recent_changes": self.recent_changes,
            "age_days": self.age_in_days(),
            "is_active": self.is_active(),
        }


@dataclass
class ConfigAnalysis:
    """Configuration files analysis."""

    tech_stack: Dict[str, List[str]] = field(default_factory=dict)
    deployment_platforms: List[str] = field(default_factory=list)
    has_ci_cd: bool = False
    has_containerization: bool = False
    has_infrastructure_as_code: bool = False
    has_testing_config: bool = False
    database_systems: List[str] = field(default_factory=list)
    message_brokers: List[str] = field(default_factory=list)
    caching_systems: List[str] = field(default_factory=list)
    monitoring_systems: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tech_stack": self.tech_stack,
            "deployment_platforms": self.deployment_platforms,
            "ci_cd_enabled": self.has_ci_cd,
            "containerized": self.has_containerization,
            "infrastructure_as_code": self.has_infrastructure_as_code,
            "testing_configured": self.has_testing_config,
            "databases": self.database_systems,
            "message_brokers": self.message_brokers,
            "caching": self.caching_systems,
            "monitoring": self.monitoring_systems,
        }


@dataclass
class SynthesisInput:
    """Structured input for LLM synthesis."""

    repository_name: str
    repository_path: str
    lens_analysis: Dict[str, Any]
    git_history: GitHistory
    config_analysis: ConfigAnalysis
    documentation_snippets: List[str] = field(default_factory=list)
    readme_content: Optional[str] = None
    synthesis_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for LLM processing."""
        return {
            "repository_name": self.repository_name,
            "repository_path": self.repository_path,
            "synthesis_timestamp": self.synthesis_timestamp,
            "lens_analysis": self.lens_analysis,
            "git_history": self.git_history.to_dict(),
            "config_analysis": self.config_analysis.to_dict(),
            "documentation": {
                "readme": self.readme_content,
                "snippets": self.documentation_snippets,
            },
            "synthesis_context": {
                "repository_age": self.git_history.age_in_days(),
                "is_active": self.git_history.is_active(),
                "total_patterns": len(self.lens_analysis.get("patterns", [])),
                "api_count": len(self.lens_analysis.get("api_contracts", [])),
                "languages": self.git_history.languages_used,
            }
        }


class MultiSourceSynthesizer:
    """
    Synthesizes multiple data sources into unified input for LLM.

    Data sources:
    1. LENS analysis (code patterns, data flows, API contracts)
    2. Git history (evolution, contributors, maturity)
    3. Configuration files (tech stack, deployment info)
    4. Documentation (README, inline comments)
    """

    def __init__(self):
        """Initialize synthesizer."""
        pass

    def synthesize(
        self,
        repo_path: str,
        lens_analysis: Dict[str, Any],
    ) -> SynthesisInput:
        """
        Synthesize all data sources into unified input.

        Args:
            repo_path: Path to repository
            lens_analysis: LENS analysis result as dict

        Returns:
            SynthesisInput ready for LLM processing
        """
        repo_path_obj = Path(repo_path)
        repo_name = repo_path_obj.name

        logger.info(f"Starting multi-source synthesis for {repo_name}")

        # Extract Git history
        git_history = self._extract_git_history(repo_path_obj)

        # Analyze configuration
        config_analysis = self._analyze_configuration(repo_path_obj)

        # Extract documentation
        readme_content = self._extract_readme(repo_path_obj)
        doc_snippets = self._extract_documentation_snippets(repo_path_obj)

        synthesis_input = SynthesisInput(
            repository_name=repo_name,
            repository_path=str(repo_path_obj.absolute()),
            lens_analysis=lens_analysis,
            git_history=git_history,
            config_analysis=config_analysis,
            documentation_snippets=doc_snippets,
            readme_content=readme_content,
        )

        logger.info(f"Multi-source synthesis complete for {repo_name}")
        return synthesis_input

    def _extract_git_history(self, repo_path: Path) -> GitHistory:
        """Extract Git history metadata."""
        history = GitHistory()

        try:
            # Get first commit date
            result = subprocess.run(
                ["git", "log", "--diff-filter=A", "--name-only", "--pretty=format:%aI"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                if lines:
                    history.first_commit_date = lines[0]

            # Get last commit date
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%aI"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.stdout:
                history.last_commit_date = result.stdout.strip()

            # Get total commits
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.stdout:
                history.total_commits = int(result.stdout.strip())

            # Get contributor count
            result = subprocess.run(
                ["git", "shortlog", "-sn"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.stdout:
                history.active_contributors = len(result.stdout.strip().split("\n"))

            # Get tags
            result = subprocess.run(
                ["git", "tag"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.stdout:
                history.tags = result.stdout.strip().split("\n")[:10]  # Last 10 tags

            # Get recent commits
            result = subprocess.run(
                ["git", "log", "-10", "--oneline"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.stdout:
                history.recent_changes = result.stdout.strip().split("\n")

        except Exception as e:
            logger.warning(f"Error extracting Git history: {e}")

        return history

    def _analyze_configuration(self, repo_path: Path) -> ConfigAnalysis:
        """Analyze configuration files."""
        config = ConfigAnalysis()

        # Check for CI/CD
        ci_cd_files = [
            ".github/workflows/",
            ".gitlab-ci.yml",
            ".circleci/config.yml",
            "Jenkinsfile",
            ".travis.yml",
        ]
        config.has_ci_cd = any((repo_path / f).exists() for f in ci_cd_files)

        # Check for containerization
        config.has_containerization = (repo_path / "Dockerfile").exists()
        config.has_containerization |= (repo_path / "docker-compose.yml").exists()

        # Check for Infrastructure as Code
        iac_files = ["terraform/", "cloudformation/", "pulumi/", "helm/"]
        config.has_infrastructure_as_code = any(
            (repo_path / f).exists() for f in iac_files
        )

        # Check for testing config
        test_files = ["pytest.ini", "jest.config.js", ".mocharc.js", "karma.conf.js"]
        config.has_testing_config = any((repo_path / f).exists() for f in test_files)

        # Detect tech stack
        config.tech_stack = self._detect_tech_stack(repo_path)

        # Detect deployment platforms
        config.deployment_platforms = self._detect_deployment_platforms(repo_path)

        # Detect infrastructure
        self._detect_infrastructure_components(repo_path, config)

        return config

    def _detect_tech_stack(self, repo_path: Path) -> Dict[str, List[str]]:
        """Detect technology stack."""
        tech_stack = {}

        # Detect languages
        languages = set()
        file_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cs": "C#",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
        }

        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in file_extensions:
                languages.add(file_extensions[file_path.suffix])

        if languages:
            tech_stack["languages"] = sorted(list(languages))

        # Detect frameworks
        frameworks = []
        if (repo_path / "requirements.txt").exists():
            content = (repo_path / "requirements.txt").read_text(errors="ignore")
            if "django" in content.lower():
                frameworks.append("Django")
            if "fastapi" in content.lower():
                frameworks.append("FastAPI")
            if "flask" in content.lower():
                frameworks.append("Flask")

        if (repo_path / "package.json").exists():
            content = (repo_path / "package.json").read_text(errors="ignore")
            if "react" in content.lower():
                frameworks.append("React")
            if "vue" in content.lower():
                frameworks.append("Vue.js")
            if "express" in content.lower():
                frameworks.append("Express")
            if "nestjs" in content.lower():
                frameworks.append("NestJS")

        if frameworks:
            tech_stack["frameworks"] = frameworks

        return tech_stack

    def _detect_deployment_platforms(self, repo_path: Path) -> List[str]:
        """Detect deployment platforms."""
        platforms = []

        if (repo_path / "Procfile").exists():
            platforms.append("Heroku")

        if (repo_path / ".gcloud" / "app.yaml").exists():
            platforms.append("Google Cloud App Engine")

        if (repo_path / "serverless.yml").exists():
            platforms.append("AWS Lambda / Serverless Framework")

        if (repo_path / "amplify.yml").exists():
            platforms.append("AWS Amplify")

        if (repo_path / "vercel.json").exists():
            platforms.append("Vercel")

        if (repo_path / "netlify.toml").exists():
            platforms.append("Netlify")

        return platforms

    def _detect_infrastructure_components(self, repo_path: Path, config: ConfigAnalysis) -> None:
        """Detect infrastructure components (databases, message brokers, etc.)."""

        # Check configuration files
        docker_compose_files = list(repo_path.glob("docker-compose*.yml"))
        for dc_file in docker_compose_files:
            try:
                content = dc_file.read_text(errors="ignore").lower()
                if "postgres" in content:
                    config.database_systems.append("PostgreSQL")
                if "mysql" in content:
                    config.database_systems.append("MySQL")
                if "mongodb" in content:
                    config.database_systems.append("MongoDB")
                if "redis" in content:
                    config.caching_systems.append("Redis")
                if "rabbitmq" in content:
                    config.message_brokers.append("RabbitMQ")
                if "kafka" in content:
                    config.message_brokers.append("Kafka")
            except Exception as e:
                logger.warning(f"Error analyzing {dc_file}: {e}")

        # Check requirements files
        req_file = repo_path / "requirements.txt"
        if req_file.exists():
            try:
                content = req_file.read_text(errors="ignore").lower()
                if "psycopg" in content or "postgres" in content:
                    config.database_systems.append("PostgreSQL")
                if "pymongo" in content:
                    config.database_systems.append("MongoDB")
                if "redis" in content:
                    config.caching_systems.append("Redis")
                if "pika" in content or "amqp" in content:
                    config.message_brokers.append("RabbitMQ")
                if "prometheus" in content:
                    config.monitoring_systems.append("Prometheus")
                if "elasticsearch" in content:
                    config.monitoring_systems.append("Elasticsearch")
            except Exception as e:
                logger.warning(f"Error analyzing {req_file}: {e}")

    def _extract_readme(self, repo_path: Path) -> Optional[str]:
        """Extract README content."""
        for readme_name in ["README.md", "README.txt", "README.rst", "readme.md"]:
            readme_path = repo_path / readme_name
            if readme_path.exists():
                try:
                    return readme_path.read_text(encoding="utf-8", errors="ignore")[:2000]  # First 2000 chars
                except Exception as e:
                    logger.warning(f"Error reading {readme_path}: {e}")
        return None

    def _extract_documentation_snippets(self, repo_path: Path) -> List[str]:
        """Extract documentation snippets."""
        snippets = []

        doc_dirs = ["docs/", "documentation/", "Documentation/"]
        for doc_dir in doc_dirs:
            doc_path = repo_path / doc_dir
            if doc_path.exists():
                md_files = list(doc_path.glob("*.md"))[:5]  # First 5 files
                for md_file in md_files:
                    try:
                        content = md_file.read_text(encoding="utf-8", errors="ignore")[:500]
                        snippets.append(f"From {md_file.name}:\n{content}")
                    except Exception as e:
                        logger.warning(f"Error reading {md_file}: {e}")

        return snippets


def get_multi_source_synthesizer() -> MultiSourceSynthesizer:
    """Get or create singleton multi-source synthesizer."""
    return MultiSourceSynthesizer()


# AC_COMPLETE: AC-MULTI-SOURCE-SYNTHESIZER-001 ✅
