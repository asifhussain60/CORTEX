"""
Presentation Layer - Flask Application

Flask app factory with dependency injection for Clean Architecture.
Routes orchestrate use cases without containing business logic.

Author: Asif Hussain
"""
from flask import Flask, request, jsonify, render_template
from pathlib import Path

from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository
from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
from src.dashboard.infrastructure.url_resolver import UrlResolver
from src.dashboard.application.use_cases.load_dashboard import LoadDashboardUseCase
from src.dashboard.application.use_cases.refresh_dashboard import RefreshDashboardUseCase
from src.dashboard.application.dtos.load_dashboard_dto import LoadDashboardRequest
from src.dashboard.application.dtos.refresh_dashboard_dto import RefreshDashboardRequest


def create_app(dashboard_base_path: Path, app_registry_db_path: Path) -> Flask:
    """
    Create Flask application with dependency injection.
    
    Args:
        dashboard_base_path: Path to dashboard JSON files
        app_registry_db_path: Path to SQLite app registry database
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Initialize repositories (Infrastructure Layer)
    dashboard_repo = JsonDashboardRepository(base_path=dashboard_base_path)
    app_repo = SqliteAppRepository(db_path=app_registry_db_path)
    
    # Initialize use cases (Application Layer)
    load_dashboard_use_case = LoadDashboardUseCase(dashboard_repo)
    refresh_dashboard_use_case = RefreshDashboardUseCase(dashboard_repo)
    
    @app.route('/')
    def index():
        """Display CORTEX dashboard"""
        return get_dashboard('cortex')
    
    @app.route('/<app_id>')
    def get_dashboard(app_id: str):
        """
        Display dashboard for specific app.
        
        Args:
            app_id: Application identifier
            
        Returns:
            HTML dashboard or 404
        """
        try:
            # Execute use case
            request_dto = LoadDashboardRequest(app_id=app_id)
            response_dto = load_dashboard_use_case.execute(request_dto)
            
            # Create URL resolver
            url_resolver = UrlResolver(request)
            
            # Render template with dashboard data
            return render_template(
                'base.html',
                app_id=response_dto.app_id,
                app_name=response_dto.app_name,
                tabs=response_dto.data.tabs,
                metadata=response_dto.data.metadata
            ), 200
        except FileNotFoundError:
            return "Dashboard not found", 404
        except Exception as e:
            return f"Error: {str(e)}", 500
    
    @app.route('/refresh/<app_id>', methods=['POST'])
    def refresh_dashboard(app_id: str):
        """
        Refresh dashboard data.
        
        Args:
            app_id: Application identifier
            
        Returns:
            JSON response with refresh status
        """
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
                "refresh_time": response_dto.refresh_time.isoformat()
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    return app
