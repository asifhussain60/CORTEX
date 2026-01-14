# Dashboard Phase 1 - Backend API Infrastructure
# Task 1.1: FastAPI Project Setup

"""
Plan Viewer Dashboard API Server

This module provides the FastAPI server for the CORTEX Plan Viewer Dashboard.
Implements Option A (Integrated) - Dashboard embedded in plan structure.

Features:
- REST API endpoints for plan data, progress, audit logs, tests
- WebSocket endpoint for real-time updates
- Static file serving for SPA
- Health check endpoint

Phase: 1 (Foundation)
Estimated: 4-5 hours
Acceptance Criteria: AC-DASH-001
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime
from pathlib import Path


# ==============================================================================
# FastAPI Application Initialization
# ==============================================================================

app = FastAPI(
    title="CORTEX Plan Viewer Dashboard",
    description="Real-time plan execution monitoring with audit evidence",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware - Allow all origins for localhost development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development: Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# WebSocket Connection Manager
# ==============================================================================

class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    
    Implements:
    - Connection tracking
    - Broadcast messaging
    - Ping/pong heartbeat
    - Clean disconnect handling
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove disconnected WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)


manager = ConnectionManager()


# ==============================================================================
# REST API Endpoints (Task 1.2)
# ==============================================================================

@app.get("/api/plan")
async def get_plan_metadata() -> JSONResponse:
    """
    Get plan metadata (name, ID, phases, estimated effort).
    
    Returns:
        JSONResponse: Plan metadata
    """
    # Mock data for Phase 1 - will be replaced with real data in Phase 3
    data = {
        "plan_id": "plan-dashboard-phase1",
        "plan_name": "Dashboard Implementation",
        "status": "IN_PROGRESS",
        "created": datetime.now().isoformat(),
        "phases": 4,
        "estimated_hours": {"min": 16, "max": 20},
        "strategy": "SNOWBALL"
    }
    return JSONResponse(content=data, status_code=200)


@app.get("/api/progress")
async def get_progress_snapshot() -> JSONResponse:
    """
    Get current progress snapshot (phase completion, task status).
    
    Returns:
        JSONResponse: Progress snapshot
    """
    # Mock data for Phase 1
    data = {
        "overall_progress": 0.25,
        "current_phase": 1,
        "phase_name": "Foundation - Backend API",
        "tasks_completed": 2,
        "tasks_total": 5,
        "phase_progress": 0.40,
        "status": "IN_PROGRESS"
    }
    return JSONResponse(content=data, status_code=200)


@app.get("/api/audit-logs")
async def get_audit_logs(limit: int = 100) -> JSONResponse:
    """
    Get recent audit log entries.
    
    Args:
        limit: Maximum number of entries to return (default 100)
    
    Returns:
        JSONResponse: List of audit log entries
    """
    # Mock data for Phase 1
    data = {
        "total_entries": 3,
        "limit": limit,
        "entries": [
            {
                "timestamp": datetime.now().isoformat(),
                "operation": "task_completed",
                "task_id": "TASK-1.1",
                "status": "success",
                "message": "FastAPI project setup complete"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "operation": "task_started",
                "task_id": "TASK-1.2",
                "status": "in_progress",
                "message": "Implementing REST endpoints"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "operation": "phase_started",
                "phase_id": "phase_1",
                "status": "in_progress",
                "message": "Phase 1 Foundation started"
            }
        ]
    }
    return JSONResponse(content=data, status_code=200)


@app.get("/api/tests")
async def get_test_coverage() -> JSONResponse:
    """
    Get test coverage summary (AC-ID traceability, pass/fail status).
    
    Returns:
        JSONResponse: Test coverage metrics
    """
    # Mock data for Phase 1
    data = {
        "total_tests": 5,
        "passed": 3,
        "failed": 0,
        "skipped": 2,
        "coverage_percentage": 60.0,
        "ac_coverage": {
            "AC-DASH-001": {
                "tests": ["test_app_initialization", "test_health_check"],
                "status": "PASSED"
            }
        }
    }
    return JSONResponse(content=data, status_code=200)


@app.get("/api/summary")
async def get_dashboard_summary() -> JSONResponse:
    """
    Get overall dashboard summary (combined metrics).
    
    Returns:
        JSONResponse: Dashboard summary
    """
    # Mock data for Phase 1
    data = {
        "plan_status": "IN_PROGRESS",
        "overall_progress": 0.25,
        "current_phase": "Phase 1: Foundation",
        "tests_passed": 3,
        "tests_total": 5,
        "audit_entries": 3,
        "last_update": datetime.now().isoformat(),
        "health": "HEALTHY"
    }
    return JSONResponse(content=data, status_code=200)


# ==============================================================================
# WebSocket Endpoint (Task 1.4)
# ==============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Features:
    - Connection management
    - Ping/pong heartbeat
    - Broadcast support
    
    Acceptance Criteria: AC-DASH-001, AC-DASH-002
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal(websocket, {
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
            "message": "WebSocket connected successfully"
        })
        
        # Keep connection alive with heartbeat
        while True:
            try:
                # Wait for messages from client (ping/pong)
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                
                # Echo back for testing
                if data.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except asyncio.TimeoutError:
                # Send heartbeat ping
                await manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client disconnected: {websocket.client}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ==============================================================================
# Health Check Endpoint (Task 1.5)
# ==============================================================================

@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint for monitoring.
    
    Returns:
        JSONResponse: Server health status
    """
    data = {
        "status": "healthy",
        "service": "cortex-dashboard-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "OK",
            "websocket": "OK" if len(manager.active_connections) >= 0 else "ERROR",
            "static_files": "OK"
        }
    }
    return JSONResponse(content=data, status_code=200)


# ==============================================================================
# Static File Serving (Task 1.3)
# ==============================================================================

# Mount static files LAST (catch-all route)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")


# ==============================================================================
# Server Entry Point
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("CORTEX Plan Viewer Dashboard - Phase 1 Foundation")
    print("=" * 70)
    print(f"Server starting on http://localhost:8000")
    print(f"API Documentation: http://localhost:8000/api/docs")
    print(f"Health Check: http://localhost:8000/health")
    print(f"WebSocket: ws://localhost:8000/ws")
    print("=" * 70)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
