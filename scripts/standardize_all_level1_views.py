#!/usr/bin/env python3
"""
Comprehensive Level 1 View Standardization Script
==================================================

Aligns ALL Level 1 pages with approved orchestrators pattern.

Following cortex-docs.prompt.md v2.0 - Python-only HTML generation.

Key Fixes:
1. Hero structure: Add glass-header, hero-section-wrapper, robot logo image
2. Hero introduction: Change from glass-panel-default to glass-card-display
3. Section titles: Use icon + text format (not div wrapper)
4. Card structure: Use card-header-centered (not separate card-icon div)
5. Card stats: Use semantic classes (stat-primary, stat-info, etc.) not generic stat-pill
6. CSS imports: Remove version query strings
7. Add favicon link

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
Version: 2.0.0
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List

project_root = Path(__file__).parent.parent


def standardize_hero_section(soup: BeautifulSoup, page_config: Dict) -> bool:
    """
    Transform hero from simple format to approved orchestrators pattern.
    
    BEFORE (generated):
    <section class="hero-introduction glass-panel-default">
        <div class="hero-robot-container">
            <i class="fas fa-icon hero-robot-icon"></i>
        </div>
        <h1>Title</h1>
        ...
    </section>
    
    AFTER (approved pattern):
    <header class="glass-header">...</header>
    <main class="container" id="main-content">
        <div class="hero-section-wrapper">
            <div class="hero-robot-container">
                <a href="../index.html">
                    <img src="../assets/images/CORTEX-logo-200.png" class="hero-robot-head" />
                </a>
            </div>
            <div class="hero-divider-line"></div>
        </div>
        <section class="glass-card-display hero-introduction">
            <div class="card-header-centered">
                <i class="card-icon-primary fas fa-icon"></i>
                <h2>Title</h2>
            </div>
            <p class="hero-description">...</p>
            <div class="hero-stats">...</div>
        </section>
    """
    # Find existing hero
    hero = soup.find('section', class_='hero-introduction')
    if not hero:
        return False
    
    # Extract data
    title = hero.find(['h1', 'h2'])
    subtitle = hero.find(class_='hero-subtitle')
    icon_element = hero.find('i', class_='hero-robot-icon')
    
    if not title:
        return False
    
    # Get icon classes (remove hero-robot-icon)
    icon_classes = [c for c in icon_element['class'] if c != 'hero-robot-icon'] if icon_element else ['fas', 'fa-robot']
    
    # Remove old page-container if exists
    page_container = soup.find('div', class_='page-container')
    if page_container:
        page_container.unwrap()
    
    # Remove old hero
    old_main = hero.find_next('main')
    hero.decompose()
    if old_main:
        old_main.unwrap()
    
    # Create new structure
    body = soup.find('body')
    
    # 1. Add glass-header
    header = soup.new_tag('header', **{'class': 'glass-header'})
    header_content = soup.new_tag('div', **{'class': 'header-content'})
    header_nav = soup.new_tag('nav', **{'class': 'header-nav'})
    header_nav.append(soup.new_string('<!-- Robot logo appears in hero section below -->'))
    header_content.append(header_nav)
    header.append(header_content)
    body.insert(0, header)
    
    # 2. Create main container
    main = soup.new_tag('main', **{'class': 'container', 'id': 'main-content'})
    
    # 3. Hero section wrapper with robot logo
    hero_wrapper = soup.new_tag('div', **{'class': 'hero-section-wrapper'})
    
    robot_container = soup.new_tag('div', **{'class': 'hero-robot-container'})
    robot_link = soup.new_tag('a', href='../index.html', title='Back to Home')
    robot_img = soup.new_tag('img', src='../assets/images/CORTEX-logo-200.png', 
                             alt='CORTEX Robot', **{'class': 'hero-robot-head'})
    robot_link.append(robot_img)
    robot_container.append(robot_link)
    hero_wrapper.append(robot_container)
    
    divider = soup.new_tag('div', **{'class': 'hero-divider-line'})
    hero_wrapper.append(divider)
    
    main.append(hero_wrapper)
    
    # 4. Page Title Card (new hero-introduction)
    new_hero = soup.new_tag('section', **{'class': 'glass-card-display hero-introduction'})
    
    card_header = soup.new_tag('div', **{'class': 'card-header-centered'})
    icon = soup.new_tag('i', **{'class': ' '.join(['card-icon-primary'] + icon_classes)})
    card_header.append(icon)
    h2 = soup.new_tag('h2')
    h2.string = title.get_text().strip()
    card_header.append(h2)
    new_hero.append(card_header)
    
    if subtitle:
        desc = soup.new_tag('p', **{'class': 'hero-description'})
        desc.string = subtitle.get_text().strip()
        new_hero.append(desc)
    else:
        # Add default description
        desc = soup.new_tag('p', **{'class': 'hero-description'})
        desc.string = f"Comprehensive {title.get_text().strip().lower()} overview and features for CORTEX system."
        new_hero.append(desc)
    
    # Add hero-stats
    stats = soup.new_tag('div', **{'class': 'hero-stats'})
    stats.append(soup.new_tag('span', **{'class': 'stat-pill'}))
    stats.find('span').string = 'CORTEX v5.0'
    new_hero.append(stats)
    
    main.append(new_hero)
    
    # Insert main after header
    header.insert_after(main)
    
    return True


def standardize_section_titles(soup: BeautifulSoup) -> int:
    """
    Transform section titles from div wrapper to direct icon + text.
    
    BEFORE: <div class="section-header"><h2 class="section-title">Title</h2></div>
    AFTER: <h2 class="section-title"><i class="fas fa-icon"></i> Title</h2>
    """
    changes = 0
    
    for section in soup.find_all('section', class_='glass-card-display'):
        header_div = section.find('div', class_='section-header')
        if not header_div:
            continue
        
        title = header_div.find('h2', class_='section-title')
        subtitle = header_div.find('p', class_='section-subtitle')
        
        if title:
            # Create new h2 with icon
            new_h2 = soup.new_tag('h2', **{'class': 'section-title'})
            icon = soup.new_tag('i', **{'class': 'fas fa-layer-group'})
            new_h2.append(icon)
            new_h2.append(soup.new_string(' ' + title.get_text().strip()))
            
            # Replace header div with just h2
            header_div.replace_with(new_h2)
            
            # Remove subtitle (not in approved pattern)
            if subtitle:
                subtitle.decompose()
            
            changes += 1
    
    return changes


def standardize_card_structure(soup: BeautifulSoup) -> int:
    """
    Transform cards from separate icon div to card-header-centered.
    
    BEFORE:
    <a class="glass-card-clickable">
        <div class="card-icon"><i class="fas fa-icon"></i></div>
        <h3 class="card-title">Title</h3>
        ...
    </a>
    
    AFTER:
    <a class="glass-card-clickable">
        <div class="card-header-centered">
            <i class="card-icon-primary fas fa-icon"></i>
            <h3 class="card-title">Title</h3>
        </div>
        ...
    </a>
    """
    changes = 0
    
    for card in soup.find_all('a', class_='glass-card-clickable'):
        icon_div = card.find('div', class_='card-icon')
        if not icon_div:
            continue
        
        icon = icon_div.find('i')
        title = card.find('h3', class_='card-title')
        
        if icon and title:
            # Create card-header-centered
            header = soup.new_tag('div', **{'class': 'card-header-centered'})
            
            # Update icon class
            icon_classes = icon.get('class', [])
            # Add card-icon-primary based on card variant
            card_classes = card.get('class', [])
            if 'card-variant-primary' in card_classes:
                icon['class'] = ['card-icon-primary'] + [c for c in icon_classes if c.startswith('fa')]
            elif 'card-variant-info' in card_classes:
                icon['class'] = ['card-icon-info'] + [c for c in icon_classes if c.startswith('fa')]
            elif 'card-variant-warning' in card_classes:
                icon['class'] = ['card-icon-warning'] + [c for c in icon_classes if c.startswith('fa')]
            elif 'card-variant-success' in card_classes:
                icon['class'] = ['card-icon-success'] + [c for c in icon_classes if c.startswith('fa')]
            elif 'card-variant-danger' in card_classes:
                icon['class'] = ['card-icon-danger'] + [c for c in icon_classes if c.startswith('fa')]
            
            # Move elements into header
            header.append(icon.extract())
            header.append(title.extract())
            
            # Remove old icon div and insert header at top of card
            icon_div.decompose()
            card.insert(0, header)
            
            changes += 1
    
    return changes


def standardize_card_stats(soup: BeautifulSoup) -> int:
    """
    Transform stat pills to semantic classes.
    
    BEFORE: <span class="stat-pill"><strong>Label:</strong> Value</span>
    AFTER: <span class="stat-primary"><i class="fas fa-icon"></i> Value</span>
    """
    changes = 0
    
    for stats_div in soup.find_all('div', class_='card-stats-tetris'):
        # Add 'card-stats' class if missing
        if 'card-stats' not in stats_div.get('class', []):
            stats_div['class'] = ['card-stats', 'card-stats-tetris']
        
        pills = stats_div.find_all('span', class_='stat-pill')
        variant_cycle = ['stat-primary', 'stat-info', 'stat-success']
        
        for i, pill in enumerate(pills):
            # Change class to semantic variant
            pill['class'] = [variant_cycle[i % len(variant_cycle)]]
            
            # Simplify content (remove <strong> tags)
            text = pill.get_text()
            pill.clear()
            
            # Add icon
            icon = soup.new_tag('i', **{'class': 'fas fa-check-circle'})
            pill.append(icon)
            pill.append(soup.new_string(' ' + text))
            
            changes += 1
    
    return changes


def fix_css_imports(soup: BeautifulSoup) -> bool:
    """Remove version query strings from CSS imports."""
    changed = False
    
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href', '')
        if '?v=' in href:
            link['href'] = href.split('?')[0]
            changed = True
    
    return changed


def add_favicon(soup: BeautifulSoup) -> bool:
    """Add favicon if missing."""
    head = soup.find('head')
    if not head:
        return False
    
    # Check if favicon exists
    if head.find('link', rel='icon'):
        return False
    
    # Add after title
    title = head.find('title')
    favicon = soup.new_tag('link', rel='icon', type='image/png', 
                          href='../assets/images/CORTEX-logo-64.png')
    
    if title:
        title.insert_after(favicon)
    else:
        head.insert(0, favicon)
    
    return True


def standardize_level1_page(page_path: Path) -> Dict:
    """Apply all standardizations to a single page."""
    print(f"\n🔧 Standardizing: {page_path.name}")
    
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    results = {
        'file': str(page_path),
        'changes': []
    }
    
    # Get page config (icon for hero)
    page_name = page_path.parent.name
    page_config = {'icon': 'fa-robot', 'title': page_name.title()}
    
    # Apply fixes
    if standardize_hero_section(soup, page_config):
        results['changes'].append('✓ Hero section restructured')
    
    section_changes = standardize_section_titles(soup)
    if section_changes:
        results['changes'].append(f'✓ {section_changes} section titles fixed')
    
    card_changes = standardize_card_structure(soup)
    if card_changes:
        results['changes'].append(f'✓ {card_changes} cards restructured')
    
    stats_changes = standardize_card_stats(soup)
    if stats_changes:
        results['changes'].append(f'✓ {stats_changes} stat pills updated')
    
    if fix_css_imports(soup):
        results['changes'].append('✓ CSS imports cleaned')
    
    if add_favicon(soup):
        results['changes'].append('✓ Favicon added')
    
    # Save if changes made
    if results['changes']:
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"✅ Applied {len(results['changes'])} fixes")
        for change in results['changes']:
            print(f"   {change}")
    else:
        print("  ℹ️  No changes needed")
    
    return results


def process_all_level1_pages():
    """Process all Level 1 pages."""
    docs_dir = project_root / "docs"
    
    level1_pages = [
        'architecture',
        'security',
        'features',
        'story',
        'sts',
        'getting-started',
        'knowledge',
        'learning-paths',
        'lens',
        'token-optimization',
        'toolkit-manager'
    ]
    
    print("🚀 Comprehensive Level 1 View Standardization")
    print(f"📋 Pages to process: {len(level1_pages)}")
    print(f"📐 Reference: docs/orchestrators/index.html (approved pattern)")
    
    results = []
    for page_name in level1_pages:
        page_path = docs_dir / page_name / "index.html"
        
        if not page_path.exists():
            print(f"⚠️  Skipping {page_name}: File not found")
            continue
        
        result = standardize_level1_page(page_path)
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("📊 Standardization Summary")
    print("="*70)
    
    total_changes = sum(len(r['changes']) for r in results)
    updated_files = sum(1 for r in results if r['changes'])
    
    print(f"✅ Files processed: {len(results)}")
    print(f"✅ Files updated: {updated_files}")
    print(f"✅ Total changes: {total_changes}")
    
    if total_changes > 0:
        print(f"\n🎉 All Level 1 views now match orchestrators pattern!")
    else:
        print("\n✅ All pages already standardized!")


if __name__ == "__main__":
    process_all_level1_pages()
