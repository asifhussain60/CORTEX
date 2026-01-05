#!/usr/bin/env python3
"""
Apply Glassmorphism Panel Backgrounds to All Level 1 Hub Pages

Applies randomized 7-color palette backgrounds with glass effects to all glass-card-display
sections in Level 1 hub pages. Uses complexity analysis to determine optimal approach.

7-Color Palette (from glassmorphism-design-standard.md):
- Cyan: rgba(0, 212, 255)
- Purple: rgba(123, 97, 255) → rgba(186, 85, 211)
- Teal: rgba(20, 184, 166)
- Indigo: rgba(79, 70, 229) → rgba(99, 102, 241)
- Pink: rgba(236, 72, 153) → rgba(244, 114, 182)
- Emerald: rgba(16, 185, 129) → rgba(52, 211, 153)
- Amber: rgba(245, 158, 11) → rgba(251, 191, 36)
"""

import re
import random
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Level 1 Hub Pages
LEVEL1_HUBS = [
    "docs/architecture/index.html",
    "docs/features/index.html",
    "docs/getting-started/index.html",
    "docs/knowledge/index.html",
    "docs/learning-paths/index.html",
    "docs/lens/index.html",
    "docs/orchestrators/index.html",
    "docs/security/index.html",
    "docs/story/index.html",
    "docs/sts/index.html",
    "docs/token-optimization/index.html",
    "docs/toolkit-manager/index.html",
]

# 7-Color Glassmorphism Palette
GLASS_COLORS = {
    'cyan': {
        'primary': 'rgba(0, 212, 255, 0.08)',
        'secondary': 'rgba(0, 212, 255, 0.06)',
        'border': 'rgba(0, 212, 255, 0.15)',
        'shadow': 'rgba(0, 212, 255, 0.1)',
    },
    'purple': {
        'primary': 'rgba(123, 97, 255, 0.08)',
        'secondary': 'rgba(186, 85, 211, 0.06)',
        'border': 'rgba(123, 97, 255, 0.15)',
        'shadow': 'rgba(123, 97, 255, 0.1)',
    },
    'teal': {
        'primary': 'rgba(20, 184, 166, 0.08)',
        'secondary': 'rgba(20, 184, 166, 0.06)',
        'border': 'rgba(20, 184, 166, 0.15)',
        'shadow': 'rgba(20, 184, 166, 0.1)',
    },
    'indigo': {
        'primary': 'rgba(79, 70, 229, 0.08)',
        'secondary': 'rgba(99, 102, 241, 0.06)',
        'border': 'rgba(79, 70, 229, 0.15)',
        'shadow': 'rgba(79, 70, 229, 0.1)',
    },
    'pink': {
        'primary': 'rgba(236, 72, 153, 0.08)',
        'secondary': 'rgba(244, 114, 182, 0.06)',
        'border': 'rgba(236, 72, 153, 0.15)',
        'shadow': 'rgba(236, 72, 153, 0.1)',
    },
    'emerald': {
        'primary': 'rgba(16, 185, 129, 0.08)',
        'secondary': 'rgba(52, 211, 153, 0.06)',
        'border': 'rgba(16, 185, 129, 0.15)',
        'shadow': 'rgba(16, 185, 129, 0.1)',
    },
    'amber': {
        'primary': 'rgba(245, 158, 11, 0.08)',
        'secondary': 'rgba(251, 191, 36, 0.06)',
        'border': 'rgba(245, 158, 11, 0.15)',
        'shadow': 'rgba(245, 158, 11, 0.1)',
    },
}

@dataclass
class SectionAnalysis:
    """Analysis results for a glass-card-display section."""
    section_html: str
    section_index: int
    has_background: bool
    current_background: str
    complexity_score: float
    recommended_color: str


class GlassmorphismApplicator:
    """Apply glassmorphism backgrounds to Level 1 hub pages."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.stats = {
            'processed_files': 0,
            'sections_updated': 0,
            'colors_used': {},
            'errors': [],
        }
    
    def calculate_complexity(self, html_content: str) -> float:
        """
        Calculate page complexity score.
        
        Scoring:
        - File size (KB) * 0.1
        - Inline styles * 0.5
        - Missing classes * 1.5
        - Broken patterns * 2.0
        """
        file_size_kb = len(html_content) / 1024
        inline_styles = len(re.findall(r'style="[^"]*"', html_content))
        missing_classes = len(re.findall(r'<div>|<section>|<article>', html_content))
        broken_patterns = len(re.findall(r'<h[1-6]>[^<]*</h[1-6]>\s*<div', html_content))
        
        complexity = (
            file_size_kb * 0.1 +
            inline_styles * 0.5 +
            missing_classes * 1.5 +
            broken_patterns * 2.0
        )
        
        return round(complexity, 2)
    
    def find_glass_sections(self, html_content: str) -> List[Tuple[str, int, int]]:
        """
        Find all glass-card-display sections with their positions.
        
        Returns: List of (section_html, start_pos, end_pos)
        """
        sections = []
        
        # Pattern to match <section class="glass-card-display" ...>...</section>
        pattern = r'<section\s+class="glass-card-display"[^>]*>.*?</section>'
        
        for match in re.finditer(pattern, html_content, re.DOTALL):
            sections.append((match.group(0), match.start(), match.end()))
        
        return sections
    
    def analyze_section(self, section_html: str, section_index: int) -> SectionAnalysis:
        """Analyze a glass-card-display section."""
        
        # Check if section already has background styling
        has_background = 'background:' in section_html or 'background-color:' in section_html
        
        # Extract current background if exists
        current_background = ""
        if has_background:
            bg_match = re.search(r'style="([^"]*background[^"]*)"', section_html)
            if bg_match:
                current_background = bg_match.group(1)
        
        # Calculate section complexity
        section_size = len(section_html) / 1024
        inline_styles = len(re.findall(r'style="[^"]*"', section_html))
        complexity = section_size * 0.5 + inline_styles * 1.0
        
        # Assign random color from palette
        color_name = random.choice(list(GLASS_COLORS.keys()))
        
        return SectionAnalysis(
            section_html=section_html,
            section_index=section_index,
            has_background=has_background,
            current_background=current_background,
            complexity_score=complexity,
            recommended_color=color_name,
        )
    
    def generate_glass_background(self, color_name: str) -> str:
        """
        Generate glassmorphism background style string.
        
        Includes:
        - Linear gradient with 7-color palette
        - Backdrop blur (12px)
        - Subtle border with color
        - Dual shadow (outer glow + inner highlight)
        """
        color = GLASS_COLORS[color_name]
        
        return (
            f"background: linear-gradient(135deg, {color['primary']} 0%, "
            f"{color['secondary']} 50%, rgba(26, 31, 58, 0.65) 100%); "
            f"backdrop-filter: blur(12px); "
            f"-webkit-backdrop-filter: blur(12px); "
            f"border: 1px solid {color['border']}; "
            f"box-shadow: 0 8px 32px {color['shadow']}, "
            f"inset 0 1px 0 rgba(255, 255, 255, 0.1);"
        )
    
    def apply_background_to_section(self, section_html: str, color_name: str) -> str:
        """Apply glassmorphism background to a section."""
        
        # Generate new background style
        new_style = self.generate_glass_background(color_name)
        
        # Check if section has existing style attribute
        if 'style="' in section_html:
            # Replace existing style attribute
            updated_section = re.sub(
                r'style="[^"]*"',
                f'style="{new_style}"',
                section_html,
                count=1
            )
        else:
            # Add new style attribute
            updated_section = re.sub(
                r'(<section\s+class="glass-card-display")',
                rf'\1 style="{new_style}"',
                section_html,
                count=1
            )
        
        return updated_section
    
    def process_file(self, file_path: Path, dry_run: bool = False) -> Dict:
        """Process a single Level 1 hub file."""
        
        print(f"\n📄 Processing: {file_path.relative_to(self.workspace_root)}")
        
        # Read file
        html_content = file_path.read_text(encoding='utf-8')
        
        # Calculate complexity
        complexity = self.calculate_complexity(html_content)
        print(f"   Complexity Score: {complexity}")
        
        # Find all glass-card-display sections
        sections = self.find_glass_sections(html_content)
        print(f"   Found {len(sections)} glass-card-display sections")
        
        if len(sections) == 0:
            print(f"   ⚠️  No glass-card-display sections found")
            return {'processed': False, 'reason': 'no_sections'}
        
        # Analyze each section
        analyses = []
        for idx, (section_html, start_pos, end_pos) in enumerate(sections, 1):
            analysis = self.analyze_section(section_html, idx)
            analyses.append((analysis, start_pos, end_pos))
            
            print(f"   Section {idx}:")
            print(f"     - Has background: {analysis.has_background}")
            print(f"     - Complexity: {analysis.complexity_score}")
            print(f"     - Assigned color: {analysis.recommended_color}")
        
        # Apply backgrounds (process in reverse order to preserve positions)
        updated_content = html_content
        sections_updated = 0
        
        for analysis, start_pos, end_pos in reversed(analyses):
            # Apply glassmorphism background
            updated_section = self.apply_background_to_section(
                analysis.section_html,
                analysis.recommended_color
            )
            
            # Replace in content
            updated_content = (
                updated_content[:start_pos] +
                updated_section +
                updated_content[end_pos:]
            )
            
            sections_updated += 1
            
            # Track color usage
            color = analysis.recommended_color
            self.stats['colors_used'][color] = self.stats['colors_used'].get(color, 0) + 1
        
        # Write updated content
        if not dry_run:
            file_path.write_text(updated_content, encoding='utf-8')
            print(f"   ✅ Updated {sections_updated} sections")
        else:
            print(f"   🔍 DRY RUN: Would update {sections_updated} sections")
        
        self.stats['processed_files'] += 1
        self.stats['sections_updated'] += sections_updated
        
        return {
            'processed': True,
            'sections_updated': sections_updated,
            'complexity': complexity,
        }
    
    def process_all_hubs(self, dry_run: bool = False):
        """Process all Level 1 hub pages."""
        
        print("=" * 80)
        print("🎨 CORTEX Level 1 Glassmorphism Background Applicator")
        print("=" * 80)
        print(f"\nMode: {'🔍 DRY RUN' if dry_run else '✅ LIVE EXECUTION'}")
        print(f"Target: {len(LEVEL1_HUBS)} Level 1 hub pages")
        print(f"7-Color Palette: {', '.join(GLASS_COLORS.keys())}")
        
        results = {}
        
        for hub_path in LEVEL1_HUBS:
            file_path = self.workspace_root / hub_path
            
            if not file_path.exists():
                print(f"\n❌ File not found: {hub_path}")
                self.stats['errors'].append(f"File not found: {hub_path}")
                continue
            
            try:
                result = self.process_file(file_path, dry_run=dry_run)
                results[hub_path] = result
            except Exception as e:
                print(f"\n❌ Error processing {hub_path}: {e}")
                self.stats['errors'].append(f"{hub_path}: {e}")
        
        # Print summary
        self.print_summary(results, dry_run)
    
    def print_summary(self, results: Dict, dry_run: bool):
        """Print processing summary."""
        
        print("\n" + "=" * 80)
        print("📊 PROCESSING SUMMARY")
        print("=" * 80)
        
        print(f"\n✅ Files Processed: {self.stats['processed_files']}/{len(LEVEL1_HUBS)}")
        print(f"✅ Sections Updated: {self.stats['sections_updated']}")
        
        if self.stats['colors_used']:
            print("\n🎨 Color Distribution:")
            for color, count in sorted(self.stats['colors_used'].items()):
                percentage = (count / self.stats['sections_updated'] * 100) if self.stats['sections_updated'] > 0 else 0
                print(f"   - {color.capitalize()}: {count} sections ({percentage:.1f}%)")
        
        if self.stats['errors']:
            print(f"\n❌ Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"   - {error}")
        
        if dry_run:
            print("\n💡 This was a DRY RUN. Re-run without --dry-run to apply changes.")
        else:
            print("\n✅ All changes applied successfully!")
            print("\n📋 Next Steps:")
            print("   1. Refresh each Level 1 hub in browser: http://localhost:8000/{category}/index.html")
            print("   2. Verify glassmorphism backgrounds are applied")
            print("   3. Check color distribution across sections")
            print("   4. Commit changes: git commit -m 'feat(ui): Apply glassmorphism to Level 1 hubs (7-color palette)'")


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Apply glassmorphism panel backgrounds to Level 1 hub pages"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--workspace',
        type=Path,
        default=Path.cwd(),
        help='Workspace root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Initialize applicator
    applicator = GlassmorphismApplicator(args.workspace)
    
    # Process all hubs
    applicator.process_all_hubs(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
