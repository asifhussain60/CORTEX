"""
Tests for SPA Static Server.

Phase: 14 - LENS Dashboard
Task: 018 - SPA HTTP Static Server
"""

import http.server
import socketserver
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from cortex.visualization.spa.static_server import (
    SPAStaticServer,
    create_server,
    serve_dashboard,
)


class TestSPAStaticServer:
    """Test SPAStaticServer class."""

    def test_mime_types_defined(self) -> None:
        """Test MIME types mapping is defined."""
        assert ".js" in SPAStaticServer.MIME_TYPES
        assert ".css" in SPAStaticServer.MIME_TYPES
        assert ".html" in SPAStaticServer.MIME_TYPES
        assert ".json" in SPAStaticServer.MIME_TYPES
        assert ".svg" in SPAStaticServer.MIME_TYPES

    def test_mime_type_javascript(self) -> None:
        """Test JavaScript MIME type."""
        assert SPAStaticServer.MIME_TYPES[".js"] == "application/javascript"
        assert SPAStaticServer.MIME_TYPES[".mjs"] == "application/javascript"

    def test_mime_type_css(self) -> None:
        """Test CSS MIME type."""
        assert SPAStaticServer.MIME_TYPES[".css"] == "text/css"

    def test_mime_type_html(self) -> None:
        """Test HTML MIME type."""
        assert SPAStaticServer.MIME_TYPES[".html"] == "text/html"
        assert SPAStaticServer.MIME_TYPES[".htm"] == "text/html"

    def test_mime_type_json(self) -> None:
        """Test JSON MIME type."""
        assert SPAStaticServer.MIME_TYPES[".json"] == "application/json"

    def test_mime_type_fonts(self) -> None:
        """Test font MIME types."""
        assert SPAStaticServer.MIME_TYPES[".woff"] == "font/woff"
        assert SPAStaticServer.MIME_TYPES[".woff2"] == "font/woff2"
        assert SPAStaticServer.MIME_TYPES[".ttf"] == "font/ttf"

    def test_guess_type_custom(self) -> None:
        """Test custom MIME type guessing."""
        handler = self._create_handler()

        assert handler.guess_type("script.js") == "application/javascript"
        assert handler.guess_type("style.css") == "text/css"
        assert handler.guess_type("data.json") == "application/json"

    def test_guess_type_case_insensitive(self) -> None:
        """Test MIME type guessing is case insensitive."""
        handler = self._create_handler()

        assert handler.guess_type("script.JS") == "application/javascript"
        assert handler.guess_type("style.CSS") == "text/css"

    def test_should_fallback_to_index_api_request(self) -> None:
        """Test API requests don't fallback to index."""
        handler = self._create_handler()
        handler.path = "/api/v1/data"

        assert handler._should_fallback_to_index() is False

    def test_should_fallback_to_index_static_asset(self) -> None:
        """Test static assets don't fallback to index."""
        handler = self._create_handler()

        handler.path = "/static/app.js"
        assert handler._should_fallback_to_index() is False

        handler.path = "/styles/main.css"
        assert handler._should_fallback_to_index() is False

        handler.path = "/images/logo.png"
        assert handler._should_fallback_to_index() is False

    def test_should_fallback_to_index_special_files(self) -> None:
        """Test special files don't fallback to index."""
        handler = self._create_handler()

        handler.path = "/favicon.ico"
        assert handler._should_fallback_to_index() is False

        handler.path = "/robots.txt"
        assert handler._should_fallback_to_index() is False

        handler.path = "/sitemap.xml"
        assert handler._should_fallback_to_index() is False

    def test_should_fallback_to_index_spa_route(self) -> None:
        """Test SPA routes fallback to index."""
        handler = self._create_handler()

        handler.path = "/dashboard"
        assert handler._should_fallback_to_index() is True

        handler.path = "/user/profile"
        assert handler._should_fallback_to_index() is True

        handler.path = "/settings"
        assert handler._should_fallback_to_index() is True

    @patch.object(SPAStaticServer, "send_header")
    @patch.object(http.server.SimpleHTTPRequestHandler, "end_headers")
    def test_end_headers_cors_enabled(
        self, mock_super_end: Mock, mock_send_header: Mock
    ) -> None:
        """Test CORS headers are added when enabled."""
        handler = self._create_handler()
        handler.enable_cors = True

        handler.end_headers()

        # Verify CORS headers
        mock_send_header.assert_any_call(
            "Access-Control-Allow-Origin", "*"
        )
        mock_send_header.assert_any_call(
            "Access-Control-Allow-Methods", "GET, POST, OPTIONS"
        )

    @patch.object(SPAStaticServer, "send_header")
    @patch.object(http.server.SimpleHTTPRequestHandler, "end_headers")
    def test_end_headers_security_headers(
        self, mock_super_end: Mock, mock_send_header: Mock
    ) -> None:
        """Test security headers are added."""
        handler = self._create_handler()

        handler.end_headers()

        # Verify security headers
        mock_send_header.assert_any_call(
            "X-Content-Type-Options", "nosniff"
        )
        mock_send_header.assert_any_call("X-Frame-Options", "SAMEORIGIN")
        mock_send_header.assert_any_call(
            "X-XSS-Protection", "1; mode=block"
        )

    @patch.object(SPAStaticServer, "send_header")
    @patch.object(http.server.SimpleHTTPRequestHandler, "end_headers")
    def test_end_headers_caching_static_assets(
        self, mock_super_end: Mock, mock_send_header: Mock
    ) -> None:
        """Test caching headers for static assets."""
        handler = self._create_handler()

        handler.path = "/static/app.js"
        handler.end_headers()

        mock_send_header.assert_any_call(
            "Cache-Control", "public, max-age=3600"
        )

    @patch.object(SPAStaticServer, "send_header")
    @patch.object(http.server.SimpleHTTPRequestHandler, "end_headers")
    def test_end_headers_caching_html(
        self, mock_super_end: Mock, mock_send_header: Mock
    ) -> None:
        """Test caching headers for HTML files."""
        handler = self._create_handler()

        handler.path = "/index.html"
        handler.end_headers()

        mock_send_header.assert_any_call(
            "Cache-Control", "no-cache, no-store, must-revalidate"
        )

    @patch.object(SPAStaticServer, "send_response")
    @patch.object(SPAStaticServer, "end_headers")
    def test_do_options(
        self, mock_end_headers: Mock, mock_send_response: Mock
    ) -> None:
        """Test OPTIONS request handling."""
        handler = self._create_handler()

        handler.do_OPTIONS()

        mock_send_response.assert_called_once_with(200)
        mock_end_headers.assert_called_once()

    def test_log_message_with_logger(self) -> None:
        """Test logging with audit logger."""
        handler = self._create_handler()
        logger = MagicMock()
        handler.logger = logger
        handler.path = "/test"
        handler.command = "GET"

        handler.log_message("Test message %s", "arg")

        logger.log_info.assert_called_once()
        call_args = logger.log_info.call_args
        assert call_args[1]["ac_id"] == "SPA-SERVER"
        assert "Test message arg" in call_args[1]["message"]

    @patch.object(http.server.SimpleHTTPRequestHandler, "log_message")
    def test_log_message_without_logger(
        self, mock_super_log: Mock
    ) -> None:
        """Test logging without audit logger falls back to parent."""
        handler = self._create_handler()
        handler.logger = None

        handler.log_message("Test message")

        mock_super_log.assert_called_once_with("Test message")

    def _create_handler(self) -> SPAStaticServer:
        """
        Create handler instance for testing.

        Returns:
            SPAStaticServer instance with mocked request/client
        """
        # Create handler without invoking parent __init__ to avoid request parsing
        handler = SPAStaticServer.__new__(SPAStaticServer)
        handler.path = "/"
        handler.command = "GET"
        handler.enable_cors = True
        handler.logger = None

        return handler


class TestCreateServer:
    """Test create_server function."""

    @patch("cortex.visualization.spa.static_server.socketserver.TCPServer")
    @patch("os.chdir")
    def test_create_server_basic(
        self, mock_chdir: Mock, mock_tcp_server: Mock
    ) -> None:
        """Test creating basic server."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)
            port = 8080

            # Mock TCPServer context manager
            mock_server_instance = MagicMock()
            mock_tcp_server.return_value.__enter__.return_value = (
                mock_server_instance
            )

            from cortex.visualization.spa.static_server import create_server

            result = create_server(root_dir, port)

            # Verify directory change
            mock_chdir.assert_called_once_with(root_dir)

            # Verify TCPServer creation
            mock_tcp_server.assert_called_once()
            call_args = mock_tcp_server.call_args
            assert call_args[0][0] == ("", port)

    @patch("cortex.visualization.spa.static_server.socketserver.TCPServer")
    @patch("os.chdir")
    def test_create_server_with_logger(
        self, mock_chdir: Mock, mock_tcp_server: Mock
    ) -> None:
        """Test creating server with logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)
            logger = MagicMock()

            # Mock TCPServer
            mock_server_instance = MagicMock()
            mock_tcp_server.return_value.__enter__.return_value = (
                mock_server_instance
            )

            from cortex.visualization.spa.static_server import create_server

            create_server(root_dir, logger=logger)

            # Verify logger was set
            assert SPAStaticServer.logger == logger

    @patch("cortex.visualization.spa.static_server.socketserver.TCPServer")
    @patch("os.chdir")
    def test_create_server_custom_port(
        self, mock_chdir: Mock, mock_tcp_server: Mock
    ) -> None:
        """Test creating server with custom port."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)
            custom_port = 3000

            # Mock TCPServer
            mock_server_instance = MagicMock()
            mock_tcp_server.return_value.__enter__.return_value = (
                mock_server_instance
            )

            from cortex.visualization.spa.static_server import create_server

            create_server(root_dir, port=custom_port)

            # Verify port in TCPServer call
            call_args = mock_tcp_server.call_args
            assert call_args[0][0] == ("", custom_port)


class TestServeDashboard:
    """Test serve_dashboard function."""

    @patch("cortex.visualization.spa.static_server.serve")
    @patch("pathlib.Path.exists")
    def test_serve_dashboard_success(
        self, mock_exists: Mock, mock_serve: Mock
    ) -> None:
        """Test serving dashboard successfully."""
        mock_exists.return_value = True

        serve_dashboard(port=8080)

        mock_serve.assert_called_once()
        call_args = mock_serve.call_args
        # Check positional argument (dashboard_dir path)
        assert call_args[0][0].name == "dist"
        # Check keyword arguments
        assert call_args[0][1] == 8080  # port

    @patch("pathlib.Path.exists")
    def test_serve_dashboard_not_found(self, mock_exists: Mock) -> None:
        """Test serving dashboard when directory doesn't exist."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as exc_info:
            serve_dashboard()

        assert "Dashboard directory not found" in str(exc_info.value)
        assert "cortex dashboard build" in str(exc_info.value)

    @patch("cortex.visualization.spa.static_server.serve")
    @patch("pathlib.Path.exists")
    def test_serve_dashboard_custom_port(
        self, mock_exists: Mock, mock_serve: Mock
    ) -> None:
        """Test serving dashboard with custom port."""
        mock_exists.return_value = True
        custom_port = 3000

        serve_dashboard(port=custom_port)

        call_args = mock_serve.call_args
        assert call_args[0][1] == custom_port

    @patch("cortex.visualization.spa.static_server.serve")
    @patch("pathlib.Path.exists")
    def test_serve_dashboard_with_logger(
        self, mock_exists: Mock, mock_serve: Mock
    ) -> None:
        """Test serving dashboard with logger."""
        mock_exists.return_value = True
        logger = MagicMock()

        serve_dashboard(logger=logger)

        call_args = mock_serve.call_args
        assert call_args[0][3] == logger  # logger is 4th positional arg
