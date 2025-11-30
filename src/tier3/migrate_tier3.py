#!/usr/bin/env python3
"""
CORTEX Tier 3 Migration Script
Migrates development context from YAML to JSON (optimized structure)

Task 0.5.3: Tier 3 Migration Script
Duration: 30-45 minutes
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict
import argparse
import yaml


class Tier3Migrator:
    """Migrates Tier 3 development context from YAML to JSON"""
    
    def __init__(self, source_yaml: Path, target_json: Path):
        """
        Initialize migrator
        
        Args:
            source_yaml: Path to development-context.yaml
            target_json: Path to target JSON file
        """
        self.source_yaml = source_yaml
        self.target_json = target_json
        self.stats = {
            'sections_migrated': 0,
            'errors': []
        }
    
    def migrate(self) -> Dict:
        """
        Execute migration from YAML to JSON
        
        Returns:
            Migration statistics dictionary
        """
        if not self.source_yaml.exists():
            self.stats['errors'].append(f"Source file not found: {self.source_yaml}")
            return self.stats
        
        try:
            # Read YAML
            print(f"Reading from {self.source_yaml}...")
            with open(self.source_yaml, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                data = {}
            
            # Add metadata
            data['migrated_at'] = datetime.now().isoformat()
            data['version'] = '1.0'
            
            # Ensure target directory exists
            self.target_json.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON
            print(f"Writing to {self.target_json}...")
            with open(self.target_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Count sections
            self.stats['sections_migrated'] = len(data.keys())
            
            print("\nMigration complete!")
            print(f"Sections migrated: {self.stats['sections_migrated']}")
            
            # List sections
            print("\nSections:")
            for section in sorted(data.keys()):
                if section not in ['migrated_at', 'version']:
                    print(f"  - {section}")
            
            return self.stats
            
        except Exception as e:
            self.stats['errors'].append(f"Migration error: {str(e)}")
            print(f"ERROR: {str(e)}")
            return self.stats


def main():
    parser = argparse.ArgumentParser(
        description='Migrate CORTEX Tier 3 data from YAML to JSON'
    )
    parser.add_argument(
        '--source',
        type=Path,
        help='Source development-context.yaml file',
        default=Path(__file__).parent.parent.parent.parent / 
                'cortex-brain' / 'development-context.yaml'
    )
    parser.add_argument(
        '--target',
        type=Path,
        help='Target JSON file',
        default=Path(__file__).parent.parent.parent.parent / 
                'cortex-brain' / 'corpus-callosum' / 'tier3' / 'development-context.json'
    )
    
    args = parser.parse_args()
    
    # Run migration
    migrator = Tier3Migrator(args.source, args.target)
    stats = migrator.migrate()
    
    # Exit with error code if there were errors
    if stats['errors']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
