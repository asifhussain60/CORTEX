#!/usr/bin/env python3
"""Quick diagnostic script to check Enhancement Catalog database state."""

import sqlite3
from pathlib import Path
from datetime import datetime

def check_database(db_path):
    """Check database tables and recent reviews."""
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"✅ Database found: {db_path}")
    print(f"   Size: {db_path.stat().st_size / 1024:.2f} KB")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n📋 Tables ({len(tables)}):")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Check if review log exists
    if ('cortex_review_log',) in tables:
        cursor.execute("SELECT COUNT(*) FROM cortex_review_log")
        count = cursor.fetchone()[0]
        print(f"\n📊 Review Log: {count} entries")
        
        if count > 0:
            cursor.execute("""
                SELECT review_type, review_timestamp, features_reviewed, new_features_found 
                FROM cortex_review_log 
                ORDER BY review_timestamp DESC 
                LIMIT 5
            """)
            print("\n🕒 Last 5 Reviews:")
            for row in cursor.fetchall():
                print(f"   • {row[0]}: {row[1]} ({row[2]} reviewed, {row[3]} new)")
    else:
        print("\n⚠️  cortex_review_log table does not exist")
    
    # Check features table
    if ('cortex_features',) in tables:
        cursor.execute("SELECT COUNT(*) FROM cortex_features")
        count = cursor.fetchone()[0]
        print(f"\n📦 Features: {count} total")
        
        if count > 0:
            cursor.execute("""
                SELECT feature_type, COUNT(*) 
                FROM cortex_features 
                GROUP BY feature_type
            """)
            print("\n📊 By Type:")
            for row in cursor.fetchall():
                print(f"   • {row[0]}: {row[1]}")
    else:
        print("\n⚠️  cortex_features table does not exist")
    
    conn.close()

if __name__ == "__main__":
    print("🔍 CORTEX Enhancement Catalog Database Diagnostic\n")
    print("=" * 60)
    
    # Check Windows path
    windows_db = Path("cortex-brain/tier3/context.db")
    check_database(windows_db)
    
    print("\n" + "=" * 60)
    print("\n💡 Expected Mac path: /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier3/context.db")
    print("   (Not accessible from Windows)")
