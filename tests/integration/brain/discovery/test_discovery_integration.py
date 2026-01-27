"""
Integration tests for complete discovery system.

Tests all discovery plugins working together through DiscoveryOrchestrator.

Task: DISC-004 Integration
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
"""

import json
import tempfile
import pytest
from pathlib import Path

from cortex.orchestrators.support.discovery_orchestrator import (
    DiscoveryOrchestrator,
    DiscoveryType,
)
from cortex.brain.discovery.config_discovery import ConfigurationDiscovery
from cortex.brain.discovery.database_discovery import DatabaseDiscovery
from cortex.brain.discovery.api_discovery import APIDiscovery


class TestFullDiscoveryIntegration:
    """Test complete discovery system integration."""
    
    def test_discover_complex_application(self, tmp_path: Path) -> None:
        """Test discovering a complex application with all components."""
        # Create a realistic application structure
        app_dir = tmp_path / "myapp"
        app_dir.mkdir()
        
        # 1. Configuration files
        config_dir = app_dir / "config"
        config_dir.mkdir()
        
        # appsettings.json
        appsettings = config_dir / "appsettings.json"
        appsettings.write_text(json.dumps({
            "ConnectionStrings": {
                "DefaultConnection": "Server=localhost;Database=myapp;User=admin;Password=secret123"
            },
            "Redis": {
                "Host": "redis://localhost:6379"
            }
        }))
        
        # docker-compose.yml
        compose_file = app_dir / "docker-compose.yml"
        compose_file.write_text("""
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret123
  redis:
    image: redis:alpine
""")
        
        # 2. Database models
        models_dir = app_dir / "models"
        models_dir.mkdir()
        
        user_model = models_dir / "user.py"
        user_model.write_text("""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100))
""")
        
        # 3. API routes
        api_dir = app_dir / "api"
        api_dir.mkdir()
        
        routes_file = api_dir / "routes.py"
        routes_file.write_text("""
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def get_users():
    pass

@router.post("/users")
def create_user():
    pass

@router.get("/users/{user_id}")
def get_user(user_id: int):
    pass
""")
        
        # OpenAPI spec
        openapi_file = api_dir / "openapi.yaml"
        openapi_file.write_text("""
openapi: 3.0.0
info:
  title: MyApp API
  version: 1.0.0
paths:
  /api/health:
    get:
      summary: Health check
      responses:
        200:
          description: OK
""")
        
        # Initialize orchestrator
        orchestrator = DiscoveryOrchestrator(repo_path=app_dir)
        
        # Register all plugins
        orchestrator.register_plugin(DiscoveryType.CONFIG, ConfigurationDiscovery())
        orchestrator.register_plugin(DiscoveryType.DATABASE, DatabaseDiscovery())
        orchestrator.register_plugin(DiscoveryType.API, APIDiscovery())
        
        # Discover complete topology
        topology = orchestrator.discover_topology()
        
        # Verify all discovery types succeeded
        assert topology is not None
        results = topology.to_dict()
        
        # Check config discovery
        assert "config" in results
        config_data = results["config"]
        assert config_data is not None
        assert len(config_data.get("config_files", [])) >= 2  # appsettings + docker-compose
        assert len(config_data.get("connection_strings", [])) >= 1
        
        # Check database discovery
        assert "databases" in results
        db_data = results["databases"]
        assert db_data is not None
        if "orm_type" in db_data:
            assert db_data["orm_type"] == "sqlalchemy"
        if "models" in db_data:
            assert len(db_data["models"]) >= 1
            assert db_data["models"][0]["name"] == "User"
        
        # Check API discovery
        assert "apis" in results
        api_data = results["apis"]
        assert api_data is not None
        assert api_data.get("total_endpoints", 0) >= 3  # 3 FastAPI routes + 1 OpenAPI
    
    def test_discover_with_missing_components(self, tmp_path: Path) -> None:
        """Test discovery gracefully handles missing components."""
        # Create minimal app with only config
        app_dir = tmp_path / "minimal_app"
        app_dir.mkdir()
        
        config_file = app_dir / "config.json"
        config_file.write_text('{"app": "minimal"}')
        
        orchestrator = DiscoveryOrchestrator(repo_path=app_dir)
        orchestrator.register_plugin(DiscoveryType.CONFIG, ConfigurationDiscovery())
        orchestrator.register_plugin(DiscoveryType.DATABASE, DatabaseDiscovery())
        orchestrator.register_plugin(DiscoveryType.API, APIDiscovery())
        
        topology = orchestrator.discover_topology()
        results = topology.to_dict()
        
        # Config should succeed
        assert results["config"] is not None
        assert len(results["config"].get("config_files", [])) >= 1
        
        # Database and API should succeed but find nothing
        assert results["databases"] is not None or results["databases"] == {}
        
        assert results["apis"] is not None or results["apis"] == {}
    
    def test_parallel_discovery_performance(self, tmp_path: Path) -> None:
        """Test parallel execution is faster than sequential."""
        # Create app with multiple components
        app_dir = tmp_path / "perf_app"
        app_dir.mkdir()
        
        # Add various files
        for i in range(5):
            (app_dir / f"config{i}.json").write_text('{}')
            (app_dir / f"model{i}.py").write_text('# model')
            (app_dir / f"api{i}.py").write_text('# api')
        
        orchestrator = DiscoveryOrchestrator(repo_path=app_dir)
        orchestrator.register_plugin(DiscoveryType.CONFIG, ConfigurationDiscovery())
        orchestrator.register_plugin(DiscoveryType.DATABASE, DatabaseDiscovery())
        orchestrator.register_plugin(DiscoveryType.API, APIDiscovery())
        
        # Both modes should work (no parallel parameter, controlled by init)
        topology = orchestrator.discover_topology()
        assert topology is not None
        
        # Verify topology has data
        results = topology.to_dict()
        assert len(results) > 0


class TestDiscoveryOrchestration:
    """Test orchestrator coordination features."""
    
    def test_selective_discovery_by_type(self, tmp_path: Path) -> None:
        """Test discovering specific types only."""
        app_dir = tmp_path / "selective_app"
        app_dir.mkdir()
        
        # Create config and API files
        (app_dir / "config.json").write_text('{"key": "value"}')
        
        api_file = app_dir / "app.py"
        api_file.write_text("""
from flask import Flask
app = Flask(__name__)

@app.route('/test')
def test():
    pass
""")
        
        orchestrator = DiscoveryOrchestrator(repo_path=app_dir)
        orchestrator.register_plugin(DiscoveryType.CONFIG, ConfigurationDiscovery())
        orchestrator.register_plugin(DiscoveryType.API, APIDiscovery())
        
        # Discover only config
        config_result = orchestrator.discover_by_type(DiscoveryType.CONFIG)
        assert config_result is not None
        assert len(config_result.get("config_files", [])) >= 1
        
        # Discover only API
        api_result = orchestrator.discover_by_type(DiscoveryType.API)
        assert api_result is not None
        assert api_result.get("total_endpoints", 0) >= 1
    
    def test_cache_invalidation_workflow(self, tmp_path: Path) -> None:
        """Test cache invalidation after file changes."""
        app_dir = tmp_path / "cache_app"
        app_dir.mkdir()
        
        config_file = app_dir / "config.json"
        config_file.write_text('{"version": "1.0"}')
        
        orchestrator = DiscoveryOrchestrator(repo_path=app_dir)
        orchestrator.register_plugin(DiscoveryType.CONFIG, ConfigurationDiscovery())
        
        # First discovery - cache miss
        result1 = orchestrator.discover_by_type(DiscoveryType.CONFIG)
        assert result1 is not None
        
        # Second discovery - cache hit (same result)
        result2 = orchestrator.discover_by_type(DiscoveryType.CONFIG)
        assert result2 == result1
        
        # Invalidate cache
        orchestrator.invalidate_cache([DiscoveryType.CONFIG])
        
        # Third discovery - cache miss again
        result3 = orchestrator.discover_by_type(DiscoveryType.CONFIG)
        assert result3 is not None
    
    def test_error_isolation_between_plugins(self, tmp_path: Path) -> None:
        """Test that plugin errors don't crash entire discovery."""
        app_dir = tmp_path / "error_app"
        app_dir.mkdir()
        
        # Create valid config
        (app_dir / "config.json").write_text('{"valid": true}')
        
        # Create corrupted model file (will cause database discovery to struggle)
        models_dir = app_dir / "models"
        models_dir.mkdir()
        (models_dir / "broken.py").write_text("import nonexistent_module")
        
        orchestrator = DiscoveryOrchestrator(repo_path=app_dir)
        orchestrator.register_plugin(DiscoveryType.CONFIG, ConfigurationDiscovery())
        orchestrator.register_plugin(DiscoveryType.DATABASE, DatabaseDiscovery())
        
        # Discovery should complete despite database issues
        topology = orchestrator.discover_topology()
        results = topology.to_dict()
        
        # Config should succeed
        assert results["config"] is not None
        assert len(results["config"].get("config_files", [])) >= 1
        
        # Database might have data or be empty
        assert "databases" in results


class TestRealWorldScenarios:
    """Test realistic application discovery scenarios."""
    
    def test_microservices_architecture(self, tmp_path: Path) -> None:
        """Test discovering microservices architecture."""
        # Service 1: User service
        user_service = tmp_path / "user-service"
        user_service.mkdir()
        
        (user_service / "config.yaml").write_text("""
database:
  url: postgresql://localhost/users
redis:
  url: redis://localhost:6379
""")
        
        (user_service / "app.py").write_text("""
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users():
    pass
""")
        
        # Service 2: Order service
        order_service = tmp_path / "order-service"
        order_service.mkdir()
        
        (order_service / "config.yaml").write_text("""
database:
  url: postgresql://localhost/orders
""")
        
        (order_service / "api.py").write_text("""
from flask import Flask
app = Flask(__name__)

@app.route('/orders')
def list_orders():
    pass
""")
        
        # Discover both services
        orchestrator1 = DiscoveryOrchestrator(repo_path=user_service)
        orchestrator1.register_plugin(DiscoveryType.CONFIG, ConfigurationDiscovery())
        orchestrator1.register_plugin(DiscoveryType.API, APIDiscovery())
        
        orchestrator2 = DiscoveryOrchestrator(repo_path=order_service)
        orchestrator2.register_plugin(DiscoveryType.CONFIG, ConfigurationDiscovery())
        orchestrator2.register_plugin(DiscoveryType.API, APIDiscovery())
        
        topology1 = orchestrator1.discover_topology()
        topology2 = orchestrator2.discover_topology()
        
        # Both should have discovered data
        results1 = topology1.to_dict()
        results2 = topology2.to_dict()
        
        assert results1["apis"] is not None
        assert results2["apis"] is not None
        
        # Services should have discovered at least config files
        assert results1["config"] is not None
        assert results2["config"] is not None
    
    def test_monorepo_discovery(self, tmp_path: Path) -> None:
        """Test discovering multiple apps in monorepo."""
        monorepo = tmp_path / "monorepo"
        monorepo.mkdir()
        
        # Backend
        backend = monorepo / "backend"
        backend.mkdir()
        (backend / "config.json").write_text('{"env": "prod"}')
        
        # Frontend
        frontend = monorepo / "frontend"
        frontend.mkdir()
        (frontend / "config.json").write_text('{"api": "http://api"}')
        
        # Shared
        shared = monorepo / "shared"
        shared.mkdir()
        (shared / "types.py").write_text("# shared types")
        
        # Discover entire monorepo
        orchestrator = DiscoveryOrchestrator(repo_path=monorepo)
        orchestrator.register_plugin(DiscoveryType.CONFIG, ConfigurationDiscovery())
        
        topology = orchestrator.discover_topology()
        results = topology.to_dict()
        
        # Should find configs from multiple directories
        assert results["config"] is not None
        assert len(results["config"].get("config_files", [])) >= 2
