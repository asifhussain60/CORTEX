"""MSBuild ProjectReference Dependency Resolver for .NET Enterprise LENS"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union
from cortex.brain.core.result import Ok, Err


class MSBuildDependencyResolver:
    """Analyze .csproj files to resolve ProjectReference dependencies"""
    
    def extract_project_references(self, csproj_path: str) -> Union[Ok, Err]:
        """
        Extract ProjectReference elements from a .csproj file
        
        Returns:
            Ok: List of relative paths to referenced projects
            Err: Error message
        """
        try:
            path = Path(csproj_path)
            if not path.exists():
                return Err(f"Project file not found: {csproj_path}")
            
            content = path.read_text(encoding='utf-8')
            
            # Parse XML
            try:
                root = ET.fromstring(content)
            except ET.ParseError as e:
                return Err(f"Invalid XML in .csproj: {str(e)}")
            
            # Extract ProjectReference elements
            references = []
            namespaces = {'': 'http://schemas.microsoft.com/developer/msbuild/2003'}
            
            # Search with and without namespace
            for elem in root.findall(".//ProjectReference"):
                include = elem.get('Include')
                if include:
                    references.append(include)
            
            return Ok(references)
        
        except Exception as e:
            return Err(f"Error extracting project references: {str(e)}")
    
    def resolve_paths(self, csproj_path: str, relative_paths: List[str]) -> Union[Ok, Err]:
        """
        Resolve relative project paths to absolute paths
        
        Args:
            csproj_path: Path to the .csproj file
            relative_paths: List of relative paths from project references
        
        Returns:
            Ok: List of absolute paths
            Err: Error message
        """
        try:
            csproj_base = Path(csproj_path).parent
            resolved = []
            
            for rel_path in relative_paths:
                # Normalize path separators
                normalized = rel_path.replace("\\", "/")
                abs_path = (csproj_base / normalized).resolve()
                
                if abs_path.exists():
                    resolved.append(str(abs_path))
            
            return Ok(resolved)
        
        except Exception as e:
            return Err(f"Error resolving paths: {str(e)}")
    
    def build_dependency_graph(self, solution_root: str) -> Union[Ok, Err]:
        """
        Build a complete project-to-project dependency graph
        
        Returns:
            Ok: {
                "projects": {project_name: project_path},
                "dependencies": {project_name: [dependent_names]},
                "circular_dependencies": [list of cycles],
                "total_projects": int,
                "total_references": int
            }
            Err: Error message
        """
        try:
            root = Path(solution_root)
            if not root.exists():
                return Err(f"Solution root not found: {solution_root}")
            
            projects = {}
            dependencies = {}
            
            # Find all .csproj files
            for csproj_path in root.rglob("*.csproj"):
                project_name = csproj_path.stem
                projects[project_name] = str(csproj_path)
                
                # Extract references from this project
                refs_result = self.extract_project_references(str(csproj_path))
                
                if refs_result.is_ok():
                    refs = refs_result.unwrap()
                    # Extract project names from paths
                    dep_names = [Path(r).stem for r in refs]
                    dependencies[project_name] = dep_names
                else:
                    dependencies[project_name] = []
            
            # Detect circular dependencies
            circulars = self._detect_circular_dependencies(dependencies)
            
            return Ok({
                "projects": projects,
                "dependencies": dependencies,
                "circular_dependencies": circulars,
                "total_projects": len(projects),
                "total_references": sum(len(deps) for deps in dependencies.values())
            })
        
        except Exception as e:
            return Err(f"Error building dependency graph: {str(e)}")
    
    def detect_layer_violations(self, dependencies: Dict[str, List[str]]) -> Union[Ok, Err]:
        """
        Detect architectural layer violations
        
        Common layers: UI -> Services -> Data (allowed)
        Violations: UI -> Data, Data -> UI
        """
        try:
            violations = []
            
            # Simple heuristic: look for patterns that suggest layer crossing
            layer_keywords = {
                "UI": ["App", "Web", "UI", "Presentation", "Forms"],
                "Service": ["Service", "Business", "Domain"],
                "Data": ["Data", "Repository", "Database", "Db", "Persistence"]
            }
            
            def get_layer(name: str) -> Optional[str]:
                name_lower = name.lower()
                for layer, keywords in layer_keywords.items():
                    if any(kw.lower() in name_lower for kw in keywords):
                        return layer
                return None
            
            for project, deps in dependencies.items():
                from_layer = get_layer(project)
                if not from_layer:
                    continue
                
                for dep in deps:
                    to_layer = get_layer(dep)
                    if not to_layer:
                        continue
                    
                    # Check for violations
                    if from_layer == "UI" and to_layer == "Data":
                        violations.append(f"{project} (UI layer) -> {dep} (Data layer)")
                    elif from_layer == "Data" and to_layer == "UI":
                        violations.append(f"{project} (Data layer) -> {dep} (UI layer)")
            
            return Ok(violations)
        
        except Exception as e:
            return Err(f"Error detecting layer violations: {str(e)}")
    
    def extract_target_framework(self, csproj_path: str) -> Union[Ok, Err]:
        """Extract single TargetFramework from .csproj"""
        try:
            path = Path(csproj_path)
            content = path.read_text(encoding='utf-8')
            
            root = ET.fromstring(content)
            
            # Look for TargetFramework element
            for elem in root.findall(".//TargetFramework"):
                if elem.text:
                    return Ok(elem.text)
            
            # If not found, return None
            return Ok(None)
        
        except Exception as e:
            return Err(f"Error extracting target framework: {str(e)}")
    
    def extract_target_frameworks(self, csproj_path: str) -> Union[Ok, Err]:
        """Extract multiple TargetFrameworks from .csproj"""
        try:
            path = Path(csproj_path)
            content = path.read_text(encoding='utf-8')
            
            root = ET.fromstring(content)
            
            # Look for TargetFrameworks element (plural)
            for elem in root.findall(".//TargetFrameworks"):
                if elem.text:
                    # Split by semicolon
                    frameworks = [f.strip() for f in elem.text.split(";")]
                    return Ok(frameworks)
            
            # Fallback to single TargetFramework
            for elem in root.findall(".//TargetFramework"):
                if elem.text:
                    return Ok([elem.text])
            
            return Ok([])
        
        except Exception as e:
            return Err(f"Error extracting target frameworks: {str(e)}")
    
    def _detect_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies in the graph"""
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
                    cycle_start = path.index(neighbor) if neighbor in path else -1
                    if cycle_start >= 0:
                        cycle = path[cycle_start:] + [neighbor]
                        cycles.append(cycle)
            
            rec_stack.discard(node)
        
        for node in dependencies:
            if node not in visited:
                dfs(node, [])
        
        return cycles
