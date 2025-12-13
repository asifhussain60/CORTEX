"""
Repository Type Classifier

Detects repository type through file pattern analysis and AST validation.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Set, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class RepoTypeClassifier:
    """
    Classify repository type based on file patterns and structure
    
    Supports 6 repository types:
    - fullstack_web: Frontend + Backend + Database
    - api_service: REST/GraphQL endpoints
    - database_project: Schema, migrations, procedures
    - console_app: CLI commands, workflows
    - microservices: Distributed services, messaging
    - library_package: Exported APIs, no application entry
    """
    
    # Confidence thresholds
    THRESHOLDS = {
        'fullstack_web': 0.70,  # Requires 2/3 layers
        'api_service': 0.60,
        'database_project': 0.50,
        'console_app': 0.60,
        'microservices': 0.50,
        'library_package': 0.60
    }
    
    def __init__(self):
        """Initialize classifier with pattern definitions"""
        self.patterns = self._define_patterns()
    
    def classify(self, repo_path: Path) -> Dict[str, Any]:
        """
        Classify repository type
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            {
                'primary_type': str,
                'secondary_types': List[str],
                'confidence_scores': Dict[str, float],
                'dashboard_template': str,
                'detected_patterns': Dict[str, bool],
                'metadata': {...}
            }
        """
        logger.info(f"🔍 Classifying repository: {repo_path.name}")
        
        # Scan repository structure
        file_tree = self._scan_repository(repo_path)
        
        # Calculate confidence scores for each type
        scores = self._calculate_scores(file_tree)
        
        # Determine primary and secondary types
        primary_type = max(scores.items(), key=lambda x: x[1])[0]
        secondary_types = [
            repo_type for repo_type, score in scores.items()
            if score >= self.THRESHOLDS[repo_type] and repo_type != primary_type
        ]
        
        # Detect architectural patterns
        patterns = self._detect_patterns(file_tree)
        
        # Select dashboard template
        template = self._select_template(primary_type, patterns)
        
        result = {
            'primary_type': primary_type,
            'secondary_types': secondary_types,
            'confidence_scores': scores,
            'dashboard_template': template,
            'detected_patterns': patterns,
            'metadata': {
                'total_files': len(file_tree['all_files']),
                'languages': file_tree['languages'],
                'frameworks': file_tree['frameworks']
            }
        }
        
        logger.info(f"✅ Classified as: {primary_type} "
                   f"(confidence: {scores[primary_type]:.1%})")
        
        return result
    
    def _scan_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Scan repository and build file tree"""
        file_tree = {
            'all_files': [],
            'by_extension': defaultdict(list),
            'by_directory': defaultdict(list),
            'languages': defaultdict(int),
            'frameworks': set(),
            'special_files': set()
        }
        
        # Directories to exclude
        exclude_dirs = {
            '.git', '.svn', 'node_modules', '__pycache__',
            'bin', 'obj', 'dist', 'build', '.venv', 'venv',
            '.vs', '.vscode', '.idea'
        }
        
        for file_path in repo_path.rglob('*'):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            if file_path.is_file():
                file_tree['all_files'].append(file_path)
                
                # Group by extension
                ext = file_path.suffix.lower()
                if ext:
                    file_tree['by_extension'][ext].append(file_path)
                    
                    # Count languages
                    if ext in ['.py']:
                        file_tree['languages']['Python'] += 1
                    elif ext in ['.cs']:
                        file_tree['languages']['C#'] += 1
                    elif ext in ['.js', '.jsx']:
                        file_tree['languages']['JavaScript'] += 1
                    elif ext in ['.ts', '.tsx']:
                        file_tree['languages']['TypeScript'] += 1
                    elif ext in ['.sql']:
                        file_tree['languages']['SQL'] += 1
                
                # Detect frameworks and special files
                self._detect_frameworks(file_path, file_tree)
        
        return file_tree
    
    def _detect_frameworks(self, file_path: Path, file_tree: Dict):
        """Detect frameworks and special files"""
        name = file_path.name.lower()
        
        # Package managers
        if name in ['package.json', 'yarn.lock', 'package-lock.json']:
            file_tree['special_files'].add('npm')
            file_tree['frameworks'].add('Node.js')
        elif name in ['requirements.txt', 'pyproject.toml', 'poetry.lock']:
            file_tree['special_files'].add('python_package')
        elif name in ['*.csproj', '*.sln']:
            file_tree['special_files'].add('dotnet')
            file_tree['frameworks'].add('.NET')
        
        # Web frameworks
        if name in ['next.config.js', 'next.config.ts']:
            file_tree['frameworks'].add('Next.js')
        elif name in ['vite.config.js', 'vite.config.ts']:
            file_tree['frameworks'].add('Vite')
        elif name == 'angular.json':
            file_tree['frameworks'].add('Angular')
        
        # Backend frameworks
        if 'Startup.cs' in name or 'Program.cs' in name:
            file_tree['frameworks'].add('ASP.NET Core')
        elif 'app.py' in name or 'main.py' in name:
            if any('flask' in p.name.lower() for p in file_path.parent.rglob('*')):
                file_tree['frameworks'].add('Flask')
            elif any('fastapi' in p.name.lower() for p in file_path.parent.rglob('*')):
                file_tree['frameworks'].add('FastAPI')
        
        # Database
        if name.endswith('.sql'):
            file_tree['special_files'].add('sql_files')
        elif 'migration' in name:
            file_tree['special_files'].add('migrations')
        
        # Docker/K8s
        if name in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
            file_tree['special_files'].add('docker')
        elif name.endswith('.yaml') and 'k8s' in str(file_path):
            file_tree['special_files'].add('kubernetes')
    
    def _calculate_scores(self, file_tree: Dict) -> Dict[str, float]:
        """Calculate confidence scores for each repo type"""
        scores = {
            'fullstack_web': 0.0,
            'api_service': 0.0,
            'database_project': 0.0,
            'console_app': 0.0,
            'microservices': 0.0,
            'library_package': 0.0
        }
        
        special_files = file_tree['special_files']
        frameworks = file_tree['frameworks']
        languages = file_tree['languages']
        
        # Full-Stack Web
        has_frontend = 'npm' in special_files and any(f in frameworks for f in ['React', 'Next.js', 'Angular', 'Vue'])
        has_backend = any(f in frameworks for f in ['ASP.NET Core', 'Flask', 'FastAPI'])
        has_database = 'sql_files' in special_files or 'migrations' in special_files
        
        if has_frontend:
            scores['fullstack_web'] += 0.35
        if has_backend:
            scores['fullstack_web'] += 0.35
        if has_database:
            scores['fullstack_web'] += 0.30
        
        # API Service
        if has_backend and not has_frontend:
            scores['api_service'] += 0.50
        if 'Controller' in str(file_tree['all_files']):
            scores['api_service'] += 0.30
        if any('swagger' in str(f).lower() for f in file_tree['all_files']):
            scores['api_service'] += 0.20
        
        # Database Project
        sql_count = len(file_tree['by_extension'].get('.sql', []))
        if sql_count > 10:
            scores['database_project'] += 0.50
        if 'migrations' in special_files:
            scores['database_project'] += 0.30
        if sql_count > 0 and not has_backend:
            scores['database_project'] += 0.20
        
        # Console App
        if 'Program.cs' in str(file_tree['all_files']) and not has_frontend and not has_backend:
            scores['console_app'] += 0.60
        if any('CommandLine' in str(f) for f in file_tree['all_files']):
            scores['console_app'] += 0.40
        
        # Microservices
        if 'docker' in special_files:
            scores['microservices'] += 0.30
        if 'kubernetes' in special_files:
            scores['microservices'] += 0.40
        if any('messagebus' in str(f).lower() or 'eventbus' in str(f).lower() 
               for f in file_tree['all_files']):
            scores['microservices'] += 0.30
        
        # Library/Package
        if 'python_package' in special_files and not any(
            'app' in str(f).lower() or 'main' in str(f).lower() 
            for f in file_tree['all_files']
        ):
            scores['library_package'] += 0.60
        if any('__init__.py' in str(f) for f in file_tree['all_files']):
            scores['library_package'] += 0.40
        
        return scores
    
    def _detect_patterns(self, file_tree: Dict) -> Dict[str, bool]:
        """Detect architectural patterns"""
        special_files = file_tree['special_files']
        
        return {
            'has_frontend': 'npm' in special_files,
            'has_backend': any(f in file_tree['frameworks'] for f in ['ASP.NET Core', 'Flask', 'FastAPI']),
            'has_database': 'sql_files' in special_files or 'migrations' in special_files,
            'has_messaging': any('messagebus' in str(f).lower() for f in file_tree['all_files']),
            'has_containerization': 'docker' in special_files or 'kubernetes' in special_files,
            'has_tests': any('test' in str(f).lower() for f in file_tree['all_files']),
            'has_ci_cd': any('.github' in str(f) or '.gitlab-ci' in str(f) 
                           for f in file_tree['all_files'])
        }
    
    def _select_template(self, primary_type: str, patterns: Dict[str, bool]) -> str:
        """Select appropriate dashboard template"""
        templates = {
            'fullstack_web': 'fullstack-web-dashboard',
            'api_service': 'api-service-dashboard',
            'database_project': 'database-schema-dashboard',
            'console_app': 'console-app-dashboard',
            'microservices': 'microservices-dashboard',
            'library_package': 'library-documentation-dashboard'
        }
        
        return templates.get(primary_type, 'fullstack-web-dashboard')
    
    def _define_patterns(self) -> Dict[str, Any]:
        """Define file patterns for classification"""
        # This will be expanded as needed
        return {}
