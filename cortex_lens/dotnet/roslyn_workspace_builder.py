"""
Phase 67 S1: Roslyn Workspace Builder

Loads .NET solutions and projects for semantic analysis using Roslyn.

Strategy: Use subprocess to invoke dotnet CLI + Roslyn analyzer tool.
This approach is more reliable than pythonnet and works cross-platform.

AC_START: AC-PHASE67-S1-WORKSPACE-001
"""

import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RoslynWorkspaceBuilder:
    """
    Builder for loading .NET solutions/projects with Roslyn semantic analysis.
    
    Uses external Roslyn CLI tool (C#) for reliable cross-platform operation.
    Falls back to syntax-only analysis if semantic extraction unavailable.
    
    Example:
        >>> builder = RoslynWorkspaceBuilder()
        >>> result = builder.load_solution(Path("MySolution.sln"))
        >>> print(f"Loaded {len(result['projects'])} projects")
    """
    
    def __init__(self, roslyn_cli_path: Optional[Path] = None):
        """
        Initialize Roslyn workspace builder.
        
        Args:
            roslyn_cli_path: Path to Roslyn CLI analyzer (optional)
        """
        self.roslyn_cli_path = roslyn_cli_path
        self._verify_dotnet_sdk()
    
    def _verify_dotnet_sdk(self) -> None:
        """Verify .NET SDK is available."""
        try:
            result = subprocess.run(
                ["dotnet", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f".NET SDK version: {version}")
            else:
                logger.warning(".NET SDK not found — semantic analysis unavailable")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f".NET SDK check failed: {e}")
    
    def is_valid_solution(self, solution_path: Path) -> bool:
        """
        Check if path points to a valid .NET solution file.
        
        Args:
            solution_path: Path to .sln file
        
        Returns:
            True if valid solution file
        """
        if not solution_path.exists():
            return False
        
        if solution_path.suffix.lower() != ".sln":
            return False
        
        # Basic validation: Check for solution header
        try:
            content = solution_path.read_text(encoding='utf-8-sig')
            return "Microsoft Visual Studio Solution File" in content
        except Exception as e:
            logger.debug(f"Error reading solution file: {e}")
            return False
    
    def is_valid_project(self, project_path: Path) -> bool:
        """
        Check if path points to a valid .NET project file.
        
        Args:
            project_path: Path to .csproj file
        
        Returns:
            True if valid project file
        """
        if not project_path.exists():
            return False
        
        if project_path.suffix.lower() != ".csproj":
            return False
        
        # Basic validation: Check for XML project structure
        try:
            content = project_path.read_text(encoding='utf-8')
            return "<Project" in content and ("Sdk=" in content or "ToolsVersion=" in content)
        except Exception as e:
            logger.debug(f"Error reading project file: {e}")
            return False
    
    def load_solution(
        self,
        solution_path: Path,
        include_semantic: bool = False
    ) -> Dict[str, Any]:
        """
        Load .NET solution with optional semantic analysis.
        
        Args:
            solution_path: Path to .sln file
            include_semantic: If True, extract semantic models (requires Roslyn CLI)
        
        Returns:
            Dictionary with solution metadata and projects
        
        Raises:
            FileNotFoundError: If solution file doesn't exist
        
        Example:
            >>> builder = RoslynWorkspaceBuilder()
            >>> result = builder.load_solution(Path("MySolution.sln"))
            >>> print(result["projects"][0]["name"])
        """
        if not solution_path.exists():
            raise FileNotFoundError(f"Solution file not found: {solution_path}")
        
        if not self.is_valid_solution(solution_path):
            raise ValueError(f"Invalid solution file: {solution_path}")
        
        logger.info(f"Loading solution: {solution_path}")
        
        # Parse solution file to extract projects
        projects = self._parse_solution_projects(solution_path)
        
        result: Dict[str, Any] = {
            "solution_path": str(solution_path),
            "solution_name": solution_path.stem,
            "projects": projects,
            "project_count": len(projects)
        }
        
        # If semantic analysis requested, invoke Roslyn CLI
        if include_semantic:
            if self.roslyn_cli_path and self.roslyn_cli_path.exists():
                result["semantic_models"] = self._extract_semantic_models(solution_path)
            else:
                logger.warning("Roslyn CLI not available — skipping semantic extraction")
                result["semantic_models"] = []
        
        logger.info(f"Loaded solution with {len(projects)} projects")
        return result
    
    def load_project(
        self,
        project_path: Path,
        include_semantic: bool = False
    ) -> Dict[str, Any]:
        """
        Load single .NET project.
        
        Args:
            project_path: Path to .csproj file
            include_semantic: If True, extract semantic model
        
        Returns:
            Dictionary with project metadata
        
        Raises:
            FileNotFoundError: If project file doesn't exist
        """
        if not project_path.exists():
            raise FileNotFoundError(f"Project file not found: {project_path}")
        
        if not self.is_valid_project(project_path):
            raise ValueError(f"Invalid project file: {project_path}")
        
        logger.info(f"Loading project: {project_path}")
        
        result: Dict[str, Any] = {
            "project_path": str(project_path),
            "name": project_path.stem,
            "directory": str(project_path.parent)
        }
        
        # Parse .csproj for metadata
        result.update(self._parse_project_metadata(project_path))
        
        # If semantic analysis requested, invoke Roslyn CLI
        if include_semantic:
            if self.roslyn_cli_path and self.roslyn_cli_path.exists():
                result["semantic_model"] = self._extract_project_semantic_model(project_path)
            else:
                logger.warning("Roslyn CLI not available — skipping semantic extraction")
                result["semantic_model"] = None
        
        return result
    
    def _parse_solution_projects(self, solution_path: Path) -> List[Dict[str, Any]]:
        """
        Parse .sln file to extract project references.
        
        Args:
            solution_path: Path to solution file
        
        Returns:
            List of project metadata dictionaries
        """
        projects = []
        solution_dir = solution_path.parent
        
        try:
            content = solution_path.read_text(encoding='utf-8-sig')
            
            # Parse Project lines (format: Project("{GUID}") = "Name", "Path", "{GUID}")
            for line in content.splitlines():
                if line.startswith("Project("):
                    parts = line.split('"')
                    if len(parts) >= 9:  # Need at least 9 parts for valid project line
                        project_name = parts[3]  # Index 3 is the project name
                        project_relative_path = parts[5]  # Index 5 is the project path
                        
                        # Normalize path separators (convert Windows \ to /)
                        project_relative_path = project_relative_path.replace('\\', '/')
                        
                        # Resolve project path
                        project_path = solution_dir / project_relative_path
                        
                        if project_path.exists() and project_path.suffix.lower() == ".csproj":
                            projects.append({
                                "name": project_name,
                                "path": str(project_path),
                                "relative_path": project_relative_path
                            })
                            logger.debug(f"Found project: {project_name} at {project_path}")
        
        except Exception as e:
            logger.error(f"Error parsing solution file: {e}", exc_info=True)
        
        return projects
    
    def _parse_project_metadata(self, project_path: Path) -> Dict[str, Any]:
        """
        Parse .csproj file for basic metadata.
        
        Args:
            project_path: Path to project file
        
        Returns:
            Dictionary with target framework, SDK, etc.
        """
        metadata: Dict[str, Any] = {
            "target_framework": None,
            "sdk": None,
            "nullable": None
        }
        
        try:
            content = project_path.read_text(encoding='utf-8')
            
            # Extract SDK attribute
            if 'Sdk="' in content:
                sdk_start = content.find('Sdk="') + 5
                sdk_end = content.find('"', sdk_start)
                metadata["sdk"] = content[sdk_start:sdk_end]
            
            # Extract TargetFramework
            if "<TargetFramework>" in content:
                tf_start = content.find("<TargetFramework>") + 17
                tf_end = content.find("</TargetFramework>", tf_start)
                metadata["target_framework"] = content[tf_start:tf_end]
            
            # Extract Nullable setting
            if "<Nullable>" in content:
                nullable_start = content.find("<Nullable>") + 10
                nullable_end = content.find("</Nullable>", nullable_start)
                metadata["nullable"] = content[nullable_start:nullable_end]
        
        except Exception as e:
            logger.debug(f"Error parsing project metadata: {e}")
        
        return metadata
    
    def _extract_semantic_models(self, solution_path: Path) -> List[Dict[str, Any]]:
        """
        Extract semantic models from solution using Roslyn CLI.
        
        Args:
            solution_path: Path to solution
        
        Returns:
            List of semantic model dictionaries (one per project)
        """
        # STUB: This will be implemented when Roslyn CLI tool is ready
        logger.warning("Semantic model extraction not yet implemented")
        return []
    
    def _extract_project_semantic_model(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract semantic model from single project using Roslyn CLI.
        
        Args:
            project_path: Path to project
        
        Returns:
            Semantic model dictionary or None
        """
        # STUB: This will be implemented when Roslyn CLI tool is ready
        logger.warning("Project semantic model extraction not yet implemented")
        return None


# AC_COMPLETE: AC-PHASE67-S1-WORKSPACE-001 ✅ Basic workspace loading implemented
