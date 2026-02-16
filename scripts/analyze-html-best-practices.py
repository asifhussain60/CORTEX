"""
CORTEX HTML Refactoring Analysis
Analyzes index.html against CORTEX UI/UX best practices
"""

from pathlib import Path
import re
from typing import Dict, List, Tuple

def analyze_html_file(html_path: Path) -> Dict[str, any]:
    """Analyze HTML file for best practice compliance."""
    
    content = html_path.read_text(encoding='utf-8')
    
    analysis = {
        'file_size': len(content),
        'file_size_kb': round(len(content) / 1024, 2),
        
        # Performance metrics
        'css_links': len(re.findall(r'<link[^>]+rel=["\']stylesheet["\']', content)),
        'external_scripts': len(re.findall(r'<script[^>]+src=["\']http', content)),
        'inline_scripts': len(re.findall(r'<script[^>]*>[^<]+</script>', content, re.DOTALL)),
        'inline_styles_tags': len(re.findall(r'<style[^>]*>', content)),
        
        # Accessibility metrics
        'aria_attributes': len(re.findall(r'aria-', content)),
        'role_attributes': len(re.findall(r'role=', content)),
        'alt_texts': len(re.findall(r'alt=', content)),
        'lang_attribute': 'lang=' in content[:500],
        
        # SEO metrics
        'meta_tags': len(re.findall(r'<meta[^>]+>', content)),
        'og_tags': len(re.findall(r'property=["\']og:', content)),
        'structured_data': '<script type="application/ld+json">' in content,
        
        # Semantic HTML
        'semantic_tags': {
            'header': len(re.findall(r'<header', content)),
            'nav': len(re.findall(r'<nav', content)),
            'main': len(re.findall(r'<main', content)),
            'article': len(re.findall(r'<article', content)),
            'section': len(re.findall(r'<section', content)),
            'footer': len(re.findall(r'<footer', content)),
        },
        
        # Mobile optimization
        'viewport_meta': 'name="viewport"' in content,
        'touch_action': 'touch-action' in content or 'inline-styles-cleanup.css' in content,
        'responsive_images': len(re.findall(r'srcset=', content)),
        
        # Security
        'csp_header': 'Content-Security-Policy' in content,
        'nonce_attributes': len(re.findall(r'nonce=', content)),
    }
    
    return analysis

def check_best_practices(analysis: Dict) -> List[Tuple[str, str, str]]:
    """Check analysis against CORTEX UI/UX best practices.
    
    Returns list of (severity, category, finding) tuples
    """
    findings = []
    
    # Performance checks (YAML: performance_optimization)
    if analysis['file_size_kb'] > 150:
        findings.append(('WARNING', 'Performance', 
                        f"HTML file is {analysis['file_size_kb']}KB (recommend <150KB)"))
    
    if analysis['css_links'] > 6:
        findings.append(('INFO', 'Performance', 
                        f"{analysis['css_links']} CSS files loaded (consider bundling)"))
    
    if analysis['inline_styles_tags'] > 3:
        findings.append(('WARNING', 'Performance', 
                        f"{analysis['inline_styles_tags']} inline <style> tags (extract to CSS files)"))
    
    # Accessibility checks (YAML: accessibility_guidelines)
    if analysis['aria_attributes'] < 10:
        findings.append(('WARNING', 'Accessibility', 
                        f"Only {analysis['aria_attributes']} ARIA attributes (add more for complex components)"))
    
    if not analysis['lang_attribute']:
        findings.append(('CRITICAL', 'Accessibility', 
                        "Missing lang= attribute on <html> tag"))
    
    # SEO checks (YAML: seo_optimization)
    if not analysis['structured_data']:
        findings.append(('WARNING', 'SEO', 
                        "Missing JSON-LD structured data"))
    
    if analysis['og_tags'] < 4:
        findings.append(('INFO', 'SEO', 
                        f"Only {analysis['og_tags']} Open Graph tags (add more for social sharing)"))
    
    # Semantic HTML checks (YAML: semantic_markup)
    semantic = analysis['semantic_tags']
    if semantic['header'] == 0:
        findings.append(('WARNING', 'Semantic HTML', 
                        "No <header> tag found"))
    if semantic['main'] == 0:
        findings.append(('CRITICAL', 'Semantic HTML', 
                        "No <main> tag found (WCAG requirement)"))
    if semantic['footer'] == 0:
        findings.append(('WARNING', 'Semantic HTML', 
                        "No <footer> tag found"))
    
    # Mobile optimization checks
    if not analysis['viewport_meta']:
        findings.append(('CRITICAL', 'Mobile', 
                        "Missing viewport meta tag"))
    
    if not analysis['touch_action']:
        findings.append(('INFO', 'Mobile', 
                        "No touch-action optimization found"))
    
    # Security checks
    if not analysis['csp_header']:
        findings.append(('CRITICAL', 'Security', 
                        "Missing Content-Security-Policy header"))
    
    return findings

def print_analysis_report(analysis: Dict, findings: List[Tuple[str, str, str]]):
    """Print formatted analysis report."""
    
    print("=" * 80)
    print("CORTEX HTML ANALYSIS REPORT")
    print("=" * 80)
    print()
    
    print(f"📊 FILE METRICS")
    print(f"  Size: {analysis['file_size']:,} bytes ({analysis['file_size_kb']} KB)")
    print(f"  CSS Links: {analysis['css_links']}")
    print(f"  External Scripts: {analysis['external_scripts']}")
    print(f"  Inline <style> Tags: {analysis['inline_styles_tags']}")
    print()
    
    print(f"♿ ACCESSIBILITY")
    print(f"  ARIA Attributes: {analysis['aria_attributes']}")
    print(f"  Role Attributes: {analysis['role_attributes']}")
    print(f"  Alt Texts: {analysis['alt_texts']}")
    print(f"  Lang Attribute: {'✅' if analysis['lang_attribute'] else '❌'}")
    print()
    
    print(f"🔍 SEO")
    print(f"  Meta Tags: {analysis['meta_tags']}")
    print(f"  Open Graph Tags: {analysis['og_tags']}")
    print(f"  Structured Data: {'✅' if analysis['structured_data'] else '❌'}")
    print()
    
    print(f"📱 SEMANTIC HTML")
    for tag, count in analysis['semantic_tags'].items():
        print(f"  <{tag}>: {count}")
    print()
    
    print(f"📱 MOBILE OPTIMIZATION")
    print(f"  Viewport Meta: {'✅' if analysis['viewport_meta'] else '❌'}")
    print(f"  Touch Action: {'✅' if analysis['touch_action'] else '❌'}")
    print(f"  Responsive Images: {analysis['responsive_images']}")
    print()
    
    print(f"🛡️ SECURITY")
    print(f"  CSP Header: {'✅' if analysis['csp_header'] else '❌'}")
    print(f"  Nonce Attributes: {analysis['nonce_attributes']}")
    print()
    
    print("=" * 80)
    print("BEST PRACTICE FINDINGS")
    print("=" * 80)
    print()
    
    if not findings:
        print("✅ No issues found! HTML follows CORTEX best practices.")
    else:
        # Group by severity
        critical = [f for f in findings if f[0] == 'CRITICAL']
        warnings = [f for f in findings if f[0] == 'WARNING']
        info = [f for f in findings if f[0] == 'INFO']
        
        if critical:
            print(f"🔴 CRITICAL ({len(critical)})")
            for _, category, finding in critical:
                print(f"  • [{category}] {finding}")
            print()
        
        if warnings:
            print(f"🟡 WARNINGS ({len(warnings)})")
            for _, category, finding in warnings:
                print(f"  • [{category}] {finding}")
            print()
        
        if info:
            print(f"🔵 INFO ({len(info)})")
            for _, category, finding in info:
                print(f"  • [{category}] {finding}")
            print()
        
        print(f"📋 TOTAL: {len(findings)} findings ({len(critical)} critical, {len(warnings)} warnings, {len(info)} info)")
    
    print()

if __name__ == "__main__":
    html_path = Path("d:/PROJECTS/CORTEX/cortex-docs/index.html")
    
    if not html_path.exists():
        print(f"❌ File not found: {html_path}")
        exit(1)
    
    print("Analyzing index.html against CORTEX UI/UX best practices...")
    print()
    
    analysis = analyze_html_file(html_path)
    findings = check_best_practices(analysis)
    print_analysis_report(analysis, findings)
