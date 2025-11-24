#!/usr/bin/env python3
"""
CORTEX End-to-End Migration Test
Tests all three tier migrations and validates results

Task 0.5.4: End-to-End Migration Test
Duration: 30-45 minutes
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import Dict, List
import argparse


class MigrationValidator:
    """Validates all tier migrations"""
    
    def __init__(self, brain_dir: Path):
        """
        Initialize validator
        
        Args:
            brain_dir: Path to cortex-brain directory
        """
        self.brain_dir = brain_dir
        self.results = {
            'tier1': {'passed': False, 'checks': []},
            'tier2': {'passed': False, 'checks': []},
            'tier3': {'passed': False, 'checks': []},
            'overall': False
        }
    
    def validate_tier1(self) -> bool:
        """Validate Tier 1 migration"""
        print("\n" + "="*60)
        print("TIER 1 VALIDATION - Working Memory (SQLite)")
        print("="*60)
        
        db_path = self.brain_dir / 'left-hemisphere' / 'tier1' / 'conversations.db'
        
        if not db_path.exists():
            print(f"❌ Database not found: {db_path}")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check schema
            checks = [
                ("Conversations table exists", 
                 "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'"),
                ("Messages table exists", 
                 "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"),
                ("Entities table exists", 
                 "SELECT name FROM sqlite_master WHERE type='table' AND name='entities'"),
                ("Files table exists", 
                 "SELECT name FROM sqlite_master WHERE type='table' AND name='files_modified'"),
            ]
            
            for check_name, query in checks:
                cursor.execute(query)
                result = cursor.fetchone()
                passed = result is not None
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}")
                self.results['tier1']['checks'].append((check_name, passed))
            
            # Check data
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cursor.fetchone()[0]
            print(f"\n📊 Data counts:")
            print(f"  Conversations: {conv_count}")
            
            cursor.execute("SELECT COUNT(*) FROM messages")
            msg_count = cursor.fetchone()[0]
            print(f"  Messages: {msg_count}")
            
            cursor.execute("SELECT COUNT(*) FROM entities")
            entity_count = cursor.fetchone()[0]
            print(f"  Entities: {entity_count}")
            
            cursor.execute("SELECT COUNT(*) FROM files_modified")
            file_count = cursor.fetchone()[0]
            print(f"  Files: {file_count}")
            
            # Check indexes
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND sql IS NOT NULL
            """)
            indexes = cursor.fetchall()
            print(f"\n📑 Indexes: {len(indexes)}")
            for idx in indexes:
                print(f"  - {idx[0]}")
            
            conn.close()
            
            # Determine pass/fail
            all_passed = all(check[1] for check in self.results['tier1']['checks'])
            has_data = conv_count > 0
            
            self.results['tier1']['passed'] = all_passed and has_data
            
            if self.results['tier1']['passed']:
                print(f"\n✅ Tier 1 validation PASSED")
            else:
                print(f"\n❌ Tier 1 validation FAILED")
            
            return self.results['tier1']['passed']
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def validate_tier2(self) -> bool:
        """Validate Tier 2 migration"""
        print("\n" + "="*60)
        print("TIER 2 VALIDATION - Knowledge Graph (SQLite + FTS5)")
        print("="*60)
        
        db_path = self.brain_dir / 'right-hemisphere' / 'tier2' / 'patterns.db'
        
        if not db_path.exists():
            print(f"❌ Database not found: {db_path}")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check schema
            checks = [
                ("Patterns table exists", 
                 "SELECT name FROM sqlite_master WHERE type='table' AND name='patterns'"),
                ("Pattern details table exists", 
                 "SELECT name FROM sqlite_master WHERE type='table' AND name='pattern_details'"),
                ("File relationships table exists", 
                 "SELECT name FROM sqlite_master WHERE type='table' AND name='file_relationships'"),
                ("FTS5 table exists", 
                 "SELECT name FROM sqlite_master WHERE type='table' AND name='patterns_fts'"),
            ]
            
            for check_name, query in checks:
                cursor.execute(query)
                result = cursor.fetchone()
                passed = result is not None
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}")
                self.results['tier2']['checks'].append((check_name, passed))
            
            # Check data
            cursor.execute("SELECT COUNT(*) FROM patterns")
            pattern_count = cursor.fetchone()[0]
            print(f"\n📊 Data counts:")
            print(f"  Patterns: {pattern_count}")
            
            cursor.execute("SELECT COUNT(*) FROM pattern_details")
            detail_count = cursor.fetchone()[0]
            print(f"  Pattern details: {detail_count}")
            
            cursor.execute("SELECT COUNT(*) FROM file_relationships")
            rel_count = cursor.fetchone()[0]
            print(f"  File relationships: {rel_count}")
            
            # Test FTS5 search
            cursor.execute("""
                SELECT COUNT(*) FROM patterns_fts 
                WHERE patterns_fts MATCH 'workflow OR pattern'
            """)
            fts_results = cursor.fetchone()[0]
            print(f"\n🔍 FTS5 test search results: {fts_results}")
            
            # Check categories
            cursor.execute("SELECT DISTINCT category FROM patterns")
            categories = [row[0] for row in cursor.fetchall()]
            print(f"\n📁 Pattern categories: {', '.join(categories)}")
            
            conn.close()
            
            # Determine pass/fail
            all_passed = all(check[1] for check in self.results['tier2']['checks'])
            has_data = pattern_count > 0
            fts_works = fts_results >= 0  # FTS search executed without error
            
            self.results['tier2']['passed'] = all_passed and has_data and fts_works
            
            if self.results['tier2']['passed']:
                print(f"\n✅ Tier 2 validation PASSED")
            else:
                print(f"\n❌ Tier 2 validation FAILED")
            
            return self.results['tier2']['passed']
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def validate_tier3(self) -> bool:
        """Validate Tier 3 migration"""
        print("\n" + "="*60)
        print("TIER 3 VALIDATION - Development Context (JSON)")
        print("="*60)
        
        json_path = self.brain_dir / 'corpus-callosum' / 'tier3' / 'development-context.json'
        
        if not json_path.exists():
            print(f"❌ JSON file not found: {json_path}")
            return False
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check required sections
            required_sections = [
                'git_activity',
                'code_changes',
                'kds_usage',
                'project_health',
                'correlations',
                'proactive_insights'
            ]
            
            print("📋 Required sections:")
            for section in required_sections:
                exists = section in data
                status = "✅" if exists else "❌"
                print(f"{status} {section}")
                self.results['tier3']['checks'].append((section, exists))
            
            # Check metadata
            has_metadata = 'migrated_at' in data and 'version' in data
            status = "✅" if has_metadata else "❌"
            print(f"\n{status} Migration metadata present")
            
            # Show sections
            print(f"\n📊 Total sections: {len(data)}")
            print(f"Sections: {', '.join(sorted(data.keys()))}")
            
            # Determine pass/fail
            all_passed = all(check[1] for check in self.results['tier3']['checks'])
            
            self.results['tier3']['passed'] = all_passed and has_metadata
            
            if self.results['tier3']['passed']:
                print(f"\n✅ Tier 3 validation PASSED")
            else:
                print(f"\n❌ Tier 3 validation FAILED")
            
            return self.results['tier3']['passed']
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def run_all_validations(self) -> bool:
        """Run all tier validations"""
        print("\n" + "="*60)
        print("CORTEX MIGRATION VALIDATION - END TO END")
        print("="*60)
        print(f"Brain directory: {self.brain_dir}")
        
        tier1_passed = self.validate_tier1()
        tier2_passed = self.validate_tier2()
        tier3_passed = self.validate_tier3()
        
        # Overall result
        self.results['overall'] = tier1_passed and tier2_passed and tier3_passed
        
        print("\n" + "="*60)
        print("OVERALL RESULTS")
        print("="*60)
        
        print(f"Tier 1 (Working Memory): {'✅ PASSED' if tier1_passed else '❌ FAILED'}")
        print(f"Tier 2 (Knowledge Graph): {'✅ PASSED' if tier2_passed else '❌ FAILED'}")
        print(f"Tier 3 (Dev Context): {'✅ PASSED' if tier3_passed else '❌ FAILED'}")
        
        if self.results['overall']:
            print(f"\n🎉 ALL VALIDATIONS PASSED - Migration successful!")
        else:
            print(f"\n❌ SOME VALIDATIONS FAILED - Review errors above")
        
        return self.results['overall']


def main():
    parser = argparse.ArgumentParser(
        description='Validate CORTEX tier migrations end-to-end'
    )
    parser.add_argument(
        '--brain-dir',
        type=Path,
        help='Path to cortex-brain directory',
        default=Path(__file__).parent.parent.parent.parent / 'cortex-brain'
    )
    
    args = parser.parse_args()
    
    # Run validation
    validator = MigrationValidator(args.brain_dir)
    success = validator.run_all_validations()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

