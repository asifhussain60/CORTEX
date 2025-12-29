"""
Browser Cache Headers Utility

Provides HTTP cache headers for static dashboard assets to optimize
browser caching and reduce server load.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0

Cache Strategy:
- HTML: No-cache (always validate)
- CSS/JS: 1 hour cache with validation
- Images/UML: 24 hours cache
- Static assets: 7 days cache with versioning
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path


class BrowserCacheHeaders:
    """
    Generates HTTP cache headers for dashboard static assets.
    
    Implements best practices for browser caching:
    - Cache-Control directives for fine-grained control
    - ETags for validation caching
    - Last-Modified headers for conditional requests
    - Vary header for content negotiation
    """
    
    # Cache durations by content type
    CACHE_DURATIONS = {
        'html': 0,  # No cache for HTML (always validate)
        'css': 3600,  # 1 hour for CSS
        'js': 3600,  # 1 hour for JavaScript
        'svg': 86400,  # 24 hours for SVG diagrams
        'png': 86400,  # 24 hours for PNG images
        'json': 3600,  # 1 hour for JSON data
        'woff2': 604800,  # 7 days for fonts
    }
    
    @staticmethod
    def get_headers_for_file(file_path: Path) -> Dict[str, str]:
        """
        Generate cache headers for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of HTTP headers
        """
        extension = file_path.suffix.lstrip('.').lower()
        cache_duration = BrowserCacheHeaders.CACHE_DURATIONS.get(extension, 3600)
        
        headers = {}
        
        # Cache-Control header
        if cache_duration == 0:
            # HTML: No cache, always revalidate
            headers['Cache-Control'] = 'no-cache, must-revalidate'
        elif cache_duration < 3600:
            # Short cache: Public, with validation
            headers['Cache-Control'] = f'public, max-age={cache_duration}, must-revalidate'
        else:
            # Long cache: Public, immutable for versioned assets
            headers['Cache-Control'] = f'public, max-age={cache_duration}, immutable'
        
        # ETag for validation caching
        if file_path.exists():
            # Use file modification time and size for ETag
            stat = file_path.stat()
            etag = f'"{stat.st_mtime}-{stat.st_size}"'
            headers['ETag'] = etag
            
            # Last-Modified header
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            headers['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Vary header for content negotiation
        headers['Vary'] = 'Accept-Encoding'
        
        # Content-Type
        content_types = {
            'html': 'text/html; charset=utf-8',
            'css': 'text/css; charset=utf-8',
            'js': 'application/javascript; charset=utf-8',
            'json': 'application/json; charset=utf-8',
            'svg': 'image/svg+xml',
            'png': 'image/png',
            'woff2': 'font/woff2',
        }
        headers['Content-Type'] = content_types.get(extension, 'application/octet-stream')
        
        return headers
    
    @staticmethod
    def get_headers_for_dashboard_html() -> Dict[str, str]:
        """
        Get cache headers specifically for dashboard HTML.
        
        Dashboard HTML should never be cached as it may contain
        dynamic content and user-specific data.
        
        Returns:
            Dictionary of HTTP headers
        """
        return {
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Content-Type': 'text/html; charset=utf-8',
            'Vary': 'Accept-Encoding',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block',
        }
    
    @staticmethod
    def get_headers_for_api_response() -> Dict[str, str]:
        """
        Get cache headers for API/AJAX responses.
        
        API responses get short cache with validation to reduce
        server load while ensuring data freshness.
        
        Returns:
            Dictionary of HTTP headers
        """
        return {
            'Cache-Control': 'private, max-age=300, must-revalidate',  # 5 minutes
            'Content-Type': 'application/json; charset=utf-8',
            'Vary': 'Accept-Encoding',
            'X-Content-Type-Options': 'nosniff',
        }
    
    @staticmethod
    def get_headers_for_uml_diagram(last_generated: datetime) -> Dict[str, str]:
        """
        Get cache headers for generated UML diagrams.
        
        Args:
            last_generated: When the UML diagram was last generated
            
        Returns:
            Dictionary of HTTP headers
        """
        return {
            'Cache-Control': 'public, max-age=86400, immutable',  # 24 hours
            'Content-Type': 'image/svg+xml',
            'Last-Modified': last_generated.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Vary': 'Accept-Encoding',
        }
    
    @staticmethod
    def should_return_304(
        request_headers: Dict[str, str],
        file_path: Path
    ) -> bool:
        """
        Check if request can be satisfied with 304 Not Modified.
        
        Args:
            request_headers: Request headers from client
            file_path: Path to the file being requested
            
        Returns:
            True if 304 can be returned, False otherwise
        """
        if not file_path.exists():
            return False
        
        stat = file_path.stat()
        
        if_none_match = request_headers.get('If-None-Match', '')
        if if_none_match:
            current_etag = f'"{stat.st_mtime}-{stat.st_size}"'
            if if_none_match == current_etag:
                return True
        
        if_modified_since = request_headers.get('If-Modified-Since', '')
        if if_modified_since:
            try:
                request_time = datetime.strptime(
                    if_modified_since,
                    '%a, %d %b %Y %H:%M:%S GMT'
                )
                file_time = datetime.fromtimestamp(stat.st_mtime)
                if file_time <= request_time:
                    return True
            except ValueError:
                pass  # Invalid date format
        
        return False
    
    @staticmethod
    def add_security_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """
        Add security headers to response.
        
        Args:
            headers: Existing headers dictionary
            
        Returns:
            Headers with security additions
        """
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }
        
        return {**headers, **security_headers}


def generate_cache_headers(
    content_type: str,
    file_path: Optional[Path] = None,
    last_modified: Optional[datetime] = None
) -> Dict[str, str]:
    """
    Convenience function to generate cache headers.
    
    Args:
        content_type: Type of content ('html', 'css', 'js', 'svg', etc.)
        file_path: Optional path to file for ETag generation
        last_modified: Optional last modified timestamp
        
    Returns:
        Dictionary of HTTP headers
    """
    if content_type == 'dashboard_html':
        return BrowserCacheHeaders.get_headers_for_dashboard_html()
    elif content_type == 'api':
        return BrowserCacheHeaders.get_headers_for_api_response()
    elif content_type == 'uml' and last_modified:
        return BrowserCacheHeaders.get_headers_for_uml_diagram(last_modified)
    elif file_path:
        return BrowserCacheHeaders.get_headers_for_file(file_path)
    else:
        # Default: 1 hour cache with validation
        return {
            'Cache-Control': 'public, max-age=3600, must-revalidate',
            'Vary': 'Accept-Encoding',
        }
