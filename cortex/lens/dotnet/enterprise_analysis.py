"""Comprehensive .NET Enterprise LENS Analysis Suite (S4-S9).

Stages 4-9: Database projects, EF migrations, Azure DevOps, WCF services,
visualization, and repository onboarding integration.

AC-PHASE55-S4-S9: Multi-stage .NET analyzers + integration
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


# ============================================================================
# STAGE 4: SQL Server Database Project Analyzer
# ============================================================================


@dataclass
class DatabaseProject:
    """Represents a SQL Server database project."""

    name: str
    path: Path
    tables: List[str] = field(default_factory=list)
    stored_procedures: List[str] = field(default_factory=list)
    views: List[str] = field(default_factory=list)
    database_references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "path": str(self.path),
            "tables": self.tables,
            "stored_procedures": self.stored_procedures,
            "views": self.views,
            "database_references": self.database_references,
        }


class DatabaseProjectAnalyzer:
    """Analyzes SQL Server database projects (.sqlproj)."""

    def __init__(self, solution_root: Path):
        """Initialize analyzer."""
        self.solution_root = Path(solution_root)
        self.database_projects: Dict[str, DatabaseProject] = {}

    def analyze_database_projects(self) -> Dict[str, DatabaseProject]:
        """Analyze all .sqlproj files in solution.

        Returns:
            Dictionary mapping project names to DatabaseProject objects
        """
        for sqlproj_file in self.solution_root.rglob("*.sqlproj"):
            self._analyze_project(sqlproj_file)

        return self.database_projects

    def _analyze_project(self, sqlproj_path: Path) -> None:
        """Analyze a single .sqlproj file.

        Args:
            sqlproj_path: Path to .sqlproj file
        """
        project_name = sqlproj_path.stem
        project = DatabaseProject(name=project_name, path=sqlproj_path)

        try:
            tree = ET.parse(str(sqlproj_path))
            root = tree.getroot()

            # Extract Build items (SQL scripts)
            for build_item in root.findall(".//Build"):
                include = build_item.get("Include", "")
                if include:
                    self._analyze_sql_file(sqlproj_path.parent / include, project)

            # Look for database references
            for db_ref in root.findall(".//DatabaseReference"):
                location = db_ref.get("Location", "")
                if location:
                    project.database_references.append(location)

        except Exception as e:
            logger.error(f"Error analyzing {sqlproj_path}: {e}")

        self.database_projects[project_name] = project

    def _analyze_sql_file(self, sql_path: Path, project: DatabaseProject) -> None:
        """Analyze SQL file for schema objects.

        Args:
            sql_path: Path to .sql file
            project: DatabaseProject to update
        """
        if not sql_path.exists():
            return

        try:
            content = sql_path.read_text()

            # Extract CREATE TABLE statements
            table_pattern = r"CREATE\s+TABLE\s+\[?(\w+)\]?\.\[?(\w+)\]?"
            for match in re.finditer(table_pattern, content, re.IGNORECASE):
                schema = match.group(1)
                table = match.group(2)
                project.tables.append(f"{schema}.{table}")

            # Extract CREATE PROCEDURE statements
            proc_pattern = r"CREATE\s+PROCEDURE\s+\[?(\w+)\]?\.\[?(\w+)\]?"
            for match in re.finditer(proc_pattern, content, re.IGNORECASE):
                schema = match.group(1)
                proc = match.group(2)
                project.stored_procedures.append(f"{schema}.{proc}")

            # Extract CREATE VIEW statements
            view_pattern = r"CREATE\s+VIEW\s+\[?(\w+)\]?\.\[?(\w+)\]?"
            for match in re.finditer(view_pattern, content, re.IGNORECASE):
                schema = match.group(1)
                view = match.group(2)
                project.views.append(f"{schema}.{view}")

        except Exception as e:
            logger.error(f"Error reading {sql_path}: {e}")


# ============================================================================
# STAGE 5: Entity Framework Migration Analyzer
# ============================================================================


@dataclass
class EFMigration:
    """Represents an Entity Framework migration."""

    name: str
    timestamp: str
    up_changes: List[str] = field(default_factory=list)
    down_changes: List[str] = field(default_factory=list)


@dataclass
class DbContext:
    """Represents an EF DbContext."""

    name: str
    path: Path
    migrations: List[EFMigration] = field(default_factory=list)
    pending_migrations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "path": str(self.path),
            "migration_count": len(self.migrations),
            "migrations": [
                {
                    "name": m.name,
                    "timestamp": m.timestamp,
                    "changes": m.up_changes + m.down_changes,
                }
                for m in self.migrations
            ],
            "pending_migrations": self.pending_migrations,
        }


class EntityFrameworkMigrationAnalyzer:
    """Analyzes Entity Framework migrations."""

    MIGRATION_PATTERN = re.compile(r"(\d{14})_(.+)\.cs$")

    def __init__(self, solution_root: Path):
        """Initialize analyzer."""
        self.solution_root = Path(solution_root)
        self.db_contexts: Dict[str, DbContext] = {}

    def analyze_migrations(self) -> Dict[str, DbContext]:
        """Analyze all EF migrations in solution.

        Returns:
            Dictionary mapping context names to DbContext objects
        """
        # Find Migrations folders
        for migrations_dir in self.solution_root.rglob("Migrations"):
            self._analyze_migrations_folder(migrations_dir)

        return self.db_contexts

    def _analyze_migrations_folder(self, migrations_dir: Path) -> None:
        """Analyze a Migrations folder.

        Args:
            migrations_dir: Path to Migrations directory
        """
        # Infer DbContext name from parent directory or config
        context_name = migrations_dir.parent.name

        if context_name not in self.db_contexts:
            self.db_contexts[context_name] = DbContext(
                name=context_name, path=migrations_dir.parent
            )

        context = self.db_contexts[context_name]

        # Find migration files
        for migration_file in sorted(migrations_dir.glob("*_*.cs")):
            match = self.MIGRATION_PATTERN.search(migration_file.name)
            if match:
                timestamp = match.group(1)
                name = match.group(2)

                migration = EFMigration(name=name, timestamp=timestamp)
                self._extract_migration_changes(migration_file, migration)

                context.migrations.append(migration)

    def _extract_migration_changes(self, migration_file: Path, migration: EFMigration) -> None:
        """Extract schema changes from migration file.

        Args:
            migration_file: Path to migration .cs file
            migration: EFMigration to update
        """
        try:
            content = migration_file.read_text()

            # Simple heuristic: find CreateTable, AddColumn, DropTable calls
            changes = []

            for pattern in [
                r"CreateTable\([^)]+\)",
                r"AddColumn\([^)]+\)",
                r"DropTable\([^)]+\)",
                r"RenameColumn\([^)]+\)",
            ]:
                for match in re.finditer(pattern, content):
                    changes.append(match.group(0)[:50])  # Truncate for readability

            migration.up_changes = changes

        except Exception as e:
            logger.error(f"Error reading {migration_file}: {e}")


# ============================================================================
# STAGE 6: Azure DevOps Pipeline Analyzer
# ============================================================================


@dataclass
class AzureDevOpsPipeline:
    """Represents an Azure DevOps pipeline configuration."""

    name: str
    file_path: Path
    triggers: List[str] = field(default_factory=list)
    stages: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    agent_pools: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "file": str(self.file_path),
            "triggers": self.triggers,
            "stages": self.stages,
            "variables": self.variables,
            "agent_pools": self.agent_pools,
        }


class AzureDevOpsPipelineAnalyzer:
    """Analyzes Azure DevOps pipelines."""

    def __init__(self, solution_root: Path):
        """Initialize analyzer."""
        self.solution_root = Path(solution_root)
        self.pipelines: Dict[str, AzureDevOpsPipeline] = {}

    def analyze_pipelines(self) -> Dict[str, AzureDevOpsPipeline]:
        """Analyze all Azure DevOps pipelines.

        Returns:
            Dictionary of Azure DevOps pipelines
        """
        # Find azure-pipelines.yml files
        for pipeline_file in self.solution_root.rglob("azure-pipelines.yml"):
            self._analyze_pipeline(pipeline_file)

        return self.pipelines

    def _analyze_pipeline(self, pipeline_file: Path) -> None:
        """Analyze a single pipeline file.

        Args:
            pipeline_file: Path to azure-pipelines.yml
        """
        try:
            import yaml

            with open(pipeline_file, "r") as f:
                config = yaml.safe_load(f)

            if not isinstance(config, dict):
                return

            pipeline_name = pipeline_file.parent.name
            pipeline = AzureDevOpsPipeline(name=pipeline_name, file_path=pipeline_file)

            # Extract triggers
            trigger = config.get("trigger", [])
            if isinstance(trigger, list):
                pipeline.triggers.extend(trigger)

            # Extract stages
            stages = config.get("stages", [])
            for stage in stages:
                if isinstance(stage, dict):
                    stage_name = stage.get("stage", "Unknown")
                    jobs = stage.get("jobs", [])
                    pipeline.stages.append(
                        {
                            "name": stage_name,
                            "job_count": len(jobs) if isinstance(jobs, list) else 1,
                        }
                    )

            # Extract variables
            variables = config.get("variables", {})
            if isinstance(variables, dict):
                pipeline.variables = variables

            # Extract agent pool
            pool = config.get("pool")
            if pool:
                if isinstance(pool, dict):
                    pipeline.agent_pools.append(pool.get("vmImage", "Unknown"))
                elif isinstance(pool, str):
                    pipeline.agent_pools.append(pool)

            self.pipelines[pipeline_name] = pipeline

        except ImportError:
            logger.warning("PyYAML not installed, cannot parse azure-pipelines.yml")
        except Exception as e:
            logger.error(f"Error analyzing {pipeline_file}: {e}")


# ============================================================================
# STAGE 7: WCF Service Contract Analyzer
# ============================================================================


@dataclass
class WCFService:
    """Represents a WCF service contract."""

    name: str
    file_path: Path
    operations: List[Dict[str, str]] = field(default_factory=list)
    endpoint: Optional[str] = None
    binding: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "file": str(self.file_path),
            "operations": self.operations,
            "endpoint": self.endpoint,
            "binding": self.binding,
        }


class WCFServiceAnalyzer:
    """Analyzes WCF service contracts."""

    SERVICE_CONTRACT_PATTERN = re.compile(r"\[ServiceContract\]\s+public\s+interface\s+(\w+)")
    OPERATION_CONTRACT_PATTERN = re.compile(r"\[OperationContract\]\s+(\w+)\s+(\w+)\s*\(([^)]*)\)")

    def __init__(self, solution_root: Path):
        """Initialize analyzer."""
        self.solution_root = Path(solution_root)
        self.services: Dict[str, WCFService] = {}

    def analyze_services(self) -> Dict[str, WCFService]:
        """Analyze all WCF services.

        Returns:
            Dictionary of WCF services
        """
        # Find C# files with ServiceContract
        for cs_file in self.solution_root.rglob("*.cs"):
            self._analyze_cs_file(cs_file)

        # Find .svc files
        for svc_file in self.solution_root.rglob("*.svc"):
            self._analyze_svc_file(svc_file)

        return self.services

    def _analyze_cs_file(self, cs_file: Path) -> None:
        """Analyze C# file for WCF service contracts.

        Args:
            cs_file: Path to .cs file
        """
        try:
            content = cs_file.read_text()

            # Find ServiceContract interfaces
            for match in re.finditer(self.SERVICE_CONTRACT_PATTERN, content):
                service_name = match.group(1)
                service = WCFService(name=service_name, file_path=cs_file)

                # Find OperationContract methods
                for op_match in re.finditer(self.OPERATION_CONTRACT_PATTERN, content):
                    return_type = op_match.group(1)
                    op_name = op_match.group(2)
                    params = op_match.group(3)

                    service.operations.append(
                        {
                            "name": op_name,
                            "return_type": return_type,
                            "parameters": params,
                        }
                    )

                self.services[service_name] = service

        except Exception as e:
            logger.error(f"Error analyzing {cs_file}: {e}")

    def _analyze_svc_file(self, svc_file: Path) -> None:
        """Analyze .svc file.

        Args:
            svc_file: Path to .svc file
        """
        try:
            content = svc_file.read_text()

            # Extract service class
            service_pattern = r'Service="([^"]+)"'
            match = re.search(service_pattern, content)

            if match:
                service_class = match.group(1)
                svc_name = svc_file.stem

                if svc_name not in self.services:
                    service = WCFService(
                        name=svc_name, file_path=svc_file, endpoint=str(svc_file)
                    )
                    self.services[svc_name] = service

        except Exception as e:
            logger.error(f"Error analyzing {svc_file}: {e}")


# ============================================================================
# STAGE 8: Solution Architecture Visualizer
# ============================================================================


class SolutionArchitectureVisualizer:
    """Generates architecture diagrams from solution structure."""

    @staticmethod
    def generate_mermaid_diagram(dependency_graph: Dict) -> str:
        """Generate Mermaid diagram from dependency graph.

        Args:
            dependency_graph: Dictionary with project dependencies

        Returns:
            Mermaid graph syntax
        """
        mermaid = "graph LR\n"

        # Add nodes with styling
        for proj_name, deps in dependency_graph.items():
            layer = SolutionArchitectureVisualizer._detect_layer(proj_name)
            color = SolutionArchitectureVisualizer._get_color_for_layer(layer)

            mermaid += f"    {proj_name}[{proj_name}]\n"
            mermaid += f"    style {proj_name} fill:{color}\n"

            # Add edges
            for dep in deps:
                mermaid += f"    {proj_name} --> {dep}\n"

        return mermaid

    @staticmethod
    def _detect_layer(project_name: str) -> str:
        """Detect architectural layer from project name."""
        name_lower = project_name.lower()

        if any(x in name_lower for x in ["ui", "web", "presentation"]):
            return "presentation"
        elif any(x in name_lower for x in ["service", "business", "logic"]):
            return "service"
        elif any(x in name_lower for x in ["data", "database", "dal", "repository"]):
            return "data"
        else:
            return "infrastructure"

    @staticmethod
    def _get_color_for_layer(layer: str) -> str:
        """Get color for architectural layer."""
        colors = {
            "presentation": "#e1f5fe",
            "service": "#fff3e0",
            "data": "#f3e5f5",
            "infrastructure": "#e8f5e9",
        }
        return colors.get(layer, "#f5f5f5")


# ============================================================================
# STAGE 9: Repository Onboarding Integration
# ============================================================================


@dataclass
class DotNetRepositoryAnalysis:
    """Complete .NET repository analysis result."""

    solution_found: bool = False
    project_count: int = 0
    database_projects: Dict[str, DatabaseProject] = field(default_factory=dict)
    ef_contexts: Dict[str, DbContext] = field(default_factory=dict)
    wcf_services: Dict[str, WCFService] = field(default_factory=dict)
    pipelines: Dict[str, AzureDevOpsPipeline] = field(default_factory=dict)
    architecture_diagram: Optional[str] = None
    coverage_percent: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "solution_found": self.solution_found,
            "project_count": self.project_count,
            "database_projects": {
                name: proj.to_dict() for name, proj in self.database_projects.items()
            },
            "ef_contexts": {
                name: ctx.to_dict() for name, ctx in self.ef_contexts.items()
            },
            "wcf_services": {
                name: svc.to_dict() for name, svc in self.wcf_services.items()
            },
            "pipelines": {
                name: pipe.to_dict() for name, pipe in self.pipelines.items()
            },
            "architecture_diagram": self.architecture_diagram,
            "coverage_percent": self.coverage_percent,
        }


class DotNetRepositoryOnboardingIntegration:
    """Integrates .NET analyzers into repository onboarding."""

    def __init__(self, solution_root: Path):
        """Initialize integration."""
        self.solution_root = Path(solution_root)
        self.analysis = DotNetRepositoryAnalysis()

    def analyze_dotnet_repository(self) -> DotNetRepositoryAnalysis:
        """Perform comprehensive .NET repository analysis.

        Returns:
            DotNetRepositoryAnalysis with all results
        """
        # Check for .sln files
        sln_files = list(self.solution_root.rglob("*.sln"))

        if not sln_files:
            self.analysis.solution_found = False
            return self.analysis

        self.analysis.solution_found = True

        # Count projects
        csproj_files = list(self.solution_root.rglob("*.csproj"))
        self.analysis.project_count = len(csproj_files)

        # Run specialized analyzers
        db_analyzer = DatabaseProjectAnalyzer(self.solution_root)
        self.analysis.database_projects = db_analyzer.analyze_database_projects()

        ef_analyzer = EntityFrameworkMigrationAnalyzer(self.solution_root)
        self.analysis.ef_contexts = ef_analyzer.analyze_migrations()

        wcf_analyzer = WCFServiceAnalyzer(self.solution_root)
        self.analysis.wcf_services = wcf_analyzer.analyze_services()

        pipeline_analyzer = AzureDevOpsPipelineAnalyzer(self.solution_root)
        self.analysis.pipelines = pipeline_analyzer.analyze_pipelines()

        # Generate visualization
        if csproj_files:
            deps = {f.stem: [] for f in csproj_files[:10]}  # Sample
            viz = SolutionArchitectureVisualizer()
            self.analysis.architecture_diagram = viz.generate_mermaid_diagram(deps)

        # Calculate coverage
        items_found = (
            len(self.analysis.database_projects)
            + len(self.analysis.ef_contexts)
            + len(self.analysis.wcf_services)
            + len(self.analysis.pipelines)
        )
        self.analysis.coverage_percent = min(100, 40 + (items_found * 10))

        return self.analysis
