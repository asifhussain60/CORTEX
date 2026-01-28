"""Dependency Extraction Layer - Parses dependencies from files.

Phase 11 - CMS-1: Dependency Synaptic Extractors

Supports Python, Node.js, Go, Java, Rust, and .NET dependency files.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

from cortex.sensory.git_sensory_receptor import (
    DependencyData,
    DependencyEcosystem,
)


logger = logging.getLogger(__name__)


class DependencySynapticExtractor(ABC):
    """Abstract base for dependency file parsers."""
    
    @abstractmethod
    def extract(self, content: str) -> List[DependencyData]:
        """Extract dependencies from file content.
        
        Args:
            content: File content as string
            
        Returns:
            List of DependencyData objects
        """
        pass
    
    @abstractmethod
    def get_ecosystem(self) -> DependencyEcosystem:
        """Get ecosystem for this extractor.
        
        Returns:
            DependencyEcosystem enum
        """
        pass


class PythonDependencyExtractor(DependencySynapticExtractor):
    """Extracts dependencies from Python files."""
    
    def get_ecosystem(self) -> DependencyEcosystem:
        """Get ecosystem."""
        return DependencyEcosystem.PYTHON
    
    def extract_requirements_txt(self, content: str) -> List[DependencyData]:
        """Parse requirements.txt format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        dependencies = []
        
        for line in content.split("\n"):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Skip -e (editable), -r (recursive), flags, etc.
            if line.startswith("-"):
                continue
            
            # Parse version specifiers: package==1.0.0, package>=1.0, etc.
            match = re.match(r'^([a-zA-Z0-9\-_.]+)\s*([<>=!~]+.*)?$', line)
            if match:
                package = match.group(1)
                version = match.group(2) if match.group(2) else "*"
                
                dependencies.append(DependencyData(
                    package=package,
                    version=version,
                    ecosystem=self.get_ecosystem(),
                    source="PyPI"
                ))
        
        return dependencies
    
    def extract_pyproject_toml(self, content: str) -> List[DependencyData]:
        """Parse pyproject.toml format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        dependencies = []
        
        # Find [project] dependencies section
        in_dependencies = False
        in_optional = False
        
        for line in content.split("\n"):
            line = line.strip()
            
            if line.startswith("[project]"):
                in_dependencies = True
                in_optional = False
                continue
            elif line.startswith("["):
                in_dependencies = False
                in_optional = False
            
            if in_dependencies and line.startswith("dependencies"):
                # Format: dependencies = ["package>=1.0", "other==2.0"]
                for dep in re.findall(r'"([^"]+)"', line):
                    match = re.match(r'^([a-zA-Z0-9\-_.]+)\s*([<>=!~]+.*)?$', dep)
                    if match:
                        package = match.group(1)
                        version = match.group(2) if match.group(2) else "*"
                        dependencies.append(DependencyData(
                            package=package,
                            version=version,
                            ecosystem=self.get_ecosystem(),
                            source="PyPI"
                        ))
        
        return dependencies
    
    def extract(self, content: str) -> List[DependencyData]:
        """Extract dependencies from Python file content.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        # Try to detect format
        if "dependencies = [" in content or "[project]" in content:
            return self.extract_pyproject_toml(content)
        else:
            return self.extract_requirements_txt(content)


class NodeJsDependencyExtractor(DependencySynapticExtractor):
    """Extracts dependencies from Node.js files."""
    
    def get_ecosystem(self) -> DependencyEcosystem:
        """Get ecosystem."""
        return DependencyEcosystem.NODEJS
    
    def extract_package_json(self, content: str) -> List[DependencyData]:
        """Parse package.json format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        import json
        
        dependencies = []
        
        try:
            data = json.loads(content)
            
            # Extract dependencies
            for section in ["dependencies", "devDependencies", "peerDependencies"]:
                for package, version in data.get(section, {}).items():
                    dependencies.append(DependencyData(
                        package=package,
                        version=version,
                        ecosystem=self.get_ecosystem(),
                        source="npm"
                    ))
        except json.JSONDecodeError:
            logger.warning("Failed to parse package.json")
        
        return dependencies
    
    def extract_yarn_lock(self, content: str) -> List[DependencyData]:
        """Parse yarn.lock format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        dependencies = []
        
        for line in content.split("\n"):
            # yarn.lock format: "package@version:"
            match = re.match(r'^"?([a-zA-Z0-9\-_./@]+)@([^:]+)"?:', line)
            if match:
                package = match.group(1).split("@")[0]  # Remove @scope
                version = match.group(2)
                
                # Skip duplicates
                if not any(d.package == package for d in dependencies):
                    dependencies.append(DependencyData(
                        package=package,
                        version=version,
                        ecosystem=self.get_ecosystem(),
                        source="yarn"
                    ))
        
        return dependencies
    
    def extract(self, content: str) -> List[DependencyData]:
        """Extract dependencies from Node.js file content.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        if content.strip().startswith("{"):
            return self.extract_package_json(content)
        else:
            return self.extract_yarn_lock(content)


class GolangDependencyExtractor(DependencySynapticExtractor):
    """Extracts dependencies from Go files."""
    
    def get_ecosystem(self) -> DependencyEcosystem:
        """Get ecosystem."""
        return DependencyEcosystem.GOLANG
    
    def extract_go_mod(self, content: str) -> List[DependencyData]:
        """Parse go.mod format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        dependencies = []
        in_require = False
        
        for line in content.split("\n"):
            line = line.strip()
            
            if line.startswith("require"):
                in_require = True
                # Single-line require
                if not line.endswith("("):
                    match = re.match(r'require\s+([^\s]+)\s+([^\s]+)', line)
                    if match:
                        dependencies.append(DependencyData(
                            package=match.group(1),
                            version=match.group(2),
                            ecosystem=self.get_ecosystem(),
                            source="go"
                        ))
                continue
            
            if in_require:
                if line == ")":
                    in_require = False
                elif line and not line.startswith("//"):
                    # Multi-line require format: "github.com/user/repo v1.0.0"
                    parts = line.split()
                    if len(parts) >= 2:
                        dependencies.append(DependencyData(
                            package=parts[0],
                            version=parts[1],
                            ecosystem=self.get_ecosystem(),
                            source="go"
                        ))
        
        return dependencies
    
    def extract(self, content: str) -> List[DependencyData]:
        """Extract dependencies from Go file content.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        return self.extract_go_mod(content)


class JavaDependencyExtractor(DependencySynapticExtractor):
    """Extracts dependencies from Java files."""
    
    def get_ecosystem(self) -> DependencyEcosystem:
        """Get ecosystem."""
        return DependencyEcosystem.JAVA
    
    def extract_maven_pom(self, content: str) -> List[DependencyData]:
        """Parse Maven pom.xml format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        dependencies = []
        
        # Simple regex parsing for <dependency> blocks
        # <groupId>org.springframework</groupId>
        # <artifactId>spring-core</artifactId>
        # <version>5.0.0</version>
        
        dep_blocks = re.findall(
            r'<dependency>.*?</dependency>',
            content,
            re.DOTALL
        )
        
        for block in dep_blocks:
            group_id = re.search(r'<groupId>([^<]+)</groupId>', block)
            artifact_id = re.search(r'<artifactId>([^<]+)</artifactId>', block)
            version = re.search(r'<version>([^<]+)</version>', block)
            
            if artifact_id and version:
                package = f"{group_id.group(1)}:{artifact_id.group(1)}" if group_id else artifact_id.group(1)
                dependencies.append(DependencyData(
                    package=package,
                    version=version.group(1),
                    ecosystem=self.get_ecosystem(),
                    source="maven"
                ))
        
        return dependencies
    
    def extract_gradle_build(self, content: str) -> List[DependencyData]:
        """Parse Gradle build.gradle format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        dependencies = []
        
        # Find dependencies block
        dep_match = re.search(r'dependencies\s*\{([^}]+)\}', content, re.DOTALL)
        if not dep_match:
            return dependencies
        
        dep_block = dep_match.group(1)
        
        # Parse lines like: implementation 'group:artifact:version'
        for line in dep_block.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            match = re.match(r"(implementation|compile|api)\s+['\"]([^:]+):([^:]+):([^'\"]+)['\"]", line)
            if match:
                group_id = match.group(2)
                artifact_id = match.group(3)
                version = match.group(4)
                package = f"{group_id}:{artifact_id}"
                
                dependencies.append(DependencyData(
                    package=package,
                    version=version,
                    ecosystem=self.get_ecosystem(),
                    source="gradle"
                ))
        
        return dependencies
    
    def extract(self, content: str) -> List[DependencyData]:
        """Extract dependencies from Java file content.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        if "<dependency>" in content:
            return self.extract_maven_pom(content)
        else:
            return self.extract_gradle_build(content)


class RustDependencyExtractor(DependencySynapticExtractor):
    """Extracts dependencies from Rust files."""
    
    def get_ecosystem(self) -> DependencyEcosystem:
        """Get ecosystem."""
        return DependencyEcosystem.RUST
    
    def extract_cargo_toml(self, content: str) -> List[DependencyData]:
        """Parse Cargo.toml format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        dependencies = []
        in_deps = False
        
        for line in content.split("\n"):
            line = line.strip()
            
            if line.startswith("[dependencies]") or line.startswith("[dev-dependencies]"):
                in_deps = True
                continue
            elif line.startswith("["):
                in_deps = False
            
            if in_deps and "=" in line and not line.startswith("#"):
                # Format: serde = "1.0" or serde = { version = "1.0" }
                match = re.match(r'([a-zA-Z0-9_\-]+)\s*=\s*(["\']([^"\']+)["\']|\{.*?\})', line)
                if match:
                    package = match.group(1)
                    version_str = match.group(2)
                    
                    # Extract version
                    version_match = re.search(r'(["\']([^"\']+)["\']|version\s*=\s*["\']([^"\']+)["\'])', version_str)
                    if version_match:
                        version = version_match.group(2) or version_match.group(3)
                        dependencies.append(DependencyData(
                            package=package,
                            version=version,
                            ecosystem=self.get_ecosystem(),
                            source="crates.io"
                        ))
        
        return dependencies
    
    def extract(self, content: str) -> List[DependencyData]:
        """Extract dependencies from Rust file content.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        return self.extract_cargo_toml(content)


class DotnetDependencyExtractor(DependencySynapticExtractor):
    """Extracts dependencies from .NET files."""
    
    def get_ecosystem(self) -> DependencyEcosystem:
        """Get ecosystem."""
        return DependencyEcosystem.DOTNET
    
    def extract_csproj(self, content: str) -> List[DependencyData]:
        """Parse .csproj XML format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        dependencies = []
        
        # Find PackageReference items
        matches = re.findall(
            r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"',
            content
        )
        
        for package, version in matches:
            dependencies.append(DependencyData(
                package=package,
                version=version,
                ecosystem=self.get_ecosystem(),
                source="NuGet"
            ))
        
        return dependencies
    
    def extract_packages_config(self, content: str) -> List[DependencyData]:
        """Parse packages.config XML format.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        dependencies = []
        
        # Find package elements
        matches = re.findall(
            r'<package\s+id="([^"]+)"\s+version="([^"]+)"',
            content
        )
        
        for package, version in matches:
            dependencies.append(DependencyData(
                package=package,
                version=version,
                ecosystem=self.get_ecosystem(),
                source="NuGet"
            ))
        
        return dependencies
    
    def extract(self, content: str) -> List[DependencyData]:
        """Extract dependencies from .NET file content.
        
        Args:
            content: File content
            
        Returns:
            List of dependencies
        """
        if "<PackageReference" in content:
            return self.extract_csproj(content)
        else:
            return self.extract_packages_config(content)


class DependencySynapticExtractorFactory:
    """Factory for creating dependency extractors.
    
    Maps ecosystems to their corresponding extractors.
    """
    
    _extractors = {
        DependencyEcosystem.PYTHON: PythonDependencyExtractor(),
        DependencyEcosystem.NODEJS: NodeJsDependencyExtractor(),
        DependencyEcosystem.GOLANG: GolangDependencyExtractor(),
        DependencyEcosystem.JAVA: JavaDependencyExtractor(),
        DependencyEcosystem.RUST: RustDependencyExtractor(),
        DependencyEcosystem.DOTNET: DotnetDependencyExtractor(),
    }
    
    @staticmethod
    def get_extractor(ecosystem: DependencyEcosystem) -> Optional[DependencySynapticExtractor]:
        """Get extractor for ecosystem.
        
        Args:
            ecosystem: Dependency ecosystem
            
        Returns:
            Extractor instance or None
        """
        return DependencySynapticExtractorFactory._extractors.get(ecosystem)
    
    @staticmethod
    def extract_dependencies(
        ecosystem: DependencyEcosystem,
        content: str
    ) -> List[DependencyData]:
        """Extract dependencies using appropriate extractor.
        
        Args:
            ecosystem: Dependency ecosystem
            content: File content
            
        Returns:
            List of dependencies
        """
        extractor = DependencySynapticExtractorFactory.get_extractor(ecosystem)
        if not extractor:
            logger.warning(f"No extractor for ecosystem: {ecosystem}")
            return []
        
        try:
            return extractor.extract(content)
        except Exception as e:
            logger.error(f"Error extracting dependencies: {e}")
            return []


if __name__ == "__main__":
    logger.info("Dependency Extraction Layer - Synaptic Extractors")
