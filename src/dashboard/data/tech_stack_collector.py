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
        sln_files = list(self.project_root.glob("**/*.sln"))
        cs_files = list(self.project_root.glob("**/*.cs"))
        
        if csproj_files or cs_files:
            # Parse solution files for project structure
            solution_info = self._parse_solution_files(sln_files)
            
            # Collect versions from all .csproj files
            all_versions = set()
            all_frameworks = {}  # Use dict to aggregate and deduplicate
            project_details = []  # Store individual project info
            
            for csproj_file in csproj_files:
                version = self._extract_dotnet_version(csproj_file)
                if version:
                    all_versions.add(version)
                
                # Extract frameworks from each project
                frameworks = self._extract_dotnet_frameworks(csproj_file)
                for fw in frameworks:
                    fw_name = fw["name"]
                    fw_version = fw["version"]
                    
                    # Skip invalid versions
                    if fw_version in ['0', '1', 'unknown', '']:
                        continue
                    
                    # Extract core package name (Autofac.Extras.Moq -> Autofac)
                    core_name = fw_name.split('.')[0] if '.' in fw_name else fw_name
                    
                    # Keep the highest version if duplicate (compare core package)
                    if core_name not in all_frameworks:
                        all_frameworks[core_name] = fw_version
                    else:
                        # Compare versions (prefer longer version strings, e.g., 6.4.0 > 6.0.1)
                        current_ver = all_frameworks[core_name]
                        if self._compare_versions(fw_version, current_ver) > 0:
                            all_frameworks[core_name] = fw_version
                
                # Store project details
                project_details.append({
                    "name": csproj_file.stem,
                    "path": str(csproj_file.relative_to(self.project_root)),
                    "framework": version,
                    "packages": len(frameworks)
                })
            
            # Determine primary .NET version (most common or latest)
            primary_version = self._determine_primary_dotnet_version(all_versions)
            
            # Create simplified framework list with categorization
            framework_list = []
            for name, ver in list(all_frameworks.items())[:20]:
                # Skip invalid versions
                if ver in ['0', '1', 'unknown']:
                    continue
                # Add category tag if identifiable
                category_tag = self._get_package_category(name)
                if category_tag:
                    framework_list.append(f"{name} {ver} ({category_tag})")
                else:
                    framework_list.append(f"{name} {ver}")
            
            # Add .NET entry with comprehensive metadata
            dotnet_name = ".NET Framework" if "Framework" in primary_version else ".NET"
            dotnet_version = primary_version.replace(".NET Framework ", "").replace(".NET ", "")
            
            techs.append(self._create_tech_entry(
                name=dotnet_name,
                version=dotnet_version,
                category="framework",
                metadata={
                    "language": "C#",
                    "file_count": len(cs_files),
                    "project_count": len(csproj_files),
                    "solution_count": len(sln_files),
                    "solutions": solution_info.get("solutions", []),
                    "projects": project_details[:10],  # Top 10 projects
                    "frameworks": framework_list,
                    "all_versions": list(all_versions),
                    "package_count": len(all_frameworks)
                }
            ))
            
            # Add C# as language
            if cs_files:
                csharp_version = self._map_dotnet_to_csharp_version(primary_version)
                techs.append(self._create_tech_entry(
                    name="C#",
                    version=csharp_version,
                    category="language",
                    metadata={
                        "file_count": len(cs_files),
                        "lines_of_code": self._count_cs_lines(cs_files[:100]),  # Sample first 100
                        "framework_version": dotnet_version
                    }
                ))
            
            # NOTE: Individual package entries removed - they're already in the frameworks list above
            # This prevents duplicate entries like "Autofac 6.4.0" and "Autofac 1" appearing separately
        
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
    
    def _extract_dotnet_frameworks(self, csproj_path: Path) -> List[Dict[str, str]]:
        """
        Extract .NET frameworks/packages from .csproj and packages.config.
        Returns list of dicts with 'name' and 'version' keys.
        """
        frameworks = []
        framework_dict = {}  # Use dict to avoid duplicates
        
        try:
            # Check for packages.config in same directory
            packages_config = csproj_path.parent / "packages.config"
            if packages_config.exists():
                pkg_content = packages_config.read_text(encoding='utf-8', errors='ignore')
                # Parse <package id="Name" version="X.Y.Z" />
                package_pattern = r'<package\s+id="([^"]+)"\s+version="([^"]+)"'
                matches = re.findall(package_pattern, pkg_content, re.IGNORECASE)
                
                for pkg_name, pkg_version in matches:
                    # Store all packages (filtering happens later in _collect_backend)
                    if pkg_name not in framework_dict:
                        framework_dict[pkg_name] = pkg_version
            
            # Also check PackageReference in .csproj (modern SDK-style)
            content = csproj_path.read_text(encoding='utf-8', errors='ignore')
            package_refs = re.findall(r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"', content, re.IGNORECASE)
            
            for pkg_name, pkg_version in package_refs:
                if pkg_name not in framework_dict:
                    framework_dict[pkg_name] = pkg_version
            
            # Also check for HintPath references (older style with packages folder)
            hint_paths = re.findall(r'<HintPath>.*?\\packages\\([^\\]+)\.([0-9.]+)', content)
            for pkg_name, pkg_version in hint_paths:
                if pkg_name not in framework_dict:
                    framework_dict[pkg_name] = pkg_version
            
            # Convert dict to list format
            frameworks = [{"name": name, "version": ver} for name, ver in framework_dict.items()]
            
        except Exception as e:
            self.logger.debug(f"Error extracting frameworks: {e}")
        
        return frameworks  # Return all packages, filtering happens in _collect_backend
    
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
        """Parse connection strings for accurate database detection with version info."""
        techs = []
        detected_dbs = {}
        
        # Parse connection strings from config files
        connection_strings = self._parse_connection_strings()
        
        for conn_info in connection_strings:
            db_type = conn_info.get('type')
            db_version = conn_info.get('version', 'unknown')
            db_server = conn_info.get('server', '')
            db_database = conn_info.get('database', '')
            db_user = conn_info.get('user', '')
            
            if db_type and db_type not in detected_dbs:
                metadata = {
                    "server": db_server,
                    "source": conn_info.get('source', 'config'),
                    "evidence": conn_info.get('evidence', 'Detected from configuration')
                }
                
                # Add database name if available
                if db_database and db_database != db_server:
                    metadata["database"] = db_database
                
                # Add user if available (Oracle)
                if db_user:
                    metadata["user"] = db_user
                
                techs.append(self._create_tech_entry(
                    name=db_type,
                    version=db_version,
                    category="database",
                    metadata=metadata
                ))
                detected_dbs[db_type] = True
        
        # If no connection strings found, check for actual database files
        if not detected_dbs:
            # Access Database - check for actual .mdb/.accdb files
            access_files = list(self.project_root.glob("**/*.mdb")) + list(self.project_root.glob("**/*.accdb"))
            if access_files:
                techs.append(self._create_tech_entry(
                    name="Microsoft Access",
                    version="unknown",
                    category="database",
                    metadata={"file_count": len(access_files)}
                ))
                detected_dbs['access'] = True
            
            # SQLite - check for actual .sqlite/.sqlite3/.db files
            sqlite_files = list(self.project_root.glob("**/*.sqlite")) + list(self.project_root.glob("**/*.sqlite3")) + list(self.project_root.glob("**/*.db"))
            real_sqlite = [f for f in sqlite_files if not any(skip in f.parts for skip in ['test', 'mock', '__pycache__', 'node_modules'])]
            if real_sqlite:
                techs.append(self._create_tech_entry(
                    name="SQLite",
                    version="3.x",
                    category="database",
                    metadata={"file_count": len(real_sqlite)}
                ))
                detected_dbs['sqlite'] = True
        
        return techs
    
    def _parse_connection_strings(self) -> List[Dict[str, str]]:
        """Parse connection strings from config files to detect databases accurately."""
        databases = []
        config_patterns = [
            'web.config', 'app.config', 'appsettings.json', 'appsettings.*.json',
            '*.config', 'database.yml', 'database.yaml', '.env'
        ]
        
        config_files = []
        for pattern in config_patterns:
            config_files.extend(self.project_root.glob(f"**/{pattern}"))
        
        # Exclude transform/example config files
        excluded_patterns = ['web.debug.config', 'web.release.config', '.example', '.sample', '.template']
        valid_config_files = [
            f for f in config_files[:50] 
            if not any(excl in f.name.lower() for excl in excluded_patterns)
        ]
        
        for config_file in valid_config_files:
            try:
                content = config_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                # Helper to check if line is active (not commented)
                def is_active_line(line_idx: int) -> bool:
                    if line_idx < 0 or line_idx >= len(lines):
                        return False
                    line = lines[line_idx].strip()
                    # Check if line itself is commented
                    if line.startswith('<!--') or line.startswith('//') or line.startswith('#'):
                        return False
                    # Check if inside XML comment block
                    if line_idx > 0 and '<!--' in lines[line_idx - 1] and '-->' not in lines[line_idx - 1]:
                        return False
                    return True
                
                # SQL Server patterns - MUST have both Server AND Database (not just sessionState)
                sql_pattern = r'(?:Server|Data Source)\s*=\s*([^;]+).*?(?:Initial Catalog|Database)\s*=\s*([^;]+)'
                for i, line in enumerate(lines):
                    # Skip sessionState configurations (not real database connections)
                    if 'sessionstate' in line.lower() or 'stateconnection' in line.lower():
                        continue
                    
                    if not is_active_line(i):
                        continue
                    
                    match = re.search(sql_pattern, line, re.IGNORECASE)
                    if match:
                        server = match.group(1).strip()
                        database = match.group(2).strip()
                        
                        # Skip example/template values
                        if any(ex in server.lower() for ex in ['example', 'myserver', 'release', 'localhost']):
                            continue
                        if any(ex in database.lower() for ex in ['example', 'mydb', 'testdb', 'sample']):
                            continue
                        
                        db_type = "Azure SQL Database" if ".database.windows.net" in server else "SQL Server"
                        databases.append({
                            'type': db_type,
                            'version': 'unknown',
                            'server': server[:50],
                            'database': database[:50],
                            'source': config_file.name,
                            'evidence': f'Found in {config_file.name} (active config)'
                        })
                        break
                
                # Oracle patterns - data source with User ID (not just driver reference)
                oracle_pattern = r'data source\s*=\s*([A-Z0-9_]+).*?User ID\s*=\s*([^;"\'\s]+)'
                for i, line in enumerate(lines):
                    if not is_active_line(i):
                        continue
                    
                    match = re.search(oracle_pattern, line, re.IGNORECASE)
                    if match:
                        tns_name = match.group(1).strip()
                        user_id = match.group(2).strip()
                        
                        # Skip example/test values
                        if any(ex in tns_name.lower() for ex in ['example', 'sample', 'test']):
                            continue
                        
                        databases.append({
                            'type': 'Oracle Database',
                            'version': 'unknown',
                            'server': tns_name[:50],  # TNS alias
                            'database': tns_name[:50],  # Oracle uses TNS for connection
                            'user': user_id[:30],
                            'source': config_file.name,
                            'evidence': f'Found in {config_file.name} (active config, user: {user_id})'
                        })
                        break
                
                # MySQL patterns
                mysql_patterns = [
                    r'Server\s*=\s*([^;]+).*?(?:Database|Db)\s*=.*?(?:Uid|User)',
                    r'mysql://([^:@]+)',
                    r'MySql\.Data|Pomelo\.EntityFrameworkCore\.MySql'
                ]
                
                for pattern in mysql_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        databases.append({
                            'type': 'MySQL',
                            'version': 'unknown',
                            'server': 'detected',
                            'source': config_file.name
                        })
                        break
                
                # PostgreSQL patterns
                postgres_patterns = [
                    r'Host\s*=\s*([^;]+).*?Port\s*=\s*(\d+).*?Database\s*=',
                    r'postgres://([^:@]+)',
                    r'Npgsql'
                ]
                
                for pattern in postgres_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        databases.append({
                            'type': 'PostgreSQL',
                            'version': 'unknown',
                            'server': 'detected',
                            'source': config_file.name
                        })
                        break
                        
            except Exception as e:
                self.logger.debug(f"Error parsing {config_file}: {e}")
        
        # Deduplicate by type
        seen = set()
        unique_dbs = []
        for db in databases:
            if db['type'] not in seen:
                unique_dbs.append(db)
                seen.add(db['type'])
        
        return unique_dbs
    
    def _compare_versions(self, ver1: str, ver2: str) -> int:
        """Compare version strings. Returns 1 if ver1 > ver2, -1 if ver1 < ver2, 0 if equal."""
        try:
            parts1 = [int(x) for x in ver1.split('.')]
            parts2 = [int(x) for x in ver2.split('.')]
            
            # Pad to same length
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))
            
            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            return 0
        except (ValueError, AttributeError):
            # Fallback to string comparison
            if ver1 > ver2:
                return 1
            elif ver1 < ver2:
                return -1
            return 0
    
    def _detect_database_with_confidence(self, db_name: str, indicators: Dict) -> int:
        """
        Intelligent database detection with confidence scoring.
        
        Args:
            db_name: Database name
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
                    self.logger.info(f"Detected {db_name} via file extension: {ext} ({len(real_matches)} files)")
                    signals += 1
                    break  # Early exit after first file match
        
        # Signal 2: Search code for patterns (OPTIMIZED with separate limits)
        for pattern in indicators.get('patterns', []):
            if self._search_code_pattern(pattern, max_files=50):
                self.logger.info(f"Detected {db_name} via code pattern: {pattern}")
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
                        self.logger.info(f"Detected {db_name} via config keyword: {keyword} in {config_file}")
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
    
    def _get_package_category(self, package_name: str) -> Optional[str]:
        """
        Determine package category for display tagging.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Category string or None
        """
        package_lower = package_name.lower()
        
        # Category mapping
        if 'autofac' in package_lower or 'unity' in package_lower or 'ninject' in package_lower:
            return 'DI Container'
        elif 'entityframework' in package_lower or 'dapper' in package_lower:
            return 'ORM'
        elif 'newtonsoft' in package_lower:
            return 'JSON'
        elif 'serilog' in package_lower or 'nlog' in package_lower or 'log4net' in package_lower:
            return 'Logging'
        elif 'xunit' in package_lower or 'nunit' in package_lower or 'moq' in package_lower:
            return 'Testing'
        elif 'enterpriselibrary' in package_lower:
            return 'Enterprise'
        elif 'automapper' in package_lower:
            return 'Mapping'
        elif 'fluentvalidation' in package_lower:
            return 'Validation'
        elif 'identitymodel' in package_lower or 'identityserver' in package_lower:
            return 'Security'
        elif 'owin' in package_lower:
            return 'Middleware'
        elif 'aspnet' in package_lower:
            return 'Web Framework'
        
        return None
    
    def _determine_status(self, name: str, version: str) -> str:
        """
        Determine if technology is current, outdated, or deprecated.
        
        Args:
            name: Technology name
            version: Version string
            
        Returns:
            "current", "outdated", or "deprecated"
        """
        # Handle unknown versions
        if version in ["unknown", "latest"]:
            return "current"
        
        # .NET Framework version logic
        if ".NET Framework" in name or name == ".NET Framework":
            try:
                ver_num = float(version)
                if ver_num < 4.6:
                    return "deprecated"  # .NET Framework < 4.6 is deprecated
                elif ver_num < 4.8:
                    return "outdated"    # 4.6-4.7.x is outdated
                elif ver_num == 4.8:
                    return "outdated"    # 4.8 is legacy, .NET 6+ is current
                else:
                    return "current"
            except ValueError:
                pass
        
        # .NET Core/.NET 5+ version logic
        if name == ".NET" or name == ".NET Core":
            try:
                ver_num = float(version.split('.')[0])  # Get major version
                if ver_num < 3:
                    return "deprecated"  # .NET Core 1.x-2.x deprecated
                elif ver_num < 6:
                    return "outdated"    # .NET Core 3.x, .NET 5 outdated
                elif ver_num < 8:
                    return "outdated"    # .NET 6-7 approaching EOL
                else:
                    return "current"     # .NET 8+ is current
            except (ValueError, IndexError):
                pass
        
        # C# version logic
        if name == "C#":
            try:
                ver_num = float(version)
                if ver_num < 7.0:
                    return "deprecated"  # C# < 7 is very old
                elif ver_num < 10.0:
                    return "outdated"    # C# 7-9 is outdated
                else:
                    return "current"     # C# 10+ is current
            except ValueError:
                pass
        
        # Python version logic
        if name == "Python":
            try:
                ver_num = float(version.rsplit('.', 1)[0])  # Get major.minor
                if ver_num < 3.7:
                    return "deprecated"  # Python < 3.7 is EOL
                elif ver_num < 3.10:
                    return "outdated"    # Python 3.7-3.9 approaching EOL
                else:
                    return "current"     # Python 3.10+ is current
            except ValueError:
                pass
        
        # Generic version heuristic for packages
        try:
            major_version = int(version.split('.')[0])
            if major_version == 0:
                return "outdated"  # 0.x versions are pre-release/experimental
            elif major_version <= 2:
                return "outdated"  # Very old major versions
            else:
                return "current"   # 3+ likely current
        except (ValueError, IndexError):
            pass
        
        return "current"  # Default to current if can't determine
    
    def _clean_version(self, version_str: str) -> str:
        """Clean version string from package manager format."""
        # Remove ^, ~, >=, etc.
        return re.sub(r'[^\d.]', '', version_str)
    
    def _parse_solution_files(self, sln_files: List[Path]) -> Dict[str, Any]:
        """
        Parse .sln files to extract project structure and metadata.
        
        Args:
            sln_files: List of solution file paths
            
        Returns:
            Dict with solution metadata including project lists
        """
        solutions = []
        
        for sln_file in sln_files:
            try:
                content = sln_file.read_text(encoding='utf-8', errors='ignore')
                
                # Extract project references
                # Format: Project("{...}") = "ProjectName", "Path\To\Project.csproj", "{GUID}"
                project_pattern = r'Project\(".*?"\)\s*=\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"'
                projects = re.findall(project_pattern, content)
                
                # Extract Visual Studio version
                vs_version = "unknown"
                vs_match = re.search(r'# Visual Studio (?:Version )?(\d+)', content)
                if vs_match:
                    vs_version = vs_match.group(1)
                elif re.search(r'VisualStudioVersion = ([\d.]+)', content):
                    vs_match = re.search(r'VisualStudioVersion = ([\d.]+)', content)
                    vs_version = vs_match.group(1) if vs_match else "unknown"
                
                # Extract format version
                format_version = "unknown"
                format_match = re.search(r'Microsoft Visual Studio Solution File, Format Version ([\d.]+)', content)
                if format_match:
                    format_version = format_match.group(1)
                
                solutions.append({
                    "name": sln_file.stem,
                    "path": str(sln_file.relative_to(self.project_root)),
                    "project_count": len(projects),
                    "projects": [{"name": p[0], "path": p[1]} for p in projects[:20]],
                    "vs_version": vs_version,
                    "format_version": format_version
                })
                
            except Exception as e:
                self.logger.debug(f"Error parsing solution file {sln_file}: {e}")
        
        return {
            "solutions": solutions,
            "total_projects": sum(s["project_count"] for s in solutions)
        }
    
    def _determine_primary_dotnet_version(self, versions: set) -> str:
        """Determine the primary .NET version from a set of versions."""
        if not versions:
            return "unknown"
        
        versions_list = list(versions)
        
        # If only one version, return it
        if len(versions_list) == 1:
            return versions_list[0]
        
        # Prefer .NET Core/.NET over Framework
        for v in versions_list:
            if ".NET Framework" not in v and v != "unknown":
                return v
        
        # Otherwise return the latest Framework version (simple string sort)
        return sorted(versions_list, reverse=True)[0]
    
    def _map_dotnet_to_csharp_version(self, dotnet_version: str) -> str:
        """Map .NET version to corresponding C# language version."""
        version_map = {
            "4.8": "7.3",
            "4.7.2": "7.3",
            "4.7.1": "7.2",
            "4.7": "7.1",
            "4.6.2": "7.0",
            "4.6.1": "6.0",
            "4.6": "6.0",
            "4.5": "5.0",
            "6.0": "10.0",
            "7.0": "11.0",
            "8.0": "12.0"
        }
        
        # Extract version number
        for key, csharp_ver in version_map.items():
            if key in dotnet_version:
                return csharp_ver
        
        return "latest"
    
    def _extract_dotnet_version(self, csproj_path: Path) -> Optional[str]:
        """
        Extract .NET version from .csproj file.
        Supports both modern SDK-style and legacy .csproj formats.
        """
        try:
            content = csproj_path.read_text(encoding='utf-8', errors='ignore')
            
            # Modern SDK-style: <TargetFramework>net6.0</TargetFramework>
            match = re.search(r'<TargetFramework>(.*?)</TargetFramework>', content)
            if match:
                framework = match.group(1)
                # Convert net6.0 -> .NET 6.0, net48 -> .NET Framework 4.8
                if framework.startswith('net') and not framework.startswith('netstandard'):
                    version_num = framework.replace('net', '')
                    if '.' in version_num:
                        return f".NET {version_num}"
                    elif len(version_num) >= 2:
                        # net48 -> .NET Framework 4.8
                        major = version_num[0]
                        minor = version_num[1:]
                        return f".NET Framework {major}.{minor}"
                return framework
            
            # Legacy format: <TargetFrameworkVersion>v4.8</TargetFrameworkVersion>
            match = re.search(r'<TargetFrameworkVersion>v?([\d.]+)</TargetFrameworkVersion>', content)
            if match:
                version = match.group(1)
                return f".NET Framework {version}"
                
        except Exception as e:
            self.logger.debug(f"Error reading {csproj_path}: {e}")
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
