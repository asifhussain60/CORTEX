"""
CORTEX Template Renderer v3.0 - Intelligent Adaptation Engine

This module implements intelligent template rendering with context-aware adaptation.
Templates automatically adjust format, verbosity, and challenge sections based on request context.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0.0
"""

import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RequestComplexity(Enum):
    """Request complexity levels for adaptation routing"""
    SIMPLE = "simple"  # Status checks, help queries
    MODERATE = "moderate"  # Single-phase implementations, bug fixes
    COMPLEX = "complex"  # Multi-phase features, architecture


class ContentType(Enum):
    """Content type classification"""
    INFORMATIONAL = "informational"  # Explaining concepts
    ACTIONABLE = "actionable"  # Implementation, changes made
    ANALYTICAL = "analytical"  # Status reports, test results, metrics
    PLANNING = "planning"  # Feature planning, design decisions


class InformationDensity(Enum):
    """Information density levels"""
    LOW = "low"  # 1-2 key points
    MEDIUM = "medium"  # 3-5 key points
    HIGH = "high"  # 6+ key points, tables, complex data


class ResponseFormat(Enum):
    """Available response formats"""
    CONCISE = "concise"  # 2-3 sentences
    SUMMARIZED = "summarized"  # Summary + collapsible details
    DETAILED = "detailed"  # Subsections with full context
    VISUAL = "visual"  # Tables, progress bars, visual indicators


class ChallengeMode(Enum):
    """Challenge section display modes"""
    SKIP = "skip"  # Don't show at all
    ACCEPT_ONLY = "accept_only"  # Brief acceptance
    CHALLENGE_ONLY = "challenge_only"  # Show concern + alternative
    MIXED = "mixed"  # Accept + minor adjustment
    INTELLIGENT = "intelligent"  # Decide based on context


@dataclass
class RequestContext:
    """Context information for intelligent adaptation"""
    complexity: RequestComplexity
    content_type: ContentType
    density: InformationDensity
    user_request: str
    has_validation_concerns: bool = False
    referenced_files_exist: bool = True
    security_concerns: bool = False


@dataclass
class AdaptationDecision:
    """Decisions made by adaptation engine"""
    format: ResponseFormat
    challenge_mode: ChallengeMode
    show_code: bool
    code_display_type: str  # "none", "pseudocode", "snippet", "full"
    use_collapsible: bool
    token_budget: int


class TemplateRenderer:
    """
    Intelligent template renderer with context-aware adaptation.
    
    Features:
    - Automatic format selection based on request context
    - Smart challenge section routing (skip, accept-only, challenge-only, mixed)
    - Progressive disclosure with collapsible sections
    - Token budget enforcement
    - Component caching for performance
    """
    
    def __init__(self, templates_path: str):
        """
        Initialize template renderer.
        
        Args:
            templates_path: Path to templates-v3-intelligent.yaml
        """
        self.templates_path = Path(templates_path)
        self.templates = self._load_templates()
        self.component_cache: Dict[str, str] = {}
        
    def _load_templates(self) -> Dict[str, Any]:
        """Load templates from YAML file"""
        with open(self.templates_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data.get('templates', {})
    
    def detect_context(self, user_request: str) -> RequestContext:
        """
        Analyze user request to determine rendering context.
        
        Args:
            user_request: The user's natural language request
            
        Returns:
            RequestContext with detected complexity, type, and density
        """
        request_lower = user_request.lower()
        
        # Detect complexity
        if any(word in request_lower for word in ["status", "help", "what is", "show me"]):
            complexity = RequestComplexity.SIMPLE
        elif any(word in request_lower for word in ["plan", "design", "architecture", "multiple phases"]):
            complexity = RequestComplexity.COMPLEX
        else:
            complexity = RequestComplexity.MODERATE
        
        # Detect content type
        if any(word in request_lower for word in ["what", "how", "explain", "tell me"]):
            content_type = ContentType.INFORMATIONAL
        elif any(word in request_lower for word in ["test", "results", "status", "metrics", "coverage"]):
            content_type = ContentType.ANALYTICAL
        elif any(word in request_lower for word in ["plan", "design", "roadmap"]):
            content_type = ContentType.PLANNING
        else:
            content_type = ContentType.ACTIONABLE
        
        # Detect information density
        word_count = len(user_request.split())
        if word_count < 10:
            density = InformationDensity.LOW
        elif word_count < 30:
            density = InformationDensity.MEDIUM
        else:
            density = InformationDensity.HIGH
        
        return RequestContext(
            complexity=complexity,
            content_type=content_type,
            density=density,
            user_request=user_request
        )
    
    def decide_adaptation(self, context: RequestContext) -> AdaptationDecision:
        """
        Make intelligent adaptation decisions based on context.
        
        Implements decision tree from base-template-v2.yaml adaptation rules.
        
        Args:
            context: Request context from detect_context()
            
        Returns:
            AdaptationDecision with format, challenge mode, code display, etc.
        """
        # Decision matrix: complexity × content_type → format
        format_matrix = {
            (RequestComplexity.SIMPLE, ContentType.INFORMATIONAL): ResponseFormat.CONCISE,
            (RequestComplexity.SIMPLE, ContentType.ACTIONABLE): ResponseFormat.CONCISE,
            (RequestComplexity.SIMPLE, ContentType.ANALYTICAL): ResponseFormat.VISUAL,
            (RequestComplexity.MODERATE, ContentType.INFORMATIONAL): ResponseFormat.SUMMARIZED,
            (RequestComplexity.MODERATE, ContentType.ACTIONABLE): ResponseFormat.SUMMARIZED,
            (RequestComplexity.MODERATE, ContentType.ANALYTICAL): ResponseFormat.VISUAL,
            (RequestComplexity.COMPLEX, ContentType.PLANNING): ResponseFormat.DETAILED,
            (RequestComplexity.COMPLEX, ContentType.ANALYTICAL): ResponseFormat.VISUAL,
        }
        
        # Get format from matrix or default to SUMMARIZED
        format_key = (context.complexity, context.content_type)
        response_format = format_matrix.get(format_key, ResponseFormat.SUMMARIZED)
        
        # Determine challenge mode
        if context.complexity == RequestComplexity.SIMPLE and context.content_type == ContentType.INFORMATIONAL:
            challenge_mode = ChallengeMode.SKIP
        elif context.has_validation_concerns or context.security_concerns:
            challenge_mode = ChallengeMode.CHALLENGE_ONLY
        elif not context.referenced_files_exist:
            challenge_mode = ChallengeMode.MIXED
        elif context.content_type == ContentType.PLANNING:
            challenge_mode = ChallengeMode.INTELLIGENT
        else:
            challenge_mode = ChallengeMode.ACCEPT_ONLY
        
        # Code display logic
        show_code = context.content_type == ContentType.ACTIONABLE and context.complexity != RequestComplexity.SIMPLE
        if not show_code:
            code_display_type = "none"
        elif context.complexity == RequestComplexity.COMPLEX:
            code_display_type = "pseudocode"
        elif "show code" in context.user_request.lower():
            code_display_type = "full"
        else:
            code_display_type = "snippet"
        
        # Collapsible sections for medium/high density
        use_collapsible = context.density in [InformationDensity.MEDIUM, InformationDensity.HIGH]
        
        # Token budget based on format
        token_budgets = {
            ResponseFormat.CONCISE: 400,
            ResponseFormat.SUMMARIZED: 600,
            ResponseFormat.DETAILED: 800,
            ResponseFormat.VISUAL: 500,
        }
        token_budget = token_budgets[response_format]
        
        return AdaptationDecision(
            format=response_format,
            challenge_mode=challenge_mode,
            show_code=show_code,
            code_display_type=code_display_type,
            use_collapsible=use_collapsible,
            token_budget=token_budget
        )
    
    def render_template(
        self,
        template_name: str,
        context: RequestContext,
        placeholders: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Render a template with intelligent adaptation.
        
        Args:
            template_name: Name of template from templates-v3-intelligent.yaml
            context: Request context for adaptation decisions
            placeholders: Optional dict of placeholder values
            
        Returns:
            Rendered markdown string
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        placeholders = placeholders or {}
        
        # Get adaptation decision
        decision = self.decide_adaptation(context)
        
        # Build response sections
        sections = []
        
        # Header
        sections.append(self._render_header(template, placeholders))
        
        # Understanding
        sections.append(self._render_understanding(template, placeholders))
        
        # Challenge (conditional)
        if decision.challenge_mode != ChallengeMode.SKIP:
            sections.append(self._render_challenge(template, decision.challenge_mode, placeholders))
        
        # Response (adaptive format)
        sections.append(self._render_response(template, decision, placeholders))
        
        # Request Echo (always show)
        sections.append(self._render_request_echo(template, placeholders))
        
        # Next Steps (format-specific)
        sections.append(self._render_next_steps(template, decision, placeholders))
        
        # Join sections and validate token budget
        rendered = "\n\n".join(filter(None, sections))
        
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        estimated_tokens = len(rendered) // 4
        if estimated_tokens > decision.token_budget:
            print(f"⚠️ Warning: Template '{template_name}' exceeds token budget: {estimated_tokens}/{decision.token_budget}")
        
        return rendered
    
    def _render_header(self, template: Dict, placeholders: Dict) -> str:
        """Render header section"""
        structure = template['structure']['header']
        header = structure['format']
        
        # Replace placeholders
        for key, value in placeholders.items():
            header = header.replace(f"{{{key}}}", value)
        
        if structure.get('include_author', True):
            header += "\n**Author:** Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX"
        
        return header
    
    def _render_understanding(self, template: Dict, placeholders: Dict) -> str:
        """Render understanding section"""
        structure = template['structure']['understanding']
        content = structure['content']
        
        # Replace placeholders
        for key, value in placeholders.items():
            content = content.replace(f"{{{key}}}", value)
        
        return f"{structure['format']}\n{content}"
    
    def _render_challenge(self, template: Dict, mode: ChallengeMode, placeholders: Dict) -> str:
        """Render challenge section based on mode"""
        structure = template['structure']['challenge']
        
        if not structure.get('display', True):
            return ""
        
        challenge_format = structure.get('format', '')
        content = structure.get('content', '')
        
        # Replace placeholders
        for key, value in placeholders.items():
            challenge_format = challenge_format.replace(f"{{{key}}}", value)
            content = content.replace(f"{{{key}}}", value)
        
        return f"{challenge_format}\n{content}"
    
    def _render_response(self, template: Dict, decision: AdaptationDecision, placeholders: Dict) -> str:
        """Render response section with adaptive format"""
        structure = template['structure']['response']
        content = structure['content']
        
        # Replace placeholders
        for key, value in placeholders.items():
            content = content.replace(f"{{{key}}}", value)
        
        return f"{structure['format']}\n{content}"
    
    def _render_request_echo(self, template: Dict, placeholders: Dict) -> str:
        """Render request echo section"""
        structure = template['structure']['request_echo']
        content = structure['content']
        
        # Replace placeholders
        for key, value in placeholders.items():
            content = content.replace(f"{{{key}}}", value)
        
        return f"{structure['format']}\n{content}"
    
    def _render_next_steps(self, template: Dict, decision: AdaptationDecision, placeholders: Dict) -> str:
        """Render next steps section"""
        structure = template['structure']['next_steps']
        content = structure['content']
        
        # Replace placeholders
        for key, value in placeholders.items():
            content = content.replace(f"{{{key}}}", value)
        
        return f"{structure['format']}\n{content}"


# Example usage
if __name__ == "__main__":
    # Initialize renderer
    renderer = TemplateRenderer("cortex-brain/response-templates/templates-v3-intelligent.yaml")
    
    # Example 1: Simple help request
    context1 = renderer.detect_context("help")
    decision1 = renderer.decide_adaptation(context1)
    print(f"Request: 'help'")
    print(f"Detected: {context1.complexity.value}, {context1.content_type.value}")
    print(f"Decision: {decision1.format.value}, {decision1.challenge_mode.value}")
    print(f"Token budget: {decision1.token_budget}\n")
    
    # Example 2: Complex planning request
    context2 = renderer.detect_context("plan authentication feature with JWT tokens and session management")
    decision2 = renderer.decide_adaptation(context2)
    print(f"Request: 'plan authentication feature...'")
    print(f"Detected: {context2.complexity.value}, {context2.content_type.value}")
    print(f"Decision: {decision2.format.value}, {decision2.challenge_mode.value}")
    print(f"Token budget: {decision2.token_budget}\n")
    
    # Example 3: Test results (analytical)
    context3 = renderer.detect_context("show me the test results")
    decision3 = renderer.decide_adaptation(context3)
    print(f"Request: 'show me the test results'")
    print(f"Detected: {context3.complexity.value}, {context3.content_type.value}")
    print(f"Decision: {decision3.format.value}, {decision3.challenge_mode.value}")
    print(f"Token budget: {decision3.token_budget}\n")
    
    # Render actual template
    rendered = renderer.render_template(
        "help_table",
        context1,
        placeholders={}
    )
    
    print("=" * 80)
    print("RENDERED TEMPLATE:")
    print("=" * 80)
    print(rendered)
