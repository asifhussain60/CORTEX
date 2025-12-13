"""
Architecture Collector

Detects architectural patterns, layers, and dependencies in repositories.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Set
from collections import defaultdict
from .base import BaseCollector

logger = logging.getLogger(__name__)


class ArchitectureCollector(BaseCollector):
    """
    Collect architecture and layer information
    
    Detects:
    - Architectural layers (presentation, business, data)
    - Common patterns (MVC, Clean Architecture, Hexagonal)
    - Module dependencies
    - Entry points
    - Service boundaries
    """
    
    # Layer detection patterns by directory name
    LAYER_PATTERNS = {
        'presentation': [
            'frontend', 'web', 'ui', 'views', 'pages', 'components',
            'controllers', 'api', 'endpoints', 'routes', 'handlers'
        ],
        'business': [
            'services', 'business', 'domain', 'core', 'application',
            'use_cases', 'usecases', 'logic', 'managers', 'handlers'
        ],
        'data': [
            'data', 'repositories', 'dal', 'database', 'persistence',
            'models', 'entities', 'db', 'storage', 'cache'
        ],
        'infrastructure': [
            'infrastructure', 'infra', 'config', 'configuration',
            'utilities', 'utils', 'helpers', 'common', 'shared'
        ],
        'tests': [
            'tests', 'test', 'spec', 'specs', '__tests__', 'testing'
        ]
    }
    
    # Architecture pattern indicators
    ARCHITECTURE_PATTERNS = {
        'clean_architecture': {
            'indicators': ['domain', 'application', 'infrastructure', 'presentation'],
            'description': 'Clean Architecture (Onion/Hexagonal)',
            'min_match': 3
        },
        'mvc': {
            'indicators': ['models', 'views', 'controllers'],
            'description': 'Model-View-Controller',
            'min_match': 2
        },
        'mvvm': {
            'indicators': ['models', 'views', 'viewmodels'],
            'description': 'Model-View-ViewModel',
            'min_match': 2
        },
        'layered': {
            'indicators': ['presentation', 'business', 'data'],
            'description': 'Traditional N-Tier/Layered',
            'min_match': 2
        },
        'microservices': {
            'indicators': ['services', 'api', 'gateway', 'docker'],
            'description': 'Microservices Architecture',
            'min_match': 2
        },
        'modular': {
            'indicators': ['modules', 'plugins', 'extensions'],
            'description': 'Modular/Plugin Architecture',
            'min_match': 1
        }
    }
    
    # Technology-specific entry points
    ENTRY_POINT_PATTERNS = {
        'python': ['main.py', 'app.py', '__main__.py', 'wsgi.py', 'asgi.py', 'manage.py'],
        'csharp': ['Program.cs', 'Startup.cs', 'App.xaml.cs'],
        'javascript': ['index.js', 'main.js', 'app.js', 'server.js'],
        'typescript': ['index.ts', 'main.ts', 'app.ts', 'server.ts']
    }
    
    @property
    def name(self) -> str:
        return 'architecture'
    
    @property
    def description(self) -> str:
        return 'Detects architectural patterns, layers, and dependencies'
    
    @property
    def required_for(self) -> list:
        return ['fullstack_web', 'api_service', 'console_app', 'microservices']
    
    def collect(
        self,
        repo_path: Path,
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect architecture information
        
        Args:
            repo_path: Repository root
            classification: Classification results from classifier
            
        Returns:
            {
                'layers': [...],
                'detected_pattern': {...},
                'entry_points': [...],
                'dependencies': [...],
                'metrics': {...}
            }
        """
        logger.info("Collecting architecture information...")
        
        # Scan directory structure
        directories = self._scan_directories(repo_path)
        
        # Detect layers
        layers = self._detect_layers(repo_path, directories)
        
        # Detect architectural pattern
        detected_pattern = self._detect_pattern(directories)
        
        # Find entry points
        entry_points = self._find_entry_points(repo_path)
        
        # Analyze module dependencies
        dependencies = self._analyze_dependencies(layers)
        
        # Calculate metrics
        metrics = self._calculate_metrics(layers, dependencies)
        
        result = {
            'layers': layers,
            'detected_pattern': detected_pattern,
            'entry_points': entry_points,
            'dependencies': dependencies,
            'metrics': metrics,
            'directory_structure': self._get_top_level_structure(repo_path)
        }
        
        logger.info(f"✅ Architecture collected: {len(layers)} layers, "
                   f"pattern: {detected_pattern.get('name', 'unknown')}")
        
        return result
    
    def collect_safe(
        self,
        repo_path: Path,
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Safe wrapper for collect with error handling"""
        try:
            return self.collect(repo_path, classification)
        except Exception as e:
            logger.error(f"Architecture collection failed: {e}")
            return {
                'layers': [],
                'detected_pattern': {'name': 'unknown', 'confidence': 0},
                'entry_points': [],
                'dependencies': [],
                'metrics': {},
                'error': str(e)
            }
    
    def _scan_directories(self, repo_path: Path) -> Set[str]:
        """Get all directory names in repo"""
        directories = set()
        
        for item in repo_path.rglob('*'):
            if item.is_dir():
                # Skip hidden directories and common non-source dirs
                if item.name.startswith('.') or item.name in [
                    'node_modules', '__pycache__', 'venv', '.venv', 
                    'bin', 'obj', 'dist', 'build', 'target'
                ]:
                    continue
                directories.add(item.name.lower())
        
        return directories
    
    def _detect_layers(
        self,
        repo_path: Path,
        directories: Set[str]
    ) -> List[Dict[str, Any]]:
        """Detect architectural layers"""
        layers = []
        
        for layer_name, patterns in self.LAYER_PATTERNS.items():
            matched_dirs = []
            
            for pattern in patterns:
                if pattern in directories:
                    matched_dirs.append(pattern)
            
            if matched_dirs:
                # Find the actual paths for these directories
                layer_paths = []
                for dir_name in matched_dirs:
                    for item in repo_path.rglob(dir_name):
                        if item.is_dir() and item.name.lower() == dir_name:
                            layer_paths.append(str(item.relative_to(repo_path)))
                
                # Count files in layer
                file_count = 0
                loc = 0
                for layer_path in layer_paths:
                    full_path = repo_path / layer_path
                    if full_path.exists():
                        for f in full_path.rglob('*'):
                            if f.is_file() and f.suffix in ['.py', '.cs', '.js', '.ts', '.java']:
                                file_count += 1
                                try:
                                    loc += len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
                                except:
                                    pass
                
                layers.append({
                    'name': layer_name.title(),
                    'detected_directories': matched_dirs,
                    'paths': layer_paths[:5],  # Limit to 5 paths
                    'file_count': file_count,
                    'loc': loc,
                    'confidence': min(len(matched_dirs) * 25, 100)
                })
        
        return sorted(layers, key=lambda x: x['confidence'], reverse=True)
    
    def _detect_pattern(self, directories: Set[str]) -> Dict[str, Any]:
        """Detect the most likely architectural pattern"""
        best_match = {
            'name': 'unknown',
            'description': 'No clear architectural pattern detected',
            'confidence': 0,
            'matched_indicators': []
        }
        
        for pattern_name, pattern_info in self.ARCHITECTURE_PATTERNS.items():
            matched = []
            for indicator in pattern_info['indicators']:
                if indicator.lower() in directories:
                    matched.append(indicator)
            
            if len(matched) >= pattern_info['min_match']:
                confidence = (len(matched) / len(pattern_info['indicators'])) * 100
                
                if confidence > best_match['confidence']:
                    best_match = {
                        'name': pattern_name,
                        'description': pattern_info['description'],
                        'confidence': round(confidence, 1),
                        'matched_indicators': matched
                    }
        
        return best_match
    
    def _find_entry_points(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Find application entry points"""
        entry_points = []
        
        for language, filenames in self.ENTRY_POINT_PATTERNS.items():
            for filename in filenames:
                for match in repo_path.rglob(filename):
                    if match.is_file():
                        entry_points.append({
                            'file': str(match.relative_to(repo_path)),
                            'language': language,
                            'type': self._classify_entry_point(filename)
                        })
        
        return entry_points[:20]  # Limit to 20 entry points
    
    def _classify_entry_point(self, filename: str) -> str:
        """Classify the type of entry point"""
        filename_lower = filename.lower()
        
        if 'main' in filename_lower or 'program' in filename_lower:
            return 'application_start'
        elif 'wsgi' in filename_lower or 'asgi' in filename_lower:
            return 'web_server'
        elif 'app' in filename_lower:
            return 'application'
        elif 'server' in filename_lower:
            return 'server'
        elif 'manage' in filename_lower:
            return 'cli_management'
        elif 'startup' in filename_lower:
            return 'configuration'
        else:
            return 'unknown'
    
    def _analyze_dependencies(
        self,
        layers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze dependencies between layers"""
        dependencies = []
        
        # Standard layer dependency assumptions
        layer_deps = {
            'Presentation': ['Business', 'Infrastructure'],
            'Business': ['Data', 'Infrastructure'],
            'Data': ['Infrastructure'],
            'Tests': ['Presentation', 'Business', 'Data']
        }
        
        layer_names = {l['name'] for l in layers}
        
        for from_layer, to_layers in layer_deps.items():
            if from_layer in layer_names:
                for to_layer in to_layers:
                    if to_layer in layer_names:
                        dependencies.append({
                            'from': from_layer,
                            'to': to_layer,
                            'type': 'dependency',
                            'inferred': True
                        })
        
        return dependencies
    
    def _calculate_metrics(
        self,
        layers: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate architecture metrics"""
        total_loc = sum(l.get('loc', 0) for l in layers)
        total_files = sum(l.get('file_count', 0) for l in layers)
        
        return {
            'layer_count': len(layers),
            'total_loc_in_layers': total_loc,
            'total_files_in_layers': total_files,
            'dependency_count': len(dependencies),
            'coupling_score': self._calculate_coupling(dependencies, len(layers)),
            'modularity_grade': self._grade_modularity(layers, dependencies)
        }
    
    def _calculate_coupling(
        self,
        dependencies: List[Dict[str, Any]],
        layer_count: int
    ) -> float:
        """Calculate coupling score (0-100, lower is better)"""
        if layer_count <= 1:
            return 0.0
        
        max_deps = layer_count * (layer_count - 1)  # Maximum possible dependencies
        actual_deps = len(dependencies)
        
        if max_deps == 0:
            return 0.0
        
        return round((actual_deps / max_deps) * 100, 1)
    
    def _grade_modularity(
        self,
        layers: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]]
    ) -> str:
        """Grade the overall modularity"""
        layer_count = len(layers)
        dep_count = len(dependencies)
        
        # More layers with reasonable dependencies = better modularity
        if layer_count >= 4 and dep_count <= layer_count * 2:
            return 'A - Highly Modular'
        elif layer_count >= 3 and dep_count <= layer_count * 3:
            return 'B - Well Structured'
        elif layer_count >= 2:
            return 'C - Moderate Structure'
        else:
            return 'D - Needs Improvement'
    
    def _get_top_level_structure(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Get top-level directory structure"""
        structure = []
        
        for item in sorted(repo_path.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                structure.append({
                    'name': item.name,
                    'type': 'directory',
                    'child_count': sum(1 for _ in item.iterdir() if not _.name.startswith('.'))
                })
            elif item.is_file() and not item.name.startswith('.'):
                structure.append({
                    'name': item.name,
                    'type': 'file',
                    'extension': item.suffix
                })
        
        return structure[:30]  # Limit to 30 items
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate collected data structure"""
        required_keys = ['layers', 'detected_pattern', 'entry_points']
        return all(key in data for key in required_keys)
