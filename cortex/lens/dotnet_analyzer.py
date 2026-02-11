# AC_START: AC-PHASE55-S1-dotnet_lens
# Description: Phase 55 S1 - .NET Enterprise LENS Enhancement
# Author: Asif Hussain
# Date: 2026-02-08
# Phase: 55, Stage 1

"""
.NET Enterprise LENS Enhancement: Monolith Discovery & Analysis.

S1 Foundation: Solution file parsing, project structure analysis.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class ProjectType(Enum):
    """Project type classification."""

    CONSOLE = "Console"
    WEB_API = "WebAPI"
    MVC = "MVC"
    BLAZOR = "Blazor"
    LIBRARY = "Library"
    TEST = "Test"
    UNKNOWN = "Unknown"


class DotNetVersion(Enum):
    """Supported .NET versions."""

    FRAMEWORK_4_8 = "net48"
    CORE_3_1 = "netcoreapp3.1"
    NET_5 = "net5.0"
    NET_6 = "net6.0"
    NET_7 = "net7.0"
    NET_8 = "net8.0"
    UNKNOWN = "unknown"


@dataclass
class NuGetPackage:
    """NuGet package reference."""

    name: str
    version: str
    framework_targets: List[str] = field(default_factory=list)
    is_development_dependency: bool = False


@dataclass
class DotNetProject:
    """Representation of a .NET project."""

    name: str
    path: str
    project_type: ProjectType
    target_framework: DotNetVersion
    packages: List[NuGetPackage] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    output_path: Optional[str] = None
    assembly_name: Optional[str] = None


@dataclass
class DotNetSolution:
    """Representation of a .NET solution."""

    name: str
    path: str
    projects: List[DotNetProject] = field(default_factory=list)
    folders: Dict[str, List[str]] = field(default_factory=dict)
    platform_target: Optional[str] = None


class SolutionFileParser:
    """Parse .NET solution (.sln) files."""

    # Regex patterns for .sln parsing
    PROJECT_PATTERN = r'Project\("([^"]*)"\)\s*=\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\s*EndProject'
    GLOBAL_SECTION_PATTERN = r"GlobalSection\((\w+)\)\s*=\s*(\w+)(.*?)EndGlobalSection"

    @staticmethod
    def parse_solution_file(file_content: str, base_path: str = "") -> Optional[DotNetSolution]:
        """Parse .sln file content.

        Args:
            file_content: Content of .sln file
            base_path: Base directory path

        Returns:
            DotNetSolution object
        """
        # AC_START: AC-PHASE55-S1-solution_parsing
        lines = file_content.split("\n")
        solution_name = Path(base_path).name

        # Extract projects
        projects = []
        project_matches = re.finditer(SolutionFileParser.PROJECT_PATTERN, file_content)

        for match in project_matches:
            project_type_guid = match.group(1)
            project_name = match.group(2)
            project_path = match.group(3)
            project_id = match.group(4)

            projects.append(
                DotNetProject(
                    name=project_name,
                    path=str(Path(base_path) / project_path),
                    project_type=SolutionFileParser._detect_project_type(project_type_guid),
                    target_framework=DotNetVersion.UNKNOWN,
                )
            )

        solution = DotNetSolution(
            name=solution_name, path=base_path, projects=projects
        )

        # AC_COMPLETE: AC-PHASE55-S1-solution_parsing
        return solution

    @staticmethod
    def _detect_project_type(type_guid: str) -> ProjectType:
        """Detect project type from GUID."""
        # Standard Visual Studio GUIDs
        guid_map = {
            "FAE04EC0-301F-11D3-BF4B-00C04F79EFBC": ProjectType.CONSOLE,  # C#
            "9A19103F-16F7-4668-BE54-9A1E7A4F7556": ProjectType.LIBRARY,  # .NET Core
            "F2A71F9B-5D33-465A-A702-920D77279786": ProjectType.LIBRARY,  # F#
        }

        return guid_map.get(type_guid, ProjectType.UNKNOWN)


class ProjectFileParser:
    """Parse .NET project (.csproj, .vbproj) files."""

    @staticmethod
    def parse_csproj(file_content: str) -> Optional[DotNetProject]:
        """Parse .csproj file.

        Args:
            file_content: Content of .csproj file

        Returns:
            DotNetProject object
        """
        # AC_START: AC-PHASE55-S1-csproj_parsing
        project = DotNetProject(
            name="Unknown",
            path="",
            project_type=ProjectType.UNKNOWN,
            target_framework=DotNetVersion.UNKNOWN,
        )

        # Extract TargetFramework
        framework_match = re.search(r"<TargetFramework>(.+?)</TargetFramework>", file_content)
        if framework_match:
            framework_str = framework_match.group(1)
            project.target_framework = ProjectFileParser._parse_framework(framework_str)

        # Extract AssemblyName
        assembly_match = re.search(r"<AssemblyName>(.+?)</AssemblyName>", file_content)
        if assembly_match:
            project.assembly_name = assembly_match.group(1)

        # Extract OutputPath
        output_match = re.search(r"<OutputPath>(.+?)</OutputPath>", file_content)
        if output_match:
            project.output_path = output_match.group(1)

        # Extract PackageReferences
        package_matches = re.finditer(
            r'<PackageReference\s+Include="(.+?)"\s+Version="(.+?)"\s*/>', file_content
        )

        for match in package_matches:
            package = NuGetPackage(
                name=match.group(1),
                version=match.group(2),
            )
            project.packages.append(package)

        # AC_COMPLETE: AC-PHASE55-S1-csproj_parsing
        return project

    @staticmethod
    def _parse_framework(framework_str: str) -> DotNetVersion:
        """Parse framework string to DotNetVersion."""
        framework_map = {
            "net48": DotNetVersion.FRAMEWORK_4_8,
            "netcoreapp3.1": DotNetVersion.CORE_3_1,
            "net5.0": DotNetVersion.NET_5,
            "net6.0": DotNetVersion.NET_6,
            "net7.0": DotNetVersion.NET_7,
            "net8.0": DotNetVersion.NET_8,
        }

        return framework_map.get(framework_str, DotNetVersion.UNKNOWN)


class MonolithAnalyzer:
    """Analyze .NET monolith for layer structure."""

    @staticmethod
    def analyze_solution(solution: DotNetSolution) -> Dict[str, Any]:
        """Analyze monolith structure.

        Args:
            solution: DotNetSolution to analyze

        Returns:
            Analysis results
        """
        # AC_START: AC-PHASE55-S1-monolith_analysis
        analysis = {
            "total_projects": len(solution.projects),
            "by_type": {},
            "by_framework": {},
            "total_dependencies": 0,
            "has_tests": False,
            "suspicious_patterns": [],
        }

        # Analyze projects
        for project in solution.projects:
            # Track by type
            type_name = project.project_type.value
            if type_name not in analysis["by_type"]:
                analysis["by_type"][type_name] = 0
            analysis["by_type"][type_name] += 1

            # Track by framework
            fw_name = project.target_framework.value
            if fw_name not in analysis["by_framework"]:
                analysis["by_framework"][fw_name] = 0
            analysis["by_framework"][fw_name] += 1

            # Track dependencies
            analysis["total_dependencies"] += len(project.packages)

            # Detect tests
            if project.project_type == ProjectType.TEST:
                analysis["has_tests"] = True

            # Detect patterns
            if "MonolithProject" in project.name:
                analysis["suspicious_patterns"].append(
                    f"Project '{project.name}' has 'Monolith' in name"
                )

        # AC_COMPLETE: AC-PHASE55-S1-monolith_analysis
        return analysis


class DotNetLensAnalyzer:
    """Main LENS analyzer for .NET enterprise code."""

    def __init__(self, semantic_mode: bool = False):
        """Initialize analyzer.

        Args:
            semantic_mode: Enable Roslyn semantic model extraction (Phase 67 S1)
        """
        self.solution_parser = SolutionFileParser()
        self.project_parser = ProjectFileParser()
        self.monolith_analyzer = MonolithAnalyzer()
        self.semantic_mode = semantic_mode

        # Phase 67 S1: Roslyn semantic integration
        self.roslyn_builder = None
        if semantic_mode:
            try:
                from cortex_lens.dotnet.roslyn_workspace_builder import (
                    RoslynWorkspaceBuilder,
                )
                self.roslyn_builder = RoslynWorkspaceBuilder()
            except ImportError as e:
                # Fallback to syntax-only mode if Roslyn components unavailable
                self.semantic_mode = False
                print(f"Warning: Roslyn semantic mode unavailable ({e}), using syntax-only mode")

    def analyze_solution_file(
        self, solution_file_path: str, solution_content: str
    ) -> Dict[str, Any]:
        """Analyze .NET solution.

        Args:
            solution_file_path: Path to .sln file
            solution_content: Content of .sln file

        Returns:
            Analysis results (syntax-only or syntax + semantic)
        """
        # AC_START: AC-PHASE55-S1-solution_analysis
        solution = self.solution_parser.parse_solution_file(solution_content, solution_file_path)

        if not solution:
            return {"error": "Failed to parse solution"}

        # Syntax analysis (always performed)
        analysis = self.monolith_analyzer.analyze_solution(solution)
        analysis["solution_name"] = solution.name
        analysis["project_count"] = len(solution.projects)
        analysis["mode"] = "syntax" if not self.semantic_mode else "semantic"

        # Phase 67 S1: Semantic analysis integration
        if self.semantic_mode and self.roslyn_builder:
            semantic_data = self._analyze_solution_semantic(solution_file_path)
            if semantic_data and "error" not in semantic_data:
                analysis["semantic"] = semantic_data
                analysis["mode"] = "hybrid"  # Both syntax + semantic

        # AC_COMPLETE: AC-PHASE55-S1-solution_analysis
        return analysis

    def _analyze_solution_semantic(self, solution_path: str) -> Dict[str, Any]:
        """
        Extract semantic model data using Roslyn (Phase 67 S1).

        Args:
            solution_path: Path to .sln file

        Returns:
            Semantic analysis results with type hierarchies, methods, attributes
        """
        # AC_START: AC-PHASE67-S1-SEMANTIC-INTEGRATION-001
        try:
            import logging
            from pathlib import Path

            from cortex_lens.dotnet.attribute_data_extractor import (
                AttributeDataExtractor,
            )
            from cortex_lens.dotnet.cross_assembly_resolver import CrossAssemblyResolver
            from cortex_lens.dotnet.method_signature_analyzer import (
                MethodSignatureAnalyzer,
            )
            from cortex_lens.dotnet.type_symbol_resolver import TypeSymbolResolver

            logger = logging.getLogger(__name__)

            # Guard against None roslyn_builder
            if not self.roslyn_builder:
                return {"error": "Roslyn builder not initialized"}

            # Load solution with semantic model
            solution_data = self.roslyn_builder.load_solution(
                Path(solution_path),
                include_semantic=True
            )

            if not solution_data or "Projects" not in solution_data:
                return {"error": "Failed to load semantic model"}

            # Extract semantic models from all projects
            semantic_models = []
            for project in solution_data["Projects"]:
                if "Types" in project:
                    semantic_models.append(project)

            if not semantic_models:
                return {"error": "No semantic data available"}

            # Initialize semantic analyzers
            type_resolver = TypeSymbolResolver(semantic_models)
            method_analyzer = MethodSignatureAnalyzer()
            attribute_extractor = AttributeDataExtractor()
            assembly_resolver = CrossAssemblyResolver(solution_data)

            # Build comprehensive semantic analysis
            all_types = type_resolver.get_all_types()
            analysis = {
                "type_count": len(all_types),
                "type_names": [t.get("Name") for t in all_types[:100]],  # Limit for readability
                "dependencies": {
                    "graph": assembly_resolver.build_assembly_graph(),
                    "build_order": assembly_resolver.get_dependency_order(),
                    "circular_refs": assembly_resolver.detect_circular_references()
                },
                "api_controllers": [],
                "authorized_types": [],
                "method_summary": {
                    "total_methods": 0,
                    "public_methods": 0,
                    "static_methods": 0
                }
            }

            # Extract API controllers, authorization info, and method stats
            for type_info in all_types[:100]:  # Process first 100 types
                type_name = type_info.get("Name", "Unknown")

                # Check for API controllers
                if attribute_extractor.is_api_controller(type_info):
                    analysis["api_controllers"].append({
                        "name": type_name,
                        "route": attribute_extractor.extract_route_template(type_info),
                        "attributes": attribute_extractor.detect_api_controller_attributes(type_info)
                    })

                # Check authorization
                if attribute_extractor.is_authorized(type_info):
                    analysis["authorized_types"].append({
                        "name": type_name,
                        "attributes": attribute_extractor.detect_authorization_attributes(type_info)
                    })

                # Aggregate method statistics
                if "Methods" in type_info:
                    analysis["method_summary"]["total_methods"] += len(type_info["Methods"])

                    public_methods = method_analyzer.get_all_public_methods(type_info)
                    analysis["method_summary"]["public_methods"] += len(public_methods)

                    static_methods = method_analyzer.get_static_methods(type_info)
                    analysis["method_summary"]["static_methods"] += len(static_methods)

            # AC_COMPLETE: AC-PHASE67-S1-SEMANTIC-INTEGRATION-001
            return analysis

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Semantic analysis failed: {e}")
            return {"error": f"Semantic analysis failed: {str(e)}"}

    def analyze_project_file(self, csproj_path: str, csproj_content: str) -> Dict[str, Any]:
        """Analyze .NET project.

        Args:
            csproj_path: Path to .csproj file
            csproj_content: Content of .csproj file

        Returns:
            Analysis results
        """
        # AC_START: AC-PHASE55-S1-project_analysis
        project = self.project_parser.parse_csproj(csproj_content)

        if not project:
            return {"error": "Failed to parse project"}

        return {
            "project_name": project.assembly_name or "Unknown",
            "target_framework": project.target_framework.value,
            "output_path": project.output_path,
            "packages": [
                {"name": p.name, "version": p.version} for p in project.packages
            ],
            "package_count": len(project.packages),
        }

        # AC_COMPLETE: AC-PHASE55-S1-project_analysis
