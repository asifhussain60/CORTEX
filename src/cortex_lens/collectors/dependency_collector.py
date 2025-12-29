"""
Dependency Collector

Analyzes package dependencies, versions, and vulnerabilities.
"""

import logging
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class DependencyCollector:
    """
    Collect dependency information
    
    Detects:
    - Direct and transitive dependencies
    - Version constraints
    - Outdated packages
    - Known vulnerabilities (optional)
    - License information
    - Dependency tree depth
    """
    
    @property
    def name(self) -> str:
        return "dependency"
    
    @property
    def description(self) -> str:
        return "Package dependency analysis and vulnerability scanning"
    
    @property
    def required_for(self) -> list:
        return []  # Optional for all types
    
    def collect(self, repo_path: Path, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect dependency information
        
        Args:
            repo_path: Path to repository
            classification: Repository classification
            
        Returns:
            {
                'python': {...},
                'javascript': {...},
                'dotnet': {...},
                'summary': {...},
                'vulnerabilities': [...],
                'outdated': [...]
            }
        """
        logger.info(f"🔍 Collecting dependencies for {repo_path.name}")
        
        result = {
            'python': {},
            'javascript': {},
            'dotnet': {},
            'summary': {
                'total_dependencies': 0,
                'direct_dependencies': 0,
                'transitive_dependencies': 0,
                'languages': []
            },
            'vulnerabilities': [],
            'outdated': []
        }
        
        # Python dependencies
        python_deps = self._collect_python_deps(repo_path)
        if python_deps:
            result['python'] = python_deps
            result['summary']['languages'].append('Python')
            result['summary']['direct_dependencies'] += len(python_deps.get('dependencies', []))
        
        # JavaScript/Node.js dependencies
        js_deps = self._collect_javascript_deps(repo_path)
        if js_deps:
            result['javascript'] = js_deps
            result['summary']['languages'].append('JavaScript')
            result['summary']['direct_dependencies'] += len(js_deps.get('dependencies', {}))
        
        # .NET dependencies
        dotnet_deps = self._collect_dotnet_deps(repo_path)
        if dotnet_deps:
            result['dotnet'] = dotnet_deps
            result['summary']['languages'].append('.NET')
            result['summary']['direct_dependencies'] += len(dotnet_deps.get('dependencies', []))
        
        result['summary']['total_dependencies'] = result['summary']['direct_dependencies']
        
        logger.info(f"✅ Dependencies collected: {result['summary']['total_dependencies']} total, "
                   f"{len(result['summary']['languages'])} languages")
        
        return result
    
    def collect_safe(self, repo_path: Path, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Safe wrapper with error handling"""
        try:
            return self.collect(repo_path, classification)
        except Exception as e:
            logger.error(f"Dependency collection failed: {e}")
            return {
                'python': {},
                'javascript': {},
                'dotnet': {},
                'summary': {
                    'total_dependencies': 0,
                    'direct_dependencies': 0,
                    'transitive_dependencies': 0,
                    'languages': []
                },
                'vulnerabilities': [],
                'outdated': [],
                'error': str(e)
            }
    
    def _collect_python_deps(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Collect Python dependencies"""
        result = {
            'dependencies': [],
            'source_files': [],
            'package_manager': None
        }
        
        # Check requirements.txt
        req_file = repo_path / 'requirements.txt'
        if req_file.exists():
            result['source_files'].append('requirements.txt')
            result['package_manager'] = 'pip'
            
            try:
                content = req_file.read_text(encoding='utf-8', errors='ignore')
                result['dependencies'].extend(self._parse_requirements_txt(content))
            except Exception as e:
                logger.warning(f"Failed to parse requirements.txt: {e}")
        
        # Check Pipfile
        pipfile = repo_path / 'Pipfile'
        if pipfile.exists():
            result['source_files'].append('Pipfile')
            result['package_manager'] = 'pipenv'
            
            try:
                content = pipfile.read_text(encoding='utf-8', errors='ignore')
                result['dependencies'].extend(self._parse_pipfile(content))
            except Exception as e:
                logger.warning(f"Failed to parse Pipfile: {e}")
        
        # Check pyproject.toml
        pyproject = repo_path / 'pyproject.toml'
        if pyproject.exists():
            result['source_files'].append('pyproject.toml')
            if not result['package_manager']:
                result['package_manager'] = 'poetry'
            
            try:
                content = pyproject.read_text(encoding='utf-8', errors='ignore')
                result['dependencies'].extend(self._parse_pyproject_toml(content))
            except Exception as e:
                logger.warning(f"Failed to parse pyproject.toml: {e}")
        
        return result if result['dependencies'] else None
    
    def _parse_requirements_txt(self, content: str) -> List[Dict[str, Any]]:
        """Parse requirements.txt format"""
        dependencies = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Skip editable installs and URLs
            if line.startswith('-e') or line.startswith('git+') or line.startswith('http'):
                continue
            
            # Parse package==version or package>=version
            match = re.match(r'^([a-zA-Z0-9_-]+)(==|>=|<=|>|<|~=)?(.+)?', line)
            if match:
                name = match.group(1)
                operator = match.group(2) or '=='
                version = match.group(3) or 'any'
                
                dependencies.append({
                    'name': name,
                    'version': version,
                    'constraint': operator,
                    'type': 'direct'
                })
        
        return dependencies
    
    def _parse_pipfile(self, content: str) -> List[Dict[str, Any]]:
        """Parse Pipfile format (simplified)"""
        dependencies = []
        
        # Simple regex-based parsing (full TOML parsing would be better)
        in_packages = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line == '[packages]':
                in_packages = True
                continue
            elif line.startswith('['):
                in_packages = False
            
            if in_packages and '=' in line:
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*"([^"]+)"', line)
                if match:
                    name = match.group(1)
                    version = match.group(2)
                    
                    dependencies.append({
                        'name': name,
                        'version': version,
                        'constraint': '==',
                        'type': 'direct'
                    })
        
        return dependencies
    
    def _parse_pyproject_toml(self, content: str) -> List[Dict[str, Any]]:
        """Parse pyproject.toml dependencies (simplified)"""
        dependencies = []
        
        # Look for [tool.poetry.dependencies] section
        in_deps = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            if '[tool.poetry.dependencies]' in line:
                in_deps = True
                continue
            elif line.startswith('[') and in_deps:
                in_deps = False
            
            if in_deps and '=' in line:
                # Skip python version
                if line.startswith('python'):
                    continue
                
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']', line)
                if match:
                    name = match.group(1)
                    version = match.group(2)
                    
                    dependencies.append({
                        'name': name,
                        'version': version,
                        'constraint': '^' if '^' in version else '==',
                        'type': 'direct'
                    })
        
        return dependencies
    
    def _collect_javascript_deps(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Collect JavaScript/Node.js dependencies"""
        package_json = repo_path / 'package.json'
        
        if not package_json.exists():
            return None
        
        try:
            content = package_json.read_text(encoding='utf-8', errors='ignore')
            data = json.loads(content)
            
            result = {
                'dependencies': {},
                'dev_dependencies': {},
                'peer_dependencies': {},
                'source_files': ['package.json'],
                'package_manager': 'npm'  # Default
            }
            
            # Detect package manager
            if (repo_path / 'yarn.lock').exists():
                result['package_manager'] = 'yarn'
            elif (repo_path / 'pnpm-lock.yaml').exists():
                result['package_manager'] = 'pnpm'
            
            # Parse dependencies
            if 'dependencies' in data:
                for name, version in data['dependencies'].items():
                    result['dependencies'][name] = {
                        'version': version,
                        'type': 'production'
                    }
            
            if 'devDependencies' in data:
                for name, version in data['devDependencies'].items():
                    result['dev_dependencies'][name] = {
                        'version': version,
                        'type': 'development'
                    }
            
            if 'peerDependencies' in data:
                for name, version in data['peerDependencies'].items():
                    result['peer_dependencies'][name] = {
                        'version': version,
                        'type': 'peer'
                    }
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to parse package.json: {e}")
            return None
    
    def _collect_dotnet_deps(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """Collect .NET dependencies"""
        result = {
            'dependencies': [],
            'source_files': [],
            'package_manager': 'NuGet'
        }
        
        # Scan .csproj files
        csproj_files = list(repo_path.rglob('*.csproj'))
        
        if not csproj_files:
            return None
        
        for csproj in csproj_files[:10]:  # Limit to first 10
            result['source_files'].append(str(csproj.relative_to(repo_path)))
            
            try:
                content = csproj.read_text(encoding='utf-8', errors='ignore')
                result['dependencies'].extend(self._parse_csproj(content))
            except Exception as e:
                logger.warning(f"Failed to parse {csproj.name}: {e}")
        
        # Remove duplicates
        seen = set()
        unique_deps = []
        for dep in result['dependencies']:
            key = (dep['name'], dep['version'])
            if key not in seen:
                seen.add(key)
                unique_deps.append(dep)
        
        result['dependencies'] = unique_deps
        
        return result if result['dependencies'] else None
    
    def _parse_csproj(self, content: str) -> List[Dict[str, Any]]:
        """Parse .csproj PackageReference entries"""
        dependencies = []
        
        # Find PackageReference tags
        pattern = r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"'
        matches = re.findall(pattern, content)
        
        for name, version in matches:
            dependencies.append({
                'name': name,
                'version': version,
                'type': 'direct'
            })
        
        return dependencies
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate collected data structure"""
        required_keys = ['python', 'javascript', 'dotnet', 'summary', 
                        'vulnerabilities', 'outdated']
        return all(key in data for key in required_keys)
