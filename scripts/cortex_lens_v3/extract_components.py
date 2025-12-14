#!/usr/bin/env python3
"""
CORTEX Lens v3.0 - Component Style Extraction Script

Extracts component styles from admin dashboard for migration to CORTEX Lens.

Usage:
    python scripts/cortex_lens_v3/extract_components.py

Output:
    - cortex-brain/documents/planning/active/cortex-enhancements/extracted-component-styles.json
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, asdict


@dataclass
class ComponentStyle:
    """Component CSS style definition."""
    name: str
    selectors: List[str]
    base_styles: Dict[str, str]
    modifiers: Dict[str, Dict[str, str]]
    states: Dict[str, Dict[str, str]]
    responsive: Dict[str, Dict[str, str]]
    migration_priority: str  # HIGH, MEDIUM, LOW
    migration_type: str  # EXTRACT, CREATE, ADAPT


class ComponentExtractor:
    """Extract component styles from CSS."""
    
    # Component categories from migration checklist
    COMPONENTS = {
        'cards': ['card', 'metric-card', 'status-card', 'info-card'],
        'navigation': ['sidebar', 'nav-item', 'breadcrumb', 'tab'],
        'buttons': ['btn', 'button', 'action-btn', 'icon-btn'],
        'forms': ['input', 'select', 'textarea', 'checkbox', 'radio', 'form-group'],
        'tables': ['table', 'table-row', 'table-header', 'data-grid'],
        'modals': ['modal', 'dialog', 'overlay'],
        'visualizations': ['chart-container', 'viz-wrapper', 'd3-container'],
        'layouts': ['container', 'grid', 'flex-layout', 'section'],
        'typography': ['heading', 'text', 'label', 'code-block'],
        'loaders': ['spinner', 'skeleton', 'progress-bar', 'loading']
    }
    
    # Migration priority based on Phase 1-6 roadmap
    PRIORITY_MAP = {
        # Phase 1-2 (HIGH)
        'card': 'HIGH', 'sidebar': 'HIGH', 'nav-item': 'HIGH', 'heading': 'HIGH',
        # Phase 3 (MEDIUM-HIGH)
        'table': 'MEDIUM', 'metric-card': 'MEDIUM', 'chart-container': 'MEDIUM',
        # Phase 4-5 (MEDIUM)
        'btn': 'MEDIUM', 'modal': 'MEDIUM', 'input': 'MEDIUM',
        # Phase 6 (LOW)
        'spinner': 'LOW', 'skeleton': 'LOW', 'progress-bar': 'LOW'
    }
    
    def __init__(self, admin_styles_dir: Path, output_file: Path):
        self.admin_styles_dir = admin_styles_dir
        self.output_file = output_file
        self.components: Dict[str, ComponentStyle] = {}
    
    def extract_from_file(self, css_file: Path):
        """Extract component styles from CSS file."""
        if not css_file.exists():
            return
        
        print(f"📄 Processing: {css_file.name}")
        
        content = css_file.read_text(encoding='utf-8')
        
        # Extract all CSS rules
        rule_pattern = r'([^{}]+)\s*\{([^}]+)\}'
        matches = re.finditer(rule_pattern, content, re.DOTALL)
        
        for match in matches:
            selectors = match.group(1).strip()
            properties = match.group(2).strip()
            
            # Check if selector matches any component
            for category, component_names in self.COMPONENTS.items():
                for comp_name in component_names:
                    if self.selector_matches_component(selectors, comp_name):
                        self.add_component_style(comp_name, selectors, properties)
    
    def selector_matches_component(self, selector: str, component_name: str) -> bool:
        """Check if selector matches component name."""
        selector_lower = selector.lower()
        return (
            f'.{component_name}' in selector_lower or
            f'#{component_name}' in selector_lower or
            f'[class*="{component_name}"]' in selector_lower or
            selector_lower.startswith(component_name)
        )
    
    def add_component_style(self, component_name: str, selector: str, properties: str):
        """Add or update component style."""
        if component_name not in self.components:
            self.components[component_name] = ComponentStyle(
                name=component_name,
                selectors=[],
                base_styles={},
                modifiers={},
                states={},
                responsive={},
                migration_priority=self.PRIORITY_MAP.get(component_name, 'MEDIUM'),
                migration_type=self.determine_migration_type(component_name)
            )
        
        component = self.components[component_name]
        
        # Add selector if not already present
        if selector not in component.selectors:
            component.selectors.append(selector)
        
        # Parse properties
        prop_dict = self.parse_properties(properties)
        
        # Categorize properties
        if ':hover' in selector or ':focus' in selector or ':active' in selector:
            state = 'hover' if ':hover' in selector else 'focus' if ':focus' in selector else 'active'
            component.states[state] = prop_dict
        elif '@media' in selector:
            breakpoint = self.extract_breakpoint(selector)
            component.responsive[breakpoint] = prop_dict
        elif '--' in selector or '[' in selector:
            modifier = self.extract_modifier(selector)
            component.modifiers[modifier] = prop_dict
        else:
            component.base_styles.update(prop_dict)
    
    def parse_properties(self, properties: str) -> Dict[str, str]:
        """Parse CSS properties into dict."""
        prop_dict = {}
        prop_pattern = r'([a-z-]+)\s*:\s*([^;]+);'
        matches = re.findall(prop_pattern, properties, re.IGNORECASE)
        
        for prop, value in matches:
            prop_dict[prop.strip()] = value.strip()
        
        return prop_dict
    
    def extract_breakpoint(self, selector: str) -> str:
        """Extract media query breakpoint."""
        match = re.search(r'min-width:\s*(\d+px|\d+em|var\([^)]+\))', selector)
        return match.group(1) if match else 'unknown'
    
    def extract_modifier(self, selector: str) -> str:
        """Extract modifier class or attribute."""
        if '--' in selector:
            match = re.search(r'--([a-z-]+)', selector)
            return match.group(1) if match else 'unknown'
        elif '[' in selector:
            match = re.search(r'\[([^\]]+)\]', selector)
            return match.group(1) if match else 'unknown'
        else:
            return 'default'
    
    def determine_migration_type(self, component_name: str) -> str:
        """Determine migration type from component migration checklist."""
        # Based on CORTEX-LENS-V3-COMPONENT-MIGRATION-CHECKLIST.md
        extract_components = [
            'card', 'metric-card', 'sidebar', 'nav-item', 'table', 
            'chart-container', 'btn', 'modal', 'input', 'heading'
        ]
        
        create_components = [
            'code-block', 'diff-viewer', 'file-tree', 'command-palette',
            'search-bar', 'filter-panel'
        ]
        
        if component_name in extract_components:
            return 'EXTRACT'
        elif component_name in create_components:
            return 'CREATE'
        else:
            return 'ADAPT'
    
    def extract_all(self):
        """Extract components from all CSS files."""
        print("🔍 Extracting component styles from admin dashboard...\n")
        
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
        """Save extracted components to JSON."""
        # Group by category
        output = {
            'components': {},
            'by_priority': {'HIGH': [], 'MEDIUM': [], 'LOW': []},
            'by_type': {'EXTRACT': [], 'CREATE': [], 'ADAPT': []},
            '_summary': {
                'total_components': len(self.components),
                'extraction_date': '2025-12-14'
            }
        }
        
        for comp_name, comp_style in self.components.items():
            comp_dict = asdict(comp_style)
            output['components'][comp_name] = comp_dict
            output['by_priority'][comp_style.migration_priority].append(comp_name)
            output['by_type'][comp_style.migration_type].append(comp_name)
        
        # Update summary
        output['_summary']['by_priority'] = {
            priority: len(comps) for priority, comps in output['by_priority'].items()
        }
        output['_summary']['by_type'] = {
            mtype: len(comps) for mtype, comps in output['by_type'].items()
        }
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(json.dumps(output, indent=2), encoding='utf-8')
        
        print(f"\n✅ Extraction complete!")
        print(f"   Total components: {len(self.components)}")
        print(f"   HIGH priority: {len(output['by_priority']['HIGH'])}")
        print(f"   MEDIUM priority: {len(output['by_priority']['MEDIUM'])}")
        print(f"   LOW priority: {len(output['by_priority']['LOW'])}")
        print(f"   Output: {self.output_file}")
    
    def print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 70)
        print("COMPONENT STYLE EXTRACTION SUMMARY")
        print("=" * 70)
        
        for comp_name, comp_style in sorted(self.components.items())[:10]:
            print(f"\n{comp_name.upper()}")
            print(f"  Priority: {comp_style.migration_priority}")
            print(f"  Type: {comp_style.migration_type}")
            print(f"  Selectors: {len(comp_style.selectors)}")
            print(f"  Base styles: {len(comp_style.base_styles)}")
            print(f"  Modifiers: {len(comp_style.modifiers)}")
            print(f"  States: {len(comp_style.states)}")
        
        if len(self.components) > 10:
            print(f"\n... and {len(self.components) - 10} more components")


def main():
    """Main execution."""
    cortex_root = Path(__file__).parent.parent.parent
    admin_styles = cortex_root / "cortex-brain" / "dashboards" / "ui" / "styles"
    output_file = cortex_root / "cortex-brain" / "documents" / "planning" / "active" / "cortex-enhancements" / "extracted-component-styles.json"
    
    extractor = ComponentExtractor(admin_styles, output_file)
    
    if extractor.extract_all():
        extractor.save_results()
        extractor.print_summary()
    else:
        print("\n❌ Extraction failed. Check admin dashboard location.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
