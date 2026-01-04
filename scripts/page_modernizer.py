"""
CORTEX Page Modernization Script
Converts existing HTML pages to modern tab-based layout with improved readability

Author: Asif Hussain
Version: 1.0.0
Date: January 4, 2026
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class PageModernizer:
    """Converts legacy HTML pages to modern tab-based layouts"""
    
    def __init__(self, backup_dir: str = "backups/page-modernization"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # CSS/JS files to inject
        self.required_css = [
            '<link rel="stylesheet" href="../assets/css/modern-tabs.css">'
        ]
        self.required_js = [
            '<script src="../assets/js/modern-tabs.js"></script>'
        ]
    
    def backup_file(self, filepath: Path) -> Path:
        """Create timestamped backup of file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{filepath.stem}_{timestamp}{filepath.suffix}"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    def inject_dependencies(self, html_content: str) -> str:
        """Inject required CSS and JS files"""
        
        # Check if already injected
        if 'modern-tabs.css' in html_content:
            print("⚠️  modern-tabs.css already present, skipping injection")
            return html_content
        
        # Inject CSS before </head>
        css_injection = '\n    ' + '\n    '.join(self.required_css) + '\n'
        html_content = html_content.replace('</head>', css_injection + '</head>')
        
        # Inject JS before </body>
        js_injection = '\n    ' + '\n    '.join(self.required_js) + '\n'
        html_content = html_content.replace('</body>', js_injection + '</body>')
        
        print("✅ Dependencies injected: modern-tabs.css, modern-tabs.js")
        return html_content
    
    def convert_descriptions_to_blocks(self, html_content: str) -> str:
        """Convert <p class="description"> to <div class="description-block">"""
        
        # Pattern: <p class="description">...</p>
        pattern = r'<p\s+class=["\']description["\']>(.*?)</p>'
        
        def replace_func(match):
            content = match.group(1)
            return f'<div class="description-block">{content}</div>'
        
        new_content = re.sub(pattern, replace_func, html_content, flags=re.DOTALL)
        
        # Count replacements
        count = len(re.findall(pattern, html_content, flags=re.DOTALL))
        if count > 0:
            print(f"✅ Converted {count} description paragraphs to blocks")
        
        return new_content
    
    def convert_tables_to_metric_cards(self, html_content: str) -> str:
        """Convert simple tables to metric cards (manual intervention recommended)"""
        
        # This is a complex transformation - we'll add a comment for manual review
        table_pattern = r'<table[^>]*>(.*?)</table>'
        tables = re.findall(table_pattern, html_content, flags=re.DOTALL)
        
        if tables:
            print(f"⚠️  Found {len(tables)} table(s) - manual conversion to metric cards recommended")
            print("    Use .metric-cards-grid for visual data presentation")
        
        return html_content
    
    def convert_lists_to_visual_data(self, html_content: str) -> str:
        """Convert simple lists to visual-data-list (manual intervention recommended)"""
        
        # Detect unordered lists with icons
        icon_list_pattern = r'<ul[^>]*>.*?<i class=["\']fa[s|r|b][^"\']*["\'].*?</ul>'
        icon_lists = re.findall(icon_list_pattern, html_content, flags=re.DOTALL)
        
        if icon_lists:
            print(f"⚠️  Found {len(icon_lists)} icon list(s) - consider converting to .visual-data-list")
            print("    Example: .visual-data-item with .visual-data-icon + .visual-data-content")
        
        return html_content
    
    def wrap_in_tabs(self, html_content: str, sections: List[Dict[str, str]]) -> str:
        """
        Wrap content sections in tab system
        
        sections: [
            {"title": "Overview", "icon": "fa-info-circle", "content": "..."},
            {"title": "Metrics", "icon": "fa-chart-line", "content": "..."},
        ]
        """
        
        # Generate tab navigation
        tab_nav = '<nav class="tab-nav">\n'
        for i, section in enumerate(sections):
            active = ' active' if i == 0 else ''
            icon = section.get('icon', 'fa-file')
            tab_nav += f'    <button class="tab-button{active}">\n'
            tab_nav += f'        <i class="fas {icon}"></i>\n'
            tab_nav += f'        {section["title"]}\n'
            tab_nav += '    </button>\n'
        tab_nav += '</nav>\n\n'
        
        # Generate tab panels
        tab_panels = '<div class="tab-content-wrapper">\n'
        for i, section in enumerate(sections):
            active = ' active' if i == 0 else ''
            tab_panels += f'    <div class="tab-panel{active}">\n'
            tab_panels += f'        <h2 style="color: #00d4ff; margin-bottom: 1.5rem; font-size: clamp(1.5rem, 4cqi, 2rem);">\n'
            tab_panels += f'            <i class="fas {section.get("icon", "fa-file")}"></i>\n'
            tab_panels += f'            {section["title"]}\n'
            tab_panels += '        </h2>\n\n'
            tab_panels += section['content']
            tab_panels += '\n    </div>\n\n'
        tab_panels += '</div>\n'
        
        # Wrap in tab container
        tab_container = f'<div id="main-content-tabs" class="tab-container">\n{tab_nav}{tab_panels}</div>'
        
        print(f"✅ Created tab system with {len(sections)} tabs")
        return tab_container
    
    def analyze_page(self, filepath: Path) -> Dict[str, any]:
        """Analyze page structure and suggest improvements"""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'filepath': str(filepath),
            'has_modern_tabs': 'modern-tabs.css' in content,
            'description_paragraphs': len(re.findall(r'<p\s+class=["\']description["\']>', content)),
            'tables': len(re.findall(r'<table', content)),
            'icon_lists': len(re.findall(r'<ul[^>]*>.*?<i class=["\']fa', content, flags=re.DOTALL)),
            'h2_sections': len(re.findall(r'<h2[^>]*>', content)),
            'file_size_kb': filepath.stat().st_size / 1024,
        }
        
        return analysis
    
    def modernize_page(self, filepath: Path, auto_backup: bool = True) -> None:
        """
        Modernize a single page
        
        Steps:
        1. Backup original
        2. Inject dependencies
        3. Convert descriptions
        4. Identify tables/lists for manual conversion
        5. Save modernized version
        """
        
        print(f"\n{'='*60}")
        print(f"Modernizing: {filepath.name}")
        print(f"{'='*60}")
        
        # Analyze first
        analysis = self.analyze_page(filepath)
        print(f"\n📊 Analysis:")
        print(f"   - Description paragraphs: {analysis['description_paragraphs']}")
        print(f"   - Tables: {analysis['tables']}")
        print(f"   - Icon lists: {analysis['icon_lists']}")
        print(f"   - H2 sections: {analysis['h2_sections']}")
        print(f"   - File size: {analysis['file_size_kb']:.1f} KB")
        
        if analysis['has_modern_tabs']:
            print("✅ Page already uses modern tabs")
            return
        
        # Backup
        if auto_backup:
            self.backup_file(filepath)
        
        # Load content
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Apply transformations
        print(f"\n🔧 Applying transformations:")
        html_content = self.inject_dependencies(html_content)
        html_content = self.convert_descriptions_to_blocks(html_content)
        html_content = self.convert_tables_to_metric_cards(html_content)
        html_content = self.convert_lists_to_visual_data(html_content)
        
        # Save modernized version
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ Page modernized: {filepath}")
        print(f"📝 Manual steps:")
        print(f"   1. Review table→metric-cards conversions")
        print(f"   2. Review list→visual-data-list conversions")
        print(f"   3. Consider wrapping sections in tabs (if ≥3 H2 sections)")
        print(f"   4. Test on mobile/tablet/desktop")
    
    def batch_modernize(self, directory: Path, pattern: str = "*.html") -> None:
        """Modernize all HTML files in directory"""
        
        files = list(directory.glob(pattern))
        print(f"\n🔍 Found {len(files)} files matching '{pattern}'")
        
        for filepath in files:
            try:
                self.modernize_page(filepath)
            except Exception as e:
                print(f"❌ Error processing {filepath.name}: {e}")


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Modernize CORTEX HTML pages")
    parser.add_argument('--file', type=str, help='Single file to modernize')
    parser.add_argument('--directory', type=str, help='Directory to batch process')
    parser.add_argument('--analyze-only', action='store_true', help='Analyze without modifying')
    
    args = parser.parse_args()
    
    modernizer = PageModernizer()
    
    if args.file:
        filepath = Path(args.file)
        if args.analyze_only:
            analysis = modernizer.analyze_page(filepath)
            print(f"\n📊 Analysis for {filepath.name}:")
            for key, value in analysis.items():
                print(f"   {key}: {value}")
        else:
            modernizer.modernize_page(filepath)
    
    elif args.directory:
        directory = Path(args.directory)
        if args.analyze_only:
            files = list(directory.glob("*.html"))
            print(f"\n📊 Batch Analysis ({len(files)} files):")
            for filepath in files:
                analysis = modernizer.analyze_page(filepath)
                print(f"\n{filepath.name}:")
                print(f"   Descriptions: {analysis['description_paragraphs']}")
                print(f"   Tables: {analysis['tables']}")
                print(f"   Sections: {analysis['h2_sections']}")
        else:
            modernizer.batch_modernize(directory)
    
    else:
        print("Usage:")
        print("  python page_modernizer.py --file path/to/file.html")
        print("  python page_modernizer.py --directory path/to/docs/")
        print("  python page_modernizer.py --file path/to/file.html --analyze-only")


if __name__ == "__main__":
    main()
