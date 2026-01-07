"""
Duplicate Content Detector

Detects duplicate content between copilot-instructions.md and CORTEX.prompt.md.

Algorithm:
- Extract all sections >3 lines
- Calculate similarity using difflib
- Flag sections with >80% similarity

Usage:
    python scripts/detect_duplicates.py

Author: Asif Hussain
"""

import difflib
from pathlib import Path
from typing import List, Dict, Tuple

CORTEX_ROOT = Path(__file__).resolve().parents[1]
FILE1 = CORTEX_ROOT / ".github" / "copilot-instructions.md"
FILE2 = CORTEX_ROOT / ".github" / "prompts" / "CORTEX.prompt.md"


def extract_sections(content: str, min_lines: int = 3) -> List[Tuple[int, str]]:
    """Extract sections with at least min_lines."""
    sections = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        # Look for section headers (## or ###)
        if lines[i].startswith('##'):
            start_line = i
            section_lines = [lines[i]]
            i += 1
            
            # Collect lines until next section or end
            while i < len(lines) and not lines[i].startswith('##'):
                section_lines.append(lines[i])
                i += 1
            
            if len(section_lines) >= min_lines:
                sections.append((start_line + 1, '\n'.join(section_lines)))
        else:
            i += 1
    
    return sections


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two texts."""
    return difflib.SequenceMatcher(None, text1, text2).ratio()


def find_duplicates(threshold: float = 0.8) -> Dict[str, List]:
    """Find duplicate sections between files."""
    results = {
        'duplicates': [],
        'total_duplication': 0,
        'file1_lines': 0,
        'file2_lines': 0
    }
    
    content1 = FILE1.read_text(encoding='utf-8')
    content2 = FILE2.read_text(encoding='utf-8')
    
    results['file1_lines'] = len(content1.split('\n'))
    results['file2_lines'] = len(content2.split('\n'))
    
    sections1 = extract_sections(content1)
    sections2 = extract_sections(content2)
    
    duplicated_lines = 0
    
    for line1, section1 in sections1:
        for line2, section2 in sections2:
            similarity = calculate_similarity(section1, section2)
            
            if similarity >= threshold:
                section1_lines = len(section1.split('\n'))
                results['duplicates'].append({
                    'file1_line': line1,
                    'file2_line': line2,
                    'similarity': similarity,
                    'lines': section1_lines,
                    'preview': section1[:100] + '...'
                })
                duplicated_lines += section1_lines
                break  # Don't count same section multiple times
    
    # Calculate duplication percentage
    total_lines = results['file1_lines'] + results['file2_lines']
    results['total_duplication'] = (duplicated_lines / total_lines * 100) if total_lines > 0 else 0
    
    return results


def main():
    """Run duplicate detection."""
    print("=" * 80)
    print("CORTEX Duplicate Content Detector")
    print("=" * 80)
    print()
    
    print(f"[*] File 1: {FILE1.relative_to(CORTEX_ROOT)}")
    print(f"[*] File 2: {FILE2.relative_to(CORTEX_ROOT)}")
    print()
    
    results = find_duplicates()
    
    print(f"[#] File 1: {results['file1_lines']} lines")
    print(f"[#] File 2: {results['file2_lines']} lines")
    print(f"[#] Total: {results['file1_lines'] + results['file2_lines']} lines")
    print()
    
    if results['duplicates']:
        print(f"[X] Found {len(results['duplicates'])} duplicate sections:")
        print(f"   Duplication: {results['total_duplication']:.1f}%")
        print()
        
        for i, dup in enumerate(results['duplicates'], 1):
            print(f"   {i}. Similarity: {dup['similarity']:.0%} ({dup['lines']} lines)")
            print(f"      File 1 line {dup['file1_line']}, File 2 line {dup['file2_line']}")
            # Skip preview to avoid emoji encoding issues
            print()
    else:
        print("[OK] No duplicate content detected!")
        print(f"   Duplication: {results['total_duplication']:.1f}%")
    
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    if results['total_duplication'] > 10:
        print("[!] Consider consolidating duplicate content using includes/ system")
        return 1
    else:
        print("[OK] Duplication level acceptable")
        return 0


if __name__ == "__main__":
    exit(main())
