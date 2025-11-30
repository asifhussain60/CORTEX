"""
File Scanner Crawler

Analyzes project file structure and detects technology stack.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Set
from collections import defaultdict

from .base_crawler import BaseCrawler


class FileScannerCrawler(BaseCrawler):
    """
    Scans project files to analyze:
    - Total files, directories, lines of code
    - Programming languages (by extension)
    - Framework indicators
    - Project size classification
    """
    
    # File extensions to language mapping
    LANGUAGE_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.md': 'Markdown',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.json': 'JSON',
        '.html': 'HTML',
        '.css': 'CSS',
        '.sh': 'Shell',
        '.sql': 'SQL',
        '.txt': 'Text',
        '.xml': 'XML',
        '.toml': 'TOML',
        '.ini': 'INI',
        '.cs': 'C#',
        '.java': 'Java',
        '.go': 'Go',
        '.rs': 'Rust',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'C/C++ Header',
    }
    
    # Framework/tool indicators
    FRAMEWORK_INDICATORS = {
        'requirements.txt': 'Python (pip)',
        'pyproject.toml': 'Python (Poetry/setuptools)',
        'setup.py': 'Python Package',
        'package.json': 'Node.js',
        'Cargo.toml': 'Rust',
        'go.mod': 'Go',
        'pom.xml': 'Java (Maven)',
        'build.gradle': 'Java (Gradle)',
        'Gemfile': 'Ruby',
        'composer.json': 'PHP',
        'mkdocs.yml': 'MkDocs',
        'pytest.ini': 'pytest',
        '.eslintrc': 'ESLint',
        'tsconfig.json': 'TypeScript',
        'Dockerfile': 'Docker',
        'docker-compose.yml': 'Docker Compose',
        '.github/workflows': 'GitHub Actions',
    }
    
    # Directories to skip
    SKIP_DIRS = {
        '.git', '.venv', 'venv', 'node_modules', '__pycache__',
        '.pytest_cache', '.mypy_cache', 'dist', 'build',
        'site', '.tox', 'htmlcov', 'logs', 'archives',
        'backups', 'temp', 'tmp', '.idea', '.vscode'
    }
    
    def get_name(self) -> str:
        return "File Scanner"
    
    def crawl(self) -> Dict[str, Any]:
        """
        Scan project files and analyze structure.
        
        Returns:
            Dict containing file structure analysis
        """
        self.log_info("Starting file structure scan")
        
        stats = {
            'total_files': 0,
            'total_directories': 0,
            'total_lines': 0,
            'languages': defaultdict(lambda: {'files': 0, 'lines': 0}),
            'frameworks': [],
            'config_files': [],
            'architecture_pattern': None,
            'project_size': None,
        }
        
        # Scan directory tree
        for root, dirs, files in os.walk(self.project_root):
            # Filter out skip directories
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            
            # Count directories
            stats['total_directories'] += len(dirs)
            
            # Process files
            for file in files:
                file_path = Path(root) / file
                
                # Count file
                stats['total_files'] += 1
                
                # Detect language
                ext = file_path.suffix.lower()
                if ext in self.LANGUAGE_MAP:
                    language = self.LANGUAGE_MAP[ext]
                    stats['languages'][language]['files'] += 1
                    
                    # Count lines for text files
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            stats['languages'][language]['lines'] += lines
                            stats['total_lines'] += lines
                    except Exception as e:
                        self.log_warning(f"Could not read {file_path}: {e}")
                
                # Detect frameworks
                relative_path = str(file_path.relative_to(self.project_root))
                for indicator, framework in self.FRAMEWORK_INDICATORS.items():
                    if indicator in relative_path or file == indicator:
                        if framework not in stats['frameworks']:
                            stats['frameworks'].append(framework)
                            self.log_info(f"Detected framework: {framework}")
                
                # Track config files
                if ext in ['.yaml', '.yml', '.json', '.toml', '.ini', '.cfg']:
                    stats['config_files'].append(relative_path)
        
        # Convert defaultdict to regular dict for JSON serialization
        stats['languages'] = dict(stats['languages'])
        
        # Detect architecture pattern
        stats['architecture_pattern'] = self._detect_architecture()
        
        # Classify project size
        stats['project_size'] = self._classify_size(stats['total_files'], stats['total_lines'])
        
        self.log_info(
            f"Scan complete: {stats['total_files']} files, "
            f"{stats['total_lines']} lines, "
            f"{len(stats['languages'])} languages"
        )
        
        return {
            "success": True,
            "data": stats
        }
    
    def _detect_architecture(self) -> str:
        """
        Detect project architecture pattern based on directory structure.
        
        Returns:
            Architecture pattern name
        """
        project_path = Path(self.project_root)
        
        # Check for plugin architecture
        if (project_path / 'src' / 'plugins').exists():
            return "plugin-based"
        
        # Check for microservices
        if (project_path / 'services').exists():
            return "microservices"
        
        # Check for monorepo
        if (project_path / 'packages').exists() or (project_path / 'apps').exists():
            return "monorepo"
        
        # Check for standard Python package
        if (project_path / 'src').exists() and (project_path / 'tests').exists():
            return "standard-package"
        
        # Check for MVC
        if all((project_path / dir).exists() for dir in ['models', 'views', 'controllers']):
            return "mvc"
        
        return "custom"
    
    def _classify_size(self, total_files: int, total_lines: int) -> str:
        """
        Classify project size based on files and lines.
        
        Args:
            total_files: Total number of files
            total_lines: Total lines of code
            
        Returns:
            Size classification (small/medium/large/enterprise)
        """
        if total_files < 100 and total_lines < 10000:
            return "small"
        elif total_files < 500 and total_lines < 50000:
            return "medium"
        elif total_files < 2000 and total_lines < 200000:
            return "large"
        else:
            return "enterprise"
