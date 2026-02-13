"""
Pytest configuration for CORTEX LENS integration tests.

Provides fixtures for .NET analysis testing and semantic integration.
"""
import pytest
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_dotnet_solution(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Create a temporary .NET solution for testing.
    
    Creates a minimal valid .NET solution with projects for testing
    semantic and syntax analysis capabilities.
    
    Args:
        tmp_path: Pytest's temporary directory fixture.
        
    Yields:
        Path: Temporary solution directory.
    """
    # Create solution directory
    sol_dir = tmp_path / "TestSolution"
    sol_dir.mkdir()
    
    # Create test project directory
    proj_dir = sol_dir / "TestProject"
    proj_dir.mkdir()
    
    # Create minimal .sln file
    sln_file = sol_dir / "TestSolution.sln"
    sln_content = '''Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 16
VisualStudioVersion = 16.0.30114.105
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "TestProject", "TestProject\\TestProject.csproj", "{12345678-1234-1234-1234-123456789012}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Any CPU = Debug|Any CPU
		Release|Any CPU = Release|Any CPU
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{12345678-1234-1234-1234-123456789012}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{12345678-1234-1234-1234-123456789012}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{12345678-1234-1234-1234-123456789012}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{12345678-1234-1234-1234-123456789012}.Release|Any CPU.Build.0 = Release|Any CPU
	EndGlobalSection
EndGlobal
'''
    sln_file.write_text(sln_content)
    
    # Create minimal .csproj file
    csproj_file = proj_dir / "TestProject.csproj"
    csproj_content = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <LangVersion>latest</LangVersion>
  </PropertyGroup>
</Project>
'''
    csproj_file.write_text(csproj_content)
    
    # Create minimal Program.cs
    program_file = proj_dir / "Program.cs"
    program_content = '''namespace TestProject
{
    class Program
    {
        static void Main(string[] args)
        {
            System.Console.WriteLine("Hello, World!");
        }
    }
}
'''
    program_file.write_text(program_content)
    
    yield sol_dir
    
    # Cleanup is automatic with tmp_path
