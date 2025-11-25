"""
CORTEX Brain Bridge Server - HTTP API for VS Code Extension

Provides REST API endpoints for the VS Code extension to communicate
with the CORTEX 2.0 brain system (Tier 1, 2, 3).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add CORTEX root to path
CORTEX_ROOT = Path(os.environ.get('CORTEX_ROOT', os.getcwd()))
sys.path.insert(0, str(CORTEX_ROOT))

# Import CORTEX 2.0 components
from src.tier1.working_memory import WorkingMemory
from src.tier2.knowledge_graph import KnowledgeGraph
from src.tier3.context_intelligence import ContextIntelligence
from src.entry_point.cortex_entry import CortexEntry
from src.config import load_config

app = Flask(__name__)
CORS(app)

# Initialize CORTEX brain components
config = load_config()
tier1 = WorkingMemory(config)
tier2 = KnowledgeGraph(config)
tier3 = ContextIntelligence(config)
cortex_entry = CortexEntry(config)

print(f"✅ CORTEX Brain Bridge Server initialized")
print(f"   Root: {CORTEX_ROOT}")
print(f"   Tier 1: {tier1}")
print(f"   Tier 2: {tier2}")
print(f"   Tier 3: {tier3}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'cortex_root': str(CORTEX_ROOT),
        'tier1_status': 'online',
        'tier2_status': 'online',
        'tier3_status': 'online'
    })


@app.route('/capture/message', methods=['POST'])
def capture_message():
    """Capture a single message to Tier 1"""
    try:
        data = request.json
        role = data.get('role')
        content = data.get('content')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Store in Tier 1 working memory
        conversation_id = tier1.store_message(
            role=role,
            content=content,
            timestamp=timestamp
        )
        
        return jsonify({
            'success': True,
            'conversationId': conversation_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/capture/conversation', methods=['POST'])
def capture_conversation():
    """Capture a full conversation to Tier 1"""
    try:
        data = request.json
        messages = data.get('messages', [])
        
        # Extract topic from first message
        topic = messages[0]['content'][:100] if messages else "Untitled"
        
        # Store conversation
        conversation_id = tier1.store_conversation(
            topic=topic,
            messages=messages
        )
        
        return jsonify({
            'success': True,
            'conversationId': conversation_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/conversation/last', methods=['GET'])
def get_last_conversation():
    """Get the most recent conversation"""
    try:
        conversation = tier1.get_last_conversation()
        
        return jsonify({
            'conversation': conversation
        })
    except Exception as e:
        return jsonify({
            'conversation': None,
            'error': str(e)
        }), 500


@app.route('/conversation/resume', methods=['POST'])
def resume_conversation():
    """Resume a conversation by ID"""
    try:
        data = request.json
        conversation_id = data.get('conversationId')
        
        # Get conversation details
        conversation = tier1.get_conversation(conversation_id)
        messages = tier1.get_conversation_messages(conversation_id)
        
        # Get context from Tier 2/3
        context = tier3.get_conversation_context(conversation_id)
        
        return jsonify({
            'messages': messages,
            'context': context
        })
    except Exception as e:
        return jsonify({
            'messages': [],
            'context': '',
            'error': str(e)
        }), 500


@app.route('/conversation/history', methods=['GET'])
def get_conversation_history():
    """Get conversation history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        conversations = tier1.get_conversation_history(limit=limit)
        
        return jsonify({
            'conversations': conversations
        })
    except Exception as e:
        return jsonify({
            'conversations': [],
            'error': str(e)
        }), 500


@app.route('/checkpoint/create', methods=['POST'])
def create_checkpoint():
    """Create a checkpoint of current state"""
    try:
        checkpoint_id = tier1.create_checkpoint()
        
        return jsonify({
            'success': True,
            'checkpointId': checkpoint_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/metrics/tokens', methods=['GET'])
def get_token_metrics():
    """Get token usage metrics"""
    try:
        # Get metrics from Tier 1
        metrics = tier1.get_token_metrics()
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({
            'sessionTokens': 0,
            'totalTokens': 0,
            'error': str(e)
        }), 500


@app.route('/optimize/tokens', methods=['POST'])
def optimize_tokens():
    """Run token optimization"""
    try:
        # Run optimization
        result = tier1.optimize_tokens()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'tokensReduced': 0,
            'percentageReduction': 0,
            'error': str(e)
        }), 500


@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear conversation cache"""
    try:
        result = tier1.clear_old_conversations()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'conversationsRemoved': 0,
            'tokensFreed': 0,
            'error': str(e)
        }), 500


@app.route('/query', methods=['POST'])
def process_query():
    """Process a query through CORTEX entry point"""
    try:
        data = request.json
        query = data.get('query', '')
        context = data.get('context', {})
        
        # Route through CORTEX entry point
        result = cortex_entry.process(query, context)
        
        return jsonify({
            'success': True,
            'response': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def main():
    parser = argparse.ArgumentParser(description='CORTEX Brain Bridge Server')
    parser.add_argument('--port', type=int, default=5555, help='Server port')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Server host')
    args = parser.parse_args()
    
    print(f"\n🧠 Starting CORTEX Brain Bridge Server")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   CORTEX Root: {CORTEX_ROOT}")
    print(f"\n✅ Server ready!\n")
    
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == '__main__':
    main()
