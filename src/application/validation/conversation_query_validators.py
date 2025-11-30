"""Validators for conversation-related queries"""
from src.application.validation.validator import Validator
from src.application.queries.conversation_queries import (
    SearchContextQuery,
    GetConversationQualityQuery,
    FindSimilarPatternsQuery
)


class SearchContextQueryValidator(Validator[SearchContextQuery]):
    """Validator for SearchContextQuery
    
    Validates:
    - search_text is not empty and within length limits
    - namespace_filter follows format if provided
    - min_relevance is between 0.0 and 1.0
    - max_results is positive and within limits
    """
    
    def __init__(self):
        super().__init__()
        
        # Required fields
        self.rule_for(lambda x: x.search_text).not_empty() \
            .with_message("Search text is required") \
            .min_length(2) \
            .with_message("Search text must be at least 2 characters") \
            .max_length(500) \
            .with_message("Search text cannot exceed 500 characters")
        
        # Optional namespace filter
        self.rule_for(lambda x: x.namespace_filter) \
            .matches(r'^[a-zA-Z0-9._-]+$') \
            .with_message("Namespace must contain only letters, numbers, dots, hyphens, and underscores") \
            .when(lambda x: x.namespace_filter is not None and x.namespace_filter.strip())
        
        # Relevance constraints
        self.rule_for(lambda x: x.min_relevance) \
            .must(lambda score: 0.0 <= score <= 1.0) \
            .with_message("Minimum relevance must be between 0.0 and 1.0")
        
        # Results constraints
        self.rule_for(lambda x: x.max_results) \
            .must(lambda n: n > 0) \
            .with_message("Maximum results must be positive") \
            .must(lambda n: n <= 100) \
            .with_message("Maximum results cannot exceed 100")


class GetConversationQualityQueryValidator(Validator[GetConversationQualityQuery]):
    """Validator for GetConversationQualityQuery
    
    Validates:
    - conversation_id is not empty
    """
    
    def __init__(self):
        super().__init__()
        
        self.rule_for(lambda x: x.conversation_id).not_empty() \
            .with_message("Conversation ID is required")


class FindSimilarPatternsQueryValidator(Validator[FindSimilarPatternsQuery]):
    """Validator for FindSimilarPatternsQuery
    
    Validates:
    - context is not empty and within length limits
    - namespace is not empty and follows format
    - pattern_type is valid if provided
    - min_confidence is between 0.0 and 1.0
    - max_results is positive and within limits
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
        self.rule_for(lambda x: x.context).not_empty() \
            .with_message("Context is required") \
            .min_length(10) \
            .with_message("Context must be at least 10 characters") \
            .max_length(5000) \
            .with_message("Context cannot exceed 5000 characters")
        
        self.rule_for(lambda x: x.namespace).not_empty() \
            .with_message("Namespace is required") \
            .matches(r'^[a-zA-Z0-9._-]+$') \
            .with_message("Namespace must contain only letters, numbers, dots, hyphens, and underscores")
        
        # Optional pattern type filter
        self.rule_for(lambda x: x.pattern_type) \
            .must(lambda pt: pt in self.VALID_PATTERN_TYPES) \
            .with_message(
                f"Pattern type must be one of: {', '.join(self.VALID_PATTERN_TYPES)}"
            ) \
            .when(lambda x: x.pattern_type is not None and x.pattern_type.strip())
        
        # Confidence constraints
        self.rule_for(lambda x: x.min_confidence) \
            .must(lambda score: 0.0 <= score <= 1.0) \
            .with_message("Minimum confidence must be between 0.0 and 1.0")
        
        # Results constraints
        self.rule_for(lambda x: x.max_results) \
            .must(lambda n: n > 0) \
            .with_message("Maximum results must be positive") \
            .must(lambda n: n <= 100) \
            .with_message("Maximum results cannot exceed 100")
