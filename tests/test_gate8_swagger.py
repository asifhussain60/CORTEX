"""
Gate 8: SWAGGER Entry Point System Tests

Tests for the SWAGGER entry point orchestrator including:
- DoR validation
- Work decomposition  
- ADO output generation
- Entry point routing
"""

import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class TestDoRValidator:
    """Tests for DoR (Definition of Ready) validation"""
    
    def test_dor_validator_importable(self):
        """DoR validator can be imported"""
        from src.agents.estimation.dor_validator import DoRValidator
        assert DoRValidator is not None
    
    def test_dor_validator_initialization(self):
        """DoR validator initializes correctly"""
        from src.agents.estimation.dor_validator import DoRValidator
        validator = DoRValidator()
        assert validator is not None
    
    def test_dor_validator_empty_requirements(self):
        """Empty requirements fail DoR validation"""
        from src.agents.estimation.dor_validator import DoRValidator
        validator = DoRValidator()
        result = validator.validate_dor("")  # Empty string, not dict
        assert result.complete_count < 4  # Should be low score
        assert not result.can_estimate
    
    def test_dor_validator_complete_requirements(self):
        """Complete requirements pass DoR validation"""
        from src.agents.estimation.dor_validator import DoRValidator
        validator = DoRValidator()
        
        # Requirements as a detailed string with all necessary context
        requirements = """
        Feature: User Password Reset
        
        Users need to be able to reset their passwords when they forget them.
        This feature allows all registered users to request a password reset via email.
        
        The system will send a reset link that expires in 30 minutes.
        User must be able to:
        - Request password reset via email address
        - Receive email with secure reset link within 5 minutes
        - Click link and enter new password
        - Password must meet complexity requirements (8+ chars, 1 uppercase, 1 number)
        
        Performance requirement: Reset email must be sent within 5 seconds.
        Security: Links expire after 30 minutes, one-time use only.
        """
        
        # Context with additional structured info
        context = {
            'dependencies': ['Email service', 'User database'],
            'acceptance_criteria': ['Can request reset', 'Email sent within 5 seconds', 'Link works'],
            'security_notes': 'OWASP A7 reviewed, rate limiting implemented',
            'user_approved': True,
            'technical_design': 'Token-based reset with Redis expiry',
            'test_strategy': 'Unit tests for token generation, integration tests for email'
        }
        
        result = validator.validate_dor(requirements, context)
        assert result.complete_count >= 6  # Should mostly pass
        # May not be 100% but should be high enough
    
    def test_dor_validator_questions_generation(self):
        """DoR validator generates clarifying questions"""
        from src.agents.estimation.dor_validator import DoRValidator
        validator = DoRValidator()
        
        # Partial requirements with vague terms
        partial_reqs = "Users need improved feature for better performance"
        
        result = validator.validate_dor(partial_reqs)
        # Should have clarifying questions since requirements are incomplete/vague
        assert len(result.clarifying_questions) > 0 or result.missing_count > 0


class TestWorkDecomposer:
    """Tests for work decomposition"""
    
    def test_work_decomposer_importable(self):
        """Work decomposer can be imported"""
        from src.agents.estimation.work_decomposer import WorkDecomposer
        assert WorkDecomposer is not None
    
    def test_work_decomposer_initialization(self):
        """Work decomposer initializes correctly"""
        from src.agents.estimation.work_decomposer import WorkDecomposer
        decomposer = WorkDecomposer()
        assert decomposer is not None
    
    def test_work_decomposer_simple_feature(self):
        """Simple feature decomposes into stories"""
        from src.agents.estimation.work_decomposer import WorkDecomposer
        decomposer = WorkDecomposer()
        
        result = decomposer.decompose_work(
            title='User Login',
            description='Basic login with email and password',
            complexity_score=25.0
        )
        
        assert result is not None
        assert result.total_features >= 1
        assert result.total_stories >= 1
        assert result.total_story_points > 0
    
    def test_work_decomposer_complex_feature(self):
        """Complex feature decomposes into epic/features/stories"""
        from src.agents.estimation.work_decomposer import WorkDecomposer
        decomposer = WorkDecomposer()
        
        result = decomposer.decompose_work(
            title='User Authentication System',
            description='''
            Complete authentication with:
            - Login/logout
            - Password reset
            - OAuth (Google, GitHub)
            - MFA
            - Session management
            ''',
            complexity_score=55.0
        )
        
        assert result is not None
        assert result.total_features >= 1
        assert result.total_stories >= 2
        assert result.total_story_points >= 8
    
    def test_work_decomposer_ado_json_output(self):
        """Work decomposer generates dict output for ADO"""
        from src.agents.estimation.work_decomposer import WorkDecomposer
        decomposer = WorkDecomposer()
        
        result = decomposer.decompose_work(
            title='Simple Feature',
            description='A simple test feature',
            complexity_score=20.0
        )
        
        # Check structure via to_dict method
        result_dict = result.to_dict()
        assert result_dict is not None
        assert 'features' in result_dict or 'stories' in result_dict


class TestSWAGGEREntryPointOrchestrator:
    """Tests for SWAGGER Entry Point Orchestrator"""
    
    def test_orchestrator_importable(self):
        """Orchestrator can be imported"""
        from src.orchestrators.swagger_entry_point_orchestrator import SWAGGEREntryPointOrchestrator
        assert SWAGGEREntryPointOrchestrator is not None
    
    def test_orchestrator_initialization(self):
        """Orchestrator initializes correctly"""
        from src.orchestrators.swagger_entry_point_orchestrator import SWAGGEREntryPointOrchestrator
        orchestrator = SWAGGEREntryPointOrchestrator()
        assert orchestrator is not None
        assert orchestrator.dor_validator is not None
        # Note: decomposer is None until DoR is complete (lazy initialization)
        assert orchestrator.estimation_blocked == True
    
    def test_orchestrator_dor_status(self):
        """Orchestrator can check DoR status"""
        from src.orchestrators.swagger_entry_point_orchestrator import SWAGGEREntryPointOrchestrator
        orchestrator = SWAGGEREntryPointOrchestrator()
        
        status = orchestrator.get_dor_status()
        assert status is not None
        assert 'score' in status or 'checklist' in status


class TestGate8Validation:
    """Tests for Gate 8 deployment validation"""
    
    def test_all_phase3_components_exist(self):
        """All Phase 3 components exist"""
        from pathlib import Path
        base = Path(__file__).parent.parent / 'src'
        
        # DoR Validator
        dor_file = base / 'agents' / 'estimation' / 'dor_validator.py'
        assert dor_file.exists(), f"Missing: {dor_file}"
        
        # Work Decomposer
        decomposer_file = base / 'agents' / 'estimation' / 'work_decomposer.py'
        assert decomposer_file.exists(), f"Missing: {decomposer_file}"
        
        # Entry Point Orchestrator
        orchestrator_file = base / 'orchestrators' / 'swagger_entry_point_orchestrator.py'
        assert orchestrator_file.exists(), f"Missing: {orchestrator_file}"
    
    def test_all_phase3_components_import(self):
        """All Phase 3 components import without errors"""
        # These should not raise ImportError
        from src.agents.estimation.dor_validator import DoRValidator
        from src.agents.estimation.work_decomposer import WorkDecomposer
        from src.orchestrators.swagger_entry_point_orchestrator import SWAGGEREntryPointOrchestrator
        
        assert DoRValidator is not None
        assert WorkDecomposer is not None
        assert SWAGGEREntryPointOrchestrator is not None
    
    def test_integration_flow_dor_validation(self):
        """DoR validation flow works in orchestrator"""
        from src.orchestrators.swagger_entry_point_orchestrator import SWAGGEREntryPointOrchestrator
        
        orchestrator = SWAGGEREntryPointOrchestrator()
        
        # Check DoR status - should start incomplete
        status = orchestrator.get_dor_status()
        assert status is not None
        assert 'score' in status
        
        # Verify estimation is blocked initially
        assert orchestrator.estimation_blocked
    
    def test_dor_enforcement_blocks_estimation(self):
        """Incomplete DoR blocks estimation"""
        from src.orchestrators.swagger_entry_point_orchestrator import SWAGGEREntryPointOrchestrator
        
        orchestrator = SWAGGEREntryPointOrchestrator()
        
        # Without completing DoR, estimation should be blocked
        assert orchestrator.estimation_blocked
        
        # Check status shows incomplete
        status = orchestrator.get_dor_status()
        # score is a string like "10%" - parse it
        score_str = status['score'].replace('%', '')
        assert float(score_str) < 100


class TestTimeframeEstimatorPhase2:
    """Tests for Phase 2 visual timeline features"""
    
    def test_generate_timeline_comparison(self):
        """Timeline comparison generates single vs team view"""
        from src.agents.estimation.timeframe_estimator import TimeframeEstimator
        
        estimator = TimeframeEstimator()
        
        # First get estimate, then generate timeline comparison
        estimate = estimator.estimate_timeframe(45.0)
        result = estimator.generate_timeline_comparison(estimate, hourly_rate=75.0)
        
        assert result is not None
        assert 'single_developer' in result
        assert 'max_team' in result
    
    def test_ascii_gantt_generation(self):
        """ASCII timeline generates correctly"""
        from src.agents.estimation.timeframe_estimator import TimeframeEstimator
        
        estimator = TimeframeEstimator()
        
        # First get estimate, then generate timeline comparison
        estimate = estimator.estimate_timeframe(45.0)
        result = estimator.generate_timeline_comparison(estimate, hourly_rate=75.0)
        
        # Should have some visual representation
        assert result is not None
        assert 'ascii_timeline' in result
        assert len(result['ascii_timeline']) > 0
    
    def test_what_if_scenarios(self):
        """What-if scenarios compare team sizes"""
        from src.agents.estimation.timeframe_estimator import TimeframeEstimator
        
        estimator = TimeframeEstimator()
        result = estimator.generate_what_if_scenarios(
            complexity=45.0,
            team_sizes=[1, 2, 3, 5],
            hourly_rate=75.0
        )
        
        assert result is not None
        assert isinstance(result, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
