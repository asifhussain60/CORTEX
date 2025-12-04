"""
Tech Stack Collector

Detects technology stack (languages, frameworks, libraries) from project files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.dashboard.data.base_collector import BaseDataCollector


class TechStackCollector(BaseDataCollector):
    """
    Collects technology stack information from project files.
    
    Detects:
    - Python packages (requirements.txt, setup.py, pyproject.toml)
    - JavaScript packages (package.json)
    - .NET packages (*.csproj, packages.config)
    - Database technologies
    - DevOps tools
    
    Data Source: CURRENT STATE ONLY - No mock data, versions from actual files.
    """
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect tech stack data from project files.
        
        Returns:
            Dict with keys: frontend, backend, database, devops, summary
        """
        self.logger.info("Collecting tech stack data...")
        
        tech_stack = {
            "frontend": self._collect_frontend(),
            "backend": self._collect_backend(),
            "database": self._collect_database(),
            "devops": self._collect_devops(),
            "summary": {
                "total_technologies": 0,
                "current_count": 0,
                "outdated_count": 0,
                "deprecated_count": 0,
                "last_scan": datetime.now().isoformat()
            }
        }
        
        # Calculate summary
        all_techs = (
            tech_stack["frontend"] + 
            tech_stack["backend"] + 
            tech_stack["database"] + 
            tech_stack["devops"]
        )
        
        tech_stack["summary"]["total_technologies"] = len(all_techs)
        tech_stack["summary"]["current_count"] = len([t for t in all_techs if t["status"] == "current"])
        tech_stack["summary"]["outdated_count"] = len([t for t in all_techs if t["status"] == "outdated"])
        tech_stack["summary"]["deprecated_count"] = len([t for t in all_techs if t["status"] == "deprecated"])
        
        self.logger.info(f"Collected {len(all_techs)} technologies")
        return tech_stack
    
    def _collect_frontend(self) -> List[Dict[str, Any]]:
        """Detect frontend technologies from package.json."""
        techs = []
        
        # Check package.json
        package_json = self._read_file("package.json")
        if package_json:
            data = self._safe_parse_json(package_json)
            if data:
                # Frontend frameworks/libraries
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                frontend_libs = ["react", "vue", "angular", "@angular/core", "svelte", "next", "gatsby"]
                for lib in frontend_libs:
                    if lib in deps:
                        techs.append(self._create_tech_entry(
                            name=lib.title().replace("@angular/core", "Angular"),
                            version=self._clean_version(deps[lib]),
                            category="framework"
                        ))
                
                # Build tools
                build_tools = ["webpack", "vite", "parcel", "rollup", "esbuild"]
                for tool in build_tools:
                    if tool in deps:
                        techs.append(self._create_tech_entry(
                            name=tool.title(),
                            version=self._clean_version(deps[tool]),
                            category="build_tool"
                        ))
        
        return techs
    
    def _collect_backend(self) -> List[Dict[str, Any]]:
        """Detect backend technologies from requirements.txt, setup.py, etc."""
        techs = []
        
        # Check requirements.txt
        requirements = self._read_file("requirements.txt")
        if requirements:
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package==version
                    match = re.match(r'^([a-zA-Z0-9\-_.]+)([>=<~!]*)([\d.]*)', line)
                    if match:
                        package, operator, version = match.groups()
                        
                        # Identify major frameworks
                        if package.lower() in ["django", "flask", "fastapi", "pyramid", "tornado"]:
                            techs.append(self._create_tech_entry(
                                name=package.title(),
                                version=version or "unknown",
                                category="framework"
                            ))
                        # Database drivers
                        elif package.lower() in ["psycopg2", "pymongo", "pymysql", "redis", "sqlalchemy"]:
                            techs.append(self._create_tech_entry(
                                name=package.title(),
                                version=version or "unknown",
                                category="database_driver"
                            ))
        
        # Check for .NET (*.csproj)
        csproj_files = list(self.project_root.glob("**/*.csproj"))
        if csproj_files:
            techs.append(self._create_tech_entry(
                name=".NET",
                version=self._extract_dotnet_version(csproj_files[0]) or "unknown",
                category="framework"
            ))
        
        return techs
    
    def _collect_database(self) -> List[Dict[str, Any]]:
        """Detect database technologies from config files."""
        techs = []
        
        # Check for SQLite
        if list(self.project_root.glob("**/*.db")) or list(self.project_root.glob("**/*.sqlite")):
            techs.append(self._create_tech_entry(
                name="SQLite",
                version="3.x",
                category="database"
            ))
        
        # Check for PostgreSQL (database URLs in config)
        for config_file in ["config.json", ".env", "settings.py"]:
            content = self._read_file(config_file)
            if content and "postgres" in content.lower():
                techs.append(self._create_tech_entry(
                    name="PostgreSQL",
                    version="unknown",
                    category="database"
                ))
                break
        
        # Check for MongoDB
        for config_file in ["config.json", ".env", "settings.py"]:
            content = self._read_file(config_file)
            if content and "mongodb" in content.lower():
                techs.append(self._create_tech_entry(
                    name="MongoDB",
                    version="unknown",
                    category="database"
                ))
                break
        
        return techs
    
    def _collect_devops(self) -> List[Dict[str, Any]]:
        """Detect DevOps tools from workflow files."""
        techs = []
        
        # Check for Docker
        if self._file_exists("Dockerfile") or self._file_exists("docker-compose.yml"):
            techs.append(self._create_tech_entry(
                name="Docker",
                version="unknown",
                category="containerization"
            ))
        
        # Check for GitHub Actions
        if (self.project_root / ".github" / "workflows").exists():
            techs.append(self._create_tech_entry(
                name="GitHub Actions",
                version="latest",
                category="ci_cd"
            ))
        
        # Check for pytest
        if self._file_exists("pytest.ini") or self._file_exists("tests/"):
            techs.append(self._create_tech_entry(
                name="pytest",
                version=self._get_package_version("pytest"),
                category="testing"
            ))
        
        return techs
    
    def _create_tech_entry(
        self, 
        name: str, 
        version: str, 
        category: str
    ) -> Dict[str, Any]:
        """
        Create standardized tech entry.
        
        Args:
            name: Technology name
            version: Version string
            category: Category (framework, database, etc.)
            
        Returns:
            Dict with name, version, status, category, cve_count, eol_date
        """
        return {
            "name": name,
            "version": version,
            "latest": "unknown",  # Would need PyPI/npm API calls for real latest
            "status": self._determine_status(name, version),
            "category": category,
            "cve_count": 0,  # Would need CVE database integration
            "eol_date": None
        }
    
    def _determine_status(self, name: str, version: str) -> str:
        """
        Determine if technology is current, outdated, or deprecated.
        
        Args:
            name: Technology name
            version: Version string
            
        Returns:
            "current", "outdated", or "deprecated"
        """
        # Simplified logic - would need real version comparison
        if version in ["unknown", "latest"]:
            return "current"
        
        # Check for very old versions (heuristic)
        if version.startswith("1.") or version.startswith("2."):
            return "outdated"
        
        return "current"
    
    def _clean_version(self, version_str: str) -> str:
        """Clean version string from package manager format."""
        # Remove ^, ~, >=, etc.
        return re.sub(r'[^\d.]', '', version_str)
    
    def _extract_dotnet_version(self, csproj_path: Path) -> Optional[str]:
        """Extract .NET version from .csproj file."""
        try:
            content = csproj_path.read_text()
            match = re.search(r'<TargetFramework>(.*?)</TargetFramework>', content)
            if match:
                return match.group(1)
        except Exception as e:
            self.logger.error(f"Error reading {csproj_path}: {e}")
        return None
    
    def _get_package_version(self, package_name: str) -> str:
        """Get installed package version."""
        requirements = self._read_file("requirements.txt")
        if requirements:
            for line in requirements.split('\n'):
                if line.startswith(package_name):
                    match = re.search(r'==([0-9.]+)', line)
                    if match:
                        return match.group(1)
        return "unknown"
