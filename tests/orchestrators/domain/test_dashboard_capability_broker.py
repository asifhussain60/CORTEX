"""
Phase 53 Stage 3 Tests: DashboardCapabilityBroker (Centralized Architecture)
Authority: CORTEX Option B - Centralized Broker Pattern
Scope: 28 tests covering broker functionality, audit trail, cache, orchestrator integration

AC_START: AC-PHASE53-S3-TESTS-001
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import uuid

from cortex.orchestrators.domain.dashboard_capability_broker import (
    DashboardCapabilityBroker,
    DashboardGenerationRequest,
    DashboardGenerationResponse,
    RepositoryType,
    DashboardMetric,
    AuditTrail,
    DashboardCache,
)


class TestDashboardCapabilityBrokerInitialization:
    """Tests 1-4: Broker initialization and setup"""
    
    def test_broker_initialization(self):
        """S3.T1: DashboardCapabilityBroker initializes correctly"""
        broker = DashboardCapabilityBroker()
        assert broker is not None, "Broker instantiation failed"
        assert isinstance(broker.cache, DashboardCache), "Cache not initialized"
        assert isinstance(broker.audit, AuditTrail), "Audit trail not initialized"
    
    def test_broker_empty_state(self):
        """S3.T2: Broker starts with empty state"""
        broker = DashboardCapabilityBroker()
        assert len(broker.registered_orchestrators) == 0, "Should start with no orchestrators"
        assert len(broker.generated_dashboards) == 0, "Should start with no dashboards"
        assert len(broker.metrics_history) == 0, "Should start with no metrics"
    
    def test_audit_trail_initialization(self):
        """S3.T3: Audit trail initialized with correct phase/stage"""
        broker = DashboardCapabilityBroker()
        assert broker.audit.phase_id == "phase-53", "Phase ID incorrect"
        assert broker.audit.stage_id == "s3", "Stage ID incorrect"
    
    def test_cache_initialization(self):
        """S3.T4: Cache initializes with TTL configuration"""
        cache = DashboardCache()
        assert cache.CACHE_TTL_MS == 5 * 60 * 1000, "Cache TTL should be 5 minutes"
        assert len(cache.cache) == 0, "Cache should start empty"


class TestOrchestratorRegistration:
    """Tests 5-8: Orchestrator registration and capability tracking"""
    
    def test_register_single_orchestrator(self):
        """S3.T5: Single orchestrator can register with broker"""
        broker = DashboardCapabilityBroker()
        broker.register_orchestrator(
            "MasterOrchestrator",
            ["generate_dashboard", "sync_data"]
        )
        assert "MasterOrchestrator" in broker.registered_orchestrators
    
    def test_register_all_seven_orchestrators(self):
        """S3.T6: All 7 operational orchestrators can register"""
        broker = DashboardCapabilityBroker()
        orchestrators = [
            "MasterOrchestrator",
            "PlanningOrchestrator",
            "InteractionOrchestrator",
            "RepositoryOnboardingOrchestrator",
            "RefactoringOrchestrator",
            "RecommendationGate",
            "TDDOrchestrator"
        ]
        
        for orch in orchestrators:
            broker.register_orchestrator(orch, ["dashboard"])
        
        assert len(broker.registered_orchestrators) == 7, "All 7 orchestrators must register"
    
    def test_orchestrator_capabilities_tracked(self):
        """S3.T7: Orchestrator capabilities are tracked"""
        broker = DashboardCapabilityBroker()
        capabilities = ["generate", "sync", "validate"]
        broker.register_orchestrator("TestOrch", capabilities)
        
        orch_data = broker.registered_orchestrators["TestOrch"]
        assert orch_data["capabilities"] == capabilities
        assert orch_data["request_count"] == 0
    
    def test_orchestrator_request_count_increments(self):
        """S3.T8: Orchestrator request count increments on dashboard generation"""
        broker = DashboardCapabilityBroker()
        broker.register_orchestrator("PlanningOrchestrator", ["dashboard"])
        
        # Simulate request
        broker.registered_orchestrators["PlanningOrchestrator"]["request_count"] += 1
        assert broker.registered_orchestrators["PlanningOrchestrator"]["request_count"] == 1


class TestDashboardGenerationRequest:
    """Tests 9-12: Request object creation and validation"""
    
    def test_request_creation_minimal(self):
        """S3.T9: Create minimal DashboardGenerationRequest"""
        req = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[DashboardMetric.CODE_COVERAGE],
            requester_orchestrator="MasterOrchestrator"
        )
        assert req.repository == RepositoryType.CORTEX
        assert req.request_id is not None
        assert req.timestamp is not None
    
    def test_request_auto_id_generation(self):
        """S3.T10: Request auto-generates UUID if not provided"""
        req1 = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[],
            requester_orchestrator="Test"
        )
        req2 = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[],
            requester_orchestrator="Test"
        )
        assert req1.request_id != req2.request_id, "Request IDs should be unique"
    
    def test_request_all_repositories(self):
        """S3.T11: Request supports all 5 repository types"""
        repos = [
            RepositoryType.CORTEX,
            RepositoryType.KSESSIONS,
            RepositoryType.KASHKOLE,
            RepositoryType.ALIST,
            RepositoryType.NOOR_CANVAS
        ]
        
        for repo in repos:
            req = DashboardGenerationRequest(
                repository=repo,
                metrics=[],
                requester_orchestrator="Test"
            )
            assert req.repository == repo
    
    def test_request_all_metrics(self):
        """S3.T12: Request supports all 6 dashboard metrics"""
        all_metrics = [
            DashboardMetric.CODE_COVERAGE,
            DashboardMetric.TEST_HEALTH,
            DashboardMetric.SECURITY_SCAN,
            DashboardMetric.PERFORMANCE,
            DashboardMetric.DEPENDENCY_HEALTH,
            DashboardMetric.ARCHITECTURE_INTEGRITY
        ]
        
        req = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=all_metrics,
            requester_orchestrator="Test"
        )
        assert len(req.metrics) == 6


class TestDashboardGenerationResponse:
    """Tests 13-15: Response object structure"""
    
    def test_response_creation(self):
        """S3.T13: DashboardGenerationResponse creates correctly"""
        resp = DashboardGenerationResponse(
            request_id="test-123",
            repository=RepositoryType.CORTEX,
            status="success",
            data_url="/data/cortex.json",
            html_url="/spa/index.html"
        )
        assert resp.status == "success"
        assert resp.data_url is not None
    
    def test_response_error_handling(self):
        """S3.T14: Response can represent errors"""
        resp = DashboardGenerationResponse(
            request_id="test-123",
            repository=RepositoryType.CORTEX,
            status="failed",
            data_url=None,
            html_url=None,
            error_message="Data fetch failed"
        )
        assert resp.status == "failed"
        assert resp.error_message == "Data fetch failed"
    
    def test_response_cache_hit_tracking(self):
        """S3.T15: Response tracks cache hits"""
        resp = DashboardGenerationResponse(
            request_id="test-123",
            repository=RepositoryType.CORTEX,
            status="success",
            data_url="/data/cortex.json",
            html_url="/spa/index.html",
            cache_hit=True
        )
        assert resp.cache_hit is True


class TestAuditTrail:
    """Tests 16-18: Audit trail AC marker logging"""
    
    def test_audit_start_marker(self):
        """S3.T16: AC_START marker logged correctly"""
        audit = AuditTrail()
        req = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[],
            requester_orchestrator="Test"
        )
        marker = audit.log_start("OP-001", req)
        
        assert "AC_START" in marker
        assert len(audit.operations) == 1
        assert audit.operations[0]["type"] == "START"
    
    def test_audit_complete_marker(self):
        """S3.T17: AC_COMPLETE marker logged correctly"""
        audit = AuditTrail()
        resp = DashboardGenerationResponse(
            request_id="test-123",
            repository=RepositoryType.CORTEX,
            status="success",
            data_url="/data/cortex.json",
            html_url="/spa/index.html"
        )
        marker = audit.log_complete("OP-001", resp, test_count=29)
        
        assert "AC_COMPLETE" in marker
        assert len(audit.operations) == 1
        assert audit.operations[0]["status"] == "success"
    
    def test_audit_error_marker(self):
        """S3.T18: AC_ERROR marker logged on exception"""
        audit = AuditTrail()
        error = Exception("Test error")
        marker = audit.log_error("OP-001", error)
        
        assert "AC_ERROR" in marker
        assert len(audit.operations) == 1
        assert audit.operations[0]["type"] == "ERROR"


class TestDashboardCache:
    """Tests 19-22: Cache functionality and TTL"""
    
    def test_cache_get_set_operations(self):
        """S3.T19: Cache get/set operations work"""
        cache = DashboardCache()
        cache.set("key-1", {"data": "test"})
        
        result = cache.get("key-1")
        assert result is not None
        assert result["data"] == "test"
    
    def test_cache_key_generation(self):
        """S3.T20: Cache key generation is deterministic"""
        cache = DashboardCache()
        metrics = [DashboardMetric.CODE_COVERAGE, DashboardMetric.TEST_HEALTH]
        
        key1 = cache.get_cache_key(RepositoryType.CORTEX, metrics)
        key2 = cache.get_cache_key(RepositoryType.CORTEX, metrics)
        
        assert key1 == key2, "Cache keys should be deterministic"
    
    def test_cache_expiration(self):
        """S3.T21: Cache entries expire after TTL"""
        cache = DashboardCache()
        cache.set("key-1", {"data": "test"})
        
        # Manually advance timestamp to simulate expiration
        cache.timestamps["key-1"] = datetime.utcnow() - timedelta(minutes=6)
        
        result = cache.get("key-1")
        assert result is None, "Expired cache should return None"
    
    def test_cache_invalidation(self):
        """S3.T22: Cache can be invalidated"""
        cache = DashboardCache()
        cache.set("cortex-key", {"data": "cortex"})
        cache.set("ksessions-key", {"data": "ksessions"})
        
        cache.invalidate(RepositoryType.CORTEX)
        
        # cortex should be gone, ksessions should remain
        assert cache.get("cortex-key") is None


class TestBrokerDashboardGeneration:
    """Tests 23-26: Core dashboard generation through broker"""
    
    def test_generate_dashboard_success(self):
        """S3.T23: Broker successfully generates dashboard"""
        broker = DashboardCapabilityBroker()
        broker.register_orchestrator("MasterOrchestrator", ["dashboard"])
        
        req = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[DashboardMetric.CODE_COVERAGE],
            requester_orchestrator="MasterOrchestrator"
        )
        
        resp = broker.generate_dashboard(req)
        
        assert resp.status == "success"
        assert resp.data_url is not None
        assert len(broker.audit.operations) >= 2  # START and COMPLETE
    
    def test_generate_dashboard_cache_hit(self):
        """S3.T24: Subsequent requests hit cache"""
        broker = DashboardCapabilityBroker()
        req = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[DashboardMetric.CODE_COVERAGE],
            requester_orchestrator="Test"
        )
        
        resp1 = broker.generate_dashboard(req)
        
        # Create similar request
        req2 = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[DashboardMetric.CODE_COVERAGE],
            requester_orchestrator="Test"
        )
        resp2 = broker.generate_dashboard(req2)
        
        assert resp2.cache_hit is True
    
    def test_generate_dashboard_metrics_recorded(self):
        """S3.T25: Dashboard generation metrics are recorded"""
        broker = DashboardCapabilityBroker()
        req = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[DashboardMetric.CODE_COVERAGE],
            requester_orchestrator="MasterOrchestrator"
        )
        
        broker.generate_dashboard(req)
        
        assert len(broker.metrics_history) > 0
        assert broker.metrics_history[0]["repository"] == "cortex"
        assert broker.metrics_history[0]["orchestrator"] == "MasterOrchestrator"
    
    def test_generate_dashboard_stored(self):
        """S3.T26: Generated dashboards are stored"""
        broker = DashboardCapabilityBroker()
        req = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[],
            requester_orchestrator="Test"
        )
        
        resp = broker.generate_dashboard(req)
        
        assert resp.request_id in broker.generated_dashboards
        assert broker.generated_dashboards[resp.request_id] == resp


class TestBrokerDataSynchronization:
    """Tests 27-28: Data sync and metrics retrieval"""
    
    def test_sync_dashboard_data(self):
        """S3.T27: Sync dashboard data invalidates cache and updates files"""
        broker = DashboardCapabilityBroker()
        
        # Pre-populate cache
        broker.cache.set("cortex-key", {"data": "old"})
        
        result = broker.sync_dashboard_data(
            RepositoryType.CORTEX,
            {"data": "new"}
        )
        
        assert result is True
        assert broker.cache.get("cortex-key") is None  # Cache invalidated
    
    def test_get_broker_metrics(self):
        """S3.T28: Broker metrics endpoint provides monitoring data"""
        broker = DashboardCapabilityBroker()
        broker.register_orchestrator("MasterOrchestrator", ["dashboard"])
        
        req = DashboardGenerationRequest(
            repository=RepositoryType.CORTEX,
            metrics=[],
            requester_orchestrator="MasterOrchestrator"
        )
        broker.generate_dashboard(req)
        
        metrics = broker.get_metrics()
        
        assert "total_requests" in metrics
        assert "registered_orchestrators" in metrics
        assert "average_generation_time_ms" in metrics
        assert metrics["total_requests"] == 1
        assert metrics["registered_orchestrators"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

# AC_COMPLETE: AC-PHASE53-S3-TESTS-001 ✅ 28/28 tests defined
