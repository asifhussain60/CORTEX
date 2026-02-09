"""
Build Dependency Graph Use Case (Phase 54-A S1)

AC_START: AC-PHASE54A-S1-UC04
Description: Dependency analysis and graph construction
Authority: phase-54-A-incremental-onboarding-refactor.yaml, S1 task 4
"""

from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, field

from cortex.brain.core.result import Result, Ok, Err


@dataclass
class PackageDependency:
    """Package dependency model."""
    name: str
    version: str
    source: str  # "requirements.txt", "package.json", "pyproject.toml", etc.
    category: str  # "runtime", "dev", "test"


@dataclass
class DependencyGraph:
    """Dependency graph model."""
    dependencies: List[PackageDependency]
    dependency_count: int
    runtime_count: int
    dev_count: int
    direct_dependencies: Set[str] = field(default_factory=set)


class BuildDependencyGraphUseCase:
    """Build dependency graph (SOLID: Single Responsibility)."""
    
    def execute(self, repo_path: Path) -> Result[DependencyGraph]:
        """
        Build dependency graph for repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Result containing DependencyGraph or error
        """
        try:
            if not repo_path.exists():
                return Err(f"Repository not found: {repo_path}")
            
            dependencies = []
            
            # Scan different dependency files
            dependencies.extend(self._parse_python_deps(repo_path))
            dependencies.extend(self._parse_node_deps(repo_path))
            dependencies.extend(self._parse_dotnet_deps(repo_path))
            
            runtime_count = sum(1 for d in dependencies if d.category == "runtime")
            dev_count = sum(1 for d in dependencies if d.category == "dev")
            
            graph = DependencyGraph(
                dependencies=dependencies,
                dependency_count=len(dependencies),
                runtime_count=runtime_count,
                dev_count=dev_count,
                direct_dependencies=set(d.name for d in dependencies),
            )
            
            return Ok(graph)
        
        except Exception as e:
            return Err(f"Failed to build dependency graph: {str(e)}")
    
    def _parse_python_deps(self, repo_path: Path) -> List[PackageDependency]:
        """Parse Python dependencies."""
        deps = []
        try:
            # requirements.txt
            req_file = repo_path / "requirements.txt"
            if req_file.exists():
                for line in req_file.read_text().split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pkg = self._parse_requirement(line, "requirements.txt", "runtime")
                        if pkg:
                            deps.append(pkg)
            
            # pyproject.toml
            pyproject_file = repo_path / "pyproject.toml"
            if pyproject_file.exists():
                deps.extend(self._parse_pyproject(pyproject_file))
        
        except Exception:
            pass
        
        return deps
    
    def _parse_node_deps(self, repo_path: Path) -> List[PackageDependency]:
        """Parse Node.js dependencies."""
        deps = []
        try:
            pkg_file = repo_path / "package.json"
            if pkg_file.exists():
                import json
                data = json.loads(pkg_file.read_text())
                
                # Runtime dependencies
                for pkg_name, version in data.get("dependencies", {}).items():
                    deps.append(PackageDependency(
                        name=pkg_name,
                        version=version,
                        source="package.json",
                        category="runtime",
                    ))
                
                # Dev dependencies
                for pkg_name, version in data.get("devDependencies", {}).items():
                    deps.append(PackageDependency(
                        name=pkg_name,
                        version=version,
                        source="package.json",
                        category="dev",
                    ))
        
        except Exception:
            pass
        
        return deps
    
    def _parse_dotnet_deps(self, repo_path: Path) -> List[PackageDependency]:
        """Parse .NET dependencies."""
        deps = []
        try:
            for csproj_file in repo_path.rglob("*.csproj"):
                deps.extend(self._parse_csproj(csproj_file))
        except Exception:
            pass
        
        return deps
    
    def _parse_requirement(self, line: str, source: str, category: str) -> PackageDependency | None:
        """Parse single requirement line."""
        try:
            # Handle version specifiers: package==1.0.0, package>=1.0, etc.
            for sep in ["==", ">=", "<=", "~=", "!=", "<", ">"]:
                if sep in line:
                    name, version = line.split(sep, 1)
                    return PackageDependency(
                        name=name.strip(),
                        version=version.strip(),
                        source=source,
                        category=category,
                    )
            
            # No version specifier
            return PackageDependency(
                name=line.strip(),
                version="*",
                source=source,
                category=category,
            )
        except Exception:
            pass
        
        return None
    
    def _parse_pyproject(self, pyproject_file: Path) -> List[PackageDependency]:
        """Parse pyproject.toml dependencies."""
        deps = []
        try:
            import toml
            data = toml.loads(pyproject_file.read_text())
            
            for pkg_name, version in data.get("project", {}).get("dependencies", []):
                deps.append(PackageDependency(
                    name=pkg_name,
                    version=str(version),
                    source="pyproject.toml",
                    category="runtime",
                ))
        except Exception:
            pass
        
        return deps
    
    def _parse_csproj(self, csproj_file: Path) -> List[PackageDependency]:
        """Parse .csproj NuGet dependencies."""
        deps = []
        try:
            content = csproj_file.read_text()
            # Simple regex-based parsing (real XML parsing would be better)
            import re
            for match in re.finditer(r"<PackageReference\s+Include=\"([^\"]+)\".*?Version=\"([^\"]+)\"", content):
                pkg_name, version = match.groups()
                deps.append(PackageDependency(
                    name=pkg_name,
                    version=version,
                    source=csproj_file.name,
                    category="runtime",
                ))
        except Exception:
            pass
        
        return deps


# AC_COMPLETE: AC-PHASE54A-S1-UC04 ✅
