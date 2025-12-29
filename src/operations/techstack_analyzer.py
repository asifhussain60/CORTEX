#!/usr/bin/env python3
"""
Technology Stack Analyzer

Detects frameworks, libraries, dependencies, and language statistics
from project files (requirements.txt, package.json, etc.).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class TechStackAnalyzer:
    """Analyzes technology stack from project files"""
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        # Python
        'django': ['django', 'Django'],
        'flask': ['flask', 'Flask'],
        'fastapi': ['fastapi', 'FastAPI'],
        'pytorch': ['torch', 'pytorch'],
        'tensorflow': ['tensorflow', 'tf'],
        'pandas': ['pandas', 'pd'],
        'numpy': ['numpy', 'np'],
        'sqlalchemy': ['sqlalchemy', 'SQLAlchemy'],
        
        # JavaScript
        'react': ['react', 'React'],
        'vue': ['vue', 'Vue'],
        'angular': ['angular', '@angular'],
        'express': ['express'],
        'next': ['next', 'nextjs'],
        'nuxt': ['nuxt', 'nuxtjs'],
        
        # .NET
        'aspnet': ['Microsoft.AspNetCore', 'ASP.NET'],
        'blazor': ['Blazor', 'blazor'],
        'entityframework': ['EntityFramework', 'EF.Core'],
    }
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze technology stack
        Returns comprehensive tech stack data
        """
        logger.info(f"Analyzing technology stack for {self.project_path}")
        
        tech_stack = {
            'languages': self._detect_languages(),
            'frameworks': self._detect_frameworks(),
            'dependencies': self._parse_dependencies(),
            'build_tools': self._detect_build_tools(),
            'databases': self._detect_databases(),
            'devops': self._detect_devops_tools(),
            'statistics': {}
        }
        
        # Calculate statistics
        tech_stack['statistics'] = self._calculate_statistics(tech_stack)
        
        logger.info(f"Tech stack analysis complete: {len(tech_stack['frameworks'])} frameworks detected")
        return tech_stack
    
    def _detect_languages(self) -> List[Dict[str, Any]]:
        """Detect programming languages and their usage"""
        language_extensions = {
            'Python': ['.py'],
            'JavaScript': ['.js', '.jsx', '.ts', '.tsx'],
            'C#': ['.cs'],
            'Java': ['.java'],
            'Go': ['.go'],
            'Rust': ['.rs'],
            'Ruby': ['.rb'],
            'PHP': ['.php'],
            'HTML': ['.html', '.htm'],
            'CSS': ['.css', '.scss', '.sass', '.less'],
            'SQL': ['.sql']
        }
        
        language_stats = {}
        
        for lang, extensions in language_extensions.items():
            files = []
            total_lines = 0
            
            for ext in extensions:
                for file_path in self.project_path.rglob(f'*{ext}'):
                    if self._should_count_file(file_path):
                        files.append(file_path)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                total_lines += len(f.readlines())
                        except:
                            pass
            
            if files:
                language_stats[lang] = {
                    'name': lang,
                    'files': len(files),
                    'lines': total_lines,
                    'extensions': extensions
                }
        
        # Sort by lines of code
        languages = sorted(
            language_stats.values(),
            key=lambda x: x['lines'],
            reverse=True
        )
        
        # Calculate percentages
        total_lines = sum(lang['lines'] for lang in languages)
        for lang in languages:
            lang['percentage'] = round((lang['lines'] / total_lines * 100), 2) if total_lines > 0 else 0
        
        return languages
    
    def _detect_frameworks(self) -> List[Dict[str, Any]]:
        """Detect frameworks used in the project"""
        detected_frameworks = []
        
        # Check dependency files
        dependencies = self._parse_dependencies()
        dep_names = [dep['name'].lower() for dep in dependencies.get('python', [])]
        dep_names += [dep['name'].lower() for dep in dependencies.get('javascript', [])]
        
        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
            for pattern in patterns:
                if any(pattern.lower() in dep for dep in dep_names):
                    detected_frameworks.append({
                        'name': framework,
                        'category': self._get_framework_category(framework),
                        'detected_from': 'dependencies'
                    })
                    break
        
        # Check code imports
        code_frameworks = self._detect_from_code()
        detected_frameworks.extend(code_frameworks)
        
        # Remove duplicates
        seen = set()
        unique_frameworks = []
        for fw in detected_frameworks:
            if fw['name'] not in seen:
                seen.add(fw['name'])
                unique_frameworks.append(fw)
        
        return unique_frameworks
    
    def _detect_from_code(self) -> List[Dict[str, Any]]:
        """Detect frameworks from code imports"""
        frameworks = []
        imports = set()
        
        # Scan Python files
        for py_file in self.project_path.rglob('*.py'):
            if self._should_count_file(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Extract imports
                        import_matches = re.findall(r'(?:from|import)\s+(\w+)', content)
                        imports.update(import_matches)
                except:
                    pass
        
        # Match imports to frameworks
        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in [imp.lower() for imp in imports]:
                    frameworks.append({
                        'name': framework,
                        'category': self._get_framework_category(framework),
                        'detected_from': 'code_imports'
                    })
                    break
        
        return frameworks
    
    def _parse_dependencies(self) -> Dict[str, List[Dict[str, str]]]:
        """Parse dependency files"""
        dependencies = {
            'python': [],
            'javascript': [],
            'dotnet': []
        }
        
        # Python - requirements.txt
        requirements_file = self.project_path / 'requirements.txt'
        if requirements_file.exists():
            dependencies['python'] = self._parse_requirements_txt(requirements_file)
        
        # Python - Pipfile
        pipfile = self.project_path / 'Pipfile'
        if pipfile.exists():
            dependencies['python'].extend(self._parse_pipfile(pipfile))
        
        # JavaScript - package.json
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            dependencies['javascript'] = self._parse_package_json(package_json)
        
        # .NET - *.csproj
        for csproj in self.project_path.rglob('*.csproj'):
            dependencies['dotnet'].extend(self._parse_csproj(csproj))
        
        return dependencies
    
    def _parse_requirements_txt(self, file_path: Path) -> List[Dict[str, str]]:
        """Parse requirements.txt"""
        deps = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package==version or package>=version
                        match = re.match(r'^([a-zA-Z0-9_-]+)([>=<~!]=?)(.+)?$', line)
                        if match:
                            deps.append({
                                'name': match.group(1),
                                'version': match.group(3) if match.group(3) else 'latest',
                                'constraint': match.group(2) if match.group(2) else ''
                            })
                        else:
                            deps.append({'name': line, 'version': 'latest', 'constraint': ''})
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
        return deps
    
    def _parse_pipfile(self, file_path: Path) -> List[Dict[str, str]]:
        """Parse Pipfile"""
        deps = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple regex parsing (could use toml for better parsing)
                matches = re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', content)
                for name, version in matches:
                    deps.append({'name': name, 'version': version, 'constraint': '=='})
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
        return deps
    
    def _parse_package_json(self, file_path: Path) -> List[Dict[str, str]]:
        """Parse package.json"""
        deps = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for dep_type in ['dependencies', 'devDependencies']:
                    if dep_type in data:
                        for name, version in data[dep_type].items():
                            deps.append({
                                'name': name,
                                'version': version,
                                'constraint': '',
                                'type': dep_type
                            })
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
        return deps
    
    def _parse_csproj(self, file_path: Path) -> List[Dict[str, str]]:
        """Parse .csproj file"""
        deps = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract PackageReference
                matches = re.findall(r'<PackageReference Include="([^"]+)" Version="([^"]+)"', content)
                for name, version in matches:
                    deps.append({'name': name, 'version': version, 'constraint': ''})
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
        return deps
    
    def _detect_build_tools(self) -> List[str]:
        """Detect build tools and task runners"""
        tools = []
        
        tool_files = {
            'webpack': ['webpack.config.js'],
            'vite': ['vite.config.js', 'vite.config.ts'],
            'gulp': ['gulpfile.js'],
            'grunt': ['Gruntfile.js'],
            'make': ['Makefile'],
            'cmake': ['CMakeLists.txt'],
            'msbuild': ['*.sln'],
            'poetry': ['pyproject.toml'],
            'pipenv': ['Pipfile']
        }
        
        for tool, patterns in tool_files.items():
            for pattern in patterns:
                if list(self.project_path.glob(pattern)):
                    tools.append(tool)
                    break
        
        return tools
    
    def _detect_databases(self) -> List[str]:
        """Detect database technologies"""
        databases = []
        
        db_patterns = {
            'postgresql': ['psycopg2', 'postgres', 'pg'],
            'mysql': ['mysql', 'pymysql', 'mysqlclient'],
            'sqlite': ['sqlite3', 'sqlite'],
            'mongodb': ['pymongo', 'mongodb', 'mongoose'],
            'redis': ['redis', 'redis-py'],
            'sqlserver': ['pyodbc', 'mssql', 'sqlserver']
        }
        
        dependencies = self._parse_dependencies()
        all_deps = []
        for dep_list in dependencies.values():
            all_deps.extend([dep['name'].lower() for dep in dep_list])
        
        for db, patterns in db_patterns.items():
            if any(pattern in dep for dep in all_deps for pattern in patterns):
                databases.append(db)
        
        return databases
    
    def _detect_devops_tools(self) -> List[str]:
        """Detect DevOps tools and configurations"""
        tools = []
        
        devops_files = {
            'docker': ['Dockerfile', 'docker-compose.yml'],
            'kubernetes': ['*.yaml', '*.yml'] + ['k8s/'],
            'github-actions': ['.github/workflows/'],
            'gitlab-ci': ['.gitlab-ci.yml'],
            'jenkins': ['Jenkinsfile'],
            'terraform': ['*.tf'],
            'ansible': ['*.yml'] + ['playbook']
        }
        
        for tool, patterns in devops_files.items():
            for pattern in patterns:
                if '/' in pattern:
                    if (self.project_path / pattern).exists():
                        tools.append(tool)
                        break
                else:
                    if list(self.project_path.rglob(pattern)):
                        tools.append(tool)
                        break
        
        return tools
    
    def _calculate_statistics(self, tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall statistics"""
        return {
            'total_languages': len(tech_stack['languages']),
            'total_frameworks': len(tech_stack['frameworks']),
            'total_dependencies': sum(len(deps) for deps in tech_stack['dependencies'].values()),
            'total_build_tools': len(tech_stack['build_tools']),
            'primary_language': tech_stack['languages'][0]['name'] if tech_stack['languages'] else 'Unknown'
        }
    
    def _get_framework_category(self, framework: str) -> str:
        """Get category for framework"""
        categories = {
            'web': ['django', 'flask', 'fastapi', 'express', 'aspnet', 'blazor'],
            'frontend': ['react', 'vue', 'angular', 'next', 'nuxt'],
            'ml': ['pytorch', 'tensorflow', 'scikit-learn'],
            'data': ['pandas', 'numpy', 'sqlalchemy']
        }
        
        for category, frameworks in categories.items():
            if framework in frameworks:
                return category
        return 'other'
    
    def _should_count_file(self, file_path: Path) -> bool:
        """Check if file should be counted"""
        exclude_patterns = [
            '.git', '.venv', 'venv', 'node_modules', '__pycache__',
            'dist', 'build', '.pytest_cache', '.tox', 'htmlcov'
        ]
        
        path_str = str(file_path)
        return not any(pattern in path_str for pattern in exclude_patterns)


def generate_techstack_json(project_path: Path, output_path: Path) -> Dict[str, Any]:
    """
    Generate techstack.json for a project
    
    Args:
        project_path: Path to project to analyze
        output_path: Path to save techstack.json
        
    Returns:
        Tech stack data
    """
    analyzer = TechStackAnalyzer(project_path)
    tech_stack = analyzer.analyze()
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tech_stack, f, indent=2)
    
    logger.info(f"Tech stack analysis saved to {output_path}")
    return tech_stack
