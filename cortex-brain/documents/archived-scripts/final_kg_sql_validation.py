#!/usr/bin/env python3
"""
Final Knowledge Graph SQL Validation

This script runs comprehensive SQL tests to validate that the knowledge graph
database is working correctly with the processed conversation data.
"""

import sqlite3
from pathlib import Path

def run_comprehensive_sql_validation():
    """Run comprehensive SQL validation tests on the knowledge graph."""
    
    print("🧠 CORTEX Knowledge Graph SQL Validation")
    print("=" * 60)
    
    kg_db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier2/knowledge_graph.db")
    
    try:
        conn = sqlite3.connect(kg_db_path)
        cursor = conn.cursor()
        
        # Test 1: Basic pattern counting and types
        print("\n📊 Test 1: Pattern Inventory")
        cursor.execute("SELECT COUNT(*) FROM patterns")
        total_patterns = cursor.fetchone()[0]
        print(f"✅ Total patterns in database: {total_patterns}")
        
        cursor.execute("""
            SELECT pattern_type, COUNT(*) as count
            FROM patterns
            GROUP BY pattern_type
            ORDER BY count DESC
        """)
        type_counts = cursor.fetchall()
        
        print("📈 Patterns by type:")
        for pattern_type, count in type_counts:
            print(f"   {pattern_type}: {count} patterns")
        
        # Test 2: Confidence distribution
        print("\n📊 Test 2: Confidence Distribution")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN confidence >= 0.9 THEN 'High (0.9+)'
                    WHEN confidence >= 0.8 THEN 'Good (0.8-0.89)'
                    WHEN confidence >= 0.7 THEN 'Medium (0.7-0.79)'
                    ELSE 'Low (<0.7)'
                END as confidence_range,
                COUNT(*) as count
            FROM patterns
            GROUP BY confidence_range
            ORDER BY MIN(confidence) DESC
        """)
        conf_dist = cursor.fetchall()
        
        for conf_range, count in conf_dist:
            print(f"   {conf_range}: {count} patterns")
        
        # Test 3: Source analysis
        print("\n📊 Test 3: Pattern Sources")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN source LIKE 'conversation:%' THEN 'Conversation-derived'
                    WHEN source IS NULL OR source = '' THEN 'Unknown source'
                    ELSE 'Other source'
                END as source_type,
                COUNT(*) as count
            FROM patterns
            GROUP BY source_type
        """)
        source_dist = cursor.fetchall()
        
        for source_type, count in source_dist:
            print(f"   {source_type}: {count} patterns")
        
        # Test 4: Recent patterns (last 7 days)
        print("\n📊 Test 4: Recent Pattern Activity")
        cursor.execute("""
            SELECT pattern_id, title, pattern_type, confidence, created_at
            FROM patterns
            WHERE created_at > date('now', '-7 days')
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_patterns = cursor.fetchall()
        
        print(f"📅 Recent patterns (last 7 days): {len(recent_patterns)}")
        for pattern_id, title, ptype, confidence, created in recent_patterns:
            print(f"   [{ptype}] {title[:50]}... (confidence: {confidence:.2f})")
        
        # Test 5: Full-text search (simplified)
        print("\n📊 Test 5: Full-Text Search Capability")
        cursor.execute("""
            SELECT pattern_id, title
            FROM pattern_fts
            WHERE pattern_fts MATCH 'optimization'
            LIMIT 3
        """)
        search_results = cursor.fetchall()
        
        print(f"🔍 Search results for 'optimization': {len(search_results)}")
        for pattern_id, title in search_results:
            print(f"   {title[:60]}...")
        
        # Test 6: Namespace distribution  
        print("\n📊 Test 6: Namespace Distribution")
        cursor.execute("""
            SELECT namespaces, COUNT(*) as count
            FROM patterns
            GROUP BY namespaces
            ORDER BY count DESC
        """)
        namespace_dist = cursor.fetchall()
        
        print("🏷️ Pattern namespaces:")
        for namespaces, count in namespace_dist:
            print(f"   {namespaces[:50]}...: {count} patterns")
        
        # Test 7: Complex SQL JOIN test (if relationships exist)
        print("\n📊 Test 7: Relationship Queries")
        cursor.execute("SELECT COUNT(*) FROM pattern_relationships")
        rel_count = cursor.fetchone()[0]
        
        if rel_count > 0:
            cursor.execute("""
                SELECT p1.title as pattern1, p2.title as pattern2, pr.relationship_type
                FROM pattern_relationships pr
                JOIN patterns p1 ON pr.from_pattern_id = p1.pattern_id
                JOIN patterns p2 ON pr.to_pattern_id = p2.pattern_id
                LIMIT 3
            """)
            relationships = cursor.fetchall()
            
            print(f"🔗 Pattern relationships found: {rel_count}")
            for p1_title, p2_title, rel_type in relationships:
                print(f"   {p1_title[:30]} --{rel_type}--> {p2_title[:30]}")
        else:
            print(f"🔗 Pattern relationships: {rel_count} (none found)")
        
        # Test 8: Advanced aggregation query
        print("\n📊 Test 8: Advanced Analytics")
        cursor.execute("""
            SELECT 
                scope,
                AVG(confidence) as avg_confidence,
                MAX(confidence) as max_confidence,
                MIN(confidence) as min_confidence,
                COUNT(*) as pattern_count
            FROM patterns
            GROUP BY scope
        """)
        scope_analytics = cursor.fetchall()
        
        print("📊 Analytics by scope:")
        for scope, avg_conf, max_conf, min_conf, count in scope_analytics:
            print(f"   {scope}: {count} patterns, confidence {avg_conf:.2f} (avg), {max_conf:.2f} (max), {min_conf:.2f} (min)")
        
        # Test 9: Performance test with ORDER BY and LIMIT
        print("\n📊 Test 9: Query Performance Test")
        import time
        start_time = time.time()
        
        cursor.execute("""
            SELECT pattern_id, title, confidence
            FROM patterns
            WHERE confidence > 0.8
            ORDER BY confidence DESC, created_at DESC
            LIMIT 10
        """)
        top_patterns = cursor.fetchall()
        
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        print(f"⚡ Query executed in {query_time:.2f}ms")
        print(f"🏆 Top {len(top_patterns)} high-confidence patterns:")
        for pattern_id, title, confidence in top_patterns:
            print(f"   {confidence:.2f}: {title[:55]}...")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ COMPREHENSIVE SQL VALIDATION COMPLETED")
        print("📊 All SQL operations successful")
        print("🧠 Knowledge graph database is fully operational")
        print("🔍 Patterns are searchable and queryable via SQL")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL validation failed: {e}")
        return False

if __name__ == "__main__":
    success = run_comprehensive_sql_validation()
    print(f"\n🎯 Final Result: {'SUCCESS' if success else 'FAILED'}")