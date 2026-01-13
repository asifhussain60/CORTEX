"""Layered Template Renderer for 3-layer response template architecture.

This module implements the renderer for ENH-TEMPLATE-001, which splits
response templates into 3 layers:
- Layer 1: Mandatory headers (CORE-026 enforcement)
- Layer 2: Executive summary format
- Layer 3: Orchestrator-specific templates

Author: Asif Hussain
Phase: 9.7
Version: 5.0
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional


class LayeredTemplateRenderer:
    """Renders templates using 3-layer architecture.
    
    Architecture:
    - Layer 1: Mandatory header (loaded at init, cached as singleton)
    - Layer 2: Executive summary (loaded at init, cached as singleton)
    - Layer 3: Orchestrator templates (lazy loaded, cached per orchestrator)
    
    Usage:
        renderer = LayeredTemplateRenderer()
        result = renderer.render('CORTEX-PLAN', 'plan_generated', context)
    """
    
    # Singleton caches for Layer 1 and Layer 2 (shared across instances)
    _LAYER1_CACHE: Optional[Dict[str, Any]] = None
    _LAYER2_CACHE: Optional[Dict[str, Any]] = None
    
    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize layered template renderer.
        
        Args:
            template_dir: Path to response-templates directory
                         (default: cortex-brain/response-templates)
        """
        self.template_dir = template_dir or Path("cortex-brain/response-templates")
        
        # Load Layer 1 and Layer 2 (singleton cached)
        self.layer1 = self._load_layer1()
        self.layer2 = self._load_layer2()
        
        # Layer 3 cache (loaded on-demand per orchestrator)
        self.layer3_cache: Dict[str, Dict[str, Any]] = {}
    
    def _load_layer1(self) -> Dict[str, Any]:
        """Load Layer 1 (mandatory header) with singleton caching.
        
        Returns:
            Layer 1 configuration dict
        """
        # Check singleton cache first
        if LayeredTemplateRenderer._LAYER1_CACHE is not None:
            return LayeredTemplateRenderer._LAYER1_CACHE
        
        # Load from file
        layer1_path = self.template_dir / "mandatory-header.yaml"
        if not layer1_path.exists():
            raise FileNotFoundError(
                f"Layer 1 (mandatory header) not found: {layer1_path}"
            )
        
        with open(layer1_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Validate Layer 1
        if data.get('layer') != 1:
            raise ValueError("mandatory-header.yaml must have layer: 1")
        
        if 'header_template' not in data:
            raise ValueError("Layer 1 must have header_template")
        
        # Cache as singleton
        LayeredTemplateRenderer._LAYER1_CACHE = data
        return data
    
    def _load_layer2(self) -> Dict[str, Any]:
        """Load Layer 2 (executive summary) with singleton caching.
        
        Returns:
            Layer 2 configuration dict
        """
        # Check singleton cache first
        if LayeredTemplateRenderer._LAYER2_CACHE is not None:
            return LayeredTemplateRenderer._LAYER2_CACHE
        
        # Load from file
        layer2_path = self.template_dir / "executive-summary.yaml"
        if not layer2_path.exists():
            raise FileNotFoundError(
                f"Layer 2 (executive summary) not found: {layer2_path}"
            )
        
        with open(layer2_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Validate Layer 2
        if data.get('layer') != 2:
            raise ValueError("executive-summary.yaml must have layer: 2")
        
        if 'sections' not in data:
            raise ValueError("Layer 2 must have sections")
        
        # Cache as singleton
        LayeredTemplateRenderer._LAYER2_CACHE = data
        return data
    
    def _load_orchestrator_templates(self, orchestrator: str) -> Dict[str, Any]:
        """Load Layer 3 templates for specific orchestrator (lazy loading).
        
        Args:
            orchestrator: Orchestrator name (e.g., 'CORTEX-PLAN', 'TDD-MASTER')
        
        Returns:
            Layer 3 templates dict
        """
        # Check cache first
        if orchestrator in self.layer3_cache:
            return self.layer3_cache[orchestrator]
        
        # Try to load orchestrator-specific file
        orchestrator_path = self.template_dir / "orchestrators" / f"{orchestrator}.yaml"
        
        # Fall back to generic.yaml if not found
        if not orchestrator_path.exists():
            orchestrator_path = self.template_dir / "orchestrators" / "generic.yaml"
        
        if not orchestrator_path.exists():
            raise FileNotFoundError(
                f"Layer 3 templates not found for {orchestrator}, "
                f"and generic.yaml fallback missing"
            )
        
        with open(orchestrator_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Validate Layer 3
        if data.get('layer') != 3:
            raise ValueError(f"{orchestrator_path} must have layer: 3")
        
        if 'templates' not in data:
            raise ValueError(f"{orchestrator_path} must have templates")
        
        # Cache for this orchestrator
        self.layer3_cache[orchestrator] = data
        return data
    
    def _validate_inheritance(self, orchestrator: str) -> bool:
        """Validate Layer 3 declares inheritance from Layer 1 and 2.
        
        Args:
            orchestrator: Orchestrator name
        
        Returns:
            True if inheritance valid
        
        Raises:
            ValueError: If inheritance declaration missing or invalid
        """
        templates = self._load_orchestrator_templates(orchestrator)
        
        if 'inherits' not in templates:
            raise ValueError(
                f"Layer 3 for {orchestrator} must declare 'inherits'"
            )
        
        inherits = templates['inherits']
        
        if 'mandatory-header.yaml' not in inherits:
            raise ValueError(
                f"Layer 3 for {orchestrator} must inherit mandatory-header.yaml"
            )
        
        if 'executive-summary.yaml' not in inherits:
            raise ValueError(
                f"Layer 3 for {orchestrator} must inherit executive-summary.yaml"
            )
        
        return True
    
    def _render_header(self, context: Dict[str, Any]) -> str:
        """Render Layer 1 (mandatory header).
        
        Args:
            context: Context dict with operation_type, phase, orchestrator
        
        Returns:
            Rendered header string
        """
        template = self.layer1['header_template']
        
        # Substitute placeholders
        result = template.format(
            operation_type=context.get('operation_type', 'Operation'),
            phase=context.get('phase', 'Phase Unknown'),
            orchestrator=context.get('orchestrator', 'Unknown')
        )
        
        return result.strip()
    
    def _render_template_content(
        self, 
        orchestrator: str, 
        template_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Render Layer 3 (orchestrator template content).
        
        Args:
            orchestrator: Orchestrator name
            template_id: Template ID (e.g., 'generic_success')
            context: Context dict for placeholder substitution
        
        Returns:
            Rendered template content
        """
        templates = self._load_orchestrator_templates(orchestrator)
        
        if template_id not in templates['templates']:
            raise KeyError(
                f"Template '{template_id}' not found for orchestrator '{orchestrator}'"
            )
        
        template = templates['templates'][template_id]
        content = template['content']
        
        # Substitute placeholders using regex (handles missing keys gracefully)
        def replace_placeholder(match):
            key = match.group(1)
            return str(context.get(key, f'{{{key}}}'))
        
        result = re.sub(r'\{(\w+)\}', replace_placeholder, content)
        
        return result.strip()
    
    def render(
        self,
        orchestrator: str,
        template_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Render complete response from 3 layers.
        
        Composition:
        1. Layer 1: Mandatory header (always first)
        2. Layer 3: Template content
        3. Layer 2: Executive format validation (future enhancement)
        
        Args:
            orchestrator: Orchestrator name
            template_id: Template ID to render
            context: Context dict for placeholder substitution
        
        Returns:
            Fully rendered response string
        
        Example:
            renderer = LayeredTemplateRenderer()
            result = renderer.render(
                'generic',
                'generic_success',
                {
                    'operation_type': 'Test Execution',
                    'phase': 'Phase 9.7',
                    'orchestrator': 'TDD-MASTER',
                    'operation': 'Unit tests',
                    'details': 'passed'
                }
            )
        """
        # Validate inheritance (raises if invalid)
        self._validate_inheritance(orchestrator)
        
        # Render Layer 1 (header)
        header = self._render_header(context)
        
        # Render Layer 3 (template content)
        content = self._render_template_content(orchestrator, template_id, context)
        
        # Compose: header + blank line + content
        result = f"{header}\n\n{content}"
        
        return result
    
    @classmethod
    def clear_singleton_cache(cls):
        """Clear singleton cache for Layer 1/2 (useful for testing)."""
        cls._LAYER1_CACHE = None
        cls._LAYER2_CACHE = None
