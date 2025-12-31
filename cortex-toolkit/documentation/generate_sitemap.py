#!/usr/bin/env python3
"""
CORTEX Documentation Sitemap Generator
Generates a comprehensive, glassmorphism-styled sitemap for docs/index.html

Author: Asif Hussain
Version: 1.0.0
Standards: glassmorphism-design-standards-v2.md
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class SitemapGenerator:
    """Generate sitemap HTML with glassmorphism styling"""
    
    def __init__(self, docs_root: str):
        self.docs_root = Path(docs_root)
        self.sitemap_data: List[Dict[str, Any]] = []
        
    def scan_documentation(self) -> List[Dict[str, Any]]:
        """Scan docs directory and build sitemap structure"""
        sitemap = []
        
        # Define main sections with icons (FontAwesome)
        sections = {
            'features': {
                'title': 'Features',
                'icon': 'fa-star',
                'description': 'Core capabilities and features'
            },
            'orchestrators': {
                'title': 'Orchestrators',
                'icon': 'fa-network-wired',
                'description': '8 intelligent workflow orchestrators'
            },
            'governance': {
                'title': 'Governance',
                'icon': 'fa-shield-alt',
                'description': 'SKULL rules and brain protection'
            },
            'knowledge': {
                'title': 'Knowledge Library',
                'icon': 'fa-book-open',
                'description': 'Technical knowledge and patterns'
            },
            'sts': {
                'title': 'Sharpen The Saw',
                'icon': 'fa-tools',
                'description': 'Security and quality practices'
            },
            'story': {
                'title': 'The Awakening',
                'icon': 'fa-book-reader',
                'description': 'CORTEX origin story'
            },
            'future': {
                'title': '4.0 Vision',
                'icon': 'fa-rocket',
                'description': 'Future roadmap and plans'
            }
        }
        
        # Scan each section
        for section_key, section_info in sections.items():
            section_path = self.docs_root / section_key
            
            if not section_path.exists():
                continue
                
            pages = []
            
            # Scan for HTML files in section
            for html_file in section_path.glob('*.html'):
                if html_file.name == 'index.html':
                    continue
                    
                page_info = self._extract_page_info(html_file)
                if page_info:
                    pages.append(page_info)
            
            # Add index page
            index_file = section_path / 'index.html'
            if index_file.exists():
                index_info = self._extract_page_info(index_file)
                if index_info:
                    pages.insert(0, index_info)
            
            if pages:
                sitemap.append({
                    'section': section_info['title'],
                    'icon': section_info['icon'],
                    'description': section_info['description'],
                    'path': section_key,
                    'pages': pages
                })
        
        return sitemap
    
    def _extract_page_info(self, html_file: Path) -> Dict[str, Any]:
        """Extract title and metadata from HTML file"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title
            title = 'Untitled'
            if '<title>' in content:
                start = content.find('<title>') + 7
                end = content.find('</title>', start)
                if end > start:
                    title = content[start:end].strip()
                    # Clean up common patterns
                    title = title.replace('CORTEX - ', '')
                    title = title.replace(' - CORTEX', '')
            
            # Extract description from meta tag
            description = ''
            if 'meta name="description"' in content:
                start = content.find('meta name="description"')
                content_start = content.find('content="', start) + 9
                content_end = content.find('"', content_start)
                if content_end > content_start:
                    description = content[content_start:content_end].strip()
            
            relative_path = html_file.relative_to(self.docs_root)
            
            return {
                'title': title,
                'description': description,
                'url': str(relative_path).replace('\\', '/'),
                'filename': html_file.name
            }
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
            return None
    
    def generate_html(self, sitemap_data: List[Dict[str, Any]]) -> str:
        """Generate glassmorphism-styled sitemap HTML"""
        
        html_sections = []
        
        for section in sitemap_data:
            pages_html = []
            
            for page in section['pages']:
                page_desc = f'<p class="sitemap-page-desc">{page["description"]}</p>' if page['description'] else ''
                
                pages_html.append(f'''
                    <a href="{page['url']}" class="sitemap-page-link">
                        <div class="sitemap-page-icon">
                            <i class="fas fa-file-alt"></i>
                        </div>
                        <div class="sitemap-page-info">
                            <h4 class="sitemap-page-title">{page['title']}</h4>
                            {page_desc}
                        </div>
                        <div class="sitemap-page-arrow">
                            <i class="fas fa-chevron-right"></i>
                        </div>
                    </a>
                ''')
            
            section_html = f'''
            <div class="sitemap-section">
                <div class="sitemap-section-header">
                    <div class="sitemap-section-icon">
                        <i class="fas {section['icon']}"></i>
                    </div>
                    <div class="sitemap-section-info">
                        <h3 class="sitemap-section-title">{section['section']}</h3>
                        <p class="sitemap-section-desc">{section['description']}</p>
                    </div>
                </div>
                <div class="sitemap-pages">
                    {''.join(pages_html)}
                </div>
            </div>
            '''
            
            html_sections.append(section_html)
        
        # Full HTML with glassmorphism styling
        full_html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Complete CORTEX Documentation Sitemap - Navigate all features, orchestrators, and knowledge resources">
    <title>Sitemap - CORTEX Documentation</title>
    <link rel="icon" type="image/png" href="assets/images/CORTEX-logo-64.png">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="assets/css/main.css">
    <style>
        /* Sitemap Glassmorphism Styles */
        .sitemap-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .sitemap-header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        
        .sitemap-header h1 {{
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
        }}
        
        .sitemap-header p {{
            font-size: 1.25rem;
            color: var(--text-secondary);
        }}
        
        .sitemap-grid {{
            display: grid;
            gap: 2rem;
        }}
        
        .sitemap-section {{
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: 2rem;
            box-shadow: var(--shadow);
            transition: all var(--transition-base);
        }}
        
        .sitemap-section:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: rgba(0, 212, 255, 0.3);
        }}
        
        .sitemap-section-header {{
            display: flex;
            align-items: flex-start;
            gap: 1.5rem;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .sitemap-section-icon {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.75rem;
            color: white;
            flex-shrink: 0;
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
        }}
        
        .sitemap-section-info {{
            flex: 1;
        }}
        
        .sitemap-section-title {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }}
        
        .sitemap-section-desc {{
            font-size: 1rem;
            color: var(--text-secondary);
            margin: 0;
        }}
        
        .sitemap-pages {{
            display: grid;
            gap: 1rem;
        }}
        
        .sitemap-page-link {{
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.25rem;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: var(--radius-md);
            text-decoration: none;
            color: inherit;
            transition: all var(--transition-base);
        }}
        
        .sitemap-page-link:hover {{
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--accent-primary);
            transform: translateX(8px);
        }}
        
        .sitemap-page-icon {{
            width: 40px;
            height: 40px;
            background: rgba(0, 212, 255, 0.1);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--accent-primary);
            font-size: 1.25rem;
            flex-shrink: 0;
        }}
        
        .sitemap-page-info {{
            flex: 1;
        }}
        
        .sitemap-page-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0 0 0.25rem 0;
        }}
        
        .sitemap-page-desc {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin: 0;
        }}
        
        .sitemap-page-arrow {{
            color: var(--text-muted);
            font-size: 1rem;
            opacity: 0;
            transform: translateX(-10px);
            transition: all var(--transition-base);
        }}
        
        .sitemap-page-link:hover .sitemap-page-arrow {{
            opacity: 1;
            transform: translateX(0);
        }}
        
        /* Back to top button */
        .back-to-top {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.25rem;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
            transition: all var(--transition-base);
            opacity: 0;
            visibility: hidden;
        }}
        
        .back-to-top.visible {{
            opacity: 1;
            visibility: visible;
        }}
        
        .back-to-top:hover {{
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(0, 212, 255, 0.6);
        }}
        
        /* Mobile Responsive */
        @media (max-width: 768px) {{
            .sitemap-container {{
                padding: 1rem;
            }}
            
            .sitemap-header h1 {{
                font-size: 2rem;
            }}
            
            .sitemap-header p {{
                font-size: 1rem;
            }}
            
            .sitemap-section {{
                padding: 1.5rem;
            }}
            
            .sitemap-section-header {{
                flex-direction: column;
                gap: 1rem;
            }}
            
            .sitemap-section-icon {{
                width: 50px;
                height: 50px;
                font-size: 1.5rem;
            }}
            
            .sitemap-section-title {{
                font-size: 1.5rem;
            }}
            
            .sitemap-page-link {{
                padding: 0.875rem 1rem;
            }}
            
            .sitemap-page-icon {{
                width: 36px;
                height: 36px;
                font-size: 1rem;
            }}
            
            .sitemap-page-title {{
                font-size: 1rem;
            }}
        }}
        
        @media (max-width: 480px) {{
            .sitemap-header h1 {{
                font-size: 1.75rem;
            }}
            
            .sitemap-section {{
                padding: 1.25rem;
            }}
            
            .sitemap-section-title {{
                font-size: 1.25rem;
            }}
            
            .sitemap-page-desc {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="main-nav">
        <div class="nav-content">
            <a href="index.html" class="logo-link">
                <img src="assets/images/CORTEX-logo-128.png" alt="CORTEX Logo" class="nav-logo">
                <span class="logo-text">CORTEX</span>
            </a>
            <div class="nav-links">
                <a href="index.html"><i class="fas fa-home"></i> Home</a>
                <a href="sitemap.html" class="active"><i class="fas fa-sitemap"></i> Sitemap</a>
                <a href="https://github.com/asifhussain60/CORTEX" target="_blank" class="github-link">
                    <i class="fab fa-github"></i> GitHub
                </a>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main>
        <div class="sitemap-container">
            <div class="sitemap-header">
                <h1><i class="fas fa-sitemap"></i> Documentation Sitemap</h1>
                <p>Complete navigation guide to all CORTEX documentation resources</p>
            </div>
            
            <div class="sitemap-grid">
                {''.join(html_sections)}
            </div>
        </div>
    </main>

    <!-- Back to Top Button -->
    <button class="back-to-top" id="backToTop" aria-label="Back to top">
        <i class="fas fa-arrow-up"></i>
    </button>

    <script>
        // Back to top functionality
        const backToTop = document.getElementById('backToTop');
        
        window.addEventListener('scroll', () => {{
            if (window.pageYOffset > 300) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }});
        
        backToTop.addEventListener('click', () => {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }});
    </script>
</body>
</html>
'''
        
        return full_html
    
    def save_sitemap(self, output_file: str):
        """Generate and save sitemap to file"""
        print("🗺️  Scanning documentation structure...")
        sitemap_data = self.scan_documentation()
        
        print(f"📊 Found {len(sitemap_data)} sections with {sum(len(s['pages']) for s in sitemap_data)} total pages")
        
        print("🎨 Generating glassmorphism-styled sitemap...")
        html = self.generate_html(sitemap_data)
        
        output_path = Path(output_file)
        output_path.write_text(html, encoding='utf-8')
        
        print(f"✅ Sitemap generated: {output_path}")
        print(f"📏 Size: {len(html):,} bytes")
        
        # Generate summary
        print("\n📋 Sitemap Summary:")
        for section in sitemap_data:
            print(f"  • {section['section']}: {len(section['pages'])} pages")


def main():
    """Main entry point"""
    import sys
    
    # Determine docs root
    if len(sys.argv) > 1:
        docs_root = sys.argv[1]
    else:
        # Assume running from cortex-toolkit/documentation
        script_dir = Path(__file__).parent
        docs_root = script_dir.parent.parent / 'docs'
    
    output_file = Path(docs_root) / 'sitemap.html'
    
    print("=" * 60)
    print("🧠 CORTEX Documentation Sitemap Generator")
    print("=" * 60)
    print(f"📂 Docs Root: {docs_root}")
    print(f"📄 Output: {output_file}")
    print()
    
    generator = SitemapGenerator(docs_root)
    generator.save_sitemap(output_file)
    
    print()
    print("=" * 60)
    print("🎉 Sitemap generation complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
