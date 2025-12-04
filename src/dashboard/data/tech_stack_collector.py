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
        
        # Check for .NET/C# (High Priority)
        csproj_files = list(self.project_root.glob("**/*.csproj"))
        cs_files = list(self.project_root.glob("**/*.cs"))
        
        if csproj_files or cs_files:
            # Detect .NET version
            dotnet_version = "unknown"
            dotnet_frameworks = []
            
            if csproj_files:
                dotnet_version = self._extract_dotnet_version(csproj_files[0]) or "unknown"
                # Extract NuGet packages (frameworks)
                dotnet_frameworks = self._extract_dotnet_frameworks(csproj_files[0])
            
            techs.append(self._create_tech_entry(
                name=".NET" if not dotnet_version.startswith("net") else f".NET {dotnet_version}",
                version=dotnet_version,
                category="framework",
                metadata={
                    "language": "C#",
                    "file_count": len(cs_files),
                    "project_count": len(csproj_files),
                    "frameworks": dotnet_frameworks
                }
            ))
            
            # Add C# as language
            if cs_files:
                techs.append(self._create_tech_entry(
                    name="C#",
                    version=dotnet_version,
                    category="language",
                    metadata={
                        "file_count": len(cs_files),
                        "lines_of_code": self._count_cs_lines(cs_files[:100])  # Sample first 100
                    }
                ))
        
        # Check Python requirements.txt
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
                        if package.lower() in ["django", "flask", "fastapi", "pyramid", "tornado", "aiohttp"]:
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
            
            # Add Python as language if requirements exist
            py_files = list(self.project_root.glob("**/*.py"))
            if py_files:
                techs.append(self._create_tech_entry(
                    name="Python",
                    version=self._extract_python_version(),
                    category="language",
                    metadata={
                        "file_count": len(py_files),
                        "has_requirements": True
                    }
                ))
        
        # Check Node.js/JavaScript
        package_json = self._read_file("package.json")
        if package_json:
            js_files = list(self.project_root.glob("**/*.js"))
            ts_files = list(self.project_root.glob("**/*.ts"))
            
            if js_files:
                techs.append(self._create_tech_entry(
                    name="JavaScript",
                    version="ES6+",
                    category="language",
                    metadata={"file_count": len(js_files)}
                ))
            
            if ts_files:
                techs.append(self._create_tech_entry(
                    name="TypeScript",
                    version="unknown",
                    category="language",
                    metadata={"file_count": len(ts_files)}
                ))
        
        return techs
    
    def _extract_dotnet_frameworks(self, csproj_path: Path) -> List[str]:
        """Extract .NET frameworks/packages from .csproj."""
        frameworks = []
        try:
            content = csproj_path.read_text(encoding='utf-8', errors='ignore')
            
            # Extract PackageReference items
            package_refs = re.findall(r'<PackageReference\s+Include="([^"]+)"', content)
            
            # Filter for major frameworks
            major_frameworks = [
                'EntityFrameworkCore', 'EntityFramework', 
                'AspNetCore', 'ASP.NET',
                'Newtonsoft.Json', 'AutoMapper',
                'Serilog', 'NLog',
                'xUnit', 'NUnit', 'MSTest'
            ]
            
            for pkg in package_refs:
                for framework in major_frameworks:
                    if framework.lower() in pkg.lower():
                        frameworks.append(pkg)
                        break
        except Exception as e:
            self.logger.debug(f"Error extracting frameworks: {e}")
        
        return frameworks[:10]  # Limit to top 10
    
    def _count_cs_lines(self, cs_files: List[Path]) -> int:
        """Count lines of code in C# files (sample)."""
        total_lines = 0
        for cs_file in cs_files:
            try:
                content = cs_file.read_text(encoding='utf-8', errors='ignore')
                # Count non-empty, non-comment lines
                lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('//')]
                total_lines += len(lines)
            except Exception:
                continue
        return total_lines
    
    def _extract_python_version(self) -> str:
        """Extract Python version from runtime or config."""
        # Check .python-version file
        py_version = self._read_file(".python-version")
        if py_version:
            return py_version.strip()
        
        # Check pyproject.toml
        pyproject = self._read_file("pyproject.toml")
        if pyproject:
            match = re.search(r'python\s*=\s*"([^"]+)"', pyproject)
            if match:
                return match.group(1)
        
        return "3.x"
    
    def _collect_database(self) -> List[Dict[str, Any]]:
        """Detect database technologies with BALANCED confidence (1+ strong signal) and early exit."""
        techs = []
        detected_dbs = set()
        
        # SQL Server Detection (High Priority)
        sql_server_indicators = {
            'files': ['.mdf', '.ldf'],
            'patterns': [
                r'Server\s*=|Data Source\s*=|Initial Catalog\s*=',
                r'SqlConnection|System\.Data\.SqlClient',
                r'Microsoft\.EntityFrameworkCore\.SqlServer',
                r'Integrated Security\s*=\s*True'
            ],
            'config_keywords': ['sqlserver', 'sql server', 'mssql', '.database.windows.net']
        }
        
        signals = self._detect_database_with_confidence('SQL Server', sql_server_indicators)
        if signals >= 1:  # Accept 1+ signals (balanced confidence)
            techs.append(self._create_tech_entry(
                name="SQL Server",
                version="unknown",
                category="database",
                metadata={"confidence_signals": signals}
            ))
            detected_dbs.add('sqlserver')
        
        # Early exit if we have 2 databases already (rare to have more)
        if len(techs) >= 2:
            return techs
        
        # Access Database Detection
        access_indicators = {
            'files': ['.mdb', '.accdb'],
            'patterns': [
                r'OleDbConnection|System\.Data\.OleDb',
                r'Microsoft\.ACE\.OLEDB|Microsoft\.Jet\.OLEDB',
                r'Provider\s*=\s*Microsoft\.(ACE|Jet)\.OLEDB'
            ],
            'config_keywords': ['access database', '.mdb', '.accdb', 'oledb']
        }
        
        signals = self._detect_database_with_confidence('Microsoft Access', access_indicators)
        if signals >= 1:  # Accept 1+ signals
            techs.append(self._create_tech_entry(
                name="Microsoft Access",
                version="unknown",
                category="database",
                metadata={"confidence_signals": signals}
            ))
            detected_dbs.add('access')
        
        # Early exit if we have 2 databases
        if len(techs) >= 2:
            return techs
        
        # PostgreSQL Detection (require 2 signals to avoid false positives)
        postgres_indicators = {
            'files': [],
            'patterns': [
                r'Npgsql|NpgsqlConnection',
                r'postgres://|postgresql://',
                r'Host\s*=.*Port\s*=.*Database\s*='
            ],
            'config_keywords': ['postgres', 'postgresql', 'npgsql']
        }
        
        signals = self._detect_database_with_confidence('PostgreSQL', postgres_indicators)
        if signals >= 2:  # Require 2 signals (PostgreSQL prone to false positives)
            techs.append(self._create_tech_entry(
                name="PostgreSQL",
                version="unknown",
                category="database",
                metadata={"confidence_signals": signals}
            ))
            detected_dbs.add('postgres')
        
        # Early exit if we have 2 databases
        if len(techs) >= 2:
            return techs
        
        # MongoDB Detection
        mongo_indicators = {
            'files': [],
            'patterns': [
                r'MongoClient|MongoDB\.Driver',
                r'mongodb://|mongodb\+srv://'
            ],
            'config_keywords': ['mongodb', 'mongo']
        }
        
        signals = self._detect_database_with_confidence('MongoDB', mongo_indicators)
        if signals >= 1:  # Accept 1+ signals
            techs.append(self._create_tech_entry(
                name="MongoDB",
                version="unknown",
                category="database",
                metadata={"confidence_signals": signals}
            ))
            detected_dbs.add('mongo')
        
        # SQLite Detection (Only if no other DB and actual SQLite files exist)
        if not detected_dbs:
            sqlite_files = list(self.project_root.glob("**/*.sqlite")) + list(self.project_root.glob("**/*.sqlite3"))
            # Exclude test databases
            real_sqlite = [f for f in sqlite_files if not any(skip in f.parts for skip in ['test', 'mock', '__pycache__'])]
            if real_sqlite or self._search_code_pattern(r'sqlite3|System\.Data\.SQLite', max_files=50):
                techs.append(self._create_tech_entry(
                    name="SQLite",
                    version="3.x",
                    category="database"
                ))
        
        return techs
    
    def _detect_database_with_confidence(self, name: str, indicators: Dict) -> int:
        """
        Intelligent database detection with confidence scoring.
        
        Args:
            name: Database name
            indicators: Dict with 'files', 'patterns', 'config_keywords'
        
        Returns:
            Confidence score (0-3): number of signals detected
        """
        signals = 0
        
        # Signal 1: Check for database-specific files (FAST - filesystem only)
        for ext in indicators.get('files', []):
            matches = list(self.project_root.glob(f"**/*{ext}"))
            if matches:
                # Exclude test/mock files
                real_matches = [m for m in matches if not any(skip in m.parts for skip in ['test', 'mock', '__pycache__'])]
                if real_matches:
                    self.logger.info(f"Detected {name} via file extension: {ext} ({len(real_matches)} files)")
                    signals += 1
                    break  # Early exit after first file match
        
        # Signal 2: Search code for patterns (OPTIMIZED with separate limits)
        for pattern in indicators.get('patterns', []):
            if self._search_code_pattern(pattern, max_files=50):
                self.logger.info(f"Detected {name} via code pattern: {pattern}")
                signals += 1
                break  # Early exit after first code match
        
        # Signal 3: Check config files for keywords (ALWAYS check - cheap operation)
        config_files = [
            'web.config', 'app.config', 'appsettings.json', 'appsettings.Development.json',
            'config.json', '.env', 'settings.py', 'database.yml', 'connection.json'
        ]
        
        for config_file in config_files:
            content = self._read_file(config_file)
            if content:
                content_lower = content.lower()
                for keyword in indicators.get('config_keywords', []):
                    if keyword.lower() in content_lower:
                        self.logger.info(f"Detected {name} via config keyword: {keyword} in {config_file}")
                        signals += 1
                        break  # Exit inner loop
                if signals >= 2:  # Exit if we have strong confidence
                    break
        
        return signals
    
    def _search_code_pattern(self, pattern: str, max_files: int = 50) -> bool:
        """
        Search code files for regex pattern with SMART PRIORITIZATION.
        Separate limits per file type to avoid flooding from node_modules.
        
        Args:
            pattern: Regex pattern to search
            max_files: Maximum files per extension (not total)
        
        Returns:
            True if pattern found (exits immediately on match)
        """
        # Define search strategy: (extension, skip_dirs, limit_per_type)
        search_strategy = [
            ('**/*.config', ['bin', 'obj', '.git', 'packages', 'node_modules'], max_files),
            ('**/*.cs', ['bin', 'obj', '.git', 'packages', 'node_modules'], max_files),
            ('**/*.csproj', ['.git'], max_files // 2),
            ('**/*.py', ['venv', '__pycache__', '.git', 'node_modules'], max_files),
            ('**/*.js', ['node_modules', '.git', 'dist', 'build', 'coverage'], max_files // 4),  # Reduced JS limit
        ]
        
        for glob_pattern, skip_dirs, limit in search_strategy:
            files_scanned = 0
            
            for file_path in self.project_root.glob(glob_pattern):
                # Pre-filter directories BEFORE reading
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue
                
                if files_scanned >= limit:
                    break  # Move to next file type
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if re.search(pattern, content, re.IGNORECASE):
                        return True  # EARLY EXIT - FOUND!
                    
                    files_scanned += 1
                except Exception:
                    continue
        
        return False
    
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
        category: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create standardized tech entry.
        
        Args:
            name: Technology name
            version: Version string
            category: Category (framework, database, etc.)
            metadata: Optional additional metadata
            
        Returns:
            Dict with name, version, status, category, cve_count, eol_date, metadata
        """
        entry = {
            "name": name,
            "version": version,
            "latest": "unknown",  # Would need PyPI/npm API calls for real latest
            "status": self._determine_status(name, version),
            "category": category,
            "cve_count": 0,  # Would need CVE database integration
            "eol_date": None
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        return entry
    
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
