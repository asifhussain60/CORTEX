#!/usr/bin/env python3
"""
Optimize story images from PNG to WebP format.

Target: <100KB per image with 85-90 quality.
Preserves original PNGs as fallback.
"""
import os
from pathlib import Path
from PIL import Image
import sys


def optimize_image(png_path: Path, output_dir: Path, quality: int = 88) -> dict:
    """
    Convert PNG to WebP with specified quality.
    
    Returns dict with size info for reporting.
    """
    try:
        # Open and convert image
        img = Image.open(png_path)
        
        # Create WebP filename
        webp_filename = png_path.stem + '.webp'
        webp_path = output_dir / webp_filename
        
        # Save as WebP with quality setting
        img.save(webp_path, 'WEBP', quality=quality, method=6)
        
        # Get size info
        original_size = png_path.stat().st_size
        webp_size = webp_path.stat().st_size
        reduction = (1 - webp_size / original_size) * 100
        
        return {
            'filename': png_path.name,
            'original_kb': original_size / 1024,
            'webp_kb': webp_size / 1024,
            'reduction_pct': reduction,
            'success': True,
            'webp_path': str(webp_path)
        }
    except Exception as e:
        return {
            'filename': png_path.name,
            'success': False,
            'error': str(e)
        }


def main():
    """Process all PNG images in illustrations/images directory."""
    # Setup paths
    script_dir = Path(__file__).parent.parent
    images_dir = script_dir / 'docs' / 'story' / 'illustrations' / 'images'
    
    if not images_dir.exists():
        print(f"❌ Error: Images directory not found: {images_dir}")
        sys.exit(1)
    
    # Find all PNG files
    png_files = sorted(images_dir.glob('*.png'))
    
    if not png_files:
        print(f"❌ Error: No PNG files found in {images_dir}")
        sys.exit(1)
    
    print(f"🖼️  Found {len(png_files)} PNG images to optimize\n")
    
    # Process each image
    results = []
    for png_path in png_files:
        print(f"Processing {png_path.name}...", end=' ')
        result = optimize_image(png_path, images_dir, quality=88)
        results.append(result)
        
        if result['success']:
            print(f"✅ {result['original_kb']:.1f}KB → {result['webp_kb']:.1f}KB ({result['reduction_pct']:.1f}% smaller)")
        else:
            print(f"❌ Error: {result['error']}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 OPTIMIZATION SUMMARY")
    print("="*70)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    if successful:
        total_original = sum(r['original_kb'] for r in successful)
        total_webp = sum(r['webp_kb'] for r in successful)
        total_saved = total_original - total_webp
        avg_reduction = sum(r['reduction_pct'] for r in successful) / len(successful)
        
        print(f"✅ Successful: {len(successful)}/{len(results)}")
        print(f"📦 Original size: {total_original / 1024:.2f} MB")
        print(f"📦 WebP size: {total_webp / 1024:.2f} MB")
        print(f"💾 Space saved: {total_saved / 1024:.2f} MB ({avg_reduction:.1f}% average reduction)")
        
        # Check if any are over 100KB
        over_100kb = [r for r in successful if r['webp_kb'] > 100]
        if over_100kb:
            print(f"\n⚠️  Warning: {len(over_100kb)} images over 100KB target:")
            for r in over_100kb:
                print(f"   - {r['filename']}: {r['webp_kb']:.1f}KB")
            print("   Consider reducing quality further if needed")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for r in failed:
            print(f"   - {r['filename']}: {r['error']}")
    
    print("\n✅ Optimization complete!")
    print(f"📁 WebP files saved to: {images_dir}")
    
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
