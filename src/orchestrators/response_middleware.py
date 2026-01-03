"""
Response Middleware - System Message Injection

Injects system messages into orchestrator responses:
- Token warnings (approaching context limit)
- Security alerts (validation issues)
- Deprecation notices (API changes)
- Success enrichment (metadata, metrics)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """System message priority levels."""
    CRITICAL = 1   # Security alerts, breaking errors
    HIGH = 2       # Token warnings, validation failures
    MEDIUM = 3     # Deprecation notices, recommendations
    LOW = 4        # Success enrichment, metadata


@dataclass
class SystemMessage:
    """System message to inject into response."""
    content: str
    priority: MessagePriority
    emoji: str
    section_title: str


class ResponseMiddleware:
    """
    Injects system messages into orchestrator responses.
    
    Checks orchestrator context for signals requiring system messages:
    - token_usage_percentage > 80% → Token warning
    - security_warnings present → Security alerts
    - deprecated_features_used → Deprecation notices
    - success_metadata present → Success enrichment
    
    Features:
        - Priority-based message ordering
        - Configurable warning thresholds
        - Template-driven message formatting
        - Non-intrusive injection (prepends to response)
    
    Example:
        >>> middleware = ResponseMiddleware()
        >>> context = {'token_usage_percentage': 85, 'session_id': 'abc123'}
        >>> messages = middleware.inject_system_messages(rendered_markdown, context)
        >>> print(messages)
        ⚠️ **Token Warning**
        
        You're approaching the context limit (85% used)...
        
        ---
        
        ## 🧠 CORTEX Response
        ...
    """
    
    def __init__(self, token_warning_threshold: int = 80):
        """
        Initialize ResponseMiddleware.
        
        Args:
            token_warning_threshold: Percentage threshold for token warnings (default: 80)
        """
        self.token_warning_threshold = token_warning_threshold
        logger.info(
            f"ResponseMiddleware initialized "
            f"(token_threshold={token_warning_threshold}%)"
        )
    
    def inject_system_messages(
        self,
        rendered_markdown: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Inject system messages into rendered markdown.
        
        Message injection order (by priority):
        1. CRITICAL: Security alerts, breaking errors
        2. HIGH: Token warnings, validation failures
        3. MEDIUM: Deprecation notices, recommendations
        4. LOW: Success enrichment, metadata
        
        Args:
            rendered_markdown: Markdown from ResponseRenderer
            context: Orchestrator execution context
        
        Returns:
            Markdown with system messages prepended
        
        Example:
            >>> middleware = ResponseMiddleware()
            >>> markdown = "## Response\\n\\nSuccess!"
            >>> context = {'token_usage_percentage': 85}
            >>> result = middleware.inject_system_messages(markdown, context)
            >>> print(result)
            ⚠️ **Token Warning**
            ...
            ---
            ## Response
            Success!
        """
        # Collect system messages
        messages: List[SystemMessage] = []
        
        # Check for token warnings
        token_message = self._check_token_warning(context)
        if token_message:
            messages.append(token_message)
        
        # Check for security alerts
        security_messages = self._check_security_alerts(context)
        messages.extend(security_messages)
        
        # Check for deprecation notices
        deprecation_messages = self._check_deprecation_notices(context)
        messages.extend(deprecation_messages)
        
        # Check for success enrichment
        enrichment_message = self._check_success_enrichment(context)
        if enrichment_message:
            messages.append(enrichment_message)
        
        # If no messages, return original markdown
        if not messages:
            return rendered_markdown
        
        # Sort messages by priority
        messages.sort(key=lambda m: m.priority.value)
        
        # Format and prepend messages
        formatted_messages = self._format_messages(messages)
        
        # Combine: system messages + separator + original response
        result = formatted_messages + "\n\n---\n\n" + rendered_markdown
        
        logger.debug(
            f"Injected {len(messages)} system messages "
            f"(priorities: {[m.priority.name for m in messages]})"
        )
        
        return result
    
    def _check_token_warning(self, context: Dict[str, Any]) -> Optional[SystemMessage]:
        """
        Check if token warning should be displayed.
        
        Args:
            context: Orchestrator context
        
        Returns:
            SystemMessage if warning needed, None otherwise
        """
        token_percentage = context.get('token_usage_percentage', 0)
        
        if token_percentage >= self.token_warning_threshold:
            session_id = context.get('session_id', 'unknown')
            total_tokens = context.get('total_tokens', 0)
            
            content = self._format_token_warning(
                token_percentage,
                session_id,
                total_tokens
            )
            
            return SystemMessage(
                content=content,
                priority=MessagePriority.HIGH,
                emoji="⚠️",
                section_title="Token Warning"
            )
        
        return None
    
    def _check_security_alerts(self, context: Dict[str, Any]) -> List[SystemMessage]:
        """
        Check for security validation warnings.
        
        Args:
            context: Orchestrator context
        
        Returns:
            List of security alert messages
        """
        security_warnings = context.get('security_warnings', [])
        if not security_warnings:
            return []
        
        messages = []
        
        for warning in security_warnings:
            content = f"**Security Alert:** {warning}"
            messages.append(SystemMessage(
                content=content,
                priority=MessagePriority.CRITICAL,
                emoji="🚨",
                section_title="Security Alert"
            ))
        
        return messages
    
    def _check_deprecation_notices(self, context: Dict[str, Any]) -> List[SystemMessage]:
        """
        Check for deprecated feature usage.
        
        Args:
            context: Orchestrator context
        
        Returns:
            List of deprecation notice messages
        """
        deprecated_features = context.get('deprecated_features_used', [])
        if not deprecated_features:
            return []
        
        messages = []
        
        for feature in deprecated_features:
            feature_name = feature.get('name', 'unknown')
            replacement = feature.get('replacement', 'See documentation')
            deprecation_version = feature.get('deprecated_in', 'v5.0')
            removal_version = feature.get('removal_in', 'v6.0')
            
            content = (
                f"**Deprecation Notice:** `{feature_name}` is deprecated "
                f"(since {deprecation_version}, will be removed in {removal_version}). "
                f"Use `{replacement}` instead."
            )
            
            messages.append(SystemMessage(
                content=content,
                priority=MessagePriority.MEDIUM,
                emoji="⚠️",
                section_title="Deprecation Notice"
            ))
        
        return messages
    
    def _check_success_enrichment(self, context: Dict[str, Any]) -> Optional[SystemMessage]:
        """
        Check for success metadata to enrich response.
        
        Args:
            context: Orchestrator context
        
        Returns:
            SystemMessage with enrichment, None if no metadata
        """
        success_metadata = context.get('success_metadata', {})
        
        if not success_metadata:
            return None
        
        # Build enrichment content
        enrichment_parts = []
        
        if 'files_modified' in success_metadata:
            count = success_metadata['files_modified']
            enrichment_parts.append(f"📝 Modified {count} file(s)")
        
        if 'tests_passed' in success_metadata:
            passed = success_metadata['tests_passed']
            total = success_metadata.get('tests_total', passed)
            enrichment_parts.append(f"✅ Tests: {passed}/{total} passed")
        
        if 'coverage_percentage' in success_metadata:
            coverage = success_metadata['coverage_percentage']
            enrichment_parts.append(f"📊 Coverage: {coverage}%")
        
        if not enrichment_parts:
            return None
        
        content = " • ".join(enrichment_parts)
        
        return SystemMessage(
            content=content,
            priority=MessagePriority.LOW,
            emoji="ℹ️",
            section_title="Metadata"
        )
    
    def _format_token_warning(
        self,
        percentage: float,
        session_id: str,
        total_tokens: int
    ) -> str:
        """
        Format token warning message.
        
        Args:
            percentage: Token usage percentage
            session_id: Current session ID
            total_tokens: Total tokens used
        
        Returns:
            Formatted warning message
        """
        return (
            f"**Token Warning:** You're approaching the context limit "
            f"({percentage:.1f}% used, {total_tokens:,} tokens).\n\n"
            f"**Recommended Actions:**\n"
            f"1. Use `cortex vacuum` to clean up unused context\n"
            f"2. Create a continuation prompt: `cortex continue {session_id}`\n"
            f"3. Start a new focused session for unrelated tasks"
        )
    
    def _format_messages(self, messages: List[SystemMessage]) -> str:
        """
        Format system messages to markdown.
        
        Args:
            messages: List of system messages
        
        Returns:
            Formatted markdown
        """
        formatted = []
        
        for message in messages:
            section = f"{message.emoji} **{message.section_title}**\n\n{message.content}"
            formatted.append(section)
        
        return "\n\n".join(formatted)
