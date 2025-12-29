"""
Repository Interface - Data Layer Contract

Defines interface for data access following Dependency Inversion Principle.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from src.dashboard.domain import Component, Dependency, Issue, HealthScore


class IComponentRepository(ABC):
    """Interface for component data access"""
    
    @abstractmethod
    def get_all(self) -> List[Component]:
        """Get all components"""
        pass
    
    @abstractmethod
    def get_by_path(self, path: str) -> Optional[Component]:
        """Get component by path"""
        pass
    
    @abstractmethod
    def get_by_health_category(self, category: str) -> List[Component]:
        """Get components by health category (healthy/warning/critical)"""
        pass
    
    @abstractmethod
    def save(self, component: Component) -> None:
        """Save component"""
        pass


class IDependencyRepository(ABC):
    """Interface for dependency data access"""
    
    @abstractmethod
    def get_all(self) -> List[Dependency]:
        """Get all dependencies"""
        pass
    
    @abstractmethod
    def get_by_source(self, source: str) -> List[Dependency]:
        """Get dependencies from a source component"""
        pass
    
    @abstractmethod
    def get_by_target(self, target: str) -> List[Dependency]:
        """Get dependencies to a target component"""
        pass
    
    @abstractmethod
    def get_circular(self) -> List[Dependency]:
        """Get circular dependencies"""
        pass
    
    @abstractmethod
    def save(self, dependency: Dependency) -> None:
        """Save dependency"""
        pass


class IIssueRepository(ABC):
    """Interface for issue data access"""
    
    @abstractmethod
    def get_all(self) -> List[Issue]:
        """Get all issues"""
        pass
    
    @abstractmethod
    def get_by_component(self, component_path: str) -> List[Issue]:
        """Get issues for a specific component"""
        pass
    
    @abstractmethod
    def get_by_severity(self, severity: str) -> List[Issue]:
        """Get issues by severity"""
        pass
    
    @abstractmethod
    def get_security_issues(self) -> List[Issue]:
        """Get security-related issues"""
        pass
    
    @abstractmethod
    def save(self, issue: Issue) -> None:
        """Save issue"""
        pass


class IHealthScoreRepository(ABC):
    """Interface for health score data access"""
    
    @abstractmethod
    def get_system_health(self) -> HealthScore:
        """Get overall system health score"""
        pass
    
    @abstractmethod
    def get_component_health(self, component_path: str) -> Optional[HealthScore]:
        """Get health score for specific component"""
        pass
    
    @abstractmethod
    def save(self, health_score: HealthScore) -> None:
        """Save health score"""
        pass
