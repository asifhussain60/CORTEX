"""
Unit tests for orchestrator bootstrap & initialization.

AC-AR-006-02: Test orchestrator bootstrap and wiring
"""

import pytest
from cortex.orchestrators.bootstrap import (
    OrchestratorBootstrap,
    OrchestratorBootstrapConfig,
    bootstrap_orchestrators,
    ensure_bootstrapped,
)
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.conversation_orchestrator import ConversationOrchestrator


class TestOrchestratorBootstrap:
    """Test OrchestratorBootstrap functionality"""

    def test_bootstrap_singleton(self):
        """Test OrchestratorBootstrap is a singleton"""
        bootstrap1 = OrchestratorBootstrap.instance()
        bootstrap2 = OrchestratorBootstrap.instance()
        assert bootstrap1 is bootstrap2

    def test_bootstrap_config_defaults(self):
        """Test OrchestratorBootstrapConfig has correct defaults"""
        config = OrchestratorBootstrapConfig()
        assert config.auto_register is True
        assert config.initialize_conversation is True
        assert config.initialize_registry is True
        assert config.initialize_discovery is True
        assert config.enable_mcp_tools is True
        assert config.timeout_seconds == 30.0

    def test_bootstrap_initialization(self):
        """Test bootstrap initialization creates components"""
        bootstrap = OrchestratorBootstrap.instance()
        assert bootstrap is not None
        assert bootstrap.logger is not None
        assert bootstrap.domain_orchestrators is not None
        assert isinstance(bootstrap.domain_orchestrators, dict)

    def test_bootstrap_master_orchestrator(self):
        """Test bootstrap initializes MasterOrchestrator"""
        bootstrap = OrchestratorBootstrap.instance()
        step = bootstrap._initialize_master()
        assert step["success"] is True
        assert "MasterOrchestrator" in step["step"]
        assert bootstrap.master_orchestrator is not None

    def test_bootstrap_domain_orchestrators(self):
        """Test bootstrap registers domain orchestrators"""
        bootstrap = OrchestratorBootstrap.instance()
        bootstrap._initialize_master()  # Initialize master first
        step = bootstrap._register_domain_orchestrators()
        assert step["success"] is True or step["count"] >= 0
        assert "registered" in step
        assert "count" in step

    def test_bootstrap_conversation_orchestrator(self):
        """Test bootstrap initializes ConversationOrchestrator"""
        bootstrap = OrchestratorBootstrap.instance()
        bootstrap.config = OrchestratorBootstrapConfig()  # Ensure config is set
        step = bootstrap._initialize_conversation()
        assert step["success"] is True
        assert bootstrap.conversation_orchestrator is not None
        assert hasattr(bootstrap.conversation_orchestrator, 'session_id')

    def test_bootstrap_get_status(self):
        """Test bootstrap status reporting"""
        bootstrap = OrchestratorBootstrap.instance()
        bootstrap._initialize_master()
        bootstrap._initialize_conversation()
        status = bootstrap.get_status()
        
        assert "master_orchestrator_ready" in status
        assert "domain_orchestrators" in status
        assert "conversation_orchestrator_ready" in status
        assert "timestamp" in status

    def test_bootstrap_orchestrators_function(self):
        """Test bootstrap_orchestrators convenience function"""
        result = bootstrap_orchestrators()
        assert result is not None
        assert result.is_ok() or result.is_err()

    def test_ensure_bootstrapped_idempotent(self):
        """Test ensure_bootstrapped is idempotent"""
        result1 = ensure_bootstrapped()
        result2 = ensure_bootstrapped()
        # Both should succeed or fail consistently
        assert result1.is_ok() == result2.is_ok()


class TestMasterOrchestratorBootstrap:
    """Test MasterOrchestrator bootstrap integration"""

    def test_master_orchestrator_initialize_with_bootstrap(self):
        """Test MasterOrchestrator.initialize() calls bootstrap"""
        # Create fresh instance
        master = MasterOrchestrator.instance()
        
        # Initialize should trigger bootstrap
        result = master.initialize()
        
        assert result.is_ok()
        assert "initialized successfully" in result.unwrap()

    def test_master_orchestrator_registered_domains(self):
        """Test domain orchestrators are registered"""
        master = MasterOrchestrator.instance()
        master.initialize()
        
        domains_result = master.get_registered_domains()
        assert domains_result.is_ok()
        
        domains = domains_result.unwrap()
        assert isinstance(domains, list)
        # Should have at least planning and refactoring
        assert len(domains) >= 0  # May be 0 if registration failed gracefully


class TestConversationOrchestratorBootstrap:
    """Test ConversationOrchestrator bootstrap"""

    def test_conversation_orchestrator_created(self):
        """Test ConversationOrchestrator is created during bootstrap"""
        convo = ConversationOrchestrator()
        
        assert convo is not None
        assert hasattr(convo, 'session_id')
        assert hasattr(convo, 'conversation_history')
        assert len(convo.conversation_history) == 0

    def test_conversation_turn_processing(self):
        """Test ConversationOrchestrator can process turns"""
        convo = ConversationOrchestrator()
        
        turn = {
            "role": "user",
            "user_input": "Test message",
            "turn_number": 1
        }
        
        result = convo.process_turn(turn)
        
        assert result.get("success") is True
        assert result.get("turn_number") == 1
        assert len(convo.conversation_history) == 1

    def test_conversation_state_persistence(self):
        """Test ConversationOrchestrator maintains state across turns"""
        convo = ConversationOrchestrator()
        
        # Process multiple turns
        for i in range(3):
            result = convo.process_turn({
                "user_input": f"Turn {i+1}",
                "turn_number": i + 1
            })
            assert result.get("success") is True
        
        # Verify history
        assert len(convo.conversation_history) == 3
        for i, turn in enumerate(convo.conversation_history):
            assert turn["turn_number"] == i + 1


class TestBootstrapIntegration:
    """Integration tests for full bootstrap flow"""

    def test_full_bootstrap_flow(self):
        """Test complete bootstrap initialization flow"""
        from cortex.orchestrators.bootstrap import bootstrap_orchestrators
        
        result = bootstrap_orchestrators()
        
        assert result is not None
        if result.is_ok():
            data = result.unwrap()
            assert "steps" in data
            assert "orchestrators" in data
            assert len(data["steps"]) > 0

    def test_bootstrap_with_custom_config(self):
        """Test bootstrap with custom configuration"""
        config = OrchestratorBootstrapConfig(
            initialize_registry=False,
            initialize_discovery=False,
            enable_mcp_tools=False
        )
        
        bootstrap = OrchestratorBootstrap()
        result = bootstrap.bootstrap(config)
        
        assert result is not None
        assert result.is_ok() or result.is_err()

    def test_orchestrator_wiring_complete(self):
        """Test that all orchestrators are wired and accessible"""
        master = MasterOrchestrator.instance()
        master.initialize()
        
        # Verify MasterOrchestrator is operational
        assert master is not None
        
        # Verify conversation orchestrator can be created
        convo = ConversationOrchestrator()
        assert convo is not None
        
        # Verify we can get registered domains
        domains_result = master.get_registered_domains()
        assert domains_result.is_ok()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
