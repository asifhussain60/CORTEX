"""Centralized Package Management Support.

Handles Directory.Build.props and Directory.Packages.props parsing:
- Detect centralized package version definitions
- Merge package versions from hierarchy (local overrides parent)
- Extract MSBuild properties and variables
- Parse NuGet.Config for private feeds
- Resolve package version variables

AC-PHASE55-S3: DependencyAnalyzer supports Directory.Packages.props
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
from xml.etree import ElementTree as ET
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class PackageVersion:
    """Represents a centralized package version."""

    name: str
    version: str
    source: str  # "Directory.Packages.props" or ".csproj"
    override_path: Optional[Path] = None  # If locally overridden


@dataclass
class CentralizedPackageContext:
    """Context for centralized package management."""

    packages: Dict[str, PackageVersion] = field(default_factory=dict)
    directory_build_props: Dict[str, str] = field(default_factory=dict)
    package_sources: List[Dict[str, str]] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "centralized_packages": {
                name: {
                    "version": pkg.version,
                    "source": pkg.source,
                    "override": str(pkg.override_path) if pkg.override_path else None,
                }
                for name, pkg in self.packages.items()
            },
            "directory_build_props": self.directory_build_props,
            "package_sources": self.package_sources,
            "properties": self.properties,
        }


class CentralizedPackageManager:
    """Manages centralized package versions from Directory.Packages.props."""

    # Common MSBuild property patterns
    MSBUILD_PROPERTY_PATTERN = re.compile(r"\$\((\w+)\)")

    def __init__(self, solution_root: Path):
        """Initialize manager with solution root.

        Args:
            solution_root: Path to solution directory
        """
        self.solution_root = Path(solution_root)
        self.context = CentralizedPackageContext()

    def analyze_centralized_packages(self) -> CentralizedPackageContext:
        """Analyze centralized package management in solution.

        Returns:
            CentralizedPackageContext with discovered packages and configuration

        Raises:
            FileNotFoundError: If solution root doesn't exist
        """
        if not self.solution_root.exists():
            raise FileNotFoundError(f"Solution root not found: {self.solution_root}")

        # Find Directory.Packages.props files (travel up directory tree)
        self._discover_directory_packages_props()

        # Find Directory.Build.props files
        self._discover_directory_build_props()

        # Find and parse NuGet.Config
        self._discover_nuget_config()

        return self.context

    def _discover_directory_packages_props(self) -> None:
        """Discover and parse Directory.Packages.props files."""
        current = self.solution_root

        # Traverse up from solution root
        while current != current.parent:
            props_file = current / "Directory.Packages.props"

            if props_file.exists():
                logger.debug(f"Found Directory.Packages.props at {props_file}")
                self._parse_directory_packages_props(props_file)
                break  # Found the main one, stop traversing up

            current = current.parent

    def _parse_directory_packages_props(self, props_file: Path) -> None:
        """Parse Directory.Packages.props file.

        Args:
            props_file: Path to Directory.Packages.props file
        """
        try:
            tree = ET.parse(str(props_file))
            root = tree.getroot()

            # Find all PackageVersion elements
            for pkg_elem in root.findall(".//{{http://schemas.microsoft.com/developer/msbuild/2003}}PackageVersion"):
                self._parse_package_version_element(pkg_elem)

            # Also try without namespace
            if not self.context.packages:
                for pkg_elem in root.findall(".//PackageVersion"):
                    self._parse_package_version_element(pkg_elem)

        except ET.ParseError as e:
            logger.error(f"Failed to parse {props_file}: {e}")
        except Exception as e:
            logger.error(f"Error processing {props_file}: {e}")

    def _parse_package_version_element(self, elem: ET.Element) -> None:
        """Parse a single PackageVersion element.

        Args:
            elem: XML element representing PackageVersion
        """
        include = elem.get("Include", "")
        version = elem.get("Version", "")

        if include and version:
            # Resolve variable references
            resolved_version = self._resolve_variables(version)

            self.context.packages[include] = PackageVersion(
                name=include,
                version=resolved_version,
                source="Directory.Packages.props",
            )
            logger.debug(f"Found package: {include} = {resolved_version}")

    def _discover_directory_build_props(self) -> None:
        """Discover and parse Directory.Build.props files."""
        current = self.solution_root

        # Traverse up from solution root
        while current != current.parent:
            props_file = current / "Directory.Build.props"

            if props_file.exists():
                logger.debug(f"Found Directory.Build.props at {props_file}")
                self._parse_directory_build_props(props_file)
                break

            current = current.parent

    def _parse_directory_build_props(self, props_file: Path) -> None:
        """Parse Directory.Build.props file.

        Args:
            props_file: Path to Directory.Build.props file
        """
        try:
            tree = ET.parse(str(props_file))
            root = tree.getroot()

            # Extract PropertyGroup elements
            for prop_group in root.findall(".//{{http://schemas.microsoft.com/developer/msbuild/2003}}PropertyGroup"):
                self._parse_property_group(prop_group)

            # Also try without namespace
            if not self.context.directory_build_props:
                for prop_group in root.findall(".//PropertyGroup"):
                    self._parse_property_group(prop_group)

        except ET.ParseError as e:
            logger.error(f"Failed to parse {props_file}: {e}")
        except Exception as e:
            logger.error(f"Error processing {props_file}: {e}")

    def _parse_property_group(self, prop_group: ET.Element) -> None:
        """Parse a PropertyGroup element.

        Args:
            prop_group: XML element representing PropertyGroup
        """
        for child in prop_group:
            # Extract tag name (remove namespace if present)
            tag = child.tag
            if "}" in tag:
                tag = tag.split("}")[-1]

            value = child.text or ""
            self.context.directory_build_props[tag] = value
            self.context.properties[tag] = value

    def _discover_nuget_config(self) -> None:
        """Discover and parse NuGet.Config file."""
        config_file = self.solution_root / "NuGet.Config"

        if config_file.exists():
            self._parse_nuget_config(config_file)
        else:
            # Try parent directory
            if self.solution_root.parent != self.solution_root.parent.parent:
                parent_config = self.solution_root.parent / "NuGet.Config"
                if parent_config.exists():
                    self._parse_nuget_config(parent_config)

    def _parse_nuget_config(self, config_file: Path) -> None:
        """Parse NuGet.Config file.

        Args:
            config_file: Path to NuGet.Config file
        """
        try:
            tree = ET.parse(str(config_file))
            root = tree.getroot()

            # Find packageSources element
            for pkg_source in root.findall(".//add"):
                key = pkg_source.get("key", "")
                value = pkg_source.get("value", "")

                if key and value:
                    self.context.package_sources.append({"name": key, "url": value})
                    logger.debug(f"Found package source: {key} = {value}")

        except ET.ParseError as e:
            logger.error(f"Failed to parse {config_file}: {e}")
        except Exception as e:
            logger.error(f"Error processing {config_file}: {e}")

    def _resolve_variables(self, value: str) -> str:
        """Resolve MSBuild variable references in values.

        Args:
            value: Value that may contain $(PropertyName) references

        Returns:
            Value with variables resolved
        """
        def replace_var(match):
            var_name = match.group(1)
            resolved = self.context.properties.get(var_name)
            return resolved if resolved is not None else match.group(0)

        return self.MSBUILD_PROPERTY_PATTERN.sub(replace_var, value)

    def get_package_version(self, package_name: str) -> Optional[str]:
        """Get the version for a package.

        Args:
            package_name: Name of the package

        Returns:
            Version string or None if not found
        """
        if package_name in self.context.packages:
            return self.context.packages[package_name].version
        return None

    def merge_with_project_packages(
        self, project_packages: Dict[str, str]
    ) -> Dict[str, str]:
        """Merge centralized package versions with project-specific ones.

        Project-specific versions override centralized versions.

        Args:
            project_packages: Dictionary of packages from .csproj

        Returns:
            Merged dictionary with all package versions
        """
        merged = {}

        # Start with centralized versions
        for name, pkg in self.context.packages.items():
            merged[name] = pkg.version

        # Override with project-specific versions
        merged.update(project_packages)

        return merged
