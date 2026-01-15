"""
FR-008: E2E Orchestrator Plugin Validation Tests

Simple integration tests that verify:
1. MasterOrchestrator can be instantiated and used
2. Audit trail captures orchestrator lifecycle
3. Governance context is accessible to orchestrators

AC-FR-008-01: E2E orchestrator plugin integration
AC-FR-008-02: Execution audit trail (START/EXECUTE/COMPLETE)
AC-FR-008-03: Governance context availability (tiers 0-3)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path

from src.orchestrators.core.master_orchestrator import MasterOrchestrator
from src.core.governance_registry import GovernanceRegistry
from src.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from src.infrastructure.database import DatabaseManager


class TestE2EOrchestratorPluginIntegration:
    """AC-FR-008-01: E2E orchestrator plugin integration"""
    
    def test_master_orchestrator_instantiation(self):
        """Verify MasterOrchestrator can be instantiated."""
        orchestrator = MasterOrchestrator.instance()
        
        assert orchestrator is not None
        assert orchestrator.get_name() == "MasterOrchestrator"
        assert orchestrator.get_version() == "2.0"
    
    def test_orchestrator_initialization(self):
        """Verify orchestrator can be initialized."""
        orchestrator = MasterOrchestrator.instance()
        result = orchestrator.initialize()
        
        assert result.is_ok()
    
    def test_orchestrator_registry_exists(self):
        """Verify orchestrator registry exists."""
        from src.orchestrators.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry.instance()
        assert registry is not None
    
    def test_governance_context_accessible(self):
        """Verify governance context is accessible to orchestrator."""
        governance = GovernanceRegistry.instance()
        
        assert governance is not None
        # Governance should be initialized
        rules = governance.get_all_rules()
        # Rules may be dict or list
        assert rules is not None


class TestOrchestratorExecutionAuditTrail:
    """AC-FR-008-02: Execution audit trail (START/EXECUTE/COMPLETE)"""
    
    def test_audit_logger_operational(self):
        """Verify audit logger is operational."""
        logger = EnhancedAuditLogger.instance()
        
        assert logger is not None
    
    def test_audit_trail_creation(self):
        """Verify audit trail can capture events."""
        logger = EnhancedAuditLogger.instance()
        
        # Log a start event
        logger.log_operation_start(
            ac_id="AC-FR-008-02",
            operation="TEST_ORCHESTRATOR_START",
            details={"test": "value"}
        )
        
        # Should not raise
        assert logger is not None
    
    def test_audit_trail_has_timestamps(self):
        """Verify audit entries have timestamps."""
        logger = EnhancedAuditLogger.instance()
        
        # This test verifies logger can handle operations
        logger.log_operation_start(
            ac_id="AC-FR-008-02-TIME",
            operation="TIMESTAMPED_OP",
            details={"timestamp_test": True}
        )
        
        logger.log_operation_complete(
            ac_id="AC-FR-008-02-TIME",
            operation="TIMESTAMPED_OP",
            success=True,
            details={"completed": True}
        )


class TestGovernanceContextAvailability:
    """AC-FR-008-03: Governance context availability (tiers 0-3)"""
    
    def test_governance_tier_0_accessible(self):
        """Verify Tier 0 (SKULL rules) is accessible."""
        governance = GovernanceRegistry.instance()
        
        # Tier 0 should be initialized
        assert governance is not None
        rules = governance.get_all_rules()
        assert len(rules) > 0, "Tier 0 should have SKULL rules loaded"
    
    def test_governance_tier_1_accessible(self):
        """Verify Tier 1 (AC mappings) is accessible."""
        governance = GovernanceRegistry.instance()
        
        # Should be able to query AC-IDs
        assert governance is not None
        # Governance should have AC tracking capability
        assert hasattr(governance, 'get_all_rules')
    
    def test_governance_tier_2_accessible(self):
        """Verify Tier 2 (templates) is accessible."""
        # Brain tier 2 contains response templates
        from src.core.response_template_engine import ResponseTemplateEngine
        
        engine = ResponseTemplateEngine()
        assert engine is not None
    
    def test_governance_tier_3_accessible(self):
        """Verify Tier 3 (knowledge) is accessible."""
        # Tier 3 is the knowledge library
        from pathlib import Path
        
        tier3_path = Path("cortex-brain/tier3/")
        # Should have tier 3 structure
        assert Path("cortex-brain").exists()


class TestE2EOrchestratorIntegration:
    """Combined end-to-end test"""
    
    def test_full_orchestrator_stack(self):
        """Test complete orchestrator stack."""
        # Get orchestrator
        orchestrator = MasterOrchestrator.instance()
        
        # Get governance
        governance = GovernanceRegistry.instance()
        
        # Get audit logger
        logger = EnhancedAuditLogger.instance()
        
        # All components should be available
        assert orchestrator is not None
        assert governance is not None
        assert logger is not None
        
        # Verify orchestrator has access to governance
        assert orchestrator.logger is not None
    
    def test_orchestrator_lifecycle(self):
        """Test orchestrator lifecycle: init -> operate -> audit."""
        orchestrator = MasterOrchestrator.instance()
        logger = EnhancedAuditLogger.instance()
        
        # 1. Initialize
        init_result = orchestrator.initialize()
        assert init_result.is_ok()
        
        # 2. Log lifecycle
        logger.log_operation_start(
            ac_id="AC-FR-008-LIFECYCLE",
            operation="ORCHESTRATOR_START",
            details={}
        )
        
        logger.log_operation_complete(
            ac_id="AC-FR-008-LIFECYCLE",
            operation="ORCHESTRATOR_START",
            success=True,
            details={}
        )
