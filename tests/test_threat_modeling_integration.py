"""
TDD Tests for Threat Modeling Integration

Tests comprehensive threat modeling functionality including:
- ThreatModelerAgent functionality
- Feature type detection
- STRIDE analysis
- OWASP mapping
- Risk rating calculation
- Mitigation strategies
- Planning orchestrator integration

Author: CORTEX Development Team
Version: 1.0
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

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
# PHASE 1: ThreatModelerAgent Core Functionality Tests
# ============================================================================

class TestThreatModelerAgentBasics:
    """Test basic agent functionality"""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = ThreatModelerAgent()
        
        assert agent.agent_name == "ThreatModeler"
        assert agent.threat_templates is not None
        assert agent.mitigation_database is not None
        assert agent.expanded_keywords is not None
        assert len(agent.threat_templates) == 5  # auth, api, data, upload, payment
        assert len(agent.mitigation_database) >= 7  # Minimum mitigations
    
    def test_agent_has_all_stride_categories(self):
        """Test agent has keywords for all STRIDE categories"""
        agent = ThreatModelerAgent()
        
        assert ThreatCategory.SPOOFING in agent.expanded_keywords
        assert ThreatCategory.TAMPERING in agent.expanded_keywords
        assert ThreatCategory.REPUDIATION in agent.expanded_keywords
        assert ThreatCategory.INFORMATION_DISCLOSURE in agent.expanded_keywords
        assert ThreatCategory.DENIAL_OF_SERVICE in agent.expanded_keywords
        assert ThreatCategory.ELEVATION_OF_PRIVILEGE in agent.expanded_keywords


class TestFeatureTypeDetection:
    """Test feature type auto-detection"""
    
    def test_detect_authentication_feature(self):
        """Test detection of authentication features"""
        agent = ThreatModelerAgent()
        
        test_cases = [
            "Implement user login with email and password",
            "Add authentication system with OAuth",
            "Create signin page with MFA support",
            "User registration and password reset"
        ]
        
        for requirements in test_cases:
            feature_type = agent._detect_feature_type(requirements)
            assert feature_type == 'authentication', f"Failed for: {requirements}"
    
    def test_detect_api_feature(self):
        """Test detection of API features"""
        agent = ThreatModelerAgent()
        
        test_cases = [
            "Create REST API for user management",
            "Build GraphQL endpoint for products",
            "Add API service for data export",
            "Implement API gateway"
        ]
        
        for requirements in test_cases:
            feature_type = agent._detect_feature_type(requirements)
            assert feature_type == 'api', f"Failed for: {requirements}"
    
    def test_detect_file_upload_feature(self):
        """Test detection of file upload features"""
        agent = ThreatModelerAgent()
        
        test_cases = [
            "Allow users to upload profile pictures",
            "Implement document upload functionality",
            "Add file attachment support",
            "Create image upload for products"
        ]
        
        for requirements in test_cases:
            feature_type = agent._detect_feature_type(requirements)
            assert feature_type == 'file_upload', f"Failed for: {requirements}"
    
    def test_detect_payment_feature(self):
        """Test detection of payment features"""
        agent = ThreatModelerAgent()
        
        test_cases = [
            "Integrate Stripe payment processing",
            "Add checkout functionality",
            "Implement billing system",
            "Create payment gateway integration"
        ]
        
        for requirements in test_cases:
            feature_type = agent._detect_feature_type(requirements)
            assert feature_type == 'payment', f"Failed for: {requirements}"
    
    def test_detect_data_storage_feature(self):
        """Test detection of data storage features"""
        agent = ThreatModelerAgent()
        
        test_cases = [
            "Create database schema for user profiles",
            "Implement data persistence layer",
            "Add CRUD operations for products",
            "Store user preferences in database"
        ]
        
        for requirements in test_cases:
            feature_type = agent._detect_feature_type(requirements)
            assert feature_type == 'data_storage', f"Failed for: {requirements}"
    
    def test_detect_general_feature(self):
        """Test detection defaults to general for unknown features"""
        agent = ThreatModelerAgent()
        
        requirements = "Implement dashboard with charts"
        feature_type = agent._detect_feature_type(requirements)
        
        assert feature_type == 'general'


class TestThreatIdentification:
    """Test threat identification and template matching"""
    
    @pytest.mark.asyncio
    async def test_identify_authentication_threats(self):
        """Test identification of authentication threats"""
        agent = ThreatModelerAgent()
        
        requirements = "Create user login system with email and password"
        report = await agent.process(requirements, feature_type='authentication')
        
        assert len(report.threats) > 0
        threat_names = [t.name for t in report.threats]
        assert 'Brute Force Attacks' in threat_names
        assert 'Session Hijacking' in threat_names
    
    @pytest.mark.asyncio
    async def test_identify_api_threats(self):
        """Test identification of API threats"""
        agent = ThreatModelerAgent()
        
        requirements = "Build REST API with database queries"
        report = await agent.process(requirements, feature_type='api')
        
        assert len(report.threats) > 0
        threat_names = [t.name for t in report.threats]
        assert 'SQL Injection' in threat_names
        assert 'Broken Object Level Authorization' in threat_names
    
    @pytest.mark.asyncio
    async def test_identify_file_upload_threats(self):
        """Test identification of file upload threats"""
        agent = ThreatModelerAgent()
        
        requirements = "Allow users to upload documents and images"
        report = await agent.process(requirements, feature_type='file_upload')
        
        assert len(report.threats) > 0
        threat_names = [t.name for t in report.threats]
        assert 'Malicious File Upload' in threat_names
    
    @pytest.mark.asyncio
    async def test_identify_payment_threats(self):
        """Test identification of payment threats"""
        agent = ThreatModelerAgent()
        
        requirements = "Integrate payment processing with Stripe"
        report = await agent.process(requirements, feature_type='payment')
        
        assert len(report.threats) > 0
        threat_names = [t.name for t in report.threats]
        assert 'Payment Amount Manipulation' in threat_names
    
    @pytest.mark.asyncio
    async def test_threats_have_matched_keywords(self):
        """Test threats include matched keywords"""
        agent = ThreatModelerAgent()
        
        requirements = "Implement login with password authentication"
        report = await agent.process(requirements, feature_type='authentication')
        
        for threat in report.threats:
            assert len(threat.keywords_matched) > 0, f"{threat.name} has no matched keywords"


class TestRiskRating:
    """Test risk rating calculation"""
    
    @pytest.mark.asyncio
    async def test_critical_rating_for_high_impact_likelihood(self):
        """Test CRITICAL rating for high impact and high likelihood threats"""
        agent = ThreatModelerAgent()
        
        requirements = "Create payment system with credit card processing"
        report = await agent.process(requirements, feature_type='payment')
        
        # Payment features should have at least one CRITICAL or HIGH threat
        high_priority = [t for t in report.threats 
                        if t.risk_rating in [RiskRating.CRITICAL, RiskRating.HIGH]]
        assert len(high_priority) > 0
    
    @pytest.mark.asyncio
    async def test_risk_score_calculation(self):
        """Test risk score is calculated correctly"""
        agent = ThreatModelerAgent()
        
        requirements = "Add user login functionality"
        report = await agent.process(requirements, feature_type='authentication')
        
        for threat in report.threats:
            # Risk score should be product of likelihood and impact
            assert threat.risk_score >= 1
            assert threat.risk_score <= 12
    
    @pytest.mark.asyncio
    async def test_context_aware_risk_rating(self):
        """Test risk rating adjusts based on context"""
        agent = ThreatModelerAgent()
        
        requirements = "Implement payment processing"
        
        # Without context
        report1 = await agent.process(requirements, feature_type='payment')
        
        # With PCI DSS context
        report2 = await agent.process(
            requirements, 
            feature_type='payment',
            context={'requires_pci_dss': True}
        )
        
        # Context should potentially increase risk ratings
        critical_count1 = len([t for t in report1.threats if t.risk_rating == RiskRating.CRITICAL])
        critical_count2 = len([t for t in report2.threats if t.risk_rating == RiskRating.CRITICAL])
        
        assert critical_count2 >= critical_count1
    
    @pytest.mark.asyncio
    async def test_overall_risk_level_calculation(self):
        """Test overall risk level is calculated correctly"""
        agent = ThreatModelerAgent()
        
        requirements = "Create admin panel with user management"
        report = await agent.process(requirements)
        
        assert report.risk_level in [RiskRating.CRITICAL, RiskRating.HIGH, 
                                     RiskRating.MEDIUM, RiskRating.LOW]


class TestOWASPMapping:
    """Test OWASP Top 10 mapping"""
    
    @pytest.mark.asyncio
    async def test_threats_have_owasp_categories(self):
        """Test all threats have OWASP category mappings"""
        agent = ThreatModelerAgent()
        
        requirements = "Build API with authentication"
        report = await agent.process(requirements)
        
        for threat in report.threats:
            assert len(threat.owasp_categories) > 0, f"{threat.name} has no OWASP mapping"
    
    @pytest.mark.asyncio
    async def test_owasp_coverage_summary(self):
        """Test OWASP coverage summary is generated"""
        agent = ThreatModelerAgent()
        
        requirements = "Create login system with database"
        report = await agent.process(requirements)
        
        assert report.owasp_coverage is not None
        assert len(report.owasp_coverage) > 0
        
        # Check format (A01, A02, etc.)
        for key in report.owasp_coverage.keys():
            assert key.startswith('A0')
    
    @pytest.mark.asyncio
    async def test_sql_injection_maps_to_a03(self):
        """Test SQL Injection maps to OWASP A03 (Injection)"""
        agent = ThreatModelerAgent()
        
        requirements = "Create API with database queries"
        report = await agent.process(requirements, feature_type='api')
        
        sql_injection = next((t for t in report.threats if t.name == 'SQL Injection'), None)
        if sql_injection:
            owasp_codes = [o.value.split(' - ')[0] for o in sql_injection.owasp_categories]
            assert 'A03:2021' in owasp_codes
    
    @pytest.mark.asyncio
    async def test_broken_auth_maps_to_a07(self):
        """Test authentication threats map to OWASP A07"""
        agent = ThreatModelerAgent()
        
        requirements = "Implement user authentication"
        report = await agent.process(requirements, feature_type='authentication')
        
        # Check at least one threat maps to A07
        a07_threats = []
        for threat in report.threats:
            owasp_codes = [o.value.split(':')[0] for o in threat.owasp_categories]
            if 'A07' in owasp_codes:
                a07_threats.append(threat)
        
        assert len(a07_threats) > 0


class TestMitigationStrategies:
    """Test mitigation strategies"""
    
    @pytest.mark.asyncio
    async def test_threats_have_mitigations(self):
        """Test all threats have mitigation strategies"""
        agent = ThreatModelerAgent()
        
        requirements = "Create user login with passwords"
        report = await agent.process(requirements)
        
        for threat in report.threats:
            assert len(threat.mitigation_strategies) > 0, f"{threat.name} has no mitigations"
    
    @pytest.mark.asyncio
    async def test_mitigations_have_code_examples(self):
        """Test mitigation strategies include code examples"""
        agent = ThreatModelerAgent()
        
        requirements = "Build API with SQL database"
        report = await agent.process(requirements, feature_type='api')
        
        sql_injection = next((t for t in report.threats if t.name == 'SQL Injection'), None)
        if sql_injection:
            mitigation = sql_injection.mitigation_strategies[0]
            assert mitigation.code_example is not None
            assert len(mitigation.code_example) > 0
            assert mitigation.language == 'csharp'
    
    @pytest.mark.asyncio
    async def test_mitigations_have_effort_estimates(self):
        """Test mitigations include effort estimates"""
        agent = ThreatModelerAgent()
        
        requirements = "Implement login system"
        report = await agent.process(requirements)
        
        for threat in report.threats:
            for mitigation in threat.mitigation_strategies:
                assert mitigation.effort_hours > 0
                assert mitigation.effectiveness_percent > 0
                assert mitigation.effectiveness_percent <= 100
    
    @pytest.mark.asyncio
    async def test_mitigations_have_implementation_steps(self):
        """Test mitigations include implementation steps"""
        agent = ThreatModelerAgent()
        
        requirements = "Create payment processing"
        report = await agent.process(requirements, feature_type='payment')
        
        for threat in report.threats:
            for mitigation in threat.mitigation_strategies:
                assert len(mitigation.implementation_steps) > 0


class TestSTRIDESummary:
    """Test STRIDE analysis summary"""
    
    @pytest.mark.asyncio
    async def test_stride_summary_generated(self):
        """Test STRIDE summary is generated"""
        agent = ThreatModelerAgent()
        
        requirements = "Build complete user management system"
        report = await agent.process(requirements)
        
        assert report.stride_summary is not None
        assert len(report.stride_summary) == 6  # All STRIDE categories
    
    @pytest.mark.asyncio
    async def test_stride_summary_has_all_categories(self):
        """Test STRIDE summary includes all categories"""
        agent = ThreatModelerAgent()
        
        requirements = "Create web application"
        report = await agent.process(requirements)
        
        expected_categories = [
            "Spoofing", "Tampering", "Repudiation",
            "Information Disclosure", "Denial of Service",
            "Elevation of Privilege"
        ]
        
        for category in expected_categories:
            assert category in report.stride_summary


class TestRecommendations:
    """Test recommendation generation"""
    
    @pytest.mark.asyncio
    async def test_recommendations_generated(self):
        """Test recommendations are generated"""
        agent = ThreatModelerAgent()
        
        requirements = "Implement user authentication"
        report = await agent.process(requirements)
        
        assert report.recommendations is not None
        assert len(report.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_critical_threats_in_recommendations(self):
        """Test critical threats appear in recommendations"""
        agent = ThreatModelerAgent()
        
        requirements = "Create payment processing with credit cards"
        report = await agent.process(requirements, feature_type='payment')
        
        if len(report.critical_threats) > 0:
            recommendations_text = ' '.join(report.recommendations)
            assert 'CRITICAL' in recommendations_text
    
    @pytest.mark.asyncio
    async def test_feature_specific_recommendations(self):
        """Test feature-specific recommendations are included"""
        agent = ThreatModelerAgent()
        
        requirements = "Add user login"
        report = await agent.process(requirements, feature_type='authentication')
        
        recommendations_text = ' '.join(report.recommendations)
        assert 'MFA' in recommendations_text or 'multi-factor' in recommendations_text.lower()


class TestThreatReport:
    """Test threat report structure"""
    
    @pytest.mark.asyncio
    async def test_report_has_required_fields(self):
        """Test report contains all required fields"""
        agent = ThreatModelerAgent()
        
        requirements = "Create user management system"
        report = await agent.process(requirements)
        
        assert report.feature_name is not None
        assert report.feature_type is not None
        assert report.threats is not None
        assert report.timestamp is not None
        assert report.risk_level is not None
        assert report.stride_summary is not None
        assert report.owasp_coverage is not None
        assert report.recommendations is not None
    
    @pytest.mark.asyncio
    async def test_report_critical_threats_property(self):
        """Test report critical_threats property works"""
        agent = ThreatModelerAgent()
        
        requirements = "Implement payment gateway"
        report = await agent.process(requirements, feature_type='payment')
        
        critical = report.critical_threats
        assert isinstance(critical, list)
        
        for threat in critical:
            assert threat.risk_rating == RiskRating.CRITICAL
    
    @pytest.mark.asyncio
    async def test_report_high_threats_property(self):
        """Test report high_threats property works"""
        agent = ThreatModelerAgent()
        
        requirements = "Create authentication system"
        report = await agent.process(requirements)
        
        high = report.high_threats
        assert isinstance(high, list)
        
        for threat in high:
            assert threat.risk_rating == RiskRating.HIGH


# ============================================================================
# PHASE 2: Planning Orchestrator Integration Tests
# ============================================================================

class TestPlanningOrchestratorIntegration:
    """Test integration with Planning Orchestrator"""
    
    @pytest.mark.skip(reason="Requires Planning Orchestrator integration implementation")
    def test_threat_modeling_after_dor(self):
        """Test threat modeling runs after DoR validation"""
        # This test will be implemented after integration
        pass
    
    @pytest.mark.skip(reason="Requires Planning Orchestrator integration implementation")
    def test_threat_report_in_planning_document(self):
        """Test threat report is included in planning document"""
        # This test will be implemented after integration
        pass
    
    @pytest.mark.skip(reason="Requires Planning Orchestrator integration implementation")
    def test_dod_validation_with_threats(self):
        """Test DoD validation includes threat mitigation checks"""
        # This test will be implemented after integration
        pass


# ============================================================================
# PHASE 3: Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance requirements"""
    
    @pytest.mark.asyncio
    async def test_analysis_completes_within_3_seconds(self):
        """Test threat analysis completes within 3 seconds"""
        agent = ThreatModelerAgent()
        
        requirements = "Create comprehensive user management system with authentication, API, and data storage"
        
        start_time = datetime.now()
        report = await agent.process(requirements)
        duration = (datetime.now() - start_time).total_seconds()
        
        assert duration < 3.0, f"Analysis took {duration}s (threshold: 3s)"
    
    @pytest.mark.asyncio
    async def test_multiple_analyses_in_sequence(self):
        """Test multiple analyses can run efficiently"""
        agent = ThreatModelerAgent()
        
        requirements_list = [
            "Implement user login",
            "Create REST API",
            "Add file upload",
            "Integrate payment processing",
            "Build data storage layer"
        ]
        
        start_time = datetime.now()
        
        for requirements in requirements_list:
            report = await agent.process(requirements)
            assert len(report.threats) > 0
        
        total_duration = (datetime.now() - start_time).total_seconds()
        avg_duration = total_duration / len(requirements_list)
        
        assert avg_duration < 3.0, f"Average analysis took {avg_duration}s (threshold: 3s)"


# ============================================================================
# PHASE 4: Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_empty_requirements(self):
        """Test handling of empty requirements"""
        agent = ThreatModelerAgent()
        
        requirements = ""
        report = await agent.process(requirements)
        
        # Should return general threats or minimal report
        assert report is not None
        assert report.feature_type == 'general'
    
    @pytest.mark.asyncio
    async def test_very_long_requirements(self):
        """Test handling of very long requirements"""
        agent = ThreatModelerAgent()
        
        requirements = "Create system " + "with feature " * 500
        report = await agent.process(requirements)
        
        assert report is not None
        assert len(report.threats) > 0
    
    @pytest.mark.asyncio
    async def test_special_characters_in_requirements(self):
        """Test handling of special characters"""
        agent = ThreatModelerAgent()
        
        requirements = "Create <script>alert('XSS')</script> login system with SQL'; DROP TABLE users;--"
        report = await agent.process(requirements)
        
        assert report is not None
    
    @pytest.mark.asyncio
    async def test_non_english_requirements(self):
        """Test handling of non-English text"""
        agent = ThreatModelerAgent()
        
        requirements = "创建用户登录系统"  # Chinese
        report = await agent.process(requirements)
        
        # Should default to general since keywords won't match
        assert report is not None


# ============================================================================
# Test Execution Summary
# ============================================================================

def test_suite_summary():
    """Summary of test suite coverage"""
    test_categories = {
        'Agent Basics': 2,
        'Feature Type Detection': 6,
        'Threat Identification': 6,
        'Risk Rating': 4,
        'OWASP Mapping': 4,
        'Mitigation Strategies': 4,
        'STRIDE Summary': 2,
        'Recommendations': 3,
        'Threat Report': 3,
        'Performance': 2,
        'Edge Cases': 4
    }
    
    total_tests = sum(test_categories.values())
    
    print(f"\n{'='*60}")
    print(f"Threat Modeling Test Suite Summary")
    print(f"{'='*60}")
    print(f"Total Test Categories: {len(test_categories)}")
    print(f"Total Tests: {total_tests}")
    print(f"\nTest Distribution:")
    for category, count in test_categories.items():
        print(f"  {category:.<35} {count:>3} tests")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    test_suite_summary()
    pytest.main([__file__, '-v', '--tb=short'])
