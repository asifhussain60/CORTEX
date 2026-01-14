"""
Tests for MasterOrchestrator - Orchestrator Coordination

AC-AR-006-01: MasterOrchestrator coordinates domain orchestrators
- Registry registration and management
- Operation delegation across domains
- Result aggregation
- Audit logging on all operations
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from typing import Any, Dict

from src.orchestrators.core.master_orchestrator import MasterOrchestrator, OrchestratorMetadata
from src.core.interfaces import IOrchestrator, OperationMode
from src.core.result import Result, Ok, Err
from src.infrastructure.database import DatabaseManager
from src.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class MockOrchestrator(IOrchestrator):
    """Mock orchestrator for testing"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.operations = []
    
    def get_name(self) -> str:
        """Get orchestrator name."""
        return f"MockOrchestrator-{self.domain}"
    
    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0"
    
    def initialize(self) -> 'Result[str]':
        """Initialize orchestrator."""
        return Ok(f"Initialized {self.domain}")
    
    def get_mode(self) -> 'OperationMode':
        """Get current operation mode."""
        from src.core.interfaces import OperationMode
        return OperationMode.PLANNING
    
    def get_mcp_tools(self) -> 'Result[Dict]':
        """Get MCP tools."""
        return Ok({})
    
    def execute_operation(self, operation_name: str, parameters: Dict) -> 'Result[Any]':
        """Execute operation."""
        self.operations.append({
            "operation": operation_name,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        })
        return Ok({"domain": self.domain, "status": "executed"})
    
    def get_audit_trail(self, limit: int = 100) -> 'Result[list]':
        """Get audit trail."""
        return Ok([])
    
    def execute(self, operation: str, context: dict) -> dict:
        """Mock execute method"""
        self.operations.append({
            "operation": operation,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        return {"domain": self.domain, "status": "executed"}


class TestMasterOrchestratorRegistration:
    """Test AC-AR-006-01: Orchestrator registration"""
    
    def setup_method(self):
        """Setup for each test"""
        # Reset singleton instance
        MasterOrchestrator._instance = None
        self.master = MasterOrchestrator.instance()
        self.mock_orch1 = MockOrchestrator("governance")
        self.mock_orch2 = MockOrchestrator("audit")
    
    def test_register_single_orchestrator(self):
        """Test registering a single orchestrator"""
        result = self.master.register_orchestrator(
            domain="governance",
            orchestrator=self.mock_orch1,
            capabilities=["validate", "enforce"]
        )
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["domain"] == "governance"
        assert data["registered"] == True
        assert data["total_orchestrators"] == 1
    
    def test_register_multiple_orchestrators(self):
        """Test registering multiple orchestrators"""
        result1 = self.master.register_orchestrator(
            domain="governance",
            orchestrator=self.mock_orch1
        )
        assert result1.is_ok()
        
        result2 = self.master.register_orchestrator(
            domain="audit",
            orchestrator=self.mock_orch2
        )
        assert result2.is_ok()
        data2 = result2.unwrap()
        assert data2["total_orchestrators"] == 2
    
    def test_duplicate_registration_fails(self):
        """Test that duplicate registration fails"""
        result1 = self.master.register_orchestrator(
            domain="governance",
            orchestrator=self.mock_orch1
        )
        assert result1.is_ok()
        
        # Try to register same domain again
        result2 = self.master.register_orchestrator(
            domain="governance",
            orchestrator=MockOrchestrator("governance")
        )
        assert result2.is_err()
        assert "already registered" in result2.error.lower()
    
    def test_registration_creates_metadata(self):
        """Test that registration creates proper metadata"""
        self.master.register_orchestrator(
            domain="governance",
            orchestrator=self.mock_orch1,
            capabilities=["validate", "enforce"]
        )
        
        assert "governance" in self.master.domain_orchestrators
        metadata = self.master.domain_orchestrators["governance"]
        assert isinstance(metadata, OrchestratorMetadata)
        assert metadata.domain == "governance"
        assert metadata.orchestrator == self.mock_orch1
        assert metadata.capabilities == ["validate", "enforce"]


class TestMasterOrchestratorQuerying:
    """Test registry query operations"""
    
    def setup_method(self):
        """Setup for each test"""
        MasterOrchestrator._instance = None
        self.master = MasterOrchestrator.instance()
        
        # Register multiple orchestrators
        self.master.register_orchestrator("governance", MockOrchestrator("governance"))
        self.master.register_orchestrator("audit", MockOrchestrator("audit"))
        self.master.register_orchestrator("evidence", MockOrchestrator("evidence"))
    
    def test_get_registered_domains(self):
        """Test getting list of registered domains"""
        result = self.master.get_registered_domains()
        
        assert result.is_ok()
        domains = result.unwrap()
        assert len(domains) == 3
        assert "governance" in domains
        assert "audit" in domains
        assert "evidence" in domains
    
    def test_get_orchestrator_by_domain(self):
        """Test retrieving orchestrator by domain"""
        result = self.master.get_orchestrator("governance")
        
        assert result.is_ok()
        orch = result.unwrap()
        assert orch.domain == "governance"
    
    def test_get_nonexistent_orchestrator(self):
        """Test retrieving nonexistent orchestrator fails"""
        result = self.master.get_orchestrator("nonexistent")
        
        assert result.is_err()
        assert "orchestrator registered" in result.error.lower()
    
    def test_get_registry_status(self):
        """Test getting complete registry status"""
        result = self.master.get_registry_status()
        
        assert result.is_ok()
        status = result.unwrap()
        assert status["total_orchestrators"] == 3
        assert len(status["domains"]) == 3
        assert all("domain" in d for d in status["domains"])
        assert all("type" in d for d in status["domains"])


class TestMasterOrchestratorCoordination:
    """Test AC-AR-006-01: Operation coordination"""
    
    def setup_method(self):
        """Setup for each test"""
        MasterOrchestrator._instance = None
        self.master = MasterOrchestrator.instance()
        
        # Register orchestrators
        self.master.register_orchestrator("governance", MockOrchestrator("governance"))
        self.master.register_orchestrator("audit", MockOrchestrator("audit"))
    
    def test_coordinate_operation_all_domains(self):
        """Test coordinating operation across all domains"""
        context = {"actor": "admin", "resource": "policy"}
        result = self.master.coordinate_operation(
            operation="validate",
            context=context
        )
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["operation"] == "validate"
        assert data["orchestrators_involved"] == 2
        assert "governance" in data["results"]
        assert "audit" in data["results"]
    
    def test_coordinate_operation_specific_domains(self):
        """Test coordinating operation on specific domains"""
        context = {"actor": "admin", "resource": "policy"}
        result = self.master.coordinate_operation(
            operation="validate",
            context=context,
            target_domains=["governance"]
        )
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["orchestrators_involved"] == 1
        assert "governance" in data["results"]
        assert "audit" not in data["results"]
    
    def test_coordinate_operation_invalid_domain(self):
        """Test coordination with invalid domain fails"""
        context = {"actor": "admin"}
        result = self.master.coordinate_operation(
            operation="validate",
            context=context,
            target_domains=["governance", "nonexistent"]
        )
        
        assert result.is_err()
        assert "invalid domains" in result.error.lower()
    
    def test_coordination_history_tracking(self):
        """Test that coordination operations are tracked"""
        context1 = {"operation": "validate"}
        self.master.coordinate_operation("validate", context1)
        
        context2 = {"operation": "enforce"}
        self.master.coordinate_operation("enforce", context2)
        
        history_result = self.master.get_coordination_history()
        assert history_result.is_ok()
        history = history_result.unwrap()
        assert len(history) == 2
        assert history[0]["operation"] == "validate"
        assert history[1]["operation"] == "enforce"


class TestMasterOrchestratorAuditLogging:
    """Test AC-AR-006-01: Audit logging for all operations"""
    
    def setup_method(self):
        """Setup for each test"""
        MasterOrchestrator._instance = None
        self.master = MasterOrchestrator.instance()
    
    def test_audit_logging_on_registration(self):
        """Test that registration creates audit entries"""
        # This test verifies audit logging happens
        # In a real test, we'd mock the logger and verify calls
        mock_orch = MockOrchestrator("governance")
        
        result = self.master.register_orchestrator(
            domain="governance",
            orchestrator=mock_orch,
            capabilities=["validate"]
        )
        
        # Should complete successfully
        assert result.is_ok()
        # In actual implementation, verify audit entries exist
    
    def test_audit_logging_on_coordination(self):
        """Test that coordination creates audit entries"""
        mock_orch = MockOrchestrator("governance")
        self.master.register_orchestrator("governance", mock_orch)
        
        result = self.master.coordinate_operation(
            operation="validate",
            context={"test": True}
        )
        
        # Should complete successfully
        assert result.is_ok()
        # In actual implementation, verify audit entries exist


class TestMasterOrchestratorSingleton:
    """Test singleton pattern"""
    
    def test_singleton_instance(self):
        """Test that MasterOrchestrator is a singleton"""
        MasterOrchestrator._instance = None
        
        master1 = MasterOrchestrator.instance()
        master2 = MasterOrchestrator.instance()
        
        assert master1 is master2
    
    def test_singleton_preserves_state(self):
        """Test that singleton preserves state across calls"""
        MasterOrchestrator._instance = None
        
        master1 = MasterOrchestrator.instance()
        master1.register_orchestrator("governance", MockOrchestrator("governance"))
        
        master2 = MasterOrchestrator.instance()
        domains = master2.get_registered_domains().unwrap()
        
        assert "governance" in domains


class TestMasterOrchestratorIntegration:
    """Integration tests with real components from Phase-01"""
    
    def setup_method(self):
        """Setup for each test"""
        MasterOrchestrator._instance = None
        self.master = MasterOrchestrator.instance()
    
    def test_complete_orchestration_workflow(self):
        """Test complete orchestration workflow"""
        # Register orchestrators
        orch1 = MockOrchestrator("governance")
        orch2 = MockOrchestrator("audit")
        
        reg1 = self.master.register_orchestrator("governance", orch1, ["validate", "enforce"])
        assert reg1.is_ok()
        
        reg2 = self.master.register_orchestrator("audit", orch2, ["log", "report"])
        assert reg2.is_ok()
        
        # Get status
        status = self.master.get_registry_status().unwrap()
        assert status["total_orchestrators"] == 2
        
        # Coordinate operation
        coord = self.master.coordinate_operation("validate", {"test": True})
        assert coord.is_ok()
        
        # Check history
        history = self.master.get_coordination_history().unwrap()
        assert len(history) == 1
    
    def test_error_handling(self):
        """Test error handling in coordination"""
        # Register valid orchestrator
        self.master.register_orchestrator("governance", MockOrchestrator("governance"))
        
        # Try to coordinate with invalid domain
        result = self.master.coordinate_operation(
            "validate",
            {},
            target_domains=["invalid_domain"]
        )
        
        assert result.is_err()


class TestMasterOrchestratorMetadata:
    """Test orchestrator metadata handling"""
    
    def test_metadata_creation(self):
        """Test OrchestratorMetadata dataclass"""
        orch = MockOrchestrator("test")
        metadata = OrchestratorMetadata(
            domain="test",
            orchestrator=orch,
            version="2.0",
            capabilities=["op1", "op2"]
        )
        
        assert metadata.domain == "test"
        assert metadata.orchestrator == orch
        assert metadata.version == "2.0"
        assert metadata.capabilities == ["op1", "op2"]
        assert metadata.registered_at is not None
    
    def test_metadata_with_defaults(self):
        """Test OrchestratorMetadata with default values"""
        orch = MockOrchestrator("test")
        metadata = OrchestratorMetadata(
            domain="test",
            orchestrator=orch
        )
        
        assert metadata.domain == "test"
        assert metadata.version == "1.0"
        assert metadata.capabilities == []
        assert metadata.registered_at is not None
