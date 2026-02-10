"""
Phase 67 S1: Roslyn Workspace Builder Tests

Unit tests for Roslyn semantic analysis workspace loading.

AC_START: AC-PHASE67-S1-TEST-001
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from cortex_lens.dotnet.roslyn_workspace_builder import RoslynWorkspaceBuilder


@pytest.fixture
def temp_dotnet_solution():
    """Create temporary .NET solution for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create solution structure
    solution_dir = temp_dir / "TestSolution"
    solution_dir.mkdir()
    
    # Create .sln file
    sln_content = """
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Core", "Core\\Core.csproj", "{12345678-1234-1234-1234-123456789012}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Any CPU = Debug|Any CPU
		Release|Any CPU = Release|Any CPU
	EndGlobalSection
EndGlobal
"""
    (solution_dir / "TestSolution.sln").write_text(sln_content.strip())
    
    # Create Core project
    core_dir = solution_dir / "Core"
    core_dir.mkdir()
    
    csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
"""
    (core_dir / "Core.csproj").write_text(csproj_content)
    
    # Create simple C# file
    cs_content = """namespace Core.Entities
{
    public interface IEntity
    {
        int Id { get; set; }
    }
    
    public class User : IEntity
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        
        public string GetDisplayName()
        {
            return $"User: {Name}";
        }
    }
}
"""
    entities_dir = core_dir / "Entities"
    entities_dir.mkdir()
    (entities_dir / "IEntity.cs").write_text(cs_content)
    
    yield solution_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestRoslynWorkspaceBuilder:
    """Test suite for RoslynWorkspaceBuilder."""
    
    def test_init(self):
        """Test workspace builder initialization."""
        builder = RoslynWorkspaceBuilder()
        
        assert builder is not None
        assert hasattr(builder, 'load_solution')
        assert hasattr(builder, 'load_project')
    
    def test_detect_solution_file(self, temp_dotnet_solution):
        """Test solution file detection."""
        builder = RoslynWorkspaceBuilder()
        
        solution_path = temp_dotnet_solution / "TestSolution.sln"
        assert solution_path.exists()
        
        # Should be able to detect it's a valid solution
        assert builder.is_valid_solution(solution_path)
    
    def test_detect_project_file(self, temp_dotnet_solution):
        """Test project file detection."""
        builder = RoslynWorkspaceBuilder()
        
        project_path = temp_dotnet_solution / "Core" / "Core.csproj"
        assert project_path.exists()
        
        # Should be able to detect it's a valid project
        assert builder.is_valid_project(project_path)
    
    def test_load_solution_basic(self, temp_dotnet_solution):
        """
        Test loading a basic .NET solution.
        
        AC: Load solution with 1 project successfully
        """
        builder = RoslynWorkspaceBuilder()
        
        solution_path = temp_dotnet_solution / "TestSolution.sln"
        result = builder.load_solution(solution_path)
        
        assert result is not None
        assert result["solution_path"] == str(solution_path)
        assert result["solution_name"] == "TestSolution"
        assert len(result["projects"]) == 1
        assert result["projects"][0]["name"] == "Core"
        assert "path" in result["projects"][0]
    
    def test_load_solution_with_semantic_model(self, temp_dotnet_solution):
        """
        Test loading solution with semantic model extraction.
        
        AC: Extract type symbols from loaded projects
        """
        builder = RoslynWorkspaceBuilder()
        
        solution_path = temp_dotnet_solution / "TestSolution.sln"
        result = builder.load_solution(solution_path, include_semantic=True)
        
        assert result["success"]
        assert result["type"] == "solution"
        assert "projects" in result
        assert len(result["projects"]) == 1
        
        # Verify semantic model data is present
        project = result["projects"][0]
        assert "semantic_model" in project
        
        semantic_model = project["semantic_model"]
        assert "Types" in semantic_model
        
        # Verify IEntity interface found
        types = semantic_model["Types"]
        type_names = [t["Name"] for t in types]
        assert "IEntity" in type_names
        assert "User" in type_names
        
        # Verify User class has expected structure
        user_type = next(t for t in types if t["Name"] == "User")
        print(f"\n=== User Type Found ===")
        print(f"Namespace: {user_type.get('Namespace')}")
        print(f"FullName: {user_type.get('FullName')}")
        print(f"Methods: {user_type.get('Methods')}")
        print(f"Properties: {user_type.get('Properties')}")
        print(f"Interfaces: {user_type.get('Interfaces')}")
        print(f"=======================\n")
        
        assert user_type["Kind"] == "Class"
        # Check for interface implementation (may be Core.Entities.IEntity or TestSolution.Core.Entities.IEntity)
        assert any("IEntity" in iface for iface in user_type["Interfaces"])
        assert len(user_type["Methods"]) >= 1, f"Expected >=1 methods, got {len(user_type['Methods'])}"  # GetDisplayName method
        assert len(user_type["Properties"]) >= 2  # Id, Name properties
        assert "User" in type_names
    
    def test_load_project_directly(self, temp_dotnet_solution):
        """
        Test loading a single project without solution.
        
        AC: Load .csproj directly
        """
        builder = RoslynWorkspaceBuilder()
        
        project_path = temp_dotnet_solution / "Core" / "Core.csproj"
        result = builder.load_project(project_path)
        
        assert result is not None
        assert result["project_path"] == str(project_path)
        assert result["name"] == "Core"
        assert result["target_framework"] == "net8.0"
        assert result["sdk"] == "Microsoft.NET.Sdk"
        assert result["nullable"] == "enable"
    
    def test_invalid_solution_path(self):
        """Test error handling for invalid solution path."""
        builder = RoslynWorkspaceBuilder()
        
        with pytest.raises(FileNotFoundError):
            builder.load_solution(Path("/nonexistent/solution.sln"))
    
    def test_invalid_project_path(self):
        """Test error handling for invalid project path."""
        builder = RoslynWorkspaceBuilder()
        
        with pytest.raises(FileNotFoundError):
            builder.load_project(Path("/nonexistent/project.csproj"))


# AC_COMPLETE: AC-PHASE67-S1-TEST-001 ✅ 8 tests defined (3 passing, 5 pending implementation)
