"""
Response Middleware - System message injection and formatting.

Adds system messages, security warnings, deprecation notices, and token usage
indicators to rendered markdown responses.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, List, Optional


class ResponseMiddleware:
    """
    Middleware for response processing and enhancement.
    
    Features:
    - Injects system messages and warnings
    - Adds token usage indicators
    - Inserts security warnings
    - Marks deprecated features
    - Adds continuation protocol messages
    """
    
    def __init__(self):
        """Initialize response middleware."""
        self.logger = logging.getLogger("cortex.orchestrators.response_middleware")
        self.logger.info("ResponseMiddleware initialized")
    
    def process(self, response: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process and enhance response with system messages.
        
        Args:
            response: Rendered markdown response
            context: Context with optional system messages
        
        Returns:
            Enhanced response with injected system messages
        """
        context = context or {}
        
        # Inject system messages in order of precedence
        enhanced = response
        
        # 1. Token usage warning (high priority)
        if context.get("token_usage_percentage", 0) > 80:
            enhanced = self._inject_token_warning(enhanced, context.get("token_usage_percentage", 0))
        
        # 2. Security warnings
        if context.get("security_warnings"):
            enhanced = self._inject_security_warnings(enhanced, context["security_warnings"])
        
        # 3. Deprecated features
        if context.get("deprecated_features_used"):
            enhanced = self._inject_deprecation_notices(enhanced, context["deprecated_features_used"])
        
        # 4. Continuation protocol
        if context.get("session_id"):
            enhanced = self._inject_continuation_protocol(enhanced, context["session_id"])
        
        self.logger.debug(f"Response enhanced with {len(context.get('security_warnings', []))} warnings")
        return enhanced
    
    def inject_system_messages(
        self,
        markdown: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Inject system messages into rendered markdown.
        
        This is the primary entry point for message injection during rendering.
        
        Args:
            markdown: Rendered markdown to enhance
            context: Context with messages to inject
        
        Returns:
            Enhanced markdown with system messages
        """
        return self.process(markdown, context)
    
    def _inject_token_warning(self, markdown: str, usage_percentage: float) -> str:
        """
        Inject token usage warning when approaching limit.
        
        Added right after header, before main content.
        """
        warning = (
            f"\n⚠️ **Token Usage Alert:** {usage_percentage:.0f}% of context window used. "
            f"Consider saving work or starting new session.\n"
        )
        
        # Insert after header (after first ---)
        if "---" in markdown:
            parts = markdown.split("---", 1)
            return f"{parts[0]}---{warning}{parts[1]}"
        else:
            return warning + markdown
    
    def _inject_security_warnings(self, markdown: str, warnings: List[str]) -> str:
        """
        Inject security warnings section.
        
        Added before main content.
        """
        if not warnings:
            return markdown
        
        section = "\n🔒 **SECURITY NOTICES:**\n"
        for warning in warnings:
            section += f"• {warning}\n"
        
        # Insert after header
        if "---" in markdown:
            parts = markdown.split("---", 1)
            return f"{parts[0]}---{section}{parts[1]}"
        else:
            return markdown + section
    
    def _inject_deprecation_notices(self, markdown: str, features: List[str]) -> str:
        """
        Inject deprecation notices for used deprecated features.
        
        Added before main content.
        """
        if not features:
            return markdown
        
        section = "\n📵 **DEPRECATED FEATURES:**\n"
        for feature in features:
            section += f"• {feature} - Plan migration to supported alternative\n"
        
        # Insert after header
        if "---" in markdown:
            parts = markdown.split("---", 1)
            return f"{parts[0]}---{section}{parts[1]}"
        else:
            return markdown + section
    
    def _inject_continuation_protocol(self, markdown: str, session_id: str) -> str:
        """
        Inject continuation protocol message at end.
        
        Enables resuming work in future sessions.
        """
        continuation = (
            f"\n\n---\n📋 **CONTINUATION:** To resume this work, use: "
            f"`continue {session_id}`\n"
        )
        
        return markdown + continuation
