"""
Tests for Demo Orchestrator

Validates discovery command routing and demonstration content generation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.operations.modules.demo.demo_orchestrator import DemoOrchestrator, handle_discovery_request


class TestDemoOrchestrator:
    """Test Demo Orchestrator functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return DemoOrchestrator()
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None
        assert orchestrator.brain_path is not None
        assert orchestrator.logger is not None
    
    def test_discover_cortex_trigger(self, orchestrator):
        """Test 'discover cortex' triggers introduction_discovery template"""
        result = orchestrator.handle_discovery("discover cortex")
        
        assert result is not None
        assert 'template_id' in result
        assert result['template_id'] == 'introduction_discovery'
        assert 'context' in result
    
    def test_explore_cortex_trigger(self, orchestrator):
        """Test 'explore cortex' triggers introduction_discovery template"""
        result = orchestrator.handle_discovery("explore cortex")
        
        assert result['template_id'] == 'introduction_discovery'
    
    def test_cortex_demo_trigger(self, orchestrator):
        """Test 'cortex demo' triggers introduction_discovery template"""
        result = orchestrator.handle_discovery("cortex demo")
        
        assert result['template_id'] == 'introduction_discovery'
    
    def test_what_can_you_do_trigger(self, orchestrator):
        """Test 'what can you do' triggers introduction_discovery template"""
        result = orchestrator.handle_discovery("what can you do?")
        
        assert result['template_id'] == 'introduction_discovery'
    
    def test_show_capabilities_trigger(self, orchestrator):
        """Test 'show capabilities' triggers introduction_discovery template"""
        result = orchestrator.handle_discovery("show me what cortex can do")
        
        assert result['template_id'] == 'introduction_discovery'


class TestSpecificDemos:
    """Test specific demonstration routing"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return DemoOrchestrator()
    
    def test_demo_planning_detection(self, orchestrator):
        """Test 'demo planning' routes to planning demo"""
        result = orchestrator.handle_discovery("demo planning")
        
        assert 'context' in result
        assert result['context'].get('demo_type') == 'planning'
        assert 'Planning System 2.0' in result['context'].get('demo_content', '')
    
    def test_demo_tdd_detection(self, orchestrator):
        """Test 'demo tdd' routes to TDD demo"""
        result = orchestrator.handle_discovery("demo tdd")
        
        assert result['context'].get('demo_type') == 'tdd'
        assert 'RED→GREEN→REFACTOR' in result['context'].get('demo_content', '')
    
    def test_demo_view_discovery_detection(self, orchestrator):
        """Test 'demo view discovery' routes to view discovery demo"""
        result = orchestrator.handle_discovery("show view discovery")
        
        assert result['context'].get('demo_type') == 'view_discovery'
        assert 'View Discovery' in result['context'].get('demo_content', '')
    
    def test_demo_feedback_detection(self, orchestrator):
        """Test 'demo feedback' routes to feedback demo"""
        result = orchestrator.handle_discovery("demo feedback")
        
        assert result['context'].get('demo_type') == 'feedback'
        assert 'Feedback System' in result['context'].get('demo_content', '')
    
    def test_demo_upgrade_detection(self, orchestrator):
        """Test 'demo upgrade' routes to upgrade demo"""
        result = orchestrator.handle_discovery("demo upgrade")
        
        assert result['context'].get('demo_type') == 'upgrade'
        assert 'Universal Upgrade System' in result['context'].get('demo_content', '')
    
    def test_demo_brain_detection(self, orchestrator):
        """Test 'show brain architecture' routes to brain demo"""
        result = orchestrator.handle_discovery("show brain architecture")
        
        assert result['context'].get('demo_type') == 'brain'
        assert 'Brain Architecture' in result['context'].get('demo_content', '')


class TestContextInjection:
    """Test context data injection"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return DemoOrchestrator()
    
    def test_context_includes_user_request(self, orchestrator):
        """Test context includes original user request"""
        user_request = "discover cortex capabilities"
        result = orchestrator.handle_discovery(user_request)
        
        assert 'context' in result
        assert result['context'].get('user_request') == user_request
    
    def test_context_includes_timestamp(self, orchestrator):
        """Test context includes timestamp"""
        result = orchestrator.handle_discovery("discover cortex")
        
        assert 'context' in result
        assert 'timestamp' in result['context']
    
    def test_custom_context_preserved(self, orchestrator):
        """Test custom context is preserved"""
        custom_context = {'custom_key': 'custom_value'}
        result = orchestrator.handle_discovery("discover cortex", custom_context)
        
        assert result['context'].get('custom_key') == 'custom_value'


class TestConvenienceFunction:
    """Test convenience function"""
    
    def test_handle_discovery_request(self):
        """Test convenience function works"""
        result = handle_discovery_request("discover cortex")
        
        assert result is not None
        assert result['template_id'] == 'introduction_discovery'


class TestCaseInsensitivity:
    """Test case insensitive matching"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return DemoOrchestrator()
    
    def test_uppercase_trigger(self, orchestrator):
        """Test uppercase triggers work"""
        result = orchestrator.handle_discovery("DISCOVER CORTEX")
        assert result['template_id'] == 'introduction_discovery'
    
    def test_mixed_case_trigger(self, orchestrator):
        """Test mixed case triggers work"""
        result = orchestrator.handle_discovery("Discover Cortex")
        assert result['template_id'] == 'introduction_discovery'
    
    def test_lowercase_trigger(self, orchestrator):
        """Test lowercase triggers work"""
        result = orchestrator.handle_discovery("discover cortex")
        assert result['template_id'] == 'introduction_discovery'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
