"""
Application registry domain entities.

Provides Application entity and ApplicationRegistry domain service
for managing multiple dashboard applications in a multi-tenant dashboard system.

This module implements the Domain layer of Clean Architecture, containing
pure business logic with no infrastructure dependencies.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


# Validation constants
APP_ID_PATTERN = r'^[a-zA-Z0-9\-]+$'
APP_ID_MAX_LENGTH = 50
APP_NAME_MAX_LENGTH = 100


@dataclass(frozen=True)
class Application:
    """
    Represents a dashboard application in the multi-app system.
    
    Immutable entity that holds application metadata. The frozen dataclass
    ensures thread-safety and prevents accidental modification.
    
    Attributes:
        id: Unique identifier (alphanumeric + hyphens, max 50 chars)
        name: Short name for internal use
        display_name: Human-readable name for UI
        dashboard_path: File system path to dashboard data
        is_active: Whether application is currently enabled
        metadata: Optional dict for extensibility (version, repo_url, etc.)
    """
    id: str
    name: str
    display_name: str
    dashboard_path: str
    is_active: bool
    metadata: Optional[Dict] = field(default=None)
    
    def __post_init__(self):
        """
        Validate application data after initialization.
        
        Raises:
            ValueError: If validation fails for any field
        """
        self._validate_id()
        self._validate_name()
    
    def _validate_id(self) -> None:
        """Validate application ID format and constraints."""
        if not self.id or not self.id.strip():
            raise ValueError("Application ID cannot be empty")
        
        if len(self.id) > APP_ID_MAX_LENGTH:
            raise ValueError(f"Application ID exceeds {APP_ID_MAX_LENGTH} characters")
        
        if not re.match(APP_ID_PATTERN, self.id):
            raise ValueError("Application ID must be alphanumeric with hyphens only")
    
    def _validate_name(self) -> None:
        """Validate application name."""
        if not self.name or not self.name.strip():
            raise ValueError("Application name cannot be empty")
        
        if len(self.name) > APP_NAME_MAX_LENGTH:
            raise ValueError(f"Application name exceeds {APP_NAME_MAX_LENGTH} characters")


class ApplicationRegistry:
    """
    Domain service for managing the application registry.
    
    Provides CRUD operations for applications with validation,
    sorting, and filtering capabilities. This is a domain service
    (not a repository) as it operates purely in memory on domain entities.
    
    Thread-safety: Not thread-safe. Wrap with locks if used in concurrent context.
    """
    
    def __init__(self):
        """Initialize empty application registry."""
        self._applications: Dict[str, Application] = {}
    
    def register(self, app: Application) -> None:
        """
        Register a new application.
        
        Args:
            app: Application entity to register
            
        Raises:
            ValueError: If application ID already exists
        """
        if app.id in self._applications:
            raise ValueError(
                f"Application {app.id} already registered. "
                f"Use update() to modify existing applications."
            )
        
        self._applications[app.id] = app
    
    def unregister(self, app_id: str) -> None:
        """
        Unregister an application by removing it from the registry.
        
        Args:
            app_id: Application ID to remove
            
        Note:
            Silently succeeds if app_id doesn't exist (idempotent operation)
        """
        self._applications.pop(app_id, None)
    
    def update(self, app: Application) -> None:
        """
        Update an existing application or add if not present.
        
        This is an upsert operation - creates if missing, updates if exists.
        
        Args:
            app: Application entity with updated data
        """
        self._applications[app.id] = app
    
    def get(self, app_id: str) -> Optional[Application]:
        """
        Get application by ID.
        
        Args:
            app_id: Application ID to retrieve
            
        Returns:
            Application entity or None if not found
        """
        return self._applications.get(app_id)
    
    def get_all(self) -> List[Application]:
        """
        Get all applications sorted by name.
        
        Returns:
            List of Application entities sorted alphabetically by name.
            Empty list if no applications registered.
        """
        return self._sorted_by_name(self._applications.values())
    
    def get_active(self) -> List[Application]:
        """
        Get only active applications.
        
        Returns:
            List of active Application entities sorted alphabetically by name.
            Empty list if no active applications.
        """
        active_apps = [app for app in self._applications.values() if app.is_active]
        return self._sorted_by_name(active_apps)
    
    @staticmethod
    def _sorted_by_name(apps) -> List[Application]:
        """
        Sort applications alphabetically by name (case-insensitive).
        
        Args:
            apps: Iterable of Application entities
            
        Returns:
            Sorted list of applications
        """
        return sorted(apps, key=lambda a: a.name.lower())
