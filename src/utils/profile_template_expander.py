"""
Profile Template Expander (Task 3.4)
Expands templates with user profile data and role-based content filtering
"""
from typing import Optional, List, Dict, Any
import re
from src.setup.models.user_profile import UserProfile


class ProfileTemplateExpander:
    """
    Expands templates with user profile information.
    
    Features:
    - User name interpolation ({{user_name}})
    - Profile field interpolation ({{user_role}}, {{user_preference}}, etc.)
    - Role-based conditional blocks ({{#if role_beginner}}...{{/if}})
    - Preference-based conditional blocks ({{#if preference_concise}}...{{/if}})
    - Technical depth adjustment based on role
    - Batch template expansion
    - Preserves non-profile variables for later expansion
    
    Usage:
        profile = UserProfile(name="Alice", role="intermediate", ...)
        expander = ProfileTemplateExpander(profile)
        result = expander.expand("Hello {{user_name}}!")
    """
    
    def __init__(self, profile: Optional[UserProfile] = None):
        """
        Initialize template expander with user profile.
        
        Args:
            profile: User profile for template expansion (optional, uses defaults if None)
        """
        self.profile = profile
        self._context = self._build_context()
    
    def _build_context(self) -> Dict[str, Any]:
        """
        Build expansion context from profile.
        
        Returns:
            Dictionary with all expansion variables and flags
        """
        if not self.profile:
            # Default context when no profile
            return {
                'user_name': 'User',
                'user_role': 'intermediate',
                'user_preference': 'balanced',
                'user_work_area': 'general',
                'user_language': 'en',
                'role_beginner': False,
                'role_intermediate': True,
                'role_expert': False,
                'preference_concise': False,
                'preference_balanced': True,
                'preference_verbose': False,
                'show_technical_details': True,
            }
        
        # Extract profile fields
        context = {
            'user_name': self.profile.name or 'User',
            'user_role': self.profile.role,
            'user_preference': self.profile.preference,
            'user_work_area': self.profile.work_area or 'general',
            'user_language': self.profile.language,
        }
        
        # Role flags
        context['role_beginner'] = self.profile.role == 'beginner'
        context['role_intermediate'] = self.profile.role == 'intermediate'
        context['role_expert'] = self.profile.role == 'expert'
        
        # Preference flags
        context['preference_concise'] = self.profile.preference == 'concise'
        context['preference_balanced'] = self.profile.preference == 'balanced'
        context['preference_verbose'] = self.profile.preference == 'verbose'
        
        # Technical depth flag (intermediate and expert see technical details)
        context['show_technical_details'] = self.profile.role in ['intermediate', 'expert']
        
        return context
    
    def expand(self, template: str) -> str:
        """
        Expand template with profile data and conditional blocks.
        
        Args:
            template: Template string with variables and conditionals
        
        Returns:
            Expanded template string
        """
        if not template:
            return ""
        
        # First, process conditional blocks
        result = self._process_conditionals(template)
        
        # Then, interpolate variables
        result = self._interpolate_variables(result)
        
        return result
    
    def _process_conditionals(self, template: str) -> str:
        """
        Process {{#if condition}}...{{/if}} blocks.
        
        Args:
            template: Template with conditional blocks
        
        Returns:
            Template with conditionals evaluated
        """
        # Pattern for conditional blocks (non-greedy to handle nested blocks)
        pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'
        
        def replace_conditional(match):
            condition = match.group(1)
            content = match.group(2)
            
            # Check if condition is true in context
            if condition in self._context and self._context[condition]:
                return content
            return ""
        
        # Process all conditionals (may need multiple passes for nested blocks)
        max_iterations = 5  # Prevent infinite loops
        for _ in range(max_iterations):
            new_template = re.sub(pattern, replace_conditional, template, flags=re.DOTALL)
            if new_template == template:
                break
            template = new_template
        
        return template
    
    def _interpolate_variables(self, template: str) -> str:
        """
        Interpolate {{variable}} placeholders with profile data.
        
        Args:
            template: Template with variable placeholders
        
        Returns:
            Template with variables replaced
        """
        # Pattern for variables
        pattern = r'\{\{(\w+)\}\}'
        
        def replace_variable(match):
            var_name = match.group(1)
            
            # Only replace profile-related variables
            if var_name in self._context:
                value = self._context[var_name]
                # Convert boolean flags to empty string (already handled by conditionals)
                if isinstance(value, bool):
                    return ""
                return str(value)
            
            # Preserve non-profile variables for later expansion
            return match.group(0)
        
        return re.sub(pattern, replace_variable, template)
    
    def get_expansion_context(self) -> Dict[str, Any]:
        """
        Get the expansion context (all variables and flags).
        
        Returns:
            Dictionary with expansion context
        """
        return dict(self._context)
    
    def batch_expand(self, templates: List[str]) -> List[str]:
        """
        Expand multiple templates at once.
        
        Args:
            templates: List of template strings
        
        Returns:
            List of expanded templates
        """
        return [self.expand(template) for template in templates]
