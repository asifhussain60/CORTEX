#!/usr/bin/env python3
"""
CORTEX Lens v3.0 - CSS Variable Extraction Script

Extracts CSS variables from admin dashboard and maps them to CORTEX Lens
with 125% typography scale multiplier.

Usage:
    python scripts/cortex_lens_v3/extract_css_variables.py

Output:
    - cortex-brain/documents/planning/active/cortex-enhancements/extracted-css-variables.json
    - Categorized variables by type (colors, spacing, typography, etc.)
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CSSVariable:
    """CSS variable with metadata."""
    name: str
    value: str
    category: str
    usage_example: str = ""
    lens_value: str = ""  # For 125% scaled typography


class CSSVariableExtractor:
    """Extract CSS variables from admin dashboard."""
    
    def __init__(self, admin_styles_dir: Path, output_file: Path):
        self.admin_styles_dir = admin_styles_dir
        self.output_file = output_file
        self.variables: Dict[str, List[CSSVariable]] = {
            'colors': [],
            'spacing': [],
            'typography': [],
            'shadows': [],
            'borders': [],
            'z_index': [],
            'transitions': [],
            'breakpoints': [],
            'glassmorphism': []
        }
    
    def categorize_variable(self, name: str) -> str:
        """Categorize variable by name prefix."""
        if name.startswith('--color-') or name.startswith('--bg-') or name.startswith('--text-'):
            return 'colors'
        elif name.startswith('--spacing-') or name.startswith('--gap-') or name.startswith('--padding-'):
            return 'spacing'
        elif name.startswith('--font-') or name.startswith('--line-height-') or name.startswith('--letter-spacing-'):
            return 'typography'
        elif name.startswith('--shadow-') or name.startswith('--box-shadow-'):
            return 'shadows'
        elif name.startswith('--border-') or name.startswith('--radius-'):
            return 'borders'
        elif name.startswith('--z-'):
            return 'z_index'
        elif name.startswith('--transition-') or name.startswith('--duration-') or name.startswith('--easing-'):
            return 'transitions'
        elif name.startswith('--breakpoint-') or name.startswith('--screen-'):
            return 'breakpoints'
        elif name.startswith('--blur-') or name.startswith('--opacity-') or name.startswith('--backdrop-'):
            return 'glassmorphism'
        else:
            return 'other'
    
    def apply_typography_scale(self, name: str, value: str) -> str:
        """Apply 125% scale to font sizes."""
        if '--font-size-' not in name:
            return value
        
        # Extract pixel value
        match = re.search(r'(\d+(?:\.\d+)?)px', value)
        if match:
            original_px = float(match.group(1))
            scaled_px = original_px * 1.25
            return f"{scaled_px}px"
        
        # Handle calc() expressions
        if 'calc(' in value:
            return value.replace('var(--scale-factor)', '1.25')
        
        return value
    
    def extract_from_file(self, css_file: Path):
        """Extract variables from a single CSS file."""
        if not css_file.exists():
            print(f"⚠️  File not found: {css_file}")
            return
        
        print(f"📄 Processing: {css_file.name}")
        
        content = css_file.read_text(encoding='utf-8')
        
        # Find :root block
        root_match = re.search(r':root\s*\{([^}]+)\}', content, re.DOTALL)
        if not root_match:
            print(f"   No :root block found in {css_file.name}")
            return
        
        root_content = root_match.group(1)
        
        # Extract all CSS variables
        variable_pattern = r'(--[a-z0-9-]+)\s*:\s*([^;]+);'
        matches = re.findall(variable_pattern, root_content, re.IGNORECASE)
        
        for name, value in matches:
            name = name.strip()
            value = value.strip()
            
            category = self.categorize_variable(name)
            lens_value = self.apply_typography_scale(name, value)
            
            var = CSSVariable(
                name=name,
                value=value,
                category=category,
                lens_value=lens_value if lens_value != value else ""
            )
            
            if category != 'other':
                self.variables[category].append(var)
    
    def extract_all(self):
        """Extract variables from all CSS files."""
        print("🔍 Extracting CSS variables from admin dashboard...\n")
        
        # Check if admin styles directory exists
        if not self.admin_styles_dir.exists():
            print(f"❌ Admin styles directory not found: {self.admin_styles_dir}")
            print(f"   Expected location: cortex-brain/dashboards/ui/styles/")
            return False
        
        # Process all CSS files
        css_files = sorted(self.admin_styles_dir.glob('*.css'))
        if not css_files:
            print(f"❌ No CSS files found in {self.admin_styles_dir}")
            return False
        
        for css_file in css_files:
            self.extract_from_file(css_file)
        
        return True
    
    def generate_usage_examples(self):
        """Generate usage examples for variables."""
        examples = {
            'colors': 'color: var(--color-primary);',
            'spacing': 'margin: var(--spacing-md);',
            'typography': 'font-size: var(--font-size-lg);',
            'shadows': 'box-shadow: var(--shadow-md);',
            'borders': 'border-radius: var(--radius-md);',
            'z_index': 'z-index: var(--z-modal);',
            'transitions': 'transition: all var(--duration-normal) var(--easing-ease-in-out);',
            'breakpoints': '@media (min-width: var(--breakpoint-md)) { ... }',
            'glassmorphism': 'backdrop-filter: var(--blur-medium);'
        }
        
        for category, example in examples.items():
            for var in self.variables[category]:
                var.usage_example = example
    
    def save_results(self):
        """Save extracted variables to JSON."""
        self.generate_usage_examples()
        
        # Convert to serializable format
        output = {
            category: [asdict(var) for var in vars_list]
            for category, vars_list in self.variables.items()
            if vars_list  # Only include non-empty categories
        }
        
        # Add summary
        total_vars = sum(len(vars_list) for vars_list in self.variables.values())
        output['_summary'] = {
            'total_variables': total_vars,
            'by_category': {
                cat: len(vars_list) for cat, vars_list in self.variables.items() if vars_list
            },
            'typography_scaled': sum(1 for var in self.variables['typography'] if var.lens_value),
            'extraction_date': '2025-12-14'
        }
        
        # Create output directory
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        self.output_file.write_text(json.dumps(output, indent=2), encoding='utf-8')
        
        print(f"\n✅ Extraction complete!")
        print(f"   Total variables: {total_vars}")
        print(f"   Categories: {len([c for c in self.variables if self.variables[c]])}")
        print(f"   Typography scaled: {output['_summary']['typography_scaled']}")
        print(f"   Output: {self.output_file}")
    
    def print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 70)
        print("CSS VARIABLE EXTRACTION SUMMARY")
        print("=" * 70)
        
        for category, vars_list in self.variables.items():
            if vars_list:
                print(f"\n{category.upper().replace('_', ' ')} ({len(vars_list)} variables):")
                for var in vars_list[:3]:  # Show first 3
                    print(f"  • {var.name}: {var.value}")
                    if var.lens_value:
                        print(f"    → Lens (125%): {var.lens_value}")
                if len(vars_list) > 3:
                    print(f"  ... and {len(vars_list) - 3} more")


def main():
    """Main execution."""
    # Paths
    cortex_root = Path(__file__).parent.parent.parent
    admin_styles = cortex_root / "cortex-brain" / "dashboards" / "ui" / "styles"
    output_file = cortex_root / "cortex-brain" / "documents" / "planning" / "active" / "cortex-enhancements" / "extracted-css-variables.json"
    
    # Extract
    extractor = CSSVariableExtractor(admin_styles, output_file)
    
    if extractor.extract_all():
        extractor.save_results()
        extractor.print_summary()
    else:
        print("\n❌ Extraction failed. Check admin dashboard location.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
