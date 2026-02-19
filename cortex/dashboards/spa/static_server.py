"""
SPA Static File Server.

Lightweight HTTP server for serving LENS Dashboard SPA locally with proper
MIME types and CORS headers for development.

Phase: 14 - LENS Dashboard
Task: 018 - SPA HTTP Static Server
"""

import http.server
import socketserver
from pathlib import Path
from typing import Dict, Optional

from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class SPAStaticServer(http.server.SimpleHTTPRequestHandler):
    """
    Enhanced static file server for SPA applications.

    Extends SimpleHTTPRequestHandler with:
    - Proper MIME type detection for modern web assets
    - CORS headers for local development
    - SPA routing (fallback to index.html)
    - Request logging
    - Security headers

    Attributes:
        root_dir: Root directory to serve files from
        enable_cors: Enable CORS headers for development
        logger: Audit logger for request tracking
    """

    # Additional MIME types for modern web assets
    MIME_TYPES: Dict[str, str] = {
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".json": "application/json",
        ".css": "text/css",
        ".html": "text/html",
        ".htm": "text/html",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".ico": "image/x-icon",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".eot": "application/vnd.ms-fontobject",
        ".map": "application/json",
    }

    root_dir: Optional[Path] = None
    enable_cors: bool = True
    logger: Optional[EnhancedAuditLogger] = None

    def __init__(self, *args, **kwargs) -> None:
        """Initialize handler with parent class."""
        super().__init__(*args, **kwargs)

    def end_headers(self) -> None:
        """
        Add custom headers before ending response.

        Adds:
        - CORS headers for local development
        - Security headers
        - Caching headers
        """
        # CORS headers for development
        if self.enable_cors:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header(
                "Access-Control-Allow-Methods", "GET, POST, OPTIONS"
            )
            self.send_header(
                "Access-Control-Allow-Headers", "Content-Type, Authorization"
            )

        # Security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")

        # Caching headers
        if self.path.endswith((".js", ".css", ".woff2", ".woff")):
            # Cache static assets for 1 hour
            self.send_header("Cache-Control", "public, max-age=3600")
        elif self.path.endswith(".html"):
            # Don't cache HTML to allow SPA updates
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")

        super().end_headers()

    def guess_type(self, path: str) -> str:
        """
        Guess MIME type for file with enhanced detection.

        Args:
            path: File path to check

        Returns:
            MIME type string
        """
        # Check custom MIME types first
        suffix = Path(path).suffix.lower()
        if suffix in self.MIME_TYPES:
            return self.MIME_TYPES[suffix]

        # Fall back to parent class
        return super().guess_type(path)

    def do_GET(self) -> None:
        """
        Handle GET requests with SPA routing support.

        For requests that don't match a file, serves index.html
        to support client-side routing.
        """
        # Try to serve the requested path
        path = self.translate_path(self.path)

        if Path(path).is_file():
            # File exists, serve it normally
            super().do_GET()
        elif Path(path).is_dir() and (Path(path) / "index.html").exists():
            # Directory with index.html, serve it
            super().do_GET()
        else:
            # File not found, check if we should serve index.html for SPA routing
            if self._should_fallback_to_index():
                self._serve_index()
            else:
                # Return 404
                super().do_GET()

    def do_OPTIONS(self) -> None:
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:
        """
        Log HTTP requests to audit logger.

        Args:
            format: Log format string
            *args: Format arguments
        """
        if self.logger:
            message = format % args
            self.logger.log_info(
                ac_id="SPA-SERVER",
                message=message,
                metadata={"path": self.path, "method": self.command},
            )
        else:
            super().log_message(format, *args)

    def _should_fallback_to_index(self) -> bool:
        """
        Check if request should fallback to index.html.

        Returns:
            True if should serve index.html, False otherwise
        """
        # Don't fallback for API requests
        if self.path.startswith("/api/"):
            return False

        # Don't fallback for static assets
        path = Path(self.path)
        if path.suffix in self.MIME_TYPES:
            return False

        # Don't fallback for special files
        if path.name in ["favicon.ico", "robots.txt", "sitemap.xml"]:
            return False

        # Fallback for everything else (SPA routes)
        return True

    def _serve_index(self) -> None:
        """Serve index.html for SPA routing."""
        # Update path to index.html
        original_path = self.path
        self.path = "/index.html"

        # Serve index.html
        super().do_GET()

        # Restore original path for logging
        self.path = original_path


def create_server(
    root_dir: Path,
    port: int = 8080,
    enable_cors: bool = True,
    logger: Optional[EnhancedAuditLogger] = None,
) -> socketserver.TCPServer:
    """
    Create configured SPA static server.

    Args:
        root_dir: Root directory to serve files from
        port: Port to listen on (default: 8080)
        enable_cors: Enable CORS headers (default: True)
        logger: Audit logger for request tracking

    Returns:
        Configured TCP server instance

    Example:
        >>> server = create_server(Path("./dist"), port=8080)
        >>> server.serve_forever()
    """
    # Configure handler class
    SPAStaticServer.root_dir = root_dir
    SPAStaticServer.enable_cors = enable_cors
    SPAStaticServer.logger = logger

    # Change to root directory
    import os

    os.chdir(root_dir)

    # Create server
    with socketserver.TCPServer(("", port), SPAStaticServer) as server:
        server.allow_reuse_address = True
        return server


def serve(
    root_dir: Path,
    port: int = 8080,
    enable_cors: bool = True,
    logger: Optional[EnhancedAuditLogger] = None,
) -> None:
    """
    Start SPA static server and serve until interrupted.

    Args:
        root_dir: Root directory to serve files from
        port: Port to listen on (default: 8080)
        enable_cors: Enable CORS headers (default: True)
        logger: Audit logger for request tracking

    Example:
        >>> serve(Path("./dist"), port=8080)
        Serving on http://localhost:8080
        ^C (Ctrl+C to stop)
    """
    server = create_server(root_dir, port, enable_cors, logger)

    print(f"Serving SPA from {root_dir}")
    print(f"Available at http://localhost:{port}")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
        print("Server stopped")


def serve_dashboard(
    port: int = 8080,
    enable_cors: bool = True,
    logger: Optional[EnhancedAuditLogger] = None,
) -> None:
    """
    Serve LENS Dashboard SPA.

    Convenience function for serving the dashboard from its default location.

    Args:
        port: Port to listen on (default: 8080)
        enable_cors: Enable CORS headers (default: True)
        logger: Audit logger for request tracking

    Example:
        >>> serve_dashboard(port=8080)
        Serving LENS Dashboard on http://localhost:8080
    """
    # Determine dashboard directory
    dashboard_dir = Path(__file__).parent.parent / "dashboard" / "dist"

    if not dashboard_dir.exists():
        raise FileNotFoundError(
            f"Dashboard directory not found: {dashboard_dir}\n"
            "Please build the dashboard first with: cortex dashboard build"
        )

    print("Starting LENS Dashboard...")
    serve(dashboard_dir, port, enable_cors, logger)
