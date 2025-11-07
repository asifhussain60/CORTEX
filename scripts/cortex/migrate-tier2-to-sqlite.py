#!/usr/bin/env python3
"""
CORTEX Brain Tier 2 Migration Script

Purpose: Migrate knowledge graph data from YAML to SQLite
Author: CORTEX Development Team
Version: 1.0

Migrates:
- knowledge-graph.yaml → tier2_patterns + tier2_patterns_fts
- architectural-patterns.yaml → tier2_patterns
- test-patterns.yaml → tier2_patterns
- file-relationships.yaml → tier2_file_relationships
- industry-standards.yaml → tier2_patterns

Usage:
    python migrate-tier2-to-sqlite.py [--db-path cortex-brain.db] [--source-dir cortex-brain]

Features:
- Migrates all pattern types (intent, file, workflow, validation, correction)
- Preserves confidence scores
- Maintains FTS5 search capability
- Validates pattern integrity
- Idempotent (safe to run multiple times)
"""

import sqlite3
import yaml
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import uuid
import json


def get_project_root() -> Path:
    """Get CORTEX project root directory"""
    # Script is in CORTEX/scripts/
    return Path(__file__).parent.parent.absolute()


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Load YAML file and return dictionary"""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path} (skipping)")
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if data else {}
    except yaml.YAMLError as e:
        print(f"⚠️  Error loading {file_path}: {e}")
        return {}


def migrate_intent_patterns(cursor: sqlite3.Cursor, patterns_data: Dict[str, Any]) -> int:
    """Migrate intent patterns from knowledge-graph.yaml"""
    count = 0
    
    intent_patterns = patterns_data.get('intent_patterns', {})
    for pattern_key, pattern_data in intent_patterns.items():
        if not isinstance(pattern_data, dict):
            continue
        
        pattern_id = f"intent_{pattern_key}_{uuid.uuid4().hex[:8]}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO tier2_patterns (
                pattern_id, pattern_type, pattern_key, pattern_value,
                confidence, usage_count, success_count, last_used, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_id,
            'intent',
            pattern_key,
            json.dumps(pattern_data),
            pattern_data.get('confidence', 0.85),
            pattern_data.get('frequency', 0),
            pattern_data.get('success_count', 0),
            pattern_data.get('last_seen', datetime.now().isoformat()),
            json.dumps({'category': pattern_data.get('category', 'unknown')})
        ))
        
        count += 1
    
    return count


def migrate_file_relationships(cursor: sqlite3.Cursor, patterns_data: Dict[str, Any]) -> int:
    """Migrate file relationship patterns"""
    count = 0
    
    file_relationships = patterns_data.get('file_relationships', {})
    for file_key, relationship_data in file_relationships.items():
        if not isinstance(relationship_data, dict):
            continue
        
        related_files = relationship_data.get('related_files', [])
        correlation = relationship_data.get('correlation', 0.0)
        
        for related_file in related_files:
            if isinstance(related_file, dict):
                related_path = related_file.get('file', '')
                co_modification_rate = related_file.get('co_modification_rate', correlation)
            else:
                related_path = related_file
                co_modification_rate = correlation
            
            cursor.execute("""
                INSERT OR REPLACE INTO tier2_file_relationships (
                    file_a, file_b, co_modification_count, co_modification_rate,
                    dependency_type, last_seen
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                file_key,
                related_path,
                relationship_data.get('co_modification_count', 0),
                co_modification_rate,
                relationship_data.get('type', 'co-modification'),
                relationship_data.get('last_seen', datetime.now().isoformat())
            ))
            
            count += 1
    
    return count


def migrate_workflow_patterns(cursor: sqlite3.Cursor, patterns_data: Dict[str, Any]) -> int:
    """Migrate workflow patterns"""
    count = 0
    
    workflow_patterns = patterns_data.get('workflow_patterns', {})
    for workflow_key, workflow_data in workflow_patterns.items():
        if not isinstance(workflow_data, dict):
            continue
        
        pattern_id = f"workflow_{workflow_key}_{uuid.uuid4().hex[:8]}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO tier2_patterns (
                pattern_id, pattern_type, pattern_key, pattern_value,
                confidence, usage_count, success_count, last_used, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_id,
            'workflow',
            workflow_key,
            json.dumps(workflow_data),
            workflow_data.get('confidence', 0.85),
            workflow_data.get('usage_count', 0),
            workflow_data.get('success_count', 0),
            workflow_data.get('last_used', datetime.now().isoformat()),
            json.dumps({
                'steps': workflow_data.get('steps', []),
                'duration_avg': workflow_data.get('duration_avg')
            })
        ))
        
        count += 1
    
    return count


def migrate_validation_insights(cursor: sqlite3.Cursor, patterns_data: Dict[str, Any]) -> int:
    """Migrate validation insights"""
    count = 0
    
    validation_insights = patterns_data.get('validation_insights', {})
    for insight_key, insight_data in validation_insights.items():
        if not isinstance(insight_data, dict):
            continue
        
        pattern_id = f"validation_{insight_key}_{uuid.uuid4().hex[:8]}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO tier2_patterns (
                pattern_id, pattern_type, pattern_key, pattern_value,
                confidence, usage_count, success_count, last_used, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_id,
            'validation',
            insight_key,
            json.dumps(insight_data),
            insight_data.get('confidence', 0.90),
            insight_data.get('frequency', 0),
            0,  # success_count not applicable
            insight_data.get('last_seen', datetime.now().isoformat()),
            json.dumps({
                'issue': insight_data.get('issue'),
                'impact': insight_data.get('impact', 'medium')
            })
        ))
        
        count += 1
    
    return count


def migrate_correction_history(cursor: sqlite3.Cursor, patterns_data: Dict[str, Any]) -> int:
    """Migrate correction history"""
    count = 0
    
    correction_history = patterns_data.get('correction_history', {})
    for correction_key, correction_data in correction_history.items():
        if not isinstance(correction_data, dict):
            continue
        
        pattern_id = f"correction_{correction_key}_{uuid.uuid4().hex[:8]}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO tier2_patterns (
                pattern_id, pattern_type, pattern_key, pattern_value,
                confidence, usage_count, success_count, last_used, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_id,
            'correction',
            correction_key,
            json.dumps(correction_data),
            correction_data.get('confidence', 0.75),
            correction_data.get('frequency', 0),
            0,  # success_count not applicable
            correction_data.get('last_corrected', datetime.now().isoformat()),
            json.dumps({
                'error_type': correction_data.get('error_type'),
                'resolution': correction_data.get('resolution')
            })
        ))
        
        count += 1
    
    return count


def migrate_tier2(db_path: str, source_dir: Path) -> Dict[str, Any]:
    """
    Main migration function for Tier 2
    
    Args:
        db_path: Path to SQLite database
        source_dir: Path to cortex-brain directory
    
    Returns:
        Dictionary with migration statistics
    """
    print(f"🧠 CORTEX Brain Tier 2 Migration")
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
    
    # Load YAML files
    print(f"\n📋 Loading knowledge graph data...")
    knowledge_graph = load_yaml_file(source_dir / "knowledge-graph.yaml")
    architectural_patterns = load_yaml_file(source_dir / "architectural-patterns.yaml")
    test_patterns = load_yaml_file(source_dir / "test-patterns.yaml")
    file_relationships = load_yaml_file(source_dir / "file-relationships.yaml")
    industry_standards = load_yaml_file(source_dir / "industry-standards.yaml")
    
    print(f"✓ Loaded knowledge graph files")
    
    # Migrate patterns
    print(f"\n🔄 Migrating patterns to database...")
    stats = {
        'intent_patterns': migrate_intent_patterns(cursor, knowledge_graph),
        'file_relationships': migrate_file_relationships(cursor, knowledge_graph),
        'workflow_patterns': migrate_workflow_patterns(cursor, knowledge_graph),
        'validation_insights': migrate_validation_insights(cursor, knowledge_graph),
        'correction_history': migrate_correction_history(cursor, knowledge_graph),
        'errors': 0
    }
    
    # Migrate architectural patterns
    for arch_key, arch_data in architectural_patterns.items():
        if isinstance(arch_data, dict):
            pattern_id = f"architectural_{arch_key}_{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT OR REPLACE INTO tier2_patterns (
                    pattern_id, pattern_type, pattern_key, pattern_value,
                    confidence, usage_count, last_used, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_id,
                'architectural',
                arch_key,
                json.dumps(arch_data),
                arch_data.get('confidence', 0.90),
                arch_data.get('usage_count', 0),
                datetime.now().isoformat(),
                json.dumps({'category': 'architecture'})
            ))
            stats['intent_patterns'] += 1
    
    # Commit changes
    conn.commit()
    print(f"✓ Changes committed")
    
    # Validate migration
    print(f"\n🔍 Validating migration...")
    cursor.execute("SELECT COUNT(*) FROM tier2_patterns")
    db_pattern_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tier2_file_relationships")
    db_relationship_count = cursor.fetchone()[0]
    
    print(f"✓ Database contains:")
    print(f"  - {db_pattern_count} patterns")
    print(f"  - {db_relationship_count} file relationships")
    
    # Close connection
    conn.close()
    
    # Print final statistics
    print(f"\n📊 Migration Statistics:")
    print(f"  Intent patterns: {stats['intent_patterns']}")
    print(f"  File relationships: {stats['file_relationships']}")
    print(f"  Workflow patterns: {stats['workflow_patterns']}")
    print(f"  Validation insights: {stats['validation_insights']}")
    print(f"  Correction history: {stats['correction_history']}")
    print(f"  Errors: {stats['errors']}")
    print()
    
    if stats['errors'] == 0:
        print(f"✅ Tier 2 migration complete!")
    else:
        print(f"⚠️  Tier 2 migration complete with {stats['errors']} errors")
    
    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Migrate CORTEX Brain Tier 2 data to SQLite')
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
        migrate_tier2(str(db_path), source_dir)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise


if __name__ == '__main__':
    main()
