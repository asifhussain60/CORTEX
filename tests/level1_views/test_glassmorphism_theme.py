#!/usr/bin/env python3
"""
Level 1 Glassmorphism Theme Validation Tests
=============================================

TDD approach for validating Level 1 views against approved orchestrators theme.

Reference Commit: 2717fed3f7222197ade58a6d66db31c087bd9233
Approved Theme: docs/orchestrators/index.html

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Tuple


class TestGlassmorphismTheme:
    """Test suite for Level 1 glassmorphism theme compliance"""
    
    @pytest.fixture
    def workspace_root(self):
        """Get workspace root directory"""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture
    def approved_theme_html(self, workspace_root):
        """Load approved orchestrators theme as reference"""
        theme_path = workspace_root / "docs" / "orchestrators" / "index.html"
        with open(theme_path, 'r', encoding='utf-8') as f:
            return BeautifulSoup(f.read(), 'html.parser')
    
    @pytest.fixture
    def level1_pages(self, workspace_root):
        """Get all Level 1 pages to test"""
        docs_dir = workspace_root / "docs"
        pages = [
            'architecture',
            'features',
            'getting-started',
            'knowledge',
            'learning-paths',
            'lens',
            'security',
            'story',
            'sts',
            'token-optimization',
            'toolkit-manager'
        ]
        return {page: docs_dir / page / "index.html" for page in pages}
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 1: CSS Path Validation (CRITICAL)
    # ═══════════════════════════════════════════════════════════════
    
    def test_css_paths_are_correct(self, level1_pages):
        """FAIL: CSS paths must be ../assets/css/ not assets/css/"""
        errors = []
        
        for page_name, page_path in level1_pages.items():
            if not page_path.exists():
                errors.append(f"{page_name}: File not found")
                continue
                
            with open(page_path, 'r', encoding='utf-8') as f:
                content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
            
            # Check CSS links
            css_links = soup.find_all('link', rel='stylesheet')
            for link in css_links:
                href = link.get('href', '')
                if 'assets/css/' in href and not href.startswith('../'):
                    errors.append(f"{page_name}: Incorrect CSS path '{href}' (should start with ../)")
        
        assert not errors, f"CSS path errors found:\n" + "\n".join(errors)
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 2: Glass Panel Classes
    # ═══════════════════════════════════════════════════════════════
    
    def test_glass_panel_classes_present(self, level1_pages):
        """FAIL: Sections must have glass-panel-* color classes"""
        errors = []
        glass_colors = ['purple', 'emerald', 'amber', 'cyan', 'teal', 'indigo', 'pink']
        
        for page_name, page_path in level1_pages.items():
            if not page_path.exists():
                continue
                
            with open(page_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            sections = soup.find_all('section', class_='glass-card-display')
            if not sections:
                errors.append(f"{page_name}: No glass-card-display sections found")
                continue
            
            found_colors = []
            for section in sections:
                classes = section.get('class', [])
                for color in glass_colors:
                    if f'glass-panel-{color}' in classes:
                        found_colors.append(color)
                        break
            
            if not found_colors:
                errors.append(f"{page_name}: No glass-panel-* color classes found in sections")
        
        assert not errors, f"Glass panel errors:\n" + "\n".join(errors)
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 3: Clickable Cards with Variants
    # ═══════════════════════════════════════════════════════════════
    
    def test_clickable_cards_with_variants(self, level1_pages):
        """FAIL: Cards must use <a> tags with glass-card-clickable and card-variant-*"""
        errors = []
        card_variants = ['primary', 'info', 'success', 'warning', 'danger']
        
        for page_name, page_path in level1_pages.items():
            if not page_path.exists():
                continue
                
            with open(page_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Check for clickable cards
            clickable_cards = soup.find_all('a', class_='glass-card-clickable')
            if not clickable_cards:
                # Only flag as error if page has sections (not empty)
                sections = soup.find_all('section', class_='glass-card-display')
                if sections:
                    errors.append(f"{page_name}: No clickable cards (<a class='glass-card-clickable'>) found")
                continue
            
            # Verify card variants
            has_variants = False
            for card in clickable_cards:
                classes = card.get('class', [])
                for variant in card_variants:
                    if f'card-variant-{variant}' in classes:
                        has_variants = True
                        break
                if has_variants:
                    break
            
            if not has_variants:
                errors.append(f"{page_name}: No card-variant-* classes found on clickable cards")
        
        assert not errors, f"Clickable card errors:\n" + "\n".join(errors)
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 4: No Inline Styles (CRITICAL)
    # ═══════════════════════════════════════════════════════════════
    
    def test_no_inline_styles(self, level1_pages):
        """FAIL: No inline style attributes allowed (CSS-only architecture)"""
        errors = []
        
        for page_name, page_path in level1_pages.items():
            if not page_path.exists():
                continue
                
            with open(page_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Find all elements with style attribute
            inline_styles = soup.find_all(style=True)
            if inline_styles:
                # Exclude <style> tags themselves
                actual_inline = [el for el in inline_styles if el.name != 'style']
                if actual_inline:
                    errors.append(
                        f"{page_name}: Found {len(actual_inline)} inline style attributes "
                        f"(first: <{actual_inline[0].name}>)"
                    )
        
        assert not errors, f"Inline style errors:\n" + "\n".join(errors)
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 5: Hero Section Structure
    # ═══════════════════════════════════════════════════════════════
    
    def test_hero_section_structure(self, level1_pages):
        """FAIL: Must have hero section with robot logo or hero-introduction"""
        errors = []
        
        for page_name, page_path in level1_pages.items():
            if not page_path.exists():
                continue
                
            with open(page_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Check for hero elements
            has_hero_robot = soup.find('div', class_='hero-robot-container') is not None
            has_hero_intro = soup.find('section', class_='hero-introduction') is not None
            
            if not (has_hero_robot or has_hero_intro):
                errors.append(f"{page_name}: Missing hero section (no hero-robot-container or hero-introduction)")
        
        assert not errors, f"Hero section errors:\n" + "\n".join(errors)
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 6: Content Volume Validation
    # ═══════════════════════════════════════════════════════════════
    
    def test_sufficient_content_volume(self, level1_pages):
        """FAIL: Pages must have substantial content (not stubs)"""
        errors = []
        min_sections = 2  # At least 2 content sections
        min_text_length = 500  # At least 500 characters of text
        
        for page_name, page_path in level1_pages.items():
            if not page_path.exists():
                continue
                
            with open(page_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Check for stub indicators
            if soup.find(class_='stub-container'):
                errors.append(f"{page_name}: Page is a stub placeholder")
                continue
            
            # Count sections
            sections = soup.find_all('section', class_='glass-card-display')
            if len(sections) < min_sections:
                errors.append(f"{page_name}: Insufficient sections ({len(sections)} < {min_sections})")
            
            # Check text volume
            main_content = soup.find('main')
            if main_content:
                text = main_content.get_text(strip=True)
                if len(text) < min_text_length:
                    errors.append(f"{page_name}: Insufficient text content ({len(text)} < {min_text_length} chars)")
        
        assert not errors, f"Content volume errors:\n" + "\n".join(errors)
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 7: Card Stats Tetris (Stat Pills)
    # ═══════════════════════════════════════════════════════════════
    
    def test_card_stats_tetris_present(self, level1_pages):
        """PASS: Cards should have stat pills for metrics"""
        warnings = []
        
        for page_name, page_path in level1_pages.items():
            if not page_path.exists():
                continue
                
            with open(page_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            clickable_cards = soup.find_all('a', class_='glass-card-clickable')
            if clickable_cards:
                has_stats = False
                for card in clickable_cards:
                    if card.find(class_='card-stats-tetris'):
                        has_stats = True
                        break
                
                if not has_stats:
                    warnings.append(f"{page_name}: No card-stats-tetris found (stat pills recommended)")
        
        # This is a warning, not a failure
        if warnings:
            pytest.skip(f"Stat pill warnings:\n" + "\n".join(warnings))
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 8: Theme Consistency with Approved Pattern
    # ═══════════════════════════════════════════════════════════════
    
    def test_theme_consistency(self, level1_pages, approved_theme_html):
        """FAIL: Pages must follow approved orchestrators theme structure"""
        errors = []
        
        # Extract approved patterns
        approved_sections = approved_theme_html.find_all('section', class_='glass-card-display')
        approved_has_masonry = any(s.find(class_='masonry-grid') for s in approved_sections)
        approved_has_section_title = any(s.find(class_='section-title') for s in approved_sections)
        
        for page_name, page_path in level1_pages.items():
            if not page_path.exists():
                continue
                
            with open(page_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            sections = soup.find_all('section', class_='glass-card-display')
            if not sections:
                continue
            
            # Check for masonry grid (approved pattern uses this)
            has_masonry = any(s.find(class_='masonry-grid') for s in sections)
            if approved_has_masonry and not has_masonry:
                errors.append(f"{page_name}: Missing masonry-grid layout (used in approved theme)")
            
            # Check for section titles
            has_section_title = any(s.find(class_='section-title') for s in sections)
            if approved_has_section_title and not has_section_title:
                errors.append(f"{page_name}: Missing section-title elements (used in approved theme)")
        
        assert not errors, f"Theme consistency errors:\n" + "\n".join(errors)


class TestContentDiversity:
    """Test content diversity and richness"""
    
    @pytest.fixture
    def workspace_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_icon_diversity(self, workspace_root):
        """PASS: Pages should use varied Font Awesome icons"""
        docs_dir = workspace_root / "docs"
        pages = ['architecture', 'features', 'security']
        
        page_icons = {}
        for page_name in pages:
            page_path = docs_dir / page_name / "index.html"
            if not page_path.exists():
                continue
            
            with open(page_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            icons = soup.find_all('i', class_=re.compile(r'fa[brs]?\s+fa-'))
            icon_classes = set()
            for icon in icons:
                classes = icon.get('class', [])
                fa_classes = [c for c in classes if c.startswith('fa-') and c != 'fa-arrow-left']
                icon_classes.update(fa_classes)
            
            page_icons[page_name] = icon_classes
        
        # Check for icon diversity
        if len(page_icons) >= 2:
            all_icons = set()
            for icons in page_icons.values():
                all_icons.update(icons)
            
            if len(all_icons) < 10:
                pytest.skip(f"Low icon diversity: {len(all_icons)} unique icons across {len(page_icons)} pages")
    
    def test_color_palette_rotation(self, workspace_root):
        """FAIL: Pages should use 7-color palette rotation"""
        docs_dir = workspace_root / "docs"
        pages = ['architecture', 'features', 'security']
        
        glass_colors = {'purple', 'emerald', 'amber', 'cyan', 'teal', 'indigo', 'pink'}
        all_colors_used = set()
        
        for page_name in pages:
            page_path = docs_dir / page_name / "index.html"
            if not page_path.exists():
                continue
            
            with open(page_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for color in glass_colors:
                if f'glass-panel-{color}' in content:
                    all_colors_used.add(color)
        
        # Should use at least 5 of the 7 colors across all pages
        assert len(all_colors_used) >= 5, \
            f"Insufficient color diversity: {len(all_colors_used)}/7 colors used. " \
            f"Missing: {glass_colors - all_colors_used}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
