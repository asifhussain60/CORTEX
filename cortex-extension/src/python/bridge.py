"""
CORTEX Python Bridge Server - HTTP API for TypeScript Communication

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import argparse
import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add CORTEX src to path
CORTEX_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(CORTEX_ROOT / "src"))

from tier1.working_memory import WorkingMemory
from tier1.work_state_manager import WorkStateManager
from tier1.session_token import SessionToken


class CortexBridgeHandler(BaseHTTPRequestHandler):
    """HTTP request handler for CORTEX brain operations"""

    def __init__(self, *args, working_memory=None, work_state=None, **kwargs):
        self.working_memory = working_memory
        self.work_state = work_state
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            if path == "/health":
                self.send_json_response({"status": "healthy"})
            
            elif path == "/conversation/last":
                conversation = self._get_last_conversation()
                self.send_json_response({"conversation": conversation})
            
            elif path == "/conversation/history":
                params = parse_qs(parsed_path.query)
                limit = int(params.get("limit", [20])[0])
                conversations = self._get_conversation_history(limit)
                self.send_json_response({"conversations": conversations})
            
            elif path == "/metrics/tokens":
                metrics = self._get_token_metrics()
                self.send_json_response(metrics)
            
            else:
                self.send_error(404, "Endpoint not found")
        
        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            if path == "/capture/message":
                self._capture_message(data)
                self.send_json_response({"success": True})
            
            elif path == "/capture/conversation":
                conversation_id = self._capture_conversation(data.get("messages", []))
                self.send_json_response({"conversationId": conversation_id})
            
            elif path == "/conversation/resume":
                result = self._resume_conversation(data.get("conversationId"))
                self.send_json_response(result)
            
            elif path == "/checkpoint/create":
                checkpoint_id = self._create_checkpoint()
                self.send_json_response({"checkpointId": checkpoint_id})
            
            elif path == "/optimize/tokens":
                result = self._optimize_tokens()
                self.send_json_response(result)
            
            elif path == "/cache/clear":
                result = self._clear_cache()
                self.send_json_response(result)
            
            else:
                self.send_error(404, "Endpoint not found")
        
        except Exception as e:
            self.send_error(500, str(e))

    def send_json_response(self, data: dict, status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[CORTEX Bridge] {format % args}")

    # === Brain Operations ===

    def _capture_message(self, data: dict):
        """Capture a single message"""
        conversation_id = self.working_memory.get_active_conversation_id()
        if not conversation_id:
            conversation_id = self.working_memory.start_conversation()
        
        self.working_memory.add_message(
            conversation_id=conversation_id,
            role=data["role"],
            content=data["content"],
            timestamp=data.get("timestamp")
        )

    def _capture_conversation(self, messages: list) -> str:
        """Capture multiple messages as a conversation"""
        conversation_id = self.working_memory.start_conversation()
        
        for msg in messages:
            self.working_memory.add_message(
                conversation_id=conversation_id,
                role=msg["role"],
                content=msg["content"],
                timestamp=msg.get("timestamp")
            )
        
        return conversation_id

    def _get_last_conversation(self) -> dict:
        """Get the most recent conversation"""
        conversations = self.working_memory.get_recent_conversations(limit=1)
        if not conversations:
            return None
        
        conv = conversations[0]
        messages = self.working_memory.get_conversation_messages(conv["id"])
        
        return {
            "id": conv["id"],
            "topic": conv.get("topic", "Untitled"),
            "timestamp": conv.get("timestamp"),
            "messages": messages
        }

    def _get_conversation_history(self, limit: int = 20) -> list:
        """Get conversation history"""
        conversations = self.working_memory.get_recent_conversations(limit=limit)
        
        result = []
        for conv in conversations:
            message_count = len(self.working_memory.get_conversation_messages(conv["id"]))
            result.append({
                "id": conv["id"],
                "topic": conv.get("topic", "Untitled"),
                "timestamp": conv.get("timestamp"),
                "messageCount": message_count
            })
        
        return result

    def _resume_conversation(self, conversation_id: str) -> dict:
        """Resume a conversation with context"""
        messages = self.working_memory.get_conversation_messages(conversation_id)
        
        # Generate context summary
        context = f"Resuming conversation with {len(messages)} messages"
        
        return {
            "messages": messages,
            "context": context
        }

    def _create_checkpoint(self) -> str:
        """Create a conversation checkpoint"""
        checkpoint_id = self.work_state.create_checkpoint()
        return checkpoint_id

    def _get_token_metrics(self) -> dict:
        """Get token usage metrics"""
        # TODO: Integrate with actual token metrics from Phase 1.5
        # For now, return placeholder data
        return {
            "sessionTokens": 5420,
            "totalTokens": 45320,
            "costEstimate": 0.0163,
            "optimizationRate": 0.62,
            "cacheStatus": "OK",
            "cacheSize": 34567,
            "patternCount": 127
        }

    def _optimize_tokens(self) -> dict:
        """Optimize token usage"""
        # TODO: Integrate with ML context optimizer from Phase 1.5
        return {
            "tokensReduced": 3240,
            "percentageReduction": 62.3
        }

    def _clear_cache(self) -> dict:
        """Clear conversation cache"""
        # TODO: Implement actual cache clearing
        return {
            "conversationsRemoved": 5,
            "tokensFreed": 12340
        }


def create_handler_class(working_memory, work_state):
    """Create handler class with injected dependencies"""
    def handler(*args, **kwargs):
        return CortexBridgeHandler(*args, working_memory=working_memory, work_state=work_state, **kwargs)
    return handler


def main():
    parser = argparse.ArgumentParser(description='CORTEX Python Bridge Server')
    parser.add_argument('--port', type=int, default=5555, help='Server port')
    args = parser.parse_args()

    # Initialize CORTEX brain components
    cortex_root = Path(CORTEX_ROOT)
    brain_path = cortex_root / "cortex-brain"
    
    working_memory = WorkingMemory(db_path=str(brain_path / "tier1" / "working_memory.db"))
    work_state = WorkStateManager(db_path=str(brain_path / "tier1" / "working_memory.db"))

    # Create handler with dependencies
    handler_class = create_handler_class(working_memory, work_state)

    # Start server
    server = HTTPServer(('localhost', args.port), handler_class)
    print(f"CORTEX Bridge Server started on port {args.port}")
    print(f"CORTEX Root: {cortex_root}")
    print("Ready to accept connections...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down CORTEX Bridge Server...")
        server.server_close()


if __name__ == "__main__":
    main()
