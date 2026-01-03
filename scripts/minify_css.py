"""
CSS Minification Script for CORTEX Glassmorphism Design System
Minifies all glass-*.css files for production deployment.
Preserves comments with license/copyright information.
"""

import re
from pathlib import Path
from typing import Dict


def minify_css(content: str, preserve_license: bool = True) -> str:
    """
    Minify CSS content while preserving license headers.
    
    Args:
        content: CSS file content
        preserve_license: Keep copyright/license comments
        
    Returns:
        Minified CSS string
    """
    # Extract license header (first multi-line comment block)
    license_header = ""
    if preserve_license:
        license_match = re.match(r'(/\*\*[\s\S]*?\*/)', content, re.MULTILINE)
        if license_match:
            license_header = license_match.group(1)
            # Minify license header (remove extra whitespace but keep readable)
            license_header = re.sub(r'\n\s+\*', '\n *', license_header)
            license_header = re.sub(r'\n{3,}', '\n\n', license_header)
            license_header += "\n\n"
    
    # Remove all comments (including license, will re-add later)
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    
    # Remove multiple newlines and whitespace
    content = re.sub(r'\n\s*\n+', '\n', content)
    
    # Remove whitespace around delimiters
    content = re.sub(r'\s*([{}:;,>~+])\s*', r'\1', content)
    
    # Remove whitespace before opening brace
    content = re.sub(r'\s+{', '{', content)
    
    # Remove trailing semicolons before closing brace
    content = re.sub(r';+}', '}', content)
    
    # Remove units from zero values (except in calc(), time values)
    content = re.sub(r'(?<![\w-])0(?:px|em|rem|%|vh|vw|vmin|vmax)(?![\w-])', '0', content)
    
    # Compress rgba/rgb values
    content = re.sub(r'rgba?\(\s*', 'rgba(', content)
    content = re.sub(r'\s*,\s*', ',', content)
    
    # Remove space after colon in properties
    content = re.sub(r':\s+', ':', content)
    
    # Compress media queries
    content = re.sub(r'@media\s+', '@media ', content)
    
    # Remove leading/trailing whitespace
    content = content.strip()
    
    # Add license header back
    if preserve_license and license_header:
        content = license_header + content
    
    return content


def minify_file(input_path: Path, output_path: Path) -> Dict[str, any]:
    """
    Minify a single CSS file.
    
    Args:
        input_path: Source CSS file
        output_path: Destination minified file
        
    Returns:
        Dict with original_size, minified_size, reduction_percent
    """
    # Read original file
    original_content = input_path.read_text(encoding='utf-8')
    original_size = len(original_content)
    original_lines = original_content.count('\n') + 1
    
    # Minify
    minified_content = minify_css(original_content, preserve_license=True)
    minified_size = len(minified_content)
    
    # Write minified file
    output_path.write_text(minified_content, encoding='utf-8')
    
    # Calculate savings
    reduction_bytes = original_size - minified_size
    reduction_percent = (reduction_bytes / original_size) * 100
    
    return {
        'file': input_path.name,
        'original_size': original_size,
        'minified_size': minified_size,
        'original_lines': original_lines,
        'reduction_bytes': reduction_bytes,
        'reduction_percent': reduction_percent
    }


def main():
    """Minify all glass CSS files."""
    # Paths
    css_dir = Path('docs/assets/css')
    minified_dir = css_dir / 'minified'
    minified_dir.mkdir(exist_ok=True)
    
    # Files to minify (7 glass system files)
    glass_files = [
        'glass-design-tokens.css',
        'glass-named-panels.css',
        'glass-base-patterns.css',
        'glass-ui-components.css',
        'glass-animations.css',
        'glass-utilities.css',
        'cortex-glass-system.css',
    ]
    
    print("=" * 70)
    print("CORTEX Glassmorphism CSS Minification")
    print("=" * 70)
    print()
    
    results = []
    
    for filename in glass_files:
        input_path = css_dir / filename
        if not input_path.exists():
            print(f"⚠️  Skipping {filename} (not found)")
            continue
        
        # Output to minified/ subdirectory with .min.css extension
        output_name = filename.replace('.css', '.min.css')
        output_path = minified_dir / output_name
        
        # Minify
        result = minify_file(input_path, output_path)
        results.append(result)
        
        # Print result
        print(f"✅ {result['file']}")
        print(f"   Original:  {result['original_size']:>8,} bytes ({result['original_lines']:>4} lines)")
        print(f"   Minified:  {result['minified_size']:>8,} bytes")
        print(f"   Saved:     {result['reduction_bytes']:>8,} bytes ({result['reduction_percent']:.1f}%)")
        print()
    
    # Summary
    total_original = sum(r['original_size'] for r in results)
    total_minified = sum(r['minified_size'] for r in results)
    total_saved = total_original - total_minified
    total_percent = (total_saved / total_original) * 100
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files Processed:  {len(results)}")
    print(f"Total Original:   {total_original:>12,} bytes ({total_original / 1024:.1f} KB)")
    print(f"Total Minified:   {total_minified:>12,} bytes ({total_minified / 1024:.1f} KB)")
    print(f"Total Saved:      {total_saved:>12,} bytes ({total_saved / 1024:.1f} KB)")
    print(f"Reduction:        {total_percent:>11.1f}%")
    print()
    print(f"📁 Minified files saved to: {minified_dir}")
    print()


if __name__ == '__main__':
    main()
