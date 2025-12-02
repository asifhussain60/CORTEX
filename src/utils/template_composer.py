"""
Template Composer Engine
Version: 3.3.0
Purpose: Compose responses from modular YAML components with profile awareness
Part of: Response Template System Refactor (Phase 5)
"""

import yaml
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import hashlib


@dataclass
class UserProfile:
    """User profile for template composition"""
    interaction_mode: str = "guided"  # autonomous, guided, educational, pair
    experience_level: str = "mid"  # junior, mid, senior, expert
    response_detail: str = "balanced"  # concise, balanced, verbose
    tech_stack: Optional[Dict[str, Any]] = None
    conversation_count: int = 0


@dataclass
class ComposedResponse:
    """Result of template composition"""
    content: str
    template_id: str
    format_id: str
    detail_level: str
    composition_time_ms: float
    cached: bool = False


class TemplateComposer:
    """
    Composes responses from modular YAML components with profile-aware variants.
    
    Features:
    - Loads components by ID
    - Applies profile-based variants (interaction mode, experience, detail level)
    - Caches composed templates (24-hour TTL)
    - Performance target: <50ms composition time
    """
    
    def __init__(self, brain_path: str = None):
        """
        Initialize TemplateComposer with paths to YAML files.
        
        Args:
            brain_path: Path to cortex-brain directory (defaults to ../../../cortex-brain)
        """
        if brain_path is None:
            # Default to cortex-brain relative to this file
            current_dir = Path(__file__).parent
            brain_path = current_dir.parent.parent / "cortex-brain"
        
        self.brain_path = Path(brain_path)
        
        # Paths to modular YAML files
        self.components_path = self.brain_path / "response-base-components.yaml"
        self.definitions_path = self.brain_path / "response-template-definitions.yaml"
        self.variants_path = self.brain_path / "response-profile-variants.yaml"
        self.routing_path = self.brain_path / "response-routing-rules.yaml"
        
        # Lazy-loaded YAML data
        self._components: Optional[Dict] = None
        self._definitions: Optional[Dict] = None
        self._variants: Optional[Dict] = None
        self._routing: Optional[Dict] = None
        
        # Composition cache (24-hour TTL)
        self._cache: Dict[str, tuple[ComposedResponse, float]] = {}
        self._cache_ttl: int = 86400  # 24 hours in seconds
    
    def _load_yaml(self, file_path: Path) -> Dict:
        """Load and parse YAML file"""
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @property
    def components(self) -> Dict:
        """Lazy-load base components"""
        if self._components is None:
            self._components = self._load_yaml(self.components_path)
        return self._components
    
    @property
    def definitions(self) -> Dict:
        """Lazy-load template definitions"""
        if self._definitions is None:
            self._definitions = self._load_yaml(self.definitions_path)
        return self._definitions
    
    @property
    def variants(self) -> Dict:
        """Lazy-load profile variants"""
        if self._variants is None:
            self._variants = self._load_yaml(self.variants_path)
        return self._variants
    
    @property
    def routing(self) -> Dict:
        """Lazy-load routing rules"""
        if self._routing is None:
            self._routing = self._load_yaml(self.routing_path)
        return self._routing
    
    def _generate_cache_key(self, template_id: str, profile: UserProfile) -> str:
        """Generate cache key from template ID and profile"""
        key_data = f"{template_id}:{profile.interaction_mode}:{profile.experience_level}:{profile.response_detail}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[ComposedResponse]:
        """Retrieve composed response from cache if not expired"""
        if cache_key in self._cache:
            response, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                response.cached = True
                return response
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, response: ComposedResponse):
        """Save composed response to cache"""
        self._cache[cache_key] = (response, time.time())
    
    def clear_cache(self):
        """Clear all cached composed templates"""
        self._cache.clear()
    
    def compose_response(
        self,
        template_id: str,
        profile: UserProfile,
        content_vars: Optional[Dict[str, str]] = None,
        force_recompose: bool = False
    ) -> ComposedResponse:
        """
        Compose a response from template ID with profile-aware variants.
        
        Args:
            template_id: Template ID from response-template-definitions.yaml
            profile: User profile (interaction mode, experience, detail level)
            content_vars: Variables to substitute in template (e.g., {{operation}})
            force_recompose: Skip cache and recompose from scratch
        
        Returns:
            ComposedResponse with composed content and metadata
        
        Raises:
            ValueError: If template_id not found
        """
        start_time = time.time()
        
        # Check cache first (unless force_recompose)
        if not force_recompose:
            cache_key = self._generate_cache_key(template_id, profile)
            cached_response = self._get_from_cache(cache_key)
            if cached_response is not None:
                # Apply content variables to cached template
                if content_vars:
                    cached_response.content = self._substitute_variables(
                        cached_response.content, content_vars
                    )
                return cached_response
        
        # Load template definition
        template = self._get_template_definition(template_id)
        if template is None:
            raise ValueError(f"Template not found: {template_id}")
        
        # Determine format based on profile and template
        format_id = self._select_format(template, profile)
        
        # Determine detail level (response_detail overrides if not balanced)
        detail_level = self._resolve_detail_level(profile)
        
        # Build section list based on format and profile
        sections = self._build_section_list(template, format_id, profile)
        
        # Compose final response
        composed_content = self._compose_sections(sections, detail_level, content_vars or {})
        
        # Calculate composition time
        composition_time_ms = (time.time() - start_time) * 1000
        
        # Create response object
        response = ComposedResponse(
            content=composed_content,
            template_id=template_id,
            format_id=format_id,
            detail_level=detail_level,
            composition_time_ms=composition_time_ms,
            cached=False
        )
        
        # Save to cache
        if not force_recompose:
            self._save_to_cache(cache_key, response)
        
        return response
    
    def _get_template_definition(self, template_id: str) -> Optional[Dict]:
        """Get template definition by ID"""
        templates = self.definitions.get('templates', {})
        for name, template in templates.items():
            if template.get('id') == template_id:
                return template
        return None
    
    def _select_format(self, template: Dict, profile: UserProfile) -> str:
        """
        Select format based on template, profile, and response detail.
        
        Priority:
        1. response_detail == 'concise' -> compact format
        2. response_detail == 'verbose' + educational mode -> educational format
        3. Template has tech_aware format and user has tech_stack -> tech_aware
        4. Template's default format
        5. standard_5_part (fallback)
        """
        # Rule 1: Concise detail -> compact format
        if profile.response_detail == 'concise':
            return 'format_compact'
        
        # Rule 2: Verbose detail + educational mode -> educational format
        if profile.response_detail == 'verbose' and profile.interaction_mode == 'educational':
            return 'format_educational'
        
        # Rule 3: Tech-aware template + tech stack -> tech_aware format
        if template.get('format') == 'tech_aware' and profile.tech_stack:
            return 'format_tech_aware'
        
        # Rule 4: Template's default format
        template_format = template.get('format', 'standard_5_part')
        return f"format_{template_format}"
        
        # Rule 5: Fallback to standard
        # (unreachable due to Rule 4, but kept for safety)
        # return 'format_standard_5_part'
    
    def _resolve_detail_level(self, profile: UserProfile) -> str:
        """
        Resolve detail level from profile.
        
        Priority:
        1. response_detail if not 'balanced'
        2. interaction_mode defaults (autonomous=concise, educational=verbose, etc.)
        3. balanced (fallback)
        """
        # If user explicitly chose concise or verbose, use it
        if profile.response_detail in ['concise', 'verbose']:
            return profile.response_detail
        
        # Balanced respects interaction_mode defaults
        if profile.response_detail == 'balanced':
            mode_defaults = {
                'autonomous': 'concise',
                'guided': 'balanced',
                'educational': 'verbose',
                'pair': 'balanced'
            }
            return mode_defaults.get(profile.interaction_mode, 'balanced')
        
        return 'balanced'
    
    def _build_section_list(
        self,
        template: Dict,
        format_id: str,
        profile: UserProfile
    ) -> List[str]:
        """
        Build list of section IDs based on template, format, and profile.
        
        Returns:
            List of section IDs to include in response
        """
        # Get format definition
        formats = self.components.get('format_variants', {})
        format_def = formats.get(format_id.replace('format_', ''), {})
        
        # Start with format's section list
        sections = format_def.get('sections', [])
        
        # Add template's required sections (if not already present)
        required_sections = template.get('required_sections', [])
        for section_id in required_sections:
            if section_id not in sections:
                sections.append(section_id)
        
        # Add profile-specific sections (e.g., learning objectives in educational mode)
        mode_variants = self.variants.get('interaction_modes', {})
        mode_def = mode_variants.get(profile.interaction_mode, {})
        additional_sections = mode_def.get('additional_sections', [])
        for section_id in additional_sections:
            if section_id not in sections:
                sections.append(section_id)
        
        return sections
    
    def _compose_sections(
        self,
        section_ids: List[str],
        detail_level: str,
        content_vars: Dict[str, str]
    ) -> str:
        """
        Compose final response by assembling sections.
        
        Args:
            section_ids: List of section IDs to include
            detail_level: Detail level (concise, balanced, verbose)
            content_vars: Variables to substitute (e.g., {{operation}})
        
        Returns:
            Composed response string
        """
        components = self.components.get('shared_components', {})
        sections_text = []
        
        for section_id in section_ids:
            # Find component by ID
            component = None
            for comp_name, comp_def in components.items():
                if comp_def.get('id') == section_id:
                    component = comp_def
                    break
            
            if component is None:
                continue  # Skip missing components
            
            # Get appropriate variant based on detail level
            content = self._get_component_content(component, detail_level)
            
            # Format section with icon and title (if not header)
            if component.get('type') == 'section':
                icon = component.get('icon', '')
                title = component.get('title', '')
                section_text = f"### {icon} {title}\n{content}"
            else:
                section_text = content
            
            sections_text.append(section_text)
        
        # Join sections with separator
        separator = self.components.get('rendering_rules', {}).get('section_separator', '\n\n')
        composed = separator.join(sections_text)
        
        # Substitute variables
        composed = self._substitute_variables(composed, content_vars)
        
        return composed
    
    def _get_component_content(self, component: Dict, detail_level: str) -> str:
        """Get component content for specified detail level"""
        # Check if component has variants
        variants = component.get('variants', {})
        if detail_level in variants:
            return variants[detail_level]
        
        # Fallback to default content
        return component.get('content', '')
    
    def _substitute_variables(self, text: str, variables: Dict[str, str]) -> str:
        """Substitute {{variable}} placeholders with values"""
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            text = text.replace(placeholder, var_value)
        return text
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        valid_entries = sum(
            1 for _, (_, timestamp) in self._cache.items()
            if current_time - timestamp < self._cache_ttl
        )
        
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self._cache) - valid_entries,
            'cache_ttl_hours': self._cache_ttl / 3600
        }
