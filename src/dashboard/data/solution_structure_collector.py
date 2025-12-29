"""
Phase 8.1: Solution Structure Collector (Backend)

GREEN phase: Implements backend data collector for solution hierarchy visualization.
Extracts solution/project structure from engineering-onboarding.json and prepares
D3.js-compatible hierarchical data format.
"""

from typing import Dict, List, Optional, Any


class SolutionStructureCollector:
    """
    Collects and structures solution/project hierarchy data for D3.js visualization.
    
    Extracts solution data from engineering-onboarding.json and builds hierarchical
    tree structure: Repository → Solutions → Projects
    
    Output format compatible with D3.js hierarchical layouts.
    """
    
    def extract_solutions_from_onboarding(self, onboarding_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract solution data from engineering-onboarding.json.
        
        Args:
            onboarding_data: Parsed engineering-onboarding.json content
            
        Returns:
            List of solution dictionaries with projects
        """
        if not onboarding_data or "sections" not in onboarding_data:
            return []
        
        sections = onboarding_data.get("sections", [])
        
        # Find "Solution Structure" section
        for section in sections:
            if section.get("title") == "Solution Structure":
                content = section.get("content", {})
                solutions = content.get("solutions", [])
                return solutions
        
        return []
    
    def build_hierarchy(self, solutions: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Build hierarchical tree structure from solution data.
        
        Creates 3-level tree:
        - Root: Repository
        - Level 1: Solutions
        - Level 2: Projects
        
        Args:
            solutions: List of solution dictionaries
            
        Returns:
            D3.js-compatible hierarchical tree
        """
        if solutions is None:
            solutions = []
        
        # Initialize root node
        root = {
            "name": "Repository",
            "type": "root",
            "children": [],
            "value": 0,  # Total LOC
            "file_count": 0  # Total files
        }
        
        # Process each solution
        for solution in solutions:
            # Skip solutions without name
            if "name" not in solution:
                continue
            
            solution_node = self._build_solution_node(solution)
            root["children"].append(solution_node)
            
            # Aggregate to root
            root["value"] += solution_node["value"]
            root["file_count"] += solution_node["file_count"]
        
        return root
    
    def _build_solution_node(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build solution node with aggregated metrics from projects.
        
        Args:
            solution: Solution dictionary with projects
            
        Returns:
            Solution node with children and metrics
        """
        solution_node = {
            "name": solution["name"],
            "type": "solution",
            "children": [],
            "value": 0,  # Total LOC
            "file_count": 0,  # Total files
            "project_count": 0
        }
        
        # Preserve original metadata
        metadata_fields = ["path", "vs_version", "description", "project_count"]
        for field in metadata_fields:
            if field in solution:
                solution_node[field] = solution[field]
        
        # Process projects
        projects = solution.get("projects", [])
        for project in projects:
            # Skip projects without name
            if "name" not in project:
                continue
            
            project_node = self._build_project_node(project)
            solution_node["children"].append(project_node)
            
            # Aggregate to solution
            solution_node["value"] += project_node["value"]
            solution_node["file_count"] += project_node["file_count"]
            solution_node["project_count"] = len(solution_node["children"])
        
        return solution_node
    
    def _build_project_node(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build project leaf node with metrics.
        
        Args:
            project: Project dictionary with LOC and file count
            
        Returns:
            Project node with value (LOC) for D3.js sizing
        """
        # Extract metrics with defaults
        loc = project.get("loc", 0)
        file_count = project.get("file_count", 0)
        
        project_node = {
            "name": project["name"],
            "type": "project",
            "value": loc,  # Used by D3.js for node sizing
            "file_count": file_count
        }
        
        # Preserve additional metadata
        optional_fields = ["type", "path", "responsibilities", "dependencies"]
        for field in optional_fields:
            if field in project:
                project_node[field] = project[field]
        
        return project_node
    
    def extract_dependencies(self, solutions: Optional[List[Dict[str, Any]]]) -> List[Dict[str, str]]:
        """
        Extract dependency edges between projects.
        
        Creates source→target edges for D3.js force-directed graph.
        
        Args:
            solutions: List of solution dictionaries
            
        Returns:
            List of dependency edges {"source": "ProjectA", "target": "ProjectB"}
        """
        if solutions is None:
            solutions = []
        
        edges = []
        
        # Process all projects across all solutions
        for solution in solutions:
            projects = solution.get("projects", [])
            
            for project in projects:
                source_name = project.get("name")
                dependencies = project.get("dependencies", [])
                
                # Skip if no name or no dependencies
                if not source_name or not dependencies:
                    continue
                
                # Create edge for each dependency
                for target_name in dependencies:
                    edges.append({
                        "source": source_name,
                        "target": target_name
                    })
        
        return edges
    
    def calculate_metadata(self, solutions: Optional[List[Dict[str, Any]]]) -> Dict[str, int]:
        """
        Calculate aggregate metadata for dashboard summary.
        
        Args:
            solutions: List of solution dictionaries
            
        Returns:
            Dictionary with totals: solutions, projects, LOC, files
        """
        if solutions is None:
            solutions = []
        
        metadata = {
            "total_solutions": 0,
            "total_projects": 0,
            "total_loc": 0,
            "total_files": 0
        }
        
        metadata["total_solutions"] = len(solutions)
        
        for solution in solutions:
            projects = solution.get("projects", [])
            metadata["total_projects"] += len(projects)
            
            for project in projects:
                metadata["total_loc"] += project.get("loc", 0)
                metadata["total_files"] += project.get("file_count", 0)
        
        return metadata
    
    def collect(self, solutions: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Main entry point: Collect complete solution structure data package.
        
        Returns hierarchical tree, dependency edges, and aggregate metadata
        for D3.js visualization and dashboard summary.
        
        Args:
            solutions: List of solution dictionaries (from engineering-onboarding.json)
            
        Returns:
            Dictionary with:
            - hierarchy: D3.js hierarchical tree
            - dependencies: List of source→target edges
            - metadata: Aggregate totals
        """
        # Handle None input
        if solutions is None:
            solutions = []
        
        # Build components
        hierarchy = self.build_hierarchy(solutions)
        dependencies = self.extract_dependencies(solutions)
        metadata = self.calculate_metadata(solutions)
        
        return {
            "hierarchy": hierarchy,
            "dependencies": dependencies,
            "metadata": metadata
        }
