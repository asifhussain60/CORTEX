"""
Unit tests for CORTEX Neural Observatory API
Tests for all NO-00x acceptance criteria
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from dashboard.api.main import app

client = TestClient(app)


class TestAPIHealth:
    """Test API health check endpoint"""
    
    def test_health_check_returns_200(self):
        """NO-004-01: API is running"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_health_check_includes_timestamp(self):
        """Timestamp present in health response"""
        response = client.get("/api/health")
        data = response.json()
        assert "timestamp" in data
        assert "service" in data


class TestBrainTiers:
    """Test brain tier visualization endpoints"""
    
    def test_get_brain_tiers_returns_200(self):
        """NO-001-01: Brain tier endpoint returns success"""
        response = client.get("/api/brain/tiers")
        assert response.status_code == 200
    
    def test_brain_tiers_includes_all_four_tiers(self):
        """NO-001-01: All 4 tiers present"""
        response = client.get("/api/brain/tiers")
        data = response.json()
        assert "tiers" in data
        assert len(data["tiers"]) == 4
    
    def test_brain_tiers_have_required_fields(self):
        """NO-001-01: Each tier has required fields"""
        response = client.get("/api/brain/tiers")
        data = response.json()
        for tier in data["tiers"]:
            assert "name" in tier
            assert "label" in tier
            assert "status" in tier
            assert "metrics" in tier
    
    def test_tier_names_correct(self):
        """NO-001-01: Tier labels are correct"""
        response = client.get("/api/brain/tiers")
        data = response.json()
        labels = [tier["label"] for tier in data["tiers"]]
        assert "Governance" in labels
        assert "Acceptance" in labels
        assert "Templates" in labels
        assert "Knowledge" in labels
    
    def test_tier_status_valid(self):
        """NO-001-02: Status values are valid"""
        response = client.get("/api/brain/tiers")
        data = response.json()
        valid_statuses = {"HEALTHY", "NOMINAL", "DEGRADED", "CRITICAL"}
        for tier in data["tiers"]:
            assert tier["status"] in valid_statuses


class TestSSOTMetrics:
    """Test SSOT metrics endpoints"""
    
    def test_get_metrics_returns_200(self):
        """NO-001-03: Metrics endpoint returns success"""
        response = client.get("/api/brain/metrics")
        assert response.status_code == 200
    
    def test_metrics_includes_phases(self):
        """NO-001-03: Metrics include phase counts"""
        response = client.get("/api/brain/metrics")
        data = response.json()
        assert "phases" in data
        assert "total" in data["phases"]
        assert "locked" in data["phases"]
    
    def test_metrics_includes_acceptance_criteria(self):
        """NO-001-03: Metrics include AC counts"""
        response = client.get("/api/brain/metrics")
        data = response.json()
        assert "acceptance_criteria" in data
        assert "total" in data["acceptance_criteria"]
        assert "completed" in data["acceptance_criteria"]
    
    def test_metrics_includes_audit_data(self):
        """NO-002-01: Metrics include audit data"""
        response = client.get("/api/brain/metrics")
        data = response.json()
        assert "audit" in data
        assert "total_entries" in data["audit"]
        assert "hash_chain_valid" in data["audit"]


class TestAuditEndpoints:
    """Test audit timeline endpoints"""
    
    def test_get_audit_entries_returns_200(self):
        """NO-002-01: Audit entries endpoint returns success"""
        response = client.get("/api/audit/entries")
        assert response.status_code == 200
    
    def test_audit_entries_are_paginated(self):
        """NO-002-01: Entries support pagination"""
        response = client.get("/api/audit/entries?limit=10&offset=0")
        data = response.json()
        assert "entries" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
    
    def test_audit_entries_have_required_fields(self):
        """NO-002-01: Each audit entry has required fields"""
        response = client.get("/api/audit/entries")
        data = response.json()
        if data["entries"]:
            entry = data["entries"][0]
            assert "id" in entry
            assert "timestamp" in entry
            assert "ac_id" in entry
            assert "operation" in entry
            assert "message" in entry


class TestOrchestratorEndpoints:
    """Test orchestrator status endpoints"""
    
    def test_get_orchestrators_returns_200(self):
        """NO-003-01: Orchestrator endpoint returns success"""
        response = client.get("/api/orchestrators")
        assert response.status_code == 200
    
    def test_orchestrators_list_present(self):
        """NO-003-01: Orchestrator list is present"""
        response = client.get("/api/orchestrators")
        data = response.json()
        assert "orchestrators" in data
        assert isinstance(data["orchestrators"], list)
    
    def test_orchestrator_has_required_fields(self):
        """NO-003-01: Each orchestrator has required fields"""
        response = client.get("/api/orchestrators")
        data = response.json()
        if data["orchestrators"]:
            orch = data["orchestrators"][0]
            assert "name" in orch
            assert "status" in orch
            assert "last_execution" in orch
            assert "operations_executed" in orch
            assert "errors" in orch


class TestWebSocketConnectivity:
    """Test WebSocket endpoints"""
    
    def test_websocket_audit_stream_connects(self):
        """NO-004-02: WebSocket can connect"""
        with client.websocket_connect("/ws/audit") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connected"
    
    def test_websocket_receives_audit_entries(self):
        """NO-004-02: WebSocket receives audit entries"""
        with client.websocket_connect("/ws/audit") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Receive audit entry
            data = websocket.receive_json()
            assert data["type"] == "audit_entry"
            assert "id" in data
            assert "timestamp" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
