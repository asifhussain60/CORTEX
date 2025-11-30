#!/usr/bin/env python3
"""
Conversation to Knowledge Graph Processor

This script processes conversations from the conversation-history.db database
and imports them into the knowledge graph using CORTEX's conversation import functionality.
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the path so we can import CORTEX modules
sys.path.append('/Users/asifhussain/PROJECTS/CORTEX/src')

def process_conversations_to_knowledge_graph():
    """Process conversations and import them into the knowledge graph."""
    
    print("🧠 CORTEX Conversation to Knowledge Graph Processor")
    print("=" * 60)
    
    # Database paths
    conv_db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/conversation-history.db")
    kg_db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier2/knowledge_graph.db")
    
    # Check database files exist
    if not conv_db_path.exists():
        print(f"❌ Conversation database not found: {conv_db_path}")
        return False
        
    if not kg_db_path.exists():
        print(f"❌ Knowledge graph database not found: {kg_db_path}")
        return False
    
    print(f"✅ Conversation database: {conv_db_path}")
    print(f"✅ Knowledge graph database: {kg_db_path}")
    
    # Get conversation data
    print("\n📊 Retrieving Conversation Data")
    try:
        conv_conn = sqlite3.connect(conv_db_path)
        conv_cursor = conv_conn.cursor()
        
        # Get all conversations
        conv_cursor.execute("""
            SELECT conversation_id, user_message, assistant_response, context, metadata, timestamp
            FROM conversations
            ORDER BY timestamp
        """)
        conversations = conv_cursor.fetchall()
        
        print(f"📈 Found {len(conversations)} conversations to process")
        
        if len(conversations) == 0:
            print("ℹ️ No conversations found to process")
            return True
        
        conv_conn.close()
        
    except Exception as e:
        print(f"❌ Failed to retrieve conversations: {e}")
        return False
    
    # Process each conversation for knowledge extraction
    print("\n🔍 Processing Conversations for Knowledge Patterns")
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
            
            print(f"\n🔄 Processing conversation {i}/{len(conversations)}: {conv_id}")
            print(f"   User: {user_msg[:80]}..." if user_msg else "   User: (empty)")
            print(f"   Timestamp: {timestamp}")
            
            # Extract patterns from this conversation
            patterns = extract_patterns_from_conversation(
                conv_id, user_msg, assistant_resp, context, metadata
            )
            
            if patterns:
                print(f"   🧠 Extracted {len(patterns)} patterns:")
                
                for j, pattern in enumerate(patterns, 1):
                    try:
                        # Insert pattern into knowledge graph
                        pattern_id = f"conv_pattern_{conv_id}_{j}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        
                        kg_cursor.execute("""
                            INSERT INTO patterns 
                            (pattern_id, title, content, pattern_type, confidence, created_at, last_accessed, 
                             access_count, source, metadata, scope, namespaces)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            pattern_id,
                            pattern['title'],
                            pattern['content'], 
                            pattern.get('pattern_type', 'solution'),
                            pattern.get('confidence', 0.8),
                            datetime.now().isoformat(),
                            datetime.now().isoformat(),
                            1,
                            f"conversation:{conv_id}",
                            json.dumps(pattern.get('metadata', {})),
                            pattern.get('scope', 'application'),
                            json.dumps(pattern.get('namespaces', ['workspace.CORTEX.conversations']))
                        ))
                        
                        patterns_created += 1
                        print(f"      {j}. {pattern['title'][:60]}... (confidence: {pattern.get('confidence', 0.8):.2f})")
                        
                    except Exception as e:
                        print(f"      ❌ Failed to store pattern {j}: {e}")
                        continue
            else:
                print("   ℹ️ No patterns extracted from this conversation")
        
        # Commit all changes
        kg_conn.commit()
        
        # Get final pattern count
        kg_cursor.execute("SELECT COUNT(*) FROM patterns")
        final_pattern_count = kg_cursor.fetchone()[0]
        
        kg_conn.close()
        
        print(f"\n📊 Knowledge Graph Processing Complete")
        print(f"   Patterns before: {initial_pattern_count}")
        print(f"   Patterns after: {final_pattern_count}")
        print(f"   New patterns created: {patterns_created}")
        
    except Exception as e:
        print(f"❌ Knowledge graph processing failed: {e}")
        return False
    
    # Test the new patterns with SQL queries
    print("\n🔍 Testing New Patterns with SQL Queries")
    try:
        kg_conn = sqlite3.connect(kg_db_path)
        kg_cursor = kg_conn.cursor()
        
        # Query patterns by source
        kg_cursor.execute("""
            SELECT pattern_id, title, confidence, scope
            FROM patterns 
            WHERE source LIKE 'conversation:%'
            ORDER BY created_at DESC
        """)
        conv_patterns = kg_cursor.fetchall()
        
        print(f"📈 Found {len(conv_patterns)} conversation-derived patterns:")
        for pattern_id, title, confidence, scope in conv_patterns:
            print(f"   - {title[:50]}... (confidence: {confidence:.2f}, scope: {scope})")
        
        # Test full-text search on new patterns
        print(f"\n🔍 Testing full-text search on conversation patterns:")
        kg_cursor.execute("""
            SELECT pattern_id, title 
            FROM pattern_fts 
            WHERE pattern_fts MATCH 'optimization OR fix OR implementation'
            AND pattern_id LIKE 'conv_pattern_%'
            LIMIT 5
        """)
        search_results = kg_cursor.fetchall()
        
        print(f"📊 Full-text search results: {len(search_results)} patterns")
        for pattern_id, title in search_results:
            print(f"   - {title[:60]}...")
        
        kg_conn.close()
        
    except Exception as e:
        print(f"❌ Pattern query testing failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Conversation to Knowledge Graph Processing COMPLETED")
    print("📊 SQL operations validated successfully")
    print("🧠 Knowledge graph now contains conversation-derived patterns")
    
    return True

def extract_patterns_from_conversation(conv_id, user_msg, assistant_resp, context, metadata):
    """Extract knowledge patterns from a single conversation."""
    patterns = []
    
    if not user_msg or not assistant_resp:
        return patterns
    
    # Pattern 1: Problem-Solution pattern
    if any(word in user_msg.lower() for word in ['fix', 'error', 'issue', 'problem', 'bug']):
        patterns.append({
            'title': f"Problem Resolution: {user_msg[:40]}...",
            'content': f"User Problem: {user_msg}\n\nSolution Applied: {assistant_resp}",
            'pattern_type': 'problem_solution',
            'confidence': 0.85,
            'metadata': {
                'original_conversation': conv_id,
                'problem_keywords': [w for w in ['fix', 'error', 'issue', 'problem', 'bug'] if w in user_msg.lower()]
            },
            'namespaces': ['workspace.CORTEX.problem_solving']
        })
    
    # Pattern 2: Implementation pattern
    if any(word in user_msg.lower() for word in ['implement', 'create', 'add', 'build']):
        patterns.append({
            'title': f"Implementation Pattern: {user_msg[:40]}...",
            'content': f"Implementation Request: {user_msg}\n\nImplementation Details: {assistant_resp}",
            'pattern_type': 'implementation',
            'confidence': 0.80,
            'metadata': {
                'original_conversation': conv_id,
                'implementation_keywords': [w for w in ['implement', 'create', 'add', 'build'] if w in user_msg.lower()]
            },
            'namespaces': ['workspace.CORTEX.implementation']
        })
    
    # Pattern 3: Optimization pattern
    if any(word in user_msg.lower() for word in ['optimize', 'improve', 'enhance', 'better']):
        patterns.append({
            'title': f"Optimization Strategy: {user_msg[:40]}...",
            'content': f"Optimization Goal: {user_msg}\n\nOptimization Approach: {assistant_resp}",
            'pattern_type': 'optimization',
            'confidence': 0.88,
            'metadata': {
                'original_conversation': conv_id,
                'optimization_keywords': [w for w in ['optimize', 'improve', 'enhance', 'better'] if w in user_msg.lower()]
            },
            'namespaces': ['workspace.CORTEX.optimization']
        })
    
    # Pattern 4: General solution pattern for long responses
    if len(assistant_resp) > 200:  # Substantial response likely contains useful information
        patterns.append({
            'title': f"Solution Pattern: {user_msg[:40]}...",
            'content': f"Query: {user_msg}\n\nDetailed Response: {assistant_resp}",
            'pattern_type': 'solution',
            'confidence': 0.75,
            'metadata': {
                'original_conversation': conv_id,
                'response_length': len(assistant_resp),
                'substantial_response': True
            },
            'namespaces': ['workspace.CORTEX.general_solutions']
        })
    
    return patterns

if __name__ == "__main__":
    success = process_conversations_to_knowledge_graph()
    sys.exit(0 if success else 1)