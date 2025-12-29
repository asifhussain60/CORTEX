#!/usr/bin/env python3
"""
Convert CORTEX Story chapters from Markdown to HTML with proper CSS classes
Replaces inline styles with semantic classes for purple/cyan dialogue colors
"""

import re
import os
from pathlib import Path

def wrap_dialogue_with_class(text):
    """
    Wrap quoted dialogue with appropriate CSS classes.
    Purple for everyone except Asif (cyan).
    """
    # Pattern to match quoted text
    dialogue_pattern = r'"([^"]+)"'
    
    def replace_dialogue(match):
        dialogue = match.group(1)
        # Simple heuristic: If dialogue contains "I" or starts with verbs common to Asif, it's probably Asif
        # Otherwise, it's likely Miss G, Copilot, or CORTEX (all purple)
        asif_indicators = ['I ', ' I ', "I'm", "I've", "I'll", 'my ', ' my', 'me ', ' me']
        
        is_asif = any(indicator in dialogue for indicator in asif_indicators)
        
        if is_asif:
            return f'<span class="dialogue-asif">"{dialogue}"</span>'
        else:
            return f'<span class="dialogue-miss-g">"{dialogue}"</span>'
    
    return re.sub(dialogue_pattern, replace_dialogue, text)

def markdown_to_html(md_content):
    """
    Convert markdown to HTML with proper CSS classes
    """
    # Remove YAML front matter
    md_content = re.sub(r'^---\n.*?\n---\n', '', md_content, flags=re.DOTALL)
    
    # Remove markdown link to stylesheet (will be handled by viewer)
    md_content = re.sub(r'<link.*?story-styles\.css.*?>', '', md_content)
    
    # Remove wrapper divs
    md_content = re.sub(r'<div class="story-container">\s*<div class="story-content">', '', md_content)
    md_content = re.sub(r'</div>\s*<div class="chapter-navigation">.*?</div>\s*</div>\s*$', '', md_content, flags=re.DOTALL)
    
    html_lines = []
    in_code_block = False
    
    for line in md_content.split('\n'):
        # Skip empty wrapper divs and navigation
        if '<div class=' in line or '</div>' in line:
            continue
            
        # Handle code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                html_lines.append('<pre><code>')
                in_code_block = True
            else:
                html_lines.append('</code></pre>')
                in_code_block = False
            continue
            
        if in_code_block:
            html_lines.append(line)
            continue
        
        # Handle headers
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
        
        # Handle images - convert to proper class-based styling
        elif '<img' in line:
            # Extract src and alt
            src_match = re.search(r'src="([^"]+)"', line)
            alt_match = re.search(r'alt="([^"]+)"', line)
            
            src = src_match.group(1) if src_match else ''
            alt = alt_match.group(1) if alt_match else ''
            
            # Determine position from class or style attribute
            if 'right' in line.lower():
                html_lines.append(f'<img src="{src}" alt="{alt}" class="story-image-right">')
            elif 'left' in line.lower():
                html_lines.append(f'<img src="{src}" alt="{alt}" class="story-image-left">')
            else:
                html_lines.append(f'<img src="{src}" alt="{alt}" class="story-image-center">')
        
        # Handle paragraphs
        elif line.strip() and not line.startswith('<'):
            # Wrap dialogue in classes
            processed_line = wrap_dialogue_with_class(line)
            
            # Handle emphasis and strong
            processed_line = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', processed_line)
            processed_line = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', processed_line)
            processed_line = re.sub(r'_([^_]+)_', r'<em>\1</em>', processed_line)
            
            html_lines.append(f'<p>{processed_line}</p>')
        
        elif line.strip():
            html_lines.append(line)
    
    return '\n'.join(html_lines)

def create_html_chapter(chapter_name, md_file, output_file):
    """
    Create HTML chapter file from markdown
    """
    print(f"Converting {chapter_name}...")
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    html_content = markdown_to_html(md_content)
    
    # Create full HTML document
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{chapter_name} - The Awakening of CORTEX</title>
<link rel="stylesheet" href="../story-styles.css">
</head>
<body>

{html_content}

</body>
</html>"""
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✓ Created {output_file}")

def main():
    """
    Convert all chapters from markdown to HTML
    """
    story_dir = Path(__file__).parent
    
    chapters = [
        ('Prologue', 'Prologue: The Basement Laboratory'),
        ('Chapter-01', 'Chapter 1: The Amnesia Crisis'),
        ('Chapter-02', 'Chapter 2: Tier 0 - The Gatekeeper'),
        ('Chapter-03', 'Chapter 3: Tier 1 - Memory Awakens'),
        ('Chapter-04', 'Chapter 4: Tier 2 - The Learning Machine'),
        ('Chapter-05', 'Chapter 5: The Test-Driven Rebellion'),
        ('Chapter-06', 'Chapter 6: The Great Orchestration'),
        ('Chapter-07', 'Chapter 7: The Planning Revolution'),
        ('Chapter-08', 'Chapter 8: The Enterprise Awakening'),
        ('Chapter-09', 'Chapter 9: The Sanitizer\'s Dilemma'),
        ('Chapter-10', 'Chapter 10: The Self-Healing System'),
        ('Chapter-11', 'Chapter 11: The Knowledge Keeper'),
        ('Chapter-12', 'Chapter 12: The Convergence'),
        ('Chapter-13', 'Chapter 13: The Refiner'),
    ]
    
    for folder, title in chapters:
        md_file = story_dir / folder / 'index.md'
        html_file = story_dir / folder / 'index.html'
        
        if md_file.exists():
            create_html_chapter(title, md_file, html_file)
        else:
            print(f"⚠ Warning: {md_file} not found")
    
    print("\n✅ All chapters converted to HTML!")

if __name__ == '__main__':
    main()
