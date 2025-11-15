#!/usr/bin/env python3
"""
Improved Conversation to Knowledge Graph Processor

This script processes conversations and extracts proper knowledge patterns
that comply with the CORTEX knowledge graph schema constraints.
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

def process_conversations_to_knowledge_graph_improved():
    """Process conversations and import them into the knowledge graph with proper pattern types."""
    
    print("🧠 CORTEX Improved Conversation to Knowledge Graph Processor")
    print("=" * 60)
    
    # Database paths
    conv_db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/conversation-history.db")
    kg_db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier2/knowledge_graph.db")
    
    print(f"✅ Using conversation database: {conv_db_path}")
    print(f"✅ Using knowledge graph database: {kg_db_path}")
    
    # Get conversation data
    print("\n📊 Retrieving Conversation Data")
    try:
        conv_conn = sqlite3.connect(conv_db_path)
        conv_cursor = conv_conn.cursor()
        
        # Get all conversations with details
        conv_cursor.execute("""
            SELECT conversation_id, user_message, assistant_response, context, metadata, timestamp
            FROM conversations
            ORDER BY timestamp
        """)
        conversations = conv_cursor.fetchall()
        
        print(f"📈 Found {len(conversations)} conversations to analyze")
        
        conv_conn.close()
        
    except Exception as e:
        print(f"❌ Failed to retrieve conversations: {e}")
        return False
    
    # Process each conversation for knowledge extraction
    print("\n🔍 Analyzing Conversations for Knowledge Patterns")
    try:
        kg_conn = sqlite3.connect(kg_db_path)
        kg_cursor = kg_conn.cursor()
        
        # Get current pattern count
        kg_cursor.execute("SELECT COUNT(*) FROM patterns")
        initial_pattern_count = kg_cursor.fetchone()[0]
        print(f"📊 Initial knowledge graph patterns: {initial_pattern_count}")
        
        patterns_created = 0
        
        for i, conv in enumerate(conversations, 1):
            conv_id, user_msg, assistant_resp, context, metadata, timestamp = conv
            
            print(f"\n🔄 Analyzing conversation {i}/{len(conversations)}: {conv_id}")
            print(f"   User: {user_msg[:60]}..." if user_msg else "   User: (empty)")
            print(f"   Length: {len(assistant_resp) if assistant_resp else 0} chars")
            
            # Extract patterns using valid pattern types
            patterns = extract_valid_patterns_from_conversation(
                conv_id, user_msg, assistant_resp, context, metadata
            )
            
            if patterns:
                print(f"   🧠 Extracted {len(patterns)} valid patterns:")
                
                for j, pattern in enumerate(patterns, 1):
                    try:
                        # Generate unique pattern ID
                        pattern_id = f"conv_{pattern['pattern_type']}_{conv_id.split('_')[-1]}_{j}"
                        
                        kg_cursor.execute("""
                            INSERT INTO patterns 
                            (pattern_id, title, content, pattern_type, confidence, created_at, last_accessed, 
                             access_count, source, metadata, scope, namespaces)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            pattern_id,
                            pattern['title'],
                            pattern['content'], 
                            pattern['pattern_type'],  # Now using valid types
                            pattern['confidence'],
                            datetime.now().isoformat(),
                            datetime.now().isoformat(),
                            1,
                            f"conversation:{conv_id}",
                            json.dumps(pattern['metadata']),
                            pattern['scope'],
                            json.dumps(pattern['namespaces'])
                        ))
                        
                        patterns_created += 1
                        print(f"      ✅ {j}. [{pattern['pattern_type']}] {pattern['title'][:45]}... (confidence: {pattern['confidence']:.2f})")
                        
                    except Exception as e:
                        print(f"      ❌ Failed to store pattern {j}: {e}")
                        continue
            else:
                print("   ℹ️ No extractable patterns found in this conversation")
        
        # Commit all changes
        kg_conn.commit()
        
        # Get final pattern count and show results
        kg_cursor.execute("SELECT COUNT(*) FROM patterns")
        final_pattern_count = kg_cursor.fetchone()[0]
        
        print(f"\n📊 Knowledge Graph Processing Results")
        print(f"   Patterns before: {initial_pattern_count}")
        print(f"   Patterns after: {final_pattern_count}")
        print(f"   New patterns created: {patterns_created}")
        
        kg_conn.close()
        
    except Exception as e:
        print(f"❌ Knowledge graph processing failed: {e}")
        return False
    
    # Test SQL queries on the updated knowledge graph
    print("\n🔍 Testing Knowledge Graph SQL Queries")
    try:
        kg_conn = sqlite3.connect(kg_db_path)
        kg_cursor = kg_conn.cursor()
        
        # Query 1: Patterns by type
        print("\n📊 Query 1: Patterns by Type")
        kg_cursor.execute("""
            SELECT pattern_type, COUNT(*) as count
            FROM patterns
            GROUP BY pattern_type
            ORDER BY count DESC
        """)
        type_counts = kg_cursor.fetchall()
        
        for pattern_type, count in type_counts:
            print(f"   {pattern_type}: {count} patterns")
        
        # Query 2: Recent conversation-derived patterns
        print("\n📊 Query 2: Recent Conversation-Derived Patterns")
        kg_cursor.execute("""
            SELECT pattern_id, title, pattern_type, confidence
            FROM patterns 
            WHERE source LIKE 'conversation:%'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_patterns = kg_cursor.fetchall()
        
        for pattern_id, title, ptype, confidence in recent_patterns:
            print(f"   [{ptype}] {title[:50]}... (confidence: {confidence:.2f})")
        
        # Query 3: Full-text search test
        print("\n📊 Query 3: Full-Text Search Test")
        kg_cursor.execute("""
            SELECT pattern_id, title, pattern_type
            FROM pattern_fts 
            WHERE pattern_fts MATCH 'optimization OR fix OR issues'
            LIMIT 3
        """)
        search_results = kg_cursor.fetchall()
        
        for pattern_id, title, ptype in search_results:
            print(f"   [{ptype}] {title[:50]}...")
        
        # Query 4: High confidence patterns
        print("\n📊 Query 4: High Confidence Patterns (>0.85)")
        kg_cursor.execute("""
            SELECT title, pattern_type, confidence, scope
            FROM patterns
            WHERE confidence > 0.85
            ORDER BY confidence DESC
            LIMIT 5
        """)
        high_conf = kg_cursor.fetchall()
        
        for title, ptype, confidence, scope in high_conf:
            print(f"   [{ptype}] {title[:40]}... ({confidence:.2f}, {scope})")
        
        kg_conn.close()
        
    except Exception as e:
        print(f"❌ SQL query testing failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ CORTEX Knowledge Graph SQL Validation COMPLETED")
    print("📊 All SQL operations executed successfully")
    print("🧠 Conversation data processed and validated in SQLite")
    print("🔍 Knowledge patterns are searchable and accessible via SQL")
    
    return True

def extract_valid_patterns_from_conversation(conv_id, user_msg, assistant_resp, context, metadata):
    """Extract knowledge patterns using only valid CORTEX pattern types."""
    patterns = []
    
    if not user_msg or not assistant_resp:
        return patterns
    
    # Valid pattern types: 'workflow', 'principle', 'anti_pattern', 'solution', 'context'
    
    # Solution pattern for fix/problem scenarios
    if any(word in user_msg.lower() for word in ['fix', 'error', 'issue', 'problem', 'bug', 'resolve']):
        patterns.append({
            'title': f"Problem Resolution Solution: {user_msg[:50]}...",
            'content': f"PROBLEM:\n{user_msg}\n\nSOLUTION:\n{assistant_resp}",
            'pattern_type': 'solution',  # Valid type
            'confidence': 0.85,
            'scope': 'application',
            'metadata': {
                'conversation_id': conv_id,
                'problem_type': 'error_resolution',
                'keywords': [w for w in ['fix', 'error', 'issue', 'problem', 'bug', 'resolve'] if w in user_msg.lower()]
            },
            'namespaces': ['workspace.CORTEX.problem_solving']
        })
    
    # Workflow pattern for implementation/process scenarios
    if any(word in user_msg.lower() for word in ['implement', 'create', 'add', 'build', 'setup', 'configure']):
        patterns.append({
            'title': f"Implementation Workflow: {user_msg[:50]}...",
            'content': f"IMPLEMENTATION REQUEST:\n{user_msg}\n\nWORKFLOW STEPS:\n{assistant_resp}",
            'pattern_type': 'workflow',  # Valid type
            'confidence': 0.80,
            'scope': 'application',
            'metadata': {
                'conversation_id': conv_id,
                'workflow_type': 'implementation',
                'keywords': [w for w in ['implement', 'create', 'add', 'build', 'setup', 'configure'] if w in user_msg.lower()]
            },
            'namespaces': ['workspace.CORTEX.implementation']
        })
    
    # Principle pattern for optimization/best practices
    if any(word in user_msg.lower() for word in ['optimize', 'improve', 'enhance', 'better', 'best practice', 'recommendation']):
        patterns.append({
            'title': f"Optimization Principle: {user_msg[:50]}...",
            'content': f"OPTIMIZATION GOAL:\n{user_msg}\n\nPRINCIPLE/APPROACH:\n{assistant_resp}",
            'pattern_type': 'principle',  # Valid type
            'confidence': 0.88,
            'scope': 'application',
            'metadata': {
                'conversation_id': conv_id,
                'principle_type': 'optimization',
                'keywords': [w for w in ['optimize', 'improve', 'enhance', 'better'] if w in user_msg.lower()]
            },
            'namespaces': ['workspace.CORTEX.optimization']
        })
    
    # Context pattern for informational/analysis scenarios
    if len(assistant_resp) > 300 and any(word in user_msg.lower() for word in ['analyze', 'explain', 'what', 'how', 'why', 'show']):
        patterns.append({
            'title': f"Analysis Context: {user_msg[:50]}...",
            'content': f"ANALYSIS REQUEST:\n{user_msg}\n\nCONTEXT PROVIDED:\n{assistant_resp[:500]}...",
            'pattern_type': 'context',  # Valid type
            'confidence': 0.75,
            'scope': 'application',
            'metadata': {
                'conversation_id': conv_id,
                'context_type': 'analysis',
                'response_length': len(assistant_resp)
            },
            'namespaces': ['workspace.CORTEX.analysis_context']
        })
    
    return patterns

if __name__ == "__main__":
    success = process_conversations_to_knowledge_graph_improved()
    sys.exit(0 if success else 1)