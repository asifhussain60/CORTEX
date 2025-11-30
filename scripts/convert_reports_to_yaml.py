#!/usr/bin/env python3
"""
Convert referential MD completion reports to machine-readable YAML format.

Usage:
    python scripts/convert_reports_to_yaml.py --dry-run
    python scripts/convert_reports_to_yaml.py --execute
"""

import argparse
import re
from pathlib import Path
from datetime import datetime
import yaml


def extract_metadata_from_md(content: str, filename: str) -> dict:
    """Extract key metadata from markdown report"""
    metadata = {
        'filename': filename,
        'conversion_date': datetime.now().isoformat(),
        'type': 'completion_report'
    }
    
    # Extract date
    date_match = re.search(r'\*\*Date:\*\*\s+(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        metadata['date'] = date_match.group(1)
    
    # Extract status
    status_match = re.search(r'\*\*Status:\*\*\s+(.+)', content)
    if status_match:
        metadata['status'] = status_match.group(1).strip()
    
    # Extract title from first heading
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    # Extract duration if present
    duration_match = re.search(r'\*\*Duration:\*\*\s+(.+)', content)
    if duration_match:
        metadata['duration'] = duration_match.group(1).strip()
    
    return metadata


def convert_report_to_yaml(md_path: Path, output_dir: Path, dry_run: bool = False):
    """Convert a single MD report to YAML"""
    content = md_path.read_text(encoding='utf-8')
    
    # Extract metadata
    metadata = extract_metadata_from_md(content, md_path.name)
    
    # Create YAML structure
    yaml_data = {
        'metadata': metadata,
        'original_file': str(md_path),
        'content_summary': content[:500] + '...' if len(content) > 500 else content,
        'archive_location': f"cortex-brain/archives/reports-archive/{md_path.name}"
    }
    
    # Generate output filename
    yaml_filename = md_path.stem + '.yaml'
    yaml_path = output_dir / yaml_filename
    
    if dry_run:
        print(f"[DRY RUN] Would convert: {md_path.name} -> {yaml_path.name}")
        print(f"  Metadata: {metadata}")
    else:
        # Write YAML file
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
        
        # Move original to archive
        archive_path = Path('cortex-brain/archives/reports-archive') / md_path.name
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.rename(archive_path)
        
        print(f"✓ Converted: {md_path.name}")
        print(f"  YAML: {yaml_path}")
        print(f"  Archived: {archive_path}")


def main():
    parser = argparse.ArgumentParser(description='Convert MD reports to YAML')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--execute', action='store_true', help='Execute conversion')
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        return
    
    # Find all completion/summary MD files
    patterns = [
        'cortex-brain/documents/reports/*COMPLETE*.md',
        'cortex-brain/documents/summaries/*SUMMARY*.md',
    ]
    
    output_dir = Path('cortex-brain/reports-index')
    
    total = 0
    for pattern in patterns:
        for md_file in Path('.').glob(pattern):
            convert_report_to_yaml(md_file, output_dir, dry_run=args.dry_run)
            total += 1
    
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Processed {total} files")
    
    if not args.dry_run and total > 0:
        print(f"\nYAML index created at: {output_dir}")
        print(f"Original files archived at: cortex-brain/archives/reports-archive/")


if __name__ == '__main__':
    main()
