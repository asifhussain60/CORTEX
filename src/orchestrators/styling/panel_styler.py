"""
Panel Styler Orchestrator - Natural Language Glassmorphism Styling.

Enables semantic styling commands like "style X like Y" using the
named panel taxonomy from glassmorphism-css-standardization.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class PanelStyle:
    """Named panel style definition."""
    name: str
    class_name: str
    use_case: str
    visual_signature: str
    css_file: str
    example_html: str


class PanelStyler:
    """
    Orchestrator for applying glassmorphism panel styles via natural language.
    
    Features:
    - Named panel taxonomy (11 semantic styles)
    - "Style X like Y" command parsing
    - HTML/CSS preview generation
    - Class name resolution
    - BEM sub-element support
    
    Panel Taxonomy:
        tetris: Compact metrics grid (6+ tiles, dashboard KPIs)
        intro: Hero description card (landing sections, CTAs)
        compact-cards: Horizontal capability row (5-6 cards)
        grid-cards: Detailed grid layout (2x3/3x3)
        hero-glass: Full-width hero sections
        sidebar-glass: Navigation/filter panels (vertical, sticky)
        modal-glass: Overlay dialogs (confirmations, forms)
        toast-glass: Notifications/alerts (4 variants)
        blob-glass: Decorative organic shapes (3 sizes)
        neon-glass: Accent panels with glow (CTAs)
        agent-showcase: Agent capability cards (2x2 grid)
    
    Usage:
        styler = PanelStyler()
        
        # Natural language commands
        result = styler.apply_style("style metrics dashboard like tetris")
        result = styler.apply_style("make card look like intro panel")
        result = styler.apply_style("use grid cards layout")
        
        # Direct panel application
        result = styler.get_panel_style("tetris")
    """
    
    # Panel taxonomy mapping
    PANEL_TAXONOMY: Dict[str, PanelStyle] = {
        "tetris": PanelStyle(
            name="Tetris Panel",
            class_name="panel-tetris",
            use_case="Compact metrics grid (6+ tiles, dashboard KPIs)",
            visual_signature="Horizontal icon+value pairs in responsive grid",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-tetris">
    <div class="panel-tetris__grid">
        <div class="panel-tetris__tile">
            <i class="panel-tetris__tile-icon fas fa-chart-line"></i>
            <div class="panel-tetris__tile-content">
                <div class="panel-tetris__tile-value">87%</div>
                <div class="panel-tetris__tile-label">Performance</div>
            </div>
        </div>
        <!-- Add 5+ more tiles -->
    </div>
</div>"""
        ),
        "intro": PanelStyle(
            name="Intro Panel",
            class_name="panel-intro",
            use_case="Hero description card (landing sections, CTAs)",
            visual_signature="Large centered card with gradient background",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-intro">
    <h1 class="panel-intro__title">Welcome to CORTEX</h1>
    <p class="panel-intro__description">
        AI-powered development orchestration with long-term memory
    </p>
    <div class="panel-intro__actions">
        <button class="panel-intro__cta">Get Started</button>
    </div>
</div>"""
        ),
        "compact-cards": PanelStyle(
            name="Compact Cards",
            class_name="panel-compact-cards",
            use_case="Horizontal capability row (5-6 cards, features)",
            visual_signature="Grid of cards with icon+title+description",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-compact-cards">
    <div class="panel-compact-cards__card">
        <i class="panel-compact-cards__icon fas fa-brain"></i>
        <h3 class="panel-compact-cards__title">AI Planning</h3>
        <p class="panel-compact-cards__description">
            Autonomous plan generation and execution
        </p>
    </div>
    <!-- Add 4-5 more cards -->
</div>"""
        ),
        "grid-cards": PanelStyle(
            name="Grid Cards",
            class_name="panel-grid-cards",
            use_case="Detailed grid layout (2x3/3x3, analysis views)",
            visual_signature="Multi-column grid with detailed content and badges",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-grid-cards">
    <div class="panel-grid-cards__card">
        <div class="panel-grid-cards__header">
            <i class="panel-grid-cards__icon fas fa-search"></i>
            <h3 class="panel-grid-cards__title">Code Analysis</h3>
        </div>
        <p class="panel-grid-cards__description">
            Deep AST-based code intelligence
        </p>
        <div class="panel-grid-cards__badges">
            <span class="panel-grid-cards__badge">Python</span>
            <span class="panel-grid-cards__badge">TypeScript</span>
        </div>
    </div>
    <!-- Add 5+ more cards -->
</div>"""
        ),
        "hero-glass": PanelStyle(
            name="Hero Glass",
            class_name="panel-hero-glass",
            use_case="Full-width hero sections (landing pages)",
            visual_signature="Full-width panel with strong blur and centered content",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-hero-glass">
    <div class="panel-hero-glass__content">
        <h1 class="panel-hero-glass__title">CORTEX 5.0</h1>
        <p class="panel-hero-glass__subtitle">
            The Future of AI-Assisted Development
        </p>
        <div class="panel-hero-glass__actions">
            <button class="panel-hero-glass__primary-cta">Explore</button>
            <button class="panel-hero-glass__secondary-cta">Learn More</button>
        </div>
    </div>
</div>"""
        ),
        "sidebar-glass": PanelStyle(
            name="Sidebar Glass",
            class_name="panel-sidebar-glass",
            use_case="Navigation/filter panels (vertical, sticky)",
            visual_signature="Vertical sidebar with sections and sticky positioning",
            css_file="glass-named-panels.css",
            example_html="""<aside class="panel-sidebar-glass">
    <nav class="panel-sidebar-glass__nav">
        <div class="panel-sidebar-glass__section">
            <h3 class="panel-sidebar-glass__section-title">Navigation</h3>
            <ul class="panel-sidebar-glass__list">
                <li><a href="#">Dashboard</a></li>
                <li><a href="#">Projects</a></li>
            </ul>
        </div>
    </nav>
</aside>"""
        ),
        "modal-glass": PanelStyle(
            name="Modal Glass",
            class_name="panel-modal-glass",
            use_case="Overlay dialogs (confirmations, forms)",
            visual_signature="Centered overlay with header, content, and footer",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-modal-glass">
    <div class="panel-modal-glass__header">
        <h2 class="panel-modal-glass__title">Confirm Action</h2>
        <button class="panel-modal-glass__close">&times;</button>
    </div>
    <div class="panel-modal-glass__content">
        <p>Are you sure you want to proceed?</p>
    </div>
    <div class="panel-modal-glass__footer">
        <button class="panel-modal-glass__button panel-modal-glass__button--cancel">Cancel</button>
        <button class="panel-modal-glass__button panel-modal-glass__button--confirm">Confirm</button>
    </div>
</div>"""
        ),
        "toast-glass": PanelStyle(
            name="Toast Glass",
            class_name="panel-toast-glass",
            use_case="Notifications/alerts (4 variants: success, error, warning, info)",
            visual_signature="Small floating panel with icon, message, and auto-dismiss",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-toast-glass panel-toast-glass--success">
    <i class="panel-toast-glass__icon fas fa-check-circle"></i>
    <div class="panel-toast-glass__content">
        <div class="panel-toast-glass__title">Success!</div>
        <div class="panel-toast-glass__message">Operation completed</div>
    </div>
    <button class="panel-toast-glass__close">&times;</button>
</div>"""
        ),
        "blob-glass": PanelStyle(
            name="Blob Glass",
            class_name="panel-blob-glass",
            use_case="Decorative organic shapes (3 sizes, liquid morphing)",
            visual_signature="Organic morphing shapes with blur and animation",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-blob-glass panel-blob-glass--md">
    <!-- Decorative blob with liquid morphing animation -->
</div>"""
        ),
        "neon-glass": PanelStyle(
            name="Neon Glass",
            class_name="panel-neon-glass",
            use_case="Accent panels with glow (CTAs, premium cards)",
            visual_signature="Glowing borders with vibrant colors and pulse animation",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-neon-glass">
    <div class="panel-neon-glass__content">
        <h3 class="panel-neon-glass__title">Premium Feature</h3>
        <p class="panel-neon-glass__description">
            Unlock advanced capabilities
        </p>
        <button class="panel-neon-glass__cta">Upgrade Now</button>
    </div>
</div>"""
        ),
        "agent-showcase": PanelStyle(
            name="Agent Showcase",
            class_name="panel-agent-showcase",
            use_case="Agent capability cards (2x2 grid with header/tags)",
            visual_signature="Header (icon+title+subtitle) + 2x2 grid + tag footer",
            css_file="glass-named-panels.css",
            example_html="""<div class="panel-agent-showcase">
    <div class="panel-agent-showcase__header">
        <i class="panel-agent-showcase__icon fas fa-robot"></i>
        <div class="panel-agent-showcase__header-content">
            <h3 class="panel-agent-showcase__title">Planning Agent</h3>
            <p class="panel-agent-showcase__subtitle">Autonomous Plan Generation</p>
        </div>
    </div>
    <div class="panel-agent-showcase__grid">
        <div class="panel-agent-showcase__capability">
            <i class="fas fa-brain"></i>
            <span>Context Analysis</span>
        </div>
        <!-- Add 3 more capabilities -->
    </div>
    <div class="panel-agent-showcase__tags">
        <span class="panel-agent-showcase__tag">AI-Powered</span>
        <span class="panel-agent-showcase__tag">Autonomous</span>
    </div>
</div>"""
        ),
    }
    
    # Command pattern matching
    STYLE_PATTERNS = [
        # "style X like Y"
        (r"style\s+(.+?)\s+like\s+(\w+(?:-\w+)*)", "apply"),
        # "make X look like Y"
        (r"make\s+(.+?)\s+look\s+like\s+(\w+(?:-\w+)*)", "apply"),
        # "use Y panel/layout/style"
        (r"use\s+(\w+(?:-\w+)*)\s+(?:panel|layout|style)", "direct"),
        # "apply Y to X"
        (r"apply\s+(\w+(?:-\w+)*)\s+to\s+(.+)", "apply_reverse"),
        # "Y style for X"
        (r"(\w+(?:-\w+)*)\s+style\s+for\s+(.+)", "apply_reverse"),
    ]
    
    def __init__(self):
        """Initialize Panel Styler."""
        self.logger = logging.getLogger("cortex.orchestrators.panel_styler")
        self.logger.info("Panel Styler initialized with 11 panel styles")
    
    def apply_style(self, command: str) -> Dict[str, Any]:
        """
        Apply glassmorphism panel style based on natural language command.
        
        Args:
            command: Natural language styling command
            
        Returns:
            Dictionary with:
                - success: bool
                - panel_name: str (matched panel)
                - class_name: str (CSS class)
                - html_example: str (BEM HTML structure)
                - css_file: str (source file)
                - target: str (optional, what to style)
                - message: str (human-readable result)
        
        Examples:
            >>> styler.apply_style("style dashboard like tetris")
            {
                'success': True,
                'panel_name': 'tetris',
                'class_name': 'panel-tetris',
                'target': 'dashboard',
                'message': 'Apply .panel-tetris class to dashboard'
            }
        """
        command_lower = command.lower().strip()
        
        # Try pattern matching
        for pattern, action_type in self.STYLE_PATTERNS:
            match = re.search(pattern, command_lower)
            if match:
                return self._process_match(match, action_type)
        
        # No pattern match - try direct panel name
        for panel_key in self.PANEL_TAXONOMY.keys():
            if panel_key in command_lower:
                return self._direct_panel_application(panel_key)
        
        # No match found
        return {
            "success": False,
            "message": f"Could not parse styling command: '{command}'",
            "suggestion": "Try: 'style X like tetris' or 'use grid-cards layout'",
            "available_panels": list(self.PANEL_TAXONOMY.keys())
        }
    
    def _process_match(self, match: re.Match, action_type: str) -> Dict[str, Any]:
        """Process regex match and extract panel + target."""
        if action_type == "apply":
            target = match.group(1).strip()
            panel_name = match.group(2).strip()
        elif action_type == "direct":
            panel_name = match.group(1).strip()
            target = None
        elif action_type == "apply_reverse":
            panel_name = match.group(1).strip()
            target = match.group(2).strip()
        else:
            return {"success": False, "message": "Unknown action type"}
        
        # Normalize panel name (handle "tetris-panel" → "tetris")
        panel_name = panel_name.replace("-panel", "").replace("_", "-")
        
        # Find matching panel
        if panel_name in self.PANEL_TAXONOMY:
            return self.get_panel_style(panel_name, target)
        
        # Try fuzzy matching
        similar_panels = self._find_similar_panels(panel_name)
        if similar_panels:
            return {
                "success": False,
                "message": f"Panel '{panel_name}' not found",
                "did_you_mean": similar_panels,
                "available_panels": list(self.PANEL_TAXONOMY.keys())
            }
        
        return {
            "success": False,
            "message": f"Unknown panel: '{panel_name}'",
            "available_panels": list(self.PANEL_TAXONOMY.keys())
        }
    
    def _direct_panel_application(self, panel_key: str) -> Dict[str, Any]:
        """Apply panel directly without target."""
        return self.get_panel_style(panel_key, target=None)
    
    def _find_similar_panels(self, query: str) -> List[str]:
        """Find panels with similar names (fuzzy matching)."""
        query_lower = query.lower()
        similar = []
        
        for panel_key, panel_style in self.PANEL_TAXONOMY.items():
            # Check if query is substring of panel name/key
            if query_lower in panel_key or query_lower in panel_style.name.lower():
                similar.append(panel_key)
            # Check if panel key is substring of query
            elif panel_key in query_lower:
                similar.append(panel_key)
        
        return similar[:3]  # Top 3 matches
    
    def get_panel_style(self, panel_name: str, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Get full panel style definition.
        
        Args:
            panel_name: Panel key (e.g., "tetris", "intro")
            target: Optional target element to apply style to
            
        Returns:
            Dictionary with panel details and application instructions
        """
        if panel_name not in self.PANEL_TAXONOMY:
            return {
                "success": False,
                "message": f"Panel '{panel_name}' not found",
                "available_panels": list(self.PANEL_TAXONOMY.keys())
            }
        
        panel = self.PANEL_TAXONOMY[panel_name]
        
        result = {
            "success": True,
            "panel_name": panel_name,
            "panel_display_name": panel.name,
            "class_name": panel.class_name,
            "use_case": panel.use_case,
            "visual_signature": panel.visual_signature,
            "css_file": panel.css_file,
            "html_example": panel.example_html,
            "css_import": "cortex-glass-system.css (includes all panels)",
        }
        
        # Add application instructions
        if target:
            result["target"] = target
            result["message"] = f"Apply `.{panel.class_name}` class to {target}"
            result["instruction"] = f'<div class="{panel.class_name}"><!-- {target} content --></div>'
        else:
            result["message"] = f"Use `.{panel.class_name}` panel style"
            result["instruction"] = f"Add class=\"{panel.class_name}\" to your HTML element"
        
        return result
    
    def list_panels(self) -> Dict[str, Any]:
        """
        List all available panel styles.
        
        Returns:
            Dictionary with panel taxonomy and metadata
        """
        panels = []
        for key, panel in self.PANEL_TAXONOMY.items():
            panels.append({
                "key": key,
                "name": panel.name,
                "class_name": panel.class_name,
                "use_case": panel.use_case,
                "visual_signature": panel.visual_signature
            })
        
        return {
            "success": True,
            "count": len(panels),
            "panels": panels,
            "css_system": "cortex-glass-system.css",
            "documentation": "docs/design-system/panel-viewer.html"
        }
    
    def generate_preview(self, panel_name: str, content: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate HTML preview for a panel with optional custom content.
        
        Args:
            panel_name: Panel key
            content: Optional dictionary with custom content (title, description, etc.)
            
        Returns:
            Complete HTML snippet with CSS imports
        """
        if panel_name not in self.PANEL_TAXONOMY:
            return f"<!-- Error: Panel '{panel_name}' not found -->"
        
        panel = self.PANEL_TAXONOMY[panel_name]
        
        # Build HTML preview
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{panel.name} Preview</title>
    <link rel="stylesheet" href="../assets/css/cortex-glass-system.css">
    <style>
        body {{
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            padding: 2rem;
            font-family: 'Segoe UI', sans-serif;
        }}
    </style>
</head>
<body>
    {panel.example_html}
</body>
</html>"""
        
        return html


# Convenience function for CLI/API usage
def style_command(command: str) -> Dict[str, Any]:
    """
    Process styling command (convenience wrapper).
    
    Args:
        command: Natural language styling command
        
    Returns:
        Styling result dictionary
    
    Example:
        >>> style_command("style dashboard like tetris")
    """
    styler = PanelStyler()
    return styler.apply_style(command)
