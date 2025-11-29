"""
Clarification Orchestrator

Manages the scope clarification workflow, including:
- Conditional activation based on validation results
- User interaction and prompt generation
- Response parsing and entity re-extraction
- Iterative clarification (maximum 2 rounds)
- Integration with ScopeInferenceEngine and ScopeValidator

This component ensures we only ask clarification questions when necessary
and stop after getting sufficient scope information.
"""

import re
from typing import Dict, List, Any, Optional
from src.agents.estimation.scope_inference_engine import ScopeInferenceEngine


class ClarificationOrchestrator:
    """Orchestrates the scope clarification workflow"""
    
    def __init__(self):
        self.current_round = 0
        self.max_rounds = 2
        self.confidence_threshold = 0.70
        self.inference_engine = ScopeInferenceEngine()
    
    def should_clarify(self, validator_result: Dict[str, Any]) -> bool:
        """
        Determine if clarification is needed based on validation results
        
        Args:
            validator_result: Dictionary with validation results
                - confidence: float (0.0-1.0)
                - is_valid: bool
                - missing_elements: list of missing element types
        
        Returns:
            bool: True if clarification is needed, False otherwise
        """
        # High confidence means no clarification needed
        if validator_result.get('confidence', 0.0) >= self.confidence_threshold:
            return False
        
        # Invalid scope needs clarification
        if not validator_result.get('is_valid', False):
            return True
        
        # Missing critical elements needs clarification
        missing = validator_result.get('missing_elements', [])
        if len(missing) > 0:
            return True
        
        return False
    
    def generate_clarification_prompt(self, validator_result: Dict[str, Any]) -> str:
        """
        Generate a user-friendly prompt asking for missing scope information
        
        Args:
            validator_result: Dictionary with validation results including
                            clarification_questions list
        
        Returns:
            str: Formatted prompt for user
        """
        confidence = validator_result.get('confidence', 0.0)
        missing_elements = validator_result.get('missing_elements', [])
        questions = validator_result.get('clarification_questions', [])
        
        # Build prompt header
        prompt_parts = [
            "I need more details to accurately scope this feature.",
            f"Current confidence: {confidence:.0%}",
            "",
            "Please provide more information about:"
        ]
        
        # Add specific questions
        for i, question in enumerate(questions, 1):
            prompt_parts.append(f"{i}. {question}")
        
        # Add helpful context
        if 'tables' in missing_elements:
            prompt_parts.append("\nFor database tables, please list specific table names.")
        if 'files' in missing_elements:
            prompt_parts.append("For code files, please include file names with extensions (e.g., UserService.cs).")
        if 'services' in missing_elements:
            prompt_parts.append("For external services, please specify service names (e.g., Azure AD, SendGrid).")
        
        return "\n".join(prompt_parts)
    
    def parse_user_response(self, user_response: str) -> Dict[str, Any]:
        """
        Parse user's response to extract scope entities
        
        Args:
            user_response: The user's text response to clarification questions
        
        Returns:
            Dictionary with:
                - entities: Dict with extracted tables, files, services, dependencies
                - confidence: float (0.0-1.0)
                - is_vague: bool indicating if response is still vague
        """
        # Use the inference engine to extract entities from response
        extracted_entities = self.inference_engine.extract_entities(user_response)
        
        # Calculate confidence from entity extraction
        confidence = self.inference_engine.calculate_confidence(extracted_entities, user_response)
        
        # Detect vague keywords in response
        vague_keywords = ['some', 'few', 'maybe', 'possibly', 'probably', 'might', 'several']
        response_lower = user_response.lower()
        vague_count = sum(1 for keyword in vague_keywords if keyword in response_lower)
        
        # Penalize if still vague
        if vague_count > 0:
            confidence = max(0.0, confidence - (vague_count * 0.15))
        
        # Check if response has actual content
        has_entities = (
            len(extracted_entities.tables) > 0 or
            len(extracted_entities.files) > 0 or
            len(extracted_entities.services) > 0 or
            len(extracted_entities.dependencies) > 0
        )
        
        is_vague = vague_count > 0 or not has_entities or confidence < 0.70
        
        return {
            'entities': {
                'tables': extracted_entities.tables,
                'files': extracted_entities.files,
                'services': extracted_entities.services,
                'dependencies': extracted_entities.dependencies
            },
            'confidence': confidence,
            'is_vague': is_vague
        }
    
    def increment_round(self):
        """Increment the clarification round counter"""
        self.current_round += 1
    
    def get_current_round(self) -> int:
        """Get the current clarification round number"""
        return self.current_round
    
    def can_continue_clarification(self) -> bool:
        """
        Check if we can continue asking for clarification
        
        Returns:
            bool: True if we haven't reached max rounds, False otherwise
        """
        return self.current_round < self.max_rounds
    
    def should_stop_clarification(self, validator_result: Dict[str, Any]) -> bool:
        """
        Determine if we should stop the clarification process
        
        Args:
            validator_result: Dictionary with validation results
        
        Returns:
            bool: True if we should stop, False if we should continue
        """
        # Stop if confidence threshold is met
        if validator_result.get('confidence', 0.0) >= self.confidence_threshold:
            return True
        
        # Stop if validation is successful
        if validator_result.get('is_valid', False):
            return True
        
        # Stop if we've reached max rounds
        if not self.can_continue_clarification():
            return True
        
        return False
    
    def reset(self):
        """Reset the orchestrator state for a new clarification workflow"""
        self.current_round = 0
    
    def run_clarification_workflow(
        self,
        initial_requirements: str,
        initial_validation: Dict[str, Any],
        max_iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run the complete clarification workflow
        
        Args:
            initial_requirements: The original requirements text
            initial_validation: Initial validation result from ScopeValidator
            max_iterations: Maximum iterations (defaults to self.max_rounds)
        
        Returns:
            Dictionary with:
                - final_scope: The final extracted scope
                - final_confidence: Final confidence score
                - rounds_completed: Number of clarification rounds
                - prompts: List of prompts generated
                - success: bool indicating if threshold was met
        """
        if max_iterations is None:
            max_iterations = self.max_rounds
        
        self.reset()
        
        # Check if clarification is needed
        if not self.should_clarify(initial_validation):
            return {
                'final_scope': initial_validation,
                'final_confidence': initial_validation.get('confidence', 0.0),
                'rounds_completed': 0,
                'prompts': [],
                'success': True
            }
        
        prompts = []
        current_validation = initial_validation
        
        # Clarification loop
        while self.can_continue_clarification():
            self.increment_round()
            
            # Generate prompt
            prompt = self.generate_clarification_prompt(current_validation)
            prompts.append(prompt)
            
            # In real usage, this would wait for user input
            # For now, we return the workflow state
            
            # Check if we should stop
            if self.should_stop_clarification(current_validation):
                break
        
        return {
            'final_scope': current_validation,
            'final_confidence': current_validation.get('confidence', 0.0),
            'rounds_completed': self.current_round,
            'prompts': prompts,
            'success': current_validation.get('confidence', 0.0) >= self.confidence_threshold
        }
