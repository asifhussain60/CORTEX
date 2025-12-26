"""
Test Configuration - pytest fixtures
FLAW TEST-07: Minimal fixtures, no proper test setup
"""
import pytest


@pytest.fixture
def app():
    """Create test Flask app"""
    from src.app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


# FLAW: No database fixtures, no mocking, tests hit real DB
