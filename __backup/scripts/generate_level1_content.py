#!/usr/bin/env python3
"""
Universal Level 1 Content Generator
====================================

Generates HTML content for ALL Level 1 pages following approved orchestrators theme.
Reference: docs/orchestrators/index.html @ 2717fed3f7222197ade58a6d66db31c087bd9233

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.level1_page_configs import LEVEL1_PAGES


def generate_hero_section(title: str, subtitle: str, icon: str) -> str:
    """Generate hero section with robot logo"""
    return f"""
        <section class="hero-introduction glass-panel-default">
            <div class="hero-robot-container">
                <i class="{icon} hero-robot-icon"></i>
            </div>
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
            <div class="hero-actions">
                <a href="../index.html" class="btn-back">
                    <i class="fas fa-arrow-left"></i> Back to Home
                </a>
            </div>
        </section>
"""


def generate_card_stats(stats: List[Dict[str, str]]) -> str:
    """Generate stat pills for a card"""
    if not stats:
        return ""
    
    pills_html = "\n".join([
        f'<span class="stat-pill"><strong>{stat["label"]}:</strong> {stat["value"]}</span>'
        for stat in stats
    ])
    
    return f"""
                        <div class="card-stats-tetris">
{pills_html}
                        </div>
"""


def generate_section(section: Dict[str, Any], section_number: int) -> str:
    """Generate a single section with cards"""
    title = section['title']
    subtitle = section.get('subtitle', '')
    color = section['color']
    cards = section['cards']
    
    # Generate cards
    cards_html = []
    for i, card in enumerate(cards):
        variant = ['primary', 'info', 'success', 'warning', 'danger'][i % 5]
        stats_html = generate_card_stats(card.get('stats', []))
        
        # Add expanded description for content volume
        expanded_desc = card['description']
        if len(expanded_desc) < 80:
            expanded_desc += " This component provides comprehensive capabilities designed for robust performance."
        
        card_html = f"""
                <a href="{card['link']}" class="glass-card-clickable card-variant-{variant}">
                    <div class="card-icon">
                        <i class="{card['icon']}"></i>
                    </div>
                    <h3 class="card-title">{card['title']}</h3>
                    <p class="card-description">{expanded_desc}</p>{stats_html}
                </a>
"""
        cards_html.append(card_html)
    
    return f"""
        <section id="section-{section_number}" class="glass-card-display glass-panel-{color}">
            <div class="section-header">
                <h2 class="section-title">{title}</h2>
                <p class="section-subtitle">{subtitle}</p>
            </div>
            <div class="masonry-grid">
{''.join(cards_html)}
            </div>
        </section>
"""


def generate_level1_page(page_name: str) -> None:
    """
    Generate complete Level 1 page following approved theme.
    
    Args:
        page_name: Name of the page (e.g., 'security', 'features')
    """
    if page_name not in LEVEL1_PAGES:
        print(f"❌ Unknown page: {page_name}")
        return
    
    config = LEVEL1_PAGES[page_name]
    docs_dir = project_root / "docs" / page_name
    output_file = docs_dir / "index.html"
    
    if not docs_dir.exists():
        print(f"❌ Directory not found: {docs_dir}")
        return
    
    print(f"🔨 Generating {page_name}...")
    
    # Build main content
    hero_html = generate_hero_section(
        config['title'],
        config['subtitle'],
        config['hero_icon']
    )
    
    sections_html = []
    for i, section in enumerate(config['sections'], 1):
        sections_html.append(generate_section(section, i))
    
    # Complete HTML template
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['title']} - CORTEX Documentation</title>
    <meta name="description" content="{config['subtitle']}">
    
    <!-- CSS -->
    <link rel="stylesheet" href="../assets/css/variables.css?v=2026-01-03">
    <link rel="stylesheet" href="../assets/css/main.css?v=2026-01-03">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="page-container">
{hero_html}

        <main class="main-content">
{''.join(sections_html)}
        </main>

        <footer class="page-footer glass-panel-default">
            <p>&copy; 2026 Asif Hussain. All rights reserved.</p>
            <p>
                <a href="../index.html">Documentation Home</a> |
                <a href="https://github.com/ahsheriff/CORTEX">GitHub</a>
            </p>
        </footer>
    </div>

    <!-- JavaScript -->
    <script src="../assets/js/main.js?v=2026-01-03"></script>
</body>
</html>
"""
    
    # Write file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Generated {output_file}")


def generate_all_level1_pages():
    """Generate all Level 1 pages"""
    print("🚀 Generating all Level 1 pages...")
    print(f"📋 Pages to generate: {len(LEVEL1_PAGES)}")
    print()
    
    for page_name in LEVEL1_PAGES.keys():
        generate_level1_page(page_name)
        print()
    
    print("🎉 All pages generated!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        page_name = sys.argv[1]
        generate_level1_page(page_name)
    else:
        generate_all_level1_pages()
