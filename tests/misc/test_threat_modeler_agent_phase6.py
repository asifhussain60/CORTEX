"""
Phase 6.1 RED - Comprehensive ThreatModeler Agent Tests

Tests for enhanced ThreatModeler agent with BaseAgent interface integration.
This file focuses on cortex_agents framework compliance.

Author: CORTEX Development Team
Version: 1.0 (Phase 6.1)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.agents.security.threat_modeler_agent import (
    ThreatModelerAgent,
    EnhancedThreat,
    ThreatReport,
    RiskRating,
    OWASPCategory,
    MitigationStrategy
)
from src.workflows.stages.threat_modeler import ThreatCategory


# ============================================================================
# Phase 6.1: BaseAgent Interface Compliance Tests
# ============================================================================

class TestThreatModelerAgentInterface:
    """Test that ThreatModelerAgent properly implements BaseAgent interface"""
    
    def test_agent_inherits_from_base_agent(self):
        """Test ThreatModelerAgent inherits from BaseAgent"""
        agent = ThreatModelerAgent()
        assert isinstance(agent, BaseAgent), "ThreatModelerAgent must inherit from BaseAgent"
    
    def test_agent_has_can_handle_method(self):
        """Test agent implements can_handle() method"""
        agent = ThreatModelerAgent()
        assert hasattr(agent, 'can_handle'), "ThreatModelerAgent must implement can_handle()"
        assert callable(agent.can_handle), "can_handle must be callable"
    
    def test_agent_has_execute_method(self):
        """Test agent implements execute() method"""
        agent = ThreatModelerAgent()
        assert hasattr(agent, 'execute'), "ThreatModelerAgent must implement execute()"
        assert callable(agent.execute), "execute must be callable"
    
    def test_can_handle_accepts_agent_request(self):
        """Test can_handle() accepts AgentRequest objects"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature": "auth"},
            user_message="Add user authentication"
        )
        
        result = agent.can_handle(request)
        assert isinstance(result, bool), "can_handle() must return boolean"
    
    def test_can_handle_recognizes_threat_modeling_intents(self):
        """Test can_handle() recognizes threat modeling intents"""
        agent = ThreatModelerAgent()
        
        valid_intents = [
            "analyze_threats",
            "threat_model",
            "security_analysis",
            "stride_analysis",
            "identify_threats"
        ]
        
        for intent in valid_intents:
            request = AgentRequest(
                intent=intent,
                context={},
                user_message="Analyze security threats"
            )
            
            assert agent.can_handle(request) is True, \
                f"Agent should handle intent: {intent}"
    
    def test_can_handle_rejects_unrelated_intents(self):
        """Test can_handle() rejects unrelated intents"""
        agent = ThreatModelerAgent()
        
        invalid_intents = [
            "plan_feature",
            "generate_code",
            "run_tests",
            "create_documentation",
            "refactor_code"
        ]
        
        for intent in invalid_intents:
            request = AgentRequest(
                intent=intent,
                context={},
                user_message="Do something"
            )
            
            assert agent.can_handle(request) is False, \
                f"Agent should not handle intent: {intent}"
    
    def test_execute_accepts_agent_request(self):
        """Test execute() accepts AgentRequest"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "authentication"},
            user_message="Add login with email and password"
        )
        
        response = agent.execute(request)
        assert isinstance(response, AgentResponse), \
            "execute() must return AgentResponse"
    
    def test_execute_returns_valid_agent_response(self):
        """Test execute() returns properly structured AgentResponse"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Create REST API for user data"
        )
        
        response = agent.execute(request)
        
        # Validate AgentResponse structure
        assert hasattr(response, 'success'), "Response must have 'success' field"
        assert hasattr(response, 'result'), "Response must have 'result' field"
        assert hasattr(response, 'message'), "Response must have 'message' field"
        assert hasattr(response, 'agent_name'), "Response must have 'agent_name' field"
        
        assert isinstance(response.success, bool), "'success' must be boolean"
        assert isinstance(response.message, str), "'message' must be string"
        assert response.agent_name == "ThreatModeler", "'agent_name' must be 'ThreatModeler'"
    
    def test_execute_with_minimal_context(self):
        """Test execute() works with minimal context"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={},
            user_message="Build payment processing feature"
        )
        
        response = agent.execute(request)
        
        assert response.success is True, "Should succeed with minimal context"
        assert 'threats' in response.result, "Result must contain 'threats'"
    
    def test_execute_extracts_feature_requirements_from_context(self):
        """Test execute() extracts requirements from AgentRequest context"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={
                "feature_description": "Implement file upload with virus scanning",
                "feature_type": "file_upload"
            },
            user_message="Analyze threats for file upload"
        )
        
        response = agent.execute(request)
        
        assert response.success is True
        assert len(response.result['threats']) > 0, "Should identify file upload threats"


# ============================================================================
# Phase 6.1: STRIDE Framework Completeness Tests
# ============================================================================

class TestSTRIDEFrameworkCompleteness:
    """Test comprehensive STRIDE analysis coverage"""
    
    def test_all_stride_categories_analyzed(self):
        """Test all 6 STRIDE categories are analyzed"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Create REST API for financial transactions with user authentication, data storage, and logging"
        )
        
        response = agent.execute(request)
        
        stride_summary = response.result.get('stride_summary', {})
        
        # Verify all STRIDE categories present
        expected_categories = [
            'spoofing',
            'tampering',
            'repudiation',
            'information_disclosure',
            'denial_of_service',
            'elevation_of_privilege'
        ]
        
        for category in expected_categories:
            assert category in stride_summary, \
                f"STRIDE category '{category}' missing from analysis"
    
    def test_spoofing_threats_identified(self):
        """Test Spoofing threats are identified for authentication features"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "authentication"},
            user_message="Add user login with password authentication"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        spoofing_threats = [
            t for t in threats 
            if t.get('category') == 'spoofing' or 
            ThreatCategory.SPOOFING.value in str(t)
        ]
        
        assert len(spoofing_threats) > 0, "Should identify spoofing threats for auth"
    
    def test_tampering_threats_identified(self):
        """Test Tampering threats are identified for data features"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "data_storage"},
            user_message="Store sensitive customer data in database"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        # Should identify data integrity threats
        assert len(threats) > 0, "Should identify tampering threats for data storage"
    
    def test_repudiation_threats_identified(self):
        """Test Repudiation threats are identified when logging absent"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Create admin API for deleting user accounts"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        # Should warn about audit logging
        assert len(threats) > 0, "Should identify repudiation threats for sensitive actions"
    
    def test_information_disclosure_threats_identified(self):
        """Test Information Disclosure threats are identified"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Expose user profile data via public API"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        # Should identify data leakage risks
        assert len(threats) > 0, "Should identify information disclosure threats"
    
    def test_denial_of_service_threats_identified(self):
        """Test DoS threats are identified for resource-intensive features"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "file_upload"},
            user_message="Allow users to upload large files"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        # Should identify resource exhaustion risks
        assert len(threats) > 0, "Should identify DoS threats for file upload"
    
    def test_elevation_of_privilege_threats_identified(self):
        """Test Privilege Escalation threats are identified"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Add role-based access control for admin features"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        # Should identify privilege escalation risks
        assert len(threats) > 0, "Should identify privilege escalation threats"


# ============================================================================
# Phase 6.1: Risk Rating Accuracy Tests
# ============================================================================

class TestRiskRatingAccuracy:
    """Test risk rating calculation accuracy"""
    
    def test_critical_risk_for_auth_bypass(self):
        """Test critical risk rating for authentication bypass"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "authentication"},
            user_message="Implement password reset without email verification"
        )
        
        response = agent.execute(request)
        
        risk_level = response.result.get('risk_level')
        assert risk_level in ['CRITICAL', 'HIGH'], \
            "Auth bypass should be CRITICAL or HIGH risk"
    
    def test_high_risk_for_sql_injection(self):
        """Test high risk rating for SQL injection vulnerability"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Create API that accepts SQL queries from users"
        )
        
        response = agent.execute(request)
        
        threats = response.result['threats']
        high_risk_threats = [
            t for t in threats 
            if t.get('risk_rating') in ['CRITICAL', 'HIGH'] or 
            t.get('risk_score', 0) >= 6
        ]
        
        assert len(high_risk_threats) > 0, "SQL injection should be HIGH risk"
    
    def test_medium_risk_for_weak_session_management(self):
        """Test medium risk rating for weak session management"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "authentication"},
            user_message="Use short session timeout of 5 minutes"
        )
        
        response = agent.execute(request)
        
        # Should identify session-related threats
        assert response.success is True
        assert len(response.result['threats']) > 0


# ============================================================================
# Phase 6.1: Mitigation Generation Quality Tests
# ============================================================================

class TestMitigationGenerationQuality:
    """Test quality of generated mitigation strategies"""
    
    def test_mitigations_include_implementation_steps(self):
        """Test mitigations include actionable implementation steps"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "authentication"},
            user_message="Add user login"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        for threat in threats[:3]:  # Check first 3 threats
            mitigations = threat.get('mitigation_strategies', [])
            assert len(mitigations) > 0, f"Threat '{threat.get('name')}' missing mitigations"
            
            for mitigation in mitigations:
                assert 'implementation_steps' in mitigation or 'steps' in mitigation, \
                    f"Mitigation missing implementation steps"
    
    def test_mitigations_include_code_examples(self):
        """Test mitigations include code examples"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Create REST API with authentication"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        has_code_example = False
        for threat in threats:
            mitigations = threat.get('mitigation_strategies', [])
            for mitigation in mitigations:
                if 'code_example' in mitigation or 'example' in mitigation:
                    has_code_example = True
                    break
            if has_code_example:
                break
        
        assert has_code_example, "At least one mitigation should include code example"
    
    def test_mitigations_specify_effort_estimate(self):
        """Test mitigations include effort estimates"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "file_upload"},
            user_message="Allow file uploads"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        has_effort_estimate = False
        for threat in threats[:3]:
            mitigations = threat.get('mitigation_strategies', [])
            for mitigation in mitigations:
                if 'effort_hours' in mitigation or 'effort' in mitigation:
                    has_effort_estimate = True
                    break
            if has_effort_estimate:
                break
        
        assert has_effort_estimate, "Mitigations should include effort estimates"


# ============================================================================
# Phase 6.1: OWASP Top 10 Mapping Tests
# ============================================================================

class TestOWASPMapping:
    """Test OWASP Top 10 2021 mapping accuracy"""
    
    def test_owasp_a01_broken_access_control(self):
        """Test OWASP A01 (Broken Access Control) mapping"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Create admin API without role checks"
        )
        
        response = agent.execute(request)
        owasp_coverage = response.result.get('owasp_coverage', {})
        
        assert 'A01' in owasp_coverage, "Should map to OWASP A01"
    
    def test_owasp_a02_cryptographic_failures(self):
        """Test OWASP A02 (Cryptographic Failures) mapping"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "data_storage"},
            user_message="Store passwords in plaintext"
        )
        
        response = agent.execute(request)
        threats = response.result['threats']
        
        # Should identify crypto-related threat
        assert len(threats) > 0, "Should identify cryptographic failure"
    
    def test_owasp_a03_injection(self):
        """Test OWASP A03 (Injection) mapping"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Accept user input for database queries"
        )
        
        response = agent.execute(request)
        owasp_coverage = response.result.get('owasp_coverage', {})
        
        assert 'A03' in owasp_coverage, "Should map to OWASP A03 (Injection)"
    
    def test_owasp_a07_authentication_failures(self):
        """Test OWASP A07 (Authentication Failures) mapping"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "authentication"},
            user_message="Implement login without rate limiting"
        )
        
        response = agent.execute(request)
        owasp_coverage = response.result.get('owasp_coverage', {})
        
        assert 'A07' in owasp_coverage, "Should map to OWASP A07"


# ============================================================================
# Phase 6.1: Feature Type Detection Tests
# ============================================================================

class TestFeatureTypeDetection:
    """Test feature type auto-detection accuracy"""
    
    def test_detect_authentication_from_keywords(self):
        """Test authentication detection from keywords"""
        agent = ThreatModelerAgent()
        
        test_cases = [
            "Add user login functionality",
            "Implement OAuth authentication",
            "Create password reset feature",
            "Build MFA (multi-factor authentication)"
        ]
        
        for user_message in test_cases:
            request = AgentRequest(
                intent="analyze_threats",
                context={},
                user_message=user_message
            )
            
            response = agent.execute(request)
            feature_type = response.result.get('feature_type', '')
            
            assert feature_type == 'authentication', \
                f"Failed to detect auth for: {user_message}"
    
    def test_detect_api_from_keywords(self):
        """Test API detection from keywords"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={},
            user_message="Create REST API endpoints for CRUD operations"
        )
        
        response = agent.execute(request)
        feature_type = response.result.get('feature_type', '')
        
        assert feature_type == 'api', "Should detect API feature"
    
    def test_detect_file_upload_from_keywords(self):
        """Test file upload detection from keywords"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={},
            user_message="Allow users to upload profile pictures"
        )
        
        response = agent.execute(request)
        feature_type = response.result.get('feature_type', '')
        
        assert feature_type == 'file_upload', "Should detect file upload"
    
    def test_detect_payment_from_keywords(self):
        """Test payment processing detection from keywords"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={},
            user_message="Integrate Stripe payment gateway for checkout"
        )
        
        response = agent.execute(request)
        feature_type = response.result.get('feature_type', '')
        
        assert feature_type == 'payment', "Should detect payment feature"
    
    def test_fallback_to_general_for_ambiguous(self):
        """Test fallback to 'general' for ambiguous features"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={},
            user_message="Improve system performance"
        )
        
        response = agent.execute(request)
        feature_type = response.result.get('feature_type', '')
        
        assert feature_type == 'general', "Should fallback to general"


# ============================================================================
# Phase 6.1: Performance and Timing Tests
# ============================================================================

class TestPerformance:
    """Test threat analysis performance"""
    
    def test_analysis_completes_within_5_minutes(self):
        """Test analysis completes within 5 minute target"""
        import time
        
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "api"},
            user_message="Create comprehensive REST API with authentication, authorization, rate limiting, and logging"
        )
        
        start = time.time()
        response = agent.execute(request)
        duration = time.time() - start
        
        assert duration < 300, f"Analysis took {duration:.2f}s (target: <300s)"
        assert response.success is True
    
    def test_minimal_feature_analysis_under_30_seconds(self):
        """Test simple feature analysis completes quickly"""
        import time
        
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "authentication"},
            user_message="Add login page"
        )
        
        start = time.time()
        response = agent.execute(request)
        duration = time.time() - start
        
        assert duration < 30, f"Simple analysis took {duration:.2f}s (target: <30s)"


# ============================================================================
# Phase 6.1: Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling in threat analysis"""
    
    def test_handles_empty_user_message(self):
        """Test handles empty user message gracefully"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={},
            user_message=""
        )
        
        response = agent.execute(request)
        
        assert response.success is False, "Should fail for empty message"
        assert response.error is not None, "Should provide error message"
    
    def test_handles_missing_context(self):
        """Test handles missing context gracefully"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context=None,
            user_message="Analyze threats"
        )
        
        response = agent.execute(request)
        
        # Should either succeed with defaults or fail gracefully
        assert response is not None
        assert hasattr(response, 'success')
    
    def test_handles_invalid_feature_type(self):
        """Test handles invalid feature type gracefully"""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            intent="analyze_threats",
            context={"feature_type": "invalid_type_xyz"},
            user_message="Build a feature"
        )
        
        response = agent.execute(request)
        
        # Should fallback to general or return sensible default
        assert response.success is True, "Should handle invalid feature type"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
