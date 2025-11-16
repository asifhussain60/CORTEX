"""Template data structures and loader for CORTEX response templates.

This module handles loading and managing YAML-based response templates.

Author: Asif Hussain
Version: 1.0
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


@dataclass
class Template:
    """Represents a single response template."""
    
    template_id: str
    triggers: List[str]
    response_type: str  # table | list | detailed | narrative | json
    context_needed: bool
    content: str
    verbosity: str = "concise"  # concise | detailed | expert
    metadata: Optional[Dict[str, Any]] = None


class TemplateLoader:
    """Loads and manages response templates from YAML file."""
    
    def __init__(self, template_file: Path):
        """Initialize template loader.
        
        Args:
            template_file: Path to response-templates.yaml
        """
        self.template_file = template_file
        self._templates: Dict[str, Template] = {}
        self._trigger_index: Dict[str, str] = {}  # trigger -> template_id
        self._loaded = False
    
    def load_templates(self) -> None:
        """Load all templates from YAML file."""
        if self._loaded:
            return
        
        if not self.template_file.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_file}")
        
        with open(self.template_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'templates' not in data:
            raise ValueError("Invalid template file: missing 'templates' section")
        
        templates_data = data['templates']
        
        for template_id, template_config in templates_data.items():
            template = Template(
                template_id=template_id,
                triggers=template_config.get('triggers', []),
                response_type=template_config.get('response_type', 'narrative'),
                context_needed=template_config.get('context_needed', False),
                content=template_config.get('content', ''),
                verbosity=template_config.get('verbosity', 'concise'),
                metadata=template_config.get('metadata', {})
            )
            
            self._templates[template_id] = template
            
            # Index triggers for fast lookup
            for trigger in template.triggers:
                self._trigger_index[trigger.lower()] = template_id
        
        self._loaded = True
    
    def load_template(self, template_id: str) -> Optional[Template]:
        """Load a specific template by ID.
        
        Args:
            template_id: The template identifier
            
        Returns:
            Template object if found, None otherwise
        """
        if not self._loaded:
            self.load_templates()
        
        return self._templates.get(template_id)
    
    def find_by_trigger(self, trigger: str) -> Optional[Template]:
        """Find template by trigger phrase.
        
        Args:
            trigger: The trigger phrase to search for
            
        Returns:
            Template object if found, None otherwise
        """
        if not self._loaded:
            self.load_templates()
        
        trigger_lower = trigger.lower().strip()
        template_id = self._trigger_index.get(trigger_lower)
        
        if template_id:
            return self._templates[template_id]
        
        # Fuzzy matching: check if trigger contains any registered trigger
        for registered_trigger, tmpl_id in self._trigger_index.items():
            if registered_trigger in trigger_lower or trigger_lower in registered_trigger:
                return self._templates[tmpl_id]
        
        return None
    
    def list_templates(self, category: Optional[str] = None) -> List[Template]:
        """List all templates, optionally filtered by category.
        
        Args:
            category: Optional category filter (e.g., 'agent', 'operation')
            
        Returns:
            List of Template objects
        """
        if not self._loaded:
            self.load_templates()
        
        templates = list(self._templates.values())
        
        if category:
            templates = [
                t for t in templates 
                if t.metadata and t.metadata.get('category') == category
            ]
        
        return templates
    
    def get_template_ids(self) -> List[str]:
        """Get all template IDs.
        
        Returns:
            List of template IDs
        """
        if not self._loaded:
            self.load_templates()
        
        return list(self._templates.keys())
    
    def get_triggers(self) -> List[str]:
        """Get all registered triggers.
        
        Returns:
            List of trigger phrases
        """
        if not self._loaded:
            self.load_templates()
        
        return list(self._trigger_index.keys())
