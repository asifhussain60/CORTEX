"""
CORTEX Tier 1: Request Logger
Logs raw requests and responses

Task 1.6: Raw Request Logging
Duration: 30 minutes
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class RequestLogger:
    """
    Logs raw requests and responses to JSONL file
    
    Responsibilities:
    - Log user requests with timestamps
    - Log system responses
    - Track request/response pairs
    - Support conversation association
    """
    
    def __init__(self, log_path: Path):
        """
        Initialize request logger
        
        Args:
            log_path: Path to request log JSONL file
        """
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_request(
        self,
        request_text: str,
        conversation_id: Optional[str] = None,
        intent: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Log a user request
        
        Args:
            request_text: The request text
            conversation_id: Associated conversation
            intent: Detected intent
            metadata: Additional metadata
            
        Returns:
            request_id: Generated request ID
        """
        import random
        
        timestamp = datetime.now()
        request_id = f"req-{timestamp.strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        
        log_entry = {
            'request_id': request_id,
            'timestamp': timestamp.isoformat(),
            'type': 'request',
            'conversation_id': conversation_id,
            'intent': intent,
            'text': request_text,
            'metadata': metadata or {}
        }
        
        self._write_entry(log_entry)
        return request_id
    
    def log_response(
        self,
        request_id: str,
        response_text: str,
        conversation_id: Optional[str] = None,
        status: str = 'success',
        metadata: Optional[Dict] = None
    ):
        """
        Log a system response
        
        Args:
            request_id: Associated request ID
            response_text: The response text
            conversation_id: Associated conversation
            status: Response status (success, error, partial)
            metadata: Additional metadata
        """
        timestamp = datetime.now()
        
        log_entry = {
            'request_id': request_id,
            'timestamp': timestamp.isoformat(),
            'type': 'response',
            'conversation_id': conversation_id,
            'status': status,
            'text': response_text,
            'metadata': metadata or {}
        }
        
        self._write_entry(log_entry)
    
    def log_error(
        self,
        request_id: str,
        error_message: str,
        conversation_id: Optional[str] = None,
        error_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Log an error
        
        Args:
            request_id: Associated request ID
            error_message: Error description
            conversation_id: Associated conversation
            error_type: Type of error
            metadata: Additional metadata
        """
        timestamp = datetime.now()
        
        log_entry = {
            'request_id': request_id,
            'timestamp': timestamp.isoformat(),
            'type': 'error',
            'conversation_id': conversation_id,
            'error_type': error_type,
            'error_message': error_message,
            'metadata': metadata or {}
        }
        
        self._write_entry(log_entry)
    
    def _write_entry(self, entry: Dict):
        """
        Write a log entry to JSONL file
        
        Args:
            entry: Log entry dictionary
        """
        with open(self.log_path, 'a', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    
    def get_recent_requests(self, limit: int = 100) -> list:
        """
        Get recent requests
        
        Args:
            limit: Maximum number to retrieve
            
        Returns:
            List of request entries
        """
        if not self.log_path.exists():
            return []
        
        entries = []
        
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        if entry.get('type') == 'request':
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        # Return most recent
        return entries[-limit:] if len(entries) > limit else entries
    
    def get_request_response_pair(self, request_id: str) -> Dict:
        """
        Get request and response for a request ID
        
        Args:
            request_id: Request ID to find
            
        Returns:
            Dictionary with request and response
        """
        if not self.log_path.exists():
            return {}
        
        request = None
        response = None
        error = None
        
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        if entry.get('request_id') == request_id:
                            if entry.get('type') == 'request':
                                request = entry
                            elif entry.get('type') == 'response':
                                response = entry
                            elif entry.get('type') == 'error':
                                error = entry
                    except json.JSONDecodeError:
                        continue
        
        return {
            'request': request,
            'response': response,
            'error': error
        }
    
    def get_conversation_requests(self, conversation_id: str) -> list:
        """
        Get all requests for a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of request entries
        """
        if not self.log_path.exists():
            return []
        
        entries = []
        
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        if entry.get('conversation_id') == conversation_id:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        return entries
    
    def get_statistics(self) -> Dict:
        """
        Get request logging statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.log_path.exists():
            return {
                'total_requests': 0,
                'total_responses': 0,
                'total_errors': 0
            }
        
        stats = {
            'total_requests': 0,
            'total_responses': 0,
            'total_errors': 0,
            'by_intent': {},
            'by_status': {}
        }
        
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        entry_type = entry.get('type')
                        
                        if entry_type == 'request':
                            stats['total_requests'] += 1
                            intent = entry.get('intent', 'unknown')
                            stats['by_intent'][intent] = stats['by_intent'].get(intent, 0) + 1
                        elif entry_type == 'response':
                            stats['total_responses'] += 1
                            status = entry.get('status', 'unknown')
                            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                        elif entry_type == 'error':
                            stats['total_errors'] += 1
                    except json.JSONDecodeError:
                        continue
        
        return stats
