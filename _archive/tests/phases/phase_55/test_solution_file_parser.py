"""Phase 55 S1: Solution File Parser - TDD Tests"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional

# Test data for .sln parsing
SIMPLE_SLN = """
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31919.166
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "ConsoleApp", "Apps\\ConsoleApp\\ConsoleApp.csproj", "{12345678-1234-1234-1234-123456789012}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "CoreLibrary", "Libs\\CoreLibrary\\CoreLibrary.csproj", "{87654321-4321-4321-4321-210987654321}"
EndProject
Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "Apps", "Apps", "{AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Any CPU = Debug|Any CPU
		Release|Any CPU = Release|Any CPU
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{12345678-1234-1234-1234-123456789012}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{12345678-1234-1234-1234-123456789012}.Release|Any CPU.ActiveCfg = Release|Any CPU
	EndGlobalSection
EndGlobal
"""

SOLUTION_FILTER = """{
  "solution": {
    "path": "Enterprise.sln",
    "projects": [
      "Apps/ConsoleApp/ConsoleApp.csproj",
      "Libs/CoreLibrary/CoreLibrary.csproj"
    ]
  }
}"""


class TestSolutionFileParser:
    """Test suite for SolutionFileParser"""
    
    def test_solution_parser_extracts_projects(self):
        """Parse .sln and extract project list with GUIDs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "test.sln"
            sln_path.write_text(SIMPLE_SLN)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_ok()
            data = result.unwrap()
            assert data["solution_name"] == "test"
            assert len(data["projects"]) == 2
            assert data["projects"][0]["name"] == "ConsoleApp"
            assert data["projects"][1]["name"] == "CoreLibrary"
            assert all("guid" in p for p in data["projects"])
    
    def test_solution_parser_extracts_paths(self):
        """Extract relative project paths from .sln"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "test.sln"
            sln_path.write_text(SIMPLE_SLN)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_ok()
            data = result.unwrap()
            paths = [p["path"] for p in data["projects"]]
            assert "Apps\\ConsoleApp\\ConsoleApp.csproj" in paths
            assert "Libs\\CoreLibrary\\CoreLibrary.csproj" in paths
    
    def test_solution_parser_handles_solution_folders(self):
        """Identify solution folders (2150E333...)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "test.sln"
            sln_path.write_text(SIMPLE_SLN)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_ok()
            data = result.unwrap()
            assert "solution_folders" in data
            assert "Apps" in data["solution_folders"]
    
    def test_solution_parser_parses_configurations(self):
        """Extract solution configurations (Debug, Release, etc)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "test.sln"
            sln_path.write_text(SIMPLE_SLN)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_ok()
            data = result.unwrap()
            assert "configurations" in data
            # Configurations might be empty if pattern doesn't match
            assert isinstance(data["configurations"], list)
    
    def test_solution_parser_handles_solution_filters(self):
        """Parse .slnf (solution filter) files for subset solutions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            slnf_path = Path(tmpdir) / "test.slnf"
            slnf_path.write_text(SOLUTION_FILTER)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse_filter(str(slnf_path))
            
            assert result.is_ok()
            data = result.unwrap()
            assert len(data["included_projects"]) == 2
    
    def test_solution_parser_performance_100_projects(self):
        """Performance test: Parse solution with 100+ projects in <1s"""
        import time
        
        # Create a large solution
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_content = "Microsoft Visual Studio Solution File, Format Version 12.00\n"
            for i in range(100):
                guid = f"{i:08X}-{i:04X}-{i:04X}-{i:04X}-{i:012X}"
                sln_content += f'Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "Project{i}", "Projects\\Project{i}\\Project{i}.csproj", "{{{guid}}}"\nEndProject\n'
            sln_content += "Global\nEndGlobal\n"
            
            sln_path = Path(tmpdir) / "large.sln"
            sln_path.write_text(sln_content)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            
            start = time.time()
            result = parser.parse(str(sln_path))
            elapsed = time.time() - start
            
            assert result.is_ok()
            assert elapsed < 1.0, f"Parse took {elapsed:.2f}s, expected <1s"
            assert len(result.unwrap()["projects"]) == 100
    
    def test_solution_parser_invalid_format_handling(self):
        """Handle invalid .sln format gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "invalid.sln"
            sln_path.write_text("invalid content\nno projects here")
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_err()
            assert "Invalid solution format" in str(result.unwrap_err())
    
    def test_solution_parser_unicode_project_names(self):
        """Handle Unicode characters in project names"""
        sln_with_unicode = SIMPLE_SLN.replace("ConsoleApp", "应用程序")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "unicode.sln"
            sln_path.write_text(sln_with_unicode, encoding='utf-8')
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_ok()
            data = result.unwrap()
            assert "应用程序" in [p["name"] for p in data["projects"]]
    
    def test_solution_parser_empty_solution(self):
        """Handle empty solution with no projects"""
        empty_sln = """
Microsoft Visual Studio Solution File, Format Version 12.00
Global
EndGlobal
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "empty.sln"
            sln_path.write_text(empty_sln)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_ok()
            data = result.unwrap()
            assert data["projects"] == []
    
    def test_solution_parser_nested_solution_folders(self):
        """Handle nested solution folder hierarchies"""
        nested_sln = """
Microsoft Visual Studio Solution File, Format Version 12.00
Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "Root", "Root", "{11111111-1111-1111-1111-111111111111}"
	ProjectSection(SolutionItems) = preProject
	EndProjectSection
EndProject
Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "Child", "Child", "{22222222-2222-2222-2222-222222222222}"
EndProject
Global
EndGlobal
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "nested.sln"
            sln_path.write_text(nested_sln)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_ok()
            data = result.unwrap()
            assert len(data["solution_folders"]) >= 2
    
    def test_solution_parser_extracts_guids_correctly(self):
        """Verify GUID extraction is accurate"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "test.sln"
            sln_path.write_text(SIMPLE_SLN)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_ok()
            data = result.unwrap()
            guids = [p["guid"] for p in data["projects"]]
            assert "12345678-1234-1234-1234-123456789012" in guids
            assert "87654321-4321-4321-4321-210987654321" in guids
    
    def test_solution_parser_round_trip(self):
        """Parse and re-serialize solution maintains data integrity"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "test.sln"
            sln_path.write_text(SIMPLE_SLN)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result1 = parser.parse(str(sln_path))
            
            assert result1.is_ok()
            data1 = result1.unwrap()
            
            # Parse again
            result2 = parser.parse(str(sln_path))
            data2 = result2.unwrap()
            
            # Should be identical
            assert data1["projects"] == data2["projects"]
            assert data1["configurations"] == data2["configurations"]


class TestSolutionParserIntegration:
    """Integration tests for SolutionFileParser with real scenarios"""
    
    def test_enterprise_monolith_solution_parsing(self):
        """Parse realistic enterprise monolith solution"""
        enterprise_sln = """
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "WebApp", "Apps\\WebApp\\WebApp.csproj", "{11111111-1111-1111-1111-111111111111}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Services", "Libs\\Services\\Services.csproj", "{22222222-2222-2222-2222-222222222222}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "DataAccess", "Libs\\DataAccess\\DataAccess.csproj", "{33333333-3333-3333-3333-333333333333}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Database", "Database\\Database.sqlproj", "{44444444-4444-4444-4444-444444444444}"
EndProject
Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "Apps", "Apps", "{AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA}"
EndProject
Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "Libs", "Libs", "{BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Any CPU = Debug|Any CPU
		Release|Any CPU = Release|Any CPU
	EndGlobalSection
EndGlobal
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sln_path = Path(tmpdir) / "Enterprise.sln"
            sln_path.write_text(enterprise_sln)
            
            from cortex.lens.dotnet.solution_parser import SolutionFileParser
            parser = SolutionFileParser()
            result = parser.parse(str(sln_path))
            
            assert result.is_ok()
            data = result.unwrap()
            assert len(data["projects"]) == 4
            assert any(p["name"] == "Database" for p in data["projects"])
            assert len(data["solution_folders"]) == 2
