"""
UrlResolver - Portable URL Resolution

Dynamically resolves base URLs from Flask request context.
Works on any machine/folder without configuration.

Author: Asif Hussain
"""
from typing import Optional


class UrlResolver:
    """Resolves URLs portably from Flask request context"""
    
    def __init__(self, request):
        """
        Initialize with Flask request object.
        
        Args:
            request: Flask request object with scheme and host attributes
        """
        self._request = request
        self._cached_base_url: Optional[str] = None
    
    def get_base_url(self) -> str:
        """
        Get base URL from request context.
        
        Returns:
            Base URL (e.g., "http://localhost:5000")
        """
        if self._cached_base_url is None:
            self._cached_base_url = f"{self._request.scheme}://{self._request.host}"
        
        return self._cached_base_url
    
    def resolve(self, path: str) -> str:
        """
        Resolve full URL for given path.
        
        Args:
            path: Path to resolve (e.g., "/static/css/style.css")
            
        Returns:
            Full URL (e.g., "http://localhost:5000/static/css/style.css")
        """
        base = self.get_base_url()
        
        # Ensure path starts with /
        if not path.startswith('/'):
            path = f"/{path}"
        
        return f"{base}{path}"
