"""
Phase 6.2 RED - Planning Orchestrator Integration Tests

Tests for threat modeling integration into planning workflow:
- Threat analysis triggered after DoR validation
- ThreatModelerAgent integration
- Threat report generation and integration into planning documents
- DoD validation with security items

Author: CORTEX Development Team
Version: 1.0 (Phase 6.2)
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from src.orchestrators.planning_orchestrator import PlanningOrchestrator
from src.cortex_agents.base_agent import AgentRequest, AgentResponse


@pytest.fixture
def cortex_root():
    """Provide cortex_root path for orchestrator initialization"""
    return str(Path(__file__).parent.parent.parent.absolute())


@pytest.fixture
def orchestrator(cortex_root):
    """Create PlanningOrchestrator instance for testing"""
    return PlanningOrchestrator(cortex_root=cortex_root)


# ============================================================================
# Phase 6.2: Planning Orchestrator Integration Tests
# ============================================================================

class TestThreatAnalysisIntegration:
    """Test threat analysis integration into planning workflow"""
    
    def test_analyze_threats_method_exists(self, orchestrator):
        """Test PlanningOrchestrator has analyze_threats() method"""
        assert hasattr(orchestrator, 'analyze_threats'), \
            "PlanningOrchestrator must have analyze_threats() method"
        assert callable(orchestrator.analyze_threats), \
            "analyze_threats must be callable"
    
    def test_analyze_threats_accepts_feature_description(self, orchestrator):
        """Test analyze_threats() accepts feature description"""
        result = orchestrator.analyze_threats(
            feature_description="Add user authentication with password login"
        )
        
        assert isinstance(result, dict), "analyze_threats() must return dict"
        assert 'success' in result or 'threats' in result, \
            "Result must contain success or threats key"
    
    def test_analyze_threats_with_plan_data_context(self, orchestrator):
        """Test analyze_threats() uses plan_data for context"""
        plan_data = {
            'metadata': {
                'feature_name': 'User Authentication',
                'priority': 'HIGH'
            },
            'phases': [
                {'name': 'Setup', 'tasks': ['Create login page']}
            ]
        }
        
        result = orchestrator.analyze_threats(
            feature_description="Implement login with email and password",
            plan_data=plan_data
        )
        
        assert result is not None, "Should return result with plan context"
        assert isinstance(result, dict), "Result must be dictionary"
    
    def test_analyze_threats_returns_threat_data(self, orchestrator):
        """Test analyze_threats() returns structured threat data"""
        result = orchestrator.analyze_threats(
            feature_description="Create REST API for user data"
        )
        
        # Should contain threat analysis results
        if result.get('success') is not False:
            assert 'threats' in result, "Result should contain threats list"
            assert 'mitigations' in result or 'recommendations' in result, \
                "Result should contain mitigations or recommendations"
    
    def test_analyze_threats_handles_empty_description(self, orchestrator):
        """Test analyze_threats() handles empty feature description"""
        result = orchestrator.analyze_threats(
            feature_description=""
        )
        
        # Should either fail gracefully or return empty results
        assert isinstance(result, dict), "Should return dict even for empty input"
    
    def test_analyze_threats_calls_threat_modeler_agent(self, orchestrator):
        """Test analyze_threats() uses ThreatModelerAgent"""
        # Verify ThreatModelerAgent is initialized
        assert hasattr(orchestrator, 'threat_modeler'), \
            "Orchestrator should have threat_modeler attribute"
        assert orchestrator.threat_modeler is not None, \
            "ThreatModelerAgent should be initialized"


class TestThreatReportIntegration:
    """Test threat report integration into planning documents"""
    
    def test_integrate_threats_into_plan_method_exists(self, orchestrator):
        """Test PlanningOrchestrator has integrate_threats_into_plan() method"""
        assert hasattr(orchestrator, 'integrate_threats_into_plan'), \
            "PlanningOrchestrator must have integrate_threats_into_plan() method"
    
    def test_integrate_threats_adds_security_section(self, orchestrator):
        """Test threat integration adds security section to plan"""
        
        plan_data = {
            'feature_name': 'User Authentication',
            'overview': 'This is a test plan'
        }
        
        threat_analysis = {
            'success': True,
            'threats': [
                {
                    'name': 'SQL Injection',
                    'risk_rating': 'HIGH',
                    'mitigation_strategies': [
                        {'name': 'Use parameterized queries'}
                    ]
                }
            ],
            'risk_level': 'HIGH'
        }
        
        updated_plan = orchestrator.integrate_threats_into_plan(
            plan_data=plan_data,
            threat_analysis=threat_analysis
        )
        
        assert isinstance(updated_plan, dict), "Should return updated plan dict"
        assert 'security' in updated_plan, "Should add security section to plan"
        assert 'threat_analysis' in updated_plan['security'], "Should include threat analysis"
    
    def test_integrate_threats_preserves_existing_content(self, orchestrator):
        """Test threat integration preserves existing plan content"""
        
        plan_data = {
            'feature_name': 'User Login',
            'phases': [
                {
                    'name': 'Phase 1: Setup',
                    'tasks': ['Task 1', 'Task 2']
                }
            ]
        }
        
        threat_analysis = {
            'success': True,
            'threats': [],
            'risk_level': 'LOW'
        }
        
        updated_plan = orchestrator.integrate_threats_into_plan(
            plan_data=plan_data,
            threat_analysis=threat_analysis
        )
        
        assert 'phases' in updated_plan, "Should preserve existing plan structure"
        assert updated_plan['phases'][0]['name'] == 'Phase 1: Setup', "Should preserve phase names"
        assert 'Task 1' in updated_plan['phases'][0]['tasks'], "Should preserve task list"
    
    def test_integrate_threats_with_critical_threats(self, orchestrator):
        """Test threat integration highlights critical threats"""
        
        plan_data = {
            'feature_name': 'API Endpoint',
            'overview': 'Test plan'
        }
        
        threat_analysis = {
            'success': True,
            'threats': [
                {
                    'name': 'Authentication Bypass',
                    'risk_rating': 'CRITICAL',
                    'description': 'Critical security issue'
                }
            ],
            'risk_level': 'CRITICAL',
            'critical_count': 1
        }
        
        updated_plan = orchestrator.integrate_threats_into_plan(
            plan_data=plan_data,
            threat_analysis=threat_analysis
        )
        
        assert 'security' in updated_plan, "Should have security section"
        assert len(updated_plan['security']['threat_analysis']['threats']) > 0, \
            "Should include critical threats in analysis"


class TestDoRThreatIntegration:
    """Test threat modeling injection after DoR validation"""
    
    @pytest.mark.skip(reason="Integration test - requires full DoR workflow")
    def test_threat_analysis_triggered_after_dor(self):
        """Test threat analysis automatically triggered after DoR validation"""
        orchestrator = PlanningOrchestrator()
        
        # This would test the full workflow:
        # DoR validation → threat analysis → plan generation
        # Requires mocking the entire planning pipeline
        pass
    
    def test_threat_analysis_uses_dor_responses(self, orchestrator):
        """Test threat analysis uses DoR responses for context"""
        
        dor_responses = {
            'Q1': 'Add user authentication',
            'Q3': 'Users can login with email and password',
            'Q6': 'Password hashing, session management'
        }
        
        # Extract feature description from DoR
        feature_description = dor_responses.get('Q3', '') + ' ' + dor_responses.get('Q6', '')
        
        result = orchestrator.analyze_threats(
            feature_description=feature_description
        )
        
        assert result is not None, "Should analyze threats from DoR responses"


class TestThreatModelerAgentInitialization:
    """Test ThreatModelerAgent initialization in orchestrator"""
    
    def test_orchestrator_initializes_threat_modeler(self, orchestrator):
        """Test PlanningOrchestrator initializes ThreatModelerAgent"""
        assert hasattr(orchestrator, 'threat_modeler'), \
            "Orchestrator should initialize ThreatModelerAgent"
    
    def test_threat_modeler_is_correct_type(self, orchestrator):
        """Test threat_modeler is ThreatModelerAgent instance"""
        from src.agents.security.threat_modeler_agent import ThreatModelerAgent
        
        if orchestrator.threat_modeler is not None:
            assert isinstance(orchestrator.threat_modeler, ThreatModelerAgent), \
                "threat_modeler should be ThreatModelerAgent instance"
    
    def test_threat_modeler_can_handle_requests(self, orchestrator):
        """Test ThreatModelerAgent in orchestrator can handle requests"""
        
        if orchestrator.threat_modeler is not None:
            request = AgentRequest(
                intent="analyze_threats",
                context={},
                user_message="Test feature"
            )
            
            can_handle = orchestrator.threat_modeler.can_handle(request)
            assert can_handle is True, "ThreatModelerAgent should handle analyze_threats"


class TestThreatAnalysisErrorHandling:
    """Test error handling in threat analysis integration"""
    
    def test_analyze_threats_handles_agent_failure(self, orchestrator):
        """Test analyze_threats() handles ThreatModelerAgent failures"""
        
        # Force an error by passing invalid data
        result = orchestrator.analyze_threats(
            feature_description=None  # Invalid input
        )
        
        # Should return error result, not raise exception
        assert isinstance(result, dict), "Should return dict on error"
        if 'success' in result:
            assert result['success'] is False, "Should indicate failure"
    
    def test_integrate_threats_handles_missing_threat_data(self, orchestrator):
        """Test threat integration handles missing threat data"""
        
        plan_data = {'feature_name': 'Test Feature', 'overview': 'Test plan'}
        threat_analysis = {}  # Empty threat analysis
        
        # Should handle gracefully
        result = orchestrator.integrate_threats_into_plan(
            plan_data=plan_data,
            threat_analysis=threat_analysis
        )
        
        assert isinstance(result, dict), "Should return dict even with missing data"
        assert 'overview' in result, "Should preserve original content"
    
    def test_integrate_threats_handles_malformed_plan(self, orchestrator):
        """Test threat integration handles malformed plan content"""
        
        plan_data = {}  # Empty plan
        threat_analysis = {
            'success': True,
            'threats': [],
            'risk_level': 'LOW'
        }
        
        result = orchestrator.integrate_threats_into_plan(
            plan_data=plan_data,
            threat_analysis=threat_analysis
        )
        
        assert isinstance(result, dict), "Should return dict for empty plan"
        assert 'security' in result, "Should add security section"


class TestThreatAnalysisPerformance:
    """Test threat analysis performance in planning workflow"""
    
    def test_threat_analysis_completes_quickly(self, orchestrator):
        """Test threat analysis completes within reasonable time"""
        import time
        
        start = time.time()
        result = orchestrator.analyze_threats(
            feature_description="Simple feature: add user profile page"
        )
        duration = time.time() - start
        
        assert duration < 10, f"Threat analysis took {duration:.2f}s (target: <10s)"
    
    def test_threat_integration_is_fast(self, orchestrator):
        """Test threat report integration is fast"""
        import time
        
        plan_data = {
            'feature_name': 'Large Test Plan',
            'phases': [{'name': f'Phase {i}', 'tasks': ['Task 1', 'Task 2']} for i in range(20)]
        }
        threat_analysis = {
            'success': True,
            'threats': [{'name': 'Test', 'risk_rating': 'LOW'}] * 10,
            'risk_level': 'LOW'
        }
        
        start = time.time()
        result = orchestrator.integrate_threats_into_plan(
            plan_data=plan_data,
            threat_analysis=threat_analysis
        )
        duration = time.time() - start
        
        assert duration < 1, f"Integration took {duration:.2f}s (target: <1s)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
