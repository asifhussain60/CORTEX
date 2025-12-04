"""Naming exception manager tests (smoke tests)."""

import pytest


class TestNamingExceptionManager:
    """Test naming exception manager."""
    
    def test_manager_exists(self):
        """Should have NamingExceptionManager class."""
        from src.governance.naming_exception_manager import NamingExceptionManager
        
        manager = NamingExceptionManager()
        assert manager is not None
    
    def test_can_check_exceptions(self):
        """Should check if file is exception."""
        from src.governance.naming_exception_manager import NamingExceptionManager
        
        manager = NamingExceptionManager()
        
        assert manager.is_exception("LICENSE") is True
        assert manager.is_exception("VERSION") is True
        assert manager.is_exception("userService.py") is False
