"""
Presentation Layer - Flask Application

Flask app factory with dependency injection for Clean Architecture.
Routes orchestrate use cases without containing business logic.

Multi-app routing: /dashboard/<app_id> pattern with validation.

Author: Asif Hussain
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for
from pathlib import Path
import re

from src.dashboard.infrastructure.repositories.json_multi_app_repository import JsonMultiAppRepository
from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
from src.dashboard.infrastructure.url_resolver import UrlResolver
from src.dashboard.application.use_cases.load_dashboard import LoadDashboardUseCase
from src.dashboard.application.use_cases.refresh_dashboard import RefreshDashboardUseCase
from src.dashboard.application.dtos.load_dashboard_dto import LoadDashboardRequest
from src.dashboard.application.dtos.refresh_dashboard_dto import RefreshDashboardRequest


# Valid app_id pattern: alphanumeric and hyphens only
APP_ID_PATTERN = re.compile(r'^[a-zA-Z0-9\-]+$')
APP_ID_MAX_LENGTH = 50


def validate_app_id(app_id: str) -> bool:
    """
    Validate app_id format for security and consistency.
    
    Security requirements:
    - Prevents path traversal (no ../ or \\)
    - Prevents command injection (alphanumeric + hyphens only)
    - Limits length to prevent DoS attacks
    
    Args:
        app_id: Application identifier to validate
        
    Returns:
        True if valid format, False otherwise
        
    Examples:
        >>> validate_app_id("cortex")
        True
        >>> validate_app_id("my-app-123")
        True
        >>> validate_app_id("../malicious")
        False
        >>> validate_app_id("app@123")
        False
    """
    if not app_id or len(app_id) > APP_ID_MAX_LENGTH:
        return False
    return APP_ID_PATTERN.match(app_id) is not None


def create_app(dashboard_base_path: Path, app_registry_db_path: Path) -> Flask:
    """
    Create Flask application with dependency injection.
    
    Supports multi-application dashboard routing with /dashboard/<app_id> pattern.
    
    Args:
        dashboard_base_path: Path to dashboard data root (contains app subdirectories)
        app_registry_db_path: Path to SQLite app registry database
        
    Returns:
        Configured Flask application with multi-app routes
    """
    app = Flask(__name__)
    
    # Initialize repositories (Infrastructure Layer)
    dashboard_repo = JsonMultiAppRepository(root_path=str(dashboard_base_path))
    app_repo = SqliteAppRepository(db_path=app_registry_db_path)
    
    # Initialize use cases (Application Layer)
    load_dashboard_use_case = LoadDashboardUseCase(dashboard_repo)
    refresh_dashboard_use_case = RefreshDashboardUseCase(dashboard_repo)
    
    @app.route('/')
    def index():
        """Redirect to CORTEX dashboard."""
        return redirect(url_for('get_dashboard', app_id='cortex'))
    
    @app.route('/<app_id>')
    def legacy_route(app_id: str):
        """
        Legacy route for backward compatibility.
        Redirects /<app_id> to /dashboard/<app_id>.
        """
        return redirect(url_for('get_dashboard', app_id=app_id))
    
    @app.route('/dashboard/<app_id>')
    def get_dashboard(app_id: str):
        """
        Display dashboard for specific application.
        
        Multi-app support: Loads dashboard data from app-specific directory.
        
        Args:
            app_id: Application identifier (alphanumeric + hyphens)
            
        Returns:
            HTML dashboard, 400 for invalid ID, or 404 for not found
        """
        # Validate app_id format
        if not validate_app_id(app_id):
            return "Invalid application ID", 400
        
        try:
            # Execute use case
            request_dto = LoadDashboardRequest(app_id=app_id)
            response_dto = load_dashboard_use_case.execute(request_dto)
            
            # Create URL resolver
            url_resolver = UrlResolver(request)
            
            # Render template with dashboard data
            return render_template(
                'dashboard_clean.html',
                app_id=response_dto.app_id,
                app_name=response_dto.app_name,
                tabs=response_dto.data.tabs,
                metadata=response_dto.data.metadata
            ), 200
        except FileNotFoundError:
            return "Dashboard not found", 404
        except Exception as e:
            return f"Error: {str(e)}", 500
    
    @app.route('/dashboard/<app_id>/refresh', methods=['POST'])
    def refresh_dashboard(app_id: str):
        """
        Refresh dashboard data for specific application.
        
        Args:
            app_id: Application identifier
            
        Returns:
            JSON response with refresh status
        """
        # Validate app_id format
        if not validate_app_id(app_id):
            return jsonify({"success": False, "error": "Invalid application ID"}), 400
        
        try:
            # Get force parameter
            force = request.args.get('force', 'false').lower() == 'true'
            
            # Execute use case
            request_dto = RefreshDashboardRequest(app_id=app_id, force=force)
            response_dto = refresh_dashboard_use_case.execute(request_dto)
            
            return jsonify({
                "app_id": response_dto.app_id,
                "success": response_dto.success,
                "message": response_dto.message,
                "force": force,
                "refresh_time": response_dto.refresh_time.isoformat()
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    return app
