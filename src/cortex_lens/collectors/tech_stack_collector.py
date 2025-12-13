"""
Technology Stack Collector

Detects frameworks, libraries, and technology versions in repositories.
"""

import logging
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class TechStackCollector:
    """
    Collect technology stack information
    
    Detects:
    - Programming languages and versions
    - Frameworks (web, mobile, desktop)
    - Package managers and dependencies
    - Build tools
    - Testing frameworks
    - Databases and ORMs
    - Cloud platforms
    - CI/CD tools
    """
    
    @property
    def name(self) -> str:
        return "tech_stack"
    
    @property
    def description(self) -> str:
        return "Technology stack and framework detection"
    
    @property
    def required_for(self) -> list:
        return []  # Optional for all types
    
    # Configuration files that indicate technologies
    TECH_INDICATORS = {
        # Python
        'requirements.txt': {'tech': 'Python', 'type': 'language'},
        'setup.py': {'tech': 'Python', 'type': 'language'},
        'pyproject.toml': {'tech': 'Python', 'type': 'language'},
        'Pipfile': {'tech': 'Python', 'type': 'language'},
        'poetry.lock': {'tech': 'Poetry', 'type': 'package_manager'},
        
        # JavaScript/Node.js
        'package.json': {'tech': 'Node.js', 'type': 'runtime'},
        'package-lock.json': {'tech': 'npm', 'type': 'package_manager'},
        'yarn.lock': {'tech': 'Yarn', 'type': 'package_manager'},
        'pnpm-lock.yaml': {'tech': 'pnpm', 'type': 'package_manager'},
        
        # .NET
        '*.csproj': {'tech': '.NET', 'type': 'language'},
        '*.sln': {'tech': '.NET', 'type': 'language'},
        'packages.config': {'tech': 'NuGet', 'type': 'package_manager'},
        
        # Java
        'pom.xml': {'tech': 'Maven', 'type': 'build_tool'},
        'build.gradle': {'tech': 'Gradle', 'type': 'build_tool'},
        
        # Ruby
        'Gemfile': {'tech': 'Ruby', 'type': 'language'},
        'Gemfile.lock': {'tech': 'Bundler', 'type': 'package_manager'},
        
        # PHP
        'composer.json': {'tech': 'PHP', 'type': 'language'},
        'composer.lock': {'tech': 'Composer', 'type': 'package_manager'},
        
        # Go
        'go.mod': {'tech': 'Go', 'type': 'language'},
        'go.sum': {'tech': 'Go', 'type': 'language'},
        
        # Rust
        'Cargo.toml': {'tech': 'Rust', 'type': 'language'},
        'Cargo.lock': {'tech': 'Rust', 'type': 'language'},
        
        # Docker
        'Dockerfile': {'tech': 'Docker', 'type': 'containerization'},
        'docker-compose.yml': {'tech': 'Docker Compose', 'type': 'orchestration'},
        
        # Kubernetes
        '*.yaml': {'tech': 'Kubernetes', 'type': 'orchestration', 'requires_content_check': True},
        
        # CI/CD
        '.github/workflows/*.yml': {'tech': 'GitHub Actions', 'type': 'ci_cd'},
        '.gitlab-ci.yml': {'tech': 'GitLab CI', 'type': 'ci_cd'},
        'Jenkinsfile': {'tech': 'Jenkins', 'type': 'ci_cd'},
        'azure-pipelines.yml': {'tech': 'Azure DevOps', 'type': 'ci_cd'},
    }
    
    # Framework patterns to search in package files
    FRAMEWORK_PATTERNS = {
        'Python': {
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'pyramid': 'Pyramid',
            'tornado': 'Tornado',
            'aiohttp': 'aiohttp',
            'pytest': 'pytest',
            'unittest': 'unittest',
            'sqlalchemy': 'SQLAlchemy',
            'pandas': 'Pandas',
            'numpy': 'NumPy',
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
        },
        'JavaScript': {
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'next': 'Next.js',
            'nuxt': 'Nuxt.js',
            'express': 'Express',
            'nestjs': 'NestJS',
            'gatsby': 'Gatsby',
            'svelte': 'Svelte',
            'jest': 'Jest',
            'mocha': 'Mocha',
            'cypress': 'Cypress',
            'playwright': 'Playwright',
        },
        '.NET': {
            'Microsoft.AspNetCore': 'ASP.NET Core',
            'Microsoft.EntityFrameworkCore': 'Entity Framework Core',
            'Newtonsoft.Json': 'JSON.NET',
            'xunit': 'xUnit',
            'nunit': 'NUnit',
            'Moq': 'Moq',
        }
    }
    
    def collect(self, repo_path: Path, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect technology stack information
        
        Args:
            repo_path: Path to repository
            classification: Repository classification
            
        Returns:
            {
                'languages': {...},
                'frameworks': [...],
                'package_managers': [...],
                'build_tools': [...],
                'testing': [...],
                'databases': [...],
                'cloud': [...],
                'ci_cd': [...],
                'versions': {...}
            }
        """
        logger.info(f"🔍 Collecting tech stack for {repo_path.name}")
        
        tech_stack = {
            'languages': {},
            'frameworks': [],
            'package_managers': [],
            'build_tools': [],
            'testing': [],
            'databases': [],
            'cloud': [],
            'ci_cd': [],
            'versions': {}
        }
        
        # Scan for configuration files
        detected_tech = self._scan_config_files(repo_path)
        
        # Categorize detected technologies
        for tech_name, tech_info in detected_tech.items():
            tech_type = tech_info['type']
            
            if tech_type == 'language':
                tech_stack['languages'][tech_name] = tech_info
            elif tech_type == 'package_manager':
                tech_stack['package_managers'].append(tech_info)
            elif tech_type == 'build_tool':
                tech_stack['build_tools'].append(tech_info)
            elif tech_type in ('containerization', 'orchestration'):
                tech_stack['cloud'].append(tech_info)
            elif tech_type == 'ci_cd':
                tech_stack['ci_cd'].append(tech_info)
        
        # Detect frameworks from package files
        frameworks = self._detect_frameworks(repo_path, tech_stack['languages'])
        tech_stack['frameworks'] = frameworks
        
        # Detect testing frameworks
        tech_stack['testing'] = self._detect_testing_frameworks(repo_path, frameworks)
        
        # Detect databases
        tech_stack['databases'] = self._detect_databases(repo_path)
        
        # Extract versions where possible
        tech_stack['versions'] = self._extract_versions(repo_path, tech_stack['languages'])
        
        logger.info(f"✅ Tech stack collected: {len(tech_stack['languages'])} languages, "
                   f"{len(tech_stack['frameworks'])} frameworks")
        
        return tech_stack
    
    def collect_safe(self, repo_path: Path, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Safe wrapper with error handling"""
        try:
            return self.collect(repo_path, classification)
        except Exception as e:
            logger.error(f"Tech stack collection failed: {e}")
            return {
                'languages': {},
                'frameworks': [],
                'package_managers': [],
                'build_tools': [],
                'testing': [],
                'databases': [],
                'cloud': [],
                'ci_cd': [],
                'versions': {},
                'error': str(e)
            }
    
    def _scan_config_files(self, repo_path: Path) -> Dict[str, Dict[str, Any]]:
        """Scan for configuration files that indicate technologies"""
        detected = {}
        
        for pattern, info in self.TECH_INDICATORS.items():
            if '*' in pattern:
                # Glob pattern
                matches = list(repo_path.rglob(pattern))
            else:
                # Exact filename
                matches = list(repo_path.rglob(pattern))
            
            if matches:
                tech_name = info['tech']
                if tech_name not in detected:
                    detected[tech_name] = {
                        'name': tech_name,
                        'type': info['type'],
                        'files': [],
                        'confidence': 'high'
                    }
                
                detected[tech_name]['files'].extend([str(m.relative_to(repo_path)) for m in matches[:5]])
        
        return detected
    
    def _detect_frameworks(self, repo_path: Path, languages: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect frameworks from package files"""
        frameworks = []
        
        # Python frameworks from requirements.txt or pyproject.toml
        if 'Python' in languages:
            frameworks.extend(self._detect_python_frameworks(repo_path))
        
        # JavaScript frameworks from package.json
        if 'Node.js' in languages:
            frameworks.extend(self._detect_js_frameworks(repo_path))
        
        # .NET frameworks from .csproj files
        if '.NET' in languages:
            frameworks.extend(self._detect_dotnet_frameworks(repo_path))
        
        return frameworks
    
    def _detect_python_frameworks(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Detect Python frameworks"""
        frameworks = []
        
        # Check requirements.txt
        req_file = repo_path / 'requirements.txt'
        if req_file.exists():
            try:
                content = req_file.read_text(encoding='utf-8', errors='ignore').lower()
                
                for pattern, name in self.FRAMEWORK_PATTERNS['Python'].items():
                    if pattern in content:
                        frameworks.append({
                            'name': name,
                            'language': 'Python',
                            'source': 'requirements.txt'
                        })
            except Exception:
                pass
        
        # Check pyproject.toml
        pyproject = repo_path / 'pyproject.toml'
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding='utf-8', errors='ignore').lower()
                
                for pattern, name in self.FRAMEWORK_PATTERNS['Python'].items():
                    if pattern in content and name not in [f['name'] for f in frameworks]:
                        frameworks.append({
                            'name': name,
                            'language': 'Python',
                            'source': 'pyproject.toml'
                        })
            except Exception:
                pass
        
        return frameworks
    
    def _detect_js_frameworks(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Detect JavaScript frameworks"""
        frameworks = []
        
        package_json = repo_path / 'package.json'
        if package_json.exists():
            try:
                content = package_json.read_text(encoding='utf-8', errors='ignore')
                data = json.loads(content)
                
                # Check dependencies and devDependencies
                all_deps = {}
                all_deps.update(data.get('dependencies', {}))
                all_deps.update(data.get('devDependencies', {}))
                
                for pattern, name in self.FRAMEWORK_PATTERNS['JavaScript'].items():
                    if any(pattern in dep.lower() for dep in all_deps.keys()):
                        frameworks.append({
                            'name': name,
                            'language': 'JavaScript',
                            'source': 'package.json',
                            'version': all_deps.get(pattern, 'unknown')
                        })
            except Exception:
                pass
        
        return frameworks
    
    def _detect_dotnet_frameworks(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Detect .NET frameworks"""
        frameworks = []
        
        csproj_files = list(repo_path.rglob('*.csproj'))
        
        for csproj in csproj_files[:5]:  # Limit to first 5
            try:
                content = csproj.read_text(encoding='utf-8', errors='ignore')
                
                for pattern, name in self.FRAMEWORK_PATTERNS['.NET'].items():
                    if pattern in content and name not in [f['name'] for f in frameworks]:
                        frameworks.append({
                            'name': name,
                            'language': '.NET',
                            'source': csproj.name
                        })
            except Exception:
                pass
        
        return frameworks
    
    def _detect_testing_frameworks(self, repo_path: Path, frameworks: List[Dict[str, Any]]) -> List[str]:
        """Detect testing frameworks"""
        testing = []
        
        # Extract testing frameworks from general framework list
        testing_keywords = ['pytest', 'unittest', 'jest', 'mocha', 'cypress', 'playwright', 
                           'xunit', 'nunit', 'junit', 'testng']
        
        for fw in frameworks:
            if any(keyword in fw['name'].lower() for keyword in testing_keywords):
                testing.append(fw['name'])
        
        return testing
    
    def _detect_databases(self, repo_path: Path) -> List[str]:
        """Detect database usage"""
        databases = []
        
        # Common database indicators
        db_patterns = {
            'postgresql': ['psycopg2', 'pg', 'postgresql'],
            'mysql': ['pymysql', 'mysql', 'mysqlclient'],
            'mongodb': ['pymongo', 'mongodb', 'mongoose'],
            'redis': ['redis', 'redis-py'],
            'sqlite': ['sqlite3', 'sqlite'],
            'sqlserver': ['pyodbc', 'sql server', 'mssql'],
        }
        
        # Scan requirements.txt and package.json
        for dep_file in ['requirements.txt', 'package.json']:
            file_path = repo_path / dep_file
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
                    
                    for db_name, patterns in db_patterns.items():
                        if any(pattern in content for pattern in patterns):
                            if db_name not in databases:
                                databases.append(db_name)
                except Exception:
                    pass
        
        return databases
    
    def _extract_versions(self, repo_path: Path, languages: Dict[str, Any]) -> Dict[str, str]:
        """Extract version information where available"""
        versions = {}
        
        # Python version from .python-version or runtime.txt
        python_version_file = repo_path / '.python-version'
        if python_version_file.exists():
            try:
                versions['Python'] = python_version_file.read_text().strip()
            except Exception:
                pass
        
        # Node.js version from .nvmrc
        nvmrc = repo_path / '.nvmrc'
        if nvmrc.exists():
            try:
                versions['Node.js'] = nvmrc.read_text().strip()
            except Exception:
                pass
        
        # .NET version from global.json
        global_json = repo_path / 'global.json'
        if global_json.exists():
            try:
                data = json.loads(global_json.read_text())
                if 'sdk' in data and 'version' in data['sdk']:
                    versions['.NET'] = data['sdk']['version']
            except Exception:
                pass
        
        return versions
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate collected data structure"""
        required_keys = ['languages', 'frameworks', 'package_managers', 'build_tools', 
                        'testing', 'databases', 'cloud', 'ci_cd', 'versions']
        return all(key in data for key in required_keys)
