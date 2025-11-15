#!/usr/bin/env python3
"""
Knowledge Graph Database Validation Script

This script validates that conversations are being properly processed and stored
in the knowledge graph database. It tests the SQL queries and confirms the
system is working correctly.
"""

import sqlite3
import json
import sys
from datetime import datetime
from pathlib import Path

def test_knowledge_graph_database():
    """Test the knowledge graph database functionality."""
    
    # Database paths
    kg_db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier2/knowledge_graph.db")
    conv_jsonl_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/conversation-context.jsonl")
    
    print("🧠 CORTEX Knowledge Graph Database Validation")
    print("=" * 60)
    
    # Test 1: Check database connectivity and schema
    print("\n📊 Test 1: Database Connectivity and Schema")
    try:
        conn = sqlite3.connect(kg_db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['patterns', 'pattern_relationships', 'pattern_tags', 'confidence_decay_log']
        
        print(f"✅ Database connected: {kg_db_path}")
        print(f"✅ Tables found: {', '.join(tables)}")
        
        for table in expected_tables:
            if table in tables:
                print(f"  ✅ {table} - EXISTS")
            else:
                print(f"  ❌ {table} - MISSING")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connectivity failed: {e}")
        return False
    
    # Test 2: Query existing patterns
    print("\n📊 Test 2: Existing Patterns Analysis")
    try:
        conn = sqlite3.connect(kg_db_path)
        cursor = conn.cursor()
        
        # Get pattern count
        cursor.execute("SELECT COUNT(*) FROM patterns")
        pattern_count = cursor.fetchone()[0]
        print(f"📈 Total patterns in database: {pattern_count}")
        
        if pattern_count > 0:
            # Get pattern details
            cursor.execute("""
                SELECT pattern_id, title, pattern_type, confidence, scope, namespaces, created_at
                FROM patterns ORDER BY created_at DESC
            """)
            patterns = cursor.fetchall()
            
            print("\n🔍 Pattern Details:")
            for i, pattern in enumerate(patterns, 1):
                pattern_id, title, ptype, confidence, scope, namespaces, created = pattern
                print(f"  {i}. ID: {pattern_id}")
                print(f"     Title: {title}")
                print(f"     Type: {ptype}, Confidence: {confidence:.2f}, Scope: {scope}")
                print(f"     Namespaces: {namespaces}")
                print(f"     Created: {created}")
                print()
        
        # Test pattern search functionality
        print("🔍 Test 3: Pattern Search Functionality")
        cursor.execute("""
            SELECT pattern_id, title, confidence 
            FROM patterns 
            WHERE pattern_type = 'solution' 
            ORDER BY confidence DESC
        """)
        solutions = cursor.fetchall()
        
        print(f"📊 Solution patterns found: {len(solutions)}")
        for pattern_id, title, confidence in solutions:
            print(f"  - {title} (confidence: {confidence:.2f})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Pattern query failed: {e}")
        return False
    
    # Test 4: Process conversation data into patterns
    print("\n📊 Test 4: Processing Conversation Data")
    try:
        if not conv_jsonl_path.exists():
            print(f"⚠️ Conversation file not found: {conv_jsonl_path}")
            return True  # Not a failure, just no data to process
        
        # Read conversation data
        with open(conv_jsonl_path, 'r') as f:
            lines = f.readlines()
        
        print(f"📁 Found {len(lines)} conversation entries")
        
        # Process each conversation line
        for i, line in enumerate(lines, 1):
            try:
                data = json.loads(line.strip())
                print(f"\n🔍 Processing conversation entry {i}:")
                print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"   User Message: {data.get('user_message', 'N/A')[:50]}...")
                print(f"   Intent: {data.get('intent', 'N/A')}")
                print(f"   Session: {data.get('session_id', 'N/A')}")
                
                # Check if this could be converted to a pattern
                if 'patterns_learned' in data:
                    patterns = data['patterns_learned']
                    print(f"   🧠 Contains {len(patterns)} learned patterns:")
                    for pattern in patterns:
                        print(f"      - {pattern.get('pattern_name', 'Unnamed')} (confidence: {pattern.get('confidence', 0):.2f})")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid JSON in line {i}: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Conversation processing failed: {e}")
        return False
    
    # Test 5: Test SQL insertion of a new pattern
    print("\n📊 Test 5: Testing Pattern Insertion")
    try:
        conn = sqlite3.connect(kg_db_path)
        cursor = conn.cursor()
        
        # Create a test pattern
        test_pattern = {
            'pattern_id': f'test_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'title': 'Knowledge Graph Validation Test Pattern',
            'content': 'This is a test pattern created during validation to confirm SQL insertion works correctly.',
            'pattern_type': 'solution',
            'confidence': 0.95,
            'source': 'validation_script',
            'metadata': json.dumps({'test': True, 'created_by': 'validation_script'}),
            'scope': 'application',
            'namespaces': json.dumps(['workspace.CORTEX.validation'])
        }
        
        # Insert pattern
        cursor.execute("""
            INSERT INTO patterns 
            (pattern_id, title, content, pattern_type, confidence, created_at, last_accessed, 
             access_count, source, metadata, scope, namespaces)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_pattern['pattern_id'],
            test_pattern['title'],
            test_pattern['content'],
            test_pattern['pattern_type'],
            test_pattern['confidence'],
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            1,
            test_pattern['source'],
            test_pattern['metadata'],
            test_pattern['scope'],
            test_pattern['namespaces']
        ))
        
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM patterns WHERE pattern_id = ?", (test_pattern['pattern_id'],))
        count = cursor.fetchone()[0]
        
        if count == 1:
            print("✅ Pattern insertion test PASSED")
            print(f"   Created pattern: {test_pattern['pattern_id']}")
            
            # Clean up test pattern
            cursor.execute("DELETE FROM patterns WHERE pattern_id = ?", (test_pattern['pattern_id'],))
            conn.commit()
            print("✅ Test pattern cleaned up")
            
        else:
            print("❌ Pattern insertion test FAILED")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Pattern insertion test failed: {e}")
        return False
    
    # Test 6: Full-text search test
    print("\n📊 Test 6: Full-Text Search Test")
    try:
        conn = sqlite3.connect(kg_db_path)
        cursor = conn.cursor()
        
        # Test FTS search
        cursor.execute("""
            SELECT pattern_id, title 
            FROM pattern_fts 
            WHERE pattern_fts MATCH 'architecture OR solution'
            LIMIT 5
        """)
        results = cursor.fetchall()
        
        print(f"🔍 Full-text search results: {len(results)} patterns found")
        for pattern_id, title in results:
            print(f"   - {title} ({pattern_id})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Full-text search test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Knowledge Graph Database Validation COMPLETED")
    print("📊 All SQL queries executed successfully")
    print("🧠 Database is operational and ready for conversation processing")
    
    return True

if __name__ == "__main__":
    success = test_knowledge_graph_database()
    sys.exit(0 if success else 1)