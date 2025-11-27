"""
Documentation Validation Service

Handles validation, constraints enforcement, and quality checks
for the doc_refresh_plugin. Follows SRP - focused only on validation.

Extracted from doc_refresh_plugin.py for token optimization.
Part of: CORTEX 3.0 Track B (Token Optimization)
"""

from typing import Dict, List, Any
import logging


class DocValidationService:
    """Service for validating documentation quality and constraints"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    # Read time validation
    def validate_read_time(self, content: str, target_minutes: int) -> Dict[str, Any]:
        """Validate content meets read time targets"""
        pass
    
    def get_read_time_recommendation(self, content: str, current_minutes: int, 
                                   target_minutes: int) -> Dict[str, Any]:
        """Get recommendations for meeting read time targets"""
        pass
    
    # Narrative validation
    def validate_narrative_flow(self, story_text: str, recap_suggestions: List[str], 
                              narrative_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate narrative flow and consistency"""
        pass
    
    def validate_story_consistency(self, story_text: str, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate story consistency with design context"""
        pass
    
    # Content validation rules
    def validate_no_new_files_rule(self, operation: str, file_path: str) -> bool:
        """Enforce: NEVER CREATE NEW FILES - Only update existing"""
        if operation == 'create':
            self.logger.error(f"FORBIDDEN: Attempted to create new file {file_path}")
            return False
        return True
    
    def validate_no_variants_rule(self, filename: str) -> bool:
        """Enforce: FORBIDDEN - Creating Quick Read, Summary, or variant versions"""
        forbidden_patterns = ['quick', 'summary', 'short', 'brief', 'condensed']
        filename_lower = filename.lower()
        
        for pattern in forbidden_patterns:
            if pattern in filename_lower:
                self.logger.error(f"FORBIDDEN: Variant file detected {filename}")
                return False
        return True
    
    def validate_target_length_constraint(self, content: str, max_length: int) -> Dict[str, Any]:
        """Enforce: If content exceeds target, TRIM - don't create alternatives"""
        current_length = len(content)
        
        if current_length > max_length:
            return {
                'action': 'trim_required',
                'current_length': current_length,
                'target_length': max_length,
                'trim_amount': current_length - max_length
            }
        
        return {'action': 'no_trim_needed', 'length_ok': True}
    
    # Quality checks
    def validate_technical_diagram_only(self, image_prompts: str) -> bool:
        """Enforce: Image prompts = TECHNICAL DIAGRAMS ONLY - no cartoons"""
        forbidden_terms = ['cartoon', 'character', 'mascot', 'cute', 'funny face']
        content_lower = image_prompts.lower()
        
        for term in forbidden_terms:
            if term in content_lower:
                self.logger.warning(f"Non-technical content detected: {term}")
                return False
        return True