"""
CORTEX 3.0 Track B: Response Generator
=====================================

Intelligent response generation system that combines templates with dynamic content
to create contextual, helpful responses without code execution.

Key Features:
- Zero-execution response generation
- Context-aware content assembly
- Multi-format output support
- Response optimization and caching
- Integration with CORTEX brain for learning

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from .template_engine import TemplateEngine, TemplateContext, RenderedTemplate, TemplateFormat


class ResponseType(Enum):
    """Types of responses."""
    INSTANT = "instant"          # Immediate template-based response
    CONTEXTUAL = "contextual"    # Context-enhanced response
    DYNAMIC = "dynamic"          # Dynamically assembled response
    CACHED = "cached"            # Previously cached response
    FALLBACK = "fallback"        # Default fallback response


class ResponsePriority(Enum):
    """Response priority levels."""
    CRITICAL = "critical"        # Critical system responses
    HIGH = "high"               # Important user requests
    NORMAL = "normal"           # Standard requests
    LOW = "low"                 # Background or optional responses


@dataclass
class ResponseContext:
    """Extended context for response generation."""
    user_request: str
    session_id: str
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    system_context: Dict[str, Any] = field(default_factory=dict)
    project_context: Dict[str, Any] = field(default_factory=dict)
    environment_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: ResponsePriority = ResponsePriority.NORMAL


@dataclass
class GeneratedResponse:
    """A generated response with metadata."""
    content: str
    format: TemplateFormat
    response_type: ResponseType
    template_id: Optional[str] = None
    generation_time_ms: float = 0
    confidence_score: float = 0.0
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cache_key: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class ResponseCache:
    """Cache entry for responses."""
    cache_key: str
    response: GeneratedResponse
    created_at: datetime
    last_accessed: datetime
    access_count: int
    context_hash: str


class ResponseGenerator:
    """
    Advanced response generator for CORTEX Track B
    
    Combines template engine with intelligent context analysis to generate
    helpful, contextual responses without requiring code execution.
    """
    
    def __init__(self, template_engine: Optional[TemplateEngine] = None):
        self.logger = logging.getLogger("cortex.track_b.response_generator")
        
        # Template engine
        self.template_engine = template_engine or TemplateEngine()
        
        # Response cache
        self.response_cache: Dict[str, ResponseCache] = {}
        self.cache_max_size = 1000
        self.cache_ttl_hours = 24
        
        # Context analyzers
        self.context_extractors: Dict[str, Any] = {}
        
        # Response patterns for learning
        self.response_patterns: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.generation_stats: Dict[str, Dict[str, Any]] = {}
        
        # Initialize built-in components
        self._initialize_context_extractors()
        self._initialize_response_patterns()
        self._initialize_fallback_responses()
    
    def _initialize_context_extractors(self):
        """Initialize context extraction functions."""
        self.context_extractors = {
            'command_intent': self._extract_command_intent,
            'help_category': self._extract_help_category,
            'error_context': self._extract_error_context,
            'project_context': self._extract_project_context,
            'user_expertise': self._extract_user_expertise,
            'response_format': self._extract_response_format,
            'urgency_level': self._extract_urgency_level
        }
    
    def _initialize_response_patterns(self):
        """Initialize common response patterns."""
        self.response_patterns = {
            'help_patterns': {
                'quick_reference': {
                    'triggers': ['quick', 'fast', 'summary', 'list'],
                    'format': 'table',
                    'template_preference': 'help_quick_reference'
                },
                'detailed_guide': {
                    'triggers': ['detailed', 'explain', 'how to', 'tutorial'],
                    'format': 'markdown',
                    'template_preference': 'help_detailed'
                },
                'examples': {
                    'triggers': ['example', 'sample', 'demo'],
                    'format': 'code_block',
                    'template_preference': 'help_examples'
                }
            },
            'status_patterns': {
                'system_health': {
                    'triggers': ['status', 'health', 'state'],
                    'format': 'dashboard',
                    'template_preference': 'status_system'
                },
                'component_status': {
                    'triggers': ['component', 'service', 'module'],
                    'format': 'list',
                    'template_preference': 'status_component'
                }
            },
            'error_patterns': {
                'command_not_found': {
                    'triggers': ['not found', 'unknown', 'invalid'],
                    'format': 'suggestion',
                    'template_preference': 'error_command_not_found'
                },
                'syntax_error': {
                    'triggers': ['syntax', 'parse', 'invalid format'],
                    'format': 'correction',
                    'template_preference': 'error_syntax'
                }
            }
        }
    
    def _initialize_fallback_responses(self):
        """Initialize fallback responses for when templates fail."""
        self.fallback_responses = {
            'general': "I understand you're looking for help, but I couldn't find a specific response. Please try rephrasing your request or use `help` for available commands.",
            'help': "Here are the available commands. Use `help <command>` for detailed information about a specific command.",
            'error': "An error occurred while processing your request. Please check your input and try again.",
            'status': "CORTEX is running normally. Use `status detailed` for more information."
        }
    
    def generate_response(self, user_request: str, context: Optional[ResponseContext] = None) -> GeneratedResponse:
        """Generate a response for the user request."""
        start_time = datetime.now()
        
        try:
            # Create default context if not provided
            if context is None:
                context = ResponseContext(
                    user_request=user_request,
                    session_id="default",
                    timestamp=datetime.now()
                )
            
            # Check cache first
            cached_response = self._check_cache(user_request, context)
            if cached_response:
                self.logger.debug(f"Returning cached response for: {user_request[:50]}...")
                return cached_response
            
            # Extract context information
            extracted_context = self._extract_context(context)
            
            # Generate response using appropriate strategy
            response = self._generate_contextual_response(context, extracted_context)
            
            # Post-process response
            response = self._post_process_response(response, context)
            
            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds() * 1000
            response.generation_time_ms = generation_time
            
            # Cache response if appropriate
            self._cache_response(user_request, context, response)
            
            # Update statistics
            self._update_generation_stats(response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._generate_fallback_response(user_request, context)
    
    def _check_cache(self, user_request: str, context: ResponseContext) -> Optional[GeneratedResponse]:
        """Check if a cached response exists for this request."""
        try:
            cache_key = self._generate_cache_key(user_request, context)
            
            if cache_key in self.response_cache:
                cached_entry = self.response_cache[cache_key]
                
                # Check if cache entry is still valid
                if datetime.now() - cached_entry.created_at < timedelta(hours=self.cache_ttl_hours):
                    # Update access statistics
                    cached_entry.last_accessed = datetime.now()
                    cached_entry.access_count += 1
                    
                    # Return cached response
                    cached_response = cached_entry.response
                    cached_response.response_type = ResponseType.CACHED
                    return cached_response
                else:
                    # Remove expired cache entry
                    del self.response_cache[cache_key]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking cache: {e}")
            return None
    
    def _generate_cache_key(self, user_request: str, context: ResponseContext) -> str:
        """Generate a cache key for the request and context."""
        # Include relevant context for cache key
        cache_data = {
            'request': user_request.lower().strip(),
            'session_id': context.session_id,
            'preferences': context.user_preferences,
            'system_state': context.system_context.get('state', '')
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()[:16]
    
    def _extract_context(self, context: ResponseContext) -> Dict[str, Any]:
        """Extract relevant context information using registered extractors."""
        extracted = {}
        
        for extractor_name, extractor_func in self.context_extractors.items():
            try:
                result = extractor_func(context)
                if result:
                    extracted[extractor_name] = result
            except Exception as e:
                self.logger.error(f"Error in context extractor {extractor_name}: {e}")
        
        return extracted
    
    def _extract_command_intent(self, context: ResponseContext) -> Optional[str]:
        """Extract command intent from user request."""
        request = context.user_request.lower()
        
        # Command patterns
        if request.startswith('/'):
            return request.split()[0][1:]  # Remove the '/' prefix
        
        # Natural language patterns
        intent_patterns = {
            'help': ['help', 'how', 'what', 'explain', 'show', 'guide'],
            'status': ['status', 'health', 'state', 'check', 'info'],
            'plan': ['plan', 'planning', 'strategy', 'roadmap'],
            'execute': ['run', 'execute', 'start', 'launch'],
            'config': ['config', 'configure', 'settings', 'setup']
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in request for pattern in patterns):
                return intent
        
        return 'general'
    
    def _extract_help_category(self, context: ResponseContext) -> Optional[str]:
        """Extract help category from request."""
        request = context.user_request.lower()
        
        categories = {
            'commands': ['command', 'cmd', 'function'],
            'configuration': ['config', 'setup', 'settings'],
            'troubleshooting': ['error', 'issue', 'problem', 'bug'],
            'getting_started': ['start', 'begin', 'new', 'first'],
            'advanced': ['advanced', 'expert', 'complex']
        }
        
        for category, keywords in categories.items():
            if any(keyword in request for keyword in keywords):
                return category
        
        return 'general'
    
    def _extract_error_context(self, context: ResponseContext) -> Optional[Dict[str, Any]]:
        """Extract error context from request."""
        request = context.user_request.lower()
        
        error_indicators = ['error', 'issue', 'problem', 'fail', 'broken', 'not work']
        
        if any(indicator in request for indicator in error_indicators):
            return {
                'has_error': True,
                'error_keywords': [word for word in error_indicators if word in request],
                'context': context.system_context.get('last_error', ''),
                'severity': self._assess_error_severity(request)
            }
        
        return None
    
    def _extract_project_context(self, context: ResponseContext) -> Dict[str, Any]:
        """Extract project-specific context."""
        project_info = context.project_context
        
        return {
            'project_type': project_info.get('type', 'unknown'),
            'language': project_info.get('language', 'unknown'),
            'framework': project_info.get('framework', 'none'),
            'has_tests': project_info.get('has_tests', False),
            'git_status': project_info.get('git_status', 'unknown')
        }
    
    def _extract_user_expertise(self, context: ResponseContext) -> str:
        """Extract or infer user expertise level."""
        # Check user preferences first
        if 'expertise_level' in context.user_preferences:
            return context.user_preferences['expertise_level']
        
        # Infer from conversation history
        if context.conversation_history:
            advanced_keywords = ['advanced', 'complex', 'optimize', 'performance', 'architecture']
            beginner_keywords = ['help', 'how', 'what', 'basic', 'simple', 'guide']
            
            recent_messages = context.conversation_history[-10:]  # Last 10 messages
            advanced_count = sum(1 for msg in recent_messages 
                                if any(keyword in str(msg).lower() for keyword in advanced_keywords))
            beginner_count = sum(1 for msg in recent_messages 
                               if any(keyword in str(msg).lower() for keyword in beginner_keywords))
            
            if advanced_count > beginner_count:
                return 'advanced'
            elif beginner_count > advanced_count:
                return 'beginner'
        
        return 'intermediate'  # Default
    
    def _extract_response_format(self, context: ResponseContext) -> str:
        """Extract preferred response format."""
        request = context.user_request.lower()
        
        format_indicators = {
            'table': ['table', 'list', 'summary', 'quick'],
            'detailed': ['detailed', 'explain', 'comprehensive', 'full'],
            'code': ['code', 'example', 'sample', 'snippet'],
            'json': ['json', 'data', 'structure'],
            'markdown': ['markdown', 'formatted', 'pretty']
        }
        
        for format_type, indicators in format_indicators.items():
            if any(indicator in request for indicator in indicators):
                return format_type
        
        return context.user_preferences.get('preferred_format', 'markdown')
    
    def _extract_urgency_level(self, context: ResponseContext) -> str:
        """Extract urgency level from request."""
        request = context.user_request.lower()
        
        urgent_keywords = ['urgent', 'critical', 'emergency', 'asap', 'immediately']
        low_keywords = ['when possible', 'later', 'eventually', 'low priority']
        
        if any(keyword in request for keyword in urgent_keywords):
            return 'urgent'
        elif any(keyword in request for keyword in low_keywords):
            return 'low'
        
        return 'normal'
    
    def _assess_error_severity(self, request: str) -> str:
        """Assess the severity of an error from the request."""
        critical_keywords = ['critical', 'fatal', 'crash', 'broken', 'emergency']
        high_keywords = ['error', 'fail', 'issue', 'problem']
        low_keywords = ['warning', 'minor', 'small', 'cosmetic']
        
        if any(keyword in request for keyword in critical_keywords):
            return 'critical'
        elif any(keyword in request for keyword in high_keywords):
            return 'high'
        elif any(keyword in request for keyword in low_keywords):
            return 'low'
        
        return 'medium'
    
    def _generate_contextual_response(self, context: ResponseContext, extracted_context: Dict[str, Any]) -> GeneratedResponse:
        """Generate a contextual response using templates and context."""
        try:
            # Determine the best response strategy
            response_strategy = self._determine_response_strategy(extracted_context)
            
            # Prepare template context
            template_context = self._prepare_template_context(context, extracted_context)
            
            # Select and render template
            rendered = self.template_engine.render_response(
                context.user_request, 
                template_context
            )
            
            if rendered:
                response = GeneratedResponse(
                    content=rendered.content,
                    format=rendered.format,
                    response_type=ResponseType.CONTEXTUAL,
                    template_id=rendered.template_id,
                    confidence_score=self._calculate_confidence_score(rendered, extracted_context),
                    sources=['template_engine', 'context_analysis'],
                    metadata=rendered.metadata
                )
            else:
                # Fall back to pattern-based response
                response = self._generate_pattern_based_response(context, extracted_context)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating contextual response: {e}")
            return self._generate_fallback_response(context.user_request, context)
    
    def _determine_response_strategy(self, extracted_context: Dict[str, Any]) -> str:
        """Determine the best response generation strategy."""
        command_intent = extracted_context.get('command_intent', 'general')
        user_expertise = extracted_context.get('user_expertise', 'intermediate')
        response_format = extracted_context.get('response_format', 'markdown')
        
        # Strategy selection logic
        if command_intent == 'help':
            if user_expertise == 'beginner':
                return 'guided_help'
            elif user_expertise == 'advanced':
                return 'technical_reference'
            else:
                return 'standard_help'
        
        elif command_intent == 'status':
            return 'dashboard_status'
        
        elif extracted_context.get('error_context'):
            return 'error_resolution'
        
        else:
            return 'general_assistance'
    
    def _prepare_template_context(self, context: ResponseContext, extracted_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context variables for template rendering."""
        template_vars = {}
        
        # Basic context
        template_vars.update({
            'user_request': context.user_request,
            'session_id': context.session_id,
            'timestamp': context.timestamp.isoformat(),
            'user_expertise': extracted_context.get('user_expertise', 'intermediate'),
            'response_format': extracted_context.get('response_format', 'markdown')
        })
        
        # System context
        if context.system_context:
            template_vars.update(context.system_context)
        
        # Project context
        if context.project_context:
            template_vars.update(context.project_context)
        
        # Error context
        if extracted_context.get('error_context'):
            template_vars.update(extracted_context['error_context'])
        
        return template_vars
    
    def _generate_pattern_based_response(self, context: ResponseContext, extracted_context: Dict[str, Any]) -> GeneratedResponse:
        """Generate response using pattern matching when template fails."""
        try:
            command_intent = extracted_context.get('command_intent', 'general')
            
            # Find matching pattern
            pattern_category = f"{command_intent}_patterns"
            
            if pattern_category in self.response_patterns:
                patterns = self.response_patterns[pattern_category]
                
                # Find best matching pattern
                best_pattern = None
                best_score = 0
                
                for pattern_name, pattern_info in patterns.items():
                    score = 0
                    for trigger in pattern_info['triggers']:
                        if trigger in context.user_request.lower():
                            score += 1
                    
                    if score > best_score:
                        best_score = score
                        best_pattern = pattern_info
                
                if best_pattern:
                    # Generate response based on pattern
                    content = self._generate_content_from_pattern(best_pattern, context, extracted_context)
                    
                    return GeneratedResponse(
                        content=content,
                        format=TemplateFormat.MARKDOWN,
                        response_type=ResponseType.DYNAMIC,
                        confidence_score=min(best_score / len(best_pattern['triggers']), 1.0),
                        sources=['pattern_matching'],
                        metadata={'pattern_used': pattern_name}
                    )
            
            # If no pattern matches, use fallback
            return self._generate_fallback_response(context.user_request, context)
            
        except Exception as e:
            self.logger.error(f"Error generating pattern-based response: {e}")
            return self._generate_fallback_response(context.user_request, context)
    
    def _generate_content_from_pattern(self, pattern: Dict[str, Any], context: ResponseContext, extracted_context: Dict[str, Any]) -> str:
        """Generate content based on a response pattern."""
        pattern_format = pattern.get('format', 'markdown')
        
        if pattern_format == 'table':
            return self._generate_table_response(context, extracted_context)
        elif pattern_format == 'list':
            return self._generate_list_response(context, extracted_context)
        elif pattern_format == 'dashboard':
            return self._generate_dashboard_response(context, extracted_context)
        else:
            return self._generate_markdown_response(context, extracted_context)
    
    def _generate_table_response(self, context: ResponseContext, extracted_context: Dict[str, Any]) -> str:
        """Generate a table-formatted response."""
        return f"""# Quick Reference

| Item | Description |
|------|-------------|
| Request | {context.user_request} |
| Intent | {extracted_context.get('command_intent', 'general')} |
| Expertise | {extracted_context.get('user_expertise', 'intermediate')} |

Use `help <command>` for detailed information.
"""
    
    def _generate_list_response(self, context: ResponseContext, extracted_context: Dict[str, Any]) -> str:
        """Generate a list-formatted response."""
        return f"""# Response to: {context.user_request}

- **Intent**: {extracted_context.get('command_intent', 'general')}
- **Category**: {extracted_context.get('help_category', 'general')}
- **Format**: {extracted_context.get('response_format', 'markdown')}

**Available Actions:**
1. Get more help: `help detailed`
2. Check system status: `status`
3. View configuration: `config`
"""
    
    def _generate_dashboard_response(self, context: ResponseContext, extracted_context: Dict[str, Any]) -> str:
        """Generate a dashboard-style response."""
        return f"""# 📊 CORTEX Dashboard

**System Status**: 🟢 Running  
**Session**: {context.session_id}  
**Time**: {context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Quick Stats
- **User Expertise**: {extracted_context.get('user_expertise', 'intermediate')}
- **Response Format**: {extracted_context.get('response_format', 'markdown')}
- **Project Type**: {extracted_context.get('project_context', {}).get('project_type', 'unknown')}

## Recent Activity
Your request: "{context.user_request}"
"""
    
    def _generate_markdown_response(self, context: ResponseContext, extracted_context: Dict[str, Any]) -> str:
        """Generate a markdown-formatted response."""
        return f"""# Response to Your Request

You asked: "{context.user_request}"

Based on the context analysis, I understand you're looking for **{extracted_context.get('command_intent', 'general')} assistance**.

## Next Steps

1. **Clarify your request** - Provide more specific details about what you need
2. **Check available commands** - Use `help` to see all available options  
3. **Review documentation** - Access detailed guides for complex topics

**Your expertise level**: {extracted_context.get('user_expertise', 'intermediate')}  
**Preferred format**: {extracted_context.get('response_format', 'markdown')}
"""
    
    def _calculate_confidence_score(self, rendered: RenderedTemplate, extracted_context: Dict[str, Any]) -> float:
        """Calculate confidence score for the response."""
        score = 0.5  # Base confidence
        
        # Template match score
        if rendered.template_id:
            score += 0.3
        
        # Context richness score
        context_factors = len(extracted_context)
        score += min(context_factors * 0.05, 0.2)
        
        # Ensure score is between 0 and 1
        return min(max(score, 0.0), 1.0)
    
    def _post_process_response(self, response: GeneratedResponse, context: ResponseContext) -> GeneratedResponse:
        """Post-process the response for optimization and personalization."""
        try:
            # Apply user preferences
            if context.user_preferences.get('concise_responses'):
                response.content = self._make_response_concise(response.content)
            
            # Add contextual footer if helpful
            if context.user_preferences.get('show_hints', True):
                response.content += self._generate_contextual_footer(context)
            
            # Format for user expertise level
            expertise = context.user_preferences.get('expertise_level', 'intermediate')
            if expertise == 'beginner':
                response.content = self._add_beginner_explanations(response.content)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error post-processing response: {e}")
            return response
    
    def _make_response_concise(self, content: str) -> str:
        """Make the response more concise."""
        # Simple concise transformation
        lines = content.split('\n')
        concise_lines = []
        
        for line in lines:
            # Skip empty lines and reduce verbosity
            if line.strip() and not line.startswith('**') or len(line.strip()) > 10:
                concise_lines.append(line)
        
        return '\n'.join(concise_lines[:10])  # Limit to 10 lines
    
    def _generate_contextual_footer(self, context: ResponseContext) -> str:
        """Generate a contextual footer with helpful hints."""
        footer_parts = []
        
        # Add session info if useful
        if context.session_id != "default":
            footer_parts.append(f"Session: {context.session_id}")
        
        # Add common next actions
        footer_parts.append("💡 **Tip**: Use `help` for more commands or `status` for system info")
        
        return "\n\n---\n" + " | ".join(footer_parts)
    
    def _add_beginner_explanations(self, content: str) -> str:
        """Add explanations for beginners."""
        # Add simple explanations for technical terms
        explanations = {
            'template': 'template (a reusable content format)',
            'context': 'context (relevant information)',
            'response': 'response (answer or reply)',
        }
        
        for term, explanation in explanations.items():
            content = content.replace(term, explanation)
        
        return content
    
    def _generate_fallback_response(self, user_request: str, context: Optional[ResponseContext] = None) -> GeneratedResponse:
        """Generate a fallback response when other methods fail."""
        try:
            # Determine fallback category
            request_lower = user_request.lower()
            
            if any(word in request_lower for word in ['help', 'how', 'what']):
                fallback_content = self.fallback_responses['help']
            elif any(word in request_lower for word in ['status', 'state']):
                fallback_content = self.fallback_responses['status']
            elif any(word in request_lower for word in ['error', 'issue']):
                fallback_content = self.fallback_responses['error']
            else:
                fallback_content = self.fallback_responses['general']
            
            return GeneratedResponse(
                content=fallback_content,
                format=TemplateFormat.PLAIN_TEXT,
                response_type=ResponseType.FALLBACK,
                confidence_score=0.3,
                sources=['fallback'],
                metadata={'fallback_reason': 'template_and_pattern_failed'}
            )
            
        except Exception as e:
            self.logger.error(f"Error generating fallback response: {e}")
            return GeneratedResponse(
                content="I'm having trouble processing your request. Please try again.",
                format=TemplateFormat.PLAIN_TEXT,
                response_type=ResponseType.FALLBACK,
                confidence_score=0.1,
                sources=['emergency_fallback']
            )
    
    def _cache_response(self, user_request: str, context: ResponseContext, response: GeneratedResponse):
        """Cache the response for future use."""
        try:
            # Don't cache fallback responses or errors
            if response.response_type == ResponseType.FALLBACK or response.confidence_score < 0.5:
                return
            
            cache_key = self._generate_cache_key(user_request, context)
            
            # Clean cache if it's getting too large
            if len(self.response_cache) >= self.cache_max_size:
                self._clean_cache()
            
            # Create cache entry
            context_hash = hashlib.sha256(json.dumps(context.__dict__, default=str, sort_keys=True).encode()).hexdigest()[:8]
            
            cache_entry = ResponseCache(
                cache_key=cache_key,
                response=response,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                context_hash=context_hash
            )
            
            response.cache_key = cache_key
            response.expires_at = datetime.now() + timedelta(hours=self.cache_ttl_hours)
            
            self.response_cache[cache_key] = cache_entry
            
        except Exception as e:
            self.logger.error(f"Error caching response: {e}")
    
    def _clean_cache(self):
        """Clean old entries from the cache."""
        try:
            now = datetime.now()
            expired_keys = []
            
            # Find expired entries
            for cache_key, cache_entry in self.response_cache.items():
                if now - cache_entry.created_at > timedelta(hours=self.cache_ttl_hours):
                    expired_keys.append(cache_key)
            
            # Remove expired entries
            for key in expired_keys:
                del self.response_cache[key]
            
            # If still too large, remove least recently accessed
            if len(self.response_cache) >= self.cache_max_size:
                sorted_entries = sorted(
                    self.response_cache.items(),
                    key=lambda x: (x[1].last_accessed, x[1].access_count)
                )
                
                # Remove oldest 25% of entries
                remove_count = len(sorted_entries) // 4
                for i in range(remove_count):
                    del self.response_cache[sorted_entries[i][0]]
            
            self.logger.debug(f"Cache cleaned. Current size: {len(self.response_cache)}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning cache: {e}")
    
    def _update_generation_stats(self, response: GeneratedResponse):
        """Update generation statistics."""
        try:
            response_type = response.response_type.value
            
            if response_type not in self.generation_stats:
                self.generation_stats[response_type] = {
                    'count': 0,
                    'total_time_ms': 0,
                    'avg_time_ms': 0,
                    'avg_confidence': 0,
                    'success_rate': 0
                }
            
            stats = self.generation_stats[response_type]
            stats['count'] += 1
            stats['total_time_ms'] += response.generation_time_ms
            stats['avg_time_ms'] = stats['total_time_ms'] / stats['count']
            
            # Update confidence average
            total_confidence = stats['avg_confidence'] * (stats['count'] - 1) + response.confidence_score
            stats['avg_confidence'] = total_confidence / stats['count']
            
            # Update success rate (responses with confidence > 0.5)
            if response.confidence_score > 0.5:
                stats['success_rate'] = ((stats['success_rate'] * (stats['count'] - 1)) + 1) / stats['count']
            else:
                stats['success_rate'] = (stats['success_rate'] * (stats['count'] - 1)) / stats['count']
                
        except Exception as e:
            self.logger.error(f"Error updating generation stats: {e}")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get response generation statistics."""
        total_responses = sum(stats['count'] for stats in self.generation_stats.values())
        
        return {
            'total_responses': total_responses,
            'cache_size': len(self.response_cache),
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'by_type': self.generation_stats,
            'average_confidence': self._calculate_average_confidence(),
            'template_stats': self.template_engine.get_template_stats()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        cached_count = sum(1 for entry in self.response_cache.values() if entry.access_count > 0)
        total_count = len(self.response_cache)
        
        return (cached_count / total_count * 100) if total_count > 0 else 0
    
    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence across all response types."""
        if not self.generation_stats:
            return 0
        
        total_confidence = sum(stats['avg_confidence'] * stats['count'] for stats in self.generation_stats.values())
        total_count = sum(stats['count'] for stats in self.generation_stats.values())
        
        return total_confidence / total_count if total_count > 0 else 0