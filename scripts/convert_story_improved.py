#!/usr/bin/env python3
"""
Improved dialogue detection for CORTEX Story
Uses context and speaker attribution to determine proper color classes
"""

import re
from pathlib import Path

def identify_speaker_and_wrap(text):
    """
    Identify the speaker based on context and wrap dialogue appropriately.
    Cyan (#00d4ff) - Asif (protagonist, narrator)
    Purple (#9d4edd) - Miss G, Copilot, CORTEX, clients
    """
    lines = []
    last_speaker = None
    
    # Split into paragraphs
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        if not para.strip():
            continue
            
        # Check if paragraph starts with speaker attribution
        miss_g_indicators = [
            'Miss G', '"Miss G', 'she said', 'She said', 'she asked', 
            'She asked', 'her voice', 'Her voice'
        ]
        asif_indicators = [
            'I said', 'I asked', 'I replied', 'I shouted', 'I muttered',
            'I whispered', 'I admitted', 'I sighed', 'I laughed'
        ]
        
        # Find all quoted text
        quotes = re.findall(r'"([^"]+)"', para)
        
        if not quotes:
            lines.append(para)
            continue
        
        # Determine speaker based on context
        is_miss_g = any(ind in para for ind in miss_g_indicators)
        is_asif = any(ind in para for ind in asif_indicators)
        
        # Process paragraph
        result = para
        
        for quote in quotes:
            # Determine class based on context or last speaker
            if is_miss_g:
                css_class = 'dialogue-miss-g'
                last_speaker = 'miss-g'
            elif is_asif:
                css_class = 'dialogue-asif'
                last_speaker = 'asif'
            else:
                # Use alternating pattern or content analysis
                if last_speaker == 'miss-g':
                    css_class = 'dialogue-asif'
                    last_speaker = 'asif'
                else:
                    # Analyze content - first person usually Asif
                    first_person = bool(re.search(r'\bI\b|\bmy\b|\bme\b|\bI\'', quote))
                    if first_person:
                        css_class = 'dialogue-asif'
                        last_speaker = 'asif'
                    else:
                        css_class = 'dialogue-miss-g'
                        last_speaker = 'miss-g'
            
            # Replace in result
            result = result.replace(f'"{quote}"', f'<span class="{css_class}">"{quote}"</span>', 1)
        
        lines.append(result)
    
    return '\n\n'.join(lines)

def markdown_to_html_improved(md_content, chapter_title):
    """
    Improved markdown to HTML conversion with better dialogue detection
    """
    # Remove YAML front matter
    md_content = re.sub(r'^---\n.*?\n---\n', '', md_content, flags=re.DOTALL)
    
    # Remove stylesheet links and wrapper divs
    md_content = re.sub(r'<link.*?>', '', md_content)
    md_content = re.sub(r'<div class="story-container">\s*<div class="story-content">', '', md_content)
    md_content = re.sub(r'</div>\s*<div class="chapter-navigation">.*?</div>\s*</div>\s*$', '', md_content, flags=re.DOTALL)
    
    html_parts = []
    in_code_block = False
    code_content = []
    
    lines = md_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Handle code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_content = []
            else:
                html_parts.append('<pre><code>' + '\n'.join(code_content) + '</code></pre>')
                in_code_block = False
                code_content = []
            i += 1
            continue
        
        if in_code_block:
            code_content.append(line)
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            html_parts.append(f'<h1>{line[2:]}</h1>')
            i += 1
        elif line.startswith('## '):
            html_parts.append(f'<h2>{line[3:]}</h2>')
            i += 1
        elif line.startswith('### '):
            html_parts.append(f'<h3>{line[4:]}</h3>')
            i += 1
        
        # Handle images
        elif '<img' in line:
            src_match = re.search(r'src="([^"]+)"', line)
            alt_match = re.search(r'alt="([^"]+)"', line)
            
            src = src_match.group(1) if src_match else ''
            alt = alt_match.group(1) if alt_match else ''
            
            if 'right' in line.lower():
                html_parts.append(f'<img src="{src}" alt="{alt}" class="story-image-right">')
            elif 'left' in line.lower():
                html_parts.append(f'<img src="{src}" alt="{alt}" class="story-image-left">')
            else:
                html_parts.append(f'<img src="{src}" alt="{alt}" class="story-image-center">')
            i += 1
        
        # Handle paragraphs - collect multi-line paragraphs
        elif line.strip() and not line.startswith('<'):
            paragraph_lines = [line]
            i += 1
            
            # Collect continuation lines
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') and not lines[i].startswith('<img') and not lines[i].startswith('```'):
                paragraph_lines.append(lines[i])
                i += 1
            
            para_text = ' '.join(paragraph_lines)
            
            # Apply dialogue detection
            para_text = identify_speaker_and_wrap(para_text)
            
            # Handle markdown formatting
            para_text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para_text)
            para_text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', para_text)
            para_text = re.sub(r'_([^_]+)_', r'<em>\1</em>', para_text)
            
            html_parts.append(f'<p>{para_text}</p>')
        else:
            i += 1
    
    return '\n\n'.join(html_parts)

def convert_chapter(chapter_folder, chapter_title):
    """Convert a single chapter"""
    print(f"Converting {chapter_title}...")
    
    md_file = Path('docs/story') / chapter_folder / 'index.md'
    html_file = Path('docs/story') / chapter_folder / 'index.html'
    
    if not md_file.exists():
        print(f"  ⚠ {md_file} not found")
        return
    
    # Read markdown
    md_content = md_file.read_text(encoding='utf-8')
    
    # Convert to HTML
    html_body = markdown_to_html_improved(md_content, chapter_title)
    
    # Create full HTML document
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{chapter_title} - The Awakening of CORTEX</title>
</head>
<body>

{html_body}

</body>
</html>"""
    
    # Write HTML
    html_file.write_text(full_html, encoding='utf-8')
    print(f"  ✓ Created {html_file}")

def main():
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
        convert_chapter(folder, title)
    
    print("\n✅ All chapters converted!")

if __name__ == '__main__':
    main()
