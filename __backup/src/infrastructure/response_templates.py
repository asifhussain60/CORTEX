"""
Response Template Infrastructure - Layer 1, 2, 3 Rendering

Part of AC-TEMPLATE-001 to 004 implementation (already complete).
Extended here to support AC-TEMPLATE-005 header enforcement.
"""

from datetime import datetime
from typing import Optional, Dict, Any


class LayeredTemplateRenderer:
    """
    Renders responses using 3-layer template architecture:
    - Layer 1: Mandatory headers (copyright, version, timestamp, author)
    - Layer 2: Executive summary format (Outcomes/In Progress/Risks/Impact)
    - Layer 3: Orchestrator-specific templates
    
    Already implemented in Phase 9. This module extends it for header enforcement.
    """
    
    def __init__(self):
        """Initialize the renderer"""
        self._layer1_template = self._load_layer1()
        self._layer2_cache = {}
        self._layer3_cache = {}
    
    def _load_layer1(self) -> Dict[str, str]:
        """Load Layer 1 mandatory headers"""
        return {
            'copyright': 'Copyright © {year} {author}. All rights reserved.',
            'version': 'CORTEX {version} | Release {release_date}',
            'timestamp': 'Timestamp: {iso_timestamp}',
            'author': 'Author: {author}'
        }
    
    def get_layer1_template(self) -> Dict[str, str]:
        """Get Layer 1 template"""
        return self._layer1_template
    
    def render_response(
        self,
        content: str,
        orchestrator: str = 'generic',
        author: str = 'Copilot',
        copyright_year: Optional[int] = None,
        version: str = '6.0.0',
        **kwargs
    ) -> str:
        """
        Render complete response with all 3 layers.
        
        Args:
            content: Main response content
            orchestrator: Orchestrator name (for Layer 3 template selection)
            author: Author/executor name
            copyright_year: Copyright year (defaults to current year)
            version: CORTEX version
            **kwargs: Additional template variables
            
        Returns:
            Fully rendered response with headers
        """
        if copyright_year is None:
            copyright_year = datetime.utcnow().year
        
        iso_timestamp = datetime.utcnow().isoformat() + "+00:00"
        release_date = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Build Layer 1 (Mandatory Headers)
        layer1 = self._render_layer1(
            copyright_year=copyright_year,
            author=author,
            version=version,
            iso_timestamp=iso_timestamp,
            release_date=release_date
        )
        
        # Build Layer 2 (Executive Summary)
        layer2 = self._render_layer2(kwargs)
        
        # Build Layer 3 (Orchestrator-specific)
        layer3_template = self._get_layer3_template(orchestrator)
        
        # Combine all layers
        response = f"""{layer1}

{layer3_template if layer3_template else ''}

{content}

---

**Version:** CORTEX {version} | **Date:** {iso_timestamp}
**Author:** {author}
**Copyright © {copyright_year} {author}. All rights reserved.**"""
        
        return response
    
    def _render_layer1(
        self,
        copyright_year: int,
        author: str,
        version: str,
        iso_timestamp: str,
        release_date: str
    ) -> str:
        """Render Layer 1 mandatory headers"""
        layer1 = []
        
        # Copyright
        layer1.append(
            self._layer1_template['copyright'].format(year=copyright_year, author=author)
        )
        
        # Version
        layer1.append(
            self._layer1_template['version'].format(version=version, release_date=release_date)
        )
        
        # Timestamp
        layer1.append(
            self._layer1_template['timestamp'].format(iso_timestamp=iso_timestamp)
        )
        
        # Author
        layer1.append(
            self._layer1_template['author'].format(author=author)
        )
        
        return '\n'.join(layer1)
    
    def _render_layer2(self, kwargs: Dict[str, Any]) -> str:
        """Render Layer 2 executive summary"""
        # Layer 2 is flexible - can be customized per orchestrator
        # For now, return empty (can be extended)
        return ""
    
    def _get_layer3_template(self, orchestrator: str) -> str:
        """Get Layer 3 template for orchestrator"""
        # Layer 3 templates are orchestrator-specific
        # For now, return generic
        return f"--- {orchestrator.upper()} OUTPUT ---"
