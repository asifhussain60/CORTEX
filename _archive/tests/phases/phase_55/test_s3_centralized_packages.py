"""Test Suite: Centralized Package Management - Stage 3.

AC-PHASE55-S3: DependencyAnalyzer supports Directory.Packages.props
"""

import pytest
import tempfile
from pathlib import Path
from cortex.lens.dotnet.centralized_packages import (
    CentralizedPackageManager,
    CentralizedPackageContext,
)


class TestCentralizedPackageDiscovery:
    """Test discovery of centralized package configurations."""

    @pytest.fixture
    def solution_with_packages(self):
        """Create solution with Directory.Packages.props."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create Directory.Packages.props at solution root
            packages_props = root / "Directory.Packages.props"
            packages_props.write_text(
                """<?xml version="1.0" encoding="utf-8"?>
                <Project>
                    <ItemGroup>
                        <PackageVersion Include="Newtonsoft.Json" Version="13.0.1" />
                        <PackageVersion Include="Microsoft.EntityFrameworkCore" Version="6.0.8" />
                        <PackageVersion Include="Microsoft.Extensions.Logging" Version="6.0.0" />
                    </ItemGroup>
                </Project>"""
            )

            yield root

    def test_centralized_packages_detects_directory_packages_props(self, solution_with_packages):
        """Test detection of Directory.Packages.props file."""
        manager = CentralizedPackageManager(solution_with_packages)
        context = manager.analyze_centralized_packages()

        # Should find 3 packages
        assert len(context.packages) == 3
        assert "Newtonsoft.Json" in context.packages
        assert "Microsoft.EntityFrameworkCore" in context.packages
        assert "Microsoft.Extensions.Logging" in context.packages

    def test_centralized_packages_parses_versions(self, solution_with_packages):
        """Test parsing of package versions."""
        manager = CentralizedPackageManager(solution_with_packages)
        context = manager.analyze_centralized_packages()

        assert context.packages["Newtonsoft.Json"].version == "13.0.1"
        assert context.packages["Microsoft.EntityFrameworkCore"].version == "6.0.8"
        assert context.packages["Microsoft.Extensions.Logging"].version == "6.0.0"

    def test_centralized_packages_merges_hierarchy(self):
        """Test merging packages from hierarchy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create parent Directory.Packages.props
            parent_props = root / "Directory.Packages.props"
            parent_props.write_text(
                """<?xml version="1.0" encoding="utf-8"?>
                <Project>
                    <ItemGroup>
                        <PackageVersion Include="Newtonsoft.Json" Version="13.0.1" />
                        <PackageVersion Include="Microsoft.EntityFrameworkCore" Version="6.0.8" />
                    </ItemGroup>
                </Project>"""
            )

            manager = CentralizedPackageManager(root)
            context = manager.analyze_centralized_packages()

            assert len(context.packages) == 2
            assert context.packages["Newtonsoft.Json"].version == "13.0.1"

    def test_centralized_packages_local_overrides_parent(self):
        """Test that local project versions override parent packages."""
        from cortex.lens.dotnet.centralized_packages import PackageVersion

        manager = CentralizedPackageManager(Path("/tmp"))

        # Simulate centralized packages
        manager.context.packages = {
            "Newtonsoft.Json": PackageVersion(
                name="Newtonsoft.Json",
                version="13.0.1",
                source="Directory.Packages.props",
            )
        }

        # Project-specific packages (override)
        project_packages = {"Newtonsoft.Json": "12.0.3"}

        merged = manager.merge_with_project_packages(project_packages)

        # Local override should win
        assert merged["Newtonsoft.Json"] == "12.0.3"

    def test_centralized_packages_parses_nuget_config(self):
        """Test parsing of NuGet.Config for package sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create NuGet.Config
            nuget_config = root / "NuGet.Config"
            nuget_config.write_text(
                """<?xml version="1.0" encoding="utf-8"?>
                <configuration>
                    <packageSources>
                        <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
                        <add key="DevOne" value="https://pkgs.dev.azure.com/company/..." />
                    </packageSources>
                </configuration>"""
            )

            manager = CentralizedPackageManager(root)
            context = manager.analyze_centralized_packages()

            assert len(context.package_sources) == 2
            sources = {s["name"]: s["url"] for s in context.package_sources}
            assert "nuget.org" in sources
            assert "DevOne" in sources

    def test_centralized_packages_expands_msbuild_properties(self):
        """Test expansion of MSBuild properties like $(TargetFramework)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create Directory.Build.props with property definitions
            props_file = root / "Directory.Build.props"
            props_file.write_text(
                """<?xml version="1.0" encoding="utf-8"?>
                <Project>
                    <PropertyGroup>
                        <TargetFramework>net6.0</TargetFramework>
                        <LangVersion>10.0</LangVersion>
                    </PropertyGroup>
                </Project>"""
            )

            manager = CentralizedPackageManager(root)
            context = manager.analyze_centralized_packages()

            assert context.directory_build_props["TargetFramework"] == "net6.0"
            assert context.directory_build_props["LangVersion"] == "10.0"
            assert context.properties["TargetFramework"] == "net6.0"

    def test_centralized_packages_handles_missing_props(self):
        """Test graceful handling when props files are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            manager = CentralizedPackageManager(root)
            context = manager.analyze_centralized_packages()

            # Should not crash, just return empty context
            assert len(context.packages) == 0
            assert len(context.directory_build_props) == 0
            assert len(context.package_sources) == 0


class TestPackageVersionResolution:
    """Test package version resolution and merging."""

    def test_get_package_version(self):
        """Test retrieving a single package version."""
        from cortex.lens.dotnet.centralized_packages import PackageVersion

        manager = CentralizedPackageManager(Path("/tmp"))

        # Add package to context
        manager.context.packages["Newtonsoft.Json"] = PackageVersion(
            name="Newtonsoft.Json",
            version="13.0.1",
            source="Directory.Packages.props",
        )

        version = manager.get_package_version("Newtonsoft.Json")
        assert version == "13.0.1"

    def test_get_nonexistent_package_version(self):
        """Test retrieving version of non-existent package."""
        manager = CentralizedPackageManager(Path("/tmp"))

        version = manager.get_package_version("NonExistent.Package")
        assert version is None

    def test_merge_adds_missing_packages(self):
        """Test that merge includes all project packages."""
        from cortex.lens.dotnet.centralized_packages import PackageVersion

        manager = CentralizedPackageManager(Path("/tmp"))

        # Set up centralized package
        manager.context.packages["Newtonsoft.Json"] = PackageVersion(
            name="Newtonsoft.Json",
            version="13.0.1",
            source="Directory.Packages.props",
        )

        # Project has additional packages
        project_packages = {
            "Newtonsoft.Json": "13.0.1",
            "Microsoft.AspNetCore.App": "6.0.0",
            "xunit": "2.4.1",
        }

        merged = manager.merge_with_project_packages(project_packages)

        # Should have all three packages
        assert len(merged) == 3
        assert merged["Newtonsoft.Json"] == "13.0.1"
        assert merged["Microsoft.AspNetCore.App"] == "6.0.0"
        assert merged["xunit"] == "2.4.1"


class TestCentralizedPackageContextSerialization:
    """Test serialization of package context."""

    def test_context_to_dict(self):
        """Test conversion to dictionary format."""
        from cortex.lens.dotnet.centralized_packages import PackageVersion

        context = CentralizedPackageContext()
        context.packages["Newtonsoft.Json"] = PackageVersion(
            name="Newtonsoft.Json",
            version="13.0.1",
            source="Directory.Packages.props",
        )
        context.package_sources = [{"name": "nuget.org", "url": "https://api.nuget.org/v3"}]

        result = context.to_dict()

        assert "centralized_packages" in result
        assert "Newtonsoft.Json" in result["centralized_packages"]
        assert result["centralized_packages"]["Newtonsoft.Json"]["version"] == "13.0.1"
        assert len(result["package_sources"]) == 1
