"""
CORTEX Cross-Tier Linking Schema Migration
Adds linking fields to enable traceability across T1/T2/T3

Phase 1: Foundation
- T1 conversations link to T2 patterns and T3 metrics
- T2 patterns link back to T1 conversations where they were applied
- T3 insights link to T1 conversations that triggered them

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime


class CrossTierLinkingMigration:
    """Adds cross-tier linking fields to existing schemas"""
    
    def __init__(self):
        self.tier1_db = Path("cortex-brain/tier1/working_memory.db")
        self.tier2_db = Path("cortex-brain/tier2/knowledge-graph.db")
        self.tier3_db = Path("cortex-brain/tier3/context.db")
    
    def migrate_tier1_schema(self):
        """Add linking fields to Tier 1 conversations table"""
        print("Migrating Tier 1 schema...")
        
        if not self.tier1_db.exists():
            print(f"  ⚠️  Tier 1 database not found: {self.tier1_db}")
            return False
        
        conn = sqlite3.connect(self.tier1_db)
        cursor = conn.cursor()
        
        try:
            # Check if columns already exist
            cursor.execute("PRAGMA table_info(conversations)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Add used_patterns column (JSON array of pattern_ids)
            if 'used_patterns' not in columns:
                cursor.execute("""
                    ALTER TABLE conversations 
                    ADD COLUMN used_patterns TEXT DEFAULT '[]'
                """)
                print("  ✅ Added 'used_patterns' column")
            else:
                print("  ℹ️  'used_patterns' column already exists")
            
            # Add used_metrics column (JSON array of insight references)
            if 'used_metrics' not in columns:
                cursor.execute("""
                    ALTER TABLE conversations 
                    ADD COLUMN used_metrics TEXT DEFAULT '[]'
                """)
                print("  ✅ Added 'used_metrics' column")
            else:
                print("  ℹ️  'used_metrics' column already exists")
            
            # Add context_quality_score column
            if 'context_quality_score' not in columns:
                cursor.execute("""
                    ALTER TABLE conversations 
                    ADD COLUMN context_quality_score REAL DEFAULT 0.0
                """)
                print("  ✅ Added 'context_quality_score' column")
            else:
                print("  ℹ️  'context_quality_score' column already exists")
            
            conn.commit()
            print("  ✅ Tier 1 schema migration complete")
            return True
            
        except Exception as e:
            print(f"  ❌ Error migrating Tier 1: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def migrate_tier2_schema(self):
        """Add linking fields to Tier 2 patterns table"""
        print("\nMigrating Tier 2 schema...")
        
        if not self.tier2_db.exists():
            print(f"  ⚠️  Tier 2 database not found: {self.tier2_db}")
            return False
        
        conn = sqlite3.connect(self.tier2_db)
        cursor = conn.cursor()
        
        try:
            # Check if columns already exist
            cursor.execute("PRAGMA table_info(patterns)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Add applied_in_conversations column (JSON array of conversation_ids)
            if 'applied_in_conversations' not in columns:
                cursor.execute("""
                    ALTER TABLE patterns 
                    ADD COLUMN applied_in_conversations TEXT DEFAULT '[]'
                """)
                print("  ✅ Added 'applied_in_conversations' column")
            else:
                print("  ℹ️  'applied_in_conversations' column already exists")
            
            # Add success_count column
            if 'success_count' not in columns:
                cursor.execute("""
                    ALTER TABLE patterns 
                    ADD COLUMN success_count INTEGER DEFAULT 0
                """)
                print("  ✅ Added 'success_count' column")
            else:
                print("  ℹ️  'success_count' column already exists")
            
            # Add failure_count column
            if 'failure_count' not in columns:
                cursor.execute("""
                    ALTER TABLE patterns 
                    ADD COLUMN failure_count INTEGER DEFAULT 0
                """)
                print("  ✅ Added 'failure_count' column")
            else:
                print("  ℹ️  'failure_count' column already exists")
            
            conn.commit()
            print("  ✅ Tier 2 schema migration complete")
            return True
            
        except Exception as e:
            print(f"  ❌ Error migrating Tier 2: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def migrate_tier3_schema(self):
        """Add linking fields to Tier 3 insights table"""
        print("\nMigrating Tier 3 schema...")
        
        if not self.tier3_db.exists():
            print(f"  ⚠️  Tier 3 database not found: {self.tier3_db}")
            return False
        
        conn = sqlite3.connect(self.tier3_db)
        cursor = conn.cursor()
        
        try:
            # Check if columns already exist
            cursor.execute("PRAGMA table_info(insights)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Add triggered_by_conversation column
            if 'triggered_by_conversation' not in columns:
                cursor.execute("""
                    ALTER TABLE insights 
                    ADD COLUMN triggered_by_conversation TEXT
                """)
                print("  ✅ Added 'triggered_by_conversation' column")
            else:
                print("  ℹ️  'triggered_by_conversation' column already exists")
            
            # Add action_taken column
            if 'action_taken' not in columns:
                cursor.execute("""
                    ALTER TABLE insights 
                    ADD COLUMN action_taken TEXT
                """)
                print("  ✅ Added 'action_taken' column")
            else:
                print("  ℹ️  'action_taken' column already exists")
            
            # Add resolution_status column
            if 'resolution_status' not in columns:
                cursor.execute("""
                    ALTER TABLE insights 
                    ADD COLUMN resolution_status TEXT DEFAULT 'open'
                """)
                print("  ✅ Added 'resolution_status' column")
            else:
                print("  ℹ️  'resolution_status' column already exists")
            
            conn.commit()
            print("  ✅ Tier 3 schema migration complete")
            return True
            
        except Exception as e:
            print(f"  ❌ Error migrating Tier 3: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def verify_migrations(self) -> dict:
        """Verify all migrations completed successfully"""
        print("\n" + "="*60)
        print("VERIFICATION REPORT")
        print("="*60)
        
        results = {
            'tier1': self._verify_tier1(),
            'tier2': self._verify_tier2(),
            'tier3': self._verify_tier3()
        }
        
        all_success = all(results.values())
        
        print("\n" + "="*60)
        if all_success:
            print("✅ ALL MIGRATIONS VERIFIED SUCCESSFULLY")
        else:
            print("⚠️  SOME MIGRATIONS INCOMPLETE")
        print("="*60)
        
        return results
    
    def _verify_tier1(self) -> bool:
        """Verify Tier 1 migrations"""
        print("\nVerifying Tier 1...")
        
        if not self.tier1_db.exists():
            print("  ❌ Database not found")
            return False
        
        conn = sqlite3.connect(self.tier1_db)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(conversations)")
            columns = {row[1] for row in cursor.fetchall()}
            
            required_columns = {'used_patterns', 'used_metrics', 'context_quality_score'}
            missing = required_columns - columns
            
            if missing:
                print(f"  ❌ Missing columns: {missing}")
                return False
            else:
                print("  ✅ All required columns present")
                return True
                
        except Exception as e:
            print(f"  ❌ Verification error: {e}")
            return False
        finally:
            conn.close()
    
    def _verify_tier2(self) -> bool:
        """Verify Tier 2 migrations"""
        print("\nVerifying Tier 2...")
        
        if not self.tier2_db.exists():
            print("  ❌ Database not found")
            return False
        
        conn = sqlite3.connect(self.tier2_db)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(patterns)")
            columns = {row[1] for row in cursor.fetchall()}
            
            required_columns = {'applied_in_conversations', 'success_count', 'failure_count'}
            missing = required_columns - columns
            
            if missing:
                print(f"  ❌ Missing columns: {missing}")
                return False
            else:
                print("  ✅ All required columns present")
                return True
                
        except Exception as e:
            print(f"  ❌ Verification error: {e}")
            return False
        finally:
            conn.close()
    
    def _verify_tier3(self) -> bool:
        """Verify Tier 3 migrations"""
        print("\nVerifying Tier 3...")
        
        if not self.tier3_db.exists():
            print("  ❌ Database not found")
            return False
        
        conn = sqlite3.connect(self.tier3_db)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(insights)")
            columns = {row[1] for row in cursor.fetchall()}
            
            required_columns = {'triggered_by_conversation', 'action_taken', 'resolution_status'}
            missing = required_columns - columns
            
            if missing:
                print(f"  ❌ Missing columns: {missing}")
                return False
            else:
                print("  ✅ All required columns present")
                return True
                
        except Exception as e:
            print(f"  ❌ Verification error: {e}")
            return False
        finally:
            conn.close()
    
    def run_full_migration(self) -> bool:
        """Run complete cross-tier linking migration"""
        print("="*60)
        print("CORTEX Cross-Tier Linking Schema Migration")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run migrations
        t1_success = self.migrate_tier1_schema()
        t2_success = self.migrate_tier2_schema()
        t3_success = self.migrate_tier3_schema()
        
        # Verify
        verification_results = self.verify_migrations()
        
        # Summary
        all_success = t1_success and t2_success and t3_success
        
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return all_success


def main():
    """Run cross-tier linking migration"""
    migration = CrossTierLinkingMigration()
    success = migration.run_full_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        return 0
    else:
        print("\n⚠️  Migration completed with warnings")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
