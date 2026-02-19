# AC_START: AC-PHASE55-S1-dotnet_tests
# Description: Phase 55 S1 Tests - .NET Enterprise LENS Enhancement
# Author: Asif Hussain
# Date: 2026-02-08
# Phase: 55, Stage 1

"""Tests for .NET Enterprise LENS (Phase 55 S1, 13 tests total)."""

import pytest
from cortex.lens.dotnet_analyzer import (
    SolutionFileParser,
    ProjectFileParser,
    MonolithAnalyzer,
    DotNetLensAnalyzer,
    ProjectType,
    DotNetVersion,
    DotNetProject,
    NuGetPackage,
)


# ============================================================================
# S1 Tests: SolutionFileParser (4 tests)
# ============================================================================


def test_solution_parser_initialization():
    """S1 Test 1: SolutionFileParser initializes."""
    parser = SolutionFileParser()
    assert parser is not None


def test_solution_parser_parse_simple_sln():
    """S1 Test 2: Parse simple .sln file."""
    sln_content = """Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31919.166
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "MyProject", "MyProject.csproj", "{ABC123}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Any CPU = Debug|Any CPU
	EndGlobalSection
EndGlobal"""

    solution = SolutionFileParser.parse_solution_file(sln_content, "/path/to")
    assert solution is not None
    assert len(solution.projects) > 0


def test_solution_parser_detect_project_type():
    """S1 Test 3: Detect C# project type from GUID."""
    # C# GUID
    proj_type = SolutionFileParser._detect_project_type("FAE04EC0-301F-11D3-BF4B-00C04F79EFBC")
    assert proj_type == ProjectType.CONSOLE


def test_solution_parser_unknown_project_type():
    """S1 Test 4: Handle unknown project type."""
    proj_type = SolutionFileParser._detect_project_type("UNKNOWN-GUID")
    assert proj_type == ProjectType.UNKNOWN


# ============================================================================
# S1 Tests: ProjectFileParser (4 tests)
# ============================================================================


def test_project_parser_initialization():
    """S1 Test 5: ProjectFileParser initializes."""
    parser = ProjectFileParser()
    assert parser is not None


def test_project_parser_parse_csproj():
    """S1 Test 6: Parse .csproj file."""
    csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <AssemblyName>MyApp</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageReference Include="Microsoft.AspNetCore.App" Version="8.0.0" />
  </ItemGroup>
</Project>"""

    project = ProjectFileParser.parse_csproj(csproj_content)
    assert project is not None
    assert project.assembly_name == "MyApp"
    assert project.target_framework == DotNetVersion.NET_8
    assert len(project.packages) == 2


def test_project_parser_parse_framework_versions():
    """S1 Test 7: Parse various framework versions."""
    assert ProjectFileParser._parse_framework("net8.0") == DotNetVersion.NET_8
    assert ProjectFileParser._parse_framework("net7.0") == DotNetVersion.NET_7
    assert ProjectFileParser._parse_framework("net6.0") == DotNetVersion.NET_6
    assert ProjectFileParser._parse_framework("net5.0") == DotNetVersion.NET_5
    assert ProjectFileParser._parse_framework("netcoreapp3.1") == DotNetVersion.CORE_3_1
    assert ProjectFileParser._parse_framework("net48") == DotNetVersion.FRAMEWORK_4_8
    assert ProjectFileParser._parse_framework("unknown") == DotNetVersion.UNKNOWN


def test_project_parser_handle_minimal_csproj():
    """S1 Test 8: Handle minimal .csproj without packages."""
    csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
</Project>"""

    project = ProjectFileParser.parse_csproj(csproj_content)
    assert project is not None
    assert project.target_framework == DotNetVersion.NET_6


# ============================================================================
# S1 Tests: MonolithAnalyzer (2 tests)
# ============================================================================


def test_monolith_analyzer_initialization():
    """S1 Test 9: MonolithAnalyzer initializes."""
    analyzer = MonolithAnalyzer()
    assert analyzer is not None


def test_monolith_analyzer_empty_solution():
    """S1 Test 10: Analyze empty solution."""
    from cortex.lens.dotnet_analyzer import DotNetSolution

    solution = DotNetSolution(name="EmptySolution", path="/path")
    analysis = MonolithAnalyzer.analyze_solution(solution)

    assert analysis["total_projects"] == 0
    assert analysis["total_dependencies"] == 0


# ============================================================================
# S1 Tests: DotNetLensAnalyzer (3 tests)
# ============================================================================


def test_dotnet_lens_analyzer_initialization():
    """S1 Test 11: DotNetLensAnalyzer initializes."""
    analyzer = DotNetLensAnalyzer()
    assert analyzer is not None
    assert analyzer.solution_parser is not None
    assert analyzer.project_parser is not None


def test_dotnet_lens_analyze_solution():
    """S1 Test 12: Analyze solution with LENS."""
    analyzer = DotNetLensAnalyzer()

    sln_content = """Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "MyApp", "MyApp.csproj", "{ABC}"
EndProject"""

    result = analyzer.analyze_solution_file("/path/solution.sln", sln_content)
    assert result is not None
    assert "project_count" in result


def test_dotnet_lens_analyze_project():
    """S1 Test 13: Analyze project with LENS."""
    analyzer = DotNetLensAnalyzer()

    csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <AssemblyName>MyLibrary</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="NUnit" Version="3.13.3" />
  </ItemGroup>
</Project>"""

    result = analyzer.analyze_project_file("/path/MyLibrary.csproj", csproj_content)
    assert result is not None
    assert result["project_name"] == "MyLibrary"
    assert result["target_framework"] == "net8.0"
    assert result["package_count"] == 1


# AC_COMPLETE: AC-PHASE55-S1-dotnet_tests ✅
# Total tests: 13 passing
