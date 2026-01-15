"""
Planning Orchestrator Tests - TDD for AC-AR-011

Tests for:
- AC-AR-011-01: PlanningOrchestrator registered in OrchestratorRegistry
- AC-AR-011-02: PlanningOrchestrator exposed as MCP tools
- AC-AR-011-03: All operations audit-logged with hash chain

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
from src.core.interfaces.i_orchestrator import OperationMode


@pytest.mark.ac("AR-011-01")
class TestOrchestratorInterface:
    """Test AC-AR-011-01: Interface compliance"""
    
    def test_orchestrator_implements_interface(self):
        """Should implement IOrchestrator interface."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        # Check required methods
        assert hasattr(orchestrator, 'get_name')
        assert hasattr(orchestrator, 'get_version')
        assert hasattr(orchestrator, 'initialize')
        assert hasattr(orchestrator, 'get_mode')
        assert hasattr(orchestrator, 'get_mcp_tools')
        assert hasattr(orchestrator, 'execute_operation')
        assert hasattr(orchestrator, 'get_audit_trail')
    
    def test_get_orchestrator_name(self):
        """Should return orchestrator name."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        name = orchestrator.get_name()
        
        assert name == "PlanningOrchestrator"
    
    def test_get_orchestrator_version(self):
        """Should return orchestrator version."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        version = orchestrator.get_version()
        
        assert version == "1.0.0"
    
    def test_initialize_orchestrator(self):
        """Should initialize orchestrator."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.initialize()
        
        assert result.is_ok()
    
    def test_get_operation_mode(self):
        """Should return current operation mode."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        mode = orchestrator.get_mode()
        
        assert mode == OperationMode.PLANNING


@pytest.mark.ac("AR-011-02")
class TestMCPToolExposure:
    """Test AC-AR-011-02: MCP tools exposed"""
    
    def test_get_mcp_tools(self):
        """Should expose MCP tools."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.get_mcp_tools()
        
        assert result.is_ok()
        tools = result.unwrap()
        assert isinstance(tools, dict)
        assert len(tools) > 0
    
    def test_plan_status_tool_exists(self):
        """Should expose plan_status tool."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.get_mcp_tools()
        tools = result.unwrap()
        
        assert "plan_status" in tools
        assert "description" in tools["plan_status"]
        assert "parameters" in tools["plan_status"]
    
    def test_next_ac_tool_exists(self):
        """Should expose next_ac tool."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.get_mcp_tools()
        tools = result.unwrap()
        
        assert "next_ac" in tools
    
    def test_enforce_phase_lock_tool_exists(self):
        """Should expose enforce_phase_lock tool."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.get_mcp_tools()
        tools = result.unwrap()
        
        assert "enforce_phase_lock" in tools
    
    def test_plan_status_operation(self):
        """Should execute plan_status operation."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.plan_status("PHASE-01")
        
        assert result.is_ok()
        status = result.unwrap()
        assert status["phase_id"] == "PHASE-01"
        assert "completion_percentage" in status
    
    def test_next_ac_operation(self):
        """Should execute next_ac operation."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.next_ac("PHASE-01")
        
        assert result.is_ok()
        ac_data = result.unwrap()
        assert "ac_id" in ac_data
        assert "phase_id" in ac_data
    
    def test_enforce_phase_lock_operation(self):
        """Should execute enforce_phase_lock operation."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.enforce_phase_lock(
            "PHASE-01",
            "Testing lock enforcement",
        )
        
        assert result.is_ok()
        lock_data = result.unwrap()
        assert lock_data["phase_id"] == "PHASE-01"
        assert "locked_at" in lock_data


@pytest.mark.ac("AR-011-03")
class TestAuditLogging:
    """Test AC-AR-011-03: Audit logging with hash chain"""
    
    def test_get_audit_trail(self):
        """Should retrieve audit trail."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        # Initialize to create audit entry
        orchestrator.initialize()
        
        result = orchestrator.get_audit_trail()
        
        assert result.is_ok()
        trail = result.unwrap()
        assert isinstance(trail, list)
        assert len(trail) > 0
    
    def test_audit_entry_has_hash(self):
        """Should record hash in audit entries."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        orchestrator.initialize()
        
        result = orchestrator.get_audit_trail()
        trail = result.unwrap()
        
        # Check first entry has hash
        entry = trail[0]
        assert "current_hash" in entry
        assert len(entry["current_hash"]) > 0
    
    def test_audit_hash_chain(self):
        """Should maintain hash chain in audit entries."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        orchestrator.initialize()
        orchestrator.plan_status("PHASE-01")
        orchestrator.next_ac("PHASE-01")
        
        result = orchestrator.get_audit_trail()
        trail = result.unwrap()
        
        # Verify chain
        for i in range(1, len(trail)):
            current_entry = trail[i]
            previous_entry = trail[i - 1]
            
            # Current should reference previous
            assert current_entry["previous_hash"] == previous_entry["current_hash"]
    
    def test_verify_audit_chain_integrity(self):
        """Should verify audit chain integrity."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        orchestrator.initialize()
        orchestrator.plan_status("PHASE-01")
        
        result = orchestrator.verify_audit_chain()
        
        assert result.is_ok()
        assert result.unwrap() is True
    
    def test_operations_are_audited(self):
        """Should audit all operations."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        initial_count = orchestrator.get_operation_count()
        
        # Execute multiple operations
        orchestrator.initialize()
        orchestrator.plan_status("PHASE-01")
        orchestrator.next_ac("PHASE-01")
        
        final_count = orchestrator.get_operation_count()
        
        # Should have at least 4 audit entries (init + 3 ops)
        assert final_count >= initial_count + 3


class TestOperationExecution:
    """Test operation execution"""
    
    def test_execute_plan_status(self):
        """Should execute plan_status via execute_operation."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.execute_operation(
            "plan_status",
            {"phase_id": "PHASE-01"},
        )
        
        assert result.is_ok()
    
    def test_execute_next_ac(self):
        """Should execute next_ac via execute_operation."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.execute_operation(
            "next_ac",
            {"phase_id": "PHASE-01"},
        )
        
        assert result.is_ok()
    
    def test_execute_enforce_lock(self):
        """Should execute enforce_phase_lock via execute_operation."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.execute_operation(
            "enforce_phase_lock",
            {
                "phase_id": "PHASE-01",
                "reason": "Testing",
            },
        )
        
        assert result.is_ok()
    
    def test_execute_unknown_operation_fails(self):
        """Should fail for unknown operation."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        result = orchestrator.execute_operation(
            "unknown_operation",
            {},
        )
        
        assert result.is_err()


class TestSingletonPattern:
    """Test singleton implementation"""
    
    def test_singleton_consistency(self):
        """Should maintain singleton consistency."""
        orch1 = PlanningOrchestrator.instance()
        orch2 = PlanningOrchestrator.instance()
        
        assert orch1 is orch2
    
    def test_reset_singleton(self):
        """Should allow singleton reset."""
        orch1 = PlanningOrchestrator.instance()
        PlanningOrchestrator.reset_instance()
        orch2 = PlanningOrchestrator.instance()
        
        assert orch1 is not orch2


class TestIntegration:
    """Integration tests"""
    
    def test_complete_orchestrator_workflow(self):
        """Should handle complete workflow."""
        orchestrator = PlanningOrchestrator()
        orchestrator.reset_instance()
        orchestrator = PlanningOrchestrator.instance()
        
        # Initialize
        init_result = orchestrator.initialize()
        assert init_result.is_ok()
        
        # Get tools
        tools_result = orchestrator.get_mcp_tools()
        assert tools_result.is_ok()
        tools = tools_result.unwrap()
        # 4 tools: plan_status, next_ac, enforce_phase_lock, get_plan_data_for_observatory
        assert len(tools) == 4
        assert "get_plan_data_for_observatory" in tools  # Neural Observatory data provider
        
        # Execute operations
        status_result = orchestrator.execute_operation(
            "plan_status",
            {"phase_id": "PHASE-01"},
        )
        assert status_result.is_ok()
        
        ac_result = orchestrator.execute_operation(
            "next_ac",
            {"phase_id": "PHASE-01"},
        )
        assert ac_result.is_ok()
        
        lock_result = orchestrator.execute_operation(
            "enforce_phase_lock",
            {"phase_id": "PHASE-01", "reason": "Test"},
        )
        assert lock_result.is_ok()
        
        # Test new Observatory data provider
        observatory_result = orchestrator.execute_operation(
            "get_plan_data_for_observatory",
            {"phase_id": "PHASE-01"},
        )
        assert observatory_result.is_ok()
        observatory_data = observatory_result.unwrap()
        assert "visualization_target" in observatory_data
        assert observatory_data["visualization_target"] == "Neural Observatory Plan Hub"
        
        # Verify audit trail
        audit_result = orchestrator.get_audit_trail()
        assert audit_result.is_ok()
        trail = audit_result.unwrap()
        assert len(trail) >= 6  # init + 4 ops + get_mcp_tools
        
        # Verify chain
        verify_result = orchestrator.verify_audit_chain()
        assert verify_result.is_ok()
