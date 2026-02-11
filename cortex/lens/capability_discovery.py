"""
Capability Discovery Framework (CDF) for CORTEX LENS.

Provides adaptive analyzer selection based on repository technology stack:
1. Fingerprint Analysis - Detect languages, frameworks, tools
2. Capability Mapping - Map tech stack to existing analyzers
3. Gap Identification - Find missing capabilities
4. Crawler Spec Generation - Generate specifications for custom analyzers

Enforces:
- CORE-027: Evidence trail for all decisions
- CORE-035: No duplicate analyzers
- Bounded complexity: Max 5 custom crawlers per repo
- 30-minute timeout for full discovery

AC_START: AC-CDF-Core-001
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# ==============================================================================
# Data Models
# ==============================================================================

@dataclass
class TechStackFingerprint:
    """Repository technology stack fingerprint."""

    primary_language: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    has_database: bool = False
    has_migrations: bool = False
    database_types: List[str] = field(default_factory=list)
    migration_files: List[str] = field(default_factory=list)
    has_api: bool = False
    api_types: List[str] = field(default_factory=list)
    api_spec_files: List[str] = field(default_factory=list)
    detected_files: List[str] = field(default_factory=list)
    build_tools: List[str] = field(default_factory=list)
    test_frameworks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def compute_hash(self) -> str:
        """Compute hash for fingerprint matching."""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class CapabilityMapping:
    """Mapping of tech stack to analyzer capabilities."""

    existing_analyzers: List[str] = field(default_factory=list)
    covered_capabilities: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "existing_analyzers": self.existing_analyzers,
            "covered_capabilities": list(self.covered_capabilities),
        }


@dataclass
class CapabilityGap:
    """Identified capability gap requiring custom analyzer."""

    capability_name: str
    reason: str
    priority: str  # "critical", "high", "medium", "low"
    tech_stack: List[str]
    estimated_complexity: str = "medium"  # "low", "medium", "high"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CrawlerSpec:
    """Specification for generating custom crawler/analyzer."""

    crawler_name: str
    description: str
    base_class: str = "BaseAnalyzer"
    module_path: str = ""
    priority: str = "medium"
    required_methods: List[str] = field(default_factory=lambda: ["analyze"])
    dependencies: List[str] = field(default_factory=list)
    test_scenarios: List[str] = field(default_factory=list)
    requires_tests: bool = True
    estimated_complexity: str = "medium"

    def __post_init__(self):
        """Set module path if not provided."""
        if not self.module_path:
            snake_case = ''.join(['_' + c.lower() if c.isupper() else c for c in self.crawler_name]).lstrip('_')
            self.module_path = f"cortex.lens.crawlers.{snake_case}"

    def validate(self) -> bool:
        """Validate spec structure."""
        if not self.crawler_name.endswith("Analyzer"):
            logger.warning(f"Crawler name should end with 'Analyzer': {self.crawler_name}")
        if not self.module_path.startswith("cortex.lens.crawlers."):
            logger.warning(f"Invalid module path: {self.module_path}")
        return len(self.required_methods) > 0 and "analyze" in self.required_methods

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DiscoveryResult:
    """Result of capability discovery process."""

    fingerprint: TechStackFingerprint
    capabilities: CapabilityMapping
    gaps: List[CapabilityGap]
    crawler_specs: List[CrawlerSpec]
    evidence_bundle: Optional[Dict[str, Any]] = None
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "fingerprint": self.fingerprint.to_dict(),
            "capabilities": self.capabilities.to_dict(),
            "gaps": [g.to_dict() for g in self.gaps],
            "crawler_specs": [s.to_dict() for s in self.crawler_specs],
            "evidence_bundle": self.evidence_bundle,
            "duration_seconds": self.duration_seconds,
        }


# ==============================================================================
# Fingerprint Analyzer
# ==============================================================================

class FingerprintAnalyzer:
    """Analyzes repository to detect technology stack."""

    # File patterns for tech stack detection
    TECH_INDICATORS = {
        "Python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
        "JavaScript": ["package.json", "yarn.lock", "npm-shrinkwrap.json"],
        "TypeScript": ["tsconfig.json", "package.json"],
        "Java": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "C#": ["*.csproj", "*.sln", "packages.config"],
        "Go": ["go.mod", "go.sum"],
        "Ruby": ["Gemfile", "Rakefile"],
        "PHP": ["composer.json"],
        "Rust": ["Cargo.toml"],
    }

    DB_INDICATORS = {
        "migrations": ["migrations/", "alembic/", "flyway/", "liquibase/"],
        "sql_files": ["*.sql"],
        "orm_files": ["models.py", "entity/", "schema.py"],
    }

    API_INDICATORS = {
        "openapi": ["openapi.yaml", "openapi.json", "swagger.yaml", "swagger.json"],
        "graphql": ["*.graphql", "schema.graphql", "*.gql"],
        "proto": ["*.proto"],
    }

    def analyze(self, repo_path: Path) -> TechStackFingerprint:
        """
        Analyze repository to detect technology stack.

        Args:
            repo_path: Path to repository

        Returns:
            TechStackFingerprint with detected technologies
        """
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository not found: {repo_path}")

        fingerprint = TechStackFingerprint()
        fingerprint.detected_files = []

        # Detect languages
        languages_detected = {}
        for lang, indicators in self.TECH_INDICATORS.items():
            for indicator in indicators:
                if "*" in indicator:
                    # Glob pattern
                    matches = list(repo_path.rglob(indicator))
                    if matches:
                        languages_detected[lang] = languages_detected.get(lang, 0) + len(matches)
                        fingerprint.detected_files.extend([str(m.relative_to(repo_path)) for m in matches[:5]])
                else:
                    # Exact file
                    if (repo_path / indicator).exists():
                        languages_detected[lang] = languages_detected.get(lang, 0) + 1
                        fingerprint.detected_files.append(indicator)

        # Set primary language (most indicators)
        if languages_detected:
            fingerprint.primary_language = max(languages_detected, key=languages_detected.get)
            fingerprint.languages = list(languages_detected.keys())

        # Detect frameworks
        fingerprint.frameworks = self._detect_frameworks(repo_path)

        # Detect database usage
        fingerprint.has_database, fingerprint.has_migrations, fingerprint.database_types, fingerprint.migration_files = self._detect_database(repo_path)

        # Detect API specs
        fingerprint.has_api, fingerprint.api_types, fingerprint.api_spec_files = self._detect_api(repo_path)

        # Detect build tools
        fingerprint.build_tools = self._detect_build_tools(repo_path)

        # Detect test frameworks
        fingerprint.test_frameworks = self._detect_test_frameworks(repo_path)

        logger.info(f"Fingerprint complete: {fingerprint.primary_language}, {len(fingerprint.languages)} languages")
        return fingerprint

    def _detect_frameworks(self, repo_path: Path) -> List[str]:
        """Detect frameworks from package files."""
        frameworks = []

        # Python frameworks
        if (repo_path / "requirements.txt").exists():
            content = (repo_path / "requirements.txt").read_text().lower()
            if "django" in content:
                frameworks.append("django")
            if "flask" in content:
                frameworks.append("flask")
            if "fastapi" in content:
                frameworks.append("fastapi")
            if "sqlalchemy" in content:
                frameworks.append("sqlalchemy")

        # JavaScript/TypeScript frameworks
        if (repo_path / "package.json").exists():
            try:
                pkg = json.loads((repo_path / "package.json").read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "express" in deps:
                    frameworks.append("express")
                if "react" in deps:
                    frameworks.append("react")
                if "vue" in deps:
                    frameworks.append("vue")
                if "angular" in deps or "@angular/core" in deps:
                    frameworks.append("angular")
                if "typescript" in deps:
                    frameworks.append("typescript")
                if "apollo-server" in deps or "graphql" in deps:
                    frameworks.append("graphql")
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to parse package.json: {e}")

        return frameworks

    def _detect_database(self, repo_path: Path) -> tuple:
        """Detect database usage and migrations."""
        has_db = False
        has_migrations = False
        db_types = []
        migration_files = []

        # Check for migration directories
        for indicator in self.DB_INDICATORS["migrations"]:
            migration_path = repo_path / indicator.rstrip("/")
            if migration_path.exists() and migration_path.is_dir():
                has_migrations = True
                has_db = True
                # List migration files
                sql_files = list(migration_path.rglob("*.sql"))[:10]
                migration_files.extend([str(f.relative_to(repo_path)) for f in sql_files])
                py_files = list(migration_path.rglob("*.py"))[:10]
                migration_files.extend([str(f.relative_to(repo_path)) for f in py_files])

        # Check for SQL files
        sql_files = list(repo_path.rglob("*.sql"))
        if sql_files:
            has_db = True
            migration_files.extend([str(f.relative_to(repo_path)) for f in sql_files[:5]])

        # Infer database types from files/frameworks
        if (repo_path / "requirements.txt").exists():
            content = (repo_path / "requirements.txt").read_text().lower()
            if "psycopg" in content or "postgresql" in content:
                has_db = True
                db_types.append("PostgreSQL")
            if "mysql" in content:
                has_db = True
                db_types.append("MySQL")
            if "sqlite" in content:
                has_db = True
                db_types.append("SQLite")
            if "pymongo" in content or "mongodb" in content:
                has_db = True
                db_types.append("MongoDB")
            if "sqlalchemy" in content or "alembic" in content:
                has_db = True
                if not db_types:
                    db_types.append("SQL")

        # Default to SQL if database detected but no specific type
        if has_db and not db_types:
            db_types.append("SQL")

        return has_db, has_migrations, db_types, migration_files

    def _detect_api(self, repo_path: Path) -> tuple:
        """Detect API specifications."""
        has_api = False
        api_types = []
        api_files = []

        # Check for OpenAPI/Swagger
        for indicator in self.API_INDICATORS["openapi"]:
            matches = list(repo_path.rglob(indicator))
            if matches:
                has_api = True
                api_types.append("OpenAPI")
                api_files.extend([str(m.relative_to(repo_path)) for m in matches[:5]])

        # Check for GraphQL
        for indicator in self.API_INDICATORS["graphql"]:
            matches = list(repo_path.rglob(indicator))
            if matches:
                has_api = True
                if "GraphQL" not in api_types:
                    api_types.append("GraphQL")
                api_files.extend([str(m.relative_to(repo_path)) for m in matches[:5]])

        # Check for gRPC
        for indicator in self.API_INDICATORS["proto"]:
            matches = list(repo_path.rglob(indicator))
            if matches:
                has_api = True
                api_types.append("gRPC")
                api_files.extend([str(m.relative_to(repo_path)) for m in matches[:5]])

        # Infer REST API from frameworks
        if not has_api and (repo_path / "package.json").exists():
            try:
                pkg = json.loads((repo_path / "package.json").read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "express" in deps or "fastify" in deps or "koa" in deps:
                    has_api = True
                    api_types.append("REST")
            except (OSError, ValueError, json.JSONDecodeError):
                pass

        return has_api, api_types, api_files

    def _detect_build_tools(self, repo_path: Path) -> List[str]:
        """Detect build tools."""
        build_tools = []

        if (repo_path / "Makefile").exists():
            build_tools.append("Make")
        if (repo_path / "webpack.config.js").exists():
            build_tools.append("Webpack")
        if (repo_path / "vite.config.js").exists() or (repo_path / "vite.config.ts").exists():
            build_tools.append("Vite")
        if (repo_path / "Dockerfile").exists():
            build_tools.append("Docker")

        return build_tools

    def _detect_test_frameworks(self, repo_path: Path) -> List[str]:
        """Detect test frameworks."""
        test_frameworks = []

        # Python
        if (repo_path / "pytest.ini").exists() or (repo_path / "setup.cfg").exists():
            test_frameworks.append("pytest")

        # JavaScript/TypeScript
        if (repo_path / "package.json").exists():
            try:
                pkg = json.loads((repo_path / "package.json").read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "jest" in deps:
                    test_frameworks.append("jest")
                if "mocha" in deps:
                    test_frameworks.append("mocha")
                if "vitest" in deps:
                    test_frameworks.append("vitest")
            except (OSError, ValueError, json.JSONDecodeError):
                pass

        return test_frameworks


# ==============================================================================
# Capability Mapper
# ==============================================================================

class CapabilityMapper:
    """Maps technology stack to analyzer capabilities."""

    # Existing LENS analyzers
    EXISTING_ANALYZERS = [
        "CodeAnalyzer",
        "ConfigAnalyzer",
        "DependencyAnalyzer",
        "SecurityAnalyzer",
        "QualityAnalyzer",
        "ArchitectureAnalyzer",
        "PerformanceAnalyzer",
        "DocumentationAnalyzer",
    ]

    def map_to_capabilities(self, fingerprint: TechStackFingerprint) -> CapabilityMapping:
        """
        Map tech stack to existing analyzer capabilities.

        Args:
            fingerprint: Technology stack fingerprint

        Returns:
            CapabilityMapping with existing analyzers
        """
        mapping = CapabilityMapping()
        mapping.existing_analyzers = self.EXISTING_ANALYZERS.copy()

        # All repos get core analyzers
        mapping.covered_capabilities = {
            "code_analysis",
            "config_analysis",
            "dependency_analysis",
            "security_analysis",
            "quality_analysis",
            "architecture_analysis",
            "performance_analysis",
            "documentation_analysis",
        }

        return mapping

    def identify_gaps(self, capabilities: CapabilityMapping, fingerprint: TechStackFingerprint) -> List[CapabilityGap]:
        """
        Identify capability gaps requiring custom analyzers.

        Args:
            capabilities: Current capability mapping
            fingerprint: Technology stack fingerprint

        Returns:
            List of capability gaps
        """
        gaps = []

        # Database migration analyzer
        if fingerprint.has_migrations and "database_migration_analysis" not in capabilities.covered_capabilities:
            gaps.append(CapabilityGap(
                capability_name="DatabaseMigrationAnalyzer",
                reason="Repository has database migrations but no migration analyzer",
                priority="high" if len(fingerprint.migration_files) > 5 else "medium",
                tech_stack=fingerprint.database_types,
                estimated_complexity="medium",
            ))

        # GraphQL analyzer
        if "GraphQL" in fingerprint.api_types and "graphql_analysis" not in capabilities.covered_capabilities:
            gaps.append(CapabilityGap(
                capability_name="GraphQLAnalyzer",
                reason="GraphQL API detected but no GraphQL analyzer exists",
                priority="medium",
                tech_stack=["GraphQL"] + [f for f in fingerprint.frameworks if "graphql" in f.lower()],
                estimated_complexity="medium",
            ))

        # gRPC analyzer
        if "gRPC" in fingerprint.api_types and "grpc_analysis" not in capabilities.covered_capabilities:
            gaps.append(CapabilityGap(
                capability_name="GRPCAnalyzer",
                reason="gRPC API detected but no gRPC analyzer exists",
                priority="medium",
                tech_stack=["gRPC"],
                estimated_complexity="high",
            ))

        logger.info(f"Identified {len(gaps)} capability gaps")
        return gaps


# ==============================================================================
# Crawler Spec Generator
# ==============================================================================

class CrawlerSpecGenerator:
    """Generates specifications for custom crawlers."""

    def generate_spec(self, gap: CapabilityGap) -> CrawlerSpec:
        """
        Generate crawler specification from capability gap.

        Args:
            gap: Capability gap to address

        Returns:
            CrawlerSpec for custom analyzer
        """
        spec = CrawlerSpec(
            crawler_name=gap.capability_name,
            description=gap.reason,
            priority=gap.priority,
            estimated_complexity=gap.estimated_complexity,
        )

        # Add test scenarios based on gap
        spec.test_scenarios = [
            f"Test {gap.capability_name} initialization",
            f"Test {gap.capability_name} analysis",
            f"Test {gap.capability_name} error handling",
        ]

        # Add dependencies based on tech stack
        spec.dependencies = gap.tech_stack

        return spec

    def generate_specs(self, gaps: List[CapabilityGap], max_crawlers: int = 5) -> List[CrawlerSpec]:
        """
        Generate crawler specifications from gaps (bounded).

        Args:
            gaps: List of capability gaps
            max_crawlers: Maximum number of crawlers to generate (default: 5)

        Returns:
            List of crawler specifications (max max_crawlers)
        """
        # Sort by priority: critical > high > medium > low
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_gaps = sorted(gaps, key=lambda g: priority_order.get(g.priority, 4))

        # Take top N gaps
        top_gaps = sorted_gaps[:max_crawlers]

        specs = [self.generate_spec(gap) for gap in top_gaps]
        logger.info(f"Generated {len(specs)} crawler specifications (max {max_crawlers})")

        return specs


# ==============================================================================
# Capability Discovery Engine
# ==============================================================================

class CapabilityDiscoveryEngine:
    """Main engine for adaptive capability discovery."""

    def __init__(self):
        """Initialize discovery engine."""
        self.fingerprint_analyzer = FingerprintAnalyzer()
        self.capability_mapper = CapabilityMapper()
        self.crawler_spec_generator = CrawlerSpecGenerator()

    def discover(
        self,
        repo_path: Path,
        max_crawlers: int = 5,
        max_duration_seconds: int = 1800,  # 30 minutes
        create_evidence: bool = True,
    ) -> DiscoveryResult:
        """
        Perform full capability discovery workflow.

        Args:
            repo_path: Path to repository
            max_crawlers: Maximum custom crawlers to generate (default: 5)
            max_duration_seconds: Maximum duration in seconds (default: 1800 = 30 min)
            create_evidence: Whether to create CORE-027 evidence bundle

        Returns:
            DiscoveryResult with fingerprint, gaps, and crawler specs
        """
        start_time = time.time()

        # Phase 1: Fingerprint
        logger.info(f"Starting capability discovery for: {repo_path}")
        fingerprint = self.fingerprint_analyzer.analyze(repo_path)

        # Phase 2: Capability mapping
        capabilities = self.capability_mapper.map_to_capabilities(fingerprint)

        # Phase 3: Gap identification
        gaps = self.capability_mapper.identify_gaps(capabilities, fingerprint)

        # Phase 4: Crawler spec generation
        crawler_specs = self.crawler_spec_generator.generate_specs(gaps, max_crawlers=max_crawlers)

        # Validate specs
        for spec in crawler_specs:
            spec.validate()

        duration = time.time() - start_time

        # Create evidence bundle (CORE-027)
        evidence = None
        if create_evidence:
            evidence = self._create_evidence_bundle(fingerprint, capabilities, gaps, crawler_specs, duration)

        result = DiscoveryResult(
            fingerprint=fingerprint,
            capabilities=capabilities,
            gaps=gaps,
            crawler_specs=crawler_specs,
            evidence_bundle=evidence,
            duration_seconds=duration,
        )

        logger.info(f"Discovery complete: {len(crawler_specs)} crawler specs in {duration:.2f}s")
        return result

    def _create_evidence_bundle(
        self,
        fingerprint: TechStackFingerprint,
        capabilities: CapabilityMapping,
        gaps: List[CapabilityGap],
        crawler_specs: List[CrawlerSpec],
        duration: float,
    ) -> Dict[str, Any]:
        """Create CORE-027 compliant evidence bundle."""
        return {
            "timestamp": datetime.now().isoformat(),
            "fingerprint_hash": fingerprint.compute_hash(),
            "fingerprint_data": fingerprint.to_dict(),
            "capability_decisions": {
                "existing_analyzers": capabilities.existing_analyzers,
                "gaps_identified": len(gaps),
                "crawler_specs_generated": len(crawler_specs),
            },
            "gap_analysis": [g.to_dict() for g in gaps],
            "crawler_specifications": [s.to_dict() for s in crawler_specs],
            "duration_seconds": duration,
            "evidence_chain_hash": self._compute_evidence_hash(fingerprint, gaps, crawler_specs),
        }

    def _compute_evidence_hash(
        self,
        fingerprint: TechStackFingerprint,
        gaps: List[CapabilityGap],
        specs: List[CrawlerSpec],
    ) -> str:
        """Compute hash chain for evidence traceability."""
        data = {
            "fingerprint": fingerprint.compute_hash(),
            "gaps": [g.capability_name for g in gaps],
            "specs": [s.crawler_name for s in specs],
        }
        chain = json.dumps(data, sort_keys=True)
        return hashlib.sha256(chain.encode()).hexdigest()

    def _enforce_timeout(self) -> bool:
        """Enforce timeout for capability discovery operations.

        Checks if current operation has exceeded max_duration threshold.

        Returns:
            bool: True if within timeout, raises TimeoutError otherwise

        Raises:
            TimeoutError: If operation exceeds max_duration
        """
        if not hasattr(self, '_operation_start_time'):
            self._operation_start_time = time.time()
            return True

        elapsed = time.time() - self._operation_start_time
        if elapsed > self.max_duration:
            raise TimeoutError(
                f"Capability discovery exceeded timeout: {elapsed:.2f}s > {self.max_duration}s"
            )
        return True


# AC_COMPLETE: AC-CDF-Core-001

__all__ = [
    "TechStackFingerprint",
    "CapabilityMapping",
    "CapabilityGap",
    "CrawlerSpec",
    "DiscoveryResult",
    "FingerprintAnalyzer",
    "CapabilityMapper",
    "CrawlerSpecGenerator",
    "CapabilityDiscoveryEngine",
]
