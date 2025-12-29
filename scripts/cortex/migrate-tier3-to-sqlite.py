#!/usr/bin/env python3
"""
CORTEX Brain Tier 3 Migration Script

Purpose: Migrate development context data from YAML to SQLite
Author: CORTEX Development Team
Version: 1.0

Migrates:
- development-context.yaml → tier3_metrics

Usage:
    python migrate-tier3-to-sqlite.py [--db-path cortex-brain.db] [--source-dir cortex-brain]

Features:
- Migrates all development metrics (git, code, testing, health, patterns, correlations)
- Preserves metric history
- Maintains JSON structure for complex metrics
- Validates data integrity
- Idempotent (safe to run multiple times)
"""

import sqlite3
import yaml
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json


def get_project_root() -> Path:
    """Get CORTEX project root directory"""
    # Script is in CORTEX/scripts/
    return Path(__file__).parent.parent.absolute()


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Load YAML file and return dictionary"""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if data else {}
    except yaml.YAMLError as e:
        print(f"⚠️  Error loading {file_path}: {e}")
        return {}


def migrate_metric(cursor: sqlite3.Cursor, category: str, metric_name: str, metric_data: Any, timestamp: str) -> None:
    """
    Migrate a single metric to tier3_metrics table
    
    Args:
        cursor: Database cursor
        category: Metric category (git, code, testing, health, patterns, correlations)
        metric_name: Name of the metric
        metric_data: Metric value (can be scalar or complex object)
        timestamp: When the metric was collected
    """
    # Convert complex objects to JSON
    if isinstance(metric_data, (dict, list)):
        metric_value_json = json.dumps(metric_data)
        metric_value_text = None
        metric_value_numeric = None
    elif isinstance(metric_data, (int, float)):
        metric_value_json = None
        metric_value_text = None
        metric_value_numeric = float(metric_data)
    elif isinstance(metric_data, str):
        metric_value_json = None
        metric_value_text = metric_data
        metric_value_numeric = None
    else:
        # Convert to string for unknown types
        metric_value_json = None
        metric_value_text = str(metric_data)
        metric_value_numeric = None
    
    cursor.execute("""
        INSERT OR REPLACE INTO tier3_metrics (
            category, metric_name, metric_value_numeric, metric_value_text,
            metric_value_json, collected_at
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        category,
        metric_name,
        metric_value_numeric,
        metric_value_text,
        metric_value_json,
        timestamp
    ))


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator between keys
    
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def migrate_tier3(db_path: str, source_dir: Path) -> Dict[str, Any]:
    """
    Main migration function for Tier 3
    
    Args:
        db_path: Path to SQLite database
        source_dir: Path to cortex-brain directory
    
    Returns:
        Dictionary with migration statistics
    """
    print(f"🧠 CORTEX Brain Tier 3 Migration")
    print(f"=" * 60)
    print(f"Database: {db_path}")
    print(f"Source: {source_dir}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"✓ Connected to database")
    
    # Load development context
    print(f"\n📋 Loading development context...")
    dev_context = load_yaml_file(source_dir / "development-context.yaml")
    
    if not dev_context:
        print(f"⚠️  No development context data found")
        return {'metrics_migrated': 0, 'errors': 0}
    
    print(f"✓ Loaded development context")
    
    # Get timestamp from data or use current
    timestamp = dev_context.get('statistics', {}).get('last_updated', datetime.now().isoformat())
    
    # Migrate metrics by category
    print(f"\n🔄 Migrating metrics to database...")
    stats = {'metrics_migrated': 0, 'errors': 0}
    
    # Define categories to migrate
    categories = {
        'git_activity': 'git',
        'code_changes': 'code',
        'kds_usage': 'cortex',
        'testing_activity': 'testing',
        'project_health': 'health',
        'work_patterns': 'patterns',
        'correlations': 'correlations',
        'proactive_insights': 'insights'
    }
    
    for yaml_key, db_category in categories.items():
        if yaml_key not in dev_context:
            continue
        
        category_data = dev_context[yaml_key]
        if not isinstance(category_data, dict):
            continue
        
        # Flatten nested structure and migrate each metric
        flattened = flatten_dict(category_data)
        
        for metric_name, metric_value in flattened.items():
            try:
                migrate_metric(cursor, db_category, metric_name, metric_value, timestamp)
                stats['metrics_migrated'] += 1
            except Exception as e:
                print(f"✗ Error migrating {db_category}.{metric_name}: {e}")
                stats['errors'] += 1
    
    # Also store the complete development context as a single JSON metric
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO tier3_metrics (
                category, metric_name, metric_value_json, collected_at
            ) VALUES (?, ?, ?, ?)
        """, (
            'context',
            'full_development_context',
            json.dumps(dev_context),
            timestamp
        ))
        stats['metrics_migrated'] += 1
    except Exception as e:
        print(f"✗ Error migrating full context: {e}")
        stats['errors'] += 1
    
    # Commit changes
    conn.commit()
    print(f"✓ Changes committed")
    
    # Validate migration
    print(f"\n🔍 Validating migration...")
    cursor.execute("SELECT COUNT(*) FROM tier3_metrics")
    db_metric_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT category) FROM tier3_metrics")
    db_category_count = cursor.fetchone()[0]
    
    print(f"✓ Database contains:")
    print(f"  - {db_metric_count} metrics")
    print(f"  - {db_category_count} categories")
    
    # Close connection
    conn.close()
    
    # Print final statistics
    print(f"\n📊 Migration Statistics:")
    print(f"  Metrics migrated: {stats['metrics_migrated']}")
    print(f"  Errors: {stats['errors']}")
    print()
    
    if stats['errors'] == 0:
        print(f"✅ Tier 3 migration complete!")
    else:
        print(f"⚠️  Tier 3 migration complete with {stats['errors']} errors")
    
    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Migrate CORTEX Brain Tier 3 data to SQLite')
    parser.add_argument(
        '--db-path',
        default='cortex-brain/cortex-brain.db',
        help='Path to SQLite database (default: cortex-brain/cortex-brain.db)'
    )
    parser.add_argument(
        '--source-dir',
        default='cortex-brain',
        help='Path to cortex-brain directory (default: cortex-brain)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    project_root = get_project_root()
    db_path = project_root / args.db_path
    source_dir = project_root / args.source_dir
    
    # Run migration
    try:
        migrate_tier3(str(db_path), source_dir)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise


if __name__ == '__main__':
    main()
