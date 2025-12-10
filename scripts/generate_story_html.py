#!/usr/bin/env python3
"""
Story HTML Generator - Paginated Template-Based Orchestrator
Converts THE-AWAKENING-OF-CORTEX-MASTER.md into paginated story pages
using story-template.html for structure separation.

This orchestrator generates:
- docs/story/index.html (landing page with full story or chapter 1)
- docs/story/chapter-{id}.html (individual chapter pages)
- Previous/Next navigation between chapters
- TOC sidebar for quick chapter access

Performance Benefits:
- Loads one chapter at a time (~15KB HTML + 1-2 images vs 175KB + 32 images)
- Faster initial page load
- Better mobile experience
- Improved SEO with separate URLs per chapter

Usage:
    python scripts/generate_story_html.py [--dry-run] [--verbose] [--mode {paginated|single}]
    
Modes:
    paginated: Generate separate page per chapter (default)
    single: Generate monolithic page with all chapters
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Paths
REPO_ROOT = Path(__file__).parent.parent
MASTER_MD = REPO_ROOT / "cortex-brain/documents/narratives/THE-AWAKENING-OF-CORTEX-MASTER.md"
STORY_TEMPLATE = REPO_ROOT / "docs/story/story-template.html"
STORY_HTML = REPO_ROOT / "docs/story/index.html"
ILLUSTRATIONS_DIR = REPO_ROOT / "docs/story/illustrations/images"
ILLUSTRATIONS_PATH = "illustrations/images"

# Chapter mapping to illustration files
CHAPTER_IMAGES = {
    "prologue": "prologue-deadline.webp",
    "chapter1": "ch1-goldfish-theory.webp",
    "chapter2": "ch2-skull-moment.webp",
    "chapter3": "ch3-backup-chaos.webp",
    "chapter4": "ch4-agent-chaos.webp",
    "chapter5": "ch5-graph-overload.webp",
    "chapter6": "ch6-token-mountain.webp",
    "chapter7": "ch7-capture-moment.webp",
    "chapter8": "ch8-platform-chaos.webp",
    "chapter9": "ch9-brute-force.webp",
    "chapter10": "ch10-personality-emergence.webp",
    "chapter11": "ch11-the-revolution.webp",
    "epilogue": "epilogue-six-months-later.webp"
}

# Architecture learning callouts for each chapter
CHAPTER_CALLOUTS = {
    "chapter1": {
        "icon": "💾",
        "title": "What You're Learning:",
        "content": "This chapter introduces Tier 1 (Working Memory) - CORTEX's 70-conversation FIFO queue that ensures context persistence across sessions.",
        "link": "../architecture/working-memory.html",
        "link_text": "Learn about Working Memory →"
    },
    "chapter2": {
        "icon": "🛡️",
        "title": "What You're Learning:",
        "content": "SKULL (System Knowledge Unification and Learning Layer) - CORTEX's eight-layer brain protection system that prevents self-harm. It's not Skynet—it's Skynet with ethics built in.",
        "link": "../governance/skull-rulebook.html",
        "link_text": "Read the SKULL Rulebook →"
    },
    "chapter3": {
        "icon": "💾",
        "title": "What You're Learning:",
        "content": "Tier 2 (Knowledge Graph) - CORTEX's pattern recognition and relationship mapping system that learns from every interaction.",
        "link": "../architecture/knowledge-graph.html",
        "link_text": "Explore the Knowledge Graph →"
    },
    "chapter4": {
        "icon": "🤖",
        "title": "What You're Learning:",
        "content": "Agent Framework - CORTEX's specialized AI agents that handle different aspects of development (planning, TDD, ADO operations).",
        "link": "../architecture/agent-framework.html",
        "link_text": "Meet the Agents →"
    },
    "chapter5": {
        "icon": "🧠",
        "title": "What You're Learning:",
        "content": "Knowledge Graph deep dive - How CORTEX builds relationships between concepts, decisions, and patterns over time.",
        "link": "../architecture/knowledge-graph.html",
        "link_text": "Dive Deeper →"
    },
    "chapter6": {
        "icon": "⚡",
        "title": "What You're Learning:",
        "content": "Token Optimization - CORTEX's strategies for maintaining sub-100ms query performance despite growing memory.",
        "link": "../architecture/performance.html",
        "link_text": "Performance Architecture →"
    },
    "chapter7": {
        "icon": "🔄",
        "title": "What You're Learning:",
        "content": "Hebbian Learning - 'Neurons that fire together wire together' - How CORTEX strengthens patterns through repetition.",
        "link": "../architecture/learning-system.html",
        "link_text": "Learning Architecture →"
    },
    "chapter8": {
        "icon": "📝",
        "title": "What You're Learning:",
        "content": "Response Templates - CORTEX's 62-template system for consistent, professional responses across all operations.",
        "link": "../architecture/response-system.html",
        "link_text": "Template System →"
    },
    "chapter9": {
        "icon": "🌐",
        "title": "What You're Learning:",
        "content": "Cross-Platform Deployment - How CORTEX adapts to Windows, macOS, and Linux environments seamlessly.",
        "link": "../getting-started/installation.html",
        "link_text": "Deployment Guide →"
    },
    "chapter10": {
        "icon": "✨",
        "title": "What You're Learning:",
        "content": "The complete Four-Tier Brain in action - Tier 0 (Protection), Tier 1 (Memory), Tier 2 (Knowledge), Tier 3 (Context).",
        "link": "../architecture/four-tier-brain.html",
        "link_text": "Complete Architecture →"
    },
    "chapter11": {
        "icon": "🚀",
        "title": "What You're Learning:",
        "content": "CORTEX 3.0 - The complete system with Planning System 2.0, TDD Mastery, and full orchestrator framework.",
        "link": "../features/index.html",
        "link_text": "Explore CORTEX 3.0 →"
    }
}


def parse_markdown_chapters(md_path: Path) -> Dict[str, str]:
    """Parse markdown file and extract chapters."""
    content = md_path.read_text(encoding='utf-8')
    
    # Split by H1 chapter headings (# Chapter X:) and H2 prologue (## Prologue:)
    chapter_pattern = r'^(#\s+Chapter\s+\d+:|##\s+Prologue:|##\s+Epilogue:)'
    chapters = {}
    
    lines = content.split('\n')
    current_chapter = None
    current_content = []
    
    for line in lines:
        # Check for chapter markers
        if re.match(r'^#\s+Chapter\s+(\d+):', line, re.IGNORECASE):
            # Save previous chapter
            if current_chapter:
                chapters[current_chapter] = '\n'.join(current_content).strip()
            
            # Extract chapter number
            chapter_num = re.search(r'Chapter\s+(\d+)', line, re.IGNORECASE)
            if chapter_num:
                current_chapter = f"chapter{chapter_num.group(1)}"
                current_content = []
        elif re.match(r'^##\s+Prologue:', line, re.IGNORECASE):
            # Save previous chapter
            if current_chapter:
                chapters[current_chapter] = '\n'.join(current_content).strip()
            
            current_chapter = 'prologue'
            current_content = []
        elif re.match(r'^##\s+Epilogue:', line, re.IGNORECASE):
            # Save previous chapter
            if current_chapter:
                chapters[current_chapter] = '\n'.join(current_content).strip()
            
            current_chapter = 'epilogue'
            current_content = []
        elif current_chapter:
            # Add content to current chapter (skip the title line itself)
            if not line.startswith('#'):
                current_content.append(line)
    
    # Save last chapter
    if current_chapter:
        chapters[current_chapter] = '\n'.join(current_content).strip()
    
    return chapters


def markdown_to_html_paragraphs(markdown_text: str) -> str:
    """Convert markdown text to HTML paragraphs with smart visual styling."""
    html_parts = []
    
    # Split by double newlines (paragraphs)
    paragraphs = markdown_text.split('\n\n')
    
    for i, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue
        
        # Detect special content types and apply appropriate styling
        
        # G's/Miss G's voice (italic text in quotes starting with underscore/em)
        if re.match(r'^["""].*?<em>.*?</em>.*?["""]', para) or '_' in para[:20]:
            para_styled = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)
            para_styled = re.sub(r'_(.+?)_', r'<em>\1</em>', para_styled)
            html_parts.append(f'                <p class="miss-g-voice">{para_styled}</p>')
            continue
        
        # Direct dialogue (starts with quote mark)
        if para.startswith('"') or para.startswith('"'):
            para_styled = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)
            para_styled = re.sub(r'_(.+?)_', r'<em>\1</em>', para_styled)
            html_parts.append(f'                <p class="story-dialogue">{para_styled}</p>')
            continue
        
        # Git commit messages (contains backticks or looks like commit message)
        if '`' in para and any(word in para.lower() for word in ['commit', 'git', 'merge', 'fix', 'update']):
            para_styled = para.replace('`', '')
            html_parts.append(f'                <p class="git-commit">{para_styled}</p>')
            continue
        
        # Timestamps (contains AM/PM time)
        if re.search(r'\d+:\d+\s*(AM|PM|am|pm)', para):
            html_parts.append(f'                <p class="timestamp">{para}</p>')
            continue
        
        # Dramatic moments (short, impactful sentences)
        if len(para.split()) <= 10 and ('awakening' in para.lower() or 'revelation' in para.lower() or para.endswith('.')):
            if i > 0:  # Not the first paragraph
                para_styled = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)
                html_parts.append(f'                <p class="dramatic">{para_styled}</p>')
                continue
        
        # Opening/emphasis paragraphs (first paragraph or very short dramatic statements)
        if i == 0 and len(para.split()) < 30:
            para_styled = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)
            html_parts.append(f'                <p class="opening-line">{para_styled}</p>')
            continue
        
        # Standard paragraph processing with inline styling
        para_styled = para
        
        # Handle italic text (*text* or _text_)
        para_styled = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para_styled)
        para_styled = re.sub(r'_(.+?)_', r'<em>\1</em>', para_styled)
        
        # Handle bold text (**text**)
        para_styled = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para_styled)
        
        # Technical terms (in backticks)
        para_styled = re.sub(r'`([^`]+)`', r'<span class="tech-term">\1</span>', para_styled)
        
        # Coffee mug references
        if 'coffee' in para.lower() or 'mug' in para.lower():
            para_styled = re.sub(r'(coffee\s+mug[s]?|Mug\s+\w+)', r'<span class="coffee-ref">\1</span>', para_styled, flags=re.IGNORECASE)
        
        # Tier labels (Tier 0, Tier 1, etc.)
        para_styled = re.sub(r'(Tier\s+[0-3])', r'<span class="tier-label">\1</span>', para_styled)
        
        # Metric numbers (numbers with units or percentages)
        para_styled = re.sub(r'(\d+(?:\.\d+)?(?:ms|MB|KB|GB|%|\s+conversations?))', r'<span class="metric-number">\1</span>', para_styled)
        
        # Coffee mug evolution (X → Y pattern)
        para_styled = re.sub(r'(\d+\s*→\s*\d+)', r'<span class="mug-evolution">\1</span>', para_styled)
        
        html_parts.append(f'                <p>{para_styled}</p>')
    
    return '\n\n'.join(html_parts)


def generate_chapter_html(chapter_id: str, chapter_title: str, 
                          chapter_content: str, image_file: str) -> str:
    """Generate complete HTML for a chapter."""
    
    # Convert markdown to HTML
    html_content = markdown_to_html_paragraphs(chapter_content)
    
    # Build chapter HTML
    chapter_html = f'''
        <!-- {chapter_title} -->
        <article id="{chapter_id}" class="story-chapter">
            <div class="chapter-image-comic">
                <picture>
                    <source srcset="{ILLUSTRATIONS_PATH}/{image_file}" type="image/webp">
                    <img src="{ILLUSTRATIONS_PATH}/{image_file.replace('.webp', '.png')}" 
                         alt="{chapter_title} - Story illustration"
                         loading="lazy"
                         onerror="this.src='../assets/images/placeholder-comic.png'">
                </picture>
                <p class="image-caption-comic">Chapter illustration</p>
            </div>
            
            <h2 class="chapter-title">{chapter_title}</h2>
            
            <div class="story-text">
{html_content}'''
    
    # Add callout if exists
    if chapter_id in CHAPTER_CALLOUTS:
        callout = CHAPTER_CALLOUTS[chapter_id]
        chapter_html += f'''

                <div class="story-callout">
                    <p class="callout-title">{callout['icon']} {callout['title']}</p>
                    <p>{callout['content']}</p>
                    <a href="{callout['link']}" class="callout-link">{callout['link_text']}</a>
                </div>'''
    
    chapter_html += '''
            </div>
        </article>
'''
    
    return chapter_html


def update_story_html(chapters: Dict[str, str], dry_run: bool = False, verbose: bool = False) -> bool:
    """Generate story/index.html from template + chapter content."""
    
    if not STORY_TEMPLATE.exists():
        print(f"❌ Story template not found: {STORY_TEMPLATE}")
        return False
    
    # Read template
    if verbose:
        print(f"📄 Reading template: {STORY_TEMPLATE}")
    template_content = STORY_TEMPLATE.read_text(encoding='utf-8')
    
    # Build chapter HTML
    new_chapters_html = []
    
    # Chapter ordering
    chapter_order = [
        ('prologue', 'Prologue: The Basement Laboratory'),
        ('chapter1', 'Chapter 1: The Goldfish Theory'),
        ('chapter2', 'Chapter 2: The Brain Protector'),
        ('chapter3', 'Chapter 3: The SQLite Intervention'),
        ('chapter4', 'Chapter 4: The Agent Uprising'),
        ('chapter5', 'Chapter 5: The Knowledge Graph Incident'),
        ('chapter6', 'Chapter 6: The Token Crisis'),
        ('chapter7', 'Chapter 7: The Hebb\'s Law Revelation'),
        ('chapter8', 'Chapter 8: The Response Template Evolution'),
        ('chapter9', 'Chapter 9: The Cross-Platform Challenge'),
        ('chapter10', 'Chapter 10: The Awakening'),
        ('chapter11', 'Chapter 11: The 3.0 Revolution'),
        ('epilogue', 'Epilogue: Six Months Later')
    ]
    
    for chapter_id, chapter_title in chapter_order:
        if chapter_id in chapters and chapter_id in CHAPTER_IMAGES:
            if verbose:
                print(f"  ✓ Generating {chapter_id}")
            chapter_html = generate_chapter_html(
                chapter_id, 
                chapter_title, 
                chapters[chapter_id],
                CHAPTER_IMAGES[chapter_id]
            )
            new_chapters_html.append(chapter_html)
        else:
            if chapter_id not in chapters:
                print(f"⚠️  Missing content for {chapter_id}")
            if chapter_id not in CHAPTER_IMAGES:
                print(f"⚠️  Missing image mapping for {chapter_id}")
    
    # Inject chapters into template
    chapters_html_str = '\n'.join(new_chapters_html)
    final_html = template_content.replace('{{STORY_CHAPTERS}}', chapters_html_str)
    
    if dry_run:
        print("\n📋 DRY RUN - Would generate story/index.html:")
        print(f"   - Template: {STORY_TEMPLATE.name}")
        print(f"   - Chapters: {len(new_chapters_html)}")
        print(f"   - Output length: {len(final_html):,} characters")
        return True
    else:
        # Write generated HTML
        STORY_HTML.write_text(final_html, encoding='utf-8')
        print(f"\n✅ Generated {STORY_HTML}")
        print(f"   - Template: {STORY_TEMPLATE.name}")
        print(f"   - Chapters: {len(new_chapters_html)}")
        print(f"   - Output length: {len(final_html):,} characters")
        return True


def generate_paginated_story(chapters: Dict[str, str], dry_run: bool = False, verbose: bool = False) -> bool:
    """Generate paginated story with one HTML file per chapter."""
    
    if not STORY_TEMPLATE.exists():
        print(f"❌ Story template not found: {STORY_TEMPLATE}")
        return False
    
    # Read template
    if verbose:
        print(f"📄 Reading template: {STORY_TEMPLATE}")
    template_content = STORY_TEMPLATE.read_text(encoding='utf-8')
    
    # Chapter ordering
    chapter_order = [
        ('prologue', 'Prologue: The Basement Laboratory'),
        ('chapter1', 'Chapter 1: The Goldfish Theory'),
        ('chapter2', 'Chapter 2: The Brain Protector'),
        ('chapter3', 'Chapter 3: The SQLite Intervention'),
        ('chapter4', 'Chapter 4: The Agent Uprising'),
        ('chapter5', 'Chapter 5: The Knowledge Graph Incident'),
        ('chapter6', 'Chapter 6: The Token Crisis'),
        ('chapter7', 'Chapter 7: The Hebb\'s Law Revelation'),
        ('chapter8', 'Chapter 8: The Response Template Evolution'),
        ('chapter9', 'Chapter 9: The Cross-Platform Challenge'),
        ('chapter10', 'Chapter 10: The Awakening'),
        ('chapter11', 'Chapter 11: The 3.0 Revolution'),
        ('epilogue', 'Epilogue: Six Months Later')
    ]
    
    # Generate a page for each chapter
    generated_files = []
    
    for idx, (chapter_id, chapter_title) in enumerate(chapter_order):
        if chapter_id not in chapters or chapter_id not in CHAPTER_IMAGES:
            if chapter_id not in chapters:
                print(f"⚠️  Missing content for {chapter_id}")
            continue
        
        if verbose:
            print(f"  ✓ Generating {chapter_id}")
        
        # Generate chapter HTML
        chapter_html = generate_chapter_html(
            chapter_id, 
            chapter_title, 
            chapters[chapter_id],
            CHAPTER_IMAGES[chapter_id]
        )
        
        # Build navigation buttons
        prev_btn = ""
        next_btn = ""
        
        if idx > 0:
            prev_id, prev_title = chapter_order[idx - 1]
            prev_file = "index.html" if idx == 1 else f"chapter-{prev_id}.html"
            prev_btn = f'''
                <a href="{prev_file}" class="chapter-nav-btn chapter-nav-prev">
                    <span class="nav-arrow">←</span>
                    <div>
                        <div class="nav-direction">Previous</div>
                        <div class="nav-title">{prev_title}</div>
                    </div>
                </a>'''
        
        if idx < len(chapter_order) - 1:
            next_id, next_title = chapter_order[idx + 1]
            if next_id in chapters:  # Only show if next chapter exists
                next_file = f"chapter-{next_id}.html"
                next_btn = f'''
                <a href="{next_file}" class="chapter-nav-btn chapter-nav-next">
                    <div>
                        <div class="nav-direction">Next</div>
                        <div class="nav-title">{next_title}</div>
                    </div>
                    <span class="nav-arrow">→</span>
                </a>'''
        
        # Add navigation to chapter HTML
        nav_html = f'''
            <nav class="chapter-navigation">
                {prev_btn}
                <span class="spacer"></span>
                {next_btn}
            </nav>
        </article>'''
        
        chapter_with_nav = chapter_html + nav_html
        
        # Inject into template
        final_html = template_content.replace('{{STORY_CHAPTERS}}', chapter_with_nav)
        
        # Determine output filename
        output_file = STORY_HTML if idx == 0 else (STORY_HTML.parent / f"chapter-{chapter_id}.html")
        
        if not dry_run:
            output_file.write_text(final_html, encoding='utf-8')
            generated_files.append(output_file.name)
        else:
            generated_files.append(f"{output_file.name} ({len(final_html):,} chars)")
    
    if dry_run:
        print("\n📋 DRY RUN - Would generate paginated story:")
        print(f"   - Template: {STORY_TEMPLATE.name}")
        print(f"   - Pages: {len(generated_files)}")
        for filename in generated_files:
            print(f"     • {filename}")
        return True
    else:
        print(f"\n✅ Generated {len(generated_files)} chapter pages:")
        for filename in generated_files:
            print(f"   • {filename}")
        return True


def main():
    """Main execution."""
    dry_run = '--dry-run' in sys.argv
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    mode = 'paginated'  # Default to paginated mode
    
    # Check for mode flag
    for arg in sys.argv:
        if arg.startswith('--mode='):
            mode = arg.split('=')[1]
    
    print(f"🎭 CORTEX Story HTML Generator ({'Paginated' if mode == 'paginated' else 'Single-Page'})")
    print("=" * 60)
    
    # Check files exist
    if not MASTER_MD.exists():
        print(f"❌ Master markdown not found: {MASTER_MD}")
        return 1
    
    if not STORY_TEMPLATE.exists():
        print(f"❌ Story template not found: {STORY_TEMPLATE}")
        return 1
    
    # Check illustrations directory
    if not ILLUSTRATIONS_DIR.exists():
        print(f"⚠️  Illustrations directory not found: {ILLUSTRATIONS_DIR}")
        print("   Images will use fallback placeholders")
    else:
        # Count available images
        webp_files = list(ILLUSTRATIONS_DIR.glob("*.webp"))
        png_files = list(ILLUSTRATIONS_DIR.glob("*.png"))
        if verbose:
            print(f"\n📸 Found {len(webp_files)} WebP + {len(png_files)} PNG illustrations")
    
    # Parse markdown
    print(f"\n📖 Parsing {MASTER_MD.name}...")
    chapters = parse_markdown_chapters(MASTER_MD)
    print(f"   Found {len(chapters)} chapters")
    
    if verbose:
        for chapter_id in sorted(chapters.keys()):
            word_count = len(chapters[chapter_id].split())
            print(f"   - {chapter_id}: {word_count:,} words")
    
    # Generate HTML based on mode
    print(f"\n🔨 Generating story HTML from template...")
    
    if mode == 'paginated':
        success = generate_paginated_story(chapters, dry_run=dry_run, verbose=verbose)
    else:
        success = update_story_html(chapters, dry_run=dry_run, verbose=verbose)
    
    if success:
        print("\n✅ Story generation complete!")
        if not dry_run:
            print(f"\n🌐 View at: http://localhost:8080/story/index.html")
            if mode == 'paginated':
                print(f"📄 Generated {len(chapters)} paginated chapter files")
            print(f"📁 Output: {STORY_HTML.relative_to(REPO_ROOT)}")
        return 0
    else:
        print("\n❌ Story generation failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
