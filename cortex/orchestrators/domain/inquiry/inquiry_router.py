"""InquiryRouter - Route questions to appropriate handlers.

AC-ID: INQUIRY-007-NEW
Purpose: Route inquiries to specialized or generic handlers
Author: Asif Hussain
Date: 2026-01-27

Routing Logic:
- USER_REPO → GenericCodeInquiryHandler (always)
- CORTEX + specialized handler available → ArchitectureInquiryHandler etc.
- CORTEX + specialized handler unavailable → GenericCodeInquiryHandler (fallback)
"""

from typing import Optional

from cortex.models.inquiry_models import AssembledContext, InquiryCategory
from cortex.orchestrators.domain.inquiry.base_inquiry_handler import (
    BaseInquiryHandler,
)
from cortex.orchestrators.domain.inquiry.generic_code_inquiry_handler import (
    GenericCodeInquiryHandler,
)


class InquiryRouter:
    """Routes inquiries to appropriate handlers.
    
    Selects between specialized CORTEX handlers and generic code handler
    based on repository type and category.
    """
    
    def __init__(self) -> None:
        """Initialize router with handler registry."""
        self.generic_handler = GenericCodeInquiryHandler()
        
        # Specialized handlers (will be implemented in subsequent tasks)
        self.specialized_handlers: dict[InquiryCategory, Optional[BaseInquiryHandler]] = {
            InquiryCategory.ARCHITECTURE: None,  # INQUIRY-009
            InquiryCategory.FEATURE: None,  # INQUIRY-010
            InquiryCategory.BEST_PRACTICE: None,  # INQUIRY-011
            InquiryCategory.TROUBLESHOOTING: None,  # INQUIRY-012
            InquiryCategory.EVOLUTION: None,  # INQUIRY-013
        }
    
    def route(self, context: AssembledContext) -> BaseInquiryHandler:
        """Route inquiry to appropriate handler.
        
        Args:
            context: Assembled context with repo type and category
            
        Returns:
            Handler instance to process the inquiry
        """
        # User repos always use generic handler
        if not context.repo_context.is_cortex_repo():
            return self.generic_handler
        
        # CORTEX repos: try specialized handler first
        specialized = self.specialized_handlers.get(context.category)
        
        if specialized is not None:
            return specialized
        
        # Fallback to generic handler
        return self.generic_handler
    
    def register_handler(
        self,
        category: InquiryCategory,
        handler: BaseInquiryHandler,
    ) -> None:
        """Register specialized handler for category.
        
        Args:
            category: Inquiry category
            handler: Handler instance
        """
        self.specialized_handlers[category] = handler
