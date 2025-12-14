#!/usr/bin/env python3
"""
CORTEX Lens v3.0 - Glassmorphism Pattern Extraction Script

Extracts glassmorphism patterns from admin dashboard CSS files.

Usage:
    python scripts/cortex_lens_v3/extract_glassmorphism.py

Output:
    - cortex-brain/documents/planning/active/cortex-enhancements/extracted-glassmorphism-patterns.json
"""

import re
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class GlassmorphismPattern:
    """Glassmorphism CSS pattern."""
    name: str
    selector: str
    backdrop_filter: str
    background: str
    border: str
    box_shadow: str = ""
    border_radius: str = ""
    use_case: str = ""


class GlassmorphismExtractor:
    """Extract glassmorphism patterns from CSS."""
    
    def __init__(self, admin_styles_dir: Path, output_file: Path):
        self.admin_styles_dir = admin_styles_dir
        self.output_file = output_file
        self.patterns: List[GlassmorphismPattern] = []
    
    def extract_from_file(self, css_file: Path):
        """Extract glassmorphism patterns from CSS file."""
        if not css_file.exists():
            return
        
        print(f"📄 Processing: {css_file.name}")
        
        content = css_file.read_text(encoding='utf-8')
        
        # Find all selectors with backdrop-filter
        # Pattern: selector { ... backdrop-filter: ...; ... }
        selector_pattern = r'([^{}]+)\s*\{([^}]+backdrop-filter[^}]+)\}'
        matches = re.finditer(selector_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            selector = match.group(1).strip()
            properties = match.group(2)
            
            # Extract glassmorphism properties
            backdrop_filter = self.extract_property(properties, 'backdrop-filter')
            background = self.extract_property(properties, 'background')
            border = self.extract_property(properties, 'border')
            box_shadow = self.extract_property(properties, 'box-shadow')
            border_radius = self.extract_property(properties, 'border-radius')
            
            if backdrop_filter:
                # Determine use case from selector
                use_case = self.determine_use_case(selector)
                
                # Create pattern name
                pattern_name = self.generate_pattern_name(selector)
                
                pattern = GlassmorphismPattern(
                    name=pattern_name,
                    selector=selector,
                    backdrop_filter=backdrop_filter,
                    background=background or 'rgba(255, 255, 255, 0.1)',
                    border=border or '1px solid rgba(255, 255, 255, 0.18)',
                    box_shadow=box_shadow,
                    border_radius=border_radius,
                    use_case=use_case
                )
                
                self.patterns.append(pattern)
    
    def extract_property(self, properties: str, prop_name: str) -> str:
        """Extract specific CSS property value."""
        pattern = rf'{prop_name}\s*:\s*([^;]+);'
        match = re.search(pattern, properties, re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def determine_use_case(self, selector: str) -> str:
        """Determine use case from selector."""
        selector_lower = selector.lower()
        
        if 'card' in selector_lower:
            return 'Card glassmorphism (main content containers)'
        elif 'sidebar' in selector_lower or 'nav' in selector_lower:
            return 'Sidebar/Navigation glassmorphism'
        elif 'modal' in selector_lower:
            return 'Modal overlay glassmorphism'
        elif 'button' in selector_lower or 'btn' in selector_lower:
            return 'Button glassmorphism'
        elif 'header' in selector_lower:
            return 'Header glassmorphism'
        elif 'footer' in selector_lower:
            return 'Footer glassmorphism'
        elif 'panel' in selector_lower or 'section' in selector_lower:
            return 'Panel/Section glassmorphism'
        else:
            return 'General glassmorphism effect'
    
    def generate_pattern_name(self, selector: str) -> str:
        """Generate pattern name from selector."""
        # Extract class name
        class_match = re.search(r'\.([a-z0-9-]+)', selector, re.IGNORECASE)
        if class_match:
            return f"glass-{class_match.group(1)}"
        else:
            return "glass-custom"
    
    def extract_all(self):
        """Extract patterns from all CSS files."""
        print("🔍 Extracting glassmorphism patterns from admin dashboard...\n")
        
        if not self.admin_styles_dir.exists():
            print(f"❌ Admin styles directory not found: {self.admin_styles_dir}")
            return False
        
        css_files = sorted(self.admin_styles_dir.glob('*.css'))
        if not css_files:
            print(f"❌ No CSS files found in {self.admin_styles_dir}")
            return False
        
        for css_file in css_files:
            self.extract_from_file(css_file)
        
        return True
    
    def save_results(self):
        """Save extracted patterns to JSON."""
        # Group patterns by use case
        grouped = {}
        for pattern in self.patterns:
            use_case = pattern.use_case or 'Other'
            if use_case not in grouped:
                grouped[use_case] = []
            grouped[use_case].append(asdict(pattern))
        
        output = {
            'patterns': grouped,
            '_summary': {
                'total_patterns': len(self.patterns),
                'unique_use_cases': len(grouped),
                'extraction_date': '2025-12-14'
            }
        }
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(json.dumps(output, indent=2), encoding='utf-8')
        
        print(f"\n✅ Extraction complete!")
        print(f"   Total patterns: {len(self.patterns)}")
        print(f"   Use cases: {len(grouped)}")
        print(f"   Output: {self.output_file}")
    
    def print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 70)
        print("GLASSMORPHISM PATTERN SUMMARY")
        print("=" * 70)
        
        for pattern in self.patterns[:5]:  # Show first 5
            print(f"\n{pattern.name.upper()}")
            print(f"  Selector: {pattern.selector}")
            print(f"  Backdrop: {pattern.backdrop_filter}")
            print(f"  Background: {pattern.background}")
            print(f"  Border: {pattern.border}")
            print(f"  Use Case: {pattern.use_case}")
        
        if len(self.patterns) > 5:
            print(f"\n... and {len(self.patterns) - 5} more patterns")


def main():
    """Main execution."""
    cortex_root = Path(__file__).parent.parent.parent
    admin_styles = cortex_root / "cortex-brain" / "dashboards" / "ui" / "styles"
    output_file = cortex_root / "cortex-brain" / "documents" / "planning" / "active" / "cortex-enhancements" / "extracted-glassmorphism-patterns.json"
    
    extractor = GlassmorphismExtractor(admin_styles, output_file)
    
    if extractor.extract_all():
        extractor.save_results()
        extractor.print_summary()
    else:
        print("\n❌ Extraction failed. Check admin dashboard location.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
