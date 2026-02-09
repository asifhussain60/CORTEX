"""Solution File (.sln) Parser for .NET Enterprise LENS Analysis"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from cortex.brain.core.result import Ok, Err


@dataclass
class ProjectEntry:
    """Represents a project entry in a solution file"""
    name: str
    path: str
    guid: str
    type_guid: str  # C# project = FAE04EC0-301F-11D3-BF4B-00C04F79EFBC


@dataclass
class SolutionFolder:
    """Represents a solution folder (logical grouping)"""
    name: str
    guid: str


class SolutionFileParser:
    """Parse Visual Studio Solution (.sln) and Solution Filter (.slnf) files"""
    
    # GUID for C# project type
    CSHARP_PROJECT_GUID = "FAE04EC0-301F-11D3-BF4B-00C04F79EFBC"
    # GUID for solution folder
    SOLUTION_FOLDER_GUID = "2150E333-8FDC-42A3-9474-1A3956D46DE8"
    # GUID for SQL Server database project
    SQLSERVER_PROJECT_GUID = "00d1a9c2-b5f0-4af3-8072-f6c62b433612"
    
    def parse(self, sln_path: str) -> Union[Ok, Err]:
        """
        Parse a Visual Studio solution file (.sln)
        
        Returns:
            Ok: {
                "solution_name": str,
                "projects": [{"name": str, "path": str, "guid": str, "type": str}],
                "solution_folders": [str],
                "configurations": [str],
                "project_count": int,
                "folder_count": int
            }
            Err: Error message
        """
        try:
            path = Path(sln_path)
            if not path.exists():
                return Err(f"Solution file not found: {sln_path}")
            
            if not path.suffix.lower() == ".sln":
                return Err(f"Not a solution file: {sln_path}")
            
            content = path.read_text(encoding='utf-8')
            
            # Validate format
            if "Microsoft Visual Studio Solution File" not in content:
                return Err("Invalid solution format: Missing Visual Studio Solution File header")
            
            projects = self._extract_projects(content)
            folders = self._extract_solution_folders(content)
            configurations = self._extract_configurations(content)
            
            return Ok({
                "solution_name": path.stem,
                "projects": projects,
                "solution_folders": folders,
                "configurations": configurations,
                "project_count": len(projects),
                "folder_count": len(folders)
            })
        
        except UnicodeDecodeError as e:
            return Err(f"Failed to decode solution file: {str(e)}")
        except Exception as e:
            return Err(f"Error parsing solution file: {str(e)}")
    
    def parse_filter(self, slnf_path: str) -> Union[Ok, Err]:
        """
        Parse a Visual Studio Solution Filter file (.slnf)
        
        Returns:
            Ok: {
                "filter_name": str,
                "included_projects": [str],
                "excluded_projects": [str]
            }
            Err: Error message
        """
        try:
            path = Path(slnf_path)
            if not path.exists():
                return Err(f"Solution filter file not found: {slnf_path}")
            
            if not path.suffix.lower() == ".slnf":
                return Err(f"Not a solution filter file: {slnf_path}")
            
            content = path.read_text(encoding='utf-8')
            data = json.loads(content)
            
            included = data.get("solution", {}).get("projects", [])
            
            return Ok({
                "filter_name": path.stem,
                "included_projects": included,
                "excluded_projects": []
            })
        
        except json.JSONDecodeError as e:
            return Err(f"Invalid JSON in solution filter: {str(e)}")
        except Exception as e:
            return Err(f"Error parsing solution filter: {str(e)}")
    
    def _extract_projects(self, content: str) -> List[Dict]:
        """Extract all Project entries from solution content"""
        projects = []
        
        # Pattern: Project("{TYPE-GUID}") = "NAME", "PATH", "{PROJECT-GUID}"
        pattern = r'Project\("{([^}]+)}"\)\s*=\s*"([^"]+)",\s*"([^"]+)",\s*"{([^}]+)}"'
        
        for match in re.finditer(pattern, content):
            type_guid, name, path_str, project_guid = match.groups()
            
            # Skip solution folders (they have a different GUID)
            if type_guid.lower() != self.SOLUTION_FOLDER_GUID.lower():
                projects.append({
                    "name": name,
                    "path": path_str,
                    "guid": project_guid,
                    "type_guid": type_guid,
                    "is_csharp": type_guid.lower() == self.CSHARP_PROJECT_GUID.lower(),
                    "is_database": type_guid.lower() == self.SQLSERVER_PROJECT_GUID.lower()
                })
        
        return projects
    
    def _extract_solution_folders(self, content: str) -> List[str]:
        """Extract solution folder names"""
        folders = []
        
        # Solution folders have type GUID 2150E333-8FDC-42A3-9474-1A3956D46DE8
        pattern = r'Project\("{' + self.SOLUTION_FOLDER_GUID + r'}"\)\s*=\s*"([^"]+)"'
        
        for match in re.finditer(pattern, content):
            folder_name = match.group(1)
            folders.append(folder_name)
        
        return folders
    
    def _extract_configurations(self, content: str) -> List[str]:
        """Extract solution configurations (Debug, Release, etc)"""
        configurations = []
        
        # Find GlobalSection(SolutionConfigurationPlatforms) section
        config_section_pattern = r'GlobalSection\(SolutionConfigurationPlatforms\)\s*=\s*preSolution(.*?)EndGlobalSection'
        match = re.search(config_section_pattern, content, re.DOTALL)
        
        if match:
            section_content = match.group(1)
            # Pattern: "Debug|Any CPU" = "Debug|Any CPU"
            config_pattern = r'"([^"]+)"\s*=\s*"[^"]+"'
            configs = re.findall(config_pattern, section_content)
            configurations = list(dict.fromkeys(configs))  # Remove duplicates while preserving order
        
        return configurations
    
    def build_project_graph(self, sln_path: str) -> Union[Ok, Err]:
        """
        Build a dependency graph by analyzing ProjectReference elements
        
        Returns:
            Ok: {
                "projects": {project_name: project_path},
                "dependencies": {project_name: [dependent_project_names]},
                "circular": [list of circular dependency chains]
            }
            Err: Error message
        """
        try:
            parse_result = self.parse(sln_path)
            if parse_result.is_err():
                return parse_result
            
            sln_data = parse_result.unwrap()
            sln_dir = Path(sln_path).parent
            
            projects = {}
            dependencies = {}
            
            # Load all .csproj files and analyze ProjectReferences
            for project in sln_data["projects"]:
                proj_path = sln_dir / project["path"]
                if proj_path.exists() and proj_path.suffix.lower() == ".csproj":
                    projects[project["name"]] = str(proj_path)
                    
                    # Extract ProjectReference elements
                    csproj_content = proj_path.read_text(encoding='utf-8')
                    refs = self._extract_project_references(csproj_content, projects)
                    dependencies[project["name"]] = refs
            
            # Detect circular dependencies
            circulars = self._detect_circular_dependencies(dependencies)
            
            return Ok({
                "projects": projects,
                "dependencies": dependencies,
                "circular": circulars,
                "total_projects": len(projects),
                "total_references": sum(len(deps) for deps in dependencies.values())
            })
        
        except Exception as e:
            return Err(f"Error building project graph: {str(e)}")
    
    def _extract_project_references(self, csproj_content: str, known_projects: Dict) -> List[str]:
        """Extract ProjectReference elements from .csproj"""
        references = []
        
        # Pattern: <ProjectReference Include="path to project" />
        pattern = r'<ProjectReference\s+Include="([^"]+)"'
        
        for match in re.finditer(pattern, csproj_content):
            ref_path = match.group(1)
            # Extract project name from path (e.g., "Libs/CoreLibrary/CoreLibrary.csproj" -> "CoreLibrary")
            proj_name = Path(ref_path).stem
            if proj_name in known_projects or proj_name in known_projects.values():
                references.append(proj_name)
        
        return references
    
    def _detect_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies in project graph"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path = path + [node]
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.discard(node)
        
        for node in dependencies:
            if node not in visited:
                dfs(node, [])
        
        return cycles
