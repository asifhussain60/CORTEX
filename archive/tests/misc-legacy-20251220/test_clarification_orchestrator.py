"""
Tests for Clarification Orchestrator

Tests the workflow for scope clarification, including:
- Conditional activation based on validator results
- User interaction and prompt generation
- Response parsing and re-extraction
- Iterative clarification (max 2 rounds)
- Integration with ScopeInferenceEngine and ScopeValidator
"""

import pytest
from src.agents.estimation.clarification_orchestrator import ClarificationOrchestrator
from src.agents.estimation.scope_inference_engine import ScopeInferenceEngine
from src.agents.estimation.scope_validator import ScopeValidator


class TestClarificationActivation:
    """Test when clarification should/shouldn't activate"""
    
    def test_high_confidence_skips_clarification(self):
        """High confidence (>0.70) should skip clarification"""
        orchestrator = ClarificationOrchestrator()
        
        validator_result = {
            'confidence': 0.85,
            'is_valid': True,
            'missing_elements': []
        }
        
        needs_clarification = orchestrator.should_clarify(validator_result)
        assert needs_clarification is False, "High confidence should skip clarification"
    
    def test_low_confidence_triggers_clarification(self):
        """Low confidence (<0.70) should trigger clarification"""
        orchestrator = ClarificationOrchestrator()
        
        validator_result = {
            'confidence': 0.45,
            'is_valid': False,
            'missing_elements': ['tables', 'files']
        }
        
        needs_clarification = orchestrator.should_clarify(validator_result)
        assert needs_clarification is True, "Low confidence should trigger clarification"
    
    def test_missing_critical_elements_triggers_clarification(self):
        """Missing critical elements should trigger clarification even with decent confidence"""
        orchestrator = ClarificationOrchestrator()
        
        validator_result = {
            'confidence': 0.65,
            'is_valid': False,
            'missing_elements': ['tables']
        }
        
        needs_clarification = orchestrator.should_clarify(validator_result)
        assert needs_clarification is True, "Missing critical elements should trigger clarification"


class TestPromptGeneration:
    """Test clarification prompt generation"""
    
    def test_generate_prompt_for_missing_tables(self):
        """Should generate specific prompt for missing tables"""
        orchestrator = ClarificationOrchestrator()
        
        validator_result = {
            'confidence': 0.40,
            'missing_elements': ['tables'],
            'clarification_questions': ['What database tables will be involved?']
        }
        
        prompt = orchestrator.generate_clarification_prompt(validator_result)
        
        assert 'database tables' in prompt.lower(), "Prompt should mention database tables"
        assert 'What database tables' in prompt, "Should include specific question"
    
    def test_generate_prompt_for_multiple_gaps(self):
        """Should handle multiple missing elements in one prompt"""
        orchestrator = ClarificationOrchestrator()
        
        validator_result = {
            'confidence': 0.30,
            'missing_elements': ['tables', 'files', 'services'],
            'clarification_questions': [
                'What database tables will be involved?',
                'What code files need to be modified?',
                'What external services will be integrated?'
            ]
        }
        
        prompt = orchestrator.generate_clarification_prompt(validator_result)
        
        assert 'database tables' in prompt.lower()
        assert 'code files' in prompt.lower()
        assert 'external services' in prompt.lower()
        assert len(prompt) < 1000, "Prompt should be concise"


class TestResponseParsing:
    """Test parsing user responses to clarification questions"""
    
    def test_parse_user_response_with_tables(self):
        """Should extract entities from user response"""
        orchestrator = ClarificationOrchestrator()
        
        user_response = """
        We'll need to modify users table, user_profiles table, and authentication_tokens table.
        Also update UserService.cs and AuthController.cs files.
        """
        
        parsed = orchestrator.parse_user_response(user_response)
        
        assert 'entities' in parsed
        assert len(parsed['entities']['tables']) >= 2
        assert len(parsed['entities']['files']) >= 2
    
    def test_parse_vague_response(self):
        """Should detect when response is still vague"""
        orchestrator = ClarificationOrchestrator()
        
        user_response = "We'll need some database changes and maybe a few service updates."
        
        parsed = orchestrator.parse_user_response(user_response)
        
        assert parsed['confidence'] < 0.70, "Vague response should have low confidence"
        assert parsed['is_vague'] is True


class TestIterativeClarification:
    """Test iterative clarification workflow"""
    
    def test_clarification_round_tracking(self):
        """Should track number of clarification rounds"""
        orchestrator = ClarificationOrchestrator()
        
        assert orchestrator.get_current_round() == 0, "Should start at round 0"
        
        orchestrator.increment_round()
        assert orchestrator.get_current_round() == 1
        
        orchestrator.increment_round()
        assert orchestrator.get_current_round() == 2
    
    def test_max_two_rounds_enforced(self):
        """Should enforce maximum of 2 clarification rounds"""
        orchestrator = ClarificationOrchestrator()
        
        orchestrator.increment_round()
        orchestrator.increment_round()
        
        can_continue = orchestrator.can_continue_clarification()
        assert can_continue is False, "Should stop after 2 rounds"
    
    def test_stop_early_when_confidence_achieved(self):
        """Should stop clarification when confidence threshold is met"""
        orchestrator = ClarificationOrchestrator()
        
        validator_result = {
            'confidence': 0.75,
            'is_valid': True,
            'missing_elements': []
        }
        
        should_stop = orchestrator.should_stop_clarification(validator_result)
        assert should_stop is True, "Should stop when confidence is met"


class TestEndToEndClarificationWorkflow:
    """Test complete clarification workflow integration"""
    
    def test_complete_workflow_with_successful_clarification(self):
        """Test full workflow from validation to clarification to completion"""
        orchestrator = ClarificationOrchestrator()
        
        # Initial vague requirements
        initial_requirements = "Add authentication to the system"
        
        # Simulate initial extraction (would be done by ScopeInferenceEngine)
        initial_scope = {
            'tables': [],
            'files': [],
            'services': [],
            'dependencies': ['authentication']
        }
        
        # Simulate validation (would be done by ScopeValidator)
        initial_validation = {
            'confidence': 0.25,
            'is_valid': False,
            'missing_elements': ['tables', 'files'],
            'clarification_questions': [
                'What database tables will store authentication data?',
                'What code files will implement authentication logic?'
            ]
        }
        
        # Should trigger clarification
        needs_clarification = orchestrator.should_clarify(initial_validation)
        assert needs_clarification is True
        
        # Generate prompt
        prompt = orchestrator.generate_clarification_prompt(initial_validation)
        assert len(prompt) > 0
        
        # Simulate user response
        user_response = """
        We'll add a users table and auth_tokens table.
        Need to create AuthService.cs and modify UserController.cs.
        """
        
        # Parse response
        parsed = orchestrator.parse_user_response(user_response)
        assert parsed['confidence'] >= 0.70, "Should have high confidence after clarification"
        assert len(parsed['entities']['tables']) >= 2
        assert len(parsed['entities']['files']) >= 2
    
    def test_workflow_stops_after_two_vague_responses(self):
        """Test that workflow stops after 2 rounds of vague responses"""
        orchestrator = ClarificationOrchestrator()
        
        # Round 1
        orchestrator.increment_round()
        validator_result_1 = {
            'confidence': 0.35,
            'is_valid': False,
            'missing_elements': ['tables']
        }
        
        assert orchestrator.can_continue_clarification() is True
        
        # Round 2
        orchestrator.increment_round()
        validator_result_2 = {
            'confidence': 0.40,
            'is_valid': False,
            'missing_elements': ['tables']
        }
        
        assert orchestrator.can_continue_clarification() is False, "Should stop after round 2"


class TestIntegrationWithScopeComponents:
    """Test integration with ScopeInferenceEngine and ScopeValidator"""
    
    def test_integrated_workflow_with_real_components(self):
        """Test clarification workflow with actual inference and validation"""
        orchestrator = ClarificationOrchestrator()
        inference_engine = ScopeInferenceEngine()
        validator = ScopeValidator()
        
        # Initial vague requirements
        requirements = "Add user management features"
        
        # Extract initial scope
        scope_entities = inference_engine.extract_entities(requirements)
        confidence = inference_engine.calculate_confidence(scope_entities, requirements)
        assert confidence < 0.70, "Initial scope should have low confidence"
        
        # Generate scope boundary for validator
        scope_boundary = inference_engine.generate_scope_boundary(scope_entities, confidence)
        
        # Validate
        validation_result = validator.validate_scope(scope_boundary)
        assert validation_result.is_valid is False
        
        # Convert validation result to dict format for orchestrator
        validation = {
            'confidence': validation_result.confidence_score,
            'is_valid': validation_result.is_valid,
            'missing_elements': validation_result.missing_elements,
            'clarification_questions': []
        }
        
        # Should trigger clarification
        needs_clarification = orchestrator.should_clarify(validation)
        assert needs_clarification is True
        
        # Generate and verify prompt
        prompt = orchestrator.generate_clarification_prompt(validation)
        assert len(prompt) > 50, "Should generate substantial prompt"
        
        # Simulate detailed response
        detailed_response = """
        We need to add users table, user_roles table, and user_sessions table.
        Create UserService.cs, RoleService.cs, and SessionManager.cs files.
        Integrate with Azure AD for authentication.
        """
        
        # Parse response
        parsed = orchestrator.parse_user_response(detailed_response)
        
        # Re-extract and validate clarified scope
        clarified_entities = inference_engine.extract_entities(detailed_response)
        clarified_confidence = inference_engine.calculate_confidence(clarified_entities, detailed_response)
        clarified_boundary = inference_engine.generate_scope_boundary(clarified_entities, clarified_confidence)
        final_validation = validator.validate_scope(clarified_boundary)
        
        assert clarified_confidence >= 0.70, "Should have high confidence after clarification"
        assert final_validation.is_valid is True
