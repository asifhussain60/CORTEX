#!/usr/bin/env python3
"""
CORTEX Story - Advanced Markdown to HTML Converter
Maintains speaker consistency and contextual image placement
"""

import re
from pathlib import Path

class DialogueTracker:
    """Track conversation flow to maintain speaker consistency"""
    def __init__(self):
        self.last_speaker = None
        self.context_buffer = []
    
    def identify_speaker(self, paragraph, quote):
        """
        Identify speaker based on narrative attribution and context.
        Returns 'asif' or 'miss-g'
        """
        # First check attribution AFTER the quote in the paragraph
        quote_pos = paragraph.find(f'"{quote}"')
        if quote_pos != -1:
            after_quote = paragraph[quote_pos + len(quote) + 2:quote_pos + len(quote) + 100]
            before_quote = paragraph[max(0, quote_pos - 100):quote_pos]
            
            # Miss G attribution patterns
            if re.search(r'(Miss\s+G|she\|She)\s+(said|asked|replied|voice|continued)', after_quote, re.IGNORECASE):
                return 'miss-g'
            if re.search(r'(Miss\s+G|she|She)\s+(said|asked|replied|voice|continued)', before_quote, re.IGNORECASE):
                return 'miss-g'
            
            # Asif attribution patterns (I said, I replied, etc.)
            if re.search(r'\bI\s+(said|asked|replied|shouted|muttered|whispered|admitted|sighed|laughed|told|gestured)', after_quote, re.IGNORECASE):
                return 'asif'
            if re.search(r'(said|asked|replied|shouted|muttered|whispered|admitted|sighed|laughed|told|gestured)\s+\bI\b', before_quote, re.IGNORECASE):
                return 'asif'
        
        # Check for Miss G's voice/name in the full paragraph
        if re.search(r'Miss\s+G', paragraph):
            return 'miss-g'
        
        # Analyze quote content for first-person indicators (Asif is the narrator)
        first_person_words = [
            r"\bI\b", r"\bI'm\b", r"\bI've\b", r"\bI'll\b", r"\bI'd\b",
            r"\bmy\b", r"\bme\b", r"\bmine\b", r"\bmyself\b"
        ]
        
        is_first_person = any(re.search(pattern, quote, re.IGNORECASE) for pattern in first_person_words)
        
        if is_first_person:
            return 'asif'
        
        # Use alternating pattern as fallback
        if self.last_speaker == 'asif':
            return 'miss-g'
        else:
            return 'asif'
    
    def wrap_dialogue(self, paragraph):
        """Wrap all quoted dialogue in the paragraph with consistent speaker classes"""
        quotes = re.findall(r'"([^"]+)"', paragraph)
        
        if not quotes:
            return paragraph
        
        result = paragraph
        
        # Process quotes in order
        for quote in quotes:
            speaker = self.identify_speaker(paragraph, quote)
            self.last_speaker = speaker
            
            css_class = f'dialogue-{speaker}'
            
            # Replace this specific quote
            old_quote = f'"{quote}"'
            new_quote = f'<span class="{css_class}">"{quote}"</span>'
            result = result.replace(old_quote, new_quote, 1)
        
        return result

def convert_markdown_to_html(md_content):
    """Convert markdown to clean HTML with proper dialogue coloring"""
    
    # Remove YAML front matter
    md_content = re.sub(r'^---\n.*?\n---\n', '', md_content, flags=re.DOTALL)
    
    # Remove stylesheet links and wrapper divs
    md_content = re.sub(r'<link.*?>', '', md_content)
    md_content = re.sub(r'<div class="story-container">\s*<div class="story-content">', '', md_content)
    md_content = re.sub(r'</div>\s*<div class="chapter-navigation">.*?</div>\s*</div>\s*$', '', md_content, flags=re.DOTALL)
    
    # Initialize dialogue tracker
    tracker = DialogueTracker()
    
    html_lines = []
    in_code_block = False
    code_lines = []
    
    lines = md_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Skip empty wrapper divs
        if line.strip() in ['<div class="story-container">', '<div class="story-content">', '</div>']:
            i += 1
            continue
        
        # Handle code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lines = []
            else:
                html_lines.append('<pre><code>')
                html_lines.extend(code_lines)
                html_lines.append('</code></pre>')
                in_code_block = False
                code_lines = []
            i += 1
            continue
        
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
            i += 1
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
            i += 1
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
            i += 1
        
        # Handle images - preserve position classes
        elif '<img' in line:
            src_match = re.search(r'src="([^"]+)"', line)
            alt_match = re.search(r'alt="([^"]+)"', line)
            
            src = src_match.group(1) if src_match else ''
            alt = alt_match.group(1) if alt_match else ''
            
            # Determine position from existing class or style attribute
            if 'right' in line.lower():
                css_class = 'story-image-right'
            elif 'left' in line.lower():
                css_class = 'story-image-left'
            elif 'center' in line.lower():
                css_class = 'story-image-center'
            else:
                css_class = 'story-image-center'
            
            html_lines.append(f'<img src="{src}" alt="{alt}" class="{css_class}">')
            i += 1
        
        # Handle horizontal rules
        elif line.strip() == '---':
            html_lines.append('<hr>')
            i += 1
        
        # Handle paragraphs - collect multi-line paragraphs
        elif line.strip() and not line.startswith('<') and line.strip() != '---':
            para_lines = [line]
            i += 1
            
            # Collect continuation lines for the same paragraph
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') and not lines[i].startswith('<img') and not lines[i].startswith('```') and lines[i].strip() != '---':
                para_lines.append(lines[i].rstrip())
                i += 1
            
            para_text = ' '.join(para_lines)
            
            # Apply dialogue detection with consistent speaker tracking
            para_text = tracker.wrap_dialogue(para_text)
            
            # Handle markdown formatting
            para_text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para_text)
            para_text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', para_text)
            para_text = re.sub(r'_([^_]+)_', r'<em>\1</em>', para_text)
            
            # Handle inline code
            para_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', para_text)
            
            html_lines.append(f'<p>{para_text}</p>')
        else:
            i += 1
    
    return '\n\n'.join(html_lines)

def create_html_document(title, body_html):
    """Create complete HTML document"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - The Awakening of CORTEX</title>
<link rel="stylesheet" href="../story-styles.css">
</head>
<body>

{body_html}

</body>
</html>"""

def convert_chapter(chapter_folder, chapter_title):
    """Convert a single chapter from markdown to HTML"""
    print(f"Converting {chapter_title}...")
    
    story_dir = Path(__file__).parent
    md_file = story_dir / chapter_folder / 'index.md'
    html_file = story_dir / chapter_folder / 'index.html'
    
    if not md_file.exists():
        print(f"  ⚠ {md_file} not found")
        return False
    
    try:
        # Read markdown
        md_content = md_file.read_text(encoding='utf-8')
        
        # Convert to HTML
        body_html = convert_markdown_to_html(md_content)
        
        # Create full HTML document
        full_html = create_html_document(chapter_title, body_html)
        
        # Write HTML
        html_file.write_text(full_html, encoding='utf-8')
        print(f"  ✓ Created {html_file.name}")
        return True
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Convert all chapters"""
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
    
    success_count = 0
    total_count = len(chapters)
    
    for folder, title in chapters:
        if convert_chapter(folder, title):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Converted {success_count}/{total_count} chapters successfully!")
    print(f"{'='*60}")
    
    if success_count == total_count:
        print("\n🎉 All chapters converted with:")
        print("  • Consistent speaker color tracking")
        print("  • Contextual image placement (left/right on desktop)")
        print("  • Mobile-friendly centered images (via CSS)")
        print("  • Clean semantic HTML structure")

if __name__ == '__main__':
    main()
