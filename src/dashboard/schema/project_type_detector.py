"""
Project Type Detector

Automatically detects project type from dashboard data.
Determines what tabs and visualizations should be shown.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Dict, Any


class ProjectTypeDetector:
    """Detects project type from dashboard data"""
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize detector with dashboard data.
        
        Args:
            data: Dashboard data dictionary
        """
        self.data = data
        self._analyze()
    
    def _analyze(self):
        """Analyze data to detect project features"""
        # Check frontend
        frontend = self.data.get("frontend")
        self._has_frontend = (
            frontend is not None and
            isinstance(frontend, dict) and
            frontend.get("components_count", 0) > 0
        )
        
        # Check backend
        backend = self.data.get("backend")
        self._has_backend = (
            backend is not None and
            isinstance(backend, dict) and
            len(backend.get("endpoints", [])) > 0
        )
        
        # Check database
        database = self.data.get("database")
        self._has_database = (
            database is not None and
            isinstance(database, dict) and
            len(database.get("schema", {}).get("tables", [])) > 0
        )
        
        # Check architecture type
        architecture = self.data.get("architecture", {})
        self._arch_type = architecture.get("type", "unknown")
    
    def get_type(self) -> str:
        """
        Get project type classification.
        
        Returns:
            Project type string: full_stack, api, frontend, database, microservices, library, unknown
        """
        # Check for microservices first
        if self._arch_type == "microservices":
            return "microservices"
        
        # Check for full-stack
        if self._has_frontend and self._has_backend:
            return "full_stack"
        
        # Check for database-only
        if self._has_database and not self._has_frontend and not self._has_backend:
            return "database"
        
        # Check for API-only
        if self._has_backend and not self._has_frontend:
            return "api"
        
        # Check for frontend-only
        if self._has_frontend and not self._has_backend:
            return "frontend"
        
        # Check metadata for library indication
        metadata = self.data.get("metadata", {})
        if metadata.get("project_type") == "library":
            return "library"
        
        return "unknown"
    
    def has_frontend(self) -> bool:
        """Check if project has frontend components"""
        return self._has_frontend
    
    def has_backend(self) -> bool:
        """Check if project has backend/API"""
        return self._has_backend
    
    def has_database(self) -> bool:
        """Check if project has database schema"""
        return self._has_database
    
    def get_features(self) -> Dict[str, bool]:
        """
        Get all detected features.
        
        Returns:
            Dictionary of feature flags
        """
        return {
            "has_frontend": self._has_frontend,
            "has_backend": self._has_backend,
            "has_database": self._has_database,
            "is_microservices": self._arch_type == "microservices",
            "is_full_stack": self._has_frontend and self._has_backend
        }
