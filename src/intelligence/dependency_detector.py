"""
Dependency Detector

Detects and parses dependencies from 12 file types across multiple languages.

Supported formats:
- Python: requirements.txt, setup.py, pyproject.toml
- Node.js: package.json
- .NET: *.csproj, packages.config
- Ruby: Gemfile
- Go: go.mod
- Rust: Cargo.toml
- PHP: composer.json
- Java: pom.xml, build.gradle
- Swift: Package.swift
- iOS: Podfile

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DependencyType(str, Enum):
    """Type of dependency."""
    RUNTIME = "runtime"
    DEV = "dev"
    TEST = "test"
    BUILD = "build"


@dataclass
class Dependency:
    """Represents a single dependency."""
    name: str
    version: str
    constraint: str  # ==, >=, ^, ~, *, etc.
    language: str
    source_file: str
    type: DependencyType = DependencyType.RUNTIME
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "constraint": self.constraint,
            "language": self.language,
            "source_file": self.source_file,
            "type": self.type.value
        }


class DependencyDetector:
    """Detects dependencies across multiple languages."""
    
    def __init__(self, repo_path: Path):
        """
        Initialize dependency detector.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = Path(repo_path)
        self.dependencies: List[Dependency] = []
    
    def detect(self) -> Dict[str, Any]:
        """
        Detect all dependencies in repository.
        
        Returns:
            Dictionary with:
                - dependencies: List of all dependencies
                - by_language: Dependencies grouped by language
                - summary: Statistics (total, languages detected)
        """
        self.dependencies = []
        
        # Detect Python
        self._detect_python()
        
        # Detect Node.js
        self._detect_nodejs()
        
        # Detect .NET
        self._detect_dotnet()
        
        # Detect Ruby
        self._detect_ruby()
        
        # Detect Go
        self._detect_go()
        
        # Detect Rust
        self._detect_rust()
        
        # Detect PHP
        self._detect_php()
        
        # Detect Java
        self._detect_java()
        
        # Detect Swift
        self._detect_swift()
        
        # Group by language
        by_language = {}
        for dep in self.dependencies:
            if dep.language not in by_language:
                by_language[dep.language] = []
            by_language[dep.language].append(dep.to_dict())
        
        # Generate summary
        languages = list(by_language.keys())
        
        return {
            "dependencies": [d.to_dict() for d in self.dependencies],
            "by_language": by_language,
            "summary": {
                "total_dependencies": len(self.dependencies),
                "languages_detected": languages,
                "language_count": len(languages)
            }
        }
    
    # ===== Python =====
    
    def _detect_python(self):
        """Detect Python dependencies."""
        # requirements.txt
        req_file = self.repo_path / "requirements.txt"
        if req_file.exists():
            self._parse_requirements_txt(req_file)
        
        # TODO: Add setup.py, pyproject.toml parsers
    
    def _parse_requirements_txt(self, file_path: Path):
        """Parse requirements.txt file."""
        content = file_path.read_text()
        
        for line in content.splitlines():
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse package==version, package>=version, etc.
            # Regex pattern: package_name constraint version
            pattern = r'^([a-zA-Z0-9_\-\.]+)\s*([=<>~!]+)\s*([0-9\.]+(?:,[<>=]+[0-9\.]+)?)'
            match = re.match(pattern, line)
            
            if match:
                name = match.group(1)
                constraint = match.group(2)
                version = match.group(3).split(',')[0]  # Take first version if range
                
                self.dependencies.append(Dependency(
                    name=name,
                    version=version,
                    constraint=constraint,
                    language="python",
                    source_file=str(file_path.relative_to(self.repo_path))
                ))
            else:
                # Package without version
                if re.match(r'^[a-zA-Z0-9_\-\.]+$', line):
                    self.dependencies.append(Dependency(
                        name=line,
                        version="*",
                        constraint="*",
                        language="python",
                        source_file=str(file_path.relative_to(self.repo_path))
                    ))
    
    # ===== Node.js =====
    
    def _detect_nodejs(self):
        """Detect Node.js dependencies."""
        pkg_file = self.repo_path / "package.json"
        if pkg_file.exists():
            self._parse_package_json(pkg_file)
    
    def _parse_package_json(self, file_path: Path):
        """Parse package.json file."""
        try:
            data = json.loads(file_path.read_text())
            
            # Runtime dependencies
            deps = data.get("dependencies", {})
            for name, version_spec in deps.items():
                self._add_nodejs_dependency(name, version_spec, file_path, DependencyType.RUNTIME)
            
            # Dev dependencies
            dev_deps = data.get("devDependencies", {})
            for name, version_spec in dev_deps.items():
                self._add_nodejs_dependency(name, version_spec, file_path, DependencyType.DEV)
        
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")
    
    def _add_nodejs_dependency(self, name: str, version_spec: str, file_path: Path, dep_type: DependencyType):
        """Add Node.js dependency with version parsing."""
        # Parse version: ^4.18.0, ~4.17.21, 4.18.0, >=4.0.0, etc.
        constraint = "="
        version = version_spec
        
        if version_spec.startswith("^"):
            constraint = "^"
            version = version_spec[1:]
        elif version_spec.startswith("~"):
            constraint = "~"
            version = version_spec[1:]
        elif version_spec.startswith(">="):
            constraint = ">="
            version = version_spec[2:]
        elif version_spec.startswith(">"):
            constraint = ">"
            version = version_spec[1:]
        
        self.dependencies.append(Dependency(
            name=name,
            version=version,
            constraint=constraint,
            language="javascript",
            source_file=str(file_path.relative_to(self.repo_path)),
            type=dep_type
        ))
    
    # ===== .NET =====
    
    def _detect_dotnet(self):
        """Detect .NET dependencies."""
        # Find all .csproj files
        for csproj in self.repo_path.rglob("*.csproj"):
            self._parse_csproj(csproj)
        
        # packages.config
        for pkg_config in self.repo_path.rglob("packages.config"):
            self._parse_packages_config(pkg_config)
    
    def _parse_csproj(self, file_path: Path):
        """Parse .csproj file for PackageReference."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find all PackageReference elements
            # Handle both namespaced and non-namespaced XML
            for elem in root.iter():
                if elem.tag.endswith("PackageReference"):
                    name = elem.get("Include")
                    version = elem.get("Version")
                    
                    if name and version:
                        self.dependencies.append(Dependency(
                            name=name,
                            version=version,
                            constraint="=",
                            language="csharp",
                            source_file=str(file_path.relative_to(self.repo_path))
                        ))
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")
    
    def _parse_packages_config(self, file_path: Path):
        """Parse packages.config file."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for package in root.findall("package"):
                name = package.get("id")
                version = package.get("version")
                
                if name and version:
                    self.dependencies.append(Dependency(
                        name=name,
                        version=version,
                        constraint="=",
                        language="csharp",
                        source_file=str(file_path.relative_to(self.repo_path))
                    ))
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")
    
    # ===== Ruby =====
    
    def _detect_ruby(self):
        """Detect Ruby dependencies from Gemfile."""
        gemfile = self.repo_path / "Gemfile"
        if gemfile.exists():
            self._parse_gemfile(gemfile)
    
    def _parse_gemfile(self, file_path: Path):
        """Parse Gemfile."""
        content = file_path.read_text()
        
        # Pattern: gem 'name', '~> 2.0'
        pattern = r"gem\s+['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"
        
        for match in re.finditer(pattern, content):
            name = match.group(1)
            version_spec = match.group(2)
            
            constraint = "="
            version = version_spec
            
            if version_spec.startswith("~>"):
                constraint = "~>"
                version = version_spec[2:].strip()
            elif version_spec.startswith(">="):
                constraint = ">="
                version = version_spec[2:].strip()
            
            self.dependencies.append(Dependency(
                name=name,
                version=version,
                constraint=constraint,
                language="ruby",
                source_file=str(file_path.relative_to(self.repo_path))
            ))
    
    # ===== Go =====
    
    def _detect_go(self):
        """Detect Go dependencies from go.mod."""
        go_mod = self.repo_path / "go.mod"
        if go_mod.exists():
            self._parse_go_mod(go_mod)
    
    def _parse_go_mod(self, file_path: Path):
        """Parse go.mod file."""
        content = file_path.read_text()
        
        # Pattern: require (
        #   github.com/package v1.2.3
        # )
        pattern = r'([a-zA-Z0-9\-\./_]+)\s+v([0-9\.]+)'
        
        for match in re.finditer(pattern, content):
            name = match.group(1)
            version = match.group(2)
            
            self.dependencies.append(Dependency(
                name=name,
                version=version,
                constraint="=",
                language="go",
                source_file=str(file_path.relative_to(self.repo_path))
            ))
    
    # ===== Rust =====
    
    def _detect_rust(self):
        """Detect Rust dependencies from Cargo.toml."""
        cargo_toml = self.repo_path / "Cargo.toml"
        if cargo_toml.exists():
            self._parse_cargo_toml(cargo_toml)
    
    def _parse_cargo_toml(self, file_path: Path):
        """Parse Cargo.toml file."""
        content = file_path.read_text()
        
        # Simple pattern: name = "version"
        pattern = r'([a-zA-Z0-9_\-]+)\s*=\s*"([0-9\.]+)"'
        
        in_dependencies = False
        for line in content.splitlines():
            if '[dependencies]' in line:
                in_dependencies = True
                continue
            elif line.startswith('[') and in_dependencies:
                in_dependencies = False
            
            if in_dependencies:
                match = re.match(pattern, line)
                if match:
                    self.dependencies.append(Dependency(
                        name=match.group(1),
                        version=match.group(2),
                        constraint="=",
                        language="rust",
                        source_file=str(file_path.relative_to(self.repo_path))
                    ))
    
    # ===== PHP =====
    
    def _detect_php(self):
        """Detect PHP dependencies from composer.json."""
        composer = self.repo_path / "composer.json"
        if composer.exists():
            self._parse_composer_json(composer)
    
    def _parse_composer_json(self, file_path: Path):
        """Parse composer.json file."""
        try:
            data = json.loads(file_path.read_text())
            
            deps = data.get("require", {})
            for name, version in deps.items():
                self.dependencies.append(Dependency(
                    name=name,
                    version=version.lstrip("^~"),
                    constraint="^" if version.startswith("^") else "~" if version.startswith("~") else "=",
                    language="php",
                    source_file=str(file_path.relative_to(self.repo_path))
                ))
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")
    
    # ===== Java =====
    
    def _detect_java(self):
        """Detect Java dependencies."""
        # Maven pom.xml
        for pom in self.repo_path.rglob("pom.xml"):
            self._parse_pom_xml(pom)
        
        # Gradle build.gradle
        for gradle in self.repo_path.rglob("build.gradle"):
            self._parse_build_gradle(gradle)
    
    def _parse_pom_xml(self, file_path: Path):
        """Parse Maven pom.xml."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Maven uses namespaces
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
            
            for dep in root.findall('.//m:dependency', ns):
                group_id = dep.find('m:groupId', ns)
                artifact_id = dep.find('m:artifactId', ns)
                version = dep.find('m:version', ns)
                
                if artifact_id is not None:
                    name = artifact_id.text
                    if group_id is not None:
                        name = f"{group_id.text}.{name}"
                    
                    self.dependencies.append(Dependency(
                        name=name,
                        version=version.text if version is not None else "*",
                        constraint="=",
                        language="java",
                        source_file=str(file_path.relative_to(self.repo_path))
                    ))
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")
    
    def _parse_build_gradle(self, file_path: Path):
        """Parse Gradle build.gradle."""
        content = file_path.read_text()
        
        # Pattern: implementation 'group:artifact:version'
        pattern = r"(?:implementation|compile|api)\s+['\"]([^'\"]+):([^'\"]+):([^'\"]+)['\"]"
        
        for match in re.finditer(pattern, content):
            group = match.group(1)
            artifact = match.group(2)
            version = match.group(3)
            
            self.dependencies.append(Dependency(
                name=f"{group}.{artifact}",
                version=version,
                constraint="=",
                language="java",
                source_file=str(file_path.relative_to(self.repo_path))
            ))
    
    # ===== Swift =====
    
    def _detect_swift(self):
        """Detect Swift dependencies."""
        # Package.swift
        pkg_swift = self.repo_path / "Package.swift"
        if pkg_swift.exists():
            self._parse_package_swift(pkg_swift)
        
        # Podfile (iOS)
        podfile = self.repo_path / "Podfile"
        if podfile.exists():
            self._parse_podfile(podfile)
    
    def _parse_package_swift(self, file_path: Path):
        """Parse Package.swift."""
        content = file_path.read_text()
        
        # Pattern: .package(url: "...", from: "1.0.0")
        pattern = r'\.package\(url:\s*"([^"]+)",\s*(?:from|exact):\s*"([^"]+)"\)'
        
        for match in re.finditer(pattern, content):
            url = match.group(1)
            version = match.group(2)
            name = url.split('/')[-1].replace('.git', '')
            
            self.dependencies.append(Dependency(
                name=name,
                version=version,
                constraint=">=",
                language="swift",
                source_file=str(file_path.relative_to(self.repo_path))
            ))
    
    def _parse_podfile(self, file_path: Path):
        """Parse Podfile (CocoaPods)."""
        content = file_path.read_text()
        
        # Pattern: pod 'Name', '~> 1.0'
        pattern = r"pod\s+['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"
        
        for match in re.finditer(pattern, content):
            name = match.group(1)
            version_spec = match.group(2)
            
            constraint = "="
            version = version_spec
            
            if version_spec.startswith("~>"):
                constraint = "~>"
                version = version_spec[2:].strip()
            
            self.dependencies.append(Dependency(
                name=name,
                version=version,
                constraint=constraint,
                language="swift",
                source_file=str(file_path.relative_to(self.repo_path))
            ))
