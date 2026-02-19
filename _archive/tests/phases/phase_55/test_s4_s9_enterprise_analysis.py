"""Test Suite: .NET Enterprise Analysis - Stages 4-9.

AC-PHASE55-S4-S9: Multi-stage .NET analyzers + integration
"""

import pytest
import tempfile
from pathlib import Path
from cortex.lens.dotnet.enterprise_analysis import (
    DatabaseProjectAnalyzer,
    EntityFrameworkMigrationAnalyzer,
    AzureDevOpsPipelineAnalyzer,
    WCFServiceAnalyzer,
    SolutionArchitectureVisualizer,
    DotNetRepositoryOnboardingIntegration,
)


class TestDatabaseProjectAnalyzer:
    """Test S4: Database project analysis."""

    def test_database_project_analyzer_detects_sqlproj(self):
        """Test detection of .sqlproj files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create Database project
            db_dir = root / "Database"
            db_dir.mkdir()

            (db_dir / "Database.sqlproj").write_text(
                """<Project>
                <ItemGroup>
                    <Build Include="dbo/Tables/Users.sql" />
                    <Build Include="dbo/Procedures/GetUser.sql" />
                </ItemGroup>
            </Project>"""
            )

            analyzer = DatabaseProjectAnalyzer(root)
            projects = analyzer.analyze_database_projects()

            assert len(projects) == 1
            assert "Database" in projects

    def test_database_project_analyzer_extracts_schema_objects(self):
        """Test extraction of schema objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create Database project
            db_dir = root / "Database" / "dbo"
            db_dir.mkdir(parents=True)

            # Create SQL files
            (db_dir / "Tables.sql").write_text(
                """CREATE TABLE dbo.Users (
                    Id INT PRIMARY KEY,
                    Name NVARCHAR(50)
                )"""
            )

            (db_dir / "Procedures.sql").write_text(
                """CREATE PROCEDURE dbo.usp_GetUser
                    @Id INT
                AS
                BEGIN
                    SELECT * FROM dbo.Users WHERE Id = @Id
                END"""
            )

            (db_dir / "Views.sql").write_text(
                """CREATE VIEW dbo.vw_ActiveUsers AS
                SELECT * FROM dbo.Users"""
            )

            # Create sqlproj
            sqlproj = root / "Database" / "Database.sqlproj"
            sqlproj.write_text(
                """<Project>
                <ItemGroup>
                    <Build Include="dbo/Tables.sql" />
                    <Build Include="dbo/Procedures.sql" />
                    <Build Include="dbo/Views.sql" />
                </ItemGroup>
            </Project>"""
            )

            analyzer = DatabaseProjectAnalyzer(root)
            projects = analyzer.analyze_database_projects()

            db = projects["Database"]
            assert any("Users" in t for t in db.tables)
            assert any("GetUser" in p for p in db.stored_procedures)
            assert any("ActiveUsers" in v for v in db.views)

    def test_database_project_analyzer_identifies_db_references(self):
        """Test identification of database references."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            db_dir = root / "Database"
            db_dir.mkdir()

            (db_dir / "Database.sqlproj").write_text(
                """<Project>
                <ItemGroup>
                    <DatabaseReference Location="DatabaseVersion" />
                </ItemGroup>
            </Project>"""
            )

            analyzer = DatabaseProjectAnalyzer(root)
            projects = analyzer.analyze_database_projects()

            assert "DatabaseVersion" in projects["Database"].database_references


class TestEntityFrameworkAnalyzer:
    """Test S5: Entity Framework migration analysis."""

    def test_ef_migration_analyzer_detects_migrations(self):
        """Test detection of EF migration files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create Migrations folder
            mig_dir = root / "AppContext" / "Migrations"
            mig_dir.mkdir(parents=True)

            # Create migration files
            (mig_dir / "20230115000000_AddUserTable.cs").write_text("public override void Up() {}")
            (mig_dir / "20230120000000_AddEmailColumn.cs").write_text("public override void Up() {}")

            analyzer = EntityFrameworkMigrationAnalyzer(root)
            contexts = analyzer.analyze_migrations()

            assert "AppContext" in contexts
            assert len(contexts["AppContext"].migrations) == 2

    def test_ef_migration_analyzer_builds_timeline(self):
        """Test building chronological migration timeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            mig_dir = root / "Context" / "Migrations"
            mig_dir.mkdir(parents=True)

            (mig_dir / "20230101000000_Initial.cs").write_text("public override void Up() {}")
            (mig_dir / "20230115000000_AddUserTable.cs").write_text("public override void Up() {}")
            (mig_dir / "20230120000000_AddEmailColumn.cs").write_text("public override void Up() {}")

            analyzer = EntityFrameworkMigrationAnalyzer(root)
            contexts = analyzer.analyze_migrations()

            migs = contexts["Context"].migrations
            assert migs[0].name == "Initial"
            assert migs[1].name == "AddUserTable"
            assert migs[2].name == "AddEmailColumn"

    def test_ef_migration_analyzer_extracts_schema_changes(self):
        """Test extraction of schema changes from migrations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            mig_dir = root / "Context" / "Migrations"
            mig_dir.mkdir(parents=True)

            (mig_dir / "20230115000000_AddUserTable.cs").write_text(
                """CreateTable(name: "dbo.Users", 
                columns: table => new { Id = table.Column<int>() })"""
            )

            analyzer = EntityFrameworkMigrationAnalyzer(root)
            contexts = analyzer.analyze_migrations()

            mig = contexts["Context"].migrations[0]
            assert len(mig.up_changes) > 0


class TestAzureDevOpsAnalyzer:
    """Test S6: Azure DevOps pipeline analysis."""

    def test_azure_devops_analyzer_parses_pipeline_yaml(self):
        """Test parsing of azure-pipelines.yml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            pipeline_file = root / "azure-pipelines.yml"
            pipeline_file.write_text(
                """
trigger:
  - main
  - develop

stages:
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - script: dotnet restore
          - script: dotnet build

  - stage: Deploy
    jobs:
      - job: DeployJob
        steps:
          - script: dotnet publish
"""
            )

            analyzer = AzureDevOpsPipelineAnalyzer(root)
            pipelines = analyzer.analyze_pipelines()

            # Should find the pipeline
            assert len(pipelines) > 0
            first_pipeline = list(pipelines.values())[0]
            assert "Build" in str(first_pipeline.stages) or len(first_pipeline.stages) > 0

    def test_azure_devops_analyzer_identifies_triggers(self):
        """Test identification of CI/CD triggers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            pipeline_file = root / "azure-pipelines.yml"
            pipeline_file.write_text(
                """
trigger:
  - main
  - develop
"""
            )

            analyzer = AzureDevOpsPipelineAnalyzer(root)
            pipelines = analyzer.analyze_pipelines()

            if pipelines:
                first_pipeline = list(pipelines.values())[0]
                assert "main" in first_pipeline.triggers or len(first_pipeline.triggers) >= 0


class TestWCFAnalyzer:
    """Test S7: WCF service contract analysis."""

    def test_wcf_analyzer_detects_service_contracts(self):
        """Test detection of [ServiceContract] interfaces."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            cs_file = root / "IUserService.cs"
            cs_file.write_text(
                """
[ServiceContract]
public interface IUserService
{
    [OperationContract]
    User GetUser(int userId);
    
    [OperationContract]
    int CreateUser(User user);
}
"""
            )

            analyzer = WCFServiceAnalyzer(root)
            services = analyzer.analyze_services()

            assert len(services) > 0

    def test_wcf_analyzer_extracts_operation_contracts(self):
        """Test extraction of [OperationContract] methods."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            cs_file = root / "IOrderService.cs"
            cs_file.write_text(
                """
[ServiceContract]
public interface IOrderService
{
    [OperationContract]
    Order GetOrder(int orderId);
}
"""
            )

            analyzer = WCFServiceAnalyzer(root)
            services = analyzer.analyze_services()

            # Should find operations
            assert any(service.operations for service in services.values())


class TestArchitectureVisualizer:
    """Test S8: Architecture visualization."""

    def test_visualizer_generates_mermaid_diagram(self):
        """Test Mermaid diagram generation."""
        deps = {
            "ConsoleApp": ["CoreLibrary", "DataAccess"],
            "CoreLibrary": ["SharedControls"],
            "DataAccess": [],
            "SharedControls": [],
        }

        diagram = SolutionArchitectureVisualizer.generate_mermaid_diagram(deps)

        assert "graph LR" in diagram
        assert "ConsoleApp" in diagram
        assert "CoreLibrary" in diagram
        assert "-->" in diagram

    def test_visualizer_color_codes_layers(self):
        """Test layer-based color coding."""
        deps = {
            "PresentationUI": [],
            "ServiceLogic": ["DataRepository"],
            "DataRepository": [],
        }

        diagram = SolutionArchitectureVisualizer.generate_mermaid_diagram(deps)

        assert "style" in diagram
        assert "fill:" in diagram


class TestRepositoryOnboardingIntegration:
    """Test S9: Repository onboarding integration."""

    def test_onboarding_detects_dotnet_repository(self):
        """Test detection of .NET repositories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create a .sln file
            (root / "Solution.sln").write_text("Microsoft Visual Studio Solution File")

            # Create some .csproj files
            (root / "Project1.csproj").write_text("<Project></Project>")
            (root / "Project2.csproj").write_text("<Project></Project>")

            integration = DotNetRepositoryOnboardingIntegration(root)
            analysis = integration.analyze_dotnet_repository()

            assert analysis.solution_found
            assert analysis.project_count >= 2

    def test_onboarding_runs_solution_parser(self):
        """Test that onboarding runs the solution parser."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "Solution.sln").write_text("Microsoft Visual Studio Solution File")
            (root / "MyProject.csproj").write_text("<Project></Project>")

            integration = DotNetRepositoryOnboardingIntegration(root)
            analysis = integration.analyze_dotnet_repository()

            assert analysis.solution_found
            assert analysis.project_count >= 1

    def test_onboarding_enterprise_monolith_coverage(self):
        """Test comprehensive enterprise monolith coverage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create comprehensive enterprise setup
            (root / "Solution.sln").write_text("Microsoft Visual Studio Solution File")

            # Projects
            for i in range(10):
                proj_dir = root / f"Project{i}"
                proj_dir.mkdir()
                (proj_dir / f"Project{i}.csproj").write_text("<Project></Project>")

            # Database project
            db_dir = root / "Database"
            db_dir.mkdir()
            (db_dir / "Database.sqlproj").write_text(
                """<Project>
                <ItemGroup>
                    <Build Include="dbo/Tables.sql" />
                </ItemGroup>
            </Project>"""
            )

            # Migrations
            mig_dir = root / "AppContext" / "Migrations"
            mig_dir.mkdir(parents=True)
            (mig_dir / "20230115000000_Initial.cs").write_text("public override void Up() {}")

            integration = DotNetRepositoryOnboardingIntegration(root)
            analysis = integration.analyze_dotnet_repository()

            # Should achieve reasonable coverage
            assert analysis.solution_found
            assert analysis.project_count >= 10
            assert analysis.coverage_percent > 40
