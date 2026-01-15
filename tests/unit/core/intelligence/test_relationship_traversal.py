# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-001-04 - Relationship Traversal Engine Tests
"""
Tests for Relationship Traversal Engine.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-04 - Relationship Traversal Engine

Tests cover:
- API endpoint relationships
- Database schema relationships
- Configuration references
- Cross-file dependency tracking
- Impact analysis
"""

import textwrap
from pathlib import Path
from typing import Any, Dict, List, Set

import pytest


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def api_endpoint_code() -> str:
    """Python code with API endpoint definitions."""
    return textwrap.dedent('''
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/api/users', methods=['GET'])
        def list_users():
            """List all users."""
            return jsonify(users=[])
        
        @app.route('/api/users/<int:user_id>', methods=['GET'])
        def get_user(user_id):
            """Get a specific user."""
            return jsonify(user={})
        
        @app.route('/api/users', methods=['POST'])
        def create_user():
            """Create a new user."""
            data = request.json
            return jsonify(user=data), 201
        
        @app.route('/api/orders/<int:order_id>', methods=['GET', 'PUT', 'DELETE'])
        def manage_order(order_id):
            """Manage a specific order."""
            pass
    ''')


@pytest.fixture
def fastapi_endpoint_code() -> str:
    """Python code with FastAPI endpoint definitions."""
    return textwrap.dedent('''
        from fastapi import FastAPI, APIRouter
        
        app = FastAPI()
        router = APIRouter(prefix="/api/v2")
        
        @router.get("/products")
        async def list_products():
            """List products."""
            return []
        
        @router.post("/products")
        async def create_product(product: dict):
            """Create product."""
            return product
        
        app.include_router(router)
    ''')


@pytest.fixture
def database_model_code() -> str:
    """Python code with database model definitions."""
    return textwrap.dedent('''
        from sqlalchemy import Column, Integer, String, ForeignKey
        from sqlalchemy.orm import relationship
        from database import Base
        
        class User(Base):
            __tablename__ = 'users'
            
            id = Column(Integer, primary_key=True)
            name = Column(String(100))
            email = Column(String(255), unique=True)
            orders = relationship("Order", back_populates="user")
        
        class Order(Base):
            __tablename__ = 'orders'
            
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey('users.id'))
            status = Column(String(50))
            user = relationship("User", back_populates="orders")
            items = relationship("OrderItem", back_populates="order")
        
        class OrderItem(Base):
            __tablename__ = 'order_items'
            
            id = Column(Integer, primary_key=True)
            order_id = Column(Integer, ForeignKey('orders.id'))
            product_id = Column(Integer, ForeignKey('products.id'))
            order = relationship("Order", back_populates="items")
    ''')


@pytest.fixture
def config_reference_code() -> str:
    """Python code with configuration references."""
    return textwrap.dedent('''
        import os
        from config import settings
        
        DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
        DEBUG = settings.DEBUG
        SECRET_KEY = settings.SECRET_KEY
        
        class AppConfig:
            API_RATE_LIMIT = settings.get('api.rate_limit', 100)
            CACHE_TTL = os.getenv('CACHE_TTL', 3600)
            LOG_LEVEL = os.environ['LOG_LEVEL']
    ''')


@pytest.fixture
def multi_file_project(tmp_path: Path) -> Dict[str, Path]:
    """Create a multi-file project for relationship analysis."""
    files = {}
    
    # models.py
    models = tmp_path / "models.py"
    models.write_text(textwrap.dedent('''
        from database import session
        
        class User:
            def save(self):
                session.add(self)
                session.commit()
        
        class Order:
            user_id: int
            
            def get_user(self):
                from models import User
                return session.query(User).get(self.user_id)
    '''))
    files['models'] = models
    
    # api.py
    api = tmp_path / "api.py"
    api.write_text(textwrap.dedent('''
        from flask import Flask
        from models import User, Order
        from services import UserService
        
        app = Flask(__name__)
        
        @app.route('/users')
        def list_users():
            return UserService.get_all_users()
    '''))
    files['api'] = api
    
    # services.py
    services = tmp_path / "services.py"
    services.write_text(textwrap.dedent('''
        from models import User, Order
        from cache import cache
        
        class UserService:
            @staticmethod
            def get_all_users():
                return User.query.all()
            
            @staticmethod
            def get_user_orders(user_id):
                return Order.query.filter_by(user_id=user_id).all()
    '''))
    files['services'] = services
    
    return files


# =============================================================================
# TEST CLASSES: API ENDPOINT DETECTION
# =============================================================================


class TestAPIEndpointRelationships:
    """Tests for API endpoint relationship detection."""

    def test_detect_flask_routes(self, api_endpoint_code: str) -> None:
        """Test detection of Flask route endpoints."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(api_endpoint_code)
        
        endpoints = result.api_endpoints
        assert len(endpoints) >= 4
        
        # Check for specific endpoints
        routes = [e.path for e in endpoints]
        assert '/api/users' in routes
        assert '/api/users/<int:user_id>' in routes

    def test_detect_http_methods(self, api_endpoint_code: str) -> None:
        """Test detection of HTTP methods for endpoints."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(api_endpoint_code)
        
        # Find the orders endpoint
        orders_endpoint = next(
            (e for e in result.api_endpoints if 'order_id' in e.path),
            None
        )
        assert orders_endpoint is not None
        assert set(orders_endpoint.methods) == {'GET', 'PUT', 'DELETE'}

    def test_detect_fastapi_routes(self, fastapi_endpoint_code: str) -> None:
        """Test detection of FastAPI route endpoints."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(fastapi_endpoint_code)
        
        endpoints = result.api_endpoints
        assert len(endpoints) >= 2
        
        # Check for prefix handling
        routes = [e.path for e in endpoints]
        assert any('/products' in r for r in routes)


# =============================================================================
# TEST CLASSES: DATABASE SCHEMA RELATIONSHIPS
# =============================================================================


class TestDatabaseSchemaRelationships:
    """Tests for database schema relationship detection."""

    def test_detect_sqlalchemy_models(self, database_model_code: str) -> None:
        """Test detection of SQLAlchemy model definitions."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(database_model_code)
        
        models = result.database_models
        assert len(models) >= 3
        
        model_names = [m.name for m in models]
        assert 'User' in model_names
        assert 'Order' in model_names
        assert 'OrderItem' in model_names

    def test_detect_foreign_keys(self, database_model_code: str) -> None:
        """Test detection of foreign key relationships."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(database_model_code)
        
        # Find Order model
        order_model = next(
            (m for m in result.database_models if m.name == 'Order'),
            None
        )
        assert order_model is not None
        
        # Check foreign key
        assert 'users.id' in [fk.reference for fk in order_model.foreign_keys]

    def test_detect_relationships(self, database_model_code: str) -> None:
        """Test detection of ORM relationships."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(database_model_code)
        
        # Find User model
        user_model = next(
            (m for m in result.database_models if m.name == 'User'),
            None
        )
        assert user_model is not None
        
        # Check relationship
        rel_targets = [r.target for r in user_model.relationships]
        assert 'Order' in rel_targets


# =============================================================================
# TEST CLASSES: CONFIGURATION REFERENCES
# =============================================================================


class TestConfigurationReferences:
    """Tests for configuration reference detection."""

    def test_detect_env_variables(self, config_reference_code: str) -> None:
        """Test detection of environment variable references."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(config_reference_code)
        
        env_vars = result.env_references
        env_names = [e.name for e in env_vars]
        
        assert 'DATABASE_URL' in env_names
        assert 'CACHE_TTL' in env_names
        assert 'LOG_LEVEL' in env_names

    def test_detect_settings_access(self, config_reference_code: str) -> None:
        """Test detection of settings module access."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(config_reference_code)
        
        settings_refs = result.config_references
        setting_names = [s.key for s in settings_refs]
        
        assert 'DEBUG' in setting_names
        assert 'SECRET_KEY' in setting_names


# =============================================================================
# TEST CLASSES: CROSS-FILE DEPENDENCIES
# =============================================================================


class TestCrossFileDependencies:
    """Tests for cross-file dependency tracking."""

    def test_track_import_dependencies(
        self, multi_file_project: Dict[str, Path]
    ) -> None:
        """Test tracking of import dependencies across files."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_directory(multi_file_project['api'].parent)
        
        # api.py should depend on models.py and services.py
        api_deps = result.get_file_dependencies(str(multi_file_project['api']))
        
        dep_sources = [d.source_module for d in api_deps]
        assert 'models' in dep_sources

    def test_build_dependency_graph(
        self, multi_file_project: Dict[str, Path]
    ) -> None:
        """Test building a complete dependency graph."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_directory(multi_file_project['api'].parent)
        
        graph = result.dependency_graph
        assert graph is not None
        
        # Should have at least 3 files
        assert len(graph.nodes) >= 3


# =============================================================================
# TEST CLASSES: IMPACT ANALYSIS
# =============================================================================


class TestImpactAnalysis:
    """Tests for impact analysis functionality."""

    def test_calculate_change_impact(
        self, multi_file_project: Dict[str, Path]
    ) -> None:
        """Test calculating impact of changing a file."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_directory(multi_file_project['api'].parent)
        
        # Changing models.py should impact services.py and api.py
        impact = result.calculate_impact(str(multi_file_project['models']))
        
        affected_files = [f for f in impact.affected_files]
        assert len(affected_files) >= 1

    def test_identify_affected_endpoints(
        self, multi_file_project: Dict[str, Path]
    ) -> None:
        """Test identifying affected API endpoints."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_directory(multi_file_project['api'].parent)
        
        # Changing User model should affect user-related endpoints
        impact = result.calculate_impact(str(multi_file_project['models']))
        
        # Should identify affected endpoints
        assert hasattr(impact, 'affected_endpoints')


# =============================================================================
# TEST CLASSES: RELATIONSHIP GRAPH
# =============================================================================


class TestRelationshipGraph:
    """Tests for relationship graph construction."""

    def test_build_model_relationship_graph(
        self, database_model_code: str
    ) -> None:
        """Test building model relationship graph."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(database_model_code)
        
        graph = result.model_graph
        assert graph is not None
        
        # Check for edges
        edges = list(graph.edges)
        assert len(edges) >= 2  # User->Order, Order->OrderItem

    def test_find_related_models(self, database_model_code: str) -> None:
        """Test finding related models."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(database_model_code)
        
        # Find models related to User
        related = result.get_related_models('User')
        assert 'Order' in related


# =============================================================================
# TEST CLASSES: INTEGRATION
# =============================================================================


class TestRelationshipEngineIntegration:
    """Integration tests for the relationship engine."""

    def test_full_analysis_pipeline(
        self, multi_file_project: Dict[str, Path]
    ) -> None:
        """Test complete relationship analysis pipeline."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_directory(multi_file_project['api'].parent)
        
        assert result is not None
        assert result.dependency_graph is not None

    def test_serialization_to_dict(self, api_endpoint_code: str) -> None:
        """Test serialization of analysis results."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(api_endpoint_code)
        
        serialized = result.to_dict()
        
        assert isinstance(serialized, dict)
        assert 'api_endpoints' in serialized
        assert 'database_models' in serialized

    def test_export_graphviz(self, database_model_code: str) -> None:
        """Test exporting relationships to graphviz format."""
        from src.core.intelligence.relationship_traversal import RelationshipEngine
        
        engine = RelationshipEngine()
        result = engine.analyze_string(database_model_code)
        
        dot = result.to_graphviz()
        
        assert isinstance(dot, str)
        assert 'digraph' in dot
