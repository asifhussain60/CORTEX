#!/usr/bin/env python3
"""Analyze HTML validation errors to create repair taxonomy."""

import re
from pathlib import Path
from collections import defaultdict
from html.parser import HTMLParser

class DetailedHTMLValidator(HTMLParser):
    """Enhanced HTML parser that tracks detailed error patterns."""
    
    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.errors = []
        self.error_types = defaultdict(int)
        self.line_num = 1
        
    def handle_starttag(self, tag, attrs):
        self.tag_stack.append((tag, self.line_num))
        
    def handle_endtag(self, tag):
        if not self.tag_stack:
            self.errors.append(f"Line {self.line_num}: Orphaned closing tag </{tag}>")
            self.error_types['orphaned_closing'] += 1
        elif self.tag_stack[-1][0] != tag:
            expected = self.tag_stack[-1][0]
            self.errors.append(f"Line {self.line_num}: Expected </{expected}>, found </{tag}>")
            self.error_types['mismatched_closing'] += 1
        else:
            self.tag_stack.pop()
    
    def handle_data(self, data):
        self.line_num += data.count('\n')
    
    def get_unclosed_tags(self):
        return [(tag, line) for tag, line in self.tag_stack]

def analyze_file(file_path: Path) -> dict:
    """Analyze a single HTML file for error patterns."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validator = DetailedHTMLValidator()
        validator.feed(content)
        
        unclosed = validator.get_unclosed_tags()
        
        # Check for specific patterns
        has_html_tag = '<html' in content
        has_closing_html = '</html>' in content
        has_body_tag = '<body' in content
        has_closing_body = '</body>' in content
        
        # Count orphaned standalone closing tags
        orphaned_pattern = re.compile(r'^\s*</(div|a|section|footer|header|ul|li)>\s*$', re.MULTILINE)
        orphaned_count = len(orphaned_pattern.findall(content))
        
        # Check for malformed emojis
        malformed_emojis = content.count('�')
        
        return {
            'file': file_path,
            'error_types': dict(validator.error_types),
            'unclosed_tags': len(unclosed),
            'unclosed_details': unclosed[:5],  # First 5
            'orphaned_standalone': orphaned_count,
            'malformed_emojis': malformed_emojis,
            'has_html_tag': has_html_tag,
            'has_closing_html': has_closing_html,
            'has_body_tag': has_body_tag,
            'has_closing_body': has_closing_body,
            'total_errors': len(validator.errors)
        }
    except Exception as e:
        return {'file': file_path, 'error': str(e)}

def main():
    """Analyze all HTML files and create taxonomy."""
    docs_dir = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
    
    print("🔍 Analyzing HTML Error Patterns...")
    print("=" * 60)
    
    # Collect all analyses
    analyses = []
    global_error_types = defaultdict(int)
    
    for html_file in sorted(docs_dir.rglob('*.html')):
        analysis = analyze_file(html_file)
        analyses.append(analysis)
        
        if 'error' not in analysis:
            for error_type, count in analysis['error_types'].items():
                global_error_types[error_type] += count
    
    # Generate taxonomy report
    print("\n📊 GLOBAL ERROR TAXONOMY")
    print("=" * 60)
    
    for error_type, count in sorted(global_error_types.items(), key=lambda x: -x[1]):
        print(f"  {error_type}: {count} occurrences")
    
    print("\n\n🏆 TOP 10 MOST BROKEN FILES")
    print("=" * 60)
    
    # Sort by total errors
    sorted_analyses = sorted(
        [a for a in analyses if 'error' not in a],
        key=lambda x: x['total_errors'],
        reverse=True
    )[:10]
    
    for i, analysis in enumerate(sorted_analyses, 1):
        rel_path = analysis['file'].relative_to(docs_dir)
        print(f"\n{i}. {rel_path}")
        print(f"   Total Errors: {analysis['total_errors']}")
        print(f"   Unclosed Tags: {analysis['unclosed_tags']}")
        print(f"   Orphaned Closing Tags: {analysis['orphaned_standalone']}")
        if analysis['malformed_emojis'] > 0:
            print(f"   Malformed Emojis: {analysis['malformed_emojis']}")
        if not analysis['has_closing_html']:
            print(f"   ⚠️  Missing </html>")
        if not analysis['has_closing_body']:
            print(f"   ⚠️  Missing </body>")
    
    print("\n\n📁 TIER BREAKDOWN")
    print("=" * 60)
    
    # Categorize by tier
    tier1 = ['index.html', 'features/index.html', 'architecture/index.html', 
             'technical/index.html', 'governance/skull-rulebook.html',
             'features/planning-system.html', 'features/tdd-mastery.html']
    
    tier1_files = [a for a in analyses if 'error' not in a 
                   and any(str(a['file']).endswith(t) for t in tier1)]
    tier1_errors = sum(a['total_errors'] for a in tier1_files)
    
    print(f"\nTier 1 (Critical Pages): {len(tier1_files)} files, {tier1_errors} errors")
    
    feature_files = [a for a in analyses if 'error' not in a 
                     and 'features/' in str(a['file']) 
                     and a not in tier1_files]
    feature_errors = sum(a['total_errors'] for a in feature_files)
    
    print(f"Tier 2 (Feature Pages): {len(feature_files)} files, {feature_errors} errors")
    
    tech_files = [a for a in analyses if 'error' not in a 
                  and ('technical/' in str(a['file']) or 'orchestration/' in str(a['file']))
                  and a not in tier1_files]
    tech_errors = sum(a['total_errors'] for a in tech_files)
    
    print(f"Tier 3 (Technical Pages): {len(tech_files)} files, {tech_errors} errors")
    
    other_files = [a for a in analyses if 'error' not in a 
                   and a not in tier1_files 
                   and a not in feature_files 
                   and a not in tech_files]
    other_errors = sum(a['total_errors'] for a in other_files)
    
    print(f"Tier 4 (Other Pages): {len(other_files)} files, {other_errors} errors")
    
    print("\n\n💡 REPAIR STRATEGY RECOMMENDATIONS")
    print("=" * 60)
    
    if global_error_types['orphaned_closing'] > 0:
        print("\n1. ORPHANED CLOSING TAGS (Primary Issue)")
        print("   Strategy: Pattern-match standalone closing tags and remove")
        print("   Pattern: ^\\s*</(div|a|section|footer|header)>\\s*$")
    
    unclosed_count = sum(1 for a in analyses if 'error' not in a and a['unclosed_tags'] > 0)
    if unclosed_count > 0:
        print(f"\n2. UNCLOSED TAGS ({unclosed_count} files affected)")
        print("   Strategy: Use BeautifulSoup with html.parser to auto-close")
        print("   Note: May need manual review for complex nesting")
    
    missing_html = sum(1 for a in analyses if 'error' not in a and not a['has_closing_html'])
    if missing_html > 0:
        print(f"\n3. MISSING </html> TAGS ({missing_html} files)")
        print("   Strategy: Append </html> after </body> if missing")
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete. Use insights to build repair script v2.")

if __name__ == '__main__':
    main()
