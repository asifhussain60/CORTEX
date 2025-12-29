"""
ApplicationRepository Interface

Abstract repository for application registry storage.
Defines contract - implementations in infrastructure layer.

This is the "Port" in Ports and Adapters (Hexagonal Architecture).
Domain layer defines the interface, infrastructure layer implements it.

Author: Asif Hussain
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.dashboard.domain.entities.application import Application


class ApplicationRepository(ABC):
    """
    Abstract repository for application registry.
    
    This interface defines the contract for managing registered applications.
    Concrete implementations live in the infrastructure layer (e.g., SqliteApplicationRepository).
    
    Methods:
        get_all: Retrieve all registered applications
        get_by_id: Retrieve specific application
        register: Register new application
        exists: Check if application is registered
    """
    
    @abstractmethod
    def get_all(self) -> List[Application]:
        """
        Retrieve all registered applications.
        
        Returns:
            List of Application entities
        """
        pass
    
    @abstractmethod
    def get_by_id(self, app_id: str) -> Optional[Application]:
        """
        Retrieve specific application by ID.
        
        Args:
            app_id: Unique application identifier
        
        Returns:
            Application entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def register(self, app: Application) -> None:
        """
        Register new application.
        
        Args:
            app: Application entity to register
        """
        pass
    
    @abstractmethod
    def exists(self, app_id: str) -> bool:
        """
        Check if application is registered.
        
        Args:
            app_id: Unique application identifier
        
        Returns:
            True if application is registered, False otherwise
        """
        pass
