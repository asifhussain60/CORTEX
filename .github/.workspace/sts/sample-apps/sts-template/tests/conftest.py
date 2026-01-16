"""
Test Configuration
TEST-04: No mocking, hits real database
"""
import pytest

# TEST-04: Minimal fixtures, no mocking setup (FLAW)
@pytest.fixture
def app():
    """Minimal app fixture"""
    from src.app import app
    return app

# Missing: Database mocks, API mocks, proper test data setup
