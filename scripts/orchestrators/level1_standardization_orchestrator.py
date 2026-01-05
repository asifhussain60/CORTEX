#!/usr/bin/env python3
"""
Level 1 View Standardization Orchestrator
==========================================

Orchestrates the complete standardization of Level 1 documentation views
based on the approved orchestrators/index.html pattern.

Features:
- Complexity analysis for visual treatment decisions
- Automated card/tile/tetris layout generation
- 7-color glassmorphism palette application
- Content regeneration to approved styles
- State tracking and validation

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import re

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


@dataclass
class ComplexityScore:
    """Complexity analysis results"""
    total_score: int
    content_volume: int  # Amount of text/data
    structural_depth: int  # Nesting levels
    data_types: int  # Lists, tables, code blocks
    recommendation: str  # Visual treatment recommendation
    

@dataclass
class VisualTreatment:
    """Visual layout decision"""
    layout_type: str  # 'card-grid', 'tetris', 'tiles', 'hero'
    color_palette: List[str]  # Glass panel colors
    use_icons: bool
    use_diagrams: bool
    

@dataclass
class StandardizationResult:
    """Result of standardization process"""
    page: str
    success: bool
    complexity_score: ComplexityScore
    visual_treatment: VisualTreatment
    changes_applied: List[str]
    errors: List[str]
    git_checkpoint: str


class ComplexityAnalyzer:
    """Analyzes content complexity to determine visual treatment"""
    
    def __init__(self):
        self.thresholds = {
            'high': 70,
            'medium': 40,
            'low': 20
        }
        
    def analyze(self, html_path: Path) -> ComplexityScore:
        """
        Analyze page complexity using multiple factors.
        
        Scoring:
        - Content volume: 0-30 points (word count, sections)
        - Structural depth: 0-25 points (nesting, hierarchy)
        - Data types: 0-45 points (tables, lists, code blocks, diagrams)
        """
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        # Remove script/style tags for analysis
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
            
        # Content volume scoring (0-30)
        text = soup.get_text()
        word_count = len(text.split())
        section_count = len(soup.find_all('section'))
        
        content_score = min(30, (word_count // 50) + (section_count * 2))
        
        # Structural depth scoring (0-25)
        max_depth = self._calculate_max_depth(soup.body if soup.body else soup)
        depth_score = min(25, max_depth * 3)
        
        # Data type scoring (0-45)
        data_score = 0
        data_score += len(soup.find_all(['table'])) * 10  # Tables are complex
        data_score += len(soup.find_all(['ul', 'ol'])) * 3  # Lists
        data_score += len(soup.find_all(['pre', 'code'])) * 5  # Code blocks
        data_score += len(soup.find_all(['img', 'svg'])) * 7  # Visual elements
        data_score = min(45, data_score)
        
        total = content_score + depth_score + data_score
        
        # Determine recommendation
        if total >= self.thresholds['high']:
            recommendation = "high_visual"  # Diagrams, hero sections, rich cards
        elif total >= self.thresholds['medium']:
            recommendation = "medium_visual"  # Card grids, tetris layouts
        else:
            recommendation = "simple_visual"  # Basic tiles, minimal decoration
            
        return ComplexityScore(
            total_score=total,
            content_volume=content_score,
            structural_depth=depth_score,
            data_types=data_score,
            recommendation=recommendation
        )
        
    def _calculate_max_depth(self, element, current_depth=0) -> int:
        """Recursively calculate maximum nesting depth"""
        if not element or not hasattr(element, 'children'):
            return current_depth
            
        max_child_depth = current_depth
        for child in element.children:
            if hasattr(child, 'children'):
                child_depth = self._calculate_max_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
                
        return max_child_depth


class VisualTreatmentDecider:
    """Decides visual treatment based on complexity and content"""
    
    GLASS_PALETTE_7COLOR = [
        'glass-panel-purple',
        'glass-panel-emerald', 
        'glass-panel-amber',
        'glass-panel-cyan',
        'glass-panel-teal',
        'glass-panel-indigo',
        'glass-panel-pink'
    ]
    
    def decide(self, complexity: ComplexityScore, page_name: str) -> VisualTreatment:
        """Decide visual treatment based on complexity score"""
        
        if complexity.recommendation == "high_visual":
            # High complexity: Rich visual treatment
            return VisualTreatment(
                layout_type='hero-card-grid',
                color_palette=self._select_palette(3),  # 3-color rotation
                use_icons=True,
                use_diagrams=True
            )
        elif complexity.recommendation == "medium_visual":
            # Medium complexity: Card grid or tetris
            return VisualTreatment(
                layout_type='tetris' if 'orchestrator' in page_name.lower() else 'card-grid',
                color_palette=self._select_palette(2),  # 2-color rotation
                use_icons=True,
                use_diagrams=False
            )
        else:
            # Low complexity: Simple tiles
            return VisualTreatment(
                layout_type='tiles',
                color_palette=self._select_palette(1),  # Single color
                use_icons=True,
                use_diagrams=False
            )
            
    def _select_palette(self, count: int) -> List[str]:
        """Select N colors from 7-color palette with rotation"""
        import random
        # Deterministic shuffle for consistency
        palette = self.GLASS_PALETTE_7COLOR.copy()
        random.seed(42)  # Fixed seed for reproducibility
        random.shuffle(palette)
        return palette[:count]


class ContentRegenerator:
    """Regenerates content to conform to approved styles"""
    
    def __init__(self, visual_treatment: VisualTreatment):
        self.visual_treatment = visual_treatment
        
    def regenerate_html(self, soup: BeautifulSoup, page_name: str) -> BeautifulSoup:
        """
        Regenerate HTML structure to match approved pattern.
        
        Pattern from orchestrators/index.html:
        - Hero section with robot head
        - Glass-card-display sections with color rotation
        - Masonry grid for cards
        - Card-stats-tetris for metadata pills
        """
        
        # Extract existing content
        sections = soup.find_all('section')
        main = soup.find('main') or soup.new_tag('main', **{'class': 'container', 'id': 'main-content'})
        
        # Clear main content (preserve header)
        if main:
            for child in list(main.children):
                if child.name == 'section':
                    child.decompose()
                    
        # Regenerate structure
        new_html = self._build_hero_section(page_name)
        
        # Process sections with color rotation
        color_idx = 0
        for section in sections:
            if section.find_parent('main'):
                color_class = self.visual_treatment.color_palette[color_idx % len(self.visual_treatment.color_palette)]
                new_section = self._convert_to_glass_section(section, color_class)
                main.append(new_section)
                color_idx += 1
                
        return soup
        
    def _build_hero_section(self, page_name: str) -> str:
        """Build hero section with robot head (approved pattern)"""
        title = page_name.replace('-', ' ').title()
        
        return f'''
        <div class="hero-section-wrapper">
            <div class="hero-robot-container">
                <a href="../index.html" title="Back to Home">
                    <img src="../assets/images/CORTEX-logo-200.png" alt="CORTEX Robot" class="hero-robot-head" />
                </a>
            </div>
            <div class="hero-divider-line"></div>
        </div>
        
        <section class="glass-card-display hero-introduction">
            <div class="card-header-centered">
                <i class="card-icon-primary fas fa-cube"></i>
                <h2>{title}</h2>
            </div>
            <p class="hero-description">
                Intelligent coordination system for {title.lower()} operations.
            </p>
        </section>
        '''
        
    def _convert_to_glass_section(self, section: BeautifulSoup, color_class: str) -> BeautifulSoup:
        """Convert section to glass-card-display with approved pattern"""
        
        # Create new section with glass styling
        new_section = section  # Reuse existing
        
        # Add/update classes
        classes = new_section.get('class', [])
        if 'glass-card-display' not in classes:
            classes.append('glass-card-display')
        if color_class and color_class not in classes:
            classes.append(color_class)
        new_section['class'] = classes
        
        # Convert content to cards if appropriate
        if self.visual_treatment.layout_type in ['card-grid', 'tetris', 'hero-card-grid']:
            self._convert_to_cards(new_section)
            
        return new_section
        
    def _convert_to_cards(self, section: BeautifulSoup):
        """Convert section content to card grid layout"""
        
        # Find lists, divs, or other content blocks
        content_blocks = section.find_all(['li', 'div', 'article'], recursive=False)
        
        if not content_blocks:
            return
            
        # Wrap in masonry grid
        grid = section.new_tag('div', **{'class': 'masonry-grid'})
        
        for block in content_blocks:
            card = self._create_card_from_block(block, section)
            grid.append(card)
            
        # Replace section content with grid
        section.clear()
        section.append(grid)
        
    def _create_card_from_block(self, block: BeautifulSoup, parent: BeautifulSoup) -> BeautifulSoup:
        """Create glass-card-clickable from content block"""
        
        card = parent.new_tag('div', **{'class': 'glass-card-clickable card-variant-primary'})
        
        # Extract title and content
        title = block.find(['h3', 'h4', 'strong']) or block.find(string=True)
        
        # Card header
        header = parent.new_tag('div', **{'class': 'card-header-centered'})
        icon = parent.new_tag('i', **{'class': 'card-icon-primary fas fa-cube'})
        h3 = parent.new_tag('h3', **{'class': 'card-title'})
        h3.string = str(title) if title else "Item"
        header.append(icon)
        header.append(h3)
        card.append(header)
        
        # Card description
        desc = parent.new_tag('p', **{'class': 'card-description'})
        desc.string = block.get_text()[:200] + "..." if len(block.get_text()) > 200 else block.get_text()
        card.append(desc)
        
        return card


class Level1StandardizationOrchestrator:
    """Master orchestrator for Level 1 view standardization"""
    
    LEVEL1_PAGES = [
        'architecture',
        'features',
        'getting-started',
        'knowledge',
        'learning-paths',
        'lens',
        'orchestrators',
        'security',
        'story',
        'sts',
        'token-optimization',
        'toolkit-manager'
    ]
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.docs_dir = workspace_root / "docs"
        self.state_file = workspace_root / "cortex-brain" / "cache" / "html-standardization-state.json"
        self.analyzer = ComplexityAnalyzer()
        self.decider = VisualTreatmentDecider()
        
    def orchestrate_all(self, dry_run: bool = False) -> List[StandardizationResult]:
        """Orchestrate standardization of all Level 1 pages"""
        
        print("=" * 70)
        print("🎨 CORTEX Level 1 View Standardization Orchestrator")
        print("=" * 70)
        print()
        print(f"📁 Workspace: {self.workspace_root}")
        print(f"📄 Pages to process: {len(self.LEVEL1_PAGES)}")
        print(f"🧪 Dry run: {dry_run}")
        print()
        
        results = []
        
        for page_name in self.LEVEL1_PAGES:
            print(f"\n{'─' * 70}")
            print(f"📄 Processing: {page_name}")
            print(f"{'─' * 70}")
            
            result = self.standardize_page(page_name, dry_run)
            results.append(result)
            
            self._print_result_summary(result)
            
        print("\n" + "=" * 70)
        print("📊 Overall Summary")
        print("=" * 70)
        
        success_count = sum(1 for r in results if r.success)
        print(f"✅ Successful: {success_count}/{len(results)}")
        print(f"❌ Failed: {len(results) - success_count}/{len(results)}")
        
        return results
        
    def standardize_page(self, page_name: str, dry_run: bool = False) -> StandardizationResult:
        """Standardize a single Level 1 page"""
        
        html_path = self.docs_dir / page_name / "index.html"
        
        if not html_path.exists():
            return StandardizationResult(
                page=page_name,
                success=False,
                complexity_score=ComplexityScore(0, 0, 0, 0, "error"),
                visual_treatment=VisualTreatment('error', [], False, False),
                changes_applied=[],
                errors=[f"File not found: {html_path}"],
                git_checkpoint=""
            )
            
        try:
            # Phase 1: Complexity Analysis
            print(f"🔍 Phase 1: Analyzing complexity...")
            complexity = self.analyzer.analyze(html_path)
            print(f"   Score: {complexity.total_score} (Content: {complexity.content_volume}, "
                  f"Structure: {complexity.structural_depth}, Data: {complexity.data_types})")
            print(f"   Recommendation: {complexity.recommendation}")
            
            # Phase 2: Visual Treatment Decision
            print(f"🎨 Phase 2: Deciding visual treatment...")
            visual_treatment = self.decider.decide(complexity, page_name)
            print(f"   Layout: {visual_treatment.layout_type}")
            print(f"   Colors: {', '.join(visual_treatment.color_palette)}")
            print(f"   Icons: {visual_treatment.use_icons}, Diagrams: {visual_treatment.use_diagrams}")
            
            # Phase 3: Content Regeneration
            print(f"🔨 Phase 3: Regenerating content...")
            
            if not dry_run:
                # Create git checkpoint
                checkpoint = self._create_git_checkpoint(page_name)
                
                # Load HTML
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    
                # Regenerate
                regenerator = ContentRegenerator(visual_treatment)
                soup = regenerator.regenerate_html(soup, page_name)
                
                # Save
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup.prettify()))
                    
                print(f"   ✅ HTML regenerated and saved")
                
                # Update state
                self._update_state(page_name, complexity, visual_treatment, checkpoint)
            else:
                checkpoint = "dry-run"
                print(f"   🧪 DRY RUN - No changes written")
                
            return StandardizationResult(
                page=page_name,
                success=True,
                complexity_score=complexity,
                visual_treatment=visual_treatment,
                changes_applied=[
                    f"Applied {visual_treatment.layout_type} layout",
                    f"Applied {len(visual_treatment.color_palette)}-color palette",
                    "Regenerated HTML structure"
                ],
                errors=[],
                git_checkpoint=checkpoint
            )
            
        except Exception as e:
            return StandardizationResult(
                page=page_name,
                success=False,
                complexity_score=ComplexityScore(0, 0, 0, 0, "error"),
                visual_treatment=VisualTreatment('error', [], False, False),
                changes_applied=[],
                errors=[str(e)],
                git_checkpoint=""
            )
            
    def _create_git_checkpoint(self, page_name: str) -> str:
        """Create git checkpoint tag"""
        import subprocess
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        tag = f"checkpoint-level1-{page_name}-{timestamp}"
        
        try:
            subprocess.run(['git', 'tag', tag], cwd=self.workspace_root, check=True)
            return tag
        except:
            return ""
            
    def _update_state(self, page_name: str, complexity: ComplexityScore, 
                     visual_treatment: VisualTreatment, checkpoint: str):
        """Update state tracking file"""
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing state
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        else:
            state = {
                "version": "2.0",
                "last_updated": "",
                "pages": {},
                "global_state": {
                    "total_pages_processed": 0,
                    "css_registry_version": "2.0",
                    "approved_panel_library_version": "1.1.0"
                }
            }
            
        # Update page state
        state["pages"][f"docs/{page_name}/index.html"] = {
            "last_modified": datetime.now().isoformat(),
            "git_checkpoint": checkpoint,
            "complexity_score": complexity.total_score,
            "visual_treatment": visual_treatment.layout_type,
            "color_palette": visual_treatment.color_palette,
            "status": "standardized",
            "approved_tag": ""
        }
        
        state["last_updated"] = datetime.now().isoformat()
        state["global_state"]["total_pages_processed"] = len(state["pages"])
        
        # Save
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    def _print_result_summary(self, result: StandardizationResult):
        """Print standardization result summary"""
        
        if result.success:
            print(f"\n✅ SUCCESS")
            print(f"   Complexity: {result.complexity_score.total_score} "
                  f"({result.complexity_score.recommendation})")
            print(f"   Layout: {result.visual_treatment.layout_type}")
            print(f"   Changes: {len(result.changes_applied)}")
            for change in result.changes_applied:
                print(f"      - {change}")
        else:
            print(f"\n❌ FAILED")
            for error in result.errors:
                print(f"   Error: {error}")


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Level 1 View Standardization Orchestrator"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without making changes'
    )
    parser.add_argument(
        '--page',
        type=str,
        help='Specific page to standardize (default: all)'
    )
    parser.add_argument(
        '--workspace',
        type=Path,
        default=Path.cwd(),
        help='Workspace root directory'
    )
    
    args = parser.parse_args()
    
    orchestrator = Level1StandardizationOrchestrator(args.workspace)
    
    if args.page:
        result = orchestrator.standardize_page(args.page, args.dry_run)
        sys.exit(0 if result.success else 1)
    else:
        results = orchestrator.orchestrate_all(args.dry_run)
        success_count = sum(1 for r in results if r.success)
        sys.exit(0 if success_count == len(results) else 1)


if __name__ == "__main__":
    main()
