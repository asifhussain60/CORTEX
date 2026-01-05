#!/usr/bin/env python3
"""
Generate a focused summary of the docs link analysis
"""

import json
from pathlib import Path

def main():
    report_path = Path('docs-link-analysis-report.json')
    
    with open(report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create focused summary
    summary = {
        'statistics': data['statistics'],
        'root_files': data['root_files'],
        'suggested_moves': data['suggested_moves'],
        'orphaned_html_files': data['orphaned_html_files'][:50],  # First 50
        'orphaned_count_total': len(data['orphaned_html_files']),
        
        # Most linked-to files (hub pages)
        'hub_pages': [],
        
        # Files linked from index.html
        'index_direct_links': sorted(data['link_graph'].get('index.html', []))[:30]
    }
    
    # Find hub pages (most referenced files)
    reverse_links = data['reverse_links']
    link_counts = [(file, len(sources)) for file, sources in reverse_links.items() if file.endswith('.html')]
    link_counts.sort(key=lambda x: x[1], reverse=True)
    summary['hub_pages'] = link_counts[:20]
    
    # Save focused summary
    output_path = Path('docs-link-analysis-SUMMARY.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Summary saved to: {output_path}")
    
    # Print key insights
    print("\n" + "="*80)
    print("🎯 KEY INSIGHTS")
    print("="*80)
    
    print("\n📍 Most Referenced Files (Hub Pages):")
    for file, count in summary['hub_pages'][:10]:
        print(f"  {count:3d} links → {file}")
    
    print(f"\n📄 Files Linked Directly from index.html: {len(data['link_graph'].get('index.html', []))}")
    print("  First 10:")
    for link in summary['index_direct_links'][:10]:
        print(f"    • {link}")
    
    print(f"\n🏝️  Total Orphaned HTML Files: {summary['orphaned_count_total']}")
    print(f"💾 Root Files to Process: {len(data['root_files']['unlinked'])}")

if __name__ == '__main__':
    main()
