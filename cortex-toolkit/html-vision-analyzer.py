#!/usr/bin/env python3
"""
HTML Vision Analyzer for CORTEX Documentation
==============================================

Analyzes screenshots/images of HTML pages to detect glassmorphism violations,
extract URLs, identify broken patterns, and calculate complexity scores.

Integrates with cortex-docs.prompt.md intelligence layer.

Author: Asif Hussain
Date: January 5, 2026
Version: 1.0.0
"""

import base64
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class VisionAnalysis:
    """Vision API analysis result."""
    structure: List[str]  # Detected HTML structure elements
    issues: List[str]  # Visual problems found
    urls: List[str]  # URLs extracted from image
    complexity_score: int  # 0-100
    pattern_violations: List[str]  # C50, C51, C52, C53 violations
    recommended_fixes: List[Dict[str, str]]  # Tool + pattern pairs
    color_analysis: Dict[str, any]  # Color scheme analysis
    spacing_issues: List[str]  # Alignment/spacing problems
    

class HTMLVisionAnalyzer:
    """Analyze HTML page screenshots for glassmorphism compliance."""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("cortex-brain/cache/vision-analysis")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Pattern signatures for detection
        self.patterns = {
            'C50': {
                'name': 'Color Rotation',
                'signature': r'card-variant-(primary|info|warning|success)',
                'violation': 'monotone cards (all same color)'
            },
            'C51': {
                'name': 'Tetris Stat Badges',
                'signature': r'stat-badge stat-(primary|info|warning)',
                'violation': 'monotone badges within cards'
            },
            'C52': {
                'name': 'Level 1 Hero Header',
                'signature': r'hero-section-wrapper.*hero-robot-container',
                'violation': 'missing or malformed hero header'
            },
            'C53': {
                'name': 'Full Section Panel Wrapping',
                'signature': r'<section class="glass-card-display">.*<h2.*</h2>.*</section>',
                'violation': 'heading not wrapped with content in panel'
            }
        }
    
    def analyze_image(self, image_path: str, context: Dict = None) -> VisionAnalysis:
        """
        Analyze screenshot of HTML page for glassmorphism compliance.
        
        Args:
            image_path: Path to screenshot file (PNG, JPG, JPEG)
            context: Optional context from user request
            
        Returns:
            VisionAnalysis with detected issues and recommendations
        """
        # Check cache first
        cache_key = self._get_cache_key(image_path)
        cached = self._load_from_cache(cache_key)
        if cached:
            print(f"✅ Using cached analysis (< 50ms)")
            return cached
        
        # Extract visual information
        print(f"🖼️ Analyzing image: {Path(image_path).name}...")
        
        # Simulate GPT-4V analysis (replace with actual API call)
        analysis = self._mock_vision_analysis(image_path, context)
        
        # Cache result
        self._save_to_cache(cache_key, analysis)
        
        return analysis
    
    def _mock_vision_analysis(self, image_path: str, context: Dict) -> VisionAnalysis:
        """
        Mock vision analysis (replace with actual GPT-4V API call).
        
        In production, this would call:
        - OpenAI GPT-4V API
        - Azure Computer Vision API
        - Google Cloud Vision API
        """
        # Simulate analysis based on image name/context
        structure = [
            "hero-section-wrapper with 200px robot logo",
            "glass-card-display hero-introduction",
            "masonry-grid with 10 card items",
            "section-title with icon"
        ]
        
        issues = [
            "All 10 cards use same purple icon (monotone)",
            "Section heading not wrapped in glassmorphism panel",
            "3 inline style attributes detected",
            "Inconsistent spacing between cards (gaps vary)"
        ]
        
        urls = [
            "http://localhost:8000/orchestrators/index.html"
        ]
        
        pattern_violations = [
            "C50: Color Rotation - all cards are primary color variant",
            "C53: Full Section Panel Wrapping - heading outside panel"
        ]
        
        recommended_fixes = [
            {
                'pattern': 'C50',
                'tool': 'validate-color-rotation.ps1',
                'args': '--autofix',
                'description': 'Apply 4-color rotation to 10 cards'
            },
            {
                'pattern': 'C53',
                'tool': 'validate-panel-wrapping.ps1',
                'args': '--autofix',
                'description': 'Wrap section heading + content in panel'
            },
            {
                'pattern': 'inline-styles',
                'tool': 'fix-inline-styles.ps1',
                'args': '--autofix',
                'description': 'Remove 3 inline styles'
            }
        ]
        
        color_analysis = {
            'primary_colors': ['#7c7cff'],  # Only purple detected
            'color_distribution': {'primary': 100, 'info': 0, 'warning': 0, 'success': 0},
            'is_monotone': True,
            'recommended_colors': ['#7c7cff', '#4a9eff', '#ffa500', '#10b981']
        }
        
        spacing_issues = [
            "Inconsistent gap between cards: 16px vs 24px",
            "Icon-title spacing: inline (should use gap: var(--spacing-sm))"
        ]
        
        # Calculate complexity score
        complexity_score = (
            len(issues) * 2 +  # 4 issues = 8
            len(pattern_violations) * 5 +  # 2 violations = 10
            (10 if color_analysis['is_monotone'] else 0) +  # Monotone = 10
            len(spacing_issues) * 1.5  # 2 spacing = 3
        )  # Total: 31 → Script-Driven
        
        return VisionAnalysis(
            structure=structure,
            issues=issues,
            urls=urls,
            complexity_score=int(complexity_score),
            pattern_violations=pattern_violations,
            recommended_fixes=recommended_fixes,
            color_analysis=color_analysis,
            spacing_issues=spacing_issues
        )
    
    def _get_cache_key(self, image_path: str) -> str:
        """Generate SHA-256 hash of image for caching."""
        with open(image_path, 'rb') as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[VisionAnalysis]:
        """Load cached analysis if exists and < 24 hours old."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        
        # Check age (24 hour TTL)
        import time
        age_seconds = time.time() - cache_file.stat().st_mtime
        if age_seconds > 86400:  # 24 hours
            cache_file.unlink()
            return None
        
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        return VisionAnalysis(**data)
    
    def _save_to_cache(self, cache_key: str, analysis: VisionAnalysis):
        """Save analysis to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(analysis.__dict__, f, indent=2)
    
    def extract_urls_from_image(self, image_path: str) -> List[str]:
        """
        Extract URLs from screenshot (browser address bar, links, etc.).
        
        Uses OCR or GPT-4V to read text from image.
        """
        # Mock implementation - in production, use OCR or GPT-4V
        return [
            "http://localhost:8000/orchestrators/index.html"
        ]
    
    def compare_vision_to_dom(self, vision_analysis: VisionAnalysis, html_path: str) -> Dict:
        """
        Compare visual analysis to actual DOM structure.
        
        Validates that what user sees matches what's in HTML.
        """
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        discrepancies = []
        
        # Check color rotation
        cards = soup.find_all(class_=re.compile(r'glass-card-clickable'))
        if vision_analysis.color_analysis['is_monotone']:
            variants = [c.get('class') for c in cards if 'card-variant' in str(c.get('class'))]
            unique_variants = set([v for sublist in variants for v in sublist if 'card-variant' in v])
            if len(unique_variants) <= 1:
                discrepancies.append({
                    'type': 'CONFIRMED',
                    'issue': 'Monotone cards',
                    'vision': 'All cards same color',
                    'dom': f'Only {unique_variants} found in DOM'
                })
        
        # Check panel wrapping
        if 'C53' in str(vision_analysis.pattern_violations):
            sections = soup.find_all('section', class_='glass-card-display')
            for section in sections:
                h2 = section.find('h2')
                content = section.find('div', class_=re.compile(r'masonry-grid|content'))
                if h2 and not content:
                    discrepancies.append({
                        'type': 'CONFIRMED',
                        'issue': 'Panel wrapping violation',
                        'vision': 'Heading outside panel',
                        'dom': f'Section has <h2> but no content inside'
                    })
        
        return {
            'discrepancies': discrepancies,
            'vision_accuracy': len(discrepancies) / max(len(vision_analysis.issues), 1) * 100
        }


def main():
    """CLI entry point for testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python html-vision-analyzer.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    analyzer = HTMLVisionAnalyzer()
    analysis = analyzer.analyze_image(image_path)
    
    print(f"\n📊 VISION ANALYSIS COMPLETE")
    print(f"\nComplexity Score: {analysis.complexity_score}")
    print(f"\nIssues Found ({len(analysis.issues)}):")
    for issue in analysis.issues:
        print(f"  ❌ {issue}")
    
    print(f"\nPattern Violations ({len(analysis.pattern_violations)}):")
    for violation in analysis.pattern_violations:
        print(f"  ⚠️ {violation}")
    
    print(f"\nRecommended Fixes ({len(analysis.recommended_fixes)}):")
    for fix in analysis.recommended_fixes:
        print(f"  🔧 {fix['pattern']}: {fix['tool']} {fix['args']}")
        print(f"     {fix['description']}")


if __name__ == '__main__':
    main()
