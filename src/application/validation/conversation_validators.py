"""Validators for conversation-related commands and queries"""
from datetime import datetime, timedelta
from src.application.validation.validator import Validator
from src.application.commands.conversation_commands import (
    CaptureConversationCommand,
    LearnPatternCommand,
    UpdateContextRelevanceCommand,
    UpdatePatternConfidenceCommand
)


class CaptureConversationValidator(Validator[CaptureConversationCommand]):
    """Validator for CaptureConversationCommand
    
    Validates:
    - conversation_id is not empty
    - title is not empty and within length limits
    - content is not empty and has minimum length
    - file_path is not empty
    - quality_score is between 0.0 and 1.0 if provided
    - entity_count is non-negative if provided
    - captured_at is not in the future if provided
    """
    
    def __init__(self):
        super().__init__()
        
        # Required fields
        self.rule_for(lambda x: x.conversation_id).not_empty() \
            .with_message("Conversation ID is required")
        
        self.rule_for(lambda x: x.title).not_empty() \
            .with_message("Title is required") \
            .max_length(500) \
            .with_message("Title cannot exceed 500 characters")
        
        self.rule_for(lambda x: x.content).not_empty() \
            .with_message("Content is required") \
            .min_length(10) \
            .with_message("Content must be at least 10 characters")
        
        self.rule_for(lambda x: x.file_path).not_empty() \
            .with_message("File path is required")
        
        # Optional fields with constraints
        self.rule_for(lambda x: x.quality_score) \
            .must(lambda score: score is None or 0.0 <= score <= 1.0) \
            .with_message("Quality score must be between 0.0 and 1.0") \
            .when(lambda x: x.quality_score is not None)
        
        self.rule_for(lambda x: x.entity_count) \
            .must(lambda count: count is None or count >= 0) \
            .with_message("Entity count cannot be negative") \
            .when(lambda x: x.entity_count is not None)
        
        self.rule_for(lambda x: x.captured_at) \
            .must(lambda dt: dt is None or dt <= datetime.now()) \
            .with_message("Captured date cannot be in the future") \
            .when(lambda x: x.captured_at is not None)


class LearnPatternValidator(Validator[LearnPatternCommand]):
    """Validator for LearnPatternCommand
    
    Validates:
    - pattern_id is not empty
    - pattern_name is not empty and within length limits
    - pattern_type is a valid type
    - pattern_content is not empty
    - source_conversation_id is not empty
    - namespace is not empty and follows format
    - confidence_score is between 0.0 and 1.0
    - tags are valid if provided
    """
    
    VALID_PATTERN_TYPES = [
        'code_structure',
        'architecture',
        'best_practice',
        'anti_pattern',
        'optimization',
        'bug_fix',
        'design_pattern',
        'decision_pattern'
    ]
    
    def __init__(self):
        super().__init__()
        
        # Required fields
        self.rule_for(lambda x: x.pattern_id).not_empty() \
            .with_message("Pattern ID is required")
        
        self.rule_for(lambda x: x.pattern_name).not_empty() \
            .with_message("Pattern name is required") \
            .max_length(200) \
            .with_message("Pattern name cannot exceed 200 characters")
        
        self.rule_for(lambda x: x.pattern_type).not_empty() \
            .with_message("Pattern type is required") \
            .must(lambda pt: pt in self.VALID_PATTERN_TYPES) \
            .with_message(
                f"Pattern type must be one of: {', '.join(self.VALID_PATTERN_TYPES)}"
            )
        
        self.rule_for(lambda x: x.pattern_content).not_empty() \
            .with_message("Pattern content is required")
        
        self.rule_for(lambda x: x.source_conversation_id).not_empty() \
            .with_message("Source conversation ID is required")
        
        self.rule_for(lambda x: x.namespace).not_empty() \
            .with_message("Namespace is required") \
            .matches(r'^[a-zA-Z0-9._-]+$') \
            .with_message("Namespace must contain only letters, numbers, dots, hyphens, and underscores")
        
        self.rule_for(lambda x: x.confidence_score) \
            .must(lambda score: 0.0 <= score <= 1.0) \
            .with_message("Confidence score must be between 0.0 and 1.0")
        
        # Optional fields with constraints
        self.rule_for(lambda x: x.tags) \
            .must(lambda tags: tags is None or all(isinstance(t, str) and t.strip() for t in tags)) \
            .with_message("All tags must be non-empty strings") \
            .when(lambda x: x.tags is not None)
        
        self.rule_for(lambda x: x.learned_at) \
            .must(lambda dt: dt is None or dt <= datetime.now()) \
            .with_message("Learned date cannot be in the future") \
            .when(lambda x: x.learned_at is not None)


class UpdateContextRelevanceValidator(Validator[UpdateContextRelevanceCommand]):
    """Validator for UpdateContextRelevanceCommand
    
    Validates:
    - conversation_id is not empty
    - new_relevance_score is between 0.0 and 1.0
    - reason is not empty and within length limits
    - updated_at is not in the future if provided
    """
    
    def __init__(self):
        super().__init__()
        
        # Required fields
        self.rule_for(lambda x: x.conversation_id).not_empty() \
            .with_message("Conversation ID is required")
        
        self.rule_for(lambda x: x.new_relevance_score) \
            .must(lambda score: 0.0 <= score <= 1.0) \
            .with_message("Relevance score must be between 0.0 and 1.0")
        
        self.rule_for(lambda x: x.reason).not_empty() \
            .with_message("Reason is required") \
            .max_length(1000) \
            .with_message("Reason cannot exceed 1000 characters")
        
        # Optional fields with constraints
        self.rule_for(lambda x: x.updated_at) \
            .must(lambda dt: dt is None or dt <= datetime.now()) \
            .with_message("Updated date cannot be in the future") \
            .when(lambda x: x.updated_at is not None)


class UpdatePatternConfidenceValidator(Validator[UpdatePatternConfidenceCommand]):
    """Validator for UpdatePatternConfidenceCommand
    
    Validates:
    - pattern_id is not empty
    - context_id is not empty
    - feedback is within length limits if provided
    - updated_at is not in the future if provided
    """
    
    def __init__(self):
        super().__init__()
        
        # Required fields
        self.rule_for(lambda x: x.pattern_id).not_empty() \
            .with_message("Pattern ID is required")
        
        self.rule_for(lambda x: x.context_id).not_empty() \
            .with_message("Context ID is required")
        
        # Optional fields with constraints
        self.rule_for(lambda x: x.feedback) \
            .max_length(2000) \
            .with_message("Feedback cannot exceed 2000 characters") \
            .when(lambda x: x.feedback is not None and x.feedback.strip())
        
        self.rule_for(lambda x: x.updated_at) \
            .must(lambda dt: dt is None or dt <= datetime.now()) \
            .with_message("Updated date cannot be in the future") \
            .when(lambda x: x.updated_at is not None)
