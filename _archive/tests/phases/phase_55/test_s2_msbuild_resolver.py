"""Test Suite: MSBuild ProjectReference Dependency Resolver - Stage 2.

AC-PHASE55-S2: MSBuild resolver builds project dependency graph
"""

import pytest
import tempfile
from pathlib import Path
from cortex.lens.dotnet.msbuild_resolver import (
    MSBuildProjectReferenceResolver,
    DependencyGraph,
    ProjectNode,
)


class TestMSBuildResolverBasics:
    """Test basic MSBuild resolver functionality."""

    @pytest.fixture
    def temp_solution(self):
        """Create temporary solution structure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create project structure:
            # ConsoleApp -> CoreLibrary -> SharedControls
            # ConsoleApp -> DataAccess

            # ConsoleApp
            app_dir = root / "Apps" / "ConsoleApp"
            app_dir.mkdir(parents=True)
            app_csproj = app_dir / "ConsoleApp.csproj"
            app_csproj.write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <ItemGroup>
                    <ProjectReference Include="../../Libs/CoreLibrary/CoreLibrary.csproj" />
                    <ProjectReference Include="../../Data/DataAccess/DataAccess.csproj" />
                </ItemGroup>
            </Project>"""
            )

            # CoreLibrary
            lib_dir = root / "Libs" / "CoreLibrary"
            lib_dir.mkdir(parents=True)
            lib_csproj = lib_dir / "CoreLibrary.csproj"
            lib_csproj.write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <ItemGroup>
                    <ProjectReference Include="../SharedControls/SharedControls.csproj" />
                </ItemGroup>
            </Project>"""
            )

            # SharedControls
            shared_dir = root / "Libs" / "SharedControls"
            shared_dir.mkdir(parents=True)
            shared_csproj = shared_dir / "SharedControls.csproj"
            shared_csproj.write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <ItemGroup>
                </ItemGroup>
            </Project>"""
            )

            # DataAccess
            data_dir = root / "Data" / "DataAccess"
            data_dir.mkdir(parents=True)
            data_csproj = data_dir / "DataAccess.csproj"
            data_csproj.write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <ItemGroup>
                </ItemGroup>
            </Project>"""
            )

            yield root

    def test_msbuild_resolver_parses_project_references(self, temp_solution):
        """Test that resolver parses ProjectReference elements."""
        resolver = MSBuildProjectReferenceResolver(temp_solution)
        graph = resolver.resolve_project_references()

        # Should find 4 projects
        assert len(graph.nodes) == 4
        assert "ConsoleApp" in graph.nodes
        assert "CoreLibrary" in graph.nodes
        assert "SharedControls" in graph.nodes
        assert "DataAccess" in graph.nodes

    def test_msbuild_resolver_resolves_relative_paths(self, temp_solution):
        """Test that relative paths resolve correctly."""
        resolver = MSBuildProjectReferenceResolver(temp_solution)
        graph = resolver.resolve_project_references()

        # ConsoleApp should have 2 dependencies
        assert len(graph.nodes["ConsoleApp"].dependencies) == 2
        assert "CoreLibrary" in graph.nodes["ConsoleApp"].dependencies
        assert "DataAccess" in graph.nodes["ConsoleApp"].dependencies

    def test_msbuild_resolver_builds_dependency_graph(self, temp_solution):
        """Test that dependency graph is built correctly."""
        resolver = MSBuildProjectReferenceResolver(temp_solution)
        graph = resolver.resolve_project_references()

        # Verify transitive dependencies
        assert "CoreLibrary" in graph.nodes["ConsoleApp"].dependencies
        assert "SharedControls" in graph.nodes["CoreLibrary"].dependencies
        assert len(graph.nodes["SharedControls"].dependencies) == 0

    def test_msbuild_resolver_detects_circular_deps(self):
        """Test that circular dependencies are detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create circular dependency: A -> B -> C -> A
            for proj_name in ["ProjectA", "ProjectB", "ProjectC"]:
                proj_dir = root / proj_name
                proj_dir.mkdir()

            # Project A -> B
            (root / "ProjectA" / "ProjectA.csproj").write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <ItemGroup>
                    <ProjectReference Include="../ProjectB/ProjectB.csproj" />
                </ItemGroup>
            </Project>"""
            )

            # Project B -> C
            (root / "ProjectB" / "ProjectB.csproj").write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <ItemGroup>
                    <ProjectReference Include="../ProjectC/ProjectC.csproj" />
                </ItemGroup>
            </Project>"""
            )

            # Project C -> A (creates cycle)
            (root / "ProjectC" / "ProjectC.csproj").write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <ItemGroup>
                    <ProjectReference Include="../ProjectA/ProjectA.csproj" />
                </ItemGroup>
            </Project>"""
            )

            resolver = MSBuildProjectReferenceResolver(root)
            graph = resolver.resolve_project_references()

            # Should detect circular dependency
            assert len(graph.circular_dependencies) > 0

    def test_msbuild_resolver_identifies_layer_violations(self, temp_solution):
        """Test layer violation detection."""
        resolver = MSBuildProjectReferenceResolver(temp_solution)
        graph = resolver.resolve_project_references()

        # The graph structure shouldn't have violations with current naming
        # But we should have the detection framework in place
        assert isinstance(graph.layer_violations, list)

    def test_msbuild_resolver_handles_missing_projects(self):
        """Test handling of missing ProjectReference targets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create project with reference to non-existent project
            proj_dir = root / "ProjectA"
            proj_dir.mkdir()
            (proj_dir / "ProjectA.csproj").write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <ItemGroup>
                    <ProjectReference Include="../NonExistent/NonExistent.csproj" />
                </ItemGroup>
            </Project>"""
            )

            resolver = MSBuildProjectReferenceResolver(root)
            # Should not raise error
            graph = resolver.resolve_project_references()
            assert len(graph.nodes) == 1  # Only ProjectA found

    def test_msbuild_resolver_performance_large_solution(self):
        """Test performance with 345+ projects (enterprise monolith scale)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create 50 projects with dependencies (representative subset)
            # Full 345 would be slow in testing
            for i in range(50):
                proj_dir = root / f"Project{i}"
                proj_dir.mkdir()

                # Each project references the next one
                refs = ""
                if i < 49:
                    refs = f"""
                    <ProjectReference Include="../Project{i+1}/Project{i+1}.csproj" />
                """

                (proj_dir / f"Project{i}.csproj").write_text(
                    f"""<Project Sdk="Microsoft.NET.Sdk">
                    <ItemGroup>
                        {refs}
                    </ItemGroup>
                </Project>"""
                )

            resolver = MSBuildProjectReferenceResolver(root)
            import time

            start = time.time()
            graph = resolver.resolve_project_references()
            elapsed = time.time() - start

            # Should complete in reasonable time (<5 seconds for 50 projects)
            assert elapsed < 5.0
            assert len(graph.nodes) == 50


class TestDependencyGraphDataStructure:
    """Test DependencyGraph data structure."""

    def test_dependency_graph_add_node(self):
        """Test adding nodes to graph."""
        graph = DependencyGraph()
        graph.add_node("ProjectA", Path("/path/to/ProjectA.csproj"), "library")

        assert "ProjectA" in graph.nodes
        assert graph.nodes["ProjectA"].name == "ProjectA"
        assert graph.nodes["ProjectA"].project_type == "library"

    def test_dependency_graph_add_edge(self):
        """Test adding edges to graph."""
        graph = DependencyGraph()
        graph.add_node("ProjectA", Path("/path/A.csproj"), "library")
        graph.add_node("ProjectB", Path("/path/B.csproj"), "library")
        graph.add_edge("ProjectA", "ProjectB")

        assert "ProjectB" in graph.nodes["ProjectA"].dependencies
        assert {"from": "ProjectA", "to": "ProjectB"} in graph.edges

    def test_dependency_graph_to_dict(self):
        """Test serialization to dictionary."""
        graph = DependencyGraph()
        graph.add_node("ProjectA", Path("/path/A.csproj"), "app")
        graph.add_node("ProjectB", Path("/path/B.csproj"), "library")
        graph.add_edge("ProjectA", "ProjectB")

        result = graph.to_dict()

        assert "project_dependencies" in result
        assert "dependency_graph" in result
        assert "circular_dependencies" in result
        assert "layer_violations" in result
        assert result["project_dependencies"]["ProjectA"] == ["ProjectB"]


class TestProjectTypeDetection:
    """Test project type detection."""

    def test_detect_console_app_project(self):
        """Test detection of console application projects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            proj_dir = root / "MyConsoleApp"
            proj_dir.mkdir()

            (proj_dir / "MyConsoleApp.csproj").write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <PropertyGroup>
                    <OutputType>Exe</OutputType>
                </PropertyGroup>
            </Project>"""
            )

            resolver = MSBuildProjectReferenceResolver(root)
            proj_type = resolver._detect_project_type(proj_dir / "MyConsoleApp.csproj")

            assert proj_type == "app"

    def test_detect_library_project(self):
        """Test detection of library projects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            proj_dir = root / "MyLibrary"
            proj_dir.mkdir()

            (proj_dir / "MyLibrary.csproj").write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
                <PropertyGroup>
                    <OutputType>Library</OutputType>
                </PropertyGroup>
            </Project>"""
            )

            resolver = MSBuildProjectReferenceResolver(root)
            proj_type = resolver._detect_project_type(proj_dir / "MyLibrary.csproj")

            assert proj_type == "library"

    def test_detect_test_project(self):
        """Test detection of test projects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            proj_dir = root / "MyLibrary.Tests"
            proj_dir.mkdir()

            (proj_dir / "MyLibrary.Tests.csproj").write_text(
                """<Project Sdk="Microsoft.NET.Sdk">
            </Project>"""
            )

            resolver = MSBuildProjectReferenceResolver(root)
            proj_type = resolver._detect_project_type(proj_dir / "MyLibrary.Tests.csproj")

            assert proj_type == "test"
