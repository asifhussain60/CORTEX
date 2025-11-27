"""
CORTEX 3.0 Phase 1 Foundation Integration Test
==============================================

Validates that all core 3.0 components work together correctly:
- Dual-Channel Memory system
- Enhanced Agent orchestration
- Smart Context Intelligence
- Unified Interface coordination

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

# Import CORTEX 3.0 components
from src.cortex_3_0.unified_interface import (
    CortexUnifiedInterface, 
    CortexRequest, 
    CortexResponse,
    CortexMode,
    RequestComplexity,
    RequestAnalyzer
)
from src.cortex_3_0.dual_channel_memory import DualChannelMemory, ChannelType
from src.cortex_3_0.enhanced_agents import EnhancedAgentSystem
from src.cortex_3_0.smart_context_intelligence import SmartContextIntelligence


class TestCORTEX30Foundation:
    """Test suite for CORTEX 3.0 foundation components"""
    
    @pytest.fixture
    def temp_brain_path(self):
        """Create temporary brain directory for testing"""
        temp_dir = tempfile.mkdtemp()
        brain_path = Path(temp_dir) / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        # Create required subdirectories
        (brain_path / "tier1").mkdir(exist_ok=True)
        (brain_path / "tier2").mkdir(exist_ok=True)
        (brain_path / "tier3").mkdir(exist_ok=True)
        
        yield str(brain_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
    @pytest.fixture
    def cortex_interface(self, temp_brain_path):
        """Create CORTEX 3.0 unified interface for testing"""
        config = {
            "cortex_30": {
                "enabled": True,
                "mode": "test"
            }
        }
        return CortexUnifiedInterface(temp_brain_path, config)
        
    def test_request_analyzer_complexity_detection(self):
        """Test that request analyzer correctly detects complexity levels"""
        analyzer = RequestAnalyzer()
        
        # Simple request
        simple_request = CortexRequest(
            request_id="test_1",
            user_message="Show me the current status",
            context={}
        )
        analysis = analyzer.analyze_request(simple_request)
        assert analysis["complexity"] == RequestComplexity.SIMPLE
        
        # Moderate request  
        moderate_request = CortexRequest(
            request_id="test_2",
            user_message="Create a new authentication feature and add tests",
            context={}
        )
        analysis = analyzer.analyze_request(moderate_request)
        assert analysis["complexity"] == RequestComplexity.MODERATE
        
        # Complex request
        complex_request = CortexRequest(
            request_id="test_3", 
            user_message="Design and implement a comprehensive user management system with multiple authentication methods and role-based access control",
            context={}
        )
        analysis = analyzer.analyze_request(complex_request)
        assert analysis["complexity"] == RequestComplexity.COMPLEX
        
        # Adaptive request
        adaptive_request = CortexRequest(
            request_id="test_4",
            user_message="Predict what features I'll need next and suggest optimizations based on my usage patterns",
            context={}
        )
        analysis = analyzer.analyze_request(adaptive_request)
        assert analysis["complexity"] == RequestComplexity.ADAPTIVE
        
    def test_mode_selection_logic(self):
        """Test that optimal mode is selected based on complexity"""
        analyzer = RequestAnalyzer()
        
        # Simple -> 2.0 compatibility
        simple_request = CortexRequest("test_1", "Show status", {})
        analysis = analyzer.analyze_request(simple_request)
        assert analysis["optimal_mode"] == CortexMode.CORTEX_20_COMPATIBILITY
        
        # Complex -> 3.0 hybrid
        complex_request = CortexRequest("test_2", "Plan and coordinate multiple features", {})
        analysis = analyzer.analyze_request(complex_request)
        assert analysis["optimal_mode"] == CortexMode.CORTEX_30_HYBRID
        
        # Adaptive -> 3.0 full
        adaptive_request = CortexRequest("test_3", "Predict and optimize my workflow", {})
        analysis = analyzer.analyze_request(adaptive_request)
        assert analysis["optimal_mode"] == CortexMode.CORTEX_30_FULL
        
    def test_capability_identification(self):
        """Test that required capabilities are correctly identified"""
        analyzer = RequestAnalyzer()
        
        # Memory capability
        memory_request = CortexRequest("test_1", "Continue from where we left off yesterday", {})
        analysis = analyzer.analyze_request(memory_request)
        assert "dual_channel_memory" in analysis["required_capabilities"]
        
        # Agent coordination capability
        coordination_request = CortexRequest("test_2", "Coordinate multiple teams to deliver this feature", {})
        analysis = analyzer.analyze_request(coordination_request)
        assert "enhanced_agents" in analysis["required_capabilities"]
        
        # Smart context capability
        smart_request = CortexRequest("test_3", "Intelligently suggest the best approach", {})
        analysis = analyzer.analyze_request(smart_request)
        assert "smart_context_intelligence" in analysis["required_capabilities"]
        
    @pytest.mark.asyncio
    async def test_dual_channel_memory_integration(self, temp_brain_path):
        """Test dual-channel memory system integration"""
        dual_memory = DualChannelMemory(temp_brain_path)
        
        # Test conversational channel
        conv_result = await dual_memory.store_conversational_context(
            conversation_id="test_conv_1",
            messages=[
                {"role": "user", "content": "Hello CORTEX"},
                {"role": "assistant", "content": "Hello! How can I help you?"}
            ],
            metadata={"session_type": "initial"}
        )
        assert conv_result["success"] == True
        assert conv_result["channel"] == ChannelType.CONVERSATIONAL
        
        # Test traditional channel
        trad_result = await dual_memory.store_traditional_execution(
            command="status check",
            result={"status": "operational", "components": ["tier1", "tier2", "tier3"]},
            metadata={"execution_type": "direct"}
        )
        assert trad_result["success"] == True
        assert trad_result["channel"] == ChannelType.TRADITIONAL
        
        # Test unified narrative creation
        narrative = await dual_memory.create_unified_narrative(
            conversational_context={"conversation_id": "test_conv_1"},
            traditional_context={"command": "status check"},
            fusion_strategy="intelligent"
        )
        assert narrative["success"] == True
        assert "summary" in narrative
        assert narrative["strategy"] == "intelligent"
        
    @pytest.mark.asyncio
    async def test_enhanced_agents_integration(self):
        """Test enhanced agent system integration"""
        agent_system = EnhancedAgentSystem()
        
        # Test workflow execution
        workflow_result = await agent_system.execute_enhanced_workflow(
            "Create a simple test feature with documentation"
        )
        assert workflow_result["success"] == True
        assert "workflow_id" in workflow_result
        assert len(workflow_result["agents_involved"]) > 0
        
        # Test agent coordination
        agents_status = agent_system.get_agent_status()
        assert "primary_agents" in agents_status
        assert "sub_agents" in agents_status
        assert agents_status["corpus_callosum"]["status"] == "operational"
        
    @pytest.mark.asyncio
    async def test_smart_context_integration(self, temp_brain_path):
        """Test smart context intelligence integration"""
        smart_context = SmartContextIntelligence(temp_brain_path)
        
        # Test intelligent session start
        session_id = await smart_context.start_intelligent_session("I want to build a feature")
        assert session_id is not None
        assert session_id.startswith("session_")
        
        # Test context assembly
        context = await smart_context.get_intelligent_context(
            session_id, "Add authentication to my project"
        )
        assert "assembled_context" in context
        assert "recommendations" in context
        assert "confidence_score" in context
        
        # Test memory optimization
        optimization_result = smart_context.memory_manager.optimize_memory_usage()
        assert optimization_result["success"] == True
        assert "memory_freed_mb" in optimization_result
        
    @pytest.mark.asyncio
    async def test_unified_interface_processing(self, cortex_interface):
        """Test unified interface request processing"""
        
        # Test simple request (2.0 compatibility mode)
        simple_response = await cortex_interface.process_request(
            "Show system status",
            context={"test": True}
        )
        assert simple_response.success == True
        assert simple_response.mode_used == CortexMode.CORTEX_20_COMPATIBILITY
        assert simple_response.complexity_detected == RequestComplexity.SIMPLE
        
        # Test moderate request (hybrid mode)
        moderate_response = await cortex_interface.process_request(
            "Create a feature plan and coordinate the implementation",
            context={"test": True}
        )
        assert moderate_response.success == True
        assert moderate_response.mode_used == CortexMode.CORTEX_30_HYBRID
        assert moderate_response.complexity_detected == RequestComplexity.MODERATE
        
    @pytest.mark.asyncio
    async def test_session_continuity(self, cortex_interface):
        """Test session continuity across requests"""
        
        session_id = "test_session_123"
        
        # First request
        response1 = await cortex_interface.process_request(
            "Start working on authentication feature",
            context={"project": "test_app"},
            session_id=session_id
        )
        assert response1.success == True
        assert response1.session_id == session_id
        
        # Second request in same session
        response2 = await cortex_interface.process_request(
            "Continue with the authentication work",
            context={"project": "test_app"},
            session_id=session_id
        )
        assert response2.success == True
        assert response2.session_id == session_id
        
        # Verify session is tracked
        assert session_id in cortex_interface.active_sessions
        session_data = cortex_interface.active_sessions[session_id]
        assert len(session_data["requests"]) == 2
        
    def test_system_status_reporting(self, cortex_interface):
        """Test comprehensive system status reporting"""
        status = cortex_interface.get_system_status()
        
        assert status["cortex_version"] == "3.0"
        assert "unified_interface" in status
        assert "dual_channel_memory" in status
        assert "enhanced_agents" in status
        assert "smart_context_intelligence" in status
        assert "compatibility" in status
        
        # Check that all subsystems report operational
        assert status["unified_interface"]["status"] == "operational"
        assert status["dual_channel_memory"]["status"] == "operational"
        assert status["enhanced_agents"]["status"] == "operational"
        assert status["smart_context_intelligence"]["status"] == "operational"
        
        # Check compatibility
        assert status["compatibility"]["cortex_20"] == "full_compatibility"
        
    @pytest.mark.asyncio
    async def test_error_handling_and_fallback(self, cortex_interface):
        """Test error handling and fallback to 2.0 compatibility"""
        
        # Test with malformed request
        response = await cortex_interface.process_request(
            "",  # Empty request
            context={"force_error": True}
        )
        
        # Should still get a response, likely with error handling
        assert isinstance(response, CortexResponse)
        assert response.request_id is not None
        
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, cortex_interface):
        """Test performance benchmarks for Phase 1 foundation"""
        
        start_time = datetime.now()
        
        # Process multiple requests to test performance
        responses = []
        for i in range(5):
            response = await cortex_interface.process_request(
                f"Test request {i}",
                context={"benchmark": True}
            )
            responses.append(response)
            
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # All requests should complete successfully
        assert all(r.success for r in responses)
        
        # Performance benchmark: 5 requests should complete in under 10 seconds
        assert total_duration < 10.0
        
        # Individual request performance
        avg_duration = sum(r.duration_seconds for r in responses) / len(responses)
        assert avg_duration < 2.0  # Average under 2 seconds per request
        
    @pytest.mark.asyncio 
    async def test_graceful_shutdown(self, cortex_interface):
        """Test graceful shutdown of all systems"""
        
        # Create some active sessions
        await cortex_interface.process_request(
            "Test request", 
            session_id="test_session_shutdown"
        )
        
        # Ensure session exists
        assert "test_session_shutdown" in cortex_interface.active_sessions
        
        # Test shutdown
        await cortex_interface.shutdown()
        
        # Should handle gracefully without errors
        # Note: In actual implementation, would check session cleanup


class TestPhase1Completion:
    """Verify Phase 1 foundation completion criteria"""
    
    def test_all_core_components_exist(self):
        """Verify all core 3.0 components are implemented"""
        
        try:
            # Test imports work
            from src.cortex_3_0.dual_channel_memory import DualChannelMemory
            from src.cortex_3_0.enhanced_agents import EnhancedAgentSystem 
            from src.cortex_3_0.smart_context_intelligence import SmartContextIntelligence
            from src.cortex_3_0.unified_interface import CortexUnifiedInterface
            
            core_components_exist = True
        except ImportError as e:
            core_components_exist = False
            
        assert core_components_exist, "All core 3.0 components must be importable"
        
    def test_unified_interface_coordinates_all_systems(self, temp_brain_path):
        """Verify unified interface properly coordinates all systems"""
        
        interface = CortexUnifiedInterface(temp_brain_path)
        
        # Check all systems are initialized
        assert interface.dual_channel_memory is not None
        assert interface.enhanced_agents is not None
        assert interface.smart_context is not None
        assert interface.request_analyzer is not None
        
        # Check system status includes all components
        status = interface.get_system_status()
        required_components = [
            "dual_channel_memory", 
            "enhanced_agents",
            "smart_context_intelligence",
            "unified_interface"
        ]
        
        for component in required_components:
            assert component in status, f"Component {component} missing from system status"
            
    def test_backward_compatibility_maintained(self, temp_brain_path):
        """Verify 2.0 compatibility is maintained"""
        
        interface = CortexUnifiedInterface(temp_brain_path)
        
        # Should have 2.0 systems available
        assert hasattr(interface, 'universal_operations')
        assert hasattr(interface, 'intent_router')
        
        # Should support 2.0 compatibility mode
        analyzer = interface.request_analyzer
        simple_request = CortexRequest("test", "show status", {})
        analysis = analyzer.analyze_request(simple_request)
        
        assert analysis["optimal_mode"] == CortexMode.CORTEX_20_COMPATIBILITY
        
    @pytest.fixture
    def temp_brain_path(self):
        """Create temporary brain directory for testing"""
        temp_dir = tempfile.mkdtemp()
        brain_path = Path(temp_dir) / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        # Create required subdirectories
        (brain_path / "tier1").mkdir(exist_ok=True)
        (brain_path / "tier2").mkdir(exist_ok=True) 
        (brain_path / "tier3").mkdir(exist_ok=True)
        
        yield str(brain_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Run the tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])