"""
Dashboard Data Adapter - JSON-based Repository Implementation

Implements repository interfaces using JSON file storage.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
import logging

from src.dashboard.data.repository_interface import (
    IComponentRepository,
    IDependencyRepository,
    IIssueRepository,
    IHealthScoreRepository
)
from src.dashboard.domain import (
    Component,
    Dependency,
    Issue,
    HealthScore,
    IssueSeverity
)

logger = logging.getLogger(__name__)


class JSONComponentRepository(IComponentRepository):
    """JSON-based component repository"""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self._cache: Optional[Dict] = None
    
    def _load_data(self) -> Dict:
        """Load data from JSON file with caching"""
        if self._cache is None:
            if self.data_file.exists() and self.data_file.stat().st_size > 0:
                try:
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        self._cache = json.load(f)
                except json.JSONDecodeError:
                    self._cache = {'components': []}
            else:
                self._cache = {'components': []}
        return self._cache
    
    def get_all(self) -> List[Component]:
        """Get all components"""
        data = self._load_data()
        return [Component.from_dict(c) for c in data.get('components', [])]
    
    def get_by_path(self, path: str) -> Optional[Component]:
        """Get component by path"""
        components = self.get_all()
        for component in components:
            if component.path == path:
                return component
        return None
    
    def get_by_health_category(self, category: str) -> List[Component]:
        """Get components by health category"""
        components = self.get_all()
        return [c for c in components if c.health_category == category]
    
    def save(self, component: Component) -> None:
        """Save component"""
        data = self._load_data()
        components = data.get('components', [])
        
        # Update existing or append new
        found = False
        for i, c in enumerate(components):
            if c['path'] == component.path:
                components[i] = component.to_dict()
                found = True
                break
        
        if not found:
            components.append(component.to_dict())
        
        data['components'] = components
        
        # Write to file
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        # Invalidate cache
        self._cache = None


class JSONDependencyRepository(IDependencyRepository):
    """JSON-based dependency repository"""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self._cache: Optional[Dict] = None
    
    def _load_data(self) -> Dict:
        """Load data from JSON file with caching"""
        if self._cache is None:
            if self.data_file.exists() and self.data_file.stat().st_size > 0:
                try:
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        self._cache = json.load(f)
                except json.JSONDecodeError:
                    self._cache = {'dependencies': []}
            else:
                self._cache = {'dependencies': []}
        return self._cache
    
    def get_all(self) -> List[Dependency]:
        """Get all dependencies"""
        data = self._load_data()
        return [Dependency.from_dict(d) for d in data.get('dependencies', [])]
    
    def get_by_source(self, source: str) -> List[Dependency]:
        """Get dependencies from a source component"""
        dependencies = self.get_all()
        return [d for d in dependencies if d.source == source]
    
    def get_by_target(self, target: str) -> List[Dependency]:
        """Get dependencies to a target component"""
        dependencies = self.get_all()
        return [d for d in dependencies if d.target == target]
    
    def get_circular(self) -> List[Dependency]:
        """Get circular dependencies"""
        dependencies = self.get_all()
        return [d for d in dependencies if d.is_circular]
    
    def save(self, dependency: Dependency) -> None:
        """Save dependency"""
        data = self._load_data()
        dependencies = data.get('dependencies', [])
        
        # Update existing or append new
        found = False
        for i, d in enumerate(dependencies):
            if d['edge_id'] == dependency.edge_id:
                dependencies[i] = dependency.to_dict()
                found = True
                break
        
        if not found:
            dependencies.append(dependency.to_dict())
        
        data['dependencies'] = dependencies
        
        # Write to file
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        # Invalidate cache
        self._cache = None


class JSONIssueRepository(IIssueRepository):
    """JSON-based issue repository"""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self._cache: Optional[Dict] = None
    
    def _load_data(self) -> Dict:
        """Load data from JSON file with caching"""
        if self._cache is None:
            if self.data_file.exists() and self.data_file.stat().st_size > 0:
                try:
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        self._cache = json.load(f)
                except json.JSONDecodeError:
                    self._cache = {'issues': []}
            else:
                self._cache = {'issues': []}
        return self._cache
    
    def get_all(self) -> List[Issue]:
        """Get all issues"""
        data = self._load_data()
        return [Issue.from_dict(i) for i in data.get('issues', [])]
    
    def get_by_component(self, component_path: str) -> List[Issue]:
        """Get issues for a specific component"""
        issues = self.get_all()
        return [i for i in issues if i.component_path == component_path]
    
    def get_by_severity(self, severity: str) -> List[Issue]:
        """Get issues by severity"""
        issues = self.get_all()
        severity_enum = IssueSeverity(severity)
        return [i for i in issues if i.severity == severity_enum]
    
    def get_security_issues(self) -> List[Issue]:
        """Get security-related issues"""
        issues = self.get_all()
        return [i for i in issues if i.is_security_issue]
    
    def save(self, issue: Issue) -> None:
        """Save issue"""
        data = self._load_data()
        issues = data.get('issues', [])
        
        # Update existing or append new
        found = False
        for i, iss in enumerate(issues):
            if iss['id'] == issue.id:
                issues[i] = issue.to_dict()
                found = True
                break
        
        if not found:
            issues.append(issue.to_dict())
        
        data['issues'] = issues
        
        # Write to file
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        # Invalidate cache
        self._cache = None


class JSONHealthScoreRepository(IHealthScoreRepository):
    """JSON-based health score repository"""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self._cache: Optional[Dict] = None
    
    def _load_data(self) -> Dict:
        """Load data from JSON file with caching"""
        if self._cache is None:
            if self.data_file.exists() and self.data_file.stat().st_size > 0:
                try:
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        self._cache = json.load(f)
                except json.JSONDecodeError:
                    self._cache = {'health_scores': {}}
            else:
                self._cache = {'health_scores': {}}
        return self._cache
    
    def get_system_health(self) -> HealthScore:
        """Get overall system health score"""
        data = self._load_data()
        system_health = data.get('health_scores', {}).get('system')
        
        if system_health:
            return HealthScore.from_dict(system_health)
        else:
            return HealthScore()
    
    def get_component_health(self, component_path: str) -> Optional[HealthScore]:
        """Get health score for specific component"""
        data = self._load_data()
        component_health = data.get('health_scores', {}).get(component_path)
        
        if component_health:
            return HealthScore.from_dict(component_health)
        return None
    
    def save(self, health_score: HealthScore) -> None:
        """Save health score"""
        data = self._load_data()
        
        if 'health_scores' not in data:
            data['health_scores'] = {}
        
        key = health_score.component_path or 'system'
        data['health_scores'][key] = health_score.to_dict()
        
        # Write to file
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        # Invalidate cache
        self._cache = None
