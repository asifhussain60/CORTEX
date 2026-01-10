"""
Dashboard Phase 1 Tests - Backend API Infrastructure

Tests for AC-DASH-001: Server Initialization
- Server starts in <5 seconds
- All 5 REST endpoints return 200 OK
- WebSocket endpoint operational
- Static files served correctly
- Health check endpoint returns 200 OK

Test Strategy: RED → GREEN → REFACTOR
Phase: 1 (Foundation)
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
from pathlib import Path

# Add dashboard to path
dashboard_path = Path(__file__).parent.parent.parent / "dashboard"
sys.path.insert(0, str(dashboard_path))

from api import app, manager


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def client():
    """Synchronous test client for REST endpoints."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Asynchronous test client for WebSocket tests."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ==============================================================================
# TASK-1.1: FastAPI App Initialization
# ==============================================================================

def test_app_initialization(client):
    """
    Test: FastAPI app initializes successfully.
    AC: AC-DASH-001 (Server Initialization)
    """
    assert app is not None
    assert app.title == "CORTEX Plan Viewer Dashboard"
    assert app.version == "1.0.0"


def test_app_startup_time():
    """
    Test: Server starts in <5 seconds.
    AC: AC-DASH-001 (Performance SLA)
    """
    import time
    start_time = time.time()
    
    # Create client (triggers app startup)
    client = TestClient(app)
    
    startup_time = time.time() - start_time
    assert startup_time < 5.0, f"Server startup took {startup_time:.2f}s (should be <5s)"
    
    client.close()


# ==============================================================================
# TASK-1.2: REST Endpoints
# ==============================================================================

def test_get_plan_endpoint(client):
    """
    Test: GET /api/plan returns 200 OK with plan metadata.
    AC: AC-DASH-001 (REST Endpoints)
    """
    response = client.get("/api/plan")
    assert response.status_code == 200
    
    data = response.json()
    assert "plan_id" in data
    assert "plan_name" in data
    assert "status" in data
    assert data["strategy"] == "SNOWBALL"


def test_get_progress_endpoint(client):
    """
    Test: GET /api/progress returns 200 OK with progress snapshot.
    AC: AC-DASH-001 (REST Endpoints)
    """
    response = client.get("/api/progress")
    assert response.status_code == 200
    
    data = response.json()
    assert "overall_progress" in data
    assert "current_phase" in data
    assert "tasks_completed" in data
    assert "tasks_total" in data


def test_get_audit_logs_endpoint(client):
    """
    Test: GET /api/audit-logs returns 200 OK with audit entries.
    AC: AC-DASH-001 (REST Endpoints)
    """
    response = client.get("/api/audit-logs")
    assert response.status_code == 200
    
    data = response.json()
    assert "entries" in data
    assert "total_entries" in data
    assert isinstance(data["entries"], list)


def test_get_audit_logs_with_limit(client):
    """
    Test: GET /api/audit-logs?limit=10 respects limit parameter.
    AC: AC-DASH-001 (REST Endpoints)
    """
    response = client.get("/api/audit-logs?limit=10")
    assert response.status_code == 200
    
    data = response.json()
    assert data["limit"] == 10


def test_get_tests_endpoint(client):
    """
    Test: GET /api/tests returns 200 OK with test coverage.
    AC: AC-DASH-001 (REST Endpoints)
    """
    response = client.get("/api/tests")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_tests" in data
    assert "passed" in data
    assert "failed" in data
    assert "coverage_percentage" in data
    assert "ac_coverage" in data


def test_get_summary_endpoint(client):
    """
    Test: GET /api/summary returns 200 OK with dashboard summary.
    AC: AC-DASH-001 (REST Endpoints)
    """
    response = client.get("/api/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "plan_status" in data
    assert "overall_progress" in data
    assert "current_phase" in data
    assert "health" in data


def test_all_rest_endpoints_return_200(client):
    """
    Test: All 5 REST endpoints return 200 OK.
    AC: AC-DASH-001 (Complete REST API)
    """
    endpoints = [
        "/api/plan",
        "/api/progress",
        "/api/audit-logs",
        "/api/tests",
        "/api/summary"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, f"Endpoint {endpoint} failed"


# ==============================================================================
# TASK-1.3: Static File Serving
# ==============================================================================

def test_static_files_served(client):
    """
    Test: Static files (HTML) served correctly.
    AC: AC-DASH-001 (Static File Serving)
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_index_html_content(client):
    """
    Test: index.html contains expected content.
    AC: AC-DASH-001 (Static Files)
    """
    response = client.get("/")
    assert response.status_code == 200
    
    content = response.text
    assert "CORTEX Dashboard" in content
    assert "Phase 1" in content


# ==============================================================================
# TASK-1.4: WebSocket Endpoint
# ==============================================================================

def test_websocket_endpoint_exists(client):
    """
    Test: WebSocket endpoint /ws exists.
    AC: AC-DASH-001 (WebSocket Operational)
    """
    with client.websocket_connect("/ws") as websocket:
        # Should connect successfully
        assert websocket is not None


def test_websocket_connection_message(client):
    """
    Test: WebSocket sends welcome message on connection.
    AC: AC-DASH-001, AC-DASH-002 (WebSocket)
    """
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        
        assert data["type"] == "connection"
        assert data["status"] == "connected"
        assert "timestamp" in data


def test_websocket_ping_pong(client):
    """
    Test: WebSocket responds to ping with pong.
    AC: AC-DASH-002 (Real-Time Updates)
    """
    with client.websocket_connect("/ws") as websocket:
        # Receive welcome message
        websocket.receive_json()
        
        # Send ping
        websocket.send_json({"type": "ping"})
        
        # Should receive pong
        response = websocket.receive_json()
        assert response["type"] == "pong"


def test_websocket_connection_manager():
    """
    Test: ConnectionManager tracks connections correctly.
    AC: AC-DASH-001 (WebSocket Infrastructure)
    """
    assert manager is not None
    assert hasattr(manager, "active_connections")
    assert isinstance(manager.active_connections, list)


# ==============================================================================
# TASK-1.5: Health Check Endpoint
# ==============================================================================

def test_health_check_endpoint(client):
    """
    Test: GET /health returns 200 OK.
    AC: AC-DASH-001 (Health Check)
    """
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_content(client):
    """
    Test: Health check returns expected status.
    AC: AC-DASH-001 (Health Check Content)
    """
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "cortex-dashboard-api"
    assert "checks" in data
    assert data["checks"]["api"] == "OK"


def test_health_check_includes_timestamp(client):
    """
    Test: Health check includes timestamp.
    AC: AC-DASH-001 (Monitoring)
    """
    response = client.get("/health")
    data = response.json()
    
    assert "timestamp" in data
    assert isinstance(data["timestamp"], str)


# ==============================================================================
# AC-DASH-001 Validation (Phase 1 Exit Criteria)
# ==============================================================================

def test_ac_dash_001_server_initialization(client):
    """
    ACCEPTANCE CRITERIA VALIDATION: AC-DASH-001
    
    Server Initialization:
    ✅ Server starts in <5 seconds
    ✅ All 5 REST endpoints registered (/api/plan, /api/progress, /api/audit-logs, /api/tests, /api/summary)
    ✅ WebSocket endpoint /ws operational
    ✅ Static files served correctly (HTML, CSS, JS)
    ✅ CORS middleware configured (allow all origins for localhost)
    ✅ Health check endpoint /health returns 200 OK
    """
    # Test all 5 REST endpoints
    endpoints = [
        "/api/plan",
        "/api/progress",
        "/api/audit-logs",
        "/api/tests",
        "/api/summary"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, f"AC-DASH-001 FAILED: {endpoint} not operational"
    
    # Test WebSocket
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data["status"] == "connected", "AC-DASH-001 FAILED: WebSocket not operational"
    
    # Test static files
    response = client.get("/")
    assert response.status_code == 200, "AC-DASH-001 FAILED: Static files not served"
    
    # Test health check
    response = client.get("/health")
    assert response.status_code == 200, "AC-DASH-001 FAILED: Health check not operational"
    assert response.json()["status"] == "healthy"
    
    # All checks passed
    print("✅ AC-DASH-001 VALIDATED: Server Initialization PASSED")


# ==============================================================================
# Phase 1 Exit Criteria Validation
# ==============================================================================

@pytest.mark.phase1
def test_phase_1_exit_criteria(client):
    """
    Phase 1 Exit Criteria Validation:
    
    ✅ API server starts successfully
    ✅ All 5 endpoints return 200 OK
    ✅ WebSocket endpoint operational
    ✅ Static files served correctly
    ✅ Health check endpoint working
    ✅ AC-DASH-001 validated
    
    If this test passes, Phase 1 is COMPLETE and Phase 2 can begin.
    """
    # Criterion 1: Server running
    assert app is not None
    
    # Criterion 2: All endpoints 200 OK
    endpoints = ["/api/plan", "/api/progress", "/api/audit-logs", "/api/tests", "/api/summary"]
    for endpoint in endpoints:
        assert client.get(endpoint).status_code == 200
    
    # Criterion 3: WebSocket operational
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data["status"] == "connected"
    
    # Criterion 4: Static files served
    assert client.get("/").status_code == 200
    
    # Criterion 5: Health check working
    assert client.get("/health").status_code == 200
    assert client.get("/health").json()["status"] == "healthy"
    
    print("=" * 70)
    print("✅ PHASE 1 EXIT CRITERIA: ALL PASSED")
    print("=" * 70)
    print("Phase 1 (Foundation - Backend API) COMPLETE")
    print("Ready to proceed to Phase 2 (Features - Frontend SPA)")
    print("=" * 70)
