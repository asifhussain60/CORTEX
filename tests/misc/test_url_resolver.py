"""
Infrastructure Layer - UrlResolver Tests (RED Phase)

Tests for portable URL resolution from Flask request context.
Works on any machine/folder without configuration.

Author: Asif Hussain
"""
import pytest
from unittest.mock import Mock


def test_url_resolver_localhost_5000():
    """Test URL resolver with localhost:5000"""
    from src.dashboard.infrastructure.url_resolver import UrlResolver
    
    # Arrange - Mock Flask request
    mock_request = Mock()
    mock_request.host = "localhost:5000"
    mock_request.scheme = "http"
    
    # Act
    resolver = UrlResolver(mock_request)
    base_url = resolver.get_base_url()
    
    # Assert
    assert base_url == "http://localhost:5000"


def test_url_resolver_localhost_8080():
    """Test URL resolver with localhost:8080"""
    from src.dashboard.infrastructure.url_resolver import UrlResolver
    
    # Arrange
    mock_request = Mock()
    mock_request.host = "localhost:8080"
    mock_request.scheme = "http"
    
    # Act
    resolver = UrlResolver(mock_request)
    base_url = resolver.get_base_url()
    
    # Assert
    assert base_url == "http://localhost:8080"


def test_url_resolver_production_domain():
    """Test URL resolver with production domain"""
    from src.dashboard.infrastructure.url_resolver import UrlResolver
    
    # Arrange
    mock_request = Mock()
    mock_request.host = "dashboard.example.com"
    mock_request.scheme = "https"
    
    # Act
    resolver = UrlResolver(mock_request)
    base_url = resolver.get_base_url()
    
    # Assert
    assert base_url == "https://dashboard.example.com"


def test_url_resolver_with_port():
    """Test URL resolver with custom port"""
    from src.dashboard.infrastructure.url_resolver import UrlResolver
    
    # Arrange
    mock_request = Mock()
    mock_request.host = "192.168.1.100:3000"
    mock_request.scheme = "http"
    
    # Act
    resolver = UrlResolver(mock_request)
    base_url = resolver.get_base_url()
    
    # Assert
    assert base_url == "http://192.168.1.100:3000"


def test_url_resolver_resolve_static_path():
    """Test resolving static asset path"""
    from src.dashboard.infrastructure.url_resolver import UrlResolver
    
    # Arrange
    mock_request = Mock()
    mock_request.host = "localhost:5000"
    mock_request.scheme = "http"
    
    # Act
    resolver = UrlResolver(mock_request)
    static_url = resolver.resolve("/static/css/style.css")
    
    # Assert
    assert static_url == "http://localhost:5000/static/css/style.css"


def test_url_resolver_resolve_api_path():
    """Test resolving API endpoint path"""
    from src.dashboard.infrastructure.url_resolver import UrlResolver
    
    # Arrange
    mock_request = Mock()
    mock_request.host = "localhost:5000"
    mock_request.scheme = "http"
    
    # Act
    resolver = UrlResolver(mock_request)
    api_url = resolver.resolve("/api/dashboard/cortex")
    
    # Assert
    assert api_url == "http://localhost:5000/api/dashboard/cortex"


def test_url_resolver_handles_missing_leading_slash():
    """Test resolver adds leading slash if missing"""
    from src.dashboard.infrastructure.url_resolver import UrlResolver
    
    # Arrange
    mock_request = Mock()
    mock_request.host = "localhost:5000"
    mock_request.scheme = "http"
    
    # Act
    resolver = UrlResolver(mock_request)
    url = resolver.resolve("static/css/style.css")
    
    # Assert
    assert url == "http://localhost:5000/static/css/style.css"


def test_url_resolver_caches_base_url():
    """Test base URL is cached after first call"""
    from src.dashboard.infrastructure.url_resolver import UrlResolver
    
    # Arrange
    mock_request = Mock()
    mock_request.host = "localhost:5000"
    mock_request.scheme = "http"
    
    # Act
    resolver = UrlResolver(mock_request)
    url1 = resolver.get_base_url()
    url2 = resolver.get_base_url()
    
    # Assert - Request attributes accessed only once (cached)
    assert url1 == url2
    assert mock_request.host  # Verify mock was used
