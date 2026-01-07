#!/usr/bin/env python3
"""
🔄 CORTEX Page Refresh & Enhancement Tool
==========================================

Discovers enhanced CORTEX functionalities and selectively recreates/refines
Level 1 and Level 2 pages with purpose-driven designs.

**Author:** Asif Hussain
**Version:** 1.0.0
**Date:** January 4, 2026
**Copyright:** © 2026 Asif Hussain. All rights reserved.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PageLevel(Enum):
    """Page hierarchy levels."""
    HOME = 0  # docs/index.html
    LEVEL_1 = 1  # Hub pages (architecture/index.html, security/index.html, etc.)
    LEVEL_2 = 2  # Detail pages (security/access-control.html, etc.)


class PagePurpose(Enum):
    """Purpose-driven page types."""
    NAVIGATION_HUB = "navigation_hub"  # Multi-panel navigation (Home, Level 1 hubs)
    TECHNICAL_DEEP_DIVE = "technical_deep_dive"  # Technical documentation with code
    CONCEPTUAL_LEARNING = "conceptual_learning"  # Learning materials with diagrams
    REFERENCE_GUIDE = "reference_guide"  # API docs, specifications
    DASHBOARD = "dashboard"  # Metrics, status, monitoring
    INTERACTIVE_TUTORIAL = "interactive_tutorial"  # Hands-on learning


@dataclass
class PageDesignProfile:
    """Design profile for a page."""
    level: PageLevel
    purpose: PagePurpose
    color_scheme: str  # Primary accent color
    layout_type: str  # multi-panel, single-column, two-column, grid
    features: List[str]  # tetris-metrics, d3-diagrams, mermaid-flows, etc.
    hero_style: str  # minimal, detailed, metric-focused


@dataclass
class PageAnalysis:
    """Analysis result for a page."""
    file_path: Path
    level: PageLevel
    purpose: PagePurpose
    current_features: List[str]
    missing_features: List[str]
    enhancement_score: int  # 0-100
    recommendations: List[str]


class PageRefreshTool:
    """Intelligent page discovery, analysis, and refresh system."""
    
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.all_pages = list(docs_dir.rglob('*.html'))
        
        # Design profiles for different page types
        self.design_profiles = self._initialize_design_profiles()
        
        # Color schemes by level
        self.color_schemes = {
            PageLevel.HOME: {
                'primary': '#00d4ff',
                'secondary': '#7c7cff',
                'accent': '#00ff88'
            },
            PageLevel.LEVEL_1: {
                'primary': '#00d4ff',
                'secondary': '#4a9eff',
                'accent': '#00b8d4'
            },
            PageLevel.LEVEL_2: {
                'primary': '#7c7cff',
                'secondary': '#9d9dff',
                'accent': '#5a5aff'
            }
        }
    
    def _initialize_design_profiles(self) -> Dict[str, PageDesignProfile]:
        """Initialize design profiles for different page types."""
        return {
            'home': PageDesignProfile(
                level=PageLevel.HOME,
                purpose=PagePurpose.NAVIGATION_HUB,
                color_scheme='#00d4ff',
                layout_type='multi-panel',
                features=['level0-tiles', 'hero-banner', 'quick-stats'],
                hero_style='detailed'
            ),
            'architecture_hub': PageDesignProfile(
                level=PageLevel.LEVEL_1,
                purpose=PagePurpose.NAVIGATION_HUB,
                color_scheme='#00d4ff',
                layout_type='tetris-cards',
                features=['tetris-metrics', 'tier-navigation', 'architecture-diagram'],
                hero_style='metric-focused'
            ),
            'security_hub': PageDesignProfile(
                level=PageLevel.LEVEL_1,
                purpose=PagePurpose.DASHBOARD,
                color_scheme='#ff6b6b',
                layout_type='multi-panel',
                features=['threat-matrix', 'compliance-status', 'category-panels'],
                hero_style='minimal'
            ),
            'technical_detail': PageDesignProfile(
                level=PageLevel.LEVEL_2,
                purpose=PagePurpose.TECHNICAL_DEEP_DIVE,
                color_scheme='#7c7cff',
                layout_type='single-column',
                features=['code-examples', 'mermaid-diagrams', 'technical-specs'],
                hero_style='minimal'
            ),
            'learning_module': PageDesignProfile(
                level=PageLevel.LEVEL_2,
                purpose=PagePurpose.CONCEPTUAL_LEARNING,
                color_scheme='#9d9dff',
                layout_type='two-column',
                features=['d3-visualizations', 'interactive-examples', 'progress-tracker'],
                hero_style='detailed'
            )
        }
    
    def detect_page_level(self, html_path: Path) -> PageLevel:
        """Detect page hierarchy level."""
        rel_path = html_path.relative_to(self.docs_dir)
        
        # Home page
        if html_path.name == 'index.html' and html_path.parent == self.docs_dir:
            return PageLevel.HOME
        
        # Level 1: Hub pages (category index pages)
        if html_path.name == 'index.html':
            return PageLevel.LEVEL_1
        
        # Level 2: Detail pages
        return PageLevel.LEVEL_2
    
    def detect_page_purpose(self, html_path: Path, content: str) -> PagePurpose:
        """Detect page purpose from content analysis."""
        
        # Navigation hub detection
        if 'multi-panel' in content or 'category-panel' in content:
            return PagePurpose.NAVIGATION_HUB
        
        # Dashboard detection
        if 'dashboard' in html_path.name.lower() or 'metrics' in content.lower():
            return PagePurpose.DASHBOARD
        
        # Technical deep dive detection
        if re.search(r'<pre><code|class="code-block', content):
            return PagePurpose.TECHNICAL_DEEP_DIVE
        
        # Learning module detection
        if 'learning' in html_path.parts or 'tutorial' in content.lower():
            return PagePurpose.CONCEPTUAL_LEARNING
        
        # Reference guide detection
        if 'api' in html_path.name.lower() or 'reference' in content.lower():
            return PagePurpose.REFERENCE_GUIDE
        
        # Default
        return PagePurpose.TECHNICAL_DEEP_DIVE
    
    def analyze_page(self, html_path: Path) -> PageAnalysis:
        """Analyze a page and provide enhancement recommendations."""
        try:
            content = html_path.read_text(encoding='utf-8')
            
            level = self.detect_page_level(html_path)
            purpose = self.detect_page_purpose(html_path, content)
            
            # Detect current features
            current_features = []
            if 'tetris-metrics' in content or 'token-metrics-tetris' in content:
                current_features.append('tetris-metrics')
            if 'd3.v7' in content or 'd3js.org' in content:
                current_features.append('d3-diagrams')
            if 'mermaid' in content:
                current_features.append('mermaid-diagrams')
            if 'multi-panel' in content:
                current_features.append('multi-panel-layout')
            if 'hero-section' in content:
                current_features.append('hero-section')
            if 'glass-card' in content:
                current_features.append('glassmorphism')
            
            # Determine missing features based on level and purpose
            missing_features = []
            recommendations = []
            
            if level == PageLevel.HOME:
                if 'level0-tile' not in content:
                    missing_features.append('level0-tiles')
                    recommendations.append('Add Level 0 navigation tiles for main categories')
                if 'hero-banner' not in content:
                    missing_features.append('hero-banner')
                    recommendations.append('Add prominent hero banner with CORTEX branding')
            
            elif level == PageLevel.LEVEL_1:
                if 'tetris-metrics' not in content and purpose == PagePurpose.NAVIGATION_HUB:
                    missing_features.append('tetris-metrics')
                    recommendations.append('Add tetris-style metric tiles for quick navigation')
                if 'category-panel' not in content and purpose != PagePurpose.DASHBOARD:
                    missing_features.append('category-panels')
                    recommendations.append('Add multi-panel layout for subcategories')
                if 'd3-diagrams' not in current_features:
                    missing_features.append('d3-overview-diagram')
                    recommendations.append('Add D3.js overview diagram showing relationships')
            
            elif level == PageLevel.LEVEL_2:
                if 'mermaid-diagrams' not in current_features:
                    missing_features.append('mermaid-technical-flows')
                    recommendations.append('Add Mermaid flowcharts/sequence diagrams')
                if purpose == PagePurpose.TECHNICAL_DEEP_DIVE:
                    if '<pre><code' not in content:
                        missing_features.append('code-examples')
                        recommendations.append('Add code examples with syntax highlighting')
                if purpose == PagePurpose.CONCEPTUAL_LEARNING:
                    if 'd3-diagrams' not in current_features:
                        missing_features.append('d3-interactive-viz')
                        recommendations.append('Add interactive D3.js visualizations')
            
            # Calculate enhancement score
            total_possible = len(current_features) + len(missing_features)
            enhancement_score = int((len(current_features) / max(total_possible, 1)) * 100)
            
            return PageAnalysis(
                file_path=html_path,
                level=level,
                purpose=purpose,
                current_features=current_features,
                missing_features=missing_features,
                enhancement_score=enhancement_score,
                recommendations=recommendations
            )
        
        except Exception as e:
            print(f"❌ Error analyzing {html_path}: {e}")
            return None
    
    def discover_enhancements(self) -> Dict:
        """Discover all pages and their enhancement opportunities."""
        results = {
            'home': [],
            'level_1': [],
            'level_2': [],
            'statistics': {
                'total_pages': 0,
                'by_level': {0: 0, 1: 0, 2: 0},
                'avg_enhancement_score': 0,
                'high_priority': []
            }
        }
        
        print("🔍 Discovering CORTEX pages and enhancement opportunities...")
        
        analyses = []
        for html_file in self.all_pages:
            # Skip archives
            if 'archive' in str(html_file).lower():
                continue
            
            analysis = self.analyze_page(html_file)
            if analysis:
                analyses.append(analysis)
                
                # Categorize by level
                if analysis.level == PageLevel.HOME:
                    results['home'].append(analysis)
                elif analysis.level == PageLevel.LEVEL_1:
                    results['level_1'].append(analysis)
                else:
                    results['level_2'].append(analysis)
        
        # Calculate statistics
        results['statistics']['total_pages'] = len(analyses)
        results['statistics']['by_level'] = {
            0: len(results['home']),
            1: len(results['level_1']),
            2: len(results['level_2'])
        }
        
        if analyses:
            results['statistics']['avg_enhancement_score'] = sum(
                a.enhancement_score for a in analyses
            ) / len(analyses)
        
        # Identify high-priority pages (score < 70)
        results['statistics']['high_priority'] = [
            {
                'file': str(a.file_path.relative_to(self.docs_dir)),
                'level': a.level.value,
                'score': a.enhancement_score,
                'missing': len(a.missing_features)
            }
            for a in sorted(analyses, key=lambda x: x.enhancement_score)[:10]
        ]
        
        return results
    
    def generate_refresh_report(self, output_path: Path):
        """Generate comprehensive refresh/enhancement report."""
        results = self.discover_enhancements()
        
        # Create detailed report
        report = {
            'metadata': {
                'generated_at': '2026-01-04',
                'tool_version': '1.0.0',
                'docs_directory': str(self.docs_dir)
            },
            'summary': results['statistics'],
            'pages_by_level': {
                'home': [self._analysis_to_dict(a) for a in results['home']],
                'level_1_hubs': [self._analysis_to_dict(a) for a in results['level_1']],
                'level_2_details': [self._analysis_to_dict(a) for a in results['level_2']]
            },
            'color_schemes': {
                'home': self.color_schemes[PageLevel.HOME],
                'level_1': self.color_schemes[PageLevel.LEVEL_1],
                'level_2': self.color_schemes[PageLevel.LEVEL_2]
            },
            'design_profiles': {
                name: {
                    'level': profile.level.value,
                    'purpose': profile.purpose.value,
                    'color_scheme': profile.color_scheme,
                    'layout_type': profile.layout_type,
                    'features': profile.features,
                    'hero_style': profile.hero_style
                }
                for name, profile in self.design_profiles.items()
            }
        }
        
        output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        
        # Print summary
        print(f"\n✅ Discovery complete:")
        print(f"   Total pages: {results['statistics']['total_pages']}")
        print(f"   Home: {results['statistics']['by_level'][0]}")
        print(f"   Level 1: {results['statistics']['by_level'][1]}")
        print(f"   Level 2: {results['statistics']['by_level'][2]}")
        print(f"   Avg enhancement score: {results['statistics']['avg_enhancement_score']:.1f}/100")
        print(f"\n📊 Top 10 high-priority pages:")
        for item in results['statistics']['high_priority']:
            print(f"   {item['file']} (Level {item['level']}, Score: {item['score']}, Missing: {item['missing']})")
        print(f"\n📄 Report saved: {output_path}")
    
    def _analysis_to_dict(self, analysis: PageAnalysis) -> Dict:
        """Convert PageAnalysis to dictionary."""
        return {
            'file': str(analysis.file_path.relative_to(self.docs_dir)),
            'level': analysis.level.value,
            'purpose': analysis.purpose.value,
            'enhancement_score': analysis.enhancement_score,
            'current_features': analysis.current_features,
            'missing_features': analysis.missing_features,
            'recommendations': analysis.recommendations
        }
    
    def selective_refresh(self, page_filter: Dict) -> List[Path]:
        """
        Select pages for refresh based on criteria.
        
        Args:
            page_filter: {
                'level': [0, 1, 2],  # Optional
                'min_score': 0-100,  # Optional
                'purpose': PagePurpose,  # Optional
                'has_missing': ['feature1', 'feature2']  # Optional
            }
        """
        results = self.discover_enhancements()
        all_analyses = results['home'] + results['level_1'] + results['level_2']
        
        filtered = []
        for analysis in all_analyses:
            # Filter by level
            if 'level' in page_filter:
                if analysis.level.value not in page_filter['level']:
                    continue
            
            # Filter by score
            if 'min_score' in page_filter:
                if analysis.enhancement_score >= page_filter['min_score']:
                    continue
            
            # Filter by purpose
            if 'purpose' in page_filter:
                if analysis.purpose != page_filter['purpose']:
                    continue
            
            # Filter by missing features
            if 'has_missing' in page_filter:
                if not any(f in analysis.missing_features for f in page_filter['has_missing']):
                    continue
            
            filtered.append(analysis.file_path)
        
        return filtered


if __name__ == '__main__':
    docs_dir = Path(__file__).parent.parent / 'docs'
    tool = PageRefreshTool(docs_dir)
    
    # Generate discovery report
    report_path = Path(__file__).parent.parent / 'reports' / 'page-refresh-analysis.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    tool.generate_refresh_report(report_path)
    
    # Example: Find Level 1 pages needing tetris metrics
    print("\n🎯 Example: Level 1 pages missing tetris-metrics:")
    candidates = tool.selective_refresh({
        'level': [1],
        'has_missing': ['tetris-metrics']
    })
    for page in candidates[:5]:
        print(f"   {page.relative_to(docs_dir)}")
    
    # Example: Find Level 2 pages missing diagrams
    print("\n🎯 Example: Level 2 pages missing diagrams:")
    candidates = tool.selective_refresh({
        'level': [2],
        'has_missing': ['d3-diagrams', 'mermaid-diagrams']
    })
    for page in candidates[:5]:
        print(f"   {page.relative_to(docs_dir)}")
