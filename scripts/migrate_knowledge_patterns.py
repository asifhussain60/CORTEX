#!/usr/bin/env python3
"""
Migrate Knowledge Graph Patterns from YAML to SQLite

Bridges the gap between designed (SQLite) and actual (YAML) pattern storage.

This script:
1. Reads patterns from knowledge-graph.yaml
2. Migrates them to tier2/knowledge_graph.db
3. Validates migration success
4. Creates backup of YAML for reference

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import yaml
import json
from pathlib import Path
from datetime import datetime
import shutil

# Paths
ROOT = Path(__file__).parent.parent
YAML_PATH = ROOT / "cortex-brain" / "knowledge-graph.yaml"
DB_PATH = ROOT / "cortex-brain" / "tier2" / "knowledge_graph.db"
BACKUP_PATH = ROOT / "cortex-brain" / "archive" / f"knowledge-graph-{datetime.now().strftime('%Y%m%d')}.yaml"


def load_yaml_patterns():
    """Load patterns from YAML knowledge graph."""
    with open(YAML_PATH) as f:
        data = yaml.safe_load(f)
    
    patterns = []
    validation_insights = data.get('validation_insights', {})
    
    for pattern_name, pattern_data in validation_insights.items():
        pattern = {
            'pattern_id': f"yaml_{pattern_name}",
            'title': pattern_name.replace('_', ' ').title(),
            'content': json.dumps(pattern_data),
            'pattern_type': 'validation_insight',
            'confidence': pattern_data.get('confidence', 1.0),
            'created_at': pattern_data.get('last_seen', datetime.now().isoformat()),
            'last_accessed': pattern_data.get('last_seen', datetime.now().isoformat()),
            'access_count': pattern_data.get('frequency', 0),
            'source': 'knowledge-graph.yaml',
            'metadata': json.dumps({
                'issue': pattern_data.get('issue', ''),
                'impact': pattern_data.get('impact', 'unknown'),
                'frequency': pattern_data.get('frequency', 0)
            }),
            'is_pinned': 1 if pattern_data.get('impact') == 'critical' else 0,
            'scope': 'global',
            'namespaces': 'validation,patterns,best-practices'
        }
        patterns.append(pattern)
    
    return patterns


def migrate_patterns():
    """Migrate patterns from YAML to SQLite."""
    print("🔄 Starting Knowledge Graph Migration")
    print(f"   YAML source: {YAML_PATH}")
    print(f"   SQLite target: {DB_PATH}")
    
    # Load YAML patterns
    patterns = load_yaml_patterns()
    print(f"\n📥 Loaded {len(patterns)} patterns from YAML")
    
    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current pattern count
    current_count = cursor.execute("SELECT COUNT(*) FROM patterns").fetchone()[0]
    print(f"   Current SQLite patterns: {current_count}")
    
    # Insert patterns
    inserted = 0
    skipped = 0
    
    for pattern in patterns:
        # Check if pattern already exists
        existing = cursor.execute(
            "SELECT id FROM patterns WHERE pattern_id = ?",
            (pattern['pattern_id'],)
        ).fetchone()
        
        if existing:
            print(f"   ⏭️  Skipped: {pattern['title']} (already exists)")
            skipped += 1
            continue
        
        # Insert pattern
        cursor.execute("""
            INSERT INTO patterns (
                pattern_id, title, content, pattern_type, confidence,
                created_at, last_accessed, access_count, source,
                metadata, is_pinned, scope, namespaces
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern['pattern_id'],
            pattern['title'],
            pattern['content'],
            pattern['pattern_type'],
            pattern['confidence'],
            pattern['created_at'],
            pattern['last_accessed'],
            pattern['access_count'],
            pattern['source'],
            pattern['metadata'],
            pattern['is_pinned'],
            pattern['scope'],
            pattern['namespaces']
        ))
        
        print(f"   ✅ Migrated: {pattern['title']}")
        inserted += 1
    
    conn.commit()
    
    # Verify migration
    final_count = cursor.execute("SELECT COUNT(*) FROM patterns").fetchone()[0]
    conn.close()
    
    print(f"\n✨ Migration Complete!")
    print(f"   Inserted: {inserted} patterns")
    print(f"   Skipped: {skipped} patterns (duplicates)")
    print(f"   Final count: {final_count} patterns in SQLite")
    
    # Create backup of YAML
    if inserted > 0:
        shutil.copy(YAML_PATH, BACKUP_PATH)
        print(f"\n💾 Backup created: {BACKUP_PATH.name}")
        print("   Original YAML preserved for reference")
    
    return inserted, skipped, final_count


def verify_migration():
    """Verify patterns are accessible and FTS is working."""
    print("\n🔍 Verifying Migration...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test full-text search
    cursor.execute("""
        SELECT title, pattern_type, confidence
        FROM patterns
        WHERE pattern_id IN (
            SELECT pattern_id FROM pattern_fts WHERE pattern_fts MATCH 'powershell'
        )
    """)
    
    results = cursor.fetchall()
    print(f"   FTS test ('powershell'): {len(results)} matches")
    
    # Test high-confidence patterns
    cursor.execute("""
        SELECT title, confidence, access_count
        FROM patterns
        WHERE confidence > 0.9
        ORDER BY confidence DESC
        LIMIT 5
    """)
    
    top_patterns = cursor.fetchall()
    print(f"\n   Top 5 High-Confidence Patterns:")
    for title, conf, count in top_patterns:
        print(f"      • {title[:50]:50s} (conf: {conf:.2f}, used: {count}x)")
    
    conn.close()
    print("\n✅ Verification complete")


if __name__ == "__main__":
    try:
        inserted, skipped, final = migrate_patterns()
        
        if inserted > 0:
            verify_migration()
            print("\n🎯 Next Steps:")
            print("   1. Knowledge graph now active with patterns")
            print("   2. Integrate pattern matching into agent router")
            print("   3. Test pattern retrieval in workflows")
            print("   4. Update TRUTH-SOURCES.yaml to mark migration complete")
        else:
            print("\nℹ️  No new patterns to migrate")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
