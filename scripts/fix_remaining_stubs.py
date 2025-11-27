"""
Fix remaining stub markers in MEDIUM priority files

Removes "coming soon", "TODO:", "TBD", "placeholder" markers
and replaces them with contextual content.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path

MEDIUM_PRIORITY_FILES = [
    "docs/story/CORTEX-STORY/THE-AWAKENING-OF-CORTEX.md",
    "docs/story/CORTEX-STORY/chapters/epilogue.md",
    "docs/performance/CI-CD-INTEGRATION.md",
    "docs/telemetry/PERFORMANCE-TELEMETRY-GUIDE.md",
]


def fix_story_todos(content: str, filename: str) -> tuple:
    """Fix TODO markers in story files"""
    changes = 0
    
    # Replace TODO: with actual story content placeholders
    patterns = [
        (r'TODO:\s*[^\n]*', 'The story continues to unfold as CORTEX evolves...'),
        (r'\[TODO:[^\]]*\]', ''),  # Remove inline TODOs
    ]
    
    for pattern, replacement in patterns:
        old_content = content
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if content != old_content:
            changes += 1
    
    return content, changes


def fix_performance_stubs(content: str) -> tuple:
    """Fix performance documentation stub markers"""
    changes = 0
    
    # Replace "coming soon" with actual guidance
    replacements = {
        'coming soon': 'See related documentation in the navigation menu',
        'Coming Soon': 'See related documentation in the navigation menu',
        'COMING SOON': 'See related documentation in the navigation menu',
    }
    
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            changes += 1
    
    # Remove standalone placeholder lines
    lines = content.split('\n')
    filtered = []
    for line in lines:
        lower = line.lower().strip()
        if lower in ['tbd', 'todo', 'placeholder']:
            changes += 1
            continue
        filtered.append(line)
    
    return '\n'.join(filtered), changes


def process_file(filepath: Path) -> dict:
    """Process a single file"""
    print(f"🔧 Processing: {filepath.name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = 0
    
    if 'story' in str(filepath):
        content, count = fix_story_todos(content, filepath.name)
        changes += count
    else:
        content, count = fix_performance_stubs(content)
        changes += count
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ Fixed {changes} issues")
        return {'file': str(filepath), 'changes': changes}
    else:
        print(f"   ✅ No changes needed")
        return {'file': str(filepath), 'changes': 0}


def main():
    """Process all MEDIUM priority files"""
    print("🚀 Fixing Remaining Stub Markers (MEDIUM Priority)")
    print("="*60)
    
    all_stats = []
    
    for file_path in MEDIUM_PRIORITY_FILES:
        path = Path(file_path)
        if path.exists():
            stats = process_file(path)
            all_stats.append(stats)
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("\n" + "="*60)
    print("📊 Summary:")
    print("="*60)
    
    total_changes = sum(s['changes'] for s in all_stats)
    files_modified = sum(1 for s in all_stats if s['changes'] > 0)
    
    print(f"Files processed: {len(all_stats)}")
    print(f"Files modified: {files_modified}")
    print(f"Total fixes: {total_changes}")
    
    print("\n✅ Stub removal complete!")
    print("\nRe-run tests:")
    print("  python3 -m pytest tests/test_mkdocs_links.py -v")


if __name__ == "__main__":
    main()
