"""
CORTEX Templates - Content Generator

Template content generation and transformation utilities.

"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import json

from cortex.templates.content_strategy import ContentPopulationStrategy
from cortex.templates.template_manager import TemplateManager


@dataclass
class ImportResult:
    """Template import result."""
    success: bool
    imported_count: int = 0
    errors: List[str] = field(default_factory=list)


class ContentGenerator:
    """Content generator for templates.
    
    Generates template skeletons, sections, and bundles.
    """
    
    def __init__(self) -> None:
        """Initialize content generator."""
        self._strategy = ContentPopulationStrategy()
        self._manager = TemplateManager()
    
    def generate_skeleton(
        self,
        template_id: str,
        domain: str,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate template skeleton.
        
        Args:
            template_id: Template ID.
            domain: Domain name.
            category: Optional category.
            
        Returns:
            Template skeleton dictionary.
        """
        return {
            'metadata': {
                'template_id': template_id,
                'version': '1.0',
                'domain': domain,
                'category': category,
            },
            'template': {
                'structure': [],
            },
            'content': {},
        }
    
    def generate_from_pattern(
        self,
        pattern: str,
        new_id: str,
        domain: str,
    ) -> Dict[str, Any]:
        """Generate template from existing pattern.
        
        Args:
            pattern: Pattern template ID.
            new_id: New template ID.
            domain: Domain name.
            
        Returns:
            Generated template dictionary.
        """
        # Get pattern template
        pattern_template = self._strategy.get_template_by_id(pattern)
        if not pattern_template:
            # Create basic skeleton
            return self.generate_skeleton(new_id, domain)
        
        # Copy and modify
        new_template = {
            'metadata': {
                'template_id': new_id,
                'version': '1.0',
                'domain': domain,
                'category': pattern_template.get('category'),
            },
            'template': {
                'structure': [],
            },
        }
        
        return new_template
    
    def generate_section(
        self,
        section_type: str,
        title: str,
        variables: Optional[List[str]] = None,
    ) -> str:
        """Generate section content.
        
        Args:
            section_type: Section type (header, body, footer).
            title: Section title.
            variables: Optional variable names.
            
        Returns:
            Generated section content.
        """
        if section_type == 'header':
            content = f"# {title}\n\n"
        elif section_type == 'body':
            content = f"## {title}\n\n"
        else:  # footer
            content = f"\n---\n{title}\n"
        
        # Add variable placeholders
        if variables:
            for var in variables:
                content += f"{{{var}}}\n"
        
        return content
    
    def generate_variable_docs(
        self,
        variables: Dict[str, str],
    ) -> str:
        """Generate variable documentation.
        
        Args:
            variables: Dictionary of variable names to types.
            
        Returns:
            Generated documentation string.
        """
        docs = "## Template Variables\n\n"
        docs += "| Variable | Type | Description |\n"
        docs += "|----------|------|-------------|\n"
        
        for var_name, var_type in variables.items():
            docs += f"| {{{var_name}}} | {var_type} | ... |\n"
        
        return docs
    
    def generate_batch(
        self,
        specs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generate batch of templates.
        
        Args:
            specs: List of template specifications.
            
        Returns:
            List of generated templates.
        """
        templates = []
        for spec in specs:
            template = self.generate_skeleton(
                template_id=spec['id'],
                domain=spec['domain'],
                category=spec.get('category'),
            )
            templates.append(template)
        
        return templates
    
    def merge(
        self,
        base: Dict[str, Any],
        overlay: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge template content.
        
        Args:
            base: Base template dictionary.
            overlay: Overlay template dictionary.
            
        Returns:
            Merged template dictionary.
        """
        merged = base.copy()
        
        # Merge content
        if 'content' in overlay:
            merged['content'] = overlay['content']
        
        # Preserve base metadata
        if 'metadata' in merged and 'metadata' in overlay:
            for key, value in overlay['metadata'].items():
                if key != 'version':  # Preserve base version
                    merged['metadata'][key] = value
        
        return merged
    
    def transform(
        self,
        content: str,
        target_format: str,
    ) -> str:
        """Transform template format.
        
        Args:
            content: Template content.
            target_format: Target format (json, yaml).
            
        Returns:
            Transformed content string.
        """
        # Parse YAML content
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError:
            # Assume it's already in target format
            return content
        
        # Transform to target format
        if target_format == 'json':
            return json.dumps(data, indent=2)
        elif target_format == 'yaml':
            return yaml.dump(data, default_flow_style=False)
        else:
            return content
    
    def export_bundle(
        self,
        domain: str,
    ) -> Dict[str, Any]:
        """Export template bundle for a domain.
        
        Args:
            domain: Domain name.
            
        Returns:
            Bundle dictionary.
        """
        templates = self._strategy.get_domain_templates(domain)
        
        return {
            'manifest': {
                'version': '1.0',
                'domain': domain,
                'template_count': len(templates),
            },
            'templates': templates,
        }
    
    def import_bundle(
        self,
        bundle_path: str,
    ) -> ImportResult:
        """Import template bundle from file.
        
        Args:
            bundle_path: Path to bundle file.
            
        Returns:
            Import result.
        """
        try:
            with open(bundle_path, 'r') as f:
                bundle = yaml.safe_load(f)
            
            if 'templates' not in bundle:
                return ImportResult(
                    success=False,
                    errors=["Bundle missing 'templates' key"],
                )
            
            templates = bundle['templates']
            return ImportResult(
                success=True,
                imported_count=len(templates),
            )
        
        except Exception as e:
            return ImportResult(
                success=False,
                errors=[str(e)],
            )
