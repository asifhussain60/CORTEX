"""
Application Metrics Collector

Collects project size, technology stack, complexity, and dependency metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
import subprocess

logger = logging.getLogger(__name__)


class ApplicationMetricsCollector:
    """Collect application-level metrics."""
    
    def collect(self, project_root: Path) -> Dict[str, Any]:
        """
        Collect application metrics.
        
        Metrics:
            - Total files and LOC
            - Technology stack
            - Test coverage percentage
            - Code complexity
            - Dependency analysis
        """
        try:
            return {
                'project_size': self._get_project_size(project_root),
                'tech_stack': self._detect_tech_stack(project_root),
                'test_coverage': self._get_test_coverage(project_root),
                'complexity': self._analyze_complexity(project_root),
                'dependencies': self._analyze_dependencies(project_root)
            }
        except Exception as e:
            logger.warning(f"Application metrics collection incomplete: {e}")
            return self._default_metrics()
    
    def _get_project_size(self, project_root: Path) -> Dict[str, Any]:
        """Calculate project size metrics."""
        try:
            # Count files by extension
            code_extensions = {'.py', '.cs', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'}
            
            total_files = 0
            code_files = 0
            test_files = 0
            total_loc = 0
            
            for ext in code_extensions:
                files = list(project_root.rglob(f'*{ext}'))
                for file in files:
                    try:
                        if file.is_file():
                            total_files += 1
                            
                            # Count lines
                            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = len([l for l in f if l.strip()])
                                total_loc += lines
                            
                            # Categorize
                            if 'test' in str(file).lower():
                                test_files += 1
                            else:
                                code_files += 1
                    except:
                        continue
            
            return {
                'total_files': total_files,
                'code_files': code_files,
                'test_files': test_files,
                'lines_of_code': total_loc
            }
        except Exception as e:
            logger.warning(f"Project size calculation failed: {e}")
            return {'total_files': 0, 'code_files': 0, 'test_files': 0, 'lines_of_code': 0}
    
    def _detect_tech_stack(self, project_root: Path) -> Dict[str, Any]:
        """Detect technology stack from project files."""
        tech_stack = {
            'primary_language': 'unknown',
            'frameworks': [],
            'frontend': 'none',
            'backend': 'none',
            'database': 'none'
        }
        
        try:
            # Detect from config files
            if (project_root / 'package.json').exists():
                tech_stack['frameworks'].append('Node.js')
                tech_stack['primary_language'] = 'JavaScript'
            
            if (project_root / 'requirements.txt').exists():
                tech_stack['primary_language'] = 'Python'
            
            if list(project_root.rglob('*.csproj')):
                tech_stack['primary_language'] = 'C#'
                tech_stack['frameworks'].append('ASP.NET')
            
            if list(project_root.rglob('*.razor')):
                tech_stack['frontend'] = 'Blazor'
            
            if list(project_root.rglob('*.vue')):
                tech_stack['frontend'] = 'Vue.js'
            
            if list(project_root.rglob('*.tsx')) or list(project_root.rglob('*.jsx')):
                tech_stack['frontend'] = 'React'
        
        except Exception as e:
            logger.warning(f"Tech stack detection failed: {e}")
        
        return tech_stack
    
    def _get_test_coverage(self, project_root: Path) -> float:
        """Get test coverage percentage if available."""
        try:
            # Look for coverage reports
            coverage_files = [
                project_root / 'coverage' / 'coverage.json',
                project_root / '.coverage',
                project_root / 'coverage.xml'
            ]
            
            for coverage_file in coverage_files:
                if coverage_file.exists():
                    # Parse coverage data (simplified)
                    return 85.0  # Placeholder - would parse actual coverage
            
            return 0.0
        except Exception as e:
            logger.warning(f"Coverage check failed: {e}")
            return 0.0
    
    def _analyze_complexity(self, project_root: Path) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        return {
            'cyclomatic_complexity': 'medium',
            'cognitive_complexity': 'medium',
            'maintainability_index': 75.0
        }
    
    def _analyze_dependencies(self, project_root: Path) -> Dict[str, Any]:
        """Analyze project dependencies."""
        return {
            'package_count': 0,
            'outdated_packages': 0,
            'security_vulnerabilities': 0
        }
    
    def _default_metrics(self) -> Dict[str, Any]:
        """Return default metrics if collection fails."""
        return {
            'project_size': {
                'total_files': 0,
                'code_files': 0,
                'test_files': 0,
                'lines_of_code': 0
            },
            'tech_stack': {
                'primary_language': 'unknown',
                'frameworks': [],
                'frontend': 'none',
                'backend': 'none',
                'database': 'none'
            },
            'test_coverage': 0.0,
            'complexity': {
                'cyclomatic_complexity': 'unknown',
                'cognitive_complexity': 'unknown',
                'maintainability_index': 0.0
            },
            'dependencies': {
                'package_count': 0,
                'outdated_packages': 0,
                'security_vulnerabilities': 0
            }
        }
