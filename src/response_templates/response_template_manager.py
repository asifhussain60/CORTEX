"""Response Template Manager for CORTEX

Backward-compatible API wrapper for the new modular template system.
Provides simple, legacy-compatible interface while leveraging Phase 5.1-5.4 enhancements.

Author: Asif Hussain
Phase: 5.5 - Backward Compatibility Integration
Version: 1.0
Created: December 2, 2025
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from .template_renderer import TemplateRenderer
from .template_loader import Template


class ResponseTemplateManager:
    """Backward-compatible manager for response templates.
    
    Provides simple API for existing CORTEX codebase while using
    new modular YAML system (base-components, templates, profiles, routing).
    
    Key Features:
    - Simple render_template(id, mode, context) API
    - Trigger-based routing with fuzzy matching
    - Automatic mode selection from user profile
    - Template listing and retrieval
    - Performance caching (5-min TTL)
    
    Usage:
        manager = ResponseTemplateManager()
        result = manager.render_template('help', mode='guided')
    """
    
    def __init__(
        self,
        template_dir: Optional[Path] = None,
        profile_manager: Optional[Any] = None
    ):
        """Initialize response template manager.
        
        Args:
            template_dir: Path to modular template directory (default: cortex-brain/response-templates)
            profile_manager: Optional UserProfileManager for dynamic mode selection
        """
        self.template_dir = template_dir or Path("cortex-brain/response-templates")
        self.profile_manager = profile_manager
        
        # Initialize renderer with modular YAML support
        self.renderer = TemplateRenderer(
            template_dir=self.template_dir,
            profile_manager=profile_manager
        )
    
    def render_template(
        self,
        template_id: str,
        mode: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render template by ID with specified mode and context.
        
        Args:
            template_id: Template identifier (e.g., 'help', 'general', 'planning')
            mode: Interaction mode (autonomous/guided/educational/pair) - defaults to profile or 'guided'
            context: Dictionary of placeholder values for substitution
            
        Returns:
            Rendered template string with placeholders substituted
            
        Example:
            manager.render_template(
                template_id='general',
                mode='guided',
                context={'operation': 'refactoring', 'status': 'in-progress'}
            )
        """
        # Resolve mode (explicit > profile > default)
        resolved_mode = self._resolve_mode(mode)
        
        # Get template definition from modular YAML
        template_def = self.renderer.templates.get(template_id)
        
        if not template_def:
            # Fallback to 'fallback' template for missing templates
            template_id = 'fallback'
            template_def = self.renderer.templates.get('fallback')
            
            if not template_def:
                # Ultimate fallback
                return self._get_emergency_fallback()
        
        # Render using TemplateRenderer (Phase 5.2 composition engine)
        try:
            rendered = self.renderer.compose_template(
                template_id=template_id,
                mode=resolved_mode,
                context=context
            )
            return rendered
        except Exception as e:
            # Graceful degradation
            return self._get_error_fallback(str(e))
    
    def render_by_trigger(
        self,
        trigger: str,
        mode: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render template by trigger phrase with fuzzy matching.
        
        Args:
            trigger: Trigger phrase (e.g., 'help', 'plan feature', 'error')
            mode: Interaction mode (defaults to profile or 'guided')
            context: Dictionary of placeholder values
            
        Returns:
            Rendered template string
            
        Example:
            manager.render_by_trigger('help', mode='autonomous')
        """
        # Route trigger to template ID
        template_id = self.route_trigger(trigger)
        
        # Render using resolved ID
        return self.render_template(
            template_id=template_id,
            mode=mode,
            context=context
        )
    
    def route_trigger(self, trigger: str) -> str:
        """Route trigger phrase to template ID using routing rules.
        
        Uses exact matching (case-insensitive) and fuzzy matching (80%+ similarity).
        Falls back to 'fallback' template if no match found.
        
        Args:
            trigger: Trigger phrase to route
            
        Returns:
            Template ID
            
        Example:
            template_id = manager.route_trigger('halp')  # Fuzzy matches to 'help'
        """
        return self.renderer.select_template_by_trigger(trigger)
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template definition by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template definition dictionary or None if not found
            
        Example:
            template = manager.get_template('help')
            if template:
                print(f"Template: {template['id']}")
        """
        return self.renderer.templates.get(template_id)
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available templates, optionally filtered by category.
        
        Args:
            category: Optional category filter (e.g., 'planning', 'error', 'help')
            
        Returns:
            List of template dictionaries with id, description, category
            
        Example:
            all_templates = manager.list_templates()
            planning_templates = manager.list_templates(category='planning')
        """
        templates = []
        
        for template_id, template_def in self.renderer.templates.items():
            # Skip internal templates
            if template_id.startswith('_'):
                continue
            
            # Extract metadata
            metadata = template_def.get('metadata', {})
            template_category = metadata.get('category', 'general')
            
            # Apply category filter
            if category and template_category != category:
                continue
            
            templates.append({
                'id': template_id,
                'description': metadata.get('description', ''),
                'category': template_category,
                'requires_profile': metadata.get('requires_profile', False)
            })
        
        return templates
    
    def _resolve_mode(self, mode: Optional[str]) -> str:
        """Resolve interaction mode from explicit arg, profile, or default.
        
        Priority:
        1. Explicit mode parameter
        2. User profile mode (if profile_manager available)
        3. Default: 'guided'
        
        Args:
            mode: Explicit mode (may be None)
            
        Returns:
            Normalized mode (autonomous/guided/educational/pair)
        """
        # 1. Explicit mode
        if mode:
            return self.renderer._normalize_mode(mode)
        
        # 2. Profile mode
        if self.profile_manager:
            try:
                profile_mode = self.profile_manager.get_user_mode()
                if profile_mode:
                    return self.renderer._normalize_mode(profile_mode)
            except Exception:
                # Profile manager error - fall through to default
                pass
        
        # 3. Default
        return 'guided'
    
    def _get_emergency_fallback(self) -> str:
        """Get emergency fallback when all template loading fails.
        
        Returns:
            Minimal hardcoded response
        """
        return """# 🧠 CORTEX Response
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 My Understanding Of Your Request
I understand you have a request, but I'm unable to load the appropriate response template.

## ⚠️ Challenge
Template system is experiencing issues.

## 💬 Response
I apologize, but I'm having trouble accessing my response templates. This is an internal system issue. Please check:

1. Template directory exists: cortex-brain/response-templates/
2. Required YAML files present: base-components.yaml, templates.yaml, profiles.yaml, routing.yaml
3. File permissions allow reading

## 📝 Your Request
[Unable to echo - template system unavailable]

## 🔍 Next Steps
1. Verify template directory structure
2. Check file permissions
3. Review logs for specific errors
"""
    
    def _get_error_fallback(self, error_message: str) -> str:
        """Get error fallback when rendering fails.
        
        Args:
            error_message: Error message to include
            
        Returns:
            Error response with details
        """
        return f"""# 🧠 CORTEX Response Error
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 My Understanding Of Your Request
I encountered an error while rendering your response.

## ⚠️ Challenge
Template rendering failed with error: {error_message}

## 💬 Response
I apologize for the error. The template system encountered an issue during rendering. This could be due to:

1. Invalid placeholder syntax in template
2. Missing required context values
3. Template composition error
4. File system access issues

## 📝 Your Request
[Rendering failed before request could be echoed]

## 🔍 Next Steps
1. Review error message above
2. Check template syntax
3. Verify context values provided
4. Consult CORTEX logs for details
"""
