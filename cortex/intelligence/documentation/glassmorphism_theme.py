"""
Glassmorphism CSS Theme Generator — MEGA-B S1

AC-MEGA-B-S1-004: GitHub Pages compatibility

Generates modern glassmorphism design theme:
- Frosted glass effects (backdrop-filter blur)
- Gradient backgrounds (linear/radial)
- Multi-layer shadows (depth perception)
- Responsive design (mobile-first)
- Minified CSS (<20KB)

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ThemeConfig:
    """
    Theme configuration.
    
    Attributes:
        primary_color: Primary color (hex)
        secondary_color: Secondary color (hex)
        glass_opacity: Glass panel opacity (0.0-1.0)
    """
    primary_color: str = "#6366f1"
    secondary_color: str = "#8b5cf6"
    glass_opacity: float = 0.1


class GlassmorphismTheme:
    """
    Glassmorphism CSS theme generator.
    
    Generates modern glass-morphic design system with:
    - Frosted glass panels (backdrop-filter)
    - Gradient backgrounds
    - Elevation shadows
    - Responsive breakpoints
    
    AC-MEGA-B-S1-004: GitHub Pages compatible CSS
    """
    
    def __init__(
        self,
        output_dir: Path,
        config: ThemeConfig,
    ) -> None:
        """
        Initialize theme generator.
        
        Args:
            output_dir: Output directory for CSS
            config: Theme configuration
        """
        self.output_dir = Path(output_dir)
        self.config = config
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, minify: bool = False) -> Path:
        """
        Generate complete theme CSS.
        
        Args:
            minify: Whether to minify CSS
            
        Returns:
            Path to generated CSS file
        """
        css_path = self.output_dir / "theme.css"
        
        # Build CSS sections
        sections = [
            self._generate_reset(),
            self._generate_base_styles(),
            self._generate_glass_effects(),
            self._generate_gradients(),
            self._generate_shadows(),
            self._generate_responsive(),
        ]
        
        # Join sections
        if minify:
            content = "".join(s.replace("\n", "") for s in sections)
        else:
            content = "\n\n".join(sections)
        
        # Write CSS
        css_path.write_text(content)
        
        return css_path
    
    def _generate_reset(self) -> str:
        """Generate CSS reset."""
        return """/* Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}"""
    
    def _generate_base_styles(self) -> str:
        """Generate base styles."""
        return f"""/* Base Styles */
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(135deg, {self.config.primary_color}20 0%, {self.config.secondary_color}20 100%);
    color: #1f2937;
    line-height: 1.6;
}}

h1, h2, h3 {{
    color: {self.config.primary_color};
    font-weight: 600;
}}"""
    
    def _generate_glass_effects(self) -> str:
        """Generate glassmorphism effects."""
        rgba = self._hex_to_rgba(self.config.primary_color, self.config.glass_opacity)
        
        return f"""/* Glass Effects */
.glass-panel {{
    background: rgba({rgba});
    backdrop-filter: blur(10px) saturate(180%);
    -webkit-backdrop-filter: blur(10px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 2rem;
}}"""
    
    def _generate_gradients(self) -> str:
        """Generate gradient backgrounds."""
        return f"""/* Gradients */
.gradient-bg {{
    background: linear-gradient(135deg, {self.config.primary_color} 0%, {self.config.secondary_color} 100%);
}}

.gradient-text {{
    background: linear-gradient(135deg, {self.config.primary_color}, {self.config.secondary_color});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}"""
    
    def _generate_shadows(self) -> str:
        """Generate shadow layers."""
        return """/* Shadows */
.shadow-sm {
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.shadow-md {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.shadow-lg {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.elevation-1 {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}"""
    
    def _generate_responsive(self) -> str:
        """Generate responsive media queries."""
        return """/* Responsive */
@media (max-width: 768px) {
    .glass-panel {
        padding: 1rem;
    }
    
    body {
        font-size: 14px;
    }
}

@media (min-width: 769px) {
    .container {
        max-width: 1200px;
        margin: 0 auto;
    }
}"""
    
    def _hex_to_rgba(self, hex_color: str, opacity: float) -> str:
        """
        Convert hex color to RGBA components.
        
        Args:
            hex_color: Hex color (#RRGGBB)
            opacity: Opacity (0.0-1.0)
            
        Returns:
            RGBA component string "R, G, B, A"
        """
        # Strip # if present
        hex_color = hex_color.lstrip("#")
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return f"{r}, {g}, {b}, {opacity}"
