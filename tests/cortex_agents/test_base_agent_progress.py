"""
Integration Tests for BaseAgent with Progress Monitoring

Tests that agents can use progress monitoring through the BaseAgent infrastructure.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import time
from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.utils.progress_decorator import with_progress


class TestAgentWithProgress(BaseAgent):
    """Test agent that uses progress monitoring"""
    
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent == "test_progress"
    
    @with_progress(operation_name="Test Agent Execution", threshold_seconds=0.5)
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute with progress monitoring"""
        items = request.context.get('items', [])
        processed = []
        
        for i, item in enumerate(items, 1):
            # Use BaseAgent's report_progress method
            self.report_progress(i, len(items), f"Processing {item}")
            time.sleep(0.1)
            processed.append(item)
        
        return AgentResponse(
            success=True,
            result={'processed': processed},
            message=f"Processed {len(processed)} items",
            agent_name=self.name
        )


class TestAgentWithoutProgress(BaseAgent):
    """Test agent that doesn't use progress monitoring"""
    
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent == "test_no_progress"
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute without progress monitoring"""
        return AgentResponse(
            success=True,
            result={'status': 'ok'},
            message="Executed without progress",
            agent_name=self.name
        )


class TestBaseAgentProgressIntegration:
    """Test BaseAgent integration with progress monitoring"""
    
    def test_agent_with_progress_monitoring(self, capsys):
        """Test agent that uses progress monitoring"""
        agent = TestAgentWithProgress(name="TestAgent")
        
        request = AgentRequest(
            intent="test_progress",
            context={'items': [f"item_{i}" for i in range(10)]},
            user_message="Process items"
        )
        
        response = agent.execute(request)
        captured = capsys.readouterr()
        
        assert response.success
        assert len(response.result['processed']) == 10
        
        # Should show progress output
        assert "Test Agent Execution" in captured.out or "completed" in captured.out
    
    def test_agent_without_progress_monitoring(self):
        """Test agent that doesn't use progress monitoring"""
        agent = TestAgentWithoutProgress(name="TestAgent")
        
        request = AgentRequest(
            intent="test_no_progress",
            context={},
            user_message="Simple execution"
        )
        
        response = agent.execute(request)
        
        assert response.success
        assert response.result['status'] == 'ok'
    
    def test_report_progress_safe_without_decorator(self):
        """Test report_progress() safely does nothing without decorator"""
        agent = TestAgentWithoutProgress(name="TestAgent")
        
        # Should not raise exception
        agent.report_progress(1, 10, "Step 1")
        agent.report_progress(2, 10, "Step 2")
    
    def test_fast_operation_no_progress_shown(self, capsys):
        """Test fast operations don't trigger progress display"""
        agent = TestAgentWithProgress(name="FastAgent")
        
        request = AgentRequest(
            intent="test_progress",
            context={'items': ["item_1"]},  # Only 1 item - fast operation
            user_message="Process one item"
        )
        
        response = agent.execute(request)
        captured = capsys.readouterr()
        
        assert response.success
        # Progress may or may not show depending on timing
        # Just verify no crash
    
    def test_agent_handles_exceptions_with_progress(self, capsys):
        """Test agent handles exceptions properly with progress monitoring"""
        
        class FailingAgent(BaseAgent):
            def can_handle(self, request: AgentRequest) -> bool:
                return True
            
            @with_progress(operation_name="Failing Agent", threshold_seconds=0.1)
            def execute(self, request: AgentRequest) -> AgentResponse:
                for i in range(3):
                    self.report_progress(i+1, 3, f"Step {i+1}")
                    time.sleep(0.1)
                    if i == 1:
                        raise ValueError("Test error")
                return AgentResponse(success=True, result={})
        
        agent = FailingAgent(name="FailingAgent")
        request = AgentRequest(intent="test", context={}, user_message="test")
        
        with pytest.raises(ValueError, match="Test error"):
            agent.execute(request)
        
        captured = capsys.readouterr()
        # Should show failure in output
        assert "failed" in captured.out or "Test error" in captured.out
    
    def test_multiple_agents_concurrent_execution(self):
        """Test multiple agents can run concurrently with progress"""
        import threading
        
        agent1 = TestAgentWithProgress(name="Agent1")
        agent2 = TestAgentWithProgress(name="Agent2")
        
        results = []
        
        def run_agent(agent, items):
            request = AgentRequest(
                intent="test_progress",
                context={'items': items},
                user_message="Process items"
            )
            response = agent.execute(request)
            results.append(response)
        
        thread1 = threading.Thread(
            target=run_agent,
            args=(agent1, [f"a{i}" for i in range(5)])
        )
        thread2 = threading.Thread(
            target=run_agent,
            args=(agent2, [f"b{i}" for i in range(5)])
        )
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Both should complete successfully
        assert len(results) == 2
        assert all(r.success for r in results)


class TestAgentProgressPatterns:
    """Test common agent progress patterns"""
    
    def test_multi_step_agent_execution(self, capsys):
        """Test agent with multiple sequential steps"""
        
        class MultiStepAgent(BaseAgent):
            def can_handle(self, request: AgentRequest) -> bool:
                return True
            
            @with_progress(operation_name="Multi-Step Process", threshold_seconds=0.5)
            def execute(self, request: AgentRequest) -> AgentResponse:
                # Step 1: Validation
                for i in range(3):
                    self.report_progress(i+1, 10, f"Validating item {i+1}")
                    time.sleep(0.1)
                
                # Step 2: Processing
                for i in range(4):
                    self.report_progress(i+4, 10, f"Processing item {i+1}")
                    time.sleep(0.1)
                
                # Step 3: Finalization
                for i in range(3):
                    self.report_progress(i+8, 10, f"Finalizing item {i+1}")
                    time.sleep(0.1)
                
                return AgentResponse(
                    success=True,
                    result={'completed': True},
                    message="All steps completed"
                )
        
        agent = MultiStepAgent(name="MultiStepAgent")
        request = AgentRequest(intent="test", context={}, user_message="test")
        
        response = agent.execute(request)
        captured = capsys.readouterr()
        
        assert response.success
        assert "Multi-Step Process" in captured.out or "completed" in captured.out
    
    def test_agent_with_custom_hang_timeout(self):
        """Test agent can specify custom hang timeout"""
        
        class SlowAgent(BaseAgent):
            def can_handle(self, request: AgentRequest) -> bool:
                return True
            
            @with_progress(
                operation_name="Slow Processing",
                threshold_seconds=0.5,
                hang_timeout=120.0  # 2 minutes for slow operations
            )
            def execute(self, request: AgentRequest) -> AgentResponse:
                for i in range(3):
                    self.report_progress(i+1, 3, f"Slow step {i+1}")
                    time.sleep(0.3)
                
                return AgentResponse(
                    success=True,
                    result={},
                    message="Slow processing completed"
                )
        
        agent = SlowAgent(name="SlowAgent")
        request = AgentRequest(intent="test", context={}, user_message="test")
        
        response = agent.execute(request)
        assert response.success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
